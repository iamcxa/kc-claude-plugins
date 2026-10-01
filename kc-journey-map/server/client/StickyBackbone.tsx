import { TLNoteShape, getColorValue, renderPlaintextFromRichText, useEditor, useValue } from 'tldraw'

// Clears tldraw's top menu bar, which sits above this canvas layer.
const PIN_TOP = 52
const STRIP_H = 56

const isActivity = (shape: { type: string; meta: Record<string, unknown> }): shape is TLNoteShape =>
	shape.type === 'note' && (shape.meta.journey as { kind?: string } | undefined)?.kind === 'activity'

export function StickyBackbone() {
	const editor = useEditor()
	const cards = useValue(
		'sticky backbone',
		() => {
			const activities = editor.getCurrentPageShapes().filter(isActivity)
			if (!activities.length) return null
			const colors = editor.getCurrentTheme().colors[editor.getColorMode()]
			const placed = activities.map((shape) => {
				const bounds = editor.getShapePageBounds(shape)!
				const topLeft = editor.pageToViewport({ x: bounds.minX, y: bounds.minY })
				const bottomRight = editor.pageToViewport({ x: bounds.maxX, y: bounds.maxY })
				return {
					id: shape.id,
					text: renderPlaintextFromRichText(editor, shape.props.richText),
					fill: getColorValue(colors, shape.props.color, 'noteFill'),
					left: topLeft.x,
					width: bottomRight.x - topLeft.x,
					bottom: bottomRight.y,
				}
			})
			if (Math.max(...placed.map((card) => card.bottom)) > PIN_TOP + STRIP_H) return null
			return { placed, fontSize: Math.min(13, Math.max(8, 22 * editor.getZoomLevel())) }
		},
		[editor]
	)
	if (!cards) return null
	return (
		<div className="sticky-backbone" style={{ height: PIN_TOP + STRIP_H + 8, fontSize: cards.fontSize }} data-testid="sticky-backbone">
			{cards.placed.map((card) => (
				<div key={card.id} className="sticky-backbone__card" title={card.text} style={{ top: PIN_TOP, height: STRIP_H, left: card.left, width: card.width, background: card.fill }}>
					{card.text}
				</div>
			))}
		</div>
	)
}
