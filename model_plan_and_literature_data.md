# Post-LDLT graft hemodynamics model: scoping document

## 1. What this project is

Companion computational model to a real, already-drafted clinical manuscript
in the parent folder (`../Graft hemodynamices.docx`, Chongqing Children's
Hospital / Chongqing General Hospital group -- Ji, Tang, and colleagues,
same broader collaborator network as this session's other Chongqing
projects). That manuscript is a pure clinical/statistical study (Doppler
ultrasound + paired t-test/ANOVA) reporting hepatic artery and portal vein
hemodynamic time-courses in 41 pediatric patients after living-donor
left-lateral-segment liver transplantation (LDLT) for biliary atresia (BA).
No computational model is built in it. This project aims to build one,
mirroring the pattern established for the CoA and fetal-DA projects this
session: a lumped-parameter (0D) hemodynamic model, calibrated against real
published group-level data, built from independently-sourced physiological
parameters where possible rather than fit wholesale to the target data.

**PII note**: this parent folder also contains a single-patient case-report
document (in Chinese) with a real patient name. That name has not been, and
will not be, reproduced anywhere in this project's outputs -- only the
anonymized clinical course (portal vein thrombosis -> recurrent anastomotic
stenosis -> balloon angioplasty -> later biliary-enteric anastomotic
stenosis -> resolution) is referenced, as a motivating example for a
possible stenosis sub-model (Section 5).

## 2. Real data available (the model's validation target)

From `../Graft hemodynamices.docx` Tables 1-2 (group-level, n=41, mean+-SD;
no per-patient data, nothing further to anonymize):

| Time | PSV, hepatic artery (cm/s) | RI, hepatic artery | Portal vein velocity (cm/s) |
|---|---|---|---|
| Pre-op | 73.32 +- 22.31 | 0.77 +- 0.09 | 16.88 +- 5.69 |
| POD1 | 53.10 +- 16.02 | 0.61 +- 0.05 | 30.80 +- 8.67 |
| POD7 | 47.02 +- 10.05 | 0.59 +- 0.03 | 30.05 +- 8.80 |
| POD14 | 42.29 +- 10.38 | 0.59 +- 0.05 | 28.39 +- 6.47 |
| POD30 | 38.51 +- 7.63 | 0.59 +- 0.01 | 26.71 +- 7.93 |

Cohort: 41 patients (22M/19F), age 4-18 months at transplant (median 5
months), all biliary atresia, all left-lateral-segment living-donor grafts,
all with UNCOMPLICATED postoperative recovery (vascular complications were
an explicit exclusion criterion in the source study) -- i.e. this is a
"normal recovery" reference dataset, not a mixed complicated/uncomplicated
cohort.

RI_HA is defined in the source paper as (PSV-EDV)/PSV, the standard
resistive index formula (same structure as PI's numerator, different
denominator -- see this session's fetal-DA project for the general
Doppler-index-definition verification precedent).

## 3. Physiological narrative to be captured by the model

1. **Pre-transplant**: biliary atresia -> progressive cirrhosis -> high
   intrahepatic vascular resistance -> portal hypertension. Despite elevated
   portal PRESSURE, portal vein VELOCITY is measured as LOW (16.9 cm/s) --
   consistent with high downstream resistance and/or collateral
   (portosystemic shunt) diversion of flow away from the intrahepatic portal
   path. Hepatic artery flow/resistance (PSV=73.3, RI=0.77) are both
   elevated -- the source paper attributes this to the diseased native
   liver's high vascular resistance being transmitted back to the arterial
   inflow (a cirrhosis-related arterial finding, not primarily an HABR
   response at this stage).
2. **Immediately post-transplant (POD1)**: the diseased native liver is
   replaced by a healthy, low-resistance graft segment. Portal vein
   resistance drops sharply -> PVV nearly doubles (16.9 -> 30.8). Hepatic
   artery PSV and RI both drop substantially (73.3->53.1, 0.77->0.61) --
   this is presented in the source paper as the combined effect of (a) the
   healthy graft's intrinsically lower vascular resistance, and (b) HABR
   -- the arterial bed constricting in response to the portal flow surge
   (though note: HABR classically predicts arterial CONSTRICTION, i.e.
   reduced flow, in response to a portal flow INCREASE -- consistent with
   PSV dropping, but the simultaneous RI drop is more directly explained by
   reduced downstream resistance from the healthy graft than by HABR
   per se; the model should be able to distinguish/attribute these two
   contributions, which the clinical paper does not formally separate).
3. **POD1 -> POD30, gradual adaptation**: PSV_HA keeps declining
   (53.1->47.0->42.3->38.5, statistically significant drop specifically
   between POD7 and POD14); RI_HA stabilizes quickly (0.61->0.59, flat
   after POD7); PVV gradually declines (30.8->30.1->28.4->26.7, no
   statistically significant pairwise differences in the source paper, but
   a visible downward trend) -- the source paper cites separate literature
   suggesting FULL portal-vein-velocity normalization takes 1-4 years,
   i.e. the 30-day window captures only the early, fast part of a much
   longer adaptation process.

## 4. Proposed model architecture (0D lumped-parameter, first draft)

Mirrors the two-compartment coupling pattern already built for the
fetal-DA project this session, but with the compartments representing the
PORTAL and HEPATIC ARTERIAL inflows to a single shared hepatic/graft
"downstream" compartment (rather than two separate downstream beds as in
the DA project) -- reflecting that both the hepatic artery and portal vein
drain into the SAME liver sinusoidal bed, a fundamentally different
topology from the DA project's two-separate-circulation structure.

Candidate state variables: hepatic arterial flow Q_HA(t), portal venous
flow Q_PV(t), sinusoidal/graft downstream pressure P_sinus(t) (or resistance
R_sinus(t) as an explicitly time-varying, not state, parameter -- see
below).

Candidate governing relationships:
- Portal inflow driven by a splanchnic driving pressure P_portal(t) (high,
  reflecting portal hypertension, pre-op; normalizing over weeks-months
  post-op) against a sinusoidal/graft resistance R_sinus(t) (high pre-op,
  reflecting cirrhosis; low immediately post-op, reflecting the healthy
  graft; the POD1-POD30 PVV decline suggests R_sinus or P_portal continues
  to evolve slightly even within this window, not an instantaneous step).
- Hepatic arterial flow governed by a systemic arterial driving
  pressure/resistance PLUS an HABR feedback term that adjusts arterial
  resistance as a function of (recent) portal flow -- the specific
  quantitative form of this feedback is the single most important
  literature question for this model (see the parallel literature-review
  fork's findings, Section 4.1 below once returned).
- A time-varying (not necessarily state-evolved via its own ODE, could be
  a prescribed function of time since transplant) representation of
  graft/portal-hypertension "recovery," since the data shows continued
  drift over 30 days that a purely instantaneous-adaptation model
  (constant post-transplant parameters) would not reproduce.

### 4.1 Literature findings (HABR quantitative form, prior LDLT models, pediatric parameters)

**This changes the shape of the project.** Harvey's own group has already built
a 0D-1D pediatric LDLT hemodynamic model directly on point: an unpublished
draft manuscript, Yu HB, Bartlett A, Hunter P, Ho H, "Hybrid 0D-1D blood flow
simulation for virtual liver transplantation in paediatric recipients"
(`E:\Google Drive\Harvey Ho Paper\2018\liver_paediatric\Blood flow simulation
for paediatric reciepient after liver transplantation_v2.pdf` -- no journal/DOI
found anywhere in the text, so this appears to be an unpublished/unfinished
draft, not a published paper). It models exactly this scenario: a donor
left-lateral-segment graft (LPV flow 193.8 mL/min at 10 mmHg) transplanted into
a pediatric recipient (recipient arterial pressure range 42.4-72.6 mmHg),
reporting HA flow falling 59.22+-11.6 -> 31.93+-7.7 mL/min post-transplant and
a post-reperfusion portal pressure gradient (HPVG) of ~10.6+-4.5 mmHg. A
companion 2018 draft, `0d-1d habr_v1.docx` (Section 3 above), covers the same
electrical-analog HABR approach for adult hepatectomy rather than pediatric
LDLT, and is itself unfinished (literal "Tba"/TODO placeholders).

**The HABR quantitative form is now settled, not an open literature
question.** Both documents cite and reuse the same empirical relationship,
originally from Ho, Sorrell, Bartlett, Hunter, "Modeling the hepatic arterial
buffer response in the liver," Med Eng Phys 2013;35:1053-8 (a real, published
paper; its PDF itself was not located in the Drive, only citing documents that
quote its result) -- found in exact numerical form in
`2021/rat liver/HABR Keagan/rundefinedmodel.m`, a MATLAB driver script for the
Simulink model:

    changeIha = 0.0007102*(changeIpv)^2 + 0.5492*changeIpv

where changeIpv/changeIha are PERCENT changes in portal-venous / hepatic-
arterial flow relative to a baseline run (e.g. changeIpv =
(oldIpv-newIpv)/oldIpv*100). Critically, this is applied as a **discrete,
between-run resistance-update rule**, not a continuous-time feedback ODE: the
Simulink model is run to steady state, the flow change is measured, the new HA
resistance is computed from the quadratic and written back into the model,
and the model is re-run -- an iterative quasi-steady scheme, not an
adenosine-washout-style first-order kinetic model. This resolves the first
open question in Section 6 below (flow-flow, not resistance-flow, and
discrete/quasi-steady, not continuously state-evolved) directly from Harvey's
own prior validated work, rather than requiring a new literature choice.

**Circuit topology** (from `HABR.mdl.autosave` / `HABRresistorsdebbaut.mdl.autosave`,
Simulink block diagrams): separate left/right-lobe subsystems, each with its
own multi-generation resistor tree for HA, PV, and HV (first-generation
resistors Rha/Rpv/Rhv plus lumped Rhatotal/Rpvtotal/Rhvtotal for later
generations), independent left/right HABR application, and three hepatic vein
outlets (left/middle/right) converging on a shared IVC resistance -- notably
MORE anatomically granular (multi-generation, left/right split) than this
project's originally-sketched single-shared-downstream-compartment design
(Section 4 above).

