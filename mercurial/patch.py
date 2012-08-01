import cStringIO, email.Parser, os, errno, re
from node import hex, nullid, short
import context
        gitsendmail = 'git-send-email' in msg.get('X-Mailer', '')
                    elif line == '---' and gitsendmail:
    p1 = parents and parents.pop(0) or None
    p2 = parents and parents.pop(0) or None
        islink = mode & 020000
        isexec = mode & 0100
        if line.startswith('diff --git'):
        isexec)) tuple.
        path = self._join(fname)
        if os.path.islink(path):
            return (os.readlink(path), (True, False))
            isexec = os.lstat(path).st_mode & 0100 != 0
        except OSError, e:
        return (self.opener.read(fname), (False, isexec))
            util.setflags(self._join(fname), islink, isexec)
                util.setflags(self._join(fname), False, True)
        try:
            util.unlinkpath(self._join(fname))
        except OSError, inst:
            if inst.errno != errno.ENOENT:
                raise
        return os.path.lexists(self._join(fname))
        addremoved = set(self.changed)
                    # addremove().
                    addremoved.discard(f)
        if addremoved:
            cwd = self.repo.getcwd()
            if cwd:
                addremoved = [util.pathto(self.repo.root, cwd, f)
                              for f in addremoved]
            scmutil.addremove(self.repo, addremoved, similarity=self.similarity)
            raise IOError
            raise IOError
        try:
            if self.copysource is None:
                data, mode = backend.getfile(self.fname)
                self.exists = True
            else:
                data, mode = store.getfile(self.copysource)[:2]
                self.exists = backend.exists(self.fname)
        except IOError:
                               "exists\n" % self.fname))
                self.lines[:] = h.new()
                self.offset += len(h.new())
        for fuzzlen in xrange(3):
            return old[top:len(old)-bot], new[top:len(new)-bot], top
    'A binary patch file. Only understands literals so far.'
    def new(self):
        size = int(line[8:].rstrip())
            except ValueError, e:
def pathstrip(path, strip):
        return '', path.rstrip()
    return path[:i].lstrip(), path[i:].rstrip()
def makepatchmeta(backend, afile_orig, bfile_orig, hunk, strip):
    abase, afile = pathstrip(afile_orig, strip)
    bbase, bfile = pathstrip(bfile_orig, strip)
            fname = isbackup and afile or bfile
            fname = isbackup and afile or bfile
        elif x.startswith('diff --git'):
def applydiff(ui, fp, backend, store, strip=1, eolmode='strict'):
                      eolmode=eolmode)
