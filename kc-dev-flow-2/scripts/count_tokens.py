"""Shared count sentences and normalized numbers for gate and learn checks."""
import re

# see docs/adr/0072-counts-cite-saved-output-and-learn-checks-referenced-evidence.md
NUMBER = r"\d+(?:,\d{3})*"
NOUN = r"(?:cells?|runs?|tests?|files?|findings?|words?|lines?|PRs?|tasks?|commits?|cases?|records?|steps?|rounds?|tokens?|briefings?|attempts?|skips?|checks?|comments?)"
COUNT = re.compile(rf"\b({NUMBER})\s*(?:of|/)\s*({NUMBER})\b|\b({NUMBER})\s+(?:\w+\s+)?{NOUN}\b", re.I)
NUMBERS = re.compile(rf"(?<![\w,]){NUMBER}(?!\w|,\d)")
SEQUENCE_NUMBER = re.compile(rf"\b((?:Cycle|Round|Batch|Step|Stage|Amendment|Attempt|Phase)\s+){NUMBER}\b", re.I)


def numbers(text):
    return {value.replace(",", "") for value in NUMBERS.findall(text)}


def prose_lines(text):
    fence = None
    for index, line in enumerate(text.splitlines()):
        match = re.match(r"^[ \t]*(`{3,}|~{3,})(.*)$", line)
        if fence is not None:
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence) and not match[2].strip():
                fence = None
            continue
        if match:
            fence = match[1]
        else:
            yield index, line


def count_sentences(text):
    result = []
    for _, line in prose_lines(text):
        if line.startswith(("Unchecked counts:", "External rounds:")):
            continue
        for sentence in re.split(r"(?<=[.;])\s+", line):
            values = {n.replace(",", "") for match in COUNT.finditer(SEQUENCE_NUMBER.sub(r"\1#", sentence)) for n in match.groups() if n}
            if values:
                result.append((sentence, values))
    return result
