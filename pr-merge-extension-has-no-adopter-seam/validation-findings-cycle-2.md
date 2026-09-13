# Validation findings, cycle 2 — candidate `17915d9e`

All four acceptance criteria passed again and cycle 1's load-failed item closed.
Two of these three defects were introduced by cycle 1's own fixes.

1. **The bare marker-count check forbids the adopter region this work declares.**
   `scripts/kc-dev-flow-contract-test.py` counted the marker over the whole file
   and sat before the block boundary was computed, so adopter prose after `:end`
   that mentions the marker exited 1. Ruling: bound the count to
   `pr_merge_mod[:mod_extension_end]`.
2. **The version-skew remedy is unrunnable in an adopter checkout.** The
   release-please runtime lives outside the plugin. Ruling: delete the command; an
   adopter on skew stops and reports upstream.
3. **Two shipped fixture resources cite an unrecorded agreement.** The release-please
   `17.11.1` agreement is true and was re-derived across all 13 rows, but it is not
   written in the section the files cite. Ruling: write it there.
