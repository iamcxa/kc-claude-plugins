import os
from pathlib import Path
import shutil,subprocess,json,os
OUT=Path(os.environ.get('EVIDENCE_ROOT','/tmp/opencode-story-done'));P=Path(os.environ.get('PRODUCT_WT','/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-story-done-reports-release-remaining'));D=Path(os.environ.get('DEV2_WT',str(P.with_name(P.name+'-dev2'))))
ROOT=OUT/'mutants';ROOT.mkdir(exist_ok=True)
results=[]
def run(name, source, rel, old, new, argv):
 dest=ROOT/name
 shutil.copytree(source,dest,dirs_exist_ok=True,ignore=shutil.ignore_patterns('node_modules','__pycache__','.git'))
 if source.name=='kc-journey-map' and not (dest/'node_modules').exists():(dest/'node_modules').symlink_to(source/'node_modules',target_is_directory=True)
 p=dest/rel;s=p.read_text();assert old in s,(name,old);p.write_text(s.replace(old,new,1))
 for cache in dest.rglob('__pycache__'):shutil.rmtree(cache)
 cp=subprocess.run(argv,cwd=dest,capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 (OUT/(name+'.log')).write_text(cp.stdout+cp.stderr)
 results.append({'name':name,'status':'passed' if cp.returncode==1 else 'failed','message':f'mutant exit {cp.returncode}; expected a test failure','mutation':f'{rel}: {old} -> {new}'})
 (OUT/'mutations.json').write_text(json.dumps(results,indent=2)+'\n')
 assert cp.returncode==1,(name,cp.returncode,cp.stdout,cp.stderr)
J=P/'kc-journey-map';K=D/'kc-dev-flow-2'
node=lambda name:['node','--test','--test-name-pattern='+name,'lib/progress.test.mjs']
run('AC2-members-as-declared',J,'lib/progress.mjs','return result\n','if (members.length && done.length === members.length) result.status = "exists"\n\t\treturn result\n',node('archive report'))
run('AC3-declared-members-only',J,'lib/progress.mjs','const members = tasks.filter((t) => key(tuple(t)) === key(identity))','const members = tasks.filter((t) => key(tuple(t)) === key(identity)).filter((t) => t["journey-required-tasks"])',node('filed membership'))
run('AC4-drop-url-rule',J,'lib/progress.mjs','if (url) return `${url[1]}#${url[2]}`','if (false) return `${url[1]}#${url[2]}`',node('filed membership'))
run('AC5-drop-release-only',J,'lib/progress.mjs','...(noStory.length ?','...(false ?',node('report separates'))
run('AC6-unbounded-lists',J,'lib/progress.mjs','rows.slice(0, limit)','rows.slice()',node('report separates'))
run('AC7-silent-failed-read',J,'lib/progress.mjs',"if (progress.diagnostic) throw Object.assign(new Error(progress.diagnostic), { exitCode: 1 })","if (progress.diagnostic) return 'unavailable'",node('archive report'))
run('AC8-remove-version-bump',J,'lib/contract-versions.json','"current": "1.1.0",\n    "versions": {\n      "1.0.0": "c1739','"current": "1.0.0",\n    "versions": {\n      "1.0.0": "c1739',['node','--test','--test-name-pattern=journey-progress registers','lib/schemas.test.mjs'])
run('AC11-unlisted-workflows',K,'scripts/design_surfaces.py','if "journey-map" not in readme_extensions(readme):','if False:',['python3','-B','scripts/test_design_surfaces.py','JourneyStoryTests'])
run('AC11-none-without-reason',K,'scripts/design_surfaces.py','if not named or (named in ("none", "none:") and not re.match(r"^none:[ \\t]*\\S", value)):','if not named:',['python3','-B','scripts/test_design_surfaces.py','JourneyStoryTests'])
run('AC13-skip-story-rule',K,'scripts/design_surfaces.py','errors.extend(check_story_record(path, text, seed))','errors.extend([])',['python3','-B','scripts/test_pr_watch.py','TasksTests.test_real_seed_subprocess_names_a_map_task_missing_its_story_record'])
run('AC15-compare-presence-only',K,'scripts/design_surfaces.py','if (named == "none:" and story) or (named != "none:" and named != story):','if False:',['python3','-B','scripts/test_design_surfaces.py','JourneyStoryTests'])
print(f'{len(results)} mutants rejected')
