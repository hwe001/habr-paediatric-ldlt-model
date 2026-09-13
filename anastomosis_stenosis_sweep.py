"""
Anastomosis-stenosis parameter for the pi-filter graft circuit, and the
graft-tolerance sweep ("how much anastomosis narrowing can the graft
compensate?") -- the deliverable both prior review boards asked for
(revision_plan.md Section 3.3).

Parameterisation. The anastomosis is a short, fixed structural resistance
in series with the respective inflow branch, distinct from Rs_HA (the
HABR-actuated arterial bed resistance) and Rs_PV:

    R_anas(s) = R_anas(0) / (1 - s)^4      (Poiseuille, diameter stenosis s)

with R_anas(0) = 8*mu*L / (pi r^4) anchored to the model's existing vessel
calibres: HA r0 = 0.06 cm (Kim et al., Radiology 2007;245(2):549-555 --
the model's HA assumption; its previously attached DOI was wrong and was
removed 2026-09-13) and
PV r0 = 0.23 cm (Chen et al. POD1 diameter), anastomosis length 2 mm
(assumed; flagged), blood viscosity 3.5 cP (adult value; infant
post-operative polycythaemia pushes it higher -- R scales linearly in mu,
reported as a caveat not swept). Sanity anchors: a healthy HA anastomosis
is ~1% of Rs_HA (negligible), reaches ~Rs_HA near 70% diameter stenosis;
the PV anastomosis, in a vessel 4x wider, becomes comparable to Rs_PV only
above ~80% -- the model should reproduce the clinical asymmetry (the
hepatic artery is the vulnerable anastomosis in infant LDLT).

Baseline state. The sweep runs on the 5-state circuit (Q_HA, Q_PV,
P_sinus, Q_HV, P_hv -- Q_PV must be a state for PV stenosis to act),
recalibrated at the POD1-anchored state: Q_PV = 175.06 mL/min (Chen formula,
compendium Section 12; the mL/min vs mL/min/100g labelling ambiguity is
unchanged and scale-free for %-based results), Q_HA = 31.93 mL/min (v4
draft post-transplant mean), Q_HV = Q_PV + Q_HA (the source's ~3%
mass-balance gap is closed by enforcing conservation -- flagged; the draft
reported Q_HV from its own 300 mL/min-scale cohort). All pressures
unchanged from the generic targets.

HABR application. Quasi-steady discrete loop (canonical convention
structure): run to periodic steady state, compute change_Ipv vs the
unstenosed baseline, update Rs_HA to the law's target flow, re-run, to a
fixed point. Both sign arms are swept, per Sections 22-23:
  - "classical": portal flow DOWN -> arterial flow UP (buffer compensation
    -- the direction the tolerance question is about);
  - "canonical": the canonical convention verbatim (arterial follows
    portal -- anti-buffer; included as the contrast arm, not a claim).
The HABR loop runs only for PV stenosis (the portal-flow-triggered
mechanism); HA-only stenosis keeps Rs_HA frozen, so the HA curve is the
uncompensated structural test in all three arms.

Numerical scheme. The stenosis resistance makes the flow branches stiff
(Euler is unstable beyond ~76% HA stenosis at the default dt), so the two
flow branches are integrated with their exact exponential map over each dt
(Q(t+dt) = Q_ss + (Q(t) - Q_ss) e^{-R dt/L}); the pressure states keep the
canonical Euler update. At s=0 this reproduces the DC targets to well under
1% (verified at runtime).

Outputs. Compensation curves (mean flows vs stenosis, both arms, HA- and
PV-only), allowable-stenosis thresholds at 90% and 80% of baseline total
graft inflow, and `stenosis_sweep_figure.png`.
"""

import numpy as np
from scipy.optimize import brentq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pi_filter_healthy_infant_model import DEFAULT_SHAPE_PARAMS, TARGETS
from ldlt_habr_consistent_units import (
    MEASURED, q_pv_flow, habr_percent_change, PV_DIAMETER_POD1_CM,
)

