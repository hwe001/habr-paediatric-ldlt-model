"""
Regenerates the scenario-comparison and diameter-sensitivity figures using
the dimensionally-consistent model (ldlt_habr_consistent_units.py).
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

MEASURED_SD = {
    "POD1":  {"PSV_HA": 16.02, "RI_HA": 0.05},
    "POD7":  {"PSV_HA": 10.05, "RI_HA": 0.03},
    "POD14": {"PSV_HA": 10.38, "RI_HA": 0.05},
    "POD30": {"PSV_HA": 7.63,  "RI_HA": 0.01},
}
MEASURED_PSV = {"POD1": 53.10, "POD7": 47.02, "POD14": 42.29, "POD30": 38.51}
MEASURED_RI = {"POD1": 0.61, "POD7": 0.59, "POD14": 0.59, "POD30": 0.59}
day = {"POD1": 1, "POD7": 7, "POD14": 14, "POD30": 30}
labels = ["POD1", "POD7", "POD14", "POD30"]
xt = [day[l] for l in labels]

psv_continuous = {"POD1": 53.10, "POD7": 52.43, "POD14": 50.94, "POD30": 49.41}
ri_continuous = {"POD1": 0.610, "POD7": 0.611, "POD14": 0.614, "POD30": 0.617}
psv_frozen = {"POD1": 53.10, "POD7": 52.43, "POD14": 52.50, "POD30": 52.57}
ri_frozen = {"POD1": 0.610, "POD7": 0.611, "POD14": 0.610, "POD30": 0.610}
psv_null = {"POD1": 53.10, "POD7": 53.13, "POD14": 53.20, "POD30": 53.27}
ri_null = {"POD1": 0.610, "POD7": 0.610, "POD14": 0.609, "POD30": 0.608}

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

for name, psv, style, color in [
    ("Continuous", psv_continuous, "s--", "tab:orange"),
    ("Acute-then-frozen", psv_frozen, "D-.", "tab:blue"),
    ("Null (no HABR)", psv_null, "^:", "tab:red"),
]:
    axes[0].plot(xt, [psv[l] for l in labels], style, color=color, label=name)
axes[0].errorbar(xt, [MEASURED_PSV[l] for l in labels],
                  yerr=[MEASURED_SD[l]["PSV_HA"] for l in labels],
                  fmt="o-", color="black", label="Measured", capsize=3, zorder=5)
axes[0].set_xlabel("Postoperative day")
axes[0].set_ylabel("Hepatic artery PSV (cm/s)")
axes[0].set_title("(a) Peak systolic velocity")
axes[0].legend(fontsize=7.5)

for name, ri, style, color in [
    ("Continuous", ri_continuous, "s--", "tab:orange"),
    ("Acute-then-frozen", ri_frozen, "D-.", "tab:blue"),
    ("Null (no HABR)", ri_null, "^:", "tab:red"),
]:
    axes[1].plot(xt, [ri[l] for l in labels], style, color=color, label=name)
axes[1].errorbar(xt, [MEASURED_RI[l] for l in labels],
                  yerr=[MEASURED_SD[l]["RI_HA"] for l in labels],
                  fmt="o-", color="black", label="Measured", capsize=3, zorder=5)
axes[1].set_xlabel("Postoperative day")
axes[1].set_ylabel("Hepatic artery RI")
axes[1].set_title("(b) Resistive index")
axes[1].legend(fontsize=7.5)

fig.suptitle("Three HABR-application scenarios vs. measured "
              "(dimensionally-consistent model)")
fig.tight_layout()
fig.savefig("HABR_Figure_4_three_scenarios_consistent.png", dpi=200)
plt.close(fig)
print("Saved: HABR_Figure_4_three_scenarios_consistent.png")

# diameter sensitivity, corrected model
growth_pct = np.array([0, 10, 20, 30, 40])
frac_explained_pod30 = np.array([25.3, -9.1, -44.3, -79.7, -114.8])

fig, ax = plt.subplots(figsize=(6.2, 4.3))
ax.plot(growth_pct, frac_explained_pod30, "o-", color="tab:red")
ax.axhline(0, color="black", lw=0.8)
ax.set_xlabel("Assumed portal-vein diameter growth by POD30 (%)")
ax.set_ylabel("% of measured PSV_HA decline\nreproduced (continuous scenario, POD30)")
ax.set_title("Sensitivity to the untested diameter-growth\nassumption "
              "(dimensionally-consistent model)")
ax.annotate("assumption used\nin the main analysis\n(0% growth)",
            xy=(0, 25.3), xytext=(14, -60),
            arrowprops=dict(arrowstyle="->", lw=1))
ax.set_ylim(-130, 40)
fig.tight_layout()
fig.savefig("HABR_Figure_7_diameter_sensitivity_consistent.png", dpi=200)
plt.close(fig)
print("Saved: HABR_Figure_7_diameter_sensitivity_consistent.png")
