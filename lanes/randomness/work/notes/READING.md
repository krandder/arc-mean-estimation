# Prior-lane facts used by the randomness lane (labels as in the source reports; outbox/ unless noted)

- unrestricted-estimators-2026-10-31.md
  - 3.1 Determinism is free on random weights: QR of three rows of W_1 frees 3n - 6 Haar angles independent of the
    reduced net; X_i = Phi^-1((U + iV) mod 1) pairwise independent N(0, I_n), risk exactly V/N; any randomized
    estimator simulable deterministically at the same average risk (extra O(n^3)); digit seeds frac(2^k w) as k grows.
    PROVEN UNDER exact-transform / digit-splitting primitives; only approximate with finitely many bits per weight.
  - 3.5 Fixed rules: risk = kernel discrepancy with k(t) = E_W <g(u), g(v)> = sum_d b_d t^d, b_d >= 0 (PROVEN).
    Positive designs: gain over RB-MC <= 2 (1 - q) / sum_{s: tau_2s <= 1/(2N)} b_2s (PROVEN, astra); mean field at
    L = alpha n: even tail = half the angular variance, gain <= ~4 (PROVEN in mean field). MEASURED (M2, L = n/4 and
    256 x 32): f1 + f2 = 0.30-0.43 at 256 x 32, 2-design ceiling 1.7 over RB-MC; plug-in even tail above degree 2:
    0.48 of the angular variance at 256 x 32 (post hoc, 3 nets; a_2 estimate negative there).
  - Deterministic centred Sobol beat scrambled Sobol 2.7-4.5x at widths 3-8 (P7 refuted its band; 54 nets).
  - Multilevel shared-trajectory sampler (lib/mlmc.py): gain Omega(n / log^2 n) at L = alpha n PROVEN UNDER layerwise
    cost hypotheses; ideal ratio 1.06 at 256 x 32 (no gain).
- bits-bounds-2026-11-01.md, 8.1-8.2: full multilevel with one reference: gains 1.21, 1.41, 1.58, 2.43 at L = n
  (n = 32-256), 0.99 at 256 x 32; several references help only at L >= 4n (MEASURED, registered, optimistic: best
  level subset chosen on the same split, setup excluded).
- nd-exact (work/nd-exact/nd-exact.md): at 8 x 256, from layer 20-48 on every sampled input shares one downstream gate
  class, so the tail is one linear map; RQMCJ (Sobol + exact tail map) 3-15x over RQMC at equal compute (MEASURED);
  a fixed Sobol rule with the tail map is competitive with RQMCJ but erratic across budgets (up to 1,100x swings).
- arc-update-2026-11-02.md
  - A2 pricing identity (PROVEN at every width): a past-measurable defect at layer l is priced by
    sum_d b_d^{(n,t)} ||M_d||^2 with b_0 >= 1/pi; infinite width b_0 = 0.973, b_1 = 0.003 at t = 31; finite width
    b_0^{(256,31)} = 0.948 (NUMERICAL).
  - RQMC (scrambled Sobol, Gaussian, not radius exact) gains over MC at 256 x 32: 1.24, 1.48, 1.74, 2.19, 2.10
    (medians over nets 200-204) at N = 2^8 ... 2^16 (MEASURED, 8 scrambles per size).
  - Nets 200-204 truths (arc-noisy, 2^26 paths, floor 1.5e-8); ladder truths n = 32, 64, 128 (seeds 300-307, 2^24
    paths, floor 6e-8) in work/arc-update/runs/truth_n*_s30?.npz.
- arc-noisy-deep-2026-10-29.md: Kerdock design (129 MUBs of R^256 + antipodes, Haar rotation per 66,048-point block,
  stratified chi radii): 0.40/N (2.4x MC) at sigma = 1e-3, depth 32, 24 nets (MEASURED); published Phase-1 entries ~3x.
- input-bits-2026-10-31.md: annealed mean Hermite degree of the input map = n / E_W V (PROVEN); ~19-21 at 256 x 32.
- relevance (in arc-update section 3): gates switched per sample vs the mean path 5-9% (MEASURED): no linear tail at
  256 x 32.
- hardness-mean-estimation-2026-10-29.md sec. 4: white-box worst-case deterministic estimation is as hard as
  derandomisation (IKW-type consequences); pseudorandom functions have predictable means (Cor. 3.3).