# --- Poiseuille anastomosis resistance -------------------------------------
MU_BLOOD_CP = 3.5          # adult blood viscosity (caveat: infant Hct higher)
L_ANASTOMOSIS_CM = 0.2     # 2 mm anastomosis segment (assumed)
PA_S_M3_TO_MMHG_S_ML = 7.5003e-9

HA_DIAMETER_CM = 0.12      # Kim et al., Radiology 2007;245(2):549-555 -- the model's HA calibre
PV_DIAMETER_CM = PV_DIAMETER_POD1_CM  # 0.46 cm, Chen et al. POD1


def poiseuille_r0(diameter_cm, length_cm=L_ANASTOMOSIS_CM, mu_cp=MU_BLOOD_CP):
    r_m = (diameter_cm / 2.0) / 100.0
    L_m = length_cm / 100.0
    mu_Pa_s = mu_cp * 1e-3
    return 8.0 * mu_Pa_s * L_m / (np.pi * r_m**4) * PA_S_M3_TO_MMHG_S_ML


R_ANAS_HA_0 = poiseuille_r0(HA_DIAMETER_CM)
R_ANAS_PV_0 = poiseuille_r0(PV_DIAMETER_CM)


def stenosis_resistance(s_pct, r0_resistance):
    return r0_resistance / (1.0 - s_pct / 100.0) ** 4


# --- POD1-anchored baseline circuit ----------------------------------------
Q_PV_POD1 = q_pv_flow(MEASURED["POD1"]["PVV"], diameter_cm=PV_DIAMETER_POD1_CM)
Q_HA_POD1 = TARGETS["Q_HA_mean"]         # 31.93 mL/min (v4 draft, post-transplant)
Q_HV_POD1 = Q_PV_POD1 + Q_HA_POD1        # conservation enforced (flagged)

POD1_TARGETS = dict(
    P_PV_src=TARGETS["P_PV_src"], P_HA_src_mean=TARGETS["P_HA_src_mean"],
    P_HA_src_amp=TARGETS["P_HA_src_amp"], P_sinus=TARGETS["P_sinus"],
    P_hv=TARGETS["P_hv"], P_IVC=TARGETS["P_IVC"],
    Q_PV=Q_PV_POD1, Q_HA=Q_HA_POD1, Q_HV=Q_HV_POD1,
)


def solve_dc_pod1():
    """Ohm's law on the time-averaged circuit at the POD1-anchored state
    (same construction as the generic model's solve_dc_resistances)."""
    q_pv = POD1_TARGETS["Q_PV"] / 60.0
    q_ha = POD1_TARGETS["Q_HA"] / 60.0
    q_hv = POD1_TARGETS["Q_HV"] / 60.0
    return dict(
        Rs_PV=(POD1_TARGETS["P_PV_src"] - POD1_TARGETS["P_sinus"]) / q_pv,
        Rs_HA=(POD1_TARGETS["P_HA_src_mean"] - POD1_TARGETS["P_sinus"]) / q_ha,
        Rs_HV=(POD1_TARGETS["P_sinus"] - POD1_TARGETS["P_hv"]) / q_hv,
        Rp_hv_out=(POD1_TARGETS["P_hv"] - POD1_TARGETS["P_IVC"]) / q_hv,
    )


DC_POD1 = solve_dc_pod1()

HR = 130.0
STEPS_PER_CYCLE = 400
DT = (60.0 / HR) / STEPS_PER_CYCLE
MMHG_PER_SEC_FLOW = 1.0 / 60.0


