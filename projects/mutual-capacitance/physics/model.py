"""Shared real-parameter geometry and closed-form approximations.
All public coordinates are metres. The numerical solver normalizes by L only
internally. D is the clear face-to-face gap, not the centre-plane distance.
"""
from pathlib import Path
import json, numpy as np
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'parameters.json').read_text(encoding='utf-8'))

def rotation(theta_deg):
    q=np.deg2rad(theta_deg);return np.array([[np.cos(q),-np.sin(q)],[np.sin(q),np.cos(q)]])
def hinge(p=P):return np.array([-p['hinge_offset_m'],p['initial_clear_gap_m']/2])
def upper(points,theta_deg,p=P):return (np.asarray(points)-hinge(p))@rotation(theta_deg).T+hinge(p)
def polygons(theta_deg,p=P,dielectric=True,thickness_factor=1):
    L=p['length_m'];D=p['initial_clear_gap_m'];t=p['electrode_thickness_m']
    lower=np.array([[0,-t],[L,-t],[L,0],[0,0]])
    top=upper([[0,D],[L,D],[L,D+t],[0,D+t]],theta_deg,p)
    if not dielectric or thickness_factor<=0:return [lower,top]
    d=p['dielectric'];a=d['x_start_m'];b=d['x_end_m'];y=d['y_bottom_m'];h=d['thickness_m']*thickness_factor
    return [lower,top,np.array([[a,y],[b,y],[b,y+h],[a,y+h]])]

def analytic(theta_deg,p=P,er=None,thickness_factor=1):
    """Local vertical-flux approximation on the ACTUAL projected overlap.
    Strip and mapped annular-sector candidates are undefined beyond overlap.
    No claim of uniformly valid electrostatics is made.
    """
    q=np.deg2rad(theta_deg);L=p['length_m'];D=p['initial_clear_gap_m'];d=p['hinge_offset_m'];eps=p['epsilon0_F_per_m']*p['air_relative_permittivity'];b=p['width_m']
    if theta_deg>=89.999:return {'strip_F':None,'wedge_F':None,'dual_wedge_F':None,'overlap_m':0,'h0_m':None,'h1_m':None,'log_gap_m':None}
    tan=np.tan(q);W=max(0,min(L,-d+(L+d)*np.cos(q)-D/2*np.sin(q)))
    h0=D/2*(1+1/np.cos(q))+d*tan;h1=h0+W*tan
    if W<=0:return {'strip_F':None,'wedge_F':None,'dual_wedge_F':None,'overlap_m':0,'h0_m':h0,'h1_m':h0,'log_gap_m':None}
    def integral(a,z,offset=0):
        return (z-a)/(h0-offset) if abs(tan)<1e-9 else np.log1p((z-a)*tan/(h0+a*tan-offset))/tan
    air=integral(0,W);area=air
    if er is not None and er!=1 and thickness_factor>0:
        mat=p['dielectric'];a=max(0,mat['x_start_m']);z=min(W,mat['x_end_m']);t=mat['thickness_m']*thickness_factor
        if z>a:area+=integral(a,z,t*(1-1/er))-integral(a,z)
    wedge=air if theta_deg<1e-7 else air*tan/q
    dual=wedge if theta_deg<1e-7 else wedge*(1+q/(2*np.pi-q))
    return {'strip_F':eps*b*area,'air_strip_F':eps*b*air,'wedge_F':eps*b*wedge,'dual_wedge_F':eps*b*dual,'overlap_m':W,'h0_m':h0,'h1_m':h1,'log_gap_m':W/air}
