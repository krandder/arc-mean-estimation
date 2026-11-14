| layer | class | nMSE | current count (registered) | lowest found | run giving it | doublings of the best main start (informed, look-ahead, backward) | best other start | verdict |
|---|---|---|---|---|---|---|---|---|
| 0 | local | 0.1 | 575 | 573 | h1c2s2 | steps -0% (h1c2 -> h1c2s2); depth -0% (h1s2 -> h1c2s2) | h1lr 587 (+3%) | converged |
| 0 | local | 0.01 | 1084 | 1065 | h1c2s2 | steps -2% (h1c2 -> h1c2s2); depth -0% (h1s2 -> h1c2s2) | h1lr 1109 (+4%) | converged |
| 0 | unres | 0.1 | 17.8 | 17.4 | cap2steps4 | steps -1% (cap2steps2 -> cap2steps4); depth -0% (steps4 -> cap2steps4); width unverified | - | unverified: no matched width partner |
| 0 | unres | 0.01 | - | not reached by any run | | | | not reached |
| 16 | local | 0.1 | 27 | 24 | h1s8 | steps -3% (h1s4 -> h1s8); depth unverified | h1lr 26 (+6%) | unverified: no matched depth partner |
| 16 | local | 0.01 | 170 | 150 | h1s8 | steps -5% (h1s4 -> h1s8); depth unverified | h1lr 175 (+17%) | not converged: steps -5% per doubling |
| 16 | unres | 0.1 | 16.4 | 15.4 | cap2steps8 | steps -1% (cap2steps4 -> cap2steps8); depth unverified; width unverified | - | unverified: no matched depth, width partner |
| 16 | unres | 0.01 | 111 | 81 | cap2steps8 | steps -5% (cap2steps4 -> cap2steps8); depth unverified; width unverified | - | not converged: steps -5% per doubling |
| 31 | local | 0.1 | 15.4 | 15.0 | cap2steps8 | steps -0% (cap2steps4 -> cap2steps8); depth unverified | h1 15.4 (+3%) | unverified: no matched depth partner |
| 31 | local | 0.01 | 90 | 75 | cap2steps8 | steps -3% (cap2steps4 -> cap2steps8); depth unverified | h1 90 (+19%) | not converged: steps -3% per doubling |
| 31 | unres | 0.1 | 15.5 | 14.7 | cap2steps8 | steps -1% (cap2steps4 -> cap2steps8); depth unverified; width unverified | - | unverified: no matched depth, width partner |
| 31 | unres | 0.01 | 88 | 70 | cap2steps8 | steps -4% (cap2steps4 -> cap2steps8); depth unverified; width unverified | - | not converged: steps -4% per doubling |

### All runs (bits at nMSE 0.1 / 0.01)

