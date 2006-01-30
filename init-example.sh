#!/bin/sh

export LASTFM_USER=username
export LASTFM_PASSWORD=secret

case $1 in
    start)
        lastfmsubmitd &
        lastmp &
        ;;
    stop)
        killall lastfmsubmitd
        killall lastmp
        ;;
    restart)
        $0 stop
        $0 start
        ;;
esac
