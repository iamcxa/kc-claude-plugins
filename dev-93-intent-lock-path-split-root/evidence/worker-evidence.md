## Evidence
DISPATCH_TOKEN: 87e4b70ca37a56e0
CANDIDATE_SHA: 218d584ecf1a2698afa4d4a3ae34f9fc17f14382
BRANCH: feature/dev-93-intentsh-lock-path-breaks-on-a-split-root-state-checkout-git
BASE_SHA: d98f40b5e2080cb884facf1734fc66052eff998
FILES: scripts/ship-flow/intent.sh, scripts/kc-dev-flow-contract-test.py
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: scripts/ship-flow/intent.sh -> AC-1,AC-2 | SHIP_LOCK_STALE_S=3 intent.sh commit against a temp git-worktree state | git checkout d98f40b5e2080cb884facf1734fc66052eff998 -- scripts/ship-flow/intent.sh
SURFACE: scripts/kc-dev-flow-contract-test.py -> AC-3 | python3 scripts/kc-dev-flow-contract-test.py | git checkout d98f40b5e2080cb884facf1734fc66052eff998 -- scripts/kc-dev-flow-contract-test.py
WITHOUT_IT_COMMAND: set -e; T=$(mktemp -d); git init -q --bare "$T/origin.git"; git clone -q "$T/origin.git" "$T/seed"; git -C "$T/seed" -c user.name=f -c user.email=f@e checkout -q -b spacedock-state/dev; echo '{"writer":1,"holder":"laptop","at":"x"}' > "$T/seed/_holder.json"; git -C "$T/seed" add _holder.json; git -C "$T/seed" -c user.name=f -c user.email=f@e commit -q -m seed; git -C "$T/seed" push -q origin spacedock-state/dev; git clone -q "$T/origin.git" "$T/bare"; git -C "$T/bare" worktree add -q "$T/state-wt" spacedock-state/dev; SHIP_LOCK_STALE_S=3 scripts/ship-flow/intent.sh commit "$T/state-wt" laptop 1 dev-93-wi 0123456789abcdef0123456789abcdef 11111111-1111-1111-1111-111111111111 d98f40b5e2080cb884facf1734fc66052eff998 $(printf x | sha256sum | cut -d' ' -f1); rm -rf "$T"
WITHOUT_IT_REMOVED_VARIANT: git checkout d98f40b5e2080cb884facf1734fc66052eff998 -- scripts/ship-flow/intent.sh
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 6
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: pre-fix on worktree state exit 6 (lock timeout); fixed on worktree state exit 0, intent committed; residue check under resolved git-dir empty (no ship-lock.d/.stale.* found)
AC-2: fixed intent.sh on plain clone (checked out to spacedock-state/dev) exit 0, intent committed
AC-3: contract-test case "kc-dev-flow-intent-lock" (worktree-style `.git`-is-a-file fixture) added to scripts/kc-dev-flow-contract-test.py; run standalone against pre-fix intent.sh -> exit 6 (reddened); against fixed intent.sh -> exit 0; full suite run -> exit 0
BLOCKER: none
