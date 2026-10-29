# usage: crawl.py <built-site> <plugin>...   lists built files, flags any outside the named plugins, and checks every link, image and anchor
import sys,os,re
from html.parser import HTMLParser
site=sys.argv[1]; base='/kc-claude-plugins'
files=[]
for r,_,fs in os.walk(site):
    for f in fs: files.append(os.path.relpath(os.path.join(r,f),site))
files.sort()
print("BUILT FILES:"); [print(" ",f) for f in files]
plugins=sys.argv[2:]
internal=[f for f in files if not (f in ('index.html','404.html','feed.xml','redirects.json','robots.txt','sitemap.xml') or f.startswith('assets/') or f.split('/')[0] in plugins)]
print("INTERNAL PATHS PRESENT:",internal or "none")
import json
sd=os.path.join(site,'assets/js/search-data.json')
if os.path.exists(sd):
    urls=sorted({v.get('url') for v in json.load(open(sd)).values()})
    print("SEARCH INDEX PAGES:",urls)
class P(HTMLParser):
    def __init__(s): super().__init__(); s.links=[]; s.ids=set()
    def handle_starttag(s,t,a):
        a=dict(a)
        if 'id' in a: s.ids.add(a['id'])
        for k in ('href','src'):
            if k in a: s.links.append((t,a[k]))
pages={}
for f in files:
    if f.endswith('.html'):
        p=P(); p.feed(open(os.path.join(site,f)).read()); pages[f]=p
bad=0
for f,p in pages.items():
    for t,l in p.links:
        if l.startswith(('http://','https://','mailto:','data:')): 
            continue
        path,_,frag=l.partition('#')
        if path=='' : tgt=f
        else:
            if path.startswith(base+'/'): tgt=path[len(base)+1:]
            elif path.startswith('/'): print("ABSOLUTE-NO-BASE",f,l); bad+=1; continue
            else: tgt=os.path.normpath(os.path.join(os.path.dirname(f),path))
            if tgt.endswith('/') or tgt=='' : tgt=os.path.join(tgt,'index.html')
        if not os.path.exists(os.path.join(site,tgt)): print("MISSING",f,l,'->',tgt); bad+=1; continue
        if frag and tgt in pages and frag not in pages[tgt].ids: print("NO ANCHOR",f,l); bad+=1
print("LINK/IMAGE PROBLEMS:",bad)
ext=sorted({l for p in pages.values() for t,l in p.links if l.startswith('http') and 'iamcxa.github.io' not in l})
print("EXTERNAL LINKS:"); [print(" ",e) for e in ext]
