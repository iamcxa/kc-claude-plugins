import { getIndexAbove, getIndices } from '@tldraw/utils'


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
			// Zero passes schema validation but renders invisible note text.
			fontSizeAdjustment: 1,
			url: '',
			scale: 1,
			textLastEditedBy: null,
			richText: richText(text),
		},
	}
}

const geo = ({ id, x, y, w, h, index, parentId, color, fill, text, size = 'm', align = 'middle', verticalAlign = 'middle', url = '', dash = 'draw' }) => ({
	...base(id, x, y, index, parentId),
	type: 'geo',
	props: {
		w,
		h,
		geo: 'rectangle',
		dash,
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

export function releaseLine({ id, x, y, w, index = 'a1', parentId = 'page:page', color = 'blue', thickness = 5 }) {
	return geo({ id, x, y, w, h: thickness, index, parentId, color, fill: 'solid' })
}

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
	fill = 'none',
	dash = 'draw',
}) {
	return geo({ id, x, y, w, h, index, parentId, color, fill, text, size, align, verticalAlign, url, dash })
}

// tldraw normalizes deep-link camera bounds; the page ID is sufficient.
export const pageLink = (room, pageId) => `http://localhost:3737/?room=${room}&d=v0.0.1.1.${pageId.replace('page:', '')}`

// Geo labels do not auto-grow; these text metrics were measured at 300px, size s.
const LINE_H = { s: 24, m: 32 }
const CHARS_PER_100PX = { s: 8.7, m: 6.5 }

export function fitHeight(text, width, size = 's', padding = 40) {
	const perLine = Math.max(8, Math.floor((width / 100) * CHARS_PER_100PX[size]))
	const lines = String(text)
		.split('\n')
		.reduce((n, line) => n + Math.max(1, Math.ceil(line.length / perLine)), 0)
	return Math.ceil(lines * LINE_H[size] + padding)
}

// Fractional-index keys encode length; hand-built sequences can fail schema validation.
export function indexes(n) {
	return getIndices(n)
}

export function page({ id, name, index = 'a1' }) {
	return { id, typeName: 'page', name, index, meta: {} }
}

export const STORY_STATUS_COLORS = { exists: 'green', gap: 'red', unverified: 'violet' }

export const QUESTION_STATUS_COLORS = { open: 'violet', answered: 'green', deferred: 'grey' }

// A native arrow, bound at both ends. Coordinates are the placeholder tldraw's own
// ExtractBindings migration leaves once a terminal is bound — the editor resolves the
// real path from the bound shapes, not from start/end.
export function connector({ id, index = 'a1', parentId = 'page:page', color = 'grey' }) {
	return {
		...base(id, 0, 0, index, parentId),
		type: 'arrow',
		props: {
			kind: 'arc',
			labelColor: 'black',
			color,
			fill: 'none',
			dash: 'draw',
			size: 's',
			arrowheadStart: 'none',
			arrowheadEnd: 'arrow',
			font: 'draw',
			start: { x: 0, y: 0 },
			end: { x: 0, y: 0 },
			bend: 0,
			richText: richText(''),
			labelPosition: 0.5,
			scale: 1,
			elbowMidPoint: 0.5,
		},
	}
}

// Binding records are separate from the arrow shape; both terminals must be removed
// together or a stale binding outlives the shapes it once pointed at.
export function connectorBindings(connectorId, fromShapeId, toShapeId) {
	return [
		{ id: `binding:${connectorId}-from`, typeName: 'binding', type: 'arrow', fromId: connectorId, toId: fromShapeId,
			meta: {}, props: { terminal: 'start', normalizedAnchor: { x: 0.5, y: 0.5 }, isExact: false, isPrecise: false, snap: 'none' } },
		{ id: `binding:${connectorId}-to`, typeName: 'binding', type: 'arrow', fromId: connectorId, toId: toShapeId,
			meta: {}, props: { terminal: 'end', normalizedAnchor: { x: 0.5, y: 0.5 }, isExact: false, isPrecise: false, snap: 'none' } },
	]
}

// Child borders preserve story coordinates used by release readback.
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

// legend: false lets a caller draw its own status-border legend (the journey board
// folds it into one top-left legend alongside its card colours) without losing the
// status border itself, which every story still needs regardless of who explains it.
export function withStoryStatus(records, progress = null, { legend: showLegend = true } = {}) {
	const parentId = records.find((r) => r.typeName === 'page').id
	const shapes = records.filter((r) => r.typeName === 'shape')
	const borders = shapes.map(storyBorder).filter(Boolean)
	if (!showLegend) return [...records, ...borders]
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
	return [...records, ...borders, ...legend, caption]
}
