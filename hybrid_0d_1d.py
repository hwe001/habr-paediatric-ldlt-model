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
  resistances (POD1-anchored: Rs_HA 97.958, Rs_PV 2.615, Rs_HV 0.377
  mmHg*s/mL) and the
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

from virtual_graft_tree import parse_exnode, parse_exelem, liver_envelope
from ldlt_habr_consistent_units import habr_percent_change, MEASURED
from preop_ba_state import q_pv_preop
from anastomosis_stenosis_sweep import (
    DC_POD1, POD1_TARGETS, simulate_circuit, stenosis_resistance,
    R_ANAS_PV_0,
)

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


def couple_tree(tree, M_total):
    """Complete the 0D-1D coupling: distribute the calibrated
    microcirculation lump M over the tree's terminals, proportional to
    each terminal's conductance-weighted baseline flow share w_t
    (m_t = M / w_t), so that (i) the coupled effective resistance
    reproduces the calibrated total exactly (to conduit precision), and
    (ii) the validated conductance weighting of the flow split is
    preserved. Returns the per-terminal micro lumps and a solver in
    which the flow split and the effective resistance are consistent
    with each other -- the fixed point of the 0D-1D loop (the circuit is
    linear, so one pass is exact; the loop is run twice to demonstrate
    convergence)."""
    Q_base = tree["assign_flows"](1.0)          # unit-root flow split
    leaves = [n for n in tree["order"] if not tree["children"].get(n)]
    w = {t: Q_base[t] for t in leaves}          # shares sum to 1
    m = {t: M_total / w[t] for t in leaves}

    def solve(m_micro, r_root=0.0):
        """R_eff and flows with micro lumps attached at the terminals.
        r_root adds a resistance to EVERY root-to-terminal path -- a
        per-branch element, NOT a series resistor at the root (a root
        series element carries the total flow and simply adds to the
        returned R_eff; the earlier "electrically exact" claim here was
        wrong and shifted the stenosis thresholds)."""
        R_down = {}
        for n in reversed(tree["order"]):
            kids = tree["children"].get(n, [])
            if not kids:
                R_down[n] = m_micro.get(n, 0.0) + r_root
                continue
            R_down[n] = sum(
                1.0 / (tree["segR"][(min(n, c), max(n, c))] + R_down[c])
                for c in kids) ** -1
        R_eff = R_down[tree["root"]]

        def flows(root_flow):
            Q = {tree["root"]: root_flow}
            for n in tree["order"]:
                kids = tree["children"].get(n, [])
                if not kids:
                    continue
                C = sum(1.0 / (tree["segR"][(min(n, c), max(n, c))]
                               + R_down[c]) for c in kids)
                for c in kids:
                    Q[c] = Q[n] * (1.0 / (tree["segR"][(min(n, c),
                                 max(n, c))] + R_down[c])) / C
            return Q

        # fixed-point loop (linear circuit -> converges in one pass)
        Q = flows(1.0)
        for _ in range(2):
            Q = flows(1.0)
        return R_eff, Q

    def pressures(Q, P_root, P_sink=None):
        """Per-node pressures along the tree given branch flows (used for
        validation against the 2018 stored pressures). The segment
        parent->c carries the branch flow Q[c] (an earlier revision used
        the parent inflow Q[n], overstating bifurcation drops). P_sink is
        accepted for signature clarity but not imposed: terminal
        pressures emerge from the accumulated drops (the micro-lump drops
        are NOT in this walk -- only conduit segment drops -- so terminal
        node pressures sit just below P_root; the lump drops connect them
        to P_sinus)."""
        P = {tree["root"]: P_root}
        for n in tree["order"]:
            for c in tree["children"].get(n, []):
                R = tree["segR"][(min(n, c), max(n, c))]
                P[c] = P[n] - Q.get(c, 0.0) / 60.0 * R   # Q mL/min -> mL/s
        return P

    R_eff, unit_Q = solve(m)
    return dict(m=m, solve=solve, R_eff=R_eff, leaves=leaves, w=w,
                unit_Q=unit_Q, pressures=pressures)


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
                stored.append(d["flow"])  # parser already returns mL/min
                model.append(Q[n])
        stored, model = np.array(stored), np.array(model)
        r = np.corrcoef(np.log10(stored), np.log10(model))[0, 1]
        ratio = np.median(model / stored)
        print(f"{name:>14}: n={len(stored)}, log-log r = {r:.3f}, "
              f"median model/stored = {ratio:.3f} "
              f"(root stored = {stored.max():.1f} mL/min)")

    print("\n=== 3. Coupled 0D-1D circuit: branch resistances from the "
          "trees, Q_PV from the coupled solve ===")
    print("(calibration targets: POD1-anchored DC_POD1 -- the generic "
          "300 mL/min-scale DC_CALIB above is superseded here)\n")
    cp, eff = {}, {}
    for name, key in (("arterial", "Rs_HA"), ("portal", "Rs_PV"),
                      ("hepatic venous", "Rs_HV")):
        t = trees[name]
        conduit = t["R_down"][t["root"]]
        cp[name] = couple_tree(t, DC_POD1[key] - conduit)
        eff[name] = cp[name]["R_eff"]
        print(f"{name:>14}: coupled R_eff = {eff[name]:.4f} vs calibrated "
              f"{DC_POD1[key]:.4f} mmHg*s/mL")

    print("\n--- baseline coupled run (tree-derived branch resistances) ---")
    base = simulate_circuit(eff["arterial"], Rs_PV_override=eff["portal"],
                            Rs_HV_override=eff["hepatic venous"])
    Q_PV_base = base["Q_PV"]
    print(f"Q_PV={base['Q_PV']:.2f} (175.06), Q_HA={base['Q_HA']:.2f} "
          f"(31.93), Q_HV={base['Q_HV']:.2f}, converged={base['converged']}")

    print("\n--- portal-anastomosis stenosis through the TREE, HABR "
          "quasi-steady loop (both sign arms) ---")

    def coupled_sweep_point(s_pct, arm):
        """Portal stenosis enters the tree at the root; the circuit and
        HABR respond; iterate the arterial micro-lump scale k to the
        quasi-steady fixed point."""
        R_anas = stenosis_resistance(s_pct, R_ANAS_PV_0)
        # a root stenosis is a TRUE series element: it adds ONCE to the
        # effective resistance (adding it per terminal path, as an earlier
        # revision did via solve(r_root=...), defines a different network
        # and shifted the tolerance thresholds by ~12 points)
        R_eff_PV = R_anas + cp["portal"]["solve"](cp["portal"]["m"])[0]
        M_HA = DC_POD1["Rs_HA"] - trees["arterial"]["R_down"][
            trees["arterial"]["root"]]
        k = 1.0
        res = None
        for _ in range(15):
            res = simulate_circuit(
                trees["arterial"]["R_down"][trees["arterial"]["root"]]
                + k * M_HA, Rs_PV_override=R_eff_PV,
                Rs_HV_override=eff["hepatic venous"])
            if not res["converged"]:
                return None
            change_Ipv = (Q_PV_base - res["Q_PV"]) / Q_PV_base * 100.0
            if arm == "none" or abs(change_Ipv) < 1e-6:
                break
            changeIha = habr_percent_change(change_Ipv)
            # classical: portal DOWN -> arterial UP -> k = 1/(1+c) < 1
            # canonical: portal DOWN -> arterial DOWN -> k = 1/(1-c) > 1
            k_new = (1.0 / (1.0 + changeIha / 100.0) if arm == "classical"
                     else 1.0 / (1.0 - changeIha / 100.0))
            done = abs(k_new - k) / k < 1e-4
            k = k_new
            if done:
                break
        return dict(s=s_pct, arm=arm, R_eff_PV=R_eff_PV, k=k, res=res)

    arms = ("none", "classical", "canonical")
    grids = {}
    for arm in arms:
        pts = [p for s in np.arange(0, 96, 5)
               if (p := coupled_sweep_point(float(s), arm)) is not None]
        grids[arm] = pts
    base_total = base["Q_HA"] + base["Q_PV"]
    print(f"\n{'arm':>10} {'90% inflow':>11} {'80% inflow':>11} "
          f"(Section 24 series-resistance reference: none 68.2/74.3, "
          f"classical 69.0/75.2, canonical 67.4/73.5)")
    for arm in arms:
        tot = np.array([p["res"]["Q_HA"] + p["res"]["Q_PV"]
                        for p in grids[arm]]) / base_total
        ss = np.array([p["s"] for p in grids[arm]])
        th = []
        for frac in (0.9, 0.8):
            idx = np.argmax(tot < frac) if np.any(tot < frac) else None
            th.append(None if idx is None or idx == 0 else
                      ss[idx - 1] + (tot[idx - 1] - frac) /
                      (tot[idx - 1] - tot[idx]) * (ss[idx] - ss[idx - 1]))
        f = [f"{x:.1f}%" if x is not None else ">95%" for x in th]
        print(f"{arm:>10} {f[0]:>11} {f[1]:>11}")

    print("\n--- portal pressure field vs the 2018 stored pressures ---")
    Q_ours = {n: q * Q_PV_base for n, q in cp["portal"]["unit_Q"].items()}
    P_ours = cp["portal"]["pressures"](Q_ours, P_root=POD1_TARGETS["P_PV_src"])
    stored_drop, our_drop = [], []
    for n, d in trees["portal"]["nodes"].items():
        if n in P_ours:
            stored_drop.append(10.0 - d["pressure"])   # 2018 root was 10 mmHg
            our_drop.append(POD1_TARGETS["P_PV_src"] - P_ours[n])
    stored_drop, our_drop = np.array(stored_drop), np.array(our_drop)
    r_press = np.corrcoef(stored_drop, our_drop)[0, 1]
    print(f"per-node pressure drops (normalised to each solve's total): "
          f"n={len(stored_drop)}, Pearson r = {r_press:.3f}")

    # figure: coupled portal tree at baseline vs stenosis + pressure check
    nodes = trees["portal"]["nodes"]
    r_ref = max(n["radius"] for n in nodes.values())
    s_show = 70.0
    p70 = coupled_sweep_point(s_show, "classical")
    Q70 = {n: q * p70["res"]["Q_PV"] for n, q in cp["portal"]["unit_Q"].items()}
    env = liver_envelope(np.vstack([n["xyz"] for n in nodes.values()]),
                         alpha_mm=22.0)
    fig = plt.figure(figsize=(14, 4.8))
    for i, (title, Q) in enumerate((
            (f"portal tree, baseline (Q_PV = {Q_PV_base:.0f} mL/min)", Q_ours),
            (f"portal anastomosis {s_show:.0f}% stenosis, coupled solve "
             f"(Q_PV = {p70['res']['Q_PV']:.0f} mL/min, HABR k = "
             f"{p70['k']:.2f})", Q70))):
        ax = fig.add_subplot(1, 3, i + 1, projection="3d")
        if env is not None:
            from mpl_toolkits.mplot3d.art3d import Poly3DCollection
            ax.add_collection3d(Poly3DCollection(
                env, facecolor="wheat", edgecolor="black",
                linewidth=0.12, alpha=0.08))
        for a, b in trees["portal"]["elems"]:
            if a not in nodes or b not in nodes:
                continue
            q = max(Q.get(a, 0.0), 1e-9)
            nrm = (np.log10(q) - -1) / (np.log10(300.0) + 1)
            nrm = float(np.clip(nrm, 0.0, 1.0))
            lw = 0.3 + 7.0 * np.sqrt(
                max(nodes[a]["radius"], nodes[b]["radius"]) / r_ref)
            ax.plot([nodes[a]["xyz"][0], nodes[b]["xyz"][0]],
                    [nodes[a]["xyz"][1], nodes[b]["xyz"][1]],
                    [nodes[a]["xyz"][2], nodes[b]["xyz"][2]],
                    color="#7b2d8b", lw=lw, alpha=0.3 + 0.7 * nrm)
        ax.set_title(title, fontsize=9)
        ax.set_axis_off()
        ax.view_init(elev=12, azim=-65)
        ax.set_proj_type("ortho")
    ax = fig.add_subplot(1, 3, 3)
    tot_o = our_drop.max()
    tot_s = stored_drop.max()
    ax.scatter(stored_drop / tot_s, our_drop / tot_o, s=6, alpha=0.4,
               color="#7b2d8b")
    ax.plot([0, 1], [0, 1], "k--", lw=0.8)
    ax.set_xlabel("2018 stored pressure drop (normalised)")
    ax.set_ylabel("coupled solve pressure drop (normalised)")
    ax.set_title(f"pressure-field validation (r = {r_press:.3f})", fontsize=9)
    ax.grid(alpha=0.25)
    fig.suptitle("0D-1D coupling wired: portal tree solves Q_PV given the "
                 "0D sinusoidal state; HABR responds (classical arm)",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig("hybrid_0d_1d_scenarios.png", dpi=150)
    print("\nFigure saved: hybrid_0d_1d_scenarios.png")
