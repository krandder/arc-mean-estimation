## 9. Pre-registration scorecard

Registrations: `PREREG.md` (Part A 21:15:54Z, Part B 21:21:14Z, Part C 21:24:21Z, Amendment A1 21:33:29Z, Amendment C1
21:51:59Z; hashes in `prereg_hashes.txt`, copies `coprover/PREREG_*_as_hashed.md`). Scorers `scratch/score_A.py`,
`score_B.py`, `score_C.py`; results `results/part{A,B,C}_scores.json`.

| id | prediction (short) | result |
|---|---|---|
| PA1 | SD(ell) n^{1/3} in [1.70, 2.05] at n = 1024 (limit 1.887), non-decreasing from n = 64 | hit (1.875) |
| PA2 | E[ell^2 | q] n^{2/3} within 25% of the limit in every bin, n = 1024 | hit (within 1-8%) |
| PA3 | median delta/delta* in [0.97, 1.03] at n >= 64; n^{2/3}(mean - 1) constant within 2x | miss (median 0.962, 0.969 at n = 64, 128; mean - 1 falls faster than n^{-2/3}) |
| PA4 | SD(delta/delta*) n^{1/3} in [1.5, 2.4], max/min <= 1.4 over n = 64-1024 | hit (1.65-1.83) |
| PA5 | sharing curves vs closure and each other; antithetic within 10% of 2^{2/3} | {{PA5}} |
| PA6 | 1/e lags: log q in [0.8n, 3.2n], ratio and angle within 2x of their rates | miss (log q at 0.78-0.80 n: n = 64 and 1024 just below 0.8n) |
| PA7 | triangle spread within 25% of 1.46 sqrt(2/PR) | {{PA7}} |
| PA8 | cloud moments of a 1/k spectrum (r3 and PR within 25%) | miss (radius-normalised PR 27% below 1/k at n = 64{{PA8X}}) |
| PA9 (A1) | PR_w slope between n = 256 and 1024: n^{2/3} (> 0.5) or 1/k (< 0.5) | {{PA9}} |
| PB1 | closed relevance half-life and area within 30% of the mean field, n = 64-1024 | registered analysis missed (coarse grid; full-grid area integrates noise: -1.28 at n = 256, 66.7 at n = 1024); revised analysis hit (interpolated half-life, area truncated at 8 T*; chosen after seeing n = 256) |
| PB2 | total relevance half-life within 30%, value at 4 T* within 2x | hit |
| PB3 | closed and total PR at t = 1, 2, 4 within 1.5x of the free product, n = 64, 256 | miss (11 of 12 clauses; total PR at n = 64, t = 4 is 1.58x) |
| PB4 | log|a| relevance above the direction's at every t >= 8, > 0.2 at t = n/2 | miss (both near zero at n = 64, t = 160-192, and n = 256, t = 1024; holds at n = 1024) |
| PB5 | perturbation survival within 30% of the mean field (eps = 0.1, 0.3); tangent >= 2x finite at t = n/4 | {{PB5}} |
| PB6 | input-cloud PR within 20% of the vertex recursion, n = 64, 256 | hit (8 of 8, within 1-17%) |
| PB7 | radius share of log-amplitude within 25% of the kernel, 256 x 32 | hit (7 of 7, within 4%) |
| PB8 | extinction (1 - 2^-8)^l within 3 SE at 8 x 256 | hit (code check) |
| PC1 | across-net CV of the cloud size within 30% of the chain's, which rises toward 0.68 | hit |
| PC2 | chain's annealed cloud size within 2.5 SE of the nets' mean | hit |
| PC3 | dividing by delta*(Qbar) at least halves the across-net CV at n = 64-256 | hit (0.57 -> 0.20, 0.47 -> 0.16, 0.75 -> 0.14) |
| PC4 | median per-net PR within 25% of the chain's PR_w; per-net PR CV < 0.35 | miss (0.67, 0.71 at n = 128, 256: variance weighting) |
| PC5 | per-net V_P(8) tracks the radius (Spearman > 0.5); within 0.12 of the per-radius mean field | hit |
| PC6 | annealed V_P below the nets' median at t = 4, 8 | hit |
| PC7 (C1) | per-net radial share within 30% of rho(q); Spearman > 0.6 | hit (median deviation 5-12%, Spearman 0.89-0.99) |

{{SCORE_TOTAL}} The misses are of three kinds: bands that did not allow for noise or grid resolution (PA6 by under 3%,
PB4 at t >= 160, PB5 {{PB5_KIND}}); a finite-n effect larger than predicted (PA3, the angle's level converging from below);
and two substantive findings, both about the cloud's dimension: the 1/k spectrum fails (PA8; the four-point law replaces
it), and the variance-weighted annealed dimension overstates the typical net's (PC4), with the linear free product
undercounting it beyond a couple of layers (PB3).

## 10. Process

