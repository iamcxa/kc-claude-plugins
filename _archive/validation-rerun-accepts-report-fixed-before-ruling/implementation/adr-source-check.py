import json
from pathlib import Path
import sys

task, record = map(Path, sys.argv[1:3])
source, adr = task.read_text(), record.read_text()
alignment = source.split('Result: the Captain chose 「', 1)[1].split('」 (host question dialog', 1)[0]
question = source.split('Result:', 1)[1].split('answering 「', 1)[1].split('」.\n', 1)[0]
gate = json.loads((task.with_suffix('') / 'review/ideation/briefing-1/index.json').read_text())
assert adr.count('Amended 2026-11-11') == 1
assert alignment in adr and question in adr and gate['question'] in adr and '核准（建議）' in adr
assert 'same ordered, non-empty list of whole-word' in adr
print('PASS: one amendment with both complete questions and replies, and the approved verdict rule')
