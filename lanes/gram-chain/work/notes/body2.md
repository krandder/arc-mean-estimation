## 3. The bits that matter at layer l: stationary regime (Part B)

Estimands (annealed, scale-free, exact replica constructions; `scratch/partB.py`; `results/partB_scores.json`).
- Closed relevance V_P(t) = E_W Var(E[u | noise up to l]) / E_W Var(u), u = a/|a|: two replicas identical at layer l with
  independent noise afterwards. It is what any description of h_l can explain about the conditional mean of the output
  direction u (for E[a] itself see 3.2: the radius carries the rest) (the relevance lane's memory
  share M_l, here weight-averaged). The same for log|a|.
- Total relevance T_P(t) = E|u - u'|^2 / (2 E_W Var u) with independent pasts and a shared future: everything before l,
  including its interaction with the future noise.
- Relevant dimension: participation ratios of the output's dependence on the past, total (four pasts under one future)
  and closed (four pasts, four independent futures; 10 replicas).

3.1 How much and for how long: the direction (HEURISTIC mean field [C+A]; NUMERICAL; PB2 hit, PB1 hit only under the
revised analysis). Two replicas that
start together and get independent noise open an angle that grows to delta* on the cloud's own time scale, so
  V_P(t) = 1 - Y((t - 1)/T*),   Y' = 1 - Y^{3/2},  Y(0) = 0,   T* = (Q + 1) delta*(Q) ~ 2.23 Q^{1/3} = 1.5 tau,
with area 2(1 - pi/(3 sqrt3)) T* = 0.79 T* and an exponential tail at rate 1.5/T*. With the future shared, the cloud angle
decays algebraically, T_P ~ (1 + (t - 1)/(2T*))^{-2}, then exponentially at rate 1/Q.

| n | closed V_P at t = 2, 4, 8, 16, 32: chain | mean field (averaged over radii) | V_P half-life / area: chain vs MF | total T_P at t = 2, 4, 8, 16, 32: chain | MF | T_P half-life, T_P(4T*): chain vs MF |
|---|---|---|---|---|---|---|
| 16 | 0.574, 0.219, 0.054, 0.012, 0.006 | 0.632, 0.268, 0.064, 0.008, 0.001 | 2.3 / 2.91 vs 3 / 2.98 | 0.725, 0.446, 0.231, 0.087, 0.024 | 0.700, 0.396, 0.172, 0.056, 0.014 | 3.5, 0.096 vs 4, 0.063 |
| 64 | 0.780, 0.469, 0.166, 0.031, 0.011 | 0.788, 0.482, 0.187, 0.037, 0.003 | 3.8 / 4.76 vs 4 / 4.85 | 0.839, 0.616, 0.393, 0.208, 0.093 | 0.823, 0.588, 0.344, 0.155, 0.053 | 5.7, 0.115 vs 6, 0.071 |
| 256 | 0.877, 0.666, 0.377, 0.126, 0.016 | 0.877, 0.665, 0.374, 0.123, 0.019 | 6.1 / 8.04 vs 6 / 7.87 | 0.905, 0.745, 0.534, 0.324, 0.168 | 0.893, 0.726, 0.511, 0.294, 0.133 | 9.0, 0.115 vs 9, 0.082 |
| 1024 | 0.928, 0.795, 0.566, 0.294, 0.089 | 0.928, 0.792, 0.567, 0.283, 0.075 | 9.6 / 14.3 vs 10 / 12.7 | 0.937, 0.817, 0.655, 0.446, 0.256 | 0.934, 0.821, 0.651, 0.442, 0.245 | 13.6, 0.107 vs 14, 0.089 |

