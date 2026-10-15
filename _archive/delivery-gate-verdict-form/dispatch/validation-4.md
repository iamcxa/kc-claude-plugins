# validation-4

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README); worker spacedock-ensign-delivery-gate-verdict-form-validation-c4, fresh
Candidate: aa6fcc91df7159cf8cc28ea2d15b532a064f6112
Model: sonnet
Codex round 4 requested at dispatch.

## Checklist

Independent verdict on #647 head aa6fcc91 against AC-9 to AC-14 (Captain amendment 2; AC-1 to AC-8 are superseded), re-running each evidence command and at least one falsifier per criterion yourself, including the observer-before-merge-guard replay on a scratch copy, the highest-numbered-record choice (validation-10 over validation-2), a line under a heading, an older record rescuing a newer one, and a REJECTED report with a matching Candidate line; judge whether the 84 to 57 word drop of the merge-ask passage and the dropped 26-word sentence lose any rule the check does not now enforce
Run the candidate's own kc-dev-flow-2/scripts/delivery_gate.py check on this task file (the latest validation dispatch record of delivery-gate-verdict-form carries a Candidate line for this head) with --pr iamcxa/kc-claude-plugins#647, once with live gh and once with a deliberately different --head, recording both outputs and exit codes
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/adr_lint.py docs/adr --since c545b896 with its exit code; your verdict, naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #647, head aa6fcc91df7159cf8cc28ea2d15b532a064f6112, base origin/main c545b896. Approved design: `## Design` and AC-9 to AC-14 in the task file, ideation approved under Captain amendment 2. The four verdict-parsing files are restored to base first (ceebf624), then the design (aa6fcc91). Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> aa6fcc91df7159cf8cc28ea2d15b532a064f6112`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO. Read archived and adopter state only through read-only commands.

Run kc-dev-flow-2/scripts/lint-skills.py and kc-dev-flow-2/scripts/delivery_gate.py from the candidate checkout, not from the package root: the installed 0.22.1 copy of the lint reads the cached tree and exits 1 for a missing skill-frontmatter-lint.sh (implementation report). kc-dev-flow-2/scripts/test_sd_dispatch.py needs --sd-plugin-root; name the root and binary you use.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Run each suite and mutation with a time cap, and remove every throwaway worktree you add before reporting. The minimal acceptance script must run unchanged in a fresh shell, name any checkout or install it needs (including which spacedock binary, if any) and write any package script as its full path; FO will run it exactly as written before the gate.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
