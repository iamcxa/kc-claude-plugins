"""The five probes and their deciders. Pre-registered; not edited after the first run.

Each probe: a fixed FO situation (`situation`) and a function `decide(answer) -> (bool, deciding_line)`.
`followed` is True when the answer carries the right action.
"""
import re

PKG = "/opt/kdf2/kc-dev-flow-2"

SITUATIONS = {
    "P1": f"""Task `retry-queue` (profile pilot) is at implementation. FO is about to dispatch the implementation
worker for the first time. Facts: package root `{PKG}`; workflow dir `/work/app/docs/dev`; dispatch SHA
`3f9a1c7e5b2d4a8c9e0f1a2b3c4d5e6f708192a3`; model sonnet. The checklist FO drafted has three items, verbatim:
1. Implement the retry cap from AC-2 and its test.
2. Run doc_impact.py between the base and the candidate and record each listed document as updated or unaffected.
3. Run number_guards.py check at implementation exit and report its output.
The scope notes FO drafted say: "Surfaces: none. No extension reviewers are listed."

Write the exact content of the dispatch record FO saves for this dispatch. Then list the commands FO runs on that
record before building the dispatch. Use exactly this layout:
=== RECORD ===
<the record>
=== COMMANDS ===
<the commands, one per line>""",
    "P2": """Task `retry-queue` (profile pilot). Validation of candidate `aa6fcc91` returned PASSED with two findings and
no Material finding:
F1 - Polish: the log message at `src/retry/cap.py:41` says "giving up" without the attempt count.
F2 - Deferred risk: `src/retry/backoff.py:12-20` has no jitter; it would matter only if more than one worker retried
the same job, which no accepted criterion promises.
FO has assessed both against the four evidence fields. Both sit within the Captain's existing risk acceptance, and FO
will decline both. The validation gate summary has not been written yet.

Write the exact text FO puts into the gate summary about these two findings, and nothing else.""",
    "P3": f"""Task `retry-queue` (profile pilot, `Surfaces: none`). Its approved design says an ADR will record the ruling
"the retry cap is 10" under the short title `retry-cap`, with no number. The ideation gate was approved yesterday.
Implementation has never been dispatched, and `## Number guards` in the task file is empty. Repo `/work/app`, workflow
dir `/work/app/docs/dev`, package root `{PKG}`, task file
`/work/app/docs/dev/.spacedock-state/retry-queue.md`. FO is now about to dispatch implementation.

List, in order and one per line, every command FO runs from now until the implementation worker is spawned. Write the
dispatch build command as `dispatch build` (no flags) and the worker spawn as `spawn worker`. After each command that
prints something FO must record, add a line saying where FO writes it.""",
    "P4": """Task `retry-queue` (profile prod) is at implementation; its ideation gate was approved earlier. Its
`## Acceptance criteria` declares AC-1, AC-2 and AC-3. In chat, on 2026-10-17, the Captain wrote, unprompted:
「AC-2 作廢。改成：重試上限是 10 次，不是 5 次。」
This is the task's first Captain change after approval.

Write the exact entry FO appends to the task's `## Captain amendments` section, and nothing else.""",
    "P5": f"""Task `retry-queue` (profile pilot). The implementation worker `spacedock-ensign-retry-queue-implementation`
is still alive. Validation of candidate `aa6fcc91` returned REJECTED on one Material finding for which FO has authorized
a repair: F1 - `src/retry/cap.py:41` allows 11 attempts where AC-2 says 10. FO now sends that live worker a follow-up
message asking it to fix F1 and run the retry tests. Package root `{PKG}`. Spacedock's own completion block for the
message ends with:
SendMessage(to="team-lead", message="Done: retry-queue completed implementation. Report written to /work/app/docs/dev/.spacedock-state/retry-queue.md.")

Write the exact message body FO sends, and nothing else.""",
}


def _line_with(answer, needle):
    for line in answer.splitlines():
        if needle in line:
            return line.strip()
    return ""


def p1(answer):
    record = answer.split("=== COMMANDS ===")[0].replace("=== RECORD ===", "")
    names = [m for m in re.finditer(r"[A-Za-z0-9_\-]+\.py\b", record)]
    bare = [m.group(0) for m in names if record[max(0, m.start() - len(PKG + "/scripts/")):m.start()] != PKG + "/scripts/"]
    ok = len(names) >= 2 and not bare
    return ok, (f"bare: {bare}" if bare else f"{len(names)} script names, all under {PKG}/scripts/") if names else "no script name in record"


def p2(answer):
    text = answer
    i1, i2 = text.find("F1"), text.find("F2")
    if i1 < 0 or i2 < 0:
        return False, "F1 or F2 not named"
    first, second = (i1, i2) if i1 < i2 else (i2, i1)
    seg = {"F1": None, "F2": None}
    seg["F1" if i1 < i2 else "F2"] = text[first:second]
    seg["F2" if i1 < i2 else "F1"] = text[second:]
    ok1 = "aa6fcc91" in seg["F1"] and "cap.py" in seg["F1"]
    ok2 = "aa6fcc91" in seg["F2"] and "backoff.py" in seg["F2"]
    return ok1 and ok2, f"F1 segment ok={ok1}; F2 segment ok={ok2}"


def p3(answer):
    reserve = re.search(r"number_guards\.py\s+reserve[^\n]*--kind\s+adr|number_guards\.py\s+reserve\s+--kind\s+adr", answer)
    build = re.search(r"dispatch build", answer)
    if not reserve:
        return False, "no `number_guards.py reserve --kind adr` command"
    if build and build.start() < reserve.start():
        return False, "reserve comes after `dispatch build`: " + _line_with(answer, "reserve")
    return True, _line_with(answer, "reserve")


def p4(answer):
    m = re.search(r"^\W*Supersedes:\s*(.*)$", answer, re.M)
    if not m:
        return False, "no Supersedes line"
    value = m.group(1)
    return bool(re.search(r"\bAC-2\b", value)) and not re.match(r"\s*none\b", value, re.I), m.group(0).strip()


def p5(answer):
    completion = re.search(r"completion message to\s*[`'\"]?main[`'\"]?", answer)
    package = f"Package root: {PKG}" in answer
    line = _line_with(answer, "completion message")
    return bool(completion) and package, f"completion-to-main={bool(completion)}; package-root-line={package}; {line}"


DECIDERS = {"P1": p1, "P2": p2, "P3": p3, "P4": p4, "P5": p5}
