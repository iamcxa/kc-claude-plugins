#!/bin/bash
for a in "$@"; do case "$a" in */pr_watch.py|pr_watch.py) export HOME=/tmp/replay-c2/fakehome; echo "$$ $*" >> /tmp/replay-c2/pr-watch-pids.log; break;; esac; done
exec /Users/kent/.pyenv/versions/3.11.14/bin/python3 "$@"
