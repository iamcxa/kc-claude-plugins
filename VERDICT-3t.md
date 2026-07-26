verdict: return

## Reasoning

This ideation should not advance yet. The core resolver design is coherent and the corpus
evidence is directionally strong, but the proposed semantic distinction is not carried through
all of the user-facing layers it touches.

The main material gap is the `shared: true` contract. The entity defines a general mapping
semantics: any page with `pages.<name>.shared === true` is shared, while `_global` is only a
grandfathered literal default. That is not just a resolver implementation detail; it changes the
meaning of mapping data. The entity proposes updates to `docs/writing-tests.md`,
`agents/e2e-mapper.md`, and `skills/e2e-test/SKILL.md`, but it does not update or even audit
`e2e-pipeline/agents/e2e-test-runner.md`, whose execution instructions still say element
resolution falls back to `pages._global.elements.<element>` and do not mention `shared: true`.
A mapping using a non-`_global` page marked `shared: true` would compile per the new resolver
contract and be documented as valid, but the LLM runner's direct execution path would not carry
that same rule. That is the same failure shape as the previous JSON-diagnostics miss: a
distinction is constructed at one layer and then disappears at a consumer.

There is a second, narrower gap in the new refusal channel. The entity correctly notes that gz
has landed and says the `shared: true` remedy should be carried as a structured repair field
rather than as prose. The current gz contract in `resolver.js` / `e2e-compile --json` carries
`step_id`, `field`, `got`, `candidates`, and `message`; I found no existing `repair` field.
The ACs then explicitly say they assert behavior, not formatting, and AC-4 verifies the prose
message shape. That means implementation could satisfy the ACs while dropping the
machine-actionable remedy into an unstructured message, or could add a new ad hoc field without
an acceptance check that proves JSON consumers receive it. Either outcome leaves the stated
"structured repair" guarantee under-specified.

I do not see evidence that the resolver mechanism itself is over-scoped. The action/expect
unification, omitted-qualifier compatibility, literal `_global` grandfathering, and
`resolve()`/`resolveMultiSite()` symmetry are justified by the existing code paths. The
machine-local corpus limitation is disclosed, and the design requires tracked resolver tests for
the shared fallback and distinct refusal messages. Those parts hold.

## Confidence Per Claim

- High: The workflow requires an independent EM-style verdict; FO approval alone is not
  adjudicative. `docs/dev/README.md` says FO holds "Nothing adjudicative" and EM holds ideation
  verdicts.
- High: `e2e-test-runner.md` is an unaddressed consumer contradiction. Its resolution order
  names explicit page, dialogs, `_global`, and location-less fallback, with no `shared: true`
  handling.
- Medium-high: The structured repair field is under-specified. gz's landed channel is present,
  but the current shape has no `repair` field and the 3t ACs do not require one.
- High: The resolver-side design is otherwise coherent enough to implement once the above
  layer-boundary issues are fixed.

## What Would Change My Mind

- Add `e2e-test-runner.md` to the design/audit/doc-diff scope, or explicitly narrow the entity so
  `shared: true` is a compiler-only contract and the direct `/e2e-test` runner is documented as
  out of scope with a follow-up task. The better fix is to carry the shared-page lookup rule into
  the runner instructions.
- Define the structured diagnostic shape for the page-binding refusals against gz's actual
  contract. If adding a `repair` field is intended, name its exact JSON shape and add an AC that
  verifies `e2e-compile --json` emits it for the wrong-page/shared-remedy case.
- Keep the existing resolver ACs and corpus checks; they are not the reason for return.

## Conditions

No narrow conditions. This is a `return`, not `narrow`, because the missing consumer carry-through
changes whether the design's guarantee reaches users.
