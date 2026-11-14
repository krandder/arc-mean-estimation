You are gpt-6-astra, co-prover on the bits-bounds lane (round 2: lemma exchange). Read-only sandbox; do not modify
files. Read, in this directory: coprover/STATEMENT_r1.md (the setting), coprover/astra_r1_answer.md (your round-1
answer), FORMAL.md (Claude's theory v1, written independently before seeing your answer), coprover/PROVENANCE.md, and
lib/meanfield.py and lib/chain3.py (the mean-field and exact finite-width three-replica recursions used in FORMAL
section 5). You may also read notes/N_definition.md and /home/agent/workspaces/mats/work/relevance/DEFINITIONS.md and
/home/agent/workspaces/mats/work/relevance/FORMAL.md (a sibling lane's definition of N(l, eps) as a linear-feature
count; it is the lane's adopted N).

Tasks, numbered, every claim labelled PROVEN / PROVEN UNDER X / HEURISTIC / CONJECTURE:

1. Audit FORMAL.md v1 claim by claim (Prop 2.2, Thm 3.1, Cor 3.2, Prop 3.3, Def 4.1, Thm 4.2, Lemma 4.3, Prop 4.4,
   Thm 5.1, Thm 5.2, Def 5.3, Thm 6.1, Cor 6.2, Thm 6.3, Props 6.4-6.6, section 7, section 8, Prop 9.1, section 10):
   CORRECT / CORRECT AFTER FIX (give the fix) / WRONG (give the counterexample). Be specific about hypotheses that are
   missing. In particular check: (a) Thm 3.1's crossing count (2p - 1) against your "about 2pM"; (b) Thm 5.2's
   recursion (the decomposition Z = aX + bY + e) and the claim that c.v and |v| are preserved in the mean-field limit;
   (c) Thm 6.1's rate-distortion step for randomised quantisers and Cor 6.2's Shannon lower bound with a cubic
   distortion that depends on (|h|, |c|, angle) rather than on h - c alone; (d) Thm 6.3's claim that the forward-only /
   two-sided separation in the cell class is unbounded as eps -> 0 at a fixed net.

2. The cubic law. (a) Derive analytically the small-angle expansion of the mean-field frozen-gate residual of Thm 5.2:
   2(1 - cos psi_{L'}) = (4/(3 pi)) L' phi^3 + (next term) as phi -> 0 at fixed L', and its behaviour when L' phi is of
   order one; locate the crossover with the radial residual 2(1 - cos phi_{L'}). (b) At finite width, the exact
   three-replica chain (lib/chain3.py) gives annealed means above the mean field: at L' = 16, phi = 0.01 the ratio is
   about 3.3 (n = 64), 1.7 (n = 128), 1.04 (n = 1024), while medians are below. Explain the enhancement (a 1/n
   expansion, or heavy-tailed frozen gains along the reference path, or correlation between flip events and later
   gains), and give its leading form in L'/n if you can.

3. The rough regime. FORMAL section 5 claims that above the linearity scale (L' phi >> 1) the future merges directions
   and the states differ through gains, with the log-gain difference between two states at angle phi having variance
   ~ c phi/n (linear in phi: per-layer variance (2/n)(5 - B(cos theta_j))/4 with 5 - B ~ 2.9 theta^2, summed along the
   contracting angles theta_j). Prove or correct this (mean field plus the leading 1/n term), give c, and say what it
   implies for the radial merge residual of a cell of angular radius phi and for the decay of the M-reference residual
   D_l(M) with M (Claude conjectures M^{-1/d} rough, M^{-3/d} smooth, d ~ the cloud's effective dimension).

4. Lower bounds in terms of the adopted N (the relevance lane's linear-feature count) and of the cell count N_cell.
   Using the relevance lane's decoupling theorem (their FORMAL.md Theorem 1) and your 5.4, state and prove the
   strongest clean forward-only versus two-sided separation you can for (i) linear-feature sweeps and (ii) cell sweeps,
   for mean estimation (not only for representation), in the average case over iid He weights. If mean estimation
   needs a different statement than representation (the tower property makes the mean exact for any feature set when
   conditional expectations are exact), say exactly what the right statement is.

5. The bottleneck (your C_comp, Claude's C4). Is there any natural restricted class containing the Gaussian closure
   with gate splits and ARC's cumulant propagation for which you can prove, at L = alpha n, that the error does not
   fall faster than the best multilevel sampler at equal cost? For example: show that the K = 2 Gaussian closure has an
   nMSE floor of order c/n (measured about 0.12/n in the stationary regime) and that order-K closures have floors
   c_K n^{-a_K} with a_K bounded, or refute this. State the weakest conjecture that would close C_comp and its
   cheapest test.

6. Anything in FORMAL v1 that is new to you and that you can strengthen, and anything in your round-1 answer you now
   consider wrong.

Be rigorous and concise; prefer a correct weaker statement to a strong wrong one. Write everything to stdout.
