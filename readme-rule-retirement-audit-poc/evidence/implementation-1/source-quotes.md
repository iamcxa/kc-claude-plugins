# Pinned check excerpts

## kc-dev-flow-2/scripts/dispatch_records.py:72-88

```text
72: 
73: PASEO_COMPLETION_LINE = ("Your final reply is your completion message: Paseo delivers it to FO when your turn ends. "
74:                          "End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.")
75: COMPLETION_PART = "a scope-notes line naming main as the completion recipient"
76: PASEO_COMPLETION = re.compile(r"^## Scope notes\b(?:(?!^## )[\s\S])*?^" + re.escape(PASEO_COMPLETION_LINE) + r"$", re.M)
77: 
78: PARTS = {
79:     "a 'Dispatched:' line with a full 40-character SHA": re.compile(r"^Dispatched:.*\b[0-9a-f]{40}\b", re.M),
80:     "a 'Model:' line": re.compile(r"^Model:[ \t]*\S", re.M),
81:     "a non-empty '## Checklist' section": re.compile(r"^## Checklist[ \t]*\n(?:[ \t]*\n)*(?!## )\S", re.M),
82:     "a non-empty '## Scope notes' section": re.compile(r"^## Scope notes[ \t]*\n(?:[ \t]*\n)*(?!## )\S", re.M),
83:     "a 'Package root:' line with an absolute path in its scope notes":
84:         re.compile(r"^## Scope notes\b(?:(?!^## )[\s\S])*?^Package root:[ \t]*/\S", re.M),
85:     COMPLETION_PART:
86:         re.compile(r"^## Scope notes\b(?:(?!^## )[\s\S])*?\bcompletion(?: message)? to [`']?main(?![\w-])", re.M | re.I),
87: }
88: 
```

## kc-dev-flow-2/scripts/dispatch_records.py:191-210

```text
191:     else:
192:         scanned, inside = [], False
193:         for number, line in enumerate(lines):
194:             if line.startswith("## "):
195:                 inside = bool(SCANNED.match(line))
196:             elif inside:
197:                 scanned.append(number)
198:     return [(number + 1, name) for number in scanned
199:             for name in dict.fromkeys(SCRIPT_TOKEN.findall(lines[number])) if name in names]
200: 
201: 
202: def check_names(files, package):
203:     names = package_scripts(package)
204:     found = False
205:     for file in files:
206:         for number, name in bare_names(Path(file).read_text(), names):
207:             print(f"{file}:{number}: bare package script name {name}")
208:             found = True
209:     return 1 if found else 0
210: 
```

## kc-dev-flow-2/scripts/dispatch_records.py:646-708

```text
646:         if not given:
647:             print(__doc__.strip())
648:             return 2
649:         readme = Path(given[0])
650:         if not readme.is_file():
651:             print(f"--readme {readme}: no such file")
652:             return 2
653:     if "--coverage" in args:
654:         return check_coverage(args, readme)
655:     if len(args) != 1 or args[0] in ("--names", "--newest"):
656:         print(__doc__.strip())
657:         return 2
658:     task = Path(args[0])
659:     folder = task_folder(task) if task.suffix == ".md" else task
660:     records = sorted((folder / "dispatch").glob("*.md"))
661:     if not records:
662:         print(f"{folder}: no dispatch records under dispatch/")
663:         return 1
664:     readme = readme or find_readme(folder)
665:     # see docs/adr/0048-paseo-stage-workers-complete-by-final-reply-and-hand-publication-to-fo.md
666:     try:
667:         listed = readme_extensions(readme) if readme else []
668:     except (OSError, UnicodeError, ValueError) as error:
669:         print(f"{readme}: {error}")
670:         return 2
671:     paseo = "paseo" in listed
672:     errors = []
673:     for path in records:
674:         text = path.read_text()
675:         for part, pattern in PARTS.items():
676:             if not pattern.search(text) and not (part == COMPLETION_PART and paseo and PASEO_COMPLETION.search(text)):
677:                 errors.append(f"{path.name}: needs {part}")
678:     if readme:
679:         errors += extension_errors(folder, readme, package)
680:     names = [path.stem for path in records]
681:     for path in records:
682:         if only_points_at_records(path.read_text(), [name for name in names if name != path.stem]):
683:             errors.append(f"{path.name}: needs a checklist of its own, not only a reference to another dispatch record")
684:     for error in errors:
685:         print(error)
686:     newest = {}
687:     for path in records:
688:         record = DIAGNOSIS_RECORD.fullmatch(path.name)
689:         if record and diagnosis_order(record) > newest.get(record[1], ((0, 0), None))[0]:
690:             newest[record[1]] = (diagnosis_order(record), path)
691:     check_symptoms([path for _, path in newest.values()])
692:     if not readme:
693:         print(f"extensions not checked: no workflow README above {folder}")
694:     if not errors:
695:         print(f"{len(records)} dispatch record(s) complete")
696:     return 1 if errors else 0
697: 
698: 
699: if __name__ == "__main__":
700:     sys.exit(main())
```

## kc-dev-flow-2/scripts/test_dispatch_records.py:293-353

```text
293:     def test_the_completion_recipient_line_is_judged_by_its_recipient_and_its_section(self):
294:         for line in ("Completion message to `main`.", "completion to `main`", "Send your phase-1 report and your completion message to main."):
295:             with self.subTest(line):
296:                 self.assertEqual(self.check({"a-1.md": COMPLETE.replace(MAIN_LINE, line + "\n")})[0], 0)
297:         for label, text in (
298:                 ("team-lead", COMPLETE.replace(MAIN_LINE, "Send completion to team-lead.\n")),
299:                 ("another branch", COMPLETE.replace(MAIN_LINE, "Send your completion message to `main-branch`.\n")),
300:                 ("outside the section", COMPLETE.replace(MAIN_LINE, "").replace("1. Independent", MAIN_LINE + "1. Independent"))):
301:             with self.subTest(label):
302:                 code, out = self.check({"a-1.md": text})
303:                 self.assertEqual(code, 1)
304:                 self.assertIn("a-1.md: needs a scope-notes line naming main as the completion recipient", out)
305: 
306:     def test_paseo_completion_passes_only_with_the_listed_extension(self):
307:         text = COMPLETE.replace(MAIN_LINE, PASEO_LINE + "\n")
308:         for value in ("[peers, paseo]", "[peers, 'paseo'] # listed", '[peers, "paseo"] # listed'):
309:             listed = "---\nentity-type: task\nextensions: " + value + "\n---\n"
310:             with self.subTest(value=value):
311:                 code, out = self.check({"implementation-1.md": text}, readme=listed)
312:                 self.assertEqual((code, out), (0, "1 dispatch record(s) complete\n"))
313:         for readme in (NO_EXTENSIONS, LISTS_ROBOREV, None,
314:                        "---\nentity-type: task\nextensions: [paseo-other]\n---\n",
315:                        "---\nentity-type: task\nextensions: [learn, peers] # paseo intentionally disabled\n---\n",
316:                        "---\nentity-type: task\nextensions: [] # paseo intentionally disabled\n---\n",
317:                        "---\nentity-type: task\nextensions: ['paseo disabled', peers]\n---\n"):
318:             with self.subTest(readme=readme):
319:                 code, out = self.check({"implementation-1.md": text}, readme=readme)
320:                 self.assertEqual(code, 1)
321:                 self.assertIn("implementation-1.md: needs a scope-notes line naming main as the completion recipient", out)
322: 
323:     def test_paseo_completion_requires_the_exact_line_inside_scope_notes(self):
324:         listed = "---\nentity-type: task\nextensions: [peers, paseo]\n---\n"
325:         missing = COMPLETE.replace(MAIN_LINE, "")
326:         for text in (COMPLETE.replace(MAIN_LINE, PASEO_LINE.replace("final", "last") + "\n"),
327:                      missing.replace("## Checklist\n", PASEO_LINE + "\n\n## Checklist\n"),
328:                      missing + "\n## Other\n\n" + PASEO_LINE + "\n"):
329:             with self.subTest(text=text):
330:                 code, out = self.check({"implementation-1.md": text}, readme=listed)
331:                 self.assertEqual(code, 1)
332:                 self.assertIn("needs a scope-notes line naming main as the completion recipient", out)
333:         self.assertEqual(self.check({"implementation-1.md": COMPLETE}, readme=listed)[0], 0)
334: 
335:     def test_paseo_extension_and_checker_share_the_completion_instruction(self):
336:         extension = Path(records.__file__).parents[1] / "extensions/paseo/EXTENSION.md"
337:         line = re.search(r'In scope notes and follow-ups, replace the main line with: "([^"]+)"',
338:                          extension.read_text())
339:         self.assertIsNotNone(line)
340:         self.assertEqual(line[1], PASEO_LINE)
341:         self.assertEqual(records.PASEO_COMPLETION_LINE, PASEO_LINE)
342: 
343:     def test_the_package_root_line_must_be_absolute_and_inside_the_scope_notes(self):
344:         moved = COMPLETE.replace("Package root: /abs/kc-dev-flow-2\n", "").replace("## Checklist\n", "Package root: /abs/kc-dev-flow-2\n## Checklist\n")
345:         for label, text in (
346:                 ("deleted", COMPLETE.replace("Package root: /abs/kc-dev-flow-2\n", "")),
347:                 ("above the checklist", moved),
348:                 ("relative", COMPLETE.replace("/abs/kc-dev-flow-2", "kc-dev-flow-2/0.21.0"))):
349:             with self.subTest(label):
350:                 code, out = self.check({"implementation-3.md": text, "validation-1.md": COMPLETE})
351:                 self.assertEqual(code, 1)
352:                 self.assertIn("implementation-3.md: needs a 'Package root:' line with an absolute path in its scope notes", out)
353:                 self.assertNotIn("validation-1.md", out)
```

## kc-dev-flow-2/scripts/test_sd_dispatch.py:34-51

```text
34: TEAM_RULE = """- **Team:** You are one worker in a team completing the project goal; your stage
35:   and handoff serve that goal. Before substantial work or retrying a failure,
36:   check this task's prior reports, linked sibling tasks and PRs, and relevant
37:   workflow state: did someone already do this, hit this, or own it now? If your
38:   environment cannot run a required checklist check, tell FO before building
39:   work that depends on it. Ask FO early about overlapping ownership, repeated
40:   failures, missing authority or evidence, or infeasible targets. Give checked
41:   sources, findings, attempts and the specific question. With a mid-run FO
42:   channel, pause dependent work and continue safe independent work; without
43:   one, end your turn with that handback instead of waiting. Never answer your
44:   own or your reviewers' permission requests; route them to FO. FO coordinates
45:   peers and decisions; do not message peers or change others' work."""
46: 
47: 
48: def assert_team(text):
49:     clauses = re.findall(r"^- \*\*Team:\*\*.*?(?=^\S|\Z)", text, re.MULTILINE | re.DOTALL)
50:     assert [" ".join(clause.split()) for clause in clauses] == [" ".join(TEAM_RULE.split())], "complete Team rule missing or duplicated"
51: 
```
