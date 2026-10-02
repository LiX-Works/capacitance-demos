"""2-D unbounded electrostatic constant-panel collocation BEM.

The finite rectangular electrodes (including thickness) have specified potential
DIFFERENCE and zero net free charge. A constant far-reference potential is an
unknown; no artificial outer boundary is used. Piecewise-constant dielectric
permittivity is solved via induced interface charge and normal-D continuity.

Unknown q_j = integrated effective surface density / epsilon_air, units V.
The normalized 2-D fundamental solution is -log(r/L)/(2*pi). Analytic panel
integrals are used for both potential and E, including the logarithmic self
term. The interface jump is q_i/l_i = 2*alpha*E_average.n, alpha=(er-1)/(er+1).
Free electrode charge per width Q' = epsilon_air*sum(q_electrode).
This code returns F/m and multiplies by b exactly once for the displayed C.
"""
import numpy as np
from scipy.linalg import solve
from dataclasses import dataclass
from model import P,polygons

@dataclass
class Panels:
    a: np.ndarray; z:np.ndarray; c:np.ndarray; tangent:np.ndarray; normal:np.ndarray; length:np.ndarray; group:np.ndarray

def panelize(polys,n=80):
    aa=[];zz=[];gg=[]
    for group,poly in enumerate(polys):
        for a,b in zip(poly,np.roll(poly,-1,axis=0)):
            ell=np.linalg.norm(b-a)
            count=max(6,int(round(n*ell)))
            # Cosine endpoint grading resolves edge and corner singularities.
            t=(1-np.cos(np.linspace(0,np.pi,count+1)))/2
            points=a[None,:]+t[:,None]*(b-a)[None,:]
            aa.extend(points[:-1]);zz.extend(points[1:]);gg.extend([group]*count)
    a=np.array(aa);z=np.array(zz);v=z-a;l=np.linalg.norm(v,axis=1);t=v/l[:,None];norm=np.stack([t[:,1],-t[:,0]],axis=1)
    return Panels(a,z,(a+z)/2,t,norm,l,np.array(gg))

def kernels(points,p,field=False,log_reference=1.):
    d=np.asarray(points)[:,None,:]-p.a[None,:,:]
    u=np.einsum('ijk,jk->ij',d,p.tangent);v=np.einsum('ijk,jk->ij',d,p.normal)
    w=u-p.length[None,:];vv=np.abs(v);r1=np.maximum(u*u+v*v,1e-290);r2=np.maximum(w*w+v*v,1e-290)
    if field:
        et=.5*np.log(r1/r2)/p.length/(2*np.pi)
        en=np.sign(v)*(np.arctan2(u,vv)-np.arctan2(w,vv))/p.length/(2*np.pi)
        return et[...,None]*p.tangent[None,:,:]+en[...,None]*p.normal[None,:,:]
    F1=.5*u*np.log(r1)-u+vv*np.arctan2(u,vv)
    F2=.5*w*np.log(r2)-w+vv*np.arctan2(w,vv)
    return -(F1-F2-p.length*np.log(log_reference))/(2*np.pi*p.length)

class Solution:
 def __init__(self,theta_deg,er=1.,n=80,params=P,thickness_factor=1,log_reference=1.):
    self.theta=theta_deg;self.er=er;self.params=params;self.scale=params['length_m'];self.eps=params['epsilon0_F_per_m']*params['air_relative_permittivity'];self.voltage=params['voltage_difference_V']
    include=er!=1 and thickness_factor>0
    self.polys=[x/self.scale for x in polygons(theta_deg,params,include,thickness_factor)]
    self.panels=pp=panelize(self.polys,n);N=len(pp.length);K=kernels(pp.c,pp,log_reference=log_reference)
    # Centre self potential exactly, and field PV on a straight panel is zero.
    np.fill_diagonal(K,(1-np.log(pp.length/(2*log_reference)))/(2*np.pi))
    A=np.zeros((N+1,N+1));rhs=np.zeros(N+1);c=pp.group<2;A[:N,:N][c]=K[c];A[:N,N][c]=1;rhs[:N][pp.group==0]=-.5*self.voltage;rhs[:N][pp.group==1]=.5*self.voltage
    if include:
        idx=np.where(pp.group==2)[0];E=kernels(pp.c[idx],pp,field=True);normal=np.einsum('ijk,ik->ij',E,pp.normal[idx]);normal[np.arange(len(idx)),idx]=0
        alpha=(er-1)/(er+1);A[idx,:N]=-2*alpha*normal
        A[idx,idx]+=1/pp.length[idx]
    # Free electrode charge conservation. Bound dielectric net charge is an
    # independently evaluated discretization diagnostic, not silently forced.
    A[N,:N]=(pp.group<2).astype(float)
    x=solve(A,rhs,assume_a='gen');self.q=x[:N];self.reference=x[N];self.log_reference=log_reference
    self.residual=float(np.max(np.abs(A@x-rhs)))
    self.Qpositive_per_m=self.eps*self.q[pp.group==1].sum();self.Qnegative_per_m=self.eps*self.q[pp.group==0].sum()
    self.Cprime=self.Qpositive_per_m/self.voltage;self.C=self.Cprime*params['width_m']
    self.boundNet=self.eps*self.q[pp.group==2].sum() if include else 0.
    self.N=N;self.eq=A;self.rhs=rhs
 def potential(self,pts_m,chunk=1600):
    pts=np.asarray(pts_m)/self.scale;ans=[]
    for i in range(0,len(pts),chunk):ans.append(kernels(pts[i:i+chunk],self.panels,log_reference=self.log_reference)@self.q+self.reference)
    return np.concatenate(ans)
 def field(self,pts_m,chunk=1600):
    pts=np.asarray(pts_m)/self.scale;ans=[]
    for i in range(0,len(pts),chunk):ans.append(np.einsum('ijk,j->ik',kernels(pts[i:i+chunk],self.panels,field=True),self.q)/self.scale)
    return np.concatenate(ans)
 def summary(self):
    return {'theta_deg':self.theta,'er':self.er,'panels':self.N,'Cprime_F_per_m':self.Cprime,'C_F':self.C,'Qpositive_C_per_m':self.Qpositive_per_m,'Qnegative_C_per_m':self.Qnegative_per_m,'boundNet_C_per_m':self.boundNet,'residual':self.residual,'farPotential_V':self.reference}

if __name__=='__main__':
 import time,json
 from model import analytic
 t=time.time()
 for a in [0,10,30,60,90,180]:
  for er in [1,4]:
   s=Solution(a,er,n=64);print(json.dumps({**s.summary(),'strip_pF':None if analytic(a,er=er)['strip_F'] is None else analytic(a,er=er)['strip_F']*1e12}),flush=True)
 print('elapsed',time.time()-t)
