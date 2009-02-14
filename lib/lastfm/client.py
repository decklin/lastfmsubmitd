import os
import sys
import logging
import tempfile

import lastfm.config
import lastfm.marshaller

SLEEP = 5
PID = lastfm.config.DefaultPath(lambda n: '/var/run/lastfm/%s.pid' % n,
                                lambda n: '~/.%s/pid' % n)

class Client:
    """Something that uses the lastfmsubmitd spool. Has a configuration
    (lastfm.config.Config), a name (mostly for logging purposes), and can
    write submissions. The word "client" does not imply anything about the
    program's function; all daemons are also clients in the sense that they
    use the spool and log through this interface."""

    def __init__(self, name, conf=None, log=True):
        """Create something that can hand submissions over to a running
        lastfmsubmitd; by default, look for the one defined by the standard
        config, but if ``conf`` is supplied, talk to that one."""

        self.name = name
        self.conf = conf or lastfm.config.Config()

    def open_log(self, debug=False, stderr=False):
        """Returns a logging object that will write to the client's log. If
        ``debug`` is true, the client's debug setting will be overridden and
        the logging object's level will be set to DEBUG. If ``stderr`` is
        true, the object will also print all messages to stderr."""

        if debug or self.conf.debug:
            level = logging.DEBUG
        else:
            level = logging.INFO

        self.log = logging.getLogger(self.name)
        self.log.setLevel(level)

        try:
            filefmt = \
                '%(asctime)s %(name)s[%(process)s] %(levelname)s: %(message)s'
            oldmask = os.umask(002)
            filehandler = logging.FileHandler(self.conf.log_path)
            filehandler.setLevel(level)
            filehandler.setFormatter(logging.Formatter(filefmt))
            self.log.addHandler(filehandler)
            os.umask(oldmask)
        except IOError:
            stderr = True

        if stderr:
            stderrfmt = '%(asctime)s %(levelname)s: %(message)s'
            stderrhandler = logging.StreamHandler(sys.stderr)
            stderrhandler.setLevel(level)
            stderrhandler.setFormatter(logging.Formatter(stderrfmt))
            self.log.addHandler(stderrhandler)

    def submit_many(self, songs):
        """Creates a uniquely named file in the spool directory containing
        the given submission. ``subs`` should be a dict containing the keys
        ``artist``, ``title``, ``length``, and ``time`` (and optionally
        ``album`` and ``mbid``). ``artist``, ``title``, ``album``, and
        ``mbid`` are strings, ``length`` is an integer, and ``time`` is a UTC
        time tuple."""

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

    def __init__(self, name, conf=None, log=True):
        Client.__init__(self, name, conf, log)
        self.conf.sleep_time = float(self.conf.cp.get('daemon', 'sleep_time',
            SLEEP))
        self.conf.pidfile_path = self.conf.cp.get('paths', 'pidfile',
            self.conf.get_path(PID))

    def fork(self):
        try:
            pid = os.fork()
            if pid:
                sys.exit(0)
        except OSError, e:
            print >>sys.stderr, "%s: can't fork: %s" % (self.name, e)
            sys.exit(1)

    def daemonize(self, fork=True):
        if fork:
            self.fork()
            if os.geteuid() == 0:
                os.setsid()
                self.fork()

            os.chdir('/')
            os.umask(0)

            devnull = os.open('/dev/null', os.O_RDWR)
            os.dup2(devnull, sys.stdin.fileno())
            os.dup2(devnull, sys.stdout.fileno())
            os.dup2(devnull, sys.stderr.fileno())
            os.close(devnull)

        if not os.path.exists(self.conf.spool_path):
            os.mkdir(self.conf.spool_path)

        try:
            pidfile = open(self.conf.pidfile_path, 'w')
            print >>pidfile, os.getpid()
            pidfile.close()
        except IOError, e:
            print >>sys.stderr, "can't open pidfile: %s" % e
            self.conf.pidfile_path = None

    def cleanup(self):
        if self.conf.pidfile_path:
            os.remove(self.conf.pidfile_path)
