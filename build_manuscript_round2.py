"""
Manuscript, round 2 -- major revision responding to reviewer round 1.
Key changes (see Response_to_Reviewer_Round1.docx for the point-by-point
account): three HABR-application scenarios presented symmetrically rather
than declaring one "corrected"; RI-flatness reframed as a hypothesis with
an explicit equivalence-test result; explicit governing equations and a
full parameter table; "validated"->"calibrated"; "parameter-free"->
"fixed-coefficient (not fit to POD7-30 data)"; uncertainty ranges instead
of false-precision percentages; a new diameter-growth sensitivity analysis
(the headline result reverses sign under a modest, untested assumption);
graft-growth dilution reframed as a testable hypothesis, not a favoured
explanation; expanded competing-mechanisms discussion.
"""

import docx
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

d = docx.Document()

d.add_heading(
    "Testing the Hepatic Arterial Buffer Response Against Real "
    "Post-Transplant Doppler Data in Paediatric Liver Recipients: "
    "A Lumped-Parameter Model Study", level=1)

# ---------------------------------------------------------------- Abstract
d.add_heading("Abstract", level=2)
d.add_paragraph(
    "The hepatic arterial buffer response (HABR) -- the tendency of "
    "hepatic arterial flow to counteract changes in portal venous flow -- "
    "is often invoked to explain the fall in hepatic artery Doppler "
    "velocity after paediatric living-donor liver transplantation (LDLT). "
    "We built a lumped-parameter ('pi-filter') hepatic circulation model, "
    "calibrated it against independent literature targets for a generic "
    "paediatric post-transplant circulation, then anchored it to a real "
    "cohort of 41 infants after left-lateral-segment LDLT for biliary "
    "atresia (Chen et al., 2022), using their own reported portal vein "
    "diameter and flow formula. We compare three ways of applying a "
    "fixed-coefficient HABR relationship (coefficients from prior "
    "unpublished electrical-analog modelling of this same clinical "
    "scenario, not re-fit here): continuously across postoperative day "
    "(POD) 1-30; applied only across POD1-7 with arterial resistance then "
    "held fixed (motivated, not proven, by the cohort's resistive index "
    "[RI] being numerically flat from POD7 onward); and a null scenario "
    "with no HABR at all. All three bracket a wide range: HABR reproduces "
    "0% (null) to approximately 13-31% (continuous) of the measured fall "
    "in hepatic artery peak systolic velocity (PSV), with wide "
    "uncertainty intervals once sampling variability is propagated. An "
    "equivalence test on RI across POD7-30, using only published summary "
    "statistics, cannot rule out a small ongoing change, so 'RI is flat' "
    "is reported as a hypothesis, not a proof that resistance adaptation "
    "has ended. A sensitivity analysis shows this whole quantitative "
    "picture is fragile: because portal vein diameter is only reported at "
    "pre-transplant and POD1 in the source cohort, we must assume it does "
    "not change thereafter, and even a modest (10%) assumed diameter "
    "increase by POD30 reverses the sign of the headline result. Two "
    "literature-grounded, non-HABR candidates for whatever residual "
    "decline exists -- systemic haemodynamic normalization (fast, days) "
    "and graft-regeneration-driven vessel-calibre dilution (slower, "
    "weeks) -- are presented as testable hypotheses, not identified "
    "mechanisms; the available data cannot distinguish between them. This "
    "is a modelling exercise that quantifies how much is, and is not, "
    "knowable about HABR's contribution from currently available data, "
    "rather than a claim to have measured that contribution precisely."
)

d.add_heading("Keywords", level=3)
d.add_paragraph(
    "hepatic arterial buffer response; liver transplantation; paediatric; "
    "Doppler ultrasound; lumped-parameter model; sensitivity analysis; "
    "biliary atresia"
)

