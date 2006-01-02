import fcntl

class Writer:

    def __init__(self, filename, log):
        self.outfile = filename
        self.lockfile = filename + ".lock"
        self.log = log

    def write(self, subs):
        lock = file(self.lockfile, 'w')
        self.log.debug("Requesting lock on %s" % self.lockfile)
        fcntl.flock(lock, fcntl.LOCK_EX)

        self.log.debug("We have lock, writing to %s" % self.outfile)
        # This will block until we have a reader (which means more writers
        # may pile up, but that's OK, because they should get the lock in
        # the order they requested them)
        out = file(self.outfile, 'w')
        for sub in subs:
            print >>out, sub
            self.log.info("Sent %s to submit daemon", sub.shortname())
        # And then we must flush and get out of the way of the next writer
        # before releasing the lock
        out.close()

        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()
        self.log.debug("Released lock")
