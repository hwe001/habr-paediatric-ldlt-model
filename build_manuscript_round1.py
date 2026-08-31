"""
Full manuscript draft, round 1, synthesizing this project's work:
- a validated generic pi-filter paediatric hepatic circulation model
- a post-LDLT HABR test on real serial-Doppler data, corrected for HABR's
  known acute time course
- a literature-based partial disambiguation of the residual (non-HABR)
  mechanism

All citations verified via the EuropePMC API before use (see
model_plan_and_literature_data.md for the verification trail).
"""

import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

d = docx.Document()

d.add_heading(
    "Testing the Hepatic Arterial Buffer Response Against Real "
    "Post-Transplant Doppler Data in Paediatric Liver Recipients: "
    "A Lumped-Parameter Model Study", level=1)

# ---------------------------------------------------------------- Abstract
d.add_heading("Abstract", level=2)
d.add_paragraph(
    "The hepatic arterial buffer response (HABR) -- the intrinsic tendency "
    "of hepatic arterial flow to counteract changes in portal venous flow "
    "-- is commonly invoked to explain the marked fall in hepatic artery "
    "Doppler velocity seen after paediatric living-donor liver "
    "transplantation (LDLT), but this explanation has not previously been "
    "tested quantitatively against real serial-Doppler data using a "
    "mechanistic model, nor checked against HABR's own well-established "
    "acute (minutes-to-hours) time course. We built a lumped-parameter "
    "(\"pi-filter\") hepatic circulation model, validated it against "
    "independent literature targets for a generic paediatric "
    "post-transplant circulation, then anchored it to a real cohort of 41 "
    "infants after left-lateral-segment LDLT for biliary atresia (Chen et "
    "al., 2022), using their own reported portal vein diameter and flow "
    "formula. Applying a parameter-free HABR relationship (from prior "
    "unpublished electrical-analog modelling of this same clinical "
    "scenario) across postoperative day (POD) 1-30 explains only 13-31% of "
    "the measured fall in hepatic artery peak systolic velocity (PSV), "
    "rising over time -- but this itself is inconsistent with HABR's known "
    "acute kinetics. The cohort's own resistive index (RI) is already flat "
    "from POD7 through POD30, showing the resistance-driven component of "
    "the change is complete by POD7. Correcting the model to apply HABR "
    "only within this legitimate window (POD1-7) and freezing arterial "
    "resistance thereafter shows HABR explains a modest, constant ~13% of "
    "the total decline, and essentially none of the substantial further "
    "fall from POD7 to POD30. A literature search for non-HABR "
    "explanations of this residual identified two candidates -- systemic "
    "hyperdynamic-circulation normalization (resolving within days) and "
    "graft-regeneration-driven dilution of Doppler velocity as vessel "
    "calibre grows with the regenerating graft (continuing over weeks) -- "
    "a timing argument favours the latter for the sustained decline, "
    "though its magnitude for this specific left-lateral-segment "
    "population remains unresolved. This is, to our knowledge, the first "
    "quantitative, time-course-respecting test of HABR against real "
    "paediatric post-LDLT Doppler data."
)

d.add_heading("Keywords", level=3)
d.add_paragraph(
    "hepatic arterial buffer response; liver transplantation; paediatric; "
    "Doppler ultrasound; lumped-parameter model; hepatic circulation; "
    "biliary atresia"
)

