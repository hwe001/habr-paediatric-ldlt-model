import docx

d = docx.Document()
d.add_heading("Response to Reviewer, Round 1", level=1)
d.add_paragraph(
    "We thank the reviewer for a detailed, substantive critique. Every "
    "point below prompted a genuine change to the analysis or model, not "
    "only wording -- in two cases (points 1 and 8) the requested check "
    "surfaced a real problem we had not previously tested."
)

points = [
    ("1. Acute-then-frozen mislabelled as 'corrected'",
     "Agreed and changed. HABR's fast kinetics describe a continuously-"
     "coupled feedback (adenosine washout responds to whatever portal "
     "flow currently is), not a one-off event -- this does not, by "
     "itself, justify freezing resistance after POD7. The manuscript now "
     "presents three scenarios (continuous / acute-then-frozen / null) "
     "symmetrically, with the acute-then-frozen scenario explicitly "
     "described as motivated by an observation (RI flatness), not "
     "physiologically proven (new Methods 2.5, citing Eipel, Abshagen "
     "and Vollmar 2010 on HABR's continuous-coupling nature)."),
    ("2. Flat RI does not prove resistance adaptation ended",
     "Agreed. We ran a Welch's t-test on the published summary statistics "
     "(new Methods 2.6 / Results 3.3): the 95% CI on the POD7-vs-POD30 RI "
     "difference is [-0.010, +0.010], which cannot exclude a true change "
     "as large as the real, independently-observed POD1-to-POD7 change. "
     "'RI is flat' is now reported as 'not detectably changing' with "
     "this explicit caveat, not as proof the resistance-driven component "
     "is complete."),
    ("3. Flow-to-velocity mapping insufficiently specified",
     "Added new Methods 2.2 (explicit governing ODEs, all five state "
     "variables and every parameter named) and 2.2.1, which states "
     "plainly that no hepatic-artery cross-sectional area is used or "
     "assumed anywhere -- Q_HA is a directly-calibrated proxy for "
     "Doppler velocity, calibrated at POD1 against real PSV_HA/RI_HA. "
     "PSV/EDV/RI extraction formulas are given explicitly. A full "
     "parameter table (new Table 3) lists every value, unit, and source."),
    ("4. 'Validated' overstates calibration by construction",
     "Changed throughout: 'validated' -> 'calibrated'; Figure 3's caption "
     "now says 'calibration targets'; Methods 2.2 states explicitly that "
     "the resistances were solved exactly (not fit approximately) from "
     "the same targets being compared against, so agreement is close by "
     "construction, not independent validation."),
    ("5. 'Parameter-free HABR' is misleading",
     "Changed throughout to 'fixed-coefficient HABR relationship "
     "(coefficients imported, not re-fit to POD7-30 data)', with an "
     "explicit list (Methods 2.3) of what IS calibrated or assumed "
     "elsewhere in the model (Rs_HA, L_HA, pressure amplitude, portal "
     "diameter)."),
    ("6. False precision on percentages",
     "Added new Methods 2.7 / Results 3.4: Monte Carlo propagation of "
     "the compared means' sampling uncertainty (SEM, n=41) gives 95% "
     "intervals alongside each point estimate. These are wide -- e.g. "
     "the POD7 continuous-scenario estimate is 13% but the interval is "
     "[6%, 77%] -- and the text now says so explicitly rather than "
     "reporting single-decimal percentages as if precise."),
    ("7. Portal-flow formula units unresolved",
     "Addressed directly in new Methods 2.4: the formula as given by "
     "Chen et al. and reproduced here yields mL/min, not mL/min/100g as "
     "labelled -- no graft-mass term appears in it. Graft weight was not "
     "available to us. We state this is inherited from the source "
     "paper's own presentation, not resolved by us, and flag the "
     "consequence: Q_HA (Doppler-calibrated) and Q_PV (this formula) are "
     "summed directly in the model with no demonstrated common physical "
     "basis. This is now an explicit limitation, not a hidden issue."),
    ("8. Constant POD1 diameter not sensitivity-tested",
     "This is the most consequential finding of the revision. New "
     "Methods 2.8 / Results 3.5: we swept assumed portal-diameter growth "
     "by POD30 from 0-40%. At just 10% growth, the headline '% of "
     "decline explained by HABR' result REVERSES SIGN (+31% to -11%). "
     "This is now presented as the central caveat on the whole "
     "quantitative analysis (new Figure 7), not a minor sensitivity "
     "footnote -- it shows the reported percentages are conditional on "
     "an assumption the data cannot verify and is not even directionally "
     "safe."),
    ("9. Graft dilution presented as favoured rather than a hypothesis",
     "Reworded throughout (Results 3.6, Discussion, Conclusion, "
     "Abstract): now explicitly 'a testable hypothesis,' with the "
     "timing argument (fast normalization vs. slower regeneration) "
     "labelled as 'a plausible basis for a hypothesis,' not a "
     "conclusion. Results 3.5's sensitivity finding is cross-referenced "
     "here specifically to show the data cannot adjudicate between "
     "candidate mechanisms quantitatively."),
    ("10. Competing-mechanism list incomplete",
     "Expanded (Results 3.6): added systemic cardiac output/pressure-"
     "amplitude changes beyond the fixed assumption, postoperative "
     "oedema, arterial spasm, anastomotic geometry, Doppler insonation "
     "angle/sampling-location variation, sedation, and heart rate, with "
     "an explicit statement that none of these were assessed and the "
     "study does not claim to have enumerated or excluded them."),
]
for title, body in points:
    d.add_heading(title, level=3)
    d.add_paragraph(body)

d.add_heading("Editorial notes", level=3)
d.add_paragraph(
    "Abstract and Discussion shortened and de-duplicated. Every equation "
    "symbol and unit is now defined (Methods 2.2, 2.2.1, Table 3). Code "
    "availability wording softened from a flat 'on request' to note "
    "intent to establish a public repository in a future revision, "
    "matching this session's practice on the two other projects. We "
    "searched for published alternatives to the two unpublished-"
    "manuscript citations and did not find an equivalent real paediatric "
    "LLS-LDLT pressure/flow dataset; this dependency is now stated "
    "plainly as a limitation rather than left implicit. Figure "
    "renumbering: the pre-existing Figures 4-6 (measured vs. scenario "
    "comparisons) are retained under the new symmetric framing; a new "
    "Figure 7 (diameter sensitivity) was added."
)
d.add_paragraph(
    "We were unable to complete full page-render QA in this pass beyond "
    "what our own Word-COM-to-PDF-to-image pipeline could check (all 15 "
    "pages, 7 figures, 3 tables rendered correctly in that check); we "
    "note the reviewer's own comment that their layout assessment was "
    "based on document structure and extracted figures rather than a "
    "full render, and would welcome a rendered check if the reviewer's "
    "environment allows it in a subsequent round."
)

d.save("Response_to_Reviewer_Round1.docx")
print("Saved: Response_to_Reviewer_Round1.docx")
