# Exact commands for AC-1..AC-7 (run once on 2026-11-12)

```sh
SB=/Users/kent/.local/bin/spacedock          # spacedock 0.27.2
WD=<kc-claude-plugins worktree>/docs/dev2    # this workflow; state checkout $WD/.spacedock-state
E=$WD/.spacedock-state/held-and-closed-tasks-leave-the-design-queue/ideation
# held-ten.txt = the ten slugs, one per line
```

## Scratch recipe (origin-less, so nothing can publish real state)

```sh
SCR=$(mktemp -d /tmp/held-closed-scratch.XXXXXX)
# small copy (3 held tasks) used by AC-4 and AC-5
mkdir -p $SCR/repo; git -C <worktree> archive 8ce0eb6050c889b21baccf50fec35231bc888d66 docs/dev2/README.md docs/dev2/_mods | tar -x -C $SCR/repo
(cd $SCR/repo && git init -q -b main && git add -A && git commit -qm base)
mkdir -p $SCR/repo/docs/dev2/.spacedock-state
git -C $WD/.spacedock-state archive eae5ea47cec926f35d164f8a88d31579196d7634 README.md fo-write-checks-parse-top-level.md seed-check-requires-alignment-result.md adoption-asks-which-extensions.md | tar -x -C $SCR/repo/docs/dev2/.spacedock-state
(cd $SCR/repo/docs/dev2/.spacedock-state && git init -q -b spacedock-state/dev2 && git add -A && git commit -qm base)   # no remote added
# full copy (whole state + package scripts) used by AC-3
mkdir -p $SCR/full; git -C <worktree> archive 8ce0eb6050c889b21baccf50fec35231bc888d66 docs/dev2/README.md docs/dev2/_mods kc-dev-flow-2/scripts kc-dev-flow-2/extensions | tar -x -C $SCR/full
(cd $SCR/full && git init -q -b main && git add -A && git commit -qm base)
mkdir -p $SCR/full/docs/dev2/.spacedock-state; git -C $WD/.spacedock-state archive eae5ea47cec926f35d164f8a88d31579196d7634 | tar -x -C $SCR/full/docs/dev2/.spacedock-state
(cd $SCR/full/docs/dev2/.spacedock-state && git init -q -b spacedock-state/dev2 && git add -A && git commit -qm base)
```

## AC-1
```sh
$SB status --workflow-dir $WD --where status=ideation --where gate-readiness=not-applicable --fields slug --json > $E/ac1-held-query.json
python3 -c 'import json,sys; rows=json.load(open(sys.argv[1]))["entities"]; got=sorted(r["slug"] for r in rows); want=sorted(open(sys.argv[2]).read().split()); print("got", len(got), "want", len(want), "equal", got==want); sys.exit(0 if got==want else 1)' $E/ac1-held-query.json $E/held-ten.txt
$SB status --workflow-dir $WD --where status=ideation --fields slug,status,gate-readiness > $E/ac1-status-with-readiness.txt
```

## AC-2
```sh
$SB status --workflow-dir $WD --next --json > $E/ac2-next.json
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); slugs={r["slug"] for r in d["ready_gates"]}|{r.get("slug") for r in d["dispatchable"]}; ten=set(open(sys.argv[2]).read().split()); hit=slugs&ten; print("rows", len(slugs), "held in next:", sorted(hit)); sys.exit(1 if hit else 0)' $E/ac2-next.json $E/held-ten.txt
```

## AC-3
```sh
cd $SCR/full && SPACEDOCK_BIN=$SB python3 -B kc-dev-flow-2/scripts/pr_watch.py --state $SCR/watch.json tasks $SCR/full/docs/dev2 > $E/base-pr-watch-tasks.txt
python3 -c 'import sys; out=open(sys.argv[1]).read(); ten=open(sys.argv[2]).read().split(); hit=[s for s in ten if s in out]; print("words", len(out.split()), "held named:", hit); sys.exit(1 if hit else 0)' $E/base-pr-watch-tasks.txt $E/held-ten.txt
```
GitHub calls in this run are reads only (`gh repo view`, `gh pr list`, `gh pr view`, `gh api` GET via the codex/copilot readers); `$SCR/watch.json` is a local file.

## AC-4
```sh
echo "- probe" > $SCR/checklist.txt
$SB dispatch build --workflow-dir $SCR/repo/docs/dev2 --entity-path $SCR/repo/docs/dev2/.spacedock-state/adoption-asks-which-extensions.md --stage ideation --checklist-file $SCR/checklist.txt
# the /tmp/spacedock-dispatch/<uuid>-...-adoption-asks-which-extensions-ideation.md it wrote was removed by exact path
```

## AC-5
```sh
cd $SCR/repo
$SB merge guard fo-write-checks-parse-top-level --verdict rejected --workflow-dir $SCR/repo/docs/dev2
$SB status --workflow-dir $SCR/repo/docs/dev2 --set fo-write-checks-parse-top-level status=done verdict=REJECTED
$SB status --workflow-dir $SCR/repo/docs/dev2 --archive fo-write-checks-parse-top-level
```
Control (inconclusive): the same two close commands on a non-held ideation task in `$SCR/full` refuse for a different reason (`git-root commit is not an exact full local commit object`), because the archive copy lacks the git history gate sources bind to. Saved as `scratch-close-non-held-control.txt`.

## AC-6
```sh
python3 - $WD/.spacedock-state/_archive/fo-interviews-extension.md <<'PY'
import sys,yaml
d=yaml.safe_load(open(sys.argv[1]).read().split('\n---\n')[0].lstrip('-\n'))
ok=False
for r in d['gates']['records']:
    at=r['attempts']
    for i,a in enumerate(at):
        res=a.get('resolution') or {}
        print(r['stage'], a['id'], res.get('decision'), (a.get('application') or {}).get('state'))
        if res.get('decision')=='hold' and i+1<len(at): ok=True
print('successor attempt after hold:', ok); sys.exit(0 if ok else 1)
PY
```

## AC-7
```sh
python3 - $WD/.spacedock-state $E/ac7-proposed-held-lines.tsv <<'PY'
import sys,yaml,pathlib
st=pathlib.Path(sys.argv[1]); bad=0
for line in open(sys.argv[2], encoding='utf-8'):
    slug,kind,quote=line.rstrip('\n').split('\t')
    d=yaml.safe_load((st/f'{slug}.md').read_text().split('\n---\n')[0].lstrip('-\n'))
    reason=[ (r['attempts'][-1].get('resolution') or {}) for r in d['gates']['records']]
    reason=[x['reason'] for x in reason if x.get('decision')=='hold'][-1]
    ok = (quote in reason) if quote else None
    if quote and not ok: bad+=1
    print(f'{slug}\t{kind}\t{"verbatim in hold reason" if ok else ("NOT FOUND" if quote else "no line proposed")}')
print('mismatches', bad); sys.exit(1 if bad else 0)
PY
```
