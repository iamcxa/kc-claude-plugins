# Disposable-container isolation feasibility — not integrated

The bounded filesystem/process/cleanup proof passed. **A cap-compliant, real-model-compatible product integration is NOT demonstrated or approved.** Product remains clean at `9bb526170156a44cff90e2a2fab9eeab081e0eb1`; all five repair groups remain open. Approval `087047c577d4f58003f6833478c345c50f7b377e` was reread before launch, under the First Officer's final existing-container alternative assignment. Native-policy and Safehouse failure records remain unchanged.

## Exact environment and confinement

The already-running Docker server is 29.4.0. The existing local `catthehacker/ubuntu:act-latest` tag resolved before launch to **`sha256:10ca2cfc3a29b70e13fe0a2a9244fe7e5d24fbd7350ac4205028335c9541f926`**, Linux arm64. Image metadata: configured user root, command `/bin/bash`, no entrypoint or declared volumes. Each actual launch overrides the user to 65534:65534 and entrypoint to `/bin/bash`, using that immutable ID and `--pull=never`. No image pull/build/tag/update, tool installation, Docker configuration/startup, real credential access or model call occurred.

Local `docker run --help`, `docker container inspect --help` and `docker container rm --help` were read before launch. Metadata was read with `docker image inspect ... --format '{{json .}}'` piped to a selected-field jq projection; an initial template referencing absent `.Config.Entrypoint` failed without launching anything. Actual child execution confirmed `/usr/bin/python3`, Python 3.12.3, nested Bash and non-root UID 65534. No model credential environment variable was forwarded.

Each case has one owned synthetic host `work` directory mounted R/W at `/work`. Its host sibling `owner` contains manifests, previous/current receipts, raw measurement output and a trusted CID file; **none of owner, host interpreter, runner source, Docker socket or control files is mounted**. The only child-readable configuration contains synthetic owner paths and a forged synthetic receipt template. Root filesystem is read-only; only `/tmp` has a 16 MiB tmpfs. Flags additionally enforce:

```text
--rm --init --read-only --cap-drop=ALL --security-opt=no-new-privileges
--ipc=private --network=none --user=65534:65534 --pids-limit=32
--memory=256m --cpus=1 --no-healthcheck --stop-timeout=1
--tmpfs=/tmp:rw,nosuid,nodev,size=16m
```

Default private PID namespace is retained; no host namespaces, privileged mode, external volume, detached container or standing service. Timeout-container inspection independently confirms those settings, including one rprivate bind mount, `Privileged=false`, 256 MiB memory and one CPU. Only disposable fixture permissions were changed to let non-root write the child work directory. All host targets are beneath `/private/tmp/pilot-isolation-proof.68ALze`; no real user/product data was an attack target.

## Actual proof and failed first instrument

The [host instrument](proof.py) imports the unchanged product `review-ablation-core.py`, extracts only the existing real ten-record fixture setup from `review-ablation.test.sh`, and calls actual `pilot_invoke`, `pilot_attempt`, `pilot_write` and `pilot_join`. [Child code](container-child.py) runs inside Bash and attempts nine write routes; it is not a new receipt validator. The earlier [unisolated negative control](../isolation-feasibility/results.json) is reused, not rerun: current preplant/prior overwrite succeed, finalization collides, and real join accepts both forged 1-ms records. Its failing assertion and exact command are preserved in the [native report](../isolation-feasibility/report.md).

The first container really executed: normal workspace/output/tmp writes succeeded and all nine owner-write attempts plus the independently grouped descendant write failed. However, its [initial instrument](initial-proof.py) expected Docker's missing-object error to say `No such object`; Docker actually said `No such container`. That assertion aborted parent finalization, and the subsequent unconditional receipt read failed. [Initial raw log](initial-run.log) is preserved as **FAILED/partial, not green**. Its CID `f62d8a631327c3c42849dea8db1195e294dad7bd9c8013ff476fa697f6932822` was read from its trusted file and explicitly inspected absent. No surviving object was deleted or ownership guessed.

The only correction accepts both actual absent-container message forms and records the raw absence message; fresh case directories/output filenames preserve the initial run. No isolation allowance changed. First Officer authorized this instrument-only correction. The corrected same five-case set exited **0** in **7.010931291 seconds**, printing `CONTAINER FILESYSTEM AND LIFECYCLE PASS (5 cases)`. [Structured results](results.json) and [raw log](run.log) retain commands, actual child/descendant reports, parent receipts and cleanup.

