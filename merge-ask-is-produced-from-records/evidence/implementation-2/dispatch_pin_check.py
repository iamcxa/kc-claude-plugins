import os
import importlib.util, json, subprocess, sys
from pathlib import Path
WT=Path(os.environ["PRODUCT_WORKTREE"])
sys.path.insert(0,str(WT/"kc-dev-flow-2/scripts"))
import test_sd_dispatch as test
texts=test.pinned_texts()
base={p: " ".join(subprocess.check_output(["git","-C",str(WT),"show","bfc53d825:kc-dev-flow-2/"+p],text=True).split()) for p in texts}
rows={"base": {k:v for k,v in test.fix_gaps(base).items() if any(v)}, "candidate": {k:v for k,v in test.fix_gaps(texts).items() if any(v)}}
Path(__file__).with_name("dispatch-pins.json").write_text(json.dumps(rows,indent=2)+"\n")
assert rows["base"]=={}, rows["base"]
assert rows["candidate"]=={}, rows["candidate"]
