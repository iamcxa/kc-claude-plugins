import json
import os
import re
import time

_DECISION = re.compile(r"\bspacedock\b[^;&|\n]*\bgate\s+(record|consume|withdraw)\b")
_REFUSAL = "A gate decision is recorded only from the Captain's Slack session."


def decide(command, platform, user_id, captain_id):
    """Return True when the command is a gate decision this session may not make."""
    if not _DECISION.search(command or ""):
        return False
    return not (platform == "slack" and captain_id and user_id == captain_id)


def _log(entry):
    home = os.environ.get("HERMES_HOME", "")
    if home:
        with open(os.path.join(home, "ops-gate-guard.log"), "a") as fh:
            fh.write(json.dumps(entry) + "\n")


def _pre_tool_call(tool_name, args, **kwargs):
    command = (args or {}).get("command", "") if tool_name == "terminal" else ""
    if not _DECISION.search(command):
        return None
    from gateway.session_context import get_session_env

    platform = get_session_env("HERMES_SESSION_PLATFORM", "").lower()
    user_id = get_session_env("HERMES_SESSION_USER_ID", "")
    refused = decide(command, platform, user_id, os.environ.get("CAPTAIN_SLACK_USER_ID", ""))
    mode = os.environ.get("OPS_GUARD_MODE", "block")
    _log({"at": time.time(), "platform": platform, "user": user_id, "mode": mode,
          "refused": refused, "command": command[:300]})
    if refused and mode == "block":
        return {"action": "block", "message": _REFUSAL}
    return None


def register(ctx):
    ctx.register_hook("pre_tool_call", _pre_tool_call)
