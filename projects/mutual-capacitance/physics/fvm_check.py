"""Independent non-uniform Cartesian finite-volume check at aligned 0/180 deg.
All lengths in metres. Face permittivity uses a distance-weighted harmonic mean.
The artificial finite-box outer Dirichlet value is zero in air; for asymmetric
dielectric it uses the 2-D BEM n=96 neutral reference, so that checkpoint is not
fully independent of BEM. Cell-wise conductors match face bounds.
"""
from pathlib import Path
import numpy as np,json,time
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from model import P
from bem import Solution
from provenance import parameter_hash
ROOT=Path(__file__).resolve().parents[1]
def axis(a,b,h,R,breaks=()):
    # Preserve all exact material/electrode faces; fill each piece at <=h.
    anchors=sorted(set([a,b,*[v for v in breaks if a<v<b]]));out=[]
    for x,y in zip(anchors,anchors[1:]):out.extend(np.linspace(x,y,max(1,int(np.ceil((y-x)/h)))+1)[:-1])
    out.append(b)
    step=h;x=b
    while x<R:step*=1.16;x=min(R,x+step);out.append(x)
    left=[];x=a;step=h
    while x>-R:step*=1.16;x=max(-R,x-step);left.append(x)
    return np.array(list(reversed(left))+out)
def fvm(theta=0,er=1,h=.0001,R=.12):
    L=P['length_m'];D=P['initial_clear_gap_m'];t=P['electrode_thickness_m'];delta=P['hinge_offset_m'];m=P['dielectric'];xlo=-L-2*delta if theta==180 else 0
    xf=axis(xlo-.002,L+.002,h,R,[xlo,-2*delta,0,L,m['x_start_m'],m['x_end_m']]);yf=axis(-.002,D+.003,h,R,[-t,0,D,D+t,m['y_bottom_m'],m['y_bottom_m']+m['thickness_m']]);x=(xf[:-1]+xf[1:])/2;y=(yf[:-1]+yf[1:])/2;wx=np.diff(xf);wy=np.diff(yf);X,Y=np.meshgrid(x,y);nx=len(x);ny=len(y)
    low=(X>0)&(X<L)&(Y>-t)&(Y<0)
    up=((X>0)&(X<L)&(Y>D)&(Y<D+t)) if theta==0 else ((X>xlo)&(X<-2*delta)&(Y>-t)&(Y<0))
    fixed=low|up;value=np.zeros(X.shape);value[low]=-.5*P['voltage_difference_V'];value[up]=.5*P['voltage_difference_V']
    e=np.ones(X.shape);e[(X>m['x_start_m'])&(X<m['x_end_m'])&(Y>m['y_bottom_m'])&(Y<m['y_bottom_m']+m['thickness_m'])]=er
    e[fixed]=np.inf
    n=nx*ny;idx=np.arange(n).reshape(ny,nx)
    with np.errstate(divide='ignore',invalid='ignore'):
     gh=wy[:,None]/((wx[:-1]/2)[None,:]/e[:,:-1]+(wx[1:]/2)[None,:]/e[:,1:]);gv=wx[None,:]/((wy[:-1]/2)[:,None]/e[:-1]+(wy[1:]/2)[:,None]/e[1:])
    gh[~np.isfinite(gh)]=0;gv[~np.isfinite(gv)]=0
    edge_a=np.r_[idx[:,:-1].ravel(),idx[:-1,:].ravel()];edge_b=np.r_[idx[:,1:].ravel(),idx[1:,:].ravel()];g=np.r_[gh.ravel(),gv.ravel()]
    row=np.r_[edge_a,edge_b,edge_a,edge_b];col=np.r_[edge_a,edge_b,edge_b,edge_a];data=np.r_[g,g,-g,-g]
    # Four zero-potential far faces in air; dielectric faces use BEM's neutral reference.
    ref=Solution(theta,er,n=96).reference if er!=1 else 0.
    boundary=np.r_[idx[0],idx[-1],idx[:,0],idx[:,-1]];gb=np.r_[2*wx/wy[0]*e[0],2*wx/wy[-1]*e[-1],2*wy/wx[0]*e[:,0],2*wy/wx[-1]*e[:,-1]]
    row=np.r_[row,boundary];col=np.r_[col,boundary];data=np.r_[data,gb]
    A=coo_matrix((data,(row,col)),shape=(n,n)).tocsr();f=fixed.ravel();v=value.ravel();rhs=np.zeros(n);np.add.at(rhs,boundary,gb*ref)
    free=np.where(~f)[0];rhs=rhs[free]-A[free][:,f]@v[f];v[free]=spsolve(A[free][:,free],rhs)
    flux=A@v;flux[boundary]-=gb*ref
    qp=flux[up.ravel()].sum()*P['epsilon0_F_per_m'];qm=flux[low.ravel()].sum()*P['epsilon0_F_per_m'];U=.5*P['epsilon0_F_per_m']*((g*(v[edge_a]-v[edge_b])**2).sum()+(gb*(v[boundary]-ref)**2).sum())
    return {'theta_deg':theta,'er':er,'h_m':h,'R_m':R,'cells':n,'outerPotential_V':ref,'outerPotentialSource':'BEM n=96 neutral reference' if er!=1 else 'zero (air symmetry)','Cprime_F_per_m':qp/P['voltage_difference_V'],'C_F':qp*P['width_m']/P['voltage_difference_V'],'energy_Cprime_F_per_m':2*U/P['voltage_difference_V']**2,'charge_balance_relative':abs(qp+qm)/qp}
if __name__=='__main__':
    rows=[];start=time.time();(ROOT/'qa').mkdir(exist_ok=True)
    for a,er,h,R in [(0,1,.0001,.08),(0,1,.00005,.08),(0,1,.000025,.08),(180,1,.0001,.08),(180,1,.00005,.08),(180,1,.000025,.08),(180,1,.00005,.16),(180,1,.00005,.32),(0,4,.00005,.12)]:
        r=fvm(a,er,h,R);r['bem_F']=Solution(a,er,n=160).C;r['relative_to_bem']=r['C_F']/r['bem_F']-1;rows.append(r);print(r,flush=True)
        (ROOT/'qa/independent-fvm.json').write_text(json.dumps({'method':__doc__,'parameterSha256':parameter_hash(ROOT),'complete':len(rows)==9,'rows':rows,'elapsed_s':time.time()-start},indent=2),encoding='utf-8')
