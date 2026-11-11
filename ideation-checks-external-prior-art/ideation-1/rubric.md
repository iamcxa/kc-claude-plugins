# Replay rubric (pre-registered; fixed before any run, confirmed by the qnow dev2 FO first)

Scored text: the lines a run added or changed in the task file. Scorer: a fresh
Claude Sonnet per text (`claude -p --tools ""`), given only this rubric and the
text under a hashed file name, blind to the arm. Each hit quotes the text; a
quote not found verbatim scores 0. Pass 1 is the score; pass 2 re-runs the same
scorer to show noise.

## Positive case 1: qnow booking-attempt-identity, dispatch ideation-2

- P1: names the WHATWG DOM AbortController / AbortSignal (or fetch's `signal`
  option) for cancelling or ignoring an async step that no longer belongs to the
  current attempt.
- P2: names the Idempotency-Key HTTP header field
  (draft-ietf-httpapi-idempotency-key-header), or the idempotency-key pattern with
  a named source, for the duplicate-send key.
- P3: every item named under P1 or P2 says adopted, adapted or rejected, with a
  reason.

## Positive case 2: qnow owner-cancels-booking, dispatch ideation-2

- P4: names HTTP conditional requests (RFC 9110 preconditions: ETag with
  If-Match, or 412 Precondition Failed), or optimistic concurrency with a named
  source, for a cancel that races a shop's confirm.
- P3 applies to P4 as well.

## Control: qnow agents-md-rules-refresh, dispatch ideation-1

- N: the count of standards, drafts, platform APIs or library patterns the text
  names as adopted or adapted.
- W: words in the prior-art part (the `### Prior art` section under arm a, the
  `Prior art:` line under arm b, any equivalent passage under base).

## Harm, every run

- H1: a cited standard, draft or API that does not exist (scorer quotes it; the
  scoring FO checks each one by its document identifier).
- H2: a cited item that the scorer judges not to bear on any decision in the
  design, with the quote and one sentence why.

## Arm c (engineering-reviewer)

The same P1 to P4, N, H1 and H2, scored on the reviewer report's text.
