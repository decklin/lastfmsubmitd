__all__ = ['marshaller', 'mbutil']

import os
import sys
import logging
import tempfile

import lastfm.marshaller
from lastfm.config import LOG_PATH, SPOOL_PATH # XXX

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

def logger(name='unknown', path=LOG_PATH, debug=False, stderr=False):
    """Returns a logging object that will write to the lastfm system log, or
    another file specified by ``path``. If ``debug`` is true, the logging
    object's level will be set to DEBUG. If ``stderr`` is true, the object
    will also print all messages to stderr. ``name`` should be set to the name
    of the program opening the log."""

    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(level)

    try:
        oldmask = os.umask(002)
        filefmt = '%(asctime)s %(name)s[%(process)s] %(levelname)s: %(message)s'
        filehandler = logging.FileHandler(path)
        filehandler.setLevel(level)
        filehandler.setFormatter(logging.Formatter(filefmt))
        logger.addHandler(filehandler)
        os.umask(oldmask)
    except IOError:
        # If we can't log it here, better do it somewhere...
        stderr = True

    if stderr:
        stderrfmt = '%(asctime)s %(levelname)s: %(message)s'
        stderrhandler = logging.StreamHandler(sys.stderr)
        stderrhandler.setLevel(level)
        stderrhandler.setFormatter(logging.Formatter(stderrfmt))
        logger.addHandler(stderrhandler)

    return logger

def submit(subs, path=SPOOL_PATH):
    """Creates a uniquely named file in the spool directory containing the
    given submissions. ``subs`` should be a list of dictionaries, each
    containing the keys ``artist``, ``title``, ``length``, and ``time`` (and
    optionally ``album`` and ``mbid``). ``artist``, ``title``, ``album``, and
    ``mbid`` are strings, ``length`` is an integer, and ``time`` is a UTC time
    tuple."""

    fd, path = tempfile.mkstemp(dir=path)
    data = os.fdopen(fd, 'w+')
    lastfm.marshaller.dump_documents(subs, data)
    os.chmod(path, 0664)
    return path

def repr(song):
    """Returns a short text representation of a song dictionary, suitable for
    logging."""
    try:
        name = '%s - %s' % (song['artist'], song['title'])
    except KeyError:
        name = 'None'
    try:
        time = '[%d:%02d]' % divmod(song['length'], 60)
    except KeyError:
        time = '[None]'

    return '%s %s' % (name, time)
