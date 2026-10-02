from pathlib import Path
import argparse,sys,json,hashlib,base64,math,platform,importlib.metadata,subprocess,re
sys.dont_write_bytecode=True
parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output',type=Path);args=parser.parse_args();root=args.root.resolve();out=args.output or root/'qa/scientific-smoke.json';mutual=root/'projects/mutual-capacitance';proxi=root/'projects/proxitouch'
import numpy as np
sys.path.insert(0,str(mutual/'physics'))
from bem import Solution
from model import polygons
checks=[]
def check(name,passed,details=None):
 checks.append({'name':name,'passed':bool(passed),'details':details});print(('PASS ' if passed else 'FAIL ')+name,flush=True)
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def tsdata(p):
 text=p.read_text(encoding='utf-8');return json.loads(text[text.index('=')+1:].strip().removesuffix(';'))
d=load(mutual/'data/results.json');params=load(mutual/'parameters.json');sha=hashlib.sha256((mutual/'parameters.json').read_bytes()).hexdigest()
check('mutual parameter SHA and embedded parameters agree',d['parameterSha256']==sha and params==d['parameters'],{'sha256':sha})
check('mutual generated TypeScript and results JSON are semantically identical',tsdata(mutual/'source/src/physics/data.ts')==d)
rows=[]
for angle in [0,30,90,180]:
 for er in [1,4]:
  frozen=next(v for v in d['curves'][str(er)] if v['theta_deg']==angle);sol=Solution(angle,er,n=128);delta=sol.C/frozen['C_F']-1
  rows.append({'theta_deg':angle,'er':er,'longPanels':128,'frozen_C_F':frozen['C_F'],'fresh_C_F':sol.C,'relativeDifference':delta,'linearResidual':sol.residual})
  print('BEM',angle,er,'relative',delta,flush=True)
check('eight n128 BEM checkpoint capacitances agree with frozen data',all(abs(v['relativeDifference'])<1e-9 for v in rows),{'relativeTolerance':1e-9,'rows':rows})
curves=[v for ls in d['curves'].values() for v in ls]+d['er_scan'];unit_err=max(abs(v['C_F']/(v['Cprime_F_per_m']*params['width_m'])-1) for v in curves)
check('mutual C equals Cprime times width across stored curve and er nodes',unit_err<1e-12,{'nodes':len(curves),'maxRelativeDifference':unit_err,'C_units':'F','Cprime_units':'F/m','width_units':'m'})
check('er scan has seven expected independently stored nodes at zero degrees',[v['er'] for v in d['er_scan']]==[1,1.5,2,3,4,6,8] and all(v['theta_deg']==0 for v in d['er_scan']))
codec=[]
def maps(group,grid,series):
 nx,ny=grid['nx'],grid['ny'];box=grid['box_m'];X,Y=np.meshgrid(np.linspace(box[0],box[1],nx),np.linspace(box[2],box[3],ny));pts=np.stack([X.ravel(),Y.ravel()],1)
 for er,ls in series.items():
  for item in ls:
   angle=item['theta_deg'];a=np.frombuffer(base64.b64decode(item['potential_u16'],validate=True),dtype='<u2');b=np.frombuffer(base64.b64decode(item['field_log_u16'],validate=True),dtype='<u2');inside=np.zeros(len(pts),bool)
   for poly in polygons(angle,dielectric=False):
    z=np.roll(poly,-1,axis=0);v=z-poly;delta=pts[:,None,:]-poly;inside|=np.all(v[None,:,0]*delta[:,:,1]-v[None,:,1]*delta[:,:,0]>=-1e-14,axis=1)
   lengths=len(a)==nx*ny and len(b)==nx*ny;equal=lengths and np.array_equal(a==65535,b==65535);correct=lengths and np.array_equal(a==65535,inside)
   codec.append({'family':group,'er':er,'theta_deg':angle,'samples':len(a),'lengthPassed':lengths,'potentialAndStrengthMasksAgree':equal,'maskMatchesConductorPolygons':correct,'missingSamples':int((a==65535).sum())})
