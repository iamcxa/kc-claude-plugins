# usage: build.sh  -> creates /tmp/kc-adr-copy-sb with 3 variant marketplaces (bare repos) and 3 sandbox homes
set -e
R=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo
T=/tmp/kc-adr-copy-sb; rm -rf $T; mkdir -p $T
for f in ~/.claude/plugins/known_marketplaces.json ~/.claude/plugins/installed_plugins.json ~/.claude/settings.json ~/.codex/config.toml; do shasum $f; done > $T/real.sha
SHA=$(git -C $R rev-parse origin/main); echo $SHA > $T/base.sha
for V in A B C; do
  W=$T/mk$V; mkdir -p $W $T/bare$V $T/home$V $T/claude$V $T/codex$V
  git -C $R archive $SHA kc-dev-flow-2 kc-adr .claude-plugin | tar -x -C $W
  python3 - $W <<'P'
import json,sys
p=sys.argv[1]+"/.claude-plugin/marketplace.json"
d=json.load(open(p)); d["name"]="mk"; d["plugins"]=[x for x in d["plugins"] if x["name"] in("kc-dev-flow-2","kc-adr")]
json.dump(d,open(p,"w"),indent=1)
P
done
# A: whole kc-adr directory copied inside the dev2 plugin
cp -R $T/mkA/kc-adr $T/mkA/kc-dev-flow-2/kc-adr
# B: kc-adr's skill directory copied into dev2's skills/
cp -R $T/mkB/kc-adr/skills/read-adr $T/mkB/kc-dev-flow-2/skills/read-adr
# C: the two-file design: copies at the dev2 paths (today they already exist; make kc-adr the source)
cmp $T/mkC/kc-adr/scripts/adr_lint.py $T/mkC/kc-dev-flow-2/scripts/adr_lint.py || echo "C: adr_lint.py differs (base)"
cp $T/mkC/kc-adr/scripts/adr_lint.py $T/mkC/kc-dev-flow-2/scripts/adr_lint.py
cp $T/mkC/kc-adr/references/adr-template.md $T/mkC/kc-dev-flow-2/references/adr-template.md
for V in A B C; do
  printf '[user]\n name = v\n email = v@example.com\n[url "file://%s/bare%s/"]\n insteadOf = https://github.com/vpoc/\n insteadOf = git@github.com:vpoc/\n[protocol "file"]\n allow = always\n' $T $V > $T/home$V/.gitconfig
  (cd $T/mk$V && git init -q -b main && git add -A && git commit -qm "variant $V" && git init -q --bare $T/bare$V/mk.git && git push -q $T/bare$V/mk.git main)
  cat > $T/env$V.sh <<E2
export RH=$HOME HOME=$T/home$V CLAUDE_CONFIG_DIR=$T/claude$V CODEX_HOME=$T/codex$V GIT_CONFIG_GLOBAL=$T/home$V/.gitconfig
E2
done
echo built
