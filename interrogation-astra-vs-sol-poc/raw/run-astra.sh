#!/bin/zsh
# usage: run-astra.sh <work-dir> <task>
W=$1; T=$2; S=$W/$T/snap; O=$W/$T/out
mkdir -p $O; cd $S
date +%s > $O/astra.start
codex exec --sandbox read-only --skip-git-repo-check --cd $S --json -m gpt-6-astra -c model_reasoning_effort='"high"' -o $O/astra-answer.md - < $W/$T/prompt-lens.md > $O/astra-events.jsonl 2> $O/astra.err
echo $? > $O/astra.exit
date +%s > $O/astra.end
