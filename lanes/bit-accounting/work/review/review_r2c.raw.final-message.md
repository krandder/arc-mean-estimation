<!-- Extracted: the reviewer/co-prover model's final message only. The full session dump (prompt echo, tool calls, intermediate output) is not in this repo. Source file: work/bit-accounting/review/review_r2c.raw -->

**Verdict: major revision.** The arithmetic largely reproduces, but certification of the reported best-found curves remains overstated.
Checked **2026-11-02 15:37 UTC**, read-only: 159 main files, 55 post-pass files; executing the scorer’s read-only portion exactly reproduced the saved scores and counts.

Recomputed directly from the curves:

| Post-pass quantity | Recomputed | Report |
|---|---:|---:|
| Explorer savings, input, 10% / 1% error | 30.761% / 12.300% | 31% / 12% |
| Explorer savings, L/4 | 30.653% / 19.263% | 31% / 19% |
| Explorer savings, L/2 | 10.794% / 14.124% | 11% / 14% |
| Explorer savings, late layers | 1.334% / 2.568% | 1% / 3% |
| Wide-decoder minus base, median [range], 110 points | −0.02465 [−1.38348, +0.14054] bits | Matches |
| Residual-centroid relative gap, median / worst, 165 points | 1.3565% / 6.0535% | 1.4% / 6% |
| 16×16 local input, median, 10% / 1% | 17.24845 / 48.75296 bits | 17.2 / 48.8 |

The last two counts come from explorer `x0`, seed 5002, and `x2`, seed 5000, respectively. **The savings and width rows use log-linear crossings**, unlike the report’s primary counts.

1. **Major — [Summary point 6 and §1](/home/agent/workspaces/mats/work/bit-accounting/bit-accounting.md:48), [§3 heading](/home/agent/workspaces/mats/work/bit-accounting/bit-accounting.md:193): certificates do not establish optimisation adequacy of the selected curves.** C1/C2 still compare anchored models; the corrected centroid tests only **r0**, at three prices on 55 ReLU-local cells. Explorer codes supply **98 of the 10%/1% counts**, but receive no corresponding centroid or doubled-training check. Moreover, a plateaued residual regressor is not proof of the optimal conditional mean. **Fix:** replace “as good as reasonably possible” and “the decoders are close to optimal” with the measured result: *the fitted residual correction improved r0 little on the tested cells*. Explicitly separate certificates for r0 from checks on the selected explorer curves.

2. **Major — [Summary opening](/home/agent/workspaces/mats/work/bit-accounting/bit-accounting.md:15), [§2 introduction](/home/agent/workspaces/mats/work/bit-accounting/bit-accounting.md:113): the one-model claim remains contradictory.** The report acknowledges failure, yet still describes the measured curve as coming “from one model” and differences from r0 as mostly “a few tenths.” Across ReLU-local cells at 10%/1%, median r0–R* gaps are **9.67 bits at input, 3.83 at L/4, and 1.39 at L/2**. **Fix:** consistently describe R* as an envelope over multiple models; retain r0 as the separate single-model result.

3. **Minor — [Summary point 5](/home/agent/workspaces/mats/work/bit-accounting/bit-accounting.md:44): decoder-width attribution is too categorical.** “Decoder and prior width do not matter” and “gains … come from the encoder’s own width” exceed a near-zero median from one anchored width experiment per cell. Individual improvements reach **1.38 bits**, and this does not test decoder capacity around explorer solutions. **Fix:** say widening decoder/prior alone produced little typical improvement under the tested training setup, supporting—but not proving—the encoder-width explanation.

4. **Minor — [summary_fill.py:158](/home/agent/workspaces/mats/work/bit-accounting/scratch/summary_fill.py:158): summary comparisons silently use secondary interpolation.** Saved training summaries contain log-linear crossings. With primary time-sharing crossings, input savings become **31.669% / 11.920%**, L/4 **31.806% / 19.222%**, and wide-decoder differences **−0.02027 [−1.55930, +0.25207] bits**. **Fix:** compute these comparisons with the primary crossing function, or explicitly label them log-linear.

5. **Minor — [status and coverage](/home/agent/workspaces/mats/work/bit-accounting/bit-accounting.md:3): “58 of the 60 ReLU local cells” is false.** There are **57 distinct ReLU-local cells**, with **55 completed**; 16×4’s 3L/4 and L−1 coincide. Missing: 32×8, seed 5001, layers 6 and 7. **Fix:** derive coverage from the manifest rather than hardcoding it.

6. **Minor — [Summary point 6](/home/agent/workspaces/mats/work/bit-accounting/bit-accounting.md:54), [certificate table and interpretation](/home/agent/workspaces/mats/work/bit-accounting/bit-accounting.md:197): tolerance passes still become stronger numerical claims.**
   - C4 is **2149/2156**, not universally 100%; the largest prior-refit reduction is **13.44%**, not “up to 10%.”
   - C7 passes its tolerance, but **70 comparisons exceed the linear-reference rate**, by up to **2.551 bits**; “at or below” is false.
   - The linear control’s maximum Gaussian-reference gap is **0.1226 bit**, exceeding the claimed 0.1.
   
   **Fix:** print counts, state the certificate tolerances, and use the actual extrema.

**r2b disposition:** #1 and #3 are acknowledged but remain contradicted by certification/single-model wording; #2’s unrestricted exceptions and control caveats are applied, with the linear tolerance error above; #4 is stated as a limit, and **12 post-pass files** still lack the pilot-initialisation marker; #5 is fixed—all 165 current centroid comparisons satisfy convergence; #6 is only partially fixed; #7 source attribution, #8 matching interpolation candidates, and #9 coverage breakdown are fixed.
