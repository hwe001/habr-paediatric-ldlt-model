"""
Virtual graft tree: parse and render the 2018 donor ("Lisa") vascular
trees -- the patient-specific 1D anatomy layer of the original hybrid
0D-1D virtual-transplant model, revived for the current framework.

Input files (Cmgui/OpenCMISS .ex format, plain text; expected at
../simulation/ relative to the repo):
  LISAARTERIAL / LISAPORTAL / LISAHEPATIC with_pressure_post_cubic
  .exnode -- per node: Flow, Strahler order, coordinates (cubic Hermite:
  value + d/ds1), radius. 9 stored values per node; we keep the 6
  non-derivative ones.
  .exelem  -- 1D line elements (2 nodes each, c.Hermite geometry,
  l.Lagrange fields); we keep the connectivity only (rendering uses
  straight segments; the cubic midpoint correction is negligible at tree
  scale and the 2018 rendered geometry (arterial_tree_simulation.png)
  confirms the straight-segment representation).

Outputs:
  virtual_graft_trees.png -- 3D rendering: one combined virtual-graft
  view plus per-tree panels, colored by flow (log scale), line width by
  radius. This is the anatomy layer for the manuscript's "virtual
  surgery" framing; the 1D Poiseuille solve coupled to the pi-filter 0D
  circuit (the restored hybrid) is the natural next step and reuses this
  parser.

Flow units: mL/s or mL/min as solved in 2018 -- reported, not assumed;
the roots' stored flows are printed for cross-checking against the
compendium (e.g. LPV flow 193.8 mL/min, Section 4.1).
"""

import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

TREES = [
    ("arterial", "../simulation/LISAARTERIALwith_pressure_post_cubic",
     "#b22222"),
    ("portal", "../simulation/LISAPORTALwith_pressure_post_cubic",
     "#7b2d8b"),
    ("hepatic venous", "../simulation/LISAHEPATICwith_pressure_post_cubic",
     "#1f5fa6"),
]


def parse_exnode(path):
    """Return dict node_id -> (flow, strahler, x, y, z, radius)."""
    nodes = {}
    cur = None
    vals = []
    with open(path) as f:
        for line in f:
            m = re.match(r"\s*Node:\s*(\d+)", line)
            if m:
                if cur is not None:
                    nodes[cur] = vals
                cur = int(m.group(1))
                vals = []
                continue
            if cur is not None:
                # derivative pairs share a line with their value; collect
                # all floats, then keep indices 0,1,2,4,6,8 (flow,
                # strahler, x, y, z, radius)
                vals.extend(float(t) for t in re.findall(
                    r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", line))
    if cur is not None:
        nodes[cur] = vals
    out = {}
    for nid, v in nodes.items():
        if len(v) >= 9:
            out[nid] = dict(flow=v[0], strahler=v[1], xyz=v[2:5],
                            radius=v[8])
    return out


def parse_exelem(path):
    """Return list of (node_a, node_b) connectivity pairs. Element lines
    are indented (' Element: 20001 0 0'); the node pair follows on the
    line after 'Nodes:'."""
    pairs = []
    lines = open(path).read().splitlines()
    i = 0
    while i < len(lines):
        if re.match(r"\s*Element:", lines[i]):
            j = i + 1
            while j < len(lines) and "Nodes" not in lines[j]:
                j += 1
            if j + 1 < len(lines):
                nums = [int(t) for t in re.findall(r"\d+", lines[j + 1])]
                nums = [n for n in nums if n > 0]
                if len(nums) >= 2:
                    pairs.append((nums[0], nums[1]))
                    i = j + 2
                    continue
            i = j
        i += 1
    return pairs


def tree_arrays(prefix):
    nodes = parse_exnode(prefix + ".exnode")
    elems = parse_exelem(prefix + ".exelem")
    return nodes, elems


if __name__ == "__main__":
    from matplotlib.colors import LogNorm

    data = {}
    print("=== Parsed trees (../simulation) ===")
    for name, prefix, color in TREES:
        nodes, elems = tree_arrays(prefix)
        flows = np.array([n["flow"] for n in nodes.values()])
        radii = np.array([n["radius"] for n in nodes.values()])
        root_id = max(nodes, key=lambda k: nodes[k]["radius"])
        data[name] = (nodes, elems, color)
        print(f"{name:>14}: {len(nodes)} nodes, {len(elems)} elements | "
              f"flow range {flows.min():.3g}..{flows.max():.3g} | "
              f"max radius {radii.max():.3g} | root node {root_id} "
              f"(r={nodes[root_id]['radius']:.3g}, "
              f"flow={nodes[root_id]['flow']:.4g}, "
              f"Strahler={nodes[root_id]['strahler']:.0f})")

    # ---- figure: combined virtual-graft view + per-tree panels -----------
    fig = plt.figure(figsize=(13, 5.2))
    ax0 = fig.add_subplot(1, 4, 1, projection="3d")
    ax0.set_title("Virtual graft (combined)", fontsize=10)
    panels = {name: fig.add_subplot(1, 4, i + 2, projection="3d")
              for i, (name, _, _) in enumerate(TREES)}

    for name, prefix, color in TREES:
        nodes, elems, color = data[name]
        fl = np.array([nodes[a]["flow"] for a, b in elems])
        rd = np.array([max(nodes[a]["radius"], nodes[b]["radius"])
                       for a, b in elems])
        lw = 0.4 + 4.0 * (rd / rd.max())
        norm = LogNorm(vmin=max(fl[fl > 0].min(), 1e-6), vmax=fl.max())
        ax_tree = panels[name]
        for k, (a, b) in enumerate(elems):
            xs = [nodes[a]["xyz"][0], nodes[b]["xyz"][0]]
            ys = [nodes[a]["xyz"][1], nodes[b]["xyz"][1]]
            zs = [nodes[a]["xyz"][2], nodes[b]["xyz"][2]]
            alpha = 0.5 + 0.5 * float(norm(fl[k]))
            ax0.plot(xs, ys, zs, color=color, lw=lw[k], alpha=alpha)
            ax_tree.plot(xs, ys, zs, color=color, lw=lw[k], alpha=alpha)
        ax_tree.set_title(name, fontsize=10)
        ax_tree.set_axis_off()
    ax0.set_axis_off()
    legend = [Line2D([0], [0], color=c, lw=3, label=n)
              for n, _, c in TREES]
    ax0.legend(handles=legend, loc="upper left", fontsize=8)
    fig.suptitle("Virtual graft: donor vascular trees (2018 patient-specific "
                 "case, flows solved; colour = tree, width = radius, "
                 "opacity = flow)", fontsize=10)
    fig.tight_layout()
    fig.savefig("virtual_graft_trees.png", dpi=150)
    print("\nFigure saved: virtual_graft_trees.png")
    print("Next step option: 1D Poiseuille solve on these trees coupled to "
          "the pi-filter 0D circuit (the restored 0D-1D hybrid) reusing "
          "this parser.")
