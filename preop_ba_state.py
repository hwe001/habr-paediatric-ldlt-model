"""
Pre-operative biliary-atresia (BA) state of the pi-filter model, and the
transplant-step transition (pre-op -> POD1) as a validation scenario.

Purpose (revision_plan.md Section 3.5 / parameter_table.md Section 7): the
clinical dataset (Chen et al. 2022) reports the cirrhotic pre-operative
state (PSV 73.32 cm/s, RI 0.77, PVV 16.88 cm/s) as well as the post-LDLT
time-course, so the model can be calibrated at PRE-op and asked whether the
transplant step -- the portal-flow surge produced by replacing the
high-resistance cirrhotic bed with the low-resistance graft -- reproduces
the measured early post-operative arterial changes. This turns "the model
is anchored at POD1" into "the model spans the transplant event itself".

What is calibrated at pre-op, and what is absorbed where (flagged, per the
compendium Section 18 philosophy):
- The HA branch (Rs_HA, L_HA, P_HA_amp) is fit to the pre-op PSV/RI targets
  (3 unknowns / 2 targets -> non-unique; an admissible family is scanned
  below, mirroring reviewer_round3_identifiability.py).
- The cirrhotic bed's elevated downstream resistance is NOT separately
  parameterised: simulate_ha_branch uses the healthy-graft downstream
  parameters (BASE_PARAMS), so the cirrhotic-bed effect is absorbed into
  the effective arterial parameters of the pre-op fit. Consequence: the
  model can attribute the PSV change at the transplant step, but the
  measured RI drop (0.77 -> 0.61) -- which per compendium Section 3.2 is
  mostly the healthy graft's low downstream resistance -- is NOT
  reproducible with a fixed downstream. That limitation is structural and
  stated in the output; it is the same attribution gap the source clinical
  paper leaves open.

Sign convention note (carried verbatim from the canonical model,
ldlt_habr_consistent_units.py lines 199-206, NOT re-interpreted here):
    change_Ipv = (Q_ref - Q_new) / Q_ref * 100
    target_mean_Q = baseline_mean_Q * (1 - habr_percent_change(change_Ipv)/100)
Applied to the POD1->POD30 window (Q declining) this yields a positive
change_Ipv and a target arterial flow BELOW baseline -- the convention the
manuscript's results build on. Applied to the transplant step (portal flow
roughly DOUBLES, so change_Ipv < 0) the same convention yields an arterial
target flow ABOVE baseline. The scenarios below report the numbers under
the canonical convention as-is; the direction relative to the measured
decline is stated plainly so the authors can judge the physiological
reading.
"""

import numpy as np
from scipy.optimize import minimize

from ldlt_habr_consistent_units import (
    MEASURED, q_pv_flow, habr_percent_change, simulate_ha_branch,
    find_Rs_HA_for_target_flow, PV_DIAMETER_POD1_CM,
)

PREOP = MEASURED["Pre-op"]
POD1 = MEASURED["POD1"]

# Forward-Euler stability pre-check: the HA-branch ODE is integrated at
# dt = period/steps_per_cycle with dQ = (... - Rs*Q ...)/L, so any candidate
# with Rs*dt/L > ~1.8 diverges (overflow, no early convergence break) and
# only burns wall-clock time before returning the 1e6 penalty. Rejecting it
# up front keeps the optimisation inside the numerically stable region
# without altering the canonical model.
DT_HA = (60.0 / 130.0) / 400.0  # matches simulate_ha_branch defaults


def _euler_stable(Rs_HA, L_HA):
    return Rs_HA * DT_HA / L_HA <= 1.8


def q_pv_preop():
    """Chen et al.'s formula with the cohort's own pre-op PV diameter."""
    return q_pv_flow(PREOP["PVV"], diameter_cm=PREOP["PV_DIAMETER_CM"])


def preop_residual(x, Q_PV_pre):
    """Relative error of (PSV, RI) against the pre-op targets; 1e6 penalty
    for nonphysical parameters or non-convergence, mirroring
    anchor_objective in the canonical model."""
    Rs_HA, L_HA, P_HA_amp = x
    if Rs_HA <= 0 or L_HA <= 0 or P_HA_amp <= 0:
        return 1e6
    if not _euler_stable(Rs_HA, L_HA):
        return 1e6
    res = simulate_ha_branch(Rs_HA, P_HA_amp, Q_PV_pre, L_HA)
    if not res["converged"]:
        return 1e6
    err_psv = (res["PSV_HA"] - PREOP["PSV_HA"]) / PREOP["PSV_HA"]
    err_ri = (res["RI_HA"] - PREOP["RI_HA"]) / PREOP["RI_HA"]
    return err_psv**2 + err_ri**2


