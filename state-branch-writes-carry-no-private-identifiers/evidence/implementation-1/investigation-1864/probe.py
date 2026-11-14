#!/usr/bin/env python3
"""Investigate review 1864 without modifying the candidate. Args: CODE RUN_DIR."""
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest import mock

code, run = map(Path, sys.argv[1:])
run.mkdir(parents=True, exist_ok=True)
(run/'tmp').mkdir(exist_ok=True)
tempfile.tempdir = str((run/'tmp').resolve())
sys.path.insert(0,str(code/'kc-dev-flow-2/scripts'))
import state_guard as guard
from test_state_guard import StateGuardTests

candidate='0c68231ca9147a9833846b47a36e2fc27846cf66'
def git_code(*args):
    return subprocess.run(['git','-C',str(code),*args],capture_output=True,check=True,text=True).stdout.strip()

def snapshot():
    return dict(head=git_code('rev-parse','HEAD'), status=git_code('status','--porcelain'),
                tracked={p:hashlib.sha256((code/p).read_bytes()).hexdigest()
                         for p in git_code('ls-files','kc-dev-flow-2/scripts/state_guard.py',
                                           'kc-dev-flow-2/scripts/test_state_guard.py').splitlines()})

before=snapshot()
assert before['head']==candidate and not before['status']
commands=[]
results=[]

def public(value):
    return str(value).replace(str(Path.home()),'~').replace(str(run),'$RUN_DIR')

def fixture():
    obj=StateGuardTests('test_push_scans_every_commit_even_after_deletion')
    obj.setUp()
    original=obj.run_command
    def observed(args,*a,**kw):
        done=original(args,*a,**kw)
        commands.append(dict(argv=[public(v) for v in args],exit=done.returncode,
                             stdout=public(done.stdout or ''),stderr=public(done.stderr or '')))
        return done
    obj.run_command=observed
    return obj

def content_case(name,initial,next_data,attributes=None,threshold=None):
    all_rows=[]
    for event in ('pre-commit','pre-push'):
        obj=fixture()
        try:
            if threshold:
                obj.git(obj.repo,'config','core.bigFileThreshold',str(threshold))
            if attributes:
                (obj.state/'.gitattributes').write_text(attributes)
                obj.git(obj.state,'add','--','.gitattributes')
            path=obj.state/'payload.txt'
            old=initial(obj)
            new=next_data(obj)
            path.write_bytes(old)
            obj.commit('payload.txt')
            obj.git(obj.state,'push','origin','spacedock-state/test')
            old_oid=obj.git(obj.state,'rev-parse','HEAD:payload.txt').stdout.strip()
            if event=='pre-commit':
                obj.install('--refuse','private-slug')
            path.write_bytes(new)
            obj.git(obj.state,'add','--','payload.txt')
            new_oid=obj.git(obj.state,'rev-parse',':payload.txt').stdout.strip()
            command=['git','-C',str(obj.state),'diff','--no-ext-diff','--no-textconv','--no-color','-U0',old_oid,new_oid]
            diff=subprocess.run(command,env=obj.env,capture_output=True,check=True).stdout
            commands.append(dict(argv=[public(v) for v in command],exit=0,
                                 stdout=public(diff.decode('utf-8','replace')),stderr=''))
            diff_kind='hunk' if b'@@' in diff else 'binary' if b'Binary files ' in diff else 'no-hunk'
            with mock.patch.dict(os.environ,obj.env,clear=True):
                scanned=guard.added_bytes(obj.state,old_oid.encode(),new_oid.encode())
            row=dict(case=name,event=event,old_bytes=len(old),new_bytes=len(new),diff_kind=diff_kind,
                     scanned_bytes=len(scanned),new_literal_present=obj.slug.encode() in new,
                     scanned_literal_present=obj.slug.encode() in scanned,
                     attributes=attributes,core_bigFileThreshold=threshold)
            if event=='pre-commit':
                direct=obj.run_command([sys.executable,'-B',guard.__file__,'scan',obj.state,'--event',event],expected=None)
                done=obj.git(obj.state,'commit','-qm','test: candidate commit probe',expected=None)
                row.update(scan_exit=direct.returncode,commit_exit=done.returncode)
                assert direct.returncode==done.returncode
            else:
                obj.git(obj.state,'commit','-qm','test: existing unpushed candidate')
                obj.install('--refuse','private-slug')
                tip=obj.git(obj.state,'rev-parse','HEAD').stdout.strip()
                previous=obj.git(obj.state,'rev-parse','HEAD^').stdout.strip()
                line=f'refs/heads/spacedock-state/test {tip} refs/heads/spacedock-state/test {previous}\n'
                direct=obj.run_command([sys.executable,'-B',guard.__file__,'scan',obj.state,'--event',event],data=line,expected=None)
                done=obj.git(obj.state,'push','origin','spacedock-state/test',expected=None)
                remote=obj.git(obj.remote,'show','spacedock-state/test:payload.txt').stdout.encode()
                row.update(scan_exit=direct.returncode,push_exit=done.returncode,
                           remote_has_identifier=obj.slug.encode() in remote)
                assert direct.returncode==done.returncode
            all_rows.append(row)
        finally:
            obj.doCleanups()
    results.extend(all_rows)