**Pediatric-specific parameters exist already**, from the Yu et al. draft, and
supersede the "would likely need to flag an age/species extrapolation caveat"
concern in Section 6 below -- there is real pediatric LDLT-specific
donor/recipient pressure and flow data already validated in a directly
analogous (adult-donor-segment-to-child) transplant scenario, just not
published, and not yet fit against serial post-operative Doppler indices
(PSV/RI/PVV) the way this project's real dataset (Section 2) would allow.

**Correction to an earlier claim in this session**: a prior literature-review
fork reported "Ho 2019 models this exact adult-to-child LLS-LDLT HABR
scenario" -- this is **not correct**. The only 2019 Ho paper actually found
(Ho H, Qiu C, "Hemodynamic aspects of the Budd-Chiari syndrome of the liver,"
Med Eng Phys 2019) models Budd-Chiari syndrome (hepatic venous outflow
obstruction), an unrelated condition, not LDLT. The real prior LDLT-specific
work is the unpublished/undated Yu et al. draft above; this should be treated
as internal, unpublished prior work (cite as personal communication / draft,
not as a citable published reference) unless Harvey indicates otherwise.

**Implication for this project's framing**: rather than building a new HABR
model from a blank slate, the natural framing is to **reuse and validate the
existing Yu/Bartlett/Hunter/Ho pediatric-LDLT 0D-1D model structure and its
already-fitted HABR quadratic against this project's new, real, serial
post-operative Doppler dataset** (Section 2) -- turning an unpublished
single-case-style draft into a dataset-validated model with a genuine n=41
cohort and a 30-day time-course, which the original draft did not have. This
also directly motivates finishing/publishing work that already exists in
draft form, consistent with how this session's other two projects (fetal DA,
umbilical artery) each closed out a stalled prior draft rather than starting
fresh.

## 4.2 Architecture decision (confirmed with Harvey, 2026-08-31)

- **Relationship to the Yu/Bartlett/Hunter/Ho unpublished draft**: build on it
  directly. This project is framed as finishing/extending that stalled draft
  -- reusing its HABR quadratic and general modeling approach, and validating
  against this project's new n=41 serial-Doppler dataset (the draft itself had
  no serial time-course, only a single pre/post snapshot). Likely
  co-authorship with Yu/Bartlett/Hunter follows from reusing their unpublished
  work; flag this for Harvey to confirm explicitly when the paper is drafted,
  but proceed with the model now.
- **Topology granularity**: simplified single-compartment, not the prior
  draft's full multi-generation/left-right-split network. Two inflow branches
  (Q_HA, Q_PV) draining into one shared downstream sinusoidal/graft
  compartment, matching what the aggregate PSV/RI/PVV validation target can
  actually constrain. The prior draft's fuller topology is noted as available
  if a future per-lobe or per-generation extension is ever motivated by
  richer data, but is out of scope now.

## 5. Possible pathology extension: portal vein anastomotic stenosis

A real, anonymized complicated case in this same project folder shows
early portal vein thrombosis (POD2) followed by recurrent portal vein
ANASTOMOTIC STENOSIS (first suspected on POD1 ultrasound, confirmed by
CT/CTA over the following months, eventually treated by balloon
angioplasty ~11 months post-transplant), and much later a separate
biliary-enteric anastomotic stenosis (unrelated vascular structure, treated
by percutaneous balloon dilation). This motivates a natural extension,
mirroring the CoA project's structure (normal-aorta base model + a
coarctation/stenosis pathology layered on top): use the SAME base
portal/hepatic-arterial model, with a discrete stenosis (orifice-type
resistance increase, analogous to the CoA project's Bernoulli/orifice
narrowing) inserted at the portal anastomosis, and check whether the
model reproduces a qualitatively-recognizable Doppler signature (e.g.
markedly reduced/turbulent post-stenotic portal velocity, compensatory
HABR-mediated arterial changes) consistent with the real complicated
case's own reported ultrasound findings ("portal vein anastomosis poorly
visualized," "anastomotic lumen narrowing"). This would NOT be a
patient-specific fit (only one anonymized case, no detailed serial
Doppler numbers were extracted from it beyond qualitative
imaging-report text) -- it would be a qualitative/plausibility check, not
a quantitative validation, and should be scoped and framed as such if
pursued.

## 6. Open questions before committing to a specific model form

- ~~Is the HABR feedback better modeled as a flow-flow relationship... or a
  resistance-flow relationship...~~ **RESOLVED by Section 4.1**: Harvey's own
  prior work uses a flow-flow quadratic (changeIha vs. changeIpv, both percent
  change), applied as a discrete quasi-steady update rather than a continuous
  kinetic ODE. Adopting this directly (rather than re-deriving from Lautt) is
  both more defensible (it is literally this same clinical scenario's prior
  model) and less work.
- Should R_sinus(t)/P_portal(t)'s post-transplant time-evolution be
  represented as an explicit prescribed function of time (e.g. an
  exponential approach to a new steady state, with a time constant fit to
  the POD1-POD30 trend) or should it emerge from a slower second-order
  physiological process (e.g. splanchnic vascular remodeling, spleen size
  normalization) with its own literature-sourced time constant? **Still
  open** -- the Yu et al. draft is a single pre/post-transplant snapshot
  comparison, not a serial time-course, so it doesn't resolve this; this
  project's own 5-point (pre-op/POD1/7/14/30) dataset is actually the richer
  time-course data source here, which argues for fitting an explicit
  prescribed-function time constant directly to it rather than searching
  further literature.
- ~~Whether pediatric-specific (rather than adult) HABR quantification exists
  at all...~~ **RESOLVED by Section 4.1**: yes, via the unpublished Yu et al.
  draft's real pediatric donor/recipient pressure-flow data in this exact
  transplant scenario -- no adult/animal extrapolation caveat needed for the
  base HABR relationship itself, though the quadratic's original derivation
  (2013 paper) may still trace back to adult data; worth flagging that
  provenance but not blocking on it given it's already Harvey's own validated
  prior choice for this precise clinical situation.
- **New open question surfaced by Section 4.1**: the Yu et al. model's
  circuit is multi-generation and left/right-lobe-split, materially more
  granular than this project's originally-sketched single-shared-compartment
  design (Section 4). Decide whether to (a) adopt that fuller topology
  wholesale, (b) simplify it to a single-compartment-per-inflow lumped model
  (faster to build and fit, closer to this project's original sketch, and
  arguably appropriately-scaled given the target data is only aggregate
  PSV/RI/PVV, not per-lobe), or (c) something in between. Leaning toward (b)
  for a first pass, matching the level of anatomical detail actually
  supported by the group-level Doppler validation target, but this is a
  judgment call worth checking with Harvey before implementation.

## 7. First-pass model results (2026-08-31)

Implemented per Section 4.2: `ldlt_habr_model.py` (pulsatile HA branch --
inertance + resistance -- draining into a shared sinusoidal compartment with
compliance + outflow resistance; portal inflow is a prescribed/measured
input, not independently simulated, since the portal trajectory itself is
data, not the thing being tested) and `calibrate_and_test.py` (the
calibration + hypothesis test described below). Fixed/representative
parameters (heart rate, inertance, compliance, outflow resistance, venous
reference pressure, portal-coupling gain, mean driving pressure) are
assumed/reasonable values, not independently sourced -- flagged here as a
first-pass limitation, same caveat this session gave the fetal-DA and
umbilical-artery projects' non-fitted constants.

**Method**: the HA branch's two truly free parameters (R_HA, systemic pulse
amplitude) are calibrated ONCE, at POD1, to exactly match the measured
PSV_HA (53.10 cm/s) and RI_HA (0.61) at that time point -- POD1 is used as
the anchor, not pre-op, because the pre-op -> POD1 transition is a discrete
graft-replacement event (diseased native liver swapped for a healthy graft),
not a same-organ flow perturbation, so applying a flow-flow HABR relationship
across it isn't mechanistically appropriate (Section 4.1). For POD7/14/30,
R_HA is NOT fit to the HA data -- it is set so the model's mean HA flow
matches exactly what the parameter-free Yu/Bartlett/Hunter/Ho HABR quadratic
predicts, given only the MEASURED portal-vein-velocity change from POD1 at
that time point. The resulting PSV_HA and RI_HA are therefore genuine
out-of-sample model predictions, tested against the real measured values.

