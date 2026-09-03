[P1] scripts/ship-flow/without-it.sh:42 — Both `eval` runs inherit host environment and unrestricted filesystem access; a malicious command can read environment variables, `$HOME`, or files outside the worktree, so “with no secrets” is not enforced.

[P1] scripts/ship-flow/without-it.sh:42 — The retained and removed checks share one worktree, so retained-run filesystem mutations persist into the removed run and can falsify the comparison; use independent clean worktrees or reset and clean before applying the removed variant.

[P2] scripts/kc-dev-flow-contract-test.py:1907 — The test only requires the rule text to exist; the runner accepts embedded newlines and external-file access, making the one-line and candidate-tree restrictions prose rather than enforceable constraints.

```text
剩餘: 無
下一步: 修正上述問題（你）
可收線: 未確認
```
