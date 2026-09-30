# Additional sensitivity analyses (revision for Medical Engineering & Physics)

Scripts added in response to reviewer comments. They use a fast solver that computes the exact
periodic steady state of the same forward-Euler map used in `ldlt_habr_consistent_units.py`,
and reproduce that model's results (Table 3 PSV values to within 0.01 cm/s, the 20.2-27.1%
identifiability envelope, and the calibre-growth results).

| File | Purpose |
|---|---|
| `model.py` | 4-state pi-filter hepatic-artery branch (`simulate` = time stepping, `simulate_fast` = exact periodic steady state) |
| `pipeline.py` | POD1 anchor fit, HABR flow-target solve, continuous / acute-then-frozen / null scenarios, fraction of PSV decline reproduced (F) |
| `sens.py` | HABR coefficient scaling, one-at-a-time assumed parameters (HR, P_HA_mean, P_IVC, C, R, L), P_HA_amp family, calibre-growth check -> `sens.json` |
| `sens2.py` | Modelled RI values, P_HA_mean extension, structural-remodelling RI |
| `figs.py` | Comparative sensitivity figure -> `fig9.png` |

Run (Python 3, numpy, scipy, matplotlib):

    cd sensitivity_analyses
    python pipeline.py
    python sens.py
    python sens2.py
    python figs.py

Key results: HABR coefficients x0.5-1.5 give F = 12.8-37.9% (x3.9 needed for F = 100%); the modelled
RI is flat or rises in every scenario and variant (measured RI falls 0.61 -> 0.59); calibre growth of 0-20%
per vessel gives F from -44% to +129%.
