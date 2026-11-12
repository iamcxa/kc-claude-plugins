"""Shared count sentences and normalized numbers for gate and learn checks."""
import re

# see docs/adr/0072-counts-cite-saved-output-and-learn-checks-referenced-evidence.md
NUMBER = r"\d+(?:,\d{3})*"
NOUN = r"(?:cells?|runs?|tests?|files?|findings?|words?|lines?|PRs?|tasks?|commits?|cases?|records?|steps?|rounds?|tokens?|briefings?|attempts?|skips?|checks?|comments?)"
# see docs/adr/0082-existing-item-effect-claims-cite-output-or-carry-a-tool-mark.md
COUNT = re.compile(rf"\b({NUMBER})\s*(?:of|/)\s*({NUMBER})\b|\b({NUMBER})\s+(?:\w+\s+)?{NOUN}\b|(?<![\d,])({NUMBER})\s*[張個次項]", re.I)
NUMBERS = re.compile(rf"(?<![A-Za-z0-9_,]){NUMBER}(?![A-Za-z0-9_]|,\d)")
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


def sentences(line):
    return [part.strip() for part in re.split(r"(?<=[。；;？?])|(?<=[.])\s+|(?=[一二三四五六七八九十]、)", line) if part.strip()]


def count_sentences(text):
    result = []
    for _, line in prose_lines(text):
        if line.startswith(("Unchecked counts:", "External rounds:")):
            continue
        for sentence in sentences(line):
            values = {n.replace(",", "") for match in COUNT.finditer(SEQUENCE_NUMBER.sub(r"\1#", sentence)) for n in match.groups() if n}
            if values:
                result.append((sentence, values))
    return result
