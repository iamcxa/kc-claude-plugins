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
}) {
	return geo({ id, x, y, w, h, index, parentId, color, fill: 'none', text, size, align, verticalAlign, url })
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

// Child borders preserve story coordinates used by release readback.
export function storyBorder(story) {
	const status = story.meta?.journey?.status
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

export function withStoryStatus(records) {
	const parentId = records.find((r) => r.typeName === 'page').id
	const shapes = records.filter((r) => r.typeName === 'shape')
	const y = Math.min(0, ...shapes.map((s) => s.y)) - 190
	let index = shapes.map((s) => s.index).sort().at(-1) ?? 'a1'
	const legend = []
	for (const [i, [status, color]] of Object.entries(STORY_STATUS_COLORS).entries()) {
		const text = `${status.toUpperCase()}\n${{ exists: 'evidence supported', gap: 'known missing', unverified: 'pending verification' }[status]}`
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
		x: 300, y: y + 100, w: 1120, h: 64, text: 'Story status is not delivery acceptance.', color: 'grey', size: 's', index: getIndexAbove(index) })
	caption.meta = { journey: { kind: 'status-legend-caption', nodeId: 'status-legend' } }
	return [...records, ...shapes.map(storyBorder).filter(Boolean), ...legend, caption]
}
