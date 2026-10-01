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
        done = subprocess.run(["python3", SCRIPT, *args], capture_output=True, text=True)
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

            self.assertEqual(reserve(a), (0, "Migration: 0013\n"))
            a.write_text("## Number guards\nMigration: 0013\n")
            self.assertEqual(reserve(b), (0, "Migration: 0014\n"))
            self.assertEqual(reserve(a), (0, "Migration: 0013\n"))
            fx.commit("adrs", **{"docs__adr__0001-a.md": "x", "docs__adr__0003-c.md": "x"})
            self.assertEqual(reserve(b, "adr"), (0, "ADR: 0004\n"))

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

            self.assertEqual(reserve(loses), (0, "Migration: 0013\n"))
            loses.write_text("## Number guards\n")
            self.assertEqual(reserve(loses), (0, "Migration: 0014\n"))
            self.assertEqual(reserve(keeps), (0, "Migration: 0013\n"))


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


class MisconfigurationTests(unittest.TestCase):
    def test_a_db_surface_without_a_migrations_path_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as td:
            fx = base_repo(tmp)
            code, out = fx.run("check", "--repo", tmp, "--base", "main", "--head", "feature",
                               "--task", str(task_file(td, surfaces="db")))
            self.assertEqual(code, 2)
            self.assertIn("Surfaces: db but no migrations-path", out)

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