| Case | Observed result and falsifier |
|---|---|
| Existing hard-link in mount input | Prelaunch admission refuses the alias; no container launched, original receipt unchanged. Removing the link-count check would admit it and fail this assertion. |
| Existing symlink in mount input | Prelaunch admission refuses the alias; no container launched, original receipt unchanged. Removing the symlink check would fail this assertion. |
| Normal | All nine owner-write routes fail with ENOENT because host paths are outside the container; normal work/output/tmp and nested Bash succeed. Parent finalization succeeds and real join accepts 10 records: measured current 1116.906083 ms, prior unchanged 100 ms. Owner exposure or accepting a planted 1-ms record would fail the assertions. |
| Child exit 7 | Same denials and normal work; raw exit 7 preserved. Actual parent writes `attempt_failed`, `cost_status=incomplete`, null exact cost/model/usage; join refuses. Omitting the terminal receipt or accepting the failed record would fail. |
| Four-second timeout | Same child/descendant denials observed before timeout. Host raw exit -9; actual parent writes incomplete failed receipt and join refuses. The container is still running after the CLI is killed, so exact-owned cleanup is necessary and actually executed. |

Nine direct-child attacks: current receipt preplant, previous overwrite/chmod, owner-ancestor rename/write/restore, path traversal, child-created symlink, attempted new hard link, protected file unlink, protected owner-directory rename, and protected empty-directory removal. Each checks actual attempted operation rather than a policy substring. Host prior bytes and sentinel remain unchanged. Existing aliases are refused, never silently repaired or claimed safe through namespaces alone.

In all three launched corrected cases, a descendant created with `start_new_session=True` has PID/group 9 while the direct Python child has PID/group 6. The descendant tries rewriting the previous receipt, records ENOENT and remains alive when the direct child observes it. This proves denial while alive in a distinct group, **not survival after namespace destruction**. Container removal terminates its private namespace, including descendants; the proof does not mistake `killpg` of the host CLI for descendant cleanup.

## Exact cleanup evidence

Each launch has a unique `pilot-proof` label and a CID file outside the child mount. If an object exists, the parent requires both exact full CID and exact label match before `docker container rm --force CID`; no broad target, prune, image/volume deletion or unrelated container operation is used. On all corrected paths, a second exact-CID inspect returns absent and read-only exact-label listing returns empty.

| Exit | Exact CID | Cleanup result |
|---|---|---|
| 0 | `3b0570f689c947a4eee208c9e2193fc1164eb6bd28877e0d3fa685dad5adb137` | Already removed by `--rm`; inspect absent; exact label empty. |
| 7 | `06a7d663f377a117810f68010460fdf1fb4e2058e913f1f117e55eca773a0e8c` | Already removed by `--rm`; inspect absent; exact label empty. |
| Timeout | `c3df71033682083d8535e5d89f89110ded1055bf85f1b435307464f18bfcda57` | After host CLI kill: `running`; CID and label matched; force-remove exit 0; inspect absent; exact label empty. |

The actual 7-second run is bounded by per-launch 20-second normal/nonzero and 4-second timeout limits, child/descendant sleeps of 15 seconds, and 10-second limits on each Docker control command; there is no retry loop. General parent interruption, daemon loss or cleanup-command timeout was not fault-injected. Product integration would need fail-closed ownership, no-CID startup-failure handling and cleanup on every exit/cancellation path before it could claim the full lifecycle. No second experiment or additional alternate primitive is authorized by this result.

## Measurement and reproducibility limits

Host command actually run after activating the existing Recce Python 3.13 environment and confirming `which python`:

```sh
python -B /tmp/pilot-isolation-proof.68ALze/container-proof.py
```

The first invocation used the archived initial bytes and wrote `container-run.log`; the corrected invocation used current `proof.py` bytes and wrote `container-v2-run.log`. To reproduce elsewhere, place `proof.py` and `container-child.py` together in a fresh owned temporary directory, bind `SOURCE` to the exact product candidate with its existing fixture, and provide the explicitly required Docker/image/Python dependencies. Never run the proof inside the durable state checkout, because it intentionally creates synthetic sibling directories and aliases. The cached image is a local prerequisite, not implicitly downloadable permission.

SHA-256: `proof.py` = `619c2d9b24bfc9691530d664e823d3419c228dabdf1c09131cfae8880db5a81d`; `container-child.py` = `ff2c471e0ff2802515a3461770fa2c222ef0f38da9d08235c197afc3dd13dd0a`; `results.json` = `a3d8b31ccd911547bf639ad32ec38eeb2bc0c0f39f4bc95a4b31ae70586aedb9`.

