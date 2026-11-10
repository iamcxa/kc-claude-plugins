# 0072. Counts cite saved output and learn checks referenced evidence

Date: 2026-11-09

## Status

Accepted

## Context

ADR 0055 accepted the known wrong-count limit in the claim-source replay and
named counts-name-the-run-that-produced-them as its follow-up. That task's
ideation records distinguish the historical behavioral result from its grader's
false pass. Issue iamcxa/kc-claude-plugins#811 reports learn Evidence quoting
18 findings from an earlier pass after a recount said 15. The local stores do
not contain that adopter's record; this is the reporter's account, not a
reproduction of that record.

The task's ideation/scan_replay.py and ideation/learn_replay2.py runs of
2026-11-09 retain the corpus and counters in scan_replay.out and learn_replay.out
on spacedock-state/dev2. The gate replay includes a correct derived "3 of 6"
citing a file that states "1/3" and "2/3". A file-content comparison cannot
judge that arithmetic, so holding an unchecked gate count would reject it.
Learn has a structured evidence-reference join before completion and a pending
claim that invalid completion leaves correctable.

## Decision

**Words:** 「核准（建議）」 — Captain, host question dialog, 2026-11-09,
counts-name-the-run-that-produced-them ideation gate, attempt 1.

**Asked (item 4, verbatim):** 「(4) 數字寫明出處：learn 提案完成時，證據裡的數字在它引用的資料找不到就擋下；摘要裡的「未查核的數字：N」改由工具自己寫進去，不擋、也不用我抄（工人原案是擋到我抄上那一行）。核准即接受上列每一項建議，包括 (4) 改成工具自己寫；要改哪項直接說。」

**Options considered:**
- Write the computed gate disclosure automatically and refuse an unsupported
  learn Evidence count before completion (chosen).
- Hold a gate until FO copies a matching disclosure line (worker's original
  recommendation, replaced by the Captain's amendment).
- Print the unchecked list without writing it into the text the Captain reads.
- Add a command recorder; citing existing saved output is the observed gap.

**Recommended:** The worker recommended the disclosure hold and the learn
reference join. The Captain accepted the learn join and replaced the gate hold
with automatic writing, as task amendment 1 records.

**Protects:**
- `kc-dev-flow-2/scripts/count_tokens.py` — shared count pattern and sentence scan
- `kc-dev-flow-2/scripts/delivery_gate.py` — count_disclosure writes the computed line
- `kc-dev-flow-2/scripts/learning.py` — evaluation checks new add Evidence against its references

The shared pattern recognizes numeric ratios and counts followed by the named
units, with at most one intervening word and grouped thousands. Fenced code,
External rounds and Unchecked counts declarations do not contribute claims.
A gate count is checked when its sentence cites a file resolving within the
task folder and that saved output holds its numbers. question scans question
plus summary and writes Unchecked counts: N into the summary; legacy calls
write into their question file. check includes the PR body and writes into
the ask text. Missing, wrong or duplicate disclosure lines are replaced, with
no content hold. Existing gate checks and their failure exits remain.

For a new learn add completion, each Evidence count must occur in the joined
pack items that its decision references. evaluation refuses a miss before
writing completion, leaving the pending token usable. Reading already
completed records retains structural validation without retroactively
applying this new content check. This is the structured refusal ADR 0055's
reopen condition permits; its claim-source reminder remains in force.

## Consequences

The Captain sees the computed disclosure without copying a line. Checking a
number's presence establishes neither truth nor the command that produced it;
a stale number in a cited file or referenced pack item still passes. Derived
gate counts are disclosed rather than refused; derived learn counts must be
stated in the referenced evidence. Gate diagnostics are bounded to eight
unchecked sentences, twelve words each, while the disclosure counts all of them.

Chat, prose-only lists such as S6/S7 not re-run, and stage reports outside the
gate summary remain unscanned. The PR body is read but not edited, so a reader
on GitHub alone does not see the ask's disclosure. Startup rules, versions and
CI topology do not change. Reopen if citations fail to identify the producing
run, or structured evidence can distinguish arithmetic without rejecting
correct derived results.
