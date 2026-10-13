// Two maps in the two shapes adopters write: one-line flow questions, and block style with
// hand-wrapped plain scalars and a sequence indented to its key.
export const FLOW = `# header comment
journey: shop
releases:
  - {id: r1, goal: "first"}
steps:
  - id: find-shop
    card: "Find a shop"
    stories:
      - id: enter-by-qr
        release: r1
        status: exists
        evidence: EnterByQr
        card: "Scan the QR code"
        questions:
          - {id: q1, status: open, ask: "Who issues codes?"}
          - {id: q2, status: answered, ask: "Old code reuse?", answer: "Never reused."}
          - {id: q3, status: deferred, because: "Wait for payments", ask: "Expiry?"}
      - id: pick-nearby
        release: r1
        status: gap
        card: "Pick a nearby shop"
        questions:
          - {id: q1, ask: "Same id in another story"}
`

export const BLOCK = `journey: review
releases:
- id: r1
  goal: first
steps:
- id: agents
  card: Agents and people
  stories:
  - id: front-door
    release: r1
    status: gap
    card: A short pointer
      wrapped onto a second line
    questions:
    - id: agents-and-people
      ask: What does opening the product page show?
      answer: A browser goes to the product page; an agent asking for markdown gets
        a short pointer, which says what it is and
        links the OpenAPI.
    - id: public-contract
      ask: How does the OpenAPI change once outside agents rely on
        it?
    - id: audience
      status: deferred
      because: Not before the first outside agent.
      ask: Should the OpenAPI split?
  - id: no-questions
    release: r1
    status: gap
    card: Nothing asked here
`

export const footprint = (over = {}) => ({
	schema: 'journey-footprint/v1', id: 'fp:t:1', kind: 'answered', task: 't', journey: 'shop', story: 'enter-by-qr',
	question: 'q1', words: '好，由平台發', date: '2026-10-13', source: 'gate-attempt:t-1', answer: 'Platform issues codes.', ...over,
})
