# randomness lane: lemma-free statement for the co-prover (round 1)

Written 2 November 2026, ~14:00Z, before this lane's own theory (FORMAL.md) was written. It contains the setting,
prior results from earlier lanes (with their labels), the hypotheses to test, and the questions. It contains none of
this lane's own lemmas.

## Setting

- Nets: width n, depth L, x ~ N(0, I_n), h_l = relu(W_l h_{l-1}), output f_W(x) = h_L in R^n. W_l iid N(0, 2/n), no
  bias, no noise. Positive homogeneity: f(x) = |x| g(x/|x|), g = f restricted to the unit sphere S^{n-1}.
- Estimand mu(W) = E_x f_W(x) in R^n. Error: nMSE = |est - mu|^2 / V(W), V(W) = tr Var_x f; ARC's weight-averaged
  criterion E_W |est - mu|^2 <= eps^2 E_W V. Plain Monte Carlo with N samples scores 1/N; "radius-exact" (RB) MC
  (evaluate g at uniform directions, multiply by m_n = E|x|) scores V_sph/N with V_sph = m_n^2 E tr Var_u g.
- Cost: one forward pass = 2 n^2 L flops. ARC's instance: n = 256, L = 32 (L = n/8); ladder n = 32, 64, 128, 256 at
  L = n/8. ARC's open problem: match sampling (error eps^2 E V at O(eps^-2) passes, all eps) with depth growing linearly
  in width, by a "mechanistic" estimator ("avoids any random or pseudorandom sampling").

## The hypothesis under test (the lane coordinator's conjecture, as Kelvin read it)

"Randomness instead of description: how many random bits does an estimator really need? Deduction uses 0 random bits
and sampling uses many. The question is the length of the shortest pseudorandom seed (deterministic point set) that
fools the net's output to precision eps. For halfspaces and low-degree PTFs short seeds exist, with bounds governed by
noise sensitivity / Gaussian surface area. Conjecture: at depth proportional to width, the output's noise sensitivity
forces long seeds, so ARC's goal is a derandomization problem for neural nets, and the obstacle is boundary mass, not
bits." The coordinator added: (a) random bits are cheap to reduce (pairwise independence suffices for Chebyshev MC),
so the real step is from few bits to zero (a short-seed PRG / small deterministic point set plus the compute to
evaluate it); (b) black-box vs white-box: a PRG must fool every net in a class without looking, while ARC's estimator
sees the weights (QMC point sets are the black-box version; white-box designs can adapt, e.g. stratify on gate
patterns); (c) for one fixed net a tiny fooling set always exists (<= n + 1 weighted points by Caratheodory), so
randomness complexity means something only together with compute. Kelvin (13:05Z) then asked to approach it "from the
sampling direction": add structure to the sample set, spend less randomness, keep precision per compute.

## Prior results (earlier lanes; reports in /home/agent/workspaces/mats/outbox; labels as given there)

- Determinism is free on random weights (unrestricted-estimators-2026-10-31.md, sec. 3.1; PROVEN UNDER exact-transform
  primitives): QR-reducing rows of W_1 frees Haar-uniform angular coordinates independent of the reduced net; they give
  pairwise-independent N(0, I_n) inputs with risk exactly V/N; any randomized estimator can be simulated
  deterministically at the same average risk (extra O(n^3)). With finitely many bits per weight only approximately.
- Fixed linear rules (same report, sec. 3.5): PROVEN: the risk of any fixed rule sum_i c_i f(x_i) averaged over W is a
  kernel discrepancy with k(t) = E_W <g(u), g(v)> (u . v = t); k(t) = sum_d b_d t^d with b_d >= 0. PROVEN [astra]: for
  positive weights summing to one, gain over RB-MC <= 2 (1 - q) / sum_{s: tau_2s <= 1/(2N)} b_2s, tau_2s = E (U . V)^2s;
  in the infinite-width mean-field limit at L = alpha n the even tail carries half the angular variance, so positive
  designs with N <= n^p gain at most about 4. MEASURED: harmonic degrees 1 + 2 carry 0.30-0.43 of the angular variance
  at 256 x 32 (2-design ceiling ~1.7 over RB-MC); centred unscrambled Sobol beat scrambled Sobol 2.7-4.5x at widths 3-8.
- Polynomials in the WEIGHTS of degree D (same report): best risk = Hermite tail of mu(W) in W, sandwiched by weight-noise
  stability; mean-field 1 - Corr ~ 3.27 delta^{2/3} (PROVEN in mean field).
- Pricing identity (arc-update-2026-11-02.md, A2, PROVEN at every finite width): for a past-measurable signed-measure
  defect Delta at layer l with t layers to go, E_future |<g_l, Delta>|^2 = sum_d b_d^{(n,t)} ||int |h| (h/|h|)^{(x)d}
  dDelta||_F^2, b_d >= 0, sum b_d = 1, b_0 >= 1/pi. Infinite width: b_0 = 0.973, b_1 = 0.003, mean degree of b_{>=2}
  = 42 at t = 31; finite width b_0^{(256,31)} = 0.948 (measured).
