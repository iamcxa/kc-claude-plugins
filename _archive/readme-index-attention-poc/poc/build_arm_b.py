#!/usr/bin/env python3
"""Split arm A's README verbatim into per-moment rule files for arm B, and check nothing was lost.

Usage: build_arm_b.py            (run from anywhere; paths are relative to this file)
Writes arm-b/rules/*.md. arm-b/README.md (the index) is written by hand and is not touched.
A `## ` heading outside a code fence starts a file; under `## Stages` each `### ` heading starts a file too.
The text before `## File Naming` (frontmatter and intro) stays in the index, so it is not split out.
Exit 1 when the concatenated rule files differ from the README text after the intro.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = (HERE / "arm-a" / "README.md").read_text()
OUT = HERE / "arm-b" / "rules"

NAMES = {
    "File Naming": "file-naming", "Schema": "schema", "Stages": "stages",
    "Dispatch facts": "dispatch-facts", "Review-finding disposition": "review-finding-disposition",
    "FO steps: review findings": "fo-steps-review-findings", "Decision records": "decision-records",
    "FO steps: decision records": "fo-steps-decision-records", "Captain amendments": "captain-amendments",
    "Affected documents": "affected-documents", "Number guards": "number-guards",
    "FO steps: number guards": "fo-steps-number-guards", "Delivery authority": "delivery-authority",
    "Extensions": "extensions", "Workflow State": "workflow-state", "Task Template": "task-template",
    "backlog": "stage-backlog", "ideation": "stage-ideation", "implementation": "stage-implementation",
    "validation": "stage-validation", "done": "stage-done",
}


def split(text):
    lines = text.splitlines(keepends=True)
    fence = False
    current = None
    in_stages = False
    chunks = []
    for line in lines:
        if line.startswith("```"):
            fence = not fence
        heading = None
        if not fence:
            if line.startswith("## "):
                heading = line[3:].strip()
                in_stages = heading == "Stages"
            elif in_stages and line.startswith("### "):
                heading = line[4:].strip().strip("`")
        if heading is not None:
            current = [heading, []]
            chunks.append(current)
        if current is not None:
            current[1].append(line)
    return chunks


def main():
    start = SRC.index("## File Naming")
    body = SRC[start:]
    chunks = split(body)
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.md"):
        old.unlink()
    for heading, lines in chunks:
        name = NAMES[heading]
        (OUT / f"{name}.md").write_text("".join(lines))
    joined = "".join("".join(lines) for _, lines in chunks)
    if joined != body:
        print("lossy split")
        return 1
    print(f"{len(chunks)} rule files, lossless")
    return 0


if __name__ == "__main__":
    sys.exit(main())
