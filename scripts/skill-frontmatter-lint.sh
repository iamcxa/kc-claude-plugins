#!/usr/bin/env bash
# skill-frontmatter-lint.sh — Assert every skill's SKILL.md has a well-formed
# YAML frontmatter block with a non-empty `name` and `description`.
#
# Why this exists: a plugin's skills are discovered by Claude Code purely from
# SKILL.md frontmatter (see e.g. e2e-pipeline/skills/e2e-flow/SKILL.md, and
# kc-plugin-forge-help/SKILL.md which builds its own skill index off it). A
# missing/malformed frontmatter block or an empty name/description silently
# breaks skill discovery with no error anywhere else in the pipeline — this
# check makes that failure loud and blocking instead. Cheap by design:
# stdlib python3 only (no PyYAML dependency, matching this job's other steps).
#
# Scope note: this checks that name/description are present and non-empty; it
# does not validate the semantic quality of the description text, nor other
# frontmatter fields (e.g. allowed-tools). See CLAUDE.md pre-merge gates table.
#
# Usage: ./scripts/skill-frontmatter-lint.sh
# Exit 0 = every skills/*/SKILL.md has valid frontmatter; exit 1 = at least one
# is missing, malformed, or a skills/* directory has no SKILL.md at all.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="${REPO_DIR_OVERRIDE:-$(cd "$SCRIPT_DIR/.." && pwd)}"

python3 - "$REPO_DIR" <<'PY'
import os
import re
import sys

repo_dir = os.path.realpath(sys.argv[1])

TOP_KEY_RE = re.compile(r'^([A-Za-z0-9_-]+):\s*(.*)$')
BLOCK_INDICATORS = {'>', '|', '>-', '|-', '>+', '|+'}


def strip_quotes(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def parse_frontmatter(text):
    """Return (fields, error). error is a reason string, or None on success."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        return None, "missing frontmatter block (file must start with '---')"

    close_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            close_idx = i
            break
    if close_idx is None:
        return None, "unterminated frontmatter block (no closing '---')"

    body = lines[1:close_idx]
    fields = {}
    i = 0
    n = len(body)
    while i < n:
        line = body[i]
        if not line.strip() or line[0].isspace():
            i += 1
            continue
        match = TOP_KEY_RE.match(line)
        if not match:
            i += 1
            continue
        key = match.group(1)
        rest = match.group(2).strip()
        i += 1
        if rest and rest not in BLOCK_INDICATORS:
            fields[key] = strip_quotes(rest)
            continue
        # Block scalar (`>`/`|`) or nested mapping/list: collect indented
        # (or blank) continuation lines until the next top-level key.
        continuation = []
        while i < n and (not body[i].strip() or body[i][0].isspace()):
            continuation.append(body[i])
            i += 1
        if rest in BLOCK_INDICATORS:
            fields[key] = "\n".join(c.strip() for c in continuation if c.strip())
        else:
            fields[key] = ""
    return fields, None


skill_dirs = []
for root, dirs, _files in os.walk(repo_dir):
    dirs[:] = [d for d in sorted(dirs) if d not in ('.git', 'node_modules')]
    if os.path.basename(root) == 'skills':
        for entry in dirs:
            skill_dirs.append(os.path.join(root, entry))
skill_dirs.sort()

failures = []
checked = 0

for skill_dir in skill_dirs:
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    rel_dir = os.path.relpath(skill_dir, repo_dir)
    if not os.path.isfile(skill_md):
        failures.append(f"{rel_dir}: no SKILL.md found in skill directory")
        continue

    rel_md = os.path.relpath(skill_md, repo_dir)
    try:
        with open(skill_md, encoding='utf-8') as handle:
            text = handle.read()
    except OSError as exc:
        failures.append(f"{rel_md}: unreadable: {exc}")
        continue

    checked += 1
    fields, error = parse_frontmatter(text)
    if error:
        failures.append(f"{rel_md}: {error}")
        continue

    name = fields.get('name', '')
    description = fields.get('description', '')
    if not name.strip():
        failures.append(f"{rel_md}: missing or empty 'name' field in frontmatter")
    if not description.strip():
        failures.append(f"{rel_md}: missing or empty 'description' field in frontmatter")

print(f"Skill frontmatter lint: checked {checked} SKILL.md file(s) across {len(skill_dirs)} skill directory(ies)")

if failures:
    print("", file=sys.stderr)
    for failure in failures:
        print(f"skill frontmatter lint failed: {failure}", file=sys.stderr)
    raise SystemExit(1)

print("Skill frontmatter lint: all skill directories have valid frontmatter")
PY