def simulate_circuit(Rs_HA, R_anas_HA=0.0, R_anas_PV=0.0,
                     t_end_cycles=100, params_shape=None,
                     P_HA_mean_src=None, P_PV_src_override=None,
                     Rs_PV_override=None, Rs_HV_override=None):
    """5-state graft circuit with series anastomosis resistances. Flow
    branches use the exact exponential map (stiff-safe); pressure states
    use the canonical Euler update. The override parameters exist for the
    recipient-size spectrum and the 0D-1D coupling (tree-derived branch
    resistances); defaults reproduce the POD1 anchor exactly."""
    p = dict(DEFAULT_SHAPE_PARAMS if params_shape is None else params_shape)
    Rs_HV = DC_POD1["Rs_HV"] if Rs_HV_override is None else Rs_HV_override
    Rs_PV = DC_POD1["Rs_PV"] if Rs_PV_override is None else Rs_PV_override
    Rp_hv_out = DC_POD1["Rp_hv_out"]
    L_HA, L_PV, L_HV = p["L_HA"], p["L_PV"], p["L_HV"]
    C_sinus, C_hv, Rp_sinus = p["C_sinus"], p["C_hv"], p["Rp_sinus"]
    P_PV_src = POD1_TARGETS["P_PV_src"] if P_PV_src_override is None \
        else P_PV_src_override
    P_HA_mean = POD1_TARGETS["P_HA_src_mean"] if P_HA_mean_src is None \
        else P_HA_mean_src
    P_HA_amp = POD1_TARGETS["P_HA_src_amp"]
    P_IVC = POD1_TARGETS["P_IVC"]
    period = 60.0 / HR

    Q_HA = POD1_TARGETS["Q_HA"] * MMHG_PER_SEC_FLOW
    Q_PV = POD1_TARGETS["Q_PV"] * MMHG_PER_SEC_FLOW
    Q_HV = POD1_TARGETS["Q_HV"] * MMHG_PER_SEC_FLOW
    P_sinus = POD1_TARGETS["P_sinus"]
    P_hv = POD1_TARGETS["P_hv"]

    k_HA = np.exp(-(Rs_HA + R_anas_HA) * DT / L_HA)
    k_PV = np.exp(-(Rs_PV + R_anas_PV) * DT / L_PV)
    k_HV = np.exp(-Rs_HV * DT / L_HV)

    hist = {k: np.empty(STEPS_PER_CYCLE) for k in ("Q_HA", "Q_PV", "Q_HV")}
    prev = None
    t = 0.0
    converged = False
    for step in range(int(round(t_end_cycles * STEPS_PER_CYCLE))):
        P_HA_src = P_HA_mean + P_HA_amp * np.sin(2 * np.pi * t / period)

        # exact map for the (stiff) flow branches over dt
        ss_HA = (P_HA_src - P_sinus) / (Rs_HA + R_anas_HA)
        Q_HA = ss_HA + (Q_HA - ss_HA) * k_HA
        ss_PV = (P_PV_src - P_sinus) / (Rs_PV + R_anas_PV)
        Q_PV = ss_PV + (Q_PV - ss_PV) * k_PV
        ss_HV = (P_sinus - P_hv) / Rs_HV
        Q_HV = ss_HV + (Q_HV - ss_HV) * k_HV

        dP_sinus = (Q_HA + Q_PV - Q_HV - P_sinus / Rp_sinus) / C_sinus
        dP_hv = (Q_HV - (P_hv - P_IVC) / Rp_hv_out) / C_hv
        P_sinus += DT * dP_sinus
        P_hv += DT * dP_hv
        t += DT

        idx = step % STEPS_PER_CYCLE
        hist["Q_HA"][idx] = Q_HA
        hist["Q_PV"][idx] = Q_PV
        hist["Q_HV"][idx] = Q_HV
        if idx == STEPS_PER_CYCLE - 1:
            this = {k: v.copy() for k, v in hist.items()}
            if prev is not None:
                rel = max(np.max(np.abs(this[k] - prev[k])) /
                          (np.max(np.abs(prev[k])) + 1e-12) for k in this)
                if rel < 1e-4:
                    converged = True
                    prev = this
                    break
            prev = this

    q = {k: float(np.mean(v)) * 60.0 for k, v in prev.items()}
    a_ha = np.pi * (HA_DIAMETER_CM / 2.0) ** 2
    psv = float(np.max(prev["Q_HA"])) * 60.0 / 60.0 / a_ha  # cm/s
    edv = float(np.min(prev["Q_HA"])) * 60.0 / 60.0 / a_ha
    return dict(converged=converged, Q_HA=q["Q_HA"], Q_PV=q["Q_PV"],
                Q_HV=q["Q_HV"], P_sinus=float(np.mean(prev["P_sinus"]))
                if "P_sinus" in prev else np.nan,
                PSV_HA=psv, EDV_HA=edv,
                RI_HA=(psv - edv) / psv if psv > 0 else np.nan)


