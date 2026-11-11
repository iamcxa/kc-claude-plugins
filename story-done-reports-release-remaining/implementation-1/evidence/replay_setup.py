from pathlib import Path
import subprocess,tarfile,io,shutil,os
OUT=Path(os.environ['EVIDENCE_ROOT']);P=Path(os.environ['PRODUCT_WT']);D=Path(os.environ['DEV2_WT']);BASE='e8664a72b0f904e5dda3c391d52ab3abaca876b4'
OUT.mkdir(parents=True,exist_ok=True)
for name,src,code,state in [('relay',os.environ['RELAY_CLONE'],'0fce82296710d7bf3b89c2871adefd71db2e2957','77f5bb4e0e286467ec7078038e8bb9d680baddde'),('qnow',os.environ['QNOW_CLONE'],'ebc59cf96fdd5303e0dfccb1559d6048724e33ae','03838f912be5a74c972750128955524d03b5a6b6')]:
 dest=OUT/'replays'/name;dest.parent.mkdir(exist_ok=True)
 subprocess.run(['git','clone','--shared','--no-checkout',src,str(dest)],check=True)
 subprocess.run(['git','-C',str(dest),'checkout','--detach',code],check=True)
 remote=subprocess.check_output(['git','-C',src,'remote','get-url','origin'],text=True).strip()
 subprocess.run(['git','-C',str(dest),'remote','set-url','origin',remote],check=True)
 st=dest/'docs/dev2/.spacedock-state';subprocess.run(['git','clone','--shared','--no-checkout',src,str(st)],check=True);subprocess.run(['git','-C',str(st),'checkout','--detach',state],check=True)
for sha,paths,dest in [(BASE,['kc-journey-map','kc-dev-flow-2/scripts'],OUT/'base'),(BASE,['docs/dev2/README.md'],OUT/'replays/local'),('10149f1c5',[],OUT/'replays/local/docs/dev2/.spacedock-state')]:
 dest.mkdir(parents=True,exist_ok=True)
 with tarfile.open(fileobj=io.BytesIO(subprocess.check_output(['git','-C',str(P),'archive',sha,*paths]))) as t:t.extractall(dest,filter='data')
(OUT/'base/kc-journey-map/node_modules').symlink_to(P/'kc-journey-map/node_modules',target_is_directory=True)
for plugin,root in [('kc-journey-map',P),('kc-dev-flow-2',D)]:shutil.copytree(root/plugin,OUT/'integrated'/plugin,ignore=shutil.ignore_patterns('node_modules','__pycache__'))
shutil.copytree(D/'docs/adr',OUT/'integrated/docs/adr');(OUT/'integrated/kc-journey-map/node_modules').symlink_to(P/'kc-journey-map/node_modules',target_is_directory=True)
for name in ['relay','qnow']:
 map=OUT/'replays'/name/'docs/journey'/('spacedock-review.yaml' if name=='relay' else 'qnow.yaml')
 cp=subprocess.run(['node',str(OUT/'base/kc-journey-map/lib/journey-progress.mjs'),str(map),'--workflow-dir',str(OUT/'replays'/name/'docs/dev2')],capture_output=True,text=True)
 (OUT/(name+'-base.json')).write_text(cp.stdout)
 assert cp.returncode in (0,1),cp.stderr
