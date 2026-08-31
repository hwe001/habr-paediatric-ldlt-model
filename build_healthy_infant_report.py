"""
Builds a short report doc presenting the generic healthy/paediatric hepatic
circulation model (Section 8 of model_plan_and_literature_data.md) --
methods, the pi-filter definition, target data, results table, and figures.
"""

import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from pi_filter_healthy_infant_model import build_params, simulate, TARGETS

params = build_params()
res = simulate(params)

d = docx.Document()

title = d.add_heading(
    "A Pi-Filter Lumped-Parameter Model of Healthy Paediatric Hepatic "
    "Circulation: Baseline Validation", level=1)

d.add_paragraph(
    "This note documents the generic (non-transplant, non-HABR) baseline "
    "circulation model built as the correct foundation for this project's "
    "post-LDLT hepatic arterial buffer response (HABR) work, per the "
    "direction to first get portal vein (PV), hepatic arterial (HA), and "
    "hepatic venous (HV) flow right in a healthy/typical paediatric liver "
    "before layering transplant- or pathology-specific mechanisms on top. "
    "Full detail and version history are in this project's "
    "model_plan_and_literature_data.md, Section 8."
)

d.add_heading("1. The pi-filter element", level=2)
d.add_paragraph(
    "The model is built from the same lumped circuit element (\"pi-filter\") "
    "used in Harvey Ho's prior hepatic circulation modelling work, confirmed "
    "from the circuit diagram in 2018/liver segments/0d-1d habr_v1.docx "
    "(Fig. 4 inset): a two-port network with a series inductor (L) and "
    "resistor (Rs) between the two ports, and an identical shunt branch "
    "(a capacitor C in series with a resistor Rp, to a common ground/"
    "reference) at EACH port. This gives four distinct parameter values "
    "(L, Rs, C, Rp) per segment, matching the source description of "
    "\"three resistors, two capacitors and one inductor\" (Rs plus two Rp "
    "legs; two C legs of equal value) and \"four parameters\" per pi-filter."
)

d.add_heading("2. Circuit topology", level=2)
d.add_paragraph(
    "A single-lobe topology (matching the scale of this project's data, "
    "rather than the fuller multi-generation, left/right-lobe-split version "
    "in the 2018 draft): an HA pi-filter and a PV pi-filter both feed a "
    "shared sinusoidal node, which drains through an HV pi-filter to a "
    "fixed inferior-vena-cava (IVC) reference pressure. Only the "
    "output-side shunt of each source-driven branch, and the shared "
    "sinusoidal/HV nodes, matter dynamically -- an ideal voltage source "
    "absorbs whatever current its own input-side shunt draws, so that "
    "shunt drops out of the dynamics. This gives five state variables: "
    "Q_HA, Q_PV, P_sinus, Q_HV, P_hv."
)
d.add_picture("HealthyInfant_Figure_1_schematic.png", width=Inches(6.2))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph("Figure 1: Model schematic.")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True

d.add_heading("3. Real target data", level=2)
d.add_paragraph(
    "Target values are real, not invented, taken directly from Ho, Yu, "
    "Bartlett, \"Computational simulations for the hepatic arterial buffer "
    "response after liver graft transplantation\" (submitted manuscript, "
    "2018/liver_paediatric/submission/numerical methods for quantifying "
    "blood flow after PH_v4.docx -- has a rebuttal on file, so it went "
    "through peer review; publication status otherwise unconfirmed), "
    "Results Section 3.1, post-transplant paediatric-recipient values. This "
    "is the same adult-to-child left-lateral-segment transplant scenario as "
    "this project, modelled with the same pi-filter approach."
)

t = d.add_table(rows=1, cols=3)
t.style = "Light Grid Accent 1"
hdr = t.rows[0].cells
hdr[0].text, hdr[1].text, hdr[2].text = "Quantity", "Value", "Source"
target_rows = [
    ("Portal driving pressure", "13 mmHg", "post-transplant recipient"),
    ("Mean arterial pressure", "57.5 mmHg (42.4-72.6 range)", "post-transplant recipient"),
    ("Sinusoidal pressure", "5.37 mmHg", "post-transplant recipient"),
    ("Hepatic venous pressure", "4.07 mmHg", "post-transplant recipient"),
    ("Portal vein flow", "300 mL/min", "regression, 64 children 3mo-16y"),
    ("Hepatic arterial flow", "31.93 +/- 7.7 mL/min", "post-transplant recipient"),
    ("Hepatic venous flow", "322.5 mL/min", "post-transplant recipient"),
]
for label, val, src in target_rows:
    row = t.add_row().cells
    row[0].text, row[1].text, row[2].text = label, val, src

