"""
Manuscript reframed for submission to Medical Engineering & Physics:
computational-physiology / model-identifiability framing, numbered
(Vancouver) citation style matching MEP house style, Highlights,
graphical abstract, and a structured Declarations section. All
substantive scientific content, numbers, tables, and reviewer-driven
precision language carried over unchanged from the round-6 manuscript;
what changes is framing, citation style, and structure.

Citation numbering (order of first appearance):
[1] Eipel, Abshagen, Vollmar 2010
[2] Ho, Sorrell, Bartlett, Hunter 2013
[3] Yu, Bartlett, Hunter, Ho (unpublished)
[4] Ho, Yu, Bartlett (unpublished)
[5] Chen et al. 2022
[6] Kim et al. 2007
[7] Plevak et al. 1993
[8] Dashti et al. 2020
[9] Byun et al. 2016
[10] Marcos et al. 2000
[11] Zhang et al. 2022
[12] Vargas and Goldaracena 2024
"""

import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

d = docx.Document()

d.add_heading(
    "A Sensitivity and Identifiability Framework for Testing the "
    "Hepatic Arterial Buffer Response After Paediatric Liver "
    "Transplantation", level=1)

# ---------------------------------------------------------------- Highlights
d.add_heading("Highlights", level=2)
for h in [
    "Dimensionally consistent pi-filter model tests HABR after paediatric LDLT",
    "Propagated parameter non-identifiability is not the dominant uncertainty",
    "Vessel-calibre growth sensitivity spans results of opposite sign",
    "Framework specifies what serial measurements would resolve HABR's role",
    "Doppler indices alone cannot quantify HABR's contribution post-transplant",
]:
    p = d.add_paragraph(style="List Bullet")
    p.add_run(h)

d.add_picture("Graphical_Abstract.png", width=Inches(6.3))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph("Graphical abstract.")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True

# ---------------------------------------------------------------- Abstract
d.add_heading("Abstract", level=2)
d.add_paragraph(
    "Post-transplant Doppler surveillance is routinely interpreted using "
    "mechanistic hypotheses -- most often the hepatic arterial buffer "
    "response (HABR) -- without models that account for their own "
    "structural uncertainty. We present a computational-physiology "
    "framework that does: a dimensionally-consistent lumped-parameter "
    "('pi-filter') hepatic circulation model, in which every state "
    "variable is a genuine volumetric flow related to Doppler velocity "
    "only through an explicit, literature-sourced vessel-calibre "
    "assumption, paired with two structural sensitivity analyses -- "
    "propagation of the model's own parameter non-identifiability, and "
    "propagation of unmeasured vessel-calibre change -- rather than a "
    "single best-fit result. Applied to a real cohort of 41 infants after "
    "left-lateral-segment living-donor liver transplantation for biliary "
    "atresia, the hepatic-arterial branch's calibration is non-"
    "identifiable (three parameters fit to two Doppler targets); "
    "propagating the whole explored parameter family gives a relatively "
    "narrow result envelope (20-27% of the measured decline in hepatic "
    "artery peak systolic velocity reproduced by postoperative day 30). "
    "Propagating illustrative postoperative growth in portal and "
    "hepatic-artery calibre -- neither measured beyond day 1 in the "
    "source cohort -- moves the same quantity from -44% to +129% across "
    "a modest illustrative range, and this dominance of calibre "
    "uncertainty over parameter non-identifiability is preserved whether "
    "growth is modelled as a pure velocity-observation effect or with "
    "additional geometric remodelling of arterial inertance. The "
    "practical result is not a quantitative attribution of HABR's role, "
    "but a specification of what would make one possible: serial "
    "hepatic-arterial and portal-vein calibre measurement, which this "
    "analysis shows matters more than any further model refinement. We "
    "argue this identifiability-and-sensitivity approach, not the "
    "specific HABR finding, is the transferable contribution, applicable "
    "to any Doppler-based mechanistic hypothesis test in post-transplant "
    "or post-surgical vascular surveillance."
)

d.add_heading("Keywords", level=3)
d.add_paragraph(
    "hepatic arterial buffer response; liver transplantation; paediatric; "
    "Doppler ultrasound; lumped-parameter model; identifiability analysis; "
    "sensitivity analysis; computational physiology"
)

