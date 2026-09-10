import { getIndexAbove, getIndices } from '@tldraw/utils'

// Record factories for agent-authored story maps.
//
// Every default here was read off a shape the tldraw editor created in a browser,
// not written from the docs. That matters for one prop in particular: the editor sets
// a note's `fontSizeAdjustment` to 1, and a note carrying 0 passes schema validation
// and then renders its label at font-size 0px — a blank sticky. The server's PATCH
// validator cannot catch it, so the fix lives here.
//
// A 12-word card at size `m` wraps and shrinks to fit a 200x200 note with growY 0
// (verified in the browser); longer text has not been tried.

export const richText = (text) => ({
	type: 'doc',
	content: String(text)
		.split('\n')
		.map((line) => (line ? { type: 'paragraph', content: [{ type: 'text', text: line }] } : { type: 'paragraph' })),
})

const base = (id, x, y, index, parentId) => ({
	id,
	typeName: 'shape',
	x,
	y,
	rotation: 0,
	index,
	parentId,
	isLocked: false,
	opacity: 1,
	meta: {},
})

export function note({ id, text, x, y, index = 'a1', parentId = 'page:page', color = 'green', size = 'm' }) {
	return {
		...base(id, x, y, index, parentId),
		type: 'note',
		props: {
			color,
			size,
			font: 'draw',
			align: 'middle',
			verticalAlign: 'middle',
			labelColor: 'black',
			growY: 0,
			fontSizeAdjustment: 1,
			url: '',
			scale: 1,
			textLastEditedBy: null,
			richText: richText(text),
		},
	}
}

export function frame({ id, name, x, y, w, h, index = 'a1', parentId = 'page:page' }) {
	return {
		...base(id, x, y, index, parentId),
		type: 'frame',
		props: { w, h, name, color: 'black' },
	}
}

const geo = ({ id, x, y, w, h, index, parentId, color, fill, text, size = 'm', align = 'middle', verticalAlign = 'middle', url = '' }) => ({
	...base(id, x, y, index, parentId),
	type: 'geo',
	props: {
		w,
		h,
		geo: 'rectangle',
		dash: 'draw',
		growY: 0,
		url,
		scale: 1,
		flipX: false,
		flipY: false,
		color,
		labelColor: 'black',
		fill,
		size,
		font: 'draw',
		align,
		verticalAlign,
		richText: richText(text ?? ''),
	},
})

// A release boundary: a thin solid bar drawn across the journey.
export function releaseLine({ id, x, y, w, index = 'a1', parentId = 'page:page', color = 'blue', thickness = 5 }) {
	return geo({ id, x, y, w, h: thickness, index, parentId, color, fill: 'solid' })
}

// An outlined box for a slice name, an ownership band, or a status card.
export function label({
	id,
	text,
	x,
	y,
	w,
	h,
	index = 'a1',
	parentId = 'page:page',
	color = 'blue',
	size = 'm',
	align = 'middle',
	verticalAlign = 'middle',
	url = '',
}) {
	return geo({ id, x, y, w, h, index, parentId, color, fill: 'none', text, size, align, verticalAlign, url })
}

// tldraw draws a shape's `url` as a real anchor inside the shape, and a deep link needs
// only a page: the camera numbers are normalised on arrival. That is enough to walk from
// a release to the board that shows what it is missing.
export const pageLink = (room, pageId) => `http://localhost:3737/?room=${room}&d=v0.0.1.1.${pageId.replace('page:', '')}`

// A geo box does not grow to fit its label — text past the bottom edge is simply drawn
// outside the box. These numbers were measured in the browser on a 300px-wide box at
// size 's': 18px draw font, 24px line box, about 26 characters before it wraps.
const LINE_H = { s: 24, m: 32 }
const CHARS_PER_100PX = { s: 8.7, m: 6.5 }

export function fitHeight(text, width, size = 's', padding = 40) {
	const perLine = Math.max(8, Math.floor((width / 100) * CHARS_PER_100PX[size]))
	const lines = String(text)
		.split('\n')
		.reduce((n, line) => n + Math.max(1, Math.ceil(line.length / perLine)), 0)
	return Math.ceil(lines * LINE_H[size] + padding)
}

// Ascending fractional indexes, from tldraw's own generator.
//
// A hand-rolled two-character run looked right and was not: the leading letter encodes
// how many characters the rest must have, so `a1` validates and `b1` does not — it needs
// `b11`. A run past 61 shapes produced keys the schema rejected, and a test that checked
// only uniqueness and order passed the whole way.
export function indexes(n) {
	return getIndices(n)
}

