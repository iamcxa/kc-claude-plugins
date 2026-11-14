import ast,subprocess,sys,json
def sh(*a):
    r=subprocess.run(a,capture_output=True,text=True); return r.stdout if r.returncode==0 else None
def methods(rev,path):
    s=sh('git','show',f'{rev}:{path}')
    if s is None: return {}
    out={}
    t=ast.parse(s)
    for c in ast.walk(t):
        if isinstance(c,ast.ClassDef):
            for f in c.body:
                if isinstance(f,(ast.FunctionDef,)) and f.name.startswith('test'):
                    out[c.name+'.'+f.name]=ast.get_source_segment(s,f)
    return out
res={}
for pr,m in [(858,'9bdc9f73083d8b2cf6a317a10f91a10a3d9fbb58'),(860,'c7d4464c5da2611d2653d3732f05a1c17eff5a9e'),(859,'c8d6dd40cf12ff6d9047e42e4d1041afa3bcf694'),(861,'629180e576a8b7dafd6d9bf12202f7d66958bd6e'),(870,'c2f035b6612f5edb42220576b3414e993531ffd6')]:
    files=sh('git','diff','--name-only',m+'^',m).split()
    tf=[f for f in files if f.rsplit('/',1)[-1].startswith('test') and f.endswith('.py')]
    new=[];mod=[]
    for f in tf:
        a=methods(m+'^',f);b=methods(m,f)
        for k,v in b.items():
            if k not in a:new.append((f,k))
            elif a[k]!=v:mod.append((f,k))
    res[pr]=dict(files=tf,added=len(new),modified=len(mod),N=len(new)+len(mod),names=[k for f,k in new+mod])
    print(pr,tf,len(new),len(mod))
json.dump(res,open(sys.argv[1],'w'),indent=1)
