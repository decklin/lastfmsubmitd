__all__ = ['config', 'client', 'marshaller']

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

def repr(song):
    """A short text representation of a song dict, suitable for logging."""

    try:
        name = '%s - %s' % (song['artist'], song['title'])
    except KeyError:
        name = 'unknown'
    try:
        time = '%d:%02d' % divmod(song['length'], 60)
    except KeyError:
        time = 'unknown'

    return '%s [%s]' % (name, time)
