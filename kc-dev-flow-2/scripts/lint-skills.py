#!/usr/bin/env python3
"""Read-only checks for declared routes; this is not a runtime skill loader."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess

VARIANT = "kc-dev-flow-2"
STAGES = ("ideation", "implementation", "validation")
PROFILES = ("poc", "pilot", "prod")
ROLES = ("science-officer", "chief-engineer")
DEFAULT_ROOT = Path(__file__).resolve().parents[1]
BASIC_LINT = DEFAULT_ROOT.parent / "scripts/skill-frontmatter-lint.sh"
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
NAMESPACE = re.compile(r"\bkc-dev-flow(?:-[a-z0-9]+)*:[a-z0-9-]+\b")


def lint_tree(root, basic_lint=BASIC_LINT):
    """Validate the scaffold's declared schema, without interpreting rule prose."""
    root = Path(root).resolve()
    errors = []

    def read(path):
        try:
            if not path.resolve().is_relative_to(root):
                raise ValueError("reference escapes the variant tree")
            text = path.read_text(encoding="utf-8")
            if not text.strip():
                raise ValueError("empty required file")
            return text
        except (OSError, ValueError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
            return ""

    if not root.is_dir():
        return [f"variant directory missing: {root}"]
    if not Path(basic_lint).is_file():
        errors.append(f"repository frontmatter check missing: {basic_lint}")
    else:
        result = subprocess.run(
            ["bash", str(basic_lint)],
            env={**os.environ, "REPO_DIR_OVERRIDE": str(root)},
            capture_output=True, text=True, check=False,
        )
        if result.returncode:
            errors.append("frontmatter: " + (result.stderr or result.stdout).strip())

    skills = {p.name for p in (root / "skills").glob("*") if p.is_dir()}
    required = set(STAGES + ROLES + ("maintain-flow",))
    if missing := required - skills:
        errors.append("missing skills: " + ", ".join(sorted(missing)))
    read(root / "README.md")
    for skill in sorted(skills):
        path = root / "skills" / skill / "SKILL.md"
        body = read(path)
        calls = re.findall(r"^Invocation: `([^`]+)`$", body, re.MULTILINE)
        if calls != [f"{VARIANT}:{skill}"]:
            errors.append(f"{skill}: expected one exact variant Invocation")
    for path in sorted(root.rglob("*.md")):
        for call in NAMESPACE.findall(read(path)):
            if call not in {f"{VARIANT}:{skill}" for skill in skills}:
                errors.append(f"{path.relative_to(root)}: unknown variant skill {call}")

    for stage in STAGES:
        folder = root / "skills" / stage
        body = read(folder / "SKILL.md")
        read(folder / "principles.md")
        if "principles.md" not in LINK.findall(body):
            errors.append(f"{stage}: missing link to stage principles.md")
        start, end = "<!-- profile-routes -->", "<!-- /profile-routes -->"
        if (body.count(start) != 1 or body.count(end) != 1
                or body.index(start) >= body.index(end)):
            errors.append(f"{stage}: expected one ordered profile routing table")
            continue
        table = body.split(start)[1].split(end)[0].strip().splitlines()
        header = "| Profile | Availability | Profile principles | Stage reference |"
        if len(table) < 3 or table[0] != header:
            errors.append(f"{stage}: invalid profile table columns")
            continue
        separator = [cell.strip() for cell in table[1].strip().strip("|").split("|")]
        if len(separator) != 4 or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator):
            errors.append(f"{stage}: invalid profile table separator")
            continue
        rows = {}
        for line in table[2:]:
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) != 4 or cells[0] not in PROFILES:
                errors.append(f"{stage}: invalid profile row {line}")
                continue
            profile, availability, shared, specific = cells
            if profile in rows:
                errors.append(f"{stage}: duplicate profile {profile}")
            rows[profile] = True
            expected = "skip" if (stage, profile) == ("ideation", "poc") else "active"
            if availability != expected:
                errors.append(f"{stage}/{profile}: availability must be {expected}")
            for cell, target in (
                (shared, root / "references/profiles" / f"{profile}.md"),
                (specific, folder / "profiles" / f"{profile}.md"),
            ):
                match = LINK.fullmatch(cell)
                if not match or (folder / match[1]).resolve() != target:
                    errors.append(f"{stage}/{profile}: route must link to {target.relative_to(root)}")
                read(target)
        if set(rows) != set(PROFILES):
            errors.append(f"{stage}: profile coverage must be poc, pilot, prod")

    for role in ROLES:
        body = read(root / "agents" / f"{role}.md")
        fields = dict(re.findall(r"^(skills|model|reasoning): (.+)$", body, re.MULTILINE))
        try:
            calls = json.loads(fields.get("skills", "null"))
        except json.JSONDecodeError:
            calls = None
        if calls != [f"{VARIANT}:{role}"]:
            errors.append(f"{role} agent: expected exact variant skill binding")
        if (fields.get("model"), fields.get("reasoning")) != ("opus", "xhigh"):
            errors.append(f"{role} agent: existing opus/xhigh policy changed")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT,
                        help="variant tree to check; defaults to this scaffold")
    args = parser.parse_args()
    errors = lint_tree(args.root)
    if errors:
        for error in errors:
            print("FAIL:", error)
        return 1
    print("PASS: basic frontmatter, declared profile routes and role bindings")
    print("Not checked: full Agent Skills conformance or host/workflow behavior")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
