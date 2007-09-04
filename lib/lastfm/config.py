import os
import ConfigParser

SPOOL_PATH = '/var/spool/lastfm'
LOG_PATH = '/var/log/lastfm/lastfm.log'

SYS_CONF = '/etc/%s.conf'
USER_CONF = os.path.expanduser('~/.%s.conf')

class SaneConfParser(ConfigParser.RawConfigParser):
    def get(self, section, option, default):
        try:
            return ConfigParser.RawConfigParser.get(self, section, option)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return default

class Config:
    """The minimum configuration needed by any program that communicates
    through the lastfmsubmitd "protocol": where to put the serialized
    submissions and where to log. Since most everything can make use of
    it, a debug flag is also provided. A standard for configuration file
    locations is defined (specify ``search`` to look for /etc/foo.conf
    or ~/.foo.conf, with the latter overriding), but arbitrary locations
    may be specified using ``path``. If no configuration files are
    provided or readable, the default values of SPOOL_PATH and LOG_PATH
    are used."""

    def __init__(self, search=None, path=None):
        self.cp = SaneConfParser()
        if search:
            self.cp.read([SYS_CONF % search, USER_CONF % search])
        if path:
            self.cp.read([path])

        self.spool_path = self.cp.get('paths', 'spool', SPOOL_PATH)
        self.log_path = self.cp.get('paths', 'log', LOG_PATH)
        self.debug = self.cp.get('general', 'debug', False)
