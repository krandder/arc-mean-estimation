You are gpt-6-astra, co-prover on the arc-update lane (round 2: audit and lemma exchange). Read-only sandbox; do not
modify any file. Read, in /home/agent/workspaces/mats/work/arc-update: FORMAL.md (my theory v1, frozen at 04:54Z before
I read your round 1), coprover/astra_r1_answer.md (your round 1), coprover/PROVENANCE.md, notes/CHECK1.md,
notes/READING.md (prior-lane facts with labels) and lib/au.py (measurement code). Label every claim PROVEN /
PROVEN UNDER <hypothesis> / HEURISTIC / CONJECTURE and prefer a correct weaker statement to a strong wrong one.

Tasks, in order of priority:
1. Audit FORMAL v1 claim by claim: A2 (Mehler-positive, orientation-free pricing at finite width with the features
   M_d = int |h| u^{tensor d} dDelta; check the Mehler step for the vector output and the remaining-future average, and
   whether sum_d b_d = 1 holds exactly at finite width), A3 (what moment matching cancels), A4 (the Isserlis constants for
   r = 3, 4, the Frobenius lower bound for any past-measurable compression, the flattening/Eckart-Young step and the
   U-statistic for the flattening Gram), A5 (suffix-split bound and the exact last-layer bottleneck; is the claim that it
   needs no no-cancellation assumption correct?), A6, B1-B3, C1-C3, D, F1-F3, S1-S4. For each: correct / needs a
   hypothesis (state it) / wrong (give the counterexample).
2. A rigorous lower bound that covers ARC's ACTUAL K = 2 estimators at depth growing with width: extend your radius
   obstruction (round 1, eqs. 5, 8, 10, 11) to ARC's K = 2 'simple' and 'augment' at L = alpha n (and, if possible, at
   fixed (256, 32) with explicit finite-n constants). What replaces (H_R) for the 'simple' covariance rule? Is there a
   version that needs no hypothesis, e.g. via the last-layer bottleneck A5 combined with a lower bound on the
   penultimate radius defect?
3. Order K: using the radially normalised features M_d (FORMAL A2-A3), derive the leading behaviour in 1/n of an
   order-K Gram-Charlier closure's first-layer defect in M_0 and in the M_d with d > K, including whether ARC's extra
   trace for odd K and the augmented variants cancel the M_0 term; state the implied exponent p_K and what your eq. (12)
   then says about the multilevel sampler.
4. Correlation growth (FORMAL B2): is there a provable annealed statement that the order-3 cumulant tensor of h_l has
   large stable rank (for example (tr K3)^2 / tr K3^2 >= c min(l n, n) for the flattening Gram K3), via replica
   moments? If not provable now, give the cleanest conjecture and the measurement that would refute it.
5. Kelvin's hypothesis: combine your Formalisation A (exact update iff H(Z_{l+1} | Z_l) = 0; cheap transitions do not
   imply cheap law propagation) with the measured facts in notes/READING.md (near-linear threshold transitions between
   learned local codes; > 256 bits at l <= 4 for 10% error; code-law propagation bias 1e-3 to 1e-4 that does not fall
   with bits; the interim "computability-vs-slope split": ~8-10 bits per halving of error at the input against ~1-1.4
   near the output). What exactly can be concluded, and what cannot?
6. Anything in FORMAL v1 that you think is the strongest new result, and anything you think should be dropped.

Write everything to stdout.
