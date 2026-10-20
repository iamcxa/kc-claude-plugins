#!/bin/zsh
W=$(cat /tmp/replay-dir.txt); S=$W/snap
cd $S
date +%s > $W/out/$1.start
case $1 in
 a1) claude -p --model sonnet --tools Read,Grep,Glob --allowedTools Read,Grep,Glob --strict-mcp-config --disable-slash-commands --output-format stream-json --verbose < $W/prompt-plain.md > $W/out/a1-events.jsonl 2> $W/out/a1.err;;
 a2) claude -p --model opus --effort high --tools Read,Grep,Glob --allowedTools Read,Grep,Glob --strict-mcp-config --disable-slash-commands --output-format stream-json --verbose < $W/prompt-lens.md > $W/out/a2-events.jsonl 2> $W/out/a2.err;;
 a3) codex exec --sandbox read-only --skip-git-repo-check --cd $S --json -m gpt-6.1-sol -c model_reasoning_effort='"high"' -o $W/out/a3-answer.md - < $W/prompt-plain.md > $W/out/a3-events.jsonl 2> $W/out/a3.err;;
 a4) codex exec --sandbox read-only --skip-git-repo-check --cd $S --json -m gpt-6.1-sol -c model_reasoning_effort='"high"' -o $W/out/a4-answer.md - < $W/prompt-lens.md > $W/out/a4-events.jsonl 2> $W/out/a4.err;;
esac
echo $? > $W/out/$1.exit
date +%s > $W/out/$1.end
