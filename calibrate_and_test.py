"""
SUPERSEDED (2026-08-31): replaced by ldlt_habr_on_pi_filter.py, which runs
this same test on the validated pi-filter circuit instead of the ad hoc
branch model here. Kept only for history. Do not use for new results.

Anchor the HA branch at POD1, then test whether the parameter-free HABR
quadratic (see ldlt_habr_model.py docstring) predicts the measured PSV_HA /
RI_HA trajectory over POD1 -> POD7 -> POD14 -> POD30, given only the
measured portal-vein-velocity (PVV) trajectory as input.

This deliberately excludes the pre-op -> POD1 transition: that step is a
discrete graft-replacement event (diseased native liver -> healthy graft),
not a same-organ flow perturbation, so applying a flow-flow HABR relationship
across it is not mechanistically appropriate (see model_plan_and_literature_
data.md Section 4.1). POD1 is instead used as the one-time calibration anchor
for the HA branch's otherwise-unconstrained parameters (R_HA, inlet pulse
amplitude).

Real data source: ../Graft hemodynamices.docx Table 2 (n=41, mean+-SD).
"""

import numpy as np
from scipy.optimize import minimize, brentq

from ldlt_habr_model import simulate, habr_percent_change

MEASURED = {
    "POD1":  {"PSV_HA": 53.10, "RI_HA": 0.61, "PVV": 30.80},
    "POD7":  {"PSV_HA": 47.02, "RI_HA": 0.59, "PVV": 30.05},
    "POD14": {"PSV_HA": 42.29, "RI_HA": 0.59, "PVV": 28.39},
    "POD30": {"PSV_HA": 38.51, "RI_HA": 0.59, "PVV": 26.71},
}

# Fixed, representative (not fitted) parameters. Flagged explicitly as
# assumptions -- this is a first-pass model, not a subject-specific fit.
FIXED = {
    "HR": 130.0,       # representative infant heart rate, 4-18 months old
    "L_HA": 0.5,       # hepatic arterial inertance (arbitrary consistent units)
    "C_sinus": 0.5,    # sinusoidal compliance
    "R_out": 2.0,      # sinusoid -> hepatic vein outflow resistance
    "P_hv": 5.0,       # hepatic vein reference pressure
    "k_pv": 0.3,       # portal-velocity -> sinusoid coupling gain
    "p0": 100.0,       # mean systemic driving pressure
}


def build_params(R_HA, dp_inlet, v_pv):
    p = dict(FIXED)
    p["R_HA"] = R_HA
    p["dp_inlet"] = dp_inlet
    p["v_pv"] = v_pv
    return p


def anchor_objective(x):
    R_HA, dp_inlet = x
    if R_HA <= 0 or dp_inlet <= 0:
        return 1e6
    params = build_params(R_HA, dp_inlet, MEASURED["POD1"]["PVV"])
    res = simulate(params)
    err_psv = (res["PSV_HA"] - MEASURED["POD1"]["PSV_HA"]) / MEASURED["POD1"]["PSV_HA"]
    err_ri = (res["RI_HA"] - MEASURED["POD1"]["RI_HA"]) / MEASURED["POD1"]["RI_HA"]
    return err_psv**2 + err_ri**2


def find_R_HA_for_target_flow(target_mean_Q, dp_inlet, v_pv, R_lo, R_hi):
    def f(R_HA):
        params = build_params(R_HA, dp_inlet, v_pv)
        res = simulate(params)
        return res["mean_Q_HA"] - target_mean_Q

    f_lo, f_hi = f(R_lo), f(R_hi)
    # expand bracket if needed (monotonic decreasing: higher R -> lower flow)
    tries = 0
    while f_lo * f_hi > 0 and tries < 40:
        R_lo *= 0.5
        R_hi *= 1.5
        f_lo, f_hi = f(R_lo), f(R_hi)
        tries += 1
    return brentq(f, R_lo, R_hi, xtol=1e-6)


