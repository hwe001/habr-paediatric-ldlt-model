"""
HABR/transplant-state test, folded back onto the validated generic pi-filter
circulation model (pi_filter_healthy_infant_model.py), replacing the earlier
ad hoc single-branch version (ldlt_habr_model.py / calibrate_and_test.py --
superseded, kept only for history; see model_plan_and_literature_data.md
Section 8).

Base circuit (unchanged from pi_filter_healthy_infant_model.py): HA pi-filter
draining into a shared sinusoidal node, HV pi-filter draining that node to
the IVC reference. Rs_PV, Rs_HV, Rp_hv_out, and all L/C "shape" parameters
are taken directly from the validated generic model -- NOT re-fit here.

Two changes on top of the generic model, both explicitly justified:

1. The portal branch is now a PRESCRIBED input, Q_PV(t), rather than its own
   L-Rs state. The generic model itself already showed (empirically) that
   Q_PV varies by well under 0.2% across a cardiac cycle -- i.e. it is, in
   its own validated form, indistinguishable from quasi-static -- so
   replacing its ODE with an algebraic value at each post-operative time
   point is a simplification justified by that model's own result, not an
   ad hoc shortcut.

   Q_PV(t) is now anchored to REAL, cohort-specific data rather than a
   value borrowed from a different paper's cohort (an earlier version of
   this script used Q_PV(t) = 300 * v_PV(t)/v_PV(POD1) mL/min, scaling a
   generic Ho/Yu/Bartlett target by this cohort's measured PVV change --
   superseded). Chen et al. 2022 (Front. Bioeng. Biotechnol.,
   doi:10.3389/fbioe.2022.903385 -- the actual published source of this
   project's clinical dataset) report this cohort's own real portal vein
   diameter (0.44 cm pre-transplant, 0.46 cm POD1) and their own flow
   formula PVF = pi*r^2*0.57*PVV*60 (mL/min/100g of graft). Q_PV(t) here
   uses that formula directly with each time point's real measured PVV,
   holding diameter fixed at the POD1 value (0.46 cm) for POD7/14/30 since
   no later diameter measurements exist in the source paper -- justified by
   checking the formula across the pre-op->POD1 transition, where diameter
   IS reported: area increased only 9.3% while velocity increased 82.5%,
   combining to a 99.4% flow increase that matches the reported 97.9%
   almost exactly, confirming velocity (not area) dominates the flow change
   in this cohort (see model_plan_and_literature_data.md Section 11). All
   values are therefore expressed in mL/min/100g (per 100 g of graft), not
   absolute mL/min -- consistent throughout since Q_HA's scale is likewise
   only ever calibrated (Step 2 below), never assumed in absolute units.

2. Rs_HA and the HA pulse amplitude are calibrated ONCE at POD1 (this
   project's real measured PSV_HA/RI_HA anchor -- see
   model_plan_and_literature_data.md Section 7 for why POD1, not pre-op, is
   used as the anchor). Thereafter, Rs_HA at POD7/14/30 is set purely by
   what the Yu/Bartlett/Hunter/Ho HABR quadratic predicts from the measured
   portal-velocity change -- not fit to the HA data. This exactly mirrors
   the falsifiable-prediction structure of the earlier (now superseded)
   test, just running on the physiologically grounded circuit instead of
   the ad hoc one.
"""

import csv

import numpy as np
from scipy.optimize import minimize, brentq

from pi_filter_healthy_infant_model import (
    TARGETS, solve_dc_resistances, DEFAULT_SHAPE_PARAMS, MMHG_PER_SEC_FLOW,
)

MEASURED = {
    "POD1":  {"PSV_HA": 53.10, "RI_HA": 0.61, "PVV": 30.80},
    "POD7":  {"PSV_HA": 47.02, "RI_HA": 0.59, "PVV": 30.05},
    "POD14": {"PSV_HA": 42.29, "RI_HA": 0.59, "PVV": 28.39},
    "POD30": {"PSV_HA": 38.51, "RI_HA": 0.59, "PVV": 26.71},
}

