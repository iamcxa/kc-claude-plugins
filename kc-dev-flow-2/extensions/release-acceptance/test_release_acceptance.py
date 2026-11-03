import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
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
    put(wf / "README.md", "---\nentity-type: task\nstate: .spacedock-state\n"
        "walk-environment: staging\nproduction-environment: production\nrelease-doc: docs/releasing.md\n---\n")
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
                             "not_tested": ["resize"], "data_left": ["one reservation"], "director_model": "opus"})
    for r in reviewers or [reviewer_o(), reviewer_s()]:
        put(walk / f"reviewer-{r['reviewer']['id']}.json", r)
    put(walk / "ruling.json", ruling or sonnet_ruling())


def pipeline(folder, wf, prior=None):
    args = ["build", folder, "--workflow-dir", wf] + (["--prior", prior] if prior else [])
    return run(*args), ""


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


class RecordedEnvironmentTests(Base):
    def target(self, name):
        meta = read(self.walk / "meta.json")
        meta["target"]["environment"] = name
        put(self.walk / "meta.json", meta)
        if (self.walk / "report.json").exists():
            self.edit_report(lambda r: r["target"].update(environment=name))

    def test_production_is_refused_at_both_tiers(self):
        self.built()
        self.target("production")
        for tier in ("walk", "final"):
            out = self.refused(tier, "REFUSED: the walk ran on production (production); walk on staging")
            self.assertIn("clean: no", out)

    def test_recorded_staging_passes_but_another_staging_does_not(self):
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn("environment: staging (production: production)", out)
        self.target("staging-2")
        self.refused("walk", "the README records staging")

    def test_each_missing_key_holds_and_restoring_it_passes(self):
        readme = self.wf / "README.md"
        original = readme.read_text()
        for key in ("walk-environment", "production-environment", "release-doc"):
            for replacement in ("", f"{key}:\n"):
                with self.subTest(key=key, replacement=replacement):
                    put(readme, re.sub(rf"^{key}:.*\n", replacement, original, flags=re.M))
                    out = self.refused("walk", "environments not recorded")
                    self.assertIn(key, out)
                    self.assertIn("references/sd/adoption.md", out)
                    put(readme, original)
                    self.assertEqual(self.check()[0], 0)

    def test_equal_environment_names_hold_even_when_target_matches(self):
        readme = self.wf / "README.md"
        put(readme, readme.read_text().replace("production-environment: production", "production-environment: staging"))
        self.refused("walk", "walk-environment is production-environment (staging)")

    def test_local_requires_the_limit_and_render_keeps_it(self):
        readme = self.wf / "README.md"
        put(readme, readme.read_text().replace("walk-environment: staging", "walk-environment: local"))
        self.target("local")
        self.refused("walk", "a local walk records its limit")
        limit = "not deployed: served assets, headers and content types not seen"
        meta = read(self.walk / "meta.json")
        meta["not_tested"].append(limit)
        put(self.walk / "meta.json", meta)
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn("environment: local (not deployed)", out)
        self.built()
        code, out = run("render", self.folder)
        self.assertEqual(code, 0, out)
        self.assertIn(f"## Not tested\n\n- resize\n- {limit}", out)
        self.edit_report(lambda r: r["not_tested"].remove(limit))
        self.refused("final", "a local walk records its limit")


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
        put(self.walk / "ruling.json", ruling)

    def test_a_works_but_unusable_item_ruled_solve_this_round_is_not_clean(self):
        self.clean_world()
        self.built()
        code, out = self.check("final")
        self.assertEqual(code, 0, out)
        self.assertIn("clean: yes", out)
        self.edit_report(lambda r: r["ruling"]["items"][0].update(when="this-round"))
        self.assertIn("clean: no", self.check("final")[1])

    def test_a_deferred_finding_ruled_solve_this_round_is_not_clean(self):
        self.clean_world()
        fix = {"title": "Fix the reserve finding", "scope": "one", "after": [], "from_items": ["t-reserve#F1"]}
        self.built()
        self.edit_report(lambda r: (r["ruling"]["deferred"][2].update(when="this-round"), r["ruling"]["tasks"].append(fix)))
        code, out = self.check("final")
        self.assertEqual(code, 0, out)
        self.assertIn("clean: no", out)
        report = read(self.walk / "report.json")
        self.assertFalse(ra.is_clean({**report, "stories": [dict(s, result="works") for s in report["stories"]],
                                      "proof_line": {"result": "works"}, "ruling": {"items": [], "deferred": [
                                          {"item": "x#F1", "ruling": "solve", "when": "this-round"}]}}))
        self.assertTrue(ra.is_clean({**report, "stories": [dict(s, result="works") for s in report["stories"]],
                                     "proof_line": {"result": "works"}, "ruling": {"items": [], "deferred": [
                                         {"item": "x#F1", "ruling": "solve", "when": "later"}]}}))

    def test_a_this_round_solve_no_task_covers_is_refused(self):
        self.built()
        self.edit_report(lambda r: r["ruling"].update(tasks=[]))
        out = self.refused("final", "ruling i1: solve this-round is covered by no task")
        self.assertIn("ruling i3: solve this-round is covered by no task", out)
        self.assertNotIn("ruling i2:", out)
        self.built()
        self.edit_report(lambda r: (r["ruling"]["deferred"][2].update(when="this-round"),
                                    r["ruling"]["tasks"][0]["from_items"].remove("i2")))
        self.refused("final", "ruling t-reserve#F1: solve this-round is covered by no task")

    def test_a_filed_task_that_names_the_complaints_covers_a_this_round_solve(self):
        filed = self.wf / ".spacedock-state/fix-all.md"
        put(filed, task_file({"journey": "book-pickup", "journey-release": "r1"}, "Scope.\nWalk complaints: o1\n"))
        self.built()
        self.edit_report(lambda r: r["ruling"].update(tasks=[]))
        out = self.refused("final", "ruling i3: solve this-round is covered by no task")
        self.assertNotIn("ruling i1:", out)
        put(filed, task_file({"journey": "book-pickup", "journey-release": "r1"}, "Scope.\nWalk complaints: o1, s3\n"))
        self.built()
        self.edit_report(lambda r: r["ruling"].update(tasks=[]))
        code, out = self.check("final")
        self.assertEqual(code, 0, out)

    def test_ruling_check_prints_nothing_for_a_clean_run_without_this_round_work(self):
        self.built()
        report = read(self.walk / "report.json")
        self.assertTrue(ra.is_clean({**report, "stories": [dict(s, result="works") for s in report["stories"]],
                                     "proof_line": {"result": "works"}, "ruling": {"items": [
                                         {"real": "yes", "ruling": "solve", "when": "next-release"}]}}))
        self.assertFalse(ra.is_clean({**report, "stories": [dict(s, result="works") for s in report["stories"]],
                                      "proof_line": {"result": "works"}, "ruling": {"items": [
                                          {"real": "yes", "ruling": "solve", "when": "this-round", "class": "works-but-unusable"}]}}))


