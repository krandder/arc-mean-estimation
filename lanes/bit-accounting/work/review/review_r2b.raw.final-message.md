<!-- Extracted: the reviewer/co-prover model's final message only. The full session dump (prompt echo, tool calls, intermediate output) is not in this repo. Source file: work/bit-accounting/review/review_r2b.raw -->

**Verdict: major revision.** The headline arithmetic reproduces, but the report does not yet establish that the curves are well optimised within each encoder class or delivered by one conditioned model.
Checked at **2026-11-02 12:25 UTC**, read-only: **159/159 main JSONs, 0/159 amendment JSONs**. No files changed.

Independent recomputation from the runs and results gave:

| Quantity | Recomputed | Report |
|---|---:|---:|
| 16×16 local input, 10% / 1% error | 26.801 / 55.326 bits | 26.8 / 55.3 |
| 32×32 local input, 10% / 1% | 52.642 / 111.990 | 52.6 / 112.0 |
| 16×16 local L/4, 10% / 1% | 4.194 / 15.990 | 4.2 / 16.0 |
| Its linear reference | 5.937 / 20.024 | 5.9 / 20.0 |
| 16×16 input slope | 8.5869 bits/halving | 8.6 |
| 32×32 input slope | 18.0116 | 18.0 |
| 16×16 output slope | 1.1733 | 1.2 |
| Unrestricted–output gap, 10%: median / maximum | 0.0423 / 0.6344 | 0.04 / 0.63 |
| Same, 1% | 0.1356 / 77.1794 | 0.14 / 77.18 |
| C6, original / longer model | 390/477 / 443/477 | 82% / 93% |
| C4 prior checks | **2149/2156 = 99.675%** | **100%** |
| Tanh input, 10% | 65.7023 bits | 65.7 |
| Linear control, 10% / 1% | 4.2039 / 11.5135 | 4.2 / 11.5 |

Executing only the scorer’s read-only portion exactly reproduces the saved scores.

1. **Major — [bit-accounting.md:174](/home/agent/workspaces/mats/work/bit-accounting/bit-accounting.md:174): certification is incomplete, and width attribution remains confounded.** “As good as reasonably possible” and “not undertrained” exceed the evidence. Explorer, corrected-centroid and decoder-width checks have **zero completed results**. The 35% local-width failure rate simultaneously changes encoder, decoder and prior capacity; it cannot establish that width-*n* is the cause. **Fix:** describe these as provisional best-found curves; complete the amendment and report its outcomes before claiming optimisation or encoder-capacity adequacy.

2. **Major — [bit-accounting.md:23](/home/agent/workspaces/mats/work/bit-accounting/bit-accounting.md:23): unrestricted equality and control explanations are overstated.** At 1% error, input-layer unrestricted counts for **all three 32×8 seeds** are 66.81–100.31 bits versus output counts 20.38–23.13. These curves do not “sit on” the output curve. Likewise, failed tanh training does not prove that a decoder “cannot invert” the map. Each control has only one seed; linear agreement is within tolerance, not exact. **Fix:** identify the failing configurations and describe control results as observations, without claiming unavoidable failure.

3. **Major — [bit-accounting.md:91](/home/agent/workspaces/mats/work/bit-accounting/bit-accounting.md:91): the reported envelope does not fulfil the one-model requirement.** Original-model C6 fails **87/477** comparisons; longer training still fails **34/477**. The claim that `r0` differs by only a few tenths is misleading: at 32×8, seed 5000, input/unrestricted, 1% error, **r0 = 99.46 bits versus R* = 66.81**. **Fix:** show the single-model and hybrid curves separately, prominently state the failed requirement, and improve conditioning/training before calling it satisfied.