# ------------------------------------------------------------ Introduction
d.add_heading("Introduction", level=2)
d.add_paragraph(
    "The hepatic arterial buffer response (HABR) is an intrinsic hepatic "
    "regulatory mechanism: a fall in portal venous flow provokes a rise in "
    "hepatic arterial flow, and vice versa, mediated by washout of "
    "adenosine in the periportal space of Mall -- a fast process, "
    "operating on a timescale of minutes to a few hours. HABR is clinically "
    "relevant after partial hepatectomy and liver transplantation, where "
    "abrupt portal flow changes are common and altered hepatic arterial "
    "flow has been linked to arterial thrombosis risk in liver grafts."
)
d.add_paragraph(
    "Prior work from this group modelled HABR using an electrical-analog "
    "(\"pi-filter\") lumped-parameter representation of the portal, "
    "hepatic arterial, and hepatic venous circulations, with an empirical "
    "quadratic regulation function relating hepatic arterial to portal "
    "flow change (Ho et al., 2013). This was subsequently applied, in "
    "unpublished draft form, to an adult-to-child left-lateral-segment "
    "(LLS) liver transplantation scenario matching real paediatric "
    "recipient pressures and flows (Yu, Bartlett, Hunter and Ho, "
    "unpublished manuscript; Ho, Yu and Bartlett, unpublished submitted "
    "manuscript), predicting that hepatic arterial flow should fall as "
    "portal flow rises after transplantation."
)
d.add_paragraph(
    "Separately, a real clinical dataset now exists that can test this "
    "prediction directly: Chen et al. (2022) report serial hepatic artery "
    "and portal vein Doppler measurements in 41 infants (4-18 months, "
    "biliary atresia) before and after LLS-LDLT, at postoperative day (POD) "
    "1, 7, 14, and 30. Hepatic artery peak systolic velocity (PSV) and "
    "resistive index (RI) both fall substantially and progressively over "
    "this month, which the authors attribute qualitatively to HABR, but "
    "without a quantitative mechanistic test."
)
d.add_paragraph(
    "This study combines these two strands: we build a validated "
    "pi-filter circulation model, anchor it to this real cohort's own "
    "data, and ask two questions. First, does the parameter-free HABR "
    "relationship, driven only by this cohort's own measured portal-flow "
    "trend, quantitatively reproduce the observed hepatic arterial "
    "trajectory? Second -- since HABR is a fast, acute mechanism, not one "
    "that should remain actively adjusting for a full month -- over what "
    "part of this trajectory is it actually appropriate to apply it, and "
    "what explains the rest?"
)

# ------------------------------------------------------------------ Methods
d.add_heading("Methods", level=2)

d.add_heading("2.1 Dataset", level=3)
d.add_paragraph(
    "Chen et al. (2022; doi:10.3389/fbioe.2022.903385) is a retrospective "
    "study of 41 infants (22 male, 19 female; median age 5 months, range "
    "4-18) with biliary atresia undergoing LLS-LDLT, with uncomplicated "
    "postoperative courses (vascular and biliary complications were "
    "exclusion criteria). Doppler measurements -- hepatic artery PSV and "
    "RI, portal vein velocity (PVV), and (at pre-transplant and POD1 only) "
    "portal vein diameter -- were taken pre-transplant and at POD1, 7, 14, "
    "and 30 (Table 1). The authors' own portal flow formula, PVF = "
    "pi*r^2*0.57*PVV*60 (mL/min per 100 g graft, r = diameter/2 in cm, PVV "
    "in cm/s), is used directly in this study to anchor the model's "
    "portal input to real, cohort-specific values rather than a value "
    "borrowed from a different population."
)

t1 = d.add_table(rows=1, cols=4)
t1.style = "Light Grid Accent 1"
hdr = t1.rows[0].cells
hdr[0].text, hdr[1].text, hdr[2].text, hdr[3].text = (
    "Time", "PSV_HA (cm/s)", "RI_HA", "PVV (cm/s)")
for row in [
    ("Pre-transplant", "73.32 +/- 22.31", "0.77 +/- 0.09", "16.88 +/- 5.69"),
    ("POD1", "53.10 +/- 16.02", "0.61 +/- 0.05", "30.80 +/- 8.67"),
    ("POD7", "47.02 +/- 10.05", "0.59 +/- 0.03", "30.05 +/- 8.80"),
    ("POD14", "42.29 +/- 10.38", "0.59 +/- 0.05", "28.39 +/- 6.47"),
    ("POD30", "38.51 +/- 7.63", "0.59 +/- 0.01", "26.71 +/- 7.93"),
]:
    cells = t1.add_row().cells
    for i, v in enumerate(row):
        cells[i].text = v
cap = d.add_paragraph("Table 1: Real cohort data (Chen et al., 2022, mean +/- SD, n=41).")
cap.runs[0].italic = True

