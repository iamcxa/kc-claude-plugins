# GitHub App credential probe

Question: with only a GitHub App installation token, can an actor reach `main`? Expected: no.
Files: `app-permissions.json`, `ruleset-main.json`, `ruleset-ops.json`, `mint_token.sh`, `probe.sh`,
`credential_audit.sh`, `askpass.sh`. Nothing here has run against GitHub yet.

## Setup (the Captain, in his browser; then three API calls)

1. Scratch repository with one commit on its default branch and no other collaborator.
2. New GitHub App: webhook inactive; repository permissions Contents read and write, Pull requests read and write (Metadata read is added by GitHub); no Administration; installable on this account only. Generate a private key.
3. Install the App on the scratch repository only.
4. Move the downloaded key to `~/.config/ops-inbox-probe/app.pem` (directory 0700, file 0600).
5. Create both rulesets as the Captain: `gh api -X POST repos/OWNER/REPO/rulesets --input ruleset-main.json`, then `ruleset-ops.json`.

## Run

```
APP_ID=.. INSTALLATION_ID=.. KEY_FILE=~/.config/ops-inbox-probe/app.pem OWNER_REPO=OWNER/REPO \
  ./mint_token.sh ~/.config/ops-inbox-probe/installation-token
env -i PATH="$PATH" HOME="$(mktemp -d)" OWNER_REPO=OWNER/REPO \
  TOKEN_FILE=~/.config/ops-inbox-probe/installation-token ./probe.sh
```

`mint_token.sh` signs with the key through `openssl` and prints only the granted permissions and expiry.
`probe.sh` runs under an empty `HOME` and environment, reads the token file itself, prints one PASS or FAIL
line per check, and prints the token nowhere. The probe leaves its `ops/probe-*` branch and Draft PR
(the ops ruleset blocks deletion); delete the scratch repository afterwards.

Check ids match the task's acceptance criteria: AC-6 push to the default branch, AC-7 API merge, AC-8 self-approval,
AC-9 `ops/*` push and Draft PR, AC-10 no other credential and no Administration.
