# Station 2 — Captain answers (verbatim, 2026-09-09)

Q: 把「派工站改用 spacedock dispatch build 派 dev entity」列為下一個 ship-flow 批次的首項，連同 DEV-151～155 與 #399，還是留給 plan session 一起排？
A (Captain): 「前者，先做完這一批」

Ruling behind DEV-156, recorded by the relay session on spacedock-dev/subspace-relay#191 § "A fourth finding": the dispatch station dispatches dev entities, several in a row, via `spacedock dispatch build --entity-path <task> --stage <stage>`; one call per task, one claim per task, fence unchanged; the Evidence block arrives after the task's validation stage; accept-evidence.sh at BASE_SHA is the third check. The FO presented it as a relayed statement and the Captain chose the option that admits it.