# Chen et al. 2022 (Front. Bioeng. Biotechnol., doi:10.3389/fbioe.2022.903385)
# real portal vein diameter; only pre-op and POD1 are reported, so POD1's
# value is held fixed for POD7/14/30 (see module docstring for the check
# justifying this).
PV_DIAMETER_POD1_CM = 0.46
PV_VELOCITY_TO_FLOW_FACTOR = 0.57  # their empirical peak-to-mean-velocity factor


def real_pvf_mL_min_per_100g(PVV_cm_s, diameter_cm=PV_DIAMETER_POD1_CM):
    """Chen et al. 2022's own formula: PVF = pi*r^2*0.57*PVV*60, mL/min/100g."""
    r = diameter_cm / 2.0
    return np.pi * r**2 * PV_VELOCITY_TO_FLOW_FACTOR * PVV_cm_s * 60.0

# Rs_PV, Rs_HV, Rp_hv_out, and all L/C shape parameters: taken directly from
# the validated generic model, not re-fit.
_GENERIC = solve_dc_resistances()
BASE_PARAMS = dict(_GENERIC)
BASE_PARAMS.update(DEFAULT_SHAPE_PARAMS)


def habr_percent_change(change_Ipv):
    """Yu/Bartlett/Hunter/Ho quadratic (percent-change form). Positive input
    means a DECREASE relative to the reference (their sign convention)."""
    return 0.0007102 * change_Ipv**2 + 0.5492 * change_Ipv


def simulate_ha_branch(Rs_HA, P_HA_amp, Q_PV_mLmin, L_HA=None, params=BASE_PARAMS,
                        P_HA_mean=None, HR=130.0,
                        t_end_cycles=80, steps_per_cycle=400):
    """Integrate the 4-state system (Q_HA, P_sinus, Q_HV, P_hv) with Q_PV(t)
    prescribed (constant within one call, representing one post-operative
    time point's quasi-static state).

    L_HA is normally taken from the generic model, but it (like all the
    L/C "shape" parameters) was never independently validated -- it was
    chosen empirically for the GENERIC model's own Rs_HA scale, which is
    very different from this cohort's calibrated Rs_HA (see Step 1's fit).
    So L_HA is re-calibrated here alongside Rs_HA (with the HA pulse
    amplitude held at the real, literature-anchored value instead) rather
    than reused verbatim -- reusing it verbatim was tried first and forced
    an unphysical fitted pulse amplitude (440 mmHg) to compensate for the
    mismatched time constant; see model_plan_and_literature_data.md Section 9.
    """
    if P_HA_mean is None:
        P_HA_mean = TARGETS["P_HA_src_mean"]
    if L_HA is None:
        L_HA = params["L_HA"]
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

    hist = {"Q_HA": np.empty(steps_per_cycle)}
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
        hist["Q_HA"][idx] = Q_HA

        if idx == steps_per_cycle - 1:
            this_cycle = hist["Q_HA"].copy()
            if prev is not None:
                rel = np.max(np.abs(this_cycle - prev)) / (np.max(np.abs(prev)) + 1e-12)
                if rel < 1e-4:
                    converged = True
                    prev = this_cycle
                    break
            prev = this_cycle

    v_sys, v_dias, v_mean = float(prev.max()), float(prev.min()), float(prev.mean())
    return {
        "PSV_HA": v_sys, "EDV_HA": v_dias, "mean_Q_HA": v_mean,
        "RI_HA": (v_sys - v_dias) / v_sys,
        "converged": converged,
    }


def anchor_objective(x, Q_PV_pod1, P_HA_amp):
    Rs_HA, L_HA = x
    if Rs_HA <= 0 or L_HA <= 0:
        return 1e6
    res = simulate_ha_branch(Rs_HA, P_HA_amp, Q_PV_pod1, L_HA=L_HA)
    if not res["converged"]:
        return 1e6
    err_psv = (res["PSV_HA"] - MEASURED["POD1"]["PSV_HA"]) / MEASURED["POD1"]["PSV_HA"]
    err_ri = (res["RI_HA"] - MEASURED["POD1"]["RI_HA"]) / MEASURED["POD1"]["RI_HA"]
    return err_psv**2 + err_ri**2