- Co-prover gpt-6-astra (`coprover/PROVENANCE.md`; every raw log shows "model: gpt-6-astra"). Explainer check
  (20:51-20:56Z, high effort): 27 findings, 13 errors, all applied to the explainer. Round 1 (21:07-21:31Z, xhigh,
  independent; told not to read this lane's directory): it agreed independently on the scaling limit, the 1.887 n^{-1/3}
  radius ratio, the 5/8 spectral gap, the relevance curves, the free-position formula and the input vertex recursion; new
  from it: the closed form m(q), the second-order angle coefficient, the n^{2/3} cloud dimension (the most consequential
  addition; I re-derived it and registered it against 1/k in Amendment A1 before the decisive runs), the radius-ratio
  effect under shared noise, and the tau^{-3} vs tau^{-5} annealed/quenched contrast. My theory v1 was frozen at
  21:14:08Z, before its answer existed.
- Pre-registration as in section 9. Disclosed before Part A: exploratory runs at n <= 256 informed PA3, PA4, PA7.
  Amendment A1 (21:33:29Z) was hashed before the n = 256 four-replica result existed but about six minutes after that run
  had started (21:27:34Z); I had not seen its output. Its n = 512 and 1024 tests are prospective.
- Deviations (`logs/deviations.log`), none hidden: (1) partB.py's input-mode alive flag was always true (fixed 21:30Z;
  affected only the n = 8 extinction field and n = 8 direction statistics; the buggy output is kept); (2) the registered
  8-replica closed-PR design shared futures across the two past pairs, which biases the closed estimator; it was
  replaced by a 10-replica four-future design before any such run (registered copy kept); (3) PB1's scoring
  (interpolated half-life, area truncated at 8 T*) was changed after seeing the n = 256 curve and is reported both ways;
  (4) score_C.py first treated the per-net radius Q as q (fixed before any Part C result was used); (5) queues were
  restructured to respect the two-process limit at load 20-35: r6 at n = 256 and r3 at n = 512, 1024 were dropped, share
  at n = 1024 ran last, r4 at n = 1024 before 512, and one early third process was stopped after a minute when the load
  rose above 16; (6) an inputVP mode (small-sigma closed relevance) was added after registration and is descriptive;
  (7) Part C's header time was typed one minute ahead of its hash; (8) the sharing runs (A-share) used a 2n burn-in and
  4n recorded layers instead of the registered 6n and 8n, omit t = 0.9, 0.99 at n = 1024, and were first scored against
  each run's own baseline instead of the registered A-r2 baseline (rescored with the registered one; every clause
  passes either way at n = 64, 256); the six-replica runs used half the registered chain budget; (9) the input vertex
  recursion first interpolated its Monte Carlo source on a coarse grid in c, which made it collapse at depth; recomputed
  by quadrature (`scratch/vertex_exact.py`), which changes the deep-layer comparison (section 4.1) but not the registered
  targets at l <= 64 by more than 2%; (10) log|a| needs a convention on the all-off output event (floors at 1e-300, which
  differ between Parts B and C); immaterial at n >= 64, fatal for the log channel at n = 16, which is not used.
- Compute: CPU only, nice 19, ionice -c3, at most two heavy processes (the machine's load was 15-35 throughout), one BLAS
  thread; no GPU.
- Review: GPT-6 (gpt-6-astra, fresh session, high effort, read-only; `review/review_gpt6_r1.md`, 00:10-00:15Z) on the
  near-final draft: verdict major revision, 14 findings (13 major or minor problems, one confirming that the central
  measurements and all 19 tests reproduce). It reproduced the n = 1024 stationary numbers, the four-replica PRs and PB5's
  98 of 100 clauses. Changes made: (1) the log|a| convention is stated and the "annealed raw quantities do not exist"
  claim narrowed to the divergent moments (section 1); (2) the vertex recursion's source is now computed by quadrature
  and section 4.1 no longer attributes its deep-layer gap to a breakdown of the 1/n expansion; (3) the scorecard tallies
  corrected (at that time 14 hits, 7 misses, 3 pending; final tallies in section 9) and PB1 reported both ways; (4) Amendment
  A1's timing stated exactly; (5) the sharing-run deviations disclosed and PA5 rescored with the registered baseline;
  (6) the direction theorem restricted to perturbations of layer l with matched Gram relations, the Haar frame of the
  nonlinear relevance operator labelled HEURISTIC, output coordinates excluded (section 7); (7) the orientation bit
  count presented as a description length, with PR not equal to the rank and no claim that an estimator must encode it;
  (8) the tangent check described as one moment ratio, with the probe corrections; (9) V_P described as the full state's
  closed relevance for the output direction, PRs as annealed moment ratios, the radial share as a variance-component
  proxy; (10) "within a few percent" limited to the relevance curves, PR_C T* given at finite Q; (11) the cloud-size
  scatter statistic stated as a squared-CV reduction and R^2 (0.88-0.93); (12) 168 nets, c ranges, PB4's failing
  points, n = 8 PR conditioning, and the vertex normalisation corrected; (13) completion criteria for the pending items
  stated (section 2.4, 9). Round 2 (fresh session, 01:42-01:46Z; `review/review_gpt6_r2.md`): verdict major revision
  on residuals; it judged findings 2, 4, 5, 8, 11, 12, 14 resolved, reproduced PA9 exactly (slope 0.6143, 90% interval
  0.599-0.629; an independent 10,000-resample bootstrap gives 0.599-0.630) and the available PA5 clauses at n = 1024,
  and asked for: the M1 paragraph to state the bit count only conditionally (if a generic rank-k subspace had to be
  encoded) with no implication for estimators; the frozen-Jacobian / nonlinear-operator distinction in the summary and
  3.3; "or the mean direction" removed from the invariance statement; V_P described as explaining the conditional mean
  of the output direction, not E[a]; "within a few percent" replaced by absolute errors; PB1 marked as revised-analysis
  wherever it says hit; PA7 shown as pending, not failed, in the scores; the direction convention on extinction stated;
  the n = 256 mean-order column recomputed with the registered baseline (4.06 / 4.06 / 3.34). All applied. After round 2
  the remaining registered runs landed (PA5 at n = 1024: hit; PA7: in band at every width run; the third-moment part of
  PA8); they were scored by the unchanged registered scorers and were not re-reviewed.
