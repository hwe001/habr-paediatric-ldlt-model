"""
Round-2 reviewer correction: the previous post-LDLT model summed Q_HA
(numerically calibrated directly to Doppler velocity, cm/s) and Q_PV
(computed in mL/min-scale units via Chen et al.'s formula) directly in the
sinusoidal-node mass balance -- a genuine dimensional inconsistency, not
just an uncertain weighting, as the reviewer correctly identified.

Fix: Q_HA is now calibrated as a real, mL/min-consistent volumetric flow
(the same convention as the generic model and as Q_PV), using an assumed
hepatic-artery cross-sectional area to convert between flow and Doppler
velocity -- exactly the same kind of conversion Chen et al. use for the
portal vein, and exactly what the reviewer's Option A requires. The area
is not invented: Kim et al. (2007, Radiology, doi:10.1148/radiol.2452061093)
report right hepatic artery diameter 1.2 +/- 0.2 mm in a healthy
(non-jaundiced) control group of infants (mean age 67 days). This is the
best available published paediatric HA calibre reference we located; it
is a NATIVE, disease-free artery in a slightly younger cohort than ours,
not a measurement of this cohort's own graft artery at the anastomosis --
an assumption, flagged as such, not a measured quantity for this cohort.

With A_HA fixed from this literature value, Rs_HA and L_HA are calibrated
(2 unknowns, 2 targets: real PSV_HA and RI_HA at POD1) in the SAME
mL/min-consistent physical units as Q_PV and the generic model -- fully
resolving the unit mismatch, not just disclosing it.
"""

import numpy as np
from scipy.optimize import minimize, brentq

from pi_filter_healthy_infant_model import TARGETS, solve_dc_resistances, DEFAULT_SHAPE_PARAMS, MMHG_PER_SEC_FLOW

MEASURED = {
    # Pre-operative biliary-atresia state (Chen et al. 2022, Tables 1-2).
    # Added for the pre-op -> POD1 transplant-step analysis (preop_ba_state.py):
    # the cirrhotic native liver's high arterial velocity/resistance and low
    # portal velocity. PV diameter pre-op is 0.44 +/- 0.09 cm (vs 0.46 at
    # POD1); the pre-op portal-flow conversion uses that value.
    "Pre-op": {"PSV_HA": 73.32, "RI_HA": 0.77, "PVV": 16.88,
               "PV_DIAMETER_CM": 0.44},
    "POD1":  {"PSV_HA": 53.10, "RI_HA": 0.61, "PVV": 30.80},
    "POD7":  {"PSV_HA": 47.02, "RI_HA": 0.59, "PVV": 30.05},
    "POD14": {"PSV_HA": 42.29, "RI_HA": 0.59, "PVV": 28.39},
    "POD30": {"PSV_HA": 38.51, "RI_HA": 0.59, "PVV": 26.71},
}

# Kim et al. 2007 (Radiology, doi:10.1148/radiol.2452061093), healthy
# (non-jaundiced) infant control group: right hepatic artery diameter
# 1.2 +/- 0.2 mm. An assumption for THIS cohort's graft artery, not a
# measurement of it -- flagged explicitly, see module docstring.
HA_DIAMETER_CM = 0.12
A_HA_CM2 = np.pi * (HA_DIAMETER_CM / 2.0) ** 2  # ~0.0113 cm^2

PV_DIAMETER_POD1_CM = 0.46
PV_VELOCITY_TO_FLOW_FACTOR = 0.57


def q_pv_flow(pvv_cm_s, diameter_cm=PV_DIAMETER_POD1_CM):
    """Chen et al.'s own formula -- mL/min-scale (see round-1 Methods 2.4
    for the unresolved mL/min vs mL/min/100g labelling issue, unchanged
    here and still flagged in the manuscript)."""
    r = diameter_cm / 2.0
    return np.pi * r**2 * PV_VELOCITY_TO_FLOW_FACTOR * pvv_cm_s * 60.0


def velocity_from_flow_mLmin(q_mLmin, area_cm2=A_HA_CM2):
    """cm/s, from a real mL/min-consistent flow and an assumed area."""
    q_cm3_s = q_mLmin / 60.0
    return q_cm3_s / area_cm2


def habr_percent_change(change_Ipv):
    return 0.0007102 * change_Ipv**2 + 0.5492 * change_Ipv


_GENERIC = solve_dc_resistances()
BASE_PARAMS = dict(_GENERIC)
BASE_PARAMS.update(DEFAULT_SHAPE_PARAMS)


