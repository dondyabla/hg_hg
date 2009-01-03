# rebase.py - rebasing feature for mercurial
#
# Copyright 2008 Stefano Tortarolo <stefano.tortarolo at gmail dot com>
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.

'''move sets of revisions to a different ancestor

This extension lets you rebase changesets in an existing Mercurial repository.

For more information:
http://www.selenic.com/mercurial/wiki/index.cgi/RebaseProject
'''

from mercurial import util, repair, merge, cmdutil, dispatch, commands
from mercurial import extensions, ancestor
from mercurial.commands import templateopts
from mercurial.node import nullrev
from mercurial.i18n import _
import os, errno

def rebasemerge(repo, rev, first=False):
    'return the correct ancestor'
    oldancestor = ancestor.ancestor

    def newancestor(a, b, pfunc):
        ancestor.ancestor = oldancestor
        anc = ancestor.ancestor(a, b, pfunc)
        if b == rev:
            return repo[rev].parents()[0].rev()
        return ancestor.ancestor(a, b, pfunc)

    if not first:
        ancestor.ancestor = newancestor
    else:
        repo.ui.debug(_("first revision, do not change ancestor\n"))
    stats = merge.update(repo, rev, True, True, False)
    return stats

def rebase(ui, repo, **opts):
    """move changeset (and descendants) to a different branch

    Rebase uses repeated merging to graft changesets from one part of history
    onto another. This can be useful for linearizing local changes relative to
    a master development tree.

    If a rebase is interrupted to manually resolve a merge, it can be continued
    with --continue or aborted with --abort.
    """
    originalwd = target = None
    external = nullrev
    state = skipped = {}

    lock = wlock = None
    try:
        lock = repo.lock()
        wlock = repo.wlock()

        # Validate input and define rebasing points
        destf = opts.get('dest', None)
        srcf = opts.get('source', None)
        basef = opts.get('base', None)
        contf = opts.get('continue')
        abortf = opts.get('abort')
        collapsef = opts.get('collapse', False)
        extrafn = opts.get('extrafn')
        if opts.get('keepbranches', None):
            if extrafn:
                raise dispatch.ParseError('rebase',
                        _('cannot use both keepbranches and extrafn'))
            def extrafn(ctx, extra):
                extra['branch'] = ctx.branch()

        if contf or abortf:
            if contf and abortf:
                raise dispatch.ParseError('rebase',
                                    _('cannot use both abort and continue'))
            if collapsef:
                raise dispatch.ParseError('rebase',
                        _('cannot use collapse with continue or abort'))

            if (srcf or basef or destf):
                raise dispatch.ParseError('rebase',
                    _('abort and continue do not allow specifying revisions'))

            originalwd, target, state, collapsef, external = restorestatus(repo)
            if abortf:
                abort(repo, originalwd, target, state)
                return
        else:
            if srcf and basef:
                raise dispatch.ParseError('rebase', _('cannot specify both a '
                                                        'revision and a base'))
            cmdutil.bail_if_changed(repo)
            result = buildstate(repo, destf, srcf, basef, collapsef)
            if result:
                originalwd, target, state, external = result
            else: # Empty state built, nothing to rebase
                repo.ui.status(_('nothing to rebase\n'))
                return

        # Rebase
        targetancestors = list(repo.changelog.ancestors(target))
        targetancestors.append(target)

        for rev in util.sort(state):
            if state[rev] == -1:
                storestatus(repo, originalwd, target, state, collapsef,
                                                                external)
                rebasenode(repo, rev, target, state, skipped, targetancestors,
                                                       collapsef, extrafn)
        ui.note(_('rebase merging completed\n'))

        if collapsef:
            p1, p2 = defineparents(repo, min(state), target,
                                                        state, targetancestors)
            concludenode(repo, rev, p1, external, state, collapsef,
                         last=True, skipped=skipped, extrafn=extrafn)

        if 'qtip' in repo.tags():
            updatemq(repo, state, skipped, **opts)

        if not opts.get('keep'):
            # Remove no more useful revisions
            if (util.set(repo.changelog.descendants(min(state)))
                                                    - util.set(state.keys())):
                ui.warn(_("warning: new changesets detected on source branch, "
                                                        "not stripping\n"))
            else:
                repair.strip(repo.ui, repo, repo[min(state)].node(), "strip")

        clearstatus(repo)
        ui.status(_("rebase completed\n"))
        if os.path.exists(repo.sjoin('undo')):
            util.unlink(repo.sjoin('undo'))
        if skipped:
            ui.note(_("%d revisions have been skipped\n") % len(skipped))
    finally:
        del lock, wlock

