#!/bin/zsh
# usage: run.sh <work-dir> <task> <a3|a4>
W=$1; T=$2; A=$3; S=$W/$T/snap; O=$W/$T/out; P=plain; [ $A = a4 ] && P=lens
mkdir -p $O; cd $S
date +%s > $O/$A.start
codex exec --sandbox read-only --skip-git-repo-check --cd $S --json -m gpt-6.1-sol -c model_reasoning_effort='"high"' -o $O/$A-answer.md - < $W/$T/prompt-$P.md > $O/$A-events.jsonl 2> $O/$A.err
echo $? > $O/$A.exit
date +%s > $O/$A.end
