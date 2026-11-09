# Frozen PR #812 replay fixture

Authorized by dispatch/implementation-1-message-1.md. Cutoff: 2026-11-08T11:13:00Z.
Every substitution and removal with source, record id and timestamp is in rewrites.json.
Live sources are preserved under ../source; they are not served. PR fields, checks and run attempt 3 use the contemporaneous hosted-refresh captures. The PR body uses the committed prepared body, not a historical GitHub response. Review comment moving commit_id values are frozen to the historical head; original_commit_id is retained. The target comment exists at run start, unlike the original two-minute delay. All other records created or updated after cutoff are excluded. Shim calls not registered are refused, logged and invalidate a run.
