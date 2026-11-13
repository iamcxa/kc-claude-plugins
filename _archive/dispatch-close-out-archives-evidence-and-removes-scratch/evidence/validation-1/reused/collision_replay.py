"""Usage: python3 -B collision_replay.py SCRIPTS OWNED_OUTPUT; exit 1 exposes lost peer work."""
import contextlib,io,json,os,pathlib,subprocess,sys,uuid
sys.path.insert(0,sys.argv[1]);import scratch
out=pathlib.Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=True)
env={**os.environ,"GIT_AUTHOR_NAME":"Fixture","GIT_COMMITTER_NAME":"Fixture","GIT_AUTHOR_EMAIL":"fixture@example.invalid","GIT_COMMITTER_EMAIL":"fixture@example.invalid","GIT_CONFIG_COUNT":"2","GIT_CONFIG_KEY_0":"commit.gpgsign","GIT_CONFIG_VALUE_0":"false","GIT_CONFIG_KEY_1":"core.hooksPath","GIT_CONFIG_VALUE_1":"/dev/null"}
def git(repo,*args):
    return subprocess.run(["git","-C",str(repo),*map(str,args)],env=env,capture_output=True,text=True,check=True).stdout
rows=[];log=io.StringIO()
for case in ("same-basename","same-origin-clones"):
    token="collision-replay-"+uuid.uuid4().hex
    repos=[];folders=[];roots=[]
    for number in (1,2):
        repo=out/f"{case}-{number}";repo.mkdir();git(repo,"init","-q","-b","main")
        owner=number if case=="same-basename" else 1
        git(repo,"remote","add","origin",f"https://example.invalid/owner-{owner}/{token}.git")
        (repo/"tracked").write_text("original");git(repo,"add","tracked");git(repo,"commit","-qm","test: seed")
        folder=repo/"task";(folder/"dispatch").mkdir(parents=True);(folder/"dispatch/implementation-1.md").write_text("# dispatch\n")
        if hasattr(scratch,"claim_root"):root=scratch.claim_root(repo,folder,"implementation-1")
        else:
            root=scratch.root_for(repo,folder.name,"implementation-1");root.mkdir(parents=True,exist_ok=True)
        repos.append(repo);folders.append(folder);roots.append(root)
    checkout=roots[1]/"peer-checkout";git(repos[1],"worktree","add","--detach",checkout)
    (checkout/"uncommitted").write_text("peer's uncommitted work")
    with contextlib.redirect_stdout(log):scratch.close(folders[0],"implementation-1")
    survives=(checkout/"uncommitted").is_file()
    rows.append(dict(case=case,roots_distinct=roots[0]!=roots[1],peer_uncommitted_file_survives=survives,peer_worktree_registered=str(checkout) in git(repos[1],"worktree","list","--porcelain")))
    if survives:
        with contextlib.redirect_stdout(log):scratch.close(folders[1],"implementation-1")
    else:git(repos[1],"worktree","prune")
    for namespace in set(root.parent.parent for root in roots):
        if namespace.is_dir() and not any(namespace.iterdir()):namespace.rmdir()
(out/"results.json").write_text(json.dumps(rows,indent=2));(out/"commands.log").write_text(log.getvalue())
print(json.dumps(rows))
sys.exit(not all(row["roots_distinct"] and row["peer_uncommitted_file_survives"] and row["peer_worktree_registered"] for row in rows))
