# A Sensitivity and Identifiability Framework for Testing the Hepatic Arterial Buffer Response After Paediatric Liver Transplantation

Python implementation of a dimensionally-consistent lumped-parameter
("pi-filter") hepatic circulation model, used to test whether the hepatic
arterial buffer response (HABR) -- the intrinsic tendency of hepatic
arterial flow to counteract portal venous flow changes -- can be
quantitatively attributed as the cause of the hepatic arterial Doppler
velocity decline observed after paediatric living-donor liver
transplantation (LDLT).

The central methodological contribution is not a single best-fit HABR
estimate, but a framework that propagates two structural uncertainties
rather than disclosing them as caveats: (1) the model's own parameter
non-identifiability, and (2) its sensitivity to postoperative vessel-calibre
change, which is not measured beyond day 1 in the real clinical cohort this
model is anchored to. The main finding is that (1) is a relatively minor
source of uncertainty here, while (2) is large enough to reverse the sign
of the conclusion -- meaning HABR's quantitative contribution cannot
currently be established, and the analysis specifies exactly what serial
measurement (hepatic-arterial and portal-vein calibre) would resolve that.

## Citation

This code accompanies the manuscript:

> "A Sensitivity and Identifiability Framework for Testing the Hepatic
> Arterial Buffer Response After Paediatric Liver Transplantation."
> Manuscript in preparation / under review at the time this repository was
> published (target journal: Medical Engineering & Physics). Please check
> for the final published citation and cite that version if available;
> otherwise cite this repository directly.

**If you use, adapt, or build on this code, please cite the paper above.**

## What's here

### Core model
- `pi_filter_healthy_infant_model.py` -- the generic (non-transplant)
  paediatric hepatic circulation model: pi-filter lumped elements (HA, PV,
  HV), calibrated exactly (via Ohm's law on the linear, time-averaged
  circuit) against independent real target pressures/flows for this
  clinical scenario.
- `ldlt_habr_consistent_units.py` -- **the canonical post-LDLT model**:
  dimensionally-consistent version anchored to the real cohort (Chen et
  al. 2022), with the hepatic-artery branch related to Doppler velocity
  via an explicit, literature-sourced cross-sectional-area assumption. Use
  this, not the earlier iterations below, for any further work.

### Superseded/historical model iterations (kept for the documented
correction trail, described in full in `model_plan_and_literature_data.md`)
- `ldlt_habr_model.py`, `calibrate_and_test.py` -- earliest version; used
  an ad hoc single-branch circuit, not the actual pi-filter element.
- `ldlt_habr_on_pi_filter.py` -- first pi-filter version; later found to
  mix Doppler-velocity-calibrated and volumetric-flow-scale state
  variables in the same mass balance (a genuine dimensional
  inconsistency), fixed in `ldlt_habr_consistent_units.py`.
- `ldlt_habr_acute_then_frozen.py` -- an intermediate step distinguishing
  HABR's acute application window from a continuously-reapplied one; the
  three-scenario comparison (continuous / acute-then-frozen / null) in the
  final analysis supersedes this as a single fixed conclusion.

### Reviewer-driven analyses (each added in response to a specific,
documented review round -- see `model_plan_and_literature_data.md`
Sections 15-21 for the full account of what each one found)
- `reviewer_round1_analyses.py` -- Welch's t-test on RI, Monte Carlo
  uncertainty intervals, an initial portal-diameter-growth sweep.
- `reviewer_round2_stats_fix.py` -- corrects a real statistical error from
  round 1 (a confidence-interval interpretation was backwards).
- `reviewer_round3_identifiability.py` -- generates and propagates the
  full admissible (Rs_HA, L_HA, P_HA_amp) parameter family.
- `reviewer_round3_diameter_2d.py` -- joint portal x hepatic-artery
  calibre-growth sensitivity, and the baseline-diameter re-anchoring check
  (catches and fixes a real bug in an earlier version of this same
  script).
- `reviewer_round4_structural_growth.py` -- distinguishes a "kinematic
  dilution only" growth model from an "exploratory structural
  remodelling" variant that also scales arterial inertance geometrically.

### Figures and manuscript-building scripts
- `plot_healthy_infant_results.py`, `plot_habr_comparison.py`,
  `plot_habr_acute_correction.py`, `plot_diameter_sensitivity.py`,
  `plot_round2_figures.py`, `plot_round3_figures.py`,
  `plot_graphical_abstract.py` -- generate all figures (`*.png`) referenced
  in the manuscript.
- `build_manuscript_round1.py` through `build_manuscript_round6.py` --
  successive manuscript drafts, each responding to one documented
  reviewer round (see `model_plan_and_literature_data.md`).
- `build_manuscript_MEP.py` -- **the final manuscript**, reframed for
  submission to Medical Engineering & Physics (numbered citation style,
  Highlights, graphical abstract, restructured Discussion).
- `build_response_to_reviewer_round1.py` through `..._round4.py` -- the
  point-by-point reviewer response letters.
- `build_healthy_infant_report.py`, `build_habr_comparison_report.py` --
  two standalone supporting reports (baseline model validation; the
  with/without-HABR comparison) written before the full manuscript.

### Outputs
- `*.docx` -- the manuscript itself (final version:
  `A Sensitivity and Identifiability Framework for Testing the Hepatic
  Arterial Buffer Response (Med Eng Phys submission).docx`), the two
  supporting reports, and all four reviewer response letters.
- `*.png` -- all figures, including the graphical abstract.
- `*.csv` -- intermediate numerical results from the reviewer-driven
  analyses.
- `model_plan_and_literature_data.md` -- the full project history: every
  parameter's source, every model iteration, and a section-by-section
  account of all four documented review rounds and how each point was
  addressed (Sections 1-21).

## Requirements

Python 3.10+, `numpy`, `scipy`, `matplotlib`. Manuscript-building scripts
additionally require `python-docx`.

## Running

```bash
python pi_filter_healthy_infant_model.py   # generic baseline model
python ldlt_habr_consistent_units.py       # canonical post-LDLT model
python reviewer_round3_identifiability.py  # identifiability envelope
python reviewer_round3_diameter_2d.py      # calibre-growth sensitivity
```

## Data availability

This project uses only aggregate, already-published group-level statistics
(mean +/- SD, n=41) from Chen et al., "Doppler evaluation of hepatic
hemodynamics after living donor liver transplantation in infants," Front
Bioeng Biotechnol 2022;10:903385 (doi:10.3389/fbioe.2022.903385, open
access) -- no per-patient or otherwise unpublished clinical data is used or
included in this repository, and no patient-identifying information of any
kind appears anywhere in this codebase.

## License

MIT (code only; see `LICENSE`).

## Additional sensitivity analyses

`sensitivity_analyses/` contains the scripts for the HABR-coefficient, assumed-parameter and RI analyses
added in the revision for Medical Engineering & Physics; see `sensitivity_analyses/README.md`.
