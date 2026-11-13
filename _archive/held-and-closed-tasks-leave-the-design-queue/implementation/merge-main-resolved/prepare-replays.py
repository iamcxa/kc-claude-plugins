#!/usr/bin/env python3
"""Export exact public sources and frozen state for origin-less acceptance."""
import argparse,io,json,os,subprocess,tarfile
from pathlib import Path
p=argparse.ArgumentParser()
for n in ("candidate","state","scratch","output"):p.add_argument("--"+n,type=Path,required=True)
a=p.parse_args();env={**os.environ,"GIT_AUTHOR_NAME":"probe","GIT_AUTHOR_EMAIL":"probe@example.invalid","GIT_COMMITTER_NAME":"probe","GIT_COMMITTER_EMAIL":"probe@example.invalid","GIT_CONFIG_GLOBAL":os.devnull,"GIT_CONFIG_SYSTEM":os.devnull}
objects=Path(subprocess.check_output(["git","-C",str(a.candidate),"rev-parse","--path-format=absolute","--git-common-dir"],text=True).strip())/"objects"
def export(source,rev,target,paths=()):
 target.mkdir(parents=True)
 data=subprocess.check_output(["git","-C",str(source),"archive",rev,*paths])
 with tarfile.open(fileobj=io.BytesIO(data)) as archive:archive.extractall(target,filter="data")
def init(target,branch):
 for args in (["init","-q","-b",branch],["add","-A"],["commit","-qm","public replay snapshot"]):subprocess.run(["git","-C",str(target),*args],env=env,check=True,capture_output=True)
 # Gate checks require historical git-root objects; this read-only object alternate supplies them.
 (target/".git/objects/info/alternates").write_text(str(objects)+"\n")
 assert not subprocess.check_output(["git","-C",str(target),"remote"],text=True).strip()
for name,rev in (("candidate","HEAD"),("base","origin/main"),("legacy","8ce0eb6050c889b21baccf50fec35231bc888d66")):
 target=a.scratch/name
 export(a.candidate,rev,target,("kc-dev-flow-2","docs/dev2/README.md","docs/dev2/_mods","docs/adr"))
 init(target,"main")
 state=target/"docs/dev2/.spacedock-state"
 export(a.state,"eae5ea47cec926f35d164f8a88d31579196d7634",state)
 init(state,"spacedock-state/dev2")
print(json.dumps(dict(objects_read_only=str(objects),frozen_state="eae5ea47cec926f35d164f8a88d31579196d7634",exports=["candidate","base","legacy"])))
