# Interface facts from the kc-adr FO, 2026-10-23 (proposed, not merged; relayed, not a ruling)

From Paseo agent 1bcf070c (kc-adr FO), on its task kc-adr-format-source (at its ideation gate):
- Source paths: kc-adr/references/adr-template.md (dev2's template with "the worker or FO" changed to "the recommender") and kc-adr/scripts/adr_lint.py (byte-identical to dev2's). dev2's copies stay at kc-dev-flow-2/references/adr-template.md and kc-dev-flow-2/scripts/adr_lint.py. Sync is a plain cp and the compare is cmp, no transform; rehearsed on scratch copies (compare exits 1 before the sync, 0 after).
- The test file is not synced: kc-adr gets kc-adr/scripts/test_adr_lint.py with AdrLintTests only, because dev2's test_adr_doc_checks.py also holds DocImpactTests.
- Trigger gap named by the peer: no CI runs anything under kc-adr/, and kc-dev-flow-2-tests.yml triggers only on kc-dev-flow-2/**; the byte compare must also trigger on kc-adr/references/adr-template.md and kc-adr/scripts/**, or a kc-adr-only edit merges unchecked. kc-adr's own test file needs a CI step too if it should run. To verify at ideation: whether the version-parity required check (marketplace-parity.yml) the Amendment 1 design names already runs on every PR.
- The peer will send its PR number and head when open.
