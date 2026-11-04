# usage: select-pages.py <repo-root> <plugin>   prints the plugin's tracked or new Markdown, and each non-Markdown file a page links to, relative to the plugin
import os, re, subprocess, sys
root, plugin = sys.argv[1], sys.argv[2]
pkg = os.path.join(root, plugin)
listed = subprocess.run(["git", "-C", pkg, "ls-files", "--cached", "--others", "--exclude-standard"], capture_output=True, text=True, check=True).stdout.splitlines()
listed = [f for f in listed if os.path.isfile(os.path.join(pkg, f)) and "tests/" not in f]
pages = [f for f in listed if f.endswith(".md")]
keep = set(pages)
for page in pages:
    for target in re.findall(r"\]\(([^)#:\s]+)", open(os.path.join(pkg, page), encoding="utf-8").read()):
        path = os.path.normpath(os.path.join(os.path.dirname(page), target))
        if path in listed:
            keep.add(path)
print("\n".join(sorted(keep)))
