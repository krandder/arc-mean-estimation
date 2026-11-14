# future-aware lane: reading notes (11:04Z, 2 Nov 2026)

## Inputs read (labels as in the sources)
- outbox/arc-update-2026-11-02.md (final 10:11Z) and work/arc-update/ (FORMAL.md A1-A6, E1-E12; PREREG.md; results/
  tables.md; lib/au.py; scratch/run_ipr2.py, run_attr.py, run_rqmc.py; HANDOFF.md; notes/ARC_SOURCES.md section 5).
  Numbers used here (MEASURED, medians over nets 200-204 at 256 x 32 unless stated): ARC k2 1.22e-3 at 393 passes,
  k2a 8.4e-4 at 452, k3f 2.0e-4 at 4.9e4; exact Gaussian recursion 1.2e-3 at 1184; radius-corrected closure (finite-
  sample recursion, rank transport) 4.9e-4 (L/n^2), and 1.9e-3, 9.2e-4 at n = 64, 128; RQMC gain over MC 1.24, 1.48,
  1.74, 2.19, 2.10 at N = 2^8..2^16; single-cut oracle Gaussian defect 6.7e-5, 1.6e-4, 2.4e-4, 2.2e-4, 1.8e-4, 1.3e-4
  at l = 1, 2, 4, 8, 16, 24; radial 8e-6 ... 1.4e-4; ~60% of the K = 2 error made by l = 8; PR3 115 -> ~1-4.
  The radial recursion's per-layer mean error (|m_l - mu_l|^2 / tr Var_l, runs/ipr2_n256_L32_s200.json) is 2e-6, 7e-6,
  2.2e-5, 4.3e-5 at l = 1-4, 2e-4 at l = 8, 4.4e-4 at l = 16: a closure's layer-l mean is already off by about its
  final error by mid depth (relevant to the hybrid's bias).
- outbox/relevance-accounting-2026-11-01.md: Theorem 1 (the future's action on the angular part is rotation-invariant
  given the past); N(l, 0.01) = 256, 192, 128, 80, 48 at l = 0, 4, 8, 16, 24; mean degree 21, 7.7, 4.1, 1.9, 1.3;
  degree-1 share 0.22, 0.48, 0.61, 0.77, 0.92; nonlinear active-subspace counts N_>=2(0.1) = 56, 24, 12, 8 at l = 8, 16,
  24, 31; top-16 active-subspace controls 1.33x at the input, 2.4x (l = 4), 4.1x (l = 8), 10x (l = 16) under the
  Gaussian replacement. Its machinery (VJPs on the cloud, whitening, the nonlinear part via E[J]) is reimplemented in
  lib/fa.py.
- ARC, "Mechanistic estimation for expectations of random products" (alignment.org, 15 May 2026; fetched 10:30Z): the
  deduction-projection loop; "mechanistic L^2 sketching" keeps the top eigenfunctions of the tail kernel
  E_f[f(x) f(x')] over the tail's LAW; worst-case error "determined by the largest unused eigenvalue". In the MLP
  setting this kernel is arc-update's Theorem A kernel |h||h'| kappa_t(u . u'); ARC's own rule therefore prescribes
  the radius first, then radially weighted angular harmonics (eigenvalues: astra r1, Q1). The realised tail kernel has
  rank <= n (its optimal sketch is the answer). Future-aware = between the two: condition on part of the realised tail.

## Reuse decisions
- Nets, truths, forward passes: import work/arc-update/lib/au.py read-only (sha recorded with the PREREG).
- RQMC and ARC kprop numbers on nets 200-204 and 300-307: reuse arc-update's runs/ (their registered results), not rerun.
- Comparators at equal cost: RQMC curves from arc-update runs/rqmc_*.json (8 scrambles per size); multilevel sampler
  ~1.0x MC at 256 x 32 [prior: unrestricted, bits-bounds]; ARC k2/k2a from runs/lad_*.json.