d.add_heading("2.2 The pi-filter lumped element and generic circulation model", level=3)
d.add_paragraph(
    "The circulation is represented with the same lumped element used in "
    "this group's prior modelling: a two-port \"pi-filter\" with a series "
    "inductor (L, inertance) and resistor (Rs) between the ports, and an "
    "identical shunt branch (a capacitor C in series with a resistor Rp, "
    "to a common reference) at each port -- four distinct parameters (L, "
    "Rs, C, Rp) per vascular segment. A single-lobe topology (matching the "
    "scale of the available data, rather than the fuller multi-generation, "
    "left/right-lobe-split network used in some prior work) has hepatic "
    "arterial (HA) and portal venous (PV) pi-filters both feeding a shared "
    "sinusoidal node, which drains through a hepatic venous (HV) pi-filter "
    "to a fixed inferior-vena-cava reference pressure (Figure 1). Only the "
    "output-side shunt of each source-driven branch, and the shared "
    "sinusoidal/HV nodes, matter dynamically, giving five state variables: "
    "Q_HA, Q_PV, P_sinus, Q_HV, P_hv."
)
d.add_picture("HealthyInfant_Figure_1_schematic.png", width=Inches(6.0))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph("Figure 1: Pi-filter circulation model schematic.")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True

d.add_paragraph(
    "This model was first validated in a generic (non-transplant, healthy/"
    "typical paediatric) configuration against independent real target "
    "data: Ho, Yu and Bartlett's unpublished manuscript on this same "
    "adult-to-child LLS scenario reports real post-transplant paediatric "
    "recipient values (portal driving pressure 13 mmHg, mean arterial "
    "pressure 57.5 mmHg [range 42.4-72.6], sinusoidal pressure 5.37 mmHg, "
    "hepatic venous pressure 4.07 mmHg, portal flow 300 mL/min, hepatic "
    "arterial flow 31.93 mL/min, hepatic venous flow 322.5 mL/min). "
    "Because this baseline configuration is linear, the three series "
    "resistances (Rs_PV, Rs_HA, Rs_HV) were solved exactly via Ohm's law "
    "on the time-averaged circuit from these targets -- a linear system's "
    "time-average response to a periodic input equals its DC solution "
    "regardless of the inertance/compliance parameters, so this "
    "reproduces the target mean flows by construction. The inertance/"
    "compliance ('shape') parameters were chosen, not derived, for "
    "physiologically reasonable pulsatility."
)
d.add_picture("HealthyInfant_Figure_2_waveforms.png", width=Inches(6.0))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph(
    "Figure 2: Generic model simulated flow (a) and pressure (b), one "
    "cardiac cycle.")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True
d.add_picture("HealthyInfant_Figure_3_comparison.png", width=Inches(5.0))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph(
    "Figure 3: Generic model mean flows vs. real targets (all within 2%).")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True

d.add_heading("2.3 HABR mechanism", level=3)
d.add_paragraph(
    "HABR is represented, as in the prior work it is drawn from, by a "
    "discrete, between-state resistance-update rule rather than a "
    "continuous-time kinetic model: changeIha = 0.0007102*x^2 + 0.5492*x, "
    "where x is the percent DECREASE in portal flow relative to a "
    "reference state and changeIha is the resulting percent decrease in "
    "hepatic arterial flow. This empirical quadratic is not re-derived "
    "here; it is reused as published/drafted in the source work."
)

d.add_heading("2.4 Post-LDLT model calibration", level=3)
d.add_paragraph(
    "Portal inflow Q_PV(t) is a prescribed input rather than an "
    "independently simulated state -- justified by the generic model's "
    "own result that PV flow varies under 0.2% across a cardiac cycle, "
    "i.e. it is already indistinguishable from quasi-static. Q_PV(t) is "
    "computed directly from this cohort's own portal vein diameter and "
    "PVV via their formula (Section 2.1). Diameter is only reported at "
    "pre-transplant (0.44 cm) and POD1 (0.46 cm); POD7/14/30 use the POD1 "
    "value. This is supported by checking the formula across the (larger) "
    "pre-op to POD1 transition, where diameter IS reported: area increased "
    "only 9.3% while velocity increased 82.5%, combining to a 99.4% flow "
    "increase that matches the reported 97.9% almost exactly -- confirming "
    "velocity, not area, dominates the flow change in this cohort, at "
    "least across that transition."
)
d.add_paragraph(
    "The HA branch's resistance (Rs_HA) and inertance (L_HA) are "
    "calibrated once, at POD1, against this cohort's own real measured "
    "PSV_HA and RI_HA -- the HA pulse amplitude is held fixed at the "
    "generic model's real literature value (15.1 mmHg) throughout. "
    "(Reusing the generic model's own L_HA verbatim, rather than "
    "re-fitting it here, produced a physiologically implausible fitted "
    "pulse amplitude of 440 mmHg, because that L_HA was tuned for the "
    "generic model's own resistance scale, roughly 100-fold different "
    "from this cohort's fitted value -- L_HA, like the other shape "
    "parameters, was never independently validated in absolute terms and "
    "is re-fit here instead.) This is the only fitting step used; "
    "PSV_HA and RI_HA at all other time points are model OUTPUT, not fit."
)

