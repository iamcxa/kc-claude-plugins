#!/usr/bin/env python3
"""Every fixture named *.valid.json validates and every *.invalid.json does not,
and each invalid fixture is rejected for the reason it was written to carry."""
import pathlib, subprocess, sys

HERE = pathlib.Path(__file__).parent
VALIDATE = HERE / "validate-contract.py"
EXPECTED_REJECTION = {
    "plan-value.invalid.json": ["140", "protects"],
    "plan-detail.invalid.json": ["colon", "bullet marker"],
}

failures = []
for fixture in sorted((HERE / "fixtures").glob("*.json")):
    r = subprocess.run([sys.executable, str(VALIDATE), str(fixture)],
                       capture_output=True, text=True)
    valid = fixture.name.endswith(".valid.json")
    if valid and r.returncode != 0:
        failures.append(f"{fixture.name}: expected VALID, got\n{r.stdout}")
    if not valid:
        if r.returncode == 0:
            failures.append(f"{fixture.name}: expected INVALID, got VALID")
        for needle in EXPECTED_REJECTION.get(fixture.name, []):
            if needle not in r.stdout:
                failures.append(f"{fixture.name}: rejection does not mention {needle!r}")

if failures:
    print("FAIL")
    for f in failures:
        print("  " + f)
    sys.exit(1)
print(f"PASS: {len(list((HERE / 'fixtures').glob('*.json')))} fixtures")

# A skill's Return template is the first thing a fresh session copies. Two of them named
# schemas they no longer satisfied, because the fields were added here and not there, and
# nothing compared the two: following the documented shape failed validation at step one.
import re as _re, json as _json, pathlib as _pathlib
_root = _pathlib.Path(__file__).parent.parent
_template_failures = []
for _name in ("kc-plan-value", "kc-plan-detail"):
    _skill = (_root / "skills" / _name / "SKILL.md").read_text()
    _m = _re.search(r"```yaml\n(schema: kc-plan-\w+/v1.*?)```", _skill, _re.S)
    if not _m:
        _template_failures.append(f"{_name}: no Return template to check")
        continue
    _keys = set(_re.findall(r"(?m)^(\w+):", _m.group(1)))
    _required = set(_json.loads((_root / "schemas" / f"{_name}.v1.schema.json").read_text())["required"])
    _missing = sorted(_required - _keys)
    if _missing:
        _template_failures.append(f"{_name}: template omits required {_missing}")
    # Asking only whether required fields are present let the template keep offering a field
    # the schema had started refusing, so following it to the letter failed at the next step.
    _schema = _json.loads((_root / "schemas" / f"{_name}.v1.schema.json").read_text())
    if _schema.get("additionalProperties") is False:
        _extra = sorted(_keys - set(_schema.get("properties", {})))
        if _extra:
            _template_failures.append(f"{_name}: template offers {_extra}, which the schema refuses")
if _template_failures:
    for _f in _template_failures:
        print("FAIL template: " + _f)
    raise SystemExit(1)
print("PASS: both Return templates carry every required field")