def solve_Rs_HA_for_flow(target_mLmin, R_anas_HA, Rs_guess):
    """brentq on mean arterial flow vs Rs_HA (monotone decreasing)."""
    def f(Rs):
        return simulate_circuit(Rs, R_anas_HA=R_anas_HA)["Q_HA"] - target_mLmin

    lo, hi = 0.02 * Rs_guess, 30.0 * Rs_guess
    f_lo, f_hi = f(lo), f(hi)
    tries = 0
    while f_lo * f_hi > 0 and tries < 30:
        lo *= 0.5
        hi *= 2.0
        f_lo, f_hi = f(lo), f(hi)
        tries += 1
    if f_lo * f_hi > 0:
        return None
    return brentq(f, lo, hi, xtol=1e-4, maxiter=60)


def sweep_point(s_pct, vessel, arm, Q_HA_base, Q_PV_base, Rs_HA_base,
                habr_enabled=True):
    """One stenosis level: returns the HABR-quasi-steady fixed point.
    habr_enabled=False keeps Rs_HA frozen (used for HA-only stenosis: the
    small P_sinus-mediated portal perturbation is deliberately excluded so
    the HA curve is the uncompensated structural test)."""
    if vessel == "HA":
        R_anas_HA, R_anas_PV = stenosis_resistance(s_pct, R_ANAS_HA_0), 0.0
    else:
        R_anas_HA, R_anas_PV = 0.0, stenosis_resistance(s_pct, R_ANAS_PV_0)

    Rs_HA = Rs_HA_base
    res = simulate_circuit(Rs_HA, R_anas_HA=R_anas_HA, R_anas_PV=R_anas_PV)
    if not res["converged"]:
        return None
    for _ in range(20):
        if arm == "none" or not habr_enabled or res["Q_PV"] <= 0:
            break
        change_Ipv = (Q_PV_base - res["Q_PV"]) / Q_PV_base * 100.0
        if abs(change_Ipv) < 1e-6:
            break
        change_Iha = habr_percent_change(change_Ipv)
        sign = -1.0 if arm == "canonical" else +1.0
        target = Q_HA_base * (1.0 + sign * change_Iha / 100.0)
        target = min(target, 3.0 * Q_HA_base)
        Rs_new = solve_Rs_HA_for_flow(target, R_anas_HA, Rs_HA)
        if Rs_new is None:
            break
        if abs(Rs_new - Rs_HA) / Rs_HA < 1e-4:
            Rs_HA = Rs_new
            res = simulate_circuit(Rs_HA, R_anas_HA=R_anas_HA,
                                   R_anas_PV=R_anas_PV)
            break
        Rs_HA = Rs_new
        res = simulate_circuit(Rs_HA, R_anas_HA=R_anas_HA, R_anas_PV=R_anas_PV)
        if not res["converged"]:
            return None
    return dict(s=s_pct, arm=arm, Rs_HA=Rs_HA, res=res)


