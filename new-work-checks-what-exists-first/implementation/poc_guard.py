import sys
from pathlib import Path
sys.path.insert(0,sys.argv[1]);from poc_readme import derive
s=derive(Path(sys.argv[2]).read_text());ok='- name: ideation' not in s and '### `ideation`' not in s;print('POC omits ideation:',ok);sys.exit(0 if ok else 1)