# ------------------------------------------------------------ Introduction
d.add_heading("1. Introduction", level=2)
d.add_paragraph(
    "Doppler ultrasound surveillance after paediatric liver "
    "transplantation is interpreted largely through qualitative "
    "physiological reasoning: a falling hepatic artery resistive index "
    "(RI) or peak systolic velocity (PSV) is commonly attributed to the "
    "hepatic arterial buffer response (HABR), the intrinsic tendency of "
    "hepatic arterial flow to counteract changes in portal venous flow, "
    "mediated by adenosine washout in the periportal space of Mall [1]. "
    "This attribution is rarely tested against a mechanistic model, and "
    "even where models exist, they are rarely checked for whether their "
    "own calibration is unique, or how sensitive their conclusions are to "
    "quantities the clinical data do not measure. This paper develops "
    "and demonstrates a general computational-physiology approach to "
    "both problems, using HABR attribution after paediatric living-donor "
    "liver transplantation (LDLT) as the test case."
)
d.add_paragraph(
    "Prior work from this group modelled HABR using an electrical-analog "
    "('pi-filter') lumped-parameter circulation model with an empirical "
    "quadratic regulation function [2], subsequently applied in "
    "unpublished draft form to an adult-to-child left-lateral-segment "
    "(LLS) transplantation scenario [3,4]. We rely on these two "
    "unpublished sources for specific calibration pressure/flow values "
    "because no equivalent published dataset for this exact clinical "
    "scenario was located; this dependence is a genuine limitation "
    "(Section 4)."
)
d.add_paragraph(
    "Chen et al. report serial hepatic artery and portal vein Doppler "
    "measurements in 41 infants (4-18 months, biliary atresia) before "
    "and after LLS-LDLT, at postoperative day (POD) 1, 7, 14, and 30 "
    "[5]. Hepatic artery PSV and RI both fall over this month, "
    "attributed qualitatively to HABR by the authors, without a "
    "quantitative mechanistic test."
)
d.add_paragraph(
    "This study makes two contributions, one methodological and one "
    "substantive, and we present the methodological contribution as the "
    "primary one. First (methods), we show how to build a lumped-"
    "parameter Doppler-interpretation model that is dimensionally "
    "consistent throughout -- every flow variable on a common physical "
    "basis, related to measured velocity only through an explicit, "
    "sourced vessel-calibre assumption -- and how to propagate, rather "
    "than merely disclose, the model's own parameter non-identifiability "
    "and its sensitivity to calibre quantities the clinical data do not "
    "measure. Second (application), applying this framework to the Chen "
    "et al. cohort shows that parameter non-identifiability is a minor "
    "source of uncertainty here, while vessel-calibre uncertainty is "
    "large enough to change the sign of the conclusion -- meaning HABR's "
    "quantitative contribution to this cohort's trajectory cannot "
    "currently be established, and specifying exactly what measurement "
    "(serial vessel calibre) would change that is itself a useful, "
    "actionable output for future study design."
)

# ------------------------------------------------------------------ Methods
d.add_heading("2. Methods", level=2)

d.add_heading("2.1 Dataset", level=3)
d.add_paragraph(
    "Chen et al. [5] (doi:10.3389/fbioe.2022.903385) report a "
    "retrospective study of 41 infants (22 male, 19 female; median age 5 "
    "months, range 4-18) with biliary atresia undergoing LLS-LDLT, with "
    "uncomplicated postoperative courses. Doppler measurements were "
    "taken pre-transplant and at POD1, 7, 14, and 30 (Table 1)."
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
cap = d.add_paragraph("Table 1: Real cohort data ([5], mean +/- SD, n=41).")
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
    "(POD), indexing which of several INDEPENDENT simulations is run, "
    "each an independently-converged periodic state."
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
    "are in mmHg; all flows (Q) are in mL/s during this integration; tau "
    "is in seconds. Under this basis: Rs and Rp in mmHg*s/mL; L in "
    "mmHg*s^2/mL; C in mL/mmHg (Table 3). Reported mean/peak flow values "
    "elsewhere in this paper are converted to mL/min (multiplying the "
    "mL/s quantity by 60) for readability; Section 2.2.1 states which "
    "convention each equation uses explicitly to avoid notational "
    "ambiguity. In the GENERIC configuration (this section), Q_PV is "
    "itself a state, governed by L_PV dQ_PV/d(tau) = P_PV - Rs_PV*Q_PV - "
    "P_sinus, with P_PV constant. In the POST-LDLT configuration (Section "
    "2.4), this equation is disabled; Q_PV is a prescribed constant for "
    "each day's simulation, overwritten between days to that day's real "
    "measured value."
)
d.add_paragraph(
    "The generic configuration was calibrated against previously-derived "
    "calibration targets [3,4] (portal driving pressure 13 mmHg, mean "
    "arterial pressure 57.5 mmHg [range 42.4-72.6], sinusoidal pressure "
    "5.37 mmHg, hepatic venous pressure 4.07 mmHg, portal flow 300 "
    "mL/min, hepatic arterial flow 31.93 mL/min, hepatic venous flow "
    "322.5 mL/min). Rs_PV, Rs_HA, Rs_HV were solved exactly via Ohm's law "
    "on the time-averaged circuit from these targets; agreement (within "
    "2%, Figure 3) is close by construction. Inertance/compliance "
    "parameters (Table 3) were chosen, not fit, for plausible "
    "pulsatility."
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
    "Q_HA(tau), as it appears in the ODE above, is in mL/s. It is "
    "related to Doppler velocity via an assumed hepatic-artery cross-"
    "sectional area A_HA: v_HA(tau) = Q_HA(tau) / A_HA (mL/s divided by "
    "cm^2 gives cm/s directly, since 1 mL = 1 cm^3; no additional unit-"
    "conversion factor is needed or applied here). One-line dimensional "
    "check: the model's POD1 mean HA flow (Section 3.2) is 25.0 mL/min = "
    "0.417 mL/s; dividing by A_HA = 0.0113 cm^2 gives a mean velocity of "
    "36.9 cm/s, consistent with (below) the simulated PSV of 53.1 cm/s, "
    "as expected for a peak-over-cycle-mean ratio in a pulsatile "
    "waveform. A_HA is set from a diameter of 1.2 mm (giving A_HA = "
    "0.0113 cm^2), the mean right hepatic artery diameter reported in a "
    "healthy, non-jaundiced infant control group (mean age 67 days) in a "
    "paediatric ultrasound reference study [6] -- an assumption for this "
    "cohort's graft artery, not a measurement of it. Section 2.7 tests "
    "both this baseline value's published uncertainty (1.0-1.4 mm) and "
    "separately, whether it changes over the postoperative month."
)
d.add_paragraph(
    "A further caveat: v = Q/A gives a cross-sectional MEAN velocity, "
    "whereas spectral Doppler PSV is conventionally read as a spatial "
    "peak, not a cross-sectional average; the source cohort's own "
    "portal-flow formula (Section 2.4) applies a factor (0.57) "
    "specifically to convert their measured (peak-like) PVV toward a "
    "mean velocity for flow calculation, and no directly analogous, "
    "independently-sourced factor is applied here on the hepatic-artery "
    "side. Because the POD1 fit (Section 2.4) calibrates directly "
    "against measured PSV_HA, this profile-shape discrepancy is absorbed "
    "into the fitted parameters rather than left as a visible residual. "
    "We therefore do NOT treat the resulting POD1 mean HA flow (Section "
    "3.2) as an independently interpretable absolute physiological "
    "quantity -- only relative (percent) changes in flow, and RI (a "
    "ratio, invariant to a fixed unmodelled profile factor as long as it "
    "does not itself change over time), are used in the conclusions that "
    "follow."
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
    "x(d) = (Q_PV(POD1) - Q_PV(d)) / Q_PV(POD1) * 100 (Q_PV from Section "
    "2.4's flow formula, each day's real measured PVV). changeIha(d) = "
    "0.0007102*x(d)^2 + 0.5492*x(d). Q_HA_target(d) = Q_HA_ref * (1 - "
    "changeIha(d)/100), Q_HA_ref being the model's periodic-steady-state "
    "mean HA flow at the POD1 anchor. Rs_HA(d) is found by Brent's "
    "method (scipy.optimize.brentq; initial bracket [0.3, 3.0] times the "
    "POD1-fitted Rs_HA, expanded geometrically by 0.7/1.4 up to 40 times "
    "if no sign change is found; convergence tolerance 1e-8; treated as "
    "a failure, and excluded, if no sign change is found within the "
    "expansion limit) such that simulating with P_HA_mean, P_HA_amp, and "
    "L_HA held at their POD1-fitted values and Q_PV fixed at Q_PV(d) "
    "gives a periodic-steady-state mean HA flow equal to Q_HA_target(d). "
    "In the CONTINUOUS scenario, the reference day is always POD1. In "
    "the ACUTE-THEN-FROZEN scenario, this is performed once, for d=POD7; "
    "Rs_HA(POD14)=Rs_HA(POD30)=Rs_HA(POD7)."
)

