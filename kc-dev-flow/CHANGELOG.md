# Changelog

## [4.0.2](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-v4.0.1...kc-dev-flow-v4.0.2) (2026-09-02)


### Bug Fixes

* **kc-dev-flow:** align standalone admission contracts ([#329](https://github.com/iamcxa/kc-claude-plugins/issues/329)) ([36a3642](https://github.com/iamcxa/kc-claude-plugins/commit/36a36426c43143ee60158ffba1fa7ec1401b244e))
* **kc-dev-flow:** align standalone migration guidance ([#319](https://github.com/iamcxa/kc-claude-plugins/issues/319)) ([9d4e499](https://github.com/iamcxa/kc-claude-plugins/commit/9d4e499ac5ac66d668131d378be41d487f89d446))
* **kc-dev-flow:** derive installed version in release tests ([#330](https://github.com/iamcxa/kc-claude-plugins/issues/330)) ([69247af](https://github.com/iamcxa/kc-claude-plugins/commit/69247afb8610b03e650d77aea542d230d1544d48))

## [4.0.1](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-v4.0.0...kc-dev-flow-v4.0.1) (2026-08-31)


### Bug Fixes

* **kc-dev-flow:** bind release receipt to final tree ([#316](https://github.com/iamcxa/kc-claude-plugins/issues/316)) ([2234e3e](https://github.com/iamcxa/kc-claude-plugins/commit/2234e3e47cd8a1ba7ec5353194738d17551302b5))

## [4.0.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-v3.0.0...kc-dev-flow-v4.0.0) (2026-08-31)


### ⚠ BREAKING CHANGES

* **kc-dev-flow:** remove setup-github-project-projection and its runtime.
* **kc-dev-flow:** Active v2 POCs must finish on the pinned 3.x package/vendor pair or be Captain re-recorded with the v3 POC fields before the 4.x cutover.
* **kc-dev-flow:** adopters must remove the retired release state and provide sprint plus sprint-readiness ready before a route first enters work.

### Features

* **kc-dev-flow:** add exact-SHA PR review handoff ([#293](https://github.com/iamcxa/kc-claude-plugins/issues/293)) ([f7a3f01](https://github.com/iamcxa/kc-claude-plugins/commit/f7a3f018e9756c44b354c3a24326594b084b044b))
* **kc-dev-flow:** add Hermes portable package ([#259](https://github.com/iamcxa/kc-claude-plugins/issues/259)) ([cd2a917](https://github.com/iamcxa/kc-claude-plugins/commit/cd2a9179fe4a4574ad6014fe6a4b369a4f0201ba))
* **kc-dev-flow:** add manual cycle-release admission ([#306](https://github.com/iamcxa/kc-claude-plugins/issues/306)) ([7256e02](https://github.com/iamcxa/kc-claude-plugins/commit/7256e02dbbc5340e4328bfeeb016448e4033fde5))
* **kc-dev-flow:** add workspace-bound Linear admission ([#307](https://github.com/iamcxa/kc-claude-plugins/issues/307)) ([6bcdea3](https://github.com/iamcxa/kc-claude-plugins/commit/6bcdea3eca985a42aeceea45534c91584fee490a))
* **kc-dev-flow:** bound POC decision-ready path ([#308](https://github.com/iamcxa/kc-claude-plugins/issues/308)) ([b8a070e](https://github.com/iamcxa/kc-claude-plugins/commit/b8a070e48860ae1cfa7ae14c99f1e743b2b40083))
* **kc-dev-flow:** give backlog an exit bar and shape a journey statement ([#267](https://github.com/iamcxa/kc-claude-plugins/issues/267)) ([a15ab03](https://github.com/iamcxa/kc-claude-plugins/commit/a15ab033a52d2cc6740543132d3c224dcbe30e9f))
* **kc-dev-flow:** let a declared size threshold stop work and hand back ([#272](https://github.com/iamcxa/kc-claude-plugins/issues/272)) ([ef808a9](https://github.com/iamcxa/kc-claude-plugins/commit/ef808a91059146f0c59c033c06fb4ae5dfb1bed9))
* **kc-dev-flow:** make Production recovery proportional ([31207d6](https://github.com/iamcxa/kc-claude-plugins/commit/31207d6ff45a5c0ddecd5b2f9f7d3dfd6961be0f))
* **kc-dev-flow:** make profile routing release-safe and schedule backlog entry ([#283](https://github.com/iamcxa/kc-claude-plugins/issues/283)) ([a2035c2](https://github.com/iamcxa/kc-claude-plugins/commit/a2035c2c99d273d255076ba35b30df5300742712))
* **kc-dev-flow:** make scaffolding and guards carry a removal condition ([#271](https://github.com/iamcxa/kc-claude-plugins/issues/271)) ([cc095b0](https://github.com/iamcxa/kc-claude-plugins/commit/cc095b063f42be603358e0d72628a3e694b451ec))
* **kc-dev-flow:** make shape name where the work touches ([#269](https://github.com/iamcxa/kc-claude-plugins/issues/269)) ([f0af07f](https://github.com/iamcxa/kc-claude-plugins/commit/f0af07f0c8c72ddc322cff93af1160192bdc04ff))
* **kc-dev-flow:** read the declared receipt field from conditional-reference blocks ([#262](https://github.com/iamcxa/kc-claude-plugins/issues/262)) ([b8ff74e](https://github.com/iamcxa/kc-claude-plugins/commit/b8ff74ec0f7abad244075553631aa414a76cd533))
* **kc-dev-flow:** route bounded POCs through one workflow ([#291](https://github.com/iamcxa/kc-claude-plugins/issues/291)) ([844edfa](https://github.com/iamcxa/kc-claude-plugins/commit/844edfa75a021cc6c013186bb88fba81f598f912))


### Bug Fixes

* **kc-dev-flow:** bind provider delivery linkage ([#309](https://github.com/iamcxa/kc-claude-plugins/issues/309)) ([36d7ec1](https://github.com/iamcxa/kc-claude-plugins/commit/36d7ec1a84e3b22917484a92cf06e5056483b1e8))
* **kc-dev-flow:** compare the route smoke's verdict the way Spacedock reads it ([#268](https://github.com/iamcxa/kc-claude-plugins/issues/268)) ([8cd6caa](https://github.com/iamcxa/kc-claude-plugins/commit/8cd6caa604de4d73ece3e8c15e1a31e72e050daf))
* **kc-dev-flow:** demote Production's release from a graph state to a terminal-approval boundary ([#276](https://github.com/iamcxa/kc-claude-plugins/issues/276)) ([8ddd794](https://github.com/iamcxa/kc-claude-plugins/commit/8ddd794d271b24c91d2bf4a9fa329ff533939485))
* **kc-dev-flow:** enforce engage reconcile deltas ([#303](https://github.com/iamcxa/kc-claude-plugins/issues/303)) ([d8092fa](https://github.com/iamcxa/kc-claude-plugins/commit/d8092fa93eec70a0d5c64d663e6c156983a785cf))
* **kc-dev-flow:** keep the adoption check from vendoring a test, and trim the README ([#257](https://github.com/iamcxa/kc-claude-plugins/issues/257)) ([54957ee](https://github.com/iamcxa/kc-claude-plugins/commit/54957ee66ab0eabfbb22406b5da48d9351002a47))
* **kc-dev-flow:** price retained comments by necessity ([#282](https://github.com/iamcxa/kc-claude-plugins/issues/282)) ([57e116a](https://github.com/iamcxa/kc-claude-plugins/commit/57e116aa48faeb0a41a5c2ab6a43cef22a9d8612))
* **kc-dev-flow:** restore four verification-discipline clauses dropped by the 3.0 rewrite ([#279](https://github.com/iamcxa/kc-claude-plugins/issues/279)) ([eb057c7](https://github.com/iamcxa/kc-claude-plugins/commit/eb057c780269114ef5fde09381e41229daf7563f))
* **kc-dev-flow:** stop the FO's verdict boundary reading as a licence to relay ([#277](https://github.com/iamcxa/kc-claude-plugins/issues/277)) ([9fee712](https://github.com/iamcxa/kc-claude-plugins/commit/9fee712cbb0a6a5657d3c6727cc9093c6af54548))


### Code Refactoring

* **kc-dev-flow:** make planning providers replaceable ([#300](https://github.com/iamcxa/kc-claude-plugins/issues/300)) ([19e1a72](https://github.com/iamcxa/kc-claude-plugins/commit/19e1a7271230b179feb8e65382a1f39d013bc922))

## [3.0.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-v2.5.0...kc-dev-flow-v3.0.0) (2026-08-19)


### ⚠ BREAKING CHANGES

* **kc-dev-flow:** add profile-native delivery routes ([#249](https://github.com/iamcxa/kc-claude-plugins/issues/249))

### Features

* **kc-dev-flow:** add profile-native delivery routes ([#249](https://github.com/iamcxa/kc-claude-plugins/issues/249)) ([e634d3e](https://github.com/iamcxa/kc-claude-plugins/commit/e634d3e71270d04d72893782e0ecb2482be772c0))
* **kc-dev-flow:** default to a stacked base and absorb the PR ceremony ([#255](https://github.com/iamcxa/kc-claude-plugins/issues/255)) ([1d13e18](https://github.com/iamcxa/kc-claude-plugins/commit/1d13e189f82d4c085f69475186b08d01c6deaad0))
* **kc-dev-flow:** make projected issues readable and identity-safe ([#240](https://github.com/iamcxa/kc-claude-plugins/issues/240)) ([54594f1](https://github.com/iamcxa/kc-claude-plugins/commit/54594f1871a1a693528f8bdbbe132010ea4fb6db))
* **kc-dev-flow:** project SD tasks as GitHub Project drafts ([f187ddb](https://github.com/iamcxa/kc-claude-plugins/commit/f187ddbdf3442b883512dc1d37c05442edf28e08))

## [2.5.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-v2.4.0...kc-dev-flow-v2.5.0) (2026-08-14)


### Features

* **kc-dev-flow:** add GitHub Project projection installer ([#227](https://github.com/iamcxa/kc-claude-plugins/issues/227)) ([f9895e5](https://github.com/iamcxa/kc-claude-plugins/commit/f9895e5ee925b1cb20e82c1e7f494212ca0ff9d7))
* **kc-dev-flow:** add proportional RoboRev implementation exit ([#239](https://github.com/iamcxa/kc-claude-plugins/issues/239)) ([387be48](https://github.com/iamcxa/kc-claude-plugins/commit/387be484ae353ebe4603720cc7cc3f8c633d25a1))


### Bug Fixes

* **kc-dev-flow:** gate delivery on GitHub PR feedback ([#220](https://github.com/iamcxa/kc-claude-plugins/issues/220)) ([951618f](https://github.com/iamcxa/kc-claude-plugins/commit/951618fbc81f9dae46a22014d109904a54eda6b2))

## [2.4.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-v2.3.0...kc-dev-flow-v2.4.0) (2026-08-13)


### Features

* **kc-dev-flow:** carve along the journey, not by layer ([#207](https://github.com/iamcxa/kc-claude-plugins/issues/207)) ([f572b01](https://github.com/iamcxa/kc-claude-plugins/commit/f572b013ceb994596a29b348a1afa74b530e461f))
* **kc-dev-flow:** route product work before harvesting ([#218](https://github.com/iamcxa/kc-claude-plugins/issues/218)) ([3e28d4a](https://github.com/iamcxa/kc-claude-plugins/commit/3e28d4a7c3e32fa53c44f21eb78bafaa5b91fa9b))


### Bug Fixes

* **kc-dev-flow:** align policy activation and retire change-shape ([#212](https://github.com/iamcxa/kc-claude-plugins/issues/212)) ([a18ba78](https://github.com/iamcxa/kc-claude-plugins/commit/a18ba78f72c03036d8463629bd19977aa684e159))
* **kc-dev-flow:** normalize inherited seed criteria ([#206](https://github.com/iamcxa/kc-claude-plugins/issues/206)) ([c41cbbb](https://github.com/iamcxa/kc-claude-plugins/commit/c41cbbbf60efa841379fc59216f3e75921174557))

## [2.3.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-v2.2.0...kc-dev-flow-v2.3.0) (2026-08-11)


### Features

* **kc-dev-flow:** add change-shape observation ([53e3232](https://github.com/iamcxa/kc-claude-plugins/commit/53e3232d61d689d34a6c493495c791fe0d0f85b4))


### Bug Fixes

* **kc-dev-flow:** validate runtime compatibility before release ([1db7e77](https://github.com/iamcxa/kc-claude-plugins/commit/1db7e7729595b090715943da544a0f8327912c05))

## [2.2.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-v2.1.0...kc-dev-flow-v2.2.0) (2026-08-11)


### Features

* **kc-dev-flow:** streamline reviews and prove minimal surfaces ([7e8fa5e](https://github.com/iamcxa/kc-claude-plugins/commit/7e8fa5e89e94c951c4d4f0c90a5476bdbd324175))

## [2.1.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-v2.0.0...kc-dev-flow-v2.1.0) (2026-08-10)


### Features

* **kc-dev-flow:** size outcomes before acceptance expands ([#197](https://github.com/iamcxa/kc-claude-plugins/issues/197)) ([2bb412e](https://github.com/iamcxa/kc-claude-plugins/commit/2bb412ea48e36a6be272ba36fc521ea3a0a7b0d0))

## [2.0.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-v1.4.0...kc-dev-flow-v2.0.0) (2026-08-10)


### ⚠ BREAKING CHANGES

* **kc-dev-flow:** adopters re-vendor. A repository using only the five-tier ladder keeps working, but plan review gains a rejection it did not have.
* **kc-dev-flow:** adopters who vendored this file re-vendor and re-declare. The stage list is unchanged for anyone using Part 2 only; the adoption section now asks them to record that Part 1 is not adopted, so the omission reads as a choice.

### Features

* **kc-dev-flow:** add what a retained document may contain, as an adoptable half ([#185](https://github.com/iamcxa/kc-claude-plugins/issues/185)) ([4963a5b](https://github.com/iamcxa/kc-claude-plugins/commit/4963a5b1cab1dbc8093628a9be6795e7ec9851ce))
* **kc-dev-flow:** classify a layer's need separately from its completeness ([#193](https://github.com/iamcxa/kc-claude-plugins/issues/193)) ([e871313](https://github.com/iamcxa/kc-claude-plugins/commit/e871313418e35f01240aea5d1d1c4f349e80b4b8))


### Bug Fixes

* **kc-dev-flow:** make document policies independently selectable ([#192](https://github.com/iamcxa/kc-claude-plugins/issues/192)) ([cc8139e](https://github.com/iamcxa/kc-claude-plugins/commit/cc8139e3b1065fceb842da41d10a7b21112fd4c2))

## [1.4.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-v1.3.0...kc-dev-flow-v1.4.0) (2026-08-09)


### Features

* **kc-dev-flow:** strengthen evidence intake and judgment ([97e3d25](https://github.com/iamcxa/kc-claude-plugins/commit/97e3d2597999c104821958494141fe14f5445abf)), closes [#170](https://github.com/iamcxa/kc-claude-plugins/issues/170) [#171](https://github.com/iamcxa/kc-claude-plugins/issues/171)

## [1.3.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-v1.2.0...kc-dev-flow-v1.3.0) (2026-08-07)


### Features

* **kc-dev-flow:** distribute policy through vendored mods ([#167](https://github.com/iamcxa/kc-claude-plugins/issues/167)) ([2e086b3](https://github.com/iamcxa/kc-claude-plugins/commit/2e086b387713dbfd12db38285fc452953f7dadd5))
* **kc-dev-flow:** give the absolutes rule an enforcement point of its own ([#164](https://github.com/iamcxa/kc-claude-plugins/issues/164)) ([f633bb9](https://github.com/iamcxa/kc-claude-plugins/commit/f633bb9ce889f25203f87230a8cc0275512941d3))
* **kc-dev-flow:** give the stopping decision an owner, and take the hazard off the path ([#159](https://github.com/iamcxa/kc-claude-plugins/issues/159)) ([04ffece](https://github.com/iamcxa/kc-claude-plugins/commit/04ffece5133286b9f1e601452647bd4a0e89ac4e))

## [1.2.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-v1.1.0...kc-dev-flow-v1.2.0) (2026-08-04)


### Features

* **kc-dev-flow:** bind the instrument, not only the claim ([#156](https://github.com/iamcxa/kc-claude-plugins/issues/156)) ([f228f76](https://github.com/iamcxa/kc-claude-plugins/commit/f228f76f67a3f9705047246c8a4dfb2c8644ddd8))

## [1.1.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-dev-flow-v1.0.0...kc-dev-flow-v1.1.0) (2026-08-04)


### Features

* **kc-dev-flow:** bound how long evidence may be sharpened before integration ([#151](https://github.com/iamcxa/kc-claude-plugins/issues/151)) ([590487d](https://github.com/iamcxa/kc-claude-plugins/commit/590487dcc17a52f4160c8493f05cd097b5d32327))
* **kc-dev-flow:** make a kernel binding resolvable, and its staleness detectable ([#147](https://github.com/iamcxa/kc-claude-plugins/issues/147)) ([ce5d484](https://github.com/iamcxa/kc-claude-plugins/commit/ce5d484b2b395b0a619840c7e65863cd611333e1))
* **kc-dev-flow:** require a verifying round to state its binding and its falsifier ([#146](https://github.com/iamcxa/kc-claude-plugins/issues/146)) ([6e09631](https://github.com/iamcxa/kc-claude-plugins/commit/6e0963141127dc348d315dc23d16c8d7a62cad90))

## 1.0.0 (2026-08-01)


### Features

* **kc-dev-flow:** add portable sprint workflow kernel ([#127](https://github.com/iamcxa/kc-claude-plugins/issues/127)) ([25c6666](https://github.com/iamcxa/kc-claude-plugins/commit/25c6666d968dece3da6521ae370e5f1647f4079d))
