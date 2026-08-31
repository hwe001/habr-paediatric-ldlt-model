"""
Manuscript, round 3 -- responding to reviewer round 2's central finding:
the previous model summed a Doppler-velocity-calibrated Q_HA with an
mL/min-scale Q_PV in the sinus mass balance, a genuine dimensional
inconsistency, not merely an uncertain weighting. This version rebuilds
the post-LDLT model so Q_HA is a real, mL/min-consistent volumetric flow
throughout (matching Q_PV and the generic model), converted to a Doppler
velocity only via an explicit, literature-sourced hepatic-artery
cross-sectional-area assumption (Kim et al. 2007). Also corrects a real
statistical error (RI confidence-interval interpretation), removes
"equivalence test" language, disambiguates cardiac-cycle vs. postoperative
-day time, gives the exact HABR-to-resistance update equation, reconsiders
the Monte Carlo intervals as illustrative (not rigorous 95% CIs) given the
repeated-measures structure, and softens conclusions to the reviewer's
suggested wording.
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
    "The hepatic arterial buffer response (HABR) is often invoked to "
    "explain the fall in hepatic artery Doppler velocity after paediatric "
    "living-donor liver transplantation (LDLT). We built a lumped-"
    "parameter ('pi-filter') hepatic circulation model, calibrated it "
    "against independent literature targets for a generic paediatric "
    "post-transplant circulation, then anchored it to a real cohort of 41 "
    "infants after left-lateral-segment LDLT for biliary atresia (Chen et "
    "al., 2022). An earlier version of this analysis calibrated the "
    "hepatic arterial (HA) state directly against Doppler velocity while "
    "the portal venous (PV) state was computed in volumetric (mL/min-"
    "scale) units, then summed the two directly in a mass-balance "
    "equation -- a dimensional inconsistency that invalidated the "
    "physical interpretation of the result. This version corrects that: "
    "the HA state is now a genuine volumetric flow throughout, related to "
    "Doppler velocity only via an explicit hepatic-artery cross-sectional-"
    "area assumption sourced from a paediatric ultrasound reference study "
    "(Kim et al., 2007), not an internally inconsistent numerical proxy. "
    "We compare three ways of applying a fixed-coefficient HABR "
    "relationship (coefficients imported from prior unpublished work, not "
    "re-fit here) across postoperative day (POD) 1-30, as alternative "
    "scenarios rather than a single preferred model: continuous "
    "application; application confined to POD1-7 with resistance then "
    "held fixed (motivated by, not proven by, the cohort's numerically "
    "flat resistive index [RI] from POD7 onward); and a null scenario "
    "with no HABR. Under the model's central (zero portal-calibre-growth) "
    "assumption, the continuous scenario reproduces roughly a quarter of "
    "the measured hepatic-artery peak systolic velocity (PSV) decline by "
    "POD30, and the direction differs from a null scenario with HABR "
    "absent. However, a sensitivity analysis shows this result is not "
    "robust: a plausible, untested 10% increase in portal vein diameter "
    "by POD30 reverses its sign. We therefore do not conclude that HABR "
    "is directionally necessary in any robust sense; we report only that, "
    "under the specific assumptions used in the primary scenario, the "
    "model predicts a reduction, and that this prediction is highly "
    "sensitive to an assumption the available data cannot test. Whatever "
    "drives the substantial residual decline is not identified by this "
    "study; graft-regeneration-driven vessel-calibre change and systemic "
    "haemodynamic normalization are presented as testable hypotheses, not "
    "established mechanisms."
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
    "equilibrates within minutes to a few hours, but describes a "
    "continuously-coupled feedback between portal flow and periportal "
    "adenosine concentration, not a single event that occurs once and "
    "then stops: whenever portal flow changes again, however much later, "
    "the same mechanism remains available to respond. How this bears on "
    "applying HABR to a full postoperative month is addressed directly "
    "in Methods 2.5."
)
d.add_paragraph(
    "HABR is clinically relevant after partial hepatectomy and liver "
    "transplantation. Prior work from this group modelled HABR using an "
    "electrical-analog ('pi-filter') lumped-parameter circulation model "
    "with an empirical quadratic regulation function (Ho, Sorrell, "
    "Bartlett and Hunter, 2013), subsequently applied in unpublished "
    "draft form to an adult-to-child left-lateral-segment (LLS) "
    "transplantation scenario (Yu, Bartlett, Hunter and Ho, unpublished "
    "manuscript; Ho, Yu and Bartlett, unpublished submitted manuscript). "
    "We rely on these two unpublished sources for specific real target "
    "pressure/flow values because no equivalent published dataset for "
    "this exact clinical scenario was located; this dependence is a "
    "genuine limitation (Discussion)."
)
d.add_paragraph(
    "Chen et al. (2022) report serial hepatic artery and portal vein "
    "Doppler measurements in 41 infants (4-18 months, biliary atresia) "
    "before and after LLS-LDLT, at POD1, 7, 14, and 30. Hepatic artery "
    "PSV and RI both fall over this month, attributed qualitatively to "
    "HABR by the authors, without a quantitative mechanistic test."
)
d.add_paragraph(
    "This study tests that attribution quantitatively, with an explicit "
    "focus on what can and cannot be concluded, and on ensuring the model "
    "used to do so is dimensionally and physically consistent. An earlier "
    "iteration of this analysis was not: it calibrated hepatic arterial "
    "flow directly against Doppler velocity while computing portal flow "
    "in volumetric units, then combined the two in a mass-balance "
    "equation without a common physical basis. This version corrects "
    "that fault directly (Methods 2.2.1) rather than only disclosing it, "
    "and re-examines every quantitative conclusion under the corrected "
    "model."
)

# ------------------------------------------------------------------ Methods
d.add_heading("Methods", level=2)

d.add_heading("2.1 Dataset", level=3)
d.add_paragraph(
    "Chen et al. (2022; doi:10.3389/fbioe.2022.903385) is a retrospective "
    "study of 41 infants (22 male, 19 female; median age 5 months, range "
    "4-18) with biliary atresia undergoing LLS-LDLT, with uncomplicated "
    "postoperative courses. Doppler measurements were taken pre-"
    "transplant and at POD1, 7, 14, and 30 (Table 1)."
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
    "The circulation is represented with a two-port 'pi-filter' lumped "
    "element (series inductor L and resistor Rs between ports; an "
    "identical shunt capacitor-resistor branch at each port). A "
    "single-lobe topology has hepatic arterial (HA) and portal venous "
    "(PV) pi-filters both feeding a shared sinusoidal node, draining "
    "through a hepatic venous (HV) pi-filter to a fixed inferior-vena-"
    "cava reference pressure P_IVC (Figure 1)."
)
d.add_paragraph(
    "Two distinct time variables are used throughout, and are never "
    "conflated: tau denotes time WITHIN one cardiac cycle (the ODE "
    "integration variable, tau in [0, T), T = 60/HR); 'day' or 'POD' "
    "denotes postoperative time, indexing which of several INDEPENDENT "
    "simulations is being run (each representing one quasi-static "
    "physiological state, not a continuous simulation spanning "
    "postoperative days). The governing equations, in tau, for a given "
    "day's simulation (forward-Euler integration, 400 steps per cardiac "
    "cycle, periodic steady state defined as relative change below 1e-4 "
    "in the Q_HA(tau) waveform between consecutive cycles):"
)
eq = d.add_paragraph()
eq.add_run(
    "L_HA dQ_HA/d(tau) = P_HA(tau) - Rs_HA*Q_HA - P_sinus\n"
    "C_sinus dP_sinus/d(tau) = Q_HA + Q_PV - Q_HV - P_sinus/Rp_sinus\n"
    "L_HV dQ_HV/d(tau) = P_sinus - Rs_HV*Q_HV - P_hv\n"
    "C_hv dP_hv/d(tau) = Q_HV - (P_hv - P_IVC)/Rp_hv_out"
).italic = True
d.add_paragraph(
    "P_HA(tau) = P_HA_mean + P_HA_amp*sin(2*pi*tau/T). In the GENERIC "
    "configuration (this section), Q_PV is itself a state governed by "
    "L_PV dQ_PV/d(tau) = P_PV - Rs_PV*Q_PV - P_sinus, with P_PV constant. "
    "In the POST-LDLT configuration (Section 2.4), this PV equation is "
    "DISABLED entirely -- Q_PV is instead a prescribed constant for the "
    "duration of that day's simulation, overwritten between days to each "
    "day's real measured value, not evolved by its own ODE. This "
    "replacement is justified in Section 2.4."
)
d.add_paragraph(
    "The generic configuration was calibrated against independent real "
    "target data from Ho, Yu and Bartlett's unpublished manuscript "
    "(portal driving pressure 13 mmHg, mean arterial pressure 57.5 mmHg "
    "[range 42.4-72.6], sinusoidal pressure 5.37 mmHg, hepatic venous "
    "pressure 4.07 mmHg, portal flow 300 mL/min, hepatic arterial flow "
    "31.93 mL/min, hepatic venous flow 322.5 mL/min). We call this step "
    "CALIBRATION, not validation: because the configuration is linear, "
    "Rs_PV, Rs_HA, Rs_HV were solved exactly via Ohm's law on the time-"
    "averaged circuit from these same targets -- agreement (within 2%, "
    "Figure 3) is close by construction. Inertance/compliance parameters "
    "(Table 3) were chosen, not fit, for plausible pulsatility."
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
    "Figure 3: Generic model mean flows vs. calibration targets (within "
    "2% by construction).")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True

d.add_heading("2.2.1 A corrected, dimensionally-consistent mapping to "
              "Doppler velocity", level=3)
d.add_paragraph(
    "An earlier iteration of this analysis calibrated Q_HA directly and "
    "only against measured Doppler velocity (cm/s), while Q_PV was "
    "computed in mL/min-scale units via the formula in Section 2.4, and "
    "the two were then summed directly in the sinusoidal-node mass "
    "balance. This is a genuine dimensional inconsistency, not merely an "
    "uncertain relative weighting: a velocity cannot be added to a "
    "volumetric flow in a conservation equation, and the resulting "
    "post-LDLT simulations were not physically interpretable."
)
d.add_paragraph(
    "This is corrected as follows. Q_HA is now a genuine volumetric flow "
    "(mL/min-scale), on the same physical basis as Q_PV and the generic "
    "model, throughout the mass balance above. It is related to Doppler "
    "velocity only at the point of comparison with measured data, via an "
    "assumed hepatic-artery cross-sectional area A_HA: v_HA(tau) = "
    "Q_HA(tau) / (60 * A_HA), matching the same flow-to-velocity logic "
    "Chen et al. use for the portal vein (Section 2.4). A_HA is set from "
    "a diameter of 1.2 mm (giving A_HA = 0.0113 cm^2), the mean right "
    "hepatic artery diameter reported in a healthy, non-jaundiced infant "
    "control group (mean age 67 days) in a paediatric ultrasound "
    "reference study (Kim et al., 2007). This is an ASSUMPTION for this "
    "cohort's graft artery, not a measurement of it: it is a native, "
    "disease-free artery in a slightly younger, non-transplant "
    "population, not the graft hepatic artery at the anastomotic Doppler "
    "sampling site used in Chen et al.'s own cohort, for which no "
    "diameter was reported. It is the best available published "
    "paediatric reference value we located, and is used because SOME "
    "area assumption is unavoidable to relate flow and velocity -- not "
    "because it is known to be an accurate value for this specific "
    "vessel. PSV, end-diastolic velocity (EDV), and RI are computed from "
    "the resulting v_HA(tau) waveform exactly as from a real Doppler "
    "trace: PSV = max(v_HA), EDV = min(v_HA), RI = (PSV-EDV)/PSV."
)

d.add_heading("2.3 Fixed-coefficient HABR relationship", level=3)
d.add_paragraph(
    "HABR is represented, as in the prior work it is drawn from, by a "
    "discrete resistance-update rule: changeIha = 0.0007102*x^2 + "
    "0.5492*x, where x is the percent DECREASE in portal flow relative to "
    "a reference day and changeIha is the resulting percent decrease in "
    "hepatic arterial flow. These coefficients are imported from prior "
    "unpublished work and NOT re-estimated to any part of this cohort's "
    "data -- a 'fixed-coefficient' HABR relationship, not a 'parameter-"
    "free' one, since Rs_HA, L_HA, the pressure amplitude, and A_HA "
    "(Section 2.2.1) are all calibrated or assumed elsewhere in the "
    "model, detailed fully in Table 3."
)
d.add_paragraph(
    "Exact update procedure, for any target day d relative to reference "
    "day POD1: x(d) = (Q_PV(POD1) - Q_PV(d)) / Q_PV(POD1) * 100 (all "
    "Q_PV values from Section 2.4's flow formula, using each day's real "
    "measured PVV). changeIha(d) = 0.0007102*x(d)^2 + 0.5492*x(d). "
    "Q_HA_target(d) = Q_HA_ref * (1 - changeIha(d)/100), where Q_HA_ref "
    "is the model's own periodic-steady-state mean HA flow at the POD1 "
    "anchor (Section 2.4). Rs_HA(d) is then found by bisection (Brent's "
    "method) such that simulating the model with P_HA_mean, P_HA_amp, "
    "and L_HA held at their POD1-fitted values, and Q_PV fixed at Q_PV(d) "
    "for that day, gives a periodic-steady-state mean HA flow equal to "
    "Q_HA_target(d). In the CONTINUOUS scenario (Section 2.5), the "
    "reference day is ALWAYS POD1, for every target day (not cumulative, "
    "sequential referencing day-to-day). In the ACUTE-THEN-FROZEN "
    "scenario, this update is performed once, for d=POD7 only (reference "
    "POD1); Rs_HA(POD14) = Rs_HA(POD30) = Rs_HA(POD7)."
)

d.add_heading("2.4 Post-LDLT model anchoring", level=3)
d.add_paragraph(
    "Q_PV is a prescribed input, not an independently simulated state "
    "(its ODE is disabled, Section 2.2), justified by the generic "
    "model's own result that PV flow varies under 0.2% across a cardiac "
    "cycle. Q_PV(d) is computed from this cohort's own portal vein "
    "diameter and PVV via Chen et al.'s reported formula, PVF = "
    "pi*r^2*0.57*PVV*60 (r = diameter/2 in cm, PVV in cm/s). This "
    "formula, as given in the source paper and reproduced here, yields a "
    "quantity with units of mL/min -- no graft-mass term appears "
    "anywhere in it, despite the source paper's own 'mL/min per 100 g "
    "graft' label. Graft weight was not reported for this cohort and was "
    "not otherwise available to us, so we cannot resolve whether this is "
    "a units error in the source presentation or an intended, "
    "unnormalized quantity mislabelled; this ambiguity is inherited from "
    "the source paper, not introduced here, and does not affect the "
    "present analysis beyond an unresolved absolute-scale label, since "
    "(following Section 2.2.1's correction) Q_PV and Q_HA are now both "
    "genuine mL/min-scale flows regardless of whether that scale should "
    "properly be read as per-100g or not."
)
d.add_paragraph(
    "Portal diameter is only reported at pre-transplant (0.44 cm) and "
    "POD1 (0.46 cm); it is held at the POD1 value for POD7/14/30 in the "
    "primary analysis. Across the pre-op to POD1 transition, where "
    "diameter IS reported, area increased 9.3% while velocity increased "
    "82.5%, combining to a 99.4% flow increase matching the reported "
    "97.9% closely -- this shows velocity dominated over THAT specific "
    "transition, but does not establish diameter stays constant over the "
    "physiologically different POD1-30 window during which graft "
    "regeneration is actively occurring. Section 2.7 tests this "
    "assumption directly rather than relying on it."
)
d.add_paragraph(
    "Rs_HA, L_HA, and the HA pulse amplitude P_HA_amp are calibrated "
    "JOINTLY at POD1 against this cohort's real measured PSV_HA and "
    "RI_HA -- three unknowns against two targets, which is necessarily "
    "underdetermined (non-unique): the fitted values reported (Table 3) "
    "are one member of a family of combinations that reproduce the POD1 "
    "targets equally well, not a uniquely identified set. We fit all "
    "three jointly, rather than fixing P_HA_amp at the generic model's "
    "literature value as an earlier iteration did, because doing so (in "
    "the now dimensionally-consistent, real-mL/min-scale formulation) "
    "could not reach the measured RI_HA=0.61 for any tested combination "
    "of Rs_HA and L_HA -- the achievable RI was capped near 0.48 across "
    "a wide grid search, indicating this single-branch (no arterial-side "
    "compliance) circuit cannot generate sufficient pulsatility "
    "amplification from the literature pressure amplitude alone. This is "
    "itself a limitation of the single-lobe, arterial-compliance-free "
    "simplification (Discussion)."
)

d.add_heading("2.5 Three HABR-application scenarios, as alternatives, not "
              "a preferred model", level=3)
d.add_paragraph(
    "Because HABR's adenosine-washout kinetics describe continuous "
    "coupling, not a one-off event, fast equilibration does not, by "
    "itself, justify confining HABR's application to any particular "
    "window -- it remains available to respond at any point. We present "
    "three scenarios as alternative possibilities:"
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Continuous: ").bold = True
p.add_run("Rs_HA(d) set from Section 2.3's update at every day d, "
          "referenced to POD1.")
p = d.add_paragraph(style="List Bullet")
p.add_run("Acute-then-frozen: ").bold = True
p.add_run(
    "Rs_HA set from the update once, for POD7 (referenced to POD1), then "
    "held fixed for POD14/30. Motivated by an observation, not a proof "
    "(Section 2.6): mean RI_HA is numerically flat (0.59) from POD7 "
    "through POD30."
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Null: ").bold = True
p.add_run(
    "Rs_HA frozen at its POD1 value throughout; only Q_PV(d)'s passive "
    "effect on the shared sinusoidal node acts."
)
d.add_paragraph("In all three, Q_PV(d) itself always uses each day's real measured value.")

d.add_heading("2.6 Testing whether RI is really flat", level=3)
d.add_paragraph(
    "RI is a waveform ratio, not a direct resistance measurement, and is "
    "additionally shaped by compliance, downstream loading, waveform "
    "morphology, and measurement variability. We compared RI_HA between "
    "time points using an unpaired Welch's t-test and 95% confidence "
    "interval on the published summary statistics (mean, SD, n=41) -- "
    "this is a conservative approximation, since the real cohort is "
    "repeated-measures on the same 41 patients and a properly paired "
    "analysis (not possible without per-patient data) would have "
    "different, likely greater, power to detect a true difference. We do "
    "not describe this as an equivalence test: no equivalence margin was "
    "prespecified and no two-one-sided-tests procedure was performed; it "
    "is an ordinary unpaired comparison of summary statistics, reported "
    "as such."
)

d.add_heading("2.7 Sensitivity to the constant-portal-diameter assumption", level=3)
d.add_paragraph(
    "Since portal diameter is unmeasured for POD7-30, and this study's "
    "candidate residual mechanism (Section 3.5) is precisely a "
    "hypothesised change in vessel calibre, holding diameter constant is "
    "not a neutral assumption. We repeated the continuous scenario's "
    "POD30 calculation under assumed portal-diameter growth by POD30 "
    "(0/10/20/30/40%, linearly interpolated across POD7/14/30), holding "
    "every other parameter fixed."
)

d.add_heading("2.8 Illustrative sensitivity intervals on the fraction of "
              "decline reproduced", level=3)
d.add_paragraph(
    "Rather than a single deterministic percentage, we generated "
    "intervals via Monte Carlo (200,000 draws per comparison): the POD1 "
    "mean and each later-day mean were each drawn INDEPENDENTLY from a "
    "normal distribution with SD = reported SD / sqrt(41), and the ratio "
    "of the (fixed) model decline to the sampled measured decline was "
    "computed for each draw; the reported interval is the 2.5th-97.5th "
    "percentile of the resulting distribution. We explicitly do not call "
    "these 95% confidence intervals: independent sampling is the wrong "
    "covariance structure for repeated measurements on the same 41 "
    "infants (a proper paired analysis, not possible without individual "
    "trajectories, would likely differ); no PVV uncertainty or model-"
    "parameter uncertainty was propagated, only the sampling uncertainty "
    "of the two compared PSV means; and no simulated draws were "
    "discarded, including draws giving a measured decline near zero or "
    "negative, which produces a heavy-tailed, at times unstable, ratio "
    "distribution (most evident at POD7, Results 3.4). We refer to these "
    "as illustrative sensitivity intervals, not confidence intervals."
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
    ("P_IVC", "2.0", "mmHg", "assumed (not reported in source)"),
    ("Rs_PV, Rs_HV, Rp_hv_out (generic)", "1.526, 0.242, 0.385",
     "model units", "solved exactly from generic targets; reused post-LDLT"),
    ("Rs_HA, L_HA (generic)", "97.96, 2.0", "model units",
     "solved/assumed for generic model; NOT reused post-LDLT (see 2.4)"),
    ("A_HA (hepatic artery area)", "0.0113", "cm^2",
     "Kim et al. 2007 (1.2 mm diameter, healthy infant control group) -- "
     "assumed for this cohort, not measured"),
    ("Rs_HA, L_HA, P_HA_amp (POD1, post-LDLT)", "127.92, 5.80, 27.43",
     "model units, model units, mmHg",
     "jointly fit to real POD1 PSV_HA/RI_HA -- 3 unknowns/2 targets, "
     "non-unique (see 2.4)"),
    ("L_PV, L_HV", "0.01, 0.02", "model units", "assumed"),
    ("C_sinus, C_hv", "2.0, 2.0", "model units", "assumed"),
    ("Rp_sinus", "500", "model units", "assumed"),
    ("Portal diameter (POD1)", "0.46", "cm",
     "Chen et al. 2022; held fixed POD7-30 in primary analysis"),
    ("PV velocity-to-flow factor", "0.57", "dimensionless", "Chen et al. 2022"),
    ("Integration", "forward Euler, 400 steps/cycle", "-", "-"),
    ("Convergence criterion", "<1e-4 relative change, consecutive cycles", "-", "-"),
]
for row in param_rows:
    cells = t3.add_row().cells
    for i, v in enumerate(row):
        cells[i].text = v
cap = d.add_paragraph(
    "Table 3: Full model parameter list. Q_HA and Q_PV are now both real, "
    "mL/min-scale volumetric flows (Section 2.2.1); Doppler velocity is "
    "obtained from Q_HA only via the assumed area A_HA.")
cap.runs[0].italic = True

d.add_heading("2.10 Candidate residual mechanisms: literature search", level=3)
d.add_paragraph(
    "A literature search (PubMed/EuropePMC, citations verified against "
    "primary sources or the EuropePMC metadata API before use) was "
    "conducted for real, plausible, non-HABR mechanisms. These are "
    "presented as testable hypotheses for future work, not identified or "
    "favoured mechanisms -- the available data cannot distinguish "
    "between them."
)

# -------------------------------------------------------------------- Results
d.add_heading("Results", level=2)

d.add_heading("3.1 Generic model calibration", level=3)
d.add_paragraph(
    "The generic pi-filter model reproduced the independent calibration "
    "targets within 2% by construction (Figure 3) and reproduced the "
    "qualitative waveform pattern reported in the source work (Figure 2)."
)

d.add_heading("3.2 POD1 anchor (dimensionally consistent)", level=3)
d.add_paragraph(
    "The jointly-fit POD1 anchor (Rs_HA=127.92, L_HA=5.80, P_HA_amp="
    "27.43 mmHg; Table 3) reproduces the measured PSV_HA (53.10 cm/s) "
    "and RI_HA (0.610) exactly by construction, with a periodic-steady-"
    "state mean HA flow of 25.0 mL/min -- within the same order of "
    "magnitude as, though about 22% below, the generic model's own "
    "31.93 mL/min target for a comparable clinical scenario, a modest "
    "external check on plausibility given the assumed HA area (Section "
    "2.2.1) is not independently verified for this cohort."
)

d.add_heading("3.3 Three scenarios, and their fragility", level=3)
d.add_paragraph(
    "Under the primary (zero portal-diameter-growth) assumption, the "
    "three scenarios diverge by POD30 (Figure 4): the null scenario "
    "predicts PSV_HA would rise slightly (53.10 to 53.27 cm/s), while "
    "both HABR scenarios predict a fall -- continuous to 49.41 cm/s, "
    "acute-then-frozen to 52.57 cm/s. We do not conclude from this that "
    "HABR is directionally necessary in any robust sense (Section 3.5 "
    "shows why); we report only that, under the assumptions used here, "
    "the continuous scenario predicts a reduction while the null does "
    "not."
)
d.add_picture("HABR_Figure_4_three_scenarios_consistent.png", width=Inches(6.3))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph(
    "Figure 4: Measured vs. all three scenarios, dimensionally-consistent "
    "model.")
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
    ("POD7", "47.02", "52.43", "52.43", "53.13"),
    ("POD14", "42.29", "50.94", "52.50", "53.20"),
    ("POD30", "38.51", "49.41", "52.57", "53.27"),
]:
    cells = t2.add_row().cells
    for i, v in enumerate(row):
        cells[i].text = v
cap = d.add_paragraph("Table 2: Simulated PSV_HA under all three scenarios vs. measured.")
cap.runs[0].italic = True

d.add_heading("3.4 RI comparison: corrected statistical interpretation", level=3)
d.add_paragraph(
    "An unpaired Welch's comparison of RI_HA finds POD1 vs. POD7 differ "
    "by 0.020 (95% CI [0.002, 0.038], p=0.032), and POD7 vs. POD30 do not "
    "detectably differ (95% CI [-0.010, +0.010], p=1.00). The correct "
    "reading of the second interval is narrower than an earlier draft of "
    "this analysis stated: a 95% CI of [-0.010, +0.010] EXCLUDES, not "
    "fails to exclude, a true difference as large as 0.020 -- the "
    "opposite of what was previously written. The proper conclusions are: "
    "(i) the data show no statistically detectable RI difference between "
    "POD7 and POD30 under this unpaired approximation; (ii) the data are "
    "compatible with true differences up to about 0.010 in magnitude; "
    "(iii) whether a 0.01 RI difference is clinically or mechanistically "
    "meaningful is a separate, unresolved question; (iv) this does NOT "
    "mean a change as large as the POD1-7 difference remains possible at "
    "POD7-30 -- under this same method, that specific magnitude would be "
    "rejected. We describe RI as 'not detectably changing' after POD7, "
    "and treat the acute-then-frozen scenario as a hypothesis motivated "
    "by, not demonstrated by, this observation."
)

d.add_heading("3.5 The primary result is not robust to the untested "
              "diameter assumption", level=3)
d.add_paragraph(
    "Repeating the continuous scenario's POD30 calculation under assumed "
    "portal-diameter growth (Section 2.7), now in the corrected, "
    "dimensionally-consistent model: at 0% growth (used above), the "
    "model reproduces approximately 25% of the measured decline; at just "
    "10% growth, this reverses sign (-9%); at 20-40% growth the mismatch "
    "grows substantially (-44% to -115%; Figure 5). This sensitivity "
    "persists after Section 2.2.1's correction -- it is a property of "
    "the HABR relationship's response to the assumed portal-flow "
    "trajectory, not an artefact of the earlier unit inconsistency. "
    "Consequently, we do not describe HABR as directionally necessary: "
    "under the constant-diameter and area assumptions used in the "
    "primary scenario, the fixed-coefficient HABR implementation "
    "predicts a reduction in hepatic arterial velocity; the direction "
    "and magnitude of this prediction are not robust to plausible "
    "alternative portal-calibre assumptions that the available data "
    "cannot rule out."
)
d.add_picture("HABR_Figure_7_diameter_sensitivity_consistent.png", width=Inches(5.5))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph(
    "Figure 5: The primary result as a function of an assumed, untested "
    "portal-diameter-growth rate (corrected model).")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True

d.add_heading("3.6 Illustrative sensitivity intervals", level=3)
d.add_paragraph(
    "Under the continuous scenario, illustrative intervals (Section 2.8; "
    "not confidence intervals) for the percentage of measured PSV_HA "
    "decline reproduced: approximately 11% [5%, 64%] at POD7, 20% [13%, "
    "43%] at POD14, 25% [18%, 40%] at POD30. The POD7 interval is wide "
    "enough that little can be concluded about magnitude at that time "
    "point from group means alone."
)

d.add_heading("3.7 Candidate mechanisms for any residual decline: "
              "testable hypotheses", level=3)
d.add_paragraph(
    "Whatever the model does not reproduce requires some other "
    "contributor. Two literature-grounded candidates are presented "
    "explicitly as hypotheses for future testing:"
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Systemic haemodynamic normalization: ").bold = True
p.add_run(
    "the elevated cardiac output/reduced systemic vascular resistance "
    "state common in cirrhosis (Plevak et al., 1993) resolves within "
    "days -- 3-5 postoperative days in one adult cohort (n=57; pulse "
    "rate 103 to 72.6 beats/min from POD1 to POD3), with related "
    "timescales of 4 days to 2 weeks cited elsewhere (Dashti et al., "
    "2020)."
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Graft-regeneration-driven vessel-calibre dilution: ").bold = True
p.add_run(
    "graft mass increases substantially over weeks after LDLT (~1.7-fold "
    "by 2 weeks in one paediatric LDLT cohort; Byun et al., 2016). If "
    "arterial or portal calibre grows with the regenerating graft, "
    "Doppler velocity at a fixed measurement point would fall even at "
    "constant flow, preserving RI. Quantitative regeneration data are "
    "inconsistent across the (adult, non-LLS) studies located: one "
    "reports monotonic mass increase through day 30 (Marcos et al., "
    "2000), another the opposite shape (Zhang et al., 2022). Graft "
    "volume does not necessarily translate into proportional arterial "
    "growth at the Doppler site, particularly near an anastomosis. "
    "Paediatric LLS grafts are often sized close to or above the "
    "recommended graft-to-recipient weight ratio, with reduction "
    "techniques used above roughly 4% to avoid a large-for-size graft "
    "(Vargas and Goldaracena, 2024) -- opposite to the undersized-graft "
    "premise of most compensatory-hypertrophy literature, so even the "
    "direction of expected calibre change here is not established."
)
d.add_paragraph(
    "Other plausible, unmodelled contributors this study cannot rule "
    "out: changes in systemic cardiac output and arterial pressure "
    "amplitude beyond the fixed assumption used here; postoperative "
    "oedema; arterial spasm; anastomotic geometry; variation in Doppler "
    "insonation angle or sampling location between visits; sedation; and "
    "heart rate. None were assessed here, and this study does not claim "
    "to have enumerated or excluded them."
)

# ---------------------------------------------------------------- Discussion
d.add_heading("Discussion", level=2)
d.add_paragraph(
    "Primary conclusion: under the specific assumptions used in the "
    "primary scenario (constant portal diameter after POD1, an assumed "
    "hepatic-artery area, a fixed-coefficient HABR relationship applied "
    "continuously), the model predicts a reduction in hepatic arterial "
    "velocity of roughly a quarter of the measured decline by POD30. "
    "This prediction's direction and magnitude are not robust to a "
    "plausible, untested change in portal calibre (Section 3.5): we "
    "therefore do not claim HABR is directionally necessary, only that "
    "it produces a directional prediction under stated assumptions that "
    "the data cannot themselves verify. Secondary conclusion: the "
    "available data -- group-level Doppler indices with no serial "
    "vessel-diameter or graft-volumetry measurements -- do not identify "
    "what mechanism is responsible for the substantial remainder. "
    "Exploratory hypothesis: graft- and vessel-calibre growth, alongside "
    "systemic haemodynamic normalization and other unmodelled factors, "
    "may contribute, and should be tested directly with serial calibre, "
    "volumetry, pressure, and flow measurements, not inferred indirectly "
    "as done here."
)
d.add_paragraph(
    "Limitations. The circulation is a single lobe with lumped elements, "
    "not the fuller multi-generation vascular tree used in some prior "
    "work by this group. The POD1 anchor's three parameters (Rs_HA, "
    "L_HA, P_HA_amp) are jointly fit to only two targets and are "
    "therefore non-unique (Section 2.4) -- a genuine identifiability gap, "
    "not fully resolved here. The hepatic-artery cross-sectional area "
    "(Section 2.2.1) is assumed from a published reference value for a "
    "different (native, non-transplant) population, not measured for "
    "this cohort's graft artery; this is now an explicit, single, "
    "clearly-sourced assumption rather than a hidden inconsistency, but "
    "it remains an assumption. The generic model's calibration targets "
    "and the HABR coefficients themselves come from two unpublished "
    "manuscripts; we searched for published alternatives providing "
    "equivalent real paediatric LLS-LDLT data and did not find one. The "
    "pre-transplant to POD1 transition is not modelled, since it is a "
    "discrete organ-replacement event. Graft-to-recipient weight ratio "
    "is unknown for this cohort. All comparisons use group-level data; "
    "no per-patient trajectory or individual-level validation was "
    "possible, and the illustrative sensitivity intervals reported "
    "(Section 3.6) are not proper confidence intervals for this reason."
)
d.add_paragraph(
    "We would not currently recommend using this framework for "
    "individual-patient interpretation. Its value at this stage is "
    "narrower: it shows that testing HABR's contribution to this "
    "cohort's PSV_HA trajectory requires serial vessel-calibre data that "
    "does not currently exist, and that a specific, previously-reported "
    "quantitative conclusion (a fixed percentage 'explained' by HABR) is "
    "conditional on an assumption that is not verifiable with the "
    "available data and is not even directionally safe."
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
    "A dimensionally-consistent, calibrated pi-filter lumped-parameter "
    "model of paediatric post-LDLT hepatic circulation shows that a "
    "fixed-coefficient hepatic arterial buffer response relationship "
    "predicts a reduction in hepatic arterial velocity under a specific "
    "set of stated assumptions, but that this prediction's direction and "
    "magnitude are not robust to a plausible, unmeasured change in "
    "portal vessel calibre. We do not conclude that HABR is directionally "
    "necessary; we conclude that its contribution to this cohort's "
    "observed trajectory cannot be established from the available data, "
    "and that resolving this requires serial vessel-calibre measurement "
    "not currently available."
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
    "Kim WS, Cheon JE, Youn BJ, Yoo SY, Kim WY, Kim IO, Yeon KM, Seo JK, "
    "Park KW. Hepatic arterial diameter measured with US: adjunct for US "
    "diagnosis of biliary atresia. Radiology. 2007;245(2):549-555. "
    "doi:10.1148/radiol.2452061093",
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
