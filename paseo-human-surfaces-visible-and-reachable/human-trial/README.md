# Attended human-surface trial, FO-run, 2026-11-01, candidate 8aa76f15f

Host srv_Vu_gVMYcYLxv, Captain's visible workspace wks_a8f029f6e72d90cb, cwd the colombo workspace.

Terminal 44e0744d "Human surface trial": FO sent `printf 'surface-ready\n'`. The Captain said 「我用手機貼上了」; capture shows `captain-visible` twice and the terminal re-wrapped to a narrower width. Pasted over Paseo with the phone offline on Tailscale, so the terminal reach does not depend on Tailscale.

Page: /tmp/hs-trial, `python3 -m http.server 52901 --bind 127.0.0.1`, tab 78f6236d in the same workspace.
Intact: naturalWidth 80 and naturalHeight 80, screenshot shows the green square, network shows probe.svg.
Negative control: probe.svg renamed, HTML still 200, svg 404, naturalWidth 0. Then restored.
Serve baseline before any change: serve-baseline.json, ports 8410, 8412, 8531, 8617, 8660, 8725, none owned by this trial.
