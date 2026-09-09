#!/usr/bin/env python3
"""Project a validated kc-plan-value/v1 document into Linear.

Usage: project-to-linear.py <document.json> <project-id> [--apply|--reconcile] [--cycle <id>]

Dry run by default: prints every write it would make. --apply performs them.
LINEAR_API_KEY must be set for either mode, because both read current state.

The fields with no Linear column of their own -- user_value, acceptance, kind,
protects, boundaries -- are rendered into the markdown shapes that
plan-lint and kc-dev-flow/scripts/linear-admission.py read back. Hand-writing
that shape is what this exists to stop: `## User value` is matched at offset
zero of the project content with no re.MULTILINE, and a `Re-verified:` line is
split on `:` so one colon silently destroys the date.
"""
import json, os, re, subprocess, sys, tempfile, pathlib, urllib.request, urllib.error

HERE = pathlib.Path(__file__).parent
API = "https://api.linear.app/graphql"


def die(msg):
    print(f"REFUSED: {msg}")
    sys.exit(1)


def gql(query, variables=None):
    key = os.environ.get("LINEAR_API_KEY")
    if not key:
        die("LINEAR_API_KEY is not set")
    request = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except (urllib.error.HTTPError, OSError, ValueError) as exc:
        die(f"Linear transport refused: {exc}")
    if payload.get("errors"):
        die(f"Linear returned errors: {payload['errors']}")
    return payload["data"]


def validate(path):
    import importlib.util

    spec = importlib.util.spec_from_file_location("vc", HERE / "validate-contract.py")
    module = importlib.util.module_from_spec(spec)
    argv = sys.argv
    sys.argv = ["validate-contract.py", str(path)]
    try:
        spec.loader.exec_module(module)
    except SystemExit as exc:
        if exc.code:
            die("document did not validate; fix it before projecting")
    finally:
        sys.argv = argv


def check_re_verified(text):
    for line in text.splitlines():
        if not line.startswith("Re-verified:"):
            continue
        body = line[len("Re-verified:"):]
        if ":" in body:
            die(f"Re-verified line carries a colon, which breaks the date parse: {line}")
        if re.search(r"\b[A-Z][A-Z0-9]*-\d+\b", body):
            die(f"Re-verified line names an issue, which the tracker rewrites into a link: {line}")
        bare = re.search(r"\b\w+\.(?:sh|com|io|net|org|app|dev|md|ts|go|py)\b", body)
        if bare:
            die(f"Re-verified line carries {bare.group(0)!r}, which the tracker autolinks into a URL "
                f"whose colons then break the date parse: {line}")


def comparable(text):
    # Linear rewrites a "- " bullet to "* " on write, so a document rendering "- " would
    # drift from itself forever and --reconcile would never converge. Both readers accept
    # either marker, so the difference is not a difference.
    return "\n".join(re.sub(r"^[-*] ", "- ", line.rstrip()) for line in (text or "").splitlines()).strip()


def section_body(text, heading):
    matches = list(re.finditer(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE))
    if len(matches) != 1:
        return None
    start = matches[0].end()
    following = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + following.start() if following else len(text)
    return text[start:end].strip()


def replace_section(text, heading, body):
    matches = list(re.finditer(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE))
    if not matches:
        first = re.search(r"^##\s+", text, re.MULTILINE)
        block = f"## {heading}\n\n{body}\n\n"
        return text[:first.start()] + block + text[first.start():] if first else \
            (text.rstrip() + "\n\n" + block).strip()
    if len(matches) != 1:
        die(f"cannot reconcile {heading!r}: the description carries {len(matches)} of them")
    start = matches[0].end()
    following = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + following.start() if following else len(text)
    return text[:start] + "\n\n" + body + ("\n\n" if following else "\n") + text[end:]


def owned_sections(issue, milestone):
    return {"Accepted outcome": issue["acceptance"]}


