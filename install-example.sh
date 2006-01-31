#!/bin/sh

# A typical setup.

groupadd lastfm
useradd -g lastfm lastfm

for d in /var/log /var/run /var/cache; do
    mkdir $d/lastfm
    chown lastfm:lastfm $d/lastfm
    chmod 775 $d/lastfm
done
