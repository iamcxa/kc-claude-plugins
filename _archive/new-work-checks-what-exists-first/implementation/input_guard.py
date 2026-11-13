import hashlib,sys
from pathlib import Path
p=Path(sys.argv[1]);ok=hashlib.sha256(p.read_bytes()).hexdigest()==sys.argv[2];print('input unchanged:',ok);sys.exit(0 if ok else 1)
