"""
Builds a short report doc presenting the post-LDLT model developed with vs.
without HABR, on the pi-filter circuit, anchored to real cohort data
(Chen et al. 2022) at POD1.
"""

import csv

import docx
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

with open("ldlt_habr_pi_filter_prediction_results.csv") as f:
    rows = list(csv.DictReader(f))
with open("ldlt_habr_pi_filter_null_model_results.csv") as f:
    null_rows = list(csv.DictReader(f))

d = docx.Document()

d.add_heading(
    "Post-LDLT Hepatic Arterial Trajectory: A Model With and Without HABR",
    level=1)

d.add_paragraph(
    "This note develops and compares two versions of the post-LDLT hepatic "
    "circulation model built on the validated pi-filter baseline (see "
    "Healthy_Paediatric_Hepatic_Circulation_Baseline_Model.docx): one with "
    "the literature hepatic arterial buffer response (HABR) feedback active, "
    "and one without it (a null model). Both are compared against this "
    "project's real serial-Doppler cohort, Chen et al. 2022 (Front. Bioeng. "
    "Biotechnol., doi:10.3389/fbioe.2022.903385), n=41 paediatric LDLT "
    "recipients, biliary atresia, ages 4-18 months."
)

d.add_heading("1. Model", level=2)
d.add_paragraph(
    "Base circuit: the validated generic pi-filter model (Rs_PV, Rs_HV, "
    "Rp_hv_out, and all L/C shape parameters reused, not re-fit). Two "
    "adaptations for the post-LDLT setting:"
)
p = d.add_paragraph(style="List Bullet")
p.add_run(
    "Portal inflow Q_PV(t) is a prescribed input (justified by the generic "
    "model's own result that PV flow is under 0.2% pulsatile -- already "
    "quasi-static), computed directly from this cohort's REAL portal vein "
    "diameter and velocity via Chen et al.'s own formula, "
    "PVF = pi*r^2*0.57*PVV*60 (mL/min/100g). Diameter is only reported at "
    "pre-transplant (0.44 cm) and POD1 (0.46 cm); POD7/14/30 use the POD1 "
    "value, justified by checking that across the (larger) pre-op->POD1 "
    "transition, velocity change (+82.5%) dominates area change (+9.3%), "
    "reproducing the reported flow change (+97.9%) almost exactly."
)
p = d.add_paragraph(style="List Bullet")
p.add_run(
    "The HA branch's resistance (Rs_HA) and inertance (L_HA) are calibrated "
    "ONCE, at POD1, against this cohort's own real measured PSV_HA (53.10 "
    "cm/s) and RI_HA (0.61) -- the HA pulse amplitude is held fixed at a "
    "real literature value (15.1 mmHg) throughout. This is the only "
    "fitting step in the HABR-on model."
)
d.add_paragraph(
    "For POD7/14/30, the two model versions diverge:"
)
p = d.add_paragraph(style="List Bullet")
p.add_run("HABR ON: ").bold = True
p.add_run(
    "Rs_HA at each time point is set so the model's mean HA flow matches "
    "exactly what the parameter-free Yu/Bartlett/Hunter/Ho HABR quadratic "
    "(changeIha = 0.0007102*x^2 + 0.5492*x, x = percent decrease in portal "
    "flow from POD1) predicts, given only the real measured portal-flow "
    "change at that time point. PSV_HA and RI_HA are the model's output, "
    "not fit."
)
p = d.add_paragraph(style="List Bullet")
p.add_run("HABR OFF (null): ").bold = True
p.add_run(
    "Rs_HA is frozen at its POD1-fitted value; only the Q_PV(t) input to "
    "the shared sinusoidal node changes. This isolates what the circuit's "
    "own passive coupling (with no active arterial feedback at all) would "
    "predict on its own."
)

d.add_heading("2. Results", level=2)
d.add_picture("HABR_Figure_1_with_without_comparison.png", width=Inches(6.3))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph(
    "Figure 1: Measured (Chen et al. 2022, mean +/- SD) vs. model with HABR "
    "on vs. model with HABR off, for hepatic artery PSV (a) and RI (b)."
)
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True

d.add_paragraph(
    "The null model (HABR off) predicts HA flow/PSV would actually drift "
    "slightly UPWARD as portal velocity falls across POD1-30 (less "
    "downstream loading on the shared sinusoidal node) -- the opposite of "
    "what is observed. Adding HABR feedback correctly flips this to the "
    "observed downward direction for both PSV_HA and RI_HA, but accounts "
    "for only part of the measured magnitude."
)

d.add_picture("HABR_Figure_2_fraction_explained.png", width=Inches(5.0))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph(
    "Figure 2: Fraction of the measured PSV_HA decline (from its POD1 "
    "value) reproduced by the parameter-free HABR model alone."
)
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True

t = d.add_table(rows=1, cols=5)
t.style = "Light Grid Accent 1"
hdr = t.rows[0].cells
for i, txt in enumerate(["Day", "PSV meas.", "PSV HABR-on", "PSV HABR-off",
                          "% of decline by HABR"]):
    hdr[i].text = txt