# ------------------------------------------------------------ Introduction
d.add_heading("Introduction", level=2)
d.add_paragraph(
    "The hepatic arterial buffer response (HABR) is an intrinsic hepatic "
    "regulatory mechanism, first described by Lautt: a fall in portal "
    "venous flow provokes a rise in hepatic arterial flow, and vice "
    "versa, mediated by washout of adenosine in the periportal space of "
    "Mall (Eipel, Abshagen and Vollmar, 2010). This washout process "
    "equilibrates quickly -- typically within minutes to a few hours -- "
    "but it is a continuously-coupled feedback relationship between "
    "portal flow and periportal adenosine concentration, not a single "
    "event that occurs once and then stops: whenever portal flow changes "
    "again, however much later, the same fast mechanism is available to "
    "respond again. This distinction -- fast equilibration versus a "
    "one-off response -- matters directly for how HABR can legitimately "
    "be applied to a full postoperative month, and is addressed "
    "explicitly in this study (Section 2.5)."
)
d.add_paragraph(
    "HABR is clinically relevant after partial hepatectomy and liver "
    "transplantation, where portal flow changes are common and altered "
    "hepatic arterial flow has been linked to arterial thrombosis risk in "
    "liver grafts. Prior work from this group modelled HABR using an "
    "electrical-analog ('pi-filter') lumped-parameter representation of "
    "the portal, hepatic arterial, and hepatic venous circulations, with "
    "an empirical quadratic regulation function relating hepatic arterial "
    "to portal flow change (Ho, Sorrell, Bartlett and Hunter, 2013). This "
    "was subsequently applied, in unpublished draft form, to an "
    "adult-to-child left-lateral-segment (LLS) liver transplantation "
    "scenario matching real paediatric recipient pressures and flows (Yu, "
    "Bartlett, Hunter and Ho, unpublished manuscript; Ho, Yu and Bartlett, "
    "unpublished submitted manuscript). We rely on these two unpublished "
    "sources for specific real target pressure/flow values because no "
    "equivalent published dataset for this exact clinical scenario "
    "(adult-donor LLS graft into a small child) was located; this "
    "dependence is a genuine limitation, addressed explicitly in the "
    "Discussion."
)
d.add_paragraph(
    "Separately, Chen et al. (2022) report serial hepatic artery and "
    "portal vein Doppler measurements in 41 infants (4-18 months, biliary "
    "atresia) before and after LLS-LDLT, at POD1, 7, 14, and 30. Hepatic "
    "artery PSV and RI both fall over this month, which the authors "
    "attribute qualitatively to HABR, without a quantitative mechanistic "
    "test."
)
d.add_paragraph(
    "This study combines these two strands, with an explicit focus on "
    "what can and cannot be concluded from the available data, rather "
    "than on producing a single best-fit number. We ask three questions. "
    "First, over what part of the POD1-30 trajectory can the fixed-"
    "coefficient HABR relationship be legitimately applied, given its "
    "known fast-but-continuous kinetics? Second, comparing that "
    "application against a continuous-application scenario and a null "
    "scenario, how much of the measured trajectory does HABR reproduce, "
    "with what uncertainty? Third, how sensitive is this conclusion to "
    "assumptions -- particularly the untested assumption that portal "
    "vein calibre does not change after POD1 -- that the available data "
    "cannot itself resolve?"
)

# ------------------------------------------------------------------ Methods
d.add_heading("Methods", level=2)

d.add_heading("2.1 Dataset", level=3)
d.add_paragraph(
    "Chen et al. (2022; doi:10.3389/fbioe.2022.903385) is a retrospective "
    "study of 41 infants (22 male, 19 female; median age 5 months, range "
    "4-18) with biliary atresia undergoing LLS-LDLT, with uncomplicated "
    "postoperative courses. Doppler measurements -- hepatic artery PSV "
    "and RI, portal vein velocity (PVV), and (at pre-transplant and POD1 "
    "only) portal vein diameter -- were taken pre-transplant and at POD1, "
    "7, 14, and 30 (Table 1)."
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

d.add_heading("2.2 Pi-filter lumped element and generic circulation model", level=3)
d.add_paragraph(
    "The circulation is represented with the lumped element used in this "
    "group's prior modelling: a two-port 'pi-filter' with a series "
    "inductor (L, inertance) and resistor (Rs) between the ports, and an "
    "identical shunt branch (a capacitor C in series with a resistor Rp, "
    "to a common reference) at each port. A single-lobe topology has "
    "hepatic arterial (HA) and portal venous (PV) pi-filters both feeding "
    "a shared sinusoidal node, draining through a hepatic venous (HV) "
    "pi-filter to a fixed inferior-vena-cava reference pressure P_IVC "
    "(Figure 1). Only the output-side shunt of each source-driven branch "
    "matters dynamically, giving five state variables and governing "
    "equations (forward-Euler time integration, 400 steps per cardiac "
    "cycle, periodic steady state defined as a relative change below "
    "1e-4 in the Q_HA waveform between consecutive cycles):"
)
eq = d.add_paragraph()
eq.add_run(
    "L_HA dQ_HA/dt = P_HA(t) - Rs_HA*Q_HA - P_sinus\n"
    "L_PV dQ_PV/dt = P_PV(t) - Rs_PV*Q_PV - P_sinus\n"
    "C_sinus dP_sinus/dt = Q_HA + Q_PV - Q_HV - P_sinus/Rp_sinus\n"
    "L_HV dQ_HV/dt = P_sinus - Rs_HV*Q_HV - P_hv\n"
    "C_hv dP_hv/dt = Q_HV - (P_hv - P_IVC)/Rp_hv_out"
).italic = True
d.add_paragraph(
    "P_HA(t) = P_HA_mean + P_HA_amp*sin(2*pi*t/T) (T = 60/HR); P_PV(t) is "
    "constant in the generic configuration (Section 2.2) or a prescribed, "
    "time-point-specific value in the post-LDLT configuration (Section "
    "2.4). This was first calibrated in a generic (non-transplant, "
    "healthy/typical paediatric) configuration against independent real "
    "target data from Ho, Yu and Bartlett's unpublished manuscript on "
    "this same adult-to-child LLS scenario (portal driving pressure 13 "
    "mmHg, mean arterial pressure 57.5 mmHg [range 42.4-72.6], sinusoidal "
    "pressure 5.37 mmHg, hepatic venous pressure 4.07 mmHg, portal flow "
    "300 mL/min, hepatic arterial flow 31.93 mL/min, hepatic venous flow "
    "322.5 mL/min). We describe this step as CALIBRATION, not validation: "
    "because this configuration is linear, the three series resistances "
    "(Rs_PV, Rs_HA, Rs_HV) were solved exactly via Ohm's law on the "
    "time-averaged circuit from these same target values -- the "
    "resulting agreement (within 2%, Figure 3; the residual gap is Euler "
    "truncation error and a small continuous leak through Rp_sinus, not "
    "a fitting error) is close by construction, not an independent test "
    "against held-out data. The inertance/compliance ('shape') "
    "parameters (Table 3) were chosen, not derived or fit, for "
    "physiologically reasonable pulsatility."
)
d.add_picture("HealthyInfant_Figure_1_schematic.png", width=Inches(6.0))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph("Figure 1: Pi-filter circulation model schematic.")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True
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
    "Figure 3: Generic model mean flows vs. calibration targets (all "
    "within 2% by construction -- see text).")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True

