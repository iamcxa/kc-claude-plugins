import sys, pathlib
sys.path.insert(0, sys.argv[1])
import delivery_gate as g
task = pathlib.Path(sys.argv[2]); q = pathlib.Path(sys.argv[3]).read_text(); s = pathlib.Path(sys.argv[4]).read_text()
report = (g.VALIDATION_SECTION.findall(task.read_text()) or [""])[-1]
import re
decl = re.findall(r"^Captain steps:[ \t]*(.*)$", s, re.M)[0].strip().strip("`\"")
probs, *_ = g.inspect_steps(pathlib.Path(decl), q + "\n" + s + "\n" + report)
print(len(probs)); [print(" ", p) for p in probs]
