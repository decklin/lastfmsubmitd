import time
import re
import lastfm

# Temporary YAML hack
TIME_RE = re.compile("""
    (\d{4})-(\d{1,2})-(\d{1,2}) # (ymd)
    (?:[Tt]|[ \t]+)
    (\d{1,2}?):(\d{2}):(\d{2}) # (hms)
    (?:\.\d*)? # (frac)
    [ \t]*
    (Z|[-+]\d{1,2}(?::\d{1,2})?)? # (tz)""", re.X)

def guess_enc(s, enc):
    try: return s.decode(enc)
    except UnicodeDecodeError: pass
    try: return s.decode('utf-8')
    except UnicodeDecodeError: pass
    try: return s.decode('latin-1') # Cultural imperialism FTW. Sigh.
    except UnicodeDecodeError:
        return s.decode('ascii', 'replace')

def parse_length(s):
    UNITS = (1, 60, 3600, 86400)
    if s.startswith('-'):
        sign = -1
        s = s[1:]
    else:
        sign = 1
    parts = [sign * int(p) for p in s.split(':')]
    return sum([p * u for p, u in zip(reversed(parts), UNITS)])

def parse_tz(tz):
    if tz is None or tz == 'Z':
        return 0
    else:
        return parse_length(tz) * 60

def parse_time(spec):
    match = TIME_RE.match(spec)
    if match:
        y, m, d, h, m, s, tz = match.groups()
        t = [int(c) for c in (y, m, d, h, m, s, 0, 0, 0)]
        utc = time.mktime(t) - time.timezone
        return time.gmtime(utc - parse_tz(tz))
    else:
        raise ValueError('Not a time spec')

def parse_string(s):
    s = s.decode('utf-8')
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
        s = s.replace('\\\\', '\\')
        s = s.replace('\\"', '"')
    return s

def dump(song):
    doc = ['---']
    for k, v in song.iteritems():
        try:
            if k == 'length':
                v = '%d:%02d' % divmod(v, 60)
            else:
                v = '%d' % v
        except TypeError:
            try:
                v = '!timestamp %s' % time.strftime(lastfm.TIME_FMT, v)
            except TypeError:
                v = '"%s"' % unicode(v).replace('"', '\\"').encode('utf-8')
        doc.append(': '.join([k, v]))
    return '\n'.join(doc)

def dump_documents(docs, out):
    print >>out, '\n'.join([dump(d) for d in docs])

def load(doc):
    song = {}
    for line in doc.split('\n'):
        if line:
            k, v = line.split(': ', 1)
            # this is to work around a design failure in 1.0 and earlier. the
            # syntax is not actually valid YAML at all. just strip it.
            if v.startswith('!timestamp '):
                v = v[11:]
            for parse in (parse_length, parse_time, parse_string):
                try:
                    v = parse(v)
                    break
                except ValueError:
                    pass
            song[k] = v
    return song

def load_documents(stream):
    docs = []
    for doc in stream.read().split('---\n'):
        doc = doc.strip()
        if doc:
            try:
                docs.append(load(doc))
            except ValueError:
                pass
    return docs