psv0 = float(rows[0]["PSV_HA_simulated"])
for i, (row, nrow) in enumerate(zip(rows[1:], null_rows)):
    cells = t.add_row().cells
    label = row["time"]
    psv_m, psv_s = float(row["PSV_HA_measured"]), float(row["PSV_HA_simulated"])
    frac = (psv0 - psv_s) / (psv0 - psv_m) * 100.0
    cells[0].text = label
    cells[1].text = f"{psv_m:.2f}"
    cells[2].text = f"{psv_s:.2f}"
    cells[3].text = f"{float(nrow['PSV_HA_null_no_habr']):.2f}"
    cells[4].text = f"{frac:.1f}%"

d.add_heading("3. Correction: HABR is acute, not continuously re-applied", level=2)
d.add_paragraph(
    "HABR is an acute (adenosine-washout, minutes-to-hours) mechanism. By "
    "POD30 it should have long ceased actively adjusting, and hepatic "
    "circulation should already be stable -- the model above instead "
    "re-applies the HABR quadratic at every time point relative to POD1, "
    "implicitly treating it as continuously active for the whole month, "
    "which is not appropriate for an acute mechanism."
)
d.add_paragraph(
    "The real data directly supports this correction: RI_HA is already "
    "flat (0.59, 0.59, 0.59) from POD7 through POD30, while PSV_HA keeps "
    "declining. Since RI is the ratio most sensitive to a resistance "
    "change, its flatness after POD7 means whatever resistance adjustment "
    "HABR was going to make had already happened by POD7. The model "
    "above's own simulated RI kept drifting (0.610 -> 0.607 -> 0.601 -> "
    "0.595) instead of plateauing -- itself evidence it was over-crediting "
    "HABR for what is, beyond POD7, a resistance-flat decline."
)
d.add_paragraph(
    "Corrected model: the HABR quadratic is applied ONCE, across "
    "POD1->POD7 (the one window with both a real portal-flow change and a "
    "real RI change -- the legitimate acute-response window). Rs_HA is "
    "then frozen at its POD7-consistent value for POD14/POD30; Q_PV(t) "
    "still updates to each time point's real measured value, so the "
    "circuit's own passive coupling through the shared sinusoidal node "
    "remains active -- isolating \"HABR already finished, only passive "
    "downstream coupling remains\" from \"HABR still actively adjusting.\""
)
d.add_picture("HABR_Figure_3_acute_correction.png", width=Inches(6.3))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph(
    "Figure 3: Measured vs. the old continuously-reapplied-HABR model vs. "
    "the corrected acute-then-frozen model vs. the pure null model. The "
    "corrected model's RI (panel b) plateaus after POD7, unlike the old "
    "model, matching the real data's qualitative shape far better."
)
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True
d.add_paragraph(
    "Result: HABR still explains 13.4% of the POD7 decline (unchanged, "
    "since POD7 is its legitimate window), but only 6.9% and 4.7% of the "
    "(larger) POD14 and POD30 declines respectively -- essentially none of "
    "the decline BEYOND POD7 is attributable to HABR. That remainder "
    "(93-95% of the additional POD7->POD30 decline) is 100% non-HABR in "
    "this corrected framing, not partially HABR-credited as in the model "
    "above."
)

d.add_heading("4. Honest interpretation", level=2)
d.add_paragraph(
    "A parameter-free, literature-anchored HABR relationship, applied only "
    "over its legitimate acute window (POD1-7), is directionally necessary "
    "(the null model gets the direction wrong) but explains only a modest "
    "share of the total decline (13% at POD7) and essentially none of the "
    "further decline from POD7 to POD30. That later, larger portion of the "
    "decline (8.51 of the cohort's 14.59 cm/s total POD1->POD30 drop) must "
    "be a non-HABR, non-resistance (pure amplitude/scale) effect, since it "
    "occurs while RI stays flat. A literature search "
    "(model_plan_and_literature_data.md Section 10) identified two real, "
    "independently plausible candidate mechanisms of exactly this kind -- "
    "postoperative hyperdynamic-circulation/pressure normalization "
    "(Plevak et al. 1993) and graft-regeneration-driven dilution of "
    "velocity at a fixed measurement point as the graft's vasculature "
    "enlarges with its rapid mass growth (Byun et al. 2016, "
    "doi:10.1097/MD.0000000000005404) -- either of which is independently "
    "large enough in magnitude to plausibly explain most of this residual. "
    "This project's data (group-level PSV/RI/PVV only, no serial "
    "vessel-diameter measurements beyond POD1) cannot distinguish between "
    "them, or a blend of both, or an unidentified third mechanism -- "
    "reported here as a genuine, unresolved question rather than resolved "
    "by picking one."
)

out_path = "PostLDLT_HABR_With_Without_Comparison.docx"
d.save(out_path)
print("Saved:", out_path)
