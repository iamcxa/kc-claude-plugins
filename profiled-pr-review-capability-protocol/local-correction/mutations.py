import json
import pathlib
import shutil
import subprocess
import tempfile

root = pathlib.Path(__file__).parent
source = pathlib.Path('/Users/kent/conductor/workspaces/kc-claude-plugins/kc-pr-review-capability-pilot/kc-pr-flow')
unit = '    if unit_kind != "arm" and not getattr(args, "unit_input", None):\n        die(unit_kind + " requires unit_input")\n'
planner = '    if unit_kind == "admission" and not getattr(args, "planner_arm_dir", None):\n        die("admission requires planner_arm_dir")\n'
mutations = {
    'admission-unit': (unit, ''),
    'admission-planner': (planner, ''),
    'adjudication-unit': (unit, unit.replace('unit_kind != "arm"', 'unit_kind == "admission"')),
    'seal-repeat': ('    except FileExistsError:\n', '    except FileExistsError:\n        if pathlib.Path(path).name == "adjudication-seal.json":\n            raise\n'),
    'compare-repeat': ('    except FileExistsError:\n', '    except FileExistsError:\n        if pathlib.Path(path).name == "timing-opened.json":\n            raise\n'),
}
results = []
for name, (old, new) in mutations.items():
    with tempfile.TemporaryDirectory(dir=root) as temporary:
        plugin = pathlib.Path(temporary) / 'kc-pr-flow'
        shutil.copytree(source, plugin)
        owner = plugin / 'scripts/review-ablation-core.py'
        text = owner.read_text()
        assert text.count(old) == 1, name
        owner.write_text(text.replace(old, new, 1))
        command = ['bash', str(plugin / 'scripts/review-ablation.test.sh'), '--case', 'pilot']
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        (root / (name + '-red.log')).write_text(result.stdout + result.stderr)
        expected = 'TypeError' if 'unit' in name or 'planner' in name else 'FileExistsError'
        assert result.returncode and expected in result.stderr, (name, result.stderr)
        results.append({'case': name, 'exit': result.returncode, 'observed': expected, 'command': command})
        print(name, result.returncode, expected, flush=True)
(root / 'mutations.json').write_text(json.dumps(results, indent=2) + '\n')
