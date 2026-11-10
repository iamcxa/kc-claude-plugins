feat(kc-dev-flow-2): disclose unchecked counts and validate learn evidence

Automatically write the computed Unchecked counts line into validation summaries and merge-ask text, including counts in the PR body. Refuse new learn add completions when Evidence counts are absent from their referenced pack items, leaving the pending claim correctable.

Captain amendment 2 treats numbers immediately following Cycle, Round, Batch, Step, Stage, Amendment, Attempt or Phase as sequence identifiers. The validator's original "Cycle 1 FO line" entry now completes without rewriting its Evidence or references; an unsupported "2 cells" still refuses and accepts correction using the same token.

Validation at 4a146449de8ad43f1eb67e59599215989c327645 (2026-11-10 UTC) is recorded in counts-name-the-run-that-produced-them/validation/implementation-4 on spacedock-state/dev2. probe.py covers the unchanged historical entry, the named labels and adjacent real counts through learning CLI and gate callers. mutations.py and retained-mutations.py demonstrate failures after removing each protected boundary. suite.json/.log carry the full-suite producer result; lint, ADR, refreshed reservation, comment, replay and reading-cost records bind their commands to the candidate.

ADR 0072 records the count disclosure and learn reference decision; amendment 2's bounded compatibility correction is recorded in the task. Startup budget, versions and CI workflows are unchanged. Presence in cited evidence establishes neither truth nor the command that produced it; the original issue's adopter record remains unavailable.

This worker made a local repair commit on the existing PR #822 branch. Product push, RoboRev and hosted CI for this candidate remain FO-owned and not run by this worker. CI cost per PR was not measured.

Evidence: https://github.com/iamcxa/kc-claude-plugins/tree/spacedock-state/dev2/counts-name-the-run-that-produced-them/validation/implementation-4
