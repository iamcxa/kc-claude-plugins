#!/usr/bin/env python3
"""Build the ship-flow UAT document straight from a sprint's `docs/dev` entities.

usage: uat-doc.py <sprint> --state-dir <dir> [--root <path>] [--flows <path>]

This is the cloud-wrapper redesign's `uat-doc.py`
(`docs/superpowers/specs/2026-09-10-ship-flow-cloud-wrapper-design.md`, section "uat"): no
`plan-receipt.json`, no `plan-approval.json`, no `close-receipt.json` -- those belonged to the
plan-flow batch-dir world this sprint's sibling task (dispatch/watch) is replacing. Reads:

  <state-dir>/*.md                    every top-level entity file whose frontmatter `sprint:`
                                       equals the given sprint (a task of this batch); a task's
                                       PR link and validation-gate status come only from its own
                                       frontmatter -- no other file is trusted for those fields.
  <state-dir>/_ship_fence/<sprint>.json   the batch record dispatch.sh/watch.sh write: per-task
                                       workspace/session ids, and the questions a cloud worker
                                       asked with the answer sent (design's "Answering
                                       principle"). Optional -- a sprint with no fence file yet
                                       still gets a document, just with no Q&A section content.

`--root` (default: `--state-dir`, resolved) and `--flows` (default: the `E2E flows` Local
Profile row, read from `<root>/docs/ship/README.md`) locate the checkout `e2e-gate.py` is run
against for the "verified" stage's own check, at the **integrated head** -- which head that is
(`preview`/`trunk`/`staging`) is read from the same README's `Integrated head` Local Profile row,
per the design: ship has no opinion of its own on before-merge vs. after-merge UAT, the row does.
`e2e-gate.py` is called in its milestone-name form (one positional arg): it resolves the sprint's
flow file and reports whether one exists, it does not itself run `e2e-cli.sh` in that form (that
requires the receipt pair this design does not produce) -- the "e2e result" line records what
`e2e-gate.py` reported, not a fabricated pass/fail this script did not observe. When the
Integrated head row or the flows directory cannot be resolved, the e2e result records that
plainly rather than guessing a root.

Exit 0 on success, document on stdout. Exit 1 printing one slug per line (nothing else) when a
task in the sprint lacks a *prepared* `validation` gate (an attempt with a `briefing` and no
`resolution`/`withdrawal` yet) -- the document is for the Captain's one-sitting `gate record` +
UAT + merge; a task not yet there is not ready to list. Exit 2 on a usage error, no task found for
the sprint, or a `_ship_fence/<sprint>.json` that parses as JSON but is malformed
(json.JSONDecodeError, KeyError, TypeError).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
TOP_KEY_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):[ \t]?(.*)$")
GATE_RECORD_RE = re.compile(r"^ {8}- id: gate:")
GATE_STAGE_RE = re.compile(r"^ {10}stage:\s*(\S+)")
GATE_ATTEMPT_RE = re.compile(r"^ {12}- id: gate-attempt:")
GATE_DECISION_KEY_RE = re.compile(r"^ {14}(resolution|withdrawal):")
REF_SAFE_RE = re.compile(r"^[A-Za-z0-9._/-]+$")
UNSAFE_MARKER = "<unsafe value refused>"


def single_line(value):
    """Collapse any embedded newline/CR run in value into one space."""
    if value is None:
        return None
    return re.sub(r"\s*[\r\n]+\s*", " ", str(value)).strip()


def sanitize_text(value):
    """Single-line-normalize free text and neutralize markdown link/heading syntax."""
    if value is None:
        return None
    value = single_line(value)
    for ch in "\\`[]()":
        value = value.replace(ch, "\\" + ch)
    return value


def render_ref(value):
    if not value:
        return None
    value = single_line(value)
    if not REF_SAFE_RE.match(value):
        return UNSAFE_MARKER
    return value


def read_frontmatter_text(text):
    m = FRONTMATTER_RE.match(text)
    return m.group(1) if m else ""


def top_fields(frontmatter_text):
    """Flat (zero-indent) `key: value` frontmatter fields only -- nested blocks (gates, mod-block)
    are read by their own dedicated parser, never by this generic scan."""
    fields = {}
    for line in frontmatter_text.splitlines():
        if line[:1] in (" ", "\t"):
            continue
        m = TOP_KEY_RE.match(line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if len(val) >= 2 and val[0] == '"' and val[-1] == '"':
            val = val[1:-1]
        fields[key] = val
    return fields


def validation_gate_status(frontmatter_text):
    """'prepared' (briefing, no resolution/withdrawal yet), 'resolved' (decision recorded), or
    'absent' (no validation-stage gate record at all) for this entity's *last* validation gate
    record's *last* attempt -- matches how `spacedock gate prepare`/`gate record` append, never
    rewrite, prior attempts."""
    lines = frontmatter_text.splitlines()
    starts = [i for i, l in enumerate(lines) if GATE_RECORD_RE.match(l)]
    validation_blocks = []
    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        stage_line = lines[start + 1] if start + 1 < len(lines) else ""
        sm = GATE_STAGE_RE.match(stage_line)
        if sm and sm.group(1) == "validation":
            validation_blocks.append((start, end))
    if not validation_blocks:
        return "absent"
    s, e = validation_blocks[-1]
    block = lines[s:e]
    attempt_starts = [i for i, l in enumerate(block) if GATE_ATTEMPT_RE.match(l)]
    if not attempt_starts:
        return "absent"
    a_start = attempt_starts[-1]
    attempt_lines = block[a_start:]
    has_decision = any(GATE_DECISION_KEY_RE.match(l) for l in attempt_lines)
    return "resolved" if has_decision else "prepared"


def load_task_entities(state_dir, sprint):
    tasks = {}
    for path in sorted(Path(state_dir).glob("*.md")):
        if path.name.startswith("_"):
            continue
        text = path.read_text(encoding="utf-8")
        frontmatter_text = read_frontmatter_text(text)
        fields = top_fields(frontmatter_text)
        if fields.get("sprint") != sprint:
            continue
        slug = path.stem
        tasks[slug] = {
            "title": fields.get("title", slug),
            "status": fields.get("status", ""),
            "pr": fields.get("pr") or None,
            "sprint_readiness": fields.get("sprint-readiness"),
            "validation_gate": validation_gate_status(frontmatter_text),
        }
    return tasks


def load_batch_record(state_dir, sprint):
    """The claim-fence file `dispatch.sh` writes: a top-level map `<slug> ->
    {workspace, session, message_sha256}` (no `sprint`/`tasks` wrapper -- that indirection was
    this task's own invention before this fix and does not match what `dispatch.sh` actually
    writes). `close.py`'s own `<slug>.debrief -> {status, path}` field, plus batch-level
    `questions`/`residuals` siblings this task's own flow adds, live as additional top-level keys
    in the same file. Absent file -> empty record, same as an unstarted batch."""
    path = Path(state_dir) / "_ship_fence" / f"{sprint}.json"
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def resolve_repo_hint(root):
    """Best-effort 'owner/repo' from the checkout's origin remote; None if it cannot be read --
    never fabricated so a rendered PR link is either correct or omitted, not guessed."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=10,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    url = result.stdout.strip()
    m = re.search(r"[:/]([^/:]+/[^/:]+?)(?:\.git)?$", url)
    return m.group(1) if m else None