d.add_heading("2.5 Respecting HABR's acute time course", level=3)
d.add_paragraph(
    "HABR's adenosine-washout kinetics operate on a timescale of minutes "
    "to a few hours -- it should not be modelled as continuously, "
    "actively re-adjusting arterial resistance throughout an entire "
    "postoperative month. This cohort's own RI_HA is already flat (0.59, "
    "0.59, 0.59) from POD7 through POD30, while PSV_HA keeps falling -- "
    "since RI is the ratio most sensitive to a resistance change, its "
    "flatness after POD7 indicates the resistance-driven component is "
    "complete by then. The HABR quadratic is therefore applied only "
    "once, across POD1-POD7 -- the one window with both a real portal-"
    "flow change and a real RI change -- and Rs_HA is frozen at its "
    "POD7-consistent value for POD14 and POD30. Q_PV(t) still updates to "
    "each time point's real measured value, so the circuit's own passive "
    "coupling through the shared sinusoidal node remains active, "
    "isolating \"HABR already finished, only passive downstream coupling "
    "remains\" from \"HABR still actively adjusting.\""
)

d.add_heading("2.6 Candidate residual mechanisms", level=3)
d.add_paragraph(
    "A literature search (PubMed/EuropePMC, citations verified against "
    "primary sources or the EuropePMC metadata API before use, not taken "
    "from search-engine summaries alone) was conducted for real, "
    "independently plausible, non-HABR mechanisms that could explain a "
    "continued fall in hepatic artery Doppler velocity over the "
    "postoperative month while RI remains flat -- i.e. a pure amplitude/"
    "scale effect on the velocity waveform rather than a resistance "
    "effect, since RI (a ratio of waveform extremes) is preserved under "
    "both vessel-calibre dilution and a uniform arterial pressure-"
    "amplitude change."
)

# -------------------------------------------------------------------- Results
d.add_heading("Results", level=2)

d.add_heading("3.1 Generic model validation", level=3)
d.add_paragraph(
    "The generic pi-filter model reproduced the independent real target "
    "flows within 2% (Q_PV 297.5 vs. 300, Q_HA 31.9 vs. 31.9, Q_HV 328.6 "
    "vs. 322.5 mL/min; P_sinus 5.43 vs. 5.37, P_hv 4.11 vs. 4.07 mmHg) and "
    "reproduced the qualitative waveform pattern reported in the source "
    "work: hepatic arterial flow visibly pulsatile, portal and hepatic "
    "venous flow both nearly flat (Figures 2-3)."
)

d.add_heading("3.2 HABR is directionally necessary but quantitatively "
              "insufficient", level=3)
d.add_paragraph(
    "Anchored at POD1 (Rs_HA=0.828, L_HA=0.034; POD1 simulated PSV_HA=53.10 "
    "cm/s, RI_HA=0.610, matching the measured values by construction), "
    "applying HABR continuously across POD1-30 (as a first, naive test) "
    "explains 13.4%, 24.3%, and 30.6% of the measured PSV_HA decline at "
    "POD7, 14, and 30 respectively. A null model (Rs_HA frozen at its "
    "POD1 value, HABR never applied) instead predicts PSV_HA would "
    "slightly RISE as portal velocity falls (less downstream loading on "
    "the shared sinusoidal node) -- the wrong direction. HABR is "
    "therefore directionally necessary, but the continuously-applied "
    "version's rising 'explained fraction' over time is itself, as shown "
    "next, an artefact of misapplying an acute mechanism."
)
d.add_picture("HABR_Figure_1_with_without_comparison.png", width=Inches(6.2))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph(
    "Figure 4: Measured vs. continuously-applied HABR model vs. null "
    "(no HABR) model.")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True
d.add_picture("HABR_Figure_2_fraction_explained.png", width=Inches(4.6))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph(
    "Figure 5: Fraction of the measured PSV_HA decline reproduced by the "
    "continuously-applied HABR model.")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True

