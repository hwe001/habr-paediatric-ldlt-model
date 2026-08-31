"""
Corrected HABR test: HABR is an acute (minutes-to-hours, adenosine-washout)
mechanism, not a slowly-continuing one. It should have fully equilibrated
long before a week has passed, and should NOT be invoked as an ongoing,
actively-readjusting mechanism throughout the following three weeks.

This is directly supported by the real data: RI_HA is already flat
(0.59, 0.59, 0.59) from POD7 through POD30, while PSV_HA keeps declining.
Since RI is the ratio most directly sensitive to a resistance change, its
flatness after POD7 means whatever resistance adjustment HABR was going to
make has already happened by POD7 -- continuing to apply the HABR quadratic
at POD14/30 (as ldlt_habr_on_pi_filter.py did) inappropriately credits an
acute mechanism for a chronic, resistance-flat decline.

Corrected structure:
- POD1: calibration anchor (Rs_HA, L_HA fit to real measured PSV_HA/RI_HA),
  unchanged from before.
- POD7: the HABR quadratic is applied ONCE, using the real POD1->POD7
  portal-flow change -- this is the one window with both a real portal
  change and a real RI change, so it is the legitimate acute-response
  window.
- POD14, POD30: Rs_HA is FROZEN at its POD7-consistent value (no further
  HABR-driven change). Q_PV(t) is still updated to each time point's real
  measured value, so the circuit's own passive coupling through the shared
  sinusoidal node is still allowed to act -- this isolates what "HABR
  already finished, only passive downstream coupling remains" predicts,
  as distinct from continuing to actively invoke HABR.

Compares four scenarios: real measured data; the old (superseded)
continuously-reapplied-HABR model; this corrected acute-then-frozen model;
and the pure null model (Rs_HA frozen at POD1, HABR never applied at all).
"""

import csv

import numpy as np

from ldlt_habr_on_pi_filter import (
    MEASURED, BASE_PARAMS, habr_percent_change, simulate_ha_branch,
    find_Rs_HA_for_target_flow, real_pvf_mL_min_per_100g,
    anchor_objective,
)
from scipy.optimize import minimize

P_HA_amp_fixed = 15.1  # TARGETS["P_HA_src_amp"], real literature value


