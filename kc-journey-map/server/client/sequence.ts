import { Editor, PageRecordType, createTLStore, defaultBindingUtils, defaultShapeUtils, defaultTools } from 'tldraw'

// Each render adds a comparison page. Native edits on older pages stay intact.
export async function addSequencePage(editor: Editor, input: { source: string; sourcePath: string; name: string }) {
	if (!input || typeof input.source !== 'string' || !/^\s*(?:%%[^\n]*\n\s*)*sequenceDiagram\b/.test(input.source)) {
		throw new Error('Provide a Mermaid sequenceDiagram from a repository .mmd file.')
	}
	if (!input.sourcePath?.endsWith('.mmd') || !input.name?.trim()) throw new Error('Provide sourcePath (.mmd) and a page name.')
	if (editor.getIsReadonly()) throw new Error('The canvas is read-only.')

	const container = document.createElement('div')
	container.className = 'tl-container'
	container.style.cssText = 'position:fixed;left:-10000px;top:0;width:1600px;height:1000px;'
	document.body.appendChild(container)
	const scratch = new Editor({
		store: createTLStore({ shapeUtils: defaultShapeUtils, bindingUtils: defaultBindingUtils }),
		shapeUtils: defaultShapeUtils, bindingUtils: defaultBindingUtils, tools: defaultTools,
		options: { text: editor.getTextOptions() },
		getContainer: () => container,
	})
	try {
		const { createMermaidDiagram } = await import('@tldraw/mermaid')
		await createMermaidDiagram(scratch, input.source, { blueprintRender: { position: { x: 0, y: 0 }, centerOnPosition: false } })
		const content = scratch.getContentFromCurrentPage(scratch.getCurrentPageShapes())
		if (!content?.shapes.length) throw new Error('The sequence produced no native shapes.')
		if (editor.getIsReadonly() || editor.getPages().length >= editor.options.maxPages) throw new Error('The canvas cannot add another page.')
		const names = new Set(editor.getPages().map((page) => page.name))
		const baseName = input.name.trim()
		let name = baseName
		for (let n = 2; names.has(name); n++) name = `${baseName} (${n})`
		const pageId = PageRecordType.createId()
		editor.run(() => {
			editor.createPage({ id: pageId, name, meta: { sequence: { source: input.sourcePath } } })
			editor.setCurrentPage(pageId)
			editor.putContentOntoCurrentPage(content, { preservePosition: true })
		})
		editor.zoomToFit()
		return { pageId, name, sourcePath: input.sourcePath, shapes: content.shapes.length }
	} finally {
		scratch.dispose()
		container.remove()
	}
}
