import os
import ConfigParser

# This module only reads generic settings applicable to any daemon or other
# process that wants to use the spool/log, so you'll probably want to subclass
# Config. Anything that uses the public interfaces in the lastfm module
# doesn't need to worry about it. I am, however, reusing all this in LastMP,
# as it is somewhat more tightly integrated. Really, it's an evil hack.

SYS_CONF = '/etc/%s.conf'
USER_CONF = os.path.expanduser('~/.%s.conf')

# Defaults

SLEEP_TIME = 5
DEBUG = False

LOG_PATH = '/var/log/lastfm/lastfm.log'
SPOOL_PATH = '/var/spool/lastfm'
PIDFILE_BASE = '/var/run/lastfm'

class NoConfError(Exception): pass

class Config:
    def __init__(self, name):
        self.name = name
        self.cp = ConfigParser.ConfigParser()

        for path in (USER_CONF % self.name, SYS_CONF % self.name):
            try:
                fp = file(path)
                self.cp.readfp(fp)
                break
            except IOError:
                pass
        else:
            raise NoConfError

        try:
            self.sleep_time = self.cp.get('daemon', 'sleep_time')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            self.sleep_time = SLEEP_TIME
        try:
            self.debug = self.cp.get('daemon', 'debug')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            self.debug = DEBUG
        try:
            self.log_path = self.cp.get('paths', 'log')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            self.log_path = LOG_PATH
        try:
            self.pidfile_path = self.cp.get('paths', 'pidfile')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            self.pidfile_path = '%s/%s.pid' % (PIDFILE_BASE, self.name)
        try:
            self.spool_path = self.cp.get('paths', 'spool')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            self.spool_path = SPOOL_PATH

    def write_pidfile(self):
        try:
            pidfile = open(self.pidfile_path, 'w')
            print >>pidfile, os.getpid()
            pidfile.close()
        except IOError:
            # XXX: log this somehow
            self.pidfile_path = None

    def remove_pidfile(self):
        if self.pidfile_path:
            os.remove(self.pidfile_path)
