"""
Corrects a real statistical error from round 1: a 95% CI of [-0.010,+0.010]
on a mean difference EXCLUDES a true difference of 0.020 -- it does not
fail to exclude it. Re-derives the proper, narrower conclusion the
reviewer specified.
"""

import numpy as np
from scipy import stats

N = 41
RI_SD = {"POD1": 0.05, "POD7": 0.03, "POD14": 0.05, "POD30": 0.01}
RI_MEAN = {"POD1": 0.61, "POD7": 0.59, "POD14": 0.59, "POD30": 0.59}

for a, b in [("POD1", "POD7"), ("POD7", "POD30")]:
    m1, s1 = RI_MEAN[a], RI_SD[a]
    m2, s2 = RI_MEAN[b], RI_SD[b]
    se = np.sqrt(s1**2 / N + s2**2 / N)
    diff = m1 - m2
    t = diff / se
    df = (s1**2/N + s2**2/N)**2 / ((s1**2/N)**2/(N-1) + (s2**2/N)**2/(N-1))
    p = 2 * (1 - stats.t.cdf(abs(t), df))
    ci_half = stats.t.ppf(0.975, df) * se
    print(f"{a} vs {b}: diff={diff:+.3f}, SE={se:.4f}, 95% CI=[{diff-ci_half:+.3f}, "
          f"{diff+ci_half:+.3f}], p={p:.3f}")
    # what magnitude of difference would be "just excluded" at 95%?
    print(f"  -> smallest |true difference| this test would flag as "
          f"significant at alpha=0.05: {ci_half:.4f}")

print()
print("Corrected interpretation (POD7 vs POD30):")
print("- No statistically detectable difference (95% CI includes 0).")
print("- Under this unpaired approximation, the data ARE compatible with")
print("  true differences up to about 0.010 in magnitude.")
print("- A true difference as large as 0.020 (the POD1-to-POD7 magnitude)")
print("  falls OUTSIDE this interval and would, under this same unpaired")
print("  method, be flagged as inconsistent with the data -- the opposite")
print("  of what round-1 text claimed.")
print("- Whether a 0.01 RI difference is clinically or mechanistically")
print("  meaningful is a separate, unresolved question.")
