#!/usr/bin/env bash
# P4: two trigger runs join events to one incident concurrently on the state branch. Local bare repo only.
set -u
T=$(mktemp -d); git init -q --bare "$T/origin.git"
git clone -q "$T/origin.git" "$T/seed" 2>/dev/null; cd "$T/seed"
git config user.email p@x; git config user.name p; git checkout -q -b spacedock-state/ops
mkdir -p inc-a/events; printf -- '---\nstatus: decision\n---\n\n## Events\n\n- e1 bound-ceiling-near 120/150\n' > inc-a.md
echo '{"id":"e1"}' > inc-a/events/e1.json; git add -A; git commit -qm seed; git push -q origin spacedock-state/ops
run() { # $1 mode (append|file) $2 writer $3 event id
  local W="$T/$2-$1"; git clone -q -b spacedock-state/ops "$T/origin.git" "$W"; cd "$W"; git config user.email p@x; git config user.name p
  if [ "$1" = append ]; then printf -- '- %s joined\n' "$3" >> inc-a.md; git add inc-a.md; else echo "{\"id\":\"$3\"}" > "inc-a/events/$3.json"; git add "inc-a/events/$3.json"; fi
  git commit -qm "join $3"; }
for mode in append file; do
  run $mode w1 e2; run $mode w2 e3
  ( cd "$T/w1-$mode" && git push -q origin spacedock-state/ops ) ; 
  cd "$T/w2-$mode"; git push -q origin spacedock-state/ops 2>/dev/null || { if git pull -q --rebase origin spacedock-state/ops 2>/dev/null; then git push -q origin spacedock-state/ops && echo "$mode: second writer rebased and pushed"; else echo "$mode: second writer REBASE CONFLICT"; git rebase --abort; fi; }
  # reset origin to seed for the next mode
  git -C "$T/origin.git" update-ref refs/heads/spacedock-state/ops $(git -C "$T/seed" rev-parse HEAD)
done
rm -rf "$T"
