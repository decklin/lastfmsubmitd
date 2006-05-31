import os
import sys
import logging

import lastfm

def getlog(name, debug=False, stderr=False):
    if debug: level = logging.DEBUG
    else: level = logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(level)

    filefmt = '%(asctime)s %(name)s[%(process)s] %(levelname)s: %(message)s'
    filehandler = logging.FileHandler(lastfm.LOG)
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

# XXX: This really shouldn't be here. It's a data thing, not a log thing.
def repr(song):
    try:
        name = '%s - %s' % (song['artist'], song['title'])
    except KeyError:
        name = 'None'
    try:
        time = '[%d:%02d]' % divmod(song['length'], 60)
    except KeyError:
        time = '[None]'

    return '%s %s' % (name, time)
