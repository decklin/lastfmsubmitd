import os
import stat
import select
import fcntl

class Reader:
    """Reads one writer at a time from our fifo, making sure it actually
    exists first."""

    def __init__(self, log, fname):
        self.log = log
        self.fname = fname
        try:
            if stat.S_ISFIFO(os.stat(self.fname).st_mode): return
        except OSError, e:
            try:
                os.mkfifo(self.fname)
            except OSError, e:
                self.log.error('Failed to create %s: %s' % (f, e))
                raise

    def select(self, timeout):
        fd = os.open(self.fname, os.O_NONBLOCK)
        rx, wx, ex = select.select([fd], [], [], timeout)
        data = []
        if fd in rx:
            while True:
                chunk = os.read(fd, 4096)
                if chunk:
                    self.log.debug('Read %d bytes' % len(chunk))
                    data.append(chunk)
                    rx, wx, ex = select.select([fd], [], [], timeout)
                else:
                    break
        os.close(fd)
        return ''.join(data)

class Writer:
    """Writes data to the fifo, or just a plain file."""

    def __init__(self, log, fname, lockname):
        self.log = log
        self.fname = fname
        self.lockname = lockname
        self.f = None
        self.lock = None

        if self.lockname:
            self.log.debug('Requesting lock on %s' % self.lockname)
            self.lock = file(self.lockname, 'w')
            # If there is a pileup, locks will be requested in order.
            fcntl.flock(self.lock, fcntl.LOCK_EX)

        # This will also block, until we have a reader.
        self.log.debug('Opening %s' % self.fname)
        self.f = file(self.fname, 'w')

    def __del__(self):
        # We must flush and get out of the way first.
        if self.f:
            self.f.close()
        if self.lock:
            fcntl.flock(self.lock, fcntl.LOCK_UN)
            self.lock.close()
            self.log.debug('Released lock')

    def write(self, s):
        self.f.write(s)
