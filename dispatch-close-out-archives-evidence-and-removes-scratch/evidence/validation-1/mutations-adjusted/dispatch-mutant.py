import sys
sys.path.insert(0,'/tmp/validate-close-854-20261112-183201/candidate/kc-dev-flow-2/scripts')
import dispatch_stage as s
s.notes_for = lambda repo, folder, record, notes, package: notes
sys.exit(s.main())
