#!/usr/bin/env bash
# usage: row71-own-probe.sh <pinned-scripts-dir>   (kc-dev-flow-2/scripts exported at c2f035b66)
set -u
S=$(cd "$1" && pwd); T=$(mktemp -d); cd "$T"
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_AUTHOR_NAME=v GIT_AUTHOR_EMAIL=v@x GIT_COMMITTER_NAME=v GIT_COMMITTER_EMAIL=v@x
G="python3 -B $S/number_guards.py"
git init -q -b main r && cd r && mkdir migrations && echo 'create table a(x int);' > migrations/0001_a.sql
git add . && git commit -qm base && BASE=$(git rev-parse HEAD)
git checkout -qb feat && echo 'create table b(y int);' > migrations/0002_b.sql && git add . && git commit -qm add && APPLIED=$(git rev-parse HEAD)
mk(){ printf -- "---\nprofile: pilot\n---\n## Number guards\nMigration: 0002\n%s\n" "$1" > ../task.md; }
chk(){ $G check --repo . --base "$BASE" --migrations-path migrations --task ../task.md --head "$(git rev-parse HEAD)" >/dev/null 2>&1; echo "exit=$? :: $1"; }
mk "Applied at: staging $APPLIED"; chk "unchanged-after-applied (expect 0)"
echo 'alter;' >> migrations/0002_b.sql; git commit -qam edit; chk "edit-applied (expect 1)"
git reset -q --hard "$APPLIED"; git rm -q migrations/0002_b.sql; git commit -qm del; chk "delete-applied (expect 1)"
git reset -q --hard "$APPLIED"; echo 'alter;' >> migrations/0002_b.sql; git commit -qam edit
mk ""; chk "edit-no-record control (expect 0)"
mk "Applied at: $APPLIED"; chk "record without environment token (expect 0: not matched)"
mk "applied at: staging $APPLIED"; chk "lowercase label (expect 0: not matched)"