def calibrate_preop_point(Q_PV_pre):
    """3 unknowns / 2 targets, multi-start Nelder-Mead (same structure as
    the POD1 anchor; several starts because the family is non-unique and
    the naive start can land on a penalty wall)."""
    starts = [
        np.array([150.0, 5.0, 30.0]),    # the POD1 anchor's start
        np.array([70.0, 0.2, 30.0]),
        np.array([100.0, 0.1, 20.0]),
    ]
    best = None
    for x0 in starts:
        opt = minimize(preop_residual, x0, args=(Q_PV_pre,),
                       method="Nelder-Mead",
                       options={"xatol": 1e-9, "fatol": 1e-14, "maxiter": 2000})
        if best is None or opt.fun < best.fun:
            best = opt
    return best


def fit_Rs_L_for_preop_amp(P_HA_amp, Q_PV_pre, x0=(100.0, 0.1)):
    """For a FIXED P_HA_amp, solve (Rs_HA, L_HA) to hit both pre-op targets
    exactly -- the round-3 family construction applied to the pre-op state."""
    def obj(y):
        Rs_HA, L_HA = y
        if Rs_HA <= 0 or L_HA <= 0:
            return 1e6
        if not _euler_stable(Rs_HA, L_HA):
            return 1e6
        res = simulate_ha_branch(Rs_HA, P_HA_amp, Q_PV_pre, L_HA)
        if not res["converged"]:
            return 1e6
        err_psv = (res["PSV_HA"] - PREOP["PSV_HA"]) / PREOP["PSV_HA"]
        err_ri = (res["RI_HA"] - PREOP["RI_HA"]) / PREOP["RI_HA"]
        return err_psv**2 + err_ri**2

    opt = minimize(obj, x0, method="Nelder-Mead",
                   options={"xatol": 1e-10, "fatol": 1e-16, "maxiter": 2000})
    Rs_HA, L_HA = opt.x
    ok = opt.fun < 1e-8
    return Rs_HA, L_HA, ok, opt.fun


def scan_preop_family(Q_PV_pre, amps=(15, 20, 30, 40, 60, 80)):
    """Admissible pre-op family: P_HA_amp values for which (Rs_HA, L_HA)
    can be solved to hit both pre-op targets exactly."""
    family = []
    for amp in amps:
        Rs_HA, L_HA, ok, fun = fit_Rs_L_for_preop_amp(float(amp), Q_PV_pre)
        if ok:
            family.append((float(amp), Rs_HA, L_HA))
    return family


def transition_scenario(Rs_HA, L_HA, P_HA_amp, Q_PV_new, apply_habr,
                        mean_Q_HA_pre):
    """Run the transplant step from the pre-op fitted state: swap the
    prescribed portal flow to its POD1 value; optionally apply the HABR
    resistance update under the canonical convention."""
    if apply_habr:
        change_Ipv = (q_pv_preop() - Q_PV_new) / q_pv_preop() * 100.0
        change_Iha = habr_percent_change(change_Ipv)
        target_Q = mean_Q_HA_pre * (1.0 - change_Iha / 100.0)
        Rs_HA = find_Rs_HA_for_target_flow(
            target_Q, P_HA_amp, Q_PV_new, L_HA,
            Rs_lo=0.02 * Rs_HA, Rs_hi=1.0 * Rs_HA)
    res = simulate_ha_branch(Rs_HA, P_HA_amp, Q_PV_new, L_HA)
    return res, Rs_HA