def allowable_stenosis(grid, fractions_of_baseline, metric="total",
                       base_Q_HA=None, base_Q_PV=None):
    """First crossing of the vessel-appropriate inflow metric below each
    fraction of its unstenosed baseline (linear interpolation on the grid).
    metric='total': Q_HA + Q_PV (the right metric for PV stenosis, where
    the question is total graft perfusion). metric='arterial': Q_HA alone
    (the right metric for HA stenosis: total inflow is propped up by the
    portal rise while the arterial supply -- and with it the biliary
    plexus -- collapses)."""
    if metric == "arterial":
        vals = np.array([pt["res"]["Q_HA"] / base_Q_HA for pt in grid])
    else:
        base_total = base_Q_HA + base_Q_PV
        vals = np.array([(pt["res"]["Q_HA"] + pt["res"]["Q_PV"]) / base_total
                         for pt in grid])
    ss = np.array([pt["s"] for pt in grid])
    out = {}
    for frac in fractions_of_baseline:
        thr = frac
        idx = np.argmax(vals < thr) if np.any(vals < thr) else None
        if idx is None or idx == 0:
            out[frac] = None
        else:
            s0, s1 = ss[idx - 1], ss[idx]
            t0, t1 = vals[idx - 1], vals[idx]
            out[frac] = s0 + (t0 - thr) / (t0 - t1) * (s1 - s0)
    return out


