"""Independent finite-width air-only 3-D constant rectangular-panel BEM.
All six faces of each finite-thickness rectangular electrode are represented.
Analytic rectangular 1/r panel integrals; a neutral two-terminal excitation with
unknown common potential. This is a checkpoint/convergence calculation, not an
experimental validation or a dielectric 3-D solution.
"""
from pathlib import Path
import numpy as np,json,time
from scipy.linalg import solve
from model import P,rotation,hinge
from bem import Solution
from provenance import parameter_hash
ROOT=Path(__file__).resolve().parents[1]

def subdiv(lo,hi,n):return lo+(hi-lo)*(1-np.cos(np.linspace(0,np.pi,n+1)))/2

def panels3d(theta,nl,nw):
 L=P['length_m'];B=P['width_m'];D=P['initial_clear_gap_m'];t=P['electrode_thickness_m'];scale=L
 centres=[];uvec=[];vvec=[];half=[];groups=[]
 for group,y0 in [(0,-t),(1,D)]:
  edges=[subdiv(0,L,nl),np.array([y0,y0+t]),subdiv(-B/2,B/2,nw)]
  for fixed in range(3):
   axes=[k for k in range(3)if k!=fixed]
   for sign in [0,-1]:
    a,b=axes;ua=np.eye(3)[a];vb=np.eye(3)[b]
    for i in range(len(edges[a])-1):
     for j in range(len(edges[b])-1):
      c=np.zeros(3);c[fixed]=edges[fixed][sign];c[a]=(edges[a][i]+edges[a][i+1])/2;c[b]=(edges[b][j]+edges[b][j+1])/2
      u=ua.copy();v=vb.copy()
      if group:
       R=rotation(theta);h=hinge();c[:2]=(c[:2]-h)@R.T+h;u[:2]=u[:2]@R.T;v[:2]=v[:2]@R.T
      centres.append(c/scale);uvec.append(u);vvec.append(v);half.append([(edges[a][i+1]-edges[a][i])/2/scale,(edges[b][j+1]-edges[b][j])/2/scale]);groups.append(group)
 return np.array(centres),np.array(uvec),np.array(vvec),np.array(half),np.array(groups)
def rect_integral(x,y,z):
 r=np.sqrt(x*x+y*y+z*z);term=x*np.log(np.maximum(y+r,1e-300))+y*np.log(np.maximum(x+r,1e-300))
 return term-z*np.arctan2(x*y,np.maximum(z*r,1e-300))
def compute(theta,nl,nw):
 c,u,v,h,group=panels3d(theta,nl,nw);N=len(c);A=np.empty((N+1,N+1));normal=np.cross(u,v);area=4*h[:,0]*h[:,1]
 for start in range(0,N,128):
  d=c[start:start+128,None,:]-c[None,:,:];x=np.einsum('ijk,jk->ij',d,u);y=np.einsum('ijk,jk->ij',d,v);z=np.abs(np.einsum('ijk,jk->ij',d,normal));a=h[:,0];b=h[:,1]
  integral=rect_integral(x+a,y+b,z)-rect_integral(x-a,y+b,z)-rect_integral(x+a,y-b,z)+rect_integral(x-a,y-b,z)
  A[start:min(N,start+128),:N]=integral/(4*np.pi*area)
 A[:N,N]=1;A[N,:N]=1;A[N,N]=0;rhs=np.r_[np.where(group==0,-.5,.5)*P['voltage_difference_V'],0]
 q=solve(A,rhs);C=P['epsilon0_F_per_m']*P['length_m']*q[:N][group==1].sum()/P['voltage_difference_V'];res=np.max(np.abs(A@q-rhs))
 base=Solution(theta,1,n=160).C
 return {'theta_deg':theta,'nl':nl,'nw':nw,'panels':N,'C3D_F':float(C),'C2D_extruded_F':float(base),'relativeDifference':float(C/base-1),'residual':float(res),'netChargeRelative':float(abs(q[:N].sum())/abs(q[:N][group==1].sum()))}
if __name__=='__main__':
 rows=[];start=time.time();(ROOT/'qa').mkdir(exist_ok=True)
 for a in [0,90,180]:
  for nl,nw in [(6,18),(10,30),(14,42)]:
   t=time.time();r=compute(a,nl,nw);rows.append(r);print(r,'s',time.time()-t,flush=True)
   (ROOT/'qa/finite-width-3d.json').write_text(json.dumps({'method':__doc__,'parameterSha256':parameter_hash(ROOT),'complete':len(rows)==9,'rows':rows,'elapsed_s':time.time()-start},indent=2),encoding='utf-8')
