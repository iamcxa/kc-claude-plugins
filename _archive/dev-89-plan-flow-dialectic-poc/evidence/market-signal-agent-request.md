## plan-flow role request: market-signal rating agent (Captain, 2026-09-03)

Captain's words: plan flow 我想新增一個功能性 agent 像是 CE 及其他角色一樣，可能叫做 seer, seeker, sentinel, or product-hunter，功能是依據討論好但還沒決定的 receipt 去爬 reddit 以及 product hunt，初步先 web search 看看效果，之後再最佳化此流程，目的是多一道 rating 關卡，確保想解決的問題真的值得解決，例如，已經有人在做（正向訊號），已經有人在討論等，但這個要注意不是每次都需要這樣走，例如做給自己的工具，這一個項目就不需要高分通過

### FO reading (design notes, not yet a Brief)
- Placement: after station 2 produces the six Seam-1 fields and before the Captain's go/discover/stop; it rates, it does not decide. Input = the draft receipt (problem statement, target human, wedge). Output = a signal report: who else is building this (positive), where it is discussed (positive), what they charge or how they fail (calibration), plus a confidence and the sources.
- Gate semantics: the report attaches to the receipt as one more premise ("market signal: N/5, sources"), not a pass/fail. Threshold is per work item, declared in the receipt's `audience:` field: `self` (Captain's own tooling) skips or accepts any score; `team` needs "someone discusses this"; `market` needs "someone pays for this". This is the "not every item needs a high score" rule made mechanical.
- Sources v1: web search only (Reddit, Product Hunt, HN, GitHub search) through the harness WebSearch/WebFetch; no scraping, no accounts. v2: direct APIs if v1 shows signal.
- Cost: one dispatch per receipt, opt-in by audience; bounded by a fixed query list and a 10-minute budget.
- This is the office-hours "status quo is your real competitor" and "demand reality" principles run against the world instead of against the Captain's memory; it strengthens Q1/Q2 with outside evidence and is the natural place for a fresh-context reviewer (like science-officer for delivery).
- Name: to be chosen by the Captain; FO's default proposal is `market-seeker` (verb, says what it does, no mystique).
- Not in DEV-89 scope. Candidate for plan-flow POC 3 after DEV-89 proves stations 1-4.
