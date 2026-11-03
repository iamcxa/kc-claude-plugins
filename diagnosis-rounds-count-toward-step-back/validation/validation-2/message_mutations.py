import json
from pathlib import Path
import shutil
import sys
import proof

out = proof.OUT
cases = [
    ('shared symptom counter drops follow-ups', 'role_triggers.py',
     'if record and symptom and not symptom.startswith("none"):',
     'if record and not record[3] and symptom and not symptom.startswith("none"):',
     'test_role_triggers.SymptomRoundsTest.test_one_plain_and_two_message_records_remind_then_owe_a_dated_call'),
    ('committed reader drops follow-ups', 'role_triggers.py',
     'if DIAGNOSIS_RECORD.fullmatch(Path(path).name):',
     'if (matched := DIAGNOSIS_RECORD.fullmatch(Path(path).name)) and not matched[3]:',
     'test_role_triggers.SymptomRoundsTest.test_one_plain_and_two_message_records_remind_then_owe_a_dated_call'),
    ('disk reader drops follow-ups', 'dispatch_records.py',
     'if (match := DIAGNOSIS_RECORD.fullmatch(p.name)) and diagnosis_order(match)',
     'if (match := DIAGNOSIS_RECORD.fullmatch(p.name)) and not match[3] and diagnosis_order(match)',
     'test_dispatch_records.SymptomDispatchTests.test_one_plain_and_two_messages_count_at_folder_and_named_dispatch_checks'),
    ('named cutoff ignores message number', 'dispatch_records.py',
     'diagnosis_order(match) <= diagnosis_order(record)', 'int(match[2]) <= int(record[2])',
     'test_dispatch_records.SymptomDispatchTests.test_one_plain_and_two_messages_count_at_folder_and_named_dispatch_checks'),
]
rows = []
for index, (name, file, old, new, test) in enumerate(cases):
    package = proof.WT.parent / '.validation-message-mutants' / str(index) / 'kc-dev-flow-2'
    shutil.copytree(proof.PKG, package, ignore=shutil.ignore_patterns('__pycache__'), dirs_exist_ok=True)
    path = package / 'scripts' / file
    text = path.read_text()
    assert old in text, name
    path.write_text(text.replace(old, new))
    for cache in package.rglob('__pycache__'):
        shutil.rmtree(cache)
    result = proof.run(sys.executable, '-B', '-m', 'unittest', test, cwd=package / 'scripts')
    output = result.stdout + result.stderr
    (out / f'message-mutation-{index}.log').write_text(output)
    assert result.returncode == 1 and 'FAILED (failures=' in output, (name, result.returncode, output)
    rows.append({'name': name, 'status': 'passed', 'message': f'mutant rejected by assertion; message-mutation-{index}.log'})
    print(f'killed: {name}', flush=True)
(out / 'message-mutations.json').write_text(json.dumps(rows, indent=2))
