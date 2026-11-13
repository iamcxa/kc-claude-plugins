"""Say whether a built dispatch (dispatch file + fetched stage definition) carries the Pilot probe text."""
import re, sys
seen, inputs = open(sys.argv[1]).read(), "".join(open(p).read() for p in sys.argv[2:])
flat = " ".join(seen.split())
need = {"permission": "Pilot ideation builds a throwaway probe on local branch `poc/<slug>`",
        "bounds": "never pushed or deployed and uses no credential or shared environment",
        "proof-run": "evidence command runs once on it, recording command, exit and output path",
        "not-provable": "`Not provable now`", "round": "A probe round is one ideation dispatch"}
have = [k for k, v in need.items() if v in flat]
ban = "Ideation writes no repository file, branch or commit" in flat
hand = bool(re.search(r"throwaway probe|may write code only", inputs))
state = "carries" if len(have) == len(need) and not hand else ("ban-only" if ban and not have and not hand else "neither")
print(f"{state} found={','.join(have) or 'none'} old-ban={ban} fo-line-in-inputs={hand}")