**Result: the literature HABR relationship reproduces the correct direction
of the continued HA decline, but only a modest fraction of its magnitude.**
A null-model comparison (R_HA frozen at its POD1-fitted value; only the
sinusoid's portal-velocity input changes) predicts HA flow would actually
drift slightly UPWARD as portal velocity falls (less downstream loading) --
the opposite of what's observed. Adding the HABR feedback correctly flips
this to the observed downward direction, but accounts for only a modest
share of the measured PSV_HA drop: 8.0% at POD7, 14.6% at POD14, 18.4% at
POD30 (measured drops of 6.08/10.81/14.59 cm/s vs. HABR-predicted drops of
0.49/1.57/2.69 cm/s). RI_HA fares worse: the model predicts RI rising
slightly (0.610 -> 0.644) over this window, while the real cohort shows RI
essentially flat-to-slightly-falling (0.61 -> 0.59).

**Honest interpretation**: a parameter-free, literature-anchored HABR
relationship, driven only by the measured portal-flow trend, is NOT
sufficient to explain the continued hepatic-arterial waveform normalization
seen over the first post-transplant month in this cohort -- most of that
effect (roughly 80%+ of the PSV_HA decline, and all of the RI_HA direction)
must come from some other mechanism this first-pass model doesn't include:
candidates include continued systemic/pulse-pressure normalization as the
child recovers postoperatively, graft vascular remodeling/adaptation beyond
the portal-flow-triggered HABR response, or declining venous
congestion/edema in the graft parenchyma. This is analogous in spirit to the
umbilical-artery project's identifiability finding: a real, falsifiable,
somewhat negative result, not a curve-fit success, and should be reported as
such rather than reframed to look like a validation.

Outputs: `ldlt_habr_prediction_results.csv` (measured vs. simulated PSV_HA/
RI_HA), `ldlt_habr_null_model_results.csv` (the no-HABR comparison).

## 8. Correction (2026-08-31): rebuilt on the actual pi-filter, not an ad hoc branch

Harvey pointed out the Section 7 model above did NOT use the documented
"pi-filter" lumped element, and asked for the right pathway first: a generic
healthy-infant liver circulation model that gets portal flow, HA flow, and
hepatic-venous (CV) flow right, before returning to transplant/HABR specifics.

**The pi-filter, confirmed from the actual source diagram**
(`2018/liver segments/0d-1d habr_v1.docx`, Fig. 4 inset, labeled "pi-filter"
in the image itself): a two-port network -- series L (inductor) + Rs
(resistor) between the ports, and an IDENTICAL shunt branch (C in series
with Rp, to a common ground/reference) at each port. Four distinct parameter
values (L, Rs, C, Rp) per segment, matching the text's "three resistors, two
capacitors and one inductor" (Rs + 2xRp = 3 resistors; C, C = 2 capacitors,
using the same value at each port) and "four parameters ... calculated from
the analytic data for liver erosion casts". Section 7's model used a plain
L+R branch into a single shared RC compartment -- structurally simpler and,
per Harvey's direction, not the right building block to reuse going forward.

**A previously-unexamined, more complete and directly relevant source was
found while re-checking this**: `2018/liver_paediatric/submission/numerical
methods for quantifying blood flow after PH_v4.docx` -- a submitted
manuscript (Ho, Yu, Bartlett, "Computational simulations for the hepatic
arterial buffer response after liver graft transplantation"; has a
`rebuttal.docx`/`rebuttal.pdf` in the same folder, so this went through peer
review; publication status not otherwise confirmed). This is the SAME
adult-to-child left-lateral-segment transplant scenario as this project,
modeled with exactly this pi-filter approach, single lobe (simpler than the
2018 draft's multi-generation, left/right-split version), and gives real,
usable target numbers directly from Results Section 3.1 -- reused here as
the generic healthy/paediatric baseline:

| Quantity | Value | Source |
|---|---|---|
| Portal driving pressure | 13 mmHg | post-transplant recipient |
| Mean arterial pressure | 57.5 mmHg (range 42.4-72.6) | post-transplant recipient |
| Sinusoidal pressure | 5.37 mmHg | post-transplant recipient |
| Hepatic venous pressure | 4.07 mmHg | post-transplant recipient |
| Portal vein flow | 300 mL/min | regression, 64 children 3mo-16y |
| Hepatic arterial flow | 31.93 +- 7.7 mL/min | post-transplant recipient |
| Hepatic venous flow | 322.5 mL/min | post-transplant recipient |

(Note: the source paper's own Q_PV+Q_HA=331.9 does not exactly equal its
own reported Q_HV=322.5 -- a ~3% mass-balance discrepancy already present in
their reported numbers, not introduced by this project.) The paper also
confirms the driving scheme: "an alternating and a direct power source"
for HA (i.e. a plain sinusoid, P_HA(t) = mean +- amplitude*sin(...), simpler
than the cardiac-shaped pulse used in this session's fetal-DA/umbilical-
artery projects) and a DC (near-constant) source for PV -- matching Fig. 2's
plotted traces (visibly pulsatile HA pressure/flow; nearly flat PV and HV).

**Implementation**: `pi_filter_healthy_infant_model.py`. Topology: HA
pi-filter and PV pi-filter both feed a shared sinusoidal node; an HV
pi-filter drains that node to a reference IVC pressure (assumed 2 mmHg,
not given in the source). Only output-side shunts matter dynamically (an
ideal voltage source absorbs its own input-side shunt's current, so it drops
out of the dynamics) -- 5 states: Q_HA, Q_PV, P_sinus, Q_HV, P_hv.

Because this baseline model is LINEAR (no HABR nonlinear resistor yet), the
three Rs values were solved EXACTLY via Ohm's law on the time-averaged (DC)
circuit from the real target pressures/flows above -- a linear system's time
-average response to a periodic input equals its DC solution regardless of
the inertance/compliance ("shape") parameters, so this reproduces the real
target MEAN flows by construction, independent of how pulsatility is tuned.
The inertance/compliance values themselves (L_HA=2.0, L_PV=0.01, L_HV=0.02,
C_sinus=C_hv=2.0, Rp_sinus=500) are chosen, not derived -- flagged as
assumed/representative, same caveat given to every other non-fitted constant
in this session's other two projects.

**Verification**: simulated mean flows match the real targets to ~1-2%
(Q_PV 297.5 vs. 300, Q_HA 31.89 vs. 31.93, Q_HV 328.6 vs. 322.5; P_sinus 5.43
vs. 5.37, P_hv 4.11 vs. 4.07 mmHg -- residual gap is Euler-integration
truncation error plus the sinusoidal-node leak resistor, not a calibration
failure). Waveform shapes match the source paper's Fig. 2 qualitatively: HA
flow visibly pulsatile (22.96-40.82 mL/min around the 31.9 mean), PV and HV
both nearly flat (297.3-297.7 and 327.6-329.7 mL/min respectively).

**Status**: this generic healthy/paediatric baseline circulation model is
now validated and is the correct foundation to build the transplant/HABR-
specific work (Section 7) back on top of, rather than the earlier ad hoc
branch model -- not yet done as of this writing.

## 9. HABR test folded back onto the pi-filter base model (2026-08-31)

Implemented `ldlt_habr_on_pi_filter.py`, replacing Section 7's ad hoc-branch
version with the same falsifiable-prediction test run on top of the
validated Section 8 circuit. Rs_PV, Rs_HV, Rp_hv_out and the shape
parameters (L_HV, C_sinus, C_hv, Rp_sinus) are reused verbatim from the
generic model, not re-fit. Two adaptations, both explicitly justified rather
than ad hoc:

- **Portal branch simplified to a prescribed input** Q_PV(t), dropping its
  own L-Rs state: justified directly by the generic model's own result
  (Section 8) that Q_PV varies by under 0.2% across a cycle, i.e. it is
  already indistinguishable from quasi-static in its own validated form.
  Q_PV(t) = 300 mL/min (the generic target) scaled by this cohort's real
  measured PVV percent-change from POD1.
- **Rs_HA and L_HA calibrated together at POD1**, HA pulse amplitude held
  fixed at the real literature value (15.1 mmHg). A first attempt reused
  the generic model's L_HA verbatim and only fit Rs_HA + pulse amplitude --
  this produced a dimensionally-inconsistent fit (pulse amplitude blew up to
  440 mmHg, non-physiological) because the generic model's L_HA was tuned
  for its own Rs_HA scale (~98), nearly 100x this cohort's fitted Rs_HA
  (~0.79) -- exposing that L_HA, like the other "shape" parameters, was
  never independently validated and should be re-fit alongside Rs_HA rather
  than held fixed across very different Rs_HA scales.

**Result, corrected and slightly improved versus Section 7**: with L_HA
properly re-fit, RI_HA now moves in the CORRECT direction under HABR alone
(0.610 -> 0.596, vs. measured 0.61 -> 0.59) -- Section 7's ad hoc model had
this backwards (predicted RI rising). The fraction of the measured PSV_HA
decline reproduced by parameter-free HABR alone is also somewhat larger on
this corrected circuit: 13.2% (POD7), 24.1% (POD14), 30.4% (POD30) of the
measured drop (vs. 8.0/14.6/18.4% in Section 7). The qualitative conclusion
is unchanged and still the headline, honest finding: literature HABR,
driven only by the measured portal-flow trend, reproduces the right
direction for both PSV_HA and RI_HA but accounts for less than a third of
the observed magnitude even at POD30 -- most of the continued post-
transplant hepatic-arterial normalization is not explained by portal-flow-
driven HABR alone. Outputs: `ldlt_habr_pi_filter_prediction_results.csv`,
`ldlt_habr_pi_filter_null_model_results.csv`.

## 10. Candidate mechanisms for the residual decline (2026-08-31, literature check)

Quantitative diagnostic: holding HABR-derived Rs_HA(t) fixed, a uniform
scale factor on arterial driving pressure (mean+amplitude together)
declining ~9%/15%/20% by POD7/14/30 closes the gap to real PSV_HA exactly,
and also improves the RI_HA match -- but since RI is scale-invariant, this
only shows the missing effect behaves like a pure AMPLITUDE scaling, not
that pressure decline specifically is the cause.

Literature check (fork) found two real candidates, both consistent with a
pure-scaling effect, not distinguishable from each other with this
project's group-level PSV/RI/PVV data alone:
- **Postoperative hyperdynamic-circulation normalization**: Plevak et al.,
  *Transplant Proc* 1993 (PMID 8470191) -- pre-transplant hyperdynamic state
  (69% of patients) trends toward normalization post-transplant; qualitative
  direction support only, no quantified %/week rate found.
- **Graft regeneration diluting velocity at a fixed measurement point**
  (mechanistically DISTINCT from pressure change): Byun, Yang, Kim,
  *Medicine (Baltimore)* 2016;95(46):e5404, DOI 10.1097/MD.0000000000005404
  (verified) -- graft mass reaches ~1.7x its initial size by ~2 weeks
  post-LDLT. If arterial caliber at the Doppler sampling point grows with
  graft mass (isometric assumption: area ~ mass^(2/3)), velocity would fall
  even at constant flow -- a fitted saturating-growth curve matched to this
  one data point predicts a PURE-DILUTION PSV_HA of 39.9/36.8/35.4 cm/s at
  POD7/14/30 (vs. real 47.0/42.3/38.5) -- i.e. comparable to or larger than
  the entire real decline, depending on the (unverified) area-scaling
  exponent. Like pressure decline, area dilution exactly preserves RI (both
  are pure velocity-scale effects), so RI matching does not distinguish them.

**Honest conclusion**: at least two real, literature-grounded mechanisms
(systemic pressure normalization; graft-growth-driven caliber dilution) are
each independently large enough to plausibly account for most of the
residual decline HABR doesn't explain, and this project's data (no serial
vessel-diameter measurements in this cohort, unlike the fetal-DA/umbilical-
artery projects) cannot distinguish between them, or a blend of both, or
some share going to a mechanism not yet identified. This is reported as a
genuine, unresolved identifiability question, not resolved further as of
this writing (paused here per Harvey's direction to first write up the
generic healthy-infant circulation model, Section 8).

## 11. The clinical dataset is now identified as a real, published, DOI-verified paper

`../Graft hemodynamices.docx` (this project's real clinical dataset,
Sections 1-2 above) is a draft of a now-PUBLISHED paper: Chen X, Xiao H,
Yang C, Chen J, Gao Y, Tang Y, Ji X, "Doppler evaluation of hepatic
hemodynamics after living donor liver transplantation in infants," Frontiers
in Bioengineering and Biotechnology 2022, doi:10.3389/fbioe.2022.903385
(same author group; confirmed by identical PSV_HA/RI_HA/PVV values at every
time point). This should be cited as this published DOI going forward, not
treated as an unpublished internal draft.

**Two new real data points this reveals, not previously available**: portal
vein diameter, pre-transplant 0.44+-0.09 cm and POD1 0.46+-0.09 cm (a modest,
non-significant +4.5% increase), and their portal flow formula:
PVF = pi*r^2*0.57*PVV*60, giving PVF in mL/min/100g (r=D/2 cm, PVV cm/s;
the 0.57 factor converts peak/PSV-type velocity to an effective mean
cross-sectional velocity for flow calculation). Reported PVF: pre-transplant
83.87+-42.81, POD1 165.99+-68.15 mL/min/100g -- reproduced by the formula
(87.8 and 175.1 using the reported mean D and mean PVV separately, close to
the reported per-patient-averaged values, as expected).

**This validates a simplifying assumption made in Section 9's HABR test**:
that project treated Q_PV(t) as scaling directly with measured PVV
(constant vessel area assumed, since no diameter data existed for
POD7/14/30). Checking this against the REAL diameter data available for the
pre-op -> POD1 transition: area (~r^2) increased only 9.3% while velocity
increased 82.5%, combining to a 99.4% flow increase -- matching the reported
flow increase (97.9%) almost exactly, and confirming velocity change, not
area change, dominates the flow change over this transition. No diameter
data exists for POD7/14/30, so the same assumption cannot be directly
checked over that (smaller-magnitude) window, but this is a meaningful,
cohort-specific piece of supporting evidence for a simplification that was
previously just assumed.

**Order-of-magnitude cross-check against the generic pi-filter baseline
model's target (Section 8)**: that model's PV flow target (300 mL/min) came
from a DIFFERENT source (Ho/Yu/Bartlett's regression-based pediatric
estimate), for an adult-donor left-lateral-segment graft reported (in the
2018 draft) as 288.5 mL in volume. Converting that to a mass (288.5 mL x 1.06
g/mL assumed liver density = 305.8 g) and normalizing the generic model's 300
mL/min target the same way gives ~98.1 mL/min/100g -- compared to this
cohort's own real POD1 value of 165.99 mL/min/100g, about 1.7x higher. This
is the right order of magnitude (same decade, not orders apart) but not a
tight match -- expected, since it compares two different cohorts/grafts via
an assumed liver density and an assumed correspondence between the 2018
draft's specific donor case and this project's own 41-patient cohort. Should
not be over-interpreted as a precise validation, only as a sanity check that
the generic model's absolute flow scale is physiologically reasonable.

## 12. Real portal-diameter anchor folded into ldlt_habr_on_pi_filter.py (2026-08-31)

`Q_PV(t)` in the HABR test now uses Chen et al. 2022's own formula
(PVF = pi*r^2*0.57*PVV*60, mL/min/100g) with their real POD1 diameter
(0.46 cm, held fixed for POD7/14/30 since no later diameter data exists,
per the check in Section 11), replacing the earlier version's borrowed
300 mL/min scale from the Ho/Yu/Bartlett paper's different cohort. Result:
Q_PV(POD1) = 175.06 mL/min/100g (their own reported value: 165.99 --
matches within the same small discrepancy noted in Section 11, from using
mean D and mean PVV separately rather than per-patient). The refit anchor
(Rs_HA=0.8284, L_HA=0.0344) and downstream HABR-predicted trajectory are
essentially unchanged in substance (HABR still explains 13.4/24.3/30.6% of
the measured PSV_HA decline at POD7/14/30, vs. 13.2/24.1/30.4% before) --
the correction makes the model properly grounded in this cohort's own real
data rather than materially changing the conclusion.

## 13. Correction: HABR is acute, not continuously re-applied (2026-08-31, Harvey)

Harvey's physiological correction: HABR is an acute (adenosine-washout,
minutes-to-hours) mechanism. By POD30 it should have long ceased actively
adjusting, and hepatic circulation should already be stable. Sections 9 and
12's model instead re-applied the HABR quadratic at every time point
relative to POD1, implicitly treating it as continuously active for the
whole month -- not appropriate for an acute mechanism.

