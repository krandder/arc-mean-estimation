# randomness lane: the question sharpened (leaf q, 2 Nov 2026 ~13:30Z)

## Corrections to the hypothesis as put to Kelvin (each with how it is checked)
1. "Sampling uses many random bits." Wrong as a resource count: Chebyshev needs only pairwise independence, so N
   samples need ~2 n b bits (b bits per coordinate), independent of N (coordinator's (a): right). Check: standard
   (Chor-Goldreich two-point sampling; notes/LITERATURE.md).
2. "The real step is from few bits to zero." On ARC's ensemble that step is free: (i) weight-derived seeds simulate
   any randomized estimator at the same average risk [prior: unrestricted 3.1]; (ii) obliviously, some fixed m-point
   design has average risk <= V_sph/m (probabilistic method, FORMAL T3). Check: proofs (FORMAL T2-T3); measured fixed
   designs vs RQMC (detqmc runs).
3. "Noise sensitivity forces long seeds." Wrong direction: on average, MC-length seeds (log2 of MC's sample count)
   always suffice; a heavy spectral tail forbids SHORT seeds (no design beats MC by more than the inverse even-tail
   share, FORMAL T4-T5). Long seeds arise only for worst-case classes (FORMAL T11). Check: proofs; measured design
   gains vs the ceiling (structure runs).
4. "The obstacle is boundary mass." The gate partition is extremely noise-sensitive (GSA ~ n L / sqrt(2 pi)); the
   output is Lipschitz with mean Hermite degree ~ n / V. Boundary mass makes all non-linear harmonics but designs
   only touch degrees <= 5 (FORMAL T7-T8). Check: noise runs (flip counts, NS curves) vs design partial sums.
5. Coordinator's (b) black-box vs white-box: right; the black-box average risk is exactly a kernel discrepancy with
   the per-net harmonic spectrum (FORMAL T1-T2). White-box alignment changes the kernel (FORMAL T9). Check: polar vs
   standard RQMC (structure runs).
6. Coordinator's (c) Caratheodory: right; for one net a weighted rule with <= n + 1 points exists; so the trade-off
   must include compute. With randomness free on average, it collapses to compute vs precision; what randomness
   still buys is a self-certified error bar (FORMAL section 5).

## Open questions and checks (registered in PREREG.md where scored)
- Q1 Per-net harmonic shares E_1, E_2, odd, even >= 4, even >= 6 at 256 x 32 and along L = n/8. Check: rotation
  variances of MC, antipodal pairs, ONB, simplex, cross-polytope, Kerdock, MUB (FORMAL T1).
- Q2 Does the black-box ceiling fall with width at L = n/8? Check: same along n = 32, 64, 128, 256.
- Q3 k-wise independent Gaussian designs: error vs k (k = 2, 3; 4 at n = 32). Check: full GF(q)^k enumeration vs truth.
- Q4 Deterministic QMC (centred Sobol, Korobov lattice): nMSE vs N and n, rate exponents. Check: vs truths.
- Q5 White-box: does the polar (W_1-aligned) frame help scrambled Sobol at 256 x 32? Check: replicate variances.
- Q6 White-box controls (first-layer features, multilevel prefix norms): residual share. Check: dev regressions (done,
  FORMAL T10) and multilevel level variances in the structure runs.
- Q7 Noise sensitivity and GSA vs depth; do NS curves and design variances agree on the spectrum (FORMAL T6)? Check:
  noise runs.
- Q8 Best structured combination at 256 x 32 and its gain over MC and RQMC (registered test).
