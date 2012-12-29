import cStringIO, email.Parser, os, errno, re
        try:
            util.unlinkpath(self._join(fname))
        except OSError, inst:
            if inst.errno != errno.ENOENT:
                raise
            return old[top:len(old)-bot], new[top:len(new)-bot], top
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

    if not repo.ui.quiet:
        hexfunc = repo.ui.debugflag and hex or short
        revs = [hexfunc(node) for node in [node1, node2] if node]

def _addmodehdr(header, omode, nmode):
    if omode != nmode:
        header.append('old mode %s\n' % omode)
        header.append('new mode %s\n' % nmode)

        return os.path.join(prefix, f)
                        _addmodehdr(header, omode, mode)
                    _addmodehdr(header, gitmode[oflag], gitmode[nflag])
            if opts.git:
                header.insert(0, mdiff.diffline(revs, join(a), join(b), opts))
                text = b85diff(to, tn)
                                    join(a), join(b), revs, opts=opts)