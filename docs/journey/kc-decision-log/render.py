#!/usr/bin/env python3
"""Render only index.html from adjacent canonical JSON-syntax YAML. No network/Git."""
from pathlib import Path
import hashlib
import html
import json
import sys
ROOT = Path(__file__).resolve().parent
CSS = '\n:root{color-scheme:light dark;--bg:light-dark(#fbfaf6,#171b20);--fg:light-dark(#202c37,#e3e9ed);--muted:light-dark(#506272,#a8b6c1);--line:light-dark(#c8d0d5,#4b5965);--blue:light-dark(#e2ecf4,#243e50);--green:light-dark(#dfebe1,#263f34);--yellow:light-dark(#fff0b9,#483f23);--focus:light-dark(#145d89,#7ac4ee)}\n*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.65 system-ui,-apple-system,"PingFang TC",sans-serif}main{max-width:1900px;padding:32px;margin:auto}h1{font-size:28px;letter-spacing:.02em;line-height:1.4;margin:0 0 12px}h2{font-size:22px;margin:36px 0 12px}h3{font-size:19px;margin:0 0 8px}p{margin:8px 0 14px;max-width:1080px}small,.muted{color:var(--muted)}a{color:var(--focus)}nav{display:flex;gap:18px;flex-wrap:wrap;margin:16px 0}button,select{font:inherit;padding:8px 12px;color:var(--fg);background:var(--bg);border:1px solid var(--line);border-radius:4px}label{display:flex;align-items:center;gap:10px;flex-wrap:wrap}select{max-width:100%}.toolbar{display:flex;flex-wrap:wrap;gap:14px;align-items:center;margin:20px 0}.flow{color:var(--muted);font-weight:500}.table-wrap{overflow:auto;border-block:1px solid var(--line);margin:16px 0}table{border-collapse:collapse;width:100%;table-layout:fixed;min-width:1600px}th,td{vertical-align:top;text-align:left;padding:12px;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}th:last-child,td:last-child{border-right:0}thead th{background:var(--green);font-size:17px}th .id{display:block;font:13px/1.5 ui-monospace,monospace;color:var(--muted);margin-bottom:4px}.story{background:var(--yellow);padding:12px;margin:0 0 12px;border:2px solid transparent;border-radius:3px;transition:opacity .15s}.story .sid{display:block;color:var(--muted);font:13px/1.5 ui-monospace,monospace;margin-bottom:5px}.story summary{cursor:pointer}.story p{font-size:14px;margin-top:12px}.story.selected{border-color:var(--focus)}.story.dimmed{opacity:.42}.band{background:var(--blue)}.matrix th:first-child{width:170px}.matrix td{font-size:14px}.matrix a{display:block;margin-bottom:5px}.matrix tbody tr:last-child td{border-bottom:0}.slice{padding:24px 0;border-bottom:1px solid var(--line)}.slice-grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}.slice ul{margin:6px 0 18px;padding-left:23px}.tag{font:13px ui-monospace,monospace}.slice-title{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}.slice-title small{font-size:14px}#slice-summary{max-width:1100px;min-height:50px;border-left:3px solid var(--focus);padding-left:12px}.questions{max-width:1100px}.questions details{padding:14px 0;border-bottom:1px solid var(--line)}.questions summary{cursor:pointer;font-weight:500}footer{padding:30px 0;color:var(--muted)}.rules{columns:2;column-gap:40px;padding-left:24px}.rules li{break-inside:avoid;margin-bottom:10px}.story:target{outline:3px solid var(--focus);outline-offset:3px}\n@media(max-width:700px){main{padding:20px 14px}.slice-grid{grid-template-columns:1fr;gap:0}.rules{columns:1}h1{font-size:24px}}\n@media(prefers-reduced-motion:reduce){*{transition:none!important}}\n@media print{main{padding:0}nav,.toolbar{display:none}.table-wrap{overflow:visible}table{min-width:0}thead th{font-size:12px}.story{padding:5px;font-size:11px}.story p{font-size:10px}.story.dimmed{opacity:1}.slice{break-inside:avoid}}\n\n.question{padding:8px 0;border-top:1px solid var(--line);font-size:13px}.question summary{font-weight:600}.effort{padding:18px;border:1px solid var(--focus)}.effort table{min-width:600px;table-layout:auto}.release-label{font-weight:700;color:var(--focus)}'

