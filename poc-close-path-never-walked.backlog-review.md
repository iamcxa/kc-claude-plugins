# Backlog admission: poc-close-path-never-walked

## Both defects, with their reproductions

Found by driving the POC close path on `capture-oracle-never-caught-anything`
(archived 2026-09-14), not by reading it. No existing test reaches either.

**1. No correction round after a POC prove stage.** `poc-close-guard.py:121` reads
`## POC outcome` via `one_yaml_section(text, "POC outcome", "poc_outcome")`, so the
prove stage writes it as a top-level section. `profile-contract-loader.py:593`
excludes only `^## Stage Report` from `work_item_authority`, so that section and
`## POC close measurement` are inside the accepted-authority hash. A
`kc-dev-flow-feedback/v1` context requires the current authority to equal the
rejected pin's, which cannot hold after prove. Observed:
`FEEDBACK_CONTEXT_MISMATCH: rejected work item or authority changed`.

**2. `poc-close-guard.py:63` misreads an empty `started:`.** The pattern is
`^started:\s*([^\n#]+?)\s*$` with `re.MULTILINE`; `\s*` crosses the newline, so the
capture begins on the next line. Reproduced standalone on the frontmatter shape
`spacedock new` emits — the match is `'completed:'`. The guard then refuses a
correct close with `admitted_at must equal frontmatter started`, comparing against
a value the reader cannot see. Nothing errors.

## Why one task and not two

They are the same symptom seen twice: the POC close path has never been walked from
prove to terminal, so nothing on it has been exercised. Defect 1's fix is a contract
or authority-rule decision; defect 2's fix is four characters and a test. Splitting
them would ask the same shape stage the same question twice.

## Profile

`pilot-product-slice`. The shape stage owes one ruling: whether the POC route gets a
correction path, or the outcome sections move out of the authority region, or a
POC's answer to findings is only its `direction` and the contract should say so. The
First Officer must not settle that alone.

The previous item on this path selected POC, ran past its declared budget, needed a
Captain amendment mid-flight, and closed with direction `change` for exactly those
reasons. Selecting POC again would repeat a measured mistake.

Verified: the loader resolves all three Pilot legs from this work item.
