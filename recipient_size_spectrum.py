"""
Recipient-size spectrum: one fixed adult left-lateral-segment graft
simulated across the infant-to-child recipient range -- the revision-plan
Section 3.2 deliverable and the model's clinical-centre-of-gravity result.

The mechanistic point the script quantifies: the graft's own low-resistance
circuit (fixed vessel calibres, fixed bed resistances) sets its ABSOLUTE
inflow almost independently of who receives it, so the graft's share of the
recipient's cardiac output scales inversely with body weight. The infant
end of the spectrum is where that share peaks -- the haemodynamic form of
large-for-size exposure -- and it is exactly where the published risk
thresholds sit (see below). Anastomosis tolerance, by contrast, is set by
graft geometry and is nearly size-invariant: the modifiable factor is the
anastomosis, not the recipient.

Bracket inputs (all literature-sourced, flagged where approximate):

- Cardiac index: infant ~200, toddler ~150, school-age ~125 mL/kg/min
  (pediatric anaesthesia reference values: Anesthesia Key "Hemodynamic
  Values in Normal Pediatric Patients"; Morgan & Mikhail's Clinical
  Anesthesiology; OpenAnesthesia "Pediatric Physiology").
- MAP: infant (1-12 mo) 49-62, toddler (1-5 y) 57-71, school age (6-12 y)
  65-78 mmHg -- midpoints used (Freeman & Harrington reference values, as
  reproduced in Haque & Zaritsky, Pediatr Crit Care Med 2008).
- Heights for BSA: WHO/CDC growth-chart medians, approximate (68 / 96 /
  121 cm for the three brackets).
- SLV: Urata formula, SLV = 706.2 x BSA + 2.4 (mL), BSA by Du Bois
  (Urata et al., Liver Transpl Surg 1995;1:296-303).
- Graft: LLS 220 g (typical adult LLS ~150-250 g -- flag). The graft-type
  variant uses a 500 g left lobe with crude allometry (vessel calibres and
  bed conductance scaled by the mass ratio; area-proportional) -- flagged
  as order-of-magnitude only.
- Clinical risk anchors: GRWR >= 2.51% associates with worse survival and
  HAT, all such recipients < 1 year old (Ueda et al., Pediatr Transplant
  2021, Kyoto, n=160); critical graft weight above which vascular
  modification is needed ~ GRWR 4% in infants (Nagata et al., Am J
  Transplant 2006); graft volume / SLV > 40% beneficial for LL grafts
  (Lee et al., Pediatr Transplant 2013).

Note on the 7-year-old bracket vs the v4 draft: the draft's recipient
arterial source is 42.4-72.6 mmHg (mean 57.5) -- a perioperative range.
The literature school-age MAP midpoint (71.5) is higher; the calibration
case (POD1 anchor) keeps the draft value, the brackets use literature MAP.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pi_filter_healthy_infant_model import TARGETS
from anastomosis_stenosis_sweep import (
    DC_POD1, POD1_TARGETS, simulate_circuit, stenosis_resistance,
    R_ANAS_HA_0, HA_DIAMETER_CM,
)

# --- literature-sourced bracket inputs --------------------------------------
BRACKETS = [
    dict(name="infant (~6-9 mo)", weight=7.0, height_cm=68.0,
         CO_index=200.0, MAP=55.5, MAP_range=(49, 62)),
    dict(name="toddler (~3 y)", weight=15.0, height_cm=96.0,
         CO_index=150.0, MAP=64.0, MAP_range=(57, 71)),
    dict(name="child (~7 y)", weight=22.0, height_cm=121.0,
         CO_index=125.0, MAP=71.5, MAP_range=(65, 78)),
]

GRAFT_MASS_G = 220.0          # adult LLS, typical ~150-250 g (flag)
LEFT_LOBE_MASS_G = 500.0      # graft-type variant (crude allometry, flag)
UEDA_GRWR_PCT = 2.51          # large-for-size / HAT risk threshold (Ueda 2021)
NAGATA_GRWR_PCT = 4.0         # vascular-modification threshold (Nagata 2006)


def urata_slv_mL(weight_kg, height_cm):
    """SLV = 706.2 x BSA + 2.4 (Urata 1995), BSA by Du Bois."""
    bsa = 0.007184 * height_cm**0.725 * weight_kg**0.425
    return 706.2 * bsa + 2.4


def graft_flows(map_mmHg, rs_scale=1.0, anas_scale=1.0):
    """Mean graft inflows at a given systemic pressure. The bed resistances
    scale with rs_scale (graft-mass allometry for the graft-type variant);
    anas_scale rescales the HA anastomosis baseline resistance."""
    Rs_HA = DC_POD1["Rs_HA"] * rs_scale
    res = simulate_circuit(Rs_HA, R_anas_HA=(R_ANAS_HA_0 * anas_scale
                                             - R_ANAS_HA_0),
                           P_HA_mean_src=map_mmHg)
    return Rs_HA, res


def ha_stenosis_thresholds(map_mmHg, fracs=(0.9, 0.8)):
    """Arterial-flow stenosis thresholds at a given MAP (Rs fixed -- the
    uncompensated structural test; all arms identical, Section 24)."""
    Rs_HA, base = graft_flows(map_mmHg)
    ss = np.arange(0, 86, 2.5)
    arts = []
    for s in ss:
        r = simulate_circuit(Rs_HA, R_anas_HA=stenosis_resistance(
            float(s), R_ANAS_HA_0), P_HA_mean_src=map_mmHg)
        arts.append(r["Q_HA"] / base["Q_HA"])
    arts = np.array(arts)
    out = {}
    for frac in fracs:
        idx = np.argmax(arts < frac) if np.any(arts < frac) else None
        out[frac] = None if idx is None or idx == 0 else \
            ss[idx - 1] + (arts[idx - 1] - frac) / (arts[idx - 1] - arts[idx]) \
            * (ss[idx] - ss[idx - 1])
    return out


if __name__ == "__main__":
    print("=== Fixed adult LLS graft (220 g) across recipient brackets ===\n")
    print(f"{'bracket':<18} {'wt kg':>6} {'MAP':>6} {'Q_HA':>6} {'Q_PV':>7} "
          f"{'total':>7} {'CO':>6} {'CO share':>8} {'GRWR%':>6} {'SLV':>6} "
          f"{'GV/SLV':>7}")
    rows = []
    for b in BRACKETS:
        Rs_HA, res = graft_flows(b["MAP"])
        total = res["Q_HA"] + res["Q_PV"]
        co = b["CO_index"] * b["weight"]
        share = 100.0 * total / co
        grwr = 100.0 * GRAFT_MASS_G / (b["weight"] * 1000.0)
        slv = urata_slv_mL(b["weight"], b["height_cm"])
        rows.append((b, res, total, co, share, grwr, slv))
        print(f"{b['name']:<18} {b['weight']:>6.1f} {b['MAP']:>6.1f} "
              f"{res['Q_HA']:>6.1f} {res['Q_PV']:>7.1f} {total:>7.1f} "
              f"{co:>6.0f} {share:>7.1f}% {grwr:>6.2f} {slv:>6.0f} "
              f"{100 * GRAFT_MASS_G / slv:>6.1f}%")

    print(f"\nClinical anchors: GRWR >= {UEDA_GRWR_PCT}% = worse survival & "
          f"HAT, all <1 y (Ueda 2021); GRWR ~{NAGATA_GRWR_PCT}% = vascular "
          f"modification needed (Nagata 2006); GV/SLV > 40% beneficial "
          f"(Lee 2013).")
    inf = rows[0]
    print(f"--> the infant bracket sits ABOVE the Ueda GRWR threshold "
          f"({inf[5]:.2f}% > {UEDA_GRWR_PCT}%) with the highest CO share "
          f"({inf[4]:.1f}%); the older brackets sit below on both.")

    print("\n=== Anastomosis tolerance is size-invariant (HA arterial-flow "
          "thresholds, % narrowing) ===")
    print(f"{'bracket':<18} {'MAP':>6} {'90%':>7} {'80%':>7}")
    thr_by_bracket = {}
    for b in BRACKETS:
        th = ha_stenosis_thresholds(b["MAP"])
        thr_by_bracket[b["name"]] = th
        print(f"{b['name']:<18} {b['MAP']:>6.1f} "
              f"{th[0.9]:>6.1f}% {th[0.8]:>6.1f}%")

    print("\n=== Graft-type variant at the infant bracket (crude allometry, "
          "order-of-magnitude only) ===")
    mass_ratio = LEFT_LOBE_MASS_G / GRAFT_MASS_G
    Rs_HA_ll = DC_POD1["Rs_HA"] / mass_ratio      # bed conductance ~ mass
    Rs_PV_ll = DC_POD1["Rs_PV"] / mass_ratio
    res_ll = simulate_circuit(Rs_HA_ll, Rs_PV_override=Rs_PV_ll,
                              P_HA_mean_src=BRACKETS[0]["MAP"])
    total_ll = res_ll["Q_HA"] + res_ll["Q_PV"]
    co_inf = BRACKETS[0]["CO_index"] * BRACKETS[0]["weight"]
    grwr_ll = 100.0 * LEFT_LOBE_MASS_G / (BRACKETS[0]["weight"] * 1000.0)
    print(f"Left lobe {LEFT_LOBE_MASS_G:.0f} g in the same infant: "
          f"Q_HA={res_ll['Q_HA']:.1f}, Q_PV={res_ll['Q_PV']:.1f}, "
          f"total={total_ll:.0f} mL/min -> CO share "
          f"{100 * total_ll / co_inf:.1f}% (LLS: {inf[4]:.1f}%), "
          f"GRWR {grwr_ll:.1f}% (>> Nagata's ~4% modification threshold)")
    print("-> the model quantifies the trade-off: metabolic reserve "
          "doubles, CO exposure more than doubles; consistent with the "
          "practice of graft reduction / monosegments at this end.")

    # --- continuous curves and figure ---------------------------------------
    W = np.linspace(5.0, 30.0, 101)
    w_b = [b["weight"] for b in BRACKETS]
    map_w = np.interp(W, w_b, [b["MAP"] for b in BRACKETS])
    ci_w = np.interp(W, w_b, [b["CO_index"] for b in BRACKETS])
    share_w, grwr_w = [], []
    for w, m, ci in zip(W, map_w, ci_w):
        _, res = graft_flows(m)
        share_w.append(100.0 * (res["Q_HA"] + res["Q_PV"]) / (ci * w))
        grwr_w.append(100.0 * GRAFT_MASS_G / w)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    ax = axes[0]
    ax.plot(W, grwr_w, "b-", lw=1.8, label="GRWR (%)")
    ax.plot(W, share_w, "r-", lw=1.8, label="graft share of cardiac output (%)")
    ax.axhline(UEDA_GRWR_PCT, color="b", ls=":", lw=1.2)
    ax.annotate(f"Ueda 2021 risk threshold ({UEDA_GRWR_PCT}%)",
                xy=(5.2, UEDA_GRWR_PCT + 0.15), fontsize=8, color="b")
    ax.axhline(NAGATA_GRWR_PCT, color="b", ls="--", lw=0.8)
    for b, r in zip(BRACKETS, rows):
        ax.axvline(b["weight"], color="0.8", lw=0.6)
    ax.set_xlabel("recipient body weight (kg)")
    ax.set_ylabel("% (GRWR, or graft share of CO)")
    ax.set_title("Fixed 220 g LLS graft vs recipient size")
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(alpha=0.25)

    ax = axes[1]
    names = [b["name"] for b in BRACKETS]
    x = np.arange(len(names))
    t90 = [thr_by_bracket[n][0.9] for n in names]
    t80 = [thr_by_bracket[n][0.8] for n in names]
    ax.bar(x - 0.18, t90, 0.36, label="90% arterial-flow threshold")
    ax.bar(x + 0.18, t80, 0.36, label="80% threshold")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{n}\n({b['weight']:.0f} kg)" for n, b in
                        zip(names, BRACKETS)], fontsize=8)
    ax.set_ylabel("allowable HA stenosis (% diameter narrowing)")
    ax.set_title("Anastomosis tolerance is size-invariant")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25, axis="y")
    fig.tight_layout()
    fig.savefig("recipient_size_spectrum_figure.png", dpi=150)
    print("\nFigure saved: recipient_size_spectrum_figure.png")

    print("\n=== Caveats ===")
    print("1. Cardiac index / MAP / heights are reference-table values; "
          "the literature pull (Step 0) should replace them with "
          "transplant-population data where available.")
    print("2. The graft circuit is FIXED (Chen-anchored); per-size Doppler "
          "targets do not exist in the repo -- absolute graft flows are "
          "nearly size-invariant by construction, which IS the argument, "
          "but its empirical support is the infant cohort only.")
    print("3. Portal driving pressure held at 13 mmHg across brackets.")
    print("4. The graft-type variant uses crude mass-proportional "
          "allometry (calibres ~ sqrt(mass), bed conductance ~ mass); "
          "order-of-magnitude only.")
    print("5. The v4 draft's recipient source (42.4-72.6 mmHg, mean 57.5) "
          "is retained for the calibration anchor; brackets use literature "
          "MAP midpoints.")
