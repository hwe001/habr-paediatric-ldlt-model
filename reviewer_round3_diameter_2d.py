"""
Round-3 reviewer requirement: HA diameter needs its own sensitivity
analysis (the earlier sweep only varied PV diameter, wrongly implying
calibre uncertainty is a portal-only issue). Tests:
1. Baseline HA diameter across the published reference uncertainty
   (1.0-1.4 mm) -- with NO postoperative growth, PROPERLY re-anchoring
   the POD1 fit for each candidate baseline diameter (an earlier version
   of this script skipped that step, which silently broke the POD1
   anchor and produced spurious baseline-sensitivity -- corrected here).
2. Postoperative HA diameter growth alone (PV growth fixed at 0%).
3. A 2D grid varying BOTH PV and HA diameter growth jointly.
"""

import numpy as np
from scipy.optimize import brentq, minimize

from ldlt_habr_consistent_units import (
    simulate_ha_branch, MEASURED, habr_percent_change,
    PV_DIAMETER_POD1_CM, PV_VELOCITY_TO_FLOW_FACTOR,
)


def q_pv_flow(pvv, diameter_cm):
    r = diameter_cm / 2.0
    return np.pi * r**2 * PV_VELOCITY_TO_FLOW_FACTOR * pvv * 60.0


def a_ha(diameter_cm):
    return np.pi * (diameter_cm / 2.0) ** 2


def velocity_from_flow(q_mLmin, area_cm2):
    return (q_mLmin / 60.0) / area_cm2


def anchor_at_pod1(A_HA, Q_PV_pod1, x0=(127.9, 5.8, 27.4)):
    """Jointly fit (Rs_HA, L_HA, P_HA_amp) to hit real POD1 PSV/RI, for a
    GIVEN A_HA -- properly re-anchoring for each candidate baseline
    diameter, unlike the earlier buggy version of this script."""
    def obj(x):
        Rs_HA, L_HA, P_amp = x
        if Rs_HA <= 0 or L_HA <= 0 or P_amp <= 0:
            return 1e6
        res = simulate_ha_branch(Rs_HA, P_amp, Q_PV_pod1, L_HA)
        if not res["converged"]:
            return 1e6
        v_sys = velocity_from_flow(res["mean_Q_HA_mLmin"] * 0 + res["PSV_HA"] * 0, A_HA) \
            if False else None
        # simulate_ha_branch already divides by the MODULE's fixed A_HA_CM2
        # internally to report PSV_HA/RI_HA; rescale its raw flow-based
        # PSV/EDV to this trial A_HA instead.
        from ldlt_habr_consistent_units import A_HA_CM2
        psv_v = res["PSV_HA"] * (A_HA_CM2 / A_HA)
        edv_v = res["EDV_HA"] * (A_HA_CM2 / A_HA)
        ri_v = (psv_v - edv_v) / psv_v
        e1 = (psv_v - 53.10) / 53.10
        e2 = (ri_v - 0.61) / 0.61
        return e1**2 + e2**2

    opt = minimize(obj, np.array(x0), method="Nelder-Mead",
                   options={"xatol": 1e-9, "fatol": 1e-14, "maxiter": 6000})
    return opt.x, opt.fun


def find_Rs_HA(target_mean_Q, P_amp, Q_PV, L_HA, Rs_lo, Rs_hi):
    def f(Rs_HA):
        res = simulate_ha_branch(Rs_HA, P_amp, Q_PV, L_HA)
        return res["mean_Q_HA_mLmin"] - target_mean_Q
    f_lo, f_hi = f(Rs_lo), f(Rs_hi)
    tries = 0
    while f_lo * f_hi > 0 and tries < 40:
        Rs_lo *= 0.7; Rs_hi *= 1.4
        f_lo, f_hi = f(Rs_lo), f(Rs_hi)
        tries += 1
    return brentq(f, Rs_lo, Rs_hi, xtol=1e-8)


def run(pv_growth_pct, ha_growth_pct, ha_diam_pod1_mm=1.2):
    ha_diam_pod1_cm = ha_diam_pod1_mm / 10.0
    A_HA_pod1 = a_ha(ha_diam_pod1_cm)
    Q_PV_pod1 = q_pv_flow(MEASURED["POD1"]["PVV"], PV_DIAMETER_POD1_CM)

    (Rs_HA_pod1, L_HA_pod1, P_HA_amp), resid = anchor_at_pod1(A_HA_pod1, Q_PV_pod1)
    assert resid < 1e-6, f"anchor fit failed, residual={resid}"

    pod1_res = simulate_ha_branch(Rs_HA_pod1, P_HA_amp, Q_PV_pod1, L_HA_pod1)
    mean_Q_HA_pod1_flow = pod1_res["mean_Q_HA_mLmin"]

    g_pv, g_ha = pv_growth_pct / 100.0, ha_growth_pct / 100.0
    pv_diam_30 = PV_DIAMETER_POD1_CM * (1 + g_pv)
    ha_diam_30 = ha_diam_pod1_cm * (1 + g_ha)
    A_HA_30 = a_ha(ha_diam_30)

    Q_PV_30 = q_pv_flow(MEASURED["POD30"]["PVV"], pv_diam_30)
    change_Ipv = (Q_PV_pod1 - Q_PV_30) / Q_PV_pod1 * 100.0
    change_Iha = habr_percent_change(change_Ipv)
    target_Q = mean_Q_HA_pod1_flow * (1.0 - change_Iha / 100.0)
    Rs_HA_30 = find_Rs_HA(target_Q, P_HA_amp, Q_PV_30, L_HA_pod1,
                           0.3 * Rs_HA_pod1, 3.0 * Rs_HA_pod1)
    res_30 = simulate_ha_branch(Rs_HA_30, P_HA_amp, Q_PV_30, L_HA_pod1)

    from ldlt_habr_consistent_units import A_HA_CM2
    psv_30 = res_30["PSV_HA"] * (A_HA_CM2 / A_HA_30)
    measured_decline = MEASURED["POD1"]["PSV_HA"] - MEASURED["POD30"]["PSV_HA"]
    model_decline = 53.10 - psv_30
    frac = model_decline / measured_decline * 100.0
    return psv_30, frac


if __name__ == "__main__":
    print("=== 1. Baseline HA diameter (1.0-1.4mm), NO growth, PROPERLY "
          "re-anchored at POD1 for each ===")
    for d in (1.0, 1.1, 1.2, 1.3, 1.4):
        psv, frac = run(pv_growth_pct=0, ha_growth_pct=0, ha_diam_pod1_mm=d)
        print(f"  HA diam={d:.1f}mm: PSV(POD30)={psv:.2f}  %explained={frac:.1f}%")

    print("\n=== 2. HA diameter growth alone (PV growth fixed at 0%) ===")
    for g in (0, 10, 20, 30, 40):
        psv, frac = run(pv_growth_pct=0, ha_growth_pct=g)
        print(f"  HA growth={g}%: PSV(POD30)={psv:.2f}  %explained={frac:.1f}%")

    print("\n=== 3. 2D grid: PV growth x HA growth (%% explained at POD30) ===")
    pv_grid = [0, 10, 20]
    ha_grid = [0, 10, 20]
    header = "PVgrowth\\HAgrowth  " + "  ".join(f"{h:>6}%" for h in ha_grid)
    print(header)
    for pvg in pv_grid:
        row = [f"{pvg:>14}%   "]
        for hag in ha_grid:
            _, frac = run(pv_growth_pct=pvg, ha_growth_pct=hag)
            row.append(f"{frac:>6.1f}%")
        print(" ".join(row))
