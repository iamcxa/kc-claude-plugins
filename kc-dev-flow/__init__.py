"""Hermes registration for KC Dev Flow's package-local skills."""

from pathlib import Path

from agent.skill_utils import parse_frontmatter


def register(ctx) -> None:
    """Expose every direct package skill under the kc-dev-flow namespace."""
    skills_root = Path(__file__).parent / "skills"
    for skill_md in sorted(skills_root.glob("*/SKILL.md")):
        frontmatter, _body = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        name = str(frontmatter.get("name", ""))
        description = str(frontmatter.get("description", ""))
        ctx.register_skill(name, skill_md, description, frontmatter)
