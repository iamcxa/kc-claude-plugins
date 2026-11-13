"""Run in dispatch scratch, after exporting candidate 9dd03d805 to reference/."""
from pathlib import Path
import shutil,subprocess
root=Path(__file__).parent
for name,patch in (("distinct","distinct.diff"),("all-raw","all-raw.diff"),("all-safe","declarations-repair.diff"),("both","both.diff")):
    target=root/name
    shutil.copytree(root/"reference",target,ignore=shutil.ignore_patterns("__pycache__"))
    subprocess.run(["git","-C",str(target),"apply",str(root/patch)],check=True)
