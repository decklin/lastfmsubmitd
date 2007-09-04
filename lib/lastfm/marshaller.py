import time
import lastfm

def guess_enc(s, enc):
    try: return s.decode(enc)
    except UnicodeDecodeError: pass
    try: return s.decode('utf-8')
    except UnicodeDecodeError: pass
    try: return s.decode('latin-1') # Cultural imperialism FTW. Sigh.
    except UnicodeDecodeError:
        return s.decode('ascii', 'replace')

def parse_length(length):
    # Just think, if we had Python 2.4, this could all be one line.
    parts = [int(p) for p in length.split(':')]; parts.reverse()
    return sum([p * u for p, u in zip(parts, (1, 60, 3600, 86400))])

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
            if v.startswith('!timestamp '):
                v = time.strptime(v[11:], lastfm.TIME_FMT)
            else:
                try:
                    v = parse_length(v)
                except ValueError:
                    v = parse_string(v)
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
