import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import types

root = Path(sys.argv[1])
prior = Path(sys.argv[2])
out = Path(__file__).parent
sys.path.insert(0, str(root / "kc-dev-flow-2/scripts"))
import count_tokens as amended
old = types.ModuleType("prior_count_tokens")
source = subprocess.check_output(["git", "-C", "/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-counts-name-the-run-that-produced-them", "show",
                                 "90f43f801be3d03ebd7d98d1a41ad78801aea54d:kc-dev-flow-2/scripts/count_tokens.py"], text=True)
exec(compile(source, "prior_count_tokens.py", "exec"), old.__dict__)

gate = []
argv = json.loads((out / "gate-replay-argv.json").read_text())
for value in argv[5:]:
    label, repo, revision = value.split("|")
    paths = subprocess.check_output(["git", "-C", repo, "ls-tree", "-r", "--name-only", revision], text=True).splitlines()
    for name in paths:
        if not re.search(r"review/validation/briefing-\d+/index\.json$", name):
            continue
        raw = subprocess.check_output(["git", "-C", repo, "show", revision + ":" + name])
        text = "\n".join(x.get("summary", "") for x in json.loads(raw).get("artifacts", []))
        before = {sentence: values for sentence, values in old.count_sentences(text)}
        after = {sentence: values for sentence, values in amended.count_sentences(text)}
        changed = [dict(sentence=sentence, before=sorted(values), after=sorted(after.get(sentence, set())))
                   for sentence, values in before.items() if values != after.get(sentence, set())]
        if changed:
            gate.append(dict(checkout=label, revision=revision, file=name,
                             sha256=hashlib.sha256(raw).hexdigest(), changes=changed))

learn = []
before = [json.loads(x) for x in (prior / "learn-replay.log").read_text().splitlines()][1:]
after = [json.loads(x) for x in (out / "learn-replay.log").read_text().splitlines()][1:]
for a, b in zip(before, after):
    assert a["store"] == b["store"]
    prior_snapshots, current_snapshots = dict(a["record_snapshots"]), dict(b["record_snapshots"])
    assert all(current_snapshots.get(job) == digest for job, digest in prior_snapshots.items())
    added = sorted(current_snapshots.keys() - prior_snapshots.keys())
    if added:
        drift = json.loads((out / "replay-store-drift.json").read_text())
        assert a["store"] == "qnow" and added == ["afdf39d82ede512b76821cee193a3754254e1854c53f7ef258208f89b86f1c62"]
        assert drift["sha256"] == current_snapshots[added[0]] and drift["state"] == "completed"
        assert all(d["action"] == "no-change" for d in drift["evaluation"]["decisions"])
        assert drift["proposal"] is None
    prior_refused = {x["job"] for x in a["refused"]}
    amended_refused = {x["job"] for x in b["refused"]}
    assert not amended_refused - prior_refused
    learn.append(dict(store=a["store"], prior_snapshots_unchanged=True, added_no_change_records=added,
                      no_longer_refused=sorted(prior_refused - amended_refused), still_refused=sorted(amended_refused)))
assert [job for row in learn for job in row["no_longer_refused"]] == [
    "ed2d3ee114280792035b9f231a95202d61ce3360dddf3bc31a84955474b1d28e"]
assert not amended.count_sentences("cycle 2, round 2")
print(json.dumps(dict(explanation="Captain amendment 2 excludes the identifier following a listed sequence label; real counts in the sentence remain.",
                     gate=gate, learn=learn, comma_defect_absent=True), indent=2))
