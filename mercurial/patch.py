import cStringIO, email.Parser, os, errno, re, posixpath
        if line.startswith('diff --git a/'):
        util.unlinkpath(self._join(fname), ignoremissing=True)
            return old[top:len(old) - bot], new[top:len(new) - bot], top
        elif x.startswith('diff --git a/'):
    hexfunc = repo.ui.debugflag and hex or short
    revs = [hexfunc(node) for node in [node1, node2] if node]
        return posixpath.join(prefix, f)

    def addmodehdr(header, omode, nmode):
        if omode != nmode:
            header.append('old mode %s\n' % omode)
            header.append('new mode %s\n' % nmode)

    def addindexmeta(meta, revs):
        if opts.git:
            i = len(revs)
            if i==2:
                meta.append('index %s..%s\n' % tuple(revs))
            elif i==3:
                meta.append('index %s,%s..%s\n' % tuple(revs))

    def gitindex(text):
        if not text:
            return hex(nullid)
        l = len(text)
        s = util.sha1('blob %d\0' % l)
        s.update(text)
        return s.hexdigest()

    def diffline(a, b, revs):
        if opts.git:
            line = 'diff --git a/%s b/%s\n' % (a, b)
        elif not repo.ui.quiet:
            if revs:
                revinfo = ' '.join(["-r %s" % rev for rev in revs])
                line = 'diff %s %s\n' % (revinfo, a)
            else:
                line = 'diff %s\n' % a
        else:
            line = ''
        return line
                        addmodehdr(header, omode, mode)
                        if util.binary(to):
                            dodiff = 'binary'
                    addmodehdr(header, gitmode[oflag], gitmode[nflag])
            if opts.git or revs:
                header.insert(0, diffline(join(a), join(b), revs))
                text = mdiff.b85diff(to, tn)
                if text:
                    addindexmeta(header, [gitindex(to), gitindex(tn)])
                                    join(a), join(b), opts=opts)
            if line.startswith('diff --git a/'):