**The real data directly supports the correction**: RI_HA is already flat
(0.59, 0.59, 0.59) from POD7 through POD30, while PSV_HA keeps declining.
Since RI is the ratio most sensitive to a resistance change, its flatness
after POD7 means whatever resistance adjustment HABR was going to make had
already happened by POD7. The old model's simulated RI kept drifting
(0.610->0.607->0.601->0.595) instead of plateauing -- itself evidence the
old model was over-crediting HABR for a chronic, resistance-flat decline.

**Corrected model** (`ldlt_habr_acute_then_frozen.py`): the HABR quadratic
is applied ONCE, across POD1->POD7 (the one window with both a real portal-
flow change and a real RI change -- the legitimate acute-response window).
Rs_HA is then FROZEN at its POD7-consistent value for POD14/POD30; Q_PV(t)
still updates to each time point's real measured value, so the circuit's
own passive coupling through the shared sinusoidal node is still active --
isolating "HABR already finished, only passive downstream coupling
remains" from "HABR still actively adjusting."

**Result**: under this corrected framing, HABR explains 13.4% of the POD7
decline (unchanged, since POD7 is still HABR's legitimate window), but only
6.9% and 4.7% of the (larger) POD14 and POD30 declines respectively --
i.e. essentially none of the decline BEYOND POD7 is attributable to HABR;
that remainder (93-95% of the additional POD7->POD30 decline) is 100%
non-HABR in this framing, not partially HABR-credited as before. The
corrected model's simulated RI now also plateaus after POD7 (0.607 -> 0.607
-> 0.606), qualitatively matching the real RI's flat shape far better than
the old continuously-reapplied model did, even though the absolute level
still differs (~0.607 vs. real 0.59).

**Sharpened conclusion**: this makes the case for a non-HABR, non-resistance
(pure amplitude/scale) mechanism -- graft-growth-driven velocity dilution
or systemic pressure/hemodynamic normalization (Section 10) -- even
stronger and more precisely scoped than before: it must now account for
essentially the ENTIRE POD7->POD30 decline (8.51 of the cohort's 14.59 cm/s
total POD1->POD30 drop), not just a residual "missing" fraction after
crediting HABR throughout. Figure: `HABR_Figure_3_acute_correction.png`.

## 14. Attempted disambiguation of the two residual mechanisms (2026-08-31)

Following Section 13's correction (HABR's legitimate window is POD1-7
only), the two literature-grounded candidates from Section 10 --
postoperative systemic-pressure/hyperdynamic-circulation normalization, and
graft-regeneration-driven caliber dilution -- must now explain almost the
entire POD7->POD30 decline (8.51 of 14.59 cm/s total), not just a residual
slice. Further literature search finds a real, if partial, disambiguator:
**timing**.

