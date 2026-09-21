
export const STORY_STATUSES = ['gap', 'unverified', 'exists']
export const QUESTION_STATUSES = ['open', 'answered', 'deferred']
export const storyStatusLabel = (status) => STORY_STATUSES.includes(status) ? status.toUpperCase() : 'UNASSESSED'

// `question:` is sugar for a one-element list; both authored forms land here.
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
			status: asked.status ?? 'open',
			because: asked.because,
		}
	})
}

export const openQuestions = (story) => (story.questions ?? []).filter((q) => q.status === 'open')

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
