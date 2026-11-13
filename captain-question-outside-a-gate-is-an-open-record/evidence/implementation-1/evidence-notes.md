# Evidence boundary

Public iamcxa/kc-claude-plugins source and task state only; no other repository,
private repository contents, credentials, or personal data were archived.
CI stdout is retained as counts/status lines; repository test fixtures are the
reproduction source. No hosted CI, independent validation, RoboRev, live released
day, or reader in another repository was exercised.

The fourteen-question fixture reuses the public ideation extraction's questions
and recorded-answer commit times. Asking times, replay task keys and the replay
owner are explicitly synthetic; it does not establish real historical waiting
intervals. The original h3 fixture was separately exercised unchanged.

Gate replay uses the public state clone and native gate attempts extracted for
2026-11-13. Unrelated task documents are excluded from that throwaway clone;
git history is unchanged. Repeated identical read-only git-log commands are
cached at its fixed HEAD, without substituting timestamps or rows. The archive
move falsifier runs uncached against a real git fixture in the normal suite.

The first design-suite attempt failed because the new skip diagnostic was
emitted for standalone files outside an adopted workflow, changing existing
notes. The implementation limits that diagnostic to a located workflow and
reruns the final suite. A local-clone hard-link denial was retried with
--no-hardlinks. The requested pytest command could not load pytest; FO explicitly
instructed using the unittest command CI runs, with no install or virtualenv.
