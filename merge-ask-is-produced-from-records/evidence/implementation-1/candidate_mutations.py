from pathlib import Path
import contextlib, io, json, unittest
from unittest import mock
exec(Path(__file__).with_name("round2_probe.py").read_text().split("if __name__=='__main__':")[0],globals())
rows=[]
for label,old,new,test in [
    ("summary fields", 'missing = [] if observed else summary_round_problems', 'missing = summary_round_problems', 'test_question_only_records_observed_facts_and_no_manual_summary'),
    ("held ask filename", '"ask" if snapshot["result"]["exit"] == 0 else "observation"', '"ask"', 'test_live_held_observation_is_not_a_successful_ask_for_the_merge_audit')]:
    mutant=tests.variant_of(old,new);log=io.StringIO()
    with mock.patch.object(tests,"gate",mutant):
        result=unittest.TextTestRunner(stream=log).run(tests.ObservedFactsTests(test))
    name=label.replace(" ","-")+"-mutation.log";(SCR/name).write_text(log.getvalue())
    assert len(result.failures)>0 and not result.errors,log.getvalue()
    rows.append(dict(mutation=label,detected=True,failures=len(result.failures),errors=len(result.errors),output=name))
for item in json.loads((SCR/"replays.json").read_text())["cases"]:
    root=SCR/("candidate-replay-complete-"+item["task"]);task=root/"workflow/.spacedock-state/task.md";q=root/"question.txt"
    records=list((task.with_suffix("")/"merge").glob("ask-*.json"));path=max(records,key=lambda p:int(p.stem.split("-")[-1]))
    dispatch=gate.dispatched_candidates(task)[1];original=dispatch.read_bytes();dispatch.write_text(original.decode().replace(item["head"],"f"*40))
    out=io.StringIO()
    try:
        with contextlib.redirect_stdout(out):code=gate.main(["question",str(task),"--text-file",str(q),"--facts-record",str(path)])
    finally:dispatch.write_bytes(original)
    assert code==1,out.getvalue()
    rows.append(dict(mutation="dispatched head",case=item["task"],exit=code,output=out.getvalue()))
(SCR/"candidate-mutations.json").write_text(json.dumps(rows,indent=2)+"\n")
