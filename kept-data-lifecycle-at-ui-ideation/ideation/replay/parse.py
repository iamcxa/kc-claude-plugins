import json,sys,re
text=open(sys.argv[1]).read(); raw=open(sys.argv[2]).read()
raw=raw[raw.index('{'):]
d,_=json.JSONDecoder().raw_decode(raw); norm=lambda s:' '.join(s.split())
T=norm(text); score=0; row=[]
for k in [f"C{i}" for i in range(1,10)]:
    h=int(d[k]["hit"]); q=d[k].get("quote","")
    ok = h==1 and bool(norm(q)) and norm(q) in T
    score+= 1 if ok else 0
    row.append(f"{k}={'1' if ok else ('q?' if h==1 else '0')}")
print(score, ' '.join(row))
