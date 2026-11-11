import sys, pathlib, subprocess, json
source=pathlib.Path(sys.argv[1]); evidence=pathlib.Path(sys.argv[2]); sys.path.insert(0,str(source/'kc-dev-flow-2/scripts'))
import test_dispatch_records as t
case=t.LiveValidationRulingTests(); case.setUp()
try:
    report=t.REPORT+'\nREJECTED\n'
    resolution=t.native_ruling(stage='ideation')
    case.new_state(report,resolution)
    a=case.git('rev-parse','HEAD')
    withdrawal=resolution+'          withdrawal:\n            by: person:captain\n            at: 2026-10-30\n            reason: Withdraw prior approval\n'
    case.save(report,withdrawal); b=case.commit('withdraw existing gate after report')
    corrected=report.replace('settle','choose')
    case.save(corrected,withdrawal); c=case.commit('rewrite report after withdrawal')
    case.save(corrected+t.AMENDMENT,withdrawal); d=case.commit('later amendment')
    case.record.write_text(case.record.read_text().replace('Independent verdict','Captain amendment 1; Independent verdict'))
    for name,script in [('tag',source.parent/'replay-original/tag/kc-dev-flow-2/scripts/dispatch_records.py'),('candidate',source/'kc-dev-flow-2/scripts/dispatch_records.py')]:
        p=subprocess.run([sys.executable,'-B',str(script),'--names',str(case.record)],capture_output=True,text=True)
        print(name,'exit='+str(p.returncode),p.stdout.strip() or '<no output>')
    print('native entries:',json.dumps(list(t.records.gate_entries(t.records.split_task(case.task.read_text())[0]))))
    print('timeline:',a,b,c,d)
    saved=evidence/'withdrawal-fixture'; case.shutil.copytree(case.root,saved)
finally:
    case.doCleanups()
