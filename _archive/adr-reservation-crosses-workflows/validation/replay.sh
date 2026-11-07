#!/usr/bin/env bash
set -euo pipefail
NG=$1; R=$(mktemp -d); cd "$R"; c() { git -c user.email=r@x -c user.name=r commit -qm "$1"; }
git init -q -b main origin; mkdir -p origin/docs/adr
for n in 0058 0059; do echo "# $n" > origin/docs/adr/$n-x.md; done
git -C origin add -A; (cd origin && c base)
git -C origin checkout -q --orphan spacedock-state/dev2; git -C origin read-tree --empty; git -C origin clean -fdq
printf -- '---\ntitle: g\n---\n\n## Number guards\n\nADR: 0060\n' > origin/gate-presentation.md
git -C origin add gate-presentation.md; (cd origin && c state); git -C origin checkout -q main
git clone -q --single-branch -b main origin jm; mkdir -p jm/docs/dev2/st
printf -- '---\nstate: st\ntrunk: main\n---\n' > jm/docs/dev2/README.md
printf -- '---\ntitle: s\n---\n\n## Number guards\n\n' > jm/docs/dev2/st/slice3.md
echo "A1 reserve:"; python3 "$NG" reserve --kind adr --repo jm --workflow-dir jm/docs/dev2 --task jm/docs/dev2/st/slice3.md || true
printf -- 'ADR: 0060\n' >> jm/docs/dev2/st/slice3.md
git -C jm checkout -qb s3; echo x > jm/docs/adr/0060-distinct.md; git -C jm add docs/adr; (cd jm && c s3)
echo "A2 check, held 0060:"; python3 "$NG" check --repo jm --workflow-dir jm/docs/dev2 --task jm/docs/dev2/st/slice3.md --head s3 || echo "exit $?"
git -C jm checkout -qb s3free main; echo x > jm/docs/adr/0061-free.md; git -C jm add docs/adr; (cd jm && c free)
sed -i.bak 's/^ADR: 0060$/ADR: 0061/' jm/docs/dev2/st/slice3.md
echo "A3 check, free 0061:"; python3 "$NG" check --repo jm --workflow-dir jm/docs/dev2 --task jm/docs/dev2/st/slice3.md --head s3free || echo "exit $?"
mkdir -p w/st/rel; printf -- '---\nstate: st\ntrunk: main\n---\n' > w/README.md
printf -- '---\ntitle: r\n---\n\n## Number guards\n\nADR: 0060\n' > w/st/rel/index.md
printf -- '---\ntitle: o\n---\n\n## Number guards\n\n' > w/st/ops.md
echo "B1 reserve, folder-form sibling holds 0060:"; python3 "$NG" reserve --kind adr --repo origin --workflow-dir w --task w/st/ops.md || true
rm -rf "$R"
