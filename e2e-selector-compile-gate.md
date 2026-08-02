---
title: "Make the compiler refuse the selector grammar the linter bans — one policy, one gate"
status: done
source: GitHub #88, sprint e2e-pipeline/S1 item 2; re-shaped after PR #123 retired two of the five ban classes
product: e2e-pipeline
sprint: S1
started: 2026-08-01
completed: 2026-08-01T13:57:23Z
verdict: PASSED
worktree:
issue: "88"
pr: pr-merge:128:artifact-v1:69eb970a5b58f3579e5f5b1767ec9ab1d717af9dd6cd9d418de889ddc03a5fe7
design: required
lane: main
id: pjjs91zrbrcm2we467a3vvp4
pr_artifact_v1: eyJhdWRpdF9saW5rIjoiW3BqXSgvaWFtY3hhL2tjLWNsYXVkZS1wbHVnaW5zL2Jsb2IvYWY2ZTllOWQxZGVlZWMwMjU5MTFkODFjMWQxMzk3ZmVjMDE1NzhlOS9lMmUtc2VsZWN0b3ItY29tcGlsZS1nYXRlLm1kKSIsImJhc2UiOiJtYWluIiwiYmFzZV9vaWQiOiIxMTE5Mzg3YjE1M2MxNjYxNWE0NTAzZjAwOTBmOGUyZmU2MGM5MDI4IiwiYm9keSI6IkNsb3NlcyAjODguXG5cbiMjIFdoYXQgd2FzIGJyb2tlblxuXG5gc2NyaXB0cy9saW50LW1hcHBpbmcuc2hgIGlzIHRoZSBwbHVnaW4ncyBzZWxlY3Rvci1ncmFtbWFyIGF1dGhvcml0eSBhbmQgKipub3RoaW5nIG9uIHRoZVxuY29tcGlsZWQgcGF0aCBpbnZva2VkIGl0KiouIEluc2lkZSB0aGUgcGx1Z2luIG9ubHkgYHRlc3QvaW50ZWdyYXRpb24tc21va2Uuc2hgIGNhbGxlZCBpdDtcbml0IGhhZCBubyByZWZlcmVuY2UgaW4gYSBjb25zdW1pbmcgcmVwbydzIGAuZ2l0aHViYCBvciBgLmdpdGhvb2tzYC4gU28gdGhlIGJhbiB3YXNcbmVuZm9yY2VkIGJ5IHJlc3RhdGluZyBpdCBpbiBmb3VydGVlbiBtYXJrZG93biBmaWxlcyBhbmQgYnkgbm90aGluZyB0aGF0IGNvdWxkIHJlZnVzZSDigJQgYVxubWFwcGluZyBjYXJyeWluZyBgPj4gbnRoPWAsIGA6aGFzLXRleHQoYCwgb3IgYSBgZmluZCByb2xlIOKApmAgc3ViY29tbWFuZCBjaGFpbiBjb21waWxlZFxuZ3JlZW4sIGRyeS1yYW4gZ3JlZW4sIGFuZCBmYWlsZWQgb25seSBvbmNlIGEgYnJvd3NlciB3YXMgYWxyZWFkeSBydW5uaW5nLlxuXG5UaGUgaXNzdWUncyAqZmlsZWQqIHByZW1pc2UgaXMgcmV0aXJlZDogUFIgIzEyMyBkZWxldGVkIGxpbnQgQ0xBU1MgMSAoYHJvbGU9WFtuYW1lPeKApl1gKVxuYW5kIENMQVNTIDMgKGJhcmUgYHRleHQ9YCkgb24gdGhlIGNhcHRhaW4ncyAyMDI2LTA3LTI1IHJ1bGluZy4gVGhyZWUgY2xhc3NlcyBzdXJ2aXZlIGFuZFxuYXJlIHdoYXQgdGhpcyBnYXRlcy4gVGhlaXIgcmV0aXJlbWVudCBub3cgaGFzIGV4cGxpY2l0IG5lZ2F0aXZlIHRlc3RzLCBiZWNhdXNlIHJlLWFkZGluZ1xuZWl0aGVyIGlzIHRoZSBzcGVjaWZpYyByZWdyZXNzaW9uIHRoYXQgd291bGQgdW5kbyAjMTIzLlxuXG4jIyBTaGFwZVxuXG5PbmUgdGFibGUgaW4gYGNvbXBpbGVyL2xpYi9zZWxlY3Rvci1wb2xpY3kuanNgLCB0d28gY29uc3VtZXJzOlxuXG4tIGBzY3JpcHRzL2xpbnQtbWFwcGluZy5zaGAgZXhlY3MgaXQgYW5kIGNhcnJpZXMgbm8gcGF0dGVybnMgb2YgaXRzIG93bi4gRXhpdCBjb2RlcyBhbmRcbiAgc3RkZXJyIGFyZSB1bmNoYW5nZWQg4oCUIHZlcmlmaWVkICoqYnl0ZS1pZGVudGljYWwqKiBhZ2FpbnN0IHRoZSBwcmV2aW91cyBpbXBsZW1lbnRhdGlvblxuICBvbiBib3RoIHNoaXBwZWQgZml4dHVyZXMuXG4tIFRoZSBjb21waWxlciBjYWxscyBpdCBiZXR3ZWVuIGByZXNvbHZlKClgIGFuZCBgZ2VuZXJhdGUoKWAuXG5cblNldmVyaXR5IGlzIGEgZnVuY3Rpb24gb2Ygc2NvcGUgKGNhcHRhaW4gcnVsaW5nLCAyMDI2LTA4LTAxKTpcblxufCBzZXZlcml0eSB8IHNjb3BlIHwgZWZmZWN0IHxcbnwtLS18LS0tfC0tLXxcbnwgKipibG9ja2luZyoqIHwgYSBiYW5uZWQgc2VsZWN0b3Igb24gYW4gZWxlbWVudCAqKnRoaXMgZmxvdyByZXNvbHZlcyoqIHwgZXhpdCAxLCBubyBgLnNoYCB3cml0dGVuLCBkaWFnbm9zdGljIG5hbWVzIG1hcHBpbmcgZmlsZSwgYHBhZ2UuZWxlbWVudGAsIGNsYXNzLCBzZWxlY3RvciwgcmVwbGFjZW1lbnQgfFxufCB3YXJuaW5nIHwgZXZlcnkgb3RoZXIgYmFubmVkIHNlbGVjdG9yIGluIHRoZSBsb2FkZWQgbWFwcGluZyBmaWxlIHwgYHBhdGg6bGluZXM6Y2xhc3NgIG9uIHN0ZGVyciwgY29tcGlsZSBwcm9jZWVkcyB8XG5cbldob2xlLWZpbGUgYmxvY2tpbmcgd2FzIHRoZSBhbHRlcm5hdGl2ZSBhbmQgd2FzICoqbWVhc3VyZWQqKiwgbm90IGFyZ3VlZDogMzkgZmluZGluZ3NcbmFjcm9zcyAyIG9mIDUgcmVhbCBjb3JwdXMgbWFwcGluZ3MsIHZlcnN1cyAzIGZpbmRpbmdzIGluIDIgb2YgNDcgZmxvd3MgYXQgcmVzb2x2ZWQgc2NvcGUuXG5XaG9sZS1maWxlIHJlZHMgZXZlcnkgZmxvdyB0aGF0IG1lcmVseSBsb2FkcyBhIG1hcHBpbmcgY2FycnlpbmcgdW5yZWxhdGVkIGxlZ2FjeSBkZWJ0LFxud2hpY2ggdGhlIGlzc3VlJ3Mgb3duIGFjY2VwdGFuY2UgaWRlYXMgYXNrIG5vdCB0byByZXF1aXJlLlxuXG4jIyBEZWx0YSBtb2RlXG5cblByZS1leGlzdGluZyB2aW9sYXRpb25zIGdvIGluIGEgYmFzZWxpbmUgdGhlIGNvbXBpbGVyICoqcmVhZHMgYW5kIG5ldmVyIHdyaXRlcyoqXG4oYC0tc2VsZWN0b3ItYmFzZWxpbmVgKS4gUmVjb3JkcyBhcmUga2V5ZWQgYnkgKiplbGVtZW50IGlkZW50aXR5KiosIHNvIHJlZm9ybWF0dGluZyBkb2VzXG5ub3QgY2h1cm4gdGhlbSwgd2hpbGUgcGFzdGluZyBhIGJhc2VsaW5lZCBzZWxlY3RvciBvbnRvIGEgZGlmZmVyZW50IGVsZW1lbnQsIGNoYW5naW5nIGFcbmJhc2VsaW5lZCBlbGVtZW50J3Mgc2VsZWN0b3IsIGFuZCByZW5hbWluZyBhbiBlbGVtZW50IGFsbCBzdGlsbCBibG9jay4gQSBiYXNlbGluZWQgZWxlbWVudFxudGhlIGZsb3cgYWN0dWFsbHkgcmVzb2x2ZXMgcHJpbnRzIGEgZGlzdGluY3QgYFJFU09MVkVTIGEgZ3JhbmRmYXRoZXJlZCBiYW5uZWQgc2VsZWN0b3JgXG5saW5lLCBzbyBuZXdseSBkZXBlbmRpbmcgb24ga25vd24gZGVidCBpcyBsb3VkIHdpdGhvdXQgYmVpbmcgZmF0YWwuXG5cblRoZSBwcm9kdWNlciBpcyBhIHNlcGFyYXRlIGJpbmFyeSDigJQgYGJpbi9lMmUtc2VsZWN0b3ItYmFzZWxpbmUuanNgIOKAlCB0aGF0IGdhdGVzIG5vdGhpbmdcbmFuZCBwcmludHMgdG8gc3Rkb3V0LiBTZXBhcmF0ZSBvbiBwdXJwb3NlOiB0aGUgZ2F0ZSB0aGVuIGhhcyBubyBjb2RlIHBhdGggdGhhdCByZWdlbmVyYXRlc1xuaXRzIG93biBiYXNlbGluZS4gU3RhdGVkIHBsYWlubHksIHN0ZG91dC1vbmx5IGRvZXMgKipub3QqKiBlbmZvcmNlIGh1bWFuIGF1dGhvcnNoaXAgKGFuXG5hZ2VudCBjYW4gcmVkaXJlY3QgYSBzdHJlYW0gYXMgZWFzaWx5IGFzIGEgcGVyc29uIGNhbik7IHdoYXQgaXQgYnV5cyBpcyB0aGF0IHdpZGVuaW5nIGFcbmJhc2VsaW5lIGxhbmRzIGluIGEgcmV2aWV3YWJsZSBkaWZmLlxuXG4jIyBFdmlkZW5jZVxuXG4qKkRpZmZlcmVudGlhbCBvbiB0aGUgcmVhbCBjb25zdW1lciBjb3JwdXMqKiDigJQgc2FtZSBmbG93IGFuZCBtYXBwaW5nIGJ5dGVzLCBib3RoIHJ1bnNcbnRocm91Z2ggdGhlIHJlYWwgQ0xJOlxuXG58IHwgYG9yaWdpbi9tYWluYCB8IHRoaXMgYnJhbmNoIHxcbnwtLS18LS0tfC0tLXxcbnwgZXhpdCB8IDAgfCAqKjEqKiB8XG58IGFydGlmYWN0IHwgYGdhdGUtc21va2UtYWxsLXBhZ2VzLnNoYCB3cml0dGVuIHwgKipub25lKiogfFxuXG5BbiBpbXBsZW1lbnRhdGlvbiB0aGF0IGRvZXMgbm90IGFjdHVhbGx5IGJsb2NrIHByb2R1Y2VzIHR3byBpZGVudGljYWwgcnVucywgd2hpY2ggaXMgd2hhdFxubWFrZXMgdGhpcyBhYmxlIHRvIGZhaWwuIFRoZSBvYnNlcnZhYmxlIGlzIHRoZSBleGl0IGNvZGUgYW5kIHRoZSBhcnRpZmFjdCdzIGV4aXN0ZW5jZSwgbm90XG50aGUgYXJ0aWZhY3QncyBjb250ZW50czogYGdyZXAgLWMgJ250aD0nIGdhdGUtc21va2UtYWxsLXBhZ2VzLnNoYCDihpIgYDBgLCBiZWNhdXNlXG5gc2VsZWN0b3ItdHJhbnNsYXRlLmpzYCBzdHJpcHMgdGhlIGNob3JkIGR1cmluZyB0cmFuc2xhdGlvbi4gVGhhdCB3aWRlbmluZyBpcyAjMTI0LCBub3RcbnRoaXMuXG5cbioqQWR2ZXJzYXJpYWwgc3BvdC1jaGVja3MqKiDigJQgdGhyZWUgY2xhaW0tYnJlYWtpbmcgZWRpdHMsIGVhY2ggY29uZmlybWVkIHJlZCB0aGVuIHJlc3RvcmVkOlxuXG58IGVkaXQgfCByZXN1bHQgfFxufC0tLXwtLS18XG58IG5ldXRyYWxpc2UgdGhlIGJsb2NraW5nIHJldHVybiBpbiBgY29tcGlsZXIuanNgIHwgNiBvZiAxMiBnYXRlIHRlc3RzIHJlZCB8XG58IGBpc0dyYW5kZmF0aGVyZWRgIHJldHVybnMgdHJ1ZSB1bmNvbmRpdGlvbmFsbHkgfCAxMSByZWQgYWNyb3NzIHBvbGljeSArIGdhdGUgfFxufCByZS1hZGQgYSBwcml2YXRlIGBoYXMtdGV4dGAgcmVnZXggdG8gYGxpbnQtbWFwcGluZy5zaGAgfCBkcmlmdCB0ZXN0IHJlZCB8XG5cblRoZSB0aGlyZCAqKmluaXRpYWxseSBzdGF5ZWQgZ3JlZW4qKiBhbmQgdGhhdCB3YXMgYSBiYWQgcHJvYmUsIG5vdCBhIHBhc3NpbmcgdGVzdDogdW5kZXJcbmBzZXQgLWV1byBwaXBlZmFpbGAgdGhlIGluamVjdGVkIGxpbmUgc2F0IGFmdGVyIGEgYG5vZGVgIGNhbGwgdGhhdCBleGl0cyAyLCBzbyBpdCBuZXZlclxucmFuLiBSZS1ydW4gd2l0aCB0aGUgcHJvYmUgcHJvdmVuIGFjdGl2ZSBmaXJzdCwgaXQgZ29lcyByZWQgYXMgZGVzaWduZWQuXG5cbioqU3VpdGUqKiDigJQgOTM0IHRlc3RzLCAxIHNraXBwZWQgKG9wdC1pbiBicm93c2VyIHRlc3QpLiBPbmUgZmFpbHVyZSBpbiB0aGUgZnVsbCBydW46XG5gbmV2ZXItZXhpdGluZyB0cmFjZSBzdG9wIGlzIGJvdW5kZWTigKZgLCB3aGljaCBpcyB0aGUga25vd24gbG9hZC1mbGFreSB0ZXN0IHRyYWNrZWQgYnlcbiMxMjIuIElzb2xhdGVkOiA0OS80OSB0d2ljZSBvbiB0aGlzIGJyYW5jaCBhbmQgNDkvNDkgb24gY2xlYW4gYG1haW5gOyB0aGUgZGlmZiB0b3VjaGVzXG5uZWl0aGVyIHRoYXQgdGVzdCBub3IgYHNjcmlwdHMvZmluYWxpemUtdHJhY2Uuc2hgLiBJdCBmYWlsZWQgb25seSBpbiBhIHJ1biB3aGVyZSB0d28gZnVsbFxuc3VpdGVzIHdlcmUgZXhlY3V0aW5nIGNvbmN1cnJlbnRseSDigJQgY29uZGl0aW9ucyBJIHdhcyBwZXJ0dXJiaW5nIG15c2VsZi5cblxuKipDb3JwdXMgbnVtYmVycyByZXByb2R1Y2UqKiB3aXRoIHRoZSBuZXcgbGludGVyOiAzOSBmaW5kaW5ncywgMiBvZiA1IG1hcHBpbmcgZmlsZXMg4oCUXG5pZGVudGljYWwgdG8gdGhlIHByZS1jaGFuZ2UgaW1wbGVtZW50YXRpb24uXG5cbiMjIEtub3duIHJlc2lkdWFsXG5cbmBlMmUtdGVzdC1ydW5uZXJgLCBgZTJlLWZsb3ctdmVyaWZpZXJgLCBhbmQgdGhlIHdhbGt0aHJvdWdoIHBhdGggYXJlIExMTS1kcml2ZW4sIHJlYWRcbm1hcHBpbmdzIGRpcmVjdGx5LCBhbmQgbmV2ZXIgcmVhY2ggdGhlIGNvbXBpbGVyLiBUaGlzIFBSIGRvZXMgbm90IGNsb3NlIHRoZSBzcHJpbnQncyBleGl0XG5jb25kaXRpb24gb24gaXRzIG93biDigJQgZmlsZWQgYXMgIzEyNiB3aXRoIGEgYmFja2xvZyBlbnRpdHkuXG5cbkRldi1mbG93IGVudGl0eTogYGUyZS1zZWxlY3Rvci1jb21waWxlLWdhdGVgLlxuXG5bcGpdKC9pYW1jeGEva2MtY2xhdWRlLXBsdWdpbnMvYmxvYi9hZjZlOWU5ZDFkZWVlYzAyNTkxMWQ4MWMxZDEzOTdmZWMwMTU3OGU5L2UyZS1zZWxlY3Rvci1jb21waWxlLWdhdGUubWQpIiwiYm9keV9zaGEyNTYiOiI2OWUwZDM5YmZlOWRjMzM3MTI0ZDYwOWZmNmEzYjMxOWRmYzdmOWNlNzhkOTc3OWIzMDg0N2ZlNDliODcwY2IwIiwiZGlmZl9zaGEyNTYiOiI1YzY3MGQ3ZDYzYmU0OTdiNTg2YzU1NjljOTM3YzA5ZGQ5NzZlNzMzYWRmNTQzNmMzNGRkNDU1ZjI2MDAxMWI5IiwiaGVhZCI6ImlhbWN4YS9lMmUtc2VsZWN0b3ItY29tcGlsZS1nYXRlIiwiaGVhZF9vaWQiOiI2NGM3Mjc4NTBiZTA2NDc3NWI5OWZmNjgyZTQ0NjM2YTdhMzdmMTA3IiwibGl2ZV9wYXRoIjoiZTJlLXNlbGVjdG9yLWNvbXBpbGUtZ2F0ZS5tZCIsInJlcG8iOiJpYW1jeGEva2MtY2xhdWRlLXBsdWdpbnMiLCJ0aXRsZSI6ImZlYXQoZTJlLXBpcGVsaW5lKTogZW5mb3JjZSB0aGUgc2VsZWN0b3IgZ3JhbW1hciBhdCBjb21waWxlIHRpbWUgKCM4OCkifQ
mod-block:
---

