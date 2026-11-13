"""Synthetic instruction check: no private repository content is accessed."""
import json,pathlib,sys,tempfile
scripts=pathlib.Path(sys.argv[1])/'kc-dev-flow-2/scripts';sys.path.insert(0,str(scripts))
import test_scratch,scratch
case=test_scratch.ScratchTests('test_missing_record_refuses_without_deletion');case.setUp()
try:
 notes=scratch.notes_for(case.repo,case.folder,'validation-1','',pathlib.Path(sys.argv[2]))
 out=pathlib.Path(sys.argv[3]);out.mkdir(exist_ok=True,parents=True)
 (out/'emitted-notes.txt').write_text(notes)
 allowed='nothing that holds a secret or a person' in notes
 # The Captain selected every private-repository output, not these two subsets.
 broad=any(x in notes.lower() for x in ['private repository','private repo','private-repository'])
 (out/'privacy.json').write_text(json.dumps(dict(synthetic_only=True,excludes_secrets_and_personal_data=allowed,excludes_all_private_repository_evidence=broad),indent=2))
 print('private-repository instruction:', 'PASS' if broad else 'MISSING; emitted rule excludes secrets and personal data only')
finally:case.doCleanups()
sys.exit(0 if broad else 1)
