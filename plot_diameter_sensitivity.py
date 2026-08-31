"""
Figure: how much the "% of measured PSV_HA decline explained by HABR"
result at POD30 depends on the untested assumption that portal-vein
diameter does not grow from POD1 to POD30 (Chen et al. 2022 report
diameter only at pre-transplant and POD1).
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

growth_pct = np.array([0, 10, 20, 30, 40])
frac_explained_pod30 = np.array([30.6, -11.2, -55.7, -102.0, -148.7])

fig, ax = plt.subplots(figsize=(6.2, 4.3))
ax.plot(growth_pct, frac_explained_pod30, "o-", color="tab:red")
ax.axhline(0, color="black", lw=0.8)
ax.set_xlabel("Assumed portal-vein diameter growth by POD30 (%)")
ax.set_ylabel("% of measured PSV_HA decline\nreproduced by HABR (POD30)")
ax.set_title("Sensitivity of the headline result to an\nuntested diameter-growth assumption")
ax.annotate("assumption used\nin the main analysis\n(0% growth)",
            xy=(0, 30.6), xytext=(14, -20),
            arrowprops=dict(arrowstyle="->", lw=1))
ax.set_ylim(-160, 45)
fig.tight_layout()
fig.savefig("HABR_Figure_7_diameter_sensitivity.png", dpi=200)
plt.close(fig)
print("Saved: HABR_Figure_7_diameter_sensitivity.png")
