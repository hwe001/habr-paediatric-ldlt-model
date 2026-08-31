"""
New quantitative analyses requested by round-1 reviewer feedback:
1. Welch's t-test (from published summary statistics only -- unpaired,
   conservative) for whether RI_HA at POD7/14/30 differ.
2. SEM-propagated uncertainty ranges for "% of measured PSV_HA decline
   reproduced by HABR," instead of single-point percentages.
3. A sensitivity sweep varying assumed portal-vein diameter growth from
   POD1 to POD30 (0% to 40%), since holding diameter constant at the POD1
   value is the same unmeasured-quantity assumption as the paper's own
   proposed residual mechanism (vessel-calibre growth).
"""

import numpy as np
from scipy import stats

from ldlt_habr_on_pi_filter import (
    MEASURED, BASE_PARAMS, habr_percent_change, simulate_ha_branch,
    find_Rs_HA_for_target_flow, anchor_objective, PV_VELOCITY_TO_FLOW_FACTOR,
)
from scipy.optimize import minimize

N = 41  # cohort size, Chen et al. 2022

print("=" * 70)
print("1. Welch's t-test on RI_HA, from published summary statistics")
print("   (unpaired -- conservative; the real cohort is repeated-measures")
print("   on the same 41 patients, which a paired test would have more")
print("   power to detect small differences with; not available here)")
print("=" * 70)

ri = {k: (v["RI_HA"], MEASURED[k].get("RI_HA_SD")) for k, v in MEASURED.items()}
RI_SD = {"POD1": 0.05, "POD7": 0.03, "POD14": 0.05, "POD30": 0.01}

for a, b in [("POD1", "POD7"), ("POD7", "POD14"), ("POD14", "POD30"),
             ("POD7", "POD30")]:
    m1, s1 = MEASURED[a]["RI_HA"], RI_SD[a]
    m2, s2 = MEASURED[b]["RI_HA"], RI_SD[b]
    se = np.sqrt(s1**2 / N + s2**2 / N)
    t = (m1 - m2) / se
    # Welch-Satterthwaite df
    df = (s1**2 / N + s2**2 / N)**2 / ((s1**2 / N)**2 / (N - 1) + (s2**2 / N)**2 / (N - 1))
    p = 2 * (1 - stats.t.cdf(abs(t), df))
    ci_half = stats.t.ppf(0.975, df) * se
    print(f"{a} ({m1:.2f}) vs {b} ({m2:.2f}): diff={m1-m2:+.3f}, SE={se:.4f}, "
          f"95% CI of diff=[{(m1-m2)-ci_half:+.3f}, {(m1-m2)+ci_half:+.3f}], "
          f"t={t:.2f}, df={df:.0f}, p={p:.3f}")

print()
print("=" * 70)
print("2. SEM-propagated uncertainty range for '% of measured PSV_HA "
      "decline reproduced by HABR' (continuous-application scenario)")
print("=" * 70)

PSV_SD = {"POD1": 16.02, "POD7": 10.05, "POD14": 10.38, "POD30": 7.63}
psv_model_continuous = {"POD1": 53.10, "POD7": 52.29, "POD14": 50.48, "POD30": 48.63}
psv_model_acute_frozen = {"POD1": 53.10, "POD7": 52.29, "POD14": 52.35, "POD30": 52.42}

rng = np.random.default_rng(0)
N_MC = 200000
for scenario, psv_model in [("continuous", psv_model_continuous),
                             ("acute-then-frozen", psv_model_acute_frozen)]:
    print(f"\n-- {scenario} scenario --")
    for label in ("POD7", "POD14", "POD30"):
        sem1 = PSV_SD["POD1"] / np.sqrt(N)
        sem2 = PSV_SD[label] / np.sqrt(N)
        pod1_draw = rng.normal(MEASURED["POD1"]["PSV_HA"], sem1, N_MC)
        t_draw = rng.normal(MEASURED[label]["PSV_HA"], sem2, N_MC)
        measured_decline = pod1_draw - t_draw
        model_decline = psv_model["POD1"] - psv_model[label]
        frac = model_decline / measured_decline * 100.0
        frac = frac[np.isfinite(frac)]
        lo, hi = np.percentile(frac, [2.5, 97.5])
        point = model_decline / (MEASURED["POD1"]["PSV_HA"] - MEASURED[label]["PSV_HA"]) * 100.0
        print(f"{label}: point estimate ~{point:.0f}%, 95% CI (from POD1/"
              f"{label} mean SEM only, not full patient variability) "
              f"[{lo:.0f}%, {hi:.0f}%]")

