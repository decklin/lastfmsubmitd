__all__ = ['logger', 'marshaller', 'queue']

# Shared log.
LOG = '/var/log/lastfm/lastfm.log'

# Our IPC mechanisms.
PID_DIR = '/var/run/lastfm'
SPOOL_DIR = '/var/spool/lastfm'

# XXX: put all this in lastfm.protocol?
TIME_FMT = '%Y-%m-%d %H:%M:%S'

# A song under this length will not be submitted.
MIN_LEN = 30

# A song over this length will not be submitted.
MAX_LEN = 3600

# A song will be submitted if it reaches this percentage...
SUB_PERCENT = 0.5

# ...or if it has been played for this many seconds.
SUB_SECONDS = 240
