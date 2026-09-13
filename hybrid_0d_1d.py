"""
The restored 0D-1D hybrid: the pi-filter HABR circuit (0D) coupled to the
patient-specific vascular trees (1D) -- the architecture of the original
virtual-transplant draft (Yu et al., 2018; IPCAI submission), rebuilt in
Python on the parsed 2018 trees.

Coupling design (quasi-steady, consistent with the repo's discrete-HABR
philosophy):
- The 1D layer owns SPACE: per-segment Poiseuille resistances from the
  stored radii and coordinates (mu = 3.5 cP, lengths from node
  coordinates, mm), tree-reduced bottom-up to an effective conduit
  resistance per branch; segment flows assigned by subtree conductance
  (all terminals at a common sink pressure).
- The 0D layer owns the ANCHORS and the LAW: the calibrated branch
  resistances (Rs_HA 97.958, Rs_PV 1.526, Rs_HV 0.242 mmHg*s/mL) and the
  Ho 2013 HABR quadratic, as in every other script here.
- Coupling rule: the calibrated total resistance = conduit (tree) +
  microcirculation lump M (the difference). HABR scales M -- the buffer
  response is an arteriolar/sinusoidal-wall phenomenon, not a conduit
  phenomenon -- and the resulting root flow re-solves the tree.

Analyses in this script:
1. Conduit-vs-microcirculation resistance split per branch (how much of
   the calibrated resistance the 2018 tree geometry alone explains).
2. Flow-split validation: the conductance-weighted assignment vs the
   2018 Simulink flows stored in the tree files (scale: stored x 60000 =
   mL/min; the arterial and portal roots decode to exactly 31.9 / 300.5
   mL/min -- the draft's own calibration values).
3. Two virtual-surgery scenarios on the arterial tree, rendered:
   (a) HABR constriction (transplant-step portal surge, classical
       direction: changeIpv = -99.4% -> changeIha = -47.6% -> root flow
       x0.524; microcirculation uniformly constricted);
   (b) virtual resection: the largest distal subtree removed -- the
       flow re-routes through the remaining tree (non-uniform), the
       spatial story the 0D model alone cannot show.

Caveats: straight-segment lengths (cubic midpoints neglected); common
sink pressure at all terminals (the 2018 solve used its own terminal
conditions -- hence the validation is a correlation, not an identity);
HABR distribution across the microcirculation is uniform here (the
heterogeneity comes from resection, not from the buffer response).
"""

import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.setrecursionlimit(100000)

from virtual_graft_tree import parse_exnode, parse_exelem
from ldlt_habr_consistent_units import habr_percent_change, MEASURED
from preop_ba_state import q_pv_preop

MU_CP = 3.5
PA_S_M3_TO_MMHG_S_ML = 7.5003e-9
FLOW_SCALE = 60000.0    # stored flow unit -> mL/min (validated below)
DC_CALIB = dict(Rs_HA=97.9580, Rs_PV=1.5260, Rs_HV=0.2419)


def seg_resistance(l_mm, r_mm):
    r_m, L_m = r_mm * 1e-3, l_mm * 1e-3
    return (8.0 * MU_CP * 1e-3 * L_m / (np.pi * r_m**4)
            * PA_S_M3_TO_MMHG_S_ML)