**Systemic-pressure/hyperdynamic-circulation normalization resolves too
fast to be the POD7-30 driver.** Further search beyond Section 10's finding
(Plevak et al. 1993, qualitative "trend toward normalization") gives an
actual timescale: cirrhosis-related hyperdynamic circulation (elevated
cardiac output, reduced systemic vascular resistance) "reversed during the
3-5 postoperative days following liver transplantation," and acute
post-reperfusion vasoplegia/vasopressor dependence is likewise typically
weaned within the first ~24-72 hours in the pediatric liver transplant ICU
literature. Both point to substantial resolution well before POD7, not a
process that continues declining for another three weeks. This mechanism
remains a plausible contributor to the POD1-7 window specifically (where it
would overlap with HABR's own legitimate window, Section 13), but is poorly
timed to explain the sustained POD7->POD30 decline.

**Graft-regeneration/caliber-dilution is temporally consistent with the
sustained decline, but its magnitude for THIS population is genuinely
uncertain, not just unverified.** Regeneration is documented to continue
over weeks (matching the observed pattern), but the actual quantitative
shape is inconsistent across the literature found: one adult right-lobe MRI
volumetric study reports monotonic recipient-graft mass increase through
day 30 (87%/101%/119% at POD7/14/30 respectively) then a partial decline by
day 60; a second adult right-lobe study (n=62) reports the opposite
qualitative shape -- peak "liver regeneration ratio" at 2 weeks, declining
progressively through 6 months. Neither is pediatric, and neither is a
left-lateral-segment (LLS) graft specifically -- this project's actual
graft type. A further, previously unconsidered complication: pediatric LLS
grafts (an adult- or larger-donor segment placed in a small infant) are
frequently sized close to or above the "ideal" graft-to-recipient weight
ratio (GRWR) range (1-3%, safe range 0.8-4%, with graft REDUCTION techniques
specifically used above ~4% to avoid a large-for-size graft) -- unlike the
classically undersized grafts that motivate the compensatory-hypertrophy
paradigm in most regeneration literature. If this cohort's grafts were
adequately or generously sized rather than significantly undersized, the
expected magnitude of catch-up growth (and therefore of caliber dilution)
would be smaller than a naive application of Byun et al.'s single data
point implied. Graft weight/GRWR was not reported in Chen et al. 2022 and
was not otherwise located for this specific cohort.

**Working conclusion**: the timing argument favors graft-growth-driven
dilution, not systemic-pressure normalization, as the better-supported
candidate for the SUSTAINED POD7->POD30 decline specifically -- pressure
normalization is better timed to (partially) explain the POD1-7 window,
where it would sit alongside HABR rather than needing to explain anything
past POD7. A unified "graft caliber growth" mechanism is also more
parsimonious than invoking two separate, independent explanations for the
simultaneously-declining PVV and PSV_HA (one mechanism affecting both
vessels' calibers as the whole graft grows, rather than an arterial-specific
pressure explanation plus an unrelated portal-specific one). This is,
however, a partial disambiguation, not a resolved one: the magnitude of the
dilution effect for this specific pediatric LLS population remains
genuinely uncertain given inconsistent, non-pediatric, non-LLS-specific
adult regeneration literature and the large-for-size consideration above.
Fully resolving this would require either serial vessel-diameter or graft-
volume measurements in this cohort (not available) or a pediatric-LLS-
specific regeneration study (not located).

## 15. Manuscript draft, round 1 (2026-08-31)

Full manuscript drafted for reviewer round 1: `build_manuscript_round1.py`
-> "A Pi-Filter Model Test of the Hepatic Arterial Buffer Response After
Paediatric LDLT.docx". Synthesizes Sections 8-14: the validated generic
pi-filter baseline, the HABR test corrected for its acute time course
(Section 13), the real portal-diameter anchor (Section 12), and the
partial mechanism disambiguation (Section 14). All 10 references verified
via the EuropePMC metadata API (or direct primary-source extraction for
Chen et al. 2022 and the internal unpublished drafts) before use, not taken
from search-engine summaries alone. Verified via the Word-COM-to-PDF-to-
image render pipeline: renders cleanly across all 11 pages, all 6 figures
and 2 tables in place. Awaiting reviewer feedback.

## 16. Major revision, round 1 reviewer response (2026-08-31)

Reviewer gave a "major revision" verdict with 10 substantive points, all
addressed with real analysis, not just rewording -- two (points 1 and 8)
surfaced genuine problems:

- **Point 1 (most important)**: acute-then-frozen was wrongly framed as
  "corrected." HABR's fast kinetics are a continuously-coupled feedback
  (adenosine washout tracks whatever portal flow currently is), not a
  one-off event that "runs out" -- this does not justify freezing
  resistance after POD7 on physiological grounds alone. Rebuilt Results/
  Discussion to present three scenarios (continuous / acute-then-frozen /
  null) symmetrically, with acute-then-frozen explicitly labelled as
  motivated by (not proven by) the RI observation. Cites Eipel, Abshagen,
  Vollmar 2010 (World J Gastroenterol, doi:10.3748/wjg.v16.i48.6046) on
  HABR's continuous-coupling nature.
- **Point 8 (most consequential finding)**: swept assumed portal-diameter
  growth by POD30 (0-40%, `reviewer_round1_analyses.py`). At just 10%
  assumed growth, the headline "% of decline explained by HABR" result
  REVERSES SIGN (+31% -> -11%). This is now the central caveat of the
  whole quantitative analysis (new `HABR_Figure_7_diameter_sensitivity.png`),
  not a footnote: the reported percentages are conditional on an
  assumption (constant portal diameter after POD1) the data cannot verify
  and that is not even directionally safe.
- **Point 2**: Welch's t-test on published summary stats -- 95% CI on
  POD7-vs-POD30 RI difference is [-0.010, +0.010], cannot exclude a true
  change as large as the real POD1-to-POD7 change. "RI is flat" downgraded
  to "not detectably changing," explicitly not proof of anything.
- **Point 3**: added explicit governing ODEs, a statement that no HA
  cross-sectional area is used anywhere (Q_HA is a directly-calibrated
  Doppler-velocity proxy), and a full parameter table.
- **Points 4-5**: terminology fixed throughout -- "validated"->"calibrated",
  "parameter-free HABR"->"fixed-coefficient HABR relationship."
- **Point 6**: Monte Carlo (SEM-based) 95% intervals added alongside every
  point-estimate percentage; POD7's interval is [6%, 77%] -- much wider
  than the false-precision "13.4%" implied.
- **Point 7**: flagged explicitly that Chen et al.'s own PVF formula, as
  given, yields mL/min not mL/min/100g (no graft-mass term present) --
  inherited from the source paper, not resolved here; also flagged the
  deeper issue this points to: Q_HA (Doppler-calibrated) and Q_PV (this
  formula) are summed directly in the sinus-node balance with no verified
  common physical basis.
- **Point 9**: graft-growth dilution reframed from "favoured explanation"
  to "testable hypothesis" throughout.
- **Point 10**: expanded competing-mechanisms list (cardiac output/pressure
  amplitude, oedema, arterial spasm, anastomotic geometry, insonation
  angle/sampling location, sedation, heart rate) with explicit
  non-assessment disclosure.

Files: `build_manuscript_round2.py` (revised manuscript, overwrites the
round-1 docx), `Response_to_Reviewer_Round1.docx` (point-by-point account),
`reviewer_round1_analyses.py` (new statistical/sensitivity analyses),
`plot_diameter_sensitivity.py` (new Figure 7). Verified via the Word-COM-
to-PDF-to-image pipeline: all 15 pages, 7 figures, 3 tables render
correctly.

## 17. Major revision, round 2: fixed the dimensional inconsistency (2026-08-31)

Reviewer round 2 identified that Q_HA (calibrated directly to Doppler
velocity, cm/s) and Q_PV (computed in mL/min-scale units) were summed
directly in the sinus mass balance -- correctly identified as a genuine
dimensional inconsistency invalidating the model's physical interpretation,
not merely an uncertain weighting (round 1 had only disclosed this as a
caveat). Also caught a real statistical error (RI CI interpretation) and
several clarity gaps.

**The fix (not just disclosure)**: found a real, verified literature value
-- Kim et al. 2007 (Radiology, doi:10.1148/radiol.2452061093), healthy
non-jaundiced infant control group, right hepatic artery diameter
1.2+-0.2mm -- and used it to convert Q_HA into a genuine mL/min-consistent
volumetric flow (same basis as Q_PV), with Doppler velocity obtained only
at the final comparison step via this assumed area. This required
re-fitting the POD1 anchor: with P_HA_amp held at the literature 15.1mmHg
value, RI=0.61 was NOT achievable for any (Rs_HA, L_HA) combination tested
(RI capped near 0.48 across a wide grid) -- P_HA_amp had to be jointly
fit alongside Rs_HA/L_HA (3 unknowns/2 targets, necessarily non-unique,
now stated explicitly), landing at 27.43 mmHg. Full corrected pipeline:
`ldlt_habr_consistent_units.py`.

**Reassuring finding**: the diameter-sensitivity fragility (headline result
reverses sign at 10% assumed portal-diameter growth) PERSISTS after the
unit fix (25.3% at 0% growth -> -9.1% at 10% growth) -- confirming this is
a genuine property of the HABR relationship's response, not an artifact of
the previous bug.

**Statistical correction**: a 95% CI of [-0.010,+0.010] on the POD7-vs-POD30
RI difference EXCLUDES a true difference of 0.020 -- round 1 text
incorrectly said the opposite ("cannot exclude"). Corrected throughout
(`reviewer_round2_stats_fix.py`).

**Other fixes**: removed "equivalence test" language (ordinary unpaired
comparison, no TOST/margin); disambiguated cardiac-cycle time (tau) from
postoperative-day time (explicit in governing equations); gave the exact
HABR-to-resistance update procedure; renamed Monte Carlo ranges "illustrative
sensitivity intervals" (not 95% CIs, given the repeated-measures structure
independent sampling doesn't capture) with explicit disclosure of what was
and wasn't propagated; adopted the reviewer's suggested softened conclusion
language throughout, removing "directionally necessary."

Files: `build_manuscript_round3.py` (revised manuscript), `Response_to_
Reviewer_Round2.docx` (professional-tone point-by-point response, no
workflow-internal commentary per the reviewer's note), `plot_round2_figures.py`
(regenerated Figures 4-5 with corrected numbers). Verified via the
Word-COM-to-PDF-to-image pipeline: all 14 pages render correctly.

## 18. Major revision, round 3: propagated the two structural uncertainties (2026-08-31)

Reviewer round 3 verdict: round 2's dimensional/statistical fixes were
correct, but the corrected model has two unresolved identifiability
problems that materially affect its results, and asked for propagation
(not more caveats). Key findings, both genuinely new analysis:

- **POD1 non-identifiability (Rs_HA, L_HA, P_HA_amp jointly fit to 2
  targets) turns out NOT to be the dominant uncertainty**: generated the
  full admissible family (`reviewer_round3_identifiability.py`, scanning
  P_HA_amp 23.5-60mmHg, re-solving Rs_HA/L_HA for each), propagated every
  member through POD30. Envelope: 20.2%-27.1% explained -- narrow, because
  Rs_HA and mean_Q_HA are nearly invariant across the family (only L_HA/
  P_HA_amp trade off against each other for pulsatility shape).
- **Vessel-calibre growth (BOTH portal and hepatic-arterial) IS the
  dominant uncertainty**: `reviewer_round3_diameter_2d.py`. HA's own
  baseline-diameter uncertainty (1.0-1.4mm, properly re-anchored -- caught
  and fixed a real bug in my own first attempt at this check, which
  skipped re-anchoring and gave a spurious result) has little effect
  (23.7%-26.4%). But HA diameter GROWTH has a large effect in the
  OPPOSITE direction to portal growth (25.3%@0% -> 191.2%@40% growth,
  amplifying rather than reversing). 2D joint grid: -44% to +129% across
  a modest, jointly plausible 0-20% growth range in each vessel.
- **Graft-mass Q_PV-scaling ambiguity checked and found NOT material**:
  scaling Q_PV 0.5-2x (as if graft mass were 200-50g) changes the result
  only 25.1%-25.5% -- a reassuring, honestly-reported negative finding.
- **Mean-velocity-vs-Doppler-PSV distinction**: v=Q/A gives cross-
  sectional mean velocity, not the spatial-peak PSV measure; no HA-side
  profile factor (analogous to Chen's portal 0.57) exists. Retracted the
  "25 mL/min external plausibility check" framing since this conflation
  is absorbed into the POD1 fit.
- **Explicit real units derived and stated**: P(mmHg)/Q(mL/s during
  integration)/tau(seconds) were already implicit in the code -- gives
  Rs/Rp in mmHg*s/mL, L in mmHg*s^2/mL, C in mL/mmHg. Sanity check: real
  Rs_HA~128 mmHg*s/mL back-of-envelope matches ΔP~50mmHg/flow~25mL/min
  (~0.42mL/s) = ~120 -- physically reasonable.
- **Removed all revision-history narrative from the manuscript** ("an
  earlier version...", "this version corrects...", "(as round 2)") --
  caught several stray instances that survived into the rendered PDF via
  a full-text grep before finalizing; process narrative now lives only in
  the response letters.

Files: `build_manuscript_round4.py`, `Response_to_Reviewer_Round3.docx`,
`plot_round3_figures.py` (new Figures 6, 8). Verified via render pipeline
AND a full-text grep of the rendered PDF for leftover revision-history
language (a good general QA technique worth reusing).

## 19. Major revision, round 4: equation fix + structural remodeling + bounded-family precision (2026-08-31)

Reviewer round 4: round 3's structural-uncertainty analyses were sound,
but flagged (1) an apparent factor-of-60 error in the flow-to-velocity
equation, (2) that the HA-growth sensitivity only changed the observation
equation's area, not the circuit's own Rs_HA/L_HA -- mislabeled as a
complete "calibre-growth" simulation, (3) "entire admissible family" claim
overstated relative to the actually-explored 23.5-60mmHg range, (4)
"plausible" calibre-growth ranges asserted without support, (5) baseline
HA diameter and postoperative growth tested separately, not combined.

- **Point 1 verified as manuscript-only**: directly checked the code
  against the reviewer's own back-of-envelope math (mean flow 25.0mL/min
  = 0.417mL/s / 0.0113cm^2 = 36.9cm/s, consistent with PSV=53.1cm/s) --
  confirmed the CODE was already correct (a double mL/min<->mL/s
  conversion in the implementation cancels out exactly), only the WRITTEN
  equation in the manuscript was wrong. Fixed to v=Q/A with an explicit
  one-line dimensional check now included.
- **Point 2**: added a genuine second analysis. Primary result relabeled
  "kinematic dilution only" (only A_HA changes at the final flow->velocity
  step; Rs_HA still solved via the same HABR flow-target procedure, L_HA
  untouched). New "exploratory structural remodeling" variant additionally
  scales L_HA geometrically (~1/(1+g)^2) with assumed growth
  (`reviewer_round4_structural_growth.py`). Result: the two give close,
  not identical, numbers (191.2% vs 185.6% at 40% HA growth) -- confirms
  the simplification isn't badly misleading for this specific check, a
  genuine finding not assumed in advance.
- **Point 3**: renamed "entire admissible family" -> "admissible family
  within the explored 23.5-60mmHg range" throughout. Tested extending to
  300mmHg (supraphysiological, for convergence only): envelope stabilizes
  20.2%->18.8%, justifying the practical range used. Reported full 19-point
  grid, L_HA range (2.16-22.23), fitting tolerances, root-finding bounds.
- **Point 4**: "plausible" -> "illustrative" throughout for calibre-growth
  ranges, adopting reviewer's suggested phrasing closely.
- **Point 5**: combined baseline HA diameter (1.0/1.2/1.4mm) with growth
  sensitivity -- shape consistent across all three baselines (129.5%,
  128.8%, 127.7% at 20% growth respectively).
- Also fixed: abstract wording (Rs_HA stable vs L_HA/P_HA_amp trading off),
  explained in 3.3 why %-reproduced still varies given near-constant mean
  flow (PSV depends on pulsatile shape, not just mean), "explained"->
  "reproduced" in 3.5, Data/code section now flags the public-repo URL as
  a pre-submission action item rather than assuming one exists (did NOT
  unilaterally create a public repo -- that requires the user's explicit
  go-ahead, per this session's standing practice).

Files: `build_manuscript_round5.py`, `Response_to_Reviewer_Round4.docx`,
`reviewer_round4_structural_growth.py`. Verified via render pipeline + full-
text grep for revision-history language (clean).

## 20. Minor revision, round 5: consistency edits (2026-08-31)

Reviewer verdict upgraded to MINOR REVISION -- "the principal substantive
modelling issues raised in the previous rounds" are resolved. Seven small
consistency fixes applied (`build_manuscript_round6.py`):
1. Sentence fragment fixed in Methods 2.6.
2. Remaining "full admissible family" instance in Table 3 -> "explored
   admissible family within P_HA_amp = 23.5-60 mmHg".
3. "pulse-pressure amplitude"/"supraphysiological pulse pressure" ->
   "sinusoidal pressure amplitude"/"supraphysiological pressure amplitude"
   throughout (P_HA_amp is a sinusoid amplitude, not conventional pulse
   pressure = 2x this value).
4. Table 3 combined-parameter rows (Rs_PV/Rs_HV/Rp_hv_out; Rs_HA/L_HA
   generic; Rs_HA/L_HA/P_HA_amp POD1) split into individual rows, each
   with its own unit in the Units column (was: units crammed into Value
   column with "see units column" placeholder).
5. Results heading "Calibre-growth sensitivity dominates: portal AND
   arterial, jointly" -> "Illustrative vessel-calibre sensitivity exceeds
   parameter-fit uncertainty" (states what's demonstrated, doesn't imply
   growth was measured).
6. Added explicit limitation sentence for the structural-remodelling
   variant directly in Methods 2.7 (previously only in Discussion):
   "Because resistance remains determined by the HABR flow target rather
   than an independent radius-resistance law, this variant evaluates
   inertial remodelling but is not a complete geometric reconstruction of
   vascular growth."
7. Code-availability placeholder ("[repository URL to be added...]")
   replaced with the reviewer's suggested neutral interim statement: "The
   code underlying this analysis will be deposited in a public repository
   before publication." -- did NOT invent a URL or unilaterally create a
   public repo; that remains an open item to raise with Harvey before
   actual submission.

Verified via render pipeline + full-text grep (clean, no leftover
revision-history language or flagged phrases). Reviewer's overall
assessment: manuscript is now "methodologically transparent, dimensionally
consistent as written, appropriately cautious" with a "useful and
appropriately limited" principal conclusion -- ready for submission after
these edits, final visual proofing, and code release.

## 21. Reframed for Medical Engineering & Physics submission (2026-08-31)

Harvey requested a reframe targeting Med Eng Phys specifically, as a
computational physiology/model-identifiability study, emphasizing the
dimensionally-consistent model + non-identifiability propagation +
"missing calibre data precludes attribution" as the METHODOLOGICAL
ADVANCE (not a predominantly negative result). `build_manuscript_MEP.py`:

- **New title**: "A Sensitivity and Identifiability Framework for Testing
  the Hepatic Arterial Buffer Response After Paediatric Liver
  Transplantation" -- leads with "framework," not the HABR finding.
- **Citation style converted** from author-year to MEP's house numbered
  Vancouver style throughout (in-text [1]-[12] in order of first
  appearance, reference list renumbered to match) -- matches the actual
  style of Ho 2013's own Med Eng Phys paper (already in the reference
  list) confirming this is the correct target format.
- **Added Elsevier-standard structure**: Highlights (5 bullets, framework-
  forward, e.g. "Propagated parameter non-identifiability is not the
  dominant uncertainty"), a new Graphical Abstract (3-panel: model
  schematic -> narrow identifiability envelope -> wide calibre-sensitivity
  grid spanning sign reversal), and a structured "Declarations" section
  (Funding/Competing interests/Ethical approval/Data availability
  subheadings) replacing the informal "Data, code, and ethics" heading.
- **Reframed Introduction**: states explicitly "this study makes two
  contributions, one methodological and one substantive, and we present
  the methodological contribution as the primary one" -- sets the
  framework-first framing from the opening rather than letting it emerge
  only in Discussion.
- **New Discussion structure** (4.1-4.3, replacing the flatter round-6
  Discussion): 4.1 "A transferable framework for Doppler-based mechanistic
  hypothesis testing" (states the 3-step methodology generally, positions
  this HABR case as ONE application); 4.2 the specific HABR finding
  (shortened, since 4.1 already carries the main argument); 4.3 "Required
  future measurement, framed as a positive output" -- explicitly reframes
  "we couldn't quantify HABR" as "we specify exactly what serial
  measurement would resolve it, and quantify how much it would matter" --
  directly addresses the reviewer's/Harvey's concern about the negative-
  result risk.
- Results 3.3/3.5 got one added sentence each connecting the specific
  numeric finding back to the general methodological point (e.g. 3.3: "a
  model can be non-identifiable in its full parameter space while still
  being well-constrained in the specific output quantity... a distinction
  only visible by propagating the family").
- All substantive numbers, tables, equations, and reviewer-driven
  precision language carried over unchanged from round 6 -- this is a
  framing/structure/citation-style change, not a re-analysis.

Verified via render pipeline (18 pages) + full-text grep (no leftover
author-year citations, no revision-history language).

**Still open, flagged not resolved**: Funding and Competing-interests
declarations left as placeholders for Harvey to complete; code repository
still not created (same standing item from round 4-6).

**Not yet done**: the pre-op -> POD1 transition itself (by far the largest
change in the dataset) has not been modeled at all yet -- Section 4.1 flags
this as mechanistically distinct (discrete graft replacement, not a flow
perturbation) and it would need its own treatment (e.g., an explicit
"cirrhotic native liver" vs. "healthy graft" resistance parameter change,
separate from the HABR feedback term). Also not yet explored: whether a
prescribed (rather than frozen-at-POD1) time-varying systemic pulse amplitude
or R_out could recover the missing 80% of the PSV_HA decline and the RI_HA
direction -- i.e., whether "other systemic recovery" is a viable, testable
mechanism rather than just a residual left unexplained.

## 22. Pre-operative BA state folded in; transplant-step transition analysed (2026-09-13)

New script `preop_ba_state.py`, plus an additive `MEASURED["Pre-op"]` entry in
`ldlt_habr_consistent_units.py` (PSV 73.32, RI 0.77, PVV 16.88, pre-op PV diameter 0.44 cm --
Chen et al. Tables 1-2). Motivation: the revision-plan validation target "the transplant step
reproduces the portal-flow doubling" requires the model to span the transplant event itself, not
start at POD1.

**Pre-op calibration works exactly.** The HA branch (Rs_HA, L_HA, P_HA_amp) fits the cirrhotic
targets to residual ~1e-26: Rs_HA=106.37 mmHg*s/mL, L_HA=0.169, P_HA_amp=33.96 mmHg, with the
cirrhotic bed absorbed into the effective arterial parameters (healthy-graft downstream held fixed,
per the Section 18 "absorbed into the fit" philosophy). Notably the fitted pre-op mean arterial flow
(30.6 mL/min) is nearly the post-transplant value (31.9): the high pre-op PSV is carried by
waveform shape, not mean flow. A forward-Euler stability pre-check (Rs*dt/L <= 1.8) was added to
the fitting objectives after unstable starts overflowed the integrator.

**The portal-flow doubling is reproduced from cohort data:** Q_PV(pre-op) = 87.78 mL/min
(PVV 16.88, D 0.44) -> Q_PV(POD1) = 175.06 (PVV 30.80, D 0.46) = x1.994.

**Transition scenarios (pre-op fitted state, portal flow swapped to POD1):**

| Scenario | PSV_HA (cm/s) | vs. measured 20.22 cm/s decline |
|---|---|---|
| Measured | 73.32 -> 53.10 | (-27.6%) |
| S1 null (Rs_HA frozen) | 72.57 | explains 3.7% |
| S2 HABR applied, canonical convention | 109.04 | explains -176.6% (opposes the decline) |

**The sign tension is the substantive finding.** The canonical convention
(`change_Ipv=(Q_ref-Q_new)/Q_ref*100`, `target=baseline*(1-changeIha/100)`) implements positive
portal->arterial flow coupling: applied to POD1->POD30 (both declining) it explains part of the
measured PSV decline (Sections 18-19, 13-31%); applied to the transplant step (portal x1.994) the
same convention drives arterial flow UP 48% (PSV 109), opposite to the measured decline. Classical
HABR (negative coupling: portal up -> arterial down) is directionally consistent with the
transplant step but inconsistent with the POD1->30 decline. **No single-sign coupling of this form
explains both windows** -- which extends the manuscript's central thesis (HABR's quantitative
contribution cannot currently be established) to the transplant event itself, and sharpens the
Section 3.2 attribution gap: the measured PSV drop at transplant is dominated by mechanisms outside
the prescribed-portal-flow coupling (graft-bed replacement), and the RI drop (0.77 -> 0.61) is
unreachable without a cirrhotic-bed parameter. Awaiting Harvey's reading of the sign convention
before any manuscript use.

**Caveats:** (1) the pre-op admissible-family scan found exact fits only at P_HA_amp = 34-40 mmHg
with the scanned starts (the scan is start-sensitive; the family is narrower than the post-LDLT
one but was not exhaustively mapped); (2) the pre-op state shares the 57.5 mmHg mean arterial
source-pressure assumption (same child pre/post, not measured separately); (3) the downstream is
held at healthy-graft parameters throughout -- the structural note in the script output states
this; the natural next extension is a cirrhotic-bed resistance scale (on Rs_HV/Rp_sinus) at pre-op,
which would let the model attribute the RI drop mechanically rather than absorbing it.

Files: `preop_ba_state.py` (new), `ldlt_habr_consistent_units.py` (MEASURED["Pre-op"] added),
`../parameter_table.md` Section 7 updated.

## 23. Cirrhotic-bed parameter added; transplant-step attribution analysed (2026-09-13)

New script `preop_ba_cirrhotic_bed.py`. The Section 22 structural limitation (cirrhotic bed
absorbed into the pre-op arterial fit) is now explicit: `k_bed >= 1` scales Rs_HV (the sinusoid ->
hepatic-vein series resistance, the intrahepatic outflow path cirrhosis obstructs) at pre-op; the
transplant step sets k_bed -> 1 (graft replaces the bed). Rp_hv_out and the pi-filter topology
leak Rp_sinus are deliberately not scaled; fibrotic stiffness (a C_sinus reduction) is not
modelled. Four transition arms per family member: null (no arterial response), required
(sign-agnostic best-fit of Rs_HA to the MEASURED POD1 state), habr_canonical (convention verbatim),
habr_classical (same quadratic magnitude, classical buffer sign for a portal-flow increase).

**Finding 1 -- k_bed is non-identifiable from the pre-op Doppler targets.** Exact pre-op fits
(PSV 73.32, RI 0.77) exist across the entire scanned range k_bed = 1-8 (P_HA_amp 40-60 mmHg on
these starts; 21 cells). Doppler indices alone cannot infer cirrhotic-bed severity in this
circuit -- k_bed joins the round-3 non-identifiable set (Rs_HA, L_HA, P_HA_amp).

**Finding 2 -- the measured transition is infeasible for ANY single arterial-resistance change,
in either sign convention.** Holding the pre-op arterial waveform shape (L_HA, P_HA_amp) fixed
and varying only Rs_HA at POD1 (healthy bed, prescribed portal surge):

| Arm | PSV, % of measured 20.22 cm/s decline | RI at POD1 | Rs_new/Rs_pre |
|---|---|---|---|
| Measured | 100 % (PSV 53.10) | 0.61 | -- |
| null | [-10.0, +3.7] % | [0.749, 0.778] | 1.0 |
| required (best compromise) | [49.1, 87.8] % | [0.795, 0.834] | [1.20, 1.40] (median x1.28) |
| habr_canonical | [-146.8, -117.0] % | [0.628, 0.708] | dilatation |
| habr_classical | [+141.9, +163.8] % | [0.824, 0.941] | constriction |

The PSV target (53.10, demands constriction) and the RI target (0.61, demands the opposite)
pull in OPPOSITE directions along the single-knob Rs_HA curve: the required arm plateaus at a
x1.28 compromise with BOTH targets missed (distance ~1e-1), and neither HABR sign application
lands near the measured state. Within this structure (fixed L_HA, P_HA_amp; one-knob bed;
prescribed portal flow), the transplant-step transition cannot be produced by any arterial
resistance mechanism -- HABR included, under either sign reading.

**Interpretation.** Feasibility is not in question globally: the canonical POD1 anchor
(`ldlt_habr_consistent_units.py`) hits both POD1 targets exactly -- but from a completely
different (Rs_HA, L_HA, P_HA_amp) corner. The measured transplant-step transition therefore
requires coordinated changes in arterial waveform parameters (L_HA, P_HA_amp) and/or downstream
structure beyond an Rs_HV scale -- i.e. the "graft replacement" component is multi-dimensional,
and the HABR contribution at the transplant step cannot be isolated even with an explicit bed
parameter. This extends the manuscript's central thesis (calibre-growth uncertainty dominates the
POD1->30 attribution) to the transplant event itself: across the transplant, structural change
swamps any flow-coupling signal.