def find_Rs_HA_for_target_flow(target_mean_Q, P_HA_amp, Q_PV_mLmin, L_HA, Rs_lo, Rs_hi):
    def f(Rs_HA):
        res = simulate_ha_branch(Rs_HA, P_HA_amp, Q_PV_mLmin, L_HA=L_HA)
        return res["mean_Q_HA"] - target_mean_Q

    f_lo, f_hi = f(Rs_lo), f(Rs_hi)
    tries = 0
    while f_lo * f_hi > 0 and tries < 40:
        Rs_lo *= 0.7
        Rs_hi *= 1.4
        f_lo, f_hi = f(Rs_lo), f(Rs_hi)
        tries += 1
    return brentq(f, Rs_lo, Rs_hi, xtol=1e-8)


def main():
    v_pv_pod1 = MEASURED["POD1"]["PVV"]
    # real, cohort-specific anchor (Chen et al. 2022's own formula + their
    # own reported POD1 diameter/velocity), replacing the earlier borrowed
    # 300 mL/min value from a different cohort's paper
    Q_PV_pod1_mLmin = real_pvf_mL_min_per_100g(v_pv_pod1)
    print(f"Real cohort-specific Q_PV(POD1) = {Q_PV_pod1_mLmin:.2f} mL/min/100g "
          f"(Chen et al. 2022 formula; their own reported value: 165.99)")

    print("=== Step 0: base circuit parameters, taken from the validated "
          "generic model (not re-fit) ===")
    for k in ("Rs_PV", "Rs_HV", "Rp_hv_out"):
        print(f"  {k} = {BASE_PARAMS[k]:.4f}")

    print("\n=== Step 1: anchor HA branch (Rs_HA, L_HA) at POD1, HA pulse "
          "amplitude held at the real literature value ===")
    P_HA_amp_fixed = TARGETS["P_HA_src_amp"]
    x0 = np.array([BASE_PARAMS["Rs_HA"], BASE_PARAMS["L_HA"]])
    opt = minimize(anchor_objective, x0, args=(Q_PV_pod1_mLmin, P_HA_amp_fixed),
                   method="Nelder-Mead",
                   options={"xatol": 1e-8, "fatol": 1e-12, "maxiter": 5000})
    Rs_HA_pod1, L_HA_pod1 = opt.x
    print(f"Fitted Rs_HA(POD1)={Rs_HA_pod1:.4f} (generic model value was "
          f"{BASE_PARAMS['Rs_HA']:.4f}), L_HA={L_HA_pod1:.4f} (generic value "
          f"was {BASE_PARAMS['L_HA']:.4f}), P_HA_amp held at {P_HA_amp_fixed:.2f} "
          f"mmHg (the real literature value), "
          f"objective={opt.fun:.3e}, converged={opt.success}")

    pod1_res = simulate_ha_branch(Rs_HA_pod1, P_HA_amp_fixed, Q_PV_pod1_mLmin,
                                   L_HA=L_HA_pod1)
    print(f"POD1 simulated: PSV_HA={pod1_res['PSV_HA']:.2f} "
          f"(measured {MEASURED['POD1']['PSV_HA']}), "
          f"RI_HA={pod1_res['RI_HA']:.3f} (measured {MEASURED['POD1']['RI_HA']})")

    mean_Q_HA_pod1 = pod1_res["mean_Q_HA"]

    print("\n=== Step 2: HABR-predicted trajectory, POD7/14/30 "
          "(Rs_HA set by the parameter-free HABR quadratic; PSV_HA/RI_HA "
          "are the falsifiable model output, not fit) ===")

    rows = [("POD1", MEASURED["POD1"]["PSV_HA"], pod1_res["PSV_HA"],
              MEASURED["POD1"]["RI_HA"], pod1_res["RI_HA"], 0.0, "(anchor)")]
    null_rows = []

    for label in ("POD7", "POD14", "POD30"):
        v_pv_t = MEASURED[label]["PVV"]
        Q_PV_t_mLmin = real_pvf_mL_min_per_100g(v_pv_t)

        # source-script sign convention: change = (old-new)/old*100, i.e.
        # POSITIVE means a DECREASE relative to the POD1 reference.
        change_Ipv = (v_pv_pod1 - v_pv_t) / v_pv_pod1 * 100.0
        change_Iha_pred = habr_percent_change(change_Ipv)
        target_mean_Q = mean_Q_HA_pod1 * (1.0 - change_Iha_pred / 100.0)

        Rs_HA_t = find_Rs_HA_for_target_flow(
            target_mean_Q, P_HA_amp_fixed, Q_PV_t_mLmin, L_HA_pod1,
            Rs_lo=0.3 * Rs_HA_pod1, Rs_hi=3.0 * Rs_HA_pod1,
        )
        res_t = simulate_ha_branch(Rs_HA_t, P_HA_amp_fixed, Q_PV_t_mLmin, L_HA=L_HA_pod1)

        rows.append((label, MEASURED[label]["PSV_HA"], res_t["PSV_HA"],
                     MEASURED[label]["RI_HA"], res_t["RI_HA"],
                     v_pv_t - v_pv_pod1, f"Rs_HA={Rs_HA_t:.3f}"))

        # null model: Rs_HA frozen at POD1 value, only Q_PV(t) input changes
        null_res = simulate_ha_branch(Rs_HA_pod1, P_HA_amp_fixed, Q_PV_t_mLmin, L_HA=L_HA_pod1)
        null_rows.append((label, null_res["PSV_HA"], null_res["RI_HA"]))

    print(f"\n{'Time':<6} {'PSV meas':>9} {'PSV sim':>8} {'RI meas':>8} "
          f"{'RI sim':>7} {'dPVV':>7}  note")
    for label, psv_m, psv_s, ri_m, ri_s, dpvv, note in rows:
        print(f"{label:<6} {psv_m:>9.2f} {psv_s:>8.2f} {ri_m:>8.3f} "
              f"{ri_s:>7.3f} {dpvv:>7.2f}  {note}")

    print("\n=== Null-model comparison (Rs_HA frozen at POD1 value, HABR OFF) ===")
    print(f"{'Time':<6} {'PSV null':>9} {'RI null':>8}   (vs measured PSV/RI above)")
    for label, psv_n, ri_n in null_rows:
        m = MEASURED[label]
        print(f"{label:<6} {psv_n:>9.2f} {ri_n:>8.3f}   "
              f"(measured {m['PSV_HA']:.2f} / {m['RI_HA']:.3f})")

    print("\n=== Fraction of the measured PSV_HA decline reproduced by HABR alone ===")
    for (label, psv_m, psv_s, ri_m, ri_s, dpvv, note), (_, psv_n, ri_n) in zip(rows[1:], null_rows):
        measured_decline = rows[0][1] - psv_m
        habr_decline = rows[0][1] - psv_s
        frac = habr_decline / measured_decline * 100.0 if measured_decline else float("nan")
        print(f"{label:<6} measured drop={measured_decline:.2f}  "
              f"HABR-model drop={habr_decline:.2f} ({frac:.1f}% of measured)  "
              f"[null-model drift alone: {rows[0][1]-psv_n:.2f}]")

    with open("ldlt_habr_pi_filter_prediction_results.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time", "PSV_HA_measured", "PSV_HA_simulated",
                    "RI_HA_measured", "RI_HA_simulated", "delta_PVV_vs_POD1", "note"])
        for row in rows:
            w.writerow(row)
    with open("ldlt_habr_pi_filter_null_model_results.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time", "PSV_HA_null_no_habr", "RI_HA_null_no_habr"])
        for row in null_rows:
            w.writerow(row)
    print("\nSaved: ldlt_habr_pi_filter_prediction_results.csv, "
          "ldlt_habr_pi_filter_null_model_results.csv")


if __name__ == "__main__":
    main()