d.add_heading("2.4 Post-LDLT model anchoring, and its non-identifiability", level=3)
d.add_paragraph(
    "Q_PV(d) is computed via the source cohort's reported formula, PVF = "
    "pi*r^2*0.57*PVV*60 (r=diameter/2 in cm, PVV in cm/s), yielding a "
    "quantity with units of mL/min despite the source paper's 'per 100 g "
    "graft' label, which includes no graft-mass term; graft weight was "
    "not available to us. Section 2.7 tests whether this ambiguity "
    "matters, by scaling Q_PV as if graft mass were 50-200 g. Portal "
    "diameter is reported only at pre-transplant (0.44 cm) and POD1 "
    "(0.46 cm); held at the POD1 value for POD7-30 in the primary "
    "analysis."
)
d.add_paragraph(
    "Rs_HA, L_HA, and P_HA_amp are calibrated JOINTLY at POD1 against "
    "real measured PSV_HA and RI_HA -- three unknowns, two targets, "
    "necessarily non-unique. Fixing P_HA_amp at the generic model's "
    "literature value (15.1 mmHg) made RI_HA=0.61 unreachable for any "
    "tested (Rs_HA, L_HA) combination (achievable RI capped near 0.48 "
    "across a wide grid search); P_HA_amp is therefore a third free "
    "parameter. Section 2.7 generates the admissible family within a "
    "prespecified, explored range of P_HA_amp (approximately 23.5 mmHg, "
    "the threshold below which no exact fit exists, to 60 mmHg, a "
    "practical bound for this analysis) and propagates every member "
    "through POD30, rather than reporting one arbitrarily-selected "
    "solution; we refer to this as the admissible family WITHIN THIS "
    "RANGE, not the entire admissible family, since no upper mathematical "
    "bound on P_HA_amp exists."
)

