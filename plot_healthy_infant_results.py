"""
Figures for the generic healthy/paediatric hepatic circulation model
(pi_filter_healthy_infant_model.py), for the write-up doc.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from pi_filter_healthy_infant_model import build_params, simulate, TARGETS

params = build_params()
res = simulate(params)

t = res["t"]

# --- Figure 1: model schematic ---
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.axis("off")


def box(x, y, w, h, label, fc="#eef3fb"):
    rect = plt.Rectangle((x, y), w, h, facecolor=fc, edgecolor="black", zorder=2)
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=9,
             zorder=3)


def arrow(x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="->", lw=1.4, color="black"))


box(0.02, 0.62, 0.16, 0.14, "HA source\n(AC+DC)")
box(0.02, 0.20, 0.16, 0.14, "PV source\n(DC)")
box(0.24, 0.62, 0.20, 0.14, "HA pi-filter\nL,Rs,C,Rp")
box(0.24, 0.20, 0.20, 0.14, "PV pi-filter\nL,Rs,C,Rp")
box(0.50, 0.41, 0.18, 0.16, "Sinusoidal\nnode  P_sinus")
box(0.74, 0.41, 0.20, 0.16, "HV pi-filter\nL,Rs,C,Rp")

arrow(0.18, 0.69, 0.24, 0.69)
arrow(0.18, 0.27, 0.24, 0.27)
arrow(0.44, 0.69, 0.50, 0.50)
arrow(0.44, 0.27, 0.50, 0.44)
arrow(0.68, 0.49, 0.74, 0.49)
ax.text(0.985, 0.49, "IVC\n(ref.)", ha="left", va="center", fontsize=9)
arrow(0.94, 0.49, 0.985, 0.49)

ax.set_xlim(0, 1.05)
ax.set_ylim(0.1, 0.85)
ax.set_title("Generic healthy/paediatric hepatic circulation model "
              "(pi-filter lumped elements)", fontsize=10)
fig.tight_layout()
fig.savefig("HealthyInfant_Figure_1_schematic.png", dpi=200)
plt.close(fig)

# --- Figure 2: flow waveforms ---
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].plot(t, res["Q_HA"] * 60, label="HA", color="tab:green")
axes[0].plot(t, res["Q_PV"] * 60, label="PV", color="black")
axes[0].plot(t, res["Q_HV"] * 60, label="HV", color="black", linestyle="--")
axes[0].set_xlabel("Time within cardiac cycle (s)")
axes[0].set_ylabel("Flow rate (mL/min)")
axes[0].set_title("(a) Simulated flow")
axes[0].legend()

axes[1].axhline(TARGETS["P_PV_src"], color="black", linestyle=":", lw=1,
                 label="PV source (const.)")
# t spans one period; reconstruct the same phase convention used in simulate()
period = t[-1] + (t[1] - t[0])
p_ha_src = TARGETS["P_HA_src_mean"] + TARGETS["P_HA_src_amp"] * np.sin(2 * np.pi * t / period)
axes[1].plot(t, p_ha_src, label="HA source (AC+DC)", color="tab:green")
axes[1].plot(t, res["P_sinus"], label="Sinusoid", color="tab:blue", linestyle="-.")
axes[1].plot(t, res["P_hv"], label="HV", color="tab:orange", linestyle="--")
axes[1].set_xlabel("Time within cardiac cycle (s)")
axes[1].set_ylabel("Pressure (mmHg)")
axes[1].set_title("(b) Simulated pressure")
axes[1].legend(fontsize=8)

fig.tight_layout()
fig.savefig("HealthyInfant_Figure_2_waveforms.png", dpi=200)
plt.close(fig)

# --- Figure 3: simulated vs target bar comparison ---
labels = ["Q_PV\n(mL/min)", "Q_HA\n(mL/min)", "Q_HV\n(mL/min)"]
sim_vals = [res["Q_PV_mean_mLmin"], res["Q_HA_mean_mLmin"], res["Q_HV_mean_mLmin"]]
target_vals = [TARGETS["Q_PV_mean"], TARGETS["Q_HA_mean"], TARGETS["Q_HV_mean"]]

fig, ax = plt.subplots(figsize=(6, 4.2))
x = np.arange(len(labels))
w = 0.35
ax.bar(x - w / 2, target_vals, w, label="Real target (Ho/Yu/Bartlett)", color="#888888")
ax.bar(x + w / 2, sim_vals, w, label="Simulated (this model)", color="tab:blue")
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylabel("Mean flow (mL/min)")
ax.set_title("Simulated vs. real target mean flows")
ax.set_ylim(0, max(max(target_vals), max(sim_vals)) * 1.25)
ax.legend()
for xi, (tv, sv) in enumerate(zip(target_vals, sim_vals)):
    ax.text(xi, max(tv, sv) + 12, f"{sv:.1f}\n({100*(sv-tv)/tv:+.1f}%)",
            ha="center", fontsize=8)
fig.tight_layout()
fig.savefig("HealthyInfant_Figure_3_comparison.png", dpi=200)
plt.close(fig)

print("Saved: HealthyInfant_Figure_1_schematic.png, "
      "HealthyInfant_Figure_2_waveforms.png, "
      "HealthyInfant_Figure_3_comparison.png")

print("\nSummary for the doc:")
print(f"Q_PV: sim={res['Q_PV_mean_mLmin']:.2f} target={TARGETS['Q_PV_mean']:.2f}")
print(f"Q_HA: sim={res['Q_HA_mean_mLmin']:.2f} target={TARGETS['Q_HA_mean']:.2f}")
print(f"Q_HV: sim={res['Q_HV_mean_mLmin']:.2f} target={TARGETS['Q_HV_mean']:.2f}")
print(f"P_sinus: sim={np.mean(res['P_sinus']):.3f} target={TARGETS['P_sinus']:.3f}")
print(f"P_hv: sim={np.mean(res['P_hv']):.3f} target={TARGETS['P_hv']:.3f}")
print(f"HA flow range: {res['Q_HA'].min()*60:.2f} - {res['Q_HA'].max()*60:.2f} mL/min")
print(f"PV flow range: {res['Q_PV'].min()*60:.2f} - {res['Q_PV'].max()*60:.2f} mL/min")
print(f"HV flow range: {res['Q_HV'].min()*60:.2f} - {res['Q_HV'].max()*60:.2f} mL/min")
