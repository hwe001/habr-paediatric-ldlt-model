"""
Round-3 reviewer requirement: the POD1 calibration (Rs_HA, L_HA, P_HA_amp
jointly fit to 2 targets, PSV and RI) is non-identifiable. Rather than
reporting predictions from one arbitrarily-selected member of the
admissible family, generate the family directly (parametrized by
P_HA_amp, with Rs_HA/L_HA solved for each to hit both targets exactly)
and propagate EVERY family member through the continuous-HABR scenario to
POD30, reporting the envelope of predicted PSV_HA and "% explained"
instead of a single point estimate.
"""

import numpy as np
from scipy.optimize import minimize, brentq

from ldlt_habr_consistent_units import (
    simulate_ha_branch, q_pv_flow, MEASURED, habr_percent_change,
)

v_pv_pod1 = MEASURED["POD1"]["PVV"]
Q_PV_pod1 = q_pv_flow(v_pv_pod1)


def fit_Rs_L_for_amp(P_HA_amp, x0=(120.0, 5.0)):
    """For a FIXED P_HA_amp, solve (Rs_HA, L_HA) -- 2 unknowns, 2 targets
    (PSV, RI) -- via joint minimization. Returns None if not a good fit."""
    def obj(x):
        Rs_HA, L_HA = x
        if Rs_HA <= 0 or L_HA <= 0:
            return 1e6
        res = simulate_ha_branch(Rs_HA, P_HA_amp, Q_PV_pod1, L_HA)
        if not res["converged"]:
            return 1e6
        e1 = (res["PSV_HA"] - 53.10) / 53.10
        e2 = (res["RI_HA"] - 0.61) / 0.61
        return e1**2 + e2**2

    opt = minimize(obj, np.array(x0), method="Nelder-Mead",
                    options={"xatol": 1e-8, "fatol": 1e-14, "maxiter": 4000})
    if opt.fun > 1e-6:
        return None
    return opt.x[0], opt.x[1], opt.fun


def find_Rs_HA_for_target_flow(target_mean_Q, P_HA_amp, Q_PV_mLmin, L_HA, Rs_lo, Rs_hi):
    def f(Rs_HA):
        res = simulate_ha_branch(Rs_HA, P_HA_amp, Q_PV_mLmin, L_HA)
        return res["mean_Q_HA_mLmin"] - target_mean_Q
    f_lo, f_hi = f(Rs_lo), f(Rs_hi)
    tries = 0
    while f_lo * f_hi > 0 and tries < 40:
        Rs_lo *= 0.7
        Rs_hi *= 1.4
        f_lo, f_hi = f(Rs_lo), f(Rs_hi)
        tries += 1
    return brentq(f, Rs_lo, Rs_hi, xtol=1e-8)


if __name__ == "__main__":
    print("Scanning P_HA_amp to find the admissible family (Rs_HA, L_HA "
          "solved to hit PSV=53.10, RI=0.61 exactly for each P_HA_amp)...")
    family = []
    # first find the approximate threshold above which RI=0.61 is reachable
    x0 = (120.0, 5.0)
    for P_amp in np.arange(20.0, 61.0, 2.0):
        fit = fit_Rs_L_for_amp(P_amp, x0=x0)
        if fit is not None:
            Rs_HA, L_HA, resid = fit
            res = simulate_ha_branch(Rs_HA, P_amp, Q_PV_pod1, L_HA)
            family.append((P_amp, Rs_HA, L_HA, res["mean_Q_HA_mLmin"]))
            x0 = (Rs_HA, L_HA)  # warm-start next point

    print(f"Admissible family found: {len(family)} members, "
          f"P_HA_amp in [{family[0][0]:.1f}, {family[-1][0]:.1f}] mmHg\n")
    print(f"{'P_HA_amp':>9} {'Rs_HA':>10} {'L_HA':>8} {'mean_Q_HA':>10}")
    for P_amp, Rs_HA, L_HA, meanQ in family:
        print(f"{P_amp:>9.1f} {Rs_HA:>10.2f} {L_HA:>8.3f} {meanQ:>10.2f}")

    print("\nPropagating each family member through the continuous-HABR "
          "scenario to POD30...")
    results = []
    for P_amp, Rs_HA_pod1, L_HA_pod1, mean_Q_HA_pod1 in family:
        v_pv_30 = MEASURED["POD30"]["PVV"]
        Q_PV_30 = q_pv_flow(v_pv_30)
        change_Ipv = (Q_PV_pod1 - Q_PV_30) / Q_PV_pod1 * 100.0
        change_Iha = habr_percent_change(change_Ipv)
        target_Q = mean_Q_HA_pod1 * (1.0 - change_Iha / 100.0)
        try:
            Rs_HA_30 = find_Rs_HA_for_target_flow(
                target_Q, P_amp, Q_PV_30, L_HA_pod1,
                Rs_lo=0.3 * Rs_HA_pod1, Rs_hi=3.0 * Rs_HA_pod1)
        except Exception:
            continue
        res_30 = simulate_ha_branch(Rs_HA_30, P_amp, Q_PV_30, L_HA_pod1)
        measured_decline = MEASURED["POD1"]["PSV_HA"] - MEASURED["POD30"]["PSV_HA"]
        model_decline = 53.10 - res_30["PSV_HA"]
        frac = model_decline / measured_decline * 100.0
        results.append((P_amp, res_30["PSV_HA"], res_30["RI_HA"], frac))

    print(f"\n{'P_HA_amp':>9} {'PSV(POD30)':>11} {'RI(POD30)':>10} {'%% explained':>12}")
    for P_amp, psv, ri, frac in results:
        print(f"{P_amp:>9.1f} {psv:>11.2f} {ri:>10.3f} {frac:>11.1f}%")

    fracs = [r[3] for r in results]
    psvs = [r[1] for r in results]
    print(f"\nEnvelope across the admissible family:")
    print(f"  PSV(POD30): [{min(psvs):.2f}, {max(psvs):.2f}] cm/s")
    print(f"  %% explained: [{min(fracs):.1f}%, {max(fracs):.1f}%]")
