# Implementation evidence

Candidate 9dd03d805d11c0c833699b1247fd11d99a74d52f supersedes initial candidate 401fc60e5c69e6e9458f9c15f31b4527af417911; base 6a1eaf837bd6087cd0b8b665dc19beaed3c44dff. commands.json records commands, exits and output names; acceptance.json maps the criteria. Local prefixes are replaced by <worktree>, <scratch>, <task>, <package> and <active-spacedock>.

Local execution used Python 3.15.0, Spacedock CLI 0.27.2 and active Spacedock plugin 0.28.0. Hosted CI uses its own pin and has not run on this branch. No model, deployment, PR, review request or product push ran.

cases.py derives variants from the retained evidence/ideation-1/fixtures/run1.md and run2.md. The two comment-field tests fail on the exact 401fc60e5 checker; both full CLI replays exit 0 on it and 1 on the corrected checker. guard-inputs.json lists eligibility inputs, accepted scalar/approval forms and limits. older-consumers.json and findings.json record five unchanged consumers for FO disposition.

corpus.py preserves the count exercise but calls main(argv) in process and omits removed experimental exemption switches. compatibility.py loads frozen base/candidate source and compares main(argv) for check and check --seed on every snapshot file. The unfinished process-per-command comparison on 401fc60e5 was stopped; none of its output is used. The corrected comparison covers 501 tasks with no unexpected changes or new proof refusal on an approved/archive task.

Corpus coverage: 236 public Pilot tasks and adopter counts 113 and 99 (previously 98). Two supplied sources match 113, so original identity is not unique. No supplied source matches the old 137 count; that fourth corpus is not reproduced.

Not archived (private): adopter task files, source-path mapping, raw per-file compatibility output and synthetic dispatch call traces; reproduce: git -C <adopter-state-checkout> archive HEAD | tar -x -C <scratch>/corpora/<label>, then run corpus.py and compatibility.py with those roots. Only counts are retained.

The design's AC-5 Not provable now note is corrected: its base log omitted SPACEDOCK_BIN (FileNotFoundError: None); /tmp extracts also hit the scope-note scratch boundary. The corrected candidate's unmodified suite, with SPACEDOCK_BIN set and the assigned package worktree, passes 52 tests. Synthetic roots left by both suite runs were identified by scope-notes pointing to this worktree and removed by exact path; cleanup JSON records names/counts.

Not provable now: AC-6 needs the first real archive after release; its observer falsifier has not run. RoboRev, product publication, Draft PR and hosted CI belong to FO. CI cost per PR was not measured; CI configuration is unchanged.
