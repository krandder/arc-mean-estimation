# Response to the gpt-6-astra review, round 1 (review/review_r1_answer.md; verdict: major revision, 16 findings)

1. (critical) Conclusion exceeds the theorem's scope. Accepted. Summary and sections 5-6 rewritten: the headline is now
   the measured loss of pre-integration at every tested budget; the general statement is restricted to net-independent
   nodes and scalar weights, with its normalisation (absolute vs ensemble ratio), budget windows and information class
   stated; "escaping needs information from the weights" removed; adaptive and nonlinear methods stated as open.
2. (major) Point corollary presented too broadly for lines. Accepted: section 5 separates the point-rule ensemble
   corollary, the LP certificate (points and lines, with r_j = N (j + 1)) and the proxy-free low-degree bound.
3. (major) Degree measurements do not certify the barrier or the design ceiling. Accepted: the table is labelled
   descriptive; its last column is called a heuristic that would apply only to Haar-randomised rules; the "about 4x"
   ceiling on designs is withdrawn (section 6).
4. (major) Gaussian extension not quantitative for vector outputs. Accepted: section 5 states the Gaussian optimality
   and nonadaptivity results separately and says the per-channel quantitative bound was not derived.
5. (major) FLOP ledger inconsistent. Accepted in part: the registered nominal model is now documented (section 1) and a
   sensitivity analysis charges what the code does (scratch/cost_sensitivity.py, results/cost_sensitivity.json): PI's
   cost rises 1.6-1.8x on n = 4-8 nets, 1.07x at 8 x 256, 1.1x at n = 32, under 1% at n >= 64; fitted exponents move
   by at most 0.01; every comparison moves against PI. The SVD overcharge for P > d affects only PI_as's fixed pilot
   (about 1,000 passes at n = 4, under 5% of the fit windows' smallest budgets). MLMC's uncharged draws are stated.
6. (major) No 256 x 32 matched-slope analysis possible. Accepted: post-hoc point runs at N = 2^1..2^6 with 16
   replicates on nets 201-204 (runs/posthoc_smallN_*); scratch/posthoc_matched.py v2 merges them.
7. (major) Scorer gave final-looking verdicts to incomplete data. Accepted: scratch/score.py now checks every net's
   expected methods and registered or amended last budgets and reports PENDING until complete; fits need four points.
8. (major) Slope evidence does not establish equivalence. Accepted: registered outcomes kept as scored; post-hoc
   matched-N slopes reported with regression standard errors, as "no consistent sign, not an equivalence test".
9. (major) Window tail sampling has an MC floor. Accepted: stated in sections 1 and 6 (relative size about 1e-16 per
   line here; a budget-dependent window would be needed for an asymptotic claim).
10. (major) Constructive upper bounds treated as implemented rates. Accepted: section 3 labels them as upper bounds for
    a different algorithm; the "pre-asymptotic" explanation is removed; c^{d/2} is conditional on power-law models.
11. (major) Bias validation. Accepted: section 1 states that the bias ratio is not a calibrated z-score, that 3 flags in
    800+ cells match the t_7 tail rate, that the small nets have no truth and that RQMCJ/PIJ rest on the tail premise.
12. (major) Line variance ratio biased downward. Accepted: P2 scored as registered; section 4.3 reports how much adding
    the variance of the line average back changes it (results/scores.json, vr_corrected).
13. (major) Frozen path imports live code. Accepted as a documentation finding: lib/line.py and lib/nets.py are
    byte-identical to frozen/, lib/est.py differs only by the unused post-hoc 'jac' option; the MLMC dependency's hash
    and date are recorded (logs/deviations.txt).
14. (major) Implementation cost promoted to a necessity claim. Accepted: section 2 calls it this algorithm's cost and
    notes possible pruning; PIJ's per-vertex tail map (about 1%) and its prefix-targeted pilot are stated in section 1.
15. (minor) Labels and numbers. Fixed: degree estimator "unbiased up to a factor 1 + 1.5e-8"; surrogate exponent with
    gamma <= a and b > gamma; squared-hinge span named; nongauss.py docstring corrected; section 4.2 slope counts (four
    above, one by 0.02, two below); pass sizes 64-512 FLOPs.
16. (minor) Tests. Added four tests (chunk invariance, tail-map linearity, coincident roots, FLOP counter); all 9 pass
    (logs/test_line.log).

# Response to round 2 (review/review_r2_answer.md; verdict: major revision, 9 findings)
1. Summary merged distinct theorems; design-constant claim. Fixed: the summary separates (a) the absolute low-budget
   bound for points and lines, (b) the point-only normalised corollary, (c) the line LP certificate; the claim that an
   outer design changes only the constant is removed (section 6 says it was not tested).
2. P8 scored over unregistered MLMC budgets. Fixed: scratch/score.py and report_tables.py use the registered range
   (2^8..2^14 for S3); P8 is now 11 of 19 (still fails); validity counts use registered cells only; deviation logged.
3. Exponent conclusion too strong; promised follow-up missing. Fixed in wording ("no consistent exponent difference in
   finite windows; inconclusive about equivalence and asymptotes"). The follow-up promised in PREREG (larger N at
   n = 128) was started post hoc on 128 x 16 nets 302 and 304 (PI_as_w at 2^9..2^10 lines) but stopped because of
   machine load after net 302 reached 2^9 lines (one extra budget, 8 replicates; runs/posthoc_largeN_n128_L16_s302.json);
   net 304 was not run. Result in section 4.3. [Corrected after review round 3, which caught that an earlier version
   of this response claimed both nets and 2^10.] No slope-difference intervals beyond regression standard errors were computed (replicate vectors
   were not saved); stated as a limitation.
4. Cost sensitivity incomplete and misquoted. Fixed: split files merged (56 records), registered comparators, a third
   scenario for the SVD; numbers in section 1 are now taken from the script's output (cost x1.54-1.83 on small nets,
   exponent shifts <= 0.017 / 0.026 / 0.033, PI worse in all 56 records); MLMC not adjusted, said so.
