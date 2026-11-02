"""Read workflow extension names from inline or block lists."""

from pathlib import Path
import re

from decision_ledger import split_task, unquote


ITEM = r''''(?:[^']|'')*'|"(?:[^"\\]|\\.)*"|[A-Za-z0-9_-]+'''
INLINE = re.compile(rf"\[([ \t]*(?:(?:{ITEM})(?:[ \t]*,[ \t]*(?:{ITEM}))*[ \t]*,?)?[ \t]*)\](?:[ \t]+#.*)?[ \t]*")
ENTRY = re.compile(rf"({ITEM})(?:[ \t]+#.*)?[ \t]*")


def readme_extensions(path):
    lines, _ = split_task(Path(path).read_text())
    if lines is None:
        raise ValueError(f"README {path} has no frontmatter, so extensions: cannot be read")
    for index, line in enumerate(lines):
        if not line.startswith("extensions:"):
            continue
        value = line[len("extensions:"):].strip()
        if value.startswith("["):
            match = INLINE.fullmatch(value)
            if not match:
                raise ValueError(f"README {path}: malformed extensions inline list")
            return [unquote(item) for item in re.findall(ITEM, match.group(1))]
        if value and not value.startswith("#"):
            raise ValueError(f"README {path}: extensions: is neither a [list] nor a block list")
        extensions = []
        for line in lines[index + 1:]:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            item = re.match(r"^[ \t]*-[ \t]+(.*)$", line)
            if not item:
                if line[:1].isspace() or line.startswith("-"):
                    raise ValueError(f"README {path}: malformed extensions block list")
                break
            raw = item.group(1).strip()
            match = ENTRY.fullmatch(raw)
            if not match:
                raise ValueError(f"README {path}: malformed extensions block item")
            extensions.append(unquote(match.group(1)))
        return extensions
    return []