d.add_heading("2.2.1 Relating simulated flow to Doppler-derived indices", level=3)
d.add_paragraph(
    "No hepatic-artery cross-sectional area is assumed or used anywhere "
    "in this model. Q_HA is not converted to a velocity via an assumed "
    "area; instead, Rs_HA and L_HA are calibrated directly so that the "
    "model's Q_HA waveform (in whatever internal units the ODE system "
    "uses) numerically matches the cohort's measured PSV_HA and RI_HA at "
    "POD1 (Section 2.4) -- Q_HA is therefore best understood as a "
    "directly-calibrated proxy for Doppler velocity, not an independently "
    "derived physical flow rate. PSV, end-diastolic velocity (EDV), and "
    "RI are extracted from the periodic Q_HA waveform exactly as they "
    "would be from a real Doppler trace: PSV = max(Q_HA) over the last "
    "converged cycle, EDV = min(Q_HA), RI = (PSV-EDV)/PSV. Because only "
    "two targets (PSV, RI) constrain the fit at POD1, and both are "
    "dimensionless ratios or a single velocity scale, this calibration "
    "does not by itself establish what a 'unit' of Q_HA corresponds to "
    "in mL/min or any other physical flow unit -- a limitation returned "
    "to in Section 2.4 and the Discussion, since Q_PV (Section 2.4) IS "
    "computed in explicit mL/min-scale units, and the two are summed "
    "directly in the sinusoidal-node mass balance above without a common "
    "verified physical basis."
)

d.add_heading("2.3 Fixed-coefficient HABR relationship", level=3)
d.add_paragraph(
    "HABR is represented, as in the prior work it is drawn from, by a "
    "discrete, between-state resistance-update rule: changeIha = "
    "0.0007102*x^2 + 0.5492*x, where x is the percent DECREASE in portal "
    "flow relative to a reference state and changeIha is the resulting "
    "percent decrease in hepatic arterial flow. These coefficients are "
    "imported from prior unpublished work and are NOT re-estimated or "
    "re-fit to any part of this cohort's data at any point -- we refer "
    "to this throughout as a 'fixed-coefficient' HABR relationship, not "
    "a 'parameter-free' one, since other parts of the model (Rs_HA, "
    "L_HA, the assumed pressure amplitude, the assumed constant portal "
    "diameter) ARE calibrated or assumed, as detailed below and in Table 3."
)

