"""Representative 2-D Laplace sections. Not full device FEM or measured data.
Finite-volume five-point operator, insulating domain boundary. The approaching
object is equipotential with a finite reference capacitance, not ideal grounding.
A fixed spine pivot turns the upper electrode assembly monotonically by pi.
"""
from pathlib import Path
import numpy as np,json,math,time
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import splu
ROOT=Path(__file__).resolve().parents[2]
NX,NY=145,111
xs=np.linspace(-5.5,5.5,NX);ys=np.linspace(-.30,7.6,NY)
dx=xs[1]-xs[0];dy=ys[1]-ys[0];X,Y=np.meshgrid(xs,ys)
def plate(cx,cy,ang,half=1.7,th=.10):
 c,s=np.cos(ang),np.sin(ang);a=(X-cx)*c+(Y-cy)*s;b=-(X-cx)*s+(Y-cy)*c
 return (abs(a)<=half)&(abs(b)<=th)
def solve(kind,q=1,d=None):
 angle=-np.pi*q
 rx=(math.cos(angle)*-1.85-math.sin(angle)*.85,1+math.sin(angle)*-1.85+math.cos(angle)*.85,angle)
 if kind=='book':
  tx=(-1.85,.15,0);mt=plate(*tx);mr=plate(*rx);seeds=np.linspace(-1.2,1.4,12);radius=.63;height=3.;offset=.25
 else:
  tx=(3.15,1.204,0);mt=plate(3.15,1.204,0,.22,.055)|plate(-3.15,1.204,0,.22,.055);mr=plate(0,1.204,0,1.93,.04);seeds=np.linspace(-.15,.15,4);radius=1.35;height=1.95;offset=0
 mo=np.zeros_like(mt)
 if d is not None:
  bottom=d+offset
  # Elliptical cap approximation for the equivalent body section.
  center=bottom+height/2
  mo=(X/radius)**2+((Y-center)/(height/2))**2<=1
 fixed=mt|mr|mo;unknown=~fixed;index=np.full(X.shape,-1,dtype=int);index[unknown]=np.arange(unknown.sum())
 A=lil_matrix((unknown.sum(),unknown.sum()));rhs=np.zeros((unknown.sum(),2));v0=mt.astype(float);v1=mo.astype(float)
 for j,i in zip(*np.nonzero(unknown)):
  row=index[j,i];diag=0
  for dj,di,w in [(0,1,1/dx**2),(0,-1,1/dx**2),(1,0,1/dy**2),(-1,0,1/dy**2)]:
   y,x=j+dj,i+di
   if x<0 or x>=NX or y<0 or y>=NY:continue
   diag+=w
   if fixed[y,x]:rhs[row,0]+=w*v0[y,x];rhs[row,1]+=w*v1[y,x]
   else:A[row,index[y,x]]=-w
  A[row,row]=diag
 A=A.tocsc();lu=splu(A);solutions=lu.solve(rhs);V0=v0.copy();V1=v1.copy();V0[unknown]=solutions[:,0];V1[unknown]=solutions[:,1]
 def charge(V,mask):
  total=0.
  for j,i in zip(*np.nonzero(mask)):
   for dj,di,w in [(0,1,dy/dx),(0,-1,dy/dx),(1,0,dx/dy),(-1,0,dx/dy)]:
    y,x=j+dj,i+di
    if 0<=x<NX and 0<=y<NY and not mask[y,x]:total+=(V[j,i]-V[y,x])*w
  return total
 vt=0.;cref=0.
 if mo.any():
  q0=charge(V0,mo);q1=charge(V1,mo);cref=.35*q1;vt=-q0/(q1+cref)
 V=V0+vt*V1;EY,EX=np.gradient(-V,dy,dx)
 def field(px,py):
  fx=np.clip((px-xs[0])/dx,0,NX-1.00001);fy=np.clip((py-ys[0])/dy,0,NY-1.00001);i=int(fx);j=int(fy);a=fx-i;b=fy-j
  def lerp(F):return (1-b)*((1-a)*F[j,i]+a*F[j,i+1])+b*((1-a)*F[j+1,i]+a*F[j+1,i+1])
  return np.array([lerp(EX),lerp(EY)])
 paths=[];ends=[]
 for local in seeds:
  p=np.array([tx[0]+local,tx[1]+(.135 if kind=='book' else .10)]);path=[p.copy()];end='boundary'
  for k in range(1600):
   e=field(*p);mag=np.linalg.norm(e)
   if mag<1e-9:break
   step=.038;mid=p+e/mag*step*.5;e2=field(*mid);mag=np.linalg.norm(e2)
   if mag<1e-9:break
   p=p+e2/mag*step;path.append(p.copy());ii=int(round((p[0]-xs[0])/dx));jj=int(round((p[1]-ys[0])/dy))
   if not(0<=ii<NX and 0<=jj<NY):break
   if mr[jj,ii]:end='receiver';break
   if mo[jj,ii]:end='target';break
   if p[1]>ys[-1]-.04 or p[1]<ys[0]+.04 or abs(p[0])>5.46:break
  path=np.asarray(path);arcs=np.r_[0,np.cumsum(np.linalg.norm(np.diff(path,axis=0),axis=1))];samples=np.linspace(0,arcs[-1],56)
  paths.append(np.stack([np.interp(samples,arcs,path[:,0]),np.interp(samples,arcs,path[:,1])],axis=1).round(5).tolist());ends.append(end)
 residual=float(np.max(np.abs(A@(solutions[:,0]+vt*solutions[:,1])-(rhs[:,0]+vt*rhs[:,1]))))
 return {'u':round(q,5),'distance':d,'coupling':abs(charge(V,mr)),'targetPotential':vt,'referenceCapacitance':cref,'residual':residual,'paths':paths,'ends':ends}
start=time.time();morph=[];approach=[];square=[]
for q in np.linspace(0,1,13):
 r=solve('book',float(q));morph.append(r);print('book',round(q,2),r['ends'],flush=True)
for d in np.linspace(4.8,.28,12):
 r=solve('book',1,float(d));approach.append(r);print('target',round(d,2),round(r['targetPotential'],3),flush=True)
square.append(solve('square'))
for d in np.linspace(4.7,1.29,9):
 r=solve('square',1,float(d));square.append(r);print('square',round(d,2),r['ends'],flush=True)
meta={'model':'representative 2-D finite-volume Laplace with finite-reference-coupled floating target','grid':[NX,NY],'maxResidual':max(s['residual'] for s in morph+approach+square),'baselineCouplingArbitrary':morph[-1]['coupling'],'slices':'3-D visual depth slices, not a full 3-D solution','directCouplingPolicy':'Only a central subset uses target-terminating states; outer depth slices retain electrode-to-electrode paths.','bookPivot':[0,1,0],'bookAngleRange':[0,-math.pi],'finiteGapSpine':'Offset upper electrode carried by a rigid dielectric spine around a fixed edge axis; no independent sliding.'}
data={'metadata':meta,'morph':morph,'approach':approach,'square':square}
(ROOT/'src/physics/revisionFieldData.ts').write_text('/* Generated by scripts/physics/solve_revision_fields.py. */\nexport const revisionFieldData='+json.dumps(data,separators=(',',':'))+';\n')
qa={**meta,'runtimeSeconds':time.time()-start}
(ROOT.parent/'qa').mkdir(parents=True,exist_ok=True)
(ROOT.parent/'qa/field-solver.json').write_text(json.dumps(qa,indent=2));print('DONE',qa,flush=True)