d.add_heading("3.3 Correcting for HABR's acute time course sharpens the "
              "conclusion", level=3)
d.add_paragraph(
    "Applying HABR only across its legitimate acute window (POD1-7) and "
    "freezing Rs_HA thereafter, the corrected model's simulated RI "
    "plateaus after POD7 (0.607, 0.607, 0.606), qualitatively matching "
    "the real RI's flat shape far better than the continuously-applied "
    "model (which kept drifting: 0.607, 0.601, 0.595). HABR explains "
    "13.4% of the POD7 decline (unchanged, since POD7 is its legitimate "
    "window) but only 6.9% and 4.7% of the larger POD14 and POD30 "
    "declines respectively -- essentially none of the decline beyond "
    "POD7 is attributable to HABR in this corrected framing (Table 2, "
    "Figure 6)."
)
d.add_picture("HABR_Figure_3_acute_correction.png", width=Inches(6.3))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph(
    "Figure 6: Measured vs. continuously-applied HABR model vs. the "
    "corrected acute-then-frozen model vs. the null model.")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True

t2 = d.add_table(rows=1, cols=4)
t2.style = "Light Grid Accent 1"
hdr = t2.rows[0].cells
for i, v in enumerate(["Day", "Measured decline (cm/s)",
                        "Corrected-model decline (cm/s)",
                        "% of measured decline explained"]):
    hdr[i].text = v
for row in [
    ("POD7", "6.08", "0.81", "13.4%"),
    ("POD14", "10.81", "0.75", "6.9%"),
    ("POD30", "14.59", "0.68", "4.7%"),
]:
    cells = t2.add_row().cells
    for i, v in enumerate(row):
        cells[i].text = v
cap = d.add_paragraph(
    "Table 2: PSV_HA decline from POD1, measured vs. the corrected "
    "(acute-then-frozen) HABR model.")
cap.runs[0].italic = True

