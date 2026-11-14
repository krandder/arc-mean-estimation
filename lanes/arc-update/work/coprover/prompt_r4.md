You are gpt-6-astra, co-prover on the arc-update lane (round 4: the radius-corrected closure as a full recursion).
Read-only sandbox; do not modify files. Read in /home/agent/workspaces/mats/work/arc-update: FORMAL.md (v1 plus
additions E1-E11; E10 is how your round 3 was applied), coprover/astra_r3_answer.md, PREREG.md Amendments 4-6, the
section "4.4 The strongest lead" of arc-update.md, scratch/run_ipr2.py and scratch/run_width.py. Label everything
PROVEN / PROVEN UNDER <hypothesis> / HEURISTIC / CONJECTURE; prefer a correct weaker statement to a strong wrong one.

Facts to take as given (MEASURED, registered; medians over nets; nMSE units; L = n/8):
- Single cut, oracle radial-Gaussian (true mean and covariance, Gaussian directions, true radius marginal by monotone
  transport, exact network afterwards): at l = 1 it falls like n^-2.5 over n = 64-256 (1.0e-4, 3.1e-5, 3.3e-6); at the
  mid cuts l = n/32, n/16, 3n/32 (mean of the three) like n^-0.67 (3.6e-4, 2.6e-4, 1.4e-4). The plain oracle Gaussian
  at l = 1 falls like n^-0.95.
- Full recursion with exact per-layer moments (each layer: exact one-layer push of the closure's own state from 2^19
  samples, then projection; two replicates, cross-product debiased): Gaussian projection 2.1e-3, 1.6e-3, ~1.2e-3 and
  radial-Gaussian projection 1.8e-3, 9.6e-4, ~4.8e-4 at n = 64, 128, 256 (at 256 x 32 four nets so far, rank
  transport, replicate noise 7e-6-4e-5). ARC's K = 2 'augment': 1.3e-3, 1.0e-3, 8.4e-4. Finite-width radius weight
  b_0^{(256,t)} = 0.82, 0.91, 0.95 at t = 8, 16, 31; |Y|^2 / tr Var = 15-28 at 256 x 32.

Tasks:
1. Write the radial closure's full-recursion error with A1 as a sum of its OWN one-step projection defects, each priced
   by A2 with the remaining depth. Under explicit hypotheses on the closure's states (state them), give the order in n
   of one step's priced defect after the radius is fixed (your round-3 first-layer analysis gives n^-2 at l = 1; what
   at a middle layer, where the cloud is concentrated in a cap?), and the conditions (a Gram / no-cancellation
   criterion, or independence across layers) under which the total is Theta(alpha / n), i.e. p_full = 1. Is the
   measured p_full ~ 0.95 (and the Gaussian recursion's ~0.4) consistent with that, and with your eq. (34)?
2. The next order in this radial setting: is there a matrix-cost family (O(n^3) per layer, or O(J n^3)) whose one-step
   defect after the radius is fixed is o(n^-2) (e.g. adding the diagonal third cumulant, or the trace sector of M_3)?
   If the cheapest fix needs the full third cumulant, what does ARC's measured ladder (cost x ~n, error / ~4-8 per
   order at L = n/8) imply for the radial closure's error-cost exponent?
3. Amplitude accuracy. With b_0 ~ 0.95 and |Y|^2 / tr Var ~ 20, derive the per-layer relative accuracy of the radius
   law needed for nMSE eps after L layers (independent vs systematic errors), and what it implies for the number J of
   quadrature nodes in your eq. (40) (state the quadrature and its error law).
4. Audit E10, E11 and section 4.4 of arc-update.md briefly: anything wrong or overstated?

Write everything to stdout.
