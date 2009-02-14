import os
import ConfigParser

class DefaultPath:
    """The default paths we want depend on whether this is a "system"
    instance (/etc, /var), or running under a normal user account ($HOME).
    So that we can reuse this code for other daemons, the paths are
    specified as lambda expressions that take the current program's name.
    They may or may not use this parameter (i.e., lastfmsubmitd itself and a
    client using this interface will have separate log files, but obviously
    must share the same spool directory). The "user" version of a path
    should contain ~, which this class will expand. Creates a callable that
    takes whether or not we want the "system" version, and the name."""

    def __init__(self, sys, user):
        self.funcs = {True: sys, False: lambda n: os.path.expanduser(user(n))}
    def __call__(self, use_sys_path, name):
        return self.funcs[use_sys_path](name)

CONF = DefaultPath(lambda n: '/etc/%s.conf' % n,
                   lambda n: '~/.%s/conf' % n)
LOG = DefaultPath(lambda n: '/var/log/lastfm/%s.log' % n,
                  lambda n: '~/.%s/log' % n)
SPOOL = DefaultPath(lambda n: '/var/spool/lastfm',
                    lambda n: '~/.lastfmsubmitd/spool')

class SaneConfParser(ConfigParser.RawConfigParser):
    def get(self, section, option, default):
        try:
            return ConfigParser.RawConfigParser.get(self, section, option)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return default

class Config:
    """The minimum configuration needed by any program that communicates
    through the lastfmsubmitd protocol: where to put the serialized
    submissions and where to log. If the provided path or ~/.NAME/config is
    found, the "user" defaults are used. Otherwise, /etc/NAME.conf is read,
    and the "system" defaults are used."""

    def __init__(self, path='', name='lastfmsubmitd'):
        self.cp = SaneConfParser()
        self.name = name
        self.use_sys_path = False
        if not self.cp.read([self.get_path(CONF), path]):
            self.use_sys_path = True
            self.cp.read([self.get_path(CONF)])

        self.log_path = self.cp.get('paths', 'log', self.get_path(LOG))
        self.spool_path = self.cp.get('paths', 'spool', self.get_path(SPOOL))
        self.debug = self.cp.get('general', 'debug', False)

    def get_path(self, f):
        return f(self.use_sys_path, self.name)
