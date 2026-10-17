import sys
BASE, CAND = (open(p).read() for p in sys.argv[1:3])
SPANS = [("startup: whole README", None, None),
         ("dispatch build: Stages paragraph", "FO resolves `<package>` in this workflow", "### `backlog`"),
         ("ideation gate: ### ideation", "### `ideation`", "### `implementation`"),
         ("amendment entry: ## Captain amendments", "## Captain amendments\n\nA change", "## Affected documents"),
         ("merge ask: ## Delivery authority", "## Delivery authority", "## Extensions")]
def words(text, a, b):
    if a is None:
        return len(text.split())
    i = text.index(a)
    return len(text[i:text.index(b, i)].split())
for name, a, b in SPANS:
    print(f"{name}\t{words(BASE, a, b)}\t{words(CAND, a, b)}")
