# One-case local evidence

This is a retained one-run command composition, not an installed runner or service. Requires Python 3.11+ and Git, plus the frozen baseline checkout and the candidate patch. Set the checkout path as the first argument and output JSON path as the second. Save the following block to a disposable file inside that checkout, then run `python3 <saved-file> <checkout> <result.json> [<alternate-checker>]`. It extracts and executes the actual surface-map contract section; it does not reimplement its assertions. It skips the unrelated close-receipt suite and applies a 60-second timeout per subprocess, with no retry. The reported extraction line range and source hashes bind what ran.

```python
import ast, pathlib, subprocess, sys, tempfile, json
ROOT = pathlib.Path(sys.argv[1])
source = ROOT / "scripts/kc-dev-flow-contract-test.py"
tree = ast.parse(source.read_text(), filename=str(source))
start = next(i for i,n in enumerate(tree.body) if isinstance(n, ast.Assign) and any(isinstance(t,ast.Name) and t.id == "surface_map_check" for t in n.targets))
end = next(i for i in range(start,len(tree.body)) if isinstance(tree.body[i],ast.With))
records = []
original_run = subprocess.run
def captured_run(*args, **kwargs):
    kwargs["timeout"] = 60
    result = original_run(*args, **kwargs)
    def safe(value):
        return value.decode() if isinstance(value,bytes) else value
    records.append(dict(argv=[str(v) for v in args[0]], stdout=safe(result.stdout), stderr=safe(result.stderr), exit=result.returncode))
    return result
subprocess.run = captured_run
def require(ok, msg):
    if not ok: raise AssertionError(msg)
def run(command, label):
    result = subprocess.run(command,cwd=ROOT,text=True,capture_output=True)
    require(result.returncode == 0, f"{label}: {result}")
namespace = dict(ROOT=ROOT,Path=pathlib.Path,sys=sys,tempfile=tempfile,subprocess=subprocess,require=require,run=run,require_ablation_only=True)
# Override checker selection in the extracted existing section, without changing product bytes.
if len(sys.argv)>3:
    tree.body[start].value = ast.Call(func=ast.Name(id="Path",ctx=ast.Load()),args=[ast.Constant(sys.argv[3])],keywords=[])
module=ast.fix_missing_locations(ast.Module(body=tree.body[start:end+1],type_ignores=[]))
try:
    exec(compile(module,str(source),"exec"),namespace)
    outcome=dict(exit=0,message="focused surface-map contract section passed")
except (AssertionError,SystemExit) as exc:
    outcome=dict(exit=1,message=str(exc))
finally:
    pathlib.Path(sys.argv[2]).write_text(json.dumps(dict(source=str(source),extracted_line_start=tree.body[start].lineno,extracted_line_end=tree.body[end].end_lineno,commands=records,outcome=outcome),indent=2)+"\n")
print(outcome["message"])
sys.exit(outcome["exit"])
```

`contract-old.json` ran the new tests against the exact original producer before the production edit: exit 1 at the new default-exclusion assertion. `contract-candidate.json` ran the same section after the one-line repair: exit 0. `contract-overbroad.json` ran an isolated copy with `_test.go` replaced by `.go` and a byte-identical sibling profile loader: exit 1 at the new non-test enforcement assertion. This known defective producer is rejected, not called ready.

`before.json` and `after.json` additionally use the exact same retained disposable Git repository, base and candidate commits, empty evidence file and Pilot work item. The only fixture change is `internal/task_test.go` containing `package internal` and a newline. Default changes from exit 1 to 0; strict `--no-exclude` remains 1. These fixture commits are test input only; no product candidate object was created. The temporary fixture path remains under the assigned worktree's `.context/go-test-probe/case` for immediate review.

## Selection and duplicate disposition

Live read-only queue capture in `queue.json` includes all 20 open PRs, the three kc-dev-flow feature PRs (414, 413, 321) with exact unchanged heads, all review/review-thread pages and general comments (all empty), and issue bodies 382, 393, 396, 409. Other open PRs concern different plugins or the broad release proposal. PR-feedback-first found no actionable candidate.

The current scope's dispositions are preserved: issue 382 has a report-tolerant authority projection and feedback-context path in the frozen loader (source inspection only here; no new issue-382 validation claim); 393 needs broader profile-recommendation behavior; 396 spans architecture contracts; 409 spans comment enforcement and a cross-repository corpus. The selected retained Go-test exclusion finding fits two files and the 150-gross-line limit. No new issue, external comment, PR or provider receipt was created.

`selection.json` records the existing owner and a repeated identical input. The worker explicitly refused a duplicate launch and continued one case. This is an exercised manual disposition within this one session, not proof of durable or concurrent automatic deduplication. No new worker/service/provider launch occurred in this worker.

## Scope and quality

Two product files, 50 gross lines (48 additions, 2 deletions), uncommitted. No CI configuration changed. Candidate compilation and diff whitespace checks passed. The relevant existing surface-map section was exercised (7 existing cases plus 6 new Go scenarios); unrelated full suites were not rerun. The only added comment explains why colocated Go tests need suffix matching; removing it would obscure the distinction from directory-based fixture exclusions. No new dependency, abstraction, installed helper or runtime surface was added.

Fresh independent review is pending. Product-object-based implementation-exit mapping is pending because product commits require exact-file Captain confirmation; no fabricated product commit was created to satisfy that interface. The optional separate-provider observation was skipped under the Captain's explicit local-only scope. Original/native knowledge terminalization, archive, cleanup and final check remain incomplete and separately owned. No stopped tree, upstream source, original cleanup, forced state or merge sentinel was used.

## Usage

`usage.json` preserves the FO-attributed anchored counter-epoch snapshot with source line offsets. It is not a final FO total, and implementation/ideation/reviewer usage remains unknown unless separately attributable. Cached input and reasoning are subsets, not extra totals. No whole-cycle cost or efficiency claim is supported. The inherited ten-minute progress checkpoint and shape cost proposals were not a measured hard token or currency cap.
