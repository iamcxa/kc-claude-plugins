# Changelog

## [0.2.0](https://github.com/iamcxa/kc-claude-plugins/compare/kc-ship-flow-v0.1.0...kc-ship-flow-v0.2.0) (2026-09-12)


### Features

* **kc-ship-flow:** add plugin skeleton, manifests, and marketplace entry ([#384](https://github.com/iamcxa/kc-claude-plugins/issues/384)) ([2c7f719](https://github.com/iamcxa/kc-claude-plugins/commit/2c7f71927f6721401bf8d0a28e67f95dc747aec5))
* **kc-ship-flow:** ci-covers.sh proves a CI check runs the package before the verdict names it (DEV-149) ([#400](https://github.com/iamcxa/kc-claude-plugins/issues/400)) ([781f962](https://github.com/iamcxa/kc-claude-plugins/commit/781f96241082ab177a55f04cfbe18c6a8dec92cb))
* **kc-ship-flow:** close.py/uat-doc.py read archived, folder-form, and two-root state ([#420](https://github.com/iamcxa/kc-claude-plugins/issues/420)) ([916010b](https://github.com/iamcxa/kc-claude-plugins/commit/916010b37040d210d2e1c15d73d31faa00df88f0))
* **kc-ship-flow:** commission docs/ship as a spacedock batch workflow ([#388](https://github.com/iamcxa/kc-claude-plugins/issues/388)) ([ac60ebe](https://github.com/iamcxa/kc-claude-plugins/commit/ac60ebe462a9177dbfcaa61f29db98444f4a384d))
* **kc-ship-flow:** dispatch one cloud first officer per dev task and watch the set to its validation gates ([#406](https://github.com/iamcxa/kc-claude-plugins/issues/406)) ([0cc25fa](https://github.com/iamcxa/kc-claude-plugins/commit/0cc25fa3ecaba9fc38c0c1a866999250d861b15e))
* **kc-ship-flow:** dispatch station builds its message from a dev entity's stage via spacedock dispatch build (DEV-156) ([#401](https://github.com/iamcxa/kc-claude-plugins/issues/401)) ([bde4b49](https://github.com/iamcxa/kc-claude-plugins/commit/bde4b49a617451a223a3c60967adaac8c0d95ff3))
* **kc-ship-flow:** merge station — verify base and accepted head, ready all, wait clean, merge in order, stop on first refusal ([#391](https://github.com/iamcxa/kc-claude-plugins/issues/391)) ([de64053](https://github.com/iamcxa/kc-claude-plugins/commit/de64053ceb5d508d91ca2441f88502d6aa2ef10c))
* **kc-ship-flow:** POC a standalone batch-station pin loader ([#385](https://github.com/iamcxa/kc-claude-plugins/issues/385)) ([e7faf67](https://github.com/iamcxa/kc-claude-plugins/commit/e7faf6768692aca95ff7538e59d9a114a3880e78))
* **kc-ship-flow:** remove every station that duplicates kc-dev-flow or Spacedock ([#410](https://github.com/iamcxa/kc-claude-plugins/issues/410)) ([96defe1](https://github.com/iamcxa/kc-claude-plugins/commit/96defe1d2a4be5c9edd39db08be2649ad71fd28a))
* **kc-ship-flow:** uat-doc.py reads docs/dev entities, close.py debriefs+closes (v2 receipt) ([#411](https://github.com/iamcxa/kc-claude-plugins/issues/411)) ([c1564b2](https://github.com/iamcxa/kc-claude-plugins/commit/c1564b218799b3baf07fc5e6c346bb6dcc476a7e))


### Bug Fixes

* **kc-ship-flow,plan-flow:** close receipt schema forbids the debrief writers' output; carried issue with no evidence file ([#397](https://github.com/iamcxa/kc-claude-plugins/issues/397)) ([6844755](https://github.com/iamcxa/kc-claude-plugins/commit/68447554384ae047a41bcd5b8e5a483b52698408))
* **kc-ship-flow:** accept station recognises any tracked read path, not a fixed extension list (DEV-134) ([#395](https://github.com/iamcxa/kc-claude-plugins/issues/395)) ([6685103](https://github.com/iamcxa/kc-claude-plugins/commit/668510376e157d1ff9f8fc7781c417c0f6b0d719))
* **kc-ship-flow:** e2e-gate.py takes root and flows dir as arguments, never from __file__ (DEV-153) ([#403](https://github.com/iamcxa/kc-claude-plugins/issues/403)) ([6b408ac](https://github.com/iamcxa/kc-claude-plugins/commit/6b408ac102978d4bbf3614a7109934191520aa9b))
* **kc-ship-flow:** the state branch is what the checkout tracks (DEV-152) ([#399](https://github.com/iamcxa/kc-claude-plugins/issues/399)) ([39cb179](https://github.com/iamcxa/kc-claude-plugins/commit/39cb179be8af4bd71063d51ce7a58e646368e45d))