**Unit-convention note (prevents confusion across scripts).** The Rs_HA = 0.8284 / 0.849 / 0.952
values in Sections 12 and 18 are from `ldlt_habr_on_pi_filter.py` (superseded), where Rs_HA is a
MULTIPLIER on the baseline resistance. All Section 22-23 fits are on the absolute scale of
`ldlt_habr_consistent_units.py` / `pi_filter_healthy_infant_model.py`
(BASE_PARAMS Rs_HA = 97.958 mmHg*s/mL), where the pre-op family sits at Rs_HA ~ 100-106.

**Caveats.** One-knob bed (no stiffness); portal flow prescribed; pre-op exact fits not found
below P_HA_amp = 40 on the scanned starts (start-sensitivity, cf. Section 22); k_bed identified
only through its non-identifiability -- no independent severity constraint. Files:
`preop_ba_cirrhotic_bed.py` (new), `../parameter_table.md` Section 7 updated.

## 24. Anastomosis-stenosis parameter and the graft-tolerance sweep (2026-09-13)

New script `anastomosis_stenosis_sweep.py` (+ `stenosis_sweep_figure.png`) -- the revision-plan
"allowable obstruction" deliverable. The anastomosis is a fixed structural resistance in series
with the inflow branch, Poiseuille-parameterised by DIAMETER stenosis s:
R_anas(s) = R_anas(0)/(1-s)^4, R_anas(0) = 8*mu*L/(pi r^4) with mu = 3.5 cP, L = 2 mm (assumed),
r0 = 0.06 cm (HA, the model's Kim 2007 calibre) / 0.23 cm (PV, Chen POD1). Sanity anchors hold:
a healthy HA anastomosis is 1.05% of Rs_HA, reaches ~Rs_HA near 70% narrowing; the PV anastomosis
is 0.18% of Rs_PV.

Circuit: the 5-state model (Q_PV must be a state for PV stenosis to act), recalibrated at the
POD1-anchored state: Q_PV = 175.06 mL/min (Section 12 convention), Q_HA = 31.93 (v4 draft
post-transplant mean), Q_HV = Q_PV + Q_HA (the source's ~3% mass-balance gap is CLOSED by
conservation -- a modelling choice, flagged). Numerical: the stenosis resistance makes the flow
branches stiff (Euler unstable beyond ~76% HA narrowing at the default dt), so the flow branches
use their exact exponential map over each dt; pressure states keep the canonical Euler update.
Verification at s=0: Q_PV 175.19 vs 175.06 target (0.07%).

HABR: quasi-steady discrete loop (run -> change_Ipv vs the unstenosed baseline -> Rs_HA update ->
re-run -> fixed point), in both sign arms (classical buffer / canonical convention, per Sections
22-23). The loop is gated to PV stenosis only (portal-flow-triggered mechanism); HA-only narrowing
keeps Rs_HA frozen -- the HA curve is the uncompensated structural test. (An earlier ungated
version accidentally let the tiny P_sinus-mediated portal perturbation drive a spurious full
arterial compensation on the HA side; caught by inspecting the Rs_HA column and gated.)

**The metric matters (methodological point for the manuscript).** For HA stenosis, TOTAL graft
inflow is misleading: the portal inflow rises as P_sinus falls (175 -> 183 mL/min across the
sweep) and props total inflow at >= 90% even while the arterial supply collapses to 13% of
baseline. HA thresholds are therefore reported on ARTERIAL flow; PV thresholds on total inflow.

**Allowable stenosis (diameter narrowing at which the metric falls below threshold):**

| Vessel | Metric | Arm | 90% | 80% |
|---|---|---|---|---|
| HA | arterial flow | all (Rs frozen) | **44.6%** | **54.8%** |
| PV | total inflow | none | 68.2% | 74.3% |
| PV | total inflow | classical buffer | 69.0% | 75.2% |
| PV | total inflow | canonical | 67.4% | 73.5% |

**Interpretation.** (1) The model reproduces the clinical asymmetry: the HA anastomosis is the
vulnerable one (arterial flow 90% threshold near ~45% narrowing; collapse beyond 60%: art%
71.0 -> 43.7 -> 13.3 at 60/70/80%), the PV anastomosis tolerates ~68-75% narrowing -- the r^4
geometry plus the 4x wider calibre. Consistent with HA complications dominating infant LDLT.
(2) The HABR buffer barely moves the PV 90%-threshold (+0.8 points) because arterial flow is only
~15% of total inflow, but at deep PV stenosis the classical buffer produces marked arterial
hyperaemia (art% 130 at 80%, 165 at 90% narrowing; PSV_HA up to 97.4 cm/s) -- a Doppler-visible
HABR signature during portal inflow obstruction. The canonical arm does the opposite (art% 45-76).
(3) Distal HA PSV falls with narrowing (59.6 -> 51.7 -> 26.4 -> 8.0 cm/s at 0/50/70/80%) -- a
parvus/tardus-like pattern; the model's PSV here is indicative (5-state waveform shape is the
generic default, not the POD1 anchored family).

