# Connect a project to its ops inbox (runbook, r1)

Run the steps in order. A step marked CAPTAIN ONLY touches an App, a key, a secret, a webhook, a ruleset or a merge; nobody else runs it. Each step names the read-back rows that prove it; S13 reads all of them.

Set these once in the shell you use, from a checkout of kc-claude-plugins at the commit you will pin (`SHA`):

    P=owner/project                          # the project repository
    T=owner/project-ops-trigger              # the trigger repository this runbook creates (S1); it holds only ops-event.yml
    SITE=project-ops-inbox                   # the Netlify site name (S2)
    INBOX=https://$SITE.netlify.app/inbox
    CAPTAIN=your-github-login                # the only login whose review records a gate
    SHA=$(git rev-parse HEAD)                # a commit of kc-claude-plugins that holds kc-ops-inbox; merged to its default branch first
    RELAY_CHECKOUT=~/path/to/project         # your clone of $P, linked to the project's own Netlify site if it has one

Secrets never go on a command line you share: `netlify env:set` takes its value as an argument, so S5 to S7 run it through a variable that you read with `read -rs` and unset afterwards.

## S1 · AGENT MAY RUN · Create the trigger repository and its one workflow

The trigger repository is private and holds only `ops-event.yml`, pinned to `$SHA`, so the inbox's credential can start nothing else.

    gh repo create $T --private --add-readme
    sed "s/__KC_OPS_INBOX_SHA__/$SHA/" kc-ops-inbox/trigger/ops-event.yml | base64 | tr -d '\n' > /tmp/ops-event.b64
    gh api -X PUT repos/$T/contents/.github/workflows/ops-event.yml -f message="add ops-event" -f content="$(cat /tmp/ops-event.b64)"

Read back by: R1 R2

## S2 · AGENT MAY RUN · Create the inbox site and link this folder to it

    netlify sites:create --name $SITE
    netlify link --name $SITE

Read back by: R3

## S3 · CAPTAIN ONLY · Register the dispatch App (in the browser)

Actions write only; install it on the trigger repository only, never on the project. Note its App ID and installation ID.

    open "https://github.com/settings/apps/new?name=$SITE-dispatch&public=false&webhook_active=false&url=https://github.com/$P&actions=write"
    # on the page: Create GitHub App > Generate a private key > Install App > Only select repositories > $T > Install

Read back by: R7 R8

## S4 · CAPTAIN ONLY · Register the agent App (in the browser)

Contents and pull requests write; install it on the project only. Note its Client ID.

    open "https://github.com/settings/apps/new?name=$SITE-agent&public=false&webhook_active=false&url=https://github.com/$P&contents=write&pull_requests=write"
    # on the page: Create GitHub App > Generate a private key > Install App > Only select repositories > $P > Install

Read back by: R9

## S5 · CAPTAIN ONLY · Store the two App keys

Then delete the two downloaded key files from your disk (not read back).

    netlify env:set DISPATCH_APP_PRIVATE_KEY "$(cat ~/Downloads/$SITE-dispatch.*.private-key.pem)" --secret
    gh secret set OPS_AGENT_APP_PRIVATE_KEY -R $T < ~/Downloads/$SITE-agent.*.private-key.pem

Read back by: R10

## S6 · CAPTAIN ONLY · Create the signing keys and store the model token

The inbox holds a list of keys, so a key can sign only what it lists (D5): one key for `prod`, one for `preview` and `dev`, and one for the read-back's own self-test. The Captain creates all three; each value goes only to the places named here, never into a repository. `OPS_INBOX_SECRET` is a placeholder: use the variable name the producer's emitter reads. `OPS_KEYS` names each key, its secret variable and its scope, and holds no value.

| Key | Secret variable on the inbox | Signs | Value also goes to |
| --- | --- | --- | --- |
| relay-prod | `KEY_RELAY_PROD` | environment `prod`, sources `urn:relay:` and `urn:sentry:` | the producer's production context |
| relay-preview | `KEY_RELAY_PREVIEW` | environments `preview` and `dev`, source `urn:relay:` | the producer's deploy-preview context |
| readback | `KEY_READBACK` | environment `prod`, source `urn:ops-inbox:` | your secrets wrapper as `OPS_READBACK_SECRET` |

    V=whsec_$(openssl rand -base64 24); netlify env:set KEY_RELAY_PROD "$V" --secret
    (cd $RELAY_CHECKOUT && netlify env:set OPS_INBOX_SECRET "$V" --secret --context production)
    V=whsec_$(openssl rand -base64 24); netlify env:set KEY_RELAY_PREVIEW "$V" --secret
    (cd $RELAY_CHECKOUT && netlify env:set OPS_INBOX_SECRET "$V" --secret --context deploy-preview)
    V=whsec_$(openssl rand -base64 24); netlify env:set KEY_READBACK "$V" --secret; unset V   # store the same value in your secrets wrapper as OPS_READBACK_SECRET
    netlify env:set OPS_KEYS '[{"name":"relay-prod","secretEnv":"KEY_RELAY_PROD","environments":["prod"],"sources":["urn:relay:","urn:sentry:"]},{"name":"relay-preview","secretEnv":"KEY_RELAY_PREVIEW","environments":["preview","dev"],"sources":["urn:relay:"]},{"name":"readback","secretEnv":"KEY_READBACK","environments":["prod"],"sources":["urn:ops-inbox:"]}]'
    claude setup-token
    gh secret set CLAUDE_CODE_OAUTH_TOKEN -R $T   # paste the token setup-token printed; gh reads it from standard input