def _applydiff(ui, fp, patcher, backend, store, strip=1,
        return pathstrip(p, strip - 1)[1]
                gp = makepatchmeta(backend, afile, bfile, first_hunk, strip)
            except PatchError, inst:
                try:
                    data, mode = backend.getfile(path)
                except IOError, e:
                    if e.errno != errno.ENOENT:
                        raise
            cfiles = list(files)
            cwd = repo.getcwd()
            if cwd:
                cfiles = [util.pathto(repo.root, cwd, f)
                          for f in cfiles]
            scmutil.addremove(repo, cfiles, similarity=similarity)
def patchbackend(ui, backend, patchobj, strip, files=None, eolmode='strict'):
        ret = applydiff(ui, fp, backend, store, strip=strip,
def internalpatch(ui, repo, patchobj, strip, files=None, eolmode='strict',
                  similarity=0):
    return patchbackend(ui, backend, patchobj, strip, files, eolmode)
def patchrepo(ui, repo, ctx, store, patchobj, strip, files=None,
    return patchbackend(ui, backend, patchobj, strip, files, eolmode)

def makememctx(repo, parents, text, user, date, branch, files, store,
               editor=None):
    def getfilectx(repo, memctx, path):
        data, (islink, isexec), copied = store.getfile(path)
        return context.memfilectx(path, data, islink=islink, isexec=isexec,
                                  copied=copied)
    extra = {}
    if branch:
        extra['branch'] = encoding.fromlocal(branch)
    ctx =  context.memctx(repo, parents, text, files, getfilectx, user,
                          date, extra)
    if editor:
        ctx._text = editor(repo, ctx, [])
    return ctx

def patch(ui, repo, patchname, strip=1, files=None, eolmode='strict',
    try:
        if patcher:
            return _externalpatch(ui, repo, patcher, patchname, strip,
                                  files, similarity)
        return internalpatch(ui, repo, patchname, strip, files, eolmode,
                             similarity)
    except PatchError, err:
        raise util.Abort(str(err))
                    gp.path = pathstrip(gp.path, strip - 1)[1]
                        gp.oldpath = pathstrip(gp.oldpath, strip - 1)[1]
                    gp = makepatchmeta(backend, afile, bfile, first_hunk, strip)
def b85diff(to, tn):
    '''print base85-encoded binary diff'''
    def gitindex(text):
        if not text:
            return hex(nullid)
        l = len(text)
        s = util.sha1('blob %d\0' % l)
        s.update(text)
        return s.hexdigest()
    def fmtline(line):
        l = len(line)
        if l <= 26:
            l = chr(ord('A') + l - 1)
        else:
            l = chr(l - 26 + ord('a') - 1)
        return '%c%s\n' % (l, base85.b85encode(line, True))
    def chunk(text, csize=52):
        l = len(text)
        i = 0
        while i < l:
            yield text[i:i + csize]
            i += csize

    tohash = gitindex(to)
    tnhash = gitindex(tn)
    if tohash == tnhash:
        return ""

    # TODO: deltas
    ret = ['index %s..%s\nGIT binary patch\nliteral %s\n' %
           (tohash, tnhash, len(tn))]
    for l in chunk(zlib.compress(tn)):
        ret.append(fmtline(l))
    ret.append('\n')
    return ''.join(ret)
class GitDiffRequired(Exception):
    pass
def diffopts(ui, opts=None, untrusted=False, section='diff'):
    def get(key, name=None, getter=ui.configbool):
        return ((opts and opts.get(key)) or
                getter(section, name or key, None, untrusted=untrusted))
    return mdiff.diffopts(
        text=opts and opts.get('text'),
        git=get('git'),
        nodates=get('nodates'),
        showfunc=get('show_function', 'showfunc'),
        ignorews=get('ignore_all_space', 'ignorews'),
        ignorewsamount=get('ignore_space_change', 'ignorewsamount'),
        ignoreblanklines=get('ignore_blank_lines', 'ignoreblanklines'),
        context=get('unified', getter=ui.config))
         losedatafn=None, prefix=''):
    '''
        order = util.deque()
    revs = None
    if not repo.ui.quiet:
        hexfunc = repo.ui.debugflag and hex or short
        revs = [hexfunc(node) for node in [node1, node2] if node]
        copy = copies.pathcopies(ctx1, ctx2)
                       copy, getfilectx, opts, losedata, prefix)
                # highlight trailing whitespace, but only in changed lines
                    yield (stripline, label)
def _addmodehdr(header, omode, nmode):
    if omode != nmode:
        header.append('old mode %s\n' % omode)
        header.append('new mode %s\n' % nmode)
            copy, getfilectx, opts, losedatafn, prefix):
    def join(f):
        return os.path.join(prefix, f)
    man1 = ctx1.manifest()
    gone = set()
    copyto = dict([(v, k) for k, v in copy.items()])

    if opts.git:
        revs = None

    for f in sorted(modified + added + removed):
        to = None
        tn = None
        dodiff = True
        if f in man1:
            to = getfilectx(f, ctx1).data()
        if f not in removed:
            tn = getfilectx(f, ctx2).data()
        a, b = f, f
        if opts.git or losedatafn:
            if f in added:
                mode = gitmode[ctx2.flags(f)]
                if f in copy or f in copyto:
                    if opts.git:
                        if f in copy:
                            a = copy[f]
                        else:
                            a = copyto[f]
                        omode = gitmode[man1.flags(a)]
                        _addmodehdr(header, omode, mode)
                        if a in removed and a not in gone:
                            op = 'rename'
                            gone.add(a)
                        else:
                            op = 'copy'
                        header.append('%s from %s\n' % (op, join(a)))
                        header.append('%s to %s\n' % (op, join(f)))
                        to = getfilectx(a, ctx1).data()
                    else:
                        losedatafn(f)
                else:
                    if opts.git:
                        header.append('new file mode %s\n' % mode)
                    elif ctx2.flags(f):
                        losedatafn(f)
                # In theory, if tn was copied or renamed we should check
                # if the source is binary too but the copy record already
                # forces git mode.
                if util.binary(tn):
                    if opts.git:
                        dodiff = 'binary'
                    else:
                        losedatafn(f)
                if not opts.git and not tn:
                    # regular diffs cannot represent new empty file
                    losedatafn(f)
            elif f in removed:
                if opts.git:
                    # have we already reported a copy above?
                    if ((f in copy and copy[f] in added
                         and copyto[copy[f]] == f) or
                        (f in copyto and copyto[f] in added
                         and copy[copyto[f]] == f)):
                        dodiff = False
                    else:
                        header.append('deleted file mode %s\n' %
                                      gitmode[man1.flags(f)])
                elif not to or util.binary(to):
                    # regular diffs cannot represent empty file deletion
                    losedatafn(f)
            else:
                oflag = man1.flags(f)
                nflag = ctx2.flags(f)
                binary = util.binary(to) or util.binary(tn)
                if opts.git:
                    _addmodehdr(header, gitmode[oflag], gitmode[nflag])
                    if binary:
                        dodiff = 'binary'
                elif binary or nflag != oflag:
                    losedatafn(f)
            if opts.git:
                header.insert(0, mdiff.diffline(revs, join(a), join(b), opts))

        if dodiff:
            if dodiff == 'binary':
                text = b85diff(to, tn)
            else:
                text = mdiff.unidiff(to, date1,
                                    # ctx2 date may be dynamic
                                    tn, util.datestr(ctx2.date()),
                                    join(a), join(b), revs, opts=opts)
            if header and (text or len(header) > 1):
                yield ''.join(header)
                yield text
            if line.startswith('diff --git'):
                filename = gitre.search(line).group(1)