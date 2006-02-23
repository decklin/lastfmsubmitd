import fcntl

# XXX: perhaps a Reader class here as well

class Writer:
    def __init__(self, filename, log):
        self.outfile = filename
        self.lockfile = filename + '.lock'
        self.log = log

        self.lock = file(self.lockfile, 'w')
        self.log.debug('Requesting lock on %s' % self.lockfile)
        fcntl.flock(self.lock, fcntl.LOCK_EX)

        # This will block until we have a reader (which means more writers
        # may pile up, but that's OK, because they should get the lock in
        # the order they requested them).
        self.out = file(self.outfile, 'w')

    def __del__(self):
        # We must flush and get out of the way of the next writer before
        # releasing the lock.
        self.out.close()
        fcntl.flock(self.lock, fcntl.LOCK_UN)
        self.lock.close()
        self.log.debug('Released lock')

    def write(self, s):
        self.out.write(s)
