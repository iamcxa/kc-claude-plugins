# Review-backend contract

A backend is one executable that answers two verbs. The listener holds no
knowledge of where a review actually runs, so a new backend needs no change to
polling, de-duplication, notification, or menu rendering.

## create

```
<backend> create <repo-slug> <pr-number> <pr-url> <head-branch> <prompt-file> [head-sha]
```

Start a review of that PR from that branch, seeded with the text in
`<prompt-file>`. Print exactly two lines to stdout and exit 0:

```
job_id=<opaque string, no spaces>
open=<URI or absolute path the user can open to watch the review>
```

`job_id` is the handle `status` will be called with, and it is opaque — pack whatever
`status` will need into it, including the account or organization the job belongs to,
because `status` receives nothing else. `head-sha` is the commit the review was
requested for; a branch can move between the decision and this call. `open` is what a menu click
and a notification click resolve to — a URI scheme, an editor URL, or a directory
path all qualify. On failure, exit non-zero and print a one-line reason to stderr; the listener
records it and retries on a later tick — **except exit code 3**, which means a side
effect was already produced and could not be finished. A retry would duplicate it,
so the listener holds that pull request for a person instead of trying again. Use 3
whenever the remote thing exists but you cannot return a usable handle for it.

## status

```
<backend> status <job_id>
```

Print exactly one word to stdout and exit 0:

| word | meaning |
|------|---------|
| `running` | the review is still in progress |
| `done` | the review finished; the listener notifies once, then stops asking |
| `error` | the review cannot finish; the listener stops asking |

An unknown or expired `job_id` is `error`, not a non-zero exit. Reserve non-zero
for "I could not determine the status" — the listener treats that as `running` and
asks again next tick, so a transient API failure never fabricates a completion.

## Rules

- **Never merge and never force-push.** Whatever runs the review must be prompted or
  configured so it cannot. Applying a fix, pushing it, and approving are the review
  skill's own behaviour and are out of a backend's hands.
- **Own your prerequisites.** Check for your CLI, credentials, and any mapping you
  need on first use, and fail with a message naming what is missing. The installer
  does not pre-validate backends it did not select.
- **Own your own credential scoping.** The listener passes the repo slug; deriving
  an account, organization, or token from it is the backend's business.
- **Keep state out of the listener.** Caches belong in your own file under the
  config directory.

## Conformance

```
scripts/backends/conformance.sh <backend-path>
```

Exercises both verbs against argument shapes and asserts the output contract
without creating real work — run it before wiring a new backend in.
