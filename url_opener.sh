#!/bin/bash

# For opening URLs sent from WeeChat on my vps using urlgrab.py
# /set urlgrab.default.localcmd "/home/nick/weechat/work/open_url.sh '%s'"
# open_url.sh just does echo '$1' | nc localhost 6666

autossh -M10666 -N -f -R 6666:localhost:6666 nick@nijotz.com &

while true; do
    echo "running netcat to receive url"
    url=$(nc -l -p 6666)
    if [ ! -z "$url" ]; then
        echo "url -> $url"
        open "$url"
    else
        echo netcat failed, trying again in 3 seconds
        sleep 3
    fi
    echo
done
