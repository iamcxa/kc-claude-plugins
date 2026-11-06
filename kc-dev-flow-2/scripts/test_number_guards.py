from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = str(ROOT / "scripts/number_guards.py")
MIGRATIONS = "apps/api/migrations"
SLOTS = "-- capacity slots\n-- keep per shop\n-- see ADR\nCREATE TABLE slots (id int);\n"


class Fixture:
    def __init__(self, tmp):
        self.repo = tmp
        self.git("init", "-q", "--initial-branch=main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        self.git("config", "commit.gpgsign", "false")

    def git(self, *args):
        return subprocess.run(["git", "-C", self.repo, *args], check=True, capture_output=True, text=True).stdout.strip()

    def commit(self, message, **files):
        for name, text in files.items():
            path = Path(self.repo, name.replace("__", "/"))
            path.parent.mkdir(parents=True, exist_ok=True)
            if text is None:
                path.unlink()
            else:
                path.write_text(text)
        self.git("add", "-A")
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def run(self, *args):
        done = subprocess.run(["python3", "-B", SCRIPT, *args], capture_output=True, text=True)
        return done.returncode, done.stdout + done.stderr

    def check(self, *args, head="feature", task=None):
        extra = ["--task", str(task)] if task else []
        return self.run("check", "--repo", self.repo, "--migrations-path", MIGRATIONS, "--base", "main",
                        "--head", head, *extra, *args)


def base_repo(tmp, top=5):
    fx = Fixture(tmp)
    files = {f"{MIGRATIONS}__{n:04d}_m{n}.sql": "SELECT 1;\n" for n in range(1, top + 1)}
    files[f"{MIGRATIONS}__0005_m5.sql"] = SLOTS
    files[f"{MIGRATIONS}__meta___journal.json"] = '{"entries":[1]}\n'
    fx.commit("base", **files)
    fx.git("checkout", "-qb", "feature")
    return fx


def mig(n, name="new"):
    return f"{MIGRATIONS}__{n:04d}_{name}.sql"


def task_file(tmp, *lines, surfaces="none"):
    path = Path(tmp, "task.md")
    path.write_text(f"Surfaces: {surfaces}\n\n## Number guards\n" + "\n".join(lines) + "\n\n## Other\nMigration: 0099\n")
    return path


class ImmutableMigrationTests(unittest.TestCase):
    def test_a_comment_trim_of_a_base_migration_is_refused_and_a_new_migration_with_a_journal_entry_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = base_repo(tmp)
            fx.commit("trim", **{mig(5, "m5"): "CREATE TABLE slots (id int);\n", mig(6): "SELECT 2;\n",
                                 f"{MIGRATIONS}__meta___journal.json": '{"entries":[1,2]}\n'})
            code, out = fx.check()
            self.assertEqual(code, 1, out)
            self.assertIn("FAIL R1", out)
            self.assertIn("0005_m5.sql", out)
            self.assertNotIn("_journal.json", out)
            fx.git("checkout", "-q", "main")
            fx.git("checkout", "-qb", "fixed")
            fx.commit("new migration", **{mig(6): "SELECT 2;\n", f"{MIGRATIONS}__meta___journal.json": '{"entries":[1,2]}\n'})
            code, out = fx.check(head="fixed")
            self.assertEqual((code, "FAIL" in out), (0, False), out)

    def test_deleting_a_base_migration_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = base_repo(tmp)
            fx.commit("delete", **{mig(4, "m4"): None})
            code, out = fx.check()
            self.assertEqual(code, 1)
            self.assertIn("FAIL R1", out)
            self.assertIn("0004_m4.sql", out)


class AppliedFreezeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.fx = base_repo(self.tmp.name)
        self.applied = self.fx.commit("add 0006 and deploy", **{mig(6, "op"): "SELECT 6;\n"})
        self.task_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.task_dir.cleanup)
        self.line = f"Applied at: uat {self.applied}"

    def test_editing_an_unmerged_migration_recorded_as_applied_is_refused_and_unrecorded_is_not(self):
        self.fx.commit("edit", **{mig(6, "op"): "SELECT 66;\n"})
        recorded = task_file(self.task_dir.name, "Migration: 0006", self.line)
        code, out = self.fx.check(task=recorded)
        self.assertEqual(code, 1, out)
        self.assertIn("FAIL R2", out)
        self.assertIn(self.applied[:12], out)
        self.assertIn("revert it and add a new migration", out)
        unrecorded = task_file(self.task_dir.name, "Migration: 0006")
        self.assertEqual(self.fx.check(task=unrecorded)[0], 0)

    def test_a_not_applied_line_in_place_of_the_record_leaves_the_edit_unfrozen(self):
        self.fx.commit("edit", **{mig(6, "op"): "SELECT 66;\n"})
        for line in (f"Not applied: uat {self.applied} - push rejected", f"Not applied: uat {self.applied}"):
            code, out = self.fx.check(task=task_file(self.task_dir.name, "Migration: 0006", line))
            self.assertEqual(code, 0, out)
        code, out = self.fx.check(task=task_file(self.task_dir.name, "Migration: 0006", self.line))
        self.assertEqual((code, "FAIL R2" in out), (1, True), out)

    def test_renumbering_an_applied_migration_is_refused(self):
        self.fx.commit("renumber", **{mig(6, "op"): None, mig(8, "op"): "SELECT 6;\n"})
        recorded = task_file(self.task_dir.name, "Migration: 0006", "Migration: 0008", self.line)
        code, out = self.fx.check(task=recorded)
        self.assertEqual(code, 1, out)
        self.assertIn("FAIL R2", out)

    def test_an_applied_task_whose_number_the_base_took_renumbers_once_its_line_is_replaced(self):
        self.fx.git("checkout", "-q", "main")
        self.fx.commit("other landed", **{mig(6, "other"): "SELECT 2;\n"})
        self.fx.git("checkout", "-q", "feature")
        code, out = self.fx.check(task=task_file(self.task_dir.name, "Migration: 0006", self.line))
        self.assertEqual((code, "FAIL R3" in out), (1, True), out)
        self.fx.commit("renumber", **{mig(6, "op"): None, mig(7, "op"): "SELECT 6;\n"})
        code, out = self.fx.check(task=task_file(self.task_dir.name, "Migration: 0007", self.line))
        self.assertEqual((code, "FAIL R2" in out), (1, True), out)
        reset = f"Not applied: uat {self.applied} - database reset"
        self.assertEqual(self.fx.check(task=task_file(self.task_dir.name, "Migration: 0007", reset))[0], 0)

    def test_a_recorded_commit_absent_from_the_clone_is_a_configuration_error(self):
        task = task_file(self.task_dir.name, "Migration: 0006", "Applied at: uat " + "0" * 40)
        code, out = self.fx.check(task=task)
        self.assertEqual(code, 2)
        self.assertIn("cannot resolve applied commit (uat)", out)


