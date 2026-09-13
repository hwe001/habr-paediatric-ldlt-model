"""
Cirrhotic-bed parameter for the pre-operative BA state, and the
transplant-step attribution analysis built on it.

Extension of preop_ba_state.py (compendium Section 22), which flagged the
structural limitation: with the downstream held at healthy-graft parameters,
the pre-op fit absorbs the cirrhotic bed into the effective arterial
parameters and the RI drop (0.77 -> 0.61) is unreachable by any transition
scenario. This script makes the bed explicit:

    k_bed >= 1 scales Rs_HV (the sinusoid -> hepatic-vein series resistance,
    i.e. the intrahepatic outflow path that cirrhosis obstructs) at pre-op.
    At the transplant step the graft replaces the bed -> k_bed drops to 1
    (the healthy BASE_PARAMS calibration state). Rp_hv_out (large-vein
    outflow) and Rp_sinus (the pi-filter's non-physiological topology leak)
    are deliberately NOT scaled.

Analysis structure (mirrors the round-3 methodology -- scan the structural
parameter, solve the rest exactly, propagate the family):

1. Admissible pre-op family over a (k_bed, P_HA_amp) grid: for each cell,
   (Rs_HA, L_HA) is solved to hit the pre-op targets (PSV 73.32, RI 0.77)
   exactly. The k_bed=1 column must reproduce the Section 22 fit (built-in
   sanity check).
2. For every family member, the transplant step (portal flow x1.994, bed
   k_bed -> 1) is run under four arms:
     - "null": Rs_HA frozen at its pre-op value (no arterial response);
     - "required": Rs_HA best-fit to the MEASURED POD1 state (PSV 53.10,
       RI 0.61) -- sign-agnostic and convention-free; its Rs_new/Rs_pre
       ratio is the arterial response the data actually demands;
     - "habr_canonical": the canonical convention's prediction (target
       flow x(1 - changeIha/100) with changeIpv = -99.4% -> dilatation);
     - "habr_classical": the classical buffer direction for a portal-flow
       INCREASE (compendium Section 3.2, as the source clinical paper
       describes it): same quadratic magnitude, arterial flow x(1 - 47.6%)
       -> constriction.
   The attribution statement is the comparison of the "required" ratio
   distribution against the two HABR predictions.

Caveats carried from Section 22: the cirrhotic bed is represented ONLY as a
resistance scale (fibrotic stiffness -- a C_sinus reduction -- is not
modelled); portal flow stays prescribed from the measured PVV; the 57.5
mmHg mean arterial source pressure is shared pre/post; no independent data
constrains k_bed, so its identified value is conditional on this circuit.
"""

import numpy as np
from scipy.optimize import minimize

from ldlt_habr_consistent_units import (
    MEASURED, q_pv_flow, habr_percent_change, simulate_ha_branch,
    find_Rs_HA_for_target_flow, BASE_PARAMS, PV_DIAMETER_POD1_CM,
)
from preop_ba_state import q_pv_preop, PREOP, POD1, _euler_stable

K_BED_GRID = (1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0)
AMP_GRID = (15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 60.0)


def params_preop(k_bed):
    """Healthy-graft parameters with the intrahepatic outflow resistance
    scaled by the cirrhotic-bed factor."""
    p = dict(BASE_PARAMS)
    p["Rs_HV"] = k_bed * p["Rs_HV"]
    return p


def fit_Rs_L_preop(k_bed, amp, Q_PV_pre):
    """Solve (Rs_HA, L_HA) to hit both pre-op targets exactly at this
    (k_bed, P_HA_amp) cell; also return the pre-op mean arterial flow."""
    def obj(y):
        Rs_HA, L_HA = y
        if Rs_HA <= 0 or L_HA <= 0 or not _euler_stable(Rs_HA, L_HA):
            return 1e6
        res = simulate_ha_branch(Rs_HA, amp, Q_PV_pre, L_HA,
                                 params=params_preop(k_bed))
        if not res["converged"]:
            return 1e6
        err_psv = (res["PSV_HA"] - PREOP["PSV_HA"]) / PREOP["PSV_HA"]
        err_ri = (res["RI_HA"] - PREOP["RI_HA"]) / PREOP["RI_HA"]
        return err_psv**2 + err_ri**2

    opt = minimize(obj, x0=(100.0, 0.5), method="Nelder-Mead",
                   options={"xatol": 1e-7, "fatol": 1e-12, "maxiter": 600})
    Rs_HA, L_HA = opt.x
    mean_Q = np.nan
    ok = opt.fun < 1e-8
    if ok:
        res = simulate_ha_branch(Rs_HA, amp, Q_PV_pre, L_HA,
                                 params=params_preop(k_bed))
        mean_Q = res["mean_Q_HA_mLmin"]
    return Rs_HA, L_HA, ok, mean_Q


