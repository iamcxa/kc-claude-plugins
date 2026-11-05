import json,os,pathlib,shutil,subprocess,sys
ROOT=pathlib.Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-extension-instruction-check-sees-every-listed-extension/.context/validation-pr787-mutations")
OUT=pathlib.Path("/tmp/pr787-validation")
SOURCE=ROOT/"kc-dev-flow-2/scripts/dispatch_records.py"
original=SOURCE.read_bytes(); text=original.decode()
env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",PR787_CODE_ROOT=str(ROOT))
test="kc-dev-flow-2/scripts/test_dispatch_records.py"
mutations=[
 ("AC-1 line anchor removed","r'^Add to scope notes:","r'Add to scope notes:",[test,"ExtensionInstructionTests.test_every_shipped_instruction_is_read_from_its_extension_file"]),
 ("AC-1 scope-line reader removed","for match in SCOPE_INSTRUCTION.finditer(text):","for match in []:",[test,"ExtensionInstructionTests.test_every_shipped_instruction_is_read_from_its_extension_file"]),
 ("AC-2 local header wrongly selected","bool(PASEO_HEADER.search(header))","True",[test,"ExtensionInstructionTests.test_paseo_requires_the_sentence_for_each_supported_header"]),
 ("AC-2 Claude header excluded","(?:Claude|Codex) via Paseo","(?:Codex) via Paseo",[test,"ExtensionInstructionTests.test_paseo_requires_the_sentence_for_each_supported_header"]),
 ("AC-2 whitespace made exact",'" ".join(paths.split()) in " ".join(text.split())',"paths in text",[test,"ExtensionInstructionTests.test_paseo_requires_the_sentence_for_each_supported_header"]),
 ("AC-3 only first cycles","if not record.is_file() or not spawn:","if not record.is_file() or not spawn or not record.name.endswith('-1.md'):",[test,"ExtensionInstructionTests.test_paseo_checks_later_spawn_records_but_not_messages_or_recovery_records"]),
 ("AC-3 roborev only first cycle","spawn.group(1) == stage)","spawn.group(1) == stage and record.name == f'{stage}-1.md')",[test,"ExtensionInstructionTests.test_a_later_implementation_record_without_the_instruction_is_checked"]),
 ("AC-3 message records selected",r'(ideation|implementation|validation)-[1-9][0-9]*\.md$',r'(ideation|implementation|validation)-[1-9][0-9]*(?:-message-[1-9][0-9]*)?\.md$',[test,"ExtensionInstructionTests.test_paseo_checks_later_spawn_records_but_not_messages_or_recovery_records"]),
 ("AC-4 task frontmatter ignored",'acceptance and record.name == "implementation-1.md"','record.name == "implementation-1.md"',[test,"ExtensionInstructionTests.test_release_acceptance_checks_an_acceptance_tasks_first_implementation_only"]),
 ("AC-4 later cycles selected",'acceptance and record.name == "implementation-1.md"','acceptance and spawn.group(1) == "implementation"',[test,"ExtensionInstructionTests.test_release_acceptance_checks_an_acceptance_tasks_first_implementation_only"]),
 ("AC-5 replay loses Claude records","(?:Claude|Codex) via Paseo","(?:Codex) via Paseo",["/tmp/pr787-validation/replay.py","--batch-only","--mutation"]),
 ("AC-6 diagnostic becomes unparseable",'{record.name}: {name} worker instruction is absent; copy the scope-note instruction of ','{record.name}: instruction for {name} is absent; copy the scope-note instruction of ',["kc-dev-flow-2/scripts/test_laws_check.py","L2Test.test_a_missing_paseo_instruction_is_a_parseable_l2_violation"])
]
rows=[]
try:
 for i,(name,before,after,args) in enumerate(mutations,1):
  assert text.count(before)==1,(name,text.count(before))
  for cache in ROOT.rglob("__pycache__"):shutil.rmtree(cache)
  SOURCE.write_text(text.replace(before,after,1))
  p=subprocess.run(["python3","-B",*args],cwd=ROOT,env=env,capture_output=True,text=True,timeout=120)
  log=OUT/f"mutation-{i}.log";log.write_text(p.stdout+p.stderr)
  expected_failure=p.returncode==1 and ("FAIL" in p.stderr or "AssertionError" in p.stderr)
  rows.append(dict(name=name,status="passed" if expected_failure else "failed",exit=p.returncode,command=["python3","-B",*args],log=str(log),message="Injected defect rejected" if expected_failure else (p.stdout+p.stderr)[-1500:]))
  print(name,p.returncode,flush=True)
  SOURCE.write_bytes(original)
 finally_unused=0
finally:
 SOURCE.write_bytes(original)
readme=ROOT/"kc-dev-flow-2/README.md";old=readme.read_bytes()
allowed={"kc-dev-flow-2/scripts/dispatch_records.py","kc-dev-flow-2/scripts/test_dispatch_records.py","kc-dev-flow-2/scripts/test_laws_check.py"}
def changed():
 return set(subprocess.check_output(["git","-C",str(ROOT),"diff","--name-only","d37c6dc653e0f45d6ca630c2faa6121c0863a57e","--","kc-dev-flow-2"],text=True).splitlines())
assert changed()==allowed
try:
 readme.write_bytes(old+b"\nTemporary validation falsifier.\n")
 got=changed()
 assert got!=allowed and "kc-dev-flow-2/README.md" in got
 rows.append(dict(name="AC-7 forbidden README edit",status="passed",message="Exact three-file whitelist rejects README delta",paths=sorted(got)))
finally:readme.write_bytes(old)
(OUT/"mutations.json").write_text(json.dumps(rows,indent=2))
p=subprocess.run(["python3","-B",test,"ExtensionInstructionTests"],cwd=ROOT,env=env,capture_output=True,text=True)
(OUT/"restored-focused.log").write_text(p.stdout+p.stderr)
assert p.returncode==0
assert subprocess.check_output(["git","-C",str(ROOT),"status","--porcelain"],text=True)==""
assert all(r["status"]=="passed" for r in rows)
print("13 falsifiers rejected; restored exact candidate; focused suite passed.")

