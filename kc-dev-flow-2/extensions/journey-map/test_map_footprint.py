#!/usr/bin/env python3
import importlib.util
import io
import json
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("map_footprint", HERE / "map_footprint.py")
mf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mf)

TASK = """---
title: A sample task
status: implementation
{journey}gates:
    version: 1
    records:
        - id: gate:sample:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:sample-ideation-1
              briefing:
                room-ref: ./sample/review/ideation/briefing-1
              resolution:
                type: Resolution
                by: person:captain
                at: "2026-10-13T03:56:22Z"
                decision: approve
                reason: 'Captain 2026-10-13: 「發佈前要先備份資料」, then 「可以」 to the plan'
---

body

## FO alignment

Release: none
{declared}
## Captain amendments

### Amendment 1 — 2026-10-14, chat
Captain: 「保留六個月」 (in chat)
Supersedes: none
"""
JOURNEY = "journey: shop\njourney-release: r1\njourney-story: checkout\n"
SRC = "gate-attempt:sample-ideation-1"


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = mf.main([str(a) for a in argv])
    return code, out.getvalue(), err.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)

    def task(self, slug="sample", journey=JOURNEY, declared="", archived=False):
        folder = self.tmp / "_archive" if archived else self.tmp
        folder.mkdir(exist_ok=True)
        path = folder / f"{slug}.md"
        path.write_text(TASK.format(journey=journey, declared=declared))
        return path

    def add(self, path, **kw):
        args = {"question": "q1", "source": SRC, "words": "發佈前要先備份資料", "answer": "Back up first."}
        args.update(kw)
        flat = [str(path)]
        for k, v in args.items():
            flat += [f"--{k}", v]
        return run("add", *flat)


class AddTests(Base):
    def test_add_appends_one_v1_line_with_the_sources_date(self):
        path = self.task()
        code, _, _ = self.add(path)
        self.assertEqual(code, 0)
        lines = [json.loads(x) for x in (self.tmp / "sample" / "footprints.jsonl").read_text().splitlines()]
        self.assertEqual([(l["schema"], l["id"], l["date"], l["journey"], l["story"]) for l in lines],
                         [("journey-footprint/v1", "fp:sample:1", "2026-10-13", "shop", "checkout")])

    def test_a_paraphrase_is_refused_though_the_source_exists(self):
        code, _, err = self.add(self.task(), words="先備份資料再發佈")
        self.assertEqual(code, 1)
        self.assertIn("words are not inside the source text", err)

    def test_a_date_or_journey_that_differs_is_refused_naming_the_cause(self):
        path = self.task()
        code, _, err = self.add(path, date="2026-10-12")
        self.assertEqual((code, "differs from the source's 2026-10-13" in err), (1, True))
        code, _, err = self.add(path, journey="other")
        self.assertEqual((code, "differs from the task's 'shop'" in err), (1, True))
        self.assertFalse((self.tmp / "sample" / "footprints.jsonl").exists())

    def test_a_resolution_by_the_first_officer_is_not_a_source(self):
        path = self.task()
        path.write_text(path.read_text().replace("by: person:captain", "by: agent:first-officer"))
        code, _, err = self.add(path)
        self.assertEqual((code, "does not resolve" in err), (1, True))

    def test_an_amendment_is_a_source_and_an_unknown_source_is_refused(self):
        path = self.task()
        self.assertEqual(self.add(path, source="amendment:1", words="保留六個月")[0], 0)
        code, _, err = self.add(path, source="gate-attempt:nope")
        self.assertEqual((code, "does not resolve" in err), (1, True))

    def test_two_stories_with_the_same_question_id_take_separate_footprints(self):
        path = self.task(declared="Map footprints: 2 in footprints.jsonl\n")
        self.assertEqual(self.add(path)[0], 0)
        self.assertEqual(self.add(path, story="payment")[0], 0)
        self.assertEqual(self.add(path)[0], 1)
        self.assertEqual(run("check", path)[0], 0)