def esc(x): return html.escape(str(x), quote=True)
def link(href,label): return '<a href="'+esc(href)+'">'+esc(label)+'</a>'
def check(j,p):
    stories=[s for a in j['steps'] for s in a['stories']]
    ids=[s['id'] for s in stories]
    assert len(j['steps'])==8 and len(ids)==len(set(ids))==28
    assert len(j['rules'])==9
    p1=['S01','S02','S04','S10','S11']
    assert sorted(s['id'] for s in stories if s.get('release')=='P1')==p1
    assert j['releases'][0]['id']=='P1'
    assert p['slices'][0]['story_ids']==p1 and len(p['slices'])==6
    membership=[x for sl in p['slices'] for x in sl['story_ids']]
    deferred=[x['story_id'] for x in p['deferred']]
    assert len(membership+deferred)==len(set(membership+deferred))==28
    assert set(ids)==set(membership+deferred) and 'S17' in deferred
    qs=[q for s in stories for q in s.get('questions',[])]
    assert len(qs)==len({q['id'] for q in qs})==35
    assert all(not {'status','evidence'}.intersection(s) for s in stories)
    assert all((ROOT / q['doc'].split('#')[0]).is_file() for q in qs)
    return stories

def effort(p):
    e=p['effort_proposal']; low,high=e['active_engineering_hours'].values()
    parts=['<aside class="effort" id="p1-contract"><h2>P1四包技術契約與估工提案</h2>',
      '<p><strong>尚未實作／驗證，未接受API。</strong>仍是S01、S02、S04、S10、S11五故事／三端／Pilot；31技術主題已有草案，Gap仍在。</p>',
      '<p><strong>完整P1：32–48 active工程小時；風險40–64h。</strong>含跨包整合、Pilot驗收重跑與一次修正；未經同類交付校準。先前原話「1-3天」保留，本輪已明確「三個完整工作日」／上限3 days，正式estimate=null、fit unknown。8h/工作天只作我方換算（4–6／風險5–8工作天），24h不是人類原話或承諾。</p>',
      '<p>三個完整工作日已確認，不再視日曆日為待選。若我方假設3×8h=24h，估量不支持該假設下完整P1可交；正式fit仍unknown，不倒推三日可交、自增預算或默縮故事。</p>',
      '<div class="table-wrap"><table><thead><tr><th>契約包</th><th>P1故事</th><th>具體提案</th><th>工程小時</th></tr></thead><tbody>']
    for g in e['packages']:
        parts.append('<tr><td>'+link('p1-technical-contract.md',g['id']+' '+g['name'])+'</td><td>'+', '.join(link('#'+x,x) for x in g['stories'])+'</td><td>'+esc(g['summary'])+'</td><td>'+esc(str(g['hours'][0])+'–'+str(g['hours'][1]))+'</td></tr>')
    parts+=['<tr><td>跨包整合／Pilot收尾</td><td>五故事</td><td>整合、驗收重跑與一次修正；不重複計算局部驗證</td><td>6–9</td></tr></tbody></table></div>',
      '<p>Claude正常工作階段本人發起唯讀Git原回執仍pending（非denied）；dot→已授權delegated local task已有命令鏈基礎，不要求前端直接shell。macOS兩已知檔4個read-deny cases只證局部機制，完整query／Git helpers／objects／aliases隔離與三端CLI仍待產品驗證，不要求使用者先供成品。</p>',
      '<p><strong>沿原生dev2：</strong>lint整體有錯為check fail但不改任何ADR Status；read/list保留安全原文與raw Status。effective僅非權威查詢，撤回整binding一律unresolved規則；循環／同key多Accepted不是原生格式錯。</p>',
      '<p>'+link('p1-technical-contract.md#native-dev2-alignment','原生ADR機制對齊')+' · '+link('p1-technical-contract.md','完整技術契約／31問題指向')+' · '+link('p1-estimate.md','估工依據／風險與fit')+'</p></aside>']
    return '\n'.join(parts)

