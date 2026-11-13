"""Run an unchanged package test entry point, recording unittest results and owned fixture paths."""
import json,pathlib,re,runpy,subprocess,sys,tempfile,unittest
report=pathlib.Path(sys.argv.pop(1));script=pathlib.Path(sys.argv.pop(1)).resolve()
key='/'.join(script.parts[script.parts.index('kc-dev-flow-2')+1:])
sys.argv=[str(script),*sys.argv[1:]];sys.path.insert(0,str(script.parent))
rows=[];owned=set();runs=[]
original_temp=tempfile.mkdtemp
def mkdtemp(*a,**kw):
 value=original_temp(*a,**kw);owned.add(str(pathlib.Path(value).resolve()));return value
tempfile.mkdtemp=mkdtemp
original_run=subprocess.run
def run(*a,**kw):
 result=original_run(*a,**kw)
 for data in (result.stdout,result.stderr):
  if isinstance(data,bytes):data=data.decode(errors='replace')
  for path in re.findall(r'/(?:private/)?tmp/spacedock-dispatch/[A-Za-z0-9._-]+\.md',data or ''):
   owned.add(str(pathlib.Path(path).resolve()))
 return result
subprocess.run=run
class Result(unittest.TextTestResult):
 def row(self,test,status,message=None):
  name=test.id();name=key+':'+name.removeprefix('__main__.')
  rows.append(dict(name=name,status=status,**({'message':message} if message else {})))
 def addSuccess(self,test):super().addSuccess(test);self.row(test,'passed')
 def addFailure(self,test,error):super().addFailure(test,error);self.row(test,'failed',self._exc_info_to_string(error,test))
 def addError(self,test,error):super().addError(test,error);self.row(test,'failed',self._exc_info_to_string(error,test))
 def addSkip(self,test,reason):super().addSkip(test,reason);self.row(test,'skipped',reason)
 def addSubTest(self,test,subtest,error):
  super().addSubTest(test,subtest,error)
  if error:self.row(subtest,'failed',self._exc_info_to_string(error,test))
 def stopTestRun(self):
  super().stopTestRun();runs.append({'testsRun':self.testsRun,'failures':len(self.failures),'errors':len(self.errors),'skips':len(self.skipped)})
original_runner=unittest.TextTestRunner
class Runner(original_runner):
 def __init__(self,*a,**kw):kw['resultclass']=Result;super().__init__(*a,**kw)
 def run(self,suite):
  def inspect(node):
   if isinstance(node,unittest.TestSuite):
    for item in node:inspect(item)
   else:
    cls=type(node)
    if hasattr(cls,'remove_artifacts') and not getattr(cls,'_recording_cleanup',False):
     original=cls.remove_artifacts
     def cleanup(case):
      if hasattr(case,'scratch_namespace'):
       owned.add(str((pathlib.Path('/tmp').resolve()/'dev2'/case.scratch_namespace/case.slug).resolve()))
       for p in pathlib.Path('/tmp/spacedock-dispatch').glob('*'+case.slug+'*'):
        if p.is_file():owned.add(str(p.resolve()))
      return original(case)
     cls.remove_artifacts=cleanup;cls._recording_cleanup=True
  module=sys.modules.get('scratch')
  if module is not None and not getattr(module,'_recording_claim',False):
   claim=module.claim_root
   def claim_root(*a,**kw):
    path=claim(*a,**kw);owned.add(str(path.parent.parent.resolve()));return path
   module.claim_root=claim_root;module._recording_claim=True
  inspect(suite);return super().run(suite)
unittest.TextTestRunner=Runner
unittest.runner.TextTestRunner=Runner
try:runpy.run_path(str(script),run_name='__main__')
finally:
 report.write_text(json.dumps(rows,indent=1))
 report.with_suffix('.meta.json').write_text(json.dumps({'script':key,'unittest_runs':runs,'owned_paths':sorted(owned)},indent=1))
