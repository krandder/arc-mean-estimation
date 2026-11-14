| layer | class | nMSE | current count (registered) | lowest found | run giving it | doublings of the best main start (informed, look-ahead, backward) | best other start | verdict |
|---|---|---|---|---|---|---|---|---|
| 0 | local | 0.1 | 575 | 573 | h1s2 | steps -0% (h1 -> h1s2); depth unverified | h1lr 587 (+3%) | unverified: no matched depth partner |
| 0 | local | 0.01 | 1084 | 1065 | h1s2 | steps -2% (h1 -> h1s2); depth unverified | h1lr 1109 (+4%) | unverified: no matched depth partner |
| 0 | unres | 0.1 | 17.8 | 17.7 | steps2 | steps -1% (base -> steps2); depth unverified; width unverified | - | unverified: no matched depth, width partner |
| 0 | unres | 0.01 | - | not reached by any run | | | | not reached |
| 16 | local | 0.1 | 27 | 25 | h1s4 | steps -4% (h1s2 -> h1s4); depth unverified | h1lr 26 (+3%) | not converged: steps -4% per doubling |
| 16 | local | 0.01 | 170 | 157 | h1s4 | steps -4% (h1s2 -> h1s4); depth unverified | h1lr 175 (+12%) | not converged: steps -4% per doubling |
| 16 | unres | 0.1 | 16.4 | 15.8 | steps4 | steps -1% (steps2 -> steps4); depth unverified; width unverified | - | unverified: no matched depth, width partner |
| 16 | unres | 0.01 | 111 | 89 | steps4 | steps -5% (steps2 -> steps4); depth unverified; width unverified | - | not converged: steps -5% per doubling |
| 31 | local | 0.1 | 15.4 | 15.1 | cap2steps4 | steps unverified; depth -1% (steps4 -> cap2steps4) | h1 15.4 (+2%) | unverified: no matched steps partner |
| 31 | local | 0.01 | 90 | 78 | cap2steps4 | steps unverified; depth -4% (steps4 -> cap2steps4) | h1 90 (+15%) | not converged: depth -4% per doubling |
| 31 | unres | 0.1 | 15.5 | 15.1 | steps4 | steps -1% (steps2 -> steps4); depth unverified; width unverified | - | unverified: no matched depth, width partner |
| 31 | unres | 0.01 | 88 | 78 | steps4 | steps -5% (steps2 -> steps4); depth unverified; width unverified | - | not converged: steps -5% per doubling |

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
| 0 | unres | base | informed | 3 | 1x | 12 | 17.8 | - |
| 0 | unres | r2 | informed | 3 | 1x | 12 | 17.9 | - |
| 0 | unres | steps2 | informed | 3 | 1x | 24 | 17.7 | - |
| 0 | unres | cap2 | informed | 6 | 1x | 12 | 17.9 | - |
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
| 16 | unres | base | informed | 3 | 1x | 12 | 16.4 | 111 |
| 16 | unres | r2 | informed | 3 | 1x | 12 | 16.4 | 110 |
| 16 | unres | steps2 | informed | 3 | 1x | 24 | 16.0 | 94 |
| 16 | unres | steps4 | informed | 3 | 1x | 48 | 15.8 | 89 |
| 16 | unres | cap2 | informed | 6 | 1x | 12 | 16.1 | 96 |
| 31 | local | base | informed | 3 | 1x | 12 | 15.5 | 90 |
| 31 | local | r2 | informed | 3 | 1x | 12 | 15.5 | 90 |
| 31 | local | steps2 | informed | 3 | 1x | 24 | 15.3 | 84 |
| 31 | local | steps4 | informed | 3 | 1x | 48 | 15.2 | 81 |
| 31 | local | cap2 | informed | 6 | 1x | 12 | 15.4 | 85 |
| 31 | local | cap2steps4 | informed | 6 | 1x | 48 | 15.1 | 78 |
| 31 | local | h1 | look-ahead | 3 | 1x | 12 | 15.4 | 90 |
| 31 | unres | base | informed | 3 | 1x | 12 | 15.5 | 88 |
| 31 | unres | r2 | informed | 3 | 1x | 12 | 15.5 | 89 |
| 31 | unres | steps2 | informed | 3 | 1x | 24 | 15.3 | 82 |
| 31 | unres | steps4 | informed | 3 | 1x | 48 | 15.1 | 78 |

### The backward curriculum (A19) against the other local starts, ARC net 4000 (bits; change against the better of the reference and look-ahead starts)

| layer | eps | backward start | reference start | look-ahead start | change |
|---|---|---|---|---|---|
| 28 | 0.1 | 15.8 | - | 15.7 | +1% |
| 28 | 0.01 | 89 | - | 84 | +7% |
| 28 | 0.001 | - | - | 260 | - |
| 24 | 0.1 | 19.6 | 17.0 | 16.9 | +16% |
| 24 | 0.01 | - | 99 | 94 | - |
| 24 | 0.001 | - | 291 | 281 | - |
