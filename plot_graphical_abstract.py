"""
Graphical abstract for the Medical Engineering & Physics submission:
model -> two structural uncertainty analyses -> conclusion.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure(figsize=(11, 4.6))
gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.1, 1.1], wspace=0.4,
                       top=0.72, bottom=0.14, left=0.05, right=0.98)

# --- Panel 1: schematic summary ---
ax0 = fig.add_subplot(gs[0])
ax0.axis("off")
ax0.set_title("Dimensionally-consistent\npi-filter model", fontsize=10, fontweight="bold")


def box(ax, x, y, w, h, label, fc="#eef3fb"):
    ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=fc, edgecolor="black", zorder=2))
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=8)


def arrow(ax, x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="black"))


box(ax0, 0.05, 0.62, 0.38, 0.16, "HA\n(mL/s)")
box(ax0, 0.05, 0.20, 0.38, 0.16, "PV\n(mL/s)")
box(ax0, 0.55, 0.41, 0.4, 0.18, "Shared\nsinusoid")
arrow(ax0, 0.43, 0.70, 0.55, 0.53)
arrow(ax0, 0.43, 0.28, 0.55, 0.46)
ax0.text(0.5, 0.05, "HABR: fixed-coefficient\nresistance update",
          ha="center", fontsize=8, style="italic")
ax0.set_xlim(0, 1)
ax0.set_ylim(0, 1)

# --- Panel 2: identifiability envelope (minor uncertainty) ---
ax1 = fig.add_subplot(gs[1])
p_amp = [24, 30, 36, 42, 48, 54, 60]
frac = [27.1, 24.3, 22.7, 21.7, 21.0, 20.6, 20.2]
ax1.plot(p_amp, frac, "o-", color="tab:purple")
ax1.set_title("Parameter non-identifiability:\nnarrow envelope (20-27%)",
               fontsize=9.5, fontweight="bold", color="tab:purple")
ax1.set_xlabel("Explored P_HA_amp (mmHg)", fontsize=8)
ax1.set_ylabel("% of decline reproduced", fontsize=8)
ax1.set_ylim(15, 30)
ax1.tick_params(labelsize=7)

# --- Panel 3: calibre-growth sensitivity (dominant uncertainty) ---
ax2 = fig.add_subplot(gs[2])
grid = np.array([[25.3, 84.1, 128.8], [-9.1, 55.7, 104.9], [-44.2, 26.6, 80.5]])
im = ax2.imshow(grid, cmap="RdBu_r", vmin=-130, vmax=130, origin="lower")
ax2.set_xticks(range(3)); ax2.set_xticklabels(["0%", "10%", "20%"], fontsize=7)
ax2.set_yticks(range(3)); ax2.set_yticklabels(["0%", "10%", "20%"], fontsize=7)
ax2.set_xlabel("Illustrative HA growth", fontsize=8)
ax2.set_ylabel("Illustrative PV growth", fontsize=8)
ax2.set_title("Vessel-calibre sensitivity:\nwide range, spans opposite sign",
               fontsize=9.5, fontweight="bold", color="tab:red")
for i in range(3):
    for j in range(3):
        ax2.text(j, i, f"{grid[i,j]:.0f}%", ha="center", va="center", fontsize=8)

fig.suptitle("Serial vessel-calibre measurement, not further model fitting, is needed\n"
              "to attribute post-transplant hepatic arterial change to HABR",
              fontsize=11, y=0.99)
fig.savefig("Graphical_Abstract.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("Saved: Graphical_Abstract.png")