if __name__ == "__main__":
    print("=== Anastomosis baseline resistances (Poiseuille, mu=3.5 cP, "
          "L=2 mm) ===")
    print(f"HA: r0={HA_DIAMETER_CM:.2f} cm -> R_anas(0)={R_ANAS_HA_0:.4f} "
          f"mmHg*s/mL ({100 * R_ANAS_HA_0 / DC_POD1['Rs_HA']:.2f}% of Rs_HA="
          f"{DC_POD1['Rs_HA']:.2f})")
    print(f"PV: r0={PV_DIAMETER_CM:.2f} cm -> R_anas(0)={R_ANAS_PV_0:.4f} "
          f"mmHg*s/mL ({100 * R_ANAS_PV_0 / DC_POD1['Rs_PV']:.2f}% of Rs_PV="
          f"{DC_POD1['Rs_PV']:.2f})")

    print("\n=== POD1-anchored baseline verification (s=0, exact-map "
          "integrator) ===")
    base = simulate_circuit(DC_POD1["Rs_HA"])
    print(f"Q_PV={base['Q_PV']:.2f} (target {Q_PV_POD1:.2f}), "
          f"Q_HA={base['Q_HA']:.2f} (target {Q_HA_POD1:.2f}), "
          f"Q_HV={base['Q_HV']:.2f}, converged={base['converged']}")
    print(f"PSV_HA={base['PSV_HA']:.2f} cm/s, RI={base['RI_HA']:.3f} "
          f"(Doppler-scale check, not a target here)")

    arms = ("none", "classical", "canonical")
    grids = {}
    for vessel in ("PV", "HA"):
        ss = np.arange(0, 96, 5) if vessel == "PV" else np.arange(0, 86, 2.5)
        for arm in arms:
            pts = []
            for s in ss:
                pt = sweep_point(float(s), vessel, arm, base["Q_HA"],
                                 base["Q_PV"], DC_POD1["Rs_HA"],
                                 habr_enabled=(vessel == "PV"))
                if pt is not None:
                    pts.append(pt)
            grids[(vessel, arm)] = pts

    print("\n=== Allowable stenosis (% diameter narrowing at which the "
          "vessel-appropriate inflow metric falls below threshold) ===")
    print("PV: total graft inflow (Q_HA+Q_PV); HA: arterial flow Q_HA "
          "(total inflow is propped up by the portal rise while the\n"
          "arterial supply collapses)\n")
    print(f"{'vessel':>6} {'metric':>9} {'arm':>10} {'90%':>7} {'80%':>7}")
    for (vessel, arm), pts in grids.items():
        metric = "arterial" if vessel == "HA" else "total"
        th = allowable_stenosis(pts, (0.9, 0.8), metric=metric,
                                base_Q_HA=base["Q_HA"], base_Q_PV=base["Q_PV"])
        f90 = f"{th[0.9]:.1f}%" if th[0.9] is not None else ">max"
        f80 = f"{th[0.8]:.1f}%" if th[0.8] is not None else ">max"
        print(f"{vessel:>6} {metric:>9} {arm:>10} {f90:>7} {f80:>7}")

    print("\n=== Compensation detail (selected levels) ===")
    for vessel in ("PV", "HA"):
        print(f"-- {vessel} anastomosis --")
        print(f"{'s%':>5} {'arm':>10} {'Q_PV':>8} {'Q_HA':>8} {'total%':>8} "
              f"{'art%':>7} {'Rs_HA':>9} {'PSV':>7}")
        base_total = base["Q_HA"] + base["Q_PV"]
        show = (0, 40, 60, 70, 80, 90) if vessel == "PV" else (0, 30, 40, 50, 60, 70, 80)
        for s in show:
            for arm in arms:
                pt = next((p for p in grids[(vessel, arm)] if p["s"] == s),
                          None)
                if pt is None:
                    continue
                r = pt["res"]
                tot = 100.0 * (r["Q_HA"] + r["Q_PV"]) / base_total
                art = 100.0 * r["Q_HA"] / base["Q_HA"]
                print(f"{s:>5.1f} {arm:>10} {r['Q_PV']:>8.1f} "
                      f"{r['Q_HA']:>8.1f} {tot:>8.1f} {art:>7.1f} "
                      f"{pt['Rs_HA']:>9.2f} {r['PSV_HA']:>7.1f}")

    # figure: PV panel = total graft inflow; HA panel = arterial flow
    # (the vessel-appropriate metrics; see the threshold table)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, vessel in zip(axes, ("PV", "HA")):
        for arm, style in zip(arms, ("k--", "g-", "r-")):
            pts = grids[(vessel, arm)]
            ss = [p["s"] for p in pts]
            if vessel == "HA":
                vals = [100.0 * p["res"]["Q_HA"] / base["Q_HA"] for p in pts]
            else:
                vals = [100.0 * (p["res"]["Q_HA"] + p["res"]["Q_PV"]) /
                        base_total for p in pts]
            ax.plot(ss, vals, style, label=arm, lw=1.8)
        ax.axhline(90, color="0.6", lw=0.8, ls=":")
        ax.axhline(80, color="0.6", lw=0.8, ls=":")
        ax.set_title(f"{vessel} anastomosis stenosis"
                     f" ({'arterial flow' if vessel == 'HA' else 'total inflow'})")
        ax.set_xlabel("diameter stenosis (%)")
        ax.set_ylim(0, 145)
        ax.grid(alpha=0.25)
    axes[0].set_ylabel("% of unstenosed baseline")
    axes[0].legend(loc="lower left", fontsize=9)
    fig.suptitle("Graft tolerance vs anastomosis stenosis "
                 "(POD1-anchored infant LLS graft circuit)")
    fig.tight_layout()
    fig.savefig("stenosis_sweep_figure.png", dpi=150)
    print("\nFigure saved: stenosis_sweep_figure.png")

    print("\n=== Caveats ===")
    print("1. mu = 3.5 cP (adult); infant post-op polycythaemia raises it "
          "-- R_anas scales linearly in mu, thresholds shift DOWN.")
    print("2. Anastomosis length 2 mm assumed; R_anas scales linearly in L.")
    print("3. Stenosis is a fixed structural resistance; no remodelling, "
          "no collateral flow, Q_PV prescribed-pressure driven.")
    print("4. HABR 'classical' arm = the buffer direction the tolerance "
          "question requires; 'canonical' = the manuscript's convention "
          "(anti-buffer; shown as contrast, per Sections 22-23 the sign "
          "question is unresolved).")
    print("5. Q_HV conservation enforced at the POD1 anchor (source data "
          "has a ~3% gap); %-based results are insensitive to the "
          "mL/min vs mL/min/100g scale (compendium Section 12).")
    print("6. The 5-state circuit's waveform shape is the generic default "
          "(its PSV/RI at baseline are indicative only, not the POD1 "
          "anchored family); the sweep's results are %-flow metrics.")
