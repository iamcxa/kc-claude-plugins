export const normalizeStory = (step, story, j) =>
 typeof story === 'string'
  ? { id: `${step.id}-${j}`, card: story, release: null }
  : { id: story.id ?? `${step.id}-${j}`, card: story.card, release: story.release ?? null }
