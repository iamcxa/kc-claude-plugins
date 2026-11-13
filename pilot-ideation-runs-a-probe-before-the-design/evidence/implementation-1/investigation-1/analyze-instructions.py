from pathlib import Path
import hashlib,json,difflib,subprocess
s=Path('/tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/implementation-1')
pkg=s/'live/package/kc-dev-flow-2'
rows=[]
def add(source,start,end=None,kind='proof/report instruction'):
    p=(s/source) if source.startswith('live/') or source=='stage-def.regenerated.txt' else pkg/source
    raw=p.read_text(); a=raw.index(start); b=a+len(start) if end is None else raw.index(end,a)+len(end)
    text=' '.join(raw[a:b].split()); line=raw[:a].count('\n')+1
    rows.append(dict(order=len(rows)+1,file=str(p.relative_to(s)),line=line,words=len(text.split()),text=text,kind=kind,order_basis='Declared read order; cold dispatch and scope not recovered.'))
add('live/checklist.txt','Acceptance criteria with reproducible evidence clauses and falsifiers,','what gets worse under it')
add('stage-def.regenerated.txt',"Each criterion's evidence command runs once on it,",'`Not provable now`.')
add('stage-def.regenerated.txt','Current design definition and acceptance criteria','identified for the user.')
add('stage-def.regenerated.txt','Required diagram defects or missing current-stage','unverified future checks do not.')
add('skills/ideation/SKILL.md','Required inputs:','available artifact/evidence.',kind='Input boundary')
add('skills/ideation/SKILL.md','Select the recorded row and read its shared profile principles first,','relevant\nadopted project learning.',kind='Declared loading order')
add('references/profiles/pilot.md','Test owned behavior and real seams rather than stable vendor internals.')
add('skills/ideation/principles.md','Use or repair what exists before','observation in this design.')
add('skills/implementation/principles.md','Before designing or coding a task,','third-party tools it will use.',kind='Linked Before new work; provenance context')
add('skills/implementation/principles.md','In the existing design or report,','changes or replaces it.',kind='Linked Before new work; provenance context')
add('skills/implementation/principles.md','Record the conclusion and observation',kind='unused') if False else None
add('skills/ideation/principles.md','In `### Worth questions`,','what cheap test checks it now.')
add('skills/ideation/principles.md','Use one PRFAQ','acceptance evidence\nplan.')
add('skills/ideation/principles.md','Before reporting, run\n`python3 <package>/scripts/design_surfaces.py','output in the Stage Report.')
add('skills/ideation/principles.md','The gate is not presentable without the','a `- AC-1:` list is not one.')
add('skills/ideation/principles.md','Correct contradictions in depicted or','if blocked, report the concrete gap.')
add('skills/ideation/principles.md','Future implementation checks may remain unverified.')
add('skills/ideation/principles.md','In the existing Stage Report checklist,','honest not-yet-verified statement.')
add('skills/ideation/principles.md','A range such as','a future proof plan is not a passed result.')
add('skills/ideation/profiles/pilot.md','Define the smallest useful end-to-end slice,','acceptance evidence and explicit non-goals.')
add('skills/ideation/profiles/pilot.md','Build the probe as the first paragraph','slice and check the next.')
# Pointer is encountered here; its target's first paragraph is the reused proof rule.
add('skills/implementation/profiles/poc.md','Build the smallest real path','the accepted budget.')
add('skills/implementation/profiles/poc.md','Record observed outcome,','avoid production scaffolding.')
add('skills/implementation/profiles/poc.md','Record `boundary-crossed:`','when it applies.')
add('skills/ideation/profiles/pilot.md','Under `Probe:`','reporting and keep the branch.')
(s/'instructions.json').write_text(json.dumps(rows,indent=2)+'\n')
files=['skills/ideation/SKILL.md','references/profiles/pilot.md','skills/ideation/principles.md','skills/ideation/profiles/pilot.md','skills/implementation/profiles/poc.md']
(s/'file-words.json').write_text(json.dumps([dict(file=p,words=len((pkg/p).read_text().split()),sha256=hashlib.sha256((pkg/p).read_bytes()).hexdigest()) for p in files],indent=2)+'\n')
old="Each criterion's evidence command runs once on it, recording command, exit\nand output path; what cannot run goes under `Not provable now`."
new="For every criterion, including provenance, run its proof once; record command, exit\nand output path beside it; if unrunnable: `Not provable now`."
workflow=(pkg/'references/sd/workflow.md').read_text(); assert workflow.count(old)==1
assert len(old.split())==len(new.split())==22
proposal=dict(file='kc-dev-flow-2/references/sd/workflow.md',line=190,removed=old,added=new,removed_words=22,added_words=22,word_delta=0,workflow_words_before=len(workflow.split()),workflow_words_after=len(workflow.replace(old,new).split()),applied=False)
(s/'proposed-wording.json').write_text(json.dumps(proposal,indent=2)+'\n')
(s/'proposed-wording.diff').write_text(''.join(difflib.unified_diff(workflow.splitlines(True),workflow.replace(old,new).splitlines(True),fromfile='a/'+proposal['file'],tofile='b/'+proposal['file'],n=2)))
print('Saved',len(rows),'source-derived instruction entries, whitespace word counts, and an unapplied 22-for-22-word proposal.')