def main():
    v_pv_pod1 = MEASURED["POD1"]["PVV"]
    Q_PV_pod1 = real_pvf_mL_min_per_100g(v_pv_pod1)

    print("=== Step 1: anchor at POD1 (unchanged) ===")
    x0 = np.array([BASE_PARAMS["Rs_HA"], BASE_PARAMS["L_HA"]])
    opt = minimize(anchor_objective, x0, args=(Q_PV_pod1, P_HA_amp_fixed),
                   method="Nelder-Mead",
                   options={"xatol": 1e-8, "fatol": 1e-12, "maxiter": 5000})
    Rs_HA_pod1, L_HA_pod1 = opt.x
    pod1_res = simulate_ha_branch(Rs_HA_pod1, P_HA_amp_fixed, Q_PV_pod1, L_HA=L_HA_pod1)
    print(f"Rs_HA(POD1)={Rs_HA_pod1:.4f}, L_HA={L_HA_pod1:.4f}")
    print(f"POD1 simulated PSV_HA={pod1_res['PSV_HA']:.2f}, RI_HA={pod1_res['RI_HA']:.3f}")
    mean_Q_HA_pod1 = pod1_res["mean_Q_HA"]

    print("\n=== Step 2: HABR applied ONCE, across POD1->POD7 (the one "
          "acute, resistance-changing window; RI still moves here) ===")
    v_pv_pod7 = MEASURED["POD7"]["PVV"]
    Q_PV_pod7 = real_pvf_mL_min_per_100g(v_pv_pod7)
    change_Ipv_pod7 = (v_pv_pod1 - v_pv_pod7) / v_pv_pod1 * 100.0
    change_Iha_pod7 = habr_percent_change(change_Ipv_pod7)
    target_Q_pod7 = mean_Q_HA_pod1 * (1.0 - change_Iha_pod7 / 100.0)
    Rs_HA_pod7 = find_Rs_HA_for_target_flow(
        target_Q_pod7, P_HA_amp_fixed, Q_PV_pod7, L_HA_pod1,
        Rs_lo=0.3 * Rs_HA_pod1, Rs_hi=3.0 * Rs_HA_pod1)
    pod7_res = simulate_ha_branch(Rs_HA_pod7, P_HA_amp_fixed, Q_PV_pod7, L_HA=L_HA_pod1)
    print(f"Rs_HA(POD7)={Rs_HA_pod7:.4f} (HABR-derived, from {change_Ipv_pod7:.2f}% "
          f"portal decrease)")
    print(f"POD7 simulated (acute-then-frozen == old continuous model here, "
          f"they agree by construction): PSV_HA={pod7_res['PSV_HA']:.2f}, "
          f"RI_HA={pod7_res['RI_HA']:.3f}")

    print("\n=== Step 3: POD14, POD30 -- Rs_HA FROZEN at Rs_HA(POD7); only "
          "Q_PV(t) (passive coupling) still updates to real measured values ===")
    rows = []
    for label in ("POD1", "POD7", "POD14", "POD30"):
        v_pv_t = MEASURED[label]["PVV"]
        Q_PV_t = real_pvf_mL_min_per_100g(v_pv_t)
        if label == "POD1":
            res = pod1_res
        elif label == "POD7":
            res = pod7_res
        else:
            # frozen resistance, passive coupling only
            res = simulate_ha_branch(Rs_HA_pod7, P_HA_amp_fixed, Q_PV_t, L_HA=L_HA_pod1)
        rows.append((label, MEASURED[label]["PSV_HA"], res["PSV_HA"],
                     MEASURED[label]["RI_HA"], res["RI_HA"]))
        print(f"{label}: measured PSV={MEASURED[label]['PSV_HA']:.2f} "
              f"RI={MEASURED[label]['RI_HA']:.3f}  |  acute-then-frozen model "
              f"PSV={res['PSV_HA']:.2f} RI={res['RI_HA']:.3f}")

    print("\n=== Comparison: old continuously-reapplied-HABR model vs. this "
          "corrected acute-then-frozen model vs. pure null (no HABR at all) ===")
    with open("ldlt_habr_pi_filter_prediction_results.csv") as f:
        old_rows = {r["time"]: r for r in csv.DictReader(f)}
    with open("ldlt_habr_pi_filter_null_model_results.csv") as f:
        old_null = {r["time"]: r for r in csv.DictReader(f)}

    print(f"{'Time':<6} {'measured':>9} {'old cont.':>10} {'acute+frozen':>13} "
          f"{'null (no HABR)':>15}")
    psv0 = rows[0][2]
    for label, psv_m, psv_s, ri_m, ri_s in rows:
        old_psv = float(old_rows[label]["PSV_HA_simulated"]) if label in old_rows else psv0
        null_psv = float(old_null[label]["PSV_HA_null_no_habr"]) if label in old_null else psv0
        print(f"{label:<6} {psv_m:>9.2f} {old_psv:>10.2f} {psv_s:>13.2f} {null_psv:>15.2f}")

    print("\n=== Fraction of measured PSV_HA decline (from POD1) attributed to "
          "HABR under each model ===")
    for label, psv_m, psv_s, ri_m, ri_s in rows[1:]:
        measured_decline = MEASURED["POD1"]["PSV_HA"] - psv_m
        acute_frozen_decline = psv0 - psv_s
        frac = acute_frozen_decline / measured_decline * 100.0
        print(f"{label:<6} measured drop={measured_decline:.2f}  "
              f"acute+frozen model drop={acute_frozen_decline:.2f} "
              f"({frac:.1f}% of measured; remainder is 100% non-HABR "
              f"in this framing, vs. partially HABR-credited before)")

    with open("ldlt_habr_acute_then_frozen_results.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time", "PSV_HA_measured", "PSV_HA_acute_then_frozen",
                     "RI_HA_measured", "RI_HA_acute_then_frozen"])
        for row in rows:
            w.writerow(row)
    print("\nSaved: ldlt_habr_acute_then_frozen_results.csv")


if __name__ == "__main__":
    main()
