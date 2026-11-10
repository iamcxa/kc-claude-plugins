Thanks for the six findings. Where each one goes in kc-dev-flow-2:

- **1 (gate reason does not quote the bound question):** `decision_ledger.py --reason <file> --task <task>` now also refuses a reason without `answering 「<bound question>」` for the task's single open gate attempt, before a Captain `gate record` is written. Quote the bound question, or withdraw and re-prepare when the Captain answered a different question. ADR 0073 records the ruling for every Captain gate. The replay of the four relay tasks refused 11 of 12 Captain resolutions.
- **2 (archive without a committed observer report):** handled separately by archive-waits-for-observer-report.
- **3 (merge ask with no `merge/ask-N.json`):** handled separately by delivery-check-before-ask-is-provable (PR #817).
- **4 (several screenshots):** built-screen `preview:` accepts a scalar or a YAML block sequence; every file is checked and printed. The 14 commented pictures from theme-switch-keeps-draft passed as a list, while the base refused it.
- **5 (archived task folder coverage):** the cause was the folder argument, not archive. `--coverage` now resolves `index.md` or the sibling `.md` and gives the file form's result.
- **6 (Captain steps location):** `question`, `check` and `steps` hold records outside `<task>/captain-steps/<N>.md`, following ADR 0054. Relative and absolute names of the right file pass.

This addresses items 1, 4, 5 and 6. Items 2 and 3 remain tracked by their own tasks; keep this issue open until those are settled.