def simulate_ha_branch(Rs_HA, P_HA_amp, Q_PV_mLmin, L_HA, params=BASE_PARAMS,
                        P_HA_mean=None, HR=130.0,
                        t_end_cycles=100, steps_per_cycle=400):
    """Same 4-state system as before, but Q_HA is now a real mL/min-scale
    flow throughout -- consistent with Q_PV -- with velocity extracted
    only at the final step via the assumed HA area."""
    if P_HA_mean is None:
        P_HA_mean = TARGETS["P_HA_src_mean"]
    period = 60.0 / HR
    dt = period / steps_per_cycle
    n_steps = int(round(t_end_cycles * steps_per_cycle))

    Rs_HV, Rp_hv_out = params["Rs_HV"], params["Rp_hv_out"]
    L_HV = params["L_HV"]
    C_sinus, C_hv = params["C_sinus"], params["C_hv"]
    Rp_sinus = params["Rp_sinus"]
    P_IVC = TARGETS["P_IVC"]

    Q_PV = Q_PV_mLmin * MMHG_PER_SEC_FLOW
    Q_HA = TARGETS["Q_HA_mean"] * MMHG_PER_SEC_FLOW
    Q_HV = TARGETS["Q_HV_mean"] * MMHG_PER_SEC_FLOW
    P_sinus = TARGETS["P_sinus"]
    P_hv = TARGETS["P_hv"]

    hist = np.empty(steps_per_cycle)
    prev = None
    t = 0.0
    converged = False

    for step in range(n_steps):
        P_HA_src = P_HA_mean + P_HA_amp * np.sin(2 * np.pi * t / period)

        dQ_HA = (P_HA_src - Rs_HA * Q_HA - P_sinus) / L_HA
        dP_sinus = (Q_HA + Q_PV - Q_HV - (P_sinus / Rp_sinus)) / C_sinus
        dQ_HV = (P_sinus - Rs_HV * Q_HV - P_hv) / L_HV
        dP_hv = (Q_HV - (P_hv - P_IVC) / Rp_hv_out) / C_hv

        Q_HA += dt * dQ_HA
        P_sinus += dt * dP_sinus
        Q_HV += dt * dQ_HV
        P_hv += dt * dP_hv
        t += dt

        idx = step % steps_per_cycle
        hist[idx] = Q_HA

        if idx == steps_per_cycle - 1:
            this_cycle = hist.copy()
            if prev is not None:
                rel = np.max(np.abs(this_cycle - prev)) / (np.max(np.abs(prev)) + 1e-12)
                if rel < 1e-4:
                    converged = True
                    prev = this_cycle
                    break
            prev = this_cycle

    q_sys_mLmin = float(prev.max()) * 60.0
    q_dias_mLmin = float(prev.min()) * 60.0
    q_mean_mLmin = float(prev.mean()) * 60.0

    v_sys = velocity_from_flow_mLmin(q_sys_mLmin)
    v_dias = velocity_from_flow_mLmin(q_dias_mLmin)
    return {
        "PSV_HA": v_sys, "EDV_HA": v_dias,
        "mean_Q_HA_mLmin": q_mean_mLmin,
        "RI_HA": (v_sys - v_dias) / v_sys,
        "converged": converged,
    }


def anchor_objective(x, Q_PV_pod1):
    Rs_HA, L_HA, P_HA_amp = x
    if Rs_HA <= 0 or L_HA <= 0 or P_HA_amp <= 0:
        return 1e6
    res = simulate_ha_branch(Rs_HA, P_HA_amp, Q_PV_pod1, L_HA)
    if not res["converged"]:
        return 1e6
    err_psv = (res["PSV_HA"] - MEASURED["POD1"]["PSV_HA"]) / MEASURED["POD1"]["PSV_HA"]
    err_ri = (res["RI_HA"] - MEASURED["POD1"]["RI_HA"]) / MEASURED["POD1"]["RI_HA"]
    return err_psv**2 + err_ri**2


def find_Rs_HA_for_target_flow(target_mean_Q_mLmin, P_HA_amp, Q_PV_mLmin, L_HA, Rs_lo, Rs_hi):
    def f(Rs_HA):
        res = simulate_ha_branch(Rs_HA, P_HA_amp, Q_PV_mLmin, L_HA)
        return res["mean_Q_HA_mLmin"] - target_mean_Q_mLmin

    f_lo, f_hi = f(Rs_lo), f(Rs_hi)
    tries = 0
    while f_lo * f_hi > 0 and tries < 40:
        Rs_lo *= 0.7
        Rs_hi *= 1.4
        f_lo, f_hi = f(Rs_lo), f(Rs_hi)
        tries += 1
    return brentq(f, Rs_lo, Rs_hi, xtol=1e-8)


