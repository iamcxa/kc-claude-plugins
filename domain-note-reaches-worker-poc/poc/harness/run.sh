#!/usr/bin/env bash
# Usage: run.sh <codex|claude> <none|A|B|C> <n>
set -euo pipefail
host="$1"; variant="$2"; n="$3"
H=/tmp/opencode/domain-poc
X="$H/harness"
r="$H/runs/$host-$variant-$n"
[ -e "$r" ] && { echo "exists: $r" >&2; exit 1; }
mkdir -p "$r"
cp -R "$H/template/relay" "$r/repo"
R="$r/repo"
git_c() { git -C "$R" -c user.email=poc@local -c user.name=poc "$@"; }

pointer='

## Domain notes

Lessons that hold across repositories of one kind are domain notes: one file each in `docs/domain/`, named for the kind (for example `netlify.md`). Before you plan or change something a name could cover, run `ls docs/domain` and read the file whose name covers it.'

prompt="$(cat "$X/task.md")"
case "$variant" in
  none) ;;
  A)
    mkdir -p "$R/docs/domain"; cp "$X/netlify.md" "$R/docs/domain/netlify.md"
    printf '%s\n' "$pointer" >> "$R/AGENTS.md"
    git_c add -A; git_c commit -qm "docs: add domain notes" ;;
  B)
    printf '%s\n' "$pointer" >> "$R/AGENTS.md"
    printf '\n/docs/domain/\n' >> "$R/.gitignore"
    git_c add -A; git_c commit -qm "docs: point at domain notes"
    mkdir -p "$R/docs/domain"; cp "$X/netlify.md" "$R/docs/domain/netlify.md" ;;
  C)
    practice="$(sed -n 's/^\*\*Practice:\*\* //p' "$X/netlify.md")"
    applic="$(sed -n 's/^\*\*Applicability:\*\* //p' "$X/netlify.md")"
    prompt="$prompt

Checklist. Answer each line in your plan:
- Per domain note netlify (applies when: $applic): $practice" ;;
  *) echo "bad variant" >&2; exit 2 ;;
esac
printf '%s\n' "$prompt" > "$r/prompt.md"
git -C "$R" status --short > "$r/git-status-before.txt"

start=$(date +%s)
case "$host" in
  codex)
    CODEX_HOME="$H/homes/codex" codex exec --json --ephemeral --ignore-user-config --ignore-rules \
      -m gpt-6.1-sol -c model_reasoning_effort=xhigh -s read-only --skip-git-repo-check \
      -C "$R" -o "$r/answer.md" "$prompt" > "$r/transcript.jsonl" 2> "$r/stderr.txt" || echo "exit=$?" >> "$r/stderr.txt" ;;
  claude)
    ( cd "$R" && claude -p "$prompt" --setting-sources project --model claude-opus-5-5 --effort high \
      --output-format stream-json --verbose --no-session-persistence --strict-mcp-config \
      --disallowedTools "Edit,Write,NotebookEdit,WebFetch,WebSearch,Agent" \
      > "$r/transcript.jsonl" 2> "$r/stderr.txt" ) || echo "exit=$?" >> "$r/stderr.txt"
    python3 -I -c 'import json,sys
res=[json.loads(l) for l in open(sys.argv[1]) if l.strip().startswith("{")]
r=[x for x in res if x.get("type")=="result"]
open(sys.argv[2],"w").write(r[-1].get("result","") if r else "")' "$r/transcript.jsonl" "$r/answer.md" ;;
  gemini)
    ( cd "$R" && agy -p "$prompt" --model gemini-4-argon-high --mode plan --output-format stream-json \
      > "$r/transcript.jsonl" 2> "$r/stderr.txt" ) || echo "exit=$?" >> "$r/stderr.txt"
    python3 -I -c 'import json,sys
res=[json.loads(l) for l in open(sys.argv[1]) if l.strip().startswith("{")]
r=[x for x in res if x.get("event")=="result"]
open(sys.argv[2],"w").write(r[-1]["result"].get("response","") if r else "")' "$r/transcript.jsonl" "$r/answer.md" ;;
esac
end=$(date +%s)
echo "$((end-start))" > "$r/seconds.txt"
git -C "$R" status --short > "$r/git-status-after.txt"
bash "$X/score.sh" "$r"