class CheckTests(Base):
    def test_a_journey_task_with_no_record_fails_and_a_task_without_a_story_passes(self):
        self.assertEqual(run("check", self.task())[0], 1)
        self.assertEqual(run("check", self.task("plain", journey="journey: shop\n"))[0], 0)

    def test_the_declared_count_must_equal_the_valid_lines(self):
        path = self.task(declared="Map footprints: 1 in footprints.jsonl\n")
        self.assertEqual(run("check", path)[0], 1)
        self.add(path)
        self.assertEqual(run("check", path)[0], 0)
        path.write_text(path.read_text().replace("1 in footprints", "2 in footprints"))
        self.assertEqual(run("check", path)[0], 1)

    def test_not_needed_needs_a_reason(self):
        self.assertEqual(run("check", self.task(declared="Map footprints: not needed: only approvals\n"))[0], 0)
        self.assertEqual(run("check", self.task(declared="Map footprints: not needed:\n"))[0], 1)

    def test_not_needed_with_a_valid_footprint_is_a_contradiction(self):
        path = self.task(declared="Map footprints: not needed: only approvals\n")
        self.add(path)
        code, _, err = run("check", path)
        self.assertEqual((code, "contradicts 1 valid" in err), (1, True))

    def test_an_edited_line_is_invalid_when_words_or_source_no_longer_match(self):
        path = self.task(declared="Map footprints: 1 in footprints.jsonl\n")
        self.add(path)
        fp = self.tmp / "sample" / "footprints.jsonl"
        for field, value in (("words", "改寫過的話"), ("source", "gate-attempt:gone"), ("date", "2026-01-01")):
            line = json.loads(fp.read_text())
            fp.write_text(json.dumps({**line, field: value}, ensure_ascii=False) + "\n")
            self.assertEqual(run("check", path)[0], 1, field)
            fp.write_text(json.dumps(line, ensure_ascii=False) + "\n")
        self.assertEqual(run("check", path)[0], 0)

    def test_another_major_is_invalid_growth_is_accepted_and_an_unknown_kind_is_skipped(self):
        path = self.task(declared="Map footprints: 1 in footprints.jsonl\n")
        self.add(path)
        fp = self.tmp / "sample" / "footprints.jsonl"
        good = json.loads(fp.read_text())
        extra = {**good, "id": "fp:sample:2", "future": "field"}
        fp.write_text(fp.read_text() + json.dumps({**good, "kind": "evidence"}, ensure_ascii=False) + "\n"
                      + json.dumps(extra, ensure_ascii=False) + "\n")
        path.write_text(path.read_text().replace("1 in footprints", "2 in footprints"))
        code, out, _ = run("check", path)
        self.assertEqual((code, "(1 skipped)" in out), (0, True))
        fp.write_text(json.dumps({**good, "schema": "journey-footprint/v2"}, ensure_ascii=False) + "\n")
        code, _, err = run("check", path)
        self.assertEqual((code, "journey-footprint/v2" in err), (1, True))


class AmendmentTests(Base):
    def test_an_amendment_with_no_captain_line_is_not_a_source_and_does_not_borrow_the_next(self):
        path = self.task(declared="Map footprints: 0 in footprints.jsonl\n")
        text = path.read_text().replace(
            "### Amendment 1 — 2026-10-14, chat\nCaptain: 「保留六個月」 (in chat)\n",
            "### Amendment 1 — 2026-10-14, chat\nNote: nobody spoke\n\n"
            "### Amendment 2 — 2026-10-20, chat\nCaptain: 「保留六個月」 (in chat)\n")
        path.write_text(text)
        task = mf.Task(path)
        self.assertNotIn("amendment:1", task.sources)
        self.assertEqual(task.sources["amendment:2"], ("2026-10-20", "「保留六個月」 (in chat)"))
        code, _, err = self.add(path, source="amendment:1", words="保留六個月")
        self.assertEqual((code, "does not resolve" in err), (1, True))
        self.assertEqual(self.add(path, source="amendment:2", words="保留六個月")[0], 0)