content_case('small-utf8-control',lambda o:b'public old\n',lambda o:o.slug.encode()+b'\n')
content_case('configured-size-threshold',lambda o:b'public old\n'*16,
             lambda o:b'public next\n'*16+o.slug.encode()+b'\n',threshold=64)
content_case('path-specific-binary-attribute',lambda o:b'public old\n',lambda o:o.slug.encode()+b'\n',
             attributes='*.txt -diff\n')
content_case('global-binary-attribute',lambda o:b'public old\n',lambda o:o.slug.encode()+b'\n',
             attributes='* -diff\n')
content_case('old-nul-new-utf8',lambda o:b'public old\0binary\n',lambda o:o.slug.encode()+b'\n')
content_case('new-nul-control',lambda o:b'public old\n',lambda o:b'prefix\0'+o.slug.encode()+b'\n')
content_case('old-utf16-new-utf8',lambda o:'public old\n'.encode('utf-16'),lambda o:o.slug.encode()+b'\n')
content_case('new-latin1-nonutf8-control',lambda o:b'public old\n',lambda o:b'\xe9 '+o.slug.encode()+b'\n')

def path_case(kind):
    for event in ('pre-commit','pre-push'):
        obj=fixture()
        try:
            if kind=='pure-rename-private-folder':
                (obj.state/'public.md').write_text('public content\n')
                obj.commit('public.md')
                obj.git(obj.state,'push','origin','spacedock-state/test')
            if event=='pre-commit':
                obj.install('--refuse','private-slug')
            relative=(obj.slug+'.md') if kind=='new-private-basename' else obj.slug+'/public.md'
            target=obj.state/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            if kind=='pure-rename-private-folder':
                obj.git(obj.state,'mv','--','public.md',relative)
            else:
                target.write_text('public content\n')
                obj.git(obj.state,'add','--',relative)
            with mock.patch.dict(os.environ,obj.env,clear=True):
                entries=guard.changes(obj.state)
            raw=obj.git(obj.state,'diff','--cached','--name-status','-M','-z').stdout
            row=dict(case=kind,event=event,path_has_identifier=True,content_has_identifier=False,
                     yielded_entries=len(entries),raw_status=public(raw))
            if event=='pre-commit':
                direct=obj.run_command([sys.executable,'-B',guard.__file__,'scan',obj.state,'--event',event],expected=None)
                done=obj.git(obj.state,'commit','-qm','test: private path commit',expected=None)
                row.update(scan_exit=direct.returncode,commit_exit=done.returncode)
            else:
                obj.git(obj.state,'commit','-qm','test: private path before install')
                obj.install('--refuse','private-slug')
                tip=obj.git(obj.state,'rev-parse','HEAD').stdout.strip()
                previous=obj.git(obj.state,'rev-parse','HEAD^').stdout.strip()
                line=f'refs/heads/spacedock-state/test {tip} refs/heads/spacedock-state/test {previous}\n'
                direct=obj.run_command([sys.executable,'-B',guard.__file__,'scan',obj.state,'--event',event],data=line,expected=None)
                done=obj.git(obj.state,'push','origin','spacedock-state/test',expected=None)
                names=obj.git(obj.remote,'ls-tree','-r','--name-only','spacedock-state/test').stdout
                row.update(scan_exit=direct.returncode,push_exit=done.returncode,remote_has_identifier=obj.slug in names)
            assert direct.returncode==done.returncode
            results.append(row)
        finally:
            obj.doCleanups()

for kind in ('new-private-folder','new-private-basename','pure-rename-private-folder'):
    path_case(kind)

after=snapshot()
assert after==before
obj=dict(candidate=candidate,git_version=git_code('--version'),before=before,after=after,results=results,
         limits=['Default large-file size threshold not exercised; a 64-byte explicit threshold reproduces the same no-hunk branch.',
                 'All private identifiers and git remotes are invented throwaway data; no live hook or clone config was changed.'])
(run/'results.json').write_text(json.dumps(obj,indent=2)+'\n')
(run/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
print(json.dumps(obj,indent=2))
