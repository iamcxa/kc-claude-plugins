# Surface-map residual

The installed checker now resolves actual committed pairs: upstream af70297ddae6ec64444849e8e3fcf57484bc16e1..552df847e6a845a6cc5ee59327f2d38161192541 and local c9c5752fda853737d4a937ad7f59564c5651ca53..fa69e442bf7899db8c72c515ecc88ea7712e8787. Retained executed outputs: ../implementation-evidence/local-product-surface-checks.json; both exit 1 (eight upstream and one local missing SURFACE lines).

The reviewed manual table already maps all nine files to accepted obligations and native evidence. The checker requires a literal `SURFACE: path -> obligation | without-it command | git removal variant` line. It mechanically parses command strings and path binding; it neither executes those commands nor proves that they ran. The existing meaningful correction-removal control uses a Go overlay for the rollback change and makes both peer-edit cases fail. No recorded Git-removal pair exists for every file, especially help/docs/test surfaces.

Serializing invented removal commands would only produce a structural pass. It would not add behavioral proof. No tautological presence checks, new per-file ablations, standing enforcement, or checker changes were introduced. Preserve the exact automated failure and the independent manual necessity review as distinct results. This residual is included in both Draft bodies; it is not described as passing coverage.
