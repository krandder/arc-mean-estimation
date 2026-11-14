You are gpt-6-astra, co-prover on the arc-update lane (round 3: the strongest positive lead and its ceiling). Read-only
sandbox; do not modify files. Read in /home/agent/workspaces/mats/work/arc-update: FORMAL.md (v1 plus additions E1-E8,
including how your round 2 was applied in E7), coprover/astra_r2_answer.md, logs/eval_attr_200.log (per-cut attribution
on eval net 200: b2 = squared past defect tested by the actual future, a2 = suffix error, for ARC K = 2 'simple', the
exact Gaussian recursion, the oracle moment-matched Gaussian of the TRUE layer-l law, and the oracle "radial-Gaussian"
= oracle Gaussian directions with the TRUE radius marginal by monotone transport; nMSE units, 2^19 pushes), and
logs/hr_200.log (fresh-layer radius-defect sign test). Label everything PROVEN / PROVEN UNDER <hypothesis> /
HEURISTIC / CONJECTURE; prefer a correct weaker statement to a strong wrong one.

Facts to take as given (MEASURED, one net unless stated): on 256 x 32 the oracle Gaussian single-cut defect is 1.4e-4,
3.4e-4, 4.5e-4, 6.2e-5, 1.9e-4, 6.7e-5 at l = 1, 2, 4, 8, 16, 24; with the true radius marginal it falls to 1.4e-5,
3.1e-5, 1.2e-5, 2.8e-5, 1.4e-4, 5.4e-5. ARC K = 2 'simple' total error 1.0e-3, of which the past defect at l = 4 is
7.8e-4. Fresh-layer radius defects are positive and decreasing through l ~ 8 and indistinguishable from zero at 16-24.
Along L = n/8 (n = 32, 64; 7-8 nets each) the best order-3 error over the best order-2 error is ~0.12-0.15 (about
L/n), the best order-4 over order-3 ~0.25-0.55, and the order-K cost grows ~50-150x per order.

Tasks:
1. The radial lead. Define precisely a deductive "radius-direction" closure that propagates the amplitude (radius) law
   of the cloud beyond Gaussian while keeping a Gaussian model of the direction (for instance: log|h| carried as a
   separate 1-D law, or as a Gaussian copula coordinate, coupled to the direction through tracked covariances), with
   cost O(n^3) per layer. Derive its first-layer defects in the radius feature M_0 and in M_d (d >= 2) of FORMAL A2: does
   it remove the n^{-1/2} radius defect, and what is the leading defect left (order in n)? What exponent p does that
   give at L = alpha n, and by your eq. (34) can such a closure beat the multilevel sampler polynomially (p > K = 2)?
   Is there an obstruction to propagating the amplitude law layer by layer (the gain at layer l+1 depends on the
   direction, which the Gaussian direction model gets wrong at the gate boundaries)?
2. The mid-layer angular defect: from A2 and the price spectrum (E6: b_{>=2}(t) ~ 0.06-0.12 at t = 8-16, spread over
   degrees up to ~2t), estimate how the angular part of the single-cut Gaussian defect should scale with n at fixed
   l/n and t/n, and whether it can be removed by any closure of fixed order.
3. ARC's own law. Suppose ARC's conjecture MSE_K <= c_K (L/n)^K is tight up to constants with c_K bounded below (and
   possibly growing) along L = alpha n, and the order-K cost is Theta(n^{K-1}) passes. State and prove the cleanest
   consequence for "matching sampling for all eps at depth growing linearly with width" (for example: the hierarchy has a
   precision floor min_K c_K alpha^K independent of n, below which it cannot run at all, and above which its gain over
   MC decays like n^{-(K-1)} at fixed order). Is the tightness assumption consistent with the measured per-order ratio
   ~L/n?
4. Audit FORMAL E1-E8 (the v2 additions) briefly: anything wrong or overstated?

Write everything to stdout.
