# Changelog

## [1.2.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-journey-map-v1.1.2...kc-journey-map-v1.2.0) (2026-09-24)


### Features

* **kc-journey-map:** report architecture components no journey step reaches ([#511](https://github.com/iamcxa/kc-claude-plugins/issues/511)) ([f4ef7ae](https://github.com/iamcxa/kc-claude-plugins/commit/f4ef7ae1a970c4fb358b5dbd2eaed9e591d4dd13))

## [1.1.2](https://github.com/iamcxa/kc-claude-plugins/compare/kc-journey-map-v1.1.1...kc-journey-map-v1.1.2) (2026-09-24)


### Bug Fixes

* **kc-journey-map:** refuse a render that would overwrite a canvas edit ([#504](https://github.com/iamcxa/kc-claude-plugins/issues/504)) ([6b8b8eb](https://github.com/iamcxa/kc-claude-plugins/commit/6b8b8eb01e6010493887f27be6bd05610bdcfcbb))

## [1.1.1](https://github.com/iamcxa/kc-claude-plugins/compare/kc-journey-map-v1.1.0...kc-journey-map-v1.1.1) (2026-09-23)


### Bug Fixes

* **kc-journey-map:** stack release-board notes by their grown height, and flag long flow, rule and status text ([#503](https://github.com/iamcxa/kc-claude-plugins/issues/503)) ([0bc541e](https://github.com/iamcxa/kc-claude-plugins/commit/0bc541e3d24d740be92c76f333601045292e118c))

## [1.1.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-journey-map-v1.0.0...kc-journey-map-v1.1.0) (2026-09-23)


### Features

* **kc-journey-map:** interrogate a release's stories before handoff, and refuse handoff on open questions ([#493](https://github.com/iamcxa/kc-claude-plugins/issues/493)) ([dd7c3c0](https://github.com/iamcxa/kc-claude-plugins/commit/dd7c3c064ab3ee460b080f5db7b7b2186d6051e3))


### Bug Fixes

* **kc-journey-map:** key readback question and answer notes by story ([#495](https://github.com/iamcxa/kc-claude-plugins/issues/495)) ([cef23ad](https://github.com/iamcxa/kc-claude-plugins/commit/cef23adeea19dca07dacdc1651c831a0e191974b))

## [1.0.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-journey-map-v0.4.1...kc-journey-map-v1.0.0) (2026-09-23)


### ⚠ BREAKING CHANGES

* **kc-journey-map:** draw answered questions, render past five releases and CJK, drop the built-in tunnel ([#490](https://github.com/iamcxa/kc-claude-plugins/issues/490))

### Features

* **kc-journey-map:** add one deferred story to an existing journey ([#482](https://github.com/iamcxa/kc-claude-plugins/issues/482)) ([302e0d6](https://github.com/iamcxa/kc-claude-plugins/commit/302e0d6b19a31ac0863336d47f10d63868123ca2))
* **kc-journey-map:** draw answered questions, render past five releases and CJK, drop the built-in tunnel ([#490](https://github.com/iamcxa/kc-claude-plugins/issues/490)) ([dbe7b6f](https://github.com/iamcxa/kc-claude-plugins/commit/dbe7b6fcd0aa884c01ccc41c6426785e43f5f74d))
* **kc-journey-map:** gate exists on its open questions, and list them ([#488](https://github.com/iamcxa/kc-claude-plugins/issues/488)) ([b8a4e68](https://github.com/iamcxa/kc-claude-plugins/commit/b8a4e68616e556cf751f26003e252c15d7b7409d))
* **kc-journey-map:** release board as a zoomed-in story map, with questions, answers and readback ([#491](https://github.com/iamcxa/kc-claude-plugins/issues/491)) ([54b9a76](https://github.com/iamcxa/kc-claude-plugins/commit/54b9a76b9c2701dff4d6c53319f9a49b826af0d1))

## [0.4.1](https://github.com/iamcxa/kc-claude-plugins/compare/kc-journey-map-v0.4.0...kc-journey-map-v0.4.1) (2026-09-17)


### Bug Fixes

* **kc-journey-map:** correct the popup check's shared-board-origin LIMIT line ([#475](https://github.com/iamcxa/kc-claude-plugins/issues/475)) ([41bfb6c](https://github.com/iamcxa/kc-claude-plugins/commit/41bfb6c0483a1580c23548100fdf0cd5f5bb1a50))

## [0.4.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-journey-map-v0.3.0...kc-journey-map-v0.4.0) (2026-09-16)


### Features

* **kc-journey-map:** add human-led architecture review ([#463](https://github.com/iamcxa/kc-claude-plugins/issues/463)) ([6570fca](https://github.com/iamcxa/kc-claude-plugins/commit/6570fca94936745a225f2e8fa301869746b20ac7))
* **kc-journey-map:** open a linked document chapter in a canvas popup ([#468](https://github.com/iamcxa/kc-claude-plugins/issues/468)) ([ba444ed](https://github.com/iamcxa/kc-claude-plugins/commit/ba444ed9b2afc1b6b353286322c9ea5828fed0d6))
* **kc-journey-map:** store images, share a board ad hoc, save it to the repo ([#466](https://github.com/iamcxa/kc-claude-plugins/issues/466)) ([64ed82b](https://github.com/iamcxa/kc-claude-plugins/commit/64ed82b399949582adb7a861c55ae6ad00cd3e0f))

## [0.3.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-journey-map-v0.2.1...kc-journey-map-v0.3.0) (2026-09-14)


### Features

* **kc-journey-map:** add native Mermaid sequence companions ([#440](https://github.com/iamcxa/kc-claude-plugins/issues/440)) ([3509e5b](https://github.com/iamcxa/kc-claude-plugins/commit/3509e5b0c3f7695a1dfa923096e654c5df41c9de))
* **kc-journey-map:** guard minimal release handoffs ([#449](https://github.com/iamcxa/kc-claude-plugins/issues/449)) ([fe1abba](https://github.com/iamcxa/kc-claude-plugins/commit/fe1abbadb59919ac2668d30531c22682ff0a40fe))


### Bug Fixes

* **kc-journey-map:** make the canvas reachable from another machine ([#442](https://github.com/iamcxa/kc-claude-plugins/issues/442)) ([ed452eb](https://github.com/iamcxa/kc-claude-plugins/commit/ed452eb2209e94524a34d1c0ca351fd60e4b692b))
* **kc-journey-map:** show journey names in canvas tabs ([#436](https://github.com/iamcxa/kc-claude-plugins/issues/436)) ([e3cca91](https://github.com/iamcxa/kc-claude-plugins/commit/e3cca9133bfb139c6cca456b372be0a563d0637d))
* **kc-journey-map:** type lib/records.mjs and run the typecheck in CI ([#441](https://github.com/iamcxa/kc-claude-plugins/issues/441)) ([0bbf623](https://github.com/iamcxa/kc-claude-plugins/commit/0bbf6233831543b8e8874a44a73b4868f6a1ed50))

## [0.2.1](https://github.com/iamcxa/kc-claude-plugins/compare/kc-journey-map-v0.2.0...kc-journey-map-v0.2.1) (2026-09-14)


### Bug Fixes

* **kc-journey-map:** draw a story's question under its own card, not beside it ([#431](https://github.com/iamcxa/kc-claude-plugins/issues/431)) ([e082613](https://github.com/iamcxa/kc-claude-plugins/commit/e082613202acbd579e9d8aa10f5d453221d29fee))
* **kc-journey-map:** measure the one-journey banner instead of assuming 70px ([#434](https://github.com/iamcxa/kc-claude-plugins/issues/434)) ([6c899f2](https://github.com/iamcxa/kc-claude-plugins/commit/6c899f2cccf28d3460fc5bb6d3c5416738d9eb8f))

## [0.2.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-journey-map-v0.1.0...kc-journey-map-v0.2.0) (2026-09-12)


### Features

* **kc-journey-map:** add editable native planning canvas ([#415](https://github.com/iamcxa/kc-claude-plugins/issues/415)) ([97a2680](https://github.com/iamcxa/kc-claude-plugins/commit/97a2680dbf0925921fc16fcab3858035d2cfcefe))
* **kc-journey-map:** add release evidence details and status borders ([#416](https://github.com/iamcxa/kc-claude-plugins/issues/416)) ([86921bd](https://github.com/iamcxa/kc-claude-plugins/commit/86921bd1d68eb5bb481effe6e82ca199c0bb80ac))
* **kc-journey-map:** derive optional local task progress ([#417](https://github.com/iamcxa/kc-claude-plugins/issues/417)) ([3fd2fc5](https://github.com/iamcxa/kc-claude-plugins/commit/3fd2fc596d93b8eae4e6d688a4cbb473fb4d4a17))
* **kc-journey-map:** prepare selected releases for development ([#419](https://github.com/iamcxa/kc-claude-plugins/issues/419)) ([0ec3380](https://github.com/iamcxa/kc-claude-plugins/commit/0ec3380f590cbaf5b01ee1c325eb222da99a3c5a))
