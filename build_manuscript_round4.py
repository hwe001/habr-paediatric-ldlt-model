"""
Manuscript, round 4 -- responding to reviewer round 3: propagates the two
principal structural uncertainties (non-unique POD1 calibration; arterial
AND portal calibre assumptions) instead of adding further verbal caveats,
per the reviewer's explicit steer. Also: explicit physical units for every
element; honest treatment of mean-velocity-vs-Doppler-PSV; a graft-mass
Q_PV-scaling check; removes revision-history narrative from the reader-
facing text (kept only in response letters); de-emphasizes the Monte Carlo
intervals in favour of the structural-sensitivity results.
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
    "living-donor liver transplantation (LDLT). We built a dimensionally-"
    "consistent lumped-parameter ('pi-filter') hepatic circulation model, "
    "calibrated it against previously-derived calibration targets for a "
    "generic paediatric post-transplant circulation, then anchored it to "
    "a real cohort of 41 infants after left-lateral-segment LDLT for "
    "biliary atresia (Chen et al., 2022). Hepatic arterial flow is "
    "related to Doppler velocity via an assumed hepatic-artery cross-"
    "sectional area (Kim et al., 2007); portal flow via the cohort's own "
    "reported diameter and flow formula. We compare three ways of "
    "applying a fixed-coefficient HABR relationship (coefficients "
    "imported from prior unpublished work, not re-fit here) across "
    "postoperative day (POD) 1-30, as alternative scenarios: continuous "
    "application; application confined to POD1-7 with resistance then "
    "held fixed (motivated by, not proven by, the cohort's numerically "
    "flat resistive index from POD7 onward); and a null scenario with no "
    "HABR. The hepatic-arterial branch's calibration at POD1 is "
    "non-identifiable (three parameters fit to two targets); propagating "
    "the entire admissible parameter family through to POD30 gives a "
    "relatively narrow envelope (20-27% of the measured peak-systolic-"
    "velocity decline reproduced), because the two parameters that "
    "determine mean flow are well-constrained even though two others "
    "trade off. This is not the dominant uncertainty, however: separately "
    "varying assumed postoperative growth in portal and hepatic-artery "
    "calibre -- neither measured beyond POD1 in the source cohort -- "
    "moves the same quantity from -44% to +129% across a modest, jointly "
    "plausible 0-20% growth range in each vessel. We therefore do not "
    "conclude that HABR's contribution to this cohort's trajectory can be "
    "quantified from the available data; systemic haemodynamic "
    "normalization and graft-regeneration-driven vessel-calibre change "
    "are presented as testable hypotheses for whatever this model does "
    "not explain, alongside model misspecification and measurement "
    "variability, which cannot be excluded either."
)

d.add_heading("Keywords", level=3)
d.add_paragraph(
    "hepatic arterial buffer response; liver transplantation; paediatric; "
    "Doppler ultrasound; lumped-parameter model; identifiability; "
    "sensitivity analysis; biliary atresia"
)

# ------------------------------------------------------------ Introduction
d.add_heading("Introduction", level=2)
d.add_paragraph(
    "The hepatic arterial buffer response (HABR) is an intrinsic hepatic "
    "regulatory mechanism, first described by Lautt: a fall in portal "
    "venous flow provokes a rise in hepatic arterial flow, and vice "
    "versa, mediated by washout of adenosine in the periportal space of "
    "Mall (Eipel, Abshagen and Vollmar, 2010). This washout process "
    "equilibrates within minutes to a few hours, but describes continuous "
    "coupling between portal flow and periportal adenosine concentration, "
    "not a single event that occurs once and then stops -- how this "
    "bears on applying HABR across a postoperative month is addressed "
    "directly in Methods 2.5."
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
    "We rely on these two unpublished sources for specific calibration "
    "pressure/flow values because no equivalent published dataset for "
    "this exact clinical scenario was located; this dependence is a "
    "genuine limitation (Discussion)."
)
d.add_paragraph(
    "Chen et al. (2022) report serial hepatic artery and portal vein "
    "Doppler measurements in 41 infants (4-18 months, biliary atresia) "
    "before and after LLS-LDLT, at POD1, 7, 14, and 30. Hepatic artery "
    "peak systolic velocity (PSV) and resistive index (RI) both fall over "
    "this month, attributed qualitatively to HABR by the authors, without "
    "a quantitative mechanistic test. This study provides one, with "
    "particular attention to two structural sources of uncertainty that "
    "bear directly on how much weight the result can carry: whether the "
    "model's own calibration is uniquely determined, and how much the "
    "conclusion depends on vessel-calibre assumptions that this cohort's "
    "own data do not measure past POD1."
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
    "cava reference pressure P_IVC (Figure 1). Two time variables are "
    "used and never conflated: tau, time within one cardiac cycle (the "
    "ODE integration variable, tau in [0,T), T=60/HR seconds); and 'day' "
    "(POD), indexing which of several INDEPENDENT simulations is being "
    "run, each an independently-converged periodic state, not a "
    "continuous simulation across postoperative days."
)
eq = d.add_paragraph()
eq.add_run(
    "L_HA dQ_HA/d(tau) = P_HA(tau) - Rs_HA*Q_HA - P_sinus\n"
    "C_sinus dP_sinus/d(tau) = Q_HA + Q_PV - Q_HV - P_sinus/Rp_sinus\n"
    "L_HV dQ_HV/d(tau) = P_sinus - Rs_HV*Q_HV - P_hv\n"
    "C_hv dP_hv/d(tau) = Q_HV - (P_hv - P_IVC)/Rp_hv_out"
).italic = True
d.add_paragraph(
    "with P_HA(tau) = P_HA_mean + P_HA_amp*sin(2*pi*tau/T). All pressures "
    "are in mmHg; all flows (Q) are in mL/s during integration (reported "
    "as mL/min after multiplying by 60); tau is in seconds. Under this "
    "basis, every element has an explicit, dimensionally consistent "
    "unit: Rs and Rp in mmHg*s/mL; L in mmHg*s^2/mL; C in mL/mmHg "
    "(Table 3 states these directly). In the GENERIC configuration "
    "(this section), Q_PV is itself a state, governed by L_PV dQ_PV/d(tau) "
    "= P_PV - Rs_PV*Q_PV - P_sinus, with P_PV constant. In the POST-LDLT "
    "configuration (Section 2.4), this equation is disabled; Q_PV is a "
    "prescribed constant for the duration of each day's simulation, "
    "overwritten between days to that day's real measured value."
)
d.add_paragraph(
    "The generic configuration was calibrated against previously-derived "
    "calibration targets from Ho, Yu and Bartlett's unpublished "
    "manuscript (portal driving pressure 13 mmHg, mean arterial pressure "
    "57.5 mmHg [range 42.4-72.6], sinusoidal pressure 5.37 mmHg, hepatic "
    "venous pressure 4.07 mmHg, portal flow 300 mL/min, hepatic arterial "
    "flow 31.93 mL/min, hepatic venous flow 322.5 mL/min). Rs_PV, Rs_HA, "
    "Rs_HV were solved exactly via Ohm's law on the time-averaged circuit "
    "from these same targets (the configuration is linear, so this is "
    "possible in closed form); agreement (within 2%, Figure 3) is close "
    "by construction, a calibration check rather than an independent "
    "validation. Inertance/compliance parameters (Table 3) were chosen, "
    "not fit, for plausible pulsatility."
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

d.add_heading("2.2.1 Mapping simulated flow to Doppler velocity", level=3)
d.add_paragraph(
    "Q_HA is a volumetric flow throughout the mass balance above, on the "
    "same physical basis as Q_PV. It is related to Doppler velocity only "
    "at the point of comparison with measured data, via an assumed "
    "hepatic-artery cross-sectional area A_HA: v_HA(tau) = Q_HA(tau) / "
    "(60*A_HA). A_HA is set from a diameter of 1.2 mm (A_HA = 0.0113 "
    "cm^2), the mean right hepatic artery diameter reported in a healthy, "
    "non-jaundiced infant control group (mean age 67 days) in a "
    "paediatric ultrasound reference study (Kim et al., 2007). This is "
    "an assumption for this cohort's graft artery, not a measurement of "
    "it: a native, disease-free artery in a slightly younger, non-"
    "transplant population, not the graft hepatic artery at the "
    "anastomotic Doppler sampling site used in Chen et al.'s cohort, for "
    "which no diameter was reported. Section 2.7 tests both this "
    "baseline value's published uncertainty (1.0-1.4 mm) and, "
    "separately, whether it changes over the postoperative month."
)
d.add_paragraph(
    "A further caveat applies to how PSV and RI are computed from "
    "v_HA(tau). The relation v = Q/A gives a cross-sectional MEAN "
    "velocity, whereas spectral Doppler PSV is conventionally read as a "
    "spatial peak within the vessel, not a cross-sectional average; Chen "
    "et al.'s own portal-flow formula (Section 2.4) applies a factor "
    "(0.57) specifically to convert their measured (peak-like) PVV "
    "toward a mean velocity for flow calculation, and no directly "
    "analogous, independently-sourced factor is applied here on the "
    "hepatic-artery side. Because the POD1 fit (Section 2.4) calibrates "
    "directly against measured PSV_HA, any such profile-shape "
    "discrepancy is silently absorbed into the fitted parameters rather "
    "than left as a visible residual. Consequently, we do NOT treat the "
    "resulting POD1 mean HA flow (Section 3.2) as an independently "
    "interpretable absolute physiological quantity -- only relative "
    "(percent) changes in flow, and the resulting RI (a ratio, invariant "
    "to a fixed unmodelled profile factor as long as it does not itself "
    "change over time), are used in the conclusions that follow."
)

d.add_heading("2.3 Fixed-coefficient HABR relationship and its exact "
              "application", level=3)
d.add_paragraph(
    "HABR is represented, as in the prior work it is drawn from, by a "
    "discrete resistance-update rule: changeIha = 0.0007102*x^2 + "
    "0.5492*x, x being the percent DECREASE in portal flow relative to a "
    "reference day. These coefficients are imported, not re-estimated "
    "here -- a 'fixed-coefficient' relationship, not a 'parameter-free' "
    "one, since Rs_HA, L_HA, P_HA_amp, and A_HA are all calibrated or "
    "assumed elsewhere (Table 3)."
)
d.add_paragraph(
    "Exact procedure, for target day d relative to reference day POD1: "
    "x(d) = (Q_PV(POD1) - Q_PV(d)) / Q_PV(POD1) * 100 (Q_PV values from "
    "Section 2.4's flow formula, using each day's real measured PVV). "
    "changeIha(d) = 0.0007102*x(d)^2 + 0.5492*x(d). Q_HA_target(d) = "
    "Q_HA_ref * (1 - changeIha(d)/100), Q_HA_ref being the model's "
    "periodic-steady-state mean HA flow at the POD1 anchor. Rs_HA(d) is "
    "then found by Brent's method (scipy.optimize.brentq; bracket "
    "initialised at [0.3, 3.0] times the POD1-fitted Rs_HA and expanded "
    "geometrically, factor 0.7/1.4, up to 40 times if the initial "
    "bracket does not contain a sign change; convergence tolerance "
    "1e-8; treated as a failure, and excluded, if no sign change is "
    "found within the expansion limit) such that simulating with "
    "P_HA_mean, P_HA_amp, and L_HA held at their POD1-fitted values and "
    "Q_PV fixed at Q_PV(d) gives a periodic-steady-state mean HA flow "
    "equal to Q_HA_target(d). In the CONTINUOUS scenario, the reference "
    "day is always POD1 (not cumulative day-to-day referencing). In the "
    "ACUTE-THEN-FROZEN scenario, this is performed once for d=POD7 only; "
    "Rs_HA(POD14)=Rs_HA(POD30)=Rs_HA(POD7)."
)

d.add_heading("2.4 Post-LDLT model anchoring, and its non-identifiability", level=3)
d.add_paragraph(
    "Q_PV(d) is computed from this cohort's own portal vein diameter and "
    "PVV via Chen et al.'s reported formula, PVF = pi*r^2*0.57*PVV*60 "
    "(r=diameter/2 in cm, PVV in cm/s). This formula, as given, yields a "
    "quantity with units of mL/min -- no graft-mass term appears in it, "
    "despite the source paper's 'mL/min per 100 g graft' label; graft "
    "weight was not available to us, and we cannot resolve whether this "
    "is a source-paper labelling error or an intended unnormalized "
    "quantity. Section 2.7 tests whether this ambiguity matters, by "
    "scaling Q_PV as if graft mass were 50-200 g rather than assuming it "
    "is exactly 100 g."
)
d.add_paragraph(
    "Portal diameter is reported only at pre-transplant (0.44 cm) and "
    "POD1 (0.46 cm); held at the POD1 value for POD7-30 in the primary "
    "analysis. Section 2.7 tests this assumption directly, together with "
    "the analogous, unmeasured assumption for hepatic-artery diameter."
)
d.add_paragraph(
    "Rs_HA, L_HA, and P_HA_amp are calibrated JOINTLY at POD1 against "
    "real measured PSV_HA and RI_HA -- three unknowns, two targets, "
    "necessarily non-unique. We found that fixing P_HA_amp at the "
    "generic model's literature value (15.1 mmHg) made RI_HA=0.61 "
    "unreachable for any tested (Rs_HA, L_HA) combination (achievable RI "
    "capped near 0.48 across a wide grid search), because this single-"
    "branch, arterial-compliance-free circuit cannot amplify pulsatility "
    "beyond what the driving pressure itself supplies. P_HA_amp was "
    "therefore included as a third free parameter. Rather than reporting "
    "results from one arbitrarily-selected member of the resulting "
    "admissible family, Section 2.7 generates the family directly (by "
    "scanning P_HA_amp and re-solving Rs_HA, L_HA for each value that "
    "admits an exact fit, starting from an initial guess of 120 mmHg-"
    "scale resistance and 5-unit inertance and warm-starting each "
    "subsequent point from the last) and propagates every member through "
    "POD30."
)

d.add_heading("2.5 Three HABR-application scenarios, as alternatives", level=3)
d.add_paragraph(
    "Because HABR's kinetics describe continuous coupling, not a one-off "
    "event, fast equilibration does not by itself justify confining "
    "HABR's application to any particular window. Three scenarios are "
    "presented as alternatives:"
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Continuous: ").bold = True
p.add_run("Rs_HA(d) set from Section 2.3's update at every day d, "
          "referenced to POD1.")
p = d.add_paragraph(style="List Bullet")
p.add_run("Acute-then-frozen: ").bold = True
p.add_run(
    "Rs_HA set once, for POD7, then held fixed. Motivated by an "
    "observation, not a proof (Section 2.6): mean RI_HA is numerically "
    "flat (0.59) from POD7 through POD30."
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Null: ").bold = True
p.add_run("Rs_HA frozen at its POD1 value throughout.")

d.add_heading("2.6 Testing whether RI is really flat", level=3)
d.add_paragraph(
    "We compared RI_HA between time points using an unpaired Welch's "
    "t-test and 95% CI on the published summary statistics -- a "
    "conservative approximation, since the cohort is repeated-measures "
    "on the same 41 patients. This is an ordinary unpaired comparison of "
    "summary statistics, not an equivalence test (no margin or two-one-"
    "sided-tests procedure was used)."
)

d.add_heading("2.7 Structural sensitivity analyses", level=3)
d.add_paragraph(
    "Three analyses address the two principal structural uncertainties "
    "directly, rather than only disclosing them:"
)
p = d.add_paragraph(style="List Bullet")
p.add_run("POD1 identifiability envelope: ").bold = True
p.add_run(
    "the admissible (Rs_HA, L_HA, P_HA_amp) family (Section 2.4) is "
    "propagated through the continuous scenario to POD30, and the range "
    "of resulting '% of decline reproduced' reported, rather than a "
    "single point estimate."
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Joint portal/hepatic-artery calibre sensitivity: ").bold = True
p.add_run(
    "assumed diameter growth by POD30 (0/10/20/30/40% for each vessel "
    "independently, plus a 2D grid varying both together, 0/10/20% each) "
    "is propagated through the continuous scenario. The hepatic-artery "
    "baseline diameter's OWN published uncertainty (1.0-1.4 mm) is also "
    "tested, with the POD1 anchor RE-FIT for each candidate baseline "
    "value: since A_HA enters the POD1 velocity calibration directly, "
    "testing a different baseline diameter without re-fitting Rs_HA, "
    "L_HA, and P_HA_amp would silently detune the POD1 anchor away from "
    "the real measured PSV_HA/RI_HA targets, producing a spurious "
    "baseline-diameter sensitivity rather than a genuine one."
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Graft-mass Q_PV scaling: ").bold = True
p.add_run(
    "Q_PV is scaled by factors of 0.5-2.0 (as if the source formula's "
    "'per 100 g' label corresponded to an actual graft mass of 200, 100, "
    "67, or 50 g respectively), holding 0% diameter growth, to check "
    "whether the unresolved graft-mass-normalization ambiguity (Section "
    "2.4) materially affects the primary result."
)

d.add_heading("2.8 Illustrative sensitivity intervals (secondary)", level=3)
d.add_paragraph(
    "In addition to the structural analyses above, which we regard as "
    "primary, Monte Carlo intervals (200,000 draws, POD1 and each later "
    "mean sampled independently with SD/sqrt(41)) are reported for the "
    "'fraction of decline reproduced' under the representative POD1 fit. "
    "We label these illustrative sensitivity intervals, not confidence "
    "intervals: independent sampling is the wrong covariance structure "
    "for this repeated-measures cohort, no PVV or model-parameter "
    "uncertainty was propagated, and no draws were discarded (including "
    "near-zero or negative simulated measured-decline draws, which "
    "produce a heavy-tailed distribution, most evident at POD7)."
)

d.add_heading("2.9 Model parameters", level=3)
t3 = d.add_table(rows=1, cols=4)
t3.style = "Light Grid Accent 1"
hdr = t3.rows[0].cells
for i, v in enumerate(["Parameter", "Value", "Units", "Source"]):
    hdr[i].text = v
param_rows = [
    ("HR", "130", "beats/min", "assumed, representative infant heart rate"),
    ("P_PV_src, P_HA_mean (generic)", "13.0, 57.5", "mmHg",
     "Ho/Yu/Bartlett calibration targets"),
    ("P_IVC", "2.0", "mmHg", "assumed (not reported in source)"),
    ("Rs_PV, Rs_HV, Rp_hv_out (generic)", "1.526, 0.242, 0.385",
     "mmHg*s/mL", "solved exactly from generic targets; reused post-LDLT"),
    ("Rs_HA, L_HA (generic)", "97.96 mmHg*s/mL, 2.0 mmHg*s^2/mL",
     "see units column", "solved/assumed for generic model; NOT reused post-LDLT (2.4)"),
    ("A_HA (hepatic artery area)", "0.0113", "cm^2",
     "Kim et al. 2007 (1.2 mm diameter, healthy infant control group) -- "
     "assumed, not measured for this cohort"),
    ("Rs_HA, L_HA, P_HA_amp (POD1, representative family member)",
     "127.92 mmHg*s/mL, 5.80 mmHg*s^2/mL, 27.43 mmHg", "see units column",
     "jointly fit to real POD1 PSV_HA/RI_HA -- 3 unknowns/2 targets, "
     "non-unique; full admissible family propagated in Section 2.7/3.3"),
    ("L_PV, L_HV", "0.01, 0.02", "mmHg*s^2/mL", "assumed"),
    ("C_sinus, C_hv", "2.0, 2.0", "mL/mmHg", "assumed"),
    ("Rp_sinus", "500", "mmHg*s/mL", "assumed"),
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
    "Table 3: Full model parameter list, with explicit physical units "
    "throughout (P in mmHg, Q in mL/s during integration, tau in seconds).")
cap.runs[0].italic = True

d.add_heading("2.10 Candidate residual mechanisms: literature search", level=3)
d.add_paragraph(
    "A literature search (PubMed/EuropePMC, citations verified against "
    "primary sources or the EuropePMC metadata API before use) was "
    "conducted for real, plausible, non-HABR mechanisms, presented as "
    "testable hypotheses, not identified mechanisms."
)

# -------------------------------------------------------------------- Results
d.add_heading("Results", level=2)

d.add_heading("3.1 Generic model calibration", level=3)
d.add_paragraph(
    "The generic pi-filter model reproduced the calibration targets "
    "within 2% by construction (Figure 3) and the qualitative waveform "
    "pattern reported in the source work (Figure 2)."
)

d.add_heading("3.2 POD1 anchor: a representative, non-unique fit", level=3)
d.add_paragraph(
    "One representative member of the admissible family (Rs_HA=127.92 "
    "mmHg*s/mL, L_HA=5.80 mmHg*s^2/mL, P_HA_amp=27.43 mmHg; Table 3) "
    "reproduces measured PSV_HA (53.10 cm/s) and RI_HA (0.610) exactly by "
    "construction, with a periodic-steady-state mean HA flow of 25.0 "
    "mL/min. We do not treat this flow value as an independently "
    "interpretable plausibility check (Section 2.2.1): it depends on the "
    "assumed HA area and an unmodelled velocity-profile factor, both "
    "absorbed into the fit."
)

d.add_heading("3.3 The POD1 non-identifiability is not the dominant "
              "source of uncertainty", level=3)
d.add_paragraph(
    "Scanning P_HA_amp from 23.5 (the approximate threshold below which "
    "RI=0.61 becomes unreachable) to 60 mmHg (a practical upper bound "
    "for this analysis, not a hard mathematical limit) and re-solving "
    "Rs_HA, L_HA for each value gives a family of 19 exact POD1 fits. "
    "Propagating every member through the continuous scenario to POD30 "
    "gives a relatively narrow envelope: 20.2-27.1% of the measured "
    "PSV_HA decline reproduced (Figure 6). This is narrower than might "
    "be expected because Rs_HA and the resulting mean HA flow are almost "
    "unchanged across the family (Rs_HA=127.9-127.9 mmHg*s/mL, mean flow "
    "=25.0 mL/min throughout) -- L_HA and P_HA_amp trade off against each "
    "other to preserve the same pulsatility ratio, but the mean-flow "
    "quantity that drives the HABR update is well-constrained by the two "
    "POD1 targets even though the full three-parameter fit is not."
)
d.add_picture("HABR_Figure_6_identifiability_envelope.png", width=Inches(5.8))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph(
    "Figure 6: '% of decline reproduced' across the admissible POD1-fit "
    "family.")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True

d.add_heading("3.4 Three scenarios (representative fit)", level=3)
d.add_paragraph(
    "Using the representative fit, under zero assumed calibre growth, "
    "the three scenarios diverge by POD30 (Figure 4, Table 2): the null "
    "scenario predicts PSV_HA would rise slightly (53.10 to 53.27 cm/s); "
    "both HABR scenarios predict a fall (continuous to 49.41 cm/s, "
    "acute-then-frozen to 52.57 cm/s). Section 3.5 shows this "
    "directional difference is itself contingent on the calibre "
    "assumptions."
)
d.add_picture("HABR_Figure_4_three_scenarios_consistent.png", width=Inches(6.3))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph("Figure 4: Measured vs. all three scenarios.")
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

d.add_heading("3.5 Calibre-growth sensitivity dominates: portal AND "
              "arterial, jointly", level=3)
d.add_paragraph(
    "The hepatic artery's OWN baseline-diameter uncertainty (1.0-1.4 mm, "
    "properly re-anchored at POD1 for each value) has little effect when "
    "calibre is held constant thereafter (23.7-26.4% explained across "
    "this range) -- baseline uncertainty is largely absorbed by "
    "recalibration, as it should be. Postoperative GROWTH is entirely "
    "different: hepatic-artery diameter growth alone (portal growth held "
    "at 0%) moves the result from 25.3% (no growth) to 191.2% at 40% "
    "growth -- growth in HA calibre amplifies the apparent effect (since "
    "dilution adds to, rather than opposes, the flow-based prediction), "
    "in the OPPOSITE direction to portal-diameter growth, which reverses "
    "its sign (Figure 7). The two are not independent: a 2D grid varying both "
    "(Figure 8) shows the result ranges from -44% (20% portal growth, no "
    "HA growth) to +129% (no portal growth, 20% HA growth) across a "
    "modest, jointly plausible range. Neither vessel's calibre change is "
    "measured in this cohort past POD1, and this analysis shows both "
    "matter, not only the portal side."
)
d.add_picture("HABR_Figure_7_diameter_sensitivity_consistent.png", width=Inches(5.3))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph("Figure 7: Portal-diameter-growth sensitivity.")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True
d.add_picture("HABR_Figure_8_2D_diameter_grid.png", width=Inches(5.3))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph(
    "Figure 8: Joint portal x hepatic-artery calibre-growth sensitivity.")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True
d.add_paragraph(
    "By contrast, the graft-mass Q_PV-scaling ambiguity (Section 2.4, "
    "2.7) has almost no effect: scaling Q_PV by 0.5-2.0x (as if graft "
    "mass were 200-50 g rather than 100 g) changes the POD30 result only "
    "from 25.5% to 25.1%. The passive sinusoidal coupling this ambiguity "
    "affects is evidently weak relative to the HABR-driven resistance "
    "change in this model; this specific concern, while conceptually "
    "valid (Section 2.4), turns out not to be a material source of "
    "uncertainty here."
)

d.add_heading("3.6 RI comparison", level=3)
d.add_paragraph(
    "POD1 vs. POD7 RI_HA differ by 0.020 (95% CI [0.002, 0.038], "
    "p=0.032); POD7 vs. POD30 do not detectably differ (95% CI [-0.010, "
    "+0.010], p=1.00) -- this interval EXCLUDES a true difference as "
    "large as 0.020. We describe RI as 'not detectably changing' after "
    "POD7, and treat the acute-then-frozen scenario as a hypothesis "
    "motivated by, not demonstrated by, this observation."
)

d.add_heading("3.7 Illustrative sensitivity intervals (secondary)", level=3)
d.add_paragraph(
    "Under the continuous scenario and the representative POD1 fit: "
    "approximately 11% [5%, 64%] at POD7, 20% [13%, 43%] at POD14, 25% "
    "[18%, 40%] at POD30 (Section 2.8). We regard these as of limited "
    "additional value beyond the structural analyses above (Section 3.3, "
    "3.5), which we consider the primary uncertainty characterisation "
    "for this study."
)

d.add_heading("3.8 Candidate mechanisms for any residual decline", level=3)
d.add_paragraph(
    "Whatever the model does not reproduce may reflect a real "
    "physiological mechanism not included here, or model "
    "misspecification, or measurement variability -- this study cannot "
    "distinguish between these possibilities. Two literature-grounded "
    "physiological candidates are presented as testable hypotheses:"
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Systemic haemodynamic normalization: ").bold = True
p.add_run(
    "resolves within days (3-5 postoperative days in one adult cohort, "
    "n=57; Plevak et al., 1993; related timescales 4 days to 2 weeks, "
    "Dashti et al., 2020)."
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Graft-regeneration-driven vessel-calibre dilution: ").bold = True
p.add_run(
    "graft mass increases substantially over weeks (~1.7-fold by 2 "
    "weeks; Byun et al., 2016), which Section 3.5 shows would materially "
    "affect Doppler velocity if it applies to vessel calibre "
    "specifically -- though quantitative regeneration data are "
    "inconsistent across the (adult, non-LLS) studies located (Marcos et "
    "al., 2000; Zhang et al., 2022), graft volume does not necessarily "
    "translate into proportional arterial growth near an anastomosis, "
    "and paediatric LLS grafts are often not classically undersized "
    "(Vargas and Goldaracena, 2024), so even the direction of expected "
    "calibre change is not established for this population."
)
d.add_paragraph(
    "Other unmodelled, plausible contributors: systemic cardiac output/"
    "pressure-amplitude changes beyond the fixed assumption used here; "
    "postoperative oedema; arterial spasm; anastomotic geometry; Doppler "
    "insonation angle or sampling-location variation; sedation; heart "
    "rate. None were assessed here."
)

# ---------------------------------------------------------------- Discussion
d.add_heading("Discussion", level=2)
d.add_paragraph(
    "This model shows that a fixed-coefficient HABR relationship "
    "predicts a fall in hepatic arterial velocity under a specific set "
    "of assumptions (constant vessel calibre after POD1, an assumed "
    "hepatic-artery area, one representative member of a non-identifiable "
    "parameter family). Two structural analyses determine how much weight "
    "this prediction can bear. The POD1 non-identifiability, propagated "
    "fully rather than reported as one point estimate, turns out to be "
    "a relatively minor source of uncertainty (20-27% across the "
    "admissible family) because the mean-flow-determining parameters are "
    "well-constrained even though the full three-parameter fit is not. "
    "The vessel-calibre assumptions are the dominant uncertainty: varying "
    "plausible, jointly-assumed portal and hepatic-artery diameter growth "
    "moves the same quantity from -44% to +129%, and neither vessel's "
    "calibre is measured past POD1 in the available data. We do not "
    "conclude that HABR's quantitative contribution to this cohort's "
    "trajectory can be established; we conclude that it cannot be, "
    "without serial vessel-calibre measurement that does not currently "
    "exist for this population."
)
d.add_paragraph(
    "Limitations. The circulation is a single lobe with lumped elements, "
    "not the fuller multi-generation vascular tree used in some prior "
    "work by this group. The generic model's calibration targets and the "
    "HABR coefficients come from two unpublished manuscripts; we searched "
    "for published alternatives and did not find equivalent real "
    "paediatric LLS-LDLT data. The assumed hepatic-artery area (Section "
    "2.2.1) is sourced from a different, native, non-transplant "
    "population; the mean-velocity-versus-Doppler-PSV distinction means "
    "the resulting absolute flow values should not be over-interpreted. "
    "The pre-transplant to POD1 transition is not modelled (discrete "
    "organ-replacement event). Graft-to-recipient weight ratio is unknown "
    "for this cohort, bearing on the unresolved portal-flow-formula "
    "normalization (Section 2.4), though this specific ambiguity was "
    "shown (Section 3.5) not to matter much in practice. All comparisons "
    "use group-level data; the illustrative sensitivity intervals "
    "(Section 3.7) are not proper confidence intervals for this cohort's "
    "repeated-measures structure."
)
d.add_paragraph(
    "We would not currently recommend this framework for individual-"
    "patient interpretation. Its contribution is narrower: it "
    "demonstrates, with the two structural analyses above, that testing "
    "HABR's contribution to this cohort's PSV_HA trajectory requires "
    "serial vessel-calibre data (both portal and hepatic-arterial) that "
    "does not currently exist, and quantifies how large a difference "
    "that missing data would make."
)

d.add_heading("Data, code, and ethics", level=2)
d.add_paragraph(
    "This is a secondary analysis of de-identified data reported in Chen "
    "et al. (2022), collected under the ethics approval described in "
    "that publication; no new human-subjects data were collected. Given "
    "the non-unique calibration and the sensitivity analyses reported "
    "here, reproducibility is particularly important; a public code "
    "repository is intended to accompany submission."
)

d.add_heading("Conclusion", level=2)
d.add_paragraph(
    "A dimensionally-consistent, calibrated pi-filter model of "
    "paediatric post-LDLT hepatic circulation shows that a fixed-"
    "coefficient hepatic arterial buffer response relationship predicts "
    "a fall in hepatic arterial velocity under specific assumptions. "
    "Propagating the model's own parameter non-identifiability shows this "
    "is a relatively minor source of uncertainty; propagating plausible, "
    "unmeasured vessel-calibre growth in both the portal and hepatic-"
    "arterial trees shows this is the dominant one, moving the result "
    "across a range wide enough to include the opposite sign. We "
    "conclude that HABR's contribution to this cohort's observed "
    "trajectory cannot be quantified from the available data, and that "
    "doing so requires serial vessel-calibre measurement not currently "
    "available for this population."
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