d.add_heading("2.4 Post-LDLT model anchoring", level=3)
d.add_paragraph(
    "Portal inflow Q_PV(t) is a prescribed input rather than an "
    "independently simulated state, justified by the generic model's own "
    "result that PV flow varies under 0.2% across a cardiac cycle. "
    "Q_PV(t) is computed from this cohort's own portal vein diameter and "
    "PVV via Chen et al.'s own reported formula, PVF = pi*r^2*0.57*PVV*60 "
    "(r = diameter/2 in cm, PVV in cm/s). We flag explicitly that this "
    "formula, as given in the source paper and reproduced here, yields a "
    "quantity with units of mL/min (cm^2 * cm/s * s/min), not mL/min per "
    "100 g graft as labelled by the source paper -- no graft-mass term "
    "appears anywhere in the formula. Graft weight was not reported for "
    "this cohort and was not otherwise available to us, so we cannot "
    "resolve whether this is a units error in the source presentation or "
    "an intended, unnormalized quantity mislabelled. This ambiguity is "
    "inherited from the source paper, not introduced here. It is "
    "partially, but not fully, mitigated by the fact that only the "
    "PERCENT CHANGE in Q_PV(t) (not its absolute value) drives the HABR "
    "relationship, which is invariant to a fixed scaling convention -- "
    "however, Q_PV(t)'s absolute value IS used directly, summed with "
    "Q_HA, in the sinusoidal-node mass balance (Section 2.2), and Q_HA's "
    "scale is fixed by an entirely separate calibration (Section 2.2.1) "
    "with no verified common physical basis. We therefore treat the "
    "relative WEIGHT of the Q_PV forcing term in the sinusoidal balance "
    "as an uncertain modelling choice and report, in the Results, how "
    "much this affects the conclusions."
)
d.add_paragraph(
    "Diameter is only reported at pre-transplant (0.44 cm) and POD1 "
    "(0.46 cm); it is held at the POD1 value for POD7/14/30 in the main "
    "analysis, since no later measurement exists. Across the pre-op to "
    "POD1 transition, where diameter IS reported, area increased 9.3% "
    "while velocity increased 82.5%, combining to a 99.4% flow increase "
    "matching the reported 97.9% closely -- this shows velocity change "
    "dominated over that specific transition, but does NOT establish "
    "that diameter stays constant over the (physiologically quite "
    "different) POD1-30 window, when graft regeneration is actively "
    "occurring. Section 2.6 describes a sensitivity analysis directly "
    "testing this assumption rather than relying on it uncritically."
)
d.add_paragraph(
    "Rs_HA and L_HA are calibrated once, at POD1, against this cohort's "
    "own measured PSV_HA and RI_HA (Section 2.2.1); the HA pulse "
    "amplitude is held fixed at the generic model's literature value "
    "(15.1 mmHg). Reusing the generic model's own L_HA verbatim (rather "
    "than re-fitting it for this cohort) produced a fitted pulse "
    "amplitude of 440 mmHg -- physiologically implausible -- because "
    "that L_HA was tuned for the generic model's own Rs_HA scale, "
    "roughly 100-fold different from this cohort's fitted value; L_HA is "
    "therefore re-fit here instead, alongside Rs_HA, at POD1 only. This "
    "is the only fitting step used to obtain the POD1 anchor; PSV_HA and "
    "RI_HA at all subsequent time points are model output under each of "
    "the three scenarios below, not further fit."
)