All model IDs, usage and costs in the valid ten-record setup are synthetic fixture values. The normal `complete` cost field is inherited fixture data, not a measured provider bill; failed cases remain incomplete. Actual provider requests and model spend are **zero**. The 1116.906083-ms measurement includes container CLI startup/execution/exit, excludes subsequent cleanup/finalization, and is not review latency. The whole proof took 7.011 seconds locally; no hosted CI/per-PR cost or real review performance was measured.

`network=none` intentionally prevents provider connectivity. Claude startup, installed CLI availability/version in this image, real authentication, Keychain compatibility, provider IPC/proxies and containerized control/treatment parity are **NOT RUN/NOT PROVEN**. Enabling network, mounting authentication or adding a host bridge would change the demonstrated boundary and needs an explicit minimal design; a bridge must not become an unsandboxed write proxy. Kernel/privileged-daemon vulnerabilities and hostile independent host writers racing alias admission are outside this proof. Host source/interpreter isolation comes from mount/process separation; this was not a privileged escape assessment.

## Smallest integration shape and count impact — UNAPPROVED

Reuse `pilot_invoke` for the measured command and `pilot_attempt` for parent-owned terminal recording, with existing `pilot_execute` preparing a child-only checkout/output area. The parent keeps manifests, receipts, raw output, executable core and trusted CID/provenance outside mounts. Existing failure/usage defects are not fixed by the container. Both arms, admission/retries and adjudication need the same pinned launch policy; unsupported Docker/image/permissions must refuse before spend, never fall back to unsandboxed execution. Host absolute command paths cannot simply be prefixed with Docker: only approved selected runtime inputs may be staged into the child view while preserving the authoritative owner outside it.

There is a **real surface/dependency delta**, even if contained in existing source files: (1) Docker daemon/platform availability and permission lifecycle, (2) immutable runtime-image availability/provenance and maintenance, and (3) per-attempt container/CID/label/cancellation lifecycle. Parent measurement authority remains the existing runner; no new ledger, CLI command, workflow or standing service is proposed. The existing local daemon was reused, not created; depending on it in the product is nevertheless unapproved and not a free relocation. Real-model image/auth/network compatibility remains an additional unresolved prerequisite, not hidden within this estimate.

Readable net cumulative estimate for the demonstrated boundary only, reusing existing fixture/assertion helpers rather than copying this standalone diagnostic:

| Work in existing owners | Code | Focused tests | Docs |
|---|---:|---:|---:|
| Immutable launch, child-view preparation and policy/provenance binding | 30–45 | 25–35 | 5–10 |
| Prelaunch link/placement admission | 10–15 | 20–25 | 3–5 |
| Exact-owned cleanup, startup/cancellation failure paths | 40–60 | 35–55 | 4–5 |
| Existing finalization/join integration and negative-control assertions | 20–40 | 30–45 | 3–5 |
| Total, excluding other repairs and unproven model compatibility | **100–160** | **110–160** | **15–25** |

Current actual cumulative count remains **6,431 / 20 files / 1,939 complete focused lines**, measured against `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`; product is unchanged. Limits remain **6,600 / 20 / 1,800**. These estimates describe final net changes relative to that base, not last-commit additions plus deletions to already-new files. Test-only helpers count as focused wherever placed.

Only the previously mapped [same-scope duplicate candidates](../isolation-feasibility/report.md#readable-count-estimate-and-reduction-evidence) remain available: posting builder 30–40, fallback constructors 12–16, CLI plumbing 18–25, provider/import templates 15–25, and ablation compare plumbing 10–15, totaling **85–121 estimated lines**. No deletion is performed or credited; no new reduction study was launched. Even generously realizing all 121 savings gives the low focused estimate `1939 + 110 - 121 = 1928`, **128 over the limit before the other repairs**. Low/high total envelopes are `6431 + 100 + 110 + 15 - 121 = 6535` and `6431 + 160 + 160 + 25 - 85 = 6691`; the latter is already 91 over total, with the other repairs/auth work excluded. Without any realized deletion, the low focused estimate is 2049, 249 over.

Therefore no cap-compliant integration is demonstrated; this proof is not a recommendation to start integrating under current authority. The First Officer owns the next single route decision with the Captain. Stop product work here: all five confirmed repair groups, equivalent reduction, F14 CI timing sequence, fresh independent review and budget-gated paid AC8/9 remain pending. No product, branch, stage/status/pin, historical report, workflow, PR or release changed.
