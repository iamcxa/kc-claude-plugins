#!/usr/bin/env python3
"""Round-trip the projector's output through the parsers that read it back.

Rendering and parsing live in different repositories' worth of code and nothing
made them agree. `## User value` sat empty in a real project for a day because
plan-lint matches it at offset zero without re.MULTILINE, and the prose that was
supposed to fill it was written by hand three paragraphs down.
"""
import importlib.util, json, pathlib, re, sys

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


P = load("proj", HERE / "project-to-linear.py")
LA = load("la", ROOT / "kc-dev-flow/scripts/linear-admission.py")

# Lifted from plan-lint rather than restated, so this test cannot drift from the rule it checks.
L1_SOURCE = re.search(r're\.search\(r"(\^## User value.+?)", d\["content"\]',
                      (ROOT / "docs/plan-flow/plan-lint.py").read_text())
assert L1_SOURCE, "plan-lint no longer carries a User value rule this test can read"
L1 = re.compile(L1_SOURCE.group(1), re.S)
failures = []


def check(name, condition, why=""):
    print(("PASS " if condition else "FAIL ") + name + (f": {why}" if why else ""))
    if not condition:
        failures.append(name)


VALUE = "A terminal user hands one link to anyone and reads their feedback back without leaving the reader."

content = P.user_value_content("A summary line.\n\n## Who\n\nSomebody.\n", VALUE)
match = L1.match(content)
check("L1 matches at offset zero", bool(match))
check("L1 captures the one line", bool(match) and match.group(1) == VALUE)
check("the prior body survives", "## Who" in content)

again = P.user_value_content(content, VALUE)
check("projecting twice is idempotent", again == content, f"{len(content)} vs {len(again)}")

replaced = P.user_value_content(content, "A different one-line value.")
check("a second run replaces rather than stacks", replaced.count("## User value") == 1)

# Linear strips trailing whitespace on write, so what comes back is not what went out.
# A project whose content is only the user value failed L1 forever until both sides saw that.
stored = P.user_value_content("", VALUE)
check("a lone user value still matches L1", bool(L1.match(stored)))
check("a lone user value has no trailing blank line", stored == stored.rstrip())
check("re-projecting stripped content does not stack",
      P.user_value_content(stored, VALUE).count("## User value") == 1)
check("re-projecting stripped content is stable", P.user_value_content(stored, VALUE) == stored)

milestone = {"integration_proof": {"proof": "Publish from the reader and open the link elsewhere.",
                                  "owner": "Kent"}}
value_issue = {"title": "A terminal user publishes a file and hands out a link that works",
               "acceptance": "On a tap-install machine they publish and a second person comments.",
               "milestone": "A", "kind": "value"}
body = P.issue_body(value_issue, milestone, None)
check("Accepted outcome parses back", LA.section(body, "Accepted outcome") == value_issue["acceptance"])
# The owner is an assignment, not a sentence. Prose cannot be queried or reassigned,
# and it duplicates the assignee field that already carries it.
check("the integration proof does not spell its owner into prose", "Owner:" not in body)
check("a matching assignee does not drift",
      P.issue_drift(body, value_issue, milestone, "Kent") == [])
check("a wrong assignee is drift",
      ("integration proof owner", "Someone Else", "Kent")
      in P.issue_drift(body, value_issue, milestone, "Someone Else"))
check("an unassigned value issue is drift",
      ("integration proof owner", "unassigned", "Kent")
      in P.issue_drift(body, value_issue, milestone, None))

defect = {"title": "A latent walk", "acceptance": "Nothing above the created directory changes mode.",
          "milestone": "A", "kind": "defect", "protects": value_issue["title"]}
declared = P.issue_body(defect, milestone, "DRC-4474")
check("a defect declares what it protects", declared.startswith("**A defect.") and "DRC-4474" in declared)
check("a defect carries no integration proof", "## Integration proof" not in declared)

try:
    LA.live_item({"url": "u", "description": body, "state": {"type": "unstarted"}})
    admitted = True
except LA.AdmissionError:
    admitted = False
check("a plan-value issue is not admission-ready", not admitted,
      "it carries no Non-goals; kc-plan-detail writes those")


# Section-scoped replacement is the whole safety property: a plan owns the sections it
# renders and nothing else, so reconciling must not touch what a person or plan-detail wrote.
LIVE = """**A defect. It delivers no user-visible value on its own; it protects DRC-4474.** Reason.

## Accepted outcome

The old outcome nobody updated.

## Scope

Hand-written, and not the plan's to touch.

## Non-goals

- Something plan-detail wrote.
"""

check("section_body reads a section", P.section_body(LIVE, "Accepted outcome") == "The old outcome nobody updated.")
check("section_body returns None when absent", P.section_body(LIVE, "Integration proof") is None)

fixed = P.replace_section(LIVE, "Accepted outcome", "The current outcome.")
check("replace_section swaps the body", P.section_body(fixed, "Accepted outcome") == "The current outcome.")
check("replace_section keeps later sections", P.section_body(fixed, "Scope") == "Hand-written, and not the plan's to touch.")
check("replace_section keeps the Non-goals bullet", "- Something plan-detail wrote." in fixed)
check("replace_section keeps the leading declaration", fixed.startswith("**A defect."))
check("replace_section still parses through the real reader",
      LA.section(fixed, "Accepted outcome") == "The current outcome.")

missing = LIVE.replace("## Accepted outcome\n\nThe old outcome nobody updated.\n\n", "")
inserted = P.replace_section(missing, "Accepted outcome", "A fresh outcome.")
check("an absent section is inserted, not refused", LA.section(inserted, "Accepted outcome") == "A fresh outcome.")
check("insertion lands before the first existing section", inserted.index("## Accepted outcome") < inserted.index("## Scope"))
check("insertion keeps the leading declaration", inserted.startswith("**A defect."))
check("insertion keeps the trailing sections", LA.section(inserted, "Scope").startswith("Hand-written"))