**Caveats.** Thresholds scale linearly with the assumed anastomosis length and viscosity (infant
post-op polycythaemia shifts HA thresholds DOWN); no remodelling/collaterals; fixed structure;
the HABR sign question of Sections 22-23 applies (classical arm used for the tolerance question,
canonical shown as contrast); %-results insensitive to the mL/min vs /100g labelling ambiguity.

Files: `anastomosis_stenosis_sweep.py` (new), `stenosis_sweep_figure.png` (new),
`../parameter_table.md` Section 7 updated.

## 25. Recipient-size spectrum: fixed LLS graft across the infant-to-child range (2026-09-13)

New script `recipient_size_spectrum.py` (+ `recipient_size_spectrum_figure.png`) -- the
revision-plan Section 3.2 deliverable. The graft circuit is FIXED (Chen-anchored, Section 24's
5-state calibration; `simulate_circuit` gained additive P_HA_mean_src / P_PV_src_override /
Rs_PV_override parameters, defaults unchanged); recipient size enters through literature-sourced
bracket inputs.

**Bracket inputs (literature):** cardiac index 200 / 150 / 125 mL/kg/min for infant / toddler /
school age (pediatric anaesthesia references: Anesthesia Key, Morgan & Mikhail, OpenAnesthesia);
MAP 49-62 / 57-71 / 65-78 mmHg, midpoints used (Freeman & Harrington values via Haque & Zaritsky
2008); heights 68 / 96 / 121 cm (growth-chart medians, approximate); SLV = 706.2 x BSA + 2.4
(Urata 1995, Du Bois BSA). Graft = 220 g LLS.

