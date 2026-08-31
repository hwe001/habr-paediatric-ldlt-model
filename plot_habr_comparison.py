"""
With-HABR vs. without-HABR (null model) comparison figure for the post-LDLT
hepatic arterial trajectory, reading the CSVs produced by
ldlt_habr_on_pi_filter.py.
"""

import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# real cohort SD (Chen et al. 2022, Table 2), for error bars on measured points
MEASURED_SD = {
    "POD1":  {"PSV_HA": 16.02, "RI_HA": 0.05},
    "POD7":  {"PSV_HA": 10.05, "RI_HA": 0.03},
    "POD14": {"PSV_HA": 10.38, "RI_HA": 0.05},
    "POD30": {"PSV_HA": 7.63,  "RI_HA": 0.01},
}

with open("ldlt_habr_pi_filter_prediction_results.csv") as f:
    rows = list(csv.DictReader(f))
with open("ldlt_habr_pi_filter_null_model_results.csv") as f:
    null_rows = list(csv.DictReader(f))

labels = [r["time"] for r in rows]
x = np.arange(len(labels))
day = {"POD1": 1, "POD7": 7, "POD14": 14, "POD30": 30}
xt = [day[l] for l in labels]

psv_meas = [float(r["PSV_HA_measured"]) for r in rows]
psv_sim = [float(r["PSV_HA_simulated"]) for r in rows]
ri_meas = [float(r["RI_HA_measured"]) for r in rows]
ri_sim = [float(r["RI_HA_simulated"]) for r in rows]
psv_null = [psv_sim[0]] + [float(r["PSV_HA_null_no_habr"]) for r in null_rows]
ri_null = [ri_sim[0]] + [float(r["RI_HA_null_no_habr"]) for r in null_rows]
psv_sd = [MEASURED_SD[l]["PSV_HA"] for l in labels]
ri_sd = [MEASURED_SD[l]["RI_HA"] for l in labels]

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

axes[0].errorbar(xt, psv_meas, yerr=psv_sd, fmt="o-", color="black",
                  label="Measured (Chen et al. 2022)", capsize=3)
axes[0].plot(xt, psv_sim, "s--", color="tab:blue", label="Model, HABR ON")
axes[0].plot(xt, psv_null, "^:", color="tab:red", label="Model, HABR OFF (null)")
axes[0].set_xlabel("Postoperative day")
axes[0].set_ylabel("Hepatic artery PSV (cm/s)")
axes[0].set_title("(a) Peak systolic velocity")
axes[0].legend(fontsize=8)

axes[1].errorbar(xt, ri_meas, yerr=ri_sd, fmt="o-", color="black",
                  label="Measured (Chen et al. 2022)", capsize=3)
axes[1].plot(xt, ri_sim, "s--", color="tab:blue", label="Model, HABR ON")
axes[1].plot(xt, ri_null, "^:", color="tab:red", label="Model, HABR OFF (null)")
axes[1].set_xlabel("Postoperative day")
axes[1].set_ylabel("Hepatic artery RI")
axes[1].set_title("(b) Resistive index")
axes[1].legend(fontsize=8)

fig.suptitle("Post-LDLT hepatic arterial trajectory: with vs. without HABR "
              "(anchored at POD1)")
fig.tight_layout()
fig.savefig("HABR_Figure_1_with_without_comparison.png", dpi=200)
plt.close(fig)

# fraction-of-decline bar chart
fig, ax = plt.subplots(figsize=(5.5, 4))
labels3 = ["POD7", "POD14", "POD30"]
measured_decline = [psv_meas[0] - psv_meas[i] for i in (1, 2, 3)]
habr_decline = [psv_sim[0] - psv_sim[i] for i in (1, 2, 3)]
frac = [100 * h / m for h, m in zip(habr_decline, measured_decline)]
xb = np.arange(3)
ax.bar(xb, measured_decline, width=0.35, label="Measured total decline",
       color="#888888")
ax.bar(xb + 0.35, habr_decline, width=0.35, label="Reproduced by HABR alone",
       color="tab:blue")
for i, f in enumerate(frac):
    ax.text(xb[i] + 0.175, measured_decline[i] + 0.3, f"{f:.0f}%",
            ha="center", fontsize=9)
ax.set_xticks(xb + 0.175)
ax.set_xticklabels(labels3)
ax.set_ylabel("PSV_HA decline from POD1 (cm/s)")
ax.set_title("Fraction of the measured decline\nreproduced by HABR alone")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig("HABR_Figure_2_fraction_explained.png", dpi=200)
plt.close(fig)

print("Saved: HABR_Figure_1_with_without_comparison.png, "
      "HABR_Figure_2_fraction_explained.png")