def concludenode(repo, rev, p1, p2, state, collapse, last=False, skipped={},
                 extrafn=None):
    """Skip commit if collapsing has been required and rev is not the last
    revision, commit otherwise
    """
    repo.ui.debug(_(" set parents\n"))
    if collapse and not last:
        repo.dirstate.setparents(repo[p1].node())
        return None

    repo.dirstate.setparents(repo[p1].node(), repo[p2].node())

    # Commit, record the old nodeid
    m, a, r = repo.status()[:3]
    newrev = nullrev
    try:
        if last:
            commitmsg = 'Collapsed revision'
            for rebased in state:
                if rebased not in skipped:
                    commitmsg += '\n* %s' % repo[rebased].description()
            commitmsg = repo.ui.edit(commitmsg, repo.ui.username())
        else:
            commitmsg = repo[rev].description()
        # Commit might fail if unresolved files exist
        extra = {'rebase_source': repo[rev].hex()}
        if extrafn:
            extrafn(repo[rev], extra)
        newrev = repo.commit(m+a+r,
                            text=commitmsg,
                            user=repo[rev].user(),
                            date=repo[rev].date(),
                            extra=extra)
        return newrev
    except util.Abort:
        # Invalidate the previous setparents
        repo.dirstate.invalidate()
        raise

def rebasenode(repo, rev, target, state, skipped, targetancestors, collapse,
               extrafn):
    'Rebase a single revision'
    repo.ui.debug(_("rebasing %d:%s\n") % (rev, repo[rev]))

    p1, p2 = defineparents(repo, rev, target, state, targetancestors)

    repo.ui.debug(_(" future parents are %d and %d\n") % (repo[p1].rev(),
                                                            repo[p2].rev()))

    # Merge phase
    if len(repo.parents()) != 2:
        # Update to target and merge it with local
        if repo['.'].rev() != repo[p1].rev():
            repo.ui.debug(_(" update to %d:%s\n") % (repo[p1].rev(), repo[p1]))
            merge.update(repo, p1, False, True, False)
        else:
            repo.ui.debug(_(" already in target\n"))
        repo.dirstate.write()
        repo.ui.debug(_(" merge against %d:%s\n") % (repo[rev].rev(), repo[rev]))
        first = repo[rev].rev() == repo[min(state)].rev()
        stats = rebasemerge(repo, rev, first)

        if stats[3] > 0:
            raise util.Abort(_('fix unresolved conflicts with hg resolve then '
                                                'run hg rebase --continue'))
    else: # we have an interrupted rebase
        repo.ui.debug(_('resuming interrupted rebase\n'))


    newrev = concludenode(repo, rev, p1, p2, state, collapse,
                          extrafn=extrafn)

    # Update the state
    if newrev is not None:
        state[rev] = repo[newrev].rev()
    else:
        if not collapse:
            repo.ui.note(_('no changes, revision %d skipped\n') % rev)
            repo.ui.debug(_('next revision set to %s\n') % p1)
            skipped[rev] = True
        state[rev] = p1

def defineparents(repo, rev, target, state, targetancestors):
    'Return the new parent relationship of the revision that will be rebased'
    parents = repo[rev].parents()
    p1 = p2 = nullrev

    P1n = parents[0].rev()
    if P1n in targetancestors:
        p1 = target
    elif P1n in state:
        p1 = state[P1n]
    else: # P1n external
        p1 = target
        p2 = P1n

    if len(parents) == 2 and parents[1].rev() not in targetancestors:
        P2n = parents[1].rev()
        # interesting second parent
        if P2n in state:
            if p1 == target: # P1n in targetancestors or external
                p1 = state[P2n]
            else:
                p2 = state[P2n]
        else: # P2n external
            if p2 != nullrev: # P1n external too => rev is a merged revision
                raise util.Abort(_('cannot use revision %d as base, result '
                        'would have 3 parents') % rev)
            p2 = P2n
    return p1, p2

def updatemq(repo, state, skipped, **opts):
    'Update rebased mq patches - finalize and then import them'
    mqrebase = {}
    for p in repo.mq.applied:
        if repo[p.rev].rev() in state:
            repo.ui.debug(_('revision %d is an mq patch (%s), finalize it.\n') %
                                        (repo[p.rev].rev(), p.name))
            mqrebase[repo[p.rev].rev()] = p.name

    if mqrebase:
        repo.mq.finish(repo, mqrebase.keys())

        # We must start import from the newest revision
        mq = mqrebase.keys()
        mq.sort()
        mq.reverse()
        for rev in mq:
            if rev not in skipped:
                repo.ui.debug(_('import mq patch %d (%s)\n')
                              % (state[rev], mqrebase[rev]))
                repo.mq.qimport(repo, (), patchname=mqrebase[rev],
                            git=opts.get('git', False),rev=[str(state[rev])])
        repo.mq.save_dirty()

def storestatus(repo, originalwd, target, state, collapse, external):
    'Store the current status to allow recovery'
    f = repo.opener("rebasestate", "w")
    f.write(repo[originalwd].hex() + '\n')
    f.write(repo[target].hex() + '\n')
    f.write(repo[external].hex() + '\n')
    f.write('%d\n' % int(collapse))
    for d, v in state.items():
        oldrev = repo[d].hex()
        newrev = repo[v].hex()
        f.write("%s:%s\n" % (oldrev, newrev))
    f.close()
    repo.ui.debug(_('rebase status stored\n'))

def clearstatus(repo):
    'Remove the status files'
    if os.path.exists(repo.join("rebasestate")):
        util.unlink(repo.join("rebasestate"))

