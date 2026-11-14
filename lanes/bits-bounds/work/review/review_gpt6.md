codex
**Verdict: major revision.** The core residual formulas and most numerical summaries check out. The claimed lower bounds, algorithm classifications, cost comparisons, and one registered score need correction. Read-only review completed at 2026-11-01 22:24 UTC; no files modified.

1. **Major — `FORMAL.md:208–216`, report Summary 6: “references are samples” is overstated.** The expansion and Jensen inequality establish an **upper bound** under negligible cross terms, not equality with stratified sampling or a “no better than” lower bound. Residual means can cancel despite positive residual second moments. **Fix:** retain the identity; remove the claimed equivalence and impossibility conclusion unless additional lower-bound assumptions are proved.

2. **Major — `FORMAL.md:217–239`, report §4: Theorem 7.5’s rate is not established.** A cubic diagonal expansion alone does not supply the asserted Sobolev kernel-quadrature lower bound; the text explicitly leaves its hypotheses unchecked. Specify spectral/coercivity conditions, source geometry, allowed derivative orders, and a precise applicable theorem. The Gaussian surrogate does not cover adaptive queries to actual finite-width networks, so closures are not the only uncovered class.

3. **Major — `FORMAL.md:247–253`, report §4: Proposition 7.8 is not a computational lower bound.** Maintaining a matrix does not inherently require matrix multiplication, and an arbitrary order-\(K\) closure need not use the stated dense contraction algorithm. **Fix:** present \(n^{K-1}\) passes as the cost of a specified implementation; withdraw universal “whatever its accuracy” conclusions for the whole closure class.

4. **Major — `scratch/run_eval.py:101–112`, report §§3–4: `D_best` is not fully forward-only.** Its frozen/radial choice uses `Af`, hence the actual future. Past-chosen references do not make these future-trained merge weights past-measurable. **Fix:** label this variant accordingly and apply forward-only bounds only to fixed F/R or the past-measurable `rule`. Two-sided assignment also uses the test output (`:129–136`), making it a representation oracle, not a cheap estimator.

5. **Major — report Summary 7–10 and §§6–7: measured failures become unsupported universal claims.** One k-means construction failing with 256 references does not show “no set” succeeds. Four measured cuts do not establish “every layer”; two widths at \(L=4n\) cannot establish that gains never grow with width. PR is not the source dimension required by the bounds, and a fitted suboptimal method’s decay exponent need not lower-bound the optimal exponent. **Fix:** restrict these statements to the tested constructions, cuts, sizes, and precision range.

6. **Major — `scratch/run_eval.py:219–226`, `scratch/run_ml.py:95–110`: cost accounting omits material work.** Setup does not include the promised fit-prefix cost or clustering; per-sample costs omit reference assignment. Frozen level-one samples can legitimately be aggregated before applying each frozen suffix, but that implementation and its setup must be priced explicitly. **Fix:** retain current ratios as ideal propagation-only comparisons and add complete costs before claiming practical gains.

7. **Major — `PREREG.md:54–55`, `scratch/score_prereg.py:156–162`, report §8: P8 tests a stricter condition than its registered wording.** The registered endpoint decrease holds on **64/64 nets**; the scorer instead requires monotonicity across all four cuts, obtaining **39/64**. **Fix:** score the endpoint prediction as written, or disclose the interpretation change and report both. Under the endpoint reading, the main score becomes **3 hits, 8 misses**.

8. **Major — `lib/chain3.py:29–41`, report P2 interpretation: the numerical chain is not an exact benchmark at the smallest angles.** Jitter introduces residual even when \(\phi=0\): at \(n=32,t=16\), 4,000 chains with seed 80 give mean frozen residual **\(1.636\times10^{-12}\)** instead of zero. Actual scored bins reach median angles around \(5.74\times10^{-6}\). Output floors also act after different rescalings in the chain and nets. **Fix:** use stable residual coordinates, specify identical regularization, and quantify numerical and Monte Carlo error; do not attribute the entire discrepancy to inverse norms.

9. **Major — `FORMAL.md:189–197`, report §§1–4: normalization is insufficiently specified.** Absolute annealed distortion, \(E[\mathrm{error}^2]/E[V]\), per-net normalized error, and medians of per-net ratios are different quantities. Measurements use \(V_{\rm ang}\), whereas the opening criterion concerns Gaussian inputs. **Fix:** define each criterion explicitly and give the radius conversion:
   \[
   V_{\rm Gaussian}=m_n^2V_{\rm ang}+(n-m_n^2)E\|A(U)\|^2.
   \]
   The rate-distortion threshold needs a deterministic distortion budget, not an unspecified future-dependent \(V\).

