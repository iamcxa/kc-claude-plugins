# Changelog

## [1.11.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-pr-flow-v1.10.0...kc-pr-flow-v1.11.0) (2026-07-30)


### Features

* **kc-pr-flow:** give a prose cut a failure signal ([7bdb8c4](https://github.com/iamcxa/kc-claude-plugins/commit/7bdb8c4158dd83eac13f23f29a391b71be337d6e))

## [1.10.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-pr-flow-v1.9.1...kc-pr-flow-v1.10.0) (2026-07-30)


### Features

* **kc-pr-flow:** add agent-native shadow review receipts ([#48](https://github.com/iamcxa/kc-claude-plugins/issues/48)) ([536be3e](https://github.com/iamcxa/kc-claude-plugins/commit/536be3e7d7d8371a9e84b693804407ea1b54bc60))
* **kc-pr-flow:** add safe resume and once-only review posting ([#56](https://github.com/iamcxa/kc-claude-plugins/issues/56)) ([927c5bd](https://github.com/iamcxa/kc-claude-plugins/commit/927c5bd7d19ed4563e883416a05b742aafc731cc))
* **kc-pr-flow:** add typed interactive review lifecycle ([a0f50f4](https://github.com/iamcxa/kc-claude-plugins/commit/a0f50f435823cc1a3b60ac001ad6e98d7ea104fe))
* **kc-pr-flow:** give the daemon its own posting authorization and once-only protection ([#59](https://github.com/iamcxa/kc-claude-plugins/issues/59)) ([2afa2f9](https://github.com/iamcxa/kc-claude-plugins/commit/2afa2f9ad4d33b03b33c016396d4e03da8495b8b))


### Bug Fixes

* **kc-pr-flow:** combine paginated reviews and preserve failures ([7093423](https://github.com/iamcxa/kc-claude-plugins/commit/709342340443dff7f17eb2ac6b178232ce9388a9))
* **kc-pr-flow:** fail closed on malformed review lists ([56b4a7e](https://github.com/iamcxa/kc-claude-plugins/commit/56b4a7e00583f8147d462c87980938cf9b5945a1))
* **kc-pr-flow:** make post fail closed on an unusable reconcile read ([#63](https://github.com/iamcxa/kc-claude-plugins/issues/63)) ([d3cb1e1](https://github.com/iamcxa/kc-claude-plugins/commit/d3cb1e1b7ab90d8ddf7efb60f3c856c29998ffb5))
* **kc-pr-flow:** resolve split-root audit links ([097685a](https://github.com/iamcxa/kc-claude-plugins/commit/097685af1a41b5485eaf469bbcc206b5205c569a))
* **kc-pr-flow:** resolve the verdict state file to one name per branch ([#78](https://github.com/iamcxa/kc-claude-plugins/issues/78)) ([b87171c](https://github.com/iamcxa/kc-claude-plugins/commit/b87171c40d595c7c60d4efa3ee16d0b4249cd9d1))
* **kc-pr-flow:** run the Gemini arbiter on agy, not the retired gemini CLI ([#58](https://github.com/iamcxa/kc-claude-plugins/issues/58)) ([7521546](https://github.com/iamcxa/kc-claude-plugins/commit/7521546b98c5cf36048813b7228d1ca58b70c4e8))


### Performance Improvements

* **kc-pr-flow:** cut the python3 spawn count in the once-only post path ([#67](https://github.com/iamcxa/kc-claude-plugins/issues/67)) ([f7dd1a0](https://github.com/iamcxa/kc-claude-plugins/commit/f7dd1a0023e6271f1d5e46ca999b9b1497817802))
* **kc-pr-flow:** remove redundant review rules ([85959dc](https://github.com/iamcxa/kc-claude-plugins/commit/85959dce110834f67d6d0e5193991a7c4b315696))

## [1.9.1](https://github.com/iamcxa/kc-claude-plugins/compare/kc-pr-flow-v1.9.0...kc-pr-flow-v1.9.1) (2026-07-14)


### Bug Fixes

* **marketplace:** repair release version propagation ([#45](https://github.com/iamcxa/kc-claude-plugins/issues/45)) ([4f8b44c](https://github.com/iamcxa/kc-claude-plugins/commit/4f8b44cfe3df0fde7f2b4ab3f1414561e149e427))

## [1.9.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-pr-flow-v1.8.0...kc-pr-flow-v1.9.0) (2026-07-14)


### Features

* **kc-pr-flow:** add optional review architecture diagrams ([#44](https://github.com/iamcxa/kc-claude-plugins/issues/44)) ([9dea537](https://github.com/iamcxa/kc-claude-plugins/commit/9dea537fae7e258cf1c5b3ac0efc72a4f0c37da6))
