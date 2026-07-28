Run `kc-pr-review` against the checked-out pull request in the current working
directory.

This is a measurement run, so the following constraints override anything the
skill says. Where they conflict with the skill, they win.

1. Do not post anything to GitHub. No review, no comment, no reaction, no
   status. Do not call `gh pr review`, `gh pr comment`, or the GitHub API with
   any non-GET method.
2. Do not modify the working tree. Write scratch files outside the clone. The
   one file you may create is the receipt named below.
3. Do not launch background work and then wait on it or defer to it. If a
   command cannot finish inline, skip it and record that you skipped it. A run
   that stops to wait produces no measurement.
4. Stop at the end of Step 6a. Do not proceed to posting or to any later step.
5. Serialize, as JSON, the findings the flow approved for emission at that
   point, and write them to the path in `KC_PR_FLOW_ABLATION_RECEIPT`.

The receipt is a single JSON object:

    {"schema": "kc-pr-flow.ablation-run/v3",
     "arm": "<KC_PR_FLOW_ABLATION_ARM>",
     "run_index": <KC_PR_FLOW_ABLATION_RUN_INDEX>,
     "slot_index": <KC_PR_FLOW_ABLATION_SLOT_INDEX>,
     "experiment_id": "<KC_PR_FLOW_ABLATION_EXPERIMENT_ID>",
     "nonce": "<KC_PR_FLOW_ABLATION_NONCE>",
     "pr": {"repository": "...", "number": 0, "base_sha": "...", "head_sha": "..."},
     "skill_sha256": "<sha256 of the loaded skills/kc-pr-review/SKILL.md>",
     "arm_manifest_sha256": "<arm_manifest_sha256 from arm-manifest.json at the plugin root>",
     "driver_prompt_sha256": "<KC_PR_FLOW_ABLATION_DRIVER_PROMPT_SHA256>",
     "model_id": "<the model id the runtime reports, not the one requested>",
     "findings": [{"path": "...", "side": "LEFT|RIGHT|FILE",
                   "anchor_sha256": "<sha256 of the anchored line>",
                   "evidence_sha256": "<sha256 of the quoted evidence>",
                   "category": "...", "claim_key": "...",
                   "severity": "CRITICAL|HIGH|MEDIUM|LOW|NIT",
                   "confidence": 0, "line": 0}],
     "usage": {"input_tokens": 0, "output_tokens": 0,
               "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
               "total_cost_usd": 0.0},
     "wallclock_ms": 0,
     "written_at": "<RFC3339, UTC, at the moment you write this file>"}

Emit one entry per finding, in the order the flow produced them. `severity` uses
the skill's own vocabulary exactly as listed. `line` is display metadata and is
not part of the compared projection.

If you cannot produce the receipt, do not write a partial or empty one. Leaving
no receipt is the correct outcome, and it is recorded as a failed run.

---

This file is byte-identical across every arm of an experiment and its SHA-256 is
pinned into every receipt, so a verdict assembled from receipts driven by two
different prompts is rejected rather than reported.

It deliberately names no mechanism internal to the skill — only the stopping
point, the output shape, and the safety constraints. An earlier draft asked for
"the findings that passed the pre-emit gate", which names the very mechanism one
arm has had removed: it re-instructs that arm to run the thing under ablation
and lets the instrument manufacture the null result it exists to test.