drifted = P.issue_drift(LIVE, defect, milestone)
check("drift is found on a stale outcome", [d[0] for d in drifted] == ["Accepted outcome"])
check("drift reports both sides", drifted[0][1] == "The old outcome nobody updated."
      and drifted[0][2] == defect["acceptance"])

aligned = P.replace_section(LIVE, "Accepted outcome", defect["acceptance"])
check("a reconciled issue no longer drifts", P.issue_drift(aligned, defect, milestone) == [])

wrong_kind = LIVE.replace("**A defect.", "**A thing.")
check("a lost kind declaration is drift",
      "kind declaration" in [d[0] for d in P.issue_drift(wrong_kind, defect, milestone)])


# Two fields were added to the contract with nothing reading them, which is the same
# shape as a rule that sat unsatisfied for a day because nothing projected into it.
B = [{"rule": "The reader holds no relay knowledge.", "agreed_with": "the maintainer", "agreed_at": "repo#43"}]
bc = P.boundaries_content("## User value\n\nA line.\n\n## Who\n\nSomebody.", B)
check("boundaries render as their own section", LA.section(bc, "Boundaries").startswith("- **The reader"))
check("rendering boundaries keeps the sections around them", LA.section(bc, "Who") == "Somebody.")
check("re-rendering boundaries does not stack", P.boundaries_content(bc, B).count("## Boundaries") == 1)
check("a changed boundary replaces rather than appends",
      P.boundaries_content(bc, [{**B[0], "rule": "A different rule."}]).count("## Boundaries") == 1)

NODES = {
  "first": {"identifier": "AA-1", "inverseRelations": {"nodes": []}},
  "second": {"identifier": "AA-2", "inverseRelations": {"nodes": [{"type": "blocks", "issue": {"identifier": "AA-1"}}]}},
  "third": {"identifier": "AA-3", "inverseRelations": {"nodes": [{"type": "blocks", "issue": {"identifier": "AA-2"}}]}},
}
plan = {"dependencies": [{"blocked": "second", "blocked_by": "first", "because": "a fact"},
                         {"blocked": "third", "blocked_by": "first", "because": "another fact"}]}
missing, extra, unknown = P.dependency_drift(plan, NODES)
check("an edge the plan states and the tracker lacks is missing", missing == [("AA-1", "AA-3", "another fact")])
check("an edge the tracker carries and the plan omits is reported", extra == [("AA-2", "AA-3")])
check("an edge naming an unknown issue is caught",
      P.dependency_drift({"dependencies": [{"blocked": "ghost", "blocked_by": "first", "because": "x"}]}, NODES)[2] != [])

SUB = json.loads((HERE / "fixtures/plan-detail.valid.json").read_text())["sub_issues"][0]
sub_body = P.detail_issue_body(SUB)
check("a sub-issue's Accepted outcome parses back",
      LA.section(sub_body, "Accepted outcome") == SUB["accepted_outcome"])
check("its Non-goals are a '- ' bullet list the reader accepts",
      LA.live_item({"url": "u", "state": {"type": "unstarted"}, "description": sub_body})["non-goals"]
      == SUB["non_goals"])
check("every AC keeps its bullet marker",
      all(line.startswith("- **AC-") for line in LA.section(sub_body, "Acceptance criteria").splitlines()))
check("the Re-verified line carries no colon after the label",
      ":" not in next(l for l in sub_body.splitlines() if l.startswith("Re-verified:"))[len("Re-verified:"):])
check("a fresh sub-issue does not drift from its own document", P.detail_drift(sub_body, SUB) == [])

# Whatever section renders last swallows every trailing line, so a Re-verified line
# placed after the sections lands inside Non-goals and the issue drifts from itself.
for heading in ("Accepted outcome", "Acceptance criteria", "Non-goals"):
    got = LA.section(sub_body, heading)
    check(f"{heading} does not swallow the provenance lines",
          "Re-verified:" not in got and "Supersedes:" not in got)

stored = sub_body.replace("\n- ", "\n* ")
check("a body Linear rewrote to '*' bullets does not drift", P.detail_drift(stored, SUB) == [],
      "otherwise --reconcile writes '- ', Linear rewrites it, and it never converges")

stale = P.replace_section(sub_body, "Non-goals", "- Something else entirely.")
check("a changed Non-goals list is drift", "Non-goals" in [d[0] for d in P.detail_drift(stale, SUB)])
no_line = "\n".join(l for l in sub_body.splitlines() if not l.startswith("Supersedes:"))
check("a missing Supersedes line is drift",
      ("Supersedes line", "absent", SUB["supersedes"]) in P.detail_drift(no_line, SUB))

def refuses(text):
    try:
        P.check_re_verified(text)
    except SystemExit:
        return True
    return False


check("a colon in Re-verified is refused", refuses("Re-verified: git show origin/main:file 2026-09-08"))
check("an issue identifier in Re-verified is refused", refuses("Re-verified: git log DRC-4411 2026-09-08"))
check("a filename the tracker would autolink is refused",
      refuses("Re-verified: git show origin/main for install.sh 2026-09-08"),
      "Linear turns install.sh into a markdown link and its colons break the date parse")
check("a clean Re-verified passes", not refuses("Re-verified: git grep publishKeyBinding at 1ea84f8e 2026-09-08"))

print(f"\n{len(failures)} failed" if failures else "\nall passed")
sys.exit(1 if failures else 0)
