import os
import stat
import select
import fcntl

import lastfm

class Reader:
    """Reads one writer at a time from our fifo, making sure it actually
    exists first."""

    def __init__(self, log, f):
        self.log = log
        self.f = f
        try:
            if stat.S_ISFIFO(os.stat(self.f).st_mode): return
        except OSError, e:
            try:
                os.mkfifo(self.f)
            except OSError, e:
                self.log.error('Failed to create %s: %s' % (f, e))
                raise

    def select(self, timeout):
        fd = os.open(self.f, os.O_NONBLOCK)
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

    def __init__(self, log, f, l):
        self.log = log
        self.outfile = f
        self.lock = l

        if self.lock:
            self.log.debug('Requesting lock on %s' % self.lock)
            self.lock = file(self.lock, 'w')

        # If there is a pileup, locks will be requested in order.
        fcntl.flock(self.lock, fcntl.LOCK_EX)
        # This will also block, until we have a reader.
        self.log.debug('Opening %s' % self.outfile)
        self.out = file(self.outfile, 'w')

    def __del__(self):
        if self.lock:
            # We must flush and get out of the way first.
            self.out.close()
            fcntl.flock(self.lock, fcntl.LOCK_UN)
            self.lock.close()
            self.log.debug('Released lock')

    def write(self, s):
        self.out.write(s)
