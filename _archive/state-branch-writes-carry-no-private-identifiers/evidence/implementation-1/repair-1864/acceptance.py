"""Replay AC-3 and AC-5 using installed candidate hooks and local remotes. Args: CODE RUN_DIR."""
from collections import Counter
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest import mock

code, run = map(Path,sys.argv[1:])
run.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(code/'kc-dev-flow-2/scripts'))
import state_guard as guard
from test_state_guard import StateGuardTests

commands=[]
results=[]
original=StateGuardTests.run_command
def public(text):
    return str(text).replace(str(Path.home()),'~')
def observed(self,args,*a,**kw):
    done=original(self,args,*a,**kw)
    commands.append(dict(argv=[public(value) for value in args],exit=done.returncode,
                         stdout=public(done.stdout or ''),stderr=public(done.stderr or '')))
    return done
def git(root,*args):
    return subprocess.run(['git','-C',str(root),*args],capture_output=True,check=True).stdout

methods=[
 ('AC-3','test_real_commit_refusals_keep_staged_bytes_and_clean_push_passes'),
 ('AC-3','test_push_scans_every_commit_even_after_deletion'),
 ('AC-3','test_no_hunk_changed_text_refuses_commit_and_push'),
 ('AC-3','test_path_identifiers_refuse_new_and_renamed_files'),
 ('AC-3','test_missing_list_still_checks_derived_classes_and_check_detects_drift'),
 ('AC-5','test_warn_then_refuse_home_and_email_and_do_not_scan_product_worktree'),
 ('AC-5','test_shared_install_preserves_hooks_and_skips_nonstate_branch'),
 ('AC-5','test_public_archive_renames_preserve_old_text_gzip_and_binary_content'),
 ('AC-5','test_path_warn_mode_and_deletions_preserve_installed_modes')]
class Checked(StateGuardTests):
    def subTest(self,**parameters):
        from contextlib import nullcontext
        return nullcontext()

with mock.patch.object(StateGuardTests,'run_command',observed):
    for criterion,method in methods:
        fixture=Checked(method)
        fixture.setUp()
        try:
            getattr(fixture,method)()
            if method=='test_real_commit_refusals_keep_staged_bytes_and_clean_push_passes':
                with mock.patch.dict(os.environ,fixture.env,clear=True):
                    compiled,present=guard.patterns(fixture.state)
                assert present
                counts=Counter(dict.fromkeys(guard.CLASSES,0))
                blobs=0
                for revision in git(fixture.remote,'rev-list','spacedock-state/test').decode().splitlines():
                    for name in filter(None,git(fixture.remote,'ls-tree','-r','--name-only','-z',revision).split(b'\0')):
                        content=git(fixture.remote,'cat-file','blob',revision+':'+os.fsdecode(name))
                        while content.startswith(b'\x1f\x8b'):
                            content=gzip.decompress(content)
                        for kind,pattern in compiled:
                            counts[kind]+=bool(pattern.search(name) or pattern.search(content))
                        blobs+=1
                assert not sum(counts.values()),dict(counts)
                results.append(dict(name='AC-3 clean remote history paths and blobs',status='passed',blobs=blobs,hits=dict(counts)))
                fresh=fixture.base/'fresh-clone'
                fixture.run_command(['git','clone','-q','--branch','spacedock-state/test',fixture.remote,fresh])
                missing=fixture.run_command([sys.executable,'-B',guard.__file__,'check',fresh],expected=1)
                assert 'unguarded:' in missing.stdout
            results.append(dict(name=criterion+' '+method,status='passed'))
        finally:
            fixture.doCleanups()
(run/'results.json').write_text(json.dumps(results,indent=2)+'\n')
(run/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
print(json.dumps(results,indent=2))
