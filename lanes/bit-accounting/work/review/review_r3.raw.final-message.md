<!-- Extracted: the reviewer/co-prover model's final message only. The full session dump (prompt echo, tool calls, intermediate output) is not in this repo. Source file: work/bit-accounting/review/review_r3.raw -->

**Verdict: major revision.** The reported U arithmetic reproduces, but the penalty implementation, fixed-distortion interpretation, numerical instability, and B1 scoring materially affect the conclusions. Checked read-only against scripts, checkpoints, raw JSON, and hashes at **2026-11-02 23:36 UTC**; no files modified.

1. **High — §3.3; [run_unscr.py:159](/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/run_unscr.py:159): detached normalisation changes the registered objective.**  
   The variance denominator is recomputed but detached. Under jointly scaling \(y_1\) and \(S\) by \(c\), the stated normalised penalty is invariant; its implemented gradient nevertheless pushes amplitudes downward. This encourages loss of signal rather than just simpler dynamics. In tanh’s input pair at μ=3, the next code falls from **14 active coordinates to zero**, with distortion **0.1653 → 1.6232**. **Fix:** implement a genuinely scale-normalised objective, or explicitly register a different constraint; rerun U before interpreting its price mechanistically.

2. **High — Summary 8; [§3.3:366](/home/agent/workspaces/mats/work/bit-accounting/bit-accounting.md:366): “extra bits at fixed distortion” is not measured here.**  
   \[
   \Delta L/\lambda=\Delta R+\Delta D/\lambda
   \]
   is a Lagrangian excess expressed in bit units. A fixed-distortion interpretation requires a justified local RD slope and small displacement; neither rate nor distortion is held fixed. For tanh, l=4, μ=3, the reported **7.1922** comprises **−9.0723 actual bits + 0.162645/0.01**; next-layer distortion rises **0.1285 → 0.3038**. **Fix:** call this an approximate Lagrangian-equivalent cost and show ΔR/ΔD separately; obtain matched-distortion curves for an actual extra-bit claim. `report_U.py` correctly computes the stated arithmetic and U thresholds; μ=0 is an appropriate fine-tuning control, but does not resolve this interpretation.

3. **High — §3.4, Summary 8; [score_P1v2.py:322](/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/score_P1v2.py:322): B1 is scored differently from registration, reversing its outcome.**  
   [PREREG:489](/home/agent/workspaces/mats/work/bit-accounting/PREREG.md:489) specifies the **best P1-B code**, including 12000-step explorers. The scorer excludes those explorers: **12/13** pass its restricted test, whereas **9/13** pass the registered test, below 75%. B2 reproduces as **10/13**, but these are interim results from 13/53 cells. The examples also silently use secondary log-linear interpolation: the primary time-sharing values for 32×8 s5000 input are **29.4490 → 27.0572 bits**, an **8.122%** saving. **Fix:** include all P1-B candidates, report B1 as an interim miss, label interpolation consistently, and withdraw the general “restarts no longer move the counts” conclusion.

4. **High — §3.2; [p2_maps.py:31](/home/agent/workspaces/mats/work/bit-accounting/scratch/p2_maps.py:31) and `active_dirs`; U affine evaluation: near-singular regressions produce unreliable statistics.**  
   Recomputing from checkpoints reproduces late 32×32 local affine R² values **0.721215** and **−2.328899** for seeds 5000/5001, l=24. An SVD rank-truncation sensitivity check (`rcond=1e-6`) gives **0.999945 / 0.999517**. Rotation also changes: seed 5001 l=24 goes from **0.000000606 → 0.195080**. These are numerical sensitivity findings, not evidence of nonlinear dynamics or biological-style rotation. **Fix:** establish conditioning/rank diagnostics, repeat with justified tolerances, and rescore H3/H4 and affected U fits. Merely mentioning “few active directions” understates the problem.

5. **High — Summary 8, §§3.1–3.3: the measurements do not establish the behaviour of optimally compressed, received bits.**  
   Maps and gates use noiseless encoder means, including sub-noise coordinates that the regression standardises back up. From the 16×16 s5000 l=4 checkpoints, tracked gates reproduce as **100%** on means but become **31.25%** after adding the actual unit channel noise; **25%** already pass by constant base-rate prediction. Moreover, the tested r0 codes are anchored codes that explorers outperform. **Fix:** distinguish encoder-mean geometry from information recoverable through the channel, report base-rate gains and noisy-code probes, and test the better explorers. Replace “certified linear pieces” with empirical affine-fit language: these checks certify neither optimality nor a global linear-piece representation.

6. **High — Summary 8 and §3.3: the ordered/chaotic separation is overstated.**  
   Four tanh layer pairs are observations from **one network seed**, not independent control replications. Its active dimensionality and baseline rate differ substantially from late ReLU codes; equal μ also need not produce equal achieved simplicity. The registered relative-cost contrast U2 actually misses, **1/4**. **Fix:** describe the observed absolute-cost difference for this control, retain U2’s failure, and require replicated, matched-complexity comparisons before asserting separation. These experiments neither establish nor refute Kelvin’s broader hypothesis.

7. **Medium — [§3.5:411](/home/agent/workspaces/mats/work/bit-accounting/bit-accounting.md:411): the noisy-transfer description omits the affine results.**  
   “Mostly worse than predicting the mean; at most 0.57” describes the MLP only: **28/40** transfers are negative, maximum **0.571859**. Affine transfers are negative on just **2/40**, with maximum **0.830279**. At k=4 on 32×32, affine R² is **0.553340, 0.341447, 0.366768**; MLP R² is **−3.100937, −2.303933, −5.944897**. H5 remains **0/3** for either fit. **Fix:** report both and distinguish failed transfer under this alignment from proof that no shared dynamics exist.

8. **Medium — preregistration provenance: the blanket “code and scorer hashed before phase-2 runs” claim is unsupported.**  
   All eight listed phase-2 analysis/training/scoring scripts other than the identity scripts match their recorded SHA-256 hashes; current PREREG also matches. However, **`p2_identity.py` and `report_P2_identity.py` have no entries**. The P2-map scorer explicitly records being written **after analysis output existed** ([hash log:161](/home/agent/workspaces/mats/work/bit-accounting/prereg_hashes.txt:161)). U/noisy/P1-B timestamps are consistent with the available execution logs, but hashes alone cannot prove when results were first inspected. **Fix:** disclose the identity provenance gap and exact scorer chronology; correct B1 rather than claiming all predictions were scored as registered.

9. **Verification — recomputed numbers.**  
   These checks reproduce the report’s arithmetic unless qualified above. U values/counts come directly from `runs/U`; the three checkpoint measurements reconstruct held-out inputs and model outputs.

   | Quantity | Recomputed |
   |---|---:|
   | ReLU median U price, μ=1 | 0.381161 |
   | ReLU median U price, μ=3 | 0.556477 |
   | Tanh median U price, μ=1 | 1.642145 |
   | Tanh median U price, μ=3 | 4.892056 |
   | U1 / U2 | 6/18 / 1/4 |
   | U3 / U4 | 28/28 / 12/12 |
   | 16×16 s5000 l=4 local affine R² | 0.986878 |
   | Same pair: tracked gate share | 1.000000 |
   | Same pair: rotation cos² | 0.526243 |
   | H5, independently counted from analysis JSON | 0/3 |
   | Registered B1, recalculated from raw curves | **9/13, miss** |
   | P1-B saving, 32×8 s5000 input, primary interpolation | **8.122%** |
