// Shared story normalization.
//
// A story is a bare string or an object; every reader of `steps[].stories[]` used to
// re-derive its own id/card/release, and a bare string structurally cannot carry
// `status`, `evidence` or `question` — which is exactly the shape the no-status lint
// has to catch, not paper over.

export const normalizeStory = (step, story, j) =>
	typeof story === 'string'
		? { id: `${step.id}-${j}`, card: story, release: null, status: undefined, evidence: undefined, question: undefined }
		: {
				id: story.id ?? `${step.id}-${j}`,
				card: story.card,
				release: story.release ?? null,
				status: story.status,
				evidence: story.evidence,
				question: story.question,
			}

// Every story in the model, each carrying the step it belongs to.
export const iterStories = (model) =>
	(model.steps ?? []).flatMap((step) => (step.stories ?? []).map((story, j) => ({ step, ...normalizeStory(step, story, j) })))
