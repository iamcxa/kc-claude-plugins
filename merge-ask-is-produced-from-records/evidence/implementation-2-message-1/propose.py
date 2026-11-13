from pathlib import Path
import difflib,json,subprocess
import investigate as p
root=p.WT/'kc-dev-flow-2';path=root/'scripts/delivery_gate.py';original=path.read_text();candidate=original
helper='''def record_review_question_problems(text, rows, extensions):
    plain = "\\n".join(outside_fences(text))
    problems = []
    if {row["reviewer"] for row in rows} != set(extensions) & {"codex", "copilot", "roborev"}:
        problems.append("configured reviewers differ from the delivery observation")
    for row in rows:
        reviewer, outcome, identity = row["reviewer"], row["outcome"], row.get("evidence")
        if outcome in {"findings", "answered"}:
            decisions = re.findall(rf"^Review decision:[ \\t]*{re.escape(reviewer)}[ \\t]+{re.escape(identity or '')}[ \\t]+(clean|disposed):[ \\t]+(\\S.*)$", plain, re.M | re.I)
            if not identity or len(decisions) != 1 or (outcome == "findings" and decisions[0][0].lower() != "disposed"):
                problems.append(f"{reviewer} needs one FO review decision at {identity or 'a missing evidence identity'}")
        if reviewer == "copilot" and outcome == "not-run":
            if not re.search(r"(?im)^Copilot (?:not read|not run):[ \\t]*\\S", plain):
                problems.append("the question needs the Copilot unread decision")
            if not re.search(r"(?im)^Copilot retry: available when the Captain confirms quota is back\\.[ \\t]*$", plain):
                problems.append("the question needs the conditional Copilot retry offer")
    return problems


'''
anchor='def reviewer_problems(task, task_text, text, second, extensions, title=None, head=None):'
assert candidate.count(anchor)==1
candidate=candidate.replace(anchor,helper+anchor.replace('head=None):','head=None, observations=None):'))
anchor='    if "copilot" in extensions:\n        for skipped in re.finditer'
assert candidate.count(anchor)==1
candidate=candidate.replace(anchor,'''    if observations is not None:
        problems += record_review_question_problems(text, observations, extensions)
        return problems, (["next: hold the ask; record the FO review decision or unread/retry decision in the question."] if problems else [])
    if "copilot" in extensions:
        for skipped in re.finditer''')
anchor='            reviewers = reviewer_facts(repo, number, extensions, str((facts or {}).get("headRefOid", "")))\n'
assert candidate.count(anchor)==1
candidate=candidate.replace(anchor,anchor+'''            found, wanted = reviewer_problems(task, task_text, gate_text, second, extensions, observations=reviewers)
            problems += found
            nexts += wanted
''')
anchor='''            if untriggered and (re.search(r"^profile:[ \\t]*prod[ \\t]*$", task_text, re.M) or re.search(r"^Surfaces:.*\\bdb\\b", task_text, re.M)):
                problems.append("second reviewer not triggered contradicts the structured prod/db trigger")
'''
assert candidate.count(anchor)==1
candidate=candidate.replace(anchor,'')
anchor='''        problems, _ = text_problems(task.read_text(), text, at_gate=True, confirmations=False)
'''
assert candidate.count(anchor)==1
candidate=candidate.replace(anchor,anchor+'''        workflow_dir, scalars, lists = find_readme(task, args.workflow_dir)
        if not workflow_dir:
            raise ValueError("cannot read current reviewer configuration")
        second, extensions = reviewer_config(scalars, lists)
        found, _ = reviewer_problems(task, task.read_text(), text, second, extensions, observations=data["reviewers"])
        problems += found
''')
anchor='        if GRANT.search(text) and (any(not data["head"].startswith(x) for x in re.findall(r"--match-head-commit\\s+([0-9a-f]{7,40})", text))):\n'
assert candidate.count(anchor)==1
candidate=candidate.replace(anchor,'        grants = re.findall(r"--match-head-commit\\s+([0-9a-f]{7,40})\\b", text)\n        if GRANT.search(text) and (not grants or any(not data["head"].startswith(x) for x in grants)):\n')
contract=root/'references/delivery-record.md';old_contract=contract.read_text();new_contract=old_contract.replace('FO still reads findings and applies the workflow\'s disposition rules.\n', '''FO still reads findings and applies the workflow's disposition rules.
Before a passing check, FO writes one `Review decision: <reviewer> <evidence> clean: <judgment>`
or `Review decision: <reviewer> <evidence> disposed: <judgment>` in the question for
`answered` or `findings`; `findings` needs `disposed`. These are head/evidence-bound
FO judgments, not new adapter outcomes or machine proof of a Captain waiver.
A configured second reviewer still needs one trigger declaration or not-triggered declaration.
Both record commands use the shared declaration/decision reader with current
configuration, including quoted prod profiles. A merge-naming question needs a valid 7–40-hex head. An unread Copilot needs a `Copilot not read: <decision>` or
`Copilot not run: <decision>` line and the conditional retry line in the question.
The existing workflow still requires Captain authority for a P1 waiver.
''')
assert new_contract!=old_contract
changes=[('kc-dev-flow-2/scripts/delivery_gate.py',original,candidate),('kc-dev-flow-2/references/delivery-record.md',old_contract,new_contract)]
patch=''.join(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+name,tofile='b/'+name)) for name,a,b in changes)
(p.S/'proposal-not-applied.patch').write_text(patch)
stat=subprocess.run(['git','-C',str(p.WT),'apply','--numstat',str(p.S/'proposal-not-applied.patch')],capture_output=True,text=True,check=True)
check=subprocess.run(['git','-C',str(p.WT),'apply','--check',str(p.S/'proposal-not-applied.patch')],capture_output=True,text=True)
(p.S/'proposal-counts.json').write_text(json.dumps({'kind':'unapplied illustrative proposal, not a repair or tested candidate','numstat':[dict(zip(('added','removed','file'),x.split('\t'))) for x in stat.stdout.splitlines()],'context_check_exit':check.returncode,'context_check_output':check.stdout+check.stderr,'production_delta_applied':{'added':0,'removed':0},'tests':'not authored/applied for the proposed grammar; investigation cases name the required regressions','limits':['Decision syntax is a proposal requiring FO authorization.','A presence check cannot authenticate reviewer reading, per-finding classification, actual repairs or Captain waiver truth.','No new factual record field; question_sha256 binds the FO judgments.','The count includes checker/contract only; future regression-test delta is not measured.']},indent=2)+'\n')
print(stat.stdout,end='')
assert check.returncode==0,check.stderr
assert path.read_text()==original and contract.read_text()==old_contract
