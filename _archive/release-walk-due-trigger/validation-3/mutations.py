import argparse, importlib.util, json, os, shutil, subprocess, sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("root");p.add_argument("evidence");a=p.parse_args()
root=Path(a.root); ev=Path(a.evidence); c=root/".validation-3-consumer"; producer=root/".validation-3-producer"; mut=root/".validation-3-support/mutation"
mut.mkdir()
for name,src in [("kc-dev-flow-2",c),("kc-journey-map",producer),("docs",producer)]:
    paths=subprocess.check_output(["git","-C",str(src),"ls-files",name],text=True).splitlines()
    for path in paths:
        target=mut/path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src/path,target)
os.symlink(producer/"kc-journey-map/node_modules",mut/"kc-journey-map/node_modules",target_is_directory=True)
ra="kc-dev-flow-2/extensions/release-acceptance/release_acceptance.py"
test="kc-dev-flow-2/extensions/release-acceptance/test_release_acceptance.py"
watch="kc-dev-flow-2/scripts/pr_watch.py"; wt="kc-dev-flow-2/scripts/test_pr_watch.py"
results=[]
def probe(name,path,old,new,command):
    file=mut/path;original=file.read_text();assert old in original,(name,old)
    file.write_text(original.replace(old,new,1))
    try:
        done=subprocess.run(command,cwd=mut,capture_output=True,text=True)
        (ev/(name+".log")).write_text(done.stdout+done.stderr)
        assert done.returncode==1 and ("FAIL" in done.stdout+done.stderr or "✖" in done.stdout), (name,done.returncode,done.stdout,done.stderr)
        results.append({"name":name,"status":"passed","message":"Fault rejected with exit 1; "+str(ev/(name+".log")),"command":command})
    finally:file.write_text(original)
try:
    py=[sys.executable,"-B"]
    probe("AC-12-archive-omitted",ra,'"--archived", "--all-fields"','"--all-fields"',py+[test,"DueTests.test_live_commented_and_quoted_task_fields_match_spacedock"])
    probe("F1-F2-raw-fields",ra,'records = due_records(args, env)','records = [task.fields for task in state_tasks(args.workflow_dir)]',py+[test,"DueTests.test_done_status_with_yaml_comment_does_not_hide_due_release","DueTests.test_claim_with_yaml_comment_silences_the_claimed_release","DueTests.test_every_due_frontmatter_value_uses_the_parsed_listing"])
    probe("AC-13-archived-only",ra,'if row.get("status") == "done"','if row.get("status") == "archived"',py+[test,"DueTests.test_recorded_real_progress_exit_one_and_claim_removal"])
    probe("AC-14-unconditional",watch,'if "release-acceptance" in listed:',"if True:",py+[wt,"TasksTests.test_release_walk_due_is_gated_by_listing_and_map_presence"])
    probe("AC-15-exit-one",ra,'done.returncode not in (0, 1)','done.returncode not in (0,)',py+[test,"DueTests.test_recorded_real_progress_exit_one_and_claim_removal"])
    probe("AC-15-ignore-diagnostic",ra,'if result.get("diagnostic") is not None:',"if False:",py+[test,"DueTests.test_producer_failures_are_diagnostic_and_never_due"])
    probe("AC-16-word-cap","kc-dev-flow-2/extensions/release-acceptance/EXTENSION.md","# release-acceptance extension","# release-acceptance extension\n"+"extra "*601,py+[test,"ContractTests.test_extension_md_stays_within_its_word_budget"])
    probe("yaml-literal-id",ra,'scalar if plain else None','scalar',py+[test,"DueTests.test_yaml_journey_scalars_reach_the_producer_without_becoming_literal_ids"])
    probe("spacedock-alias-removed",ra,'directory + os.pathsep + str(binary.parent.resolve())','str(binary.parent.resolve())',py+[test,"DueTests.test_renamed_spacedock_bin_is_executed_instead_of_a_path_decoy"])
    probe("producer-pending-label","kc-journey-map/lib/progress.mjs","'pending delivery acceptance'","'accepted by delivery'",["node","--test","kc-journey-map/lib/schemas.test.mjs"])
    probe("producer-table-unversioned","kc-journey-map/lib/schemas.mjs","['releases',","['deliveries',",["node","--test","kc-journey-map/lib/schemas.test.mjs"])
finally:
    (ev/"mutations.json").write_text(json.dumps(results,indent=2))
    shutil.rmtree(mut)
print(f"PASS: {len(results)} independent mutations rejected")