def required_Rs_new(Rs_pre, L_HA_pre, amp, Q_PV_pod1):
    """Sign-agnostic arm: the arterial resistance at POD1 that best
    reproduces the MEASURED POD1 state (PSV 53.10, RI 0.61) given this
    family member's (L_HA, P_HA_amp) and the healthy graft downstream."""
    def obj(Rs_new):
        Rs_new = float(np.ravel(Rs_new)[0])  # NM passes a shape-(1,) array
        if Rs_new <= 0 or not _euler_stable(Rs_new, L_HA_pre):
            return 1e6
        res = simulate_ha_branch(Rs_new, amp, Q_PV_pod1, L_HA_pre)
        if not res["converged"]:
            return 1e6
        err_psv = (res["PSV_HA"] - POD1["PSV_HA"]) / POD1["PSV_HA"]
        err_ri = (res["RI_HA"] - POD1["RI_HA"]) / POD1["RI_HA"]
        return err_psv**2 + err_ri**2

    opt = minimize(obj, x0=(Rs_pre,), method="Nelder-Mead",
                   options={"xatol": 1e-7, "fatol": 1e-12, "maxiter": 600})
    Rs_new = float(opt.x[0])
    res = simulate_ha_branch(Rs_new, amp, Q_PV_pod1, L_HA_pre)
    return Rs_new, opt.fun, res


def habr_Rs_new(mean_Q_pre, L_HA_pre, amp, Q_PV_pod1, direction):
    """Quadratic-magnitude HABR prediction; direction='canonical' applies
    the canonical convention verbatim (dilatation for the portal surge),
    direction='classical' the same magnitude with the classical buffer sign
    for a portal-flow INCREASE (constriction)."""
    change_Ipv = (q_pv_preop() - Q_PV_pod1) / q_pv_preop() * 100.0
    change_Iha = habr_percent_change(change_Ipv)          # negative: -47.6%
    if direction == "canonical":
        target_Q = mean_Q_pre * (1.0 - change_Iha / 100.0)
    else:
        target_Q = mean_Q_pre * (1.0 + change_Iha / 100.0)
    Rs_lo, Rs_hi = 0.02 * 100.0, 20.0 * 100.0
    try:
        Rs_new = find_Rs_HA_for_target_flow(
            target_Q, amp, Q_PV_pod1, L_HA_pre, Rs_lo=Rs_lo, Rs_hi=Rs_hi)
    except ValueError:
        return None
    return Rs_new


