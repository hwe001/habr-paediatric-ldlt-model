"""
SUPERSEDED (2026-08-31): this ad hoc single L+R branch / shared-RC-compartment
model was replaced by the actual documented "pi-filter" element (see
pi_filter_healthy_infant_model.py and ldlt_habr_on_pi_filter.py) per Harvey's
direction -- kept only for history (model_plan_and_literature_data.md
Sections 7-9). Do not use for new results.

0D lumped-parameter model of hepatic arterial (HA) and portal venous (PV)
inflow to a shared post-LDLT graft/sinusoidal compartment, with hepatic
arterial buffer response (HABR) feedback.

Architecture (see graft_hemodynamics_model/model_plan_and_literature_data.md,
Sections 4/4.1/4.2): a single pulsatile HA branch (inertance + resistance)
driven by a periodic systemic pressure pulse, draining into one shared
sinusoidal compartment (compliance + fixed outflow resistance to the hepatic
vein). Portal inflow is NOT independently simulated -- the measured/
interpolated portal vein velocity (PVV) trajectory is used directly as a
prescribed input, since this project's mechanistic question is whether the
literature HABR relationship predicts the HA trajectory GIVEN the observed
portal trajectory, not whether the portal trajectory itself is reproducible.

HABR quadratic (percent-change form) is reused, not re-derived, from Harvey's
own unpublished prior work (Yu, Bartlett, Hunter, Ho, "Hybrid 0D-1D blood flow
simulation for virtual liver transplantation in paediatric recipients",
draft ms., itself citing Ho, Sorrell, Bartlett, Hunter, Med Eng Phys 2013):

    change_Iha = 0.0007102 * change_Ipv**2 + 0.5492 * change_Ipv

where change_Ipv / change_Iha are PERCENT changes in portal / hepatic-
arterial flow relative to a reference state. In the source work this is an
empirical between-run steady-state relationship (not a continuous-time
kinetic model); it is used the same way here -- to set a target mean HA flow
at each post-operative time point, given the portal flow change at that time
point relative to a POD1 reference.
"""

import numpy as np


def _inlet_shape(phase, systole_frac):
    """Non-negative periodic pulse shape (phase in [0,1)), continuity-matched
    at the systole/diastole junction (half-sine upstroke, exponential decay)."""
    t_sys = systole_frac
    return np.where(
        phase < t_sys,
        np.sin(0.5 * np.pi * phase / t_sys),
        np.exp(-4.0 * (phase - t_sys) / (1.0 - t_sys)),
    )


def inlet_pulse(t, period, p0, dp, systole_frac=0.35, shape_mean=None):
    """Periodic driving pressure, oscillating around mean level p0 with
    perturbation amplitude dp (same normalized-shape construction as this
    session's umbilical-artery 0D model, solve_0d_model.py): the pulse never
    collapses toward zero during diastole the way a bare 0-to-peak pulse
    would, which is what lets the HA branch sustain forward diastolic flow
    with a physiological (non-reversed) resistive index.
    """
    phase = (t % period) / period
    shape = _inlet_shape(np.asarray(phase), systole_frac)
    if shape_mean is None:
        grid = np.linspace(0, 1, 400, endpoint=False)
        shape_mean = _inlet_shape(grid, systole_frac).mean()
    return p0 + dp * (shape / shape_mean - 1.0)


def simulate(params, t_end_cycles=40, steps_per_cycle=400, return_series=False):
    """Integrate the HA + shared-sinusoid ODE system to a periodic state.

    params: dict with keys
        HR        -- heart rate, bpm
        p0        -- mean systemic driving pressure
        dp_inlet  -- systemic inlet pulse perturbation amplitude
        R_HA      -- hepatic arterial resistance
        L_HA      -- hepatic arterial inertance
        C_sinus   -- sinusoidal compartment compliance
        R_out     -- sinusoid -> hepatic vein outflow resistance
        P_hv      -- hepatic vein reference pressure
        v_pv      -- prescribed (measured) portal vein velocity, used
                     directly as a portal-inflow proxy into the sinusoid
                     (see module docstring)
        k_pv      -- coupling gain from v_pv into the sinusoid mass balance

    Returns dict with steady-state PSV_HA, EDV_HA, RI_HA, PI_HA, mean Q_HA,
    and (if return_series) the last-cycle time series.
    """
    HR = params["HR"]
    period = 60.0 / HR
    dt = period / steps_per_cycle
    n_steps = int(round(t_end_cycles * steps_per_cycle))

    R_HA = params["R_HA"]
    L_HA = params["L_HA"]
    C_sinus = params["C_sinus"]
    R_out = params["R_out"]
    P_hv = params["P_hv"]
    v_pv = params["v_pv"]
    k_pv = params["k_pv"]
    dp_inlet = params["dp_inlet"]
    p0 = params["p0"]

    grid = np.linspace(0, 1, 400, endpoint=False)
    shape_mean = _inlet_shape(grid, 0.35).mean()

    Q_HA = 0.0
    P_sinus = p0

    Q_hist = np.empty(steps_per_cycle)
    prev_cycle_Q = None
    t = 0.0
    converged = False
    last_full_cycle = None

    for step in range(n_steps):
        P_ao = inlet_pulse(t, period, p0, dp_inlet, shape_mean=shape_mean)

        dQ_HA = (P_ao - R_HA * Q_HA - P_sinus) / L_HA
        dP_sinus = (Q_HA + k_pv * v_pv - (P_sinus - P_hv) / R_out) / C_sinus

        Q_HA += dt * dQ_HA
        P_sinus += dt * dP_sinus
        t += dt

        idx = step % steps_per_cycle
        Q_hist[idx] = Q_HA

        if idx == steps_per_cycle - 1:
            this_cycle = Q_hist.copy()
            if prev_cycle_Q is not None:
                rel_change = np.max(np.abs(this_cycle - prev_cycle_Q)) / (
                    np.max(np.abs(prev_cycle_Q)) + 1e-12
                )
                if rel_change < 1e-4:
                    converged = True
                    last_full_cycle = this_cycle
                    break
            prev_cycle_Q = this_cycle
            last_full_cycle = this_cycle

    v_sys = float(np.max(last_full_cycle))
    v_dias = float(np.min(last_full_cycle))
    v_mean = float(np.mean(last_full_cycle))
    RI = (v_sys - v_dias) / v_sys
    PI = (v_sys - v_dias) / v_mean

    out = {
        "PSV_HA": v_sys,
        "EDV_HA": v_dias,
        "mean_Q_HA": v_mean,
        "RI_HA": RI,
        "PI_HA": PI,
        "converged": converged,
    }
    if return_series:
        out["Q_series"] = last_full_cycle
        out["t_series"] = np.arange(steps_per_cycle) * dt
    return out


def habr_percent_change(change_Ipv):
    """Yu/Bartlett/Hunter/Ho quadratic (percent-change form)."""
    return 0.0007102 * change_Ipv**2 + 0.5492 * change_Ipv
