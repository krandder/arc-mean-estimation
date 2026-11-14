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