| layer | class | run | start | depth | width | steps (k) | 0.1 | 0.01 |
|---|---|---|---|---|---|---|---|---|
| 0 | local | base | informed | 3 | 1x | 12 | 642 | 1126 |
| 0 | local | r2 | informed | 3 | 1x | 12 | 642 | 1125 |
| 0 | local | steps2 | informed | 3 | 1x | 24 | 647 | 1126 |
| 0 | local | cap2 | informed | 6 | 1x | 12 | 642 | 1125 |
| 0 | local | h1 | look-ahead | 3 | 1x | 12 | 575 | 1084 |
| 0 | local | h1s2 | look-ahead | 3 | 1x | 24 | 573 | 1065 |
| 0 | local | h1c2 | look-ahead | 6 | 1x | 12 | 574 | 1084 |
| 0 | local | h1lr | look-ahead lr 3e-4 | 3 | 1x | 12 | 587 | 1109 |
| 0 | local | rndhi | random lr 1e-3 | 3 | 1x | 12 | - | - |
| 0 | local | rndmid | random lr 3e-4 | 3 | 1x | 12 | - | - |
| 0 | local | h1c2s2 | look-ahead | 6 | 1x | 24 | 573 | 1065 |
| 0 | local | bwd1 | backward one-step | 3 | 1x | 12 | - | - |
| 0 | unres | base | informed | 3 | 1x | 12 | 17.8 | - |
| 0 | unres | r2 | informed | 3 | 1x | 12 | 17.9 | - |
| 0 | unres | steps2 | informed | 3 | 1x | 24 | 17.7 | - |
| 0 | unres | steps4 | informed | 3 | 1x | 48 | 17.5 | - |
| 0 | unres | cap2 | informed | 6 | 1x | 12 | 17.9 | - |
| 0 | unres | cap2steps4 | informed | 6 | 1x | 48 | 17.4 | - |
| 0 | unres | cap2steps2 | informed | 6 | 1x | 24 | 17.7 | - |
| 16 | local | base | informed | 3 | 1x | 12 | 32 | 185 |
| 16 | local | r2 | informed | 3 | 1x | 12 | 32 | 186 |
| 16 | local | steps2 | informed | 3 | 1x | 24 | 31 | 182 |
| 16 | local | cap2 | informed | 6 | 1x | 12 | 31 | 185 |
| 16 | local | h1 | look-ahead | 3 | 1x | 12 | 27 | 170 |
| 16 | local | h1s2 | look-ahead | 3 | 1x | 24 | 26 | 164 |
| 16 | local | h1s4 | look-ahead | 3 | 1x | 48 | 25 | 157 |
| 16 | local | h1c2 | look-ahead | 6 | 1x | 12 | 27 | 169 |
| 16 | local | h1lr | look-ahead lr 3e-4 | 3 | 1x | 12 | 26 | 175 |
| 16 | local | rndhi | random lr 1e-3 | 3 | 1x | 12 | 27 | - |
| 16 | local | rndmid | random lr 3e-4 | 3 | 1x | 12 | 30 | - |
| 16 | local | h1s8 | look-ahead | 3 | 1x | 96 | 24 | 150 |
| 16 | local | bwd1 | backward one-step | 3 | 1x | 12 | 28 | - |
| 16 | unres | base | informed | 3 | 1x | 12 | 16.4 | 111 |
| 16 | unres | r2 | informed | 3 | 1x | 12 | 16.4 | 110 |
| 16 | unres | steps2 | informed | 3 | 1x | 24 | 16.0 | 94 |
| 16 | unres | steps4 | informed | 3 | 1x | 48 | 15.8 | 89 |
| 16 | unres | cap2 | informed | 6 | 1x | 12 | 16.1 | 96 |
| 16 | unres | cap2steps4 | informed | 6 | 1x | 48 | 15.6 | 85 |
| 16 | unres | cap2steps8 | informed | 6 | 1x | 96 | 15.4 | 81 |
| 16 | unres | cap2steps2 | informed | 6 | 1x | 24 | 15.8 | 89 |
| 31 | local | base | informed | 3 | 1x | 12 | 15.5 | 90 |
| 31 | local | r2 | informed | 3 | 1x | 12 | 15.5 | 90 |
| 31 | local | steps2 | informed | 3 | 1x | 24 | 15.3 | 84 |
| 31 | local | steps4 | informed | 3 | 1x | 48 | 15.2 | 81 |
| 31 | local | cap2 | informed | 6 | 1x | 12 | 15.4 | 85 |
| 31 | local | cap2steps4 | informed | 6 | 1x | 48 | 15.1 | 78 |
| 31 | local | cap2steps8 | informed | 6 | 1x | 96 | 15.0 | 75 |
| 31 | local | h1 | look-ahead | 3 | 1x | 12 | 15.4 | 90 |
| 31 | local | cap2steps2 | informed | 6 | 1x | 24 | 15.2 | 81 |
| 31 | unres | base | informed | 3 | 1x | 12 | 15.5 | 88 |
| 31 | unres | r2 | informed | 3 | 1x | 12 | 15.5 | 89 |
| 31 | unres | steps2 | informed | 3 | 1x | 24 | 15.3 | 82 |
| 31 | unres | steps4 | informed | 3 | 1x | 48 | 15.1 | 78 |
| 31 | unres | cap2 | informed | 6 | 1x | 12 | 15.3 | 84 |
| 31 | unres | cap2steps4 | informed | 6 | 1x | 48 | 14.9 | 73 |
| 31 | unres | cap2steps8 | informed | 6 | 1x | 96 | 14.7 | 70 |
| 31 | unres | cap2steps2 | informed | 6 | 1x | 24 | 15.1 | 78 |

### The backward curriculum (A19) against the other local starts, ARC net 4000 (bits; change against the better of the reference and look-ahead starts)

| layer | eps | backward start | reference start | look-ahead start | change |
|---|---|---|---|---|---|
| 28 | 0.1 | 15.8 | 15.8 | 15.7 | +1% |
| 28 | 0.01 | 89 | 85 | 84 | +7% |
| 28 | 0.001 | - | 262 | 260 | - |
| 24 | 0.1 | 19.6 | 17.0 | 16.9 | +16% |
| 24 | 0.01 | - | 99 | 94 | - |
| 24 | 0.001 | - | 291 | 281 | - |
| 20 | 0.1 | 42 | 22 | 19.7 | +116% |
| 20 | 0.01 | - | 142 | 125 | - |
| 20 | 0.001 | - | 372 | 357 | - |