if __name__ == "__main__":
    Q_PV_pre = q_pv_preop()
    Q_PV_pod1 = q_pv_flow(POD1["PVV"], diameter_cm=PV_DIAMETER_POD1_CM)
    decline_measured = PREOP["PSV_HA"] - POD1["PSV_HA"]

    print("=== Pre-op admissible family over (k_bed, P_HA_amp) ===")
    print("(k_bed = cirrhotic scale on Rs_HV at pre-op; transplant step "
          "sets k_bed -> 1)\n")
    cells = []
    for k_bed in K_BED_GRID:
        row = []
        for amp in AMP_GRID:
            Rs_HA, L_HA, ok, mean_Q = fit_Rs_L_preop(k_bed, amp, Q_PV_pre)
            if ok:
                row.append((amp, Rs_HA, L_HA, mean_Q))
        if row:
            amps = [r[0] for r in row]
            print(f"k_bed={k_bed:4.1f}: exact fits at P_HA_amp in "
                  f"[{min(amps):.0f}, {max(amps):.0f}] ({len(row)} cells)")
            for amp, Rs_HA, L_HA, mean_Q in row:
                cells.append(dict(k_bed=k_bed, amp=amp, Rs_pre=Rs_HA,
                                  L_pre=L_HA, mean_Q_pre=mean_Q))
        else:
            print(f"k_bed={k_bed:4.1f}: no exact fit")
    print(f"\nFamily size: {len(cells)} cells")

    print("\n=== Transplant step (portal x1.994, bed -> healthy) per arm ===")
    rows = []
    for c in cells:
        # null: no arterial response
        res_null = simulate_ha_branch(c["Rs_pre"], c["amp"], Q_PV_pod1,
                                      c["L_pre"])
        null_psv = res_null["PSV_HA"] if res_null["converged"] else np.nan
        null_frac = (PREOP["PSV_HA"] - null_psv) / decline_measured * 100.0

        # required: best-fit arterial resistance to the measured POD1 state
        Rs_req, dist, res_req = required_Rs_new(
            c["Rs_pre"], c["L_pre"], c["amp"], Q_PV_pod1)
        req_ratio = Rs_req / c["Rs_pre"]
        req_frac = (PREOP["PSV_HA"] - res_req["PSV_HA"]) / decline_measured * 100.0

        # HABR predictions (both sign conventions, same quadratic magnitude)
        Rs_can = habr_Rs_new(c["mean_Q_pre"], c["L_pre"], c["amp"],
                             Q_PV_pod1, "canonical")
        Rs_cls = habr_Rs_new(c["mean_Q_pre"], c["L_pre"], c["amp"],
                             Q_PV_pod1, "classical")

        def outcome(Rs_new):
            if Rs_new is None:
                return (np.nan, np.nan, np.nan)
            r = simulate_ha_branch(Rs_new, c["amp"], Q_PV_pod1, c["L_pre"])
            if not r["converged"]:
                return (np.nan, np.nan, np.nan)
            frac = (PREOP["PSV_HA"] - r["PSV_HA"]) / decline_measured * 100.0
            return (r["PSV_HA"], r["RI_HA"], frac)

        can_psv, can_ri, can_frac = outcome(Rs_can)
        cls_psv, cls_ri, cls_frac = outcome(Rs_cls)

        rows.append(dict(cell=c, null_psv=null_psv, null_frac=null_frac,
                         Rs_req=Rs_req, req_ratio=req_ratio, req_dist=dist,
                         req_psv=res_req["PSV_HA"], req_ri=res_req["RI_HA"],
                         req_frac=req_frac,
                         can_psv=can_psv, can_ri=can_ri, can_frac=can_frac,
                         cls_psv=cls_psv, cls_ri=cls_ri, cls_frac=cls_frac))

    def rng(key):
        vals = [r[key] for r in rows if np.isfinite(r[key])]
        return (f"[{min(vals):.1f}, {max(vals):.1f}]" if vals else "n/a")

    print(f"PSV at POD1, % of the measured {decline_measured:.2f} cm/s decline explained:")
    print(f"  null              : {rng('null_frac')} %")
    print(f"  required (fit)    : {rng('req_frac')} %  (by construction, near 100)")
    print(f"  habr_canonical    : {rng('can_frac')} %")
    print(f"  habr_classical    : {rng('cls_frac')} %")
    print("\nRI at POD1 (measured 0.61):")
    ri_null = [simulate_ha_branch(r['cell']['Rs_pre'], r['cell']['amp'],
                                  Q_PV_pod1, r['cell']['L_pre'])["RI_HA"]
               for r in rows]
    ri_req = [r["req_ri"] for r in rows]
    ri_can = [r["can_ri"] for r in rows if np.isfinite(r["can_ri"])]
    ri_cls = [r["cls_ri"] for r in rows if np.isfinite(r["cls_ri"])]
    def rrng(v):
        return f"[{min(v):.3f}, {max(v):.3f}]" if v else "n/a"
    print(f"  null              : {rrng(ri_null)}")
    print(f"  required (fit)    : {rrng(ri_req)}")
    print(f"  habr_canonical    : {rrng(ri_can)}")
    print(f"  habr_classical    : {rrng(ri_cls)}")

    print("\nArterial resistance response Rs_new/Rs_pre:")
    req_ratios = [r["req_ratio"] for r in rows]
    print(f"  required (data)   : {rrng(req_ratios)}  "
          f"(median x{np.median(req_ratios):.2f})")
    print(f"  habr_canonical    : dilatation (quadratic magnitude "
          f"{abs(habr_percent_change(-99.4)):.1f}% flow)")
    print(f"  habr_classical    : constriction (same magnitude)")

    print("\n=== Closest family members to the measured POD1 state "
          "(required arm) ===")
    print(f"{'k_bed':>6} {'amp':>5} {'Rs_pre':>9} {'Rs_new':>9} "
          f"{'Rs_ratio':>9} {'PSV':>7} {'RI':>6} {'dist':>9}")
    for r in sorted(rows, key=lambda r: r["req_dist"])[:5]:
        c = r["cell"]
        print(f"{c['k_bed']:>6.1f} {c['amp']:>5.0f} {c['Rs_pre']:>9.3f} "
              f"{r['Rs_req']:>9.3f} {r['req_ratio']:>9.3f} "
              f"{r['req_psv']:>7.2f} {r['req_ri']:>6.3f} "
              f"{r['req_dist']:>9.2e}")

    print("\n=== Structural notes ===")
    print("1. The 'required' arm is sign-agnostic: its Rs_new/Rs_pre "
          "distribution is what the measured transition demands, against\n"
           "   which the two HABR sign conventions are compared. If the "
           "required ratios cluster NEAR OR BELOW 1 (no constriction), the\n"
           "   transplant-step PSV decline does not require an arterial "
           "response at all -- the bed replacement plus prescribed portal\n"
           "   surge account for it, and both HABR sign applications "
           "over-correct.")
    print("2. k_bed is represented as an Rs_HV scale only; fibrotic "
          "stiffness (lower C_sinus) is not modelled. The identified\n"
           "   k_bed range is conditional on this one-knob parameterisation "
           "and on the prescribed-portal-flow structure.")
    print("3. No independent measurement constrains k_bed; its identified "
          "value is an inference from Doppler indices, not a measured\n"
           "   severity.")
