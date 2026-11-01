"""Build a validation dispatch for a dev2 task.
usage: validate.py <task> <pr> <head 40-hex> [extra checklist line]"""
import subprocess, json, os, re, sys
t, pr, head = sys.argv[1:4]; extra = sys.argv[4]+"\n" if len(sys.argv)>4 else ""
W="/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2"; S=W+"/.spacedock-state"
PK="/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1"
run=lambda *a: subprocess.run(list(a),capture_output=True,text=True)
assert re.fullmatch(r"[0-9a-f]{40}",head), "full head sha required"
st=run("spacedock","status","--workflow-dir",W,"--set",t,f"pr=iamcxa/kc-claude-plugins#{pr}","status=validation")
if st.returncode: print("SET-FAIL",(st.stdout+st.stderr).strip()[-300:]); sys.exit(1)
EP=f"{S}/{t}.md" if os.path.exists(f"{S}/{t}.md") else f"{S}/{t}/index.md"
s=open(EP).read()
prof=re.search(r"^profile: *(\S+)",s,re.M).group(1)
ng=re.findall(r"^(ADR|Migration): (\d{4})",s,re.M)
n=max([int(__import__("re").fullmatch(r"validation-(\d+)\.md",f).group(1)) for f in os.listdir(f"{S}/{t}/dispatch") if __import__("re").fullmatch(r"validation-(\d+)\.md",f)]+[0])+1
WH=run("git","-C",W,"rev-parse","HEAD").stdout.strip()
ck=(f"Independent verdict on PR #{pr} head {head[:8]} against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states\n"
    f"{extra}"
    f"A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; {PK}/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition\n")
ngl="".join(f"Number guards: {k}: {v}\n\n" for k,v in ng)
sc=(f"Package root: {PK}\n\n{ngl}Profile: {prof}. Start in the assigned worktree; verify pwd and git root before edits. Candidate: iamcxa/kc-claude-plugins PR #{pr}, head {head}, base origin/main. This task; other PRs may be in flight and are not your candidate. "
    f"Check the candidate out detached in a throwaway worktree and remove it after. Commit your stage report with `spacedock state commit {t} --workflow-dir {W}`. "
    "Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not push, comment on any PR, request reviews or mark ready.\n\n"
    "Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).\n")
body=f"# validation-{n}\n\nDispatched: {WH} (workflow checkout, kc-dev-flow-2 0.33.1 README); batch 11\nCandidate: {head}\nModel: {os.environ.get('MODEL_LABEL','sonnet')}\n{os.environ.get('ROSTER_LINE','')}\n\n## Checklist\n\n{ck}\n## Scope notes\n\n{sc}"
REC=f"{S}/{t}/dispatch/validation-{n}.md"; open(REC,"w").write(body)
r=run("python3",f"{PK}/scripts/dispatch_records.py","--names",REC)
if r.returncode: os.remove(REC); print("NAMES-FAIL (record removed)",r.stdout); sys.exit(1)
print(run("spacedock","state","commit",t,"--workflow-dir",W).stdout.strip()[-60:])
open("/tmp/fo-vck.txt","w").write(ck); open("/tmp/fo-vsc.txt","w").write(sc)
b=run("spacedock","dispatch","build","--workflow-dir",W,"--entity-path",EP,"--stage","validation","--checklist-file","/tmp/fo-vck.txt","--scope-notes-file","/tmp/fo-vsc.txt")
if b.returncode: print("BUILD-FAIL",b.stderr[-300:]); sys.exit(1)
d=json.loads(b.stdout); print(d["name"]); print(d["prompt"])
