import os
import tempfile

import lastfm

class Spool:
    """Represents uncommitted submissions on disk. May be extended by writing
    a new file in the spool directory."""

    def __init__(self, log):
        self.log = log
        self.files = []
        self.subs = []

    def poll(self):
        n = 0
        for f in os.listdir(lastfm.SPOOL_DIR):
            path = os.path.join(lastfm.SPOOL_DIR, f)
            if path not in self.files:
                self.files.append(path)
                data = file(path)
                for doc in lastfm.marshaller.load_documents(data.read()):
                    try:
                        self.subs.append(doc)
                        n += 1
                    except ValueError, e:
                        self.log.warning('Invalid data, ignoring: %s' % e)
        return n

    def sync(self):
        newfile = write(self.subs)
        for f in self.files:
            os.unlink(f)
        self.files = [newfile]

def write(subs):
    """Creates a uniquely named file in the spool directory containing the
    given subs."""

    fd, path = tempfile.mkstemp(dir=lastfm.SPOOL_DIR)
    os.close(fd)

    data = file(path, 'w+')
    lastfm.marshaller.dump_documents(subs, data)
    return path
