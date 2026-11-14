# gram-chain lane: theory v1 (1 November 2026, frozen before reading gpt-6-astra round 1)

Model S, h_l = relu(W_l h_{l-1}) + sigma xi_l, W_l iid N(0, 2/n), xi_l iid N(0, I_n); output a = relu(W_L h_{L-1})
(no output noise). Stationary regime: sigma = 1, infinite past. Input regime: sigma = 0 (or small), h_0 = x ~ N(0, I_n).
R replicas share all weights. G_ab = h^(a).h^(b)/n; Q = G_aa; delta = 1 - cos(angle); ell = log|h1| - log|h2|;
q = Q/n. Layer l = L - t (t layers to go, counting the output layer). Labels: PROVEN, PROVEN UNDER <hypothesis>,
HEURISTIC (mean field / leading order, tested), CONJECTURE. Provenance [C] unless stated. Numbers from
`scratch/theory_numbers.py` (`results/theory_numbers.json`, `logs/theory_numbers.log`).

## 1. Exactness and its extensions (PROVEN)

1.1 (P-G1, numerics lane.) Given the past, z_i = (w_i . h^(a))_a are iid over units, N(0, 2G); G' = (1/n) sum_i v_i v_i^T,
v_i = relu(z_i) + sigma xi_i, xi_i iid N(0, S). G is Markov; every rotation-invariant function of the replicas' path has
the same law under chain and net.
1.2 Augmented chains. The same argument applies to any finite family of vectors the next weight matrix acts on:
(a) tangent vectors t' = D(z_base) W t: v_i[t] = 1[z_i[base] > 0] z_i[t] (no noise); (b) correlated noise (any PSD S),
per-chain equivalence labels, per-coordinate Bernoulli sharing (the mask is iid over units); (c) sigma = 0 with
replicas = inputs (exact Wishart start); (d) Gram surgery: at a layer, replace G by any PSD matrix that is the Gram
matrix of vectors constructed from the replicas (a perturbation of given norm orthogonal to their span, a radius
rescaling, a direction swap). Implemented and tested against explicit nets in `lib/gc2.py`, `tests/test_gc2.py` (19
checks pass, `logs/test_gc2.log`).
1.3 Response invariance. Let v be a perturbation of layer l's state that is measurable with respect to the past and
the replicas' noise up to l. The joint law of the future paths of the replicas and of the perturbed replica depends on v
only through the Gram matrix of {h^(a)_l} and h_l + v. Proof: given the past, W_{l+1} O has the law of W_{l+1} for every
orthogonal O; take O fixing every h^(a)_l and mapping v to any v' with the same Gram relations; the future driven by
W_{l+1} O from (h, h + v) is the future driven by W_{l+1} from (h, h + v'). Consequence: annealed, every direction
orthogonal to the replicas' span has the same future response. Annealed quantities can count directions (through
spectral moments) but cannot name them. This does not hold for output coordinates (E[h' | h] is along the all-ones
vector) or for the past's cloud, which has coordinate structure.
1.4 Annealed tangent conservation. E_W |D_{l+1} W_{l+1} v|^2 = |v|^2 for every past-measurable v and every nonzero h_l
(E[1(z_0 > 0) z_1^2] = E[z_1^2]/2 by z -> -z); by the tower property E_W |J_{l -> L} v|^2 = |v|^2. The typical value decays
(E log of the one-layer factor = -5/(2n) + O(n^-2)) and an all-off layer (probability 2^-n) kills it, so annealed
tangent means are carried by rare paths.
1.5 Integrability. E Q = infinity (P-G2) and the radius ratio does not shrink at large Q (section 2), so annealed second
moments of raw-state differences, E|h1 - h2|^2, are infinite (n = 64: the top 1% of chains by radius carry 82% of the
sample mean; `scratch/quick_radial_tail.py`). All annealed quantities in this lane use scale-free observables: the
direction u = h/|h| (or the output direction a/|a|) and log radii.

## 2. Large-n structure of the two-replica stationary law (independent noise; HEURISTIC, leading order)

2.1 Three time scales. Per layer, given (Q, delta, ell):
- radius (exact chain): E dQ = 1, Var dQ = (5/n) Q^2 + O(Q); in q = Q/n and s = t/n,
  dq = ds + sqrt5 q dW_q (stationary density (2/5) q^-2 exp(-2/(5q)));
- angle, mean field: E[delta' | .] = (1 + Q f(delta))/(Q + 1) + O(delta/n), f(d) = 1 - kappa(1 - d) = d - c_k d^{3/2} -
  d^{5/2}/(15 sqrt2 pi) + ..., c_k = 2 sqrt2/(3 pi); fixed point delta*(Q) = eps[1 - 0.7 eps + O(eps^2)],
  eps = (c_k Q)^{-2/3} = 2.231 Q^{-2/3}; linear relaxation rate 3/(2 Q delta*) + 1/(Q + 1) ~ 0.672 Q^{-1/3} per layer;
- radius ratio: E[d ell | .] = -ell/(Q + 1) (the +1 of the noise pulls the larger radius back more); the gain difference of
  two directions at angle theta has Var(A1 - A2) = (4/n)(3 - J_2(theta)/pi), so Var((1/2) log(A1/A2)) = 4 delta/n + O(delta^2/n)
  (J_2 the degree-2 arc-cosine function; J_2(theta) = 3 pi - 2 pi theta^2 + O(theta^4)); the noise cross terms add
  2/(nQ) per layer (subleading).
2.2 Scaling limit. x = n^{2/3} delta is fast (relaxes in n^{1/3} layers) and slaved to x*(q) = 2.231 q^{-2/3};
y = n^{1/3} ell and q are slow and form, on the time scale s = t/n, the diffusion
  dq = ds + sqrt5 q dW_q,   dy = -(y/q) ds + sqrt(4 x*(q)) dW_y = -(y/q) ds + 2.987 q^{-1/3} dW_y,   W_q, W_y independent.
Predictions (simulated limiting SDE): E y^2 = 3.56, SD(y) = 1.89, i.e. SD(ell) -> 1.89 n^{-1/3}; E[y^2 | q] = 2.7, 3.3,
3.7, 4.1, 4.5, 4.8, 5.1 on q-bins [0, 0.3), [0.3, 0.6), [0.6, 1.2), [1.2, 2.5), [2.5, 5), [5, 10), [10, inf). (Exploratory
chain: SD(ell) n^{1/3} = 1.52, 1.70, 1.82 at n = 16, 64, 256, approaching 1.89 from below.)
2.3 Angle fluctuations. Given q, x = x* + n^{-1/3} xi with xi an OU process: drift slope -(3/2) c_k x*^{1/2}, per-layer
relative variance kappa_x/n of delta' (kappa_x = Var(delta'|G) n/delta^2; a Bernoulli-gated estimate gives 5 from the
numerator alone and 8 with the radius denominator; to be measured from one exact step). Relative SD of delta given q:
sqrt(kappa_x/(3 c_k x*^{1/2})) n^{-1/3} = 1.76 (kappa_x = 5) to 2.23 (kappa_x = 8) n^{-1/3} at the median q
(exploratory: 1.85 n^{-1/3}).
2.4 Mean corrections. E[delta | q] = delta*(Q)(1 + b(q) n^{-2/3} + o(n^{-2/3})). Mechanisms, each O(n^{-2/3}) relative:
the curvature of the drift (negative, -Var(x)/(4 x*^2)), the radius denominator and noise in the angle step, the
transfer from angle to radius ratio (the gain difference converts angular into radial discrepancy), and the lag of
delta behind the radius (Q moves by n^{-1/3} relative within one relaxation time). Prediction: b(q) > 0 and (E delta /
delta* - 1) n^{2/3} tends to a constant (the numerics lane's ratios 1.12 -> 1.00 at n = 8 -> 1024 fall like n^{-0.6}).
b is not derived here.
2.5 Mixing. The limiting radius diffusion in u = log q has generator with Morse-type Schrodinger form
V(u) = 0.625 + 2.5(e^{-2(u - u0)} - 2 e^{-(u - u0)}), u0 = log 0.2, diffusion 5/2: Morse parameter lambda = 1, so the only
bound state is the stationary one and the spectrum of minus the generator is {0} U [5/8, inf) (PROVEN for the limiting
diffusion). The radius therefore relaxes at rate 5/(8n) per layer (time scale 1.6 n layers, with a power-law prefactor
from the continuous spectrum); it is the slowest observable. Given q, the radius ratio relaxes at rate 1/(Q + 1)
(Q layers) and the angle at rate 0.672 Q^{-1/3} (about 1.5 Q^{1/3} layers).
2.6 Noise sharing. Mean field depends only on E S_12 = c: delta*(c) = eps_c[1 - (2/(3(1 - c)) + 1/30) eps_c + ...],
eps_c = ((1 - c)/(c_k Q))^{2/3}; hence C(t) = 1 - E delta(c = t)/E delta(c = 0) -> 1 - (1 - t)^{2/3} ([A] input-bits r1)
for Gaussian correlation t (Hermite degree generating function) and for per-coordinate Bernoulli sharing (ANOVA over
scalar coordinates): finite-Q mean field 0.18, 0.38, 0.62 at n = 128 (t = 0.25, 0.5, 0.75). Per-layer Bernoulli sharing
(layer-block ANOVA) differs: the injections are discrete. CONJECTURE: for refresh probability eps >> 1/sqrt(Q) the block
curve follows (1 - t)^{2/3} too, and below that it is linear with slope D_block ~ 2.99 Q^{1/6}.
2.7 Three and four replicas. Independent noise: replicas are iid draws from mu^W, so the three angles are equal to
leading order and differ by about sqrt(2/PR_C) relative (Gaussian-cloud heuristic); the 4-replica chain gives
E_W tr C_u^2 for the direction cloud C_u, and 2m replicas give tr C_u^m. CONJECTURE (numerics lane, untested by moments):
the angular cloud spectrum is 1/k over k = 2..n; then PR_C = (H_n - 1)^2/(pi^2/6 - 1) ~ 1.55 (ln n)^2 and
tr C^3 tr C / (tr C^2)^2 = (zeta(3) - 1)(H_n - 1)/(zeta(2) - 1)^2 (testable with 6 and 8 replicas).

## 3. Relevance at layer l, stationary regime (direction observable; HEURISTIC mean field, adiabatic in Q)

3.1 Definitions (all weight averages of scale-free quantities; replica constructions exact).
- Closed relevance V_P(t) = E_W Var(E[u_L | noise up to l] | W) / E_W Var(u_L | W): 1 - E|u - u'|^2 / E|u - u''|^2 with
  (u, u') identical at layer l and independent noise after, (u, u'') independent throughout. This is the relevance
  lane's memory share M_l, annealed. It prices what a description of h_l can explain for E[a].
- Total relevance T_P(t) = E|u - u'|^2 / E|u - u''|^2 with (u, u') independent up to l and sharing noise after.
- Block total effect T_B(t, b): replicas share all noise except layers (l - b, l].
3.2 Mean-field curves (independent of n after scaling). With T* = (Q + 1) delta*(Q) ~ 2.231 Q^{1/3}:
  V_P(t) = 1 - Y((t - 1)/T*),  Y' = 1 - Y^{3/2}, Y(0) = 0;   T_P(t) ~ (1 + (t - 1)/(2 T*))^{-2} (then e^{-t/Q});
  single injection: delta_0 = 1/(Q + 1), delta_t ~ delta_0 (1 + c_k sqrt(delta_0) t/2)^{-2}.
The closed relevance decays exponentially (rate 1.5/T*), the total relevance algebraically. Area of V_P:
2(1 - pi/(3 sqrt3)) T* = 0.791 T*. Finite-Q recursions at the median radius: V_P halves after 5, 8, 12 layers at
n = 64, 256, 1024 (area 5.4, 8.9, 14.5 layers); T_P halves after 7, 11, 16 and is still 0.06 at t = 64 for n = 256.
3.3 Reading. The direction of the state at layer l matters for the output's mean (closed sense) for about
0.8 T* = 1.8 Q^{1/3} = 1.5 n^{1/3} layers; beyond that only the radius matters, for about n layers (2.5). The past keeps a
long algebraic total effect (it changes which future noise matters) that a description of h_l cannot use for E[a].
3.4 Dimension (linear-response heuristic, free probability). In the linear approximation the closed-relevance
covariance is B C B^T with C the cloud and B the future's noise-averaged Jacobian; by 1.3 the future's singular frame is
Haar relative to the past outside the state's span, so the spectrum is the free multiplicative convolution of the two.
With p(X) = phi(X^2)/phi(X)^2 (phi = tr/n) one has p(XY) = p(X) + p(Y) - 1 for free X, Y, so
  1/PR_rel = 1/PR_C + 1/PR_M - 1/n.
For t ReLU layers with frozen gates p(M) = 2t + 1 (one layer: E tr((W^T D W)^2)/n = 3, so p = 3; free product adds 2
per layer), PR_M = n/(2t + 1) (Fuss-Catalan-type, t << n). Hence
  PR_rel(t) ~ [1/PR_C + 2t/n]^{-1};
with PR_C from 2.7 at n = 256 (37.7): 29, 15, 9.5, 5.5 at t = 1, 5, 10, 20. Where it fails: the cloud's angular size
sqrt(2 delta*) ~ 2.5 n^{-1/3} (0.4 rad at n = 256) exceeds the future's coherence radius (about 1.4/t rad, kstar-frames)
once t > 3-4, so gate switching across the cloud adds higher-degree relevance that the linear PR does not count. The
replica estimands (4 replicas, shared future, for the total version; 8 replicas, 4 pasts x 2 independent futures, for
the closed version) measure the truth including that.

## 4. Input regime (sigma = 0, replicas = inputs)

4.1 Angular dimension of the input cloud (HEURISTIC: leading order in 1/n, kernel + vertex). At infinite width iid
inputs are equicorrelated (c_l = kappa^(l)(0)), so the cloud is isotropic and its anisotropy is a 1/n effect. With
eta_ab = sqrt(n)(G_ab/q - c_l), the double difference D = eta_13 - eta_14 - eta_23 + eta_24 of four inputs is free of
radial (diagonal) fluctuations at linear order and obeys
  D' = kappa'(c_l) D + zeta_l,   Var zeta_l = E[(relu z1 - relu z2)^2 (relu z3 - relu z4)^2]/q^2  (z equicorrelated, c_l),
with V_D(0) = 4. The angular participation ratio of Cov_x(h_l) is PR(l) = 4 n (1 - c_l)^2 / V_D(l). Results:
PR(l)/n = 0.652, 0.241, 0.074, 0.040, 0.021 at l = 1, 4, 16, 32, 64 (167, 62, 19, 10.3, 5.3 at n = 256), against the
input-bits lane's measured 159, 57, 17, 9.6, 6.1 [MEASURED there]. Asymptotically (theta_l ~ 3 pi/l, Var zeta ~ 2 theta^4,
kappa' ~ 1 - theta/pi): V_D ~ (2/3)(3 pi)^4 / l^3 and PR(l) ~ 1.5 n / l. Breaks down at l ~ n (PR = O(1)): 2.0 and 0.3
against 3.6 and 1.9 at l = 128, 256.
4.2 What carries the input at layer l: at sigma = 0, a = |h_l| F(u_l) exactly (homogeneity), so the output direction
depends only on u_l and log|a| = log|h_l| + log A_l(u_l). The radius |h_l| carries the amplitude collected up to l (the
input-bits lane's C_l/n per unit log-variance), the direction u_l carries the output direction and the future amplitude
C_L - C_l. Exact annealed version: Var(log|h_l|), Var(log A_l(u_l)) and their covariance from the input chain, with the
amplitude replica built by Gram surgery (direction of x', radius of x).
4.3 Small sigma: the closed relevance of the layer-l state is 1 minus the future noise's share of the variance; it is
near 1 while the radius is far above the noise floor and falls on the input-bits lane's scale L ~ n/2 - n at
sigma = 1e-3 (their onset); the chain computes it exactly.

## 5. Annealed versus quenched (HEURISTIC, testable)

5.1 Hypothesis H-rad: per-net (fixed-W) quantities depend on the net mainly through its radius history; the radius at a
layer varies by O(1) across nets (the stationary law) and by n^{-1/3} within a net (2.2). Consequences:
- the fixed-W variance of the direction, Var(u | W) ~ 2 delta*(Q(W)), is not self-averaging: its across-net CV tends to
  CV(q^{-2/3}) = 0.679 under the inverse-gamma radius (n -> inf); given the net's radius it should self-average;
- V_P(t; W) depends on W through T*(Q(W)) ~ Q^{1/3} (CV of T* also 0.679), so at fixed t it scatters most where V_P is
  steep (t ~ T*);
- ratio-of-annealed-means estimands weight large-radius nets; e.g. the annealed PR of the direction cloud is a ratio of
  E_W tr C^2-type moments dominated by small-radius nets (larger angular clouds).
5.2 Where the annealed count misleads: (a) tangent means (1.4) are carried by rare nets; (b) raw-state moments (1.5) are
infinite; (c) per-net relevance can concentrate in a few net-specific directions while the annealed PR, a ratio of
means over nets whose top directions differ, looks spread; the per-net PR distribution against the annealed ratio
measures this.
5.3 Across-net second moments of an r-replica quantity are 2r-replica quantities, so Var_W of V_P (2 replicas -> 4)
and of Var(u | W) (2 -> 4) are exact chain outputs; they test H-rad without nets.

## 6. What the chain explains (to be scored against earlier measurements in part D)
- cloud size: angle delta*(Q), with the measured 1/k shape the 5-8x excess (numerics lane; spectrum shape still a
  conjecture here, 2.7);
- births: n arccos(rho)/pi given the Gram, 0.62-0.63 sqrt(n) (exact chain), L0 0.59;
- interaction order: single injections decay algebraically while the cloud decays fast: D_u ~ 2.99 Q^{1/6} (numerics
  lane), and the flat low-order shares S1 ~ 2/3, C(t) ~ 1 - (1 - t)^{2/3} (2.6);
- input regime: amplitude/direction split (annealed 0.60/0.36 at 256 x 32 vs nets 0.49/0.47), 3n/l decay of differing
  gates (kernel), angular PR of the input cloud (4.1, new).
