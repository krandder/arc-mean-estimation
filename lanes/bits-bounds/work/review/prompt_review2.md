You are an adversarial reviewer (fresh session; you have not worked on this lane). Read-only sandbox; do not modify
files. A first review (review/review_gpt6.md, 16 findings) was applied; since then a closure test and a third
co-prover round were added. Review the new parts of the report /home/agent/workspaces/mats/outbox/bits-bounds-2026-11-01.md
(the short answer and item 10 of the summary, the closing scorecard paragraph of the summary, section 4's last bullet,
section 7's last bullet, section 8's rows B1-B4 and the reading under the table, section 9's closure bullets, section 10)
and their support in this directory: FORMAL.md (section 0 item 9, the closures row of section 10, section 11 C4),
PREREG.md (Amendments 3 and 4) and prereg_hashes.txt, lib/closure.py, tests/test_closure.py, scratch/run_closure.py,
scratch/score_closure.py, scratch/score_closure4.py, scratch/check_r3.py, scratch/check_quadrature.py,
results/closure_scores.json, results/closure4_scores.json, results/posthoc_closure.md, results/quadrature_check.jsonl,
runs/closure_*.json, logs/queue_closure4.log, logs/check_r3.log, coprover/astra_r3_answer.md and the round-3 entry of
coprover/PROVENANCE.md.

Check, and report numbered findings (each: severity major/minor, location, what is wrong, the fix):
1. Is the report's statement of the round-3 results faithful to coprover/astra_r3_answer.md: what is unconditional,
   what holds only under (H_R), the constants (9/16, 81/(256 pi), c(alpha), C_V), and the reading "gain bounded by a
   constant at the recursion's own cost"? Is any conditional result presented as unconditional?
2. Recompute from runs/closure_*.json: the registered B1-B4 outcomes, the medians quoted, the per-net geometric means
   and the log-log slopes with their standard errors, and the annealed ratios n E[err^2]/E[V].
3. Is "the error stops falling, so the gain peaks (H_peak)" warranted with 4 nets at n = 192 and 256 and per-net
   gains spread over two decades? Is the comparison of the measured annealed ratio with c(alpha) stated correctly?
4. Cost accounting: is the gain (1/(2n))/nMSE an honest comparison with Monte Carlo at the closure's matrix-product
   cost? Is the implementation-cost figure (about 2005 + 2n passes) computed as described?
5. Numerics of lib/closure.py: the Drezner quadrature, clipping of correlations, floors, symmetrisation; is the
   quadrature check (48 against 128 nodes on two nets) enough to rule out numerical causes of the flattening? Any
   other numerical issue at n = 192-256, L = n (near-degenerate covariances, correlations near 1)?
6. The cross-product estimator (a - mu1).(a - mu2): unbiasedness, and its noise relative to the reported per-net nMSE
   at n = 256 with 2^15 inputs per estimate.
7. scratch/check_r3.py: are the formulas right (degree-1 and degree-2 arc-cosine kernels, the Gaussian fourth moment,
   the Laplace identity for E|G|, the binomial sum for a_n, the iteration for C_V)? Do its outputs support the claims
   logged in PROVENANCE?
8. Were the 16 findings of review/review_gpt6.md applied in the report's sections 1-10? List any that are not.
9. Overclaims or missing caveats anywhere in the new text.

Verdict: accept / minor revision / major revision. Be concrete and concise. Write everything to stdout.