def build_tree(prefix):
    nodes = parse_exnode(prefix + ".exnode")
    elems = parse_exelem(prefix + ".exelem")
    for v in nodes.values():
        v["xyz"] = np.asarray(v["xyz"])
    adj = {}
    segR = {}
    for a, b in elems:
        if a not in nodes or b not in nodes:
            continue
        L = float(np.linalg.norm(nodes[a]["xyz"] - nodes[b]["xyz"]))
        r = 0.5 * (nodes[a]["radius"] + nodes[b]["radius"])
        R = seg_resistance(L, r)
        segR[(min(a, b), max(a, b))] = R
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    root = max(nodes, key=lambda k: nodes[k]["radius"])
    parent, order = {root: None}, [root]
    for n in order:
        for c in adj.get(n, []):
            if c not in parent:
                parent[c] = n
                order.append(c)

    def segR_of(child):
        p = parent[child]
        return segR[(min(p, child), max(p, child))]

    children = {n: [c for c in adj.get(n, []) if parent.get(c) == n]
                for n in order}
    # bottom-up reduction: R_down(n) = effective resistance from n to the
    # common sink through its subtree
    R_down = {}
    for n in reversed(order):
        kids = children[n]
        R_down[n] = (sum(1.0 / (segR_of(c) + R_down[c]) for c in kids) ** -1
                     if kids else 0.0)

    def assign_flows(root_flow):
        Q = {}
        Q[root] = root_flow
        for n in order:
            kids = children[n]
            if not kids:
                continue
            C = sum(1.0 / (segR_of(c) + R_down[c]) for c in kids)
            for c in kids:
                Q[c] = Q[n] * (1.0 / (segR_of(c) + R_down[c])) / C
        return Q

    return dict(nodes=nodes, elems=elems, adj=adj, parent=parent,
                children=children, order=order, root=root, segR=segR,
                R_down=R_down, assign_flows=assign_flows)


def subtree_nodes(tree, start):
    out, stack = [], [start]
    while stack:
        n = stack.pop()
        out.append(n)
        stack.extend(tree["children"].get(n, []))
    return out


def render(ax, tree, Q, color, vmin, vmax):
    nodes, elems = tree["nodes"], tree["elems"]
    qs = np.array([Q.get(a, 0.0) for a, b in elems])
    norm = np.log10(np.maximum(qs, 1e-3))
    norm = (norm - vmin) / (vmax - vmin + 1e-12)
    for k, (a, b) in enumerate(elems):
        if a not in nodes or b not in nodes:
            continue
        ax.plot([nodes[a]["xyz"][0], nodes[b]["xyz"][0]],
                [nodes[a]["xyz"][1], nodes[b]["xyz"][1]],
                [nodes[a]["xyz"][2], nodes[b]["xyz"][2]],
                color=color, lw=0.4 + 3.5 * norm[k],
                alpha=0.35 + 0.65 * norm[k])


