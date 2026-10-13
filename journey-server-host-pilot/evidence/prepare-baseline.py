from pathlib import Path
import shutil,sys,subprocess
root=Path(sys.argv[1]).resolve()
evidence=Path(__file__).resolve().parent
assert subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()=='6d0f8da951b5ea9ea50fca6bd3685fc360bf502f', 'use the pinned baseline checkout'
scratch=evidence/'.scratch/baseline'
scratch.mkdir(parents=True,exist_ok=True)
(evidence/'.scratch/empty.npmrc').write_text('')
for name in ['package.json','package-lock.json']:
 shutil.copyfile(root/'kc-journey-map'/name,scratch/name)
for sub in ['server','lib']:
 for src in (root/'kc-journey-map'/sub).rglob('*'):
  if src.is_file() and src.suffix in ['.ts','.tsx','.mjs','.css'] and '.test.' not in src.name:
   dest=scratch/src.relative_to(root/'kc-journey-map')
   dest.parent.mkdir(parents=True,exist_ok=True)
   shutil.copyfile(src,dest)
print(scratch)
