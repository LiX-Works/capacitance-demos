from pathlib import Path
import subprocess,os,time,json,hashlib
R=Path(__file__).resolve().parents[2];report={'sourceSha256':hashlib.sha256((R/'dist/Capacitance-Lab-offline.html').read_bytes()).hexdigest(),'steps':[]}
steps=[('interactions',['python','tests/interactions.py'],{}),('final-captures',['python','tests/capture_matrix.py'],{}),('transitions',['python','tests/capture_matrix.py'],{'MODE':'transitions'}),('playback',['python','tests/playback.py'],{})]
for name,cmd,env in steps:
 report['active']=name;(R/'qa/final-pipeline.json').write_text(json.dumps(report,indent=2));t=time.time()
 with (R/'qa'/(name+'.log')).open('w')as out:rc=subprocess.run(cmd,cwd=R/'source',env={**os.environ,**env},stdout=out,stderr=subprocess.STDOUT).returncode
 report['steps'].append({'name':name,'returncode':rc,'seconds':time.time()-t});print(name,rc,flush=True)
report['passed']=all(x['returncode']==0 for x in report['steps']);report['active']='complete';(R/'qa/final-pipeline.json').write_text(json.dumps(report,indent=2))
