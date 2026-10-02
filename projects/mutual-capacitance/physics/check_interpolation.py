"""A posteriori midpoint checks of the displayed linear C interpolation.
No interpolated frame is advertised as another PDE solve. These fresh solves
quantify only midpoint discrepancies, not a rigorous interval error bound.
"""
from pathlib import Path
import json
from bem import Solution
from provenance import load_dataset
R=Path(__file__).resolve().parents[1];d=load_dataset(R);rows=[]
for er in [1,4]:
 c=d['curves'][str(er)]
 for a,b in zip(c,c[1:]):
  theta=(a['theta_deg']+b['theta_deg'])/2;v=Solution(theta,er,n=128);interp=(a['C_F']+b['C_F'])/2
  rows.append({'er':er,'theta_deg':theta,'bracket':[a['theta_deg'],b['theta_deg']],'solved_F':v.C,'interpolated_F':interp,'relativeDifference':interp/v.C-1})
 print(er,'worst midpoint',max((abs(x['relativeDifference'])for x in rows if x['er']==er)),flush=True)
(R/'qa/interpolation-check.json').write_text(json.dumps({'parameterSha256':d['parameterSha256'],'additionalIndependentMidpointSolves':len(rows),'scope':'Midpoint samples only, not a proven maximum over each interval or field topology validation.','rows':rows},indent=2),encoding='utf-8')
