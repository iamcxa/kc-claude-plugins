from pathlib import Path
import contextlib,io,json,os
from unittest import mock
exec(Path(__file__).with_name("round2_probe.py").read_text().split("if __name__=='__main__':")[0],globals())
item=json.loads((SCR/'replays.json').read_text())['cases'][0]
root=SCR/('repair-final-replay-complete-'+item['task']); task=root/'workflow/.spacedock-state/task.md'; q=root/'question.txt'
p=next((gate.task_folder(task)/'merge').glob('ask-*.json'))
buf=io.StringIO()
with contextlib.redirect_stdout(buf): before=gate.main(['question',str(task),'--text-file',str(q),'--facts-record',str(p)])
assert before==0,buf.getvalue()
changed='f'*40
with tests.stubbed(root,head=changed,pr=tests.pr_json(head=changed),files=['kc-dev-flow-2/scripts/delivery_gate.py']), tests.quiet_roles(), mock.patch.object(gate,'reviewer_facts',return_value=[]),contextlib.redirect_stdout(buf):
 code=gate.main(['check',str(task),'--pr','iamcxa/kc-claude-plugins#860','--text-file',str(q),'--record-facts','--workflow-dir',str(root/'workflow')])
assert code==1,buf.getvalue()
with contextlib.redirect_stdout(buf):after=gate.main(['question',str(task),'--text-file',str(q),'--facts-record',str(p)])
assert after==1,buf.getvalue()
(SCR/'results/late-head.log').write_text(buf.getvalue())
(SCR/'results/late-head.json').write_text(json.dumps(dict(initial_question=before,changed_live_head=changed,dispatched_head=item['head'],later_check=code,old_record_question_after_later_hold=after,limit='Mocked provider counterexample; no live PR push/merge. Workflow final --match-head-commit also pins GitHub merge; not executed.'),indent=2))
