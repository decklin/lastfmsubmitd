import os
import sys
import logging

def getlog(name, logfile, debug=False, stderr=False):
    if debug: level = logging.DEBUG
    else: level = logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(level)

    os.umask(002)

    filefmt = '%(asctime)s %(name)s[%(process)s] %(levelname)s: %(message)s'
    filehandler = logging.FileHandler(logfile)
    filehandler.setLevel(level)
    filehandler.setFormatter(logging.Formatter(filefmt))
    logger.addHandler(filehandler)

    if stderr:
        stderrfmt = '%(levelname)s: %(message)s'
        stderrhandler = logging.StreamHandler(sys.stderr)
        stderrhandler.setLevel(level)
        stderrhandler.setFormatter(logging.Formatter(stderrfmt))
        logger.addHandler(stderrhandler)

    return logger

def short_name(track):
    return '%s - %s [%d:%02d]' % ((track['artist'], track['title']) +
        divmod(track['length'], 60))