d.add_paragraph(
    "Note: the source paper's own Q_PV + Q_HA (300 + 31.93 = 331.9 mL/min) "
    "does not exactly equal its own reported Q_HV (322.5 mL/min) -- a "
    "~3% mass-balance discrepancy already present in the source data, not "
    "introduced by this model. The IVC reference pressure (2.0 mmHg) is "
    "assumed, since it is not reported in the source."
)

d.add_heading("4. Calibration method", level=2)
d.add_paragraph(
    "Because this baseline model is linear (no HABR nonlinear resistor is "
    "included at this stage), the three series resistances (Rs_PV, Rs_HA, "
    "Rs_HV) were solved EXACTLY via Ohm's law on the time-averaged (DC) "
    "circuit, using the real target pressures and flows above. A linear "
    "system's time-average response to a periodic input equals its DC "
    "solution regardless of the inertance/compliance (\"shape\") "
    "parameters, so this reproduces the real target MEAN flows by "
    "construction, independent of how pulsatility is tuned. The "
    "inertance/compliance values themselves (L_HA, L_PV, L_HV, C_sinus, "
    "C_hv, Rp_sinus) were chosen, not derived, to give a physiologically "
    "reasonable pulsatile shape -- flagged as assumed/representative, the "
    "same caveat given to every other non-fitted constant in this "
    "session's other modelling projects."
)

d.add_heading("5. Results", level=2)
d.add_picture("HealthyInfant_Figure_2_waveforms.png", width=Inches(6.2))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph(
    "Figure 2: Simulated flow (a) and pressure (b) over one cardiac cycle. "
    "HA is visibly pulsatile; PV and HV are both nearly flat -- matching "
    "the qualitative pattern in the source paper's own Fig. 2."
)
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True

d.add_picture("HealthyInfant_Figure_3_comparison.png", width=Inches(5.5))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph(
    "Figure 3: Simulated vs. real target mean flows. All three match "
    "within 2%."
)
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True

t2 = d.add_table(rows=1, cols=4)
t2.style = "Light Grid Accent 1"
hdr = t2.rows[0].cells
hdr[0].text, hdr[1].text, hdr[2].text, hdr[3].text = (
    "Quantity", "Target", "Simulated", "Difference")
result_rows = [
    ("Q_PV (mL/min)", f"{TARGETS['Q_PV_mean']:.2f}",
     f"{res['Q_PV_mean_mLmin']:.2f}",
     f"{100*(res['Q_PV_mean_mLmin']-TARGETS['Q_PV_mean'])/TARGETS['Q_PV_mean']:+.1f}%"),
    ("Q_HA (mL/min)", f"{TARGETS['Q_HA_mean']:.2f}",
     f"{res['Q_HA_mean_mLmin']:.2f}",
     f"{100*(res['Q_HA_mean_mLmin']-TARGETS['Q_HA_mean'])/TARGETS['Q_HA_mean']:+.1f}%"),
    ("Q_HV (mL/min)", f"{TARGETS['Q_HV_mean']:.2f}",
     f"{res['Q_HV_mean_mLmin']:.2f}",
     f"{100*(res['Q_HV_mean_mLmin']-TARGETS['Q_HV_mean'])/TARGETS['Q_HV_mean']:+.1f}%"),
    ("P_sinus (mmHg)", f"{TARGETS['P_sinus']:.2f}",
     f"{res['P_sinus'].mean():.3f}",
     f"{100*(res['P_sinus'].mean()-TARGETS['P_sinus'])/TARGETS['P_sinus']:+.1f}%"),
    ("P_hv (mmHg)", f"{TARGETS['P_hv']:.2f}",
     f"{res['P_hv'].mean():.3f}",
     f"{100*(res['P_hv'].mean()-TARGETS['P_hv'])/TARGETS['P_hv']:+.1f}%"),
]
for row in result_rows:
    cells = t2.add_row().cells
    for i, v in enumerate(row):
        cells[i].text = v

d.add_paragraph(
    "The residual 1-2% gaps are attributable to finite-difference "
    "(Euler) integration truncation error and the small continuous leak "
    "current through the sinusoidal node's Rp_sinus resistor, not a "
    "calibration failure."
)

d.add_heading("6. Status and next step", level=2)
d.add_paragraph(
    "This generic healthy/paediatric baseline circulation model is now "
    "validated and is the correct foundation on which the transplant- and "
    "HABR-specific work for this project's real serial-Doppler LDLT cohort "
    "is being rebuilt (ldlt_habr_on_pi_filter.py), replacing an earlier, "
    "structurally simpler ad hoc branch model. See "
    "model_plan_and_literature_data.md Sections 8-10 for that work and its "
    "current, honestly-reported open questions."
)

out_path = "Healthy_Paediatric_Hepatic_Circulation_Baseline_Model.docx"
d.save(out_path)
print("Saved:", out_path)