print()
print("=" * 70)
print("3. Sensitivity sweep: assumed portal-vein diameter growth POD1->POD30")
print("=" * 70)
print("(Real diameter only reported at pre-op/POD1 in Chen et al. 2022; "
      "POD7-30 diameter is unmeasured -- this sweep tests how much the "
      "'held constant' assumption matters, using the same unmeasured "
      "quantity as the paper's own proposed residual mechanism.)")

D_POD1 = 0.46

def q_pv_with_diameter(pvv, diameter_cm):
    r = diameter_cm / 2.0
    return np.pi * r**2 * PV_VELOCITY_TO_FLOW_FACTOR * pvv * 60.0

x0 = np.array([BASE_PARAMS["Rs_HA"], BASE_PARAMS["L_HA"]])
Q_PV_pod1 = q_pv_with_diameter(MEASURED["POD1"]["PVV"], D_POD1)
opt = minimize(anchor_objective, x0, args=(Q_PV_pod1, 15.1), method="Nelder-Mead",
               options={"xatol": 1e-8, "fatol": 1e-12, "maxiter": 5000})
Rs_HA_pod1, L_HA_pod1 = opt.x
pod1_res = simulate_ha_branch(Rs_HA_pod1, 15.1, Q_PV_pod1, L_HA=L_HA_pod1)
mean_Q_HA_pod1 = pod1_res["mean_Q_HA"]

print(f"\n{'Diam. growth by POD30':>22} {'PSV POD7':>9} {'PSV POD14':>10} "
      f"{'PSV POD30':>10} {'% explained POD30':>18}")
for growth_pct in (0, 10, 20, 30, 40):
    growth_frac_pod30 = growth_pct / 100.0
    # linear interpolation of diameter growth across POD7/14/30
    diam_at = {
        "POD7": D_POD1 * (1 + growth_frac_pod30 * (7 / 30)),
        "POD14": D_POD1 * (1 + growth_frac_pod30 * (14 / 30)),
        "POD30": D_POD1 * (1 + growth_frac_pod30 * (30 / 30)),
    }
    psv_out = {}
    for label in ("POD7", "POD14", "POD30"):
        v_pv_t = MEASURED[label]["PVV"]
        Q_PV_t = q_pv_with_diameter(v_pv_t, diam_at[label])
        change_Ipv = (Q_PV_pod1 - Q_PV_t) / Q_PV_pod1 * 100.0
        change_Iha = habr_percent_change(change_Ipv)
        target_Q = mean_Q_HA_pod1 * (1.0 - change_Iha / 100.0)
        Rs_HA_t = find_Rs_HA_for_target_flow(
            target_Q, 15.1, Q_PV_t, L_HA_pod1,
            Rs_lo=0.3 * Rs_HA_pod1, Rs_hi=3.0 * Rs_HA_pod1)
        res = simulate_ha_branch(Rs_HA_t, 15.1, Q_PV_t, L_HA=L_HA_pod1)
        psv_out[label] = res["PSV_HA"]
    measured_decline_30 = MEASURED["POD1"]["PSV_HA"] - MEASURED["POD30"]["PSV_HA"]
    model_decline_30 = pod1_res["PSV_HA"] - psv_out["POD30"]
    frac30 = model_decline_30 / measured_decline_30 * 100.0
    print(f"{growth_pct:>21}% {psv_out['POD7']:>9.2f} {psv_out['POD14']:>10.2f} "
          f"{psv_out['POD30']:>10.2f} {frac30:>17.1f}%")

print("\nNote: Q_PV(t) here uses the flow formula exactly as given by Chen "
      "et al. (pi*r^2*0.57*PVV*60); this is NOT divided by any graft-mass "
      "term despite the paper's own 'mL/min/100g' label -- the formula as "
      "written and reproduced here yields an absolute mL/min-scale "
      "quantity. This ambiguity (present in the source paper, not "
      "introduced here) does not by itself invalidate the sensitivity "
      "sweep above, since only the PERCENT CHANGE in this quantity feeds "
      "the HABR relationship (invariant to a fixed, if unresolved, scaling "
      "convention) -- but it does mean this quantity's absolute magnitude, "
      "as used directly in the sinusoidal node's mass balance alongside "
      "Q_HA (whose scale is separately, directly calibrated to Doppler "
      "velocity units), is not on a common physical footing. See the "
      "manuscript's Methods and Limitations for the sensitivity check on "
      "this specific coupling.")
