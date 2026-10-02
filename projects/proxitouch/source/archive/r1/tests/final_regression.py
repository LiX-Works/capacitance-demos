"""Final-source regression. Performance runs alone; static captures may overlap playback."""
from pathlib import Path
import subprocess,os,json,time,hashlib
ROOT=Path(__file__).resolve().parents[2];source=ROOT/'source';status={'sourceSha256':hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest(),'steps':[]}
(ROOT/'qa/final').mkdir(parents=True,exist_ok=True)
def save(): (ROOT/'qa/final/pipeline.json').write_text(json.dumps(status,indent=2))
def run(name,cmd,env=None):
 print('START',name,flush=True);start=time.time();status['active']=name;save()
 with (ROOT/'qa/final'/(name+'.log')).open('w') as log:
  result=subprocess.run(cmd,cwd=source,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,**(env or {})})
 status['steps'].append({'name':name,'returncode':result.returncode,'elapsedSeconds':round(time.time()-start,2)});save()
 if result.returncode:raise RuntimeError(name+' failed')
 print('DONE',name,flush=True)
run('performance',['python','tests/performance.py'])
playlog=(ROOT/'qa/final/full-playback.log').open('w');play=subprocess.Popen(['python','tests/full_playback.py'],cwd=source,stdout=playlog,stderr=subprocess.STDOUT);status['playbackPid']=play.pid;save()
run('scenes-1920',['python','tests/capture_scenes.py',str(ROOT/'qa/captures/1920x1080')])
run('scenes-2560',['python','tests/capture_scenes.py',str(ROOT/'qa/captures/2560x1440')],{'PT_WIDTH':'2560','PT_HEIGHT':'1440'})
run('transitions',['python','tests/capture_transitions.py',str(ROOT/'qa/transitions')])
run('extras',['python','tests/final_extras.py'],{'PT_OFFLINE_BROWSER':'1'})
run('explore',['python','tests/explore_interaction.py'])
status['active']='waiting-for-unaccelerated-playback';save();code=play.wait(timeout=1100);playlog.close()
status['steps'].append({'name':'full-playback','returncode':code});status['active']='complete';
checks={}
for size in ['1920x1080','2560x1440']:
 d=json.loads((ROOT/'qa/captures'/size/'report.json').read_text());checks[size]=len(d['scenes'])==46 and not d['errors']
d=json.loads((ROOT/'qa/transitions/report.json').read_text());checks['transitionCaptureCount']=len(d['captures'])==90 and not d['errors'];checks['fullPlayback']=json.loads((ROOT/'qa/full-playback/report.json').read_text()).get('complete',False)
checks['sameFinalSource']=hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest()==status['sourceSha256'];status['checks']=checks;status['complete']=all(checks.values()) and code==0;save();print('FINAL',status['complete'],flush=True)
