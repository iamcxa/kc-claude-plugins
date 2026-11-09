# Registered replay results

Primary results use the unchanged pre-registered grader. The separate post-hoc manual column was defined after the first valid result, under FO dispatch/implementation-1-message-3.md. It does not change AC-3.

| Run | Host | Arm / wording | Verdict | Found | Read comments | Precision miss | Tokens | Counted | post-hoc manual |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-base-1-registered | claude | base / 0 | REJECTED | True | True | False | {"usage": {"input_tokens": 94, "cache_creation_input_tokens": 202015, "cache_read_input_tokens": 7371336, "output_tokens": 38405, "output_tokens_details": {"thinking_tokens": 14713}, "server_tool_use": {"web_search_requests": 0, "web_fetch_requests": 0}, "service_tier": "standard", "cache_creation": {"ephemeral_1h_input_tokens": 201230, "ephemeral_5m_input_tokens": 0}, "inference_geo": "global", "iterations": [{"input_tokens": 2, "output_tokens": 907, "cache_read_input_tokens": 212314, "cache_creation_input_tokens": 523, "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 523}, "type": "message"}], "speed": "standard", "fallback_credit": null}, "modelUsage": {"claude-opus-5-5": {"inputTokens": 94, "outputTokens": 38405, "cacheReadInputTokens": 7371336, "cacheCreationInputTokens": 202015, "webSearchRequests": 0, "costUSD": 3.8565082, "contextWindow": 1000000, "maxOutputTokens": 128000, "thinkingTokens": 14713, "cacheCreationEphemeral5mInputTokens": 0, "cacheCreationEphemeral1hInputTokens": 201230, "canonicalModel": "claude-opus-5-5", "provider": "firstParty", "costBasis": "list"}, "claude-fable-5-1": {"inputTokens": 196282, "outputTokens": 3873, "cacheReadInputTokens": 0, "cacheCreationInputTokens": 0, "webSearchRequests": 0, "costUSD": 2.15647, "contextWindow": 1000000, "maxOutputTokens": 64000, "thinkingTokens": 0, "cacheCreationEphemeral5mInputTokens": 0, "cacheCreationEphemeral1hInputTokens": 0, "canonicalModel": "claude-fable-5-1", "provider": "firstParty", "costBasis": "list"}}, "total_cost_usd": 6.0129782} | True | True |
| claude-base-2-registered | claude | base / 0 | REJECTED | True | True | False | {"usage": {"input_tokens": 100, "cache_creation_input_tokens": 194955, "cache_read_input_tokens": 7506632, "output_tokens": 42568, "output_tokens_details": {"thinking_tokens": 14590}, "server_tool_use": {"web_search_requests": 0, "web_fetch_requests": 0}, "service_tier": "standard", "cache_creation": {"ephemeral_1h_input_tokens": 194955, "ephemeral_5m_input_tokens": 0}, "inference_geo": "global", "iterations": [{"input_tokens": 2, "output_tokens": 1213, "cache_read_input_tokens": 208154, "cache_creation_input_tokens": 235, "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 235}, "type": "message"}], "speed": "standard", "fallback_credit": null}, "modelUsage": {"claude-opus-5-5": {"inputTokens": 100, "outputTokens": 42568, "cacheReadInputTokens": 7506632, "cacheCreationInputTokens": 194955, "webSearchRequests": 0, "costUSD": 3.9127264000000004, "contextWindow": 1000000, "maxOutputTokens": 128000, "thinkingTokens": 14590, "cacheCreationEphemeral5mInputTokens": 0, "cacheCreationEphemeral1hInputTokens": 194955, "canonicalModel": "claude-opus-5-5", "provider": "firstParty", "costBasis": "list"}}, "total_cost_usd": 3.9127264000000004} | True | True |
| claude-base-3-registered | claude | base / 0 | REJECTED | True | True | False | {"usage": {"input_tokens": 110, "cache_creation_input_tokens": 180635, "cache_read_input_tokens": 7673414, "output_tokens": 30198, "output_tokens_details": {"thinking_tokens": 7801}, "server_tool_use": {"web_search_requests": 0, "web_fetch_requests": 0}, "service_tier": "standard", "cache_creation": {"ephemeral_1h_input_tokens": 178679, "ephemeral_5m_input_tokens": 0}, "inference_geo": "global", "iterations": [{"input_tokens": 2, "output_tokens": 1053, "cache_read_input_tokens": 191873, "cache_creation_input_tokens": 240, "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 240}, "type": "message"}], "speed": "standard", "fallback_credit": null}, "modelUsage": {"claude-opus-5-5": {"inputTokens": 110, "outputTokens": 30198, "cacheReadInputTokens": 7673414, "cacheCreationInputTokens": 180635, "webSearchRequests": 0, "costUSD": 3.578294799999999, "contextWindow": 1000000, "maxOutputTokens": 128000, "thinkingTokens": 7801, "cacheCreationEphemeral5mInputTokens": 0, "cacheCreationEphemeral1hInputTokens": 178679, "canonicalModel": "claude-opus-5-5", "provider": "firstParty", "costBasis": "list"}, "claude-fable-5-1": {"inputTokens": 172180, "outputTokens": 15384, "cacheReadInputTokens": 0, "cacheCreationInputTokens": 0, "webSearchRequests": 0, "costUSD": 2.491, "contextWindow": 1000000, "maxOutputTokens": 64000, "thinkingTokens": 0, "cacheCreationEphemeral5mInputTokens": 0, "cacheCreationEphemeral1hInputTokens": 0, "canonicalModel": "claude-fable-5-1", "provider": "firstParty", "costBasis": "list"}}, "total_cost_usd": 6.069294799999999} | True | True |
| claude-candidate-1-registered | claude | candidate / 1 | REJECTED | True | True | False | {"usage": {"input_tokens": 80, "cache_creation_input_tokens": 170036, "cache_read_input_tokens": 5315802, "output_tokens": 27011, "output_tokens_details": {"thinking_tokens": 8416}, "server_tool_use": {"web_search_requests": 0, "web_fetch_requests": 0}, "service_tier": "standard", "cache_creation": {"ephemeral_1h_input_tokens": 168088, "ephemeral_5m_input_tokens": 0}, "inference_geo": "global", "iterations": [{"input_tokens": 2, "output_tokens": 1282, "cache_read_input_tokens": 180780, "cache_creation_input_tokens": 742, "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 742}, "type": "message"}], "speed": "standard", "fallback_credit": null}, "modelUsage": {"claude-opus-5-5": {"inputTokens": 80, "outputTokens": 27011, "cacheReadInputTokens": 5315802, "cacheCreationInputTokens": 170036, "webSearchRequests": 0, "costUSD": 2.9581444000000006, "contextWindow": 1000000, "maxOutputTokens": 128000, "thinkingTokens": 8416, "cacheCreationEphemeral5mInputTokens": 0, "cacheCreationEphemeral1hInputTokens": 168088, "canonicalModel": "claude-opus-5-5", "provider": "firstParty", "costBasis": "list"}, "claude-fable-5-1": {"inputTokens": 166600, "outputTokens": 10966, "cacheReadInputTokens": 0, "cacheCreationInputTokens": 0, "webSearchRequests": 0, "costUSD": 2.2142999999999997, "contextWindow": 1000000, "maxOutputTokens": 64000, "thinkingTokens": 0, "cacheCreationEphemeral5mInputTokens": 0, "cacheCreationEphemeral1hInputTokens": 0, "canonicalModel": "claude-fable-5-1", "provider": "firstParty", "costBasis": "list"}}, "total_cost_usd": 5.1724444} | False | True |
| claude-candidate-2-registered | claude | candidate / 1 | no verdict | None | True | None | null | False | None |
| claude-candidate-3-registered | claude | candidate / 1 | no verdict | None | True | None | null | False | None |
| codex-base-1 | codex | base / 0 | no verdict | None | False | None | null | False | None |
| codex-base-1-fixed | codex | base / 0 | REJECTED | True | True | False | {"input_tokens": 3558585, "cached_input_tokens": 3432704, "cache_write_input_tokens": 0, "output_tokens": 28699, "reasoning_output_tokens": 9219} | False | True |
| codex-base-1-registered | codex | base / 0 | REJECTED | False | True | False | {"input_tokens": 2245802, "cached_input_tokens": 2128000, "cache_write_input_tokens": 0, "output_tokens": 20393, "reasoning_output_tokens": 5657} | True | True |
| codex-base-2-registered | codex | base / 0 | REJECTED | True | True | False | {"input_tokens": 6018775, "cached_input_tokens": 5883008, "cache_write_input_tokens": 0, "output_tokens": 30958, "reasoning_output_tokens": 11695} | False | True |
| codex-base-3-registered | codex | base / 0 | REJECTED | True | True | False | {"input_tokens": 6035001, "cached_input_tokens": 5899264, "cache_write_input_tokens": 0, "output_tokens": 33408, "reasoning_output_tokens": 12655} | True | True |
| codex-candidate-1-registered | codex | candidate / 1 | REJECTED | True | True | False | {"input_tokens": 5760144, "cached_input_tokens": 5614464, "cache_write_input_tokens": 0, "output_tokens": 30531, "reasoning_output_tokens": 11709} | True | True |
| codex-candidate-2-registered | codex | candidate / 1 | REJECTED | True | True | False | {"input_tokens": 2487826, "cached_input_tokens": 2381952, "cache_write_input_tokens": 0, "output_tokens": 22051, "reasoning_output_tokens": 7227} | True | True |
| codex-candidate-3-registered | codex | candidate / 1 | REJECTED | True | True | False | {"input_tokens": 2731642, "cached_input_tokens": 2608896, "cache_write_input_tokens": 0, "output_tokens": 22367, "reasoning_output_tokens": 6604} | False | True |

## Per-host comparison

{
  "codex": {
    "valid_runs": {
      "base": 2,
      "candidate": 2
    },
    "found": {
      "base": 1,
      "candidate": 2
    },
    "passed": false,
    "precision_misses": 0,
    "mean_report_words": {
      "base": 842,
      "candidate": 1030.5
    },
    "post_hoc_found": {
      "base": 2,
      "candidate": 2
    },
    "post_hoc_complete": false,
    "primary_beats_base": null,
    "post_hoc_beats_base": null,
    "counts_disagree_on_beating_base": null,
    "precision_misses_all_completed": 0,
    "precision_candidate_reports_assessed": 3,
    "precision_candidate_reports_missing": 0,
    "available_subset_primary_beats_base": true,
    "available_subset_post_hoc_beats_base": false,
    "available_subset_counts_disagree": true
  },
  "claude": {
    "valid_runs": {
      "base": 3,
      "candidate": 0
    },
    "found": {
      "base": 3,
      "candidate": 0
    },
    "passed": false,
    "precision_misses": 0,
    "mean_report_words": {
      "base": 958.3333333333334,
      "candidate": null
    },
    "post_hoc_found": {
      "base": 3,
      "candidate": 0
    },
    "post_hoc_complete": false,
    "primary_beats_base": null,
    "post_hoc_beats_base": null,
    "counts_disagree_on_beating_base": null,
    "precision_misses_all_completed": 0,
    "precision_candidate_reports_assessed": 1,
    "precision_candidate_reports_missing": 2,
    "available_subset_primary_beats_base": null,
    "available_subset_post_hoc_beats_base": null,
    "available_subset_counts_disagree": null
  }
}

Only completed reports without fixture gaps or falsifier defects enter host counts. Original interrupted harness attempt is retained but excluded by FO dispatch/implementation-1-message-2.md. A run with any refused call is excluded. Three valid base and candidate runs per host are required; available-subset comparisons are diagnostic and do not satisfy AC-3. The comment was available from run start; these are reconstructed historical responses, not live PR proof. No delivery, adoption or future error-rate claim follows.

## Post-hoc deciding lines

claude-base-1-registered — post-hoc True:

> - F1 Material: on the README's new dispatch path, dispatch_stage.py drops the round-two step-back questions (kc-dev-flow-2/scripts/dispatch_stage.py `main`, where checks pass).

claude-base-2-registered — post-hoc True:

> - F1 Material: dispatch_stage.py `main` discards successful `dispatch_records.py` stderr, so the round-two step-back questions are never shown before dispatch. Boundary contract[docs/adr/0026-role-calls-are-owed-on-counts-read-from-task-records-and-a-dated-call-clears-them.md#consequences] (amended 2026-11-03); trigger acceptance step 4, probe.json, Codex review comment 4505793059 on this head. Needs decision instead only if FO reads the design's "prints nothing of theirs" as a ruling over ADR 0026.

claude-base-3-registered — post-hoc True:

> - F1 Material: The wrapper swallows dispatch_records.py's step-back questions on a successful check.

claude-candidate-1-registered — post-hoc True:

> - F1 Material: a successful round-two dispatch built through `dispatch_stage.py` does not show the step-back questions (Codex P2, review comment 4505793059 on 778367ad). `main` captures both checks' output and writes stderr only when a check fails.

codex-base-1-fixed — post-hoc True:

> - F1 Material: Same-head review comment 4505793059 reproduces: valid repeated-symptom dispatch suppresses the required operator questions (dispatch_stage.py:193–202).

codex-base-1-registered — post-hoc True:

> - F1 Material: Successful checker stderr is discarded by the prescribed dispatcher (kc-dev-flow-2/scripts/dispatch_stage.py:191-202).

codex-base-2-registered — post-hoc True:

> - F1 Material: Candidate suppresses successful checkers' required step-back reminder (kc-dev-flow-2/scripts/dispatch_stage.py:194–202); independently confirms https://github.com/iamcxa/kc-claude-plugins/pull/812#discussion_r4505793059, original_commit_id 778367adde2e20e0b3e51966ddba2d9f77f9e614. Earlier comment 4505536959 originated at afa4523468 and its preservation defect is repaired by the verified whole-scope guard; current-commit mapping alone does not make it a new finding.

codex-base-3-registered — post-hoc True:

> - F2 Material: Successful record checks lose the repeated-diagnosis step-back reminder.

codex-candidate-1-registered — post-hoc True:

> - F1 Material: current-head review comment [4505793059](https://github.com/iamcxa/kc-claude-plugins/pull/812#discussion_r4505793059) is independently reproduced at `kc-dev-flow-2/scripts/dispatch_stage.py:193–201`. Released user/workflow: First Officer using the prescribed second implementation dispatch with the same symptom. Observable harm: the wrapper returns a successful real envelope while suppressing the required three questions. Boundary: contract[docs/adr/0026-role-calls-are-owed-on-counts-read-from-task-records-and-a-dated-call-clears-them.md#consequences], 2026-11-03 amendment, requires the reminder before dispatch. Trigger: `reproduce-warning.py`, `warning-probe.log`, repeated in `acceptance.log`; direct strict checker exits 0 with the questions, wrapper exits 0 without them. No supplied FO decline or Captain waiver covers it; return for authorized repair and exact-head validation.

codex-candidate-2-registered — post-hoc True:

> - F1 Material: Candidate drops successful record checks' required step-back questions (kc-dev-flow-2/scripts/dispatch_stage.py:193-202; PR inline comment 4505793059).

codex-candidate-3-registered — post-hoc True:

> - F1 Material: Required step-back reminder is suppressed on successful repeated dispatch.

## FO reading cost

{
  "all_completed": {
    "base": 1107.5714285714287,
    "candidate": 937.5
  },
  "valid": {
    "base": 911.8,
    "candidate": 1030.5
  }
}

The startup/dispatch/idle/merge-ask inputs are unchanged. Worker principles and unchanged workflow bytes are measured in words.json.

## Precision review

precision-review.json audits whether the old comment was actually called unaddressed; auto_precision_signal remains in results.json. The excluded Codex base-2 run mentions that old comment inside its F1 paragraph but explicitly says it is repaired: its broad automatic signal is a false positive. Primary target grading is unchanged. Report word counts use the full appended report output, including any superseding entries.

## Final disposition

HOLD: AC-3 is not claimed. The original 12 scheduled cells were attempted on both hosts; 14 raw attempts include the two excluded preliminary runs. Only 7 reports meet the registered validity rules. Five scheduled calls were refused by the frozen transport; two of those Claude candidate runs also timed out without reports at the registered 1800-second limit. Final CLI token totals were not returned for those timeouts; per-message usage snapshots are retained separately, without inventing a total. There is no Claude-only substitute and no Codex route failure claim.

Claude base scored 3 of 3, so the strict candidate-greater-than-base bar cannot be achieved for this fixed baseline even with three candidate hits. Codex's available valid subset differs by scoring method: registered 1/2 base versus 2/2 candidate, post-hoc 2/2 versus 2/2. The primary method says candidate beats base on that subset; the post-hoc method says tied. This is a disclosed difference, not an eligible three-per-arm result; the Captain owns the interpretation under FO message-3.

Wording 2 was not run: valid comparisons are incomplete, the Claude baseline is saturated, and the remaining budget cannot complete the required valid cells. No third wording or further fixture extension was applied. Stop at 14, not 16, because even two perfect retries could supply only 9 valid reports, short of 12. Recommend keeping the product candidate local and returning the evidence route to FO/Captain; no improvement, publication, merge, adoption or release is proved.
