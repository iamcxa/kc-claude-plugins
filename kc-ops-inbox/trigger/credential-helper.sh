#!/bin/sh
# git credential helper: for `get`, answers with the project token only when git's own parsed fields say
# protocol=https, host exactly $OPS_CREDENTIAL_HOST (default github.com) and no username other than x-access-token.
# Every other request, and every other action, gets no answer.
[ "$1" = get ] || exit 0
HOST=${OPS_CREDENTIAL_HOST:-github.com}
protocol= host= username=
while IFS='=' read -r key value; do
  case "$key" in
    protocol) protocol=$value ;;
    host) host=$value ;;
    username) username=$value ;;
    "") break ;;
  esac
done
[ "$protocol" = https ] || exit 0
[ "$host" = "$HOST" ] || exit 0
[ -z "$username" ] || [ "$username" = x-access-token ] || exit 0
[ -n "${OPS_GIT_TOKEN:-}" ] || exit 0
printf 'username=x-access-token\npassword=%s\n' "$OPS_GIT_TOKEN"
