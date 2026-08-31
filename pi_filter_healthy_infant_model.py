"""
Generic healthy-infant/paediatric liver circulation model, built from the
actual "pi-filter" lumped element used in Harvey's own prior work, not the
simplified ad hoc single-resistor branch used in ldlt_habr_model.py (that
earlier, simplified version is now superseded by this one as the base
circulation model -- see model_plan_and_literature_data.md Section 8).

Pi-filter definition (confirmed from the circuit diagram in
`2018/liver segments/0d-1d habr_v1.docx`, Fig. 4 inset, and matching the text
"consists of three resistors, two capacitors and one inductor"): a two-port
network with a series L + Rs branch between the two ports, and an identical
shunt branch (C in series with Rp, to a common ground/reference) at EACH
port. Four distinct parameter values (L, Rs, C, Rp) per pi-filter, even
though there are 6 physical elements (L, Rs, C, C, Rp, Rp), because the two
shunt legs use the same C and Rp.

Circuit topology (single-lobe/single-segment case, matching the real,
submitted manuscript this model is built from -- see below -- rather than
the fuller multi-generation, left/right-split version in the 2018 draft,
which is out of scope for a first generic model per Harvey's direction):

    P_HA_src(t) --[HA pi-filter]--> P_sinus <--[PV pi-filter]-- P_PV_src
                                       |
                                [HV pi-filter]
                                       |
                                    P_IVC (reference)

Only the OUTPUT-side shunt of each source-driven branch and the shared
sinusoidal/HV nodes matter dynamically (an ideal voltage source absorbs
whatever current its own input-side shunt draws, so that shunt has no effect
on the rest of the circuit and is omitted here).

Target values are REAL, not invented: taken directly from Ho, Yu, Bartlett,
"Computational simulations for the hepatic arterial buffer response after
liver graft transplantation" (submitted manuscript, `2018/liver_paediatric/
submission/numerical methods for quantifying blood flow after PH_v4.docx`),
Results Section 3.1, the POST-transplant paediatric-recipient values -- i.e.
real paediatric portal/hepatic-arterial/hepatic-venous pressures and flows,
used here as the generic healthy-infant baseline this project needs before
returning to the transplant-specific HABR question.
"""

import numpy as np

MMHG_PER_SEC_FLOW = 1.0 / 60.0  # mL/min -> mL/s

# --- Real target values (Ho/Yu/Bartlett PH_v4 manuscript, Results 3.1) ---
TARGETS = {
    "P_PV_src": 13.0,       # mmHg, portal driving pressure (post-transplant)
    "P_HA_src_mean": 57.5,  # mmHg, mean arterial pressure (42.4-72.6 mmHg range)
    "P_HA_src_amp": 15.1,   # mmHg, half the 42.4-72.6 swing
    "P_sinus": 5.37,        # mmHg
    "P_hv": 4.07,           # mmHg
    "P_IVC": 2.0,           # mmHg -- ASSUMED (not reported in the source paper)
    "Q_PV_mean": 300.0,     # mL/min
    "Q_HA_mean": 31.93,     # mL/min
    "Q_HV_mean": 322.5,     # mL/min (note: source paper's own Q_PV+Q_HA=331.9
                            # does not exactly equal its reported Q_HV=322.5;
                            # a ~3% mass-balance discrepancy in the SOURCE
                            # data itself, not introduced here)
}


def solve_dc_resistances(targets=TARGETS):
    """Exactly reproduce the real mean flows/pressures via simple Ohm's law
    on the DC (time-averaged) circuit -- valid because this baseline model
    is linear (no HABR nonlinear resistor yet), so a linear system's time-
    average response to a periodic input equals its DC/steady solution
    regardless of the inertance/compliance ("shape") parameters chosen
    below. This means Rs values derived here reproduce the target MEAN
    flows exactly, independent of how the pulsatile waveform is tuned.
    """
    q_pv = targets["Q_PV_mean"] * MMHG_PER_SEC_FLOW
    q_ha = targets["Q_HA_mean"] * MMHG_PER_SEC_FLOW
    q_hv = targets["Q_HV_mean"] * MMHG_PER_SEC_FLOW

    Rs_PV = (targets["P_PV_src"] - targets["P_sinus"]) / q_pv
    Rs_HA = (targets["P_HA_src_mean"] - targets["P_sinus"]) / q_ha
    Rs_HV = (targets["P_sinus"] - targets["P_hv"]) / q_hv
    Rp_hv_out = (targets["P_hv"] - targets["P_IVC"]) / q_hv
    return dict(Rs_PV=Rs_PV, Rs_HA=Rs_HA, Rs_HV=Rs_HV, Rp_hv_out=Rp_hv_out)


