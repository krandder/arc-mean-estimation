<!-- Extracted: the reviewer/co-prover model's final message only. The full session dump (prompt echo, tool calls, intermediate output) is not in this repo. Source file: work/bit-accounting-arc/review/review_r3.raw -->

**Verdict: fixable issues.** Checked 2026-11-02 at 15:18 UTC against **449 deduplicated run files**; duplicate filenames had identical contents. No files modified. A22’s pending results are excluded.

A20’s run normalization, convex-hull interpolation, and matched-partner comparisons work on the current data. Independent enumeration of two-point mixtures agreed with `R_lin` on **1,347 checks**. Regenerating the main tables, C7 table, consistency table, and convergence table in memory reproduced their saved outputs.

Remaining findings:

1. **Major — convergence wording still exceeds A18’s scope (r2 #8).**  
   Summary 7 calls layer 0 “converged” throughout **3–1% and 0.3–0.1% error**, but A18 checks only **10% and 1%**, on net 4000. Replace those broader claims with the specific checks performed. Summary 6’s “pushed … until” also suggests completion despite failed and unverified cells.

2. **Major — “within 1%” still conflates output baselines (r2 #4).**  
   §4.8 says layer-31 unrestricted is “within 1%.” Against the registered output-cell baseline, that describes the **10%** points; at 1%/0.1%, it is approximately **6–12% below** that baseline. Against the best-known envelope, net 4000’s base code is **20%/29% above** it. State the baseline, accuracy, and whether this means one-sided shortfall or absolute agreement.

3. **Major — export fixes are incomplete (r2 #6/#9).**  
   `scratch/export_curves.py:90–102` exits early for look-ahead-only cells: **18 measured narrow-deep cells lack `bits_best_known` and its winning run**. Exported C7 uses the scorer’s `fixlam` checks only: ARC layer 0 exports **3 checks instead of 9**, omitting `fixlamlo` and `fixlamh1`. The saved export also omits layer-0 unrestricted’s **1% “not reached”** A18 entry. Apply the common export logic before returning and include every dedicated variant.

4. **Minor — normalization is incomplete for theoretical benchmarks (r2 #2).**  
   Learned/reference distortions use `V_net`, but Gaussian-bound calculations in `score_P1_v3.py`/`report_tables.py`, and water-filling in `spectrum_table.py`, still use original `V`. For ARC-4000’s output at 10%, the Gaussian benchmark becomes **19.226 bits**, versus **19.348** currently calculated. Use `V_net` consistently.

5. **Minor — several unmarked numbers remain stale (r2 #14).**

   | Location | Report | Generated files / raw recomputation |
   |---|---|---|
   | §4.2, layer 28 at 1% | +6% | **+6.51%, rounds +7%** |
   | §4.2, layer 16 one-step change | +4% | **+3.27%, rounds +3%** |
   | §4.2, layer 16 comparator at 0.1% | 432 | **431**, better of the two starts |
   | §4.3, output above envelope, net 4000 | +3% / +24% / +37% | **+4% / +31% / +45%** |
   | §4.8, C6 passes | 515/517 | **555/557**; **505/507** excluding output cells |
   | §6 and `scorecard.md`, v3 P1.11 | 5306/5691 | **5402/5787**, threshold **5209**, still pass |

   Summary 6’s layer-31 **78-bit** value also needs “local”: unrestricted already reaches **73 bits**, before A22.

6. **Minor — scorer coverage needs explicit qualification (r2 #7).**  
   V3 correctly uses both starts and checks the finer slope intervals. However, P1.5/P1.10 skip missing unrestricted layers **32, 128, 192** and report passes under headings retaining the full prediction. Label these **passes on measured combinations (7/10 layer/class combinations per net)**; keep the original full-coverage prediction distinct from this amended assessment.

7. **Minor — wording fixes remain partial (r2 #5/#10/#11).**  
   Summary 5’s “matches … given enough training” exceeds residual layer-31 gaps of **5–7%**; say “approaches.” The backward gain-copy defect and absence of fresh-input, between-anchor validation remain unfixed, although §4.2 now discloses them appropriately. §4.9 still labels the explanatory “accounts for most” inference **MEASURED**; that inference remains **HEURISTIC**.

8. **Minor — the convergence checker is not fully general (r2 #1).**  
   Current verdicts are correct, but `conv_subset.py:81–85` can check the best **main** start instead of the actual winning run, and aggregates base restarts rather than selecting the lowest individual run. This does not change today’s twelve rows; it does not fully implement A18/A20 for a future different winner.

Numerical spot-checks reproduced these **12 summary values** directly from normalized run JSON:

| ARC layer | 10% | 1% | 0.1% |
|---|---:|---:|---:|
| 0 | 630 | 1139 | 1625 |
| 2 | 358 | 849 | 1302 |
| 4 | 230 | 654 | 1062 |
| 8 | 111 | 409 | 767 |

All current convergence-table verdicts follow the matched comparisons:

| Layer/class | Lowest at 10% | Lowest at 1% |
|---|---|---|
| 0 local | **572.67 — converged** | **1064.77 — converged** |
| 0 unrestricted | **17.46 — unverified depth/width** | **not reached** |
| 16 local | **25.02 — not converged** | **156.91 — not converged** |
| 16 unrestricted | **15.60 — unverified width** | **84.61 — not converged** |
| 31 local | **15.07 — converged** | **77.78 — not converged** |
| 31 unrestricted | **14.87 — unverified width** | **73.36 — not converged** |

Backward counts also reproduce: layer 28 **15.798/89.280**, layer 24 **19.643/unreached**, layer 20 **42.446/unreached**, and A21 layer 16 **27.858/unreached**. The report’s remaining problems concern scope, incomplete exports, and stale transcription; these checks do not establish that the counts are intrinsic network limits.