def render(j,p,stories):
    acts=j['steps']; membership={x:sl['id'] for sl in p['slices'] for x in sl['story_ids']}; deferred={x['story_id'] for x in p['deferred']}
    h=['<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
       '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; script-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'">',
       '<title>kc-decision-log｜CLI故事與切片</title><style>'+CSS+'</style></head><body><main>',
       '<header><p class="flow">KC-DECISION-LOG / CLI-FIRST DESIGN PROPOSAL</p><h1>從同一份裁示，到可追溯的協作</h1>',
       '<p><strong>D5 CLI優先方向已接受；本PR為規劃設計；CLI未實作／部署，非ready handoff。</strong>P1五故事／Pilot已選，其他五片仍候選。卡片與AC是設計意圖，不是實作進度。</p>',
       '<p>本機設計投影；雲端 kc-decision-log-design 同步待受支援入口。未做視覺runtime驗證。</p>',
       '<nav aria-label="討論導覽">'+''.join(link(x,y) for x,y in [('#story-map','完整故事'),('#p1-contract','P1契約與估工'),('#slice-map','切片地圖'),('#slice-details','逐片驗收'),('#rules','規則'),('README.md','文件入口'),('cli-first-design.md','CLI設計')])+'</nav></header>',
       '<p>'+esc(j['persona'])+'</p><p>'+esc(j['one_journey'])+'</p>',effort(p),
       '<section id="story-map"><h2>8活動／28故事</h2><p>點開卡片可看detail；P1卡片另含35題的Fact／Gap答案與對應技術草案。</p>']
    options='<option value="all">完整旅程</option>'+''.join('<option value="'+esc(sl['id'])+'">'+esc(sl['id']+' · '+sl['name']+('（已選）' if sl['id']=='P1' else '（候選）'))+'</option>' for sl in p['slices'])+'<option value="deferred">明示延後</option>'
    h+=['<div class="toolbar"><label for="slice-select">強調切片<select id="slice-select">'+options+'</select></label><button id="expand" type="button" aria-pressed="false">展開全部故事細節</button></div><p id="slice-summary" aria-live="polite">P1已選；其餘切片候選，S03／S12／S17／S28延後。</p>',
        '<div class="table-wrap"><table aria-label="八活動故事地圖"><thead><tr>'+''.join('<th scope="col"><span class="id">'+esc(a['id'])+'</span>'+esc(a['activity'])+'</th>' for a in acts)+'</tr></thead><tbody><tr>']
    for a in acts:
        h.append('<td>')
        for s in a['stories']:
            label=' · 已選P1' if s.get('release')=='P1' else (' · 延後' if s['id'] in deferred else '')
            h.append('<details class="story" id="'+esc(s['id'])+'" data-slice="'+esc(membership.get(s['id'],'deferred'))+'" data-release="'+esc(s.get('release',''))+'"><summary><span class="sid">'+esc(s['id']+label)+'</span>'+esc(s['card'])+'</summary><p>'+esc(s['detail'])+'</p>')
            if s.get('technical_proposal'):h.append('<p>'+link('p1-technical-contract.md','四包技術草案（未實作／驗證）')+' · '+link('p1-estimate.md','P1估工提案')+'</p>')
            for q in s.get('questions',[]):
                h.append('<details class="question" id="'+esc(q['id'])+'"><summary>'+esc(q['id']+' · '+q['ask'])+'</summary><p>'+esc(q['answer'])+'</p><p>'+link(q['doc'],'對應設計／契約')+'</p></details>')
            h.append('</details>')
        h.append('</td>')
    h+=['</tr></tbody></table></div></section><section id="slice-map"><h2>六片地圖</h2><p>建議順序P1 → P2 → P3 → P4a → P4b → P5；順序不等於整片硬依賴，當次必要能力／證據不可跳過。</p>',
       '<div class="table-wrap"><table class="matrix"><thead><tr><th>成果</th>'+''.join('<th>'+esc(a['id']+' '+a['activity'])+'</th>' for a in acts)+'</tr></thead><tbody>']
    for sl in p['slices']:
        h.append('<tr class="slice-row" data-slice="'+esc(sl['id'])+'"><th class="band">'+link('#'+sl['id'],sl['id']+' '+sl['name']+('（已選）' if sl['id']=='P1' else '（候選）'))+'</th>')
        for a in acts:h.append('<td>'+(''.join(link('#'+s['id'],s['id']+' '+s['card']) for s in a['stories'] if s['id'] in sl['story_ids']) or '—')+'</td>')
        h.append('</tr>')
    h.append('<tr><th>明示延後</th>')
    for a in acts:h.append('<td>'+(''.join(link('#'+s['id'],s['id']+' '+s['card']) for s in a['stories'] if s['id'] in deferred) or '—')+'</td>')
    h+=['</tr></tbody></table></div></section><section id="slice-details"><h2>逐片範圍與驗收</h2>']
    for sl in p['slices']:
        h.append('<article class="slice" id="'+esc(sl['id'])+'"><div class="slice-title"><h3>'+esc(sl['id']+' · '+sl['name'])+'</h3><small>'+esc('已選／Pilot' if sl['id']=='P1' else '候選')+' · '+esc('、'.join(sl['story_ids']))+'</small></div><p><strong>成果：</strong>'+esc(sl['outcome'])+'</p><p><strong>沿用：</strong>'+esc(sl['reused'])+'</p>')
        if sl['id']=='P1':h.append('<p><strong>32–48 active工程小時；風險40–64h；正式fit unknown。</strong>'+link('#p1-contract','四包／五故事對應與限制')+' · '+link('p1-technical-contract.md','完整契約草案')+' · '+link('p1-estimate.md','估工')+'</p>')
        h.append('<div class="slice-grid"><div><strong>本片範圍</strong><ul>'+''.join('<li>'+esc(x)+'</li>' for x in sl['scope'])+'</ul><strong>本片不做</strong><ul>'+''.join('<li>'+esc(x)+'</li>' for x in sl['not_doing'])+'</ul></div><div><strong>依賴／待驗前提</strong><ul>'+''.join('<li><strong>'+esc(x['target'])+'</strong>（'+esc(x['kind'])+'）<br>'+esc(x['available'])+'</li>' for x in sl['depends_on'])+'</ul><strong>驗收條件</strong><ul>'+''.join('<li>'+esc(x)+'</li>' for x in sl['acceptance'])+'</ul></div></div><p><strong>移除測試：</strong>'+esc(sl['removal_test'])+'</p></article>')
    h+=['</section><section id="decisions"><h2>已確認方向D1–D5</h2>']
    h += ['<p><strong>'+esc(d['topic'])+'</strong>：'+esc(d['decision'])+'</p>' for d in p['discussion_decisions']]
    h+=['</section><section id="rules"><h2>九項邊界</h2><ul class="rules">']+['<li>'+esc(x['id']+' '+x['text'])+'</li>' for x in j['rules']]+['</ul></section>',
      '<footer><p>唯一編輯來源：'+link('journey.yaml','journey.yaml')+'／'+link('slices-proposal.yaml','slices-proposal.yaml')+'；可讀'+link('story-map.md','故事地圖')+'／'+link('slice-map.md','切片地圖')+'。HTML由'+link('render.py','render.py')+'只生成本頁，不重寫Markdown。</p><p>31技術草案仍待驗證；無ready handoff、三端UAT、正式fit或新增外部動作。前輪審查及handoff僅支持其原來源，不冒用到本次hash。</p></footer></main><script>',
      'const proposals='+json.dumps({x['id']:x['outcome'] for x in p['slices']},ensure_ascii=False)+';',r"""
const picker=document.getElementById('slice-select');const summary=document.getElementById('slice-summary');const storyCards=[...document.querySelectorAll('.story')];
picker.addEventListener('change',()=>{const id=picker.value;for(const card of storyCards){card.classList.toggle('selected',id!=='all'&&card.dataset.slice===id);card.classList.toggle('dimmed',id!=='all'&&card.dataset.slice!==id)}summary.textContent=id==='all'?'P1已選；其他切片候選，S03／S12／S17／S28延後。':id==='deferred'?'延後故事保留全圖；S17不是CLI P3必要成果。':id+' · '+proposals[id]});
const expander=document.getElementById('expand');expander.addEventListener('click',()=>{const open=expander.getAttribute('aria-pressed')!=='true';for(const card of storyCards)card.open=open;expander.setAttribute('aria-pressed',String(open));expander.textContent=open?'收合全部故事細節':'展開全部故事細節'});
</script></body></html>"""]
    (ROOT/'index.html').write_text('\n'.join(h)+'\n')
if __name__=='__main__':
    j=json.loads((ROOT/'journey.yaml').read_text());p=json.loads((ROOT/'slices-proposal.yaml').read_text());stories=check(j,p)
    if '--check' not in sys.argv:render(j,p,stories)
    print('Validated: 8 activities, 28 stories, P1 exact 5, 35 questions, 6 slices, S17 deferred; HTML-only renderer.')
    for n in ['journey.yaml','slices-proposal.yaml']:print(n+' sha256='+hashlib.sha256((ROOT/n).read_bytes()).hexdigest())