def restorestatus(repo):
    'Restore a previously stored status'
    try:
        target = None
        collapse = False
        external = nullrev
        state = {}
        f = repo.opener("rebasestate")
        for i, l in enumerate(f.read().splitlines()):
            if i == 0:
                originalwd = repo[l].rev()
            elif i == 1:
                target = repo[l].rev()
            elif i == 2:
                external = repo[l].rev()
            elif i == 3:
                collapse = bool(int(l))
            else:
                oldrev, newrev = l.split(':')
                state[repo[oldrev].rev()] = repo[newrev].rev()
        repo.ui.debug(_('rebase status resumed\n'))
        return originalwd, target, state, collapse, external
    except IOError, err:
        if err.errno != errno.ENOENT:
            raise
        raise util.Abort(_('no rebase in progress'))

def abort(repo, originalwd, target, state):
    'Restore the repository to its original state'
    if util.set(repo.changelog.descendants(target)) - util.set(state.values()):
        repo.ui.warn(_("warning: new changesets detected on target branch, "
                                                    "not stripping\n"))
    else:
        # Strip from the first rebased revision
        merge.update(repo, repo[originalwd].rev(), False, True, False)
        rebased = filter(lambda x: x > -1, state.values())
        if rebased:
            strippoint = min(rebased)
            repair.strip(repo.ui, repo, repo[strippoint].node(), "strip")
        clearstatus(repo)
        repo.ui.status(_('rebase aborted\n'))

def buildstate(repo, dest, src, base, collapse):
    'Define which revisions are going to be rebased and where'
    state = {}
    targetancestors = util.set()

    if not dest:
         # Destination defaults to the latest revision in the current branch
        branch = repo[None].branch()
        dest = repo[branch].rev()
    else:
        if 'qtip' in repo.tags() and (repo[dest].hex() in
                                [s.rev for s in repo.mq.applied]):
            raise util.Abort(_('cannot rebase onto an applied mq patch'))
        dest = repo[dest].rev()

    if src:
        commonbase = repo[src].ancestor(repo[dest])
        if commonbase == repo[src]:
            raise util.Abort(_('cannot rebase an ancestor'))
        if commonbase == repo[dest]:
            raise util.Abort(_('cannot rebase a descendant'))
        source = repo[src].rev()
    else:
        if base:
            cwd = repo[base].rev()
        else:
            cwd = repo['.'].rev()

        if cwd == dest:
            repo.ui.debug(_('already working on current\n'))
            return None

        targetancestors = util.set(repo.changelog.ancestors(dest))
        if cwd in targetancestors:
            repo.ui.debug(_('already working on the current branch\n'))
            return None

        cwdancestors = util.set(repo.changelog.ancestors(cwd))
        cwdancestors.add(cwd)
        rebasingbranch = cwdancestors - targetancestors
        source = min(rebasingbranch)

    repo.ui.debug(_('rebase onto %d starting from %d\n') % (dest, source))
    state = dict.fromkeys(repo.changelog.descendants(source), nullrev)
    external = nullrev
    if collapse:
        if not targetancestors:
            targetancestors = util.set(repo.changelog.ancestors(dest))
        for rev in state:
            # Check externals and fail if there are more than one
            for p in repo[rev].parents():
                if (p.rev() not in state and p.rev() != source
                            and p.rev() not in targetancestors):
                    if external != nullrev:
                        raise util.Abort(_('unable to collapse, there is more '
                                'than one external parent'))
                    external = p.rev()

    state[source] = nullrev
    return repo['.'].rev(), repo[dest].rev(), state, external

def pullrebase(orig, ui, repo, *args, **opts):
    'Call rebase after pull if the latter has been invoked with --rebase'
    if opts.get('rebase'):
        if opts.get('update'):
            raise util.Abort(_('--update and --rebase are not compatible'))

        cmdutil.bail_if_changed(repo)
        revsprepull = len(repo)
        orig(ui, repo, *args, **opts)
        revspostpull = len(repo)
        if revspostpull > revsprepull:
            rebase(ui, repo, **opts)
    else:
        orig(ui, repo, *args, **opts)

def uisetup(ui):
    'Replace pull with a decorator to provide --rebase option'
    entry = extensions.wrapcommand(commands.table, 'pull', pullrebase)
    entry[1].append(('', 'rebase', None,
                     _("rebase working directory to branch head"))
)

cmdtable = {
"rebase":
        (rebase,
        [
        ('', 'keep', False, _('keep original revisions')),
        ('', 'keepbranches', False, _('keep original branches')),
        ('s', 'source', '', _('rebase from a given revision')),
        ('b', 'base', '', _('rebase from the base of a given revision')),
        ('d', 'dest', '', _('rebase onto a given revision')),
        ('', 'collapse', False, _('collapse the rebased revisions')),
        ('c', 'continue', False, _('continue an interrupted rebase')),
        ('a', 'abort', False, _('abort an interrupted rebase')),] +
         templateopts,
        _('hg rebase [-s rev | -b rev] [-d rev] [--collapse] | [-c] | [-a] | '
                                                                '[--keep]')),
}