def simulate(params, HR=130.0, t_end_cycles=60, steps_per_cycle=400):
    """Integrate the 5-state pi-filter circuit (Q_HA, Q_PV, P_sinus, Q_HV,
    P_hv) to a periodic state. `params` must supply Rs_PV, Rs_HA, Rs_HV,
    Rp_hv_out (from solve_dc_resistances) plus the "shape" parameters
    L_HA, L_PV, L_HV, C_sinus, C_hv, Rp_sinus (leak at the shared sinusoidal
    node -- large/weak by default, not a real physiological pathway, just
    part of the pi-filter's own topology).
    """
    period = 60.0 / HR
    dt = period / steps_per_cycle
    n_steps = int(round(t_end_cycles * steps_per_cycle))

    Rs_PV, Rs_HA, Rs_HV = params["Rs_PV"], params["Rs_HA"], params["Rs_HV"]
    Rp_hv_out = params["Rp_hv_out"]
    L_HA, L_PV, L_HV = params["L_HA"], params["L_PV"], params["L_HV"]
    C_sinus, C_hv = params["C_sinus"], params["C_hv"]
    Rp_sinus = params["Rp_sinus"]
    P_PV_src = TARGETS["P_PV_src"]
    P_HA_mean = TARGETS["P_HA_src_mean"]
    P_HA_amp = TARGETS["P_HA_src_amp"]
    P_IVC = TARGETS["P_IVC"]

    Q_HA = TARGETS["Q_HA_mean"] * MMHG_PER_SEC_FLOW
    Q_PV = TARGETS["Q_PV_mean"] * MMHG_PER_SEC_FLOW
    Q_HV = TARGETS["Q_HV_mean"] * MMHG_PER_SEC_FLOW
    P_sinus = TARGETS["P_sinus"]
    P_hv = TARGETS["P_hv"]

    hist = {k: np.empty(steps_per_cycle) for k in
            ("Q_HA", "Q_PV", "P_sinus", "Q_HV", "P_hv")}
    prev_cycle = None
    t = 0.0
    converged = False

    for step in range(n_steps):
        # "an alternating and a direct power source" -- pure sinusoid, per
        # the source manuscript's own description (not the more elaborate
        # cardiac-shaped pulse used in this session's other projects).
        P_HA_src = P_HA_mean + P_HA_amp * np.sin(2 * np.pi * t / period)

        dQ_HA = (P_HA_src - Rs_HA * Q_HA - P_sinus) / L_HA
        dQ_PV = (P_PV_src - Rs_PV * Q_PV - P_sinus) / L_PV
        dP_sinus = (Q_HA + Q_PV - Q_HV - (P_sinus / Rp_sinus)) / C_sinus
        dQ_HV = (P_sinus - Rs_HV * Q_HV - P_hv) / L_HV
        dP_hv = (Q_HV - (P_hv - P_IVC) / Rp_hv_out) / C_hv

        Q_HA += dt * dQ_HA
        Q_PV += dt * dQ_PV
        P_sinus += dt * dP_sinus
        Q_HV += dt * dQ_HV
        P_hv += dt * dP_hv
        t += dt

        idx = step % steps_per_cycle
        hist["Q_HA"][idx] = Q_HA
        hist["Q_PV"][idx] = Q_PV
        hist["P_sinus"][idx] = P_sinus
        hist["Q_HV"][idx] = Q_HV
        hist["P_hv"][idx] = P_hv

        if idx == steps_per_cycle - 1:
            this_cycle = {k: v.copy() for k, v in hist.items()}
            if prev_cycle is not None:
                rel = max(
                    np.max(np.abs(this_cycle[k] - prev_cycle[k])) /
                    (np.max(np.abs(prev_cycle[k])) + 1e-12)
                    for k in this_cycle
                )
                if rel < 1e-4:
                    converged = True
                    prev_cycle = this_cycle
                    break
            prev_cycle = this_cycle

    out = {"converged": converged, "t": np.arange(steps_per_cycle) * dt}
    for k, v in prev_cycle.items():
        out[k] = v
        if k.startswith("Q_"):
            out[k + "_mean_mLmin"] = float(np.mean(v)) * 60.0
    return out


DEFAULT_SHAPE_PARAMS = dict(
    L_HA=2.0, L_PV=0.01, L_HV=0.02,
    C_sinus=2.0, C_hv=2.0, Rp_sinus=500.0,
)


def build_params():
    p = solve_dc_resistances()
    p.update(DEFAULT_SHAPE_PARAMS)
    return p


if __name__ == "__main__":
    params = build_params()
    print("Resistances solved exactly from real target flows/pressures:")
    for k in ("Rs_PV", "Rs_HA", "Rs_HV", "Rp_hv_out"):
        print(f"  {k} = {params[k]:.4f}")

    res = simulate(params)
    print(f"\nConverged: {res['converged']}")
    print(f"{'Quantity':<12} {'Simulated mean':>15} {'Target':>10}")
    print(f"{'Q_PV (mL/min)':<12} {res['Q_PV_mean_mLmin']:>15.2f} "
          f"{TARGETS['Q_PV_mean']:>10.2f}")
    print(f"{'Q_HA (mL/min)':<12} {res['Q_HA_mean_mLmin']:>15.2f} "
          f"{TARGETS['Q_HA_mean']:>10.2f}")
    print(f"{'Q_HV (mL/min)':<12} {res['Q_HV_mean_mLmin']:>15.2f} "
          f"{TARGETS['Q_HV_mean']:>10.2f}")
    print(f"{'P_sinus (mmHg)':<12} {np.mean(res['P_sinus']):>15.3f} "
          f"{TARGETS['P_sinus']:>10.3f}")
    print(f"{'P_hv (mmHg)':<12} {np.mean(res['P_hv']):>15.3f} "
          f"{TARGETS['P_hv']:>10.3f}")

    print(f"\nHA flow range: {res['Q_HA'].min()*60:.2f} - "
          f"{res['Q_HA'].max()*60:.2f} mL/min "
          f"(pulsatile, driven by the AC+DC HA source)")
    print(f"PV flow range: {res['Q_PV'].min()*60:.2f} - "
          f"{res['Q_PV'].max()*60:.2f} mL/min (should be nearly flat)")
    print(f"HV flow range: {res['Q_HV'].min()*60:.2f} - "
          f"{res['Q_HV'].max()*60:.2f} mL/min (should be nearly flat, "
          f"damped by the sinusoidal compliance)")
