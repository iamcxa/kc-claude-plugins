# POC: Paseo daemon in Docker, reached through Paseo Hub

Disposable proof, removed with the POC branch if the stop conditions fire. Image base: `ghcr.io/getpaseo/paseo` pinned by digest in `Dockerfile`; Paseo 0.13.0.

## Local rehearsal (no credential, no Hub, no GitHub)

```sh
docker build -t ops-poc-paseo:local .
# credential audit of the image's own baseline, as the agent user
docker run --rm --network none --entrypoint bash -v "$PWD/audit.sh:/audit.sh:ro" ops-poc-paseo:local -c 'su paseo -s /bin/bash -c /audit.sh'
# ops task and default-branch refusal against a local bare remote; /fixture holds docs/ops and fixture-event.json from the scratch repository
docker run --rm --network none --entrypoint bash -v "$PWD/rehearse-remote.sh:/r.sh:ro" -v /path/to/fixture:/fixture:ro ops-poc-paseo:local -c 'su paseo -s /bin/bash -c /r.sh'
```

## Live run (every step needs the Captain's approval first)

1. Captain creates `poc.env` outside the repository holding `CLAUDE_CODE_OAUTH_TOKEN` and `PASEO_PASSWORD`; `POC_ENV_FILE=<path> docker compose up -d`.
2. `docker exec -u paseo ops-poc-paseo paseo hub login <origin>`, then `paseo hub connect` and `paseo hub permissions grant hub.execute`.
3. Fill the `<>` placeholders in `ops-event-poc.yml`; `paseo hub deploy --dry-run`, then `paseo hub deploy`.
4. AC-1: `send-event.sh <deliveryKey>` twice with one key; it validates the event against contract v1 first (`CONTRACT_DIR` is a checkout of the r1 branch). AC-5: `docker compose stop`, send, `docker compose start`.
5. AC-2 and AC-3: from the Paseo app, ask the running agent to run `/opt/poc/ac2-probe.sh <open non-draft PR number>` and `/opt/poc/audit.sh`, so both see the real `GH_TOKEN` environment without printing it. AC-4: add `127.0.0.1:6767` as a direct host in the Paseo app.
