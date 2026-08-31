"""
Figures for round-3 revision: the POD1-identifiability envelope, and the
2D portal x hepatic-artery diameter-growth sensitivity grid.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# --- Figure 6: identifiability envelope ---
p_amp = [24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60]
frac = [27.1, 26.0, 25.1, 24.3, 23.7, 23.1, 22.7, 22.3, 22.0, 21.7, 21.4, 21.2,
        21.0, 20.8, 20.7, 20.6, 20.4, 20.3, 20.2]

fig, ax = plt.subplots(figsize=(6.2, 4.3))
ax.plot(p_amp, frac, "o-", color="tab:purple")
ax.axhline(25.3, color="gray", lw=0.8, ls="--", label="representative member (used elsewhere, P_amp=27.4)")
ax.set_xlabel("P_HA_amp (mmHg) -- one coordinate of the admissible POD1 family")
ax.set_ylabel("% of measured PSV_HA decline\nreproduced (continuous scenario, POD30)")
ax.set_title("POD1 non-identifiability: envelope across the\nadmissible "
              "(Rs_HA, L_HA, P_HA_amp) family")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig("HABR_Figure_6_identifiability_envelope.png", dpi=200)
plt.close(fig)
print("Saved: HABR_Figure_6_identifiability_envelope.png")

# --- Figure 7 (new numbering): 2D PV x HA diameter-growth grid ---
pv_grid = [0, 10, 20]
ha_grid = [0, 10, 20]
grid = np.array([
    [25.3, 84.1, 128.8],
    [-9.1, 55.7, 104.9],
    [-44.2, 26.6, 80.5],
])

fig, ax = plt.subplots(figsize=(6.0, 5.0))
im = ax.imshow(grid, cmap="RdBu_r", vmin=-130, vmax=130, origin="lower")
ax.set_xticks(range(len(ha_grid)))
ax.set_xticklabels([f"{h}%" for h in ha_grid])
ax.set_yticks(range(len(pv_grid)))
ax.set_yticklabels([f"{p}%" for p in pv_grid])
ax.set_xlabel("Assumed HA diameter growth by POD30")
ax.set_ylabel("Assumed PV diameter growth by POD30")
ax.set_title("% of measured PSV_HA decline reproduced,\nas a joint function "
              "of portal and arterial calibre growth")
for i in range(len(pv_grid)):
    for j in range(len(ha_grid)):
        ax.text(j, i, f"{grid[i,j]:.0f}%", ha="center", va="center",
                 color="black", fontsize=11)
fig.colorbar(im, ax=ax, label="% explained")
fig.tight_layout()
fig.savefig("HABR_Figure_8_2D_diameter_grid.png", dpi=200)
plt.close(fig)
print("Saved: HABR_Figure_8_2D_diameter_grid.png")