4. **Major — [bit-accounting.md:210](/home/agent/workspaces/mats/work/bit-accounting/bit-accounting.md:210), [run_vr_cert2.py:178](/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/run_vr_cert2.py:178): uncertainty remains unsupported, and the amendment reuses evaluation data for fitting.** The asserted **0.05-bit selection bias** is not established by the saved uncertainty statistics; distortion uncertainty also affects crossings. Expected KL is an information upper bound, but the selected finite-sample estimate is not a confidence bound or exact mutual information. Additionally, explorer initialisation fits least squares on `xe[:16384]`, drawn from the evaluation set. **Fix:** initialise on pilot/training samples, select on validation data, evaluate on untouched samples, and report uncertainty; otherwise explicitly leave its magnitude unquantified.

5. **Major — [score_P1v2.py:155](/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/score_P1v2.py:155): C5v2 ignores its registered convergence requirement.** `conv` only adds a flag; the pass fraction uses `ok` alone, and P1.1 consumes that fraction. An unchanged held-out reconstruction with training loss falling from 0.02 to 0.01 incorrectly passes. **Fix:** require convergence for a certified pass, or classify unconverged comparisons separately and keep the prediction pending. This has **no current numerical effect**, because no amendment results exist yet.

6. **Minor — [build_report.py:81](/home/agent/workspaces/mats/work/bit-accounting/scratch/build_report.py:81), [bit-accounting.md:192](/home/agent/workspaces/mats/work/bit-accounting/bit-accounting.md:192): rounding becomes a false universal claim.** Seven C4 comparisons fail. For example, 16×16, seed 5002, input/unrestricted, λ≈0.000316: refitting reduces **20.294 to 18.177 bits**, over 10%. Thus “never gives a lower rate” and “the learned prior is tight” are unsupported. **Fix:** print passed/total counts or sufficient precision and describe the actual tolerance and exceptions.

7. **Minor — [score_P1v2.py:191](/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/score_P1v2.py:191): fixed-point attribution is wrong and absent from the table.** Pooling different variable-rate curves can improve a crossing without using any fixed point, yet the scorer labels that improvement `fixed`. **67 of 259** such labels are false by removing fixed points and recomputing. The Markdown table also omits the promised source marker. **Fix:** track the actual interpolation endpoints and print their sources.

8. **Minor — [score_P1v2.py:193](/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/score_P1v2.py:193): the secondary interpolation comparison changes the candidate set.** `R_loglinear` omits pooled/fixed-point crossings. Consequently it exceeds the “conservative” primary count at **64 targets**. Example: 32×32, seed 5002, input/local, D=0.3: stored log-linear **17.072**, primary **12.874**; log-linear with the same candidates is **12.748**. **Fix:** use identical candidates for both interpolation methods and regenerate the comparison.

9. **Minor — [bit-accounting.md:53](/home/agent/workspaces/mats/work/bit-accounting/bit-accounting.md:53): the uncovered-region description is inaccurate.** The 130 uncovered targets are not exclusively tiny errors at early layers: **24 are at D=0.3, 0.1, 0.03 or 0.01**. For **36/130**, the linear reference also fails to reach the target. **Fix:** break coverage down by network and target; only provide a reference upper estimate where one exists. “There the linear reference gives the count” is false as written.

The r2a findings were **not all resolved**: **#3, #8 and #11** have substantive fixes; **#1, #2, #7 and #9** have implementations awaiting results; **#4** has disclosure but no quantified uncertainty; **#5** remains a failed requirement; **#6** now checks all targets but retains coverage gaps; **#10** fixes pooling but leaves attribution wrong; **#12** is acknowledged in §3 but contradicted by the Summary.

Preregistration checks: **P1.2 = 6/6, P1.3 = 12/12, P1.4 = 6/6, P1.5 = all three parts pass; P1.1 correctly remains pending.** C5v2 violates P1-A as noted above. Current preregistration/trainer/scorer hashes match their latest logged hashes, and the substantive deviations are disclosed. However, the hash log explicitly records a **12-cell test run before the v2 scorer hash**; “hashed before any scoring” is therefore too strong. P2.0 remains a registered future phase.

The plain answer supported today is: **best-found local rates generally decrease with depth on these sampled ReLU networks; unrestricted rates usually approach output rates, with substantial exceptions. Optimisation adequacy and the single-model requirement remain unresolved.**
