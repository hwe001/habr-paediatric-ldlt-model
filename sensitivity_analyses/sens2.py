import numpy as np, json
from pipeline import *
z,_=fit_pod1(); Rs1,L1=z
base=scenarios(Rs1,L1,27.43)
# RI values table
tab={s:{d:(round(base[s][d][0],2),round(base[s][d][1],3)) for d in (1,7,14,30)} for s in base}
print(tab)
# P_HA_mean extra
def pert(p):
    zz,fv=fit_pod1(p=p)
    if fv>1e-8: return None
    sc=scenarios(zz[0],zz[1],27.43,p=p); return (round(F_of(sc),1),round(sc['cont'][30][1]-sc['cont'][1][1],4))
for m in (45,50,55,60,65,68):
    p=dict(P0); p['PHA_mean']=float(m); print('PHA_mean',m,pert(p))
# structural remodelling: L scaled with HA growth g at POD30 -> RI, PSV
def struct(g):
    ref=simulate_fast(Rs1,L1,27.43,qpv(1))['meanQ']
    Qd=qpv(30); x=100*(qpv(1)-Qd)/qpv(1); ch=A_COEF*x*x+B_COEF*x
    L30=L1/(1+g)**2
    Rs=solve_Rs(ref*(1-ch/100),Rs1,L30,27.43,Qd)
    pd=dict(P0); pd['AHA']=P0['AHA']*(1+g)**2
    r=simulate_fast(Rs,L30,27.43,Qd,pd); return r['PSV'],r['RI']
for g in (0.0,0.1,0.2,0.3,0.4): print('struct g',g,[round(v,3) for v in struct(g)])
# P_IVC, HR effect on absolute RI etc skipped
