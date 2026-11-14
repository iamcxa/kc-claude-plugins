# Blind reader dispositions

Inputs: shipped contract bytes, fourteen fixture asks/answers, and fifty-six declared clocks only. The reader did not see implementation or expected product output. See blind-output/report.md for hashes and questions; blind-comparison.json compares actual candidate CLI output.

1. Inclusive instant: accepted. Section 8 says lines written by that instant. Product and blind reader close at the answer instant.
2. Minute rounding: accepted as unspecified presentation precision. Product retains exact waiting_since but rounds elapsed minutes to one decimal, matching the pre-existing timeline convention. Six numeric differences are no more than 0.05 minute; blind-comparison.json records each, with an explicit 0.051-minute comparison tolerance. No date or membership tolerance was applied.
3. Ordering/envelope: accepted. The contract promises neither; comparison joins by key and checks duplicates separately.
4. Local export enumeration: accepted for this local proof; release and remote-branch reading remain unverified.
5. Accepted-event interruptions: accepted. Contract section 4 explicitly ignores invalid post-close events. These fixtures do not exercise that branch; the writer suite does.
6. Future-version unknown state: accepted as conservative. It remains unknown; the product's existing reader test exercises the same choice. Not a new external compatibility guarantee.
7. Truncated prose: not repaired during blind read. It does not alter synthetic event folding, but limits historical fidelity; see finding F3 in findings.md.

No clarification from an author was needed. Every reader question/choice above has a disposition; none is silently treated as a product requirement.
