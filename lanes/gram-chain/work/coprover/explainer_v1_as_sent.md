# The replica Gram chain: what it is, what it computes, what it cannot (1 November 2026)

For Kelvin. Lane gram-chain (bead pool-qxszj1.23). Model S, h_l = relu(W_l h_{l-1}) + xi_l, W_l iid N(0, 2/n), sigma = 1
(sigma is a pure scale). Labels: PROVEN, NUMERICAL (exact chain, sampled), HEURISTIC (mean-field), MEASURED (nets).
Math checked by gpt-6-astra (section 8).

## 1. The object

Take R copies ("replicas") of one net: they share every weight matrix and differ only in their noise (or, at sigma = 0,
in their input). A sharing pattern says, layer by layer, which replicas get the same noise vector; more generally S_ab is
the correlation of their noise (1 = shared, 0 = independent). The replica Gram matrix is the R x R matrix

    G_l[a,b] = h_l^(a) . h_l^(b) / n,   Q_a = G_aa (radius),   rho_ab = G_ab / sqrt(G_aa G_bb),   delta_ab = 1 - rho_ab (angle).

## 2. Why it is an exact Markov chain (PROVEN; numerics lane P-G1)

Condition on everything up to layer l-1. The rows w_i of W_l are iid N(0, (2/n) I) and independent of that past. So for
each unit i the pre-activations across replicas, z_i = (w_i . h^(a))_{a=1..R}, form a Gaussian vector with covariance
2 G_{l-1}, iid over the n units, and the noise vectors xi_i are iid over i with covariance S. Hence

    G_l = (1/n) sum_{i=1..n} v_i v_i^T,   v_i = relu(z_i) + xi_i,   z_i ~ N(0, 2 G_{l-1}),   xi_i ~ N(0, S):

a sum of n iid rank-one matrices whose law depends on the past only through G_{l-1}. The weights are integrated out
exactly, one layer at a time: no large-n limit and no Gaussian closure. A step costs O(n R^2) instead of the net's
O(n^2 R). The conditional mean is the infinite-width kernel map plus the noise,

    E[G_l[a,b] | G_{l-1}] = sqrt(G_aa G_bb) kappa(rho_ab) + S_ab,   kappa(rho) = (sqrt(1 - rho^2) + (pi - arccos rho) rho) / pi,

and the conditional covariance is (1/n) times the four-point source, so the chain's 1/n expansion is the Roberts-Yaida
kernel + four-point-vertex recursion with a noise source; the chain keeps all orders. Consequence: every
rotation-invariant function of the replicas (radii, overlaps, and anything that needs only the next layer's weights
integrated out, such as the expected number of gates where replicas a and b disagree, n arccos(rho_ab)/pi) has the same
joint law under the chain as under the net with random weights.

## 3. What has a stationary law and what does not

A correction to how this is usually put: one input does have a stationary law in Model S. Its radius is an exact
one-dimensional chain (a Kesten perpetuity), with median 0.577 n and tail P(Q > x) ~ (2n/5)/x. What it lacks is a mean:
E[Q_l | Q_{l-1}] = Q_{l-1} + 1 exactly, so E Q grows by one noise unit per layer forever and the stationary mean is
infinite (PROVEN). The kernel recursion is an equation for E Q, so it, and its 1/n vertex correction, have no fixed point.
(At sigma = 0 there is no stationary law at all: Q -> 0 almost surely.)

The normalised replica quantities (angles, radius ratios) have bounded or light-tailed laws, and their recursion has a
fixed point. For two replicas with equal radii Q and noise correlation c, the conditional mean gives
rho' = (Q kappa(rho) + c)/(Q + 1): each layer's unshared noise opens the angle by (1 - c)/(Q + 1), and the ReLU kernel
closes a finite angle, 1 - kappa(1 - delta) = delta - c_k delta^{3/2} - delta^{5/2}/(15 sqrt2 pi) + ..., c_k = 2 sqrt2/(3 pi).
The balance is

    delta*(Q) = eps [1 - (2/(3(1 - c)) + 1/30) eps + O(eps^2)],   eps = ((1 - c)/(c_k Q))^{2/3} = 2.231 ((1 - c)/Q)^{2/3}.

The expansion is of the mean-field fixed point (at c = 0 the two terms are within 0.3% of it for Q >= 148); using it
for the chain freezes Q (HEURISTIC). Independent noise (c = 0): delta* = 2.231 Q^{-2/3}, i.e. about 3.2 n^{-2/3} at the
median radius. Shared noise (c = 1): the replicas merge. Antithetic noise (c = -1): 2^{2/3} times the independent angle.

## 4. The stationary law for 2 and 3 replicas

Two replicas, independent noise. Three coordinates on three time scales.
- The common radius Q: each replica's marginal is exactly the one-input law; it moves on a scale of n layers.
- The angle delta: fast. In mean field it relaxes in about 1.5 Q^{1/3} layers (8 at n = 256) and follows delta*(Q). In
  the exact chain (1,000-4,000 chains per width) the median of delta/delta*(Q) is 1.04, 0.99, 1.00 at n = 16, 64, 256
  and its SD 0.76, 0.47, 0.28, i.e. about 1.85 n^{-1/3} (NUMERICAL); the numerics lane's mean ratio falls from 1.12 at
  n = 8 to 1.00 at n = 1024.
