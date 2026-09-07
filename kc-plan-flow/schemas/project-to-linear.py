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
  issues(first: 250) { nodes { id identifier title } } } }"""


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    document, project_id = pathlib.Path(sys.argv[1]), sys.argv[2]
    apply = "--apply" in sys.argv[3:]
    validate(document)
    plan = json.loads(document.read_text())
    if plan["schema"] != "kc-plan-value/v1":
        die(f"this projects kc-plan-value/v1, not {plan['schema']}")

    project = gql(PROJECT_Q, {"id": project_id})["project"]
    if not project:
        die(f"no project {project_id}")
    existing_titles = {n["title"]: n["identifier"] for n in project["issues"]["nodes"]}
    existing_milestones = {n["name"]: n for n in project["projectMilestones"]["nodes"]}

    writes = []
    content = user_value_content(project["content"], plan["project"]["user_value"])
    if content != (project["content"] or ""):
        writes.append(("project content", project_id, {"content": content}))

    for milestone in plan["milestones"]:
        found = existing_milestones.get(milestone["name"])
        fields = {
            "name": milestone["name"],
            "targetDate": milestone["target"],
            "description": milestone["description"],
        }
        if not found:
            writes.append(("milestone create", milestone["name"], fields))
        elif any(found.get(k) != v for k, v in
                 (("targetDate", fields["targetDate"]), ("description", fields["description"]))):
            writes.append(("milestone update", found["id"], fields))

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
        if issue["title"] in existing_titles:
            writes.append(("issue exists, skipped", existing_titles[issue["title"]], issue["title"]))
        else:
            writes.append(("issue create", issue["milestone"], {"title": issue["title"], "description": body}))

    for kind, target, payload in writes:
        summary = payload if isinstance(payload, str) else json.dumps(payload)[:160]
        print(f"{'APPLY' if apply else 'DRY  '} {kind:22} {target:44} {summary}")

    created = sum(1 for k, _, _ in writes if k == "issue create")
    print(f"\n{created} issues to create, 0 admitted to a cycle.")
    print("plan-lint judges only admitted issues, so these are unexamined until a cycle takes them.")
    print("They carry no Non-goals and no acceptance criteria either; kc-plan-detail writes those.")

    if not apply:
        print("\nDry run. Re-run with --apply to perform these writes.")
        return 0

    team = gql("query($id: String!) { project(id: $id) { teams(first: 1) { nodes { id } } } }",
               {"id": project_id})["project"]["teams"]["nodes"]
    if not team:
        die("project has no team, so issues cannot be created")
    team_id = team[0]["id"]
    milestone_ids = {name: node["id"] for name, node in existing_milestones.items()}

    for kind, target, payload in writes:
        if kind == "project content":
            gql("mutation($i: String!, $c: String!) { projectUpdate(id: $i, input: {content: $c}) { success } }",
                {"i": target, "c": payload["content"]})
        elif kind == "milestone create":
            node = gql("mutation($p: String!, $n: String!, $t: TimelessDate, $d: String) {"
                       " projectMilestoneCreate(input: {projectId: $p, name: $n, targetDate: $t, description: $d})"
                       " { projectMilestone { id } } }",
                       {"p": project_id, "n": payload["name"], "t": payload["targetDate"],
                        "d": payload["description"]})
            milestone_ids[payload["name"]] = node["projectMilestoneCreate"]["projectMilestone"]["id"]
        elif kind == "milestone update":
            gql("mutation($i: String!, $t: TimelessDate, $d: String) {"
                " projectMilestoneUpdate(id: $i, input: {targetDate: $t, description: $d}) { success } }",
                {"i": target, "t": payload["targetDate"], "d": payload["description"]})
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
