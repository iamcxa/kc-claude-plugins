# Bounded paired native-client check

Use the existing [protected stdio helper](agent-pairing.md) with two separately
approved installations. Pairing remains default off outside fresh synthetic
validation. This recipe changes neither room/record permissions nor concurrency.
A native run and final canvas appearance alone are not acceptance evidence.

Requires Node22.13+, macOS Swift/unlocked user Keychain, Claude Code2.1.303 and
Codex CLI0.162.1. Verify installed help and the version-matched official
[Codex schema](https://raw.githubusercontent.com/openai/codex/rust-v0.162.1/codex-rs/core/config.schema.json)
before model calls. The launcher refuses another client version; reverify rather
than upgrade, fall back, change the model catalog or bypass permissions.

## Independent installations

Choose a fresh owned0700 test root and two different0700 protected-store roots.
Start the existing private Node host with fresh storage, a verified synthetic
operator and two fresh registered rooms. No existing A/B/qnow-day2 room or deployed
credential is a target. Keep existing native model login stores and HOME/CODEX_HOME.
Do not copy, inspect or print their credentials or add persistent native MCP config.
The local owner-login socket and signed-in browser remain the legitimate human
entry; the operator inspects and approves each request in **帳號與代理**.

Create two nonsecret JSON files using exactly the six fields in agent-pairing.md.
Choose distinct installationId values and self-reported labels. C requests only
fresh room A; D requests fresh A and B. Use the exact canonical **API** origin and
immutable backendId: the development Vite/browser origin can differ. Endpoint,
backend or store mismatch must not reuse credentials. No implicit alias discovery,
credential forwarding or HTTP redirect follow-up is permitted. Unadmitted LAN HTTP
and aliases remain refused; hosted HTTPS/alias/provider proof is separate.

```sh
node scripts/agent-helper.mjs begin /absolute/test/C.json /absolute/test/store-C
# In the verified browser inspect C's exact backend, original room and capabilities; approve.
node scripts/agent-helper.mjs finish /absolute/test/C.json /absolute/test/store-C
node scripts/agent-helper.mjs begin /absolute/test/D.json /absolute/test/store-D
# Independently inspect/approve D for fresh A and B, then redeem with its original helper.
node scripts/agent-helper.mjs finish /absolute/test/D.json /absolute/test/store-D
```

Record separate family IDs and actual current scopes without retaining secrets or
digests. Consent includes complete-record read/add/change/delete/whole replacement,
assets and actual configured save/repository scopes. The three-tool test allowlist
does not narrow the human's broader grant. Node scopes reflect the configured save
directory/repository allowlist; Cloudflare has no save/repository capability. Check
actual unsupported/denied outcomes rather than inferring them from the UI.

## Finite native invocation

Each invocation launches the same agent-helper.mjs mcp with the installation JSON
and exact protected-store root. Generated config contains only paths/IDs, never a
bearer/token environment option. The launcher passes a small environment retaining
existing login locations, uses a fresh neutral cwd and sets per-run isolation. Codex
uses fixed gpt-6.1-sol/high, no daemon, ignores user config and uses read-only sandbox.
Claude account/model selection remains its existing native default. No global
settings, model catalog or native executable changes are made. The launcher keeps
the built-in provider configuration unchanged; application/tool replay is disabled,
but undocumented native internal transport retries are not controlled or proven.
The per-run suppress_unstable_features_warning flag hides development-feature
startup warnings while retaining skip_host_skill_discovery. Native error/unknown
events still stop the observer; no global warning or permission setting changes.

Prepare an exact prompt file and a **new nonexistent** receipt directory per phase.
Use absolute installed executable paths; run from this package:

```sh
node scripts/private-native-client.mjs claude /absolute/test/C.json /absolute/test/store-C /absolute/test/C-write.txt /absolute/test/C-write-receipts /absolute/path/to/claude
node scripts/private-native-client.mjs codex /absolute/test/D.json /absolute/test/store-D /absolute/test/D-write.txt /absolute/test/D-write-receipts /absolute/path/to/codex
```

Inspect result.json, stdout.jsonl and stderr.txt privately. The native allowlist is
get_doc/patch_doc/health; put_doc remains ungranted for this test. Additional native
built-ins can remain advertised, including model-dependent wrappers. This is
observation-based acceptance, not proof that those tools were removed or could not
execute. The launcher stops on an observed other tool/unrecognized native item,
error, unknown result, more than eight observed calls or180-second timeout, without
relaunch/replay. It preserves raw events and the stop reason. A protocol requiring
a non-journey wrapper is a failed bounded run; do not silently count only its inner
calls. Metadata or mere advertisement is not an executed call. Observer termination
cannot retrospectively prevent an operation already started by the native runtime.

## Exact sequential acceptance

Generate complete standard note JSON with note() in lib/records.mjs, using the actual
fresh page IDs, random nonce/text, distinct shape IDs and positions. Give that JSON
to the model. patch_doc arguments are `{room:A,body:{put:[completeRecord],remove:[]}}`:
use singular put. Require put=1/removed=0 plus exact immutable readback; misspelled
puts, zero counts, advancing clock, process exit or model summary alone do not pass.
Preserve every baseline record and retain separate family admission receipts.

1. Browser opens fresh A. Native C reads A, writes complete C and reads A back.
2. Native D reads C in A, adds complete D and reads A. Browser receives both.
3. A fresh C process with the same C installation reads exact C+D. Native D reads B,
   adds complete B and reads B; A hash stays unchanged and B has no C/D records.
4. Native C attempts B read and B write once each in separately bounded prompts.
   Require typed denial and unchanged A/B hashes, with no private B content. An
   expected-denial invocation may exit unsuccessfully; preserve it without replay.
5. In A use a real browser pointer/keyboard to create a human note. Native D reads
   exact C+D+human text; browser/backend agree. Inspect desktop/390px light/dark,
   hit testing, focus return and below-fold scroll in affected integration states.
6. End owned native processes; revoke only the two synthetic families and prove new
   requests denied. Confirm authenticated helper revoke before forget removes exact
   owned Keychain items. Unknown revoke stays paused; do not delete protected repair
   material or retry unknown storage/renewal outcomes. Never enumerate other items.

Retain native actual tool arguments/results, version/candidate, family/admission
mapping, before/after record hashes and browser readback. Receipt room=null alone
is not mutation authorship. Full-record sequential sentinels make no conflict-free
simultaneous-write claim. Actual paired human/model steps can exceed five minutes;
unit tests or scripted HTTP cannot replace them. Detailed identity/usage remains
local; publish only sanitized conclusions. Remote Node/Cloudflare TLS/Access,
Free-plan fit, physical devices and established-stream stop require separate proof.

Run launcher regressions with `node --test scripts/private-native-client.test.mjs`.
Existing agent installation/protected-store and host-contract checks remain separate
from native-client/browser acceptance; no CI trigger, dependency or deployment change
is introduced by this recipe.

The [pairing guide](agent-pairing.md) owns canonical endpoint derivation, consent
binding and recovery for stale in-flight requests. Verify that exact API endpoint
separately from the human-entry origin before approving each installation.
