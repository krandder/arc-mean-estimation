# adaptive-regions: assumptions and open questions, each with its check (written 15:08Z, 2 Nov 2026)

Lane adaptive-regions, bead pool-ttdzrk.18. Kelvin (2 Nov ~15:00Z): "Here instead of 'looking for good moves' what we
are looking for are the regions that we need to understand and sample more to better estimate the mean"; earlier:
"some kind of monte-carlo thing, where we simultaneously 'learn' structure and similarity about different 'branches'".
Main's follow-up (Kelvin): "what would be needed for this algorithm to be able to really basically stop visiting some
regions?" -> settle-ability with certified bounds (IBP, CROWN), my own code.

## Assumptions (A) and how each is checked
A1. Estimand and score are arc-update's: mu = E h_L (all n outputs), nMSE = |est - mu|^2 / tr Var f, MC = 1/N.
    Check: reuse au.nmse and the truths (runs/truth_*.npz, au.load_arc_truth); MC on a dev net reproduces 1/N.
A2. For a partition with exact p_k, the stratified estimator with Neyman allocation has variance (sum p_k sigma_k)^2 / N
    with sigma_k^2 = tr Var(f | R_k) (vector f: the trace adds over outputs, Neyman is optimal for the trace).
    Check: derivation in FORMAL S1; numerical check on a dev net (sampled stratified estimator vs formula).
A3. Proportional allocation (post-stratification with exact p_k) is free: it needs only the region index of each MC
    sample. Its variance is sum p_k sigma_k^2 / N + O(K / N^2). Check: FORMAL S1; dev test.
A4. The diagnostic's ideal gains (oracle Neyman, oracle proportional) are upper bounds on what any allocation rule
    (MC-UCB, MISER, VEGAS) achieves on the same partition; bandit regret only lowers them. Check: FORMAL S1, S6.
A5. Held-out scoring removes the optimism of a tree fitted on the same samples. Check: train/held-out split; report
    both; the held-out gain is the one used.
A6. Cost: one forward pass = 2 n^2 L flops; region routing (depth D dot products of length n) costs D n flops per
    point, i.e. D/(2 n L) passes; p_k by cheap low-dimensional sampling or Genz is charged in flops too.
    Check: explicit flop counts in lib/ar.py.
A7. Width trend: beta is measured on the arc-update ladder L = n/8 (n = 32, 64, 128 on nets 300-307) and 256 x 32
    (nets 200-204). Nets 9500 (n <= 128) and 100 (256) are dev nets for choices only.

## Open questions (Q) and how each gets answered
Q1. Is there a theorem that caps the gain of ANY partition (white-box, adaptive), or only weight-independent ones?
    -> FORMAL (own proof attempts) + gpt-6-astra round 1 (independent, launched 15:07Z from a lemma-free statement).
Q2. How fast does the gain grow with K for the strongest region families, and does the growth hold as n grows?
    -> diagnostic: gain(K) and fitted beta per family per width, medians over nets, held-out.
Q3. How concentrated is the variance over regions (does Neyman beat proportional by a growing factor)?
    -> share of sum p_k sigma_k carried by the top q of regions; ratio Neyman / proportional vs K.
Q4. What does a local linear model per region add?  -> per-cell regression control variate fitted on train, scored
    held-out; and the exact local Jacobian at a cell point (white-box) as a second variant.
Q5. Branch similarity: how fast does one region's linear map stop predicting f as the input angle grows, per layer?
    -> measured relative prediction error and gate disagreements vs angle; compare with n arccos(rho)/pi per layer.
Q6. Settle-ability: what mass can be certified (IBP, CROWN) to nMSE 1e-3, 1e-4, 1e-5 as the tree grows, at what cost,
    and at which layer depth do regions of the state become certifiable?
    -> own IBP and CROWN on the tree cells (cones) and on boxes around layer-l states; covering numbers per layer.
Q7. How many full gate regions carry the mass (the cost of "understanding" exactly)?
    -> collision (birthday) estimate of the effective number of activation patterns through layer l.
Q8. Is beta > 0 uniform in width?  Decision rule (to be registered before the scored diagnostic): the full test runs
    only if the median held-out beta of the best family does not fall with n (n = 32 -> 256) and the median gain at
    the largest K grows with n or stays above RQMC's gain. Otherwise the lane reports the negative with its mechanism.
