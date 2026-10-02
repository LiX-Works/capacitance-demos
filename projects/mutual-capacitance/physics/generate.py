from pathlib import Path
from copy import deepcopy
import json,hashlib,time,base64,os
import numpy as np
from scipy.special import ellipk
from scipy.interpolate import PchipInterpolator
from shapely.geometry import Polygon
from model import P,polygons,upper,analytic
from bem import Solution
from provenance import parameter_hash,require_validation
ROOT=Path(__file__).resolve().parents[1]
N=128
ANGLES=sorted(set(P['angle_scan_deg']+[.25,.5,1,3,4,7.5]))
# This is a display sampling grid, not a mesh used by the BEM solver.
BOX=[-.030,.028,-.010,.030];NX,NY=117,101

def closest(points,poly):
    a=poly;b=np.roll(poly,-1,axis=0);v=b-a
    d=points[:,None,:]-a[None,:,:];u=np.clip(np.einsum('ijk,jk->ij',d,v)/np.sum(v*v,axis=1),0,1)
    q=a[None,:,:]+u[:,:,None]*v[None,:,:];r=np.linalg.norm(q-points[:,None,:],axis=2);k=r.argmin(axis=1)
    return r[np.arange(len(points)),k],q[np.arange(len(points)),k]

def trace(sol):
    theta=sol.theta;L=P['length_m'];D=P['initial_clear_gap_m'];te=P['electrode_thickness_m'];rot=np.deg2rad(theta)
    # Stable seed identities across the whole rotation. Flux lines are not particles.
    initial=np.array([[L*f,D-.000008] for f in [.018,.075,.16,.28,.43,.59,.74,.87,.97]]+[[L*.008,D+te+.000008],[L*.992,D+te+.000008]])
    pts=upper(initial,theta);paths=[[p.copy()]for p in pts];active=np.ones(len(pts),bool);ends=['max_steps']*len(pts)
    lower,up=polygons(theta)[:2];objects=polygons(theta,dielectric=sol.er!=1)
    for k in range(1500):
        ids=np.where(active)[0]
        if len(ids)==0:break
        a=pts[ids];E=sol.field(a);norm=np.linalg.norm(E,axis=1);direction=E/np.maximum(norm[:,None],1e-12)
        distances=[closest(a,x)[0]for x in objects];near=np.min(distances,axis=0)
        steps=np.clip(near*.18,.000003,.00032)
        # Enough substeps through the finite dielectric boundary.
        mid=a+direction*(steps*.5)[:,None];em=sol.field(mid);d=em/np.maximum(np.linalg.norm(em,axis=1)[:,None],1e-12);new=a+d*steps[:,None]
        dist,nearest=closest(new,lower)
        for j,i in enumerate(ids):
            paths[i].append(new[j].copy());pts[i]=new[j]
            if dist[j]<.000006 or (0<new[j,0]<L and -te<new[j,1]<0):paths[i].append(nearest[j]);active[i]=False;ends[i]='fixed_electrode'
            elif np.linalg.norm(new[j]-np.array([0,.002]))>.11:active[i]=False;ends[i]='outside_display_extent'
            elif norm[j]<1e-8:active[i]=False;ends[i]='small_field'
    output=[]
    for p in paths:
        arr=np.asarray(p);arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(arr,axis=0),axis=1))];u=np.linspace(0,max(arc[-1],1e-14),88)
        output.append(np.stack([np.interp(u,arc,arr[:,0]),np.interp(u,arc,arr[:,1])],axis=1).round(8).tolist())
    return output,ends

