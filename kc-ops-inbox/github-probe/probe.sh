#!/usr/bin/env bash
# Credential probe: with only an installation token, can the actor reach main?
# usage: env -i PATH="$PATH" HOME="$(mktemp -d)" OWNER_REPO=owner/repo TOKEN_FILE=/path probe.sh
# Prints one PASS or FAIL line per check with HTTP status or git exit code; never the token.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
: "${OWNER_REPO:?}" "${TOKEN_FILE:?}"
API=${API_URL:-https://api.github.com}
REMOTE=${REMOTE_URL:-https://github.com/$OWNER_REPO.git}
PROBE_TOKEN=$(<"$TOKEN_FILE"); export PROBE_TOKEN
export GIT_ASKPASS="$HERE/askpass.sh" GIT_TERMINAL_PROMPT=0 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
fails=0
say() { echo "$1 $2 :: $3"; [ "$1" = FAIL ] && fails=$((fails + 1)); }
redact() { sed "s/$PROBE_TOKEN/<token>/g"; }
api() { curl -sS -o /tmp/probe.$$ -w '%{http_code}' -X "$1" -H "Authorization: Bearer $PROBE_TOKEN" -H "Accept: application/vnd.github+json" ${3:+-d "$3"} "$API/repos/$OWNER_REPO$2"; }
msg() { python3 -I -c 'import json,sys;d=json.load(open(sys.argv[1]));print(d.get("message","")[:160])' /tmp/probe.$$ 2>/dev/null | redact; }
errs() { python3 -I -c 'import json,sys;print(json.load(open(sys.argv[1])).get("errors",""))' /tmp/probe.$$ 2>/dev/null | redact | head -c 200; }
field() { python3 -I -c 'import json,sys;print(json.load(open(sys.argv[1])).get(sys.argv[2]))' /tmp/probe.$$ "$1" 2>/dev/null; }
trap 'rm -f /tmp/probe.$$' EXIT

if "$HERE/credential_audit.sh"; then say PASS AC-10a "no GitHub credential besides the installation token"; else say FAIL AC-10a "another credential source exists (listed above)"; fi

W=$(mktemp -d); cd "$W"
git clone -q "$REMOTE" work 2>&1 | redact; cd work || exit 2
git config user.email probe@example.invalid; git config user.name probe
DEF=$(git symbolic-ref --short refs/remotes/origin/HEAD); DEF=${DEF#origin/}
BASE=$(git ls-remote origin "refs/heads/$DEF" | cut -f1)

echo probe > probe.txt; git add probe.txt; git commit -qm "probe: direct commit"
out=$(git push origin "HEAD:$DEF" 2>&1 | redact); rc=${PIPESTATUS[0]}
after=$(git ls-remote origin "refs/heads/$DEF" | cut -f1)
if [ "$rc" != 0 ] && [ "$after" = "$BASE" ]; then say PASS AC-6 "push to $DEF refused (exit $rc), $DEF unchanged :: $(echo "$out" | tail -2 | tr '\n' ' ')"
else say FAIL AC-6 "push to $DEF exit $rc, before=$BASE after=$after"; fi

BR="ops/probe-$(date +%s)"
git checkout -q -b "$BR"
out=$(git push origin "$BR" 2>&1 | redact); rc=${PIPESTATUS[0]}
if [ "$rc" = 0 ]; then say PASS AC-9a "push to $BR accepted"; else say FAIL AC-9a "push to $BR refused (exit $rc) :: $(echo "$out" | tail -1)"; fi

code=$(api POST /pulls "{\"title\":\"probe\",\"head\":\"$BR\",\"base\":\"$DEF\",\"draft\":true}")
N=$(field number); DRAFT=$(field draft); NODE=$(field node_id)
if [ "$code" = 201 ] && [ "$DRAFT" = True ]; then say PASS AC-9b "Draft PR #$N opened"; else say FAIL AC-9b "open Draft PR HTTP $code :: $(msg)"; fi

code=$(api PUT "/pulls/$N/merge" '{"merge_method":"squash"}')
say NOTE draft-merge "HTTP $code :: $(msg) (a draft refuses any merge, so this is not rule evidence)"
gq=$(curl -sS -o /tmp/probe.$$ -w '%{http_code}' -X POST -H "Authorization: Bearer $PROBE_TOKEN" -d "{\"query\":\"mutation(\$id:ID!){markPullRequestReadyForReview(input:{pullRequestId:\$id}){pullRequest{isDraft}}}\",\"variables\":{\"id\":\"$NODE\"}}" "$API/graphql")
say NOTE ready "GraphQL HTTP $gq :: $(redact < /tmp/probe.$$ | head -c 200)"

code=$(api POST "/pulls/$N/reviews" '{"event":"APPROVE"}'); m=$(msg); e=$(errs)
api GET "/pulls/$N" >/dev/null; ms=$(field mergeable_state)
if [ "$code" -ge 400 ]; then say PASS AC-8 "self-approval REFUSED HTTP $code ($m $e); mergeable_state=$ms"; else say NOTE AC-8 "self-approval accepted HTTP $code; counted? mergeable_state=$ms"; fi

code=$(api PUT "/pulls/$N/merge" '{"merge_method":"squash"}'); m=$(msg)
state=$(api GET "/pulls/$N" >/dev/null; field state)
if [ "$code" -ge 400 ] && [ "$state" = open ]; then say PASS AC-7 "API merge of the ready PR refused HTTP $code, PR still $state :: $m"; else say FAIL AC-7 "API merge HTTP $code, PR state $state"; fi

code=$(api POST /rulesets '{"name":"probe","target":"branch","enforcement":"disabled"}')
if [ "$code" -ge 400 ]; then say PASS AC-10b "creating a ruleset refused HTTP $code :: $(msg)"; else say FAIL AC-10b "ruleset creation HTTP $code"; fi

echo "probe branch $BR and PR #$N are left in place (ops/* deletion is blocked by design); delete the scratch repository."
exit $((fails > 0))
