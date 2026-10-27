# 0035. learn and peers are on by default, and an adopter picks the recommended extensions at install

Date: 2026-10-25

## Status

Accepted

## Context

The workflow template shipped `extensions: []` and the package README table gave no tier, so an adopter had to know which of seven extensions to list. All six known adopters already list `learn` and `peers`; `kc-paseo-plugins` lists `journey-map` and `release-acceptance` together, `subspace-relay` lists `journey-map` alone (read from each default branch, 2026-10-25). Neither `spacedock:commission` nor `spacedock:refit` knows `extensions:` (`grep -rn "extensions:"` over Spacedock 0.27.3 finds nothing), so the choice lives in the package's `references/sd/adoption.md`. A template default reaches an adopter at its next re-sync: `git merge-file` merges an adopter `[]` clean to `[learn, peers]` and conflicts on any other list.

## Decision

**Words:** 「版本走查預設全部都啟用，我們要討論一下預設值，列一下哪些建議啟用，哪些預設啟用」 then 「那就改成版本走查跟地圖一起？我想要讓必要的成為預設，建議的寫在repo readme，adopter 安裝時讓使用者用ui選」, then 「我認為 peers 應該也要預設開啟，它不是只有給 paseo 也是給 cc/codex 的基本準則，不是嗎？」, then 「那就這樣做，learn+peers預設開啟，其他建議」 — Captain, 2026-10-25, chat; and 「准」 — Captain, 2026-10-25, chat, at the ideation gate, accepting D1 to D3 as recommended.

**Options considered:**
- `learn` and `peers` required and the template default; `journey-map` with `release-acceptance` as one choice, `codex` and `roborev` recommended; `copilot` optional; the recommended list in the package README; chosen at install through the host's Ask UI (chosen)
- `learn` alone required (FO's first recommendation; the Captain asked about `peers` and ruled both required)
- `extensions: []` in the template and the install ask writing the required pair (D3; not chosen: the Captain ruled the template carries the default)
- the root `README.md` as the list's home (D1; not chosen: the package README already holds the table and a lint can check it against the template line)

**Recommended:** `learn` and `peers` in the template, the tier list in the package README, `copilot` offered unchecked and `second-reviewer: copilot` written when `codex` and `copilot` are both chosen, and the one-time re-sync conflict accepted (the design's D1 to D3); the Captain accepted all three.

**Protects:** none

The template line names exactly the README rows tiered `required`, and `lint-skills.py` refuses a tree where they differ. The install ask turns on a recommended or optional row only from an answer, and lists no row whose probe failed.

## Consequences

A new adopter gets `learn` and `peers` without being asked. Each existing adopter README meets one conflict hunk on the `extensions:` line at its next re-sync, and a wrong resolution drops that adopter's extensions with only the sync PR's review to catch it. The Ask UI rendering and its option cap were not exercised by any worker. Reopen if an adopter loses an extension to a re-sync, or if the host caps a multi-select below four options.
