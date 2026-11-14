## 3. The bits that matter at layer l: stationary regime (Part B)

Estimands (annealed, scale-free, exact replica constructions; `scratch/partB.py`; `results/partB_scores.json`).
- Closed relevance V_P(t) = E_W Var(E[u | noise up to l]) / E_W Var(u), u = a/|a|: two replicas identical at layer l,
  independent noise afterwards. It is what any description of h_l can explain about E[a] (the relevance lane's memory
  share M_l, here weight-averaged). The same for log|a|.
- Total relevance T_P(t) = E|u - u'|^2 / (2 E_W Var u) with independent pasts and a shared future: everything before l,
  including its interaction with the future noise.
- Relevant dimension: participation ratios of the output's dependence on the past, total (four pasts under one future)
  and closed (four pasts, four independent futures, 10 replicas).

3.1 How much and for how long: the direction (HEURISTIC mean field [C+A]; NUMERICAL, PB1-PB2). Two replicas that start
together and get independent noise open an angle that grows to delta* on the cloud's own time scale, so
  V_P(t) = 1 - Y((t - 1)/T*),   Y' = 1 - Y^{3/2},  Y(0) = 0,   T* = (Q + 1) delta*(Q) ~ 2.23 Q^{1/3} = 1.5 tau,
with total area 2(1 - pi/(3 sqrt3)) T* = 0.79 T* and an exponential tail at rate 1.5/T*. With the future shared, the cloud
angle decays algebraically, T_P ~ (1 + (t - 1)/(2T*))^{-2}, then exponentially at rate 1/Q.

{{TABLE_B}}

The closed relevance agrees with the mean field averaged over the radius law to within 0.003 at n = 256 and its area to
within 2-3% at n = 64-256 (PB1 hit {{PB1N}}); the total relevance's half-life agrees within 5% and its tail at 4 T* is
1.4-1.7 times the mean field (PB2 hit {{PB2N}}), the slower tail [A] attributes to unequal radii under shared noise. The
curves collapse in (t - 1)/T* across n (fig 2). Scaling: the direction of the state at layer L - t matters for the mean
for about 0.8 T* ~ 1.6 n^{1/3} layers (2-3 n^{1/3} to fall below 10%).

3.2 The amplitude remembers much longer (NUMERICAL). The closed relevance of log|a| is 0.79, 0.58, 0.34, 0.14 at t = 8, 16,
32, 64 for n = 64 and 0.96, 0.87, 0.71, 0.51, 0.30, 0.13 at t = 8, 16, 32, 64, 128, 256 for n = 256: it collapses in
t/n (fig 2, right) and halves after about n/4. PB4 missed as registered: at t >= 160 both relevances are zero within their
standard errors and the strict clause "log above direction at every t >= 8" fails on noise; the substantive part
(0.34 and 0.30 at t = n/2 against 0.01 for the direction) holds. The radial share of a net's (scale-normalised) output
variance is rho(q) = m(q)/(m(q) + 2A q^{-2/3}) (FORMAL 7.11 [C], with [A]'s m): 0.10, 0.24, 0.35, 0.46, 0.60, 0.75, 0.84 at
q = 0.1, 0.3, 0.577, 1, 2, 5, 10, independent of n at leading order; the chain's ratio of means is 0.375 and 0.349 at
n = 64 and 256 {{RHO1024}}. For a net's raw output the closed relevance at layer l is then
M_l ~ (1 - rho) V_P^dir(t) + rho V_P^log(t): small-radius nets forget in about 2 n^{1/3} layers, large-radius nets keep their
radius for order n layers. The relevance lane's per-net memory shares for raw a (their `results/report_tables.md`:
0.94, 0.79, 0.58, 0.40, 0.15 at t = 2, 4, 8, 16, 32 for n = 64, radial share 0.51-0.72) fit this two-channel form with
rho ~ 0.6 (0.54, 0.36, 0.20 predicted at t = 8, 16, 32).

3.3 How many directions are relevant (HEURISTIC free product [C+A; relevance lane Corollary 1c]; NUMERICAL, PB3). Given
the past, the future's singular frame is Haar relative to the cloud (section 7), so in the linear regime the spectrum of
the relevant covariance is the free multiplicative convolution of the cloud's spectrum and the future's, and
participation ratios combine as 1/PR = 1/PR_C + 1/PR_M - 1/n, with PR_M = n/(2t + 1) for t frozen-gate ReLU layers (one
layer has phi(M^2)/phi(M)^2 = 3). With PR_C = n/tau (2.4),
  PR_rel(t) = n/(tau + 2t):
of order n^{2/3} near the output and n/(2t) beyond t ~ tau/2. This replaces the "Lyapunov covariance times future
amplification, direction by direction" picture: the cloud's axes are past-measurable while the future's amplified
directions (covariant Lyapunov vectors k >= 2 included) are future-measurable and Haar relative to them, so dimensions
combine harmonically rather than direction by direction.

{{TABLE_PR}}

{{READ_PR}}

3.4 Survival of a layer-l difference (PB5). {{PERT}}

3.5 The stationary answer in one paragraph. At layer L - t, the state's direction decides a fraction
1 - Y((t - 1)/T*) of the output direction's variance (T* = 2.23 Q^{1/3}), spread over about n/(tau + 2t) directions
(n^{2/3} near the output); the radius carries a share rho(q) of the raw output variance for order n layers. Each net's
radius sets T*, tau, PR_C and rho; the directions themselves are net-specific and invisible to the chain (section 7).
