# Backward bits: what the recursion's target is, and what a code can reach (v1, 2 Nov 2026 ~13:00Z)

Lane backward-bits (bead pool-qxszj1.27). Labels: PROVEN (proof here), CITED (standard result, reference given),
HEURISTIC, MEASURED (later, in the report). All information in bits.

## 0. Setting

Model S: h_0 = x ~ N(0, I_n); h_l = relu(W_l h_{l-1}) + sigma xi_l, xi_l ~ N(0, I_n) iid, l = 1..L-1; output
h_L = a = relu(W_L h_{L-1}) (no noise; as in the bit-accounting S4 runs). Markov chain h_0 -> h_1 -> ... -> h_L.
A code at layer l is a measurable map c_l = f_l(h_l) into a finite set (deterministic code; rate H(c_l)), or more
generally a random variable U with U - h_l - (h_{l+1}, ..., h_L) Markov (stochastic code; rate I(h_l; U)).
The output code c_L = Q(a) is a K-cell quantiser ("the last layer, trained until convergence"). Since a is a
deterministic function of h_{L-1}, c_L is also a code of h_{L-1}. Indexing below: the code at layer l is judged
against the code one layer later, c_{l+1}; Kelvin's "layer l-1 against layer l" is the same with l shifted.

Posterior of the next code: S_l(h) = P(c_{l+1} = . | h_l = h), a point of the simplex over the values of c_{l+1}.

## 1. Kelvin's target is the relevance ceiling (PROVEN)

Define the erased bits E_{l+1} = E_h H(c_{l+1} | h_l = h) = E H(S_l(h_l)) and the target
    T_l = H(c_{l+1}) - E_{l+1} = I(h_l; c_{l+1}).
For every code U of layer l (deterministic or stochastic), I(U; c_{l+1}) <= T_l (data processing on
U - h_l - c_{l+1}). So T_l is exactly Kelvin's "the bits of layer l+1, minus the bits the noise between the layers
destroys", and it is the most that any code of layer l can carry about c_{l+1}. Main's identification is correct.
Note T_l <= H(c_{l+1}): no target exceeds its successor's rate.

## 2. Every informative code carries strictly less than its own rate (PROVEN)

Assume l + 1 <= L - 1 (Gaussian noise between h_l and h_{l+1}) and every value of c_{l+1} has positive probability.
Proposition 2. (a) A deterministic code c_l that is not a.s. constant has H(c_l | c_{l+1}) > 0, hence
I(c_l; c_{l+1}) < H(c_l). (b) A stochastic code U with I(h_l; U) > 0 has I(U; c_{l+1}) < I(h_l; U).
Proof. Given h_l = h, h_{l+1} has the everywhere positive density N(relu(W h), sigma^2 I). Each cell
{f_{l+1} = j} has positive probability under the absolutely continuous law of h_{l+1}, so positive Lebesgue measure,
so P(c_{l+1} = j | h_l = h) > 0 for all j and h. (a) For values k of c_l and j of c_{l+1}:
P(c_l = k, c_{l+1} = j) = E[1{f_l(h_l) = k} P(c_{l+1} = j | h_l)] > 0 whenever P(c_l = k) > 0. If c_l = phi(c_{l+1})
a.s., then every k of positive probability equals phi(j) for the same j, so c_l is a.s. constant. (b) The gap is
I(h_l; U) - I(U; c_{l+1}) = I(h_l; U | c_{l+1}) (chain rule with U - h_l - c_{l+1}). If it were 0, then
p(u | h, c) = p(u | c); with U - h_l - c_{l+1}, p(u | h, c) = p(u | h); since every c has positive probability
given every h, p(u | h) = p(u | c = j) for all j, so p(u | h) does not depend on h and I(h_l; U) = 0. QED.
Consequence for main's criterion. "Rate reaches the target within tolerance AND prediction of c_{l+1} near the
limit" asks for H(c_l) ~ T_l and I(c_l; c_{l+1}) ~ T_l. By Proposition 2 these are incompatible except in the
limit where the gap H(c_l | c_{l+1}) is small; how small it can be at rate T_l is a property of the noise and the
code geometry, measured by the rate-relevance curve (section 4). A code with rate = T_l carries less than T_l; a
code carrying T_l - eps needs rate T_l - eps + (its gap).

## 3. Carrying the whole target needs infinite rate (PROVEN under a checkable condition)

