You are working in the subspace-relay repository in your current directory.

Relay is about to add "pair a computer with an account once". A person runs a CLI command on their computer; the CLI asks the relay to start a pairing and prints a link. The person opens the link in a browser on the same computer, signs in, and approves. The relay must accept the approval only when the browser approving it is on the same computer as the CLI request that started the pairing; otherwise it shows a refusal. The person can also cancel from the terminal.

Write the validation plan for this feature: the browser test cases and endpoint integration test cases that a validator should run locally under Netlify dev (`pnpm dev`, http://localhost:8888) before the change is reviewed, and what each case must show to pass.

Do not implement anything and do not start servers or install packages. Read whatever in the repository you need. Reply with the plan only, as a numbered list of cases.
