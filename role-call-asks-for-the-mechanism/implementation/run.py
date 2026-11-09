import subprocess, sys, json, pathlib, shlex, time
wt, ev, name, *cmd = sys.argv[1:]
ev=pathlib.Path(ev)
started=time.time()
with (ev/(name+'.log')).open('w') as log:
    result=subprocess.run(cmd,cwd=wt,stdout=log,stderr=subprocess.STDOUT)
data={'name':name,'command':shlex.join(cmd),'cwd':wt,'exit':result.returncode,'seconds':round(time.time()-started,2)}
(ev/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data));sys.exit(result.returncode)