def issue_drift(live_description, issue, milestone, assignee=None):
    drifted = []
    planned_assignee = issue.get("assignee")
    if issue["kind"] == "value" and (assignee or "") != (planned_assignee or ""):
        drifted.append(("acceptance owner", assignee or "unassigned",
                        planned_assignee or "someone who is not building underneath it"))
    for heading, planned in owned_sections(issue, milestone).items():
        found = section_body(live_description, heading)
        if found is None:
            drifted.append((heading, "absent or duplicated", planned))
        elif comparable(found) != comparable(planned):
            drifted.append((heading, found, planned))
    if issue["kind"] != "value":
        first = live_description.strip().split("\n\n")[0]
        if not first.startswith(f"**A {issue['kind']}."):
            drifted.append(("kind declaration", first[:60], f"**A {issue['kind']}. ..."))
    return drifted


def user_value_content(current, user_value):
    if "\n" in user_value.strip():
        die("user_value must be one line")
    block = f"## User value\n\n{user_value}\n"
    body = current or ""
    match = re.match(r"^## User value\n\n.+?(?:\n\n|\Z)", body, re.S)
    rest = body[match.end():] if match else body
    rest = rest.lstrip("\n")
    return (block + "\n" + rest).rstrip() if rest else block.rstrip()


def boundaries_content(current, boundaries):
    block = "## Boundaries\n\n" + "\n\n".join(
        f"- **{b['rule']}**\n  Agreed with {b['agreed_with']}, {b['agreed_at']}."
        for b in boundaries)
    body = current or ""
    match = re.search(r"^## Boundaries\n.*?(?=^## |\Z)", body, re.S | re.M)
    if match:
        return (body[:match.start()] + block + "\n\n" + body[match.end():]).rstrip()
    return (body.rstrip() + "\n\n" + block).strip()


def dependency_drift(plan, existing):
    # An edge the plan states but the tracker does not carry is a plan nobody can act on.
    # An edge the tracker carries and the plan does not is reported, never deleted: it may
    # be a fact someone learned after the document was written.
    by_title = {t: n for t, n in existing.items()}
    live = set()
    for title, node in by_title.items():
        for rel in (node.get("inverseRelations") or {}).get("nodes", []):
            if rel["type"] == "blocks":
                live.add((rel["issue"]["identifier"], node["identifier"]))
    ident = {t: n["identifier"] for t, n in by_title.items()}
    missing, unknown = [], []
    planned = set()
    for edge in plan.get("dependencies", []):
        a, b = ident.get(edge["blocked_by"]), ident.get(edge["blocked"])
        if not (a and b):
            unknown.append(edge)
            continue
        planned.add((a, b))
        if (a, b) not in live:
            missing.append((a, b, edge["because"]))
    extra = sorted(live - planned)
    return missing, extra, unknown


def issue_body(issue, milestone, value_identifier):
    parts = []
    if issue.get("user_story"):
        parts.append(issue["user_story"])
    if issue["kind"] != "value":
        noun = "defect" if issue["kind"] == "defect" else "measurement"
        target = value_identifier or issue.get("protects", "")
        parts.append(
            f"**A {noun}. It delivers no user-visible value on its own; it protects "
            f"{target}.**"
        )
    parts.append("## Accepted outcome\n\n" + issue["acceptance"])
    body = "\n\n".join(parts)
    check_re_verified(body)
    return body


def detail_issue_body(sub):
    body = "\n\n".join([
        f"**The gap:** {sub['gap']}",
        f"Re-verified: {sub['re_verified']}",
        f"Supersedes: {sub['supersedes']}",
        "## Accepted outcome\n\n" + sub["accepted_outcome"],
        "## Acceptance criteria\n\n" + "\n".join(sub["acceptance"]),
        "## Non-goals\n\n" + "\n".join(f"- {item}" for item in sub["non_goals"]),
    ])
    check_re_verified(body)
    return body


def detail_owned(sub):
    return {
        "Accepted outcome": sub["accepted_outcome"],
        "Acceptance criteria": "\n".join(sub["acceptance"]),
        "Non-goals": "\n".join(f"- {item}" for item in sub["non_goals"]),
    }


def detail_drift(live, sub):
    drifted = []
    for heading, planned in detail_owned(sub).items():
        found = section_body(live, heading)
        if found is None:
            drifted.append((heading, "absent or duplicated", planned))
        elif comparable(found) != comparable(planned):
            drifted.append((heading, found, planned))
    for label, value in (("Re-verified", sub["re_verified"]), ("Supersedes", sub["supersedes"])):
        line = next((l for l in live.splitlines() if l.startswith(f"{label}:")), None)
        if line is None:
            drifted.append((f"{label} line", "absent", value))
        elif line[len(label) + 1:].strip() != value.strip():
            drifted.append((f"{label} line", line[len(label) + 1:].strip(), value))
    return drifted