def render_pr(pr_field, repo_hint):
    if not pr_field:
        return "not recorded"
    value = single_line(pr_field)
    m = re.match(r"^([\w.-]+/[\w.-]+)#(\d+)$", value)
    if m:
        return f"https://github.com/{m.group(1)}/pull/{m.group(2)}"
    m = re.match(r"^pr-merge:(\d+)$", value)
    if m:
        if repo_hint:
            return f"https://github.com/{repo_hint}/pull/{m.group(1)} (merged)"
        return f"PR #{m.group(1)} (merged via pr-merge)"
    m = re.match(r"^#(\d+)$", value)
    if m and repo_hint:
        return f"https://github.com/{repo_hint}/pull/{m.group(1)}"
    if m:
        return f"PR {value}"
    return sanitize_text(value)


def read_local_profile_row(readme_path, label):
    if not readme_path or not Path(readme_path).is_file():
        return None
    text = Path(readme_path).read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) >= 2 and cells[0] == label:
            return cells[1]
    return None


def run_e2e_gate(root, flows, sprint):
    if not root:
        return "not recorded (no --root and no resolvable state-dir root)"
    if not flows:
        return "not recorded (Integrated head row's E2E flows location could not be resolved)"
    flows_dir = flows if os.path.isabs(flows) else str(Path(root) / flows)
    if not os.path.isdir(flows_dir):
        return f"not recorded (flows directory not found: {render_ref(flows_dir)})"
    script = Path(__file__).resolve().parent / "e2e-gate.py"
    try:
        proc = subprocess.run(
            [sys.executable, str(script), "--root", str(root), "--flows", flows_dir, sprint],
            capture_output=True, text=True, timeout=120,
        )
    except OSError as exc:
        return f"e2e-gate.py failed to run: {sanitize_text(str(exc))}"
    tail_lines = [l for l in (proc.stdout or proc.stderr or "").splitlines() if l.strip()]
    tail = tail_lines[-1] if tail_lines else ""
    return f"{sanitize_text(tail)} (exit {proc.returncode})"


def render_doc(sprint, tasks, record, e2e_result, repo_hint):
    lines = [f"# UAT: {sanitize_text(sprint)}", ""]
    lines.append(f"e2e result at the integrated head: {e2e_result}")
    lines.append("")

    for slug in sorted(tasks):
        task = tasks[slug]
        lines.append(f"## {slug} — {sanitize_text(task['title'])}")
        lines.append("")
        lines.append(f"- PR: {render_pr(task['pr'], repo_hint)}")
        lines.append(f"- Validation gate: {task['validation_gate']}")
        lines.append("")

    lines.append("## Questions asked and answered")
    lines.append("")
    questions = record.get("questions") or []
    if questions:
        for q in questions:
            lines.append(
                f"- {sanitize_text(q.get('task', ''))}: {sanitize_text(q.get('question', ''))} "
                f"-> {sanitize_text(q.get('answer', ''))}"
            )
    else:
        lines.append("- none recorded.")
    lines.append("")

    return "\n".join(lines).rstrip("\n") + "\n"


