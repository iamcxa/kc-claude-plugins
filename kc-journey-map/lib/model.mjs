
export const STORY_STATUSES = ['gap', 'unverified', 'exists']
export const QUESTION_STATUSES = ['open', 'answered', 'deferred']

// `question:` is sugar for a one-element list; both authored forms land here. `status:`
// and `because:` are the earlier shapes (pre-`answer:`/`doc:`) — still read so an older
// file does not break. A `deferred` question's `because:` becomes its answer when no
// explicit `answer:` was given: "parked, for this reason" is itself an answer to show,
// not a third state the card needs to distinguish.
const normalizeQuestions = (story, storyId) => {
	const authored = Array.isArray(story.questions)
		? story.questions
		: story.question === undefined || story.question === null
			? []
			: [story.question]
	return authored.map((q, k) => {
		const asked = typeof q === 'string' ? { ask: q } : q
		return {
			id: asked.id ?? `${storyId}-q${k}`,
			ask: asked.ask,
			status: asked.status,
			because: asked.because,
			answer: asked.answer ?? (asked.status === 'deferred' && asked.because ? asked.because : undefined),
			doc: asked.doc,
		}
	})
}

// A question is answered when there is something to show for it — an answer card hangs
// under it, nothing else. A bare legacy `status: answered` with no text or link now
// reads as unanswered: a claim with nothing to show is not a shown answer.
export const isQuestionAnswered = (q) => Boolean(q.answer) || Boolean(q.doc)

export const openQuestions = (story) => (story.questions ?? []).filter((q) => !isQuestionAnswered(q))

export const normalizeStory = (step, story, j) => {
	if (typeof story === 'string') {
		const id = `${step.id}-${j}`
		return { id, card: story, release: null, status: undefined, evidence: undefined, questions: [] }
	}
	const id = story.id ?? `${step.id}-${j}`
	return {
		id,
		card: story.card,
		release: story.release ?? null,
		status: story.status,
		evidence: story.evidence,
		questions: normalizeQuestions(story, id),
	}
}

export const iterStories = (model) =>
	(model.steps ?? []).flatMap((step) => (step.stories ?? []).map((story, j) => ({ step, ...normalizeStory(step, story, j) })))
