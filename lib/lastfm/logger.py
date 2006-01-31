import os
import logging

def getlog(name, logfile, debug=False):
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        '%(asctime)s %(name)s[%(process)s] %(levelname)s: %(message)s')

    os.umask(002)
    loghandler = logging.FileHandler(logfile)
    loghandler.setLevel(level)
    loghandler.setFormatter(formatter)
    logger.addHandler(loghandler)

    return logger

def short_name(track):
    return '%s - %s [%d:%02d]' % ((track['artist'], track['title']) +
        divmod(track['length'], 60))
