# Adaptive region trees for the mean of a random deep ReLU net: what can stratification plus local models buy? (statement for round 1, lemma-free)

Setting. f(x) = h_L(x) in R^n, h_0 = x ~ N(0, I_n), h_l = relu(W_l h_{l-1}), W_l iid N(0, 2/n) (n x n), no biases, so f
is continuous, piecewise linear on polyhedral cones, positively homogeneous: f(x) = |x| g(x/|x|). Estimand mu = E f (all n
outputs). Error nMSE = |est - mu|^2 / tr Var f, so N-sample Monte Carlo scores 1/N. Cost unit: one forward pass,
2 n^2 L flops. Regime of interest: depth growing with width, L = n/8 (n = 32, 64, 128, 256), and ARC's contest net
256 x 32. Comparator: scrambled-Sobol RQMC, measured gains over MC ~1.2-2.6 (256 x 32) to ~3-6 (32 x 4), fitted
MSE exponents 1.0-1.18 over N = 2^8..2^16.

Known results you may use (from sibling lanes; say so if you rely on them):
- (K1) Weight-averaged kernel E_W f(x).f(x') = |x||x'| kappa(<xhat, xhat'>) at every width; for any rule nu (weighted
  points or line integrals) chosen independently of W, E_W |mu - nu(f)|^2 is the kernel discrepancy. Rank lemma: no rule
  linear in N sampled values (signed weights allowed) cancels degree-2j angular energy better than MC until N ~ dim of
  degree-j harmonics ~ n^j/j!; for positive weights at n = 256 every even power from degree 6 on is paid in full for
  N <= ~8.6e4. Proxy-free: absolute ensemble MSE >= 1/(4 pi^2 N) for N <= n/2.
- (K2) Under a Gaussian surrogate prior (f Gaussian with the nets' mean and covariance) adaptive information does not
  help on average (Wasilkowski-Wozniakowski 1984; varying cardinality: Wasilkowski 1986). The real prior is not
  Gaussian: excess kurtosis over nets of a unit output at a fixed input 6.9-9.1 (n = 32-256, L = n/8); the net is
  identified by ~nL evaluations.
- (K3) Spectrum along L = alpha n (limits as n grows, measured at 256 x 32): angular degree 1 ~0.29, degree 2 ~0.21,
  odd 0.57, even 0.43, even >= 6 ~0.17 of the angular variance; mean Hermite degree of f ~ n / E V ~ 20 at 256 x 32.
  The finite-width variance is made by persistent activation-norm fluctuations accumulated over the first layers.
- (K4) Output cloud at 256 x 32: covariance participation ratio ~1.9 at the last layer (the variance is mostly one
  scalar amplitude times a nearly fixed direction); the input-side gradient covariance E[J^T J] has participation
  ratio ~n/4 at the first layer (17.5, 33, 67 at n = 64, 128, 256); 99% of the value function's variance needs all n
  input directions.
- (K5) Gate geometry: expected Gaussian perimeter of the gate partition ~ nL/sqrt(2 pi); some gate changes with
  probability 0.93-0.98 already at input correlation 1 - 1e-6; for two inputs whose layer-(l-1) states have cosine rho,
  the expected number of layer-l gates that disagree is exactly n arccos(rho)/pi (replica Gram chain).
- (K6) A certified branch-and-bound over input cones (symbolic linear bounds from the actual weights) lost to RQMC by
  1e3-1e6x from width 4 to 32 and certified nothing from width 6 on.

The idea under test (MCTS-like): grow a tree of input-space regions; in some regions "understand" f (a local model
whose region mean is exact), in others "sample more" (allocation proportional to p_k sigma_k, Neyman, or a bandit
version MC-UCB / MISER / VEGAS). Bookkeeping: with K regions, exact p_k and Neyman allocation, MSE = (sum_k p_k sigma_k)^2
/ N (sigma_k^2 = tr Var(f | region k)). If (sum p_k sigma_k)^2 / tr Var f ~ K^{-beta} and K ~ N^a (a < 1), MSE ~
N^{-(1 + a beta)}. So beta, uniformly in width, is the key quantity.

Questions (prove, disprove, or give the sharpest statement you can; label each claim PROVEN / PROVEN UNDER <hyp> /
HEURISTIC / CONJECTURE; give constants where you can):
Q1. Ceilings. (a) Fixed (weight-independent) strata with weight-independent allocation: what does K1 imply for beta,
  per net (Haar-rotated strata) and on average? (b) Arbitrary partitions chosen with full knowledge of W (white-box,
  adaptive), any allocation: is there a ceiling on the gain tr Var / (sum p_k sigma_k)^2 in terms of K and a structural
  dimension of f (input side: how many directions or how much information the partition carries; output side: the
  law of f(x))? In particular for trees whose cells are cut by hyperplanes from a candidate family (orthonormal-frame
  coordinates; first-layer gate normals w_i), with depth D. (c) Is there any construction in which beta > 0 holds
  uniformly as n grows along L = n/8, and what property of f would it need?
Q2. Neyman vs proportional. The gain of Neyman over proportional allocation is 1 + CV_p(sigma)^2. What non-Gaussian or
  white-box feature of these nets could make it grow with K (heavy-tailed local variance, rare high-variance regions)?
  What does homogeneity imply (radial vs angular strata)?
Q3. "Understanding" a region. Inside a full gate region f is exactly linear, f = A_k x, so E[f; R_k] = A_k p_k c_k
  needs the region's Gaussian probability p_k and centroid c_k. What do these cost (polyhedral cones with up to nL
  facets), how much mass does a region carry, and does any region family make p_k and c_k cheap while keeping f
  nearly linear inside? A local linear control variate per coarse cell: what can it remove?
Q4. Bandit allocation (MC-UCB type) with K arms and N samples: the regret over oracle Neyman, and what it implies for
  the attainable exponent when K ~ N^a.
Q5. Settling regions (MCTS-Solver / alpha-beta analogue): a region can be dropped only when p_k (upper - lower) is
  below its share of the error budget, with certified bounds (interval bound propagation; CROWN-style backward linear
  relaxation). What bound widths should one expect for a cone of angular radius delta through L layers of width n,
  and what does that imply for the mass that can be settled with K regions? Regions of a deep layer's state (the deep
  cloud is low-dimensional) can be bounded through few layers, but their probabilities are that layer's law: what
  does settling at depth buy?
Q6. Branch similarity: how well does one region's linear map predict f at input angle theta (in terms of K5), and what
  covering number of "similar branches" does that imply?
Q7. Predictions for the measurements (n = 32, 64, 128, 256, L = n/8): beta and the gain at K = 2^4, 2^8, 2^12 for
  (i) frame splits (random frame; W_1's SVD frame; the top eigenvectors of E[J^T J]), (ii) first-layer gate-sign splits
  (units ordered by importance), (iii) a greedy CART tree scored on held-out data, with and without a local linear
  model per cell.
