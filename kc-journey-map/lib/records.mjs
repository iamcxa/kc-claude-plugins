import { getIndices } from '@tldraw/utils'


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