10. **Major — `FORMAL.md:101–106`: the claimed MPS inclusion of arbitrary cumulant closures is undefined.** A truncated cumulant list does not automatically define a signed measure or a nonlinear push-forward. The telescoping identity is correct when the pairings exist. **Fix:** specify a measure-valued reconstruction or a valid functional calculus before applying it to all four families.

11. **Minor — `lib/bb.py:104–119`: k-means can return stale training labels.** When the iteration cap is reached, labels precede the final center update. In the \(32\times32\), seed-100 replay, recomputing final labels changes the layer-24 two-sided \(M=16\) `D_best` from **0.0421501 to 0.0436199**. **Fix:** recompute assignments before returning and regenerate affected results.

12. **Minor — `scratch/run_ml.py:43`: “best subset” excludes the empty subset.** Plain MC is therefore unavailable even when every hierarchy loses: the independently reproduced seed-100 \(32\times32\) optimum is **1.187981**, versus **1** for the empty hierarchy. **Fix:** include it or consistently say “best nonempty hierarchy”; distinguish forced-reference losses from the best available sampler.

13. **Minor — `FORMAL.md:289–298`, report §6: the hash formulas are correct, but the prose is not precise.** “About 4 at every budget” confuses a lower bound with the actual gain: at \(T=1\), the gain is \(K\); enumeration gives zero error. Arbitrary iid values are not necessarily a uniformly random finite-alphabet function. **Fix:** state \(K\ge2\), finite variance, distinct queries, the annealed criterion, and the comparator. Present the unknown-bias result separately as a minimax table theorem; remove “hard exactly when.”

14. **Minor — `scratch/posthoc.py:17–28`, report cell-bit tables: these are interpolated estimates, not registered grid counts.** The code interpolates between tested \(M\) values and chooses the better M=1 merge using test residuals. **Fix:** disclose both choices beside the table and distinguish them from registered `D_best` grid counts. “Zero bits at \(7L/8\) for \(L\ge n\)” also needs a precision qualifier: \(32\times32\) has median **1.7 bits at \(\epsilon^2=0.01\)**.

15. **Minor — report §§4–5, §8; `FORMAL.md:214–215`: several summaries need correction.** E3 headlines minimize configuration medians, whereas registered P9 minimizes per net first: \(128\times128\) gives **0.813509 versus 0.737594**, respectively. F1 contains **44 overlapping nets plus 8 new nets**, not 52 plus 8. P5 has **17 passing groups and 10 failing groups**; say so explicitly. FORMAL’s bias-ratio counts remain stale at 414/282 instead of **453/315**.

16. **Minor — remaining theorem hypotheses:** state integrability for Thm 4.2, nonzero references and a boundary convention for Lemma 4.3/Thm 5.1, and \(n\ge2\), fixed finite \(t\), \(\phi\to0\) for Prop 5.3. Prop 7.7 requires \(q\ll\mu\), matching feature marginals, and finite relevant moments; under the report’s `estimate − truth` convention its displayed sign should be positive. Cor 7.2’s regularity/entropy assumptions must apply to the **radius-weighted angular law**. With these qualifications, I found no algebraic error in the principal one-layer, mean-field, finite-width cubic, or angular quantization formulas.

Independent recomputations from `runs/`:

| Quantity | Recomputed |
|---|---:|
| PR fit | \(1.043694(n/l)+1.378591\), \(R^2=0.961277\) |
| \(D_{\rm best}(256)\), \(128\times128,\ l=64\) | 0.006502779 |
| Corresponding squared sample-mean residual | 0.0000603866 |
| Rough bias/\((D/M)\) median | 0.822811; 453 entries |
| E3 random-reference minimum configuration median, \(128\times128\) | 0.813509 |
| F1 random-reference median gain, \(256\times256\) | 2.431625 |
| P1 slope median; passing fraction | 2.907351; 133/169 |
| G1 width medians; stability factor | 1.017598, 1.767184, 0.499956; 2.035374 |

All seven existing tests pass. E1 seed replay and an independently enumerated F1 hierarchy reproduce saved values exactly. Both generated tables and the ML/gain score files reproduce in memory.

Registration chronology is consistent with the recorded run starts: main hash **21:32:27 < 21:32:31**, Amendment 1 **21:45:37 < 21:51:21**, Amendment 2 **22:04:20 < 22:04:27**. Historical document prefixes reproduce their hashes. The main scorer was hashed **after outputs existed**; timestamps cannot verify its narrower “before reading” assertion. Amendment 3 was appended during this review and is outside the reviewed report’s scope.