class AcceptedTests(Base):
    def accepted(self, release="book-pickup/r1"):
        return run("accepted", release, "--workflow-dir", self.wf)

    def not_accepted(self, needle):
        code, out = self.accepted()
        self.assertEqual(code, 1, out)
        self.assertIn("not accepted: book-pickup/r1:", out)
        self.assertIn(needle, out)

    def close(self):
        RulingTests.clean_world(self)
        self.built()
        self.assertEqual(self.check("final")[0], 0)
        archive = self.folder.parent / "_archive"
        put(archive / "r1-acceptance.md", task_file({"release-acceptance": "book-pickup/r1", "pr": "local-merge:" + "a" * 40}))
        self.folder.with_suffix(".md").unlink()
        shutil.move(self.folder, archive / "r1-acceptance")
        self.folder = archive / "r1-acceptance"
        self.walk = self.folder / "walk"
        return self.folder.with_suffix(".md")

    def rewalk(self, prior=True, archived=True, previous=None, slug="r1-rewalk"):
        previous = self.folder if previous is None else previous
        previous_report = previous / "walk/report.json"
        parent = self.folder.parent if archived else self.folder.parent.parent
        folder = parent / slug
        shutil.copytree(previous, folder)
        for path in (folder / "walk").glob("reviewer-*.json"):
            reviewer = read(path)
            reviewer["marks"] = [{"complaint": c["id"], "status": "fixed", "reason": "fixed on re-walk"}
                                 for c in reviewer["complaints"]]
            reviewer["complaints"] = []
            for story in reviewer["stories"]:
                story["complaints"] = []
            put(path, reviewer)
        put(folder / "walk/ruling.json", {"items": [], "tasks": [], "deferred": [
            {"item": d, "ruling": "do-not-solve", "when": "never", "why": "settled"} for d in DEFERRED]})
        code, out = run("build", folder, "--workflow-dir", self.wf, "--prior", previous_report)
        self.assertEqual(code, 0, out)
        put(folder.with_suffix(".md"), task_file({"release-acceptance": "book-pickup/r1", "pr": "local-merge:" + "b" * 40},
            f"Prior walk: {previous_report}\n" if prior else ""))
        return folder

    def test_no_task_and_live_task_hold_production(self):
        self.not_accepted("r1-acceptance is not archived")
        self.folder.with_suffix(".md").unlink()
        self.not_accepted("no acceptance task")

    def test_archive_needs_a_local_merge_sentinel(self):
        task = self.close()
        original = task.read_text()
        for merged in ("", "local-merge:", "https://github.com/example/repo/pull/1", "pr-merge:" + "a" * 40):
            put(task, task_file({"release-acceptance": "book-pickup/r1", "pr": merged}))
            self.not_accepted("has no pr: local-merge:<sha>")
        put(task, original)
        self.assertEqual(self.accepted()[0], 0)

    def test_clean_closed_walk_names_task_sentinel_and_release_document(self):
        self.close()
        code, out = self.accepted()
        self.assertEqual(code, 0, out)
        self.assertEqual(out, "accepted: book-pickup/r1 by r1-acceptance (local-merge:" + "a" * 40 +
                         "); production release per docs/releasing.md\n")
        readme = self.wf / "README.md"
        put(readme, readme.read_text().replace("docs/releasing.md", "ops/production.md"))
        self.assertIn("production release per ops/production.md", self.accepted()[1])

    def test_clean_archived_production_walk_is_not_accepted(self):
        self.close()
        self.edit_report(lambda r: r["target"].update(environment="production"))
        self.not_accepted("the walk ran on production")

    def test_minimal_forged_clean_report_is_not_accepted(self):
        self.close()
        put(self.walk / "report.json", {"schema": "release-acceptance/v1",
            "walk": {"journey": "book-pickup", "release": "r1"},
            "target": {"environment": "staging", "ref": "abc"}, "stories": [],
            "proof_line": {"result": "works"}, "smoke": {"result": "passed"}, "walks": []})
        self.not_accepted("reviewers")

    def test_clean_report_still_needs_valid_ruling_and_complaint_rows(self):
        self.close()
        original = read(self.walk / "report.json")
        self.edit_report(lambda r: r["ruling"]["director"].update(model="sonnet"))
        self.not_accepted("director.model")
        put(self.walk / "report.json", original)
        self.edit_report(lambda r: r["complaint_rows"].clear())
        self.not_accepted("complaint_rows")

    def test_clean_rewalk_still_needs_its_prior_digest(self):
        self.close()
        folder = self.rewalk()
        self.assertEqual(self.accepted()[0], 0)
        path = folder / "walk/report.json"
        report = read(path)
        report["prior"]["digest"] = "sha256:" + "0" * 64
        put(path, report)
        self.not_accepted("prior report's digest does not match")

    def test_clean_local_walk_still_needs_its_recorded_limit(self):
        self.close()
        readme = self.wf / "README.md"
        put(readme, readme.read_text().replace("walk-environment: staging", "walk-environment: local"))
        self.edit_report(lambda r: r["target"].update(environment="local"))
        self.not_accepted("a local walk records its limit")

    def test_missing_malformed_or_unclean_report_holds(self):
        self.close()
        path = self.walk / "report.json"
        original = read(path)
        for change in (lambda r: r["stories"][0].update(result="broken"),
                       lambda r: r["proof_line"].update(result="broken"),
                       lambda r: r["smoke"].update(result="failed"),
                       lambda r: r["ruling"]["items"][0].update(when="this-round"),
                       lambda r: r["walks"][0].update(marks=[{"status": "partly-fixed"}])):
            report = copy.deepcopy(original)
            change(report)
            put(path, report)
            self.not_accepted("is not clean")
        path.unlink()
        self.not_accepted("report.json is absent")
        for content in ("not json", "{}", "null"):
            put(path, content)
            self.not_accepted("r1")
        put(path, original)
        self.assertEqual(self.accepted()[0], 0)

    def test_newest_unclean_rewalk_overrides_older_clean_walk(self):
        self.close()
        folder = self.rewalk()
        path = folder / "walk/report.json"
        report = read(path)
        report["stories"][0]["result"] = "broken"
        put(path, report)
        self.not_accepted("r1-rewalk is not clean")
        report["stories"][0]["result"] = "works"
        put(path, report)
        code, out = self.accepted()
        self.assertEqual(code, 0, out)
        self.assertIn("by r1-rewalk (local-merge:", out)

    def test_live_rewalk_holds_even_with_an_older_clean_archive(self):
        self.close()
        self.rewalk(archived=False)
        self.not_accepted("r1-rewalk is not archived")

    def test_parallel_walks_hold_until_prior_is_named(self):
        self.close()
        folder = self.rewalk(prior=False)
        self.not_accepted("r1-acceptance, r1-rewalk are both newest; name the prior walk")
        with folder.with_suffix(".md").open("a") as f:
            f.write("Prior walk: _archive/r1-acceptance/walk/report.json\n")
        self.assertEqual(self.accepted()[0], 0)

    def test_three_walks_point_to_the_immediately_preceding_report(self):
        self.close()
        second = self.rewalk()
        third = self.rewalk(slug="r1-rewalk-again")
        self.not_accepted("r1-rewalk, r1-rewalk-again are both newest")
        shutil.rmtree(third)
        third.with_suffix(".md").unlink()
        third = self.rewalk(previous=second, slug="r1-rewalk-again")
        previous_report = second / "walk/report.json"
        code, out = run("check", third, "--tier", "final", "--workflow-dir", self.wf, "--prior", previous_report)
        self.assertEqual(code, 0, out)
        self.assertEqual(read(third / "walk/report.json")["prior"]["digest"],
                         "sha256:" + hashlib.sha256(previous_report.read_bytes()).hexdigest())
        code, out = self.accepted()
        self.assertEqual(code, 0, out)
        self.assertIn("by r1-rewalk-again (local-merge:", out)
        code, out = run("check", third, "--tier", "final", "--workflow-dir", self.wf,
                        "--prior", self.walk / "report.json")
        self.assertEqual(code, 1, out)
        self.assertIn("prior report's digest does not match", out)

    def test_foreign_release_and_cyclic_prior_are_refused(self):
        task = self.close()
        self.edit_report(lambda r: r["walk"].update(release="r2"))
        self.not_accepted("report does not describe book-pickup/r1")
        self.edit_report(lambda r: r["walk"].update(release="r1"))
        with task.open("a") as f:
            f.write(f"Prior walk: {self.walk / 'report.json'}\n")
        self.not_accepted("Prior walk chain is cyclic")

    def test_third_walk_cannot_drop_inherited_unresolved_complaints(self):
        self.close()
        second = self.rewalk()
        third = self.rewalk(previous=second, slug="r1-rewalk-inherited")
        for who, status in (("o", "partly-fixed"), ("s", "deferred")):
            path = second / f"walk/reviewer-{who}.json"
            reviewer = read(path)
            reviewer["marks"][0].update(status=status, reason="still needs work")
            if status == "deferred":
                reviewer["marks"][0]["release"] = "r2"
            put(path, reviewer)
        previous_report = second / "walk/report.json"
        code, out = run("build", second, "--workflow-dir", self.wf, "--prior", self.walk / "report.json")
        self.assertEqual(code, 0, out)
        code, out = run("check", second, "--tier", "final", "--workflow-dir", self.wf,
                        "--prior", self.walk / "report.json")
        self.assertEqual(code, 0, out)
        self.assertIn("clean: no", out)
        report = read(third / "walk/report.json")
        report["prior"]["digest"] = "sha256:" + hashlib.sha256(previous_report.read_bytes()).hexdigest()
        put(third / "walk/report.json", report)
        self.not_accepted("own prior complaint o2 left unmarked")
        code, out = run("build", third, "--workflow-dir", self.wf, "--prior", previous_report)
        self.assertEqual(code, 1, out)
        for who in ("o", "s"):
            path = third / f"walk/reviewer-{who}.json"
            reviewer = read(path)
            reviewer["marks"] = read(second / f"walk/reviewer-{who}.json")["marks"]
            put(path, reviewer)
            code, out = run("build", third, "--workflow-dir", self.wf, "--prior", previous_report)
            self.assertEqual(code, 1 if who == "o" else 0, out)
            if who == "o":
                self.assertIn("own prior complaint s2 left unmarked", out)
        code, out = run("check", third, "--tier", "final", "--workflow-dir", self.wf, "--prior", previous_report)
        self.assertEqual(code, 0, out)
        self.assertIn("clean: no", out)
        rows = read(third / "walk/report.json")["complaint_rows"]
        self.assertEqual({(r["complaint"], r["reviewer"], r["status"], r["reason"]) for r in rows},
                         {("o2", "o", "partly-fixed", "still needs work"),
                          ("s2", "s", "deferred:r2", "still needs work")})
        rendered = run("render", third)[1]
        self.assertIn("| o2 | o | none | partly-fixed | still needs work |", rendered)
        self.assertIn("| s2 | s | none | deferred:r2 | still needs work |", rendered)
        self.not_accepted("r1-rewalk-inherited is not clean")
        path = third / "walk/reviewer-o.json"
        reviewer = read(path)
        reviewer["marks"][0].update(status="fixed", reason="verified fixed")
        put(path, reviewer)
        code, out = run("build", third, "--workflow-dir", self.wf, "--prior", previous_report)
        self.assertEqual(code, 0, out)
        code, out = self.accepted()
        self.assertEqual(code, 0, out)
        self.assertIn("by r1-rewalk-inherited (local-merge:", out)

    def test_disconnected_self_cycle_cannot_hide_an_unclean_rewalk(self):
        self.close()
        folder = self.rewalk()
        path = folder / "walk/report.json"
        report = read(path)
        report["proof_line"]["result"] = "broken"
        put(path, report)
        task = folder.with_suffix(".md")
        put(task, task.read_text().replace(str(self.walk / "report.json"), str(path)))
        self.not_accepted("one acyclic Prior walk chain")

    def test_disconnected_two_walk_cycle_cannot_hide_unclean_walks(self):
        self.close()
        first = self.rewalk()
        second = first.parent / "r1-rewalk-again"
        shutil.copytree(first, second)
        for folder, prior in ((first, second), (second, first)):
            path = folder / "walk/report.json"
            report = read(path)
            report["proof_line"]["result"] = "broken"
            put(path, report)
            put(folder.with_suffix(".md"), task_file({"release-acceptance": "book-pickup/r1", "pr": "local-merge:" + "b" * 40},
                f"Prior walk: {prior / 'walk/report.json'}\n"))
        self.not_accepted("one acyclic Prior walk chain")

    def test_other_releases_are_not_acceptance_and_bad_argument_is_usage(self):
        self.close()
        self.assertEqual(self.accepted("book-pickup/r2")[0], 1)
        for release in ("r1", "/r1", "book-pickup/", "book-pickup/r1/extra"):
            self.assertEqual(self.accepted(release)[0], 2)


