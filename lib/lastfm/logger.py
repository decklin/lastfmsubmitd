import logging

LASTFM_LOG = '/var/log/lastfm.log'

def create_log(name, debug=False):

    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    log = logging.getLogger(name)
    log.setLevel(level)

    format = logging.Formatter(
        '%(asctime)s %(name)s[%(process)s] %(levelname)s: %(message)s')

    logfile = logging.FileHandler(LASTFM_LOG)
    logfile.setLevel(level)
    logfile.setFormatter(format)
    log.addHandler(logfile)

    return log
