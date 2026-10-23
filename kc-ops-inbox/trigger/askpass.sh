#!/bin/sh
# Git credential prompt handler: answers only for the GitHub host (or OPS_ASKPASS_HOST), never for another remote a command names.
HOST=${OPS_ASKPASS_HOST:-github.com}
case "$1" in
  "Username for 'https://$HOST'"*) echo x-access-token ;;
  "Password for 'https://x-access-token@$HOST'"*) echo "$OPS_GIT_TOKEN" ;;
  *) exit 1 ;;
esac