class DirectorSkillTests(unittest.TestCase):
    def test_skill_has_pass_three_and_the_agent_keeps_sonnet(self):
        skill = (PACKAGE / "skills/design-director/SKILL.md").read_text()
        row = next(line for line in skill.splitlines() if line.startswith("| 3 |"))
        for name in ("Reviewer reports:", "Deferred:", "Screenshots:", "Walk:", "Task folder:", "ADR folder:"):
            self.assertIn(name, row)
        self.assertIn("release_ruling", skill)
        self.assertNotIn("Items:", skill)
        agent = (PACKAGE / "agents/design-director.md").read_text()
        self.assertRegex(agent, r"(?m)^model: sonnet$")


class DirectorModelTests(Base):
    def model(self):
        code, out = run("director-model", self.folder, "--workflow-dir", self.wf)
        self.assertEqual(code, 0, out)
        return out

    def test_opus_when_a_task_of_the_release_ran_its_ideation_on_opus(self):
        out = self.model()
        self.assertIn("director model: opus (design-opus:t-reserve)", out)

    def test_sonnet_when_no_task_did(self):
        put(self.wf / ".spacedock-state/t-reserve/dispatch/ideation-1.md", "Model: sonnet\n")
        self.assertIn("director model: sonnet", self.model())
        self.assertNotIn("opus", self.model())

    def test_poc_and_unrecorded_tasks_print_notes_and_do_not_count_as_opus(self):
        put(self.wf / ".spacedock-state/t-reserve/dispatch/ideation-1.md", "Model: sonnet\n")
        out = self.model()
        self.assertIn("no ideation stage: t-collect-b", out)
        self.assertIn("ideation model unrecorded: t-collect-a", out)
        self.assertIn("director model: sonnet", out)

    def test_an_archived_task_s_opus_counts(self):
        put(self.wf / ".spacedock-state/t-reserve/dispatch/ideation-1.md", "Model: sonnet\n")
        put(self.wf / ".spacedock-state/_archive/t-ready/dispatch/ideation-1.md", "Model: claude-opus-4\n")
        self.assertIn("director model: opus (design-opus:t-ready)", self.model())

    def test_any_ideation_record_naming_opus_counts(self):
        put(self.wf / ".spacedock-state/t-reserve/dispatch/ideation-1.md", "Model: sonnet\n")
        put(self.wf / ".spacedock-state/t-collect-a/dispatch/ideation-1.md", "Model: sonnet\n")
        put(self.wf / ".spacedock-state/t-collect-a/dispatch/ideation-2.md", "Model: opus\n")
        self.assertIn("director model: opus (design-opus:t-collect-a)", self.model())

    def test_a_task_of_another_release_does_not_count(self):
        put(self.wf / ".spacedock-state/t-reserve/dispatch/ideation-1.md", "Model: sonnet\n")
        put(self.wf / ".spacedock-state/t-other/dispatch/ideation-1.md", "Model: opus\n")
        self.assertIn("director model: sonnet", self.model())

    def test_the_report_records_one_model_and_check_refuses_a_different_one(self):
        report = self.built()
        self.assertEqual(report["ruling"]["director"], {"agent": "kc-dev-flow-2:design-director", "model": "opus"})
        self.assertEqual(self.check("final")[0], 0)
        self.edit_report(lambda r: r["ruling"]["director"].update(model="sonnet"))
        self.refused("final", "ruling.director.model is 'sonnet' but the walk covers tasks that call for opus")
        self.built()
        self.edit_report(lambda r: r["ruling"]["director"].pop("model"))
        self.refused("final", "ruling.director.model is None")

    def test_no_item_carries_a_per_item_model(self):
        report = self.built()
        for item in report["ruling"]["items"] + report["ruling"]["deferred"]:
            self.assertFalse({"model", "escalated_for", "sonnet_ruling"} & set(item))
        self.assertEqual(run("escalate", self.folder, "--workflow-dir", self.wf)[0], 2)


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

    def rewalk_clean_line(self, mutate=None):
        folder = self.second_folder(mutate)
        (code, out), _ = self.rebuild(folder)
        self.assertEqual(code, 0, out)
        code, out = run("check", folder, "--tier", "final", "--workflow-dir", self.wf, "--prior", self.prior)
        self.assertEqual(code, 0, out)
        return next(line for line in out.splitlines() if line.startswith("clean:"))

    def test_a_rewalk_with_a_partly_fixed_prior_complaint_is_not_clean(self):
        self.first_walk()
        self.assertEqual(self.rewalk_clean_line(), "clean: no")

    def test_a_rewalk_is_clean_when_every_prior_complaint_is_fixed_deferred_or_will_not_fix(self):
        self.first_walk()
        self.assertEqual(self.rewalk_clean_line(lambda o, s: o["marks"][1].update(status="fixed")), "clean: yes")
        self.assertEqual(self.rewalk_clean_line(
            lambda o, s: o["marks"][1].update(status="deferred", release="r2")), "clean: yes")
        self.assertEqual(self.rewalk_clean_line(
            lambda o, s: o["marks"][1].update(status="will-not-fix")), "clean: yes")

    def test_marks_without_a_prior_walk_are_refused(self):
        o = reviewer_o()
        o["marks"] = [{"complaint": "o1", "status": "fixed", "reason": "r"}]
        write_walk(self.folder, [o, reviewer_s()])
        self.refused("walk", "marks without a prior walk")


class DueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.wf = self.root / "workflow"
        self.state = self.wf / ".spacedock-state"
        put(self.wf / "README.md", "---\nentity-type: task\nid-style: slug\nstate: .spacedock-state\nstages:\n  states:\n    - name: implementation\n      initial: true\n    - name: done\n      terminal: true\n---\n")
        self.document = read(HERE / "fixtures/journey-progress-v1.json")
        self.map = self.root / "journey.yaml"
        shutil.copyfile(REPO / "kc-journey-map/skills/kc-journey-map/references/journey.example.yaml", self.map)
        self.populate()
        self.progress = self.root / "producer.json"
        self.log = self.root / "calls.json"
        self.stub()
        node = self.root / "bin/node"
        put(node, f"#!{sys.executable}\n" +
            "import json,os,sys\nfrom pathlib import Path\n" +
            f"Path({str(self.log)!r}).write_text(json.dumps({{'argv':sys.argv[1:],'PATH':os.environ['PATH']}}))\n" +
            "p=json.loads(Path(sys.argv[1]).read_text())\nprint(p['stdout'])\nprint(p.get('stderr',''),file=sys.stderr)\nsys.exit(p['exit'])\n")
        node.chmod(0o755)
        patch = mock.patch.dict(os.environ, {"PATH": str(node.parent) + os.pathsep + os.environ.get("PATH", "")})
        patch.start()
        self.addCleanup(patch.stop)

    def populate(self, status="done"):
        for story in self.document["stories"]:
            for tid in story["taskIds"]:
                put(self.state / f"{tid}.md", task_file({"title": tid, "status": status,
                    "journey": "book-pickup", "journey-release": story["release"], "journey-story": story["story"],
                    "journey-required-tasks": "'" + json.dumps(story["taskIds"]) + "'", "journey-mapping-complete": "true"}))

    def stub(self, document=None, code=1, stdout=None, stderr=""):
        put(self.progress, {"exit": code, "stdout": stdout if stdout is not None else json.dumps(document or self.document), "stderr": stderr})

    def due(self, progress=True, maps=None):
        return run("due", "--workflow-dir", self.wf, *(["--progress", self.progress] if progress else []), *(maps or [self.map]))

    def test_recorded_real_progress_exit_one_and_claim_removal(self):
        code, out = self.due()
        self.assertEqual(code, 0, out)
        self.assertEqual(out.count("next:"), 2, out)
        self.assertNotIn("not run:", out)
        claim = self.state / "accept.md"
        put(claim, task_file({"release-acceptance": "book-pickup/r1"}))
        self.assertNotIn("release book-pickup/r1 ", self.due()[1])
        put(claim, task_file({"title": "claim removed"}))
        self.assertIn("release book-pickup/r1 ", self.due()[1])

    def test_live_archived_flat_and_folder_claims_and_empty_value(self):
        for name in ("claim.md", "claim/index.md", "_archive/claim.md", "_archive/claim/index.md"):
            with self.subTest(name=name):
                path = self.state / name
                put(path, task_file({"release-acceptance": "book-pickup/r1"}))
                self.assertNotIn("release book-pickup/r1 ", self.due()[1])
                put(path, task_file({"release-acceptance": ""}))
                self.assertIn("release book-pickup/r1 ", self.due()[1])
                path.unlink()

    def test_no_done_task_skips_producer_and_all_claimed_skips_producer(self):
        self.populate("implementation")
        self.assertEqual(self.due(), (0, ""))
        self.assertFalse(self.log.exists())
        self.populate()
        for release in self.document["releases"]:
            put(self.state / f"claim-{release['release']}.md", task_file({"release-acceptance": "book-pickup/" + release["release"]}))
        self.assertEqual(self.due(), (0, ""))
        self.assertFalse(self.log.exists())

    def test_missing_producer_prints_once_even_without_done_tasks(self):
        self.populate("implementation")
        self.assertEqual(self.due(progress=False), (0, "release-acceptance not run: kc-journey-map not found\n"))
        self.progress.unlink()
        self.assertEqual(self.due()[1], "release-acceptance not run: kc-journey-map not found\n")

    def test_nonmap_yaml_is_silent_and_done_folder_tasks_are_candidates(self):
        put(self.map, "other: yaml\n")
        self.assertEqual(self.due(progress=False), (0, ""))
        put(self.map, "journey: book-pickup\n")
        for task in self.state.glob("*.md"):
            put(task.with_suffix("") / "index.md", task.read_text())
            task.unlink()
        self.assertEqual(self.due()[1].count("next:"), 2)

    def test_producer_failures_are_diagnostic_and_never_due(self):
        bad_schema = {**self.document, "schema": "journey-progress/v2"}
        diagnostic = {**self.document, "diagnostic": "task observation failed"}
        for options, reason in (({"code": 2, "stderr": "cannot load\nextra"}, "cannot load"),
                                ({"stdout": "not json"}, "Expecting value"),
                                ({"document": bad_schema}, "expected journey-progress/v1"),
                                ({"document": diagnostic}, "task observation failed"),
                                ({"document": {**self.document, "releases": None}}, "invalid progress")):
            with self.subTest(options=options):
                self.stub(**options)
                code, out = self.due()
                self.assertEqual(code, 0, out)
                self.assertIn(f"release-acceptance not run: {self.map}: {reason}", out)
                self.assertNotIn("next:", out)
        with mock.patch.object(ra.subprocess, "run", side_effect=subprocess.TimeoutExpired("node", 60)):
            self.assertIn("timed out", self.due()[1])

    def test_spacedock_bin_leads_path_and_producer_argv_is_explicit(self):
        binary = self.root / "selected/spacedock"
        put(binary, "#!/bin/sh\nexit 0\n")
        binary.chmod(0o755)
        with mock.patch.dict(os.environ, {"SPACEDOCK_BIN": str(binary)}):
            self.due()
        logged = read(self.log)
        search = logged["PATH"].split(os.pathsep)
        self.assertEqual(search[1], str(binary.resolve().parent))
        self.assertFalse(Path(search[0]).exists(), "the command alias must be removed after the producer exits")
        self.assertEqual(logged["argv"], [str(self.progress), str(self.map), "--workflow-dir", str(self.wf)])

    def test_missing_selected_spacedock_is_diagnostic_instead_of_using_path_fallback(self):
        with mock.patch.dict(os.environ, {"SPACEDOCK_BIN": str(self.root / "missing/spacedock-preview")}):
            code, out = self.due()
        self.assertEqual(code, 0, out)
        self.assertIn("SPACEDOCK_BIN is not executable:", out)
        self.assertNotIn("next:", out)

    def test_yaml_journey_scalars_reach_the_producer_without_becoming_literal_ids(self):
        for value in ("book-pickup # comment", "'book-pickup' # comment", '"book\\x2dpickup" # comment',
                      ">-\n  book-pickup"):
            with self.subTest(value=value):
                put(self.map, "journey: " + value + "\n")
                code, out = self.due()
                self.assertEqual(code, 0, out)
                self.assertEqual(out.count("next:"), 2, out)
                self.assertTrue(self.log.is_file(), "the producer must read the YAML identity")
                self.log.unlink()

    def test_renamed_spacedock_bin_is_executed_instead_of_a_path_decoy(self):
        binary = self.root / "selected tool's bin/spacedock-preview"
        selected = self.root / "selected.json"
        put(binary, f"#!{sys.executable}\nimport json,sys\nfrom pathlib import Path\n" +
            f"Path({str(selected)!r}).write_text(json.dumps(sys.argv[1:]))\n" +
            f"print({json.dumps(self.document)!r})\n")
        binary.chmod(0o755)
        decoy = binary.with_name("spacedock")
        put(decoy, "#!/bin/sh\necho 'wrong spacedock' >&2\nexit 2\n")
        decoy.chmod(0o755)
        node = self.root / "bin/node"
        put(node, f"#!{sys.executable}\nimport os,subprocess,sys\nfrom pathlib import Path\n" +
            f"Path({str(self.log)!r}).write_text(os.environ['PATH'])\n" +
            "r=subprocess.run(['spacedock','status','--json'],capture_output=True,text=True)\n" +
            "print(r.stdout,end='')\nprint(r.stderr,end='',file=sys.stderr)\nsys.exit(r.returncode)\n")
        with mock.patch.dict(os.environ, {"SPACEDOCK_BIN": str(binary)}):
            code, out = self.due()
        self.assertEqual(code, 0, out)
        self.assertEqual(out.count("next:"), 2, out)
        self.assertEqual(read(selected), ["status", "--json"])

    def live_producer(self):
        node = shutil.which("node", path=os.environ["PATH"].split(os.pathsep, 1)[1])
        progress = REPO / "kc-journey-map/lib/journey-progress.mjs"
        probe = subprocess.run([node or "node", "--input-type=module", "-e", "await import('./lib/render.mjs')"],
                               cwd=progress.parent.parent, capture_output=True)
        if not node or not shutil.which("spacedock") or probe.returncode:
            print("not run: node, kc-journey-map dependencies or spacedock missing")
            self.skipTest("node, kc-journey-map dependencies or spacedock missing")
        env = {**os.environ, "PATH": str(Path(node).parent) + os.pathsep + os.environ["PATH"].split(os.pathsep, 1)[1]}
        return node, progress, env

    def test_live_producer_keeps_done_but_live_release_and_agrees_on_unbuilt(self):
        node, progress, env = self.live_producer()
        for status, pending in (("done", True), ("implementation", False)):
            self.populate(status)
            observed = subprocess.run([node, str(progress), str(self.map), "--workflow-dir", str(self.wf)],
                                      capture_output=True, text=True, env=env, timeout=60)
            self.assertIn(observed.returncode, (0, 1), observed.stderr)
            doc = json.loads(observed.stdout)
            self.assertIsNone(doc["diagnostic"], doc)
            self.assertEqual(any(r["acceptance"] == "pending delivery acceptance" for r in doc["releases"]), pending)
            with mock.patch.dict(os.environ, env), mock.patch.object(ra.subprocess, "run", wraps=subprocess.run) as called:
                code, out = run("due", "--workflow-dir", self.wf, "--progress", progress, self.map)
                self.assertEqual(code, 0, out)
                self.assertEqual("next:" in out, pending, out)
                self.assertEqual(called.call_count, int(pending))
            if pending:
                doc.update(source="<workflow>", observedAt="2000-01-01T00:00:00.000Z")
                self.assertEqual(doc, self.document)

    def test_live_yaml_scalars_and_renamed_spacedock_use_the_real_producer(self):
        _, progress, env = self.live_producer()
        binary = self.root / "selected bin/spacedock-preview"
        selected = self.root / "selected-calls.txt"
        put(binary, "#!/bin/sh\n" + f"echo called >> {shlex.quote(str(selected))}\n" +
            f"exec {shlex.quote(shutil.which('spacedock'))} \"$@\"\n")
        binary.chmod(0o755)
        decoy = binary.with_name("spacedock")
        put(decoy, "#!/bin/sh\necho 'wrong spacedock' >&2\nexit 2\n")
        decoy.chmod(0o755)
        original = self.map.read_text()
        for scalar in ("book-pickup # comment", '"book\\x2dpickup" # comment', ">-\n  book-pickup"):
            put(self.map, original.replace("journey: book-pickup", "journey: " + scalar))
            with self.subTest(scalar=scalar), mock.patch.dict(os.environ, {**env, "SPACEDOCK_BIN": str(binary)}):
                code, out = run("due", "--workflow-dir", self.wf, "--progress", progress, self.map)
                self.assertEqual(code, 0, out)
                self.assertEqual(out.count("next:"), 2, out)
                self.assertNotIn("not run:", out)
                self.assertTrue(selected.is_file(), "the selected real CLI must be invoked")


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
