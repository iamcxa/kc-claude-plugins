import sys, unittest
sys.path.insert(0, sys.argv[1])
sys.argv = sys.argv[:1]
import test_delivery_gate as t

class RemovedScratchInReport(t.TaskFolderCaptainTests):
    def test_report_naming_removed_tmp_scratch(self):
        gone = "/tmp/ccx-ideation-removed-scratch-worktree"
        report = f"- DONE: cleanup\n  removed the scratch worktree {gone} as told\n"
        run = self.run_question(report)
        print("report names removed /tmp path -> exit", run.returncode, "| S4 in output:", "S4" in run.stdout)
        self.assertEqual(run.returncode, 0, run.stdout)
        run = self.run_question(report, message=f"Review this candidate. Read {gone}")
        print("FO message names the same path -> exit", run.returncode, "|", [l for l in run.stdout.splitlines() if "S4" in l])
        self.assertEqual(run.returncode, 1, run.stdout)

if __name__ == "__main__":
    unittest.main(defaultTest="RemovedScratchInReport", verbosity=1)
