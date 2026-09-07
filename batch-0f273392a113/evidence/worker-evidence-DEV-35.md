## Evidence
DISPATCH_TOKEN: dev35-repair-2026-09-07-r1
CANDIDATE_SHA: c6c4fe19b3a6aee39eb3a4692e0a2fc4a125c4cc
BRANCH: conductor/dev-35-cloud-headed-playwright
BASE_SHA: c0c314597f4c8786cf7e6cd7a15df46293db7cc9
FILES: experiments/netlify-refine-poc/qnow-next/LOCAL_STACK.md, experiments/netlify-refine-poc/qnow-next/local/headed-browser-environment.mjs, experiments/netlify-refine-poc/qnow-next/local/headed-browser-smoke.mjs, experiments/netlify-refine-poc/qnow-next/test/headed-browser-environment.test.mjs
TESTS: node --check (3 files) -> exit 0; npm run type-check -> exit 0; npm run test:headed-browser -> exit 1 on macOS (21 tests: 8 pass, 1 skipped, 12 display/proc-dependent fail — same 12 as base)
WITHOUT_IT_COMMAND: node /tmp/wi-1175.mjs <abs path to local/headed-browser-environment.mjs>  (asserts NO_PROC_PROCESS_TABLE is raised when the /proc probe returns false)
WITHOUT_IT_REMOVED_VARIANT: sed -i.bak "s/if (!hasProcDirectory()) throw unavailable('NO_PROC_PROCESS_TABLE');/if (false) throw unavailable('NO_PROC_PROCESS_TABLE');/" experiments/netlify-refine-poc/qnow-next/local/headed-browser-environment.mjs
WITHOUT_IT_OBSERVED: worker: retained 0; removed 1; base 1. FO: see README entry (script-based re-run)
SELF_CHECK: accept-evidence: REFUSE: AC-3: cannot extract paths (extension list — S43/DEV-134)
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
F1..F8: NO_PROC guard + test; pid guard + test; stderr tail in receipt; LAUNCH_FAILED line; finally wrapped; executablePath catch narrowed; SIGINT sibling (skipped without display); LOCAL_STACK order corrected
BLOCKER: station AC-3 extension list (.mjs)
