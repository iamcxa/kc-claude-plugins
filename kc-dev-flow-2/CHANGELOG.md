# Changelog

## [0.22.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.21.0...kc-dev-flow-2-v0.22.0) (2026-10-13)


### Features

* **kc-dev-flow-2:** journey-map extension records a Captain ruling as a versioned footprint ([#627](https://github.com/iamcxa/kc-claude-plugins/issues/627)) ([133f131](https://github.com/iamcxa/kc-claude-plugins/commit/133f1315c4c44d902ddc3accf67cf23e99f1431e))


### Bug Fixes

* **kc-dev-flow-2:** FO checks the workflow README against the trunk's before each dispatch ([#631](https://github.com/iamcxa/kc-claude-plugins/issues/631)) ([a8fe8d3](https://github.com/iamcxa/kc-claude-plugins/commit/a8fe8d39899e3124769ff03c829af311af02a353))
* **kc-dev-flow-2:** read a Copilot answer without a review as not run, not as answered ([#630](https://github.com/iamcxa/kc-claude-plugins/issues/630)) ([6d0f8da](https://github.com/iamcxa/kc-claude-plugins/commit/6d0f8da951b5ea9ea50fca6bd3685fc360bf502f))

## [0.21.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.20.0...kc-dev-flow-2-v0.21.0) (2026-10-13)


### Features

* **kc-dev-flow-2:** peers extension lets FO ask a peer session of the same harness ([#620](https://github.com/iamcxa/kc-claude-plugins/issues/620)) ([f74f380](https://github.com/iamcxa/kc-claude-plugins/commit/f74f38042e8dab8683ae0b2633ca5f84bae07eee))


### Bug Fixes

* **kc-dev-flow-2:** FO runs the acceptance script as written before showing it at the validation gate ([#625](https://github.com/iamcxa/kc-claude-plugins/issues/625)) ([a592e8b](https://github.com/iamcxa/kc-claude-plugins/commit/a592e8b7241f4f278c23b3a013ff4e0db281570d))

## [0.20.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.19.1...kc-dev-flow-2-v0.20.0) (2026-10-12)


### Features

* **kc-dev-flow-2:** a second remote reviewer joins only when a recorded trigger holds ([#618](https://github.com/iamcxa/kc-claude-plugins/issues/618)) ([2c249ec](https://github.com/iamcxa/kc-claude-plugins/commit/2c249ec712f582c1b81fe61b3af4b3b3e8065988))
* **kc-dev-flow-2:** copilot extension requests GitHub Copilot review and waits for its answer on the head ([#616](https://github.com/iamcxa/kc-claude-plugins/issues/616)) ([df01c81](https://github.com/iamcxa/kc-claude-plugins/commit/df01c819d13591366dcb1b28277b06ef6a9114b1))
* **kc-dev-flow-2:** the learn extension saves the observer report in the task's state ([#614](https://github.com/iamcxa/kc-claude-plugins/issues/614)) ([ac6dc6e](https://github.com/iamcxa/kc-claude-plugins/commit/ac6dc6edfbf305aa31ad4855a7b646899140669c))

## [0.19.1](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.19.0...kc-dev-flow-2-v0.19.1) (2026-10-12)


### Bug Fixes

* **kc-dev-flow-2:** an ADR without a Words line can still be a precedent, quoted by its decision sentence ([#612](https://github.com/iamcxa/kc-claude-plugins/issues/612)) ([fcc6bc3](https://github.com/iamcxa/kc-claude-plugins/commit/fcc6bc3fafd116addf0283f0938e4584f2738011))

## [0.19.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.18.0...kc-dev-flow-2-v0.19.0) (2026-10-12)


### Features

* **kc-dev-flow-2:** FO checks the loaded package is not older than the workflow README before each dispatch ([#610](https://github.com/iamcxa/kc-claude-plugins/issues/610)) ([f9d2dc8](https://github.com/iamcxa/kc-claude-plugins/commit/f9d2dc8aced2f5560f6f2cb0ea21bb1766dd986f))


### Bug Fixes

* **kc-dev-flow-2:** pr_watch reads Codex review only for a PR added with --codex ([#609](https://github.com/iamcxa/kc-claude-plugins/issues/609)) ([6396786](https://github.com/iamcxa/kc-claude-plugins/commit/639678689b3bf4705f05b97b9aae69b9b55481cb))

## [0.18.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.17.0...kc-dev-flow-2-v0.18.0) (2026-10-12)


### Features

* **kc-dev-flow-2:** learn extension at archive, decision ledger, observer and decide-by-precedent ([#605](https://github.com/iamcxa/kc-claude-plugins/issues/605)) ([5345420](https://github.com/iamcxa/kc-claude-plugins/commit/5345420e8e137079c2044d97f3ce1b0d86744265))

## [0.17.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.16.0...kc-dev-flow-2-v0.17.0) (2026-10-12)


### Features

* **kc-dev-flow-2:** optional extensions, with codex review and a roborev gate as the first two ([#603](https://github.com/iamcxa/kc-claude-plugins/issues/603)) ([49c670c](https://github.com/iamcxa/kc-claude-plugins/commit/49c670cb1a7a806043973fa7c1552fc17a0ddae8))


### Bug Fixes

* **kc-dev-flow-2:** close eight workflow gaps and four script findings (batch 3) ([4361b36](https://github.com/iamcxa/kc-claude-plugins/commit/4361b36040303e056c172e40cca2454e3165f77b))

## [0.16.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.15.1...kc-dev-flow-2-v0.16.0) (2026-10-11)


### Features

* **kc-dev-flow-2:** maintain-flow replays a closed task before a behaviour change ships ([#598](https://github.com/iamcxa/kc-claude-plugins/issues/598)) ([ce66abd](https://github.com/iamcxa/kc-claude-plugins/commit/ce66abddb8a6f49623ffa31d4ee02b953f14c72a))

## [0.15.1](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.15.0...kc-dev-flow-2-v0.15.1) (2026-10-11)


### Bug Fixes

* **kc-dev-flow-2:** three 0.15.0 workflow gaps found by Codex on an adopter sync ([#596](https://github.com/iamcxa/kc-claude-plugins/issues/596)) ([a26efa4](https://github.com/iamcxa/kc-claude-plugins/commit/a26efa4fe8e6ea92030667a3611cdfbdbf4c4359))

## [0.15.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.14.0...kc-dev-flow-2-v0.15.0) (2026-10-11)


### Features

* **kc-dev-flow-2:** FO watches the PRs it opens and learns their changes itself ([#594](https://github.com/iamcxa/kc-claude-plugins/issues/594)) ([2c9183f](https://github.com/iamcxa/kc-claude-plugins/commit/2c9183f49989390d80a2ccffb713de7b25de87de))
* **kc-dev-flow-2:** read a Codex PR review round from the PR itself ([#593](https://github.com/iamcxa/kc-claude-plugins/issues/593)) ([2b165d4](https://github.com/iamcxa/kc-claude-plugins/commit/2b165d4b1b0ec58414484f88c9aaa433fbeb7c8f))
* **kc-dev-flow-2:** settle the batch-2 workflow rulings ([#592](https://github.com/iamcxa/kc-claude-plugins/issues/592)) ([8134645](https://github.com/iamcxa/kc-claude-plugins/commit/8134645d09b31248343373cf199bfe43b33e8ec3))


### Bug Fixes

* **kc-dev-flow-2:** validation checks every ADR the candidate changed, without typed numbers ([#590](https://github.com/iamcxa/kc-claude-plugins/issues/590)) ([03045a4](https://github.com/iamcxa/kc-claude-plugins/commit/03045a47ea850266b46dad557229343bd56e1d04))

## [0.14.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.13.0...kc-dev-flow-2-v0.14.0) (2026-10-10)


### Features

* **kc-dev-flow-2:** a Captain ruling must answer the question it settles ([#585](https://github.com/iamcxa/kc-claude-plugins/issues/585)) ([7d97d3a](https://github.com/iamcxa/kc-claude-plugins/commit/7d97d3aa15ed443be1d6fb0e7dff25c264a090e5))
* **kc-dev-flow-2:** give each worker only the workflow text it acts on ([#587](https://github.com/iamcxa/kc-claude-plugins/issues/587)) ([4064fb5](https://github.com/iamcxa/kc-claude-plugins/commit/4064fb5c42812c79fa9320560f670c4a6c5ae576))


### Bug Fixes

* **kc-dev-flow-2:** an older ADR a change touches says the recommendation was not recorded ([#589](https://github.com/iamcxa/kc-claude-plugins/issues/589)) ([097bfea](https://github.com/iamcxa/kc-claude-plugins/commit/097bfeae9751746a3d101d5530b4411fc4368e14))

## [0.13.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.12.0...kc-dev-flow-2-v0.13.0) (2026-10-09)


### Features

* **kc-dev-flow-2:** save each dispatch's instruction with the task, and validation reads it ([#582](https://github.com/iamcxa/kc-claude-plugins/issues/582)) ([cf62851](https://github.com/iamcxa/kc-claude-plugins/commit/cf62851339043cf3843f081488a71abf3ab403ec))

## [0.12.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.11.0...kc-dev-flow-2-v0.12.0) (2026-10-09)


### Features

* **kc-dev-flow-2:** budget the workflow template's words and refuse repeated passages ([#579](https://github.com/iamcxa/kc-claude-plugins/issues/579)) ([7b84465](https://github.com/iamcxa/kc-claude-plugins/commit/7b84465e4e678d7da6e736d1c81ac75ceab4ea76))

## [0.11.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.10.6...kc-dev-flow-2-v0.11.0) (2026-10-09)


### Features

* **kc-dev-flow-2:** learn lists package-issue candidates, and rulings record the recommendation ([#576](https://github.com/iamcxa/kc-claude-plugins/issues/576)) ([fcc5a41](https://github.com/iamcxa/kc-claude-plugins/commit/fcc5a417bb523b7cb6200c003efd8e5b01cfb374))


### Bug Fixes

* **kc-dev-flow-2:** state commit instructions carry --workflow-dir ([#574](https://github.com/iamcxa/kc-claude-plugins/issues/574)) ([ff26e72](https://github.com/iamcxa/kc-claude-plugins/commit/ff26e7247bb96969e0ea88203142f5575dbb6ab4))

## [0.10.6](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.10.5...kc-dev-flow-2-v0.10.6) (2026-10-09)


### Bug Fixes

* **kc-dev-flow-2:** plural task numbering, package rules in learning coverage, state commits through SD ([#572](https://github.com/iamcxa/kc-claude-plugins/issues/572)) ([e6bc63e](https://github.com/iamcxa/kc-claude-plugins/commit/e6bc63e9f5178050c276e6cc55e6d1239ccbb1f9))

## [0.10.5](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.10.4...kc-dev-flow-2-v0.10.5) (2026-10-09)


### Bug Fixes

* **kc-dev-flow-2:** approval accepts a recommendation only when the gate says so, and a rework is committed ([#568](https://github.com/iamcxa/kc-claude-plugins/issues/568)) ([63ac3db](https://github.com/iamcxa/kc-claude-plugins/commit/63ac3db94c3fed97bb3ef62498097f1ff331bab6))

## [0.10.4](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.10.3...kc-dev-flow-2-v0.10.4) (2026-10-01)


### Bug Fixes

* **kc-dev-flow-2:** a POC task changes no migration file and check enforces it ([#555](https://github.com/iamcxa/kc-claude-plugins/issues/555)) ([a822c3e](https://github.com/iamcxa/kc-claude-plugins/commit/a822c3e31521de37ed04b7798113995dd2f1fc38))

## [0.10.3](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.10.2...kc-dev-flow-2-v0.10.3) (2026-10-01)


### Bug Fixes

* **kc-dev-flow-2:** send a validation-gate revise to implementation ([#553](https://github.com/iamcxa/kc-claude-plugins/issues/553)) ([53bbe40](https://github.com/iamcxa/kc-claude-plugins/commit/53bbe4029dddadf8d122b1856af19f511b0d66c2))

## [0.10.2](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.10.1...kc-dev-flow-2-v0.10.2) (2026-10-01)


### Bug Fixes

* **kc-dev-flow-2:** close five release-review and number-guard workflow gaps ([#549](https://github.com/iamcxa/kc-claude-plugins/issues/549)) ([04557aa](https://github.com/iamcxa/kc-claude-plugins/commit/04557aa6f6e9e7a53e810a42eda9e21f353aed77))

## [0.10.1](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.10.0...kc-dev-flow-2-v0.10.1) (2026-09-30)


### Bug Fixes

* **kc-dev-flow-2:** a repair's validation recheck waits for the repair, and a failed push does not freeze a migration ([#544](https://github.com/iamcxa/kc-claude-plugins/issues/544)) ([893ba0d](https://github.com/iamcxa/kc-claude-plugins/commit/893ba0d89d168d7457f635f247806b1d93863924))

## [0.10.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.9.0...kc-dev-flow-2-v0.10.0) (2026-09-30)


### Features

* **kc-dev-flow-2:** check the ideation seed and acceptance criteria, record Captain amendments, keep ADR drafts unnumbered ([#537](https://github.com/iamcxa/kc-claude-plugins/issues/537)) ([2bd1bfa](https://github.com/iamcxa/kc-claude-plugins/commit/2bd1bfab0b3b72070536a62cbbb788d26d8ce776))
* **kc-dev-flow-2:** refuse edits to applied migrations and reserve migration and ADR numbers per task ([#533](https://github.com/iamcxa/kc-claude-plugins/issues/533)) ([b202457](https://github.com/iamcxa/kc-claude-plugins/commit/b202457454a07eef151b763c92b5e3876aba2192))
* **kc-dev-flow-2:** review a changed release as one journey before its tasks are split ([#540](https://github.com/iamcxa/kc-claude-plugins/issues/540)) ([fffe58e](https://github.com/iamcxa/kc-claude-plugins/commit/fffe58e889d7005cb0775a18ddca6181cb3b5dc1))
* **kc-dev-flow-2:** state the package root, completion recipient and secret wrapper in every dispatch ([#535](https://github.com/iamcxa/kc-claude-plugins/issues/535)) ([d0f91b4](https://github.com/iamcxa/kc-claude-plugins/commit/d0f91b4832d9ec3e25d29b0ef778fdd5472aa203))
* **kc-dev-flow-2:** stop review rounds by rule, dispatch repairs at once, and enforce the added-comment maximum ([#536](https://github.com/iamcxa/kc-claude-plugins/issues/536)) ([05b772b](https://github.com/iamcxa/kc-claude-plugins/commit/05b772b7ffef31553c7fd625dd74fdfe240910d1))

## [0.9.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.8.0...kc-dev-flow-2-v0.9.0) (2026-09-25)


### Features

* **kc-dev-flow-2:** keep review roles on their declared model, measure added comments, and wait for CI test jobs before merge ([#515](https://github.com/iamcxa/kc-claude-plugins/issues/515)) ([2f1ef55](https://github.com/iamcxa/kc-claude-plugins/commit/2f1ef55335a2447d57b2823f2304a0db0bd6b461))

## [0.8.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.7.0...kc-dev-flow-2-v0.8.0) (2026-09-24)


### Features

* **kc-dev-flow-2:** declare POC boundary crossings at the validation gate ([#509](https://github.com/iamcxa/kc-claude-plugins/issues/509)) ([2342a9c](https://github.com/iamcxa/kc-claude-plugins/commit/2342a9c6a2b4f1a7786dfdb6dda1bd52b5e6e8a6))

## [0.7.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.6.0...kc-dev-flow-2-v0.7.0) (2026-09-24)


### Features

* **kc-dev-flow-2:** require design artifacts by change surface at ideation ([#505](https://github.com/iamcxa/kc-claude-plugins/issues/505)) ([81a906c](https://github.com/iamcxa/kc-claude-plugins/commit/81a906cb1fd82568fb224af38c9d82d1097e700b))

## [0.6.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.5.0...kc-dev-flow-2-v0.6.0) (2026-09-23)


### Features

* **kc-dev-flow-2:** default workflow workers to sonnet ([#502](https://github.com/iamcxa/kc-claude-plugins/issues/502)) ([4a33f11](https://github.com/iamcxa/kc-claude-plugins/commit/4a33f1176a8051d7ace8c0d8712596546a5585c3))
* **kc-dev-flow-2:** derive the POC workflow README from the five-stage one and check drift ([#499](https://github.com/iamcxa/kc-claude-plugins/issues/499)) ([9c75b0a](https://github.com/iamcxa/kc-claude-plugins/commit/9c75b0aafe9b530ac038f43e850bc3c775ebb235))
* **kc-dev-flow-2:** require ADR-format decision records and a per-document verdict on affected documents ([#500](https://github.com/iamcxa/kc-claude-plugins/issues/500)) ([32c705d](https://github.com/iamcxa/kc-claude-plugins/commit/32c705d62aca63e9cdbc3979c512a2e31ba57213))


### Bug Fixes

* **kc-dev-flow-2:** name package files in the workflow source instead of linking them ([#501](https://github.com/iamcxa/kc-claude-plugins/issues/501)) ([47b089f](https://github.com/iamcxa/kc-claude-plugins/commit/47b089f49b1a2cc2d0b48040fdb060c52d75d1c7))
* **kc-dev-flow-2:** reconcile a delivery already sent under a lost token without a false stopped attestation ([#497](https://github.com/iamcxa/kc-claude-plugins/issues/497)) ([b64079c](https://github.com/iamcxa/kc-claude-plugins/commit/b64079c020d1663d90a7159843091611d1b2c45f))

## [0.5.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.4.0...kc-dev-flow-2-v0.5.0) (2026-09-23)


### Features

* **kc-dev-flow-2:** check PR head, added comments, screenshots and stash use at delivery ([#496](https://github.com/iamcxa/kc-claude-plugins/issues/496)) ([7e193c4](https://github.com/iamcxa/kc-claude-plugins/commit/7e193c4b44d5aae022de9260b55b88f5ecada650))

## [0.4.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.3.0...kc-dev-flow-2-v0.4.0) (2026-09-23)


### Features

* **kc-dev-flow-2:** add Decision records as an FO responsibility ([#481](https://github.com/iamcxa/kc-claude-plugins/issues/481)) ([e8280d8](https://github.com/iamcxa/kc-claude-plugins/commit/e8280d8ee737beebb050c1ab350211a63d375121))
* **kc-dev-flow-2:** require a Captain-run acceptance script at validation gates ([#480](https://github.com/iamcxa/kc-claude-plugins/issues/480)) ([cc9ab70](https://github.com/iamcxa/kc-claude-plugins/commit/cc9ab70f9a1a5e5aa9726ed12a900a1bf04d35e4))


### Bug Fixes

* **kc-dev-flow-2:** document the stage report form and unblock a lost delivery token ([#477](https://github.com/iamcxa/kc-claude-plugins/issues/477)) ([bcf3c5c](https://github.com/iamcxa/kc-claude-plugins/commit/bcf3c5ce21233bc2ce0d7f4075fbffae28ed1d6f))

## [0.3.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.2.0...kc-dev-flow-2-v0.3.0) (2026-09-17)


### Features

* **kc-dev-flow-2:** require a recorded FO alignment decision before ideation ([#474](https://github.com/iamcxa/kc-claude-plugins/issues/474)) ([5e7d3f8](https://github.com/iamcxa/kc-claude-plugins/commit/5e7d3f87df9919f763b07ffcfae62c1afe19efce))
* **kc-dev-flow-2:** serialize learning evaluation while another job is in flight ([#473](https://github.com/iamcxa/kc-claude-plugins/issues/473)) ([66e226a](https://github.com/iamcxa/kc-claude-plugins/commit/66e226a67a672859afa5c528a4eb078c6814f87c))


### Bug Fixes

* **kc-dev-flow-2:** name the gated-stage dispatch view and the install/adoption routes ([#471](https://github.com/iamcxa/kc-claude-plugins/issues/471)) ([a6b45c7](https://github.com/iamcxa/kc-claude-plugins/commit/a6b45c7e7726c827c81c59e9c8c81c487da56cd3))

## [0.2.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-2-v0.1.0...kc-dev-flow-2-v0.2.0) (2026-09-16)


### Features

* **kc-dev-flow-2:** add experimental flow with Spacedock adoption ([#459](https://github.com/iamcxa/kc-claude-plugins/issues/459)) ([c8342cc](https://github.com/iamcxa/kc-claude-plugins/commit/c8342ccc25a62a2556175ab49719bd5af630b2d0))
* **kc-dev-flow-2:** add local learning evaluation proposals ([#461](https://github.com/iamcxa/kc-claude-plugins/issues/461)) ([e589b37](https://github.com/iamcxa/kc-claude-plugins/commit/e589b3781a40e9b4f549f1efde4c8e2f80831b9c))
* **kc-dev-flow-2:** add manual learning delivery loop ([#462](https://github.com/iamcxa/kc-claude-plugins/issues/462)) ([d24b854](https://github.com/iamcxa/kc-claude-plugins/commit/d24b854cec9dd93e1800e2b2d8d866186b42b268))
