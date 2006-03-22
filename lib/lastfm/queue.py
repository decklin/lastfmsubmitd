import os
import stat
import select
import fcntl

import lastfm

class Reader:
    """Reads one writer at a time from our fifo, making sure it actually
    exists first."""

    def __init__(self, log):
        self.log = log
        try:
            assert stat.S_ISFIFO(os.stat(lastfm.FIFO).st_mode)
        except OSError, AssertionError:
            self.log.debug('Creating %s' % self.fifoname)
            os.mkfifo(lastfm.FIFO)

    def select(self, timeout):
        fd = os.open(lastfm.FIFO, os.O_NONBLOCK)
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

    def __init__(self, log, f, uselock):
        self.log = log
        self.outfile = f
        self.uselock = uselock

        if self.uselock:
            self.log.debug('Requesting lock on %s' % lastfm.LOCK)
            self.lock = file(lastfm.LOCK, 'w')

        # If there is a pileup, locks will be requested in order.
        fcntl.flock(self.lock, fcntl.LOCK_EX)
        # This will also block, until we have a reader.
        self.log.debug('Opening %s' % self.outfile)
        self.out = file(self.outfile, 'w')

    def __del__(self):
        if self.uselock:
            # We must flush and get out of the way first.
            self.out.close()

            fcntl.flock(self.lock, fcntl.LOCK_UN)
            self.lock.close()
            self.log.debug('Released lock')

    def write(self, s):
        self.out.write(s)
