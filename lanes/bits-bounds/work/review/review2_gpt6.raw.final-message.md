<!-- Extracted: the reviewer/co-prover model's final message only. The full session dump (prompt echo, tool calls, intermediate output) is not in this repo. Source file: work/bits-bounds/review/review2_gpt6.raw -->

**Verdict: major revision.** The registered scores and quoted statistics reproduce. The main problems are unsupported plateau claims, missing theorem qualifiers, and incomplete application of the first review. Read-only checks completed **2026-11-01 23:02 UTC**; no files modified.

Locations below refer to the [report](/home/agent/workspaces/mats/outbox/bits-bounds-2026-11-01.md) unless another file is named.

1. **Major — Summary 10, closing scorecard paragraph, §8 reading; FORMAL §11 C4.** “The error stops falling,” “so the gain peaks,” and “that closes the lead” exceed the evidence. The late-width slope is **0.526 ± 1.293 SE**, with a conventional 95% interval **[−2.25, 3.30]**. This includes continued \(n^{-2}\) decay and growing gain. Geometric means reuse the same small sample; they do not establish the conclusion “more firmly.” **Fix:** say B3/B4 passed their registered finite-width comparisons, while \(H_{\rm peak}\) remains unresolved.

2. **Major — §5 regime map; Summary 10, §§4, 7, 9; FORMAL §11.** Section 9 correctly distinguishes the unconditional **one-defect** theorem from the full recursion under \(H_R\). However, §5’s unqualified “gains at most a constant” drops that hypothesis. The displayed full-recursion bound also omits **“for sufficiently large \(n\), at fixed \(\alpha\)”**, and its gain bound concerns **annealed risk**, not median or individual-net gain. **Fix:** carry all three qualifications into each conclusion. The constants \(9/16\), \(81/(256\pi)\), and the formula for \(c(\alpha)\) faithfully match round 3.

3. **Minor — PREREG Amendment 3; `scratch/run_closure.py:3–5`; `results/posthoc_closure.md`.** The cross-product removes upward bias from reference sampling, not sampling noise. For \(d=a-\mu\), output covariance \(\Sigma\), and \(N\) samples per half,
   \[
   \operatorname{Var}(U\mid W)=2d^\top\Sigma d/N+\operatorname{tr}(\Sigma^2)/N^2.
   \]
   Replaying seed 103 gives approximate normalized SE **\(6.54\times10^{-5}\)** against nMSE **\(4.72\times10^{-4}\)** at \(256^2\), and **\(3.04\times10^{-5}\)** against **\(8.40\times10^{-5}\)** at \(128^2\). Dividing by estimated \(V\), taking reciprocals, and logging do not preserve unbiasedness. **Fix:** say “unbiased squared-error numerator,” report reference uncertainty, and distinguish it from between-net variation.

4. **Minor — Summary 10, §9; FORMAL §11; `lib/closure.py`.** “Quadrature ruled out” and especially “the flattening is not numerical” are too broad. Changing node count on two selected nets does not test shared correlation clipping, cancellation in covariance subtraction, variance floors, or all configurations. Symmetrisation does not enforce positive semidefiniteness. My additional deep-net checks found **no material instability**: maximum off-diagonal \(|r|\) was 0.999906 at \(256^2\), seed 103; its worst relative negative eigenvalue was only \(−1.22\times10^{-16}\). **Fix:** report the specific convergence evidence, without claiming all numerical explanations excluded; add singular/near-singular moment tests.

5. **Minor — §9 implementation-cost claim; `scratch/run_closure.py:5–9,53`.** The arithmetic is correct:
   \[
   (60\cdot48+1130)/2=2005.
   \]
   But this is an assumed operation-cost estimate, not measured “actual cost”; mean propagation also adds roughly one pass. The \(2n\) comparison is an honest, explicitly optimistic matrix-product-only benchmark against Gaussian-input MC. “Below 0.4 everywhere” holds for **configuration medians**, not individual nets: \(128^2\), seed 103 has estimated implementation-cost gain **5.26**. **Fix:** use “estimated cost” and “median gain below 0.4.”

6. **Minor — `scratch/check_r3.py:127–136`; `logs/check_r3.log`; PROVENANCE C5.** The \(C_V\) recurrence loses precision near one. Its reported tail constant **281.6272** should approach **\(9\pi^2/2=44.4132\)**. A stable recurrence for \(1-c_j\) gives approximately **\(C_V=13.4810099\)**, so the headline **13.48** and quoted \(c(\alpha)\) survive. **Fix:** use the stable recurrence and a controlled tail estimate; do not treat the current tail calculation as numerical certification.

7. **Minor — §§8, 10; round-3 PROVENANCE entry.** Two factual errors: there are **76 closure runs**, not 84; **48 reuse E1–E3 weight instances**, so “further nets” is misleading. Round 3 started **22:17:59**, before Amendment 3’s first evaluation at **22:21:02**; it was not “asked after Amendment 3’s results.” Its prompt references the hardness-lane results. **Fix:** correct the population and chronology.

8. **Major — Summary 6, §4 Thm 7.4, §6 S1; first-review finding 1.** The report still concludes that merges do no worse than stratified sampling without controlling the displayed cross terms. FORMAL explicitly requires **equal-mass cells and negligible cross terms** for its \(D/M\) conclusion. **Fix:** retain those conditions and identify the comparator precisely; Jensen alone does not establish the unconditional comparison.