USERS_Q = """query { users(first: 100) { nodes { id name } } }"""

PROJECT_Q = """query($id: String!) { project(id: $id) {
  id name content
  projectMilestones(first: 50) { nodes { id name targetDate description } }
  issues(first: 250) { nodes { id identifier title description assignee { name } } } } }"""

RELATIONS_Q = """query($ids: [ID!]) { issues(filter: {id: {in: $ids}}) { nodes { identifier
  inverseRelations(first: 20) { nodes { type issue { identifier } } } } } }"""


def run_lint(project_id, expected_receipt):
    root = HERE.parent.parent
    lint = root / "docs/plan-flow/plan-lint.py"
    if not lint.is_file():
        print("plan-lint is not in this checkout; the receipt is unverified")
        return
    with tempfile.NamedTemporaryFile(suffix=".json") as snapshot:
        fetch = subprocess.run([sys.executable, str(lint), "fetch", project_id, snapshot.name],
                               cwd=root, capture_output=True, text=True)
        if fetch.returncode:
            print(f"plan-lint fetch failed; the receipt is unverified: {fetch.stderr.strip()[:200]}")
            return
        run = subprocess.run([sys.executable, str(lint), "lint", snapshot.name],
                             cwd=root, capture_output=True, text=True)
    tail = [l for l in run.stdout.splitlines() if l.startswith("LINT ")]
    if not tail:
        print("plan-lint produced no verdict; the receipt is unverified")
        return
    verdict = tail[-1]
    receipt = re.search(r"receipt ([0-9a-f]+)", verdict)
    receipt = receipt.group(1) if receipt else ""
    print(f"\n{verdict.split('| order')[0].strip()}")
    if receipt == expected_receipt:
        print(f"receipt matches the document: {receipt}")
    else:
        print(f"RECEIPT MISMATCH: the document claims {expected_receipt}, the tracker produced {receipt}")
        print("The document was written against a different state. Re-lint and update it before it is quoted.")


