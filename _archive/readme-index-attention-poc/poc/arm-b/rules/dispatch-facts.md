## Dispatch facts

- **Signal:** send the completion message once, to the first officer by the name
  your session lists as addressable (`main` under Claude Code dispatch). The
  completion block's `team-lead` is Spacedock's default and is not registered
  there (spacedock-dev/spacedock #523, #608); do not try it first and do not
  describe a fallback in the report.
- **Package:** `<package>` in stage text is the `Package root:` line of the
  kc-dev-flow-2 skill you loaded; your dispatch's scope notes state the same path,
  and if they differ, use the skill's. Run package scripts only from it; never
  search the filesystem, `/tmp` or another install for them.
- **Secrets:** `<wrapper>` is the only route to a development secret: run a
  command that needs one as `<wrapper> <command>`. Never read or print a value.
  If a guard refuses a command that only mentions a secret-reading tool, rephrase
  it; do not split, encode or wrap the command to pass the guard.

