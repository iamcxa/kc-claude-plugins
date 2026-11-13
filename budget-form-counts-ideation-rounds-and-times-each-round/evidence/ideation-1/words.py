import re, sys
def words(t): return len(re.findall(r"[a-z0-9<>/_.\-]+", t.lower().replace("`", "")))
print(words(sys.stdin.read()))