maps('global',d['fieldGrid'],d['fields']);maps('local',d['localFieldGrid'],d['localFields']);maps('erFields',d['fieldGrid'],{key:[value] for key,value in d['erFields'].items()})
check('all U16LE field maps have expected lengths and conductor masks',all(v['lengthPassed'] and v['potentialAndStrengthMasksAgree'] and v['maskMatchesConductorPolygons'] for v in codec),{'maps':len(codec),'rows':codec,'codec':'base64 little-endian unsigned 16-bit; 65535 missing; potential min/max from fieldGrid; E log10 range -2..5'})
angles=d['angles'];pathbad=[]
for key,ls in d['fields'].items():
 if len(ls)!=len(angles) or [v['theta_deg'] for v in ls]!=angles:pathbad.append(key+':angles')
 for item in ls:
  p=item['paths_m']
  if len(p)!=11 or any(len(v)!=88 or any(len(point)!=2 or not all(math.isfinite(t) for t in point) for point in v) for v in p):pathbad.append(str((key,item['theta_deg'])))
check('mutual angular fieldline schema and coordinates are finite',not pathbad,{'failures':pathbad,'pathsPerPose':11,'pointsPerPath':88,'coordinate_units':'m'})
for name,families in [('revisionFieldData',['morph','approach','square']),('haloFieldData',['states'])]:
 data=tsdata(proxi/f'source/src/physics/{name}.ts');families_data=[(family,data[family]) for family in families]
 if name=='haloFieldData':families_data.append(('baseline',[data['baseline']]))
 bad=[];poses=0
 for family,series in families_data:
  for i,item in enumerate(series):
   poses+=1
   if not math.isfinite(item['coupling']) or not math.isfinite(item['residual']) or item['coupling']<0 or any(len(p)!=56 or any(len(point)!=2 or not all(math.isfinite(v) for v in point) for point in p) for p in item['paths']):bad.append([family,i])
 check('proxi '+name+' finite precomputed paths and scalar schema',not bad,{'poses':poses,'failures':bad,'coordinate_units':'arbitrary teaching units; not SI sensor dimensions'})
node_code=r'''(async()=>{const {pathToFileURL}=require('url'),path=require('path');const base=path.resolve(process.argv[1],'projects/proxitouch/dist/js');const {interaction}=await import(pathToFileURL(base+'/physics/interaction.js').href),{MicroAssembly}=await import(pathToFileURL(base+'/models/Dome.js').href),{FringeField}=await import(pathToFileURL(base+'/models/FringeField.js').href);const fringe=new FringeField();fringe.set(1,0);fringe.update();const finalLowerCentre=Array.from(fringe.tx.world).slice(12,15),finalUpperCentre=Array.from(fringe.rx.world).slice(12,15);const g=new MicroAssembly();const rows=[];for(const depth of[-1,-.08,-.04,0,.1,.5,1]){const s=interaction(depth);g.set(depth);rows.push({depth,signalArea:s.area,geometryArea:g.area,areaDifference:g.area-s.area,planeY:g.planeY,contact:s.contact,finite:Object.values(s).filter(x=>typeof x==='number').every(Number.isFinite),normalized:['areaNormalized','pressure','hc','cb','halo','core','haloDominance','coreDominance'].every(k=>s[k]>=0&&s[k]<=1)});}console.log(JSON.stringify({rows,pivot:fringe.pivot.position,finalLowerCentre,finalUpperCentre,halfTurn:fringe.pivot.rotation[2],geometryPass:Math.abs(finalLowerCentre[1]-finalUpperCentre[1])<1e-6&&Math.abs(finalLowerCentre[0]+1.85)<1e-6&&Math.abs(finalUpperCentre[0]-1.85)<1e-6&&Math.abs(fringe.pivot.rotation[2]+Math.PI)<1e-12}));})();'''
r=subprocess.run(['node','-e',node_code,str(root)],capture_output=True,text=True,encoding='utf-8',check=True);state=json.loads(r.stdout)
check('proxi stored runtime contact area agrees with geometry at seven depths',state['geometryPass'] and all(x['finite'] and x['normalized'] and abs(x['areaDifference'])<1e-12 for x in state['rows']),state)
report={'scope':'Limited offline scientific smoke audit. Exactly eight n128 BEM solves. No field tracing, full regeneration, browser UI, or experimental validation. These samples do not establish whole-model correctness, continuum convergence, or 3D dielectric accuracy.','environment':{'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'libraries':{name:importlib.metadata.version(name) for name in ['numpy','scipy','shapely','numba']},'node':subprocess.check_output(['node','--version'],text=True).strip()},'checks':checks,'passed':all(c['passed'] for c in checks)}
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',str(out),flush=True);sys.exit(0 if report['passed'] else 1)