d.add_heading("2.5 Three HABR-application scenarios", level=3)
d.add_paragraph(
    "Because HABR's adenosine-washout kinetics describe a continuously-"
    "coupled feedback relationship rather than a one-off event (Section "
    "1), its fast equilibration time does not, by itself, justify "
    "confining its application to any particular window of the "
    "postoperative month -- it remains available to respond to portal "
    "flow changes at any point. We therefore present three scenarios as "
    "alternative, equally-motivated possibilities, not as one 'correct' "
    "model with the others as baselines:"
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Continuous: ").bold = True
p.add_run(
    "Rs_HA is re-set at every time point from the HABR relationship, "
    "using the percent portal-flow change from POD1 to that time point -- "
    "consistent with HABR remaining available to respond throughout."
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Acute-then-frozen: ").bold = True
p.add_run(
    "Rs_HA is set from the HABR relationship once, using the POD1-to-"
    "POD7 portal-flow change, then held fixed for POD14/30. This is "
    "motivated by an observation, not a proof (Section 2.6): the "
    "cohort's mean RI_HA is numerically flat (0.59) from POD7 through "
    "POD30. If this reflects a real absence of further resistance "
    "change, HABR's own logic implies no further Rs_HA adjustment would "
    "occur after POD7 either -- but Section 2.6 tests whether the data "
    "can actually support this premise."
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Null: ").bold = True
p.add_run(
    "Rs_HA is frozen at its POD1 value throughout; only Q_PV(t)'s "
    "passive effect on the shared sinusoidal node is allowed to act. "
    "This isolates the circuit's behaviour with HABR entirely absent."
)
d.add_paragraph(
    "In all three, Q_PV(t) itself always updates to each time point's "
    "real measured value."
)

d.add_heading("2.6 Testing whether RI is really flat", level=3)
d.add_paragraph(
    "RI is a ratio of waveform extremes, not a direct measurement of "
    "vascular resistance, and is additionally influenced by arterial "
    "compliance, downstream loading, waveform morphology, and measurement "
    "variability -- its numerical flatness alone does not prove "
    "resistance-mediated adaptation has ended. We tested this "
    "quantitatively using only the published summary statistics (mean, "
    "SD, n=41 at each time point): a two-sample Welch's t-test (and 95% "
    "confidence interval on the mean difference) between each pair of "
    "time points. This is a conservative, unpaired approximation -- the "
    "real cohort is repeated-measures on the same 41 patients, and a "
    "properly paired analysis (not possible without per-patient data) "
    "would have more power to detect small true differences, since "
    "between-subject variability would cancel out."
)

d.add_heading("2.7 Uncertainty on the 'fraction explained'", level=3)
d.add_paragraph(
    "Rather than reporting the ratio of model-predicted to measured "
    "PSV_HA decline as a single deterministic percentage, we propagate "
    "the sampling uncertainty of the two compared means (POD1 and each "
    "later time point) via Monte Carlo (200,000 draws per comparison, "
    "each mean drawn from a normal distribution with the reported SD/"
    "sqrt(41)) and report the resulting 95% interval alongside the point "
    "estimate. This still likely understates the true uncertainty, since "
    "it does not capture parameter uncertainty in the model itself, only "
    "sampling uncertainty in the two measured means being compared."
)

d.add_heading("2.8 Sensitivity to the constant-portal-diameter assumption", level=3)
d.add_paragraph(
    "Since Chen et al. (2022) report portal vein diameter only at "
    "pre-transplant and POD1, and this study's own candidate residual "
    "mechanism (Section 3.6) is precisely a hypothesised change in "
    "vessel calibre, holding diameter constant for POD7-30 is not a "
    "neutral simplifying assumption -- it directly assumes away the "
    "effect under investigation for the portal side of the circuit. We "
    "therefore repeated the continuous-HABR scenario's POD30 calculation "
    "under a range of assumed portal-diameter growth by POD30 (0%, 10%, "
    "20%, 30%, 40%, linearly interpolated across POD7/14/30), keeping "
    "every other parameter fixed."
)

d.add_heading("2.9 Model parameters", level=3)
t3 = d.add_table(rows=1, cols=4)
t3.style = "Light Grid Accent 1"
hdr = t3.rows[0].cells
for i, v in enumerate(["Parameter", "Value", "Units", "Source"]):
    hdr[i].text = v
param_rows = [
    ("HR", "130", "beats/min", "assumed, representative infant heart rate"),
    ("P_PV_src (generic)", "13.0", "mmHg", "Ho/Yu/Bartlett unpublished target"),
    ("P_HA_mean", "57.5", "mmHg", "Ho/Yu/Bartlett unpublished target"),
    ("P_HA_amp", "15.1", "mmHg", "Ho/Yu/Bartlett unpublished target; held fixed post-LDLT"),
    ("P_IVC", "2.0", "mmHg", "assumed (not reported in source)"),
    ("Rs_PV", "1.526", "model units", "solved exactly from generic targets; reused post-LDLT"),
    ("Rs_HV", "0.242", "model units", "solved exactly from generic targets; reused post-LDLT"),
    ("Rp_hv_out", "0.385", "model units", "solved exactly from generic targets; reused post-LDLT"),
    ("Rs_HA (generic)", "97.96", "model units", "solved exactly from generic targets; NOT reused post-LDLT (see 2.4)"),
    ("Rs_HA (POD1, post-LDLT)", "0.828", "model units", "fit to real POD1 PSV_HA/RI_HA"),
    ("L_HA (generic)", "2.0", "model units", "assumed; NOT reused post-LDLT (see 2.4)"),
    ("L_HA (POD1, post-LDLT)", "0.0344", "model units", "fit to real POD1 PSV_HA/RI_HA"),
    ("L_PV, L_HV", "0.01, 0.02", "model units", "assumed"),
    ("C_sinus, C_hv", "2.0, 2.0", "model units", "assumed"),
    ("Rp_sinus", "500", "model units", "assumed"),
    ("Portal diameter (POD1)", "0.46", "cm", "Chen et al. 2022; held fixed POD7-30 in main analysis"),
    ("PV velocity-to-flow factor", "0.57", "dimensionless", "Chen et al. 2022"),
    ("Integration", "forward Euler, 400 steps/cycle", "-", "-"),
    ("Convergence criterion", "<1e-4 relative change, consecutive cycles", "-", "-"),
]
for row in param_rows:
    cells = t3.add_row().cells
    for i, v in enumerate(row):
        cells[i].text = v
cap = d.add_paragraph(
    "Table 3: Full model parameter list. 'Model units' are the ODE "
    "system's own internal units; Q_HA is calibrated directly against "
    "Doppler cm/s measurements (Section 2.2.1) and Q_PV against Chen et "
    "al.'s formula (Section 2.4) -- the two are not on an independently "
    "verified common physical basis (Section 2.4).")
cap.runs[0].italic = True

d.add_heading("2.10 Candidate residual mechanisms: literature search", level=3)
d.add_paragraph(
    "A literature search (PubMed/EuropePMC, citations verified against "
    "primary sources or the EuropePMC metadata API before use) was "
    "conducted for real, plausible, non-HABR mechanisms that could "
    "contribute to a continued fall in hepatic artery Doppler velocity "
    "over the postoperative month. These are presented in Results/"
    "Discussion as testable hypotheses for future work, not as "
    "identified or favoured mechanisms -- the available data cannot "
    "distinguish between them, nor rule out mechanisms not considered "
    "here (Section 3.6)."
)

# -------------------------------------------------------------------- Results
d.add_heading("Results", level=2)

d.add_heading("3.1 Generic model calibration", level=3)
d.add_paragraph(
    "The generic pi-filter model reproduced the independent calibration "
    "targets within 2% by construction (Q_PV 297.5 vs. 300, Q_HA 31.9 "
    "vs. 31.9, Q_HV 328.6 vs. 322.5 mL/min; P_sinus 5.43 vs. 5.37, P_hv "
    "4.11 vs. 4.07 mmHg; Figure 3) and reproduced the qualitative "
    "waveform pattern reported in the source work: hepatic arterial flow "
    "visibly pulsatile, portal and hepatic venous flow both nearly flat "
    "(Figure 2)."
)

d.add_heading("3.2 Three scenarios bracket a wide range, not a single answer", level=3)
d.add_paragraph(
    "Anchored at POD1 (Rs_HA=0.828, L_HA=0.034; simulated PSV_HA=53.10 "
    "cm/s, RI_HA=0.610, matching measured values by construction), the "
    "three scenarios diverge substantially by POD30 (Table 2, Figure 4). "
    "The null scenario predicts PSV_HA would slightly RISE (53.10 to "
    "53.27 cm/s) as portal velocity falls -- the wrong direction "
    "relative to the measured fall. Both HABR scenarios move in the "
    "correct direction, but by very different amounts: the continuous "
    "scenario reaches 48.63 cm/s at POD30 (a 30% point estimate of the "
    "measured decline, Section 3.4), while the acute-then-frozen "
    "scenario reaches only 52.42 cm/s (a 5% point estimate). We do not "
    "identify either HABR scenario as more 'correct' than the other on "
    "mechanistic grounds alone; Section 3.3 examines whether the RI data "
    "used to motivate the acute-then-frozen scenario can bear that "
    "weight."
)
d.add_picture("HABR_Figure_3_acute_correction.png", width=Inches(6.3))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph(
    "Figure 4: Measured vs. all three scenarios (continuous, acute-then-"
    "frozen, null).")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True

t2 = d.add_table(rows=1, cols=5)
t2.style = "Light Grid Accent 1"
hdr = t2.rows[0].cells
for i, v in enumerate(["Day", "Measured PSV (cm/s)", "Continuous",
                        "Acute-then-frozen", "Null"]):
    hdr[i].text = v
for row in [
    ("POD1", "53.10", "53.10", "53.10", "53.10"),
    ("POD7", "47.02", "52.29", "52.29", "53.13"),
    ("POD14", "42.29", "50.48", "52.35", "53.20"),
    ("POD30", "38.51", "48.63", "52.42", "53.27"),
]:
    cells = t2.add_row().cells
    for i, v in enumerate(row):
        cells[i].text = v
cap = d.add_paragraph("Table 2: Simulated PSV_HA under all three scenarios vs. measured.")
cap.runs[0].italic = True

d.add_heading("3.3 RI-flatness is a hypothesis, not a demonstrated result", level=3)
d.add_paragraph(
    "An unpaired Welch's t-test on the published summary statistics "
    "finds no detectable difference between RI_HA at POD7, POD14, and "
    "POD30 (all pairwise p=1.00 to 3 decimal places, since the reported "
    "means round identically to 0.59 at all three time points) -- but "
    "the 95% confidence interval on the POD7-vs-POD30 difference is "
    "[-0.010, +0.010], meaning a true difference as large as the real, "
    "independently-observed POD1-to-POD7 change (0.020, itself only "
    "marginally significant at p=0.032 by the same unpaired method) "
    "cannot be excluded by these summary statistics alone. A properly "
    "paired analysis, not possible without individual patient "
    "trajectories, would likely have more power to detect a genuine "
    "small change. We therefore describe RI as 'not detectably changing' "
    "rather than 'complete' or 'finished,' and treat the acute-then-"
    "frozen scenario as a hypothesis worth exploring, not a demonstrated "
    "correction to the continuous scenario."
)

d.add_heading("3.4 Uncertainty on the fraction of decline reproduced", level=3)
d.add_paragraph(
    "Point estimates for the percentage of the measured PSV_HA decline "
    "reproduced, with 95% intervals from Monte Carlo propagation of the "
    "compared means' sampling uncertainty alone (Section 2.7; this is a "
    "lower bound on the true uncertainty): continuous scenario, "
    "approximately 13% [6%, 77%] at POD7, 24% [16%, 52%] at POD14, 31% "
    "[22%, 49%] at POD30; acute-then-frozen scenario, approximately 13% "
    "[6%, 76%] at POD7, 7% [4%, 15%] at POD14, 5% [3%, 7%] at POD30. The "
    "POD7 interval in particular is wide enough (6-77%) that little can "
    "be concluded about the precise magnitude at that time point from "
    "group means alone; the point estimates should not be read with the "
    "false precision of the single-decimal percentages used in an "
    "earlier draft of this analysis."
)

d.add_heading("3.5 The headline result is highly sensitive to the untested "
              "diameter assumption", level=3)
d.add_paragraph(
    "Repeating the continuous scenario's POD30 calculation under assumed "
    "portal-diameter growth (Section 2.8) shows the '% of decline "
    "explained' result is not robust: at 0% assumed growth (the "
    "assumption used above, since no later measurement exists), HABR "
    "explains approximately 31% of the decline; at just 10% assumed "
    "diameter growth by POD30, the sign REVERSES (-11%, i.e. the model "
    "would then predict PSV_HA changing in the wrong direction); at 20-"
    "40% growth, the mismatch grows substantially (Figure 7). This is "
    "not a minor caveat: it shows that resolving HABR's real "
    "contribution to this cohort's PSV_HA trajectory requires serial "
    "vessel-diameter data that does not currently exist, and that the "
    "specific percentages reported above are conditional on an "
    "assumption (constant portal diameter after POD1) that cannot be "
    "verified with the available data and is not even directionally "
    "safe."
)
d.add_picture("HABR_Figure_7_diameter_sensitivity.png", width=Inches(5.5))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph(
    "Figure 7: The headline '% of decline explained by HABR' result as a "
    "function of an assumed, untested portal-diameter-growth rate.")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True

d.add_heading("3.6 Candidate mechanisms for any residual decline: testable "
              "hypotheses, not identified mechanisms", level=3)
d.add_paragraph(
    "Whatever fraction of the decline HABR does not explain requires "
    "some other contributor. We identify two literature-grounded "
    "candidates, presented here explicitly as hypotheses for future "
    "testing, not as established or favoured explanations:"
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Systemic haemodynamic normalization: ").bold = True
p.add_run(
    "the elevated cardiac output/reduced systemic vascular resistance "
    "state common in cirrhosis (Plevak et al., 1993) has a documented "
    "resolution timescale of days -- reversing within 3-5 postoperative "
    "days in one adult cohort (n=57; pulse rate 103 to 72.6 beats/min "
    "from POD1 to POD3), with related timescales of 4 days to 2 weeks "
    "cited elsewhere (Dashti et al., 2020)."
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Graft-regeneration-driven vessel-calibre dilution: ").bold = True
p.add_run(
    "graft mass increases substantially over weeks after LDLT (~1.7-fold "
    "by 2 weeks in one paediatric LDLT cohort; Byun et al., 2016). If "
    "arterial or portal calibre grows with the regenerating graft, "
    "Doppler velocity at a fixed measurement point would fall even at "
    "constant flow, and RI would be preserved, exactly as demonstrated "
    "in Section 3.5. However, quantitative regeneration data are "
    "inconsistent across the (adult, non-left-lateral-segment) studies "
    "located: one MRI volumetric study reports monotonic mass increase "
    "through day 30 (Marcos et al., 2000) while another reports the "
    "opposite shape, peaking at 2 weeks then declining (Zhang et al., "
    "2022). Graft volume does not necessarily translate into proportional "
    "growth of the hepatic artery specifically at the Doppler sampling "
    "site, particularly near a surgical anastomosis. Paediatric LLS "
    "grafts are additionally often sized close to or above the "
    "recommended graft-to-recipient weight ratio, with reduction "
    "techniques used above roughly 4% specifically to avoid a large-for-"
    "size graft (Vargas and Goldaracena, 2024) -- the opposite of the "
    "classically undersized graft that motivates compensatory-hypertrophy "
    "literature, so even the DIRECTION of expected calibre change in this "
    "specific population is not established, let alone its magnitude."
)
d.add_paragraph(
    "Other plausible, unmodelled contributors that this study cannot "
    "rule out include: changes in systemic cardiac output and arterial "
    "pressure amplitude not captured by the fixed pulse-amplitude "
    "assumption; postoperative periportal or graft oedema; arterial "
    "spasm; anastomotic geometry and any residual stenosis short of a "
    "clinically flagged complication; variation in Doppler insonation "
    "angle or sampling location between visits; sedation; and changes in "
    "heart rate. Early post-transplant Doppler indices are well known to "
    "vary for reasons beyond intrinsic haemodynamics, and RI is normally "
    "interpreted alongside the full waveform and clinical context, not "
    "as an isolated number. None of these were assessed here, and this "
    "study does not claim to have enumerated or excluded them."
)
d.add_paragraph(
    "A timing argument -- haemodynamic normalization resolves within "
    "days, graft regeneration continues over weeks -- offers a plausible "
    "basis for expecting graft-calibre change to matter more for the "
    "SUSTAINED POD7-30 decline specifically, and normalization to matter "
    "more for POD1-7 (alongside HABR). This is offered as a hypothesis "
    "motivating future measurement, not a conclusion: Section 3.5 shows "
    "directly that this project's own model results are not robust "
    "enough to the diameter assumption to adjudicate between candidate "
    "mechanisms on quantitative grounds alone."
)

# ---------------------------------------------------------------- Discussion
d.add_heading("Discussion", level=2)
d.add_paragraph(
    "Primary conclusion: the fixed-coefficient HABR relationship, "
    "applied in any of the three scenarios tested, reproduces the "
    "correct DIRECTION of the observed hepatic arterial PSV decline (the "
    "null scenario does not), but the magnitude it reproduces ranges "
    "widely (0-31% by POD30 across scenarios and their uncertainty "
    "intervals) and is highly sensitive to an untested assumption about "
    "portal vessel calibre. Secondary conclusion: the available data -- "
    "group-level Doppler indices with no serial vessel-diameter or "
    "graft-volumetry measurements -- do not identify what mechanism is "
    "responsible for whatever HABR does not explain. Exploratory "
    "hypothesis: graft- and vessel-calibre growth may contribute, "
    "alongside systemic haemodynamic normalization and other unmodelled "
    "factors, and this should be tested directly with serial calibre, "
    "volumetry, pressure, and flow measurements in a comparable cohort, "
    "not inferred indirectly as done here."
)
d.add_paragraph(
    "Several limitations bear on how these results should be read. The "
    "circulation is represented as a single lobe with lumped elements, "
    "not the fuller multi-generation vascular tree used in some prior "
    "work by this group. Several inertance/compliance parameters are "
    "assumed, not fit or measured. The generic model's calibration "
    "targets, and the HABR coefficients themselves, come from two "
    "unpublished manuscripts rather than peer-reviewed published "
    "sources; we searched for published alternatives providing "
    "equivalent real paediatric LLS-LDLT pressure/flow data and did not "
    "find one, but this dependency remains a genuine weakness of the "
    "evidentiary basis, not a fully resolved limitation. The pre-"
    "transplant to POD1 transition -- by far the largest change in the "
    "dataset -- is not modelled, since it is a discrete organ-replacement "
    "event rather than a same-vessel flow perturbation. Graft-to-"
    "recipient weight ratio is unknown for this cohort. The Q_HA and "
    "Q_PV state variables are calibrated/computed via different, "
    "independently unverified routes and are summed directly in the "
    "sinusoidal-node mass balance without a demonstrated common physical "
    "basis (Section 2.2.1, 2.4) -- Section 3.5's sensitivity result "
    "shows this matters quantitatively, not just formally. All "
    "comparisons use group-level (mean +/- SD) data; no per-patient "
    "trajectory or individual-level validation was possible."
)
d.add_paragraph(
    "A practical observation for clinical Doppler surveillance: RI_HA "
    "not detectably changing after POD7 while PSV_HA continues to fall "
    "is, at minimum, worth further study as a possible signal that the "
    "later decline reflects something other than continued resistance "
    "adaptation -- though Section 3.3 shows this cannot be confirmed "
    "from group summary statistics, and Section 3.5 shows that even the "
    "qualitative story is not robust to a plausible but unmeasured "
    "change in vessel calibre. We would not currently recommend using "
    "this framework for individual-patient interpretation; its value at "
    "this stage is in showing what additional measurements (serial "
    "vessel diameter chief among them) would be needed to make such "
    "interpretation possible."
)

d.add_heading("Data, code, and ethics", level=2)
d.add_paragraph(
    "This is a secondary analysis of de-identified data reported in Chen "
    "et al. (2022), collected under the ethics approval described in "
    "that publication; no new human-subjects data were collected. Model "
    "code is available from the authors on request; establishing a "
    "public repository is intended for a future revision."
)

d.add_heading("Conclusion", level=2)
d.add_paragraph(
    "A calibrated pi-filter lumped-parameter model, anchored to real "
    "post-LDLT paediatric Doppler data, shows that a fixed-coefficient "
    "hepatic arterial buffer response relationship reproduces the "
    "correct direction of the observed hepatic arterial velocity "
    "decline, but its quantitative contribution is uncertain and highly "
    "sensitive to an unmeasured vessel-calibre assumption -- to the "
    "point that a plausible 10% diameter change would reverse the "
    "result's sign. Framing HABR's contribution to this trajectory as a "
    "precisely-quantified percentage is not supported by the available "
    "data; framing it as directionally necessary but quantitatively "
    "open, pending serial vessel-calibre measurement, is."
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
    "Eipel C, Abshagen K, Vollmar B. Regulation of hepatic blood flow: "
    "the hepatic arterial buffer response revisited. World J "
    "Gastroenterol. 2010;16(48):6046-6057. doi:10.3748/wjg.v16.i48.6046",
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
