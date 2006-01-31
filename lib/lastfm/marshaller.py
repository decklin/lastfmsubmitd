import time
import lastfm

def parse_length(length):
    # Just think, if we had Python 2.4, this could all be one line.
    parts = [int(p) for p in length.split(':')]; parts.reverse()
    return sum([p * u for p, u in zip(parts, (1, 60, 3600, 86400))])

def dump(song):
    doc = ['---']
    for k, v in song.items():
        if k in ('time'):
            v = '!timestamp %s' % time.strftime(lastfm.TIME_FMT, v)
        elif k in ('length'):
            v = '%d:%02d' % divmod(v, 60)
        else:
            v = unicode(v).encode('utf-8')
        doc.append(': '.join((k, v)))
    return '\n'.join(doc)

def dump_documents(docs, out):
    out.write('\n'.join([dump(d) for d in docs]))

def load(doc):
    song = {}
    for line in doc.split('\n'):
        try:
            k, v = line.split(': ', 1)
            if k in ('time'):
                v = time.strptime(v, '!timestamp %s' % lastfm.TIME_FMT)
            elif k in ('length'):
                v = parse_length(v)
            else:
                v = v.decode('utf-8')
            song[k] = v
        except ValueError:
            pass
    return song

def load_documents(docs):
    for doc in map(str.strip, docs.split('---\n')):
        if doc:
            yield load(doc)
