from pathlib import Path
import subprocess,sys
s=Path(__file__).parent
cases=[('2 ideation, 1 implementation and 2 validation cycles',2,0),('2 ideation, 1 implementation and 2 validation cycles',3,1),('3 ideation, 1 implementation and 2 validation cycles',3,0),('1 implementation and 2 validation cycles',2,0),('1 implementation and 2 validation cycles',3,1),('two ideation, one implementation and two validation cycles, in one package PR.',3,1)]
for i,(budget,n,expected) in enumerate(cases,1):
 r=subprocess.run([sys.executable,'-B',str(s/'run.py'),f'replay-{i}','bash',str(s/'replay.sh'),str(s/'candidate/kc-dev-flow-2/scripts'),str(s),'merge-ask-holds-missing-clauses',budget,str(n)])
 assert r.returncode==expected,(i,r.returncode,expected)
print('All six replay exits match 0/1/0/0/1/1')
