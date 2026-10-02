from pathlib import Path
import json,base64,time
import numpy as np
from model import P
from bem import Solution
from provenance import load_dataset
R=Path(__file__).resolve().parents[1];d=load_dataset(R)
box=[-.003,.023,-.00055,.0042];nx,ny=141,96;X,Y=np.meshgrid(np.linspace(box[0],box[1],nx),np.linspace(box[2],box[3],ny));pts=np.stack([X.ravel(),Y.ravel()],1)
maps={}
for er in [1,4]:
 arr=[]
 for theta in d['angles']:
  s=Solution(theta,er,n=128);V=s.potential(pts);E=np.linalg.norm(s.field(pts),axis=1);inside=np.zeros(len(pts),bool)
  for poly in s.polys[:2]:
   a=poly*s.scale;b=np.roll(a,-1,axis=0);v=b-a;delta=pts[:,None,:]-a;inside|=np.all(v[None,:,0]*delta[:,:,1]-v[None,:,1]*delta[:,:,0]>=-1e-14,axis=1)
  v=np.round(np.clip((V+P['voltage_difference_V']/2)/P['voltage_difference_V'],0,1)*65534).astype('<u2');e=np.round(np.clip((np.log10(np.maximum(E,.01))+2)/7,0,1)*65534).astype('<u2');v[inside]=65535;e[inside]=65535
  arr.append({'theta_deg':theta,'potential_u16':base64.b64encode(v.tobytes()).decode(),'field_log_u16':base64.b64encode(e.tobytes()).decode()})
 maps[str(er)]=arr;print('local',er,'finished',flush=True)
d['localFieldGrid']={'box_m':box,'nx':nx,'ny':ny,'description':'A display sampling window near the material: not a changed physical geometry or computational domain.'};d['localFields']=maps
s=json.dumps(d,separators=(',',':'));(R/'data/results.json').write_text(s,encoding='utf-8');(R/'source/src/physics/data.ts').write_text('/* Generated SI electrostatics data, never measured sensor data. */\nexport const DATA:any = '+s+';\n',encoding='utf-8');print('bytes',len(s),flush=True)
