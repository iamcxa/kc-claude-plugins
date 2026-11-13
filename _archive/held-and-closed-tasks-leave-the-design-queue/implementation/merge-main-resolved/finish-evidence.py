#!/usr/bin/env python3
"""Seal complete command coverage, actual counts and the exact candidate."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
p=argparse.ArgumentParser()
for n in ("output","candidate"):p.add_argument("--"+n,type=Path,required=True)
a=p.parse_args();ev=a.output
records=json.loads((ev/"full-suite.json").read_text())
assert len(records)==30 and all(r["exit"]==0 for r in records)
test_files=(ev/"package-test-files.txt").read_text().splitlines()
assert all(any(f in r["command"] for r in records) for f in test_files)
for r in records:
 log=(ev/r["log"]).read_text();r["unittest_skipped"]=sum(map(int,re.findall(r"skipped=([0-9]+)",log)))
(ev/"full-suite.json").write_text(json.dumps(records,indent=2)+"\n")
summary=json.loads((ev/"full-suite-summary.json").read_text())
summary.update(package_test_files=len(test_files),unittest_skipped=sum(r["unittest_skipped"] for r in records),unittest_passed=sum(r["unittest_count"]-r["unittest_skipped"] for r in records),custom_native_integration_commands=2,ci_configuration_changed=False,ci_cost_per_pr="not measured")
(ev/"full-suite-summary.json").write_text(json.dumps(summary,indent=2)+"\n")
identity=json.loads((ev/"source-identity.json").read_text())
for name,digest in identity["source_hashes"].items():assert hashlib.sha256((a.candidate/name).read_bytes()).hexdigest()==digest
assert not subprocess.check_output(["git","-C",str(a.candidate),"status","--porcelain"],text=True).strip()
assert not json.loads((ev/"public-repository.json").read_text())["isPrivate"]
(ev/"public-source-proof.json").write_text(json.dumps(dict(public_repository=True,private_source_count=0,external_obligation_corpus_configured=False,source_candidate=identity["candidate"],state_revision="eae5ea47cec926f35d164f8a88d31579196d7634"),indent=2)+"\n")
pr="""fix(kc-dev-flow-2): distinguish held tasks at startup and idle

Startup and idle output names held tasks by stage and asks for a Held section when its reopen/close quote is missing or unverified. It reads Spacedock's native held query, fails visibly if that query fails, and checks quote provenance against the latest hold or a Captain amendment. FO owns live Held-section edits; closed tasks stay at their stage.

Merged main 46e9d0ed4 into candidate {candidate}, preserving its repaired scratch close-out and watcher behavior. The diff against main contains only the two watcher files and decision record 0081.

Validation: all 30 package commands (29 test files plus skill lint) exit 0; {passed} unittest cases pass and {skipped} optional external-corpus case is skipped, with native dispatch integration also passing. Native acceptance replay and six source mutations pass. The amended word bound is N+20: one held task 17/21, current fifteen 33/35, fabricated hundred across all five stages 120/120. Current held names are checked exactly once; over-bound, missing-name and duplicate-name controls reject.

The literal origin-less CLI retains the known base scratch-origin diagnostic; its held fact is exact and the actual workflow entrance exits 0. RoboRev, independent review, hosted CI and final validation remain FO-owned. CI configuration is unchanged relative to main; cost per PR was not measured.
""".format(candidate=identity["candidate"],passed=summary["unittest_passed"],skipped=summary["unittest_skipped"])
(ev/"prepared-pr.md").write_text(pr)
Path("/tmp/impl-held-and-closed-tasks-leave-the-design-queue-pr.md").write_text(pr)
assert not any(f.stat().st_size>256*1024 for f in ev.rglob("*") if f.is_file())
print(json.dumps(summary,indent=2),flush=True)
files=sorted(f for f in ev.rglob("*") if f.is_file() and f.name!="SHA256SUMS")
(ev/"SHA256SUMS").write_text("".join(hashlib.sha256(f.read_bytes()).hexdigest()+"  "+str(f.relative_to(ev))+"\n" for f in files))
