import os
import sys
import logging
import tempfile

import lastfm.config

SLEEP_TIME = 5
PIDFILE_BASE = '/var/run/lastfm'

class Client:
    """Something that uses the lastfmsubmitd spool. Has a configuration
    (lastfm.config.Config), and can store submissions or open a log in
    the places defined by it. The word "client" does not imply anything
    about the program's function; all daemons are also clients in the
    sense that they use the spool and log through this interface."""

    def __init__(self, conf=None, path=None):
        """Create something that can hand submissions over to a running
        lastfmsubmitd; by default, look for the one defined by the
        standard config, but if ``conf`` is or ``path`` is supplied,
        talk to that one."""
        if conf:
            self.conf = conf
        elif path:
            self.conf = lastfm.config.Config(path=path)
        else:
            self.conf = lastfm.config.Config(search='lastfmsubmitd')

    def open_log(self, name, debug=False, stderr=False):
        """Returns a logging object that will write to the client's log.
        If ``debug`` is true, the client's debug setting will be overridden
        and the logging object's level will be set to DEBUG. If
        ``stderr`` is true, the object will also print all messages
        to stderr. ``name`` should be set to the name of the program
        opening the log."""

        if debug or self.conf.debug:
            level = logging.DEBUG
        else:
            level = logging.INFO

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        try:
            oldmask = os.umask(002)
            filefmt = \
                '%(asctime)s %(name)s[%(process)s] %(levelname)s: %(message)s'
            filehandler = logging.FileHandler(self.conf.log_path)
            filehandler.setLevel(level)
            filehandler.setFormatter(logging.Formatter(filefmt))
            self.logger.addHandler(filehandler)
            os.umask(oldmask)
        except IOError:
            # If we can't log it here, better do it somewhere...
            stderr = True

        if stderr:
            stderrfmt = '%(asctime)s %(levelname)s: %(message)s'
            stderrhandler = logging.StreamHandler(sys.stderr)
            stderrhandler.setLevel(level)
            stderrhandler.setFormatter(logging.Formatter(stderrfmt))
            self.logger.addHandler(stderrhandler)

        return self.logger

    def submit_many(self, songs):
        """Creates a uniquely named file in the spool directory
        containing the given submission. ``subs`` should be a dict
        containing the keys ``artist``, ``title``, ``length``, and
        ``time`` (and optionally ``album`` and ``mbid``). ``artist``,
        ``title``, ``album``, and ``mbid`` are strings, ``length`` is an
        integer, and ``time`` is a UTC time tuple."""

        fd, path = tempfile.mkstemp(dir=self.conf.spool_path)
        spool_file = os.fdopen(fd, 'w+')
        lastfm.marshaller.dump_documents(songs, spool_file)
        os.chmod(path, 0664)

        return path

    def submit(self, song):
        return self.submit_many([song])

class Daemon(Client):
    """A Client which runs in the background, and therefore needs additional
    configuration options and the ability to use a pidfile. The name used for
    both pidfile and logging is unified."""

    def __init__(self, name, conf=None, path=None):
        Client.__init__(self, conf, path)
        self.name = name
        self.conf.sleep_time = float(self.conf.cp.get('daemon', 'sleep_time',
            SLEEP_TIME))
        self.conf.pidfile_path = self.conf.cp.get('paths', 'pidfile',
            '%s/%s.pid' % (PIDFILE_BASE, self.name))

    def open_log(self, debug=False, stderr=False):
        return Client.open_log(self, self.name, debug, stderr)

    def write_pidfile(self):
        try:
            pidfile = open(self.conf.pidfile_path, 'w')
            print >>pidfile, os.getpid()
            pidfile.close()
        except IOError, e:
            print >>sys.stderr, "can't open pidfile: %s" % e
            self.conf.pidfile_path = None

    def remove_pidfile(self):
        if self.conf.pidfile_path:
            os.remove(self.conf.pidfile_path)
