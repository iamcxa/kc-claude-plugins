# Offline acceptance of the first reading

Requires Python 3.11.8 or newer and Git. FO supplies three local inputs outside saved state: the private clone at candidate `c4f37b507347bf969cb9b76d7963aee5d4270df7`, this public task's absolute Markdown filename, and a dispatch-owned scratch directory. No network, credential or agent launch is used. The script exports committed bytes into scratch and does not change the source checkout.

From any fresh shell, with those explicit inputs supplied as `PRIVATE_CLONE`, `TASK_FILE` and `SCRATCH_ROOT`:

```sh
python3 -B "${TASK_FILE%.md}/evidence/validation-1/acceptance.py" "$PRIVATE_CLONE" "$TASK_FILE" "$SCRATCH_ROOT"
```

The five observations, taking less than five minutes on this stored set:

1. Frozen grading, scan and reading functions are unchanged, and the reading commit precedes preparation and transcript start for each collected run. The earlier operator abort is excluded from this chronology claim.
2. Regenerating the table compares equal byte for byte; every stored collection grade reproduces.
3. The existing grading fixtures pass; preparation refuses both the spend-cap and invalid-trial fixtures.
4. Every collected transcript remains marked contaminated, and the final reading remains indeterminate. A successful scan exit alone does not mean uncontaminated.
5. The current public task file and folder have zero hits in each printed marker category; the private source checkout remains clean.

Not archived (private): regenerated table, individual grades, transcript extracts and chronology output; reproduce with the command above. The committed primary sources remain at the candidate under `behaviour/cells/` and `behaviour/results/`.

This repeats mechanical checks only. It does not substitute for the validator's manual reading of each task, prove that omitted model-run criteria were absent, attest an isolated environment, verify the launcher or external wall cap, establish a no-skill control, or scan a fresh public clone and all published history. The privacy scan matches run/session identifiers, the case slug, the supplied clone directory name and exact long case lines; it cannot rule out paraphrases, renamed clones or other private aliases. ADR lint and FO's gate and publication obligations are separate.