Proposition 3. Suppose step l is noisy (l + 1 <= L - 1, sigma > 0; at l = L - 1 the output code itself attains its
ceiling) and that on some linear region R of h -> relu(W_{l+1} h) with P(h_l in R) > 0 the posterior S_l is not
constant (the non-degeneracy condition; it fails e.g. for a constant next code). Then no code with countably many values carries T_l, and every stochastic code with
I(U; c_{l+1}) = T_l has I(h_l; U) = infinity.
Proof. I(h_l, U; c_{l+1}) = I(h_l; c_{l+1}) (U - h_l - c_{l+1}) = I(U; c_{l+1}) + I(h_l; c_{l+1} | U); so
I(U; c_{l+1}) = T_l iff p(c | h_l, U) = p(c | U) a.s., and p(c | h_l, U) = S_l(h_l); so S_l(h_l) is a.s. a function
of U and I(h_l; U) >= I(h_l; S_l(h_l)). On R, S_l(h) = (phi_sigma * 1_A)(M h) for a matrix M and a cell indicator
1_A: a Gaussian convolution of a bounded function is real-analytic, so S_l is real-analytic on the connected open
set R. A non-constant real-analytic function on a connected open set equals a given value only on a null set
(the zero set of a non-zero real-analytic function has measure zero), and h_l has a density, so S_l(h_l) has no
atoms on R: its law has a continuous part of mass P(R) > 0, and I(h_l; S_l(h_l)) = H(S_l(h_l)) = infinity. QED.
The condition is checked numerically (the posterior varies within regions; it does for every non-trivial code).

## 4. The rate-relevance curve of a layer, and what can be certified

For a deterministic code with cells k, the loss against the ceiling is exactly
    T_l - I(c_l; c_{l+1}) = E KL( S_l(h_l) || mu_{c_l(h_l)} ),   mu_k = E[S_l(h_l) | c_l = k]       (PROVEN, standard)
so fitting a code is Bregman (KL) clustering of the posteriors S_l(h) (Slonim-Tishby sequential IB; with the rate
term, the deterministic information bottleneck of Strouse-Schwab 2017, objective H(c_l) - beta I(c_l; c_{l+1})).
The layer's curve I_l(R) = max {I(c_l; c_{l+1}) : H(c_l) <= R} is non-decreasing, I_l(R) < min(R, T_l) for R > 0
(sections 2-3), and I_l(R) -> T_l only as R -> infinity.
HEURISTIC (high resolution): if S_l(h) moves on a d-dimensional set, cells of Fisher diameter e cost about
d log2(1/e) bits and lose about e^2, so T_l - I_l(R) ~ C 2^(-2R/d): d/2 extra bits per halving of the loss.
Lower bound for codes with at most K cells (Pinsker, then the spectral relaxation of k-means; PROVEN for the population
covariance; the reported value is a plug-in estimate with a Monte Carlo correction (denominator M - 1), not a certified
bound):
    T_l - I(c_l; c_{l+1}) >= (1 / (2 ln 2)) sum_{j >= K} lambda_j(Cov S_l(h_l)),
lambda_j in decreasing order (Pinsker: KL >= |p - q|_1^2 / (2 ln 2) >= |p - q|_2^2 / (2 ln 2); the k-means
objective with K cells is at least the sum of the covariance eigenvalues beyond the top K - 1). It bounds codes by
their number of cells, not their entropy, and may be loose; it is reported where it is informative.
What is certifiable per layer: (i) T_l, H(c_l), I(c_l; c_{l+1}) near-exactly (estimators, section 7); (ii) the
consistency facts T_l <= H(c_{l+1}), I(c_l; c_{l+1}) <= min(H(c_l), T_l); (iii) optimality of a trained code within
its class only empirically (restarts, larger encoders, clustering the exact posteriors, a 1-D case with a known
optimum), plus the K-cell lower bound above.

## 5. Where Kelvin's number is a code length, and where it is not

5.1 Simulation with shared randomness (CITED). If encoder and decoder share unlimited random bits, the least rate
that lets the decoder output a c_{l+1} with the exact joint law with h_l is T_l per sample in the block setting
(classical reverse Shannon theorem: Bennett, Shor, Smolin, Thapliyal 2002; Cuff 2008), and at most
T_l + log2(T_l + 1) + 5 bits on average one-shot (Li and El Gamal 2018, strong functional representation lemma;
Harsha, Jain, McAllester, Radhakrishnan 2010 for the first one-shot bound). So "R minus the destroyed bits" is
exactly the cost of re-generating the next code with the right statistics, provided the receiver shares a random
seed. It is not the rate of any partition of h_l (sections 2-3).
5.2 Per-sample reproduction with the shared future noise (PROVEN). If the decoder must output the same c_{l+1} as the
sample, given the shared noise xi_{l+1}, any message m of h_l has
    H(m) >= I(h_l; m) >= H(c_{l+1} | xi_{l+1}) = T_l + I(h_l; xi_{l+1} | c_{l+1})
