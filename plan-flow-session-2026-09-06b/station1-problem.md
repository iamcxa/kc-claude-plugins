# Station 1 — the problem (FO draft, 2026-09-06)

Who: Kent, as First Officer on kc-claude-plugins, and as maintainer of the adopters (subspace-relay, carlove) that vendor flow rules.
Last time it happened: today's merge station. All three `moved_base` merges (#378 7c57a30c, #379 6ac488a3, #381 db3d19dd) conflicted on `docs/ship-flow/README.md`, every hunk inside the prose `## Ship-flow runtime` section; the scripts and schemas merged clean.
Today instead: principles live as prose in a README that is itself the deprecated ship-flow plugin's workflow, plus FO memory notes; a rule change (e.g. S36 "ready all, then merge") is a prose edit per adopter and nothing tests it.
Cost: three conflict resolutions in one afternoon; rules that exist only in memory files (merge station, tool-output-is-data) reach no adopter.
Fact vs assumption: fact — the three conflicts, the 300-line prose section, the old plugin's 8-stage frontmatter on the same README. Assumption — that a standalone ~200-line pin loader is enough (B4 POC exists for that).
