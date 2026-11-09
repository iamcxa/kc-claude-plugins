# Captain key block for the record-only inbox (given 2026-11-03, re-given 2026-11-06)

It holds no secret value: the key is generated at run time, written to both sites, and never printed. It supersedes runbook 第 6 段 (S6) for the record-only trial. It sets only the relay-preview key, not the readback key. It sets `OPS_RULES` to record-all. Relay's four deploy-preview vars go on `subspace-relay-staging`. Running it again regenerates the pair, so it is safe to repeat. The Captain pastes it in zsh as-is, and it should end with `ALL DONE`.

```
bash -c '
set -e
INBOX=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-ops-inbox-r1-setup-and-isolation/kc-ops-inbox
RELAY_SITE=48214294-e093-4e98-a27b-36ad594cd669
V="whsec_$(openssl rand -base64 24)"
cd "$INBOX"
netlify env:set KEY_RELAY_PREVIEW "$V" --secret --context production deploy-preview branch-deploy --force >/dev/null
NETLIFY_SITE_ID=$RELAY_SITE netlify env:set OPS_INBOX_SECRET "$V" --secret --context deploy-preview --force >/dev/null
unset V
netlify env:set OPS_KEYS "[{\"name\":\"relay-preview\",\"secretEnv\":\"KEY_RELAY_PREVIEW\",\"environments\":[\"preview\",\"dev\"],\"sources\":[\"urn:relay:\"]}]" --force >/dev/null
netlify env:set OPS_RULES "[{\"name\":\"record-all\",\"match\":{},\"receiver\":\"record\"}]" --force >/dev/null
NETLIFY_SITE_ID=$RELAY_SITE netlify env:set OPS_INBOX_URL https://subspace-relay-ops-inbox.netlify.app/inbox --context deploy-preview --force >/dev/null
NETLIFY_SITE_ID=$RELAY_SITE netlify env:set RELAY_OPS_INBOX_PREVIEW_PR 455 --context deploy-preview --force >/dev/null
NETLIFY_SITE_ID=$RELAY_SITE netlify env:set RELAY_OPS_INBOX_ENABLED true --context deploy-preview --force >/dev/null
echo ALL DONE
'
```

Unverified: the reason the first inbox write failed on 2026-11-03. The suspicion is that a secret cannot be set in Netlify's dev context, so this block names three contexts. If a line fails, the block stops there and earlier writes stay.