9. **Major — Short answer, Summary 6/9, §§4–5, §9; first-review findings 2, 4, 5.** “Closures are the gap” and “no point or cell method … gains more than constants” still overstate coverage: the actual-network adaptive point class remains uncovered. “All merge methods” also includes future-selected `D_best`, outside the stated past-chosen linear-rule identity. Summary 9 says ARC is rough at every measured cut, whereas §6 explicitly excludes \(l=28\). **Fix:** name the restricted classes, exclude future-selected rules, and preserve the cut exception.

10. **Minor — §8 P2 and following reading; first-review finding 8.** P2 still attributes the discrepancy to normalization, despite §10 claiming the jitter caveat was applied. **Fix:** state beside P2 that the chain’s small-angle jitter/floor and Monte Carlo uncertainty prevent attributing the whole discrepancy to inverse norms.

11. **Minor — §6 hash proposition; first-review finding 13.** “About 4 at every budget” remains incorrect: the formula gives gain \(K\) at \(T=1\), and enumeration has zero error. Arbitrary iid table values also need not form a uniformly random finite-alphabet function. **Fix:** describe \(4(K-1)/K\) as a lower bound and retain the actual iid-value model.

12. **Minor — §4 Prop. 7.7; first-review finding 16.** The report retains the wrong minus sign. Under its estimate-minus-truth convention, FORMAL correctly gives **\(+E[r(dq/d\mu-1)]\)**. **Fix:** change the sign and state the absolute-continuity, matching-marginal, and integrability assumptions.

13. **Minor — §5 E3 headline and §10 completion claim; first-review finding 15.** The \(128^2\) headline remains **0.813509**, the minimum of configuration medians, rather than **0.737594**, the median of per-net minima used by P9. **Fix:** disclose the aggregation order explicitly and distinguish the descriptive headline from the registered statistic.

14. **Minor — §10 “16 findings, each applied”; first-review finding 11.** The k-means code fix is present, but affected results were not regenerated; this is disclosed, yet “each applied” implies fuller completion. **Fix:** distinguish implemented fixes, disclosure-only responses, and outstanding corrected-result sensitivity checks.

Independent recomputation from all 76 raw closure JSONs:

| \(n\times L\) | Nets | Median gain | Geometric-mean nMSE | SE of mean log10 nMSE | \(n\sum U/\sum V\) |
|---|---:|---:|---:|---:|---:|
| 16×16 | 8 | 0.380143 | 0.078814 | 0.1393 | 0.977095 |
| 32×32 | 8 | 0.278796 | 0.037203 | 0.1973 | 0.432951 |
| 64×64 | 8 | 0.629668 | 0.0059066 | 0.3190 | 0.619373 |
| 128×128 | 8 | 3.259550 | 0.0015189 | 0.2757 | 0.208511 |
| 192×192 | 4 | 0.868137 | 0.0035793 | 0.2728 | 0.280969 |
| 256×256 | 4 | 1.018650 | 0.0017883 | 0.2242 | 0.727687 |
| 16×8 | 8 | 2.283113 | 0.013158 | 0.1421 | 0.207283 |
| 32×16 | 8 | 0.592422 | 0.026699 | 0.1650 | 0.601699 |
| 64×32 | 8 | 0.797570 | 0.0096424 | 0.0939 | 0.582310 |
| 128×64 | 8 | 0.887413 | 0.0038889 | 0.1771 | 0.344321 |
| 256×128 | 4 | 0.402872 | 0.0026002 | 0.3308 | 1.253282 |

**Registered outcomes reproduce:** B1 slopes are **−0.721008** at \(\alpha=1/2\), **−2.053687** at \(\alpha=1\); B2 growth factors are **0.388685** and **8.574545**. Thus B1/B2 pass at \(1/2\), fail at 1. B3 and B4 pass.

| Per-net log-log slope ± SE | \(n=16–128\) | \(n=128–256\) | \(n=16–256\) |
|---|---:|---:|---:|
| \(\alpha=1\) | −1.974719 ± 0.352975 | 0.526005 ± 1.293143 | −1.541357 ± 0.255167 |
| \(\alpha=1/2\) | −0.674496 ± 0.237699 | −0.580723 ± 1.127202 | −0.725419 ± 0.197577 |

Comparing the last column with \(c(\alpha)\) is the correct normalization. “0.2–1.0” describes the \(L=n\) results approximately; across both depths the range is **0.207–1.253**. These point estimates are roughly 100–913 times their respective conditional floors, but do not test the asymptotic theorem or prove \(H_R\).

All three closure tests pass. Re-executing `check_r3.py` in memory reproduces its log; the arc-cosine kernels, Gaussian fourth moment, Laplace identity, binomial sum, and counterexample formulas check out, subject to finding 6. Amendment 3/4 hashes reproduce, and their recorded registration times precede their respective run starts.

First-review findings **1, 2, 4, 5, 8, 13, 15, 16 remain incompletely reflected in the report**; **11 has a code fix and disclosure but no regenerated results**. The other findings are addressed in the reviewed text.