def main():
    print("=== Step 1: anchor HA branch parameters at POD1 ===")
    x0 = np.array([0.3, 80.0])
    opt = minimize(anchor_objective, x0, method="Nelder-Mead",
                   options={"xatol": 1e-6, "fatol": 1e-10, "maxiter": 2000})
    R_HA_pod1, dp_inlet_fit = opt.x
    print(f"Fitted R_HA(POD1)={R_HA_pod1:.4f}, dp_inlet={dp_inlet_fit:.2f}, "
          f"objective={opt.fun:.3e}, converged={opt.success}")

    pod1_params = build_params(R_HA_pod1, dp_inlet_fit, MEASURED["POD1"]["PVV"])
    pod1_res = simulate(pod1_params)
    print(f"POD1 simulated: PSV_HA={pod1_res['PSV_HA']:.2f} "
          f"(measured {MEASURED['POD1']['PSV_HA']}), "
          f"RI_HA={pod1_res['RI_HA']:.3f} (measured {MEASURED['POD1']['RI_HA']}), "
          f"mean_Q_HA={pod1_res['mean_Q_HA']:.3f}")

    v_pv_pod1 = MEASURED["POD1"]["PVV"]
    mean_Q_HA_pod1 = pod1_res["mean_Q_HA"]

    print("\n=== Step 2: HABR-predicted trajectory, POD7/14/30 ===")
    print("(R_HA at each time point is solved so that the model's mean HA "
          "flow matches the HABR quadratic's prediction; PSV_HA and RI_HA "
          "are NOT fit -- they are the model's falsifiable output.)")

    rows = []
    rows.append(("POD1", MEASURED["POD1"]["PSV_HA"], pod1_res["PSV_HA"],
                 MEASURED["POD1"]["RI_HA"], pod1_res["RI_HA"], 0.0, "(anchor)"))

    # null-model comparison: what if R_HA never changed from POD1 at all?
    null_rows = []

    for label in ("POD7", "POD14", "POD30"):
        v_pv_t = MEASURED[label]["PVV"]
        # source-script sign convention: change = (old-new)/old*100, i.e.
        # POSITIVE means a DECREASE relative to the POD1 reference.
        change_Ipv = (v_pv_pod1 - v_pv_t) / v_pv_pod1 * 100.0
        change_Iha_pred = habr_percent_change(change_Ipv)
        target_mean_Q = mean_Q_HA_pod1 * (1.0 - change_Iha_pred / 100.0)

        R_HA_t = find_R_HA_for_target_flow(
            target_mean_Q, dp_inlet_fit, v_pv_t,
            R_lo=0.3 * R_HA_pod1, R_hi=3.0 * R_HA_pod1,
        )
        params_t = build_params(R_HA_t, dp_inlet_fit, v_pv_t)
        res_t = simulate(params_t)

        rows.append((label, MEASURED[label]["PSV_HA"], res_t["PSV_HA"],
                     MEASURED[label]["RI_HA"], res_t["RI_HA"],
                     -change_Ipv, f"R_HA={R_HA_t:.3f}"))

        # null model: same R_HA as POD1, only v_pv (sinusoid input) changes
        null_params = build_params(R_HA_pod1, dp_inlet_fit, v_pv_t)
        null_res = simulate(null_params)
        null_rows.append((label, null_res["PSV_HA"], null_res["RI_HA"]))

    print(f"\n{'Time':<6} {'PSV meas':>9} {'PSV sim':>8} {'RI meas':>8} "
          f"{'RI sim':>7} {'%dQ_pv':>8}  note")
    for label, psv_m, psv_s, ri_m, ri_s, dqpv, note in rows:
        print(f"{label:<6} {psv_m:>9.2f} {psv_s:>8.2f} {ri_m:>8.3f} "
              f"{ri_s:>7.3f} {dqpv:>8.2f}  {note}")

    print("\n=== Null-model comparison (R_HA fixed at POD1 value, HABR OFF) ===")
    print(f"{'Time':<6} {'PSV null':>9} {'RI null':>8}   (vs measured PSV/RI above)")
    for label, psv_n, ri_n in null_rows:
        m = MEASURED[label]
        print(f"{label:<6} {psv_n:>9.2f} {ri_n:>8.3f}   "
              f"(measured {m['PSV_HA']:.2f} / {m['RI_HA']:.3f})")

    print("\n=== Fraction of the measured PSV_HA decline reproduced by HABR alone ===")
    for (label, psv_m, psv_s, ri_m, ri_s, dqpv, note), (_, psv_n, ri_n) in zip(rows[1:], null_rows):
        measured_decline = rows[0][1] - psv_m
        null_decline = rows[0][1] - psv_n
        habr_decline = rows[0][1] - psv_s
        frac = habr_decline / measured_decline * 100.0 if measured_decline else float("nan")
        print(f"{label:<6} measured drop={measured_decline:.2f} cm/s  "
              f"HABR-model drop={habr_decline:.2f} cm/s ({frac:.1f}% of measured)  "
              f"[null-model drift alone: {null_decline:.2f} cm/s]")

    import csv
    with open("ldlt_habr_prediction_results.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time", "PSV_HA_measured", "PSV_HA_simulated",
                    "RI_HA_measured", "RI_HA_simulated", "pct_change_PVV_vs_POD1",
                    "note"])
        for row in rows:
            w.writerow(row)
    with open("ldlt_habr_null_model_results.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time", "PSV_HA_null_no_habr", "RI_HA_null_no_habr"])
        for row in null_rows:
            w.writerow(row)

    print("\nSaved: ldlt_habr_prediction_results.csv, "
          "ldlt_habr_null_model_results.csv")


if __name__ == "__main__":
    main()