class MissingValidationGate(Exception):
    def __init__(self, slugs):
        super().__init__(", ".join(slugs))
        self.slugs = slugs


def build_doc(sprint, state_dir, root=None, flows=None):
    tasks = load_task_entities(state_dir, sprint)
    if not tasks:
        raise LookupError(f"no docs/dev entities found for sprint {sprint!r} under {state_dir}")

    missing = sorted(slug for slug, t in tasks.items() if t["validation_gate"] != "prepared")
    if missing:
        raise MissingValidationGate(missing)

    record = load_batch_record(state_dir, sprint)

    resolved_root = str(Path(root).resolve()) if root else str(Path(state_dir).resolve())
    readme_path = Path(resolved_root) / "docs" / "ship" / "README.md"
    if not readme_path.is_file():
        readme_path = Path(state_dir) / "docs" / "ship" / "README.md"
    resolved_flows = flows or read_local_profile_row(readme_path, "E2E flows")
    integrated_head = read_local_profile_row(readme_path, "Integrated head")

    e2e_result = run_e2e_gate(resolved_root, resolved_flows, sprint)
    if integrated_head:
        e2e_result = f"[{sanitize_text(integrated_head)}] {e2e_result}"

    repo_hint = resolve_repo_hint(resolved_root)
    return render_doc(sprint, tasks, record, e2e_result, repo_hint)


# --- legacy compatibility -----------------------------------------------
#
# dev-debrief.py and ship-debrief.py dynamically import this module (`_load_uat_doc()`) to reuse
# its plan-flow-batch-dir readers (`find_worker_evidence_files`, `load_defaults_decisions`).
# Both scripts are themselves removal candidates under the cloud-wrapper design ("What leaves
# kc-ship-flow": "spacedock debrief, run by each worker" replaces them) -- that removal is this
# sprint's second task, not this one. Keeping these two functions here, unchanged from the v1
# uat-doc.py they were written against, is scoped compatibility until that removal lands; nothing
# in the rewritten `build_doc`/`main` above calls them.

EVIDENCE_FIELD_RE = re.compile(r"^([A-Z][A-Z0-9_]*):\s?(.*)$")


def parse_evidence_block(text):
    """First '## Evidence' fenced block's top-level 'KEY: value' fields."""
    m = re.search(r"^## Evidence\s*$", text, re.MULTILINE)
    if not m:
        return {}
    body = text[m.end():]
    fields = {}
    for line in body.splitlines():
        fm = EVIDENCE_FIELD_RE.match(line)
        if fm:
            fields.setdefault(fm.group(1), fm.group(2))
    return fields


def find_worker_evidence_files(batch_dir, issue):
    """Files for exactly this issue id: 'worker-evidence-<issue>.md' or
    'worker-evidence-<issue>-<anything>.md', never a longer issue id that
    happens to share this one as a prefix (DEV-9 must not match DEV-90)."""
    import glob as _glob

    pattern = os.path.join(batch_dir, "evidence", f"worker-evidence-{issue}*.md")
    boundary = re.compile(r"^worker-evidence-" + re.escape(issue) + r"(?:[.-]|$)")
    return sorted(p for p in _glob.glob(pattern) if boundary.match(os.path.basename(p)))


def load_defaults_decisions(batch_dir):
    """'- ' and '* ' top-level bullets under the decisions heading; a non-bullet,
    non-blank line continues the previous bullet (a wrapped line)."""
    readme = os.path.join(batch_dir, "README.md")
    if not os.path.isfile(readme):
        return None
    with open(readme, encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"^## Decisions made under `defaults`.*?$", text, re.MULTILINE)
    if not m:
        return None
    rest = text[m.end():]
    next_heading = re.search(r"^## ", rest, re.MULTILINE)
    section = rest[:next_heading.start()] if next_heading else rest

    decisions = []
    current = None
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            if current is not None:
                decisions.append(current)
            current = stripped[2:].strip()
        elif stripped and current is not None:
            current += " " + stripped
    if current is not None:
        decisions.append(current)
    return decisions


def main(argv):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("sprint")
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--root")
    parser.add_argument("--flows")
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2

    try:
        doc = build_doc(args.sprint, args.state_dir, root=args.root, flows=args.flows)
    except MissingValidationGate as exc:
        for slug in exc.slugs:
            print(slug)
        return 1
    except LookupError as exc:
        print(f"uat-doc: {exc}", file=sys.stderr)
        return 2
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"uat-doc: malformed batch record for sprint {args.sprint}: {exc!r}", file=sys.stderr)
        return 2

    sys.stdout.write(doc)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
