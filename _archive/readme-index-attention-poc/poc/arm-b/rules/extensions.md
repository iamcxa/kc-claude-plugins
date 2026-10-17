## Extensions

Extensions are optional accessories in `<package>/extensions/<name>/`, each described by
its `EXTENSION.md`: what it needs, the stage or FO step it joins, the instruction it
adds, how its result is read, and what happens when it cannot run. This README's
frontmatter `extensions:` lists the ones this repository uses; an unlisted extension is
not probed and adds nothing. For a listed extension FO follows its `EXTENSION.md`: at a
worker dispatch of its stage FO adds its instruction line to the scope notes, and at its
FO step FO reads the result as the file says. A listed extension that cannot run, or that FO does not request because a ruling says not to, is
reported as `<name> not run: <reason>` in the stage report or gate summary, and never
counts as a clean result. A merge ask names each listed reviewer that was not read, and
the Captain decides. Where two remote reviewers are listed, frontmatter `second-reviewer:`
names the one that joins only when a trigger holds: the task's `Surfaces:` include `db`,
its profile is `prod`, a dispatch said its design is hard to reverse, the change touches authority,
approval, merge or review rules, or the Captain asks. FO records `second reviewer: <name>
because <trigger>` or `second reviewer: not triggered` in the gate summary, and an
untriggered second reviewer is not named as unread.

