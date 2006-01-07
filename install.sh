#!/bin/sh

# If you're installing by hand, run this as root, and run the daemons from the
# following user accounts.

./setup.py install

groupadd lastfm
useradd -g lastfm lastfmsubmitd
useradd -g lastfm lastmp

RUN=/var/run/lastfmsubmitd
CACHE=/var/cache/lastfmsubmitd
LOG=/var/log/lastfm.log

touch $LOG
chown 664 $LOG
chgrp lastfm $LOG

mkdir $RUN
chgrp lastfm $RUN
chmod 775 $RUN

mkfifo $RUN/fifo
chgrp lastfm $RUN/fifo
chmod 660 $RUN/fifo

mkdir $CACHE
chgrp lastfm $CACHE
chmod 775 $CACHE

touch $CACHE/subs
chgrp lastfm $CACHE/subs
chmod 660 $CACHE/subs
