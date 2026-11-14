# Final update against the 11:33Z table (the one Kelvin has)

Generated 17:05Z, same method as results/update_vs_1133Z.md: the 11:33Z table rebuilt from the run files and the
pre-A20 code (results/P1_tables_as_of_1133Z_reconstructed.md) against the final tables (results/P1_tables_final.md).
Every cell: results/table_diff_1133Z_to_final.md.

One line: are the later layers converged by the registered rule (A18, matched doubling partners, < 3% per doubling)?
No at 1% error: layer 31 local 75 bits (registered 90, still -3% per doubling), layer 31 unrestricted 70 (88, -4%),
layer 16 local 150 (170, -5%), layer 16 unrestricted 81 (111, -5%). At 10% error they are unverified rather than no:
every last doubling moved them by at most 3% (layer 31 local 15.4 -> 15.0, unrestricted 15.5 -> 14.7; layer 16 local
27 -> 24, unrestricted 16.4 -> 15.4), but the matched depth or width partner at 8x steps was not run. Only layer 0
local is converged (573 / 1065 bits at 10% / 1%, registered 575 / 1084); layer-0 unrestricted never reaches 1% error.

What changed since 11:33Z:
- A20 (the review-r2 analysis corrections) alone moves no table cell by more than 5%.
- New runs: the reference-start base finished at ARC layers 4, 12, 20 and 28 on all four nets; the medians at layers
  12 and 20 move by more than 5% because at 11:33Z they were net 4000's look-ahead start alone (layer 12 at 10% / 1%:
  44 -> 74 and 244 -> 289 bits; layer 20: 19.6 -> 27 and 125 -> 148). The profile is non-increasing in depth at 10%
  error (P1.4); at 1% and 0.1% the medians rise from layer 28 to 31 (89 -> 95 and 266 -> 307 bits), where the layer-31
  codes are among the least converged.
- Statuses: certified cells unchanged (narrow-deep layer-0 unrestricted on nets 216, 217, 221); convergence verdicts
  as above (new); predictions P1.2, P1.4, P1.5, P1.7, P1.10 now pass (most were unevaluable at 11:33Z, P1.10's
  synchronisation part passes on the measured combinations only); P1.8 (layer-31 part) and P1.12 (random-start toy)
  remain misses.
- The backward curriculum (A19/A21) lowers no cell: layers 28, 24, 20 and the one-step variant at 16 and 0 are all
  above the look-ahead start, and below layer 28 it never reaches 1% error.

Per-layer profile cells that moved by more than 5% since the 11:33Z table (median over nets; full list: results/table_diff_1133Z_to_final.md):