5. Sobol o(1/N) not established for the implementation. Fixed: section 3 states the assumption (ideal nested-uniform
   scrambling, bounded gains) and that it is not shown for SciPy's LMS + digital shift; the window's C_eps/N term is
   stated; the table column is "constructive upper-bound exponents (another algorithm)".
6. Completeness checks and tests. Fixed in part: complete() now requires every budget of the registered grid and the
   registered replicate count, and missing methods leave a test pending instead of raising; the FLOP test is described
   as a check of the counter against the nominal formula, and the tail-map test as linearity only (the tail premise
   stays empirical). Not done: instrumented operation counts.
7. Bias calibration and tail-floor magnitude. Fixed in wording: the t_7 rate is labelled an illustration; the 1e-16 tail
   term is labelled a heuristic estimate, not measured.
8. Frozen execution provenance. Kept as a retrospective qualification (section 1 and logs/deviations.txt); future
   registered runs should import frozen siblings and record loaded-module hashes.
9. Labels and numbers. Fixed: b > gamma added; 836-984 passes; equivalent points are RQMC-RB points; exponent gains
   about 2/d (constructive) and 1/d (Poisson); the review line distinguishes resolved items from disclosed limitations.

# Response to round 3 (review/review_r3_answer.md; verdict: minor revision, 9 items)
1. Summary: the coefficient is now (c/2)/N; "only" removed (the wider nets' registered fits were also steeper, over
   smaller sample counts); 2. resolved; 3. this response corrected, the follow-up's reading qualified ("consistent with
   the window explanation but not establishing it"), its equal-cost ratio removed (the new budget lies beyond RQMC's
   cost range); 4. scenario A called allowance-based, "about 0.026"; 5. resolved; 6. score.py now also requires the
   replicate metadata, N = 2^p and finite positive variances, and alpha() requires four valid points (current results
   unchanged); 7. resolved as disclosure; 8. section 1 now says the file equality was checked retrospectively and loaded
   modules were not recorded; 9. the headline gives the equal-cost ranges over all common budgets (1.2-110x small nets,
   15-716x at 8 x 256, 21-2,956x ladder and 256 x 32) and names the per-net minima separately.
