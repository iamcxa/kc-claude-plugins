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
