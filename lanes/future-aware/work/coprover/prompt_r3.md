You are gpt-6-astra, co-prover on the future-aware lane (round 3: an audit). Read-only sandbox; do not modify files.
Read in /home/agent/workspaces/mats/work/future-aware: FORMAL.md sections E9-E12 (and E1-E8 for context),
coprover/astra_r1_answer.md and coprover/astra_r2_answer.md (your earlier rounds), scratch/run_cut.py,
scratch/run_ridge.py, lib/fa.py (CondProjector, features), and the run files runs/ridge_n64_L8_s30*_x.json and
runs/cut_n64_L8_s30*.json. Label everything PROVEN / PROVEN UNDER <hypothesis> / HEURISTIC / CONJECTURE; prefer a
correct weaker statement to a strong wrong one.

Audit, claim by claim, with severity (major / minor) and a concrete fix:
1. E10: the exact identity for the "k features exact, linear-Gaussian complement" projection (is the whitened split
   z_Q = P_B z + eta, eta ~ N(0, P_perp) independent, correct for CondProjector as implemented? is the Hermite identity
   right, including convergence conditions and the |alpha| <= 2 cancellation?).
2. E11: does the ridge experiment (independently permuted whitened feature coordinates) test what it claims, and does
   the conclusion "the future reads the joint dependence inside the span, not k one-dimensional laws" follow? Note that
   permuting whitened coordinates keeps their covariance only in expectation, and that the complement is regenerated
   from the permuted features.
3. E12: the random-sign pricing bound for future-chosen spans: is the statement correct as written (the adapted-basis
   identification of "alpha inside V" with P_V^{tensor d}, the use of your flattening bound on the Hadamard-product tensor
   H_d, the normalisation of Hermite coefficients versus tensors, the independence assumption)? Give the strongest
   correct version.
4. E9 as written: does it represent your round-2 answer correctly?
5. Anything in E1-E12 that is now inconsistent with the dev/eval facts the files show.
Write everything to stdout.
