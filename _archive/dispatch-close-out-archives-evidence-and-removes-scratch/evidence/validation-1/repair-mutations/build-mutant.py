import sys
sys.path.insert(0,'/tmp/validate-close-854-20261112-183201/candidate/kc-dev-flow-2/scripts')
import scratch,dispatch_stage
scratch.check_owner=lambda *args: None
sys.exit(dispatch_stage.main())
