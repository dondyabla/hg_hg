# template-filters.py - common template expansion filters
#
# Copyright 2005-2008 Matt Mackall <mpm@selenic.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

import cgi, re, os, time, urllib
import encoding, node, util

def addbreaks(text):
    '''replace raw newlines with xhtml line breaks.'''
    return text.replace('\n', '<br/>\n')

agescales = [("year", 3600 * 24 * 365),
             ("month", 3600 * 24 * 30),
             ("week", 3600 * 24 * 7),
             ("day", 3600 * 24),
             ("hour", 3600),
             ("minute", 60),
             ("second", 1)]

def age(date):
    '''turn a (timestamp, tzoff) tuple into an age string.'''

    def plural(t, c):
        if c == 1:
            return t
        return t + "s"
    def fmt(t, c):
        return "%d %s" % (c, plural(t, c))

    now = time.time()
    then = date[0]
    if then > now:
        return 'in the future'

    delta = max(1, int(now - then))
    if delta > agescales[0][1] * 2:
        return util.shortdate(date)

    for t, s in agescales:
        n = delta // s
        if n >= 2 or s == 1:
            return '%s ago' % fmt(t, n)

def basename(path):
    return os.path.basename(path)

def datefilter(text):
    return util.datestr(text)

def domain(author):
    '''get domain of author, or empty string if none.'''
    f = author.find('@')
    if f == -1:
        return ''
    author = author[f + 1:]
    f = author.find('>')
    if f >= 0:
        author = author[:f]
    return author

def email(text):
    return util.email(text)

def escape(text):
    return cgi.escape(text, True)

para_re = None
space_re = None

def fill(text, width):
    '''fill many paragraphs.'''
    global para_re, space_re
    if para_re is None:
        para_re = re.compile('(\n\n|\n\\s*[-*]\\s*)', re.M)
        space_re = re.compile(r'  +')

    def findparas():
        start = 0
        while True:
            m = para_re.search(text, start)
            if not m:
                uctext = unicode(text[start:], encoding.encoding)
                w = len(uctext)
                while 0 < w and uctext[w - 1].isspace():
                    w -= 1
                yield (uctext[:w].encode(encoding.encoding),
                       uctext[w:].encode(encoding.encoding))
                break
            yield text[start:m.start(0)], m.group(1)
            start = m.end(1)

    return "".join([space_re.sub(' ', util.wrap(para, width=width)) + rest
                    for para, rest in findparas()])

def fill68(text):
    return fill(text, 68)

def fill76(text):
    return fill(text, 76)

def firstline(text):
    '''return the first line of text'''
    try:
        return text.splitlines(True)[0].rstrip('\r\n')
    except IndexError:
        return ''

def hexfilter(text):
    return node.hex(text)

def hgdate(text):
    return "%d %d" % text

def isodate(text):
    return util.datestr(text, '%Y-%m-%d %H:%M %1%2')

def isodatesec(text):
    return util.datestr(text, '%Y-%m-%d %H:%M:%S %1%2')

def indent(text, prefix):
    '''indent each non-empty line of text after first with prefix.'''
    lines = text.splitlines()
    num_lines = len(lines)
    endswithnewline = text[-1:] == '\n'
    def indenter():
        for i in xrange(num_lines):
            l = lines[i]
            if i and l.strip():
                yield prefix
            yield l
            if i < num_lines - 1 or endswithnewline:
                yield '\n'
    return "".join(indenter())

def json(obj):
    if obj is None or obj is False or obj is True:
        return {None: 'null', False: 'false', True: 'true'}[obj]
    elif isinstance(obj, int) or isinstance(obj, float):
        return str(obj)
    elif isinstance(obj, str):
        u = unicode(obj, encoding.encoding, 'replace')
        return '"%s"' % jsonescape(u)
    elif isinstance(obj, unicode):
        return '"%s"' % jsonescape(obj)
    elif hasattr(obj, 'keys'):
        out = []
        for k, v in obj.iteritems():
            s = '%s: %s' % (json(k), json(v))
            out.append(s)
        return '{' + ', '.join(out) + '}'
    elif hasattr(obj, '__iter__'):
        out = []
        for i in obj:
            out.append(json(i))
        return '[' + ', '.join(out) + ']'
    else:
        raise TypeError('cannot encode type %s' % obj.__class__.__name__)

def _uescape(c):
    if ord(c) < 0x80:
        return c
    else:
        return '\\u%04x' % ord(c)

_escapes = [
    ('\\', '\\\\'), ('"', '\\"'), ('\t', '\\t'), ('\n', '\\n'),
    ('\r', '\\r'), ('\f', '\\f'), ('\b', '\\b'),
]

def jsonescape(s):
    for k, v in _escapes:
        s = s.replace(k, v)
    return ''.join(_uescape(c) for c in s)

def localdate(text):
    return (text[0], util.makedate()[1])

def nonempty(str):
    return str or "(none)"

def obfuscate(text):
    text = unicode(text, encoding.encoding, 'replace')
    return ''.join(['&#%d;' % ord(c) for c in text])

def permissions(flags):
    if "l" in flags:
        return "lrwxrwxrwx"
    if "x" in flags:
        return "-rwxr-xr-x"
    return "-rw-r--r--"

def person(author):
    '''get name of author, or else username.'''
    if not '@' in author:
        return author
    f = author.find('<')
    if f == -1:
        return util.shortuser(author)
    return author[:f].rstrip()

def rfc3339date(text):
    return util.datestr(text, "%Y-%m-%dT%H:%M:%S%1:%2")

def rfc822date(text):
    return util.datestr(text, "%a, %d %b %Y %H:%M:%S %1%2")

def short(text):
    return text[:12]

def shortdate(text):
    return util.shortdate(text)

def stringescape(text):
    return text.encode('string_escape')

def stringify(thing):
    '''turn nested template iterator into string.'''
    if hasattr(thing, '__iter__') and not isinstance(thing, str):
        return "".join([stringify(t) for t in thing if t is not None])
    return str(thing)

def strip(text):
    return text.strip()

def stripdir(text):
    '''Treat the text as path and strip a directory level, if possible.'''
    dir = os.path.dirname(text)
    if dir == "":
        return os.path.basename(text)
    else:
        return dir

def tabindent(text):
    return indent(text, '\t')

def urlescape(text):
    return urllib.quote(text)

def userfilter(text):
    return util.shortuser(text)

def xmlescape(text):
    text = (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;')) # &apos; invalid in HTML
    return re.sub('[\x00-\x08\x0B\x0C\x0E-\x1F]', ' ', text)

filters = {
    "addbreaks": addbreaks,
    "age": age,
    "basename": basename,
    "date": datefilter,
    "domain": domain,
    "email": email,
    "escape": escape,
    "fill68": fill68,
    "fill76": fill76,
    "firstline": firstline,
    "hex": hexfilter,
    "hgdate": hgdate,
    "isodate": isodate,
    "isodatesec": isodatesec,
    "json": json,
    "jsonescape": jsonescape,
    "localdate": localdate,
    "nonempty": nonempty,
    "obfuscate": obfuscate,
    "permissions": permissions,
    "person": person,
    "rfc3339date": rfc3339date,
    "rfc822date": rfc822date,
    "short": short,
    "shortdate": shortdate,
    "stringescape": stringescape,
    "stringify": stringify,
    "strip": strip,
    "stripdir": stripdir,
    "tabindent": tabindent,
    "urlescape": urlescape,
    "user": userfilter,
    "xmlescape": xmlescape,
}