**Results (fixed 220 g LLS graft):**

| Bracket | wt (kg) | MAP | Q_HA / Q_PV (mL/min) | CO share | GRWR | GV/SLV |
|---|---|---|---|---|---|---|
| infant ~6-9 mo | 7 | 55.5 | 30.7 / 175.5 | **14.7%** | **3.14%** | 88.1% |
| toddler ~3 y | 15 | 64.0 | 35.9 / 174.2 | 9.3% | 1.47% | 49.9% |
| child ~7 y | 22 | 71.5 | 40.4 / 173.0 | 7.8% | 1.00% | 35.9% |

(1) **The hyperperfusion exposure is the infant end, quantified.** The graft's absolute inflow is
nearly size-invariant (set by its own low-resistance circuit), so its share of the recipient's
cardiac output scales inversely with weight: 14.7% at 7 kg vs 7.8% at 22 kg. The infant bracket
sits ABOVE the published large-for-size risk threshold (GRWR >= 2.51%: worse survival and HAT, all
recipients < 1 y -- Ueda 2021, Kyoto, n=160); the older brackets sit below on both GRWR and CO
share. The model metric and the clinical risk line land on the same end of the spectrum.
(2) **Anastomosis tolerance is exactly size-invariant.** The HA arterial-flow stenosis thresholds
(90%/80% of baseline flow) are 44.6%/54.8% narrowing at EVERY bracket: the threshold is a
resistance ratio (R_anas/Rs_HA), and the driving pressure cancels. Clinically: the modifiable
factor is anastomosis quality, not recipient size. (3) **Graft-type trade-off at the infant
bracket** (crude mass-proportional allometry -- order of magnitude only): a 500 g left lobe takes
24.8% of the infant's CO at GRWR 7.1% (>> Nagata's ~4% vascular-modification threshold) -- the
model quantifies why metabolic reserve doubles while CO exposure more than doubles, consistent
with graft-reduction/monosegment practice at this end.

**Caveats.** Reference-table haemodynamics (not transplant-population data); per-size Doppler
targets do not exist -- the near-size-invariance of absolute graft flows is the argument, but its
empirical support is the infant cohort only; portal driving pressure fixed at 13 mmHg; the
calibration anchor keeps the draft's 57.5 mmHg mean (brackets use literature midpoints).

Files: `recipient_size_spectrum.py` (new), `recipient_size_spectrum_figure.png` (new),
`anastomosis_stenosis_sweep.py` (additive override parameters),
`../parameter_table.md` Section 7 updated.

## 26. The 0D-1D hybrid restored: HABR circuit coupled to the 2018 patient-specific trees (2026-09-13)

New scripts `virtual_graft_tree.py` (parser/renderer for the 2018 Cmgui-format Lisa trees in
../simulation/) and `hybrid_0d_1d.py` (the coupling). The trees parse fully: ~1,030 nodes/elements
per tree (arterial / portal / hepatic venous), cubic-Hermite geometry, with per-node Flow,
Strahler order, radius. Stored flows decode as x60,000 = mL/min: the arterial root = 31.9 and the
portal root = 300.5 mL/min -- exactly the draft's own calibration values, confirming the 2018
solve and its scale.

**Coupling design (quasi-steady, per the repo's discrete-HABR philosophy):** the 1D layer owns
space -- per-segment Poiseuille resistances (stored radii/coordinates, mu = 3.5 cP), tree-reduced
bottom-up to effective conduit resistance, segment flows assigned by subtree conductance at a
common sink. The 0D layer owns the anchors (calibrated branch resistances) and the HABR law.
Coupling rule: calibrated total = conduit + microcirculation lump M; HABR scales M (the buffer
response is arteriolar, not conduit), and the resulting root flow re-solves the tree.

**Findings.** (1) The 2018 trees are pure conduit: the reduced tree resistance is ~0.01% of the
calibrated totals on all three branches -- physiologically correct (large vessels are transparent
pipes) and the quantitative justification for HABR acting on the microcirculation lump: the 0D
resistance IS the microcirculation, the tree carries its spatial distribution. (2) Flow-split
validation vs the 2018 stored flows: log-log r = 0.71 (arterial) / 0.63 (portal), with a
systematic ~12x terminal-flow deviation -- the 2018 solve used heterogeneous terminal conditions
(generation-lumped resistances, not stored in the files); the reconstruction is therefore
topologically exact but hydraulically approximate, honestly stated. (3) Virtual-surgery scenarios
on the arterial tree (`hybrid_0d_1d_scenarios.png`): (a) HABR constriction -- transplant-step
portal surge (changeIpv = -99.4%, classical read: changeIha = -47.6%) constricts the
microcirculation and scales the whole tree's flows x0.524 (uniform, as physiology requires);
(b) virtual resection -- a 348-node distal subtree (34% of the tree, 3.9% of baseline flow)
removed; its flow re-routes through the remaining tree, the non-uniform spatial response the 0D
model alone cannot show.

**Next refinements (not blocking):** full bidirectional iteration (tree R_eff -> 0D -> HABR ->
tree per quasi-steady step); the 2018 generation-lumped terminal resistances recovered to close
the flow-split validation; anastomosis stenosis placed on the tree root and propagated spatially.

Files: `virtual_graft_tree.py` (new; fixed element parser -- element lines are indented),
`hybrid_0d_1d.py` (new), `virtual_graft_trees.png`, `hybrid_0d_1d_scenarios.png` (new).
