__all__ = ['marshaller', 'mbutil']

import os
import sys
import logging
import tempfile

import lastfm.marshaller

# Shared stuff.
LOG = '/var/log/lastfm/lastfm.log'
PID_DIR = '/var/run/lastfm'
SPOOL_DIR = '/var/spool/lastfm'

# All times look like this.
TIME_FMT = '%Y-%m-%d %H:%M:%S'

# A song under this length will not be submitted.
MIN_LEN = 30

# A song over this length will not be submitted.
MAX_LEN = 3600

# A song will be submitted if it reaches this percentage...
SUB_PERCENT = 0.5

# ...or if it has been played for this many seconds.
SUB_SECONDS = 240

def logger(name, debug=False, stderr=False):
    if debug: level = logging.DEBUG
    else: level = logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(level)

    filefmt = '%(asctime)s %(name)s[%(process)s] %(levelname)s: %(message)s'
    filehandler = logging.FileHandler(LOG)
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

def submit(subs):
    """Creates a uniquely named file in the spool directory containing the
    given subs."""

    fd, path = tempfile.mkstemp(dir=SPOOL_DIR)
    os.close(fd)

    data = file(path, 'w+')
    lastfm.marshaller.dump_documents(subs, data)
    return path

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