def project_detail(plan, project_id, apply, reconcile, cycle_id):
    project = gql(PROJECT_Q, {"id": project_id})["project"]
    if not project:
        die(f"no project {project_id}")
    nodes = project["issues"]["nodes"]
    parent = next((n for n in nodes if n["title"] == plan["value_issue"]), None)
    if not parent:
        die(f"no issue titled {plan['value_issue']!r} in this project; kc-plan-value writes it first")
    existing = {n["title"]: n for n in nodes}

    for finding in plan["archaeology"]:
        print(f"      archaeology {finding['classification']:22} at {finding['ref']}  {finding['question'][:70]}")

    writes = []
    for sub in plan["sub_issues"]:
        if sub["title"] in existing:
            node = existing[sub["title"]]
            drifted = detail_drift(node["description"] or "", sub)
            writes.append((("sub-issue DRIFT" if drifted else "sub-issue aligned"), node["identifier"],
                           {"detail": drifted} if drifted else sub["title"]))
        else:
            writes.append(("sub-issue create", parent["identifier"],
                           {"title": sub["title"], "description": detail_issue_body(sub)}))

    for kind, target, payload in writes:
        summary = payload if isinstance(payload, str) else json.dumps(payload)[:150]
        print(f"{'APPLY' if apply else 'DRY  '} {kind:24} {target:44} {summary}")
        if kind == "sub-issue DRIFT":
            for heading, live, planned in payload["detail"]:
                print(f"      {heading}\n        live    {live[:110]}\n        planned {planned[:110]}")

    created = sum(1 for k, _, _ in writes if k == "sub-issue create")
    drifting = sum(1 for k, _, _ in writes if k.endswith("DRIFT"))
    admitted = "into a cycle" if cycle_id else "with no cycle"
    print(f"\n{created} sub-issues to create {admitted}, {drifting} drifting, under {parent['identifier']}.")
    if not cycle_id:
        print("plan-lint judges only admitted issues, so these stay unexamined until a cycle takes them.")
        print("Pass --cycle <id> to admit them, or record them in the document's lint.unjudged.")
    if drifting and not reconcile:
        print("Drift is reported, never repaired by default. Re-run with --reconcile.")

    if not apply:
        print("\nDry run. Re-run with --apply to create, or --reconcile to also repair drift.")
        return 0

    team = gql("query($id: String!) { project(id: $id) { teams(first: 1) { nodes { id } } } }",
               {"id": project_id})["project"]["teams"]["nodes"]
    if not team:
        die("project has no team, so sub-issues cannot be created")
    parent_node = gql("query($i: String!) { issue(id: $i) { id projectMilestone { id } } }",
                      {"i": parent["identifier"]})["issue"]
    for kind, target, payload in writes:
        if kind == "sub-issue create":
            people = {u["name"]: u["id"] for u in gql(USERS_Q)["users"]["nodes"]}
            fields = {"teamId": team[0]["id"], "projectId": project_id, "parentId": parent_node["id"],
                      "title": payload["title"], "description": payload["description"]}
            if parent_node["projectMilestone"]:
                fields["projectMilestoneId"] = parent_node["projectMilestone"]["id"]
            if cycle_id:
                fields["cycleId"] = cycle_id
            gql("mutation($f: IssueCreateInput!) { issueCreate(input: $f) { issue { identifier } } }", {"f": fields})
        elif kind == "sub-issue DRIFT":
            if not reconcile:
                print(f"left  {kind:24} {target}")
                continue
            node = gql("query($i: String!) { issue(id: $i) { id description } }", {"i": target})["issue"]
            body = node["description"] or ""
            for heading, _, planned in payload["detail"]:
                if heading.endswith(" line"):
                    label = heading[:-5]
                    lines = [l for l in body.splitlines() if not l.startswith(f"{label}:")]
                    body = "\n".join(lines).rstrip() + f"\n\n{label}: {planned}"
                else:
                    body = replace_section(body, heading, planned)
            gql("mutation($i: String!, $d: String!) { issueUpdate(id: $i, input: {description: $d}) { success } }",
                {"i": node["id"], "d": body})
        else:
            continue
        print(f"done  {kind:24} {target}")

    run_lint(project_id, plan["lint"]["receipt"])
    return 0


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    document, project_id = pathlib.Path(sys.argv[1]), sys.argv[2]
    flags = sys.argv[3:]
    apply = "--apply" in flags
    reconcile = "--reconcile" in flags
    apply = apply or reconcile
    validate(document)
    plan = json.loads(document.read_text())
    cycle_id = next((flags[i + 1] for i, f in enumerate(flags) if f == "--cycle" and i + 1 < len(flags)), None)
    if plan["schema"] == "kc-plan-detail/v1":
        return project_detail(plan, project_id, apply, reconcile, cycle_id)
    if plan["schema"] != "kc-plan-value/v1":
        die(f"this projects kc-plan-value/v1 and kc-plan-detail/v1, not {plan['schema']}")

    project = gql(PROJECT_Q, {"id": project_id})["project"]
    if not project:
        die(f"no project {project_id}")
    existing = {n["title"]: n for n in project["issues"]["nodes"]}
    existing_titles = {t: n["identifier"] for t, n in existing.items()}
    existing_milestones = {n["name"]: n for n in project["projectMilestones"]["nodes"]}

    writes = []
    content = user_value_content(project["content"], plan["project"]["user_value"])
    content = boundaries_content(content, plan["project"]["boundaries"])
    if content != (project["content"] or ""):
        kind = "project content" if not (project["content"] or "").strip() else "project content DRIFT"
        writes.append((kind, project_id, {"content": content}))

    for milestone in plan["milestones"]:
        found = existing_milestones.get(milestone["name"])
        fields = {
            "name": milestone["name"],
            "targetDate": milestone["target"],
            "description": milestone["description"],
        }
        if not found:
            writes.append(("milestone create", milestone["name"], fields))
        else:
            differs = [k for k in ("targetDate", "description") if found.get(k) != fields[k]]
            if differs:
                was = {k: found.get(k) for k in differs}
                writes.append(("milestone DRIFT", found["id"], {**fields, "live": was}))

    by_milestone = {m["name"]: m for m in plan["milestones"]}
    value_identifier = None
    for issue in plan["issues"]:
        if issue["kind"] == "value":
            value_identifier = existing_titles.get(issue["title"])
    for issue in plan["issues"]:
        milestone = by_milestone.get(issue["milestone"])
        if not milestone:
            die(f"issue {issue['title']!r} names milestone {issue['milestone']!r}, which the document does not define")
        if issue["kind"] != "value" and not issue.get("protects"):
            die(f"a {issue['kind']} must name the value issue it protects: {issue['title']!r}")
        body = issue_body(issue, milestone, value_identifier)
        if issue.get("identifier") and issue["identifier"] not in {n["identifier"] for n in project["issues"]["nodes"]}:
            die(f"{issue['identifier']} is named in the plan and absent from the project. An identifier "
                "does not go stale the way a title does; fix the plan rather than creating a second issue.")
        if issue["title"] in existing:
            node = existing[issue["title"]]
            drifted = issue_drift(node["description"] or "", issue, milestone,
                                  (node.get("assignee") or {}).get("name"))
            if drifted:
                writes.append(("issue DRIFT", node["identifier"],
                               {"sections": [d[0] for d in drifted], "detail": drifted}))
            else:
                writes.append(("issue aligned", node["identifier"], issue["title"]))
        else:
            # Creating an issue is the irreversible half. The draft-first rule was written into
            # the skill and then broken by its own author within the hour, so it is checked here.
            ruling = plan.get("captain_ruling") or {}
            if not ruling.get("ruled_on"):
                die(f"no captain ruling recorded, so {issue['title']!r} would be created from a draft "
                    "nobody saw. Put the draft in front of them, record what they ruled, then run this again.")
            writes.append(("issue create", issue["milestone"],
                           {"title": issue["title"], "description": body,
                            "assignee": issue.get("assignee")}))

    # Relations are fetched only for the issues the plan names: asking for them across a
    # whole project exceeded the provider's query complexity limit at 250 by 20.
    named = {e[k] for e in plan.get("dependencies", []) for k in ("blocked", "blocked_by")}
    wanted = [existing[t]["id"] for t in named if t in existing]
    relations = {}
    if wanted:
        for node in gql(RELATIONS_Q, {"ids": wanted})["issues"]["nodes"]:
            relations[node["identifier"]] = node["inverseRelations"]
    for title, node in existing.items():
        node["inverseRelations"] = relations.get(node["identifier"], {"nodes": []})
    missing, extra, unknown = dependency_drift(plan, existing)
    for a, b, because in missing:
        writes.append(("dependency missing", f"{a} blocks {b}", because))
    for a, b in extra:
        writes.append(("dependency unstated", f"{a} blocks {b}",
                       "carried by the tracker and absent from the plan; reported, never deleted"))
    for edge in unknown:
        die(f"dependency names an issue this document does not define: {edge['blocked_by']!r} -> {edge['blocked']!r}")

    # The plan was walked and the tracker was not, so a section the contract deleted stayed on
    # a live issue unreported, and two issues closed by hand had no projector path at all.
    planned_titles = {i["title"] for i in plan["issues"]}
    owned_headings = {"Accepted outcome"}
    for title, node in existing.items():
        if title in planned_titles:
            continue
        body = node.get("description") or ""
        strays = [h for h in ("Integration proof",) if section_body(body, h) is not None]
        if strays:
            writes.append(("tracker only, stale section", node["identifier"],
                           f"carries {strays} which this contract no longer defines"))
    for issue in plan["issues"]:
        node = existing.get(issue["title"])
        if not node:
            continue
        body = node.get("description") or ""
        strays = [h for h in ("Integration proof",)
                  if h not in owned_headings and section_body(body, h) is not None]
        if strays:
            writes.append(("stale section", node["identifier"],
                           f"carries {strays} which this contract no longer defines"))

    for kind, target, payload in writes:
        summary = payload if isinstance(payload, str) else json.dumps(payload)[:150]
        print(f"{'APPLY' if apply else 'DRY  '} {kind:24} {target:44} {summary}")
        if kind == "issue DRIFT":
            for heading, live, planned in payload["detail"]:
                print(f"      {heading}\n        live    {live[:110]}\n        planned {planned[:110]}")

    created = sum(1 for k, _, _ in writes if k == "issue create")
    drifting = [w for w in writes if "DRIFT" in w[0]]
    print(f"\n{created} issues to create, {len(drifting)} drifting, 0 admitted to a cycle.")
    print("plan-lint judges only admitted issues, so these are unexamined until a cycle takes them.")
    print("They carry no Non-goals and no acceptance criteria either; kc-plan-detail writes those.")
    if drifting and not reconcile:
        print("\nDrift is reported, never repaired by default. The plan owns only the sections it")
        print("renders; the rest of a description belongs to kc-plan-detail or to a person.")
        print("Re-run with --reconcile to replace those sections and nothing else.")

    if not apply:
        print("\nDry run. Re-run with --apply to create, or --reconcile to also repair drift.")
        return 0

    team = gql("query($id: String!) { project(id: $id) { teams(first: 1) { nodes { id } } } }",
               {"id": project_id})["project"]["teams"]["nodes"]
    if not team:
        die("project has no team, so issues cannot be created")
    team_id = team[0]["id"]
    milestone_ids = {name: node["id"] for name, node in existing_milestones.items()}

    for kind, target, payload in writes:
        if kind in ("project content", "project content DRIFT"):
            if kind.endswith("DRIFT") and not reconcile:
                print(f"left  {kind:24} {target}")
                continue
            gql("mutation($i: String!, $c: String!) { projectUpdate(id: $i, input: {content: $c}) { success } }",
                {"i": target, "c": payload["content"]})
        elif kind == "milestone create":
            node = gql("mutation($p: String!, $n: String!, $t: TimelessDate, $d: String) {"
                       " projectMilestoneCreate(input: {projectId: $p, name: $n, targetDate: $t, description: $d})"
                       " { projectMilestone { id } } }",
                       {"p": project_id, "n": payload["name"], "t": payload["targetDate"],
                        "d": payload["description"]})
            milestone_ids[payload["name"]] = node["projectMilestoneCreate"]["projectMilestone"]["id"]
        elif kind == "milestone DRIFT":
            if not reconcile:
                print(f"left  {kind:24} {target}")
                continue
            gql("mutation($i: String!, $t: TimelessDate, $d: String) {"
                " projectMilestoneUpdate(id: $i, input: {targetDate: $t, description: $d}) { success } }",
                {"i": target, "t": payload["targetDate"], "d": payload["description"]})
        elif kind == "issue DRIFT":
            if not reconcile:
                print(f"left  {kind:24} {target}")
                continue
            node = gql("query($i: String!) { issue(id: $i) { id description } }", {"i": target})["issue"]
            body = node["description"] or ""
            for heading, _, planned in payload["detail"]:
                if heading in ("kind declaration", "acceptance owner"):
                    die(f"{target}: {heading} is not a section. Set the assignee, or fix the plan.")
                planned = planned
                body = replace_section(body, heading, planned)
            gql("mutation($i: String!, $d: String!) { issueUpdate(id: $i, input: {description: $d}) { success } }",
                {"i": node["id"], "d": body})
        elif kind == "dependency missing":
            a, b = target.split(" blocks ")
            ids = {n["identifier"]: n["id"] for n in project["issues"]["nodes"]}
            gql("mutation($a: String!, $b: String!) { issueRelationCreate("
                "input: {issueId: $a, relatedIssueId: $b, type: blocks}) { success } }",
                {"a": ids[a], "b": ids[b]})
        elif kind in ("dependency unstated", "issue aligned", "stale section", "tracker only, stale section"):
            continue
        elif kind == "issue create":
            people = {u["name"]: u["id"] for u in gql(USERS_Q)["users"]["nodes"]}
            milestone_id = milestone_ids.get(target)
            if not milestone_id:
                die(f"milestone {target!r} has no id, so {payload['title']!r} cannot be placed")
            fields = {"teamId": team_id, "projectId": project_id, "projectMilestoneId": milestone_id,
                      "title": payload["title"], "description": payload["description"]}
            if payload.get("assignee"):
                who = people.get(payload["assignee"])
                if not who:
                    die(f"the tracker has no member named {payload['assignee']!r}; an assignee that "
                        "cannot be resolved would create an issue nobody runs the acceptance for")
                fields["assigneeId"] = who
            gql("mutation($f: IssueCreateInput!) { issueCreate(input: $f) { issue { identifier } } }",
                {"f": fields})
        print(f"done  {kind:22} {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
