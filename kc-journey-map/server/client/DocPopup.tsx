import { useEffect, useRef, useState } from 'react'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import mermaid from 'mermaid'
import GithubSlugger from 'github-slugger'

mermaid.initialize({ startOnLoad: false, securityLevel: 'strict' })

type DocState =
	| { kind: 'loading' }
	| { kind: 'unavailable'; reason: string }
	| { kind: 'missing-heading'; html: string }
	| { kind: 'ready'; html: string }

export interface DocTarget {
	owner: string
	repo: string
	refAndPath: string
	chapter?: string
	sourceUrl: string
}

async function renderMermaidBlocks(container: HTMLElement) {
	const blocks = container.querySelectorAll<HTMLElement>('pre code.language-mermaid')
	let i = 0
	for (const block of Array.from(blocks)) {
		const id = `popup-mermaid-${Date.now()}-${i++}`
		try {
			const { svg } = await mermaid.render(id, block.textContent ?? '')
			const wrapper = document.createElement('div')
			wrapper.className = 'doc-popup-mermaid'
			wrapper.innerHTML = svg
			block.closest('pre')?.replaceWith(wrapper)
		} catch {
			// leave the code block as text; the rest of the document still renders
		}
	}
}

export function DocPopup({ target, onClose, returnFocusTo }: { target: DocTarget; onClose: () => void; returnFocusTo: HTMLElement | null }) {
	const [state, setState] = useState<DocState>({ kind: 'loading' })
	const dialogRef = useRef<HTMLDialogElement>(null)
	const bodyRef = useRef<HTMLDivElement>(null)
	useEffect(() => {
		const dialog = dialogRef.current
		if (!dialog) return
		dialog.showModal()
		// tldraw's own Escape handling runs on `document.body` (bubble phase) and
		// calls preventDefault() there; since a native <dialog>'s "Escape closes
		// the topmost modal" behavior only fires if defaultPrevented is still
		// false once the whole dispatch finishes, that handler silently
		// suppresses the browser's close. A capture-phase listener on the dialog
		// itself runs ahead of body in bubble order and stops it first.
		const stopEscape = (e: KeyboardEvent) => {
			if (e.key === 'Escape') e.stopPropagation()
		}
		dialog.addEventListener('keydown', stopEscape, true)
		return () => {
			dialog.removeEventListener('keydown', stopEscape, true)
			if (dialog.open) dialog.close()
			// showModal() restores focus to the previously focused element on
			// close per the HTML spec; this is a fallback for when the trigger
			// element itself was removed or replaced while the popup was open.
			returnFocusTo?.focus?.()
		}
	}, [returnFocusTo])

	useEffect(() => {
		let cancelled = false
		setState({ kind: 'loading' })
		const q = new URLSearchParams({ owner: target.owner, repo: target.repo, refPath: target.refAndPath })
		fetch(`/repo-doc?${q}`)
			.then((r) => r.json())
			.then((result: { state: 'ok'; content: string; sha: string } | { state: 'unavailable'; reason: string }) => {
				if (cancelled) return
				if (result.state !== 'ok') {
					setState({ kind: 'unavailable', reason: result.reason })
					return
				}
				const raw = marked.parse(result.content, { async: false }) as string
				const clean = DOMPurify.sanitize(raw, { FORBID_TAGS: ['script'], FORBID_ATTR: ['onerror', 'onload', 'onclick'] })
				if (target.chapter) {
					const slugger = new GithubSlugger()
					const headingMatch = /<h[1-6][^>]*>(.*?)<\/h[1-6]>/gi
					let found = false
					let m: RegExpExecArray | null
					while ((m = headingMatch.exec(clean))) {
						const text = m[1].replace(/<[^>]+>/g, '')
						if (slugger.slug(text) === target.chapter) {
							found = true
							break
						}
					}
					setState(found ? { kind: 'ready', html: clean } : { kind: 'missing-heading', html: clean })
					return
				}
				setState({ kind: 'ready', html: clean })
			})
			.catch((e) => !cancelled && setState({ kind: 'unavailable', reason: String(e) }))
		return () => {
			cancelled = true
		}
	}, [target])

	useEffect(() => {
		if ((state.kind === 'ready' || state.kind === 'missing-heading') && bodyRef.current) {
			renderMermaidBlocks(bodyRef.current)
			if (target.chapter && state.kind === 'ready') {
				const slugger = new GithubSlugger()
				for (const h of Array.from(bodyRef.current.querySelectorAll('h1,h2,h3,h4,h5,h6'))) {
					if (slugger.slug(h.textContent ?? '') === target.chapter) {
						h.scrollIntoView({ block: 'start' })
						break
					}
				}
			}
		}
	}, [state, target.chapter])

	return (
		<dialog
			ref={dialogRef}
			className="doc-popup"
			onCancel={(e) => {
				e.preventDefault()
				onClose()
			}}
			onClick={(e) => {
				if (e.target === dialogRef.current) onClose()
			}}
		>
			<div className="doc-popup-chrome">
				<a href={target.sourceUrl} target="_blank" rel="noopener noreferrer" className="doc-popup-source-link">
					Open on GitHub
				</a>
				<button type="button" onClick={onClose} aria-label="Close">
					Close
				</button>
			</div>
			<div className="doc-popup-body" ref={bodyRef}>
				{state.kind === 'loading' && <p>Loading…</p>}
				{state.kind === 'unavailable' && <p className="doc-popup-unavailable">Document unavailable: {state.reason}</p>}
				{state.kind === 'missing-heading' && (
					<>
						<p className="doc-popup-missing-heading">
							Heading "{target.chapter}" was not found in this document; showing the top of the chapter.
						</p>
						<div dangerouslySetInnerHTML={{ __html: state.html }} />
					</>
				)}
				{state.kind === 'ready' && <div dangerouslySetInnerHTML={{ __html: state.html }} />}
			</div>
		</dialog>
	)
}