- The radius ratio log|h1| - log|h2|: slow (it is pulled back mainly by the noise's +1, at rate about 1/Q per layer) and
  of size n^{-1/3}: SD 1.5-1.8 n^{-1/3} at n = 16-256 (NUMERICAL).
So: a heavy-tailed radius and, given it, an angle pinned at delta*(Q) ~ Q^{-2/3} with relative fluctuations of order
n^{-1/3}, plus a radius ratio of order n^{-1/3}.

Three replicas, independent noise: three angles, each near delta*(Q). They are three independent draws from one net's noise
cloud, so each squared distance has relative SD sqrt(2/PR), PR the cloud's participation ratio, and two distances that
share a replica are correlated 1/4 (Gaussian cloud). The mean (max - min)/mean of the three angles is 0.75, 0.56, 0.39 at
n = 16, 64, 256 (NUMERICAL), against 1.46 sqrt(2/PR) = 0.70, 0.50, 0.34 from the numerics lane's 4-replica PR. The triangle becomes equilateral only as fast as PR grows (logarithmically if the cloud spectrum is 1/k).
Mixed sharing: if replicas 1 and 2 share all noise except layer j and 3 is independent, delta_12/delta_13 is layer j's
total effect relative to the cloud. In mean field one layer's noise opens 1/(Q + 1), then decays algebraically,
delta_t ~ delta_0/(1 + (c_k/2) sqrt(delta_0) t)^2, so the single-layer effects add up to 2.99 Q^{1/6} times the cloud
(the numerics lane's interaction-order mechanism).

## 5. What the chain computes exactly

Weight-averaged moments of fixed-weight quantities, whenever the fixed-weight quantity is a polynomial in a fixed number
of independent noise draws (or inputs):
- cloud size E_W tr Cov(h | W) = E|h1 - h2|^2/2 (2 replicas, independent noise); tr Cov^2 = E[((h1 - h2).(h3 - h4))^2]/4
  (4 replicas), hence participation ratios as ratios of such means;
- the Sobol total effect of any block B of layers, E|f - f^(B)|^2/2 (replicas sharing all noise except B); closed indices
  from replicas sharing only B; mean interaction orders as sum_B E T_B / E V;
- generating functions over a sharing probability or correlation t, C(t) = 1 - E|f - f_t|^2 / E|f - f_0|^2. The mean field
  gives 1 - (1 - t)^{2/3} at large Q ([A], input-bits round 1): 0.175, 0.370, 0.603 at t = 0.25, 0.5, 0.75. The input-bits
  lane measured 0.16-0.18, 0.36-0.38, 0.60-0.64 at n = 8-128, flat in width (MEASURED there; the match is HEURISTIC
  support, not noted before). The same law gives a first-order share of 2/3 and, for layer blocks, ANOVA orders with a
  k^{-5/3} tail cut off near k ~ sqrt(Q): flat low-order shares while the mean order grows like Q^{1/6} (HEURISTIC);
- the across-net scatter of any such quantity: E_W[T(W)^2] needs 4 replicas, so Var_W T, and whether T self-averages, are
  chain quantities;
- gate statistics in closed form given G (disagreements, births, cascades);
- at sigma = 0 with replicas = inputs, the exact multi-input Gram recursion (the input regime: amplitude/direction split,
  the 3n/l decay of differing gates);
- tangent replicas: the joint Gram of states and tangent vectors J u is also an exact chain (same proof), so annealed
  moments of linear responses are computable. One fact to keep in mind: E_W |J u|^2 = |u|^2 exactly at every depth
  (PROVEN; criticality), while the typical |J u|^2 decays like exp(-2.5 t/n), so annealed linear-response means are
  carried by rare nets.
For all R together, the replica Gram arrays are the Gram-de Finetti (Dovbysh-Sudakov) representation: their laws fix the
across-net law of the fixed-weight noise law mu^W up to rotation. R = 2-4 gives its first few moments.

## 6. What it cannot compute

- Per-net ratios: the fixed-weight Sobol index T_B(W)/V(W), a per-net participation ratio, a median over the noise. The
  chain gives the means of numerator and denominator and their joint moments, not the mean of the ratio. The radius
  varies across nets with a heavy tail, so ratios of annealed means weight large-radius nets; conditioning on one
  replica's radius approximately fixes this at large n (the radius varies by only n^{-1/3} within a net) but is not exact.
- Which directions. Given the past, the future weights are rotation invariant about the replicas' span, so every annealed
  quantity is the same for every direction orthogonal to the replicas. The chain can say how much of a layer-l difference
  survives and how many directions carry it (spectral moments such as tr C^2), never which directions; that needs the
  specific weights (a backward pass). The kstar-frames lane's Proposition 2 is the same fact seen from the past.
- Anything needing unboundedly many replicas (entropies, the law of a per-net ratio) is reachable only through moments.
- It averages over the weights: it describes typical and average nets and does not estimate a fixed net's mean.

## 7. Next in this lane

The stationary law for R = 2, 3, 4 and sharing patterns at n = 8-1024 with error bars, its large-n limit (angle slaved
to the radius; radius and radius ratio a joint diffusion on the scale of n layers) and mixing times; then the annealed
count of the bits that matter at layer l (total effect of everything before l, survival of a random-direction
perturbation, a participation ratio) against n, L - l and sigma in both regimes, and where per-net values depart from it.

## 8. Check

(filled in after gpt-6-astra's check)