## Problem

`scripts/lint-mapping.sh` is the plugin's selector-grammar authority and **nothing on
the compiled path invokes it**. Proven by two independent strategies, both over the
tracked tree at `origin/main` (`1119387`):

- `git grep -n -I -- 'lint-mapping'` — every hit outside the script itself is prose
  (CLAUDE.md, agents/*.md, docs/*.md, references/*.md) or `test/integration-smoke.sh`.
  No `.github/workflows/` hit, no `bin/`, no `compiler/` hit.
- `git grep -n 'selector-translate' -- e2e-pipeline` — the compiler's only selector
  code path is the *translator*, which converts forms; it never refuses one.

So the ban is enforced by restating it in fourteen markdown files and by nothing that
can say no. A mapping carrying `>> nth=`, `:has-text(`, or a `find role …` subcommand
chain compiles green, dry-runs green, and fails only after browser startup — which is
exactly the expensive-late-detection the issue was filed for.

The premise the issue was *originally* written against is retired: PR #123 (`7108495`)
deleted lint CLASS 1 (`role=X[name=…]`) and CLASS 3 (bare `text=`) on the captain's
2026-07-25 ruling. Three classes survive and are what this entity gates:

| class | pattern | why it still breaks |
|---|---|---|
| CLASS 2 | `>> nth=N` | Playwright chord; on the `click`/`fill` path the raw value goes to `agent-browser` and does not resolve |
| CLASS 4 | `:has-text(` | broken in agent-browser, no equivalent, times out |
| CLASS 5 | `find role\|text\|label\|testid …` as a `selector:` value | a CLI subcommand chain, not selector grammar |

## Scope (captain / EM authored, not inferred)

Scope for this entity is not composed here. It is the EM `proceed` determination
recorded on issue #88 (2026-08-01,
[#88 comment](https://github.com/iamcxa/kc-claude-plugins/issues/88#issuecomment-5145878666)),
which the captain explicitly delegated ("D2 EM 已裁 proceed，不用你管"). Its five
conditions are carried into the ACs below verbatim in substance:

1. One shared policy module, not two implementations plus parity tests.
2. Hard-fail at compile/dry-run, **plus** the scoped/delta mode `docs/dev/ROADMAP.md`
   already writes into this sprint item ("including a scoped legacy migration path").
3. The baseline must not be regenerable by the thing it gates.
4. CLASS 3 enforcement must not return — it is retired, not deferred.
5. At least one AC is E2E-first: a fixture carrying each surviving banned class exits
   **before browser startup**, observed on the real CLI rather than a unit test
   asserting a validator returned false.

**Baseline file location — one decision taken rather than re-escalated.** The delta
baseline records real grandfathered violations, and the only real corpus lives in a
private consumer repo. Presented to the captain last session with a recommendation; the
reply was to proceed. Taken: **the baseline file lives in the consumer repo**
(`.claude/e2e/selector-baseline.tsv` by default, `--selector-baseline` to override); the
plugin defines the format and ships **synthetic** fixtures only. No consumer app's
violation inventory enters this public marketplace repo.

**Gate granularity — captain ruled, 2026-08-01: option B, "two severities".** Blocking on
the flow-resolved scope, non-blocking warnings on the whole mapping file. Asked because
the EM routed it there and because it decides how obstructive the gate is on the captain's
own repo; the ruling is recorded verbatim in the next section, which the ACs are written
against.

## Gate granularity — measured, and the alternative named on record

The ideation clause requires the simplest alternative be named and refused (Proof Policy
rule 4). The alternative to gating **every** `selector:` value in a loaded mapping is
gating **only the selectors a flow actually resolves**. It matters because whole-file
granularity is what forces the baseline contract into existence at all.

Measured against the real consumer corpus at `/Users/kent/Project/carlove/.claude/e2e`
(47 flows, 5 mappings), by running this plugin's own `parser.js` + `resolver.js` over
every flow and classifying every `selector` value in the resolved output
(`/tmp/measure-resolved-scope.js`, reproducible):

| scope | banned findings | unique records | blast radius on day one |
|---|---|---|---|
| mapping-file | **39** | 36 | 2 of 5 mappings — which reds *every* flow that loads them |
| flow-resolved | **≥3** | 3 | 2 of 47 flows, and only 1 of those is differential-capable (AC-5) |

The resolved number is a **floor, not an exact count**: 43 of the corpus's 47 flows already
carry pre-existing parse or resolve errors (`vehicle-brand-select.yaml` alone has 32), so
element references that never resolve were never classified. Those errors are corpus rot
that predates this entity; the floor is still the right decision input, because it can
only move up and the mapping-file number is fixed at 39.

Independently corroborating: the 4 compiled artifacts in that repo contain **zero**
`>> nth=` tokens, because `compiler/lib/selector-translate.js:93-95` silently strips the
chord on the visibility path. So the class survives by being invisible, and the flows it
actually reaches are few.

**Captain ruled 2026-08-01 — option B, two severities, one policy table.** The choice was
put to the captain in consequence terms rather than mechanism terms: option A taxes every
future edit to a mapping with an unrelated backlog of 39 findings; option B keeps the door
narrow and lets rot sit longer, but visibly. The ruling was B, with the explicit condition
that the other findings still print every run. What it selects:

- **Blocking — flow-resolved scope.** A banned selector on an element the flow resolves
  fails compile and dry-run. This is the defect the issue reports.
- **Warning — mapping-file scope.** Every other banned selector in a loaded mapping is
  printed with `path:line:class` on stderr, non-blocking. Latent rot stays visible
  instead of silently accumulating.
- The baseline is **consulted** only for blocking findings, but it is **produced** by
  walking the mapping file, so adopting one covers all 36 banned elements rather than
  only the ~3 a flow reaches today. That asymmetry is deliberate and its cost is named in
  the design section: a future flow that starts resolving a grandfathered element compiles
  green, and prints a distinct resolved-grandfathered line every run.

Refusal of the pure alternatives, on record: pure file-scope contradicts the issue's own
acceptance idea ("without requiring an unrelated whole-file migration") and multiplies
the migration by 12×; pure resolved-scope with no warning channel loses the visibility of
the other 36 findings entirely, which is the only reason file-scope was attractive.

## Appetite

**Estimate: 7 hours** implementation (one dispatch), plus validation. Revised twice: 3h at
first draft, 4h after the EM priced the flag threading, and 7h after the EM walked the
diff surface the option-B ruling actually implies — a five-export module, a bash→Node
wrapper that must preserve three exit codes and the `path:line: class:` stderr shape,
**resolution provenance threaded through `resolver.js` including the multi-site branch**,
a post-resolve two-severity gate, a separate baseline producer, three test files plus a
scratch-plugin drift harness, a cross-repo differential run, and four doc surfaces.

**Tolerance: +40% (10 hours).**

**The re-cut is pre-authorized at the seam, not at the clock.** If resolution provenance
(the `resolver.js` change below) is not landing within the first third of the dispatch,
the worker **drops the baseline and ships the blocking gate alone**, files the baseline as
its own entity, and reports the cut — without a round trip. That seam is the load-bearing
one: everything else is local, and a worker who discovers mid-dispatch that the identity
it needs does not exist will otherwise either re-derive the design or quietly ship
file-scope blocking, which is the thing the captain overruled.

## Fastest path / smallest cut, and which one is taken

- **Fastest path**: have the compiler shell out to `scripts/lint-mapping.sh` per mapping
  file. One process boundary, zero new policy code.
- **Smallest cut**: hard-fail only, no delta mode.
- **Simplest alternative to the whole baseline contract**: gate only resolved selectors —
  named, measured, and partially adopted above rather than refused.
- **Taken**: the policy moves **into** a Node module (`compiler/lib/selector-policy.js`)
  and `lint-mapping.sh` becomes a thin wrapper that execs it, preserving its exit codes
  and stderr shape. Shelling out to bash was refused because it makes the policy
  unavailable to the `--json` structured-error channel, puts a bash dependency on the Node
  compiler, and leaves the bash regexes as the sole implementation — a second consumer
  would still have to reimplement them to get structured findings.
- Delta mode is **not** cut: ROADMAP:169 scopes it into this sprint item, and even at the
  narrower resolved granularity the corpus still needs 3 grandfathered records, so
  hard-fail alone still reds a real repo on day one.

## Design determination — `design: required`

This decides a contract, not just behavior: a new CLI flag, a new on-disk file format
that consuming repos will commit, and a new module boundary two consumers read.

**Module.** `compiler/lib/selector-policy.js`, **core-Node only** — the linter must stay
wireable into a consumer `.githooks` without `npm install`, and that is a test line
(AC-2), not a comment. Exports:
- `BANNED_CLASSES` — the policy table: `{id, label, pattern, guidance}` per class.
- `classifySelector(value)` → class id or `null`. The one function every traversal calls
  to decide whether a string is banned.
- `scanMappingText(text, filePath)` → findings with **line numbers**, no YAML structure
  required. Consumed by `lint-mapping.sh` and by the file-scope warning channel.
- `scanElements(elements)` → findings over `{mappingFile, page, element, selector}`
  records. Consumed by the blocking gate and by the baseline producer.
- `parseBaseline(text)` / `isGrandfathered(finding, baseline)`.

**Two traversals, one policy.** The text scan and the element scan are different code,
because line numbers and element identity are different facts and neither traversal
produces the other's. What is shared is the *decision*: both call `classifySelector`. The
claim this entity makes is the bounded one — "one banned-class table, two traversals" —
and the enforcement point for it is AC-2's drift test, which proves the bash consumer's
verdicts track the table. There is no mechanism that would stop someone adding a second
table tomorrow, so this entity does not claim there is one.

**Where the two severities are wired — this is what the captain's ruling changed.**
Both live in `compiler/compiler.js`; `parser.js` is not touched, because parse time
structurally cannot see the blocking set (`compiler.js:52-64` returns on parse errors
*before* `resolve()` runs, and `validateMapping()` at `parser.js:388-400` sees only
`version` and `pages`).

| severity | scope | wiring point | effect |
|---|---|---|---|
| warning | every `selector:` in each loaded mapping file | after `parse()` succeeds, over the raw mapping bytes | `path:line:class` on stderr; never enters `errors` |
| **blocking** | selectors the flow actually resolves | after `resolve()` succeeds, **before** `generate()` and before the output write | returns `{success:false, errors, errorDetails}`; no `.sh` written |

**Resolution provenance — the load-bearing change, and it is not in the compiler.**
`resolver.js` currently discards the identity the blocking gate and the baseline key both
need: `resolveElement()` returns `{ selector: entry.selector }` and
`elementResultFromEntry()` returns `{selector, cssSelector}` — element name, page, and
mapping file all die there, even though `buildSymbolTable` already holds `page` on the
entry (`resolver.js:61`). Threading `{page, element}` out of those two functions, and
`mappingFile` in from `compiler.js` (which already computes `mappingPaths`), is the seam
the appetite's pre-authorized re-cut is anchored on. The cross-site branch
(`resolveMultiSite`) resolves against a different mapping per site; the baseline key uses
the mapping file's **basename**, which is already unique per site, so no site field is
added.

**Baseline format.** One record per line, tab-separated:

```
<mapping-file-basename>\t<page>.<element>\t<class-id>\t<selector-value>
```

`#` comments and blank lines allowed; matching is exact on all four fields. Keyed by
**element identity**, not line number and not count. A line number churns on every
unrelated edit above it; a count passes the same-count swap (delete one occurrence, paste
onto a different element). Element identity refuses both, and refuses a *changed selector*
on a known element. It does not survive an element **rename** — a rename reads as a new
element and blocks, which is the safe direction and is stated here so it is not discovered
as a surprise. Measured relevance: the corpus contains `role=switch >> nth=1` three times
and `.ant-modal role=button[name="holder"] >> nth=0` twice, so a `(file, class, selector)`
key would have granted those two strings a permanent licence in files `e2e-mapper` authors
by pattern repetition.

**What the baseline grandfathers, stated precisely, because the two-severity split makes
it ambiguous.** The producer walks the mapping file, so a baseline covers **every**
banned element in it (36 records for the corpus), not just the ~3 currently reached by a
flow. That is deliberate: a banned selector on an element that already exists is exactly
the pre-existing debt the captain's ruling says must not tax unrelated work. What it costs
is that a *future* flow which starts resolving one of those elements compiles green.
Mitigation, and it is the reason this is acceptable rather than a hole: a grandfathered
finding that is **actually resolved by the flow** prints its own distinct stderr line every
run ("resolved a grandfathered banned selector"), separate from the file-scope warnings —
so newly depending on known-broken debt is loud, even though it is not fatal. What still
blocks: a new element, a changed selector on a known element, or a rename.

**No regeneration by the gate.** The compile path contains **no write call** to the
baseline path — that is the enforcement point, and AC-4 tests it by byte-comparison.
The producer is a **separate binary that does no gating**, `bin/e2e-selector-baseline.js
<mapping.yaml>`, which walks the YAML and prints records to **stdout** with no
output-path argument. It is separate on purpose: an earlier draft put `--format=baseline`
on `lint-mapping.sh`, which is line-oriented and YAML-structure-blind
(`scripts/lint-mapping.sh:135-158` matches raw lines with no page/element context) and
therefore cannot emit an element-keyed record at all. To be explicit about what stdout-only
does and does not buy: an agent can redirect stdout in an inner loop exactly as easily as a
person can, so it does not enforce human authorship. What it buys is that adopting or
widening a baseline lands as a reviewable diff rather than as a side effect of a gate run.

## Reverse-recovery audit (against `origin/main` `1119387`, fetched 2026-08-01)

| layer | verdict | evidence |
|---|---|---|
| Policy definition | **WORKING** | `scripts/lint-mapping.sh:135-158` — three surviving classes, post-#123 |
| Policy as a reusable unit | **EXISTS_BROKEN** | it exists only as inline bash regexes inside the CLI script; no module, no export. Re-run over the corpus: 2 files exit 2, 39 findings, all `>>nth` — the regexes run, they are just not reusable |
| Compiler invocation of policy | **MISSING** | two-strategy grep above; `compiler/parser.js:388-401 validateMapping()` validates `version` and `pages` only |
| Resolution provenance | **EXISTS_BROKEN** | `resolver.js:61` builds symbol-table entries carrying `page`, then `resolveElement()` (`:213`) returns `{selector}` and `elementResultFromEntry()` (`:226`) returns `{selector, cssSelector}` — element name, page, and mapping file are all discarded before the resolved output. The blocking gate and the baseline key both need them. This is the seam the pre-authorized re-cut is anchored on |
| Chord handling in the compiler | **EXISTS_BROKEN** | `compiler/lib/selector-translate.js:93-95` silently strips `>> nth=N` on the visibility path, which is why CLASS 2 has been survivable and invisible — and why the compiled artifacts show zero chords. Narrowing that behavior is #124, not this entity |
| Diagnostics channel | **WORKING** | `compiler/compiler.js:54-64` already surfaces parse errors as `errorDetails` for `--json` |
| Delta / baseline mode | **MISSING** | `git grep -e selector-baseline -e selector-policy` — zero hits |
| Test fixtures for banned forms | **WORKING** | `test/fixtures/legacy-playwright-mapping.yaml` (must exit 2), `test/fixtures/native-css-mapping.yaml` (must exit 0) |

Single broken seam → repair scoped to that seam. The policy is not rebuilt; it is
**extracted** from the bash script and then wired to a second consumer.

**Enforcement facts read live**, not from `.github/`: required contexts come from
`gh api repos/iamcxa/kc-claude-plugins/branches/main/protection` at implementation time.
No job is renamed by this task.

## Spike

**No spike needed, restated against the post-resolve mechanism** — the first draft's
waiver cited `parser.js` returning blocking errors before `resolve()`, which proves the
wrong thing now that blocking happens *after* `resolve()`. The mechanisms this design
actually relies on:

- **Blocking between resolve and codegen.** `compiler.js:114-156` already returns
  `{success:false, errors, errorDetails}` from the post-resolve branch on
  `resolveResult.errors`, and `generate()` plus the output write are strictly downstream
  (`:195-208`). Adding one more source of blocking errors at that point uses an existing
  return path, not a new one.
- **A shared `compiler/lib/` module with two consumers** — `selector-translate.js` is
  exactly that shape today.
- **The banned-class regexes** are the ones running in `lint-mapping.sh` now, with
  fixtures pinning both directions.
- **Resolved-scope classification** was not spiked but **measured** end to end, by running
  the real `parser.js` + `resolver.js` over all 47 corpus flows (table above).

The one mechanism that is neither proven nor measured is **threading provenance through
`resolver.js`**. It is not spiked because it is not risky-unknown, it is
tedious-and-wide — and that is precisely why the appetite's re-cut is anchored on it
rather than on the clock.

## Pre-mortem

If this ships exactly per spec and still fails, the most likely cause is
**criteria that pass without delivering value**: the gate fires at compile, so a repo
whose findings are fully grandfathered gets a green compile forever, while the actual
generator of violations — `e2e-mapper` — keeps emitting them and nothing tells it.
Mitigation inside this scope: grandfathered findings and file-scope findings both print
on stderr every run, so a growing baseline is visible rather than absorbed. Closing the
generator side is #124's and the mapper's business.

**A second failure mode the EM found and this entity now owns naming:** the sprint's exit
condition is "invalid selectors fail before browser startup", and the *compiled* path is
not the only path to a browser. `e2e-test-runner`, `e2e-flow-verifier`, and the
walkthrough path are LLM-driven and read the mapping directly. This entity does not reach
them, and no existing entity owns them — #124 is the chord-narrowing question and #91 is
multi-match semantics. A backlog entity is filed for the runner-path remainder as part of
this stage rather than left as a bare out-of-scope line; **#88 alone does not close the
sprint exit condition**, and saying so here is the point.

## Acceptance criteria

**AC-1 — A banned class on an element the flow resolves fails compile and dry-run**

The compiled artifact is not written, and the failure names mapping path, line, page and
element, banned class, and replacement guidance. The same banned class on an element the
flow does **not** resolve does not block.
Verified by, against one fixture mapping carrying a banned selector on two elements where
the flow references only the first: `node bin/e2e-compile.js <flow> --mappings-dir
<fixture-dir>` exits 1 naming the referenced element, with no `.sh` in the output dir;
`--dry-run` behaves the same; the `--json` document carries the class id in `errors[]`;
and the unreferenced element appears on stderr as a `path:line:class` warning in that
same run — one command proving both severities. RED evidence recorded first.
Falsifier: delete the blocking call from `compiler.js` between `resolve()` and
`generate()` and the exit-1 case goes green while the warning line survives, which
distinguishes this from a total wiring failure.

**AC-2 — The bash linter's verdicts are produced by the shared table, not its own copy**

Changing `BANNED_CLASSES` changes what `scripts/lint-mapping.sh` reports.
Verified by: a drift test that runs the linter against a fixture, then re-runs it against
a scratch copy of the plugin whose `BANNED_CLASSES` has one class removed, and asserts the
linter's findings changed accordingly — proving the bash consumer reads the module rather
than a private pattern.
Falsifier: reintroduce an inline regex for that class in `lint-mapping.sh` and the second
run still reports it, so the test goes red.
Bounded claim recorded in the docs: "one banned-class table, two traversals" — not "one
implementation" and not "no second table can exist", neither of which has an enforcement
point.

**AC-3 — A baseline grandfathers existing findings without hiding new ones**

An otherwise-blocking mapping compiles when every blocking finding is listed in the
baseline; a newly introduced violation still fails, and the failure names only the new
finding.
Verified by: the fixture carries the same banned selector on two elements, one the flow
resolves and one it does not — so under the ruled resolved-scope granularity there is
**1 blocking finding and 1 warning**, not 2 blocking (corrected here after validation
caught this text still describing the pre-ruling file-scope shape). With the blocking one
listed in the baseline → exit 0, and its *resolved* grandfathered line printed distinctly
from the file-scope warning; then, each as its own case → (a) a violating selector on a
new element → exit 1 naming only it; (b) re-point an existing baselined selector string
onto a second element → exit 1, proving the record is keyed by element identity, not by
`(file, class, selector)`; (c) change the selector on a baselined element to a different
banned form → exit 1, proving the record pins the value too.
Falsifier: make `isGrandfathered` return true unconditionally and all three negative cases
go green.

**AC-4 — The gate cannot regenerate its own baseline**

No compile-path invocation writes the baseline file, and the CLI exposes no flag that does.
Verified by: byte-compare the baseline file before and after a compile run over a
violating mapping; `e2e-compile --help` output contains no baseline-writing option; the
only producer is `bin/e2e-selector-baseline.js`, a separate binary that gates nothing,
writes to stdout, and takes no output-path argument.
Falsifier: add an `--update-baseline` flag that writes the file and the byte-compare test
goes red.
Also verified here, since it is the other property with no home: `selector-policy.js`
loads with no `node_modules` resolvable — the test asserts the module's own `require`
calls resolve only to Node builtins, so the `.githooks`-without-`npm install` claim in the
docs has an enforcement point rather than a promise.

**AC-5 — A flow that compiles green today is refused, and the artifact a browser would have run is never produced**

Baseline that can move the wrong way, **re-measured live rather than assumed** — the first
draft named two flows and one of them was already failing:

| corpus flow | today, real CLI | differential-capable? |
|---|---|---|
| `gate-smoke-all-pages.yaml` | **exit 0**, `gate-smoke-all-pages.sh` written, resolving `role=combobox >> nth=0` | **yes** — the whole AC rests on this one |
| `vehicle-brand-select.yaml` | **exit 1**, no `.sh`, 6 pre-existing `unsupported expect string` errors | no — identical before and after, so it can never show the gate |

So the honest delta this entity can demonstrate on the real corpus is **1 of 1
differential-capable flow**, not "≥3 of ≥3". Stated that way because the larger number
would read as more evidence while being less.

End state: `gate-smoke-all-pages.yaml` is refused with exit 1, naming
`role=combobox >> nth=0` and its class, and writes no `.sh`; with a baseline adopted it
compiles again with the resolved-grandfathered stderr line; a hand-added violation on a
new element is refused.
Verified by (E2E, real runtime, not a unit test): a **differential** run of the real CLI
over the same flow and mapping bytes — at `origin/main` (exit 0, `.sh` present) and at the
branch head (exit 1, `.sh` absent, class id on stderr). Both exit codes and both output-dir
listings recorded as command output.
Note on the observable, and why it is the exit code and the artifact rather than the
artifact's contents: the written script contains **zero** `nth=` tokens — verified,
`grep -c 'nth=' gate-smoke-all-pages.sh` → `0`, `grep -c combobox` → `1` — because
`selector-translate.js:93-95` strips the chord during translation. The banned form reaches
the artifact only as the widened pattern it degrades into, which is #124's defect, not an
observable for this one.
The differential is what makes this able to fail: an implementation that does not actually
block produces two identical runs.

## Test plan

1. `compiler/test/selector-policy.test.js` — per class: one violating and one clean
   selector; comment/description lines carrying a banned token are ignored (the PR #8 C2
   narrowing); quoted and unquoted YAML scalars; baseline parse/match; `#` comments;
   duplicate-string-on-a-different-element must not match a baseline record; changed
   selector on a baselined element must not match; builtins-only `require` assertion.
2. `compiler/test/selector-gate.test.js` — compile and dry-run against fixture mappings;
   asserts exit status, the diagnostic fields, no output file, `--json` `errors[]`
   carrying the class id, that a file-scope-only finding warns without blocking, and that
   a resolved grandfathered finding prints its own distinct line.
3. Drift test (AC-2) — bash consumer against a perturbed copy of the policy module.
4. `bin/e2e-selector-baseline.js` — output over a fixture mapping is exactly the records
   the gate would match, round-tripped through `parseBaseline`; and the fixture's
   grandfathered set makes the AC-3 fixture compile clean, so producer and consumer are
   proven to agree rather than asserted to.
4. `test/integration-smoke.sh` — unchanged expectations must still hold (it calls the
   linter directly; the wrapper preserves exit codes 0/1/2 and the `path:line: class:`
   stderr shape).
5. Full suite at stage exit. No version, marketplace, or SKILL.md frontmatter surface is
   touched, so `version-parity-check.sh` / `marketplace-verify.sh` /
   `skill-frontmatter-lint.sh` are not earned by this diff — stated so validation can
   check the classification rather than the checklist.

## Measurement

The two channels are **disjoint** — a finding is blocking or it is a warning, never
counted in both. On the corpus that is 3 blocking and 36 warnings, not 3 and 39.

- Blocking refusals on the real corpus: 0 of 3 today → 3 of 3 with no baseline; 0 of 3
  with the baseline adopted, each printing the resolved-grandfathered line.
- File-scope findings surfaced: 0 of 36 today → 36 of 36 as warnings.
- Differential-capable corpus flows refused: 0 of 1 → 1 of 1 (AC-5's table).
- Policy definition sites: 2 (bash regexes + prose) → 1 table + prose that points at it.
- Diff coverage on the executable surface: bar 85%, measured on added/changed executable
  lines only. Prior gates in this repo have twice mis-derived this number by counting
  comment lines lcov emits `DA` records for — the denominator is executable lines, and
  numerator and denominator are reported separately.

## Doc diff (proposed here, applied in implementation, verified at validation)

- `e2e-pipeline/CLAUDE.md` § Selector Priority — "Enforcement lives in
  `scripts/lint-mapping.sh` (what's banned)" becomes "Enforcement lives in
  `compiler/lib/selector-policy.js` (the single banned-class table), invoked by
  `scripts/lint-mapping.sh` and by the compiler at parse time"; items 7/8/9's
  "BANNED — see `scripts/lint-mapping.sh`" pointers retarget to the module; the bounded
  claim "one banned-class table, two traversals" is stated where the absolute would be.
- `e2e-pipeline/docs/ci-integration.md` § Mapping Linter — compile and dry-run now enforce
  the same table, blocking on what a flow resolves and warning on the rest;
  `--selector-baseline` and the baseline record format; the baseline is produced by
  `bin/e2e-selector-baseline.js <mapping.yaml>` on stdout; and the linter's new
  prerequisite — it now requires `node` on PATH, where it was previously pure bash with
  zero dependencies and wireable into a `.githooks` without `npm install`.
- `e2e-pipeline/skills/e2e-compile/SKILL.md` — the new failure mode and its remedy.
- `e2e-pipeline/agents/e2e-mapper.md` — producer-side: emitting a banned form now fails
  the consumer's compile, not just its lint.
- `e2e-pipeline/CHANGELOG.md` is release-please-owned; not hand-edited.

## Implementation dispatch sizing

**One dispatch.** Three behaviors (policy module + linter delegation; compiler wiring;
baseline/delta mode) but they are sequentially dependent, not independent — 2 and 3 both
consume 1 — so splitting buys no parallel wall-clock and pays three cold starts.

**Implementation re-verifies before building** (README ideation clause): re-fetch
`origin/main`, re-run `/tmp/measure-resolved-scope.js`, **and re-run the two live compiles
in AC-5's table** — the finding counts are not enough, because AC-5 rests on
`gate-smoke-all-pages.yaml` still exiting 0 today and `vehicle-brand-select.yaml` still
exiting 1 for unrelated reasons. An earlier draft of this entity named both flows as
differential subjects and was wrong about one of them. Report any movement; a premise that
has collapsed is escalated, not built around.

## Out of scope, with owners

- Narrowing the `>> nth=` chord ban to the interaction path — **#124**.
- Multi-match visibility semantics — **#91**.
- Migrating the grandfathered findings — the consumer repo, tracked by its own baseline diff.
- Any change to `selector-translate.js` translation behavior — **#124**.
- Enforcing the policy on the LLM-driven paths (`e2e-test-runner`, `e2e-flow-verifier`,
  walkthrough) — **no owner today; a backlog entity is filed by this stage.** Without it
  the sprint exit condition is not met by #88 alone.
- An element that declares `css_selector:` is still refused when its `selector:` carries a
  banned class. The mitigation applies to the click path only, while `selector:` still
  feeds the visibility path, so refusing is correct — recorded because it is surprising.

## Stage Report: ideation

**TL;DR** — #88's filed premise was retired by PR #123; three ban classes survive and
none is enforced anywhere the compiler can reach. This entity extracts the bash regexes
into a dependency-free `compiler/lib/selector-policy.js`, has `scripts/lint-mapping.sh`
exec that module instead of carrying its own patterns, calls it from `parser.js` so
compile and dry-run hard-fail before any artifact is written, and adds a delta baseline
(consumer-repo-owned, stdout-only producer, keyed by element identity) so real
grandfathered findings do not red a working repo on day one. Five ACs; AC-5 is the
E2E/value one and is a differential against `origin/main`, so an implementation that does
not actually block produces two identical runs and the AC fails. One dispatch, 4h
appetite, +50% tolerance. `design: required` — it decides a CLI flag, an on-disk format
consumers commit, and a module boundary two consumers read.

**Scope authorship** — not composed by the agent. Carried from the EM `proceed`
determination on issue #88 (2026-08-01), which the captain delegated explicitly. One
sub-decision (gate granularity) is escalated to the captain rather than taken here.

**Reverse-recovery** — one broken seam (policy exists but only as inline bash), repair
scoped to it. No greenfield.

**Pre-mortem** — criteria that pass without delivering value; plus the named gap that
#88 alone does not close the sprint exit condition, because the LLM-driven browser paths
are unreached.

**`--ac-scan`** — `spacedock status --read e2e-selector-compile-gate --ac-scan`: all five
ACs resolve; each reports `unevidenced=true` (expected at ideation) and `citations=0`,
which is the known-untrustworthy counter recorded in ROADMAP's "Hazard carried forward",
not a finding about the ACs.

**`dev-flow-work-context-check.py validate`** — re-run after this revision, since an edit
invalidates the prior receipt.

### Gate cycle 1 — EM verdict `narrow`, four conditions, all addressed

| # | EM finding | disposition |
|---|---|---|
| 1 | AC-2's parity test is tautological — both sides are one code path, so no edit can redden it | **Fixed.** AC-2 is now a *drift* test against a perturbed copy of the module; the "no second table exists" absolute is replaced by the bounded "one table, two traversals" |
| 2 | AC-5 measures refusal rate but is titled as value; the "no browser spawned" probe cannot fail because `e2e-compile` never spawns one | **Fixed.** AC-5 is now a differential against `origin/main` on two named real flows, with the written artifact as the observable |
| 3 | The baseline's no-count residual is ~13% of the real corpus (`role=switch >> nth=1` ×3) | **Fixed, and stronger than the proposed count-pinning.** Records are keyed by element identity, which is stable across formatting *and* refuses a re-paste onto a different element |
| 4 | The resolved-scope alternative was never named; it is what forces the baseline into existence | **Named, measured, escalated, ruled.** Captain ruled option B (two severities) on 2026-08-01; the ACs are written against that answer |
| 5 (cond.) | Module must stay dependency-free; the linter's new Node prerequisite is undocumented | Adopted into the design and into the `ci-integration.md` doc diff |
| 6 (cond.) | AC-4's "human redirect" wording overclaims | Rewritten: the enforcement point is the absent write call; stdout-only buys a reviewable diff, not human authorship |
| 7 (cond.) | Implementation re-verifies corpus numbers against fresh `origin/main` | Written into the dispatch sizing section |
| NM | The translator's silent chord strip is missing from the audit | Added as a fifth audit row |
| NM | `css_selector:`-mitigated elements are still refused | Recorded in Out of scope with its reason |
| NM | Sprint exit is not met by #88 alone; the runner path has no owner | Recorded in the pre-mortem and Out of scope; a backlog entity is filed by this stage |

### Gate cycle 2 — EM verdict `narrow`, six findings, all addressed

The cycle-2 verdict named the real defect of cycle 1's revision: adopting the captain's
option-B ruling moved the blocking decision from parse time to resolve time, and the
document was updated in its prose without being updated in its mechanism.

| # | EM finding | disposition |
|---|---|---|
| 1 | The blocking gate was wired to `parser.js validateMapping()`, which structurally cannot see the resolved set | **Fixed.** A wiring table now names both severities' points: warnings after `parse()`, blocking after `resolve()` and before `generate()`. AC-1's falsifier retargeted. `parser.js` is no longer touched at all |
| 2 | `resolver.js` discards element identity (`resolveElement` → `{selector}`), so the baseline key is not computable; it had no audit row, no price, no cross-site answer | **Fixed.** New `EXISTS_BROKEN` audit row with the three line numbers; the threading is named; the cross-site key resolves to the mapping file's basename, already unique per site; and the appetite's re-cut is anchored on this seam |
| 3 | The only baseline producer (`lint-mapping.sh --format=baseline`) is line-oriented and YAML-blind, so it cannot emit an element-keyed record | **Fixed.** Producer moved to a separate binary, `bin/e2e-selector-baseline.js`, which walks the YAML and gates nothing — which also removes the "the gate produces its own baseline" smell entirely |
| 4 | The producer emits the file-scope set while the baseline gates the blocking set, so the natural adoption pre-disarms 12× the ruled surface | **Answered, not machinery.** The asymmetry is kept and made explicit: an already-existing banned element *is* the pre-existing debt the ruling protects. What it costs — a future flow resolving one compiles green — is stated, and mitigated by a distinct resolved-grandfathered stderr line every run. A new element, a changed selector, and a rename all still block |
| 5 | AC-5's differential was degenerate on one of its two named flows, and its observable was one the EM measured as always-zero | **Fixed, and re-measured live rather than taken.** `vehicle-brand-select.yaml` exits 1 today for six unrelated `unsupported expect string` errors — dropped. AC-5 now rests on `gate-smoke-all-pages.yaml` alone and says so: 1 of 1 differential-capable flow. Observable is exit code + artifact presence + class id; the artifact's *contents* are explicitly not the observable, because `grep -c 'nth=' gate-smoke-all-pages.sh` → 0 (the translator strips the chord) |
| 6 | AC-1 was still titled and verified as file-scope blocking, re-installing option A | **Fixed.** Retitled to the resolved element; the fixture now carries the banned class on two elements where the flow references only one, so a single command proves both severities |

**Corrected in the other direction — one EM number was wrong and is not adopted.** The
cycle-2 report gives 23 flows with pre-existing parse/resolve errors and calls the
entity's figure wrong by ~2×. Re-ran `/tmp/measure-resolved-scope.js` and counted its
error block directly: **43**, against 47 total flow files (the entity's earlier "45" was
also wrong, and is corrected to 47). The floor argument holds at either number; the number
recorded is the one that reproduces.

**Non-material items adopted:** the two rule-6 absolutes at the module design
("`BANNED_CLASSES` appears once in the repo", "every consumer's decision goes through this
one function") are deleted in favour of the bounded claim plus its enforcement point;
element-name stability is bounded to reformatting, with rename called out as blocking;
condition 5 (dependency-free module) became a test line inside AC-4 instead of prose; the
Measurement channels are stated disjoint (3 blocking + 36 warnings, never 39).

**Appetite:** raised 4h → 7h, tolerance +40% (10h), on the EM's walk of the implied diff
surface. Per the EM's own guidance the estimate is not being raised further to chase the
diff — the re-cut is pre-authorized at the `resolver.js` seam instead, so the worker takes
it without a round trip.

## Stage Report: implementation

**TL;DR** — The policy is now one table in `compiler/lib/selector-policy.js` with two
traversals over it. `scripts/lint-mapping.sh` execs the module and carries no patterns of
its own (exit codes and stderr byte-identical to the predecessor on both shipped
fixtures). `compiler.js` blocks between `resolve()` and `generate()` on banned selectors
the flow resolves, and warns on the rest of the mapping file. `resolver.js` gained the
element provenance the blocking scope and the baseline key both need. A baseline the
compile path only reads grandfathers pre-existing debt, keyed by element identity, and its
producer is a separate binary that gates nothing. Two commits: `dc1d6a6` (build) and
`bb7fc94` (the validation round's fixes).

### RED before GREEN

- `selector-policy.test.js` written first: `Cannot find module '../lib/selector-policy.js'`,
  0 pass / 1 fail. GREEN after the module: 26/26, now 28/28.
- `selector-lint-drift.test.js` written first and run against the **pre-change** bash
  linter: `AssertionError: expected NOT to match /has-text/` — the linter kept reporting a
  class the module no longer carried, which is the drift the AC exists to catch. GREEN
  after the wrapper: 2/2.
- `selector-gate.test.js` surfaced a real defect at first run rather than confirming the
  code: the fixture's two elements share one banned selector string, and the channel split
  swallowed the sibling's warning. That is why the fixture is shaped that way.

### Two defects found by writing the tests, not by reading the code

1. **The gate fixture's identical-selector siblings.** The first channel split subtracted
   by `(class, selector)` string, so an element sharing a banned string with a blocking
   one lost its warning entirely. Rebuilt on element identity after validation showed the
   same bug had a second face (see cycle 1, finding 4).
2. **`runCompile` in the gate test used `execFileSync`,** which returns only stdout — so
   every "it warned about X" assertion on a *passing* compile was matching against `''`.
   A check that cannot fail. Switched to `spawnSync`.

### Named what CI would do differently

Tests added, so the job's margin was the relevant check; no OS/libc/locale/clock-dependent
behaviour and no CI-pinned tool in the diff. Required contexts read live from
`gh api …/branches/main/protection`: one required check, `version parity (plugin.json /
marketplace.json / codex / README)`. No job renamed. It passed on `dc1d6a6`.

### Checks the diff earned, and the ones it did not

No version value, `marketplace.json` structure, plugin directory, or SKILL.md frontmatter
block is touched, so `version-parity-check.sh` and `marketplace-verify.sh` are not earned —
though the validator ran parity anyway and it passes. `skill-frontmatter-lint.sh` run
regardless (35/35) because a SKILL.md body changed. No `.github/workflows/` file touched.

### Full suite at stage exit

`node --test compiler/test/*.test.js` → **936 tests, 935 pass, 0 fail, 1 skipped**
(the opt-in browser test), run with nothing else competing for the machine.

Two earlier runs each reported one failure in `trace-finalization.test.js`. Both were
written off per the per-failing-line rule, not per impression: the file alone is 49/49
twice on this branch and 49/49 on clean `main`; the diff touches neither that test nor
`scripts/finalize-trace.sh`; and both failures occurred in runs where a second full suite
was executing concurrently — a condition I was perturbing myself, which Proof Policy 7
says makes the number evidence about the perturbation. It is issue #122's known
load-flaky file.

### Feedback Cycle 1 — budget record

| | |
|---|---|
| Round effort | ~1.5h against the ideation-declared 7h estimate |
| Deviation | within the declared +40% tolerance; no design reset |
| Reviewers | cross-model (`agy`), silent-failure, correctness/back-compat, security, fresh-context validator |
| Findings | 17 raised · **10 fixed** · 4 declined with reasons · 3 confirmed clean |

**Fixed (10).** `>> nth=-1` invisible to the pattern; `selector: "div #main >> nth=1"`
collapsing to `"div` in the text traversal; the channel split rebuilt on element identity;
AC-1's missing path and line in the blocking diagnostic; `recordReference` silently
no-oping; CRLF and embedded tabs in baseline records; the cross-site mapping key not
using a basename; `--help` on the linter; the `>>` append-redirect in `SKILL.md`; five
stale `scripts/lint-mapping.sh` authority pointers plus the unenforced "never writes"
absolute and a `resolver.js:62` reference this diff shifted to `:64`.

**Declined (4), each named rather than dropped:**
- *Every blocking error prints twice.* Reproduced on `origin/main` for parse errors
  (`054-service-category-foundation`: each `ERROR:` line appears 2×). Pre-existing and
  general; fixing it is unrelated churn in a PR that already carries a gate.
- *`--json` loses structured fields for a thrown baseline error.* Real, and identical to
  how every other thrown error in `bin/e2e-compile.js` is already wrapped. Not introduced
  here.
- *No regression test for `EACCES`/`EISDIR` on the baseline read.* The rethrow is a
  one-line `if (e.code === 'ENOENT')`; a test would pin the shape but the reviewer's own
  verdict was "correctly coded, untested". Accepted as residual.
- *`scanMappingText` cannot read block/folded scalars.* Not fixed — fixing it means a
  YAML parser in a module that must stay dependency-free. Instead the predecessor's
  caveat, dropped in the port, is restored to the docstring and pinned by a test, together
  with proof that the element traversal does see those values. The bound is one-directional:
  a lint that passes where a compile blocks, never the reverse.

**Confirmed clean (3):** the security lens found no findings (argv passthrough is an
array not a shell string; `js-yaml` 4's `load` is the safe loader; the read-only claim
holds structurally); `loadSelectorBaseline` swallows only `ENOENT`; the linter fails
closed when `node` is missing.

### One process error of mine, recorded because it invalidated a result

Cycle 1's validator graded `dc1d6a6` **while I was editing the worktree it was reading**.
It caught this itself, re-ran everything in an isolated detached checkout, and said which
SHA its verdict applied to. Its AC-1 FAIL was correct for that commit. Cycle 2 grades a
frozen `bb7fc94` in the validator's own isolated worktree, which is what should have
happened the first time.

## Stage Report: validation

**TL;DR** — Two fresh-context validation cycles, two cross-model rounds, three lens
reviewers. Cycle 1 rejected on AC-1 and on my own process error (it graded a commit while
I edited the worktree under it). Cycle 2, against a frozen `bb7fc94` in the validator's own
isolated checkout, returned **5 of 5 ACs PASS**, diff coverage **91.7%** against an 85%
bar, and suite green in isolation — with two Material findings, both of which were already
closed by commits that landed after the SHA it graded, and both re-verified closed at head.
Final head `0a8b8a7`: **946 tests, 945 pass, 0 fail, 1 skipped**; CI green on that exact
commit.

### Evidence block

- **Lenses:** diff classified as executable + prose + a shell-script contract change.
  Fired — **correctness** (exercise-based, per the prose clause: the reviewer ran the
  documented commands rather than reading them) `1 Material`; **silent-failure**
  `1 Material, 1 non-material`; **security** (a shell script and a new CLI reading
  untrusted YAML) `0 findings`; **manifest/back-compat** (`lint-mapping.sh` gained a
  `node` prerequisite, and an installed copy reads it) `0 Material`. Not fired:
  **type-design** — no new or changed type, the findings are plain records;
  **concurrency** — no locks, async ordering or shared mutable state; **resource-lifecycle**
  — no processes, handles or unbounded growth beyond a synchronous file read.
- **Diff coverage:** **320/349 = 91.7%** on executable added/changed `.js` lines
  (bar 85%). Method: `git diff --unified=0` added lines ∩ lcov `DA` records, then a
  second filter dropping blank, comment and bare-brace lines — the filter two prior gates
  in this repo skipped, which is why one reported 58/58 where the truth was 17/17. Numerator
  and denominator reported separately. Most misses are subprocess-only paths node's coverage
  does not instrument; each was exercised by hand. The 7 added executable lines in
  `scripts/lint-mapping.sh` were all exercised, including the no-`node` and missing-module
  branches under `env -i`.
- **Adversarial:** 3 edits by me, 3 more by the cycle-2 validator, none reused. Mine:
  neutralising the blocking return (7 red), grandfathering everything (7 red), dropping
  resolver provenance (8 red), plus re-adding a private regex to the linter (drift test
  red). The validator's third edit reddened 9. **Its first two did not** — that is the
  finding, not a pass: the `nth=-1` widening and the quoted-`#` fix had no falsifier.
  Both now have one, each probed by reverting the fix and watching exactly one test redden.
  One of my own probes also silently failed to run at first — a line placed after an
  `exec` under `set -e` — and was re-run only after proving it fired.
- **Cross-model:** `agy` 1.1.9 (Google Antigravity), cross-vendor to the Claude session
  running the gate, **two rounds** — one on the build, one on the fixes. Round 1: 3 P1,
  3 P2, 1 P3. Round 2: 1 P1, 3 P2, 3 P3, and 2 categories explicitly clean. `codex` not
  attempted this time: the same gate last session ran 40 minutes without finishing and
  `agy` completed, so `agy` was taken first rather than after an observed failure. Every P1
  from both rounds is fixed; two P2s are declined with reproduced evidence (both inputs are
  invalid YAML — `js-yaml` rejects them, so no consumer reaches the scan).
- **E2E:** the AC-5 differential on the real consumer corpus, through the real CLI, all
  three legs reproduced independently by the validator: `main` exit 0 with the `.sh`
  written; branch exit 1 with the output directory empty and the class named; branch with
  an adopted baseline exit 0, `.sh` written, and the distinct resolved-grandfathered line.

### Scope checkpoint

Every changed file maps to an AC or to the ideation-approved doc diff; **zero unmapped**.
Confirmed independently by the cycle-2 validator. No version, marketplace, or SKILL.md
frontmatter surface is touched, so `version-parity-check.sh` and `marketplace-verify.sh`
are not earned by the diff — both were run anyway and pass, as does
`skill-frontmatter-lint.sh` (35/35).

### Feedback Cycle 2 — budget record

| | |
|---|---|
| Round effort | ~1h against the ideation-declared 7h estimate (cumulative ~2.5h) |
| Deviation | within the declared +40% tolerance; the pre-authorised re-cut was **not** taken — resolver provenance landed inside the first third, as its trigger required |
| Findings | 12 raised · **7 fixed** · 3 declined with reasons · 2 already closed at head |

**Fixed (7):** cross-site basename collisions now refused rather than silently merging two
mappings into one key namespace; `locateSelectorLine` rewritten to attribute each
`selector:` line to its nearest preceding key and to return a line only when exactly one
candidate matches (it previously inherited a sibling's line, and picked the first page's
line for a duplicated element name — a confident wrong answer, which its own docstring
forbade); the double-quote unescape bounded to the two escapes the docstring names;
falsifiable tests for the `nth=-1` and quoted-`#` fixes; `--help` exits 0 rather than
being reported as a usage error; a `docs/debugging.md` anchor this branch's own heading
rename had broken.

**Declined (3):** the double-printed `ERROR:` lines (reproduced on `origin/main` with an
unrelated resolve error — pre-existing and general, and fixing it is unrelated churn);
`--json` losing structured fields for a thrown baseline error (identical to how every
other thrown error is already wrapped); a quoted scalar with trailing content and an
unterminated quote (both rejected by `js-yaml` with a parse error, so the mapping never
loads — handling them would mean the linter disagreeing with the YAML spec).

### Residuals accepted, named rather than left implicit

1. **`scanMappingText` cannot read block or folded scalars.** The linter misses
   `selector: >` values; the compiler blocks them. Reproduced by the validator in the
   claimed direction — a lint that passes where a compile blocks, never the reverse.
   Closing it means a YAML parser in a module that must stay dependency-free.
2. **A baseline grandfathers a whole file's banned elements, not just the ones a flow
   reaches.** A future flow that starts resolving one compiles green. Mitigated by the
   distinct resolved-grandfathered line, and deliberate: an element that already exists is
   the pre-existing debt the captain's ruling protects.
3. ~~`test/integration-smoke.sh`'s 10 added lines are unexercised.~~ **Withdrawn — the
   claim was false.** `git diff --stat origin/main...HEAD -- '*integration-smoke*'` is
   empty: this branch adds zero lines to that file, exactly as the entity's own test plan
   (item 4) says. The residual was carried over from a validator's coverage note without
   being checked against the diff, which is the inherited-claim case Proof Policy 6 names.
   The file's real contract — the linter's exit codes and `path:line: class:` stderr shape,
   which it consumes — was verified directly against the wrapper and is byte-identical to
   the predecessor on both shipped fixtures.
4. **`#88` does not close the sprint exit condition.** The LLM-driven browser paths are
   unreached; filed as **#126** with a backlog entity.

### Validation gate — EM verdict `narrow`, merge authorised on two conditions

| # | EM finding | disposition |
|---|---|---|
| 1 (Material) | AC-4's byte-compare runs only on a *blocked* compile, while two docs cite it as the enforcement point for "the compile path only ever opens the baseline for reading". A regenerate-on-green write would be added on the success path, which that assertion cannot see | **Fixed** in `64c7278`. The grandfathered success case byte-compares too, and the assertion was probed: appending to the baseline after a green compile reddens it |
| 2 (Material) | Accepted residual 3 claimed `test/integration-smoke.sh` had 10 unexercised added lines; the branch adds **zero** lines to that file | **Withdrawn above.** A validator's coverage note adopted without checking it against the diff — the inherited-claim case Proof Policy 6 names |
| NM | The cross-site resolved-provenance channel has no test, and stamps the mapping file by a different expression than the single-site path — a mismatch fails **open** | **Fixed** in `64c7278`, and the first version of that test did not discriminate (one site made the fallback right by accident and it stayed green when the stamp was deleted). Two sites now, banned element in the second, probed red |
| NM | The documented exit codes still called `1` the usage-error code after `--help` moved to `0` | Fixed |
| NM | `dc1d6a6`'s commit body carries "a baseline the compiler reads and **never** writes" with no enforcement point named. The doc was fixed later; a commit message is immutable | Recorded, not actionable. Proof Policy 6 puts commit messages in scope precisely because nothing downstream checks them, and this is that case landing on me |

**Circuit breakers — EM ruled neither fires.** One rejected cycle, not two: cycle 1 was
rejected on AC-1, cycle 2 passed all five ACs, and a passed gate that surfaces Material
findings is not a rejected cycle. The budget brake fires on *exceeding* tolerance; ~2.5h
against a 7h estimate is under it. So the verdict stayed with EM and no Gate Authority
bullet routed this to the captain.

**Final head `64c7278`** — 947 tests, 946 pass, 0 fail, 1 skipped; biome clean.

## Delivered — awaiting terminalization by the state holder

PR [#128](https://github.com/iamcxa/kc-claude-plugins/pull/128) squash-merged on captain
approval, `2026-08-01T13:57:23Z`, merge commit `8634d89`. Exact-head CI re-confirmed green
on `64c7278` immediately before the merge, and `version parity` — the sole required
context — is green on the merge commit itself. `release-please` is running on `main` and
will open its own Release PR; no version was hand-bumped anywhere in this branch.

**Not done here, and why.** This workspace is a **non-holder** of `spacedock-state/dev`
(the holder is the `antananarivo` workspace). The `pr-merge` lifecycle hook refuses to run
its terminal transaction — clear the `mod-block`, set `completed` to the authenticated
`mergedAt`, set the passed verdict and `done`, then the fail-closed archive move — from a
non-holder or from a detached substitute, and that refusal is the point. So the frontmatter
here still reads `status: validation` with an empty `verdict`, deliberately: writing those
cells by hand from a workspace the hook will not run in would produce an entity that *looks*
terminal without the transaction that makes it so.

**What the holder needs, all of it authenticated and already recorded above:** product PR
`#128`, merge commit `8634d89`, `mergedAt 2026-08-01T13:57:23Z`, verdict PASSED on the EM
validation gate (`narrow` + merge authorisation, both conditions landed in `64c7278`).

**Measurement, for the human-triggered ledger pass.** The ledger's source is the *archived*
entity, so the row is not written here either — but the observations it will need are:

| cell | value | derivation |
|---|---|---|
| `task_id` | `pjjs91zrbrcm2we467a3vvp4` | frontmatter |
| `slug` | `e2e-selector-compile-gate` | |
| `dispatches` | `8` | 3 EM (2 ideation cycles + 1 validation gate), 2 fresh-context validators, 3 lens reviewers. Implementation was **not** dispatched — it ran in the FO session, which is the ideation-declared sizing (one worker session) collapsing into the orchestrator, and worth reading as such rather than as a dispatch count of 9 |
| `rework_rounds` | `2` | two validation feedback cycles, both budget-recorded above |
| `wallclock_hours` | `7.3` | entity opened `2026-08-01T06:39:59Z` → `mergedAt 13:57:23Z`. Against the ideation-declared 7h estimate with a +40% tolerance — inside it, and the pre-authorised re-cut was not taken |
| `tokens_if_known` | `n/a` | no dispatch reported an observable figure; not inferred |
| `diff_coverage` | `91.7` | 320/349 executable added/changed `.js` lines, measured by the cycle-2 validator with the comment-line filter applied. Folding in the 7 added `.sh` lines gives 89.3%; the `.js`-only figure is recorded because that is what the bar is scoped to |
| `escaped_defects_7d` | `pending:2026-08-08` | seven days from `completed` |

Cross-model gate for the record: `agy` 1.1.9, two rounds, cross-vendor to the Claude
session that ran the gate. `codex` was not attempted — the same gate one session earlier
ran 40 minutes without finishing while `agy` completed, so `agy` was taken first rather
than after an observed `codex` failure. Stated plainly because the workflow asks that a
skipped preferred reviewer carry its observed failure, and this one carries a prior
session's rather than this session's.