d.add_heading("2.5 Three HABR-application scenarios, as alternatives", level=3)
d.add_paragraph(
    "HABR's adenosine-washout kinetics equilibrate within minutes to a "
    "few hours, but describe continuous coupling between portal flow "
    "and periportal adenosine concentration, not a single event that "
    "occurs once and then stops [1]. Fast equilibration therefore does "
    "not by itself justify confining HABR's application to any "
    "particular window of the postoperative month. Three scenarios are "
    "presented as alternatives, not as one preferred model with the "
    "others as baselines:"
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Continuous: ").bold = True
p.add_run("Rs_HA(d) set from Section 2.3's update at every day d.")
p = d.add_paragraph(style="List Bullet")
p.add_run("Acute-then-frozen: ").bold = True
p.add_run(
    "Rs_HA set once, for POD7, then held fixed. Motivated by, not proven "
    "by (Section 2.6): mean RI_HA is numerically flat (0.59) from POD7 "
    "through POD30."
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Null: ").bold = True
p.add_run("Rs_HA frozen at its POD1 value throughout.")

d.add_heading("2.6 Testing whether RI is really flat", level=3)
d.add_paragraph(
    "We compared RI between time points using an unpaired Welch's "
    "t-test and a 95% confidence interval calculated from the published "
    "summary statistics (mean, SD, n=41) -- a conservative "
    "approximation, since the cohort is repeated-measures on the same "
    "41 patients. This is an ordinary unpaired comparison of summary "
    "statistics, not an equivalence test."
)

d.add_heading("2.7 Structural sensitivity analyses", level=3)
d.add_paragraph(
    "Four analyses address the model's structural uncertainties -- the "
    "methodological core of this study:"
)
p = d.add_paragraph(style="List Bullet")
p.add_run("POD1 identifiability envelope: ").bold = True
p.add_run(
    "the admissible (Rs_HA, L_HA, P_HA_amp) family within P_HA_amp in "
    "[23.5, 60] mmHg (19 values, spaced 2 mmHg apart from 24 to 60, plus "
    "the 23.5 mmHg threshold point) is propagated through the continuous "
    "scenario to POD30. Each point is fit by minimising squared relative "
    "error in PSV and RI jointly (Nelder-Mead, tolerance 1e-8 on "
    "parameters / 1e-14 on the objective; a fit is accepted only if the "
    "residual objective is below 1e-6, otherwise excluded), warm-started "
    "from the previous point's solution. To check whether 60 mmHg "
    "understates the envelope, we additionally solved points up to 300 "
    "mmHg (a supraphysiological pressure amplitude, useful only to test "
    "mathematical convergence): the result stabilises asymptotically "
    "(20.2% at 60 mmHg to 18.8% at 300 mmHg), so extending the explored "
    "range further would change the envelope only marginally."
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Illustrative portal/hepatic-artery calibre-growth sensitivity: ").bold = True
p.add_run(
    "assumed diameter growth by POD30 (0/10/20/30/40% for each vessel "
    "independently, plus a 2D grid varying both together, 0/10/20% each) "
    "is propagated through the continuous scenario, using the "
    "representative POD1 fit. We call these growth values illustrative, "
    "not plausible or probable: no source measures serial vascular "
    "calibre change in this population, which is precisely the premise "
    "motivating this analysis. Two variants are distinguished explicitly: "
    "(i) KINEMATIC DILUTION ONLY -- only A_HA (used in the flow-to-"
    "velocity conversion, Section 2.2.1) is changed for the growth "
    "calculation; Rs_HA is still re-solved via Section 2.3's HABR "
    "flow-target procedure exactly as in the primary analysis, but L_HA "
    "and the underlying circuit are otherwise unaffected by the assumed "
    "growth -- this is the PRIMARY analysis reported in Results 3.5, and "
    "is a velocity-observation effect, not a full physical simulation of "
    "arterial remodelling; (ii) EXPLORATORY STRUCTURAL REMODELLING -- "
    "L_HA is additionally scaled geometrically, L_HA(d) = L_HA_pod1 / "
    "(1+g)^2 for assumed radius growth fraction g (inertance scaling as "
    "1/r^2 for a fixed-length vessel), with Rs_HA still solved via the "
    "same HABR flow-target procedure using this grown L_HA; this is a "
    "secondary, exploratory check, reported in Results 3.5, of whether "
    "the kinematic-only simplification materially misleads. Because "
    "resistance remains determined by the HABR flow target rather than "
    "an independent radius-resistance law, this variant evaluates "
    "inertial remodelling but is not a complete geometric reconstruction "
    "of vascular growth. The hepatic-artery baseline diameter's own "
    "published uncertainty (1.0-1.4 mm) is tested with the POD1 anchor "
    "RE-FIT for each candidate baseline (re-fitting is necessary because "
    "A_HA enters the POD1 velocity calibration directly), and combined "
    "with the growth sensitivity to check whether the growth-sensitivity "
    "shape depends on the assumed baseline."
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Graft-mass Q_PV scaling: ").bold = True
p.add_run(
    "Q_PV scaled by 0.5-2.0x (as if graft mass were 200-50 g), holding "
    "0% diameter growth, to check whether the unresolved graft-mass-"
    "normalization ambiguity (Section 2.4) materially affects the "
    "primary result."
)

d.add_heading("2.8 Illustrative sensitivity intervals (secondary)", level=3)
d.add_paragraph(
    "Monte Carlo intervals (200,000 draws, POD1 and each later mean "
    "sampled independently with SD/sqrt(41)) for the 'fraction of "
    "decline reproduced' under the representative POD1 fit, reported as "
    "illustrative sensitivity intervals, not confidence intervals: "
    "independent sampling is the wrong covariance structure for this "
    "repeated-measures cohort, no PVV or model-parameter uncertainty was "
    "propagated, and no draws were discarded (including near-zero or "
    "negative simulated measured-decline draws, which produce a heavy-"
    "tailed distribution at POD7). We regard these as secondary to the "
    "structural analyses in Section 2.7, which are this study's "
    "principal methodological contribution."
)

d.add_heading("2.9 Model parameters", level=3)
t3 = d.add_table(rows=1, cols=4)
t3.style = "Light Grid Accent 1"
hdr = t3.rows[0].cells
for i, v in enumerate(["Parameter", "Value", "Units", "Source"]):
    hdr[i].text = v
param_rows = [
    ("HR", "130", "beats/min", "assumed, representative infant heart rate"),
    ("P_PV_src (generic)", "13.0", "mmHg", "calibration target [3,4]"),
    ("P_HA_mean (generic)", "57.5", "mmHg", "calibration target [3,4]"),
    ("P_IVC", "2.0", "mmHg", "assumed (not reported in source)"),
    ("Rs_PV (generic)", "1.526", "mmHg*s/mL", "solved exactly from generic targets; reused post-LDLT"),
    ("Rs_HV (generic)", "0.242", "mmHg*s/mL", "solved exactly from generic targets; reused post-LDLT"),
    ("Rp_hv_out (generic)", "0.385", "mmHg*s/mL", "solved exactly from generic targets; reused post-LDLT"),
    ("Rs_HA (generic)", "97.96", "mmHg*s/mL", "solved for generic model; NOT reused post-LDLT (2.4)"),
    ("L_HA (generic)", "2.0", "mmHg*s^2/mL", "assumed for generic model; NOT reused post-LDLT (2.4)"),
    ("A_HA (hepatic artery area)", "0.0113", "cm^2",
     "[6] (1.2 mm diameter, healthy infant control group) -- assumed, "
     "not measured for this cohort"),
    ("Rs_HA (POD1, representative family member)", "127.92", "mmHg*s/mL",
     "jointly fit to real POD1 PSV_HA/RI_HA with L_HA, P_HA_amp -- 3 "
     "unknowns/2 targets, non-unique; explored admissible family within "
     "P_HA_amp = 23.5-60 mmHg (19 points, Rs_HA range 127.92-127.93, L_HA "
     "range 2.16-22.23 mmHg*s^2/mL) propagated in Section 2.7/3.3"),
    ("L_HA (POD1, representative family member)", "5.80", "mmHg*s^2/mL",
     "jointly fit, as above"),
    ("P_HA_amp (POD1, representative family member)", "27.43", "mmHg",
     "jointly fit, as above"),
    ("L_PV, L_HV", "0.01, 0.02", "mmHg*s^2/mL", "assumed"),
    ("C_sinus, C_hv", "2.0, 2.0", "mL/mmHg", "assumed"),
    ("Rp_sinus", "500", "mmHg*s/mL", "assumed"),
    ("Portal diameter (POD1)", "0.46", "cm",
     "[5]; held fixed POD7-30 in primary analysis"),
    ("PV velocity-to-flow factor", "0.57", "dimensionless", "[5]"),
    ("Integration", "forward Euler, 400 steps/cycle", "-", "-"),
    ("Convergence criterion", "<1e-4 relative change, consecutive cycles", "-", "-"),
]
for row in param_rows:
    cells = t3.add_row().cells
    for i, v in enumerate(row):
        cells[i].text = v
cap = d.add_paragraph(
    "Table 3: Full model parameter list, with explicit physical units "
    "throughout.")
cap.runs[0].italic = True

d.add_heading("2.10 Candidate residual mechanisms: literature search", level=3)
d.add_paragraph(
    "A literature search (PubMed/EuropePMC, citations verified against "
    "primary sources or the EuropePMC metadata API before use) was "
    "conducted for real, plausible, non-HABR mechanisms, presented as "
    "testable hypotheses, not identified mechanisms."
)

# -------------------------------------------------------------------- Results
d.add_heading("3. Results", level=2)

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
    "mL/min (0.417 mL/s; 36.9 cm/s cross-sectional mean velocity, "
    "Section 2.2.1). We do not treat this flow value as an independently "
    "interpretable plausibility check: it depends on the assumed HA area "
    "and an unmodelled velocity-profile factor, both absorbed into the "
    "fit."
)

d.add_heading("3.3 Parameter non-identifiability, propagated: a minor "
              "source of uncertainty", level=3)
d.add_paragraph(
    "Across the 19-point explored family (P_HA_amp 24-60 mmHg, plus the "
    "23.5 mmHg threshold point), Rs_HA varies only from 127.92 to 127.93 "
    "mmHg*s/mL and the resulting mean HA flow is unchanged at 25.0 "
    "mL/min, while L_HA ranges from 2.16 to 22.23 mmHg*s^2/mL -- L_HA "
    "and P_HA_amp trade off against each other to preserve the same "
    "pulsatility ratio at POD1, while Rs_HA (and the mean flow it "
    "implies) is well-constrained by the two POD1 targets regardless. "
    "Propagating every member through POD30 gives a relatively narrow "
    "envelope: 20.2-27.1% of the measured PSV_HA decline reproduced "
    "(Figure 6), stabilising toward about 18.8% if the explored P_HA_amp "
    "range is extended to a supraphysiological 300 mmHg (Section 2.7). "
    "Despite Rs_HA and mean flow being nearly constant across the "
    "family, the PSV-based 'fraction reproduced' still varies "
    "measurably (20.2-27.1%) because PSV depends on the PULSATILE SHAPE "
    "of the waveform, not only its mean: different (L_HA, P_HA_amp) "
    "combinations that reproduce the same POD1 mean flow and PSV/RI can "
    "still respond differently in peak-to-mean ratio once Rs_HA is "
    "subsequently adjusted at POD30 to hit a new HABR-implied mean-flow "
    "target, which is why the envelope is narrow but not exactly zero. "
    "This result is itself methodologically important: it demonstrates "
    "that a model can be non-identifiable in its full parameter space "
    "while still being well-constrained in the specific output quantity "
    "a downstream analysis depends on -- a distinction only visible by "
    "propagating the family, not by reporting a single fit."
)
d.add_picture("HABR_Figure_6_identifiability_envelope.png", width=Inches(5.8))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph(
    "Figure 6: '% of decline reproduced' across the admissible POD1-fit "
    "family within the explored P_HA_amp range.")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True

d.add_heading("3.4 Three scenarios (representative fit)", level=3)
d.add_paragraph(
    "Using the representative fit, under zero assumed calibre growth, "
    "the three scenarios diverge by POD30 (Figure 4, Table 2): the null "
    "scenario predicts PSV_HA would rise slightly (53.10 to 53.27 cm/s); "
    "both HABR scenarios predict a fall (continuous to 49.41 cm/s, "
    "acute-then-frozen to 52.57 cm/s). Section 3.5 shows this "
    "directional difference is contingent on the calibre assumptions."
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

d.add_heading("3.5 Illustrative vessel-calibre sensitivity exceeds "
              "parameter-fit uncertainty", level=3)
d.add_paragraph(
    "The hepatic artery's OWN baseline-diameter uncertainty (1.0-1.4 mm, "
    "re-anchored at POD1 for each value) has little effect when calibre "
    "is held constant thereafter (23.7-26.4% reproduced across this "
    "range). Postoperative GROWTH is different: hepatic-artery diameter "
    "growth alone (portal growth held at 0%, kinematic-dilution-only "
    "variant) moves the result from 25.3% (no growth) to 191.2% at 40% "
    "growth -- in the OPPOSITE direction to portal-diameter growth, "
    "which reverses its sign (Figure 7). A 2D grid varying both (Figure "
    "8) ranges from -44% (20% portal growth, no HA growth) to +129% (no "
    "portal growth, 20% HA growth) across an ILLUSTRATIVE, unvalidated "
    "0-20% growth range in each vessel -- we do not claim this range is "
    "clinically probable, only that it is a modest range worth showing "
    "the consequences of, since no source measures serial calibre change "
    "in this population. The growth-sensitivity shape is consistent "
    "across the tested baseline diameters (at 20% HA growth: 129.5%, "
    "128.8%, 127.7% reproduced for 1.0, 1.2, 1.4 mm baseline "
    "respectively) -- the conclusion does not depend on which baseline "
    "value within its published uncertainty is assumed. This directly "
    "demonstrates that, for this application, vessel-calibre "
    "uncertainty -- not parameter non-identifiability -- is the "
    "quantity that must be constrained before HABR's contribution can "
    "be attributed."
)
d.add_picture("HABR_Figure_7_diameter_sensitivity_consistent.png", width=Inches(5.3))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph("Figure 7: Portal-diameter-growth sensitivity.")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True
d.add_picture("HABR_Figure_8_2D_diameter_grid.png", width=Inches(5.3))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = d.add_paragraph(
    "Figure 8: Joint portal x hepatic-artery calibre-growth sensitivity "
    "(illustrative range).")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.runs[0].italic = True
d.add_paragraph(
    "Because the primary HA-growth analysis above is a kinematic "
    "dilution only effect (only A_HA changes; Section 2.7), we checked "
    "whether this simplification materially misleads by additionally "
    "scaling L_HA geometrically in an exploratory structural remodelling "
    "variant (Table 4). The two give qualitatively similar, "
    "quantitatively close results (e.g. at 40% HA growth: 191.2% "
    "kinematic-only vs. 185.6% structural remodelling) -- the kinematic-"
    "only simplification is not wildly misleading for this specific "
    "comparison, though it remains, precisely, a velocity-observation "
    "effect rather than a complete physical simulation of how arterial "
    "growth would alter circuit impedance."
)
t4 = d.add_table(rows=1, cols=4)
t4.style = "Light Grid Accent 1"
hdr = t4.rows[0].cells
for i, v in enumerate(["HA growth", "Kinematic-only (% reproduced)",
                        "Structural remodelling (% reproduced)", "PSV(POD30), kinematic vs. structural"]):
    hdr[i].text = v
for row in [
    ("0%", "25.3%", "25.3%", "49.41 vs. 49.41"),
    ("10%", "84.1%", "80.5%", "40.84 vs. 41.36"),
    ("20%", "128.8%", "123.7%", "34.31 vs. 35.06"),
    ("30%", "163.6%", "158.0%", "29.24 vs. 30.05"),
    ("40%", "191.2%", "185.6%", "25.21 vs. 26.03"),
]:
    cells = t4.add_row().cells
    for i, v in enumerate(row):
        cells[i].text = v
cap = d.add_paragraph(
    "Table 4: Kinematic-dilution-only vs. exploratory structural-"
    "remodelling variants of the HA-growth sensitivity (portal growth "
    "held at 0%).")
cap.runs[0].italic = True
d.add_paragraph(
    "By contrast, the graft-mass Q_PV-scaling ambiguity (Section 2.4, "
    "2.7) has almost no effect: scaling Q_PV by 0.5-2.0x changes the "
    "POD30 result only from 25.5% to 25.1%. This specific ambiguity, "
    "while conceptually valid, is not a material source of uncertainty "
    "in this model -- a further illustration that the framework "
    "distinguishes which uncertainties matter, not merely that "
    "uncertainty exists."
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
    "[18%, 40%] at POD30. Regarded as of limited additional value beyond "
    "the structural analyses above."
)

d.add_heading("3.8 Candidate mechanisms for any residual decline", level=3)
d.add_paragraph(
    "Whatever the model does not reproduce may reflect a real "
    "physiological mechanism not included here, model misspecification, "
    "or measurement variability -- this study cannot distinguish between "
    "these possibilities. Two literature-grounded physiological "
    "candidates are presented as testable hypotheses:"
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Systemic haemodynamic normalization: ").bold = True
p.add_run(
    "resolves within days (3-5 postoperative days in one adult cohort, "
    "n=57; [7]; related timescales 4 days to 2 weeks, [8])."
)
p = d.add_paragraph(style="List Bullet")
p.add_run("Graft-regeneration-driven vessel-calibre dilution: ").bold = True
p.add_run(
    "graft mass increases substantially over weeks (~1.7-fold by 2 "
    "weeks; [9]), which Section 3.5 shows would materially affect "
    "Doppler velocity if it applies to vessel calibre specifically -- "
    "though quantitative regeneration data are inconsistent across the "
    "(adult, non-LLS) studies located ([10]; [11]), graft volume does "
    "not necessarily translate into proportional arterial growth near "
    "an anastomosis, and paediatric LLS grafts are often not classically "
    "undersized [12], so even the direction of expected calibre change "
    "is not established for this population."
)
d.add_paragraph(
    "Other unmodelled, plausible contributors: systemic cardiac output/"
    "pressure-amplitude changes beyond the fixed assumption used here; "
    "postoperative oedema; arterial spasm; anastomotic geometry; Doppler "
    "insonation angle or sampling-location variation; sedation; heart "
    "rate. None were assessed here."
)

# ---------------------------------------------------------------- Discussion
d.add_heading("4. Discussion", level=2)

d.add_heading("4.1 A transferable framework for Doppler-based mechanistic "
              "hypothesis testing", level=3)
d.add_paragraph(
    "The methodological contribution of this study is a way of testing "
    "mechanistic hypotheses against post-transplant (or, more broadly, "
    "post-surgical) Doppler surveillance data that treats the model's "
    "own uncertainty as a first-class output, not an afterthought: (i) "
    "enforce dimensional consistency throughout, so that every state "
    "variable is on a common physical basis and Doppler velocity enters "
    "only through an explicit, sourced calibre assumption; (ii) when "
    "calibration is non-identifiable, propagate the admissible parameter "
    "family rather than reporting one arbitrarily-selected solution; "
    "(iii) test sensitivity to every quantity the clinical data do not "
    "measure directly, not only the one a specific hypothesis happens to "
    "highlight. Applied here, step (ii) shows the model's own non-"
    "identifiability is a minor concern (Section 3.3), while step (iii) "
    "shows an unmeasured quantity -- vessel calibre, on both the portal "
    "and hepatic-arterial side -- is large enough to reverse the "
    "conclusion's sign (Section 3.5). This ordering is itself a finding: "
    "it would have been easy to treat the non-identifiability as the "
    "main caveat and stop there, when in fact it is not what limits this "
    "analysis."
)

d.add_heading("4.2 What this means for HABR attribution in this cohort", level=3)
d.add_paragraph(
    "Under the model's stated assumptions (constant vessel calibre after "
    "POD1, an assumed hepatic-artery area, one representative member of "
    "a non-identifiable parameter family), the fixed-coefficient HABR "
    "relationship predicts a fall in hepatic arterial velocity. We do "
    "not conclude that HABR's quantitative contribution to this cohort's "
    "trajectory can be established: the vessel-calibre sensitivity "
    "(Section 3.5) shows the result is not robust to a plausible, "
    "unmeasured change in either vessel's calibre, whether modelled as a "
    "pure velocity-observation effect or with additional structural "
    "remodelling."
)

d.add_heading("4.3 Required future measurement, framed as a positive "
              "output", level=3)
d.add_paragraph(
    "Rather than treating the absence of a quantitative HABR attribution "
    "as simply a negative result, this analysis specifies precisely what "
    "would resolve it: serial measurement of both hepatic-artery and "
    "portal-vein calibre (diameter or cross-sectional area), at the same "
    "postoperative time points already collected for velocity and RI in "
    "studies like [5]. This is a modest addition to an existing "
    "surveillance protocol -- ultrasound calibre measurement, not a new "
    "imaging modality -- and the sensitivity analysis here quantifies "
    "how much it would matter (a 10% unmeasured calibre change is enough "
    "to reverse the sign of the conclusion), which is a stronger "
    "justification for collecting it than intuition alone would provide. "
    "We consider this specification, together with the identifiability-"
    "propagation and dimensional-consistency methodology (Section 4.1), "
    "the paper's principal contribution -- more durable than any single "
    "quantitative HABR estimate, which the same missing data would in "
    "any case make premature."
)

d.add_heading("4.4 Limitations", level=3)
d.add_paragraph(
    "The circulation is a single lobe with lumped elements, not the "
    "fuller multi-generation vascular tree used in some prior work by "
    "this group. The generic model's calibration targets and the HABR "
    "coefficients come from two unpublished manuscripts [3,4]; we "
    "searched for published alternatives and did not find equivalent "
    "real paediatric LLS-LDLT data. The assumed hepatic-artery area "
    "(Section 2.2.1) is sourced from a different, native, non-transplant "
    "population [6]; the mean-velocity-versus-Doppler-PSV distinction "
    "means the resulting absolute flow values should not be over-"
    "interpreted. The structural-remodelling variant (Section 3.5) "
    "scales inertance geometrically but leaves Rs_HA determined by the "
    "HABR flow-target procedure rather than by an independent geometric "
    "resistance law. The pre-transplant to POD1 transition is not "
    "modelled, since it is a discrete organ-replacement event rather "
    "than a same-vessel flow perturbation. Graft-to-recipient weight "
    "ratio is unknown for this cohort. All comparisons use group-level "
    "data; the illustrative sensitivity intervals (Section 3.7) are not "
    "proper confidence intervals for this cohort's repeated-measures "
    "structure."
)
d.add_paragraph(
    "We would not currently recommend this framework for individual-"
    "patient interpretation. Its demonstrated value is at the cohort/"
    "study-design level: identifying, before further data collection, "
    "which uncertainties are worth resolving and which are not."
)

d.add_heading("5. Conclusion", level=2)
d.add_paragraph(
    "We present a dimensionally-consistent lumped-parameter framework "
    "for testing mechanistic Doppler-interpretation hypotheses, "
    "combining explicit vessel-calibre-to-velocity mapping with "
    "propagation of both parameter non-identifiability and calibre-"
    "assumption sensitivity. Applied to hepatic arterial buffer response "
    "attribution after paediatric LDLT, the framework shows that "
    "parameter non-identifiability is a relatively minor uncertainty "
    "(20-27% of the measured decline reproduced across the explored "
    "family) while illustrative vessel-calibre growth -- unmeasured "
    "beyond POD1 in the available data -- dominates, spanning a range "
    "wide enough to include the opposite sign. HABR's quantitative "
    "contribution to this cohort's observed trajectory therefore cannot "
    "be established from current data; what can be established is "
    "exactly what serial measurement would make that possible. We "
    "propose this identifiability-and-sensitivity approach as a general "
    "template for testing mechanistic hypotheses against post-surgical "
    "Doppler surveillance data."
)

d.add_heading("Declarations", level=2)
d.add_heading("Funding", level=3)
d.add_paragraph("[To be completed by the corresponding author before submission.]")
d.add_heading("Competing interests", level=3)
d.add_paragraph("[To be completed by the corresponding author before submission.]")
d.add_heading("Ethical approval", level=3)
d.add_paragraph(
    "This is a secondary analysis of de-identified data reported in "
    "Chen et al. [5], collected under the ethics approval described in "
    "that publication; no new human-subjects data were collected."
)
d.add_heading("Data availability", level=3)
d.add_paragraph(
    "The code underlying this analysis will be deposited in a public "
    "repository before publication."
)

d.add_heading("References", level=2)
refs = [
    "[1] Eipel C, Abshagen K, Vollmar B. Regulation of hepatic blood "
    "flow: the hepatic arterial buffer response revisited. World J "
    "Gastroenterol 2010;16(48):6046-6057. doi:10.3748/wjg.v16.i48.6046",
    "[2] Ho H, Sorrell K, Bartlett A, Hunter P. Modeling the hepatic "
    "arterial buffer response in the liver. Med Eng Phys 2013;35:1053-8. "
    "doi:10.1016/j.medengphy.2012.10.008",
    "[3] Yu HB, Bartlett A, Hunter P, Ho H. Hybrid 0D-1D blood flow "
    "simulation for virtual liver transplantation in paediatric "
    "recipients. Unpublished manuscript.",
    "[4] Ho H, Yu HB, Bartlett A. Computational simulations for the "
    "hepatic arterial buffer response after liver graft transplantation. "
    "Unpublished manuscript.",
    "[5] Chen X, Xiao H, Yang C, Chen J, Gao Y, Tang Y, Ji X. Doppler "
    "evaluation of hepatic hemodynamics after living donor liver "
    "transplantation in infants. Front Bioeng Biotechnol 2022;10:903385. "
    "doi:10.3389/fbioe.2022.903385",
    "[6] Kim WS, Cheon JE, Youn BJ, Yoo SY, Kim WY, Kim IO, Yeon KM, Seo "
    "JK, Park KW. Hepatic arterial diameter measured with US: adjunct "
    "for US diagnosis of biliary atresia. Radiology 2007;245(2):549-555. "
    "doi:10.1148/radiol.2452061093",
    "[7] Plevak DJ, Southorn PA, Narr BJ, Winter PB, Rettke SR. "
    "Hyperdynamic circulatory state after liver transplantation. "
    "Transplant Proc 1993;25(2):1837-8.",
    "[8] Dashti SH, Kasraianfard A, Ebrahimi A, Nassiri-Toosi M, Pakshir "
    "MS, Rahimi M, Jafarian A. Hemodynamic changes and early recovery of "
    "liver graft function after liver transplantation. Int J Organ "
    "Transplant Med 2020;11(1):1-7.",
    "[9] Byun SH, Yang HS, Kim JH. Liver graft hyperperfusion in the "
    "early postoperative period promotes hepatic regeneration 2 weeks "
    "after living donor liver transplantation. Medicine (Baltimore) "
    "2016;95(46):e5404. doi:10.1097/MD.0000000000005404",
    "[10] Marcos A, Fisher RA, Ham JM, Shiffman ML, Sanyal AJ, Luketic "
    "VA, Sterling RK, Fulcher AS, Posner MP. Liver regeneration and "
    "function in donor and recipient after right lobe adult to adult "
    "living donor liver transplantation. Transplantation "
    "2000;69(7):1375-1379.",
    "[11] Zhang Y, Li B, He Q, Chu Z, Ji Q. Comparison of liver "
    "regeneration between donors and recipients after adult right lobe "
    "living-donor liver transplantation. Quant Imaging Med Surg "
    "2022;12(6):3184-3192. doi:10.21037/qims-21-1077",
    "[12] Vargas PA, Goldaracena N. Alternatives to left lateral segment "
    "for pediatric liver transplantation, or required surgeon toolkit? "
    "Hepatobiliary Surg Nutr 2024;13(2):376-378. doi:10.21037/hbsn-23-671",
]
for r in refs:
    d.add_paragraph(r)

out_path = "A Sensitivity and Identifiability Framework for Testing the Hepatic Arterial Buffer Response (Med Eng Phys submission).docx"
d.save(out_path)
print("Saved:", out_path)
