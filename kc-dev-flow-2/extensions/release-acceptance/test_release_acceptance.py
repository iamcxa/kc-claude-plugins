import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
REPO = PACKAGE.parent
spec = importlib.util.spec_from_file_location("release_acceptance", HERE / "release_acceptance.py")
ra = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ra)
sys.path.insert(0, str(PACKAGE / "scripts"))
import delivery_gate  # noqa: E402

STORIES = ["reserve-copy", "check-ready", "collect-book"]
PNG = b"\x89PNG\r\n\x1a\n"
DEFERRED = ["t-collect-a#declined-1", "t-ready#F1", "t-reserve#F1"]


def put(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(obj, bytes):
        path.write_bytes(obj)
    else:
        path.write_text(obj if isinstance(obj, str) else json.dumps(obj, indent=2))


def read(path):
    return json.loads(Path(path).read_text())


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = ra.main([str(a) for a in argv])
        except SystemExit as exit_:
            code = exit_.code
    return code, out.getvalue() + err.getvalue()


def task_file(fields, body=""):
    return "---\n" + "".join(f"{k}: {v}\n" for k, v in fields.items()) + "---\n\n" + body


def validation(*bullets, older=()):
    old = "## Stage Report: validation\n\n" + "".join(f"- {b}\n" for b in older) + "\n### Summary\n\nold\n\n" if older else ""
    return old + "## Stage Report: validation (cycle 2)\n\n" + "".join(f"- {b}\n" for b in bullets) + "\n### Summary\n\nnew\n"


def walk_list():
    return {
        "schema": "release-walk/v1", "journey": "book-pickup", "persona": "A reader.",
        "release": {"id": "r1", "name": "RELEASE 1", "goal": "A reader can reserve a book, check readiness and collect it."},
        "source": {"file": "journey.yaml", "commit": "a" * 40},
        "proof_line": "A reader can reserve a book, check readiness and collect it.",
        "stories": [{"order": i + 1, "id": s, "card": s} for i, s in enumerate(STORIES)],
    }


def story(sid, result, complaints=(), cause=None):
    row = {"id": sid, "result": result, "entry": "home page", "evidence": ["shot.png"], "complaints": list(complaints)}
    if cause:
        row["cause"] = cause
    return row


def complaint(cid, stories, rank):
    return {"id": cid, "stories": stories, "rank": rank, "seen": f"what {cid} saw", "evidence": ["shot.png"]}


def reviewer_o():
    return {
        "reviewer": {"id": "o", "model": "opus", "persona": "impatient first-timer"},
        "stories": [story("reserve-copy", "works", ["o2"]), story("check-ready", "broken", ["o1"]), story("collect-book", "works")],
        "proof_line": {"result": "broken", "evidence": [], "cause": ""},
        "complaints": [complaint("o1", ["check-ready"], 1), complaint("o2", ["reserve-copy"], 2), complaint("o3", [], 3)],
        "deferred_verdicts": [{"item": "t-ready#F1", "verdict": "agree", "why": "saw it"},
                              {"item": "t-reserve#F1", "verdict": "disagree", "why": "blocks me"},
                              {"item": "t-collect-a#declined-1", "verdict": "agree", "why": "fine"}],
        "would_miss": "a keyboard-only path", "recommend": "fix check-ready first",
    }


def reviewer_s():
    return {
        "reviewer": {"id": "s", "model": "sonnet", "persona": "keyboard-only power user"},
        "stories": [story("reserve-copy", "works", ["s2"]), story("check-ready", "broken", ["s1"]),
                    story("collect-book", "missing-entry-point", ["s3"])],
        "proof_line": {"result": "broken", "evidence": [], "cause": ""},
        "complaints": [complaint("s1", ["check-ready"], 1), complaint("s2", ["reserve-copy"], 2),
                       complaint("s3", ["collect-book"], 1), complaint("s4", [], 4)],
        "deferred_verdicts": [{"item": "t-ready#F1", "verdict": "agree", "why": "same"},
                              {"item": "t-reserve#F1", "verdict": "agree", "why": "same"},
                              {"item": "t-collect-a#declined-1", "verdict": "cannot-tell", "why": "no picture"}],
        "would_miss": "mouse paths", "recommend": "add a collect link",
    }


def sonnet_ruling():
    def item(iid, src, stories, real, ruling, cls, **extra):
        base = {"id": iid, "from": src, "stories": stories, "real": real, "ruling": ruling, "class": cls, "why": f"why {iid}"}
        base.update(extra)
        return base
    return {
        "items": [
            item("i1", ["o1", "s1"], ["check-ready"], "yes", "solve", "defect", how="fix the status read", when="this-round"),
            item("i2", ["o2", "s2"], ["reserve-copy"], "yes", "solve", "works-but-unusable", how="move the action above the fold",
                 when="next-release", release="r2"),
            item("i3", ["s3"], ["collect-book"], "yes", "solve", "defect", how="add the collect link", when="this-round",
                 sides=[{"reviewer": "o", "position": "works", "picked": False, "why": "no entry in the picture"},
                        {"reviewer": "s", "position": "missing-entry-point", "picked": True, "why": "picture shows none"}]),
            item("i4", ["s4"], [], "unverified", "decision", "not-defect"),
            item("i5", ["o3"], [], "yes", "do-not-solve", "polish"),
        ],
        "deferred": [
            {"item": "t-collect-a#declined-1", "ruling": "do-not-solve", "how": "", "when": "never", "why": "settled"},
            {"item": "t-ready#F1", "ruling": "do-not-solve", "how": "", "when": "never", "why": "settled"},
            {"item": "t-reserve#F1", "ruling": "solve", "how": "move it", "when": "later", "release": "r3", "why": "real"},
        ],
        "tasks": [{"title": "Fix check-ready and the reserve action", "scope": "both", "after": [], "from_items": ["i1", "i2"]},
                  {"title": "Add the collect link", "scope": "one", "after": ["Fix check-ready and the reserve action"], "from_items": ["i3"]}],
    }


def build_world(root, with_walk=True):
    """A workflow with split-root state, tasks of release r1 and r2, and one acceptance task folder with a walk."""
    wf = Path(root) / "wf"
    state = wf / ".spacedock-state"
    put(wf / "README.md", "---\nentity-type: task\nstate: .spacedock-state\n---\n")
    base = {"journey": "book-pickup", "journey-release": "r1", "profile": "pilot"}
    put(state / "t-reserve.md", task_file({**base, "journey-story": "reserve-copy"},
        validation("F1 Polish: the reserve button label is long", older=["F9 Deferred risk: an old finding"])))
    put(state / "t-reserve/dispatch/ideation-1.md", "Dispatched: x\nModel: opus\n")
    put(state / "_archive/t-ready.md", task_file({**base, "journey-story": "check-ready"},
        validation("F1 Deferred risk: ready can read stale")))
    put(state / "_archive/t-ready/dispatch/ideation-1.md", "Model: sonnet\n")
    put(state / "t-collect-a.md", task_file({**base, "journey-story": "collect-book"},
        validation("declined: host component Button at x.d.ts: no such prop")))
    put(state / "t-collect-b.md", task_file({**base, "journey-story": "collect-book", "profile": "poc"}, validation()))
    put(state / "t-other.md", task_file({**base, "journey-release": "r2", "journey-story": "x"}, validation("F1 Deferred risk: other release")))
    put(state / "r1-acceptance.md", task_file({"journey": "", "release-acceptance": "book-pickup/r1"}, validation("F1 Deferred risk: self")))
    folder = state / "r1-acceptance"
    if with_walk:
        write_walk(folder)
    return wf, folder


def write_walk(folder, reviewers=None, ruling=None):
    walk = Path(folder) / "walk"
    put(walk / "walk.json", walk_list())
    put(walk / "shot.png", PNG)
    put(walk / "smoke.json", {"result": "passed", "check": "reserve then collect; fails on an empty vault", "evidence": ["shot.png"]})
    put(walk / "meta.json", {"target": {"environment": "staging", "ref": "abc"}, "diversity": {"mode": "multi-model"},
                             "not_tested": ["resize"], "data_left": ["one reservation"]})
    for r in reviewers or [reviewer_o(), reviewer_s()]:
        put(walk / f"reviewer-{r['reviewer']['id']}.json", r)
    put(walk / "ruling-sonnet.json", ruling or sonnet_ruling())


def pipeline(folder, wf, prior=None):
    """escalate, write an opus ruling that repeats the listed entries with the escalation's own reasons, build."""
    walk = Path(folder) / "walk"
    code, out = run("escalate", folder, "--workflow-dir", wf)
    assert code == 0, out
    listed = [m.group(1) for m in re.finditer(r"^escalate (\S+):", out, re.M)]
    sonnet = read(walk / "ruling-sonnet.json")
    opus = {"items": [i for i in sonnet["items"] if i["id"] in listed],
            "deferred": [d for d in sonnet["deferred"] if d["item"] in listed],
            "tasks": [t for t in sonnet["tasks"] if set(t["from_items"]) <= set(listed)]}
    put(walk / "ruling-opus.json", opus)
    args = ["build", folder, "--workflow-dir", wf] + (["--prior", prior] if prior else [])
    return run(*args), out


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.wf, self.folder = build_world(self.tmp.name)
        self.walk = self.folder / "walk"

    def check(self, tier="walk", prior=None):
        args = ["check", self.folder, "--tier", tier, "--workflow-dir", self.wf] + (["--prior", prior] if prior else [])
        return run(*args)

    def built(self):
        (code, out), _ = pipeline(self.folder, self.wf)
        self.assertEqual(code, 0, out)
        return read(self.walk / "report.json")

    def edit_reviewer(self, who, fn):
        path = self.walk / f"reviewer-{who}.json"
        data = read(path)
        fn(data)
        put(path, data)

    def edit_report(self, fn):
        data = read(self.walk / "report.json")
        fn(data)
        put(self.walk / "report.json", data)

    def refused(self, tier, needle):
        code, out = self.check(tier)
        self.assertEqual(code, 1, out)
        self.assertIn(needle, out)
        return out


class RoutingTests(Base):
    def test_routes_one_owner_two_owners_and_no_story(self):
        self.built()
        code, out = self.check("final")
        self.assertEqual(code, 0, out)
        self.assertIn("route i1: t-ready", out)
        self.assertIn("route i2: t-reserve", out)
        self.assertIn("route i3: review-release", out)
        self.assertIn("route i4: bug task, no story", out)

    def test_removing_one_of_two_owners_changes_the_route(self):
        self.built()
        (self.wf / ".spacedock-state/t-collect-b.md").unlink()
        self.assertIn("route i3: t-collect-a", self.check("final")[1])

    def test_no_owner_at_all_routes_to_review_release(self):
        self.built()
        for name in ("t-collect-a.md", "t-collect-b.md"):
            path = self.wf / ".spacedock-state" / name
            path.write_text(path.read_text().replace("journey-story: collect-book", "journey-story: elsewhere"))
        self.assertIn("route i3: review-release", self.check("final")[1])


class EnvironmentTests(Base):
    def morning(self):
        for who in ("o", "s"):
            def fn(data, who=who):
                data["stories"] = [story(s, "not-reachable", [f"{who}m"], cause="the login stops at an unknown code") for s in STORIES]
                data["complaints"] = [complaint(f"{who}m", [], 1)]
                data["proof_line"] = {"result": "not-reachable", "evidence": [], "cause": "the login stops at an unknown code"}
            self.edit_reviewer(who, fn)

    def test_every_row_not_reachable_is_an_environment_block_not_a_defect(self):
        self.morning()
        code, out = self.check("walk")
        self.assertEqual(code, 1)
        self.assertIn("fewer than two reviewers operated the product", out)
        self.assertIn("Captain decision: environment (the login stops at an unknown code)", out)
        self.assertNotIn("route ", out)
        self.assertIn("clean: no", out)

    def test_one_reviewer_who_operated_changes_the_count(self):
        self.morning()
        self.edit_reviewer("o", lambda d: d["stories"][0].update(result="works", cause=None))
        self.assertIn("reviewers who did: 1", self.check("walk")[1])


class MalformedTests(Base):
    def case(self, who, fn, needle):
        self.edit_reviewer(who, fn)
        self.refused("walk", needle)

    def test_story_missing_duplicated_unknown(self):
        self.case("o", lambda d: d["stories"].pop(), "walk story collect-book missing")
        self.setUp()
        self.case("o", lambda d: d["stories"].append(copy.deepcopy(d["stories"][0])), "walk story reserve-copy duplicated")
        self.setUp()
        self.case("o", lambda d: d["stories"][0].update(id="no-such"), "story no-such is not on the walk")

    def test_result_outside_the_four(self):
        self.case("o", lambda d: d["stories"][0].update(result="fine"), "result 'fine' is not one of")

    def test_not_reachable_needs_a_cause(self):
        self.case("o", lambda d: d["stories"][0].update(result="not-reachable", complaints=["o1"], cause=None), "not-reachable names no cause")

    def test_non_works_needs_a_complaint(self):
        self.case("o", lambda d: d["stories"][1].update(complaints=[]), "broken names no complaint")

    def test_works_needs_evidence(self):
        self.case("o", lambda d: d["stories"][0].update(evidence=[]), "works with no evidence")

    def test_complaint_id_must_be_defined(self):
        self.case("o", lambda d: d["stories"][1].update(complaints=["zz"]), "complaint id 'zz' is not defined")

    def test_proof_line_must_be_present(self):
        self.case("o", lambda d: d.pop("proof_line"), "proof line is absent")

    def test_evidence_outside_the_walk_folder_is_refused(self):
        outside = self.tmp_path / "outside.png"
        outside.write_bytes(PNG)
        self.case("o", lambda d: d["stories"][0].update(evidence=["../../../../outside.png"]), "outside.png is not a file")
        self.setUp()
        self.case("o", lambda d: d["stories"][0].update(evidence=[str(outside)]), "outside.png is not a file")

    @property
    def tmp_path(self):
        return Path(self.tmp.name)

    def test_one_reviewer_id_reported_twice_is_refused(self):
        other = reviewer_s()
        other["reviewer"]["id"] = "o"
        other["complaints"] = [dict(c, id=f"x{c['id']}") for c in other["complaints"]]
        for r in other["stories"]:
            r["complaints"] = [f"x{c}" for c in r["complaints"]]
        put(self.walk / "reviewer-s.json", other)
        self.refused("walk", "reviewer id 'o' appears 2 times")

    def test_evidence_must_be_a_file(self):
        self.case("o", lambda d: d["stories"][0].update(evidence=["gone.png"]), "evidence gone.png is not a file")

    def test_duplicate_complaint_id_across_reviewers(self):
        self.case("s", lambda d: d["complaints"][0].update(id="o1"), "complaint id 'o1' used 2 times")

    def test_schema_string_and_consolidation_are_checked_on_the_report(self):
        self.built()
        self.edit_report(lambda r: r.update(schema="release-acceptance/v2"))
        self.refused("final", "is not release-acceptance/v1")
        self.built()
        self.edit_report(lambda r: r["stories"][1].update(result="works"))
        self.refused("final", "stories[].result differs from the most severe result")

    def test_report_stories_missing_duplicated_unknown(self):
        self.built()
        self.edit_report(lambda r: r["stories"].pop())
        self.refused("final", "stories[]: walk story collect-book missing")
        self.built()
        self.edit_report(lambda r: r["stories"].append(copy.deepcopy(r["stories"][0])))
        self.refused("final", "stories[]: walk story reserve-copy duplicated")
        self.built()
        self.edit_report(lambda r: r["stories"][0].update(id="no-such"))
        self.refused("final", "stories[]: story no-such is not on the walk")

    def test_walk_list_schema_other_than_v1_is_refused(self):
        put(self.walk / "walk.json", {**walk_list(), "schema": "release-walk/v2"})
        self.refused("walk", "is not release-walk/v1")

    def test_report_that_does_not_match_walk_json_is_refused(self):
        self.built()
        self.edit_report(lambda r: r["walk"].update(release="r9"))
        self.refused("final", "walk does not match walk.json")


class DiversityTests(Base):
    def test_two_operating_reviewers_pass_with_the_counts_line(self):
        code, out = self.check("walk")
        self.assertEqual(code, 0, out)
        self.assertIn("reviewers: 2 (models: 2)", out)
        self.assertNotIn("model consensus is not independent", out)

    def test_equal_personas_are_refused(self):
        self.edit_reviewer("s", lambda d: d["reviewer"].update(persona="impatient first-timer"))
        self.refused("walk", "two reviewers share a persona")

    def test_equal_models_under_multi_model_are_refused(self):
        self.edit_reviewer("s", lambda d: d["reviewer"].update(model="opus"))
        self.refused("walk", "the reviewers share one model")

    def test_equal_models_with_no_declaration_are_refused(self):
        self.edit_reviewer("s", lambda d: d["reviewer"].update(model="opus"))
        put(self.walk / "meta.json", {"target": {"environment": "staging", "ref": "abc"}})
        self.refused("walk", "diversity.mode is not declared")

    def test_single_model_declaration_is_accepted_and_says_so(self):
        self.edit_reviewer("s", lambda d: d["reviewer"].update(model="opus"))
        put(self.walk / "meta.json", {"target": {"environment": "staging", "ref": "abc"}, "diversity": {"mode": "single-model"}})
        code, out = self.check("walk")
        self.assertEqual(code, 0, out)
        self.assertIn("reviewers: 2 (models: 1)", out)
        self.assertIn("model consensus is not independent", out)

    def test_a_provider_key_is_an_unknown_key(self):
        self.edit_reviewer("s", lambda d: d["reviewer"].update(provider="other"))
        self.refused("walk", "unknown key ['provider']")


class TargetTests(Base):
    def test_a_walk_names_the_environment_and_ref_it_ran_against(self):
        for target in ({}, {"environment": "staging"}, {"ref": "abc"}, {"environment": " ", "ref": "abc"}):
            put(self.walk / "meta.json", {"target": target, "diversity": {"mode": "multi-model"}})
            self.refused("walk", "target needs a non-empty environment and ref")
        (self.walk / "meta.json").write_text("{}")
        self.refused("walk", "target needs")
        self.setUp()
        self.built()
        self.edit_report(lambda r: r.pop("target"))
        self.refused("final", "target needs")


class SmokeTests(Base):
    def test_smoke_absent_failed_or_without_its_file_is_refused_at_both_tiers(self):
        (self.walk / "smoke.json").unlink()
        self.refused("walk", "smoke is absent")
        put(self.walk / "smoke.json", {"result": "failed", "check": "c", "evidence": ["shot.png"]})
        self.refused("walk", "not passed")
        put(self.walk / "smoke.json", {"result": "passed", "check": "c", "evidence": ["missing.png"]})
        self.refused("walk", "evidence missing.png is not a file")
        put(self.walk / "smoke.json", {"result": "passed", "check": "c", "evidence": ["shot.png"]})
        self.built()
        for change, needle in ((lambda r: r.pop("smoke"), "smoke is absent"),
                               (lambda r: r["smoke"].update(result="not-run"), "not passed"),
                               (lambda r: r["smoke"].update(evidence=["missing.png"]), "evidence missing.png is not a file")):
            self.built()
            self.edit_report(change)
            self.refused("final", needle)


class DeferredTests(Base):
    def test_lists_only_newest_report_findings_of_the_release_including_archived(self):
        code, out = run("deferred", "book-pickup/r1", "--workflow-dir", self.wf)
        self.assertEqual(code, 0)
        ids = [line.split(":")[0] for line in out.splitlines()]
        self.assertEqual(ids, DEFERRED)
        self.assertNotIn("old finding", out)
        self.assertNotIn("other release", out)
        self.assertNotIn("self", out)

    def test_needs_decision_and_built_screen_lines_are_listed_in_order(self):
        put(self.wf / ".spacedock-state/t-screen.md", task_file(
            {"journey": "book-pickup", "journey-release": "r7"},
            validation("Needs decision: who owns the toast", "Built screen finding: clipped label", "Built screen finding: low contrast")))
        ids = [i for i, _ in ra.deferred_items(self.wf, "book-pickup", "r7")]
        self.assertEqual(ids, ["t-screen#decision-1", "t-screen#screen-1", "t-screen#screen-2"])

    def test_scanning_only_live_tasks_would_drop_the_archived_item(self):
        archived = self.wf / ".spacedock-state/_archive/t-ready.md"
        live = self.wf / ".spacedock-state/t-ready.md"
        shutil.move(archived, live)
        out = run("deferred", "book-pickup/r1", "--workflow-dir", self.wf)[1]
        self.assertIn("t-ready#F1", out)

    def test_finding_pattern_is_the_gate_s(self):
        self.assertIs(ra.FINDING, delivery_gate.FINDING)

    def test_every_deferred_item_needs_a_verdict_from_each_reviewer_and_a_ruling(self):
        self.edit_reviewer("o", lambda d: d["deferred_verdicts"].pop())
        self.refused("walk", "deferred item t-collect-a#declined-1 has no verdict")
        self.setUp()
        self.built()
        self.edit_report(lambda r: r["ruling"]["deferred"].pop())
        self.refused("final", "has no director ruling")

    def test_a_walk_with_no_deferred_items_needs_no_verdicts(self):
        for name in ("t-reserve.md", "t-collect-a.md"):
            (self.wf / ".spacedock-state" / name).unlink()
        (self.wf / ".spacedock-state/_archive/t-ready.md").unlink()
        self.edit_reviewer("o", lambda d: d.update(deferred_verdicts=[]))
        self.edit_reviewer("s", lambda d: d.update(deferred_verdicts=[]))
        self.assertEqual(self.check("walk")[0], 0)


class RulingTests(Base):
    def case(self, fn, needle):
        self.built()
        self.edit_report(fn)
        self.refused("final", needle)

    def test_complaint_in_no_item_is_refused(self):
        self.case(lambda r: r["ruling"]["items"][3].update(**{"from": ["s3"]}), "complaint s4 is in no ruling item's from")

    def test_unverified_must_be_a_decision(self):
        self.case(lambda r: r["ruling"]["items"][3].update(ruling="solve", how="x", when="this-round"), "real unverified must be ruled decision")

    def test_real_no_or_do_not_solve_needs_a_why(self):
        self.case(lambda r: r["ruling"]["items"][4].update(why=""), "real no or do-not-solve needs a why")

    def test_solve_needs_how_and_when(self):
        self.case(lambda r: r["ruling"]["items"][0].update(how=""), "solve needs a how and a when")
        self.case(lambda r: r["ruling"]["items"][0].update(when=""), "solve needs")

    def test_fourth_task_is_refused(self):
        def more(r):
            r["ruling"]["tasks"] += [{"title": f"t{i}", "scope": "s", "after": [], "from_items": ["i1"]} for i in range(2)]
        self.case(more, "4 backlog tasks proposed, at most 3")

    def test_task_without_from_items_is_refused(self):
        self.case(lambda r: r["ruling"]["tasks"][0].update(from_items=[]), "has no from_items")

    def test_deferral_without_a_release_is_refused(self):
        self.case(lambda r: r["ruling"]["items"][1].pop("release"), "deferral names no release")
        self.case(lambda r: r["ruling"]["deferred"][2].pop("release"), "deferral names no release")
        self.case(lambda r: r["ruling"]["items"][1].update(release="the release after r1"), "deferral names no release id")

    def clean_world(self):
        for who in ("o", "s"):
            def fn(data, who=who):
                data["stories"] = [story(x, "works", [f"{who}2"] if x == "reserve-copy" else []) for x in STORIES]
                data["proof_line"] = {"result": "works", "evidence": ["shot.png"], "cause": ""}
                data["complaints"] = [complaint(f"{who}2", ["reserve-copy"], 2)]
            self.edit_reviewer(who, fn)
        ruling = sonnet_ruling()
        ruling["items"] = [ruling["items"][1]]
        ruling["tasks"] = []
        put(self.walk / "ruling-sonnet.json", ruling)

    def test_a_works_but_unusable_item_ruled_solve_this_round_is_not_clean(self):
        self.clean_world()
        self.built()
        code, out = self.check("final")
        self.assertEqual(code, 0, out)
        self.assertIn("clean: yes", out)
        self.edit_report(lambda r: r["ruling"]["items"][0].update(when="this-round"))
        self.assertIn("clean: no", self.check("final")[1])

    def test_ruling_check_prints_nothing_for_a_clean_run_without_this_round_work(self):
        self.built()
        report = read(self.walk / "report.json")
        self.assertTrue(ra.is_clean({**report, "stories": [dict(s, result="works") for s in report["stories"]],
                                     "proof_line": {"result": "works"}, "ruling": {"items": [
                                         {"real": "yes", "ruling": "solve", "when": "next-release"}]}}))
        self.assertFalse(ra.is_clean({**report, "stories": [dict(s, result="works") for s in report["stories"]],
                                      "proof_line": {"result": "works"}, "ruling": {"items": [
                                          {"real": "yes", "ruling": "solve", "when": "this-round", "class": "works-but-unusable"}]}}))


class DirectorSkillTests(unittest.TestCase):
    def test_skill_has_pass_three_and_the_agent_keeps_sonnet(self):
        skill = (PACKAGE / "skills/design-director/SKILL.md").read_text()
        row = next(line for line in skill.splitlines() if line.startswith("| 3 |"))
        for name in ("Reviewer reports:", "Deferred:", "Screenshots:", "Walk:", "Task folder:", "ADR folder:", "Items:"):
            self.assertIn(name, row)
        self.assertIn("release_ruling", skill)
        agent = (PACKAGE / "agents/design-director.md").read_text()
        self.assertRegex(agent, r"(?m)^model: sonnet$")


class EscalationTests(Base):
    def listed(self):
        code, out = run("escalate", self.folder, "--workflow-dir", self.wf)
        self.assertEqual(code, 0, out)
        return {m.group(1): m.group(2) for m in re.finditer(r"^escalate (\S+): (.*)$", out, re.M)}, out

    def test_each_condition_prints_its_reason_and_the_plain_item_prints_none(self):
        found, out = self.listed()
        self.assertEqual(found["i1"], "backlog-or-decision")
        self.assertEqual(found["i2"], "design-opus:t-reserve, backlog-or-decision")
        self.assertEqual(found["i3"], "reviewers-disagree, backlog-or-decision")
        self.assertEqual(found["i4"], "unverified, backlog-or-decision")
        self.assertNotIn("i5", found)
        self.assertIn("design-opus:t-reserve", found["t-reserve#F1"])
        self.assertIn("reviewers-disagree", found["t-reserve#F1"])
        self.assertIn("reviewers-disagree", found["t-collect-a#declined-1"])
        self.assertNotIn("t-ready#F1", found)

    def test_poc_and_unrecorded_owners_print_notes_and_do_not_count_as_opus(self):
        found, out = self.listed()
        self.assertIn("no ideation stage: t-collect-b", out)
        self.assertIn("ideation model unrecorded: t-collect-a", out)
        self.assertNotIn("design-opus:t-collect", out)

    def test_an_archived_owner_s_opus_counts(self):
        put(self.wf / ".spacedock-state/_archive/t-ready/dispatch/ideation-1.md", "Model: claude-opus-4\n")
        found, _ = self.listed()
        self.assertEqual(found["i1"], "design-opus:t-ready, backlog-or-decision")
        self.assertIn("t-ready#F1", found)

    def test_any_ideation_record_naming_opus_counts(self):
        put(self.wf / ".spacedock-state/t-collect-a/dispatch/ideation-1.md", "Model: sonnet\n")
        put(self.wf / ".spacedock-state/t-collect-a/dispatch/ideation-2.md", "Model: opus\n")
        found, _ = self.listed()
        self.assertIn("design-opus:t-collect-a", found["i3"])

    def test_nothing_listed_prints_none(self):
        put(self.walk / "ruling-sonnet.json", {"items": [dict(sonnet_ruling()["items"][4])] , "deferred": [], "tasks": []})
        _, out = self.listed()
        self.assertIn("escalate: none", out)

    def test_a_sonnet_ruled_item_that_meets_a_condition_is_refused_and_opus_with_its_fields_is_accepted(self):
        report = self.built()
        self.assertEqual(report["ruling"]["items"][3]["model"], "opus")
        self.assertEqual(report["ruling"]["items"][3]["sonnet_ruling"], {"real": "unverified", "ruling": "decision"})
        self.assertEqual(self.check("final")[0], 0)
        self.edit_report(lambda r: r["ruling"]["items"][3].update(model="sonnet", escalated_for=[]))
        self.refused("final", "ruling i4: meets unverified")
        self.built()
        self.edit_report(lambda r: r["ruling"]["items"][3].pop("sonnet_ruling"))
        self.refused("final", "model opus needs escalated_for and sonnet_ruling")

    def test_the_merged_ruling_names_each_model_and_keeps_sonnet_for_the_rest(self):
        report = self.built()
        by_id = {i["id"]: i for i in report["ruling"]["items"]}
        self.assertEqual(by_id["i5"]["model"], "sonnet")
        self.assertEqual(by_id["i5"]["escalated_for"], [])
        self.assertEqual(report["ruling"]["director"]["models"], ["sonnet", "opus"])
        self.assertEqual([t["title"] for t in report["ruling"]["tasks"]],
                         ["Fix check-ready and the reserve action", "Add the collect link"])

    def test_escalate_prints_the_items_line_with_each_item_s_complaints(self):
        _, out = self.listed()
        self.assertIn("Items: i1 (o1, s1); i2 (o2, s2); i3 (s3); i4 (s4); t-collect-a#declined-1; t-reserve#F1", out)

    def test_build_refuses_an_opus_ruling_that_groups_other_complaints_under_an_item(self):
        run("escalate", self.folder, "--workflow-dir", self.wf)
        sonnet = read(self.walk / "ruling-sonnet.json")
        opus = {"items": [dict(i, **{"from": ["o3"]}) if i["id"] == "i1" else i for i in sonnet["items"] if i["id"] != "i5"],
                "deferred": [d for d in sonnet["deferred"] if d["item"] != "t-ready#F1"], "tasks": []}
        put(self.walk / "ruling-opus.json", opus)
        code, out = run("build", self.folder, "--workflow-dir", self.wf)
        self.assertEqual(code, 1)
        self.assertIn("groups different complaints under item i1", out)

    def test_build_refuses_an_opus_ruling_that_misses_an_escalated_item(self):
        run("escalate", self.folder, "--workflow-dir", self.wf)
        put(self.walk / "ruling-opus.json", {"items": [], "deferred": [], "tasks": []})
        code, out = run("build", self.folder, "--workflow-dir", self.wf)
        self.assertEqual(code, 1)
        self.assertIn("opus ruling must cover exactly the escalated entries", out)


class RecordTests(Base):
    def test_render_is_deterministic_and_check_catches_one_character(self):
        self.built()
        code, record = run("render", self.folder)
        self.assertEqual(code, 0)
        put(self.walk / "record.md", record)
        self.assertEqual(run("render", self.folder, "--check")[0], 0)
        digest = hashlib.sha256((self.walk / "report.json").read_bytes()).hexdigest()
        self.assertTrue(record.rstrip().endswith(f"Report digest: sha256:{digest}"))
        put(self.walk / "record.md", record.replace("fix the status read", "fix the status reed"))
        self.assertEqual(run("render", self.folder, "--check")[0], 1)

    def test_a_mutated_ruling_field_changes_the_digest(self):
        self.built()
        first = run("render", self.folder)[1].splitlines()[-1]
        self.edit_report(lambda r: r["ruling"]["items"][0].update(how="other"))
        self.assertNotEqual(first, run("render", self.folder)[1].splitlines()[-1])

    def test_record_opens_with_one_row_per_complaint_with_task_status_and_reason(self):
        self.built()
        record = run("render", self.folder)[1]
        self.assertEqual(record.splitlines()[2], "## Complaints")
        head = [line for line in record.split("## Summary")[0].splitlines()[5:] if line.startswith("| ")]
        self.assertEqual(sorted(r.split(" | ")[0].strip("| ") for r in head), ["o1", "o2", "o3", "s1", "s2", "s3", "s4"])
        by = {r.split(" | ")[0].strip("| "): [c.strip(" |") for c in r.split(" | ")] for r in head}
        self.assertEqual(by["o1"][2:5], ["Fix check-ready and the reserve action", "to-fix", "fix the status read"])
        self.assertEqual(by["o2"][3], "deferred:r2")
        self.assertEqual(by["s3"][2], "Add the collect link")
        self.assertEqual(by["s4"][2:4], ["none", "decision"])
        self.assertEqual(by["o3"][3], "will-not-fix")

    def test_a_filed_task_s_one_line_links_a_complaint_to_it(self):
        put(self.wf / ".spacedock-state/fix-ready.md",
            task_file({"journey": "book-pickup", "journey-release": "r1"}, "Scope.\nWalk complaints: o1, s1\n"))
        self.built()
        record = run("render", self.folder)[1]
        row = next(line for line in record.splitlines() if line.startswith("| o1 "))
        self.assertIn("fix-ready", row)
        self.assertEqual(ra.complaint_links(self.wf, "book-pickup", "r1")["s1"], ["fix-ready"])

    def test_a_hand_edited_row_is_refused(self):
        self.built()
        self.edit_report(lambda r: r["complaint_rows"][0].update(status="fixed"))
        self.refused("final", "complaint_rows is not one row per reviewer complaint")
        self.built()
        self.edit_report(lambda r: r["complaint_rows"].pop())
        self.refused("final", "complaint_rows is not one row per reviewer complaint")


class RewalkTests(Base):
    def first_walk(self):
        self.built()
        self.prior = self.tmp_path / "prior-report.json"
        shutil.copy(self.walk / "report.json", self.prior)

    @property
    def tmp_path(self):
        return Path(self.tmp.name)

    def second_folder(self, mutate=None):
        folder = self.wf / ".spacedock-state/r1-rewalk"
        o, s = reviewer_o(), reviewer_s()
        o["marks"] = [{"complaint": "o1", "status": "fixed", "reason": "ready shows now"},
                      {"complaint": "o2", "status": "partly-fixed", "reason": "still below the fold on mobile"},
                      {"complaint": "o3", "status": "will-not-fix", "reason": "agreed polish"}]
        s["marks"] = [{"complaint": "s1", "status": "fixed", "reason": "ready shows now"},
                      {"complaint": "s2", "status": "deferred", "release": "r2", "reason": "moved to r2"},
                      {"complaint": "s3", "status": "fixed", "reason": "link added"},
                      {"complaint": "s4", "status": "will-not-fix", "reason": "no picture"}]
        o["complaints"] = [complaint("n1", ["collect-book"], 2)]
        o["stories"] = [story("reserve-copy", "works"), story("check-ready", "works"), story("collect-book", "works", ["n1"])]
        o["proof_line"] = {"result": "works", "evidence": ["shot.png"], "cause": ""}
        s["complaints"] = []
        s["stories"] = [story(x, "works") for x in STORIES]
        s["proof_line"] = {"result": "works", "evidence": ["shot.png"], "cause": ""}
        s["deferred_verdicts"] = [dict(v, verdict="agree") for v in s["deferred_verdicts"]]
        o["deferred_verdicts"] = [dict(v, verdict="agree") for v in o["deferred_verdicts"]]
        if mutate:
            mutate(o, s)
        ruling = {"items": [{"id": "j1", "from": ["n1"], "stories": ["collect-book"], "real": "yes", "ruling": "do-not-solve",
                             "class": "polish", "why": "cosmetic"}],
                  "deferred": [{"item": d, "ruling": "do-not-solve", "how": "", "when": "never", "why": "settled"} for d in DEFERRED],
                  "tasks": []}
        write_walk(folder, [o, s], ruling)
        return folder

    def rebuild(self, folder, prior=None):
        return pipeline(folder, self.wf, prior or self.prior)

    def test_a_rewalk_marks_every_own_complaint_accepts_new_ones_and_opens_with_the_table(self):
        self.first_walk()
        folder = self.second_folder()
        (code, out), _ = self.rebuild(folder)
        self.assertEqual(code, 0, out)
        code, out = run("check", folder, "--tier", "final", "--workflow-dir", self.wf, "--prior", self.prior)
        self.assertEqual(code, 0, out)
        record = run("render", folder)[1]
        lines = record.splitlines()
        self.assertEqual(lines[2], "## Complaints")
        body = "\n".join(lines)
        for cid, status in (("o1", "fixed"), ("o2", "partly-fixed"), ("s2", "deferred:r2"), ("o3", "will-not-fix"), ("n1", "will-not-fix")):
            self.assertRegex(body, rf"\| {cid} \| \w \| [^|]+ \| {status} \|")
        self.assertLess(body.index("| n1 |"), body.index("## Summary"))
        self.assertIn("Re-walk of the walk whose report digest is sha256:", body)
        row = next(r for r in read(folder / "walk/report.json")["complaint_rows"] if r["complaint"] == "o1")
        self.assertEqual(row["task"], "Fix check-ready and the reserve action")

    def rewalk_check(self, folder, prior=None):
        return run("check", folder, "--tier", "walk", "--workflow-dir", self.wf, "--prior", prior or self.prior)

    def test_a_prior_report_whose_digest_does_not_match_is_refused(self):
        self.first_walk()
        folder = self.second_folder()
        (code, out), _ = self.rebuild(folder)
        self.assertEqual(code, 0, out)
        other = self.tmp_path / "other.json"
        shutil.copy(self.prior, other)
        other.write_text(other.read_text() + " ")
        code, out = run("check", folder, "--tier", "final", "--workflow-dir", self.wf, "--prior", other)
        self.assertEqual(code, 1)
        self.assertIn("prior report's digest does not match", out)

    def test_a_reviewer_whose_model_persona_or_id_differs_is_refused(self):
        self.first_walk()
        for key, value, needle in (("model", "haiku", "id, model or persona differs"),
                                   ("persona", "someone else", "id, model or persona differs"),
                                   ("id", "z", "not a reviewer of the prior walk")):
            folder = self.second_folder(lambda o, s, key=key, value=value: o["reviewer"].update({key: value}))
            code, out = self.rewalk_check(folder)
            self.assertEqual(code, 1, out)
            self.assertIn(needle, out)

    def test_an_own_prior_complaint_left_unmarked_is_refused(self):
        self.first_walk()
        folder = self.second_folder(lambda o, s: o["marks"].pop(0))
        code, out = self.rewalk_check(folder)
        self.assertEqual(code, 1)
        self.assertIn("own prior complaint o1 left unmarked", out)

    def test_a_reviewer_who_did_not_return_leaves_their_complaints_unmarked(self):
        self.first_walk()
        folder = self.second_folder()
        (folder / "walk/reviewer-s.json").unlink()
        code, out = self.rewalk_check(folder)
        self.assertEqual(code, 1)
        self.assertIn("fewer than two reviewers operated", out)
        self.assertIn("prior reviewer s is absent from the re-walk", out)

    def test_a_third_prior_reviewer_missing_is_refused_though_two_still_operate(self):
        third = reviewer_o()
        third["reviewer"] = {"id": "t", "model": "haiku", "persona": "screen-reader user"}
        third["complaints"] = [complaint("t1", ["check-ready"], 1)]
        third["stories"] = [story("reserve-copy", "works"), story("check-ready", "broken", ["t1"]), story("collect-book", "works")]
        write_walk(self.folder, [reviewer_o(), reviewer_s(), third])
        (code, out), _ = pipeline(self.folder, self.wf)
        self.assertEqual(code, 0, out)
        self.prior = self.tmp_path / "prior-report.json"
        shutil.copy(self.walk / "report.json", self.prior)
        folder = self.second_folder()
        code, out = self.rewalk_check(folder)
        self.assertEqual(code, 1)
        self.assertIn("prior reviewer t is absent from the re-walk", out)
        self.assertNotIn("fewer than two", out)

    def test_a_mark_needs_a_known_status_a_reason_and_a_deferral_its_release(self):
        self.first_walk()
        for fn, needle in ((lambda o, s: o["marks"][0].update(status="done"), "needs a status of"),
                           (lambda o, s: o["marks"][0].update(reason=""), "needs a status of"),
                           (lambda o, s: s["marks"][1].pop("release"), "deferral of 's2' names no release")):
            code, out = self.rewalk_check(self.second_folder(fn))
            self.assertEqual(code, 1, out)
            self.assertIn(needle, out)

    def test_a_new_complaint_may_not_reuse_a_prior_id(self):
        self.first_walk()
        folder = self.second_folder(lambda o, s: o["complaints"][0].update(id="o1"))
        self.assertIn("reuses a prior complaint id", self.rewalk_check(folder)[1])

    def test_marks_without_a_prior_walk_are_refused(self):
        o = reviewer_o()
        o["marks"] = [{"complaint": "o1", "status": "fixed", "reason": "r"}]
        write_walk(self.folder, [o, reviewer_s()])
        self.refused("walk", "marks without a prior walk")


class ContractTests(unittest.TestCase):
    def test_schema_prints_the_table_and_the_version_and_exits_zero(self):
        code, out = run("schema", "release-acceptance")
        self.assertEqual(code, 0, out)
        self.assertIn("release-acceptance 1.0.0", out)
        self.assertIn("`complaint_rows`", out)

    def test_a_changed_field_table_without_a_version_bump_exits_one(self):
        original = ra.FIELDS
        try:
            ra.FIELDS = original + (("extra", "a new field"),)
            code, out = run("schema", "release-acceptance")
        finally:
            ra.FIELDS = original
        self.assertEqual(code, 1)
        self.assertIn("the field table changed but version 1.0.0 did not", out)

    def test_an_unknown_schema_name_exits_one(self):
        self.assertEqual(run("schema", "journey-footprint")[0], 1)

    def test_no_released_file_names_a_kc_journey_map_path(self):
        for name in ("release_acceptance.py", "EXTENSION.md", "contract-versions.json"):
            self.assertNotRegex((HERE / name).read_text(), r"kc-journey-map/|kc_journey_map|from kc|\.\./kc-journey")
        test_source = Path(__file__).read_text()
        imports = [line for line in test_source.splitlines() if re.match(r"\s*(import|from)\s", line)]
        self.assertEqual([line for line in imports if "journey" in line], [])

    def test_the_adr_the_schema_footer_names_exists(self):
        self.assertTrue((REPO / "docs/adr" / f"0033-{ra.ADR_TITLE}.md").is_file())

    def test_extension_md_stays_within_its_word_budget(self):
        self.assertLessEqual(len((HERE / "EXTENSION.md").read_text().split()), 600)


class ReportForJourneyAcceptTests(Base):
    def test_the_report_keeps_top_level_stories_and_the_shipped_accept_reads_them(self):
        node = shutil.which("node")
        accept = REPO / "kc-journey-map/lib/journey-accept.mjs"
        example = REPO / "kc-journey-map/skills/kc-journey-map/references/journey.example.yaml"
        probe = subprocess.run([node, "-e", "import('yaml')"], cwd=accept.parent, capture_output=True) if node and accept.is_file() else None
        if probe is None or probe.returncode:
            print("not run: node or journey-accept.mjs missing, or its yaml dependency is not installed")
            self.skipTest("node or journey-accept.mjs unavailable")
        self.built()
        journey = self.walk / "journey.yaml"
        journey.write_text(example.read_text().replace("check-ready, card: \"See that the book is ready to collect\", release: r1, status: unverified",
                                                       "check-ready, card: \"See that the book is ready to collect\", release: r1, status: exists"))
        before = hashlib.sha256(journey.read_bytes()).hexdigest()
        done = subprocess.run([node, str(accept), str(journey), str(self.walk / "report.json")], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        proposals = json.loads(done.stdout)["proposals"]
        self.assertEqual({p["story"] for p in proposals}, {"collect-book", "check-ready"})
        self.assertEqual(hashlib.sha256(journey.read_bytes()).hexdigest(), before)
        self.assertIn("status: exists", journey.read_text())


if __name__ == "__main__":
    unittest.main()
