<!-- Extracted: the reviewer/co-prover model's final message only. The full session dump (prompt echo, tool calls, intermediate output) is not in this repo. Source file: work/scale-mode/review/check2_gpt6.raw -->

The revision addresses the main objections, but “all 9 applied” is too strong.

1. **Applied — §4:** The exponent argument now states its assumptions and is explicitly conditional.
2. **Applied — Summary, §§5, 8:** Failed escape tests no longer establish an asymptotic negative; two-level slopes and untested higher orders are distinguished.
3. **Applied — Summary, §7:** N2’s registered success is reported separately from external leaderboard evidence.
4. **Partly — §§5–7:** Gain intervals, truth sensitivity and leave-one-width-out slopes were added; crossover uncertainty remains absent, and “resolved” needs qualification.
5. **Applied — §§6, 9:** Transfers are identified as operationalizations; the surviving cell-mean improvement at 128×32 is reported.
6. **Partly — §§5–7:** Extrapolations are disclosed in prose, but §§6–7 still lack flags on the affected table entries.
7. **Partly — §7:** The floor’s direction is corrected, but its new numerical example mixes COV and ARC-k2 costs.
8. **Applied — Summary, §§3, 8:** The connection to the radius-corrected closure is appropriately narrowed.
9. **Applied — §§3, 6, 9:** Printed precision, provenance, ranges and partial repricing are distinguished.

Checked read-only on 2026-11-02. Re-running `scripts/explore_uncertainty.py` reproduced `results/explore_uncertainty.txt` exactly. Independent arithmetic reproduced E1 LVTV2’s nMSE **0.000363302**, cost **687.7106**, gain **2.4661** and crossover **2.2803**; E3’s 512-cell statistic **0.889458**; and E4’s mean COV/RQMC errors **4.47158e-6 / 7.48092e-7**. The **40/45** prediction count matches.

Remaining fixes:

1. **§7, unfloored COV score:** With the table’s COV cost, the result is `4.4715848e-6 × 2049.0103 / 65536 = 1.39806e-7`, not **1.05e-7**. The latter uses ARC-k2’s **1545.0376** passes. Use **1.40e-7**, or explicitly identify a different accounting convention. This also corrects the earlier review’s conflated example.
2. **§5, width exponent:** `score.json` gives LVTV2 error scaling **n^-0.31283**, not **n^-0.33**. Change to **n^-0.31**.
3. **§6, truth sensitivity:** **52%** measures `|error_A − error_B| / error_cross`, not either half’s displacement from cross-half scoring. The maximum individual displacement is **30.7%**; the maximum median displacement is **10.6%**. Name the statistic precisely; “medians move by ≤13%” is conservative but unnecessarily loose.
4. **Summary, §§5–6, uncertainty:** Replace “resolved” with “the exploratory pointwise 95% interval excludes 1, conditional on the saved truths and interpolation model.” The script does not propagate truth uncertainty into these intervals, provide crossover intervals, or update width-slope intervals for scramble uncertainty. Label crossovers as point estimates and existing slope intervals as nets-only.
5. **§§6–7, tables:** Flag SL3’s extrapolated `G_RQ` entries at 128×32 and 256×64; flag ARC-k3f/SL3’s own-cost `G_RQ` in §7 and the mixed measured/projected full-budget column. Keep the measured limits and slope −1 adjacent to those tables.
6. **§8, scope:** Qualify both “~0.1 on the L=n/4 diagonal” statements as **“at widths 128 and 256”**; width 64 gives **0.45**. Also restrict “most accurate order-2-cost estimator … on these shapes” to the tested deep shapes: §7 shows ARC-k2a outperforming LVTV2 at Phase 2.

**Verdict: minor revision.**
