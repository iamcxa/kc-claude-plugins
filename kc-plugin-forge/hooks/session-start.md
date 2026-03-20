---
event: SessionStart
---

Check if the working tree has uncommitted changes to plugin-related files. If so, remind the user to run forge validation.

```bash
# Find plugin-related modifications in all git repos under the working directory
DIRTY_PLUGIN_FILES=$(git diff --name-only HEAD 2>/dev/null | grep -E '(skills/|agents/|\.claude-plugin/|hooks/)' | head -10)
```

If `DIRTY_PLUGIN_FILES` is non-empty, output:

```
forge hint: detected uncommitted plugin changes:
{list of files, max 5}

Consider running `/kc-plugin-forge validate-only` before committing.
```

If no plugin-related changes are found, output nothing (silent).
