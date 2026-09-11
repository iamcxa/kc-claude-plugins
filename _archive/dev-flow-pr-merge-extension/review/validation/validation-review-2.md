# dev-flow-pr-merge-extension — validation gate, attempt 2

Candidate: d34abf13 (PR #414, CI green, MERGEABLE). Round 1 finding (released-body hash claim unenforced) fixed: `contract-manifest.json` pins `pr_merge_released_body.sha256`; the contract test fails naming the released body on a real one-word edit (worker cycle 3 and FO isolated check), passes when restored. block==resource byte-for-byte; portable-delivery 14/14 mutants rejected; scope confined to kc-dev-flow/, the adopter mod, two scripts/ tests.
Question for the Captain: approve validation and merge #414?
