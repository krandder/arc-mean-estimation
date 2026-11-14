You are a co-prover (gpt-6-astra, read-only sandbox; do not modify files) for the bits-bounds lane in
/home/agent/workspaces/mats/work/bits-bounds. Labels for every claim: PROVEN, PROVEN UNDER <hypothesis>, NUMERICAL,
HEURISTIC, CONJECTURE. Be precise about hypotheses and regimes. Write everything to stdout.

Setting. He-ReLU nets: width n, depth L, W_l iid N(0, 2/n) entries, no bias, h_0 = u a unit input, h_l = relu(W_l h_{l-1}),
A(u) = h_L(u). Cut at layer l, future g_l (layers l+1..L), L' = L - l. Unit inputs are uniform on the sphere.
V_ang = tr Var_u A(u). The layer gain of a state h is G(h) = |relu(W h)|/|h|.

PART 1 (independent; do this BEFORE reading FORMAL.md section 6.6).
1. Two unit inputs u, u' with layer-j states at angle theta_j. Prove or refute: log|h_L(u)| - log|h_L(u')| is a
   martingale over layers whose conditional increment variance v_n(theta_j) depends on the current angle only, so
   Var(log|h_L(u)| - log|h_L(u')|) = sum_j E v_n(theta_j). Handle dead states (G = 0 has probability 2^{-n}). Give
   v_n(theta) to leading order in 1/n, its small-angle form, and n * sum_j v(theta_j) along the mean-field angles of
   two independent inputs (cos theta_{j+1} = kappa(cos theta_j), theta_0 = pi/2). What share of it is made after
   layer l, as a function of l?
2. One radial merge at layer l: a state h is replaced by (|h|/|c|) g_l(c) for a reference state c at angle phi. Its
   future-averaged squared error is |h|^2 rho(phi) with rho depending on (phi, n, L') only. Derive rho in mean field
   and its form when L' phi >> 3 pi with L' <= alpha n (the rough regime). Is rho(phi) >= a phi a valid minorant
   there, with which a (in units of E|A|^2, and in units of V_ang)? Is the resulting D_R(1)/V_ang width-free?
3. Forward-only cell methods with radial merges (M past-chosen references, any assignment): under a minorant
   rho(phi) >= a min(phi, phi_0) and a small-ball condition for the radius-weighted angular law of the layer-l cloud,
   P_w(angle(h, c) <= r) <= K (r/theta)^d for all c and r <= theta, prove or refute
   log2 M >= d log2( a (E|h|^2/V) (d/(d+1)) theta / eps^2 ) - log2 K for reaching distortion eps^2 V.
4. Effective dimension. Suppose the layer-l angular cloud is approximately Gaussian with covariance eigenvalues
   lambda_k proportional to exp(-2 (k - 1) l/n) (participation ratio PR ~ coth(l/n) ~ n/l). What is its small-ball
   exponent as a function of the scale r, and the local exponent gamma(M) of the best M-point quantiser's distortion
   when the distortion is linear in the angle? Compare with a measurement: for k-means references on actual nets in the
   rough regime, D_R(M) ~ M^{-gamma} over M = 4..256 with gamma x PR having median 0.72 (10-90%: 0.29-1.24), and
   about 1.03 in intermediate cells.
5. Is N_l(eps) = (d_l/p) log2(D_l(1)/eps^2) (p = 1 rough, p = 3 smooth) the right count of "bits that matter at
   layer l" for forward-only cell methods (lower bound and achievability)? What does it say about when enumerating
   cells at layer l and sampling the rest can beat plain sampling, and the shared-trajectory multilevel sampler, at
   L = alpha n?

PART 2 (audit). Now read FORMAL.md section 6.6 and audit each item (a)-(f): is each label right, are the hypotheses
complete, are the numbers consistent with results/variance_made.md and results/bits5_posthoc_old.json (computed by
scratch/variance_made.py and scratch/score_bits5.py --old)? The variance profile is attributed to the input-bits lane
(/home/agent/workspaces/mats/outbox/input-bits-2026-10-31.md, section 2.2); check that attribution against that file.
Give numbered findings (severity, location, what is wrong, the fix).
