import datetime,hashlib,json,os,pathlib,subprocess,sys
out=pathlib.Path(__file__).parent
name,cwd,*cmd=sys.argv[1:]
identity=json.loads((out/'identity.json').read_text())
meta=dict(name=name,cwd=cwd,argv=cmd,identity=identity,started=datetime.datetime.now(datetime.timezone.utc).isoformat(),env={k:os.environ[k] for k in ('SPACEDOCK_BIN','PYTHONDONTWRITEBYTECODE','GIT_DIR','GIT_WORK_TREE') if k in os.environ})
with (out/(name+'.log')).open('w') as log:
 p=subprocess.Popen(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT)
 meta['pid']=p.pid
 (out/(name+'-running.json')).write_text(json.dumps(meta,indent=2)+'\n')
 code=p.wait()
meta.update(exit=code,ended=datetime.datetime.now(datetime.timezone.utc).isoformat(),log=name+'.log',sha256=hashlib.sha256((out/(name+'.log')).read_bytes()).hexdigest())
(out/(name+'.json')).write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps(meta))
sys.exit(code)