// Pages are records too. A journey gets one room and two pages: the story map people
// talk over, and the journey board the code is cited on. Same model, different question.
export function page({ id, name, index = 'a1' }) {
	return { id, typeName: 'page', name, index, meta: {} }
}

export const STORY_STATUS_COLORS = { exists: 'green', gap: 'red', unverified: 'violet' }

// Standard child shapes keep portable exports readable without changing a story's
// page parent or direct coordinates, which read.mjs uses for release membership.
export function storyBorder(story) {
	const status = story.meta?.journey?.progress?.status ?? story.meta?.journey?.status
	if (story.type !== 'note' || story.meta?.journey?.kind !== 'story' || !Object.hasOwn(STORY_STATUS_COLORS, status)) return null
	const scale = story.props.scale
	const border = label({ id: `${story.id}-status-border`, parentId: story.id, x: 0, y: 0,
		w: 200 * scale, h: (200 + story.props.growY) * scale, text: '', color: STORY_STATUS_COLORS[status], size: 'xl' })
	border.props.dash = 'solid'
	border.props.scale = scale
	border.isLocked = true
	border.meta = { journey: { kind: 'story-border', nodeId: story.meta.journey.nodeId } }
	return border
}

export function storyProgress(progress, model, story) {
	if (!progress) return undefined
	return (progress.journey === model.journey && progress.stories?.find((s) =>
		s.journey === model.journey && s.release === story.release && s.story === story.id)) ||
		{ status: 'unverified', diagnostic: 'No matching task observation' }
}

export function releaseProgressText(progress, model, releaseId) {
	const release = progress.journey === model.journey && progress.releases?.find((r) => r.release === releaseId)
	return release ? `${release.doneStories}/${release.totalStories} stories development-complete\n${release.acceptance}` : 'Development progress unverified'
}

export function withStoryStatus(records, progress = null) {
	const parentId = records.find((r) => r.typeName === 'page').id
	const shapes = records.filter((r) => r.typeName === 'shape')
	const captionText = progress
		? `DEVELOPMENT PROGRESS — local Spacedock tasks\nObserved: ${progress.observedAt}\nSource: ${progress.source}\nTask completion is not delivery acceptance or proof of usability.${progress.diagnostic ? `\n${progress.diagnostic}` : ''}`
		: 'Story status is not delivery acceptance.'
	const captionH = progress ? fitHeight(captionText, 1120) : 64
	const y = Math.min(0, ...shapes.map((s) => s.y)) - (progress ? 130 + captionH : 190)
	let index = shapes.map((s) => s.index).sort().at(-1) ?? 'a1'
	const legend = []
	for (const [i, [status, color]] of Object.entries(STORY_STATUS_COLORS).entries()) {
		const text = progress
			? { exists: 'DEVELOPMENT COMPLETE\npending delivery acceptance', gap: 'DEVELOPMENT INCOMPLETE\nrequired task work remains', unverified: 'DEVELOPMENT UNVERIFIED\nmapping or observation uncertain' }[status]
			: `${status.toUpperCase()}\n${{ exists: 'evidence supported', gap: 'known missing', unverified: 'pending verification' }[status]}`
		const id = `shape:${parentId.slice(5)}-status-legend-${status}`
		const sample = label({ id, parentId, x: 300 + i * 380, y, w: 360, h: 90, text, color, size: 's', index: index = getIndexAbove(index) })
		sample.meta = { journey: { kind: 'status-legend', nodeId: status } }
		const border = label({ id: `${id}-border`, parentId: id, x: 0, y: 0, w: 360, h: 90, text: '', color, size: 'xl' })
		border.props.dash = 'solid'
		border.isLocked = true
		border.meta = { journey: { kind: 'legend-border', nodeId: status } }
		legend.push(sample, border)
	}
	const caption = label({ id: `shape:${parentId.slice(5)}-status-legend-caption`, parentId,
		x: 300, y: y + 100, w: 1120, h: captionH, text: captionText, color: 'grey', size: 's', index: getIndexAbove(index) })
	caption.meta = { journey: { kind: 'status-legend-caption', nodeId: 'status-legend' } }
	return [...records, ...shapes.map(storyBorder).filter(Boolean), ...legend, caption]
}
