import numpy as np
from scipy.optimize import brentq, minimize

P0 = dict(HR=130.0, PHA_mean=57.5, PIVC=2.0, RsHV=0.242, RpHVout=0.385, LHV=0.02, Csin=2.0, Chv=2.0, Rpsin=500.0,
          AHA=0.0113, PHA_amp=27.43)
# measured cohort
PSV_meas = {1: 53.10, 7: 47.02, 14: 42.29, 30: 38.51}
RI_meas = {1: 0.61, 7: 0.59, 14: 0.59, 30: 0.59}
PVV = {1: 30.80, 7: 30.05, 14: 28.39, 30: 26.71}
r_pv = 0.46 / 2.0

def qpv(day, scale=1.0, growth=0.0):
    # mL/s ; Chen formula, diameter fixed at POD1 value unless growth
    r = r_pv * (1 + growth * (day - 1) / 29.0) if False else r_pv
    return np.pi * r ** 2 * 0.57 * PVV[day] * scale  # mL/s (x60 gives mL/min)

def simulate(RsHA, LHA, PHA_amp, Qpv, p=None, nsteps=400, tol=1e-6, maxcyc=400):
    p = P0 if p is None else p
    T = 60.0 / p['HR']; dt = T / nsteps
    tau = (np.arange(nsteps)) * dt
    PHA = p['PHA_mean'] + PHA_amp * np.sin(2 * np.pi * tau / T)
    # states: QHA, Psin, QHV, Phv
    Q = 0.4; Ps = 4.0; Qh = Qpv + 0.4; Ph = p['PIVC'] + p['RpHVout'] * Qh
    prev = None
    for cyc in range(maxcyc):
        QHAs = np.empty(nsteps)
        for k in range(nsteps):
            dQ = (PHA[k] - RsHA * Q - Ps) / LHA
            dPs = (Q + Qpv - Qh - Ps / p['Rpsin']) / p['Csin']
            dQh = (Ps - p['RsHV'] * Qh - Ph) / p['LHV']
            dPh = (Qh - (Ph - p['PIVC']) / p['RpHVout']) / p['Chv']
            Q += dt * dQ; Ps += dt * dPs; Qh += dt * dQh; Ph += dt * dPh
            QHAs[k] = Q
        m = QHAs.mean()
        if prev is not None and abs(m - prev) / abs(m) < tol and cyc > 5:
            break
        prev = m
    v = QHAs / p['AHA']
    PSV = v.max(); EDV = v.min()
    return dict(PSV=PSV, RI=(PSV - EDV) / PSV, meanQ=m * 60.0, v=v, Psin=Ps)


def simulate_fast(RsHA, LHA, PHA_amp, Qpv, p=None, nsteps=400):
    """exact periodic steady state of the forward-Euler map (same discretisation as the time-stepping code)"""
    p = P0 if p is None else p
    T = 60.0 / p['HR']; dt = T / nsteps
    J = np.array([[-RsHA / LHA, -1 / LHA, 0, 0],
                  [1 / p['Csin'], -1 / (p['Rpsin'] * p['Csin']), -1 / p['Csin'], 0],
                  [0, 1 / p['LHV'], -p['RsHV'] / p['LHV'], -1 / p['LHV']],
                  [0, 0, 1 / p['Chv'], -1 / (p['RpHVout'] * p['Chv'])]])
    A = np.eye(4) + dt * J
    tau = np.arange(nsteps) * dt
    PHA = p['PHA_mean'] + PHA_amp * np.sin(2 * np.pi * tau / T)
    def g(k):
        return np.array([PHA[k] / LHA, Qpv / p['Csin'], 0.0, p['PIVC'] / (p['RpHVout'] * p['Chv'])])
    # x_{k+1} = A x_k + dt g_k ; x_N = A^N x_0 + c
    c = np.zeros(4); AN = np.eye(4)
    for k in range(nsteps):
        c = A @ c + dt * g(k); AN = A @ AN
    x0 = np.linalg.solve(np.eye(4) - AN, c)
    x = x0.copy(); Q = np.empty(nsteps)
    for k in range(nsteps):
        x = A @ x + dt * g(k); Q[k] = x[0]
    v = Q / p['AHA']
    PSV = v.max(); EDV = v.min()
    return dict(PSV=PSV, RI=(PSV - EDV) / PSV, meanQ=Q.mean() * 60.0, v=v, Psin=x[1])
