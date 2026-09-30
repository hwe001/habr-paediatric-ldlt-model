import numpy as np
from scipy.optimize import brentq, minimize
from model import *
A_COEF, B_COEF = 0.0007102, 0.5492

def fit_pod1(p=None, PHA_amp=27.43, x0=(127.92, 5.80), psv=53.10, ri=0.610):
    p = P0 if p is None else p
    q1 = qpv(1)
    def obj(z):
        Rs, L = np.exp(z)
        r = simulate_fast(Rs, L, PHA_amp, q1, p)
        return ((r['PSV'] - psv) / psv) ** 2 + ((r['RI'] - ri) / ri) ** 2
    res = minimize(obj, np.log(x0), method='Nelder-Mead', options=dict(xatol=1e-9, fatol=1e-16, maxiter=2000))
    return np.exp(res.x), res.fun

def solve_Rs(target_meanQ, Rs0, L, PHA_amp, Qpv, p=None):
    f = lambda Rs: simulate_fast(Rs, L, PHA_amp, Qpv, p)['meanQ'] - target_meanQ
    lo, hi = 0.3 * Rs0, 3.0 * Rs0
    k = 0
    while f(lo) * f(hi) > 0 and k < 40:
        lo *= 0.7; hi *= 1.4; k += 1
    return brentq(f, lo, hi, xtol=1e-8)

def scenarios(Rs1, L1, PHA_amp, p=None, coef_scale=1.0, AHA_growth=None, qscale=1.0):
    """continuous, acute-then-frozen, null. returns dict scen -> {day: (PSV, RI)}"""
    p = dict(P0 if p is None else p)
    ref = simulate_fast(Rs1, L1, PHA_amp, qpv(1) * qscale, p)['meanQ']
    out = {'cont': {}, 'frozen': {}, 'null': {}}
    Rs_by_day = {}
    for d in (1, 7, 14, 30):
        Qd = qpv(d) * qscale
        x = 100 * (qpv(1) - qpv(d)) / qpv(1)
        ch = coef_scale * (A_COEF * x * x + B_COEF * x)
        target = ref * (1 - ch / 100)
        Rs_by_day[d] = Rs1 if d == 1 else solve_Rs(target, Rs1, L1, PHA_amp, Qd, p)
    Rs7 = Rs_by_day[7]
    for d in (1, 7, 14, 30):
        Qd = qpv(d) * qscale
        pd = dict(p)
        if AHA_growth is not None: pd['AHA'] = p['AHA'] * (1 + AHA_growth[d]) ** 2
        for scen, Rs in (('cont', Rs_by_day[d]), ('frozen', Rs1 if d == 1 else Rs7), ('null', Rs1)):
            r = simulate_fast(Rs, L1, PHA_amp, Qd, pd)
            out[scen][d] = (r['PSV'], r['RI'], r['meanQ'])
    return out

def F_of(sc):
    return 100 * (sc['cont'][1][0] - sc['cont'][30][0]) / (PSV_meas[1] - PSV_meas[30])

if __name__ == '__main__':
    z, f = fit_pod1(); print('POD1 fit', z, f)
    sc = scenarios(z[0], z[1], 27.43)
    for s in sc:
        print(s, {d: tuple(round(v, 3) for v in sc[s][d][:2]) for d in sc[s]})
    print('F', F_of(sc))