class ReserveTests(unittest.TestCase):
    def test_reserve_never_collides_and_never_fills_a_gap(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as state:
            fx = base_repo(tmp, top=12)
            fx.git("checkout", "-q", "main")
            a, b = Path(state, "a.md"), Path(state, "b.md")
            a.write_text("")
            b.write_text("")

            def reserve(task, kind="migration"):
                return fx.run("reserve", "--kind", kind, "--repo", tmp, "--migrations-path", MIGRATIONS,
                              "--base", "main", "--state-dir", state, "--task", str(task))

            self.assertEqual(reserve(a)[0], 0)
            self.assertIn("Migration: 0013\n", reserve(a)[1])
            a.write_text("## Number guards\nMigration: 0013\n")
            self.assertIn("Migration: 0014\n", reserve(b)[1])
            self.assertIn("Migration: 0013\n", reserve(a)[1])
            fx.commit("adrs", **{"docs__adr__0001-a.md": "x", "docs__adr__0003-c.md": "x"})
            self.assertIn("ADR: 0004\n", reserve(b, "adr")[1])

    def test_a_task_that_loses_a_collision_reserves_again_above_the_one_that_keeps_its_number(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as state:
            fx = base_repo(tmp, top=12)
            fx.git("checkout", "-q", "main")
            keeps, loses = Path(state, "keeps.md"), Path(state, "loses.md")
            keeps.write_text("## Number guards\nMigration: 0013\nApplied at: uat " + "a" * 40 + "\n")
            loses.write_text("## Number guards\nMigration: 0013\n")

            def reserve(task):
                return fx.run("reserve", "--kind", "migration", "--repo", tmp, "--migrations-path", MIGRATIONS,
                              "--base", "main", "--state-dir", state, "--task", str(task))

            self.assertIn("Migration: 0013\n", reserve(loses)[1])
            loses.write_text("## Number guards\n")
            self.assertIn("Migration: 0014\n", reserve(loses)[1])
            self.assertIn("Migration: 0013\n", reserve(keeps)[1])


class RecheckTests(unittest.TestCase):
    def test_a_number_taken_on_the_base_after_reservation_is_refused_and_a_renumber_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as td:
            fx = base_repo(tmp, top=12)
            fx.commit("mine", **{mig(13, "mine"): "SELECT 1;\n"})
            fx.git("checkout", "-q", "main")
            fx.commit("other landed", **{mig(13, "other"): "SELECT 2;\n"})
            fx.git("checkout", "-q", "feature")
            code, out = fx.check(task=task_file(td, "Migration: 0013"))
            self.assertEqual(code, 1, out)
            self.assertIn("FAIL R3", out)
            self.assertIn("0013_other.sql", out)
            fx.commit("renumber", **{mig(13, "mine"): None, mig(14, "mine"): "SELECT 1;\n"})
            self.assertEqual(fx.check(task=task_file(td, "Migration: 0014"))[0], 0)

    def test_a_migration_number_below_the_base_maximum_is_out_of_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = base_repo(tmp)
            fx.git("checkout", "-q", "main")
            fx.commit("base skips 6", **{mig(7, "other"): "SELECT 2;\n"})
            fx.git("checkout", "-q", "feature")
            fx.commit("gap filler", **{mig(6, "late"): "SELECT 1;\n"})
            code, out = fx.check()
            self.assertEqual(code, 1)
            self.assertIn("not above the base maximum 0007", out)

    def test_an_added_number_the_task_did_not_reserve_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as td:
            fx = base_repo(tmp)
            fx.commit("unreserved", **{mig(6, "op"): "SELECT 1;\n"})
            code, out = fx.check(task=task_file(td, "Migration: 0007"))
            self.assertEqual(code, 1, out)
            self.assertIn("FAIL R4", out)
            self.assertIn("R4 skipped", fx.check()[1])

    def test_an_added_adr_number_the_task_did_not_reserve_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as td:
            fx = base_repo(tmp)
            fx.commit("adr", **{"docs__adr__0002-mine.md": "x"})
            code, out = fx.check(task=task_file(td, "ADR: 0003"))
            self.assertEqual(code, 1, out)
            self.assertIn("FAIL R4", out)
            self.assertIn("0002-mine.md", out)
            self.assertEqual(fx.check(task=task_file(td, "ADR: 0002"))[0], 0)

    def test_a_number_written_outside_the_number_guards_section_reserves_nothing(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as td:
            fx = base_repo(tmp)
            fx.commit("outside", **{mig(99, "op"): "SELECT 1;\n"})
            code, out = fx.check(task=task_file(td, "Migration: 0006"))
            self.assertEqual(code, 1, out)
            self.assertIn("FAIL R4", out)

    def test_an_added_adr_number_already_on_the_base_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as td:
            fx = base_repo(tmp)
            fx.git("checkout", "-q", "main")
            fx.commit("adr 2 landed", **{"docs__adr__0001-a.md": "x", "docs__adr__0002-b.md": "x"})
            fx.git("checkout", "-q", "feature")
            fx.commit("adr 2 mine", **{"docs__adr__0002-mine.md": "x"})
            code, out = fx.check(task=task_file(td, "ADR: 0002"))
            self.assertEqual(code, 1, out)
            self.assertIn("FAIL R5", out)
            self.assertIn("0002-b.md", out)


class PocFreezeTests(unittest.TestCase):
    def poc_task(self, tmp, profile="poc"):
        path = Path(tmp, "task.md")
        path.write_text(f"---\nprofile: {profile}\n---\n\n## Number guards\n")
        return path

    def test_any_change_under_the_migrations_directory_fails_r6_for_a_poc_task_and_names_the_path(self):
        changes = {
            "add": {mig(6, "poc"): "SELECT 2;\n"},
            "edit": {mig(5, "m5"): "SELECT 9;\n"},
            "delete": {mig(4, "m4"): None},
            "journal": {f"{MIGRATIONS}__meta___journal.json": '{"entries":[1,2]}\n'},
            "snapshot": {f"{MIGRATIONS}__meta__0005_snapshot.json": "{}\n"},
        }
        for name, files in changes.items():
            with self.subTest(change=name), tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as td:
                fx = base_repo(tmp)
                fx.commit(name, **files)
                code, out = fx.check(task=self.poc_task(td))
                self.assertEqual(code, 1, out)
                for path in files:
                    self.assertIn(f"FAIL R6: {path.replace('__', '/')}", out)
                self.assertIn("a POC task changes none of it", out)

    def test_no_r6_for_a_non_poc_task_for_no_change_or_for_a_migration_that_landed_on_the_base_later(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as td:
            fx = base_repo(tmp)
            journal = {f"{MIGRATIONS}__meta___journal.json": '{"entries":[1,2]}\n'}
            fx.commit("journal", **journal)
            self.assertEqual(fx.check(task=self.poc_task(td, "pilot"))[0], 0)
            fx.git("reset", "-q", "--hard", "main")
            self.assertEqual(fx.check(task=self.poc_task(td))[0], 0)
            fx.git("checkout", "-q", "main")
            fx.commit("later base migration", **{mig(6, "later"): "SELECT 3;\n"})
            fx.git("checkout", "-q", "feature")
            fx.commit("unrelated", other="x")
            code, out = fx.check(task=self.poc_task(td))
            self.assertEqual(code, 0, out)
            fx.commit("journal", **journal)
            code, out = fx.check(task=self.poc_task(td))
            self.assertEqual((code, "_journal.json" in out, "0006_later" in out), (1, True, False), out)

    def test_a_poc_task_without_a_migrations_path_is_skipped_and_exits_0(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as td:
            fx = base_repo(tmp)
            fx.commit("add", **{mig(6, "poc"): "SELECT 2;\n"})
            code, out = fx.run("check", "--repo", tmp, "--base", "main", "--head", "feature",
                               "--task", str(self.poc_task(td)))
            self.assertEqual(code, 0, out)
            self.assertIn("migration guard skipped", out)


class NoMigrationsDeclaredTests(unittest.TestCase):
    def run_none(self, fx, task, *args):
        return fx.run("check", "--repo", fx.repo, "--migrations-path", "none", "--base", "main", "--head", "feature",
                      "--task", str(task), *args)

    def test_a_db_task_on_a_clean_candidate_passes_with_the_skip_line_and_the_readme_value_is_read(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as wf:
            fx = Fixture(tmp)
            fx.commit("base", app="x")
            fx.git("checkout", "-qb", "feature")
            fx.commit("work", app="y")
            task = task_file(td, surfaces="db")
            code, out = self.run_none(fx, task)
            self.assertEqual(code, 0, out)
            self.assertIn("migration guard skipped: README declares migrations-path: none", out)
            self.assertIn("PASS: no findings", out)
            Path(wf, "README.md").write_text("---\ntrunk: main\n# no migration files\nmigrations-path: none\n---\n")
            code, out = fx.run("check", "--repo", tmp, "--workflow-dir", wf, "--head", "feature", "--task", str(task))
            self.assertEqual((code, "README declares migrations-path: none" in out), (0, True), out)

    def test_the_adr_rules_still_run_for_a_db_task(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as td:
            fx = Fixture(tmp)
            fx.commit("base", **{"docs__adr__0001-first.md": "x"})
            fx.git("checkout", "-qb", "feature")
            fx.commit("clash", **{"docs__adr__0001-second.md": "x"})
            code, out = self.run_none(fx, task_file(td, "ADR: 0001", surfaces="db"))
            self.assertEqual((code, "FAIL R5" in out), (1, True), out)

    def test_an_added_numbered_sql_file_fails_r7_for_a_poc_and_a_non_poc_task_and_other_changes_do_not(self):
        for profile in ("pilot", "poc"):
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as td:
                fx = Fixture(tmp)
                fx.commit("base", **{"db__old__0001_old.sql": "x"})
                fx.git("checkout", "-qb", "feature")
                fx.commit("edit and unrelated sql", **{"db__old__0001_old.sql": "y", "db__seed.sql": "z"})
                task = Path(td, "task.md")
                task.write_text(f"---\nprofile: {profile}\n---\n\nSurfaces: db\n")
                code, out = self.run_none(fx, task)
                self.assertEqual((code, "FAIL R7" in out), (0, False), out)
                fx.commit("added", **{"db__migs__0002_x.sql": "x"})
                code, out = self.run_none(fx, task)
                self.assertEqual((code, "FAIL R7: db/migs/0002_x.sql" in out), (1, True), out)

    def test_reserve_refuses_a_migration_number_under_none_and_still_prints_the_next_adr_number(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as state:
            fx = Fixture(tmp)
            fx.commit("base", **{"docs__adr__0001-a.md": "x"})
            task = Path(state, "t.md")
            task.write_text("")

            def reserve(kind):
                return fx.run("reserve", "--kind", kind, "--repo", tmp, "--migrations-path", "none", "--base", "main",
                              "--state-dir", state, "--task", str(task))

            code, out = reserve("migration")
            self.assertEqual((code, "no migration number to reserve" in out, "no migration file matching" in out),
                             (2, True, False), out)
            self.assertIn("ADR: 0002\n", reserve("adr")[1])


class HelpTests(unittest.TestCase):
    def test_help_names_every_rule_from_r1_to_r8_and_holder_sources(self):
        done = subprocess.run(["python3", "-B", SCRIPT, "--help"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        rules = done.stdout.split("Limits:")[0]
        for n in range(1, 9):
            self.assertRegex(rules, rf"\bR{n} ")
        for source in ("*.md", "*/index.md", "origin/spacedock-state/*"):
            self.assertIn(source, done.stdout)


class CrossWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        origin = root / "origin"
        origin.mkdir()
        self.origin = Fixture(str(origin))
        self.origin.commit("base", **{"docs__adr__0058-old.md": "x", "docs__adr__0059-old.md": "x"})
        self.origin.git("checkout", "-q", "--orphan", "spacedock-state/dev2")
        self.origin.git("rm", "-rf", ".")
        self.origin.commit("holders", **{
            "gate-presentation.md": "## Number guards\nADR: 0060\n",
            "rel__index.md": "## Number guards\nADR: 0057\nMigration: 0070\n",
            "_archive__old.md": "## Number guards\nADR: 0099\n",
            "rel__review__notes.md": "## Number guards\nADR: 0098\n",
        })
        self.origin.git("checkout", "-q", "main")
        self.repo = str(root / "second")
        subprocess.run(["git", "clone", "-q", "--single-branch", "-b", "main", str(origin), self.repo],
                       check=True, capture_output=True)
        self.fx = Fixture(self.repo)
        self.workflow = root / "workflow" / "dev2"
        self.state = self.workflow / "st"
        self.state.mkdir(parents=True)
        self.state_fx = Fixture(str(self.state))
        (self.workflow / "README.md").write_text("---\nstate: st\ntrunk: main\n---\n")
        self.task = self.state / "slice3.md"
        self.task.write_text("## Number guards\n")

    def run_guard(self, command, *extra):
        return subprocess.run(
            ["python3", "-B", SCRIPT, command, "--repo", self.repo,
             "--workflow-dir", str(self.workflow), "--task", str(self.task), *extra],
            capture_output=True, text=True)

    def reserve(self, *extra):
        return self.run_guard("reserve", "--kind", "adr", *extra)

    def candidate(self, number=60):
        self.task.write_text(f"## Number guards\nADR: {number:04d}\n")
        self.fx.git("checkout", "-qb", "feature")
        self.fx.commit("candidate", **{f"docs__adr__{number:04d}-distinct.md": "x"})

    def test_single_branch_clone_fetches_foreign_holder_at_reserve(self):
        self.assertNotIn("origin/spacedock-state/", self.fx.git("branch", "-r"))
        done = self.reserve()
        self.assertEqual((done.returncode, done.stdout), (0, "ADR: 0061\n"), done.stderr)
        self.assertIn("origin/spacedock-state/dev2", self.fx.git("branch", "-r"))

    def test_deleted_origin_state_branch_releases_its_adr_number(self):
        done = self.reserve()
        self.assertEqual((done.returncode, done.stdout), (0, "ADR: 0061\n"), done.stderr)
        self.assertIn("origin/spacedock-state/dev2", self.fx.git("branch", "-r"))
        self.origin.git("branch", "-D", "spacedock-state/dev2")
        done = self.reserve()
        self.assertEqual((done.returncode, done.stdout), (0, "ADR: 0060\n"), done.stderr)
        self.assertNotIn("origin/spacedock-state/dev2", self.fx.git("branch", "-r"))
        self.assertIn("origin/main", self.fx.git("branch", "-r"))
        self.candidate()
        done = self.run_guard("check")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("PASS: no findings", done.stdout)

    def test_merge_ask_refuses_held_number_and_accepts_free_number(self):
        self.candidate()
        done = self.run_guard("check")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("FAIL R8: docs/adr/0060-distinct.md: 0060 is held by "
                      "origin/spacedock-state/dev2:gate-presentation.md; "
                      "delete this task's ADR: line, run reserve again and renumber", done.stdout)
        self.fx.git("checkout", "-qb", "free", "main")
        self.fx.commit("free", **{"docs__adr__0061-free.md": "x"})
        self.task.write_text("## Number guards\nADR: 0061\n")
        done = self.run_guard("check")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("PASS: no findings", done.stdout)

    def test_own_folder_holder_counts_at_reserve_and_check(self):
        self.origin.git("branch", "-D", "spacedock-state/dev2")
        folder = self.state / "rel"
        folder.mkdir()
        (folder / "index.md").write_text("## Number guards\nADR: 0060\n")
        done = self.reserve()
        self.assertEqual((done.returncode, done.stdout), (0, "ADR: 0061\n"), done.stderr)
        self.candidate()
        done = self.run_guard("check")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(f"0060 is held by {(folder / 'index.md').resolve()}", done.stdout)

    def test_remote_folder_holder_counts_and_archive_and_review_do_not(self):
        self.origin.git("checkout", "-q", "spacedock-state/dev2")
        self.origin.commit("folder holder", **{"rel__index.md": "## Number guards\nADR: 0062\nMigration: 0070\n"})
        self.origin.git("checkout", "-q", "main")
        done = self.reserve()
        self.assertEqual((done.returncode, done.stdout), (0, "ADR: 0063\n"), done.stderr)
        self.fx.commit("migration base", **{"migrations__0001_first.sql": "x"})
        done = self.reserve("--kind", "migration", "--migrations-path", "migrations", "--base", "HEAD")
        self.assertEqual((done.returncode, done.stdout), (0, "Migration: 0071\n"), done.stderr)

    def test_own_task_pushed_copy_is_excluded_but_sibling_on_own_branch_counts(self):
        self.state_fx.git("remote", "add", "origin", self.origin.repo)
        self.task.rename(self.state / "gate-presentation.md")
        self.task = self.state / "gate-presentation.md"
        self.candidate()
        done = self.run_guard("check")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.origin.git("checkout", "-q", "spacedock-state/dev2")
        self.origin.commit("sibling", **{"other.md": "## Number guards\nADR: 0060\n"})
        self.origin.git("checkout", "-q", "main")
        done = self.run_guard("check")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("origin/spacedock-state/dev2:other.md", done.stdout)

    def test_no_origin_same_basename_and_slug_is_foreign(self):
        self.task.rename(self.state / "gate-presentation.md")
        self.task = self.state / "gate-presentation.md"
        self.candidate()
        done = self.run_guard("check")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("origin/spacedock-state/dev2:gate-presentation.md", done.stdout)

    def test_explicit_state_branch_excludes_only_own_task(self):
        self.origin.git("branch", "-m", "spacedock-state/dev2", "spacedock-state/unique")
        (self.workflow / "README.md").write_text(
            "---\nstate: st\ntrunk: main\nstate-branch: spacedock-state/unique\n---\n")
        self.state_fx.git("remote", "add", "origin", self.origin.repo)
        self.task.rename(self.state / "gate-presentation.md")
        self.task = self.state / "gate-presentation.md"
        self.candidate()
        done = self.run_guard("check")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_number_already_on_base_gets_r5_without_r8(self):
        self.candidate()
        self.fx.git("checkout", "-q", "main")
        self.fx.commit("landed", **{"docs__adr__0060-landed.md": "x"})
        done = self.run_guard("check", "--head", "feature", "--base", "main")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("FAIL R5", done.stdout)
        self.assertNotIn("FAIL R8", done.stdout)

    def test_blind_read_warnings_go_to_stderr_and_cached_holders_still_count(self):
        done = self.reserve()
        self.assertEqual((done.returncode, done.stdout), (0, "ADR: 0061\n"), done.stderr)
        self.assertIn("state checkout has no origin; no other workflow sees these reservations", done.stderr)
        self.fx.git("remote", "set-url", "origin", str(Path(self.tmp.name) / "missing"))
        done = self.reserve()
        self.assertEqual((done.returncode, done.stdout), (0, "ADR: 0061\n"), done.stderr)
        self.assertIn("state fetch failed; reading local origin/spacedock-state/* refs only", done.stderr)
        self.candidate()
        done = self.run_guard("check")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("FAIL R8", done.stdout)
        self.assertIn("state fetch failed; reading local origin/spacedock-state/* refs only", done.stderr)


class MisconfigurationTests(unittest.TestCase):
    def test_a_db_surface_without_a_migrations_path_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as td:
            fx = base_repo(tmp)
            code, out = fx.run("check", "--repo", tmp, "--base", "main", "--head", "feature",
                               "--task", str(task_file(td, surfaces="db")))
            self.assertEqual(code, 2)
            self.assertIn("Surfaces: db but no migrations-path", out)
            self.assertIn("migrations-path: <directory>", out)
            self.assertIn("migrations-path: none", out)

    def test_no_db_surface_and_no_key_skips_loudly(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = base_repo(tmp)
            code, out = fx.run("check", "--repo", tmp, "--base", "main", "--head", "feature")
            self.assertEqual(code, 0)
            self.assertIn("migration guard skipped: no migrations-path declared", out)

    def test_a_declared_path_absent_at_the_base_or_without_migration_files_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = base_repo(tmp)
            code, out = fx.run("check", "--repo", tmp, "--migrations-path", "nowhere/migrations",
                               "--base", "main", "--head", "feature")
            self.assertEqual((code, "no migration file matching" in out), (2, True), out)
            fx.commit("readme only", **{"docs__README.md": "x"})
            code, out = fx.run("check", "--repo", tmp, "--migrations-path", "docs", "--base", "main", "--head", "feature")
            self.assertEqual((code, "no migration file matching" in out), (2, True), out)

    def test_an_unresolvable_ref_exits_2_and_names_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = base_repo(tmp)
            code, out = fx.check("--base", "no-such-ref")
            self.assertEqual(code, 2)
            self.assertIn("no-such-ref", out)

    def test_the_workflow_readme_supplies_trunk_and_migrations_path(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as wf:
            fx = base_repo(tmp)
            fx.commit("trim", **{mig(5, "m5"): "CREATE TABLE slots (id int);\n"})
            Path(wf, "README.md").write_text(f"---\ntrunk: main\nmigrations-path: {MIGRATIONS}\n---\n# wf\n")
            code, out = fx.run("check", "--repo", tmp, "--workflow-dir", wf, "--head", "feature")
            self.assertEqual((code, "FAIL R1" in out), (1, True), out)


if __name__ == "__main__":
    unittest.main()
