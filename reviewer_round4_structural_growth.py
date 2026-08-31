"""
Round-4 reviewer point 2: the existing HA-growth sensitivity only changes
the flow-to-velocity OBSERVATION equation's area (A_HA), leaving the
circuit's own Rs_HA/L_HA unchanged -- a "kinematic dilution" effect, not a
physical simulation of arterial growth. This adds a second, exploratory
"structural remodeling" variant in which L_HA ALSO scales geometrically
with assumed radius growth (inertance ~ 1/r^2 for a fixed-length vessel),
while Rs_HA continues to be solved via the same HABR flow-target
procedure (representing the idea that the flow-target itself is set by
HABR's regulatory response, on top of whatever passive geometric change
has occurred) -- a specific, stated modelling choice, not the only
possible way to combine the two effects.

Also combines baseline HA diameter (1.0/1.2/1.4mm) with postoperative
growth, since Round 4 point 5 asks whether the growth-sensitivity shape
is similar across baselines.
"""

import numpy as np
from scipy.optimize import brentq, minimize

from ldlt_habr_consistent_units import (
    simulate_ha_branch, MEASURED, habr_percent_change,
    PV_DIAMETER_POD1_CM, PV_VELOCITY_TO_FLOW_FACTOR, A_HA_CM2,
)


def q_pv_flow(pvv, diameter_cm=PV_DIAMETER_POD1_CM):
    r = diameter_cm / 2.0
    return np.pi * r**2 * PV_VELOCITY_TO_FLOW_FACTOR * pvv * 60.0


def a_ha(diameter_cm):
    return np.pi * (diameter_cm / 2.0) ** 2


def anchor_at_pod1(A_HA, Q_PV_pod1, x0=(127.9, 5.8, 27.4)):
    def obj(x):
        Rs_HA, L_HA, P_amp = x
        if Rs_HA <= 0 or L_HA <= 0 or P_amp <= 0:
            return 1e6
        res = simulate_ha_branch(Rs_HA, P_amp, Q_PV_pod1, L_HA)
        if not res["converged"]:
            return 1e6
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


def run(ha_growth_pct, ha_diam_pod1_mm=1.2, structural=False):
    """structural=False: kinematic dilution only (only A_HA changes at
    the observation-equation step). structural=True: L_HA additionally
    scaled geometrically (~1/(1+g)^2) before solving Rs_HA to the same
    HABR flow target."""
    ha_diam_pod1_cm = ha_diam_pod1_mm / 10.0
    A_HA_pod1 = a_ha(ha_diam_pod1_cm)
    Q_PV_pod1 = q_pv_flow(MEASURED["POD1"]["PVV"])

    (Rs_HA_pod1, L_HA_pod1, P_HA_amp), resid = anchor_at_pod1(A_HA_pod1, Q_PV_pod1)
    assert resid < 1e-6

    pod1_res = simulate_ha_branch(Rs_HA_pod1, P_HA_amp, Q_PV_pod1, L_HA_pod1)
    mean_Q_HA_pod1 = pod1_res["mean_Q_HA_mLmin"]

    g_ha = ha_growth_pct / 100.0
    ha_diam_30 = ha_diam_pod1_cm * (1 + g_ha)
    A_HA_30 = a_ha(ha_diam_30)
    L_HA_30 = L_HA_pod1 / (1 + g_ha) ** 2 if structural else L_HA_pod1

    Q_PV_30 = q_pv_flow(MEASURED["POD30"]["PVV"])
    change_Ipv = (Q_PV_pod1 - Q_PV_30) / Q_PV_pod1 * 100.0
    change_Iha = habr_percent_change(change_Ipv)
    target_Q = mean_Q_HA_pod1 * (1.0 - change_Iha / 100.0)
    Rs_HA_30 = find_Rs_HA(target_Q, P_HA_amp, Q_PV_30, L_HA_30,
                           0.3 * Rs_HA_pod1, 3.0 * Rs_HA_pod1)
    res_30 = simulate_ha_branch(Rs_HA_30, P_HA_amp, Q_PV_30, L_HA_30)

    psv_30 = res_30["PSV_HA"] * (A_HA_CM2 / A_HA_30)
    measured_decline = MEASURED["POD1"]["PSV_HA"] - MEASURED["POD30"]["PSV_HA"]
    model_decline = 53.10 - psv_30
    frac = model_decline / measured_decline * 100.0
    return psv_30, frac


if __name__ == "__main__":
    print("=== Kinematic dilution only (area changes; Rs_HA/L_HA circuit "
          "parameters unaffected by growth) vs. structural remodeling "
          "(L_HA also scaled geometrically) ===")
    for g in (0, 10, 20, 30, 40):
        psv_k, frac_k = run(g, structural=False)
        psv_s, frac_s = run(g, structural=True)
        print(f"HA growth={g}%: kinematic-only frac={frac_k:.1f}%  "
              f"structural frac={frac_s:.1f}%  (PSV: {psv_k:.2f} vs {psv_s:.2f})")

    print("\n=== Growth sensitivity (kinematic-only) across baseline HA "
          "diameters 1.0/1.2/1.4mm ===")
    for baseline in (1.0, 1.2, 1.4):
        print(f"baseline={baseline}mm:")
        for g in (0, 10, 20, 30, 40):
            psv, frac = run(g, ha_diam_pod1_mm=baseline, structural=False)
            print(f"  growth={g}%: frac={frac:.1f}%")
