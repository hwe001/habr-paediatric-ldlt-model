"""
Figure comparing four trajectories: measured, the old (superseded)
continuously-reapplied-HABR model, the corrected acute-then-frozen model,
and the pure null (no HABR at all).
"""

import csv

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
day = {"POD1": 1, "POD7": 7, "POD14": 14, "POD30": 30}

with open("ldlt_habr_pi_filter_prediction_results.csv") as f:
    old_rows = {r["time"]: r for r in csv.DictReader(f)}
with open("ldlt_habr_pi_filter_null_model_results.csv") as f:
    old_null = {r["time"]: r for r in csv.DictReader(f)}
with open("ldlt_habr_acute_then_frozen_results.csv") as f:
    new_rows = {r["time"]: r for r in csv.DictReader(f)}

labels = ["POD1", "POD7", "POD14", "POD30"]
xt = [day[l] for l in labels]

psv_meas = [float(old_rows[l]["PSV_HA_measured"]) for l in labels]
ri_meas = [float(old_rows[l]["RI_HA_measured"]) for l in labels]
psv_sd = [MEASURED_SD[l]["PSV_HA"] for l in labels]
ri_sd = [MEASURED_SD[l]["RI_HA"] for l in labels]

psv_old = [float(old_rows[l]["PSV_HA_simulated"]) for l in labels]
ri_old = [float(old_rows[l]["RI_HA_simulated"]) for l in labels]

psv_new = [float(new_rows[l]["PSV_HA_acute_then_frozen"]) for l in labels]
ri_new = [float(new_rows[l]["RI_HA_acute_then_frozen"]) for l in labels]

psv_null = [psv_old[0]] + [float(old_null[l]["PSV_HA_null_no_habr"]) for l in labels[1:]]
ri_null = [ri_old[0]] + [float(old_null[l]["RI_HA_null_no_habr"]) for l in labels[1:]]

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

axes[0].errorbar(xt, psv_meas, yerr=psv_sd, fmt="o-", color="black",
                  label="Measured", capsize=3, zorder=5)
axes[0].plot(xt, psv_old, "s--", color="tab:orange",
              label="Old: HABR continuously re-applied")
axes[0].plot(xt, psv_new, "D-.", color="tab:blue",
              label="Corrected: HABR acute (POD1-7), then frozen")
axes[0].plot(xt, psv_null, "^:", color="tab:red", label="Null: no HABR at all")
axes[0].axvline(7, color="gray", lw=0.8, ls=":")
axes[0].set_xlabel("Postoperative day")
axes[0].set_ylabel("Hepatic artery PSV (cm/s)")
axes[0].set_title("(a) Peak systolic velocity")
axes[0].legend(fontsize=7.5)

axes[1].errorbar(xt, ri_meas, yerr=ri_sd, fmt="o-", color="black",
                  label="Measured", capsize=3, zorder=5)
axes[1].plot(xt, ri_old, "s--", color="tab:orange",
              label="Old: HABR continuously re-applied")
axes[1].plot(xt, ri_new, "D-.", color="tab:blue",
              label="Corrected: HABR acute (POD1-7), then frozen")
axes[1].plot(xt, ri_null, "^:", color="tab:red", label="Null: no HABR at all")
axes[1].axvline(7, color="gray", lw=0.8, ls=":")
axes[1].set_xlabel("Postoperative day")
axes[1].set_ylabel("Hepatic artery RI")
axes[1].set_title("(b) Resistive index")
axes[1].legend(fontsize=7.5)

fig.suptitle("Correcting for HABR's acute time course: resistance-driven "
              "change should stop after POD7")
fig.tight_layout()
fig.savefig("HABR_Figure_3_acute_correction.png", dpi=200)
plt.close(fig)
print("Saved: HABR_Figure_3_acute_correction.png")
