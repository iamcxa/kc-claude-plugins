"""Count overruled run-1 rulings whose evidence or change names a declared prop, slot or hook.
Usage: python3 -I count_citations.py out/   (run from the replay folder)
strict: the text names `children`, `error`, `hint`, `placeholder`, `disabled`, `trailing`, `info`, a hook or part of react-native.d.ts (useToast, ScrollView, FlatList, Modal.Content, contentContainerStyle).
broad: strict, or any mention of a declaration file, a Settings* component, `prop`, `slot` or a backticked name."""
import glob, re, sys
strict = re.compile(r"`(?:children|error|hint|placeholder|disabled|trailing|info)`|\b(?:children|placeholder|trailing|useToast|ScrollView|FlatList|Modal\.Content|contentContainerStyle|hint prop|error prop|error slot|hint slot|disabled prop)\b")
broad = re.compile(r"d\.ts|declaration|ui\.d|react-native|Settings(?:Row|Action|Input|Select|Section|Card)|ModalProps|prop\b|slot|`\w+`")
over = 0; s = b = 0
for path in sorted(glob.glob(sys.argv[1].rstrip("/") + "/*.yaml")):
    for item in re.split(r"\n\s*-\s+finding:", "\n" + open(path).read())[1:]:
        if not re.search(r"ruling:\s*overruled", item):
            continue
        over += 1
        text = " ".join(re.findall(r"(?:evidence|change):\s*(.*)", item))
        st = bool(strict.search(text)); s += st; b += st or bool(broad.search(text))
print(f"overruled {over}, strict {s}, broad {b}")