class AuditTests(Base):
    def setUp(self):
        super().setUp()
        (self.tmp / "README.md").write_text("---\ncommissioned-by: test\n---\n")

    def test_audit_needs_since_and_counts_unrecorded_and_invalid_from_the_cutover(self):
        self.task("a", archived=True)
        self.task("b", archived=True, declared="Map footprints: not needed: approvals only\n")
        self.assertEqual(run("audit", self.tmp)[0], 2)
        code, out, _ = run("audit", self.tmp, "--since", "2026-10-13")
        self.assertEqual((code, "unrecorded 1" in out, "invalid 0" in out), (1, True, True))
        code, out, _ = run("audit", self.tmp, "--since", "2026-10-15")
        self.assertEqual((code, "unrecorded 0" in out), (0, True))

    def test_audit_counts_a_bad_line_as_invalid_not_unrecorded(self):
        path = self.task("c", archived=True, declared="Map footprints: 1 in footprints.jsonl\n")
        folder = path.with_suffix("")
        folder.mkdir()
        (folder / "footprints.jsonl").write_text('{"schema": "journey-footprint/v2"}\n')
        code, out, _ = run("audit", self.tmp, "--since", "2026-10-13")
        self.assertEqual((code, "unrecorded 0" in out, "invalid 1" in out), (1, True, True))


    def test_a_declared_state_checkout_that_is_missing_is_an_error_naming_the_path(self):
        (self.tmp / "README.md").write_text("---\nstate: .spacedock-state\n---\n")
        code, out, err = run("audit", self.tmp, "--since", "2026-10-13")
        self.assertEqual((code, "unrecorded" in out, ".spacedock-state" in err), (2, False, True))
        (self.tmp / ".spacedock-state" / "_archive").mkdir(parents=True)
        self.assertEqual(run("audit", self.tmp, "--since", "2026-10-13")[0], 0)

    def test_a_path_that_is_not_a_workflow_directory_is_an_error_not_a_clean_audit(self):
        for target in (self.tmp / "no-such-dir", self.tmp / "README.md", self.tmp / "empty"):
            (self.tmp / "empty").mkdir(exist_ok=True)
            code, out, err = run("audit", target, "--since", "2026-10-13")
            self.assertEqual((code, "unrecorded" in out, str(target) in err), (2, False, True), target)

    def test_a_valid_workflow_with_no_archive_directory_is_a_stated_zero(self):
        code, out, _ = run("audit", self.tmp, "--since", "2026-10-13")
        self.assertEqual(code, 0)
        self.assertIn(f"archive none: {self.tmp / '_archive'} does not exist", out)
        self.assertIn("unrecorded 0", out)


class SchemaTests(Base):
    def copy_package(self):
        pkg = self.tmp / "pkg"
        (pkg / "extensions/journey-map").mkdir(parents=True)
        (pkg / "scripts").mkdir()
        shutil.copy(HERE / "map_footprint.py", pkg / "extensions/journey-map")
        shutil.copy(HERE / "contract-versions.json", pkg / "extensions/journey-map")
        shutil.copy(HERE.parent.parent / "scripts/decision_ledger.py", pkg / "scripts")
        return pkg / "extensions/journey-map"

    def schema(self, where):
        import subprocess
        done = subprocess.run(["python3", "-B", str(where / "map_footprint.py"), "schema", "journey-footprint"],
                              capture_output=True, text=True)
        return done.returncode, done.stdout, done.stderr

    def test_the_table_and_version_print_and_the_recorded_hash_holds(self):
        code, out, err = self.schema(HERE)
        self.assertEqual((code, err), (0, ""))
        self.assertTrue(out.startswith("journey-footprint 1.0.0\n"))
        self.assertIn("| `words` |", out)

    def test_an_edited_table_with_an_unchanged_version_fails_naming_the_schema(self):
        where = self.copy_package()
        script = where / "map_footprint.py"
        script.write_text(script.read_text().replace('("words",', '("quote",'))
        code, _, err = self.schema(where)
        self.assertEqual(code, 1)
        self.assertIn("journey-footprint: the field table changed but version 1.0.0 did not", err)

    def test_a_bumped_version_with_no_recorded_hash_fails(self):
        where = self.copy_package()
        versions = where / "contract-versions.json"
        versions.write_text(versions.read_text().replace('"current": "1.0.0"', '"current": "1.1.0"'))
        code, _, err = self.schema(where)
        self.assertEqual(code, 1)
        self.assertIn("current version 1.1.0 has no recorded hash", err)

    def test_the_history_footer_names_files_that_exist(self):
        footer = mf.FOOTER
        self.assertTrue((HERE.parent.parent / "CHANGELOG.md").is_file())
        self.assertIn("kc-dev-flow-2/CHANGELOG.md", footer)
        self.assertTrue(list((HERE.parents[2] / "docs/adr").glob(f"*-{mf.ADR_TITLE}.md")), mf.ADR_TITLE)
        self.assertIn("schema journey-footprint", footer)

    def test_the_extension_points_at_a_schema_command_that_runs_and_names_where_history_lives(self):
        import subprocess
        doc = " ".join((HERE / "EXTENSION.md").read_text().split())
        command = re.search(r"`python3 (<package>/extensions/journey-map/map_footprint\.py schema journey-footprint)`", doc)
        self.assertTrue(command, "EXTENSION.md must name the schema command")
        script = command.group(1).replace("<package>", str(HERE.parent.parent))
        done = subprocess.run(["python3", "-B", *script.split()], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        for pointer in ("CHANGELOG.md", "docs/adr", "Read the CHANGELOG when", "read the ADR before"):
            self.assertIn(pointer, done.stdout)
        for pointer in ("CHANGELOG", "ADR in the repository's `docs/adr/`", "Read the CHANGELOG when", "read the ADR before"):
            self.assertIn(pointer, doc)


if __name__ == "__main__":
    unittest.main()
