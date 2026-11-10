from pathlib import Path
import hashlib,io,json,subprocess,tarfile
p=Path(__file__).resolve().parent;m=json.loads((p/'identity.json').read_text());repo=m['product_repo']
assert subprocess.check_output(['git','-C',repo,'rev-parse','HEAD'],text=True).strip()==m['head']
assert subprocess.check_output(['git','-C',repo,'branch','--show-current'],text=True).strip()=='spacedock-ensign/amendment-checked-when-written'
assert subprocess.check_output(['git','-C',repo,'status','--porcelain'],text=True)==''
archive=subprocess.check_output(['git','-C',repo,'archive',m['head'],'kc-dev-flow-2'])
count=0
with tarfile.open(fileobj=io.BytesIO(archive)) as t:
 for member in t.getmembers():
  if member.isfile():
   assert t.extractfile(member).read()==(p/'candidate'/member.name).read_bytes(),member.name
   count+=1
(p/'final-identity.json').write_text(json.dumps({**m,'branch':'spacedock-ensign/amendment-checked-when-written','clean_product':True,'package_files_byte_equal_to_candidate':count},indent=2)+'\n')
manifest={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.iterdir()) if f.is_file() and f.name!='manifest.json'}
(p/'manifest.json').write_text(json.dumps({'candidate':m['head'],'files':manifest},indent=2)+'\n')
print('Product clean; all',count,'package source files still match the exact candidate; evidence manifest sealed.')
