# Ideation-1 replay evidence

Pinned state branches (`origin/spacedock-state/dev2`, read 2026-11-11): this workflow `e5efef4e`, qnow `d80c162d0c525e4b3400861fdd30e6fc5b3d040d`, subspace-relay `13ef35675e1a1150fe480e71a0e747a7b37cfa87`, subspace-web `faf28a257b22f92b4036cff8518a80ff10cd0fd2`. Package: kc-dev-flow-2 0.38.1.

    for r in qnow:d80c162d0c525e4b3400861fdd30e6fc5b3d040d subspace-relay:13ef35675e1a1150fe480e71a0e747a7b37cfa87 subspace-web:faf28a257b22f92b4036cff8518a80ff10cd0fd2; do
      mkdir -p "$OUT/${r%%:*}" && git -C "<clone of ${r%%:*}>" archive "${r#*:}" | tar -x -C "$OUT/${r%%:*}"; done
    python3 budget_lines.py <state root>                   # Budget line per task, unit tags
    python3 overrun_holds.py <state root>...               # tasks held at the first implementation/validation overrun
    KC_DEV_FLOW_2_SCRIPTS=<package>/scripts python3 archive_counts.py <this workflow's state root>
    KC_DEV_FLOW_2_SCRIPTS=<package>/scripts python3 cycle_counts.py <state root> [archive]   # max(records, report headings); superseded by archive_counts.py for this workflow

`counts.txt` holds the outputs of the 2026-11-11 run (paths there are the local extracts). `relay-role-triggers-replay.txt` is `role_triggers.py --rev <commit>` over each relay commit that touched the task; `amendment-budget-line.txt` is the throwaway `design_surfaces.py check`.