The closed relevance agrees with the mean field averaged over the radius law to within 0.003-0.014 at n = 256-1024 and
the curves collapse in (t - 1)/T* (fig 2); the total relevance's tail is 1.2-1.6 times the mean field at t = 4T*, the
slower tail gpt-6-astra attributes to unequal radii under shared noise. V_P copies the whole state, so it is the closed
relevance of the full layer-l state for the output direction (its angular part dominates; the radial part is 3.2).
PB1 scoring, both ways: the registered analysis missed (the first recorded t below 0.5 is 8 at n = 256, against 6,
because t = 7 is not recorded; the full-grid area integrates noise out to t = 4n and gives -1.28 at n = 256 and 66.7 at
n = 1024); the revised analysis (linear interpolation between recorded t, area truncated at 8 T*, where the mean field is
below 1e-3) hits; the revision was made after seeing the n = 256 curve (`logs/deviations.log`). Scaling: the layer-l state
matters for the output direction's mean for about 0.8 T* ~ 1.6 n^{1/3} layers in total, and its relevance falls below 10%
after about 2-3 n^{1/3} layers.

3.2 The amplitude remembers far longer (NUMERICAL). The closed relevance of log|a| is 0.96, 0.87, 0.71, 0.51, 0.30, 0.13
at t = 8, 16, 32, 64, 128, 256 for n = 256 and 0.99, 0.97, 0.93, 0.83, 0.71, 0.56, 0.31, 0.14 at t = 8, 16, 32, 64, 128,
256, 512, 1024 for n = 1024: it collapses in t/n and halves after about n/4 (fig 2, right; at n = 16, dead outputs, 2^-16 per
sample, make the log channel unusable). PB4 missed as registered: the strict clause "log above direction at every
t >= 8" fails where both relevances are near zero (n = 64 at t = 160-192, n = 256 at t = 1024; log-channel standard errors
were not saved); the
substantive part (0.34, 0.30, 0.31 at t = n/2 for n = 64, 256, 1024, against about 0.01 for the direction) holds. The radial share of a net's
(scale-normalised) output variance, measured by the small-fluctuation proxy Var(log|a|)/(Var(log|a|) + tr Cov(u)) (a
variance-component ratio, not a Sobol share), is rho(q) = m(q)/(m(q) + 2A q^{-2/3}) (FORMAL 7.11 [C], with A's m;
HEURISTIC): 0.10, 0.24, 0.35,
0.46, 0.60, 0.75, 0.84 at q = 0.1, 0.3, 0.577, 1, 2, 5, 10, independent of n at leading order; the chain's ratio of means is
0.375, 0.349, 0.354 at n = 64, 256, 1024. For a net's raw output the closed relevance at layer l is then
M_l ~ (1 - rho) V_P^dir(t) + rho V_P^log(t): small-radius nets forget in about 2 n^{1/3} layers, large-radius nets keep their
radius for order n layers (the stationary lane's long-memory net, Q = 9 x median, is an instance). The relevance lane's
per-net memory shares for raw a at n = 64 (their `results/report_tables.md`: 0.58, 0.40, 0.15 at t = 8, 16, 32, radial
share 0.5-0.7) fit this two-channel form with rho ~ 0.6 (0.54, 0.36, 0.21).

3.3 How many directions are relevant (HEURISTIC free product [C+A; relevance lane Corollary 1c]; NUMERICAL; PB3 missed on
1 of 12 clauses). Given the past, the frozen future Jacobian's transverse singular frame is Haar (section 7, PROVEN);
assuming the same for the full relevance operator (HEURISTIC), in the linear regime the relevant covariance has the free
multiplicative convolution of the cloud's spectrum and the future's, and
participation ratios combine as 1/PR = 1/PR_C + 1/PR_M - 1/n, with PR_M = n/(2t + 1) for t frozen-gate ReLU layers (one
layer has phi(M^2)/phi(M)^2 = 3). With PR_C = n/tau, PR_rel(t) = n/(tau + 2t). This replaces "Lyapunov covariance times
future amplification, direction by direction": the cloud's axes are past-measurable while the future's amplified
directions (covariant Lyapunov vectors k >= 2 included) are future-measurable and Haar relative to them.
- The future's second spectral moment matches free probability: two orthonormal tangent probes read, up to
  finite-dimensional corrections (the probes live in the n - 1 transverse dimensions) and a ratio-of-means weighting,
  (tr M)^2/(tr M^2 - (tr M)^2/n) = n/(p - 1); the exact tangent chain gives 125.8, 63.6, 32.7, 15.2, 7.9 at t = 1, 2, 4, 8,
  16 (n = 256) against n/(2t) = 128, 64, 32, 16, 8 (`results/prM_tangent.json`, post hoc). This checks one moment ratio,
  not the whole spectral law.
- The output's dependence on the past spans more directions than the linear formula once gates switch across the cloud:

| n | t | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|---|
| 64 | total PR (chain) | 15.0 | 12.5 | 9.3 | 5.7 | 3.9 | 2.4 |
| 64 | closed PR (chain) | 15.0 | 12.3 | 8.3 | 4.9 | 2.9 | 1.4 |
| 64 | n/(n/PR_C + 2t) | 12.9 | 9.2 | 5.9 | 3.4 | 1.8 | 1.0 |
| 256 | total PR (chain) | 38.8 | 30.2 | 25.0 | 18.2 | 12.6 | 7.4 |
| 256 | closed PR (chain) | 38.8 | 29.9 | 23.7 | 16.3 | 8.7 | 4.5 |
| 256 | n/(n/PR_C + 2t) | 35.4 | 27.7 | 19.4 | 12.1 | 6.9 | 3.7 |

  The formula is 9-16% low at t = 1 (and t = 2 at n = 256) and 22-58% low at t = 2-4 (PB3's single failing clause:
  total PR at n = 64, t = 4, 1.58 times). Writing PR = n/(n/PR_C + c t), the chain gives c ~ 1.1-1.6 for the closed
  version and c ~ 1.0-1.6 for the total version at t <= 16, between the soft-gate value 1 (each layer acting like a
  Gaussian matrix on differences whose gates differ) and the frozen-gate 2. So at n = 256 the closed relevance of layer
  L - t has variance-weighted participation ratios of about 39, 30, 24, 16 and 9 at t = 1, 2, 4, 8, 16. These are annealed
  moment ratios, not per-net dimensions: Part C finds the median net's cloud PR at about 0.7 of the variance-weighted
  value. For t of order n the formula fails altogether (the future saturates at one direction).

3.4 Survival of a layer-l difference (PB5 {{PB5_STATUS}}). A replica perturbed by a vector of relative size eps orthogonal
to the state, all noise shared afterwards: in the finite-angle regime the angle decays algebraically, (1 + eps t/(3 pi))^{-2}
before the dilution e^{-t/Q} takes over [A]; for eps t << 3 pi it decays only through the dilution, and the exact annealed
mean decays even more slowly (annealed tangent means are carried by rare nets, section 1). Chain against the mean field
(hidden direction): eps = 0.3 at n = 256 survives 0.937, 0.780, 0.406, 0.207 at t = 1, 4, 16, 32 against 0.929, 0.756, 0.386,
0.198; eps = 0.1: 0.916, 0.703, 0.505 at t = 4, 16, 32 against 0.885, 0.635, 0.434; eps = 1e-3: 0.995, 0.977, 0.864 at t = 4,
16, 64 against 0.961, 0.861, 0.606. At n = 1024 the finite-eps survival matches the mean field within 0-3% (eps = 0.3:
0.778, 0.427, 0.230 at t = 4, 16, 32 against 0.777, 0.423, 0.231). Small differences outlive large ones (10x at t = n/4,
n = 256), the same mechanism as
the interaction order (a lone injection decays slowly, the full cloud fast). Two orthogonal finite perturbations' responses
spread over more directions than tangent ones (n = 64, t = 8: 4.7 against 3.6).

3.5 The stationary answer. At layer L - t, the state decides a fraction 1 - Y((t - 1)/T*) of the output direction's
variance (T* = 2.23 Q^{1/3}), spread over about n/(n/PR_C + c t) directions (c ~ 1.1-1.6; order n^{2/3} near the output, as
variance-weighted participation ratios); the radius carries a share rho(q) of the output variance (small-fluctuation
variance proxy, HEURISTIC) for order n layers. Each net's radius sets T*,
PR_C and rho; the directions themselves are net-specific and invisible to the chain (section 7).
