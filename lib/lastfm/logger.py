import os
import logging

LASTFM_LOG = '/var/log/lastfm.log'

def getlog(self, name, logfile=LASTFM_LOG, debug=False):
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    log = logging.getLogger(name)
    log.setLevel(level)

    format = logging.Formatter(
        '%(asctime)s %(name)s[%(process)s] %(levelname)s: %(message)s')

    logfile = logging.FileHandler(logfile)
    logfile.setLevel(level)
    logfile.setFormatter(format)
    log.addHandler(logfile)

    return log

def short_name(track):
    return '%s - %s [%d:%02d]' % ((track['artist'], track['title']) +
        divmod(track['length'], 60))