def fieldmap(sol):
    xs=np.linspace(BOX[0],BOX[1],NX);ys=np.linspace(BOX[2],BOX[3],NY);X,Y=np.meshgrid(xs,ys);points=np.stack([X.ravel(),Y.ravel()],axis=1)
    V=sol.potential(points);E=np.linalg.norm(sol.field(points),axis=1);inside=np.zeros(len(points),bool)
    for poly in sol.polys[:2]:
        # Convex CCW polygon point inclusion.
        a=poly*sol.scale;b=np.roll(a,-1,axis=0);v=b-a;d=points[:,None,:]-a;cross=v[None,:,0]*d[:,:,1]-v[None,:,1]*d[:,:,0];inside|=np.all(cross>=-1e-14,axis=1)
    Vq=np.round(np.clip((V+sol.voltage/2)/sol.voltage,0,1)*65534).astype('<u2');Vq[inside]=65535
    # Quantization range 0.01...100000 V/m, 7 decades, 16-bit logarithmic storage.
    Eq=np.round(np.clip((np.log10(np.maximum(E,.01))+2)/7,0,1)*65534).astype('<u2');Eq[inside]=65535
    return {'potential_u16':base64.b64encode(Vq.tobytes()).decode(),'field_log_u16':base64.b64encode(Eq.tobytes()).decode(),'fieldMaxSample_V_per_m':float(E[~inside].max())}

