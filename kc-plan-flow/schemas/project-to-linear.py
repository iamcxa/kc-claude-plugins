#!/usr/bin/env python3
"""Project a validated kc-plan-value/v1 document into Linear.

Usage: project-to-linear.py <document.json> <project-id> [--apply]

Dry run by default: prints every write it would make. --apply performs them.
LINEAR_API_KEY must be set for either mode, because both read current state.

The fields with no Linear column of their own -- user_value, acceptance, kind,
protects, integration_proof -- are rendered into the markdown shapes that
plan-lint and kc-dev-flow/scripts/linear-admission.py read back. Hand-writing
that shape is what this exists to stop: `## User value` is matched at offset
zero of the project content with no re.MULTILINE, and a `Re-verified:` line is
split on `:` so one colon silently destroys the date.
"""
import json, os, re, sys, pathlib, urllib.request, urllib.error

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
    owned = {"Accepted outcome": issue["acceptance"]}
    if issue["kind"] == "value":
        proof = milestone["integration_proof"]
        owned["Integration proof"] = f"{proof['proof']}\n\n**Owner: {proof['owner']}.**"
    return owned


def issue_drift(live_description, issue, milestone):
    drifted = []
    for heading, planned in owned_sections(issue, milestone).items():
        found = section_body(live_description, heading)
        if found is None:
            drifted.append((heading, "absent or duplicated", planned))
        elif found.strip() != planned.strip():
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


def issue_body(issue, milestone, value_identifier):
    parts = []
    if issue["kind"] != "value":
        noun = "defect" if issue["kind"] == "defect" else "measurement"
        target = value_identifier or issue.get("protects", "")
        parts.append(
            f"**A {noun}. It delivers no user-visible value on its own; it protects "
            f"{target}.** It is an issue rather than a sub-issue for that reason."
        )
    parts.append("## Accepted outcome\n\n" + issue["acceptance"])
    if issue["kind"] == "value":
        proof = milestone["integration_proof"]
        parts.append(
            "## Integration proof\n\n"
            f"{proof['proof']}\n\n**Owner: {proof['owner']}.**"
        )
    body = "\n\n".join(parts)
    check_re_verified(body)
    return body


PROJECT_Q = """query($id: String!) { project(id: $id) {
  id name content
  projectMilestones(first: 50) { nodes { id name targetDate description } }
  issues(first: 250) { nodes { id identifier title description } } } }"""


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
    if plan["schema"] != "kc-plan-value/v1":
        die(f"this projects kc-plan-value/v1, not {plan['schema']}")

    project = gql(PROJECT_Q, {"id": project_id})["project"]
    if not project:
        die(f"no project {project_id}")
    existing = {n["title"]: n for n in project["issues"]["nodes"]}
    existing_titles = {t: n["identifier"] for t, n in existing.items()}
    existing_milestones = {n["name"]: n for n in project["projectMilestones"]["nodes"]}

    writes = []
    content = user_value_content(project["content"], plan["project"]["user_value"])
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
        if issue["title"] in existing:
            node = existing[issue["title"]]
            drifted = issue_drift(node["description"] or "", issue, milestone)
            if drifted:
                writes.append(("issue DRIFT", node["identifier"],
                               {"sections": [d[0] for d in drifted], "detail": drifted}))
            else:
                writes.append(("issue aligned", node["identifier"], issue["title"]))
        else:
            writes.append(("issue create", issue["milestone"], {"title": issue["title"], "description": body}))

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
                if heading == "kind declaration":
                    die(f"{target} has lost its kind declaration; repair that by hand, not by section replace")
                planned = planned
                body = replace_section(body, heading, planned)
            gql("mutation($i: String!, $d: String!) { issueUpdate(id: $i, input: {description: $d}) { success } }",
                {"i": node["id"], "d": body})
        elif kind == "issue aligned":
            continue
        elif kind == "issue create":
            milestone_id = milestone_ids.get(target)
            if not milestone_id:
                die(f"milestone {target!r} has no id, so {payload['title']!r} cannot be placed")
            gql("mutation($t: String!, $p: String!, $m: String!, $ti: String!, $d: String!) {"
                " issueCreate(input: {teamId: $t, projectId: $p, projectMilestoneId: $m,"
                " title: $ti, description: $d}) { issue { identifier } } }",
                {"t": team_id, "p": project_id, "m": milestone_id,
                 "ti": payload["title"], "d": payload["description"]})
        print(f"done  {kind:22} {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
