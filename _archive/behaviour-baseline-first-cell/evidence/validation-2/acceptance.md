# Offline acceptance of the second reading

Requires Python 3.11.8 or newer and Git. FO supplies three explicit local inputs outside saved state: `PRIVATE_CLONE`, a clean local clone at candidate `02fcf256d8ca2aa4f4d44edd64d7162e3c049b1d`; `TASK_FILE`, this public task's absolute Markdown filename; and `SCRATCH_ROOT`, an existing dispatch-owned scratch directory outside both checkouts. No user-visible screen changes. No network, credential or agent launch is used. The script exports committed bytes into disposable scratch and changes neither source checkout nor task records.

Run from a fresh shell with those inputs supplied:

```sh
python3 -B "${TASK_FILE%.md}/evidence/validation-2/acceptance.py" "$PRIVATE_CLONE" "$TASK_FILE" "$SCRATCH_ROOT"
```

Five observations, designed to finish within five minutes on the stored set:

1. Frozen rules precede every preparation and transcript start, by commit ancestry and recorded times. The sole later runner edit is the table's opening label.
2. The second table and scan reproduce byte for byte, each collection grade reproduces, and both decision readings agree with the committed conclusion.
3. Existing grading and contamination fixtures pass. Both dry preparation checks refuse their stored cap/invalid fixtures before any agent or network action.
4. The first reading's inputs and outputs are unchanged; its table reproduces and remains indeterminate. Combined launch records remain within the committed cap.
5. The current task file and folder print zero hits for run identifiers, session identifiers, the case slug, supplied private source names and exact long case lines. The source remains clean at the candidate. The disposable export is removed on exit.

Not archived (private): regenerated tables, grades, transcripts, manual per-run notes, timestamps and package-check outputs; reproduce with the command above and the candidate's `behaviour/` files. The public privacy file holds hit counts only.

This script does not replace the validator's human reading of each criterion and flag. It does not attest historical commit timestamps, model identity beyond saved transcripts, instruction loading without a tool call, an isolated environment, the parked launcher, external caps, or a no-method control. A zero marker count is limited to the current local task snapshot; it does not scan a fresh public clone, published head or all history, or exclude paraphrases and unknown aliases. ADR lint configuration, FO's acceptance replay and closure remain separate obligations. Neither reading establishes release acceptance or causal improvement.