(m is independent of xi_{l+1}; c_{l+1} = psi(m, xi_{l+1}) is a function of (h_l, xi_{l+1}), and xi_{l+1} is
independent of h_l). The bits the noise "erases" are not erased when the noise is shared: this is the S4 regime,
whose counts rise toward the output.
5.3 The ladder at layer l (PROVEN): for every code U of h_l,
    I(U; c_{l+1}) <= T_l <= H(c_{l+1} | xi_{l+1}) <= H(c_{l+1}),
and, at a noisy step (sigma > 0, l + 1 <= L - 1, every value of c_{l+1} of positive probability), I(U; c_{l+1}) < rate(U)
when rate(U) > 0 (Proposition 2).

## 6. The chain: what the recursion's targets count (PROVEN)

The truth at layer l is I*_l = I(h_l; c_L), the information about the output code; I*_0 <= ... <= I*_{L-1} = H(c_L)
by data processing. The recursion's target T_l = I(h_l; c_{l+1}) is about the next CODE.
Proposition 6. (a) If c_{l+1} is sufficient for c_L (P(c_L | h_{l+1}) depends on h_{l+1} only through c_{l+1}), then
h_l - c_{l+1} - c_L is Markov and T_l = I*_l + I(h_l; c_{l+1} | c_L) >= I*_l: the target over-counts by what layer l
knows about the next code's own resolution beyond the output code. (b) Without sufficiency the two are not ordered:
a constant c_{l+1} gives T_l = 0 < I*_l whenever I*_l > 0.
Proof. (a) P(c_L | h_l, c_{l+1}) = E[P(c_L | h_{l+1}) | h_l, c_{l+1}] = P(c_L | c_{l+1}); then the chain rule
I(h_l; c_{l+1}, c_L) = I(h_l; c_{l+1}) = I(h_l; c_L) + I(h_l; c_{l+1} | c_L). (b) Immediate. QED.
By section 3 sufficiency costs infinite rate at a noisy step under the non-degeneracy condition, so a finite chain
with such steps sits in case (b): its targets are properties of its own codes, not of the net. Measured per layer: T_l, I*_l, the code's I(c_l; c_L) (best decoder), and the
chain's own prediction of c_L through its kernels P(c_{k+1} | c_k) (a Markov chain over codes). The accumulated loss
is A_l = I*_l - I(c_l; c_L) >= 0.

## 7. Three chains and one direct code (the procedure as run)

