import json, re, sys
from pathlib import Path

TITLE = "Forward successful record checks' step-back warnings"
def mentioned(text, target):
    return target in text or (target == '4505793059' and TITLE.lower() in text.lower())

def found(text, target='4505793059'):
    for bullet in re.findall(r'^- F\d+\b[^\n]*(?:\n(?!\n|[-#])[^\n]*)*', text, re.M):
        if mentioned(bullet, target) and not re.search(r'\b(already fixed|is fixed|addressed and fixed|no longer unaddressed)\b', bullet, re.I):
            return True
    for paragraph in re.split(r'\n\s*\n', text):
        if mentioned(paragraph, target) and re.search(r'\b(REJECTED|HOLD|BLOCKED|NOT PASSED)\b', paragraph):
            if re.search(r'\b(unaddressed|not addressed|unresolved|repair required|must repair)\b', paragraph, re.I):
                return True
    return False

if __name__ == '__main__':
    print(json.dumps({'found':found(Path(sys.argv[1]).read_text())}))
