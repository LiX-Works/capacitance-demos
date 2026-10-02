from pathlib import Path
from copy import deepcopy
import json,time
import numpy as np
from scipy.special import ellipk
from shapely.geometry import Polygon
from model import P,polygons,upper,hinge,analytic
from bem import Solution
ROOT=Path(__file__).resolve().parents[1]
trials=[]
for D in [.0005,.001,.002]:
 p=deepcopy(P);p['initial_clear_gap_m']=D;p['dielectric']['y_bottom_m']=D*.125;p['dielectric']['thickness_m']=D*.40
 row={'D_mm':D*1e3,'ideal_pF':p['epsilon0_F_per_m']*p['length_m']*p['width_m']/D*1e12,'values':[]}
 for a in [0,10,30,90,180]:
  air=Solution(a,1,n=96,params=p);di=Solution(a,4,n=96,params=p)
  row['values'].append({'theta':a,'air_pF':air.C*1e12,'dielectric_pF':di.C*1e12,'model_relative_gain':di.C/air.C-1})
 trials.append(row)
print(json.dumps(trials,indent=2))
(ROOT/'qa/parameter-trials.json').write_text(json.dumps(trials,indent=2),encoding='utf-8')