def validation():
    rows=[]
    for a in [0,30,90,180]:
        for er in [1,4]:
            for n in [32,64,128,192]:rows.append({'n':n,**Solution(a,er,n=n).summary()})
    checks=[]
    def add(name,ok,detail):checks.append({'name':name,'passed':bool(ok),'detail':detail})
    poses=[polygons(a)for a in np.linspace(0,180,721)]
    add('Rigid rotation is collision-free for conductors and dielectric',all(not Polygon(p[0]).intersects(Polygon(p[1])) and not Polygon(p[2]).intersects(Polygon(p[1]))for p in poses),'721 angles, exact rectangular outlines, no hand-tuned translation')
    end=polygons(180);add('Final gap is exactly 2 delta; the two finite-thickness plates are coplanar',np.allclose(sorted(end[0][:,1]),sorted(end[1][:,1]),atol=1e-14) and abs(end[0][:,0].min()-end[1][:,0].max()-2*P['hinge_offset_m'])<1e-14,{'gap_m':2*P['hinge_offset_m']})
    maxdiff=0
    for a in [0,30,90,180]:
        for er in [1,4]:
            vals=[r['C_F']for r in rows if r['theta_deg']==a and r['er']==er];maxdiff=max(maxdiff,abs(vals[-1]/vals[-2]-1))
    add('128 to 192 long-face panels changes C less than 0.02%',maxdiff<.0002,{'max_relative':maxdiff})
    a=Solution(35,1,n=N);one=Solution(35,1,n=N,thickness_factor=1);zero=Solution(35,4,n=N,thickness_factor=0)
    add('epsilon_r=1 and dielectric thickness=0 return the exact air model',a.C==one.C and a.C==zero.C,{'air_F':a.C,'er1_F':one.C,'t0_F':zero.C})
    tiny=[Solution(0,4,n=N,thickness_factor=t).C for t in [1,.5,.1,.02,.002,0]]
    add('Dielectric size shrinking continuously approaches air',all(x>y for x,y in zip(tiny,tiny[1:])),{'thickness_factors':[1,.5,.1,.02,.002,0],'C_F':tiny})
    v=deepcopy(P);v['width_m']*=2;c=Solution(20,4,n=N,params=v)
    add('2-D Cprime is multiplied by physical width exactly once',abs(c.C/(2*Solution(20,4,n=N).C)-1)<1e-12 and abs(c.Cprime/Solution(20,4,n=N).Cprime-1)<1e-12,'Doubling b doubles F, not F/m')
    v=deepcopy(P);v['voltage_difference_V']=3;c=Solution(20,4,n=N,params=v);old=Solution(20,4,n=N)
    add('Linear dielectric C is invariant to voltage, charge scales with V',abs(c.C/old.C-1)<1e-10 and abs(c.Qpositive_per_m/(3*old.Qpositive_per_m)-1)<1e-10,'1 V vs 3 V')
    c=Solution(55,1,n=N,log_reference=20);d=Solution(55,1,n=N,log_reference=.05)
    add('Unbounded neutral solution does not depend on logarithmic reference length',abs(c.C/d.C-1)<1e-10,{'relative':abs(c.C/d.C-1)})
    # Finite thickness -> the zero-thickness conformal coplanar result.
    k=2*P['hinge_offset_m']/(2*P['length_m']+2*P['hinge_offset_m']);exact=P['epsilon0_F_per_m']*P['width_m']*ellipk(1-k*k)/ellipk(k*k)
    thin=[]
    for t in [.0001,.00002,.000002]:
        pp=deepcopy(P);pp['electrode_thickness_m']=t;s=Solution(180,1,n=160,params=pp);thin.append({'thickness_m':t,'C_F':s.C,'relativeToThinFormula':s.C/exact-1})
    add('Coplanar thin limit agrees with elliptic-integral solution within 0.2%',abs(thin[-1]['relativeToThinFormula'])<.002,{'exact_C_F':exact,'finiteThicknessSequence':thin})
    add('Geometric strip formula has correct parallel-plate limit',abs(analytic(1e-7)['strip_F']/(P['epsilon0_F_per_m']*P['width_m']*P['length_m']/P['initial_clear_gap_m'])-1)<1e-6,analytic(1e-7))
    result={'parameterSha256':parameter_hash(ROOT),'convergence':rows,'checks':checks,'selected_parameters':P,'cps_thin_F':exact,'cps_thickness_sequence':thin,'note':'Discretization consistency is not experimental validation. Dielectric bound-net-charge residual is reported, not silently set to zero.'}
    (ROOT/'qa').mkdir(exist_ok=True)
    (ROOT/'qa/numerical-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('VALIDATION',[(c['name'],c['passed']) for c in checks],flush=True)
    return result

def main():
    start=time.time();valid=validation();require_validation(valid);curves={};fields={}
    for er in [1,4]:
        series=[];fl=[]
        for angle in ANGLES:
            sol=Solution(angle,er,n=N);row=sol.summary();row['analytic']=analytic(angle,er=er);series.append(row)
            paths,ends=trace(sol);field={'theta_deg':angle,'paths_m':paths,'path_ends':ends,**fieldmap(sol)};fl.append(field)
            print('DATA',er,angle,round(sol.C*1e12,5),'pF',ends,'elapsed',round(time.time()-start,1),flush=True)
        curves[str(er)]=series;fields[str(er)]=fl
    er_scan=[]
    for er in [1,1.5,2,3,4,6,8]:
        sol=Solution(0,er,n=N);er_scan.append({**sol.summary(),'analytic':analytic(0,er=er)})
    data={'parameters':P,'parameterSha256':valid['parameterSha256'],'meshLongPanels':N,'angles':ANGLES,'curves':curves,'fields':fields,'fieldGrid':{'box_m':BOX,'nx':NX,'ny':NY,'potential_min_V':-P['voltage_difference_V']/2,'potential_max_V':P['voltage_difference_V']/2,'E_log10_min':-2,'E_log10_max':5,'missing_u16':65535},'er_scan':er_scan,'validation':{'convergenceMaxRelative':max(c['detail'].get('max_relative',0) if isinstance(c['detail'],dict)else 0 for c in valid['checks']),'cps_thin_F':valid['cps_thin_F']},'provenance':{'solver':'2D unbounded constant-panel BEM; analytic panel kernels; dielectric interface jumps','C_units':'F','Cprime_units':'F/m','coordinates':'m','fields':'V and V/m','displayInterpolation':'Linear interpolation between computed angular nodes; never described as a newly solved PDE','isMeasured':False,'finiteWidth3DValidated':False}}
    (ROOT/'data/results.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
    (ROOT/'source/src/physics/data.ts').write_text('/* Generated from parameters.json by physics/generate.py. Do not edit. */\nexport const DATA:any = '+json.dumps(data,separators=(',',':'))+';\n',encoding='utf-8')
    (ROOT/'qa/compute-summary.json').write_text(json.dumps({'elapsed_s':time.time()-start,'angularSolutions':len(ANGLES)*2,'curveNodes':len(ANGLES),'erScan':len(er_scan),'parametersSha256':valid['parameterSha256'],'dataBytes':(ROOT/'data/results.json').stat().st_size},indent=2),encoding='utf-8')
    print('COMPLETE',time.time()-start,flush=True)
if __name__=='__main__':main()