- Mean Hermite degree of the input map (input-bits-2026-10-31.md, PROVEN annealed): n / E_W V (~19-21 at 256 x 32).
- Samplers at 256 x 32: scrambled Sobol RQMC 1.2-2.2x over MC (N = 2^8-2^16); a Kerdock design (129 mutually unbiased
  bases of R^256 with antipodes = antipodal spherical 5-design, Haar-rotated blocks, stratified chi radii) 2.4x over MC
  at sigma = 1e-3 (arc-noisy-deep-2026-10-29.md); the multilevel shared-trajectory sampler (unrestricted 3.7; gain
  Omega(n / log^2 n) at L = alpha n PROVEN UNDER layerwise cost hypotheses) ~1.0 at 256 x 32, 1.2 -> 2.4 at L = n
  (n = 32 -> 256); RQMC with the exact linear tail 3-15x over RQMC at 8 x 256 (nd-exact), where the deep part is one
  linear map (not at 256 x 32, where gates still flip in the last layers).

## Questions (label every claim PROVEN / PROVEN UNDER <hypothesis> / HEURISTIC / CONJECTURE)

1. **Formalise randomness complexity here.** Define the right trade-off among random bits R, compute T and precision
   eps, in three models: (a) average over ARC's ensemble, black-box oblivious point sets; (b) average, white-box (the
   estimator reads W); (c) worst case over a class of weights. Prove what collapses and what non-trivial trade-off
   survives (for example: what an estimator's own randomness buys that a fixed design cannot, such as an unbiased
   self-certified error bar, and how many bits that needs). Correct the hypothesis above where it is wrong, precisely.
2. **Black-box designs, bounds on the point count.** Lower and upper bounds on N(eps) (equivalently the seed length
   log2 N) for a W-independent design to fool deep random ReLU nets to normalised precision eps on average, in terms of
   the per-net spherical-harmonic energy spectrum E_d(W) of m_n g and its average, and in terms of noise sensitivity
   (the Ornstein-Uhlenbeck decorrelation of the output, NS(delta) = E|f(x) - f(y)|^2 / (2 V) for rho = 1 - delta
   correlated Gaussians). In particular: is there a two-sided relation between NS(delta) and the harmonic tail beyond
   degree t? How do antipodal designs (which kill odd degrees but double even-degree aliasing) and spherical t-designs
   (kill degrees 1..t; size >= ~ n^{t/2} / (t/2)!) trade off? What is known or derivable about the low-degree share
   (degrees 1, 2, odd vs even) at L = alpha n, finite and infinite width?
3. **Bounded independence.** Exact k-wise independent Gaussian designs (coordinates k-wise independent, e.g. from
   degree-(k-1) polynomials over GF(q), q > n, discretised to q levels): what error do they achieve for f(x) = |x| g(u)
   as k grows, compared with spherical designs plus exact radius? Is Gaussian moment matching even the right notion for
   positively homogeneous f?
4. **White-box structure.** What can a design adapted to the net buy, at negligible cost: (i) rotating a QMC point set
   into a basis aligned with the first layer (polar factor of W_1, or right singular vectors of W_1), so Sobol's
   best-stratified low-dimensional projections align with first-layer gates; (ii) control variates on first-layer
   features with closed-form means (z_i, |z_i|, relu(z_i), |h_1|^2, quadratic forms); (iii) multilevel prefix controls.
   Any argument (ANOVA in the aligned basis, kernel spectra) for or against a gain that grows with n at L = alpha n?
   Note: a design aligned to W_1 without further randomisation can be biased on the ensemble when its points are
   atypical (e.g. standard basis vectors in the polar frame activate essentially one first-layer neuron); say what
   randomisation restores unbiasedness at how many random bits.
5. **Gaussian surface area and noise sensitivity of the gate partition.** For random He-ReLU nets compute or bound the
   expected Gaussian surface area of the layer-l zero sets {z_{l,i} = 0} (per neuron and summed), at infinite and
   finite width, and the probability that the gate pattern up to layer l changes under rho-correlated noise. What do
   these say, if anything, about fooling the OUTPUT (continuous, piecewise linear) versus fooling the gate pattern
   (Boolean)? Relate the high-degree Hermite tail of a piecewise-linear function to the surface measure of its kink set
   and the gradient jumps across it.
6. **Worst-case PRGs.** What do the Gaussian PRGs for halfspaces, PTFs, intersections and functions of halfspaces
   (Meka-Zuckerman, Kane, Harsha-Klivans-Meka, O'Donnell-Servedio-Tan, Chattopadhyay-De-Servedio, Hatami-Hoza-Tal-Tell
   for threshold circuits) imply for deep ReLU nets? Which sub-structures are covered (e.g. the first-layer gate cell is
   an intersection of n origin halfspaces), with what seed lengths, and why does none of it bear on ARC's average-case
   problem at the precision sampling reaches? Mark citations you cannot check as unverified.
7. **Verdict.** Does the randomness framing say anything new and checkable about ARC's goal, beyond "precision per
   compute"? Give the single strongest defensible statement and the single most promising structured-sampling route at
   256 x 32, with a falsifiable prediction for it.
