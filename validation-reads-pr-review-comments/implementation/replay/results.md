# Registered replay results

| Run | Host | Arm / wording | Verdict | Found | Read comments | Precision miss | Tokens | Counted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| codex-base-1 | codex | base / 0 | no verdict | False | False | False | null | False |
| codex-base-1-fixed | codex | base / 0 | REJECTED | True | True | False | {"input_tokens": 3558585, "cached_input_tokens": 3432704, "cache_write_input_tokens": 0, "output_tokens": 28699, "reasoning_output_tokens": 9219} | False |
| codex-base-1-registered | codex | base / 0 | REJECTED | False | True | False | {"input_tokens": 2245802, "cached_input_tokens": 2128000, "cache_write_input_tokens": 0, "output_tokens": 20393, "reasoning_output_tokens": 5657} | True |
| codex-base-2-registered | codex | base / 0 | no verdict | False | False | False | null | False |
| codex-base-3-registered | codex | base / 0 | no verdict | False | False | False | null | False |
| codex-candidate-1-registered | codex | candidate / 1 | no verdict | False | False | False | null | False |
| codex-candidate-2-registered | codex | candidate / 1 | no verdict | False | False | False | null | False |
| codex-candidate-3-registered | codex | candidate / 1 | no verdict | False | False | False | null | False |

## Per-host comparison

{
  "codex": {
    "valid_runs": {
      "base": 1,
      "candidate": 0
    },
    "found": {
      "base": 0,
      "candidate": 0
    },
    "passed": false,
    "precision_misses": 0,
    "mean_report_words": {
      "base": 797,
      "candidate": null
    }
  },
  "claude": {
    "valid_runs": {
      "base": 0,
      "candidate": 0
    },
    "found": {
      "base": 0,
      "candidate": 0
    },
    "passed": false,
    "precision_misses": 0,
    "mean_report_words": {
      "base": null,
      "candidate": null
    }
  }
}

Only completed reports without fixture gaps or falsifier defects enter host counts. Original interrupted harness attempt is retained but excluded by FO dispatch/implementation-1-message-2.md. A run with any refused call is excluded. Three valid base and candidate runs per host are required. The comment was available from run start; these are reconstructed historical responses, not live PR proof. No delivery, adoption or future error-rate claim follows.
