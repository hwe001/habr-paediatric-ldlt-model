import numpy as np, json, time
from pipeline import *
import model
t0=time.time()
z,_=fit_pod1(); Rs1,L1=z
base=scenarios(Rs1,L1,27.43)
F0=F_of(base); dRI0=base['cont'][30][1]-base['cont'][1][1]
print('base F',F0,'dRI',dRI0, 'time',time.time()-t0)
out={'base':dict(F=F0,dRI=dRI0)}
# 1) HABR coefficient scale
hc={}
for s in (0.5,0.75,1.0,1.25,1.5,2.0,3.0,4.0):
    sc=scenarios(Rs1,L1,27.43,coef_scale=s); hc[s]=dict(F=F_of(sc),PSV30=sc['cont'][30][0],RI30=sc['cont'][30][1])
    print('coef x',s,hc[s])
# coefficient scale needed for F=100
from scipy.optimize import brentq as bq
sstar=bq(lambda s:F_of(scenarios(Rs1,L1,27.43,coef_scale=s))-100,1.0,10.0,xtol=1e-3)
hc['s_for_F100']=sstar; print('scale for F=100%',sstar)
out['habr_coef']=hc
# 2) tornado on assumed parameters (refit POD1 for each)
def run_pert(name,mods,lo_hi):
    res={}
    for tag,val in lo_hi:
        p=dict(P0); 
        for k,f in mods.items(): p[k]=f(val)
        try:
            zz,fv=fit_pod1(p=p)
            if fv>1e-8: res[tag]=None; continue
            sc=scenarios(zz[0],zz[1],27.43,p=p)
            res[tag]=dict(F=F_of(sc),dRI=sc['cont'][30][1]-sc['cont'][1][1],Rs1=zz[0],L1=zz[1])
        except Exception as e:
            res[tag]=None
    return res
tor={}
tor['HR (110, 150 bpm)']=run_pert('HR',{'HR':lambda v:v},[('lo',110.0),('hi',150.0)])
tor['P_HA_mean (43, 72 mmHg)']=run_pert('PHA',{'PHA_mean':lambda v:v},[('lo',43.0),('hi',72.0)])
tor['P_IVC (0, 5 mmHg)']=run_pert('IVC',{'PIVC':lambda v:v},[('lo',0.0),('hi',5.0)])
tor['C_sinus (x0.5, x2)']=run_pert('Cs',{'Csin':lambda v:2.0*v},[('lo',0.5),('hi',2.0)])
tor['C_hv (x0.5, x2)']=run_pert('Ch',{'Chv':lambda v:2.0*v},[('lo',0.5),('hi',2.0)])
tor['R_p,sinus (x0.5, x2)']=run_pert('Rp',{'Rpsin':lambda v:500.0*v},[('lo',0.5),('hi',2.0)])
tor['L_HV (x0.5, x2)']=run_pert('Lh',{'LHV':lambda v:0.02*v},[('lo',0.5),('hi',2.0)])
tor['R_s,HV (x0.75, x1.25)']=run_pert('RsHV',{'RsHV':lambda v:0.242*v},[('lo',0.75),('hi',1.25)])
tor['R_p,hv,out (x0.75, x1.25)']=run_pert('RpHV',{'RpHVout':lambda v:0.385*v},[('lo',0.75),('hi',1.25)])
for k,v in tor.items(): print(k,{a:(None if b is None else (round(b['F'],1),round(b['dRI'],4))) for a,b in v.items()})
out['tornado']=tor
# P_HA_amp family + graft mass scaling
fam={}
for amp in (24,30,40,50,60):
    zz,fv=fit_pod1(PHA_amp=float(amp),x0=(128,5.8))
    sc=scenarios(zz[0],zz[1],float(amp))
    fam[amp]=dict(F=F_of(sc),dRI=sc['cont'][30][1]-sc['cont'][1][1],fit=fv)
print('amp family',fam); out['amp_family']=fam
# calibre growth (kinematic) for reference: growth applied to AHA at POD30 in continuous scenario
def growth_F(gha,gpv):
    # replicate: HA area growth (diameter growth) scales AHA; portal diameter growth scales Qpv
    import pipeline as pl
    sc_days={}
    ref=simulate_fast(Rs1,L1,27.43,qpv(1))['meanQ']
    res={}
    for d in (1,30):
        frac=(d-1)/29.0
        Qd=qpv(d)*(1+gpv*frac)**2
        x=100*(qpv(1)-Qd)/qpv(1); ch=A_COEF*x*x+B_COEF*x
        tgt=ref*(1-ch/100)
        Rs=Rs1 if d==1 else solve_Rs(tgt,Rs1,L1,27.43,Qd)
        pd=dict(P0); pd['AHA']=P0['AHA']*(1+gha*frac)**2
        res[d]=simulate_fast(Rs,L1,27.43,Qd,pd)['PSV']
    return 100*(res[1]-res[30])/(PSV_meas[1]-PSV_meas[30])
gr={}
for g in (0.0,0.1,0.2): 
    gr[('HA',g)]=growth_F(g,0.0); gr[('PV',g)]=growth_F(0.0,g)
print('growth check',gr)
out['growth_check']={f'{a}_{b}':v for (a,b),v in gr.items()}
json.dump(out,open('sens.json','w'),indent=1,default=float)
print('done',time.time()-t0)
