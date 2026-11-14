## 3. The bits that matter at layer l: stationary regime (Part B)

Estimands (all annealed, scale-free, exact replica constructions; t = layers to go including the output layer).
- Closed relevance V_P(t) = E_W Var(E[u | noise up to l]) / E_W Var(u), u = a/|a|: two replicas identical at l with
  independent noise afterwards. This is what a description of h_l can explain about E[a] (the relevance lane's memory
  share M_l, here annealed). The same for log|a| (the amplitude).
- Total relevance T_P(t) = E|u - u'|^2 / (2 E_W Var u) with independent pasts and a shared future: the total effect of
  everything before l, including its interaction with the future noise.
- Relevant dimension: participation ratios of the output's dependence on the past, total (P1..P4 under one future) and
  closed (four pasts, four independent futures; 10 replicas).

3.1 How much and for how long (HEURISTIC mean field [C+A]; NUMERICAL test, PREREG PB1, PB2, PB4). Two replicas that start
together and get independent noise open an angle that grows to delta* on the cloud's own time scale, so in mean field
  V_P(t) = 1 - Y((t - 1)/T*),  Y' = 1 - Y^{3/2}, Y(0) = 0,  T* = (Q + 1) delta*(Q) ~ 2.231 Q^{1/3} = 1.5 tau,
with area 2(1 - pi/(3 sqrt3)) T* = 0.79 T* and an exponential tail at rate 1.5/T*; with the shared future the cloud angle
decays algebraically, T_P ~ (1 + (t - 1)/(2T*))^{-2}, then exponentially at rate 1/Q (and, [A], more slowly because unequal
radii make the same noise rotate replicas differently).
{{TABLE_B}}
{{READ_B}}

3.2 The amplitude remembers much longer. {{AMP_B}} The radial share of a net's output variance has the closed form
rho_rad(q) = m(q)/(m(q) + 2A q^{-2/3}) (FORMAL 7.11 [C], with A's m): 0.10, 0.24, 0.35, 0.46, 0.60, 0.75, 0.84 at
q = 0.1, 0.3, 0.577, 1, 2, 5, 10, independent of n at leading order. So for the raw output a net's relevance at layer l is
M_l ~ (1 - rho_rad) V_P^dir(t) + rho_rad V_P^log(t): small-radius nets forget in ~2 n^{1/3} layers, large-radius nets keep
their radius for order n layers (the stationary lane's long-memory net, Q = 9 x median, is an instance). {{PC7}}

3.3 How many directions (HEURISTIC free-position formula [C+A], relevance lane Corollary 1c; NUMERICAL test PB3).
Given the past, the future's singular frame is Haar relative to the cloud (section 7), so in the linear regime the
spectrum of the relevant covariance is the free multiplicative convolution of the cloud's spectrum and the future's;
participation ratios combine as 1/PR = 1/PR_C + 1/PR_M - 1/n, with PR_M = n/(2t + 1) for t frozen-gate ReLU layers (one
layer has phi(M^2)/phi(M)^2 = 3). With PR_C = n/tau (2.4):
  PR_rel(t) = n/(tau + 2t):
about n^{2/3} directions near the output, falling like n/(2t) beyond t ~ tau/2.
{{TABLE_PR}}
{{READ_PR}}

3.4 Survival of a layer-l difference (PB5). {{PERT}}

3.5 The stationary answer in one line. At layer L - t the state's direction decides a fraction 1 - Y((t - 1)/T*) of the
output direction's variance (T* ~ 2 n^{1/3}; about 0.8 T* layers of relevance in total) and that part lives in about
n/(tau + 2t) directions (n^{2/3} near the output); the radius carries a share rho_rad(q) of the raw output variance for
order n layers. Each net's radius sets T*, tau, PR_C and rho_rad; the directions themselves are net-specific and
invisible to the chain (section 7).