Read back by: R11 R12 R23

## S7 · CAPTAIN ONLY · Store the Slack webhook

Create an incoming webhook for one channel in Slack first. R14, seeing the notice in the channel, is proven in S13.

    read -rs V   # paste the webhook URL; it stays out of shell history
    netlify env:set SLACK_WEBHOOK_URL "$V" --secret; unset V

Read back by: R13

## S8 · AGENT MAY RUN · Deploy the inbox and set its settings

Needs S3's App ID and installation ID and S4's Client ID.

    (cd kc-ops-inbox && npm ci && netlify deploy --prod --site $SITE --dir public --functions netlify/functions)
    netlify env:set OPS_TRIGGER_REPO $T
    netlify env:set OPS_WORKFLOW ops-event.yml
    netlify env:set DISPATCH_APP_ID <S3 App ID>
    netlify env:set DISPATCH_INSTALLATION_ID <S3 installation ID>
    gh variable set OPS_PROJECT_REPO -R $T --body $P
    gh variable set OPS_AGENT_APP_CLIENT_ID -R $T --body <S4 Client ID>

Read back by: R4 R5

## S9 · AGENT MAY RUN · Create the state branch and open the setup Draft PR

The PR adds `ops-gate.yml` (pinned to `$SHA`) and `docs/ops/README.md`; the script also sets the `OPS_CAPTAIN_LOGIN` variable.

    kc-ops-inbox/setup/make-state-branch.sh $P
    kc-ops-inbox/setup/make-setup-pr.sh $P $SHA $CAPTAIN

Read back by: R6 R21

## S10 · CAPTAIN ONLY · Apply the rulesets, one command each

Rerun only the line a read-back row names. The first four lines protect the project; the fifth protects the trigger repository. Then check that no project workflow holds a secret an agent branch could reach: read the workflows R18 lists, and if none runs with its secret on a push to a non-default branch or on a pull request from any author, give `--workflows-checked` to the read-back in S13. A project that fails the check applies the sixth line instead.

    gh api -X POST repos/$P/rulesets --input kc-ops-inbox/setup/ruleset-main.json
    gh api -X POST repos/$P/rulesets --input kc-ops-inbox/setup/ruleset-ops-branches.json
    gh api -X POST repos/$P/rulesets --input kc-ops-inbox/setup/ruleset-state-branch.json
    gh api -X POST repos/$T/rulesets --input kc-ops-inbox/setup/ruleset-trigger-main.json
    # only for a project that fails the workflow check: the agent may then create only ops/** and the state branch
    gh api -X POST repos/$P/rulesets --input kc-ops-inbox/setup/ruleset-agent-creations.json

Read back by: R15 R16 R17 R18 R19

## S11 · CAPTAIN ONLY · Merge the setup PR

So `ops-gate.yml` is on the default branch before any ops PR opens.

    gh pr merge ops-inbox-setup -R $P --squash

Read back by: R20

## S12 · CAPTAIN ONLY · Set the trigger rules and your Slack user

The inbox decides what each verified event does by an ordered rule list, first match wins. Leave `OPS_RULES` unset to use the default list, which is the approved routing table: prod warning goes to the agent, prod critical to the agent and a mention of you, preview critical to the agent, every other event with an environment is only recorded, and an event without an environment (a Sentry alert) goes to the agent. Heartbeats are always only recorded, and a recovered event joins its open incident or is recorded when none is open. To change a cell, set `OPS_RULES` to a list of `{name, match, receiver}`: `match` may hold `type`, `source` (prefixes ending in `:`), `environment` and `severity`, each a list of alternatives, all of which must match; `receiver` is `record`, `agent` or `captain`; the last rule must have `match` `{}`. An invalid list makes the inbox refuse every event with 500. Your Slack user id (the profile menu's Copy member ID) is needed because the default list routes to you.

    netlify env:set OPS_CAPTAIN_SLACK_USER <your Slack member ID>
    # optional: netlify env:set OPS_RULES '[{"name":"prod-critical","match":{"environment":["prod"],"severity":["critical"]},"receiver":"captain"},{"name":"rest","match":{},"receiver":"record"}]'

Read back by: R24

## S13 · ANYONE · Read every step back

Reads with your gh and netlify logins and sends one signed self-test event. The first run always waits on R14: open the self-test notice in Slack, Copy link, and run the same command again with `--slack-link`. Exit 0 only when every row is PASS.

    <wrapper> node kc-ops-inbox/bin/readback.mjs --project $P --trigger $T --inbox $INBOX [--slack-link <link>] [--workflows-checked]

`<wrapper>` is your secrets wrapper, which puts `OPS_READBACK_SECRET` in the read-back's environment without printing it.

Read back by: R14 R22
