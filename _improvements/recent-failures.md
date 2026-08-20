---
schema: kc-dev-flow-recent-failures/v1
observed_home: docs/dev/.spacedock-state/_debriefs/
newest_observed: 2026-07-30-02.md
observed: [2026-07-30-02.md, 2026-07-30-01.md, 2026-07-26-02.md, 2026-07-26-01.md]
generated_from_revision: 974a1fbf6747e519d045cd5b11a02f9d0cc564d6
---

- A harness read `--arms A,A_prime,B` as first-and-last, dropped the middle arm, and returned a plausible verdict for a comparison nobody asked for — wrong answers from the measuring instrument get cited as evidence. Check: assert the parsed arm count equals the count passed.
- A merged PR deleted an enumerated section and took the span-table harness from 80/80 to 50/80. Check: re-derive the table from the live tree; hand-adjusting its line numbers is what the table's own contract forbids.
- `review-post.test.sh` collides on shared payload state when two runs overlap. Check: treat "unsettled prior attempt exists for this payload" as an untrustworthy result and rerun isolated, never as a failure to debug.
- A cross-vendor reviewer timed out, then entered project selection instead of reviewing the diff. Check: an unavailable reviewer reports UNAVAILABLE; no run was represented as a clean verdict, and none should be.
- Release readiness failed on under-versioning, a sanitize violation, an internal-branded GIF, and reachable `js-yaml` advisories — none of which ordinary green CI exposed. Check: run the release gates, not the merge gates.
- release-please produced different changelogs depending on which Conventional Commit paragraph preceded the `BREAKING CHANGE` footer. Check: dry-run parse the squash message before merging, because the squash subject is the release input.
- The same defect shape shipped four times: correct in most places, missed in the one place that mattered, and the first officer caught none of them. Check: allowlist the sites that must change; a shape filter finds the easy ones and misses the load-bearing one.
- `npm test` runs nowhere in CI — 61 of 71 test files belong to plugins no workflow mentions, and the two required checks verify manifests, not behavior. Check: confirm a suite actually runs in CI before adding a gate that assumes it does.
- Five tracked tests hardcode one machine's absolute path, so the suite is green there and red everywhere else. Check: run from a clean checkout at a different path before trusting green.
- Reading the diff did not find the consumer-boundary defects; compiling a fixture and reading the generated script did, after five reviews had passed that same diff. Check: exercise the artifact the consumer sees, not the change that produced it.
- A documented guarantee — "leaves exactly one path to the POST" — landed with its code, passed CI, and passed review while being false; one crafted input walked a second path. Check: an absolute names its enforcement point or becomes the bounded claim the code supports.
- A symmetry assertion held in both worlds and proved nothing; it surfaced only because the RED count came in three lower than the number of assertions written. Check: count RED assertions against assertions authored, and assert the reason, not just the outcome token.
