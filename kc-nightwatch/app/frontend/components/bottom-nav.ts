import { html } from 'htm/preact'

type Page = 'dashboard' | 'runs' | 'health' | 'config'

interface Props {
  current: Page
}

export function BottomNav({ current }: Props) {
  const tabStyle = (page: Page) => `
    flex:1;
    display:flex;
    align-items:center;
    justify-content:center;
    height:100%;
    color:${current === page ? 'var(--accent)' : 'var(--muted)'};
    border-top:2px solid ${current === page ? 'var(--accent)' : 'transparent'};
    text-decoration:none;
    font-size:14px;
    font-weight:${current === page ? '600' : '400'};
  `

  return html`
    <nav style="position:fixed;bottom:0;left:0;right:0;height:48px;background:var(--panel);border-top:1px solid var(--border);display:flex;z-index:50;">
      <a href="#/dashboard" style="${tabStyle('dashboard')}">Dashboard</a>
      <a href="#/runs" style="${tabStyle('runs')}">Runs</a>
      <a href="#/health" style="${tabStyle('health')}">Health</a>
      <a href="#/config" style="${tabStyle('config')}">Config</a>
    </nav>
  `
}
