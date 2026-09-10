# Captain-authorized local commits

Exactly two local product commits were created from the independently reviewed, Captain-approved nine files. No product content was changed during this action. Captain accepted the retained baseline cask-version failure for these commits; this is not permission for product push, PR, merge, installation or terminalization.

| Repository | Parent | Commit | Exact committed patch SHA-256 |
| --- | --- | --- | --- |
| Upstream | af70297ddae6ec64444849e8e3fcf57484bc16e1 | 552df847e6a845a6cc5ee59327f2d38161192541 | 6dc9e67966b29ba29eca9ce28a375081ff6c0345ac32f4ef13846bc8d0e2f93e |
| Local coordinator | c9c5752fda853737d4a937ad7f59564c5651ca53 | fa69e442bf7899db8c72c515ecc88ea7712e8787 | 2ffa88aaef51a4b482a71d190b5f3cbcbc2a5579d539a7cb87adfab12d685d0c |

Both roots/branches/base hashes and exact file sets were verified immediately before staging. The index began empty; only the eight upstream files and one local mod were staged and committed. Parent/commit diffs match the previously approved patches byte for byte. Both product trees are clean. Raw commands, paths and outputs are in local-product-commit-receipt.json.

## Authorized post-commit check

The installed surface-map checker now successfully resolves real base/candidate commit objects in both repositories. It returns 1 for both maps: the retained independently reviewed manual map is a table, whereas the checker requires one `SURFACE:` line plus path-bound Git-removal/without-it command pairs for every changed file (including Go tests). Raw output is in local-product-surface-checks.json: eight missing upstream SURFACE lines and one missing local line.

This is an evidence-format/retained-proof limitation, not a passing automated mapping result. Existing native tests, the exact correction-removal Go overlay, and independent necessity review remain their original evidence; they do not establish an executed Git-removal pair for every file. No invented removal command or unexecuted proof was added to make the checker pass, and no new ablation/full/race tests were run. The manual map and frozen approved report/Briefing remain unchanged.

## Remaining boundaries

The final unchanged-source focused/full/race results remain bound by the matching committed patch digest: focused 76 pass; full/race each 3,107 pass events, 11 skip, and the pre-existing cask leaf/parent failures accepted by Captain for this local commit step. Optional RoboRev remains unavailable because provider/model invocation is not authorized; zero requests. No product push/PR/merge/install, task terminalization, original live approval/rebinding, cloud operation or resource cleanup occurred. State receipt publication is separately authorized.
