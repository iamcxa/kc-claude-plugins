#!/usr/bin/env bash
# replay.sh <scripts dir> <scratch> <task> <budget> <pending record n>
# Builds a replay commit in a scratch clone: Budget section + Budget header on ideation-1,
# dispatch records from n on removed, then runs role_triggers with --pending ideation-n.
set -u
P=$1 X=$2 T=$3 B=$4 N=$5
R=$X/replay; f=_archive/$T.md; d=_archive/$T/dispatch
git -C $R checkout -q -f origin/HEAD 2>/dev/null || git -C $R checkout -q -f master 2>/dev/null || git -C $R checkout -q -f main
git -C $R checkout -q -B replay
mkdir -p $X/pending; cp $R/$d/ideation-$N.md $X/pending/ideation-$N.md
python3 - "$R/$f" "$R/$d/ideation-1.md" "$B" <<'PY'
import sys, re
task, rec, b = sys.argv[1:]
t = open(task).read()
t = re.sub(r"\n## ", f"\n## Budget\n{b}\n\n## ", t, count=1)
open(task, "w").write(t)
r = open(rec).read().split("\n")
r.insert(1, f"Budget: {b}")
open(rec, "w").write("\n".join(r))
PY
for g in $R/$d/*.md; do n=$(basename $g); case $n in ideation-1.md) ;; ideation-*.md) k=${n#ideation-}; k=${k%%[.-]*}; [ $k -ge $N ] && git -C $R rm -q $d/$n;; *) git -C $R rm -q $d/$n;; esac; done
git -C $R -c user.name=replay -c user.email=replay@example.invalid commit -q -am "replay $T budget '$B' pending ideation-$N"
python3 -B $P/role_triggers.py $R $T --pending $X/pending/ideation-$N.md --budget-only