| table / layer / column | 11:33Z | now | change |
|---|---|---|---|
| arc: per-layer profile / 12 / local 0.01 | 244 (n=1) | 289 [244-333] | +18% |
| arc: per-layer profile / 12 / local 0.1 | 44 (n=1) | 74 [44-97] | +68% |
| arc: per-layer profile / 12 / ratio 0.1 | 2.9 (n=1) | 3.3 [2.9-5.0] | +14% |
| arc: per-layer profile / 12 / slope 0.003-0.001 | 198 (n=1) | 184 [169-187] | -7% |
| arc: per-layer profile / 20 / local 0.01 | 125 (n=1) | 148 [125-203] | +18% |
| arc: per-layer profile / 20 / local 0.1 | 19.6 (n=1) | 27 [19.7-42] | +38% |
| arc: per-layer profile / 20 / ratio 0.01 | 1.5 (n=1) | 1.6 [1.5-1.8] | +7% |
| arc: per-layer profile / 20 / ratio 0.1 | 1.3 (n=1) | 1.5 [1.3-1.5] | +15% |
| arc: per-layer profile / 20 / slope 0.03-0.01 | 84 (n=1) | 94 [84-119] | +12% |
| arc: per-layer profile / 24 / ratio 0.01 | 1.1 [1.0-1.2] | 1.2 [1.1-1.2] | +9% |
| arc: per-layer profile / 28 / local 0.01 | 84 (n=1) | 89 [84-123] | +6% |
| arc: per-layer profile / 28 / local 0.1 | 15.7 (n=1) | 19.1 [15.7-28] | +22% |
| arc: per-layer profile / 31 / ratio 0.01 | 1.0 [1.0-1.1] | 1.1 [1.0-1.1] | +10% |
| arc: per-layer profile / 4 / local 0.001 | 1165 [1016-1308] | 1062 [972-1106] | -9% |
| arc: per-layer profile / 4 / slope 0.003-0.001 | 336 [283-425] | 249 [236-252] | -26% |
| arc: per-layer profile / 4 / slope 0.03-0.01 | 270 [245-275] | 251 [241-271] | -7% |
| arc: per-layer profile / out / local 0.01 | 94 [84-126] | 89 [84-123] | -5% |
| arc: per-layer profile / out / slope 0.03-0.01 | 59 [53-76] | 54 [53-74] | -8% |
| arc: per-layer profile / 12 / starts | reference 0/4, look-ahead 1/4 | reference 4/4, look-ahead 1/4 | reference 0/4, look-ahead 1/4 -> reference 4/4, look-ahead 1/4 |
| arc: per-layer profile / 20 / starts | reference 0/4, look-ahead 1/4 | reference 4/4, look-ahead 1/4 | reference 0/4, look-ahead 1/4 -> reference 4/4, look-ahead 1/4 |
| arc: per-layer profile / 28 / starts | reference 0/4, look-ahead 1/4 | reference 4/4, look-ahead 1/4 | reference 0/4, look-ahead 1/4 -> reference 4/4, look-ahead 1/4 |
| arc: per-layer profile / 4 / starts | reference 0/4, look-ahead 4/4 | reference 4/4, look-ahead 4/4 | reference 0/4, look-ahead 4/4 -> reference 4/4, look-ahead 4/4 |
| nd: per-layer profile / 16 / unres 0.01 | - | 2.9 [2.0-3.2] | - -> value |
| nd: per-layer profile / 16 / unres 0.1 | - | 1.4 [0.81-1.5] | - -> value |
| nd: per-layer profile / 192 / starts | reference 0/6, look-ahead 6/6 | reference 6/6, look-ahead 6/6 | reference 0/6, look-ahead 6/6 -> reference 6/6, look-ahead 6/6 |

Certified cells now (registered certificates, A19 consistency and C7 included): nd net 216 layer 0 unres, nd net 217 layer 0 unres, nd net 221 layer 0 unres

Prediction statuses changed (11:33Z A4 scorer -> final A20 scorer): P1.2: fail, too few cells -> pass; P1.4: fail -> pass; P1.5: fail -> pass; P1.7: fail, too few cells -> pass; P1.10: fail -> pass

Is the count converged by the registered rule (A18; A20 matched partners)? ARC net 4000:

| layer | class | error | converged? | lowest found (registered count) | why |
|---|---|---|---|---|---|
| 0 | local | 10% | yes | 573 (575) | converged; steps -0% (h1c2 -> h1c2s2); depth -0% (h1s2 -> h1c2s2) |
| 0 | local | 1% | yes | 1065 (1084) | converged; steps -2% (h1c2 -> h1c2s2); depth -0% (h1s2 -> h1c2s2) |
| 0 | unres | 10% | unverified | 17.4 (17.8) | unverified: no matched width partner; steps -1% (cap2steps2 -> cap2steps4); depth -0% (steps4 -> cap2steps4); width unverified |
| 0 | unres | 1% | not reached | - (-) | not reached;  |
| 16 | local | 10% | unverified | 24 (27) | unverified: no matched depth partner; steps -3% (h1s4 -> h1s8); depth unverified |
| 16 | local | 1% | no | 150 (170) | not converged: steps -5% per doubling; steps -5% (h1s4 -> h1s8); depth unverified |
| 16 | unres | 10% | unverified | 15.4 (16.4) | unverified: no matched depth, width partner; steps -1% (cap2steps4 -> cap2steps8); depth unverified; width unverified |
| 16 | unres | 1% | no | 81 (111) | not converged: steps -5% per doubling; steps -5% (cap2steps4 -> cap2steps8); depth unverified; width unverified |
| 31 | local | 10% | unverified | 15.0 (15.4) | unverified: no matched depth partner; steps -0% (cap2steps4 -> cap2steps8); depth unverified |
| 31 | local | 1% | no | 75 (90) | not converged: steps -3% per doubling; steps -3% (cap2steps4 -> cap2steps8); depth unverified |
| 31 | unres | 10% | unverified | 14.7 (15.5) | unverified: no matched depth, width partner; steps -1% (cap2steps4 -> cap2steps8); depth unverified; width unverified |
| 31 | unres | 1% | no | 70 (88) | not converged: steps -4% per doubling; steps -4% (cap2steps4 -> cap2steps8); depth unverified; width unverified |
