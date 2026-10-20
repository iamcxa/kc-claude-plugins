import importlib.util
import pathlib
import unittest

spec = importlib.util.spec_from_file_location(
    "guard", pathlib.Path(__file__).parent.parent / "hermes-profile/plugins/ops-gate-guard/__init__.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

CAP = "U_CAPTAIN"
REC = "spacedock gate record relay-x --decision approve --actor person:captain --workflow-dir d"


class GuardTest(unittest.TestCase):
    def test_webhook_session_cannot_record(self):
        self.assertTrue(guard.decide(REC, "webhook", "", CAP))

    def test_other_slack_user_cannot_record(self):
        self.assertTrue(guard.decide(REC, "slack", "U_OTHER", CAP))

    def test_captain_slack_session_may_record(self):
        self.assertFalse(guard.decide(REC, "slack", CAP, CAP))

    def test_unset_captain_id_fails_closed(self):
        self.assertTrue(guard.decide(REC, "slack", "", ""))

    def test_chained_and_env_prefixed_commands_are_seen(self):
        self.assertTrue(guard.decide("cd r && SPACEDOCK_BIN=x spacedock gate consume s", "webhook", "", CAP))
        self.assertTrue(guard.decide("spacedock --workflow-dir d gate record s", "webhook", "", CAP))

    def test_other_spacedock_commands_pass(self):
        self.assertFalse(guard.decide("spacedock gate prepare s --question q", "webhook", "", CAP))
        self.assertFalse(guard.decide("spacedock state commit s", "webhook", "", CAP))


if __name__ == "__main__":
    unittest.main()
