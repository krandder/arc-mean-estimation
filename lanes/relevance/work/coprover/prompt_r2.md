You are the co-prover and auditor (gpt-6-astra, round 2) for the relevance-accounting lane. You MAY now read the whole
directory /home/agent/workspaces/mats/work/relevance/ (read-only). Your round-1 answer is coprover/astra_r1_answer.md;
how I used it is in coprover/PROVENANCE.md. Theory: FORMAL.md (v1 frozen 21:17:35Z; v2 appended, frozen before this
round, see logs/freeze_times.txt). Definitions: DEFINITIONS.md. Registrations: PREREG.md Parts 1-2 with hashes in
prereg_hashes.txt (frozen copies in frozen/). Code: lib/rel.py, lib/accounting.py, lib/gates.py, lib/theory_v1.py,
lib/theory_v2.py; runners scratch/eval_part1.py, scratch/eval_part2.py; scorers scratch/score_part1.py,
scratch/score_part2.py; data runs/eval_*.json, runs/p2_*.json; scores results/part1_scores.json (and part2 when present).
You may run small computations (python3 or /home/agent/.venvs/arc-noisy/bin/python, one thread, minutes). Label every
claim PROVEN / PROVEN UNDER <hypothesis> / NUMERICAL / HEURISTIC / CONJECTURE; number your answers T1..T8.

T1 (theory audit). Check FORMAL v1 and v2 line by line: Theorem 1 and Corollaries 1a-1c, the identities of section 2,
the degree-spectrum formulas (3a-3c), the generic-capture model (4b, v2.4), the N rule (4c, 4d), v2.1-v2.6. List every
error, overclaim or missing hypothesis, with the fix.
T2 (estimators). Audit the measurement code: pick-freeze residuals with independent future-noise pairs, the U-statistic
for |E[a Z^T]|^2 and its jackknife, the Mehler curve, the active-subspace matrices (vector and scalar), the true-law
projection residual, the exact-identity parts, the gate-count construction (mixed forward pass, orderings, the
cross-realisation products for sigma > 0), N_>=2 along the nonlinear active subspace, and the split-sample N_1. Bias,
wrong normalisation, or mismatch with DEFINITIONS/PREREG?
T3 (scoring). Does score_part1.py implement PREREG Part 1 exactly (P1-P11), and score_part2.py Part 2 (PG1-PG3, PS1,
PS2)? Recompute three or four reported numbers independently from runs/.
T4 (lower bound). Is "debiased eigenvalues lambda_hat_j - tr Var(a)/P" the right correction for the first-chaos tail?
Give a valid (conservative) lower confidence bound for sum_{j>k} lambda_j(C_1) from the data the runs store, or say what
must be stored.
T5 (higher degrees). Prove or refute a lower bound on N(l, eps) for the optimal (possibly future-informed) projection when
the degree >= 2 part is a sum of many rank-one gate terms with Gaussian (Haar) normals: e.g. a Wishart-type argument
showing that capturing 1 - eps' of a degree-2 part made of G >> r gates in effective cloud dimension r needs about
(1 - eps') r directions. Under what conditions on G, r and the weights does it hold?
T6 (stationary slow mode). At large t one direction explains 95-99% of V_l but is not the radius (overlap 0.6-0.95 with
the mean direction in whitened coordinates). Identify this direction theoretically (e.g. the top right singular vector of
the noise-averaged future Jacobian, or the gradient of the slow amplitude response), predict the residual left after it,
and the decay rate of V_l at large t (5/n, 5/(2n) + 1/Q, or other). Use runs/eval_stat_*.json.
T7 (gates). Predict how G(l, eps) (number of future gates needed, PREREG Part 2) scales with n, l, L and eps, and whether
"many gates (more than n) with overlapping normals" or "few gates spread over many directions" explains the large N.
T8 (red team). Attack the report's main claims as they stand in FORMAL v2 sections 5-6 and v2.1-v2.6, in particular the
M1 conclusion ("resolving the relevant bits is not a route to beating sampling at ARC's shape; the obstruction is the
spread degree >= 2 part"). What is wrong, overstated, or untested?
