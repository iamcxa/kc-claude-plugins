#!/bin/bash
# Replay design_surfaces.py check at the task-file revision each backlog and ideation briefing binds.
# Usage (from the state checkout): bash chat-only-evidence-observer-blind/measure/replay.sh <package root> <slug>...
# Reads <slug>/review/<stage>/briefing-N/index.json (or the _archive copy), takes the sha in the artifact's
# git-root://state/<sha>/<slug>.md uri, extracts <slug>.md (and <slug>/ when it exists yet) at that sha into a fresh temp directory and runs
# the check there (--seed for backlog). Prints one line per briefing: stage, sha, exit code, first output line.
P=$1; shift
for s in "$@"; do
  for stage in backlog ideation; do
    for f in "$s/review/$stage"/briefing-*/index.json "_archive/$s/review/$stage"/briefing-*/index.json; do
      [ -f "$f" ] || continue
      sha=$(python3 -I -c 'import json,re,sys; print(re.search(r"git-root://state/([0-9a-f]{40})/", json.load(open(sys.argv[1]))["artifacts"][0]["uri"]).group(1))' "$f")
      d=$(mktemp -d)
      git archive "$sha" -- "$s.md" | tar -x -C "$d"
      git archive "$sha" -- "$s" 2>/dev/null | tar -x -C "$d" 2>/dev/null
      flag=; [ "$stage" = backlog ] && flag=--seed
      out=$(python3 -B "$P/scripts/design_surfaces.py" check $flag "$d/$s.md" 2>&1 | head -1)
      python3 -B "$P/scripts/design_surfaces.py" check $flag "$d/$s.md" >/dev/null 2>&1
      echo "$s $stage ${sha:0:8} exit=$? $out"
      rm -rf "$d"
    done
  done
done
