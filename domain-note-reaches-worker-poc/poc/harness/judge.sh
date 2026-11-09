#!/usr/bin/env bash
# Usage: judge.sh <run-dir>. Blinded strict judgment of answer.md; writes judge.json and prints one line.
# Fixed 2026-11-09 after the baseline showed score.sh's "applied" over-counts incidental IP mentions.
set -euo pipefail
r="$1"
blind="$(sed -E 's#`?docs/domain/[A-Za-z.-]*`?#[a source]#g; s#[Dd]omain notes?#[a source]#g; s#`?netlify\.md`?#[a source]#g' "$r/answer.md")"
q='You are grading a validation plan for a feature tested through Netlify dev on http://localhost:8888. Grade one question only.

Question: does the plan REQUIRE the browser test cases to run with `localhost` explicitly resolved to IPv4 (127.0.0.1) in one run AND explicitly resolved to IPv6 (::1) in another run, on the browser side?

- YES: both explicit browser-side resolutions are required for the browser cases.
- PARTIAL: it varies the address family only for the CLI or request client, or makes the IPv6 (or IPv4) run conditional or optional, or names both families without requiring browser runs in each.
- NO: none of the above.

Reply with exactly one JSON object and nothing else: {"grade":"YES|PARTIAL|NO","quote":"<the shortest sentence from the plan that decides it, or empty>"}

The plan:
'
tmp=$(mktemp -d)
out="$(cd "$tmp" && printf '%s\n%s\n' "$q" "$blind" | claude -p --setting-sources project --model claude-sonnet-5-5 \
  --no-session-persistence --strict-mcp-config --disallowedTools "Bash,Read,Grep,Glob,Edit,Write,WebFetch,WebSearch,Agent" \
  --output-format json 2>/dev/null)"
rm -rf "$tmp"
printf '%s' "$out" | python3 -I -c 'import json,sys,re
o=json.load(sys.stdin); t=o.get("result","")
m=re.search(r"\{.*\}", t, re.S)
j=json.loads(m.group(0)) if m else {"grade":"ERROR","quote":t[:200]}
open(sys.argv[1],"w").write(json.dumps(j, ensure_ascii=False))
print(sys.argv[2]+"\t"+j.get("grade","ERROR"))' "$r/judge.json" "$(basename "$r")"
