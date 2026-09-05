## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex, read after the final push and confirmed against ls-remote>
BRANCH: feature/dev-95-ac367-three-lint-rules
BASE_SHA: df43392f77fc753ea721066db14db4a52bcf4e97
FILES: <comma-separated>
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit <code>
SURFACE: <one line per changed file: path -> AC-N | proving command | removing command>
WITHOUT_IT_COMMAND: <one self-contained shell line exercising an AC; exits 0 on the candidate, non-zero on the removed variant>
WITHOUT_IT_REMOVED_VARIANT: <removes every surface the command reads>
WITHOUT_IT_OBSERVED: retained -> exit <code>; removed -> exit <code>
AC-1: <L6 on both fixtures>
AC-2: <L9 per Issue>
AC-3: <L10 on three fixtures>
AC-4: <eight-rule diff: identical | differences>
AC-5: <mutation exit and line>
BLOCKER: none | <what stopped you and at which step>
