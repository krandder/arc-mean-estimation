| prediction | registered scorer (v1) | A4 scorer (v2) | A20 scorer (v3) |
|---|---|---|---|
| P1.1: C1 passes at L - l <= 8 (both curves reached) on >= 75% of cells | pass (hits 53, n 54, need 41) | pass (hits 53, n 54, need 41) | pass (hits 53, n 54, need 41) |
| P1.2: ARC local R(0.1) at l in {0, 2, 4} >= 4 x R_out(0.1), 4 of 4 nets | pass (hits 4, n 4, need 4) | pass (hits 4, n 4, need 4) | pass (hits 4, n 4, need 4) |
| P1.3: ARC local l = 31 within 15% of R_out at 0.1 and 0.01, >= 3 of 4 nets | pass (hits 4, n 4, need 3) | pass (hits 4, n 4, need 3) | pass (hits 4, n 4, need 3) |
| P1.4: local R(0.1) non-increasing in l (10% + 1 bit), ARC >= 3 of 4, narrow-deep >= 5 of 6 | pass (arc_hits 4, nd_hits 6) | fail | pass |
| P1.5: slopes: ARC l = 0 above l = 31 near 0.01 (4 of 4); narrow-deep l >= 32 in [0.8, 1.6] (>= 5 of 6) | pass (arc_hits 4, arc_n 4, nd_hits 6, nd_n 6) | fail (arc_hits 4, arc_n 4, nd_hits 0, nd_n 0) | pass (arc_hits 4, arc_n 4, nd_hits 6, nd_n 6) |
| P1.6: ARC local slope near 0.01 within [0.5, 2] x N(l, 0.01) at l = 16-31 on >= 75% | pass (hits 16, n 16, need 12) | pass (hits 16, n 16, need 12) | pass (hits 15, n 16, need 12) |
| P1.7: ARC 4000 local R(0.1) within 2x of the bits-bounds formula (d = PR) at l = 4, 8, 16 | pass (hits 3, n 3, need 3) | pass (hits 3, n 3, need 3) | pass (hits 3, n 3, need 3) |
| P1.8: C6 passes on >= 90%; layer 31 local within 10% of the gram reference at 0.1 and 0.01 (>= 3 of 4) | fail (c6_pass 555, c6_n 557, l31_hits 0, l31_n 4) | fail (c6_pass 555, c6_n 557, l31_hits 0, l31_n 4) | fail (c6_pass 555, c6_n 557, l31_hits 0, l31_n 4) |
| P1.9: C2 passes on all nets; R_out(0.01) <= 0.8 R_G(0.01) on >= 3 of 4 ARC nets | pass (ratio_hits 4) | pass (c2_pass 120, c2_n 120, ratio_hits 4) | pass (c2_pass 120, c2_n 120, ratio_hits 4) |
| P1.10: narrow-deep: both classes at l >= 32 within max(0.5 bit, 10%) of R_out; local R(0.1) at l = 0 >= 3 R_out | fail (n 6, sync_hits 0, input_hits 6) | fail (n 6, sync_hits 0, input_hits 6) | pass (n 6, sync_hits 6, input_hits 6) |
| P1.11: output-mean error < nMSE / 10 on >= 90% of resolved points with nMSE <= 0.1 | pass (hits 5477, n 5862, need 5276) | pass (hits 5477, n 5862, need 5276) | pass (hits 5480, n 5865, need 5279) |
| P1.12: C5 (planted toy) passes for both classes at k = 4 and 16 (registered random local start) | fail | fail | fail |