- Chain K (Kelvin's rule as written): code at l = the most relevant code with H(c_l) <= T_l (+ tolerance).
- Chain R (main's second condition): the cheapest code with I(c_l; c_{l+1}) >= T_l - eps; its rate may exceed T_l and
  even H(c_{l+1}).
- Chain P (the recursion with the output code as the fixed target, still one noisy layer per step): the target
  posterior at layer l is P~_l(h) = E_xi q_{l+1}(c_{l+1}(relu(W_{l+1} h) + sigma xi)), q_{l+1}(k) the mean of P~_{l+1}
  over cell k (P~_{L-1} exact); target T~_l = H(c_L) - E H(P~_l); code by the rate rule. It equals I*_l only when
  every cell is sufficient (P~_{l+1} constant within each cell of c_{l+1}). Exact cell averages are not enough:
  averaging within a lossy cell and pushing back through the noisy layer loses information even with infinite samples
  (a projection error, distinct from estimation error; review r1 #2). Its error is measured against I*_l.
- Direct codes (forward/output-targeted comparison): at each layer the same clustering on the exact posterior
  P(c_L | h_l) (Monte Carlo over the whole future), at the rate of chain K's code and at rate I*_l.
Convergence criterion used (replaces main's): a step is converged when (i) T_l is estimated within its tolerance;
(ii) the posterior predictor's excess cross-entropy is below its tolerance; (iii) the chosen code's rate and
relevance are within tolerance across restarts and of the code obtained by clustering the exact Monte Carlo
posteriors at the same rate. The deficit T_l - I(c_l; c_{l+1}) is reported, not required to vanish.

## 8. Estimators (what "near-exact" means here)

For N held-out points h_l^(i) and M independent noise draws each: counts n_ij of c_{l+1} = j.
- E_{l+1}: mean over i of the plug-in entropy of n_i./M plus the Miller-Madow term (m_i - 1)/(2 M ln 2), m_i = number
  of distinct codes seen; leading bias O(1/M^2) after correction; checked by M-doubling.
- H(c_{l+1}): plug-in on the N M pooled codes (bias (K - 1)/(2 N M ln 2), negligible).
- I(c_l; c_{l+1}) = H(c_{l+1}) - sum_k pi_k H(mu_k), mu_k the mean of n_i./M over the held-out points of cell k
  (unbiased for the cell's posterior; plug-in bias about (m_k - 1)/(2 N_k M ln 2) plus the between-point variance
  term, both checked by halving N).
- Codes are fitted on training points and evaluated on held-out points with fresh draws (no reuse).
- Standard errors by bootstrap over held-out points; tolerances registered in PREREG.md.

## 9. Addition v1.1 (2 Nov ~15:15Z, after the closed-form Gaussian chain): when the recursion is exact

Proposition 7 (PROVEN). Let m_{L-1} = c_L and, for l < L-1, let m_l be a re-simulation of m_{l+1}: given h_l, draw a
fresh copy of the next layer, h'_{l+1} = relu(W_{l+1} h_l) + sigma xi' (xi' independent of everything), and output
m_{l+1}(h'_{l+1}) (using fresh private noise for m_{l+1}'s own re-simulations). Then for every l the conditional law of
m_l given h_l equals the law of c_L given h_l. Hence the recursion's target T_l = I(h_l; m_{l+1}(h_{l+1})) equals
I*_l = I(h_l; c_L) at every layer and the code's information rate I(h_l; m_l) equals I*_l. In the entropy sense of
section 1 the erased bits of step l are H(c_L) - I*_l (the code's private noise decides them); I*_{l+1} - I*_l >= 0 is the
information lost across the transition. (Correction v1.3 after review r2: the earlier text called the latter the erased
bits. Re-simulation is sufficient for T_l = I*_l, not shown necessary.)
Proof. Downward induction. If law(m_{l+1} | h_{l+1}) = law(c_L | h_{l+1}), then law(m_l | h_l) =
E[law(m_{l+1} | h'_{l+1}) | h_l] = E[law(c_L | h_{l+1}) | h_l] = law(c_L | h_l) (h'_{l+1} has the law of h_{l+1} given h_l,
and h_l -> h_{l+1} -> c_L is Markov). T_l is computed with the actual h_{l+1}, whose conditional law given h_l is the
same, so T_l = I(h_l; c_L). QED.
Meaning. Run with codes that reproduce the next code's statistics (stochastic codes; in the linear-Gaussian chain the
analog code z_l = b h_l + noise chosen by your rate rule is exactly such a code), your recursion is exact: its targets
are what each layer knows about the output code, with no drift, all the way to the input; they are the per-sample
communication cost of re-generating the output code's statistics from layer l when sender and receiver share random
bits (section 5.1; one-shot within log2(T + 1) + 5 bits). The same codes are poor predictors: by Proposition 2b,
I(m_l; c_L) < I(h_l; m_l) = I*_l. Deterministic partitions are not re-simulations (Proposition 2a), which is where the
drift of the measured chains comes from.
Closed form (scripts/exact_gauss_chain.py): h_l = rho h_{l-1} + s xi_l, analog codes z = b h + N(0, 1), output code with
4.92 bits. Rate rule: T_l = I*_l at every layer (rho = 0.999: 4.17 ... 2.52 bits), and the codes know 88% (l = 14) to
81% (l = 0) of I*_l about the output code; 95% relevance rule: rate about 4.97 bits at every layer (no compression),
target stuck at 4.19, knows 95-99%.

## 10. Corrections v1.2 after the gpt-6-astra round-1 review (2 Nov ~15:25Z; review/review_r1.raw)
- Propositions 3, 6 and section 5.3 now state their conditions (noisy step, sigma > 0, non-degeneracy) (finding 1).
- Chain P's target equals I*_l only under cell sufficiency, not under exact cell averages (finding 2).
- The K-cell lower bound is reported as an estimate (finding 8).
- Scope (finding 21): every information count here is about one fixed 64-cell output quantiser (k-means on the output)
  at one noise level per config; carrying its information is not a guarantee about a continuous-output distortion.
  The output code's own distortion is reported (nMSE 0.4-7%).
- The exact 1-D chain's rate-rule answers are "best within the candidate set" (optimal partitions for every cell count,
  rate-penalised optima, every 2-cell code, rate-penalised 3-6-cell codes): the rate-constrained frontier is not fully
  enumerated, and the reviewer found a 0.05-bit omission by exhaustive search on an 8-point example (finding 20).
