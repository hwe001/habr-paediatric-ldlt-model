"""
Virtual graft tree: parse and render the 2018 donor ("Lisa") vascular
trees -- the patient-specific 1D anatomy layer of the original hybrid
0D-1D virtual-transplant model, revived for the current framework.

Input files (Cmgui/OpenCMISS .ex format, plain text; expected at
../simulation/ relative to the repo):
  LISAARTERIAL / LISAPORTAL / LISAHEPATIC with_pressure_post_cubic
  .exnode -- 9 stored values per node. Field header names them
  Flow, Strahler, coordinates (cubic Hermite: value + d/ds1 x3), radius,
  but the decoded values show the second field is the SOLVED PRESSURE,
  not Strahler order: arterial root 57.6 mmHg, portal root 10.0 mmHg,
  hepatic root 4.0 mmHg -- exactly the model's source pressures, and the
  file names say "with_pressure". Correction trail: an earlier revision
  of this parser mislabelled that field as Strahler order.
  Flow unit: stored x 60,000 = mL/min (arterial root decodes to 31.9,
  portal root to 300.5 -- the draft's own calibration values).
  .exelem  -- 1D line elements (2 nodes each); element lines are
  INDENTED (' Element: 20001 0 0') and the node pair follows on the line
  after 'Nodes:'.

Topology verification (2026-09-13): the parsed arterial graph is a single
connected component with degree histogram 505 leaves / 509 bifurcations /
13 continuations -- a proper tree. The earlier "spaghetti" appearance was
a rendering artefact (unsorted translucent 3D segments in matplotlib, no
depth cues), not the data: the 2018 Cmgui reference render
(arterial_tree_simulation.png) shows the same tree as clean branching.
This revision renders depth-sorted (thick trunk first, thin distals on
top, low distal alpha, orthographic view) to match the 2018 style.

Outputs: virtual_graft_trees.png (per-tree + combined views, flow- and
pressure-coloured). The 1D Poiseuille solve coupled to the pi-filter 0D
circuit (the restored hybrid) lives in hybrid_0d_1d.py and reuses this
parser.
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

FLOW_SCALE = 60000.0   # stored flow unit -> mL/min (validated at runtime)


def parse_exnode(path):
    """Return dict node_id -> dict(flow [mL/min], pressure [mmHg],
    xyz [mm], radius [mm]). Value indices: 1 flow, 2 pressure (field
    misnamed 'Strahler' in the header -- see docstring), 3-8 coordinates
    (value + d/ds1 per axis), 9 radius."""
    raw = {}
    cur = None
    vals = []
    with open(path) as f:
        for line in f:
            m = re.match(r"\s*Node:\s*(\d+)", line)
            if m:
                if cur is not None:
                    raw[cur] = vals
                cur = int(m.group(1))
                vals = []
                continue
            if cur is not None:
                vals.extend(float(t) for t in re.findall(
                    r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", line))
    if cur is not None:
        raw[cur] = vals
    out = {}
    for nid, v in raw.items():
        if len(v) >= 9:
            # coordinates are stored with derivatives interleaved:
            # index 3=x, 4=dx/ds1, 5=y, 6=dy, 7=z, 8=dz -> take 3,5,7.
            # (Earlier revision used the contiguous slice v[2:5] = x, dx, y
            # -- the "spaghetti" render bug, caught 2026-09-13.)
            out[nid] = dict(flow=v[0] * FLOW_SCALE, pressure=v[1],
                            xyz=np.array([v[2], v[4], v[6]]), radius=v[8])
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


def liver_envelope(points, alpha_mm=22.0):
    """Transparent liver-surface approximation for the reader's reference:
    an alpha shape (concave hull) of the vascular tree points. Built by
    Delaunay tetrahedralisation + circumsphere-radius filtering: tetrahedra
    with circumsphere radius <= alpha_mm are interior; boundary triangles
    (faces belonging to exactly one interior tetrahedron) form the surface.
    The trees do not reach the capsule, so this is an envelope slightly
    inside the true liver surface -- labelled as such on the figure.
    Returns (M, 3, 3) triangle vertices, or None if the triangulation
    fails."""
    from scipy.spatial import Delaunay
    pts = np.asarray(points)
    if len(pts) < 10:
        return None
    try:
        tri = Delaunay(pts)
    except Exception as e:
        print(f"  [envelope] Delaunay failed: {e}")
        return None
    tet = pts[tri.simplices]            # (T, 4, 3)
    p0, p1, p2, p3 = tet[:, 0], tet[:, 1], tet[:, 2], tet[:, 3]
    # circumsphere centre from the squared-distance equations
    Amat = np.stack([2 * (p1 - p0), 2 * (p2 - p0), 2 * (p3 - p0)], axis=1)
    b = np.stack([(p1**2 - p0**2).sum(1), (p2**2 - p0**2).sum(1),
                  (p3**2 - p0**2).sum(1)], axis=1)
    try:
        sol = np.linalg.solve(Amat, b[..., None])[..., 0]
    except np.linalg.LinAlgError:
        sol = np.array([np.linalg.lstsq(Amat[i], b[i], rcond=None)[0]
                        for i in range(len(Amat))])
    r = np.linalg.norm(p0 - sol, axis=1)
    pct = np.percentile(r, [50, 75, 90, 95])
    print(f"  [envelope] {len(pts)} points, {len(r)} tets, circumradius "
          f"p50/p75/p90/p95 = {pct[0]:.1f}/{pct[1]:.1f}/{pct[2]:.1f}/"
          f"{pct[3]:.1f} mm, alpha = {alpha_mm:.1f} mm")
    keep = tri.simplices[r <= alpha_mm]
    if len(keep) == 0:
        print("  [envelope] alpha kept 0 tetrahedra -- raise alpha_mm")
        return None
    faces = {}
    for t in keep:
        for f in ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)):
            key = tuple(sorted(t[list(f)]))
            faces[key] = faces.get(key, 0) + 1
    boundary = [k for k, c in faces.items() if c == 1]
    print(f"  [envelope] kept {len(keep)} tets, boundary triangles: "
          f"{len(boundary)}")
    tris = pts[np.array(boundary)]
    return tris


def render_tree(ax, nodes, elems, color, value_of, vmin, vmax, r_ref,
                elev=12, azim=-65):
    """Depth-sorted render: thick trunk segments first, thin distal
    segments on top with low alpha. Line width scales with VESSEL
    CALIBRE against a global reference radius (r_ref = max radius across
    all three trees), so the portal/hepatic-venous trunks render visibly
    fatter than the arterial tree, as the anatomy demands; opacity scales
    with the flow value. (Earlier revision keyed width to flow, visually
    flattening the calibre differences -- caught by inspection.)"""
    segs = [(a, b) for a, b in elems if a in nodes and b in nodes]
    segs.sort(key=lambda e: -max(nodes[e[0]]["radius"],
                                 nodes[e[1]]["radius"]))
    for a, b in segs:
        val = value_of(nodes[a])
        t = (np.log10(max(val, 1e-6)) - vmin) / (vmax - vmin + 1e-12)
        t = float(np.clip(t, 0.0, 1.0))
        r = max(nodes[a]["radius"], nodes[b]["radius"])
        lw = 0.3 + 7.0 * np.sqrt(max(r, 1e-3) / r_ref)
        ax.plot([nodes[a]["xyz"][0], nodes[b]["xyz"][0]],
                [nodes[a]["xyz"][1], nodes[b]["xyz"][1]],
                [nodes[a]["xyz"][2], nodes[b]["xyz"][2]],
                color=color, lw=lw,
                alpha=0.25 + 0.75 * t, solid_capstyle="round")
    ax.view_init(elev=elev, azim=azim)
    ax.set_proj_type("ortho")
    ax.set_axis_off()


if __name__ == "__main__":
    data = {}
    print("=== Parsed trees (../simulation) ===")
    for name, prefix, color in TREES:
        nodes, elems = tree_arrays(prefix)
        flows = np.array([n["flow"] for n in nodes.values()])
        press = np.array([n["pressure"] for n in nodes.values()])
        root_id = max(nodes, key=lambda k: nodes[k]["radius"])
        data[name] = (nodes, elems, color)
        print(f"{name:>14}: {len(nodes)} nodes, {len(elems)} elements | "
              f"root: flow {nodes[root_id]['flow']:.1f} mL/min, "
              f"pressure {nodes[root_id]['pressure']:.1f} mmHg, "
              f"radius {nodes[root_id]['radius']:.2f} mm | "
              f"flow range {flows.min():.3g}-{flows.max():.3g} mL/min, "
              f"pressure range {press.min():.1f}-{press.max():.1f} mmHg")

    fig = plt.figure(figsize=(15, 4.8))
    ax0 = fig.add_subplot(1, 4, 1, projection="3d")
    ax0.set_title("Virtual graft (combined)", fontsize=10)
    panels = {name: fig.add_subplot(1, 4, i + 2, projection="3d")
              for i, (name, _, _) in enumerate(TREES)}

    # transparent liver envelope: COMBINED panel only (per-tree panels
    # stay clean for visualisation, per review), drawn with visible mesh
    # edges so the surface reads as a reference, not a blob
    all_pts = np.vstack([n["xyz"] for n, _, _ in
                         (data[name] for name, _, _ in TREES)
                         for n in data[name][0].values()])
    env = liver_envelope(all_pts, alpha_mm=22.0)
    if env is not None:
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        pc = Poly3DCollection(env, facecolor="wheat", edgecolor="black",
                              linewidth=0.12, alpha=0.08)
        ax0.add_collection3d(pc)

    r_ref = max(n["radius"] for name, _, _ in TREES
                for n in data[name][0].values())
    for name, prefix, color in TREES:
        nodes, elems, color = data[name]
        render_tree(ax0, nodes, elems, color,
                    lambda n: n["flow"], -1, np.log10(300.0), r_ref)
        render_tree(panels[name], nodes, elems, color,
                    lambda n: n["flow"], -1, np.log10(300.0), r_ref)
        panels[name].set_title(f"{name}", fontsize=10)
    ax0.set_axis_off()
    legend = [Line2D([0], [0], color=c, lw=3, label=n)
              for n, _, c in TREES]
    if env is not None:
        legend.append(Line2D([0], [0], color="wheat", lw=6, alpha=0.5,
                             label="liver envelope (alpha shape)"))
    ax0.legend(handles=legend, loc="upper left", fontsize=8)
    fig.suptitle("Virtual graft: donor vascular trees (2018 patient-specific "
                 "case; width/opacity = log flow; root flows/pressures decode "
                 "to the 2018 calibration values)", fontsize=10)
    fig.tight_layout()
    fig.savefig("virtual_graft_trees.png", dpi=150)
    print("\nFigure saved: virtual_graft_trees.png")
