import json,subprocess,sys,os,time
cwd=sys.argv[1]
p=subprocess.Popen(["codex","app-server"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,cwd=cwd)
def send(o): p.stdin.write(json.dumps(o)+"\n"); p.stdin.flush()
def recv(id_):
    while True:
        l=p.stdout.readline()
        if not l: return None
        m=json.loads(l)
        if m.get("id")==id_: return m
send({"id":1,"method":"initialize","params":{"clientInfo":{"name":"t","version":"0"}}}); r=recv(1)
send({"method":"initialized"})
send({"id":2,"method":"skills/list","params":{"cwds":[cwd],"forceReload":True}}); r=recv(2)
p.kill()
for e in r["result"]["data"]:
    for s in e["skills"]: print(s["name"], s.get("path",""))
    if e.get("errors"): print("errors",e["errors"])