if __name__ == "__main__":
    print(f"Assumed HA diameter: {HA_DIAMETER_CM*10:.1f} mm (Kim et al. 2007, "
          f"healthy infant control group), area={A_HA_CM2:.5f} cm^2\n")

    v_pv_pod1 = MEASURED["POD1"]["PVV"]
    Q_PV_pod1 = q_pv_flow(v_pv_pod1)

    print("=== Anchor at POD1 (Rs_HA, L_HA, P_HA_amp jointly fit, 3 unknowns "
          "/ 2 targets -- necessarily non-unique, see text) ===")
    x0 = np.array([150.0, 5.0, 30.0])
    opt = minimize(anchor_objective, x0, args=(Q_PV_pod1,),
                   method="Nelder-Mead",
                   options={"xatol": 1e-9, "fatol": 1e-14, "maxiter": 8000})
    Rs_HA_pod1, L_HA_pod1, P_HA_amp_fixed = opt.x
    pod1_res = simulate_ha_branch(Rs_HA_pod1, P_HA_amp_fixed, Q_PV_pod1, L_HA_pod1)
    print(f"Rs_HA(POD1)={Rs_HA_pod1:.4f}, L_HA={L_HA_pod1:.4f}, "
          f"P_HA_amp={P_HA_amp_fixed:.2f} mmHg (literature value was "
          f"{TARGETS['P_HA_src_amp']:.2f})")
    print(f"POD1 simulated: PSV_HA={pod1_res['PSV_HA']:.2f} (measured 53.10), "
          f"RI_HA={pod1_res['RI_HA']:.3f} (measured 0.61), "
          f"mean_Q_HA={pod1_res['mean_Q_HA_mLmin']:.2f} mL/min "
          f"(generic-model target was 31.93 mL/min), converged={opt.success}")

    mean_Q_HA_pod1 = pod1_res["mean_Q_HA_mLmin"]

    print("\n=== Continuous-application scenario ===")
    rows_continuous = [("POD1", pod1_res["PSV_HA"], pod1_res["RI_HA"])]
    for label in ("POD7", "POD14", "POD30"):
        v_pv_t = MEASURED[label]["PVV"]
        Q_PV_t = q_pv_flow(v_pv_t)
        change_Ipv = (Q_PV_pod1 - Q_PV_t) / Q_PV_pod1 * 100.0
        change_Iha = habr_percent_change(change_Ipv)
        target_Q = mean_Q_HA_pod1 * (1.0 - change_Iha / 100.0)
        Rs_HA_t = find_Rs_HA_for_target_flow(
            target_Q, P_HA_amp_fixed, Q_PV_t, L_HA_pod1,
            Rs_lo=0.3 * Rs_HA_pod1, Rs_hi=3.0 * Rs_HA_pod1)
        res_t = simulate_ha_branch(Rs_HA_t, P_HA_amp_fixed, Q_PV_t, L_HA_pod1)
        rows_continuous.append((label, res_t["PSV_HA"], res_t["RI_HA"]))
        print(f"{label}: measured PSV={MEASURED[label]['PSV_HA']:.2f} RI={MEASURED[label]['RI_HA']:.3f} | "
              f"model PSV={res_t['PSV_HA']:.2f} RI={res_t['RI_HA']:.3f} (Rs_HA={Rs_HA_t:.3f})")

    print("\n=== Null scenario (Rs_HA frozen at POD1) ===")
    for label in ("POD7", "POD14", "POD30"):
        v_pv_t = MEASURED[label]["PVV"]
        Q_PV_t = q_pv_flow(v_pv_t)
        res_null = simulate_ha_branch(Rs_HA_pod1, P_HA_amp_fixed, Q_PV_t, L_HA_pod1)
        print(f"{label}: model PSV={res_null['PSV_HA']:.2f} RI={res_null['RI_HA']:.3f}")

    print("\n=== Diameter-growth sensitivity re-check (0/10/20/30/40% by POD30), "
          "now in consistent units ===")
    for growth_pct in (0, 10, 20, 30, 40):
        g = growth_pct / 100.0
        diam = {"POD7": PV_DIAMETER_POD1_CM * (1 + g * 7 / 30),
                "POD14": PV_DIAMETER_POD1_CM * (1 + g * 14 / 30),
                "POD30": PV_DIAMETER_POD1_CM * (1 + g * 30 / 30)}
        psv_out = {}
        for label in ("POD7", "POD14", "POD30"):
            v_pv_t = MEASURED[label]["PVV"]
            Q_PV_t = q_pv_flow(v_pv_t, diam[label])
            change_Ipv = (Q_PV_pod1 - Q_PV_t) / Q_PV_pod1 * 100.0
            change_Iha = habr_percent_change(change_Ipv)
            target_Q = mean_Q_HA_pod1 * (1.0 - change_Iha / 100.0)
            Rs_HA_t = find_Rs_HA_for_target_flow(
                target_Q, P_HA_amp_fixed, Q_PV_t, L_HA_pod1,
                Rs_lo=0.3 * Rs_HA_pod1, Rs_hi=3.0 * Rs_HA_pod1)
            res_t = simulate_ha_branch(Rs_HA_t, P_HA_amp_fixed, Q_PV_t, L_HA_pod1)
            psv_out[label] = res_t["PSV_HA"]
        measured_decline_30 = MEASURED["POD1"]["PSV_HA"] - MEASURED["POD30"]["PSV_HA"]
        model_decline_30 = pod1_res["PSV_HA"] - psv_out["POD30"]
        frac30 = model_decline_30 / measured_decline_30 * 100.0
        print(f"{growth_pct}% growth: PSV POD30={psv_out['POD30']:.2f}, "
              f"% explained={frac30:.1f}%")