if __name__ == "__main__":
    print("=== 1. Conduit vs microcirculation resistance split ===")
    trees = {}
    for name, prefix, calib in (
            ("arterial", "../simulation/LISAARTERIALwith_pressure_post_cubic",
             "Rs_HA"),
            ("portal", "../simulation/LISAPORTALwith_pressure_post_cubic",
             "Rs_PV"),
            ("hepatic venous",
             "../simulation/LISAHEPATICwith_pressure_post_cubic", "Rs_HV")):
        t = build_tree(prefix)
        trees[name] = t
        conduit = t["R_down"][t["root"]]
        total = DC_CALIB[calib]
        print(f"{name:>14}: conduit R = {conduit:9.4f}  vs calibrated total "
              f"R = {total:9.4f} mmHg*s/mL  -> conduit is "
              f"{100 * conduit / total:5.2f}% of the total "
              f"(micro lump M = {total - conduit:9.4f})")

    print("\n=== 2. Flow-split validation vs the 2018 stored flows ===")
    print("(stored x 60000 = mL/min; conductance-weighted split with common "
          "sink pressure)")
    for name, root_flow_mLmin in (("arterial", 31.93), ("portal", 300.0)):
        t = trees[name]
        Q = t["assign_flows"](root_flow_mLmin)
        stored, model = [], []
        for n, d in t["nodes"].items():
            if n in Q and d["flow"] > 0:
                stored.append(d["flow"] * FLOW_SCALE)
                model.append(Q[n])
        stored, model = np.array(stored), np.array(model)
        r = np.corrcoef(np.log10(stored), np.log10(model))[0, 1]
        ratio = np.median(model / stored)
        print(f"{name:>14}: n={len(stored)}, log-log r = {r:.3f}, "
              f"median model/stored = {ratio:.3f} "
              f"(root stored = {stored.max():.1f} mL/min)")

    print("\n=== 3. Virtual-surgery scenarios on the arterial tree ===")
    t = trees["arterial"]
    change_Ipv = -99.4    # transplant-step portal surge (Section 22)
    change_Iha = habr_percent_change(change_Ipv)   # -47.6, classical read
    root_flow_base = 31.93
    Q_base = t["assign_flows"](root_flow_base)

    # (a) HABR constriction: micro lump M scaled by 1/(1+changeIha/100)
    #     (classical direction: portal UP -> arterial flow DOWN)
    root_flow_habr = root_flow_base * (1.0 + change_Iha / 100.0)
    Q_habr = t["assign_flows"](root_flow_habr)

    # (b) virtual resection: remove a distal subtree of moderate size.
    # Descend from the root following the largest child until the subtree
    # covers <= 40% of the tree (the trunk children span nearly everything).
    big = t["root"]
    n_total = len(t["nodes"])
    while True:
        kids = t["children"].get(big, [])
        if not kids:
            break
        cand = max(kids, key=lambda c: len(subtree_nodes(t, c)))
        if len(subtree_nodes(t, cand)) <= 0.40 * n_total:
            big = cand
            break
        big = cand
    removed = subtree_nodes(t, big)
    removed_set = set(removed)
    Q_res = t["assign_flows"](root_flow_base)
    removed_flow = Q_res[big]   # flow entering the resected subtree
    rerouted = root_flow_base - removed_flow
    print(f"resected subtree: node {big} ({len(removed)} nodes = "
          f"{100 * len(removed) / n_total:.0f}% of the tree; its flow "
          f"{removed_flow:.2f} mL/min = "
          f"{100 * removed_flow / root_flow_base:.1f}% of baseline "
          f"re-routes through the remaining {100 - 100 * len(removed) / n_total:.0f}%)")
    print(f"HABR scenario: changeIpv={change_Ipv}% -> changeIha="
          f"{change_Iha:.1f}% -> arterial root flow "
          f"{root_flow_base:.2f} -> {root_flow_habr:.2f} mL/min")

    # figure: three panels, drawn inline (colour/width/alpha by log flow)
    qs_all = np.array([Q_base.get(a, 0.0) for a, b in t["elems"]])
    qs_all = qs_all[qs_all > 0]
    vmin, vmax = np.log10(max(qs_all.min(), 1e-4)), np.log10(qs_all.max())
    nodes = t["nodes"]
    fig = plt.figure(figsize=(14, 5.0))
    for i, (title, Q, hide) in enumerate((
            ("baseline (Q_HA = 31.9 mL/min)", Q_base, set()),
            (f"HABR constriction (root x{1 + change_Iha / 100:.3f})",
             Q_habr, set()),
            (f"virtual resection ({len(removed)} nodes removed)",
             Q_res, removed_set))):
        ax = fig.add_subplot(1, 3, i + 1, projection="3d")
        for a, b in t["elems"]:
            if a not in nodes or b not in nodes:
                continue
            if a in hide or b in hide:
                continue
            q = max(Q.get(a, 0.0), 1e-9)
            nrm = (np.log10(q) - vmin) / (vmax - vmin + 1e-12)
            nrm = float(np.clip(nrm, 0.0, 1.0))
            ax.plot([nodes[a]["xyz"][0], nodes[b]["xyz"][0]],
                    [nodes[a]["xyz"][1], nodes[b]["xyz"][1]],
                    [nodes[a]["xyz"][2], nodes[b]["xyz"][2]],
                    color="#b22222", lw=0.4 + 3.5 * nrm,
                    alpha=0.35 + 0.65 * nrm)
        ax.set_title(title, fontsize=9)
        ax.set_axis_off()
    fig.suptitle("0D-1D hybrid: patient-specific arterial tree driven by the "
                 "HABR circuit (colour/width = log flow)", fontsize=10)
    fig.tight_layout()
    fig.savefig("hybrid_0d_1d_scenarios.png", dpi=150)
    print("\nFigure saved: hybrid_0d_1d_scenarios.png")