if __name__ == "__main__":
    Q_PV_pre = q_pv_preop()
    Q_PV_pod1 = q_pv_flow(POD1["PVV"], diameter_cm=PV_DIAMETER_POD1_CM)

    print("=== Portal-flow conversion (Chen et al. formula) ===")
    print(f"Q_PV(pre-op)  = {Q_PV_pre:.2f} mL/min  (PVV 16.88 cm/s, D 0.44 cm)")
    print(f"Q_PV(POD1)    = {Q_PV_pod1:.2f} mL/min  (PVV 30.80 cm/s, D 0.46 cm)")
    print(f"Portal surge at transplant: x{Q_PV_pod1 / Q_PV_pre:.3f} "
          f"(the 'portal-flow doubling')\n")

    print("=== Pre-op calibration (3 unknowns / 2 targets, multi-start) ===")
    best = calibrate_preop_point(Q_PV_pre)
    Rs_pre, L_pre, amp_pre = best.x
    res_pre = simulate_ha_branch(Rs_pre, amp_pre, Q_PV_pre, L_pre)
    print(f"Rs_HA={Rs_pre:.4f}, L_HA={L_pre:.5f}, P_HA_amp={amp_pre:.2f} mmHg "
          f"(residual {best.fun:.3e})")
    print(f"Pre-op simulated: PSV={res_pre['PSV_HA']:.2f} (target 73.32), "
          f"RI={res_pre['RI_HA']:.3f} (target 0.77), "
          f"mean_Q_HA={res_pre['mean_Q_HA_mLmin']:.2f} mL/min")
    if best.fun > 1e-6:
        print("WARNING: the pre-op targets were NOT reached exactly -- see "
              "the admissible-family scan and the structural note below.\n")

    print("\n=== Admissible pre-op family (P_HA_amp scan) ===")
    family = scan_preop_family(Q_PV_pre)
    if family:
        amps = [f[0] for f in family]
        print(f"{len(family)} amplitudes admit an exact fit: "
              f"P_HA_amp in [{min(amps):.0f}, {max(amps):.0f}] mmHg")
        for amp, Rs_f, L_f in family:
            print(f"  amp={amp:5.1f}  Rs_HA={Rs_f:9.4f}  L_HA={L_f:.5f}")
    else:
        print("NO amplitude admits an exact fit to BOTH pre-op targets -- "
              "the healthy-graft downstream cannot produce RI=0.77 "
              "(structural, see module docstring).")

    print("\n=== Transplant step: pre-op -> POD1 scenarios ===")
    decline_measured = PREOP["PSV_HA"] - POD1["PSV_HA"]
    print(f"Measured PSV decline: {PREOP['PSV_HA']:.2f} -> {POD1['PSV_HA']:.2f} "
          f"cm/s ({-100 * (POD1['PSV_HA'] - PREOP['PSV_HA']) / PREOP['PSV_HA']:.1f}%)")

    change_Ipv = (Q_PV_pre - Q_PV_pod1) / Q_PV_pre * 100.0
    change_Iha = habr_percent_change(change_Ipv)
    print(f"\nHABR law, canonical convention: change_Ipv = {change_Ipv:.1f}% "
          f"-> change_Iha = {change_Iha:.1f}%")
    print(f"  -> implied target mean flow = pre-op mean x "
          f"{1 - change_Iha / 100.0:.3f}")

    res_null, _ = transition_scenario(Rs_pre, L_pre, amp_pre, Q_PV_pod1,
                                      apply_habr=False,
                                      mean_Q_HA_pre=res_pre["mean_Q_HA_mLmin"])
    frac_null = (PREOP["PSV_HA"] - res_null["PSV_HA"]) / decline_measured * 100.0
    print(f"\nS1 null (Rs_HA frozen at pre-op): "
          f"PSV={res_null['PSV_HA']:.2f} cm/s, "
          f"RI={res_null['RI_HA']:.3f} -> explains {frac_null:.1f}% of the "
          f"measured decline")

    res_habr, Rs_new = transition_scenario(
        Rs_pre, L_pre, amp_pre, Q_PV_pod1, apply_habr=True,
        mean_Q_HA_pre=res_pre["mean_Q_HA_mLmin"])
    frac_habr = (PREOP["PSV_HA"] - res_habr["PSV_HA"]) / decline_measured * 100.0
    print(f"S2 HABR applied (canonical convention): "
          f"PSV={res_habr['PSV_HA']:.2f} cm/s, RI={res_habr['RI_HA']:.3f} "
          f"(Rs_HA {Rs_pre:.3f} -> {Rs_new:.3f}) -> "
          f"{frac_habr:.1f}% of the measured decline")

    print("\n=== Structural note (unchanged by calibration choice) ===")
    print("The measured RI drop (0.77 -> 0.61) requires the downstream bed "
          "resistance to fall -- i.e. the healthy graft replacing the\n"
          "cirrhotic bed. With the downstream held at the healthy-graft "
          "parameters (BASE_PARAMS) throughout, the pre-op fit absorbs the\n"
          "cirrhotic bed into the effective arterial parameters and the "
          "transition scenarios cannot reproduce the RI drop. The PSV\n"
          "attribution above is therefore conditional on that structural "
          "choice; a cirrhotic-bed parameter (e.g. a resistance scale on\n"
          "Rs_HV/Rp_sinus at pre-op) is the natural next extension.")