d.add_heading("3.4 Candidate mechanisms for the residual decline", level=3)
d.add_paragraph(
    "Two real, literature-grounded candidates were identified for the "
    "substantial POD7-30 decline (8.51 of the cohort's 14.59 cm/s total "
    "POD1-30 fall) that HABR does not explain:"
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Systemic hyperdynamic-circulation normalization: ").bold = True
p.add_run(
    "the elevated cardiac output/reduced systemic vascular resistance "
    "state common in cirrhosis (Plevak et al., 1993) has a documented "
    "resolution timescale of days, not weeks -- reversing within 3-5 "
    "postoperative days in one adult cohort (n=57; pulse rate 103 to 72.6 "
    "beats/min from POD1 to POD3), with related normalization timescales "
    "of 4 days to 2 weeks cited elsewhere (Dashti et al., 2020)."
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Graft-regeneration-driven vessel-calibre dilution: ").bold = True
p.add_run(
    "graft mass increases substantially in the weeks after LDLT (~1.7-fold "
    "by 2 weeks in one paediatric LDLT cohort; Byun et al., 2016), which "
    "would dilute Doppler velocity at a fixed measurement point as vessel "
    "calibre grows with the regenerating graft, even at constant "
    "underlying flow -- and, being a pure calibre effect, would preserve "
    "RI just as a pressure-amplitude effect would. However, the "
    "quantitative regeneration time course in the literature is "
    "inconsistent: one adult right-lobe MRI volumetric study reports "
    "monotonic recipient-graft mass increase through day 30 (87%/101%/"
    "119% at POD7/14/30; Marcos et al., 2000) while another (n=62) "
    "reports the opposite shape -- peak regeneration ratio at 2 weeks, "
    "declining progressively through 6 months (Zhang et al., 2022). "
    "Neither is paediatric or left-lateral-segment specific, and "
    "paediatric LLS grafts are often sized close to or above the "
    "recommended graft-to-recipient weight ratio range, with reduction "
    "techniques used above roughly 4% specifically to avoid a large-for-"
    "size graft (Vargas and Goldaracena, 2024) -- the opposite of the "
    "classically undersized graft that motivates most compensatory-"
    "hypertrophy literature, so the expected magnitude of dilution in "
    "this specific population is genuinely uncertain, not merely "
    "unverified."
)
d.add_paragraph(
    "A timing argument favours graft-calibre dilution over systemic "
    "normalization as the better-supported candidate for the SUSTAINED "
    "POD7-30 decline specifically: hyperdynamic-circulation resolution is "
    "essentially complete well before POD7, while graft regeneration is "
    "documented to continue over weeks. Systemic normalization remains a "
    "plausible contributor to the POD1-7 window, alongside HABR. A single "
    "graft-calibre-growth mechanism is also more parsimonious than "
    "invoking two independent explanations for the simultaneously-"
    "declining PVV and PSV_HA. This is a partial, not a full, "
    "disambiguation -- it identifies which candidate is better supported "
    "for which window, without pinning down the magnitude of either."
)

# ---------------------------------------------------------------- Discussion
d.add_heading("Discussion", level=2)
d.add_paragraph(
    "This study makes a narrow, specific contribution: to our knowledge, "
    "the first quantitative test of the hepatic arterial buffer response "
    "against real serial paediatric post-LDLT Doppler data that "
    "explicitly respects HABR's known acute (minutes-to-hours) time "
    "course, rather than treating it as a mechanism that remains actively "
    "adjusting for a full postoperative month. The result is a sharper, "
    "more defensible conclusion than a naive continuous application would "
    "give: HABR reliably explains the DIRECTION of early hepatic arterial "
    "change and a modest, time-limited fraction of its magnitude (~13% at "
    "POD7), but essentially none of the substantial further decline from "
    "POD7 to POD30. This later, larger portion of the change requires a "
    "non-resistance, amplitude-scaling explanation, since it occurs while "
    "RI stays flat -- and the timing of two literature-grounded "
    "candidates (systemic hyperdynamic-circulation resolution, which is "
    "too fast; graft-regeneration-driven calibre dilution, which "
    "continues over the right timescale) favours the latter, though its "
    "magnitude for this specific left-lateral-segment paediatric "
    "population remains genuinely unresolved."
)
d.add_paragraph(
    "Several limitations bear on how these results should be read. "
    "First, the circulation is represented as a single lobe with lumped "
    "pi-filter elements, not the fuller multi-generation, left/right-"
    "lobe-split vascular tree used in some prior work by this group -- an "
    "appropriate simplification given the target data is only aggregate "
    "PSV/RI/PVV, not per-lobe or per-generation, but a real limitation if "
    "finer anatomical detail is later required. Second, several "
    "inertance/compliance ('shape') parameters were chosen for "
    "physiologically reasonable pulsatility rather than independently "
    "fitted or measured -- only the mean-flow-determining resistances are "
    "exactly, not approximately, matched to real target data. Third, the "
    "generic model's validation targets come from a different (adult-"
    "donor) case reported in unpublished prior work, not this specific "
    "cohort; the post-LDLT model is anchored to this cohort's own real "
    "portal diameter and Doppler data specifically to mitigate this, but "
    "the underlying pi-filter parameters (beyond the resistances fit "
    "directly to this cohort) are not independently re-derived for it. "
    "Fourth, the pre-transplant to POD1 transition -- by far the largest "
    "change in the dataset -- is not modelled here: it is a discrete "
    "organ-replacement event (the cirrhotic native liver is replaced by a "
    "healthy graft, a physically different vessel with different "
    "intrinsic properties), not a same-vessel flow perturbation, so a "
    "resistance-change interpretation does not straightforwardly apply "
    "across it. Fifth, the graft-to-recipient weight ratio for this "
    "specific cohort is unknown, so the plausibility and magnitude of the "
    "graft-dilution hypothesis cannot be directly assessed for these "
    "patients; the regeneration literature available is adult, not "
    "left-lateral-segment specific, and inconsistent in shape across "
    "studies. Sixth, all comparisons use group-level (mean +/- SD) data, "
    "not per-patient trajectories, and the model is not validated against "
    "individual patients' courses."
)
d.add_paragraph(
    "A practical observation for clinical Doppler surveillance follows "
    "from this work: RI_HA plateauing early (by POD7) while PSV_HA keeps "
    "falling is itself an interpretable signal -- it indicates that "
    "whatever continues to drive the PSV decline after that point is not "
    "a resistance/buffering phenomenon, and should prompt consideration "
    "of scale/calibre-related explanations (e.g. graft growth) rather "
    "than continued vasoregulatory adaptation. Directly resolving the "
    "residual mechanism identified here would require either serial "
    "vessel-diameter or graft-volumetry measurements in a comparable "
    "paediatric LLS-LDLT cohort, or a dedicated regeneration study in "
    "this specific graft type and recipient size range -- neither of "
    "which currently exists to our knowledge."
)

d.add_heading("Data, code, and ethics", level=2)
d.add_paragraph(
    "This is a secondary analysis of de-identified data reported in Chen "
    "et al. (2022), collected under the ethics approval described in that "
    "publication; no new human-subjects data were collected. Model code "
    "is available from the authors upon request."
)

d.add_heading("Conclusion", level=2)
d.add_paragraph(
    "A validated pi-filter lumped-parameter model of paediatric hepatic "
    "circulation, anchored to real post-LDLT Doppler data, shows that the "
    "hepatic arterial buffer response -- applied only within its "
    "physiologically legitimate acute window -- explains the direction "
    "but only a modest, time-limited fraction of the hepatic arterial "
    "normalization observed after paediatric living-donor liver "
    "transplantation. The substantial further change from POD7 to POD30 "
    "occurs while the resistive index remains flat, pointing to a "
    "non-resistance, amplitude-scaling mechanism; a literature-timing "
    "argument favours graft-regeneration-driven vessel-calibre dilution "
    "over systemic pressure normalization for this later window, though "
    "this is a partial, not complete, disambiguation and the magnitude of "
    "the effect for this specific patient population remains an open, "
    "testable question."
)

d.add_heading("References", level=2)
refs = [
    "Byun SH, Yang HS, Kim JH. Liver graft hyperperfusion in the early "
    "postoperative period promotes hepatic regeneration 2 weeks after "
    "living donor liver transplantation. Medicine (Baltimore). "
    "2016;95(46):e5404. doi:10.1097/MD.0000000000005404",
    "Chen X, Xiao H, Yang C, Chen J, Gao Y, Tang Y, Ji X. Doppler "
    "evaluation of hepatic hemodynamics after living donor liver "
    "transplantation in infants. Front Bioeng Biotechnol. "
    "2022;10:903385. doi:10.3389/fbioe.2022.903385",
    "Dashti SH, Kasraianfard A, Ebrahimi A, Nassiri-Toosi M, Pakshir MS, "
    "Rahimi M, Jafarian A. Hemodynamic changes and early recovery of "
    "liver graft function after liver transplantation. Int J Organ "
    "Transplant Med. 2020;11(1):1-7.",
    "Ho H, Sorrell K, Bartlett A, Hunter P. Modeling the hepatic arterial "
    "buffer response in the liver. Med Eng Phys. 2013;35:1053-8. "
    "doi:10.1016/j.medengphy.2012.10.008",
    "Ho H, Yu HB, Bartlett A. Computational simulations for the hepatic "
    "arterial buffer response after liver graft transplantation. "
    "Unpublished manuscript.",
    "Marcos A, Fisher RA, Ham JM, Shiffman ML, Sanyal AJ, Luketic VA, "
    "Sterling RK, Fulcher AS, Posner MP. Liver regeneration and function "
    "in donor and recipient after right lobe adult to adult living donor "
    "liver transplantation. Transplantation. 2000;69(7):1375-1379.",
    "Plevak DJ, Southorn PA, Narr BJ, Winter PB, Rettke SR. Hyperdynamic "
    "circulatory state after liver transplantation. Transplant Proc. "
    "1993;25(2):1837-8.",
    "Vargas PA, Goldaracena N. Alternatives to left lateral segment for "
    "pediatric liver transplantation, or required surgeon toolkit? "
    "Hepatobiliary Surg Nutr. 2024;13(2):376-378. doi:10.21037/hbsn-23-671",
    "Yu HB, Bartlett A, Hunter P, Ho H. Hybrid 0D-1D blood flow "
    "simulation for virtual liver transplantation in paediatric "
    "recipients. Unpublished manuscript.",
    "Zhang Y, Li B, He Q, Chu Z, Ji Q. Comparison of liver regeneration "
    "between donors and recipients after adult right lobe living-donor "
    "liver transplantation. Quant Imaging Med Surg. 2022;12(6):3184-3192. "
    "doi:10.21037/qims-21-1077",
]
for r in refs:
    d.add_paragraph(r)

out_path = "A Pi-Filter Model Test of the Hepatic Arterial Buffer Response After Paediatric LDLT.docx"
d.save(out_path)
print("Saved:", out_path)
