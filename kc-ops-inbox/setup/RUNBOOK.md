# Connect a project to its ops inbox (runbook, r1)

Run the steps in order. A step marked CAPTAIN ONLY touches an App, a key, a secret, a webhook, a ruleset or a merge; nobody else runs it. Each step names the read-back rows that prove it; S12 reads all of them.

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

## S6 · CAPTAIN ONLY · Create and store the signing secret and the model token

The signing secret goes to the inbox and to the producer, never into a repository. `OPS_INBOX_SECRET` is a placeholder: use the variable name the producer's emitter reads.

    V=whsec_$(openssl rand -base64 24)
    netlify env:set WEBHOOK_SECRET "$V" --secret
    (cd $RELAY_CHECKOUT && netlify env:set OPS_INBOX_SECRET "$V" --secret --context deploy-preview); unset V
    claude setup-token
    gh secret set CLAUDE_CODE_OAUTH_TOKEN -R $T   # paste the token setup-token printed; gh reads it from standard input

Read back by: R11 R12

## S7 · CAPTAIN ONLY · Store the Slack webhook

Create an incoming webhook for one channel in Slack first. R14, seeing the notice in the channel, is proven in S12.

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

Rerun only the line a read-back row names. The first four lines protect the project; the fifth protects the trigger repository. Then check that no project workflow holds a secret an agent branch could reach: read the workflows R18 lists, and if none runs with its secret on a push to a non-default branch or on a pull request from any author, give `--workflows-checked` to the read-back in S12. A project that fails the check applies the sixth line instead.

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

## S12 · ANYONE · Read every step back

Reads with your gh and netlify logins and sends one signed self-test event. The first run always waits on R14: open the self-test notice in Slack, Copy link, and run the same command again with `--slack-link`. Exit 0 only when every row is PASS.

    <wrapper> node kc-ops-inbox/bin/readback.mjs --project $P --trigger $T --inbox $INBOX [--slack-link <link>] [--workflows-checked]

`<wrapper>` is your secrets wrapper, which puts `WEBHOOK_SECRET` in the read-back's environment without printing it.

Read back by: R14 R22
