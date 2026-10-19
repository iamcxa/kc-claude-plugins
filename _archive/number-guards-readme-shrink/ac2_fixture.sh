set -u
S=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-number-guards-readme-shrink/kc-dev-flow-2/scripts/number_guards.py
R=/tmp/ngrs/fx; rm -rf $R; mkdir -p $R/db; cd $R
g(){ git -C $R -c user.email=t@e.com -c user.name=t -c commit.gpgsign=false "$@"; }
g init -q --initial-branch=main
for n in 1 2 3; do echo "SELECT $n;" > db/000${n}_m$n.sql; done
g add -A; g commit -qm base
g checkout -qb feat
echo "SELECT 4;" > db/0004_new.sql; g add -A; g commit -qm add; APPLIED=$(g rev-parse HEAD)
printf -- "---\nprofile: pilot\n---\n\n## Number guards\nMigration: 0004\nApplied at: uat $APPLIED\n" > /tmp/ngrs/task.md
printf -- "---\nprofile: poc\n---\n\n## Number guards\n" > /tmp/ngrs/poc.md
run(){ echo "\$ $1"; shift; python3 -B $S "$@"; echo "exit=$?"; }
echo "SELECT 44;" > db/0004_new.sql; g commit -qam edit
run "R2 edit" check --repo $R --migrations-path db --base main --head feat --task /tmp/ngrs/task.md
g reset -q --hard $APPLIED; g mv db/0004_new.sql db/0004_renamed.sql; g commit -qm rename
run "R2 rename" check --repo $R --migrations-path db --base main --head feat --task /tmp/ngrs/task.md
g reset -q --hard $APPLIED; g rm -q db/0004_new.sql; g commit -qm delete
run "R2 delete" check --repo $R --migrations-path db --base main --head feat --task /tmp/ngrs/task.md
g reset -q --hard $APPLIED
run "R6 poc" check --repo $R --migrations-path db --base main --head feat --task /tmp/ngrs/poc.md
run "no base" check --repo $R
run "no migrations-path (surfaces db)" check --repo $R --base main --head feat --task <(printf "Surfaces: db\n\n## Number guards\n")
run "no migrations-path (poc)" check --repo $R --base main --head feat --task /tmp/ngrs/poc.md
echo '$ --help | grep R1..R6'; python3 -B $S --help | grep -o 'R[1-6] [a-z]*' ; echo "exit=${pipestatus[1]:-$?}"
