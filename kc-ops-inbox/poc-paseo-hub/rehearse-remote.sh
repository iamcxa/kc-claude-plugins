#!/usr/bin/env bash
# Local rehearsal of the ops task step against a bare remote that refuses the default branch, run as the paseo user in the
# image with no network. Input: /fixture holds docs/ops/README.md and fixture-event.json copied from the scratch repository.
# It proves the spacedock steps and the ref-refusal shape only; the Draft PR needs GitHub and is not run here.
set -euo pipefail
W=$(mktemp -d); cd "$W"
git init -q --bare remote.git
cat > remote.git/hooks/pre-receive <<'H'
#!/bin/sh
while read old new ref; do case "$ref" in refs/heads/ops/*) ;; *) [ "$old" = 0000000000000000000000000000000000000000 ] && [ "$ref" = refs/heads/master ] || { echo "refused: $ref" >&2; exit 1; } ;; esac; done
H
chmod +x remote.git/hooks/pre-receive
git init -q -b master work; cd work
git config user.name rehearsal; git config user.email rehearsal@example.invalid
mkdir -p docs; cp -R /fixture/docs/ops docs/ops; cp /fixture/fixture-event.json event.json
git add -A; git commit -q -m seed; git remote add origin "$W/remote.git"; git push -q origin master
SLUG=bound-ceiling-near-rehearsal
git switch -q -c "ops/$SLUG"
{ printf -- '---\ntitle: %s\n---\n\n## Event\n\n' "$SLUG"; cat event.json; } | spacedock new "$SLUG" --workflow-dir docs/ops > /dev/null
spacedock state commit "$SLUG" --workflow-dir docs/ops > /dev/null
git log --oneline -1
git push -q origin "ops/$SLUG" && echo "ops branch push: accepted"
git switch -q master; git commit -q --allow-empty -m "direct"
before=$(git -C "$W/remote.git" rev-parse master)
git push origin master >/dev/null 2>&1 || true
[ "$(git -C "$W/remote.git" rev-parse master)" = "$before" ] && echo "default branch push: refused, remote master unchanged" || { echo "default branch push: ACCEPTED"; exit 1; }
git -C "$W/remote.git" branch --list 'ops/*'
ls docs/ops
