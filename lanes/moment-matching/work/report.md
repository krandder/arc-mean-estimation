# Moment matching: how much do the input's degree-<=d moments pin down E f? (2026-11-03; saved by main from the lane's message)

MEASURED (exploratory): median gap/sd over 3 nets; gap = max - min of E f over input laws matching all Gaussian moments
up to degree d (LP over a growing point set). Highest-degree values are lower bounds (runs stopped early); n=6, d=6 one net.
Full tables and fits: runs/tables.md, runs/fs_table.md. Code: cg.py.

| n | L=1 | L=2 | L=4 | L=8 | degrees |
|---|---|---|---|---|---|
| 4 | 1.07/.59/.44/.28 | 1.79/1.30/.92/.66 | 1.18/.63/.45/.30 | 1.13/.74/.52/.39 | d=2/4/6/8 |
| 6 | 1.34/.60/.38 | 1.84/1.09/- | 1.99/1.07/.67 | 1.82/1.26/- | d=2/4/6 |
| 8 | 1.36/.67 | 2.14/1.27 | 2.29/1.57 | 2.60/1.58 | d=2/4 |

- No net gets below 10% of sd at any degree run (lowest 0.21). Odd degrees add almost nothing; d=1 unbounded.
- Fit gap ~ d^-1 suggests d ~ 20-60 for 10% and ~200-650 for 1% (EXTRAPOLATION). A single 1-D ReLU reaches 10% only at d=16.
- Depth: at n=4 depth raises the gap but not its decay rate (exponent 0.9-1.1). At n=6-8 deeper nets have 1.5-2.5x larger
  gaps at the same degree and decay more slowly from d=2 to 4; too few degrees to fit a rate.
- Method: fixed 2^16 points still grew ~3%/doubling, so gaps come from continuously added points. Linear control 0
  everywhere; parity control above its built-in bound 1.26 sd but does not drop at d=n.
