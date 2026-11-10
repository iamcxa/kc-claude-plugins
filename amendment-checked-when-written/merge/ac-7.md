# AC-7 hosted evidence (recorded by FO, 2026-11-10)

Captain's word for the pin: the Captain chose 「移到 0.38.0（建議）」 (host question dialog, 2026-11-10), answering 「要不要把 dev2 狀態分支的法規檢查（dev2-laws.yml）釘選從 0.26.0 移到 0.38.0？我建議移：這會讓 0.26.0 之後加的規則（含 #828 的第四條法規）開始審之後的每次推送，也是 #828 任務收尾的最後條件。我在本機用 0.38.0 重放最近 5 次推送都通過，但那 5 次沒有被審到的事件。」.

- Release carrying L4: tag `kc-dev-flow-2-v0.38.0`, commit `ec2bae0d6b9c4cedc5fc67adfc99d7043143c5de` (`git rev-parse 'kc-dev-flow-2-v0.38.0^{commit}'`, 2026-11-10).
- Pin commit on `spacedock-state/dev2`: `b062fabaeea583022b65bd5c536a0fac088d81e8`; `.github/workflows/dev2-laws.yml` package ref moved from `22219a3e4bc48a69a893bd757923e8c034d1ba6e` (tag `kc-dev-flow-2-v0.26.0`) to the tag commit above. One line changed.
- Hosted run on that push: `dev2-laws` run 42833194068, conclusion success. Its log prints `L4 amendment-moves-use-fresh-ids: 0 events judged in 7a5e517b0b9c..b062fabaeea5, 0 violated`. Lines saved in `ac-7-run-42833194068.log` (`gh run view 42833194068 --log`, filtered to the `ref:` and law lines).
- Falsifier: the previous hosted run on the old pin, 42824638737 (push `7a5e517b0`), prints L1 and L2 lines and no L4 line. Lines saved in `ac-7-old-pin-run-42824638737.log`.

Limit: both runs judged 0 events, so the hosted evidence shows L4 runs on dev2 pushes, not that it has judged a real amendment move there.
