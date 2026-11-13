"""Restore committed public evidence, then remove only recorded owned scratch."""
import gzip,hashlib,json,pathlib,shutil,subprocess,sys
from datetime import datetime
from zoneinfo import ZoneInfo
e=pathlib.Path(__file__).resolve().parent;s=pathlib.Path(sys.argv[1]);t=pathlib.Path(sys.argv[2]).resolve();commit=sys.argv[3]
sys.path.insert(0,str(t/'candidate/kc-dev-flow-2/scripts'))
import scratch
slug='dispatch-close-out-archives-evidence-and-removes-scratch';prefix=slug+'/evidence/validation-2/'
def git(*args):return subprocess.check_output(['git','-C',str(s),*args])
assert subprocess.run(['git','-C',str(s),'merge-base','--is-ancestor',commit,'origin/spacedock-state/dev2']).returncode==0
manifest=git('show',commit+':'+prefix+'SHA256SUMS').decode();rows=[]
for line in manifest.splitlines():
 digest,name=line.split('  ',1)
 raw=subprocess.run(['git','-C',str(s),'show',commit+':'+prefix+name],capture_output=True)
 compressed=raw.returncode!=0
 data=gzip.decompress(git('show',commit+':'+prefix+name+'.gz')) if compressed else raw.stdout
 assert hashlib.sha256(data).hexdigest()==digest,name
 rows.append({'path':name,'compressed':compressed,'matches_original':True})
(e/'committed-restore.json').write_text(json.dumps({'evidence_commit':commit,'pushed_to_state_branch':True,'restored_files':len(rows),'files':rows},indent=2))
account=json.loads(gzip.decompress((e/'scratch-accounting-before-cleanup.json.gz').read_bytes()))
roots=account['owned_cleanup_roots'];assert str(t) in roots
files=json.loads((e/'native-artifact-cleanup-candidates.json').read_text())['files'];removed_files=[]
for row in files:
 p=pathlib.Path(row['path']);assert p.parent==pathlib.Path('/tmp/spacedock-dispatch')
 assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
 p.unlink();removed_files.append({'path':str(p),'absent':not p.exists()})
removed=[]
for name in sorted(roots,key=lambda x:(x==str(t),x)):
 p=pathlib.Path(name)
 assert p==t or p==pathlib.Path('/private/tmp/close-854-captain-verified') or (p.parent==pathlib.Path('/private/tmp/dev2') and p.name not in ('.','..'))
 existed=p.exists()
 if existed:shutil.rmtree(p)
 removed.append({'path':name,'removed_now':existed,'already_removed_by_fixture':not existed,'absent':not p.exists()})
assert all(r['absent'] for r in removed+removed_files)
end=datetime.now(ZoneInfo('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S Asia/Taipei')
receipt={'evidence_commit':commit,'evidence_restore_passed_before_cleanup':True,'end_time':end,'directory_roots':removed,'native_artifact_files':removed_files,'all_absent':True,'shared_parent_directories_left_untouched':True}
(e/'cleanup.json').write_text(json.dumps(receipt,indent=2))
(e/'cleanup-paths.txt').write_text('\n'.join(r['path'] for r in removed+removed_files)+'\n')
retained=scratch.evidence(s/slug,'validation-2')
print(json.dumps({'restored_files':len(rows),'directory_roots':len(removed),'native_artifact_files':len(removed_files),'removed_now':[r['path'] for r in removed if r['removed_now']],'all_absent':True,'retained':retained,'end_time':end},indent=2))
