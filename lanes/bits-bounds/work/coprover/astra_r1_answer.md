codex
1. Target 1: computational model

DEFINITION. A bounded-memory sweep algorithm has:

- Read-only access to weight blocks W_1,...,W_L, in at most p complete forward or backward passes.
- M bits of persistent working memory. Particles, cumulants, mixture components, cached weights, cell descriptions and accumulated answers all count.
- A public random tape independent of the weights. It cannot store information learned about the weights.
- Charged computation between reads, including preprocessing, integration subroutines and computation after the last pass.
- An output in R^n.

A current weight block may be read repeatedly while the algorithm remains at that layer. Retaining any part of it after advancing uses memory. There is no free external storage.

For finite-precision inputs this is a word-RAM model with specified word length b. For Gaussian real weights, one can instead request successive bits of entries, charging for them. Statements about M numbers require a precision assumption: M unrestricted real numbers are not M bits.

I measure arithmetic work in units of n^2 scalar operations, so a dense matrix-vector product costs order one. Precision costs are additional. The model can impose a polynomial work budget B(n,L,1/eps) and constant p.

PROVEN: placement of the four families.

a. ARC-style cumulant closures.
One forward pass. Keeping all symmetric moments through order K requires

  S_K = sum_{j=0}^K binom(n+j-1,j) = binom(n+K,K)

numbers. Memory is O(b S_K). Standard fixed-order tensor propagation takes n^{O(K)} arithmetic work per layer, plus the actual closure-evaluation cost. The model does not assume that the closure is accurate.

b. Gaussian closures with gate splits.
One forward pass with S active Gaussian components uses O(b S n^2) bits for means, covariances and weights. Dense covariance propagation costs O(S n^3) scalar operations per layer; splitting, truncation and mixture reduction are charged separately. Replacing a truncated Gaussian by a Gaussian is an approximation, not an exact operation.

c. Branch-and-bound on input cones.
A breadth-first implementation can use one forward pass. On a cell C, h_l(x)=A_C x; maintaining A_C and all accumulated gate inequalities requires at most O(n^2 L) numbers per active cell. With B active cells, a straightforward bound is O(b B n^2 L) memory and O(B n^3) propagation work per layer, plus branching and certified Gaussian integration.

A depth-first implementation may use much less cell memory, but it must either cache the weights, use additional passes, or pay for repeated access. None is free.

d. Multilevel shared-trajectory sampling.
One pass computes the reference trajectory and its required norm products. A second forward pass propagates all sampled trajectories, stopping each at its assigned level. With m_j samples at level j, memory is O(b n sum_j m_j), plus reference data and accumulators. Work is O(L + sum_j m_j r_j) matrix-vector products.

Alternatively, caching all weights permits sequential trajectories with O(b L n^2) weight memory.

PROVEN limitation. When M permits storing all weights, this model contains essentially every polynomial-time algorithm on the explicit network. Thus a strong time lower bound for the whole model is an explicit computational lower bound. A trajectory-entropy argument alone cannot supply it.

Below I distinguish:

  N_law: bits needed to distinguish past laws for future mean queries;
  N_path: bits needed to reconstruct individual future-relevant trajectories;
  N_lin: number of linear summary coordinates.

These quantities have different lower-bound meanings.


2. Target 2: definitions and lower bounds

Throughout the proofs, delta is an absolute root-mean-square error tolerance. For a fixed network, substitute delta=eps sqrt(V(W)).

For an ensemble, I explicitly use

  E_W ||mu_hat-mu||^2 <= eps^2 E_W V(W).

This is different from E_W[||mu_hat-mu||^2/V(W)]<=eps^2. Bounds transfer between these formulations on variance bands v_-<=V(W)<=v_+. They should not otherwise be interchanged.

2.1. The exact information parameter for forward-only mean estimation

DEFINITION. Write A for the prefix weights and B for the suffix weights. Let P_A be the cut-state law. Define

  f_B(h) = g_B(h)                         in the noiseless case,
  f_B(h) = E_future-noise[G_B(h,noise)]   in Model S.

Set

  T(A)(B) = integral f_B(h) P_A(dh).

Thus T(A) is the entire function of future weights that a prefix summary must support.

For independent prefix and suffix distributions nu and pi, regard T(A) as a random element of the Hilbert space

  H = L^2(pi; R^n).

For any square-integrable random element Z, define its K-point quantization error by

  D_K(Z) = inf_{z_1,...,z_K} E min_i ||Z-z_i||^2.

Define

  N_law(l,D) = min{b integer >=0 : D_{2^b}(T(A)) <= D}.

This accounts for the past through P_A and for the future through the distribution of mean-query functions f_B. It measures uncertainty about a law, rather than uncertainty about an individual input.

PROVEN: exact one-pass characterization.

Every forward-only algorithm whose cut state contains b bits has annealed squared error at least

  D_{2^b}(T(A)).

Conversely, with unrestricted computation, a quantizer attaining that distortion gives a b-bit one-way estimator. If the infimum is not attained, the converse holds with arbitrarily small additional error.

Proof. Fix the algorithm’s public randomness. Its prefix state takes at most 2^b values. For each state s, the suffix computation defines a function d_s(B), an element of H. Its error is

  E_A ||T(A)-d_{S(A)}||_H^2
    >= E_A min_s ||T(A)-d_s||_H^2
    >= D_{2^b}(T(A)).

Averaging over public randomness preserves the inequality.

Conversely, encode A by the nearest quantizer center T_i and decode by evaluating T_i(B). This has precisely the quantizer’s distortion. This is an information-theoretic construction: finding the index and evaluating a center may be computationally expensive. QED.

PROVEN: uniform version.

For a family P of possible prefix laws and a family B of suffixes, define

  d(P,Q) = sup_B ||integral f_B d(P-Q)||.

A deterministic one-way algorithm uniformly accurate to delta needs

  b >= log_2 Pack(P,d,2 delta),

where packing means pairwise distance strictly greater than 2 delta. A delta-cover gives an upper bound

  b <= ceil(log_2 Cover(P,d,delta)).

Proof. If two packed laws had the same message, the common answer for every suffix would be within delta of both means, contradicting the triangle inequality. For the upper bound, transmit a covering-center index and answer using that center’s mean function. QED.

PROVEN limitation. These quantities cannot exceed the information needed to describe the prefix weights to adequate precision.

For example, suppose sigma=0 and every weight matrix has operator norm at most B, with C=B+1. Approximate each prefix matrix to operator-norm error

  eta = min{1, delta/[sqrt(n) l C^{L-1}]}.

ReLU is 1-Lipschitz, so telescoping the layer errors gives

  ||mu(W)-mu(W_tilde)|| <= sqrt(n) l C^{L-1} eta <= delta.

Entrywise grids with spacing 2 eta/n achieve that operator-norm accuracy. Since each entry lies in [-B,B], a sufficient prefix description length is

  n^2 l ceil(log_2(3+Bn/eta)) bits.

The decoder may still face a hard integration problem. This is exactly where an information upper bound stops being an algorithmic upper bound.

2.2. Future-aware law information

DEFINITION. If the encoder knows B, replace the random function T(A) by the vector mu(A,B). The corresponding b-bit distortion is

  E_B D_{2^b}(mu(A,B) | B).

This can be much smaller than forward-only distortion: the encoder answers one query instead of preparing for all possible queries.

PROVEN qualification. This describes an ideal future-informed encoder. A preliminary backward pass must actually convey enough information about B to the prefix computation. Its communication, memory and computation count. Small future-aware output entropy does not imply that the relevant future information has a small computable description.

For p streaming passes, the standard cut reduction produces a communication protocol using at most about 2pM bits: each crossing or reset transfers the current memory. Consequently, one-way lower bounds do not automatically survive additional passes.

2.3. Trajectory bits, future metrics and Gaussian rate-distortion

DEFINITION. For a fixed network, let H~P_l and Y=f_B(H). Define

  N_path^fixed(l,D) = min{b : D_{2^b}(Y)<=D}.

Its information relaxation is

  R_path(l,D)
    = inf I(H;Z),

where the infimum is over encoders and decoders satisfying

  E ||f_B(H)-a(Z)||^2 <= D.

Mutual information is measured in bits.

A forward-blind version uses the distortion

  E_{H,B} ||f_B(H)-a(Z,B)||^2,

with Z generated from H before B is known.

These definitions account for future nonlinearities exactly. Their local linear approximations involve Jacobians, but the definitions do not.

PROVEN: when this is a memory lower bound.

If an algorithm must encode each cut state into b bits and reconstruct its future output with average squared error D, then

  b >= R_path(l,D),

and deterministic fixed-length encoding needs at least N_path^fixed(l,D) bits.

Proof. For the encoded state Z,

  I(H;Z) <= H(Z) <= b.

The reconstruction constraint makes this encoder admissible in the definition of R_path. The fixed-length statement is precisely the quantization definition. QED.

This restriction applies to trajectory-preserving particle compression and suitable cellwise reconstruction schemes. It does not apply to all mean estimators, cumulant closures or mixture closures.

COUNTEREXAMPLE, PROVEN. Let H~N(m,C), and let f_B(h)=Ah. The trajectory rate-distortion can be arbitrarily large, but

  E f_B(H)=Am.

If m is known, integration requires no trajectory representation. Hence N_path is not a general lower bound for estimating the mean.

PROVEN: exact Gaussian formula.

Suppose H~N(m,C) and f_B(h)=Ah+c. Let lambda_1,...,lambda_d be the positive eigenvalues of

  A C A^T,

equivalently of C^{1/2} A^T A C^{1/2} after removing zero eigenvalues.

For 0<D<sum_i lambda_i,

  R_path(l,D)
    = (1/2) sum_i [log_2(lambda_i/theta)]_+,

where theta is the unique solution of

  sum_i min(lambda_i,theta)=D.

For D>=sum_i lambda_i, the rate is zero.

Proof of the lower bound. Diagonalize the centered Gaussian output Y. Replace any reconstruction by E[Y|Z], which can only reduce error. Put

  d_i = E Var(Y_i|Z).

Then 0<=d_i<=lambda_i and sum_i d_i<=D. Gaussian maximal entropy and conditional subadditivity give

  I(Y;Z)
    >= (1/2) sum_i log_2(lambda_i/d_i).

Minimizing this expression subject to the distortion constraint gives d_i=min(lambda_i,theta), by the elementary Lagrange-multiplier equations.

For achievability, independently in each coordinate construct

  Y_i = Y_hat_i + E_i,

with independent Gaussian terms of variances lambda_i-d_i and d_i. This has distortion d_i and mutual information (1/2)log_2(lambda_i/d_i). Coordinates with d_i=lambda_i are not transmitted. Since Y is a function of H, the encoder can implement this test channel from H. QED.

The matrix C^{1/2}A^TAC^{1/2}, rather than C or A^TA alone, is the appropriate local combination of past and future.

PROVEN warning. In the noiseless case, with arbitrary future-aware encoders, Y=g_l(H_l) is the final output at every cut. Therefore N_path^fixed and R_path are independent of l for a fixed network.

A genuinely layer-dependent theory must impose additional restrictions, such as future blindness, local encoders, computable partitions or limited passes. Otherwise “bits at layer l” simply means “bits in the final output.”

2.4. Linear summaries

DEFINITION. Let the cut operator have kernel mu(A,B), acting from L^2(nu) to L^2(pi;R^n), and let its singular values be s_1>=s_2>=....

Define

  N_lin(l,D) = min{r : sum_{j>r} s_j^2 <= D}.

PROVEN. For one-way summaries consisting of r linear functionals of the prefix law and a linear suffix readout, the optimal annealed squared error is

  sum_{j>r} s_j^2.

Proof. Such a scheme produces a rank-at-most-r approximation S to the cut operator T. Let Q project onto the range of S. Then

  ||T-S||_HS^2
    >= ||(I-Q)T||_HS^2
    = sum_j s_j^2(1-||Q u_j||^2)
    >= sum_{j>r} s_j^2.

The last step uses 0<=||Q u_j||^2<=1 and sum_j ||Q u_j||^2<=r. Truncated singular-value decomposition attains equality.

The encoder functions in this decomposition are linear in P_A, since mu(A,B)=integral f_B dP_A. QED.

This is the appropriate parameter for K1. It does not lower-bound nonlinear closures. K2’s nonlinear description-length bounds are an explicit obstruction to extending it indiscriminately.

2.5. Explicit forward-only versus future-aware separation

PROVEN. There is a width-d, depth-2 bias-free ReLU family for which constant relative precision requires Omega(d) forward-only bits, but O(log d) bits with a preliminary future-reading pass.

Let u in {0,1}^d and

  W_1 = diag(1+u_1,...,1+u_d).

The suffix selects coordinate j and places it in the first output coordinate:

  a(x) = (1+u_j) ReLU(x_j) e_1.

Write

  c = 1/sqrt(2 pi),
  v = (pi-1)/(2 pi).

Then

  mu = c(1+u_j)e_1,
  V = v(1+u_j)^2.

For deterministic uniform guarantees, any

  eps < 1/[4 sqrt(pi-1)]

lets the output distinguish u_j by thresholding at 3c/2. Since j is unknown when the prefix is summarized, distinct u require distinct messages: at least d bits.

For randomized mean-square guarantees, let U and J be uniform. Thresholding makes a bit error only when the first output coordinate has error at least c/2. Thus

  Pr(bit error)
    <= 4 E||mu_hat-mu||^2/c^2
    <= 16(pi-1) eps^2.

If eps<=1/[8 sqrt(pi-1)], this is at most 1/4.

Let S be the message and R public randomness. Binary entropy and conditioning give

  H(U|S,R)
    <= sum_j H(U_j|S,R)
    <= d h_2(1/4).

Consequently,

  b >= I(U;S|R)
    >= d[1-h_2(1/4)]
    > 0.188 d.

If the suffix is read first, retain j using ceil(log_2 d) bits. On reading the prefix, retain only u_j and output its known mean. For fixed eps the total memory is O(log d).

Thus the memory separation is Omega(d/log d), or d versus one payload bit if j is public side information. Additional precision costs O(log(1/eps)).

This is a worst-case ReLU construction. It is not an average-case lower bound for iid He weights.

2.6. A matching “hash-table” query lower bound

PROVEN. Let K>=2, and suppose an unknown table y_1,...,y_K in {0,1} is accessible only by value queries. Define

  mu = K^{-1} sum_i y_i,
  V = K^{-1} sum_i (y_i-mu)^2.

For 0<eps<=1/2, any algorithm using at most m distinct queries and satisfying

  E_algorithm (mu_hat-mu)^2 <= eps^2 V

for every table must have

  m >= K/[2(1+eps^2 K)]
    >= (1/4) min(K,eps^{-2}).

Conversely,

  m = ceil(K/[1+eps^2(K-1)])

uniform queries without replacement suffice.

Proof of the lower bound. Draw p uniformly from [0,1], then draw the table entries independently as Bernoulli(p). Adaptive querying provides no advantage in choosing the next unseen entry: conditional on p, all unseen entries remain independent Bernoulli(p).

After m queries with s ones, p has posterior Beta(s+1,m-s+1). With u=K-m unseen entries, the expected posterior variance of the table mean is

  E Var(mu | observations)
    = u/(6K^2) + u^2/[6K^2(m+2)]
    = (K-m)(K+2)/[6K^2(m+2)].

Here E[p(1-p)|observations], averaged over observations, is 1/6, and the average posterior variance of p is 1/[6(m+2)].

Also,

  E V = (K-1)/(6K).

Every estimator’s Bayes risk is at least the expected posterior variance. Therefore

  (K-m)(K+2) <= eps^2 K(K-1)(m+2).

Solving for m, and using eps^2<=1/4, gives the stated lower bound.

For the upper bound, the mean of m uniform samples without replacement has variance

  [(K-m)/(m(K-1))] V.

The displayed choice of m makes this at most eps^2 V. QED.

If K=2^N, the query complexity is therefore

  Theta(min(2^N,eps^{-2})).

The essential restriction is value-oracle access. Readable neural-network weights are not such an oracle.


3. Target 3: matching constructions, multilevel comparison and random-network estimates

3.1. What matches which bound

PROVEN.

- N_law is matched exactly, information-theoretically, by a codebook of mean-query functions.
- N_lin is matched by truncated singular-value decomposition.
- The table-query lower bound is matched by sampling without replacement or full enumeration.
- Gaussian R_path is matched by the Gaussian test channel; this is an information-rate result, not a finite-word implementation guarantee.

None of the first three facts, by itself, supplies an efficient codebook or an efficient integration algorithm for random networks.

A concrete finite-bit Gaussian construction is also available. Suppose the first r covariance eigenvalues leave tail variance at most D/2. Put

  T = sum_i lambda_i,
  t = sqrt(2 log(8T/D)),
  Delta = sqrt(D/(2r)).

Clip coordinate i at ±t sqrt(lambda_i), then round to a grid of spacing Delta. Discard the remaining coordinates. This uses at most

  ceil sum_{i=1}^r log_2[3+2t sqrt(2r lambda_i/D)]

bits and has squared error at most D.

Proof. For Z~N(0,1),

  E(|Z|-t)_+^2 <= exp(-t^2/2).

Thus total clipping error is at most D/8; rounding error is at most r Delta^2/4=D/8. Applying (a+b)^2<=2a^2+2b^2 and adding the D/2 discarded tail gives D. QED.

This matches the leading small-D rate for a fixed finite rank, with additional logarithmic terms.

3.2. Integrating irrelevant bits

PROVEN UNDER an explicit integration-access hypothesis.

Suppose a cut partition produces a discrete variable Z with K cells, known probabilities p_z, and computable conditional output means

  m_z = E[Y|Z=z].

Then

  mu = sum_z p_z m_z.

Enumeration is exact. Sampling Z and evaluating m_Z is unbiased, with variance

  tr Var(m_Z) <= V.

With uniform cells and unrestricted unknown m_z, Section 2.6 gives the matching worst-case query complexity.

The construction cost matters. Let B be the cost of obtaining the partition and probabilities, and c the cost of a conditional-mean query. The resulting bound is

  B + O(c min(K,eps^{-2})).

If the “query” requires a full trajectory, c=L. If a cut-state representative is already available, it may cost L-l. Computing the cell probability or conditional mean is never implicitly free.

In the sweep model, evaluating K representatives can use one batch with O(Kn) numbers, or cached weights with sequential evaluation. A claim of both tiny memory and one pass must account for this tradeoff.

PROVEN: useful approximate version.

Suppose c(Z) is a computable output approximation whose mean mu_c is known and

  E||Y-c(Z)||^2 <= D.

Then

  mu_hat = mu_c + m^{-1} sum_{i=1}^m [Y_i-c(Z_i)]

is unbiased and satisfies

  E||mu_hat-mu||^2 <= D/m.

This follows directly from independence and variance <= second moment.

Alternatively, the deterministic answer mu_c has squared error at most D by Jensen’s inequality. If mu_c is computed with deterministic error at most eta, the control-variate estimator has MSE at most

  eta^2 + D/m.

This identifies two separate requirements: a good representation and a cheap integral of that representation.

3.3. Best allocation within a multilevel hierarchy

PROVEN. Conditional on a reference trajectory, suppose a telescoping estimator has independent level samples, level variances v_j and per-sample costs c_j. If the telescoping expectation equals mu for every reference, sharing that reference creates no additional bias or reference-mean variance.

Ignoring integer sample counts, the minimum work for squared error delta^2 is

  C_hierarchy(delta)
    = [sum_j sqrt(v_j c_j)]^2/delta^2.

Proof. With m_j samples, variance is sum_j v_j/m_j and work is sum_j m_j c_j. Cauchy-Schwarz gives

  (sum_j sqrt(v_j c_j))^2
    <= (sum_j v_j/m_j)(sum_j m_j c_j).

Equality holds when m_j is proportional to sqrt(v_j/c_j). Rounding each m_j upward adds at most sum_j c_j work. QED.

Thus the best shared-trajectory sampler within a specified collection of hierarchies has cost

  setup + inf_hierarchy [sum_j sqrt(v_j c_j)]^2/delta^2,

plus integer-allocation overhead. An upper bound for one dyadic hierarchy is not a lower bound for this infimum.

PROVEN UNDER H_ML. Assume the K5 residual bound holds uniformly over the depth regime being considered:

  E||Y-G_r||^2 <= C V_ang(1/r+n/L^2),

with an integrable initial control, terminal exact correction, and costs O(r). Here V_ang is the variance after integrating the input radius.

Dyadic differences then have

  v_j <= C' V_ang(1/r_{j-1}+n/L^2),
  c_j <= C'' r_j.

Summing their square-root variance-cost products gives

  sum_j sqrt(v_j c_j)
    <= C''' sqrt(V_ang)[log(2L)+sqrt(n/L)].

The geometric-series calculation uses sum_j sqrt(r_j)=O(sqrt(L)).

Writing rho=V_ang/V<=1, and allowing ordinary radius-exact MC as an alternative, yields

  C_dyadic
    = O( L
         + rho eps^{-2} min{L, log^2(2L)+n/L} ).

The O(L) term includes the reference pass and integer sample counts.

Conditional depth comparison, with rho of constant order:

- L<sqrt(n): this bound certifies no growing gain over ordinary MC.
- sqrt(n)<L<n: the variance-work gain can be of order L/[log^2 L+n/L].
- L=alpha n: the variance-work gain is order n/log^2 n.
- L>>n: the same calculation predicts order L/log^2 L, only if H_ML remains valid in this regime.

The last two gains require enough precision, or amortization, for setup not to dominate. For fixed eps, the unavoidable O(L) setup prevents the total-cost gain from growing without bound.

The statement supports K5 in its stated regime. Uniform extrapolation into all four regimes is a separate hypothesis.

3.4. Comparison with the relevant-bits estimator

PROVEN UNDER the partition-access hypothesis.

A K-cell exact conditional estimator has cost

  C_cells = B + O(c min(K,eps^{-2})).

It beats the best multilevel sampler precisely when this is smaller than the multilevel infimum above. A small K alone is insufficient: B and c can dominate.

For example, at L=alpha n, beating the displayed dyadic variance-work bound by enumeration requires

  B + c K = o(eps^{-2} log^2 n),

in the regime where setup is negligible. If each cell evaluation costs order n, this requires

  K = o(eps^{-2} log^2 n/n),

as well as inexpensive cell construction.

I cannot prove such an efficiently constructible partition for the genuine He ensemble. Nor can I prove that none exists. That is the central computational gap.

3.5. What can actually be estimated about N for random networks?

PROVEN: a general output-information upper bound.

For any R^d-valued Y with covariance eigenvalues lambda_i, its squared-error rate-distortion is at most that of the Gaussian with the same covariance. In particular, if V=tr Cov(Y),

  R_Y(D) <= (d/2) log_2(1+V/D).

Proof of the displayed bound. Let Z=Y+G with independent Gaussian G of covariance (D/d)I, and reconstruct by Z. Distortion is D. Gaussian maximal entropy gives

  I(Y;Z)
    <= (1/2) log_2 det(I+d Cov(Y)/D)
    <= (d/2) log_2(1+V/D).

The eigenvalue-wise Gaussian upper bound follows similarly by using the Gaussian test-channel coefficients coordinatewise; the distortion computation uses only covariance. QED.

This bounds R_path, not N_law and not computational work.

PROVEN UNDER a quantitative ray approximation.

Suppose a unit vector q satisfies

  E||(I-qq^T)(Y-EY)||^2 <= D/2.

Discarding that transverse component and encoding the remaining scalar gives

  R_path(D) <= (1/2) log_2(1+2V/D).

Thus, if a final cloud has transverse variance O(V/n), then for eps^2 much larger than 1/n,

  R_path(eps^2 V) = O(log(1/eps)).

K9 makes this plausible at L=alpha n. It does not establish a uniform finite-n bound or an efficient scalar-amplitude integral. This small future-aware trajectory rate is compatible with a large forward-only law description.

HEURISTIC: a local Lyapunov-spectrum estimate.

Let t=L-l. Assume, explicitly:

- The relevant cut fluctuations have approximately isotropic covariance tau_l^2 I in a d-dimensional tangent space.
- The future can be replaced at the desired precision by a fixed Jacobian.
- Its squared singular values satisfy
    s_i^2 approximately s_0^2 exp[-2t(i-1)/n].

Then the predictive covariance eigenvalues are

  lambda_i approximately a exp[-beta(i-1)],
  a=tau_l^2 s_0^2, beta=2t/n.

Under an exact geometric spectrum, the water-filling formula in Section 2.3 is exact. In the range beta<<1, 1<<r<<d and u=beta r large, it gives

  D/T approximately (1+u) exp(-u),
  R_path(D) approximately u^2/(4 beta ln 2),

where T=sum_i lambda_i. Consequently,

  R_path(D)
    approximately [n/(8t ln 2)] log^2(T/D),

up to log-log corrections, dimension saturation and any retained radial mode.

When t is comparable to or larger than n, use the exact geometric formula; the continuum approximation can otherwise incorrectly predict fewer than one relevant mode.

This is not a proved random-network estimate. In particular:

- The past covariance need not be isotropic in the future singular frame.
- Sorted past and future Lyapunov exponents cannot simply be added.
- A Jacobian describes infinitesimal changes, whereas the cloud has finite angular size.
- Typical singular-value decay does not control annealed squared error.

PROVEN: an exact obstruction to the last extrapolation is

  E_future J_l(h)^T J_l(h) = I

for fixed nonzero h; see Section 5. Typical contraction and annealed energy preservation coexist.

HEURISTIC: chart count from cloud size and frame coherence.

K8 suggests a cloud angular radius of order 1/l. K7 suggests frame coherence on angular scale 1/t. If the cloud were a regular k-dimensional patch, covering it by such charts would require approximately

  K_chart approximately (1+t/l)^k,
  log_2 K_chart approximately k log_2(1+t/l).

To enforce an output error delta with local sensitivity s and state radius R_l, a more conservative resolution is

  min{c/t, delta/(R_l s)},

giving the heuristic bit count

  k log_2[1+(1/l) max{t/c, R_l s/delta}].

The regular-patch assumption, the chart error, and the cost of integrating each chart are all unproved. Frame coherence alone proves none of them.

PROVEN: gate counts give entropy upper bounds, not hardness lower bounds.

If a binary gate-difference mask has expected Hamming weight qn, then

  H(mask) <= n h_2(q).

This follows from entropy subadditivity and concavity of binary entropy.

Substituting K8’s measured q approximately 3/l suggests O((n/l)log l) bits for one such mask. Substituting K10’s O(sqrt(n)) flips suggests O(sqrt(n)log n) bits. Neither substitution implies independence, predictive relevance or integration hardness.

PROVEN/GIVEN: what is known about N_law.

K1 and K2 provide fixed-dimension, high-precision restrictions and description-length bounds in their stated models. They do not determine N_law when n,L and precision scale together. In particular, K1’s exponentially rare ray event cannot by itself establish a polynomial-budget annealed lower bound at L=alpha n.

I do not obtain a justified formula for N_law(n,L,l,eps) in that regime.

3.6. Noise scale and covariance

PROVEN. If the initial condition scales with sigma, then pathwise

  h_l^{sigma}(sigma h_0,xi) = sigma h_l^1(h_0,xi).

The same scaling holds for the stationary law when it exists. Consequently, normalized predictive distortions and their information rates are invariant under sigma.

For a fixed initial law N(0,I), changing sigma also changes the relative input scale:

  h_l^{sigma}(X,xi) = sigma h_l^1(X/sigma,xi).

Therefore finite-depth quantities need not be sigma-independent.

PROVEN UNDER externally fixed gates. If A_j=D_j W_j are fixed independently of the Gaussian input and noises, the resulting linear Gaussian system has covariance

  C_l
    = A_{l:1} A_{l:1}^T
      + sigma^2 sum_{j=1}^l A_{l:j+1} A_{l:j+1}^T,

with empty products equal to I. The future predictive spectrum is the spectrum of

  A_{L:l+1} C_l A_{L:l+1}^T.

Water filling then gives the exact trajectory information rate.

Conditioning an actual ReLU network on its gate pattern does not justify this Gaussian formula: the conditioning truncates the Gaussian variables.

Finally, the stationary annealed Model S law has infinite second moment, as proved below. Stationary covariance-based N estimates therefore require a quenched, truncated or other explicitly specified normalization.


4. Target 4: the hash argument

PROVEN true statement.

If the remaining problem is an arbitrary unknown table on K=2^N equally likely relevant states, and the algorithm can learn it only by value queries, then normalized mean estimation requires

  Theta(min(2^N,eps^{-2}))

queries. Section 2.6 proves this, including adaptive randomized algorithms.

Thus “enumerate all relevant states or sample them” is a correct optimality statement in a precise oracle model.

UNPROVEN transfer.

A small effective dimension followed by many changing random gates does not establish that readable network weights behave like this oracle. It says nothing by itself about whether moments, conditional integrals, telescoping controls or algebraic identities can be computed cheaply.

PROVEN false statement.

“Dependence on many interacting bits, with hash-like randomness, implies that averaging requires sampling.”

Two counterexamples:

a. Known formula.
Parity depends on every input bit and is maximally nonadditive, but its mean under uniform independent bits is known exactly.

b. A genuinely random table.
Let y_1,...,y_K be independent Rademacher values. The estimator zero, making no queries, satisfies

  E mu^2 = 1/K,
  E V = 1-1/K.

Its annealed normalized MSE is 1/(K-1). Increasing the number of independent table entries makes the quenched mean easier to predict from the ensemble.

The lower bound in Section 2.6 deliberately includes uncertainty about the table’s common bias. Independent random signs with known bias do not provide that hardness.

PROVEN network counterexample.

If the cut state lies on a fixed ray,

  H_l = S v,  S>=0,

positive homogeneity gives

  mu = E[S] g_l(v).

Every subsequent gate is independent of S. The future can be evaluated on one representative ray.

For example, a prefix h_1(x)=ReLU(x_1)e_1 has E[S]=1/sqrt(2 pi), and arbitrary-depth suffix weights can be integrated exactly with one suffix evaluation.

This disproves a universal “deep collapse implies hashing implies sampling optimality” statement. It does not refute the average-case conjecture for iid He networks.

K5 separately disproves optimality of ordinary full-trajectory MC in its regime. Optimality of the best multilevel sampler remains the substantive open claim.


5. Exact structure: lemmas and proofs

5.1. Radius integration

PROVEN. Write X=RU, with U uniform on the unit sphere and R independent, distributed as chi_n. Let

  m_n = E R = sqrt(2) Gamma((n+1)/2)/Gamma(n/2),
  A(U)=h_L(U).

Then

  mu = m_n E A,

and

  V = (n-m_n^2) E||A||^2
      + m_n^2 tr Var(A).

Proof. Positive homogeneity gives h_L(X)=R A(U). Use E R^2=n, independence, and subtract ||m_n E A||^2 from the second moment. QED.

The radius-exact estimator averages m_n A(U); its variance is exactly the second term.

5.2. A future-kernel characterization of law information

PROVEN. For a random noiseless suffix, define

  k(h,h') = E_B g_B(h)·g_B(h').

Then, for two cut laws P,Q with finite second moments,

  ||T(P)-T(Q)||_{L^2(B)}^2
    = double-integral k(h,h') d(P-Q)(h) d(P-Q)(h').

Proof. Expand the squared norm of the difference of the two means and exchange expectations and integrals. Finite second moments justify the exchange by Cauchy-Schwarz. QED.

By rotational invariance and homogeneity, K1 gives

  k(h,h') = ||h|| ||h'|| kappa_{n,t}(cos angle(h,h')).

Moreover, k(h,h)=||h||^2. Hence the forward-blind trajectory metric is

  E_B ||g_B(h)-g_B(h')||^2
    = (||h||-||h'||)^2
      + 2||h||||h'||[1-kappa_{n,t}(cos angle(h,h'))].

This is an exact past/future geometry. For mean estimation, however, its kernel acts on differences of laws, not on an individual cloud’s covering number.

5.3. Annealed tangent-energy preservation

PROVEN. For a fixed nonzero h and a finite iid He-ReLU suffix,

  E_B J_B(h)^T J_B(h)=I.

Proof for one layer. A row w~N(0,(2/n)I) contributes

  E[1_{w·h>0} ww^T] = (1/n)I.

Indeed, the integrand ww^T is unchanged under w->-w, which exchanges the two half-spaces. Summing n rows gives I.

For multiple layers, condition on the current state and tangent vector and repeat. If the trajectory becomes identically zero through a strictly negative preactivation layer, its derivative also becomes zero; this does not invalidate the induction. Boundary events have probability zero for a nonzero current state. QED.

Thus a typical low-rank picture cannot be substituted into an annealed quadratic criterion without controlling the exceptional expansion events.

5.4. A precise future-blind subspace separation

PROVEN. Fix a nonzero cut state h and let u=h/||h||. Let F be the top-k right singular subspace of the future Jacobian restricted to u-perp. Resolve ties with an independent rotation-equivariant rule.

For every d-dimensional prefix-measurable subspace S contained in u-perp,

  E_B tr(P_S P_F) = kd/(n-1).

Proof. The suffix distribution is invariant under every input rotation fixing h. Therefore the expected projector onto F commutes with every rotation of u-perp. It must equal a scalar multiple of the identity on that space. Its trace is k, so

  E_B P_F = [k/(n-1)] P_{u-perp}.

Taking its inner product with P_S proves the claim. QED.

Consequently, capturing an expected fraction 1-eta of this frame requires

  d >= (1-eta)(n-1)

without future information. A future-aware choice S=F needs only k dimensions.

The dimension separation is order n/k. This is an exact representation theorem. It is not a mean-estimation lower bound.

5.5. Noise stationarity versus moments

PROVEN. In Model S with fresh iid weights and sigma>0,

  E||H_{l+1}||^2 = E||H_l||^2 + n sigma^2.

Therefore, from H_0~N(0,I),

  E||H_l||^2 = n(1+l sigma^2).

Proof. Conditional on h,

  E_W ||ReLU(Wh)||^2=||h||^2.

The added Gaussian noise has zero cross term and second moment n sigma^2. QED.

PROVEN. The annealed Markov chain nevertheless has a unique stationary distribution, with finite first moment and infinite second moment.

Proof of existence and uniqueness. For every h!=0, all n preactivations are negative with probability p=2^{-n}. On that event, the next state is exactly sigma xi. For h=0 this occurs with probability one. Thus the transition kernel satisfies the uniform minorization

  K(h,·) >= p N(0,sigma^2 I).

Writing K=p nu+(1-p)R gives an invariant distribution

  pi = p sum_{j>=0}(1-p)^j nu R^j,

and total-variation contraction by at most (1-p)^t after t steps. Hence the invariant distribution is unique.

For the first moment, let

  S = (2/n) sum_{i=1}^n Z_i^2 1_{Z_i>0}.

Conditional on h, the norm of ReLU(Wh) has law ||h|| sqrt(S). Since E S=1 and S is nonconstant,

  q=E sqrt(S)<1.

Therefore

  E||H_{l+1}|| <= q E||H_l|| + sigma E||xi||.

Starting at zero gives a uniform first-moment bound; convergence to stationarity and truncation give a finite stationary first moment.

If the stationary second moment were finite, the preceding second-moment identity would imply

  E_pi||H||^2 = E_pi||H||^2+n sigma^2,

a contradiction. QED.

Thus K10’s stationary thin-cloud description can describe typical mass, but cannot mean a stationary annealed law with finite covariance.

5.6. Exact first-layer mean

PROVEN. For any deterministic W,

  E ReLU(WX)_i = ||W_{i,:}||/sqrt(2 pi).

Proof. W_{i,:}X is a centered Gaussian of variance ||W_{i,:}||^2. Its positive-part mean is its standard deviation divided by sqrt(2 pi). QED.

Large input dimension and many gate decisions therefore coexist with an elementary exact mean.


6. Conjecture ledger

Finite experiments can refute specified finite-n inequalities or produce counterexample algorithms. They cannot, by themselves, logically refute an asymptotic complexity conjecture with unspecified constants.

6.1. SINGLE BOTTLENECK: computational sufficiency of the information parameter

CONJECTURE C_comp, a restricted form of C0*.

Fix alpha>0, gamma>0 and a constant pass budget. At L=alpha n and eps=n^{-gamma}, every uniform polynomial-memory sweep estimator attaining the stated annealed error has expected work at least

  n^{-o(1)} C_ML^*(n,L,eps),

where C_ML^* includes preprocessing and denotes the optimal cost within the specified shared-trajectory multilevel family.

Conditional consequence. This gives the requested “no polynomial improvement over the best multilevel sampler” conclusion in the sweep model.

What is missing. A reduction connecting readable weights to a hard integration problem. Section 2.6 would apply if such a reduction made the residual accessible only through sufficiently expensive value queries. No such reduction has been proved here.

Known open problem? C0* is explicitly open in the statement. Its precise status in the wider literature is unsure. General streaming or rate-distortion results do not establish it.

Evidence for: K6’s failed deductive approaches, changing future frames, and nontrivial amplitude variation after directional collapse.

Evidence against treating it as obvious: exact moment identities, cheap ray integration, possible computable amplitude closures, and the substantial improvement already obtained by multilevel controls.

Cheapest useful experiment: widths 16,32,64,128 at fixed L/n, with a precision sweep, comparing a tuned multilevel baseline against a low-rank conditional-mean/control-variate hybrid. Include setup, reference computation, pilot fitting and failed refinements. A growing advantage suggests a counterexample algorithm worth analyzing.

6.2. Extension of the multilevel residual bound

CONJECTURE H_ML.

The residual and layer-cost bounds used in Section 3.3 hold with constants independent of n,L,r over the additional depth regime being claimed.

Conditional proof. The dyadic variance bound, geometric-series sum and allocation theorem give the displayed cost immediately.

Known open problem? K5 supplies the stated established case. Uniform extension outside it is unsure.

Evidence for: angular merging and the supplied multilevel results.

Evidence against: nonuniform finite-width effects, reference-path fluctuations, and exceptional amplification at very large depth.

Cheapest test: measure

  E||Y-G_r||^2 / [V_ang(1/r+n/L^2)]

on dyadic r across L/sqrt(n) and L/n, including confidence intervals and tail contributions. Systematic growth challenges uniformity.

6.3. Turning the Lyapunov picture into a predictive quantizer

CONJECTURE H_local, only where the local estimate is invoked.

For the selected cut and precision, a computable affine or piecewise-affine predictor a(H) satisfies

  E||g_l(H)-a(H)||^2 <= eta^2 V,

and its predictive covariance spectrum is within fixed multiplicative factors of the proposed spectrum. These conditions must hold in the same averaged or per-net sense as the error criterion.

Conditional proof. If a is quantized with distortion D, then

  E||g_l(H)-a_hat(H)||^2 <= 2 eta^2 V+2D.

Water filling or the finite-grid construction then supplies the representation bound.

Known open problem? The required finite-width, gated-network statement is unsure. Oseledets-type theorems do not provide it.

Evidence for: measured Lyapunov spectra and late directional collapse.

Evidence against: frame decorrelation on scale 1/(L-l), the cloud’s finite angular radius, and exact annealed tangent-energy preservation.

Cheapest test: at widths 32 and 64, compare actual future outputs with affine predictors and spectral quantizers at several cuts. Measure prediction residual and discarded sensitivity directly; do not infer either from a Jacobian spectrum alone.

6.4. Computing the integral of the representation

CONJECTURE H_access.

For a proposed K-cell representation, its probabilities and integrated baseline can be computed with total baseline error at most delta/4, in preprocessing cost B small enough to satisfy the desired comparison with C_ML^*.

Conditional proof. Section 3.2 gives the deterministic approximation or control-variate estimator, with explicitly budgeted baseline bias and residual variance.

Known open problem? For a particular representation this is a concrete algorithm-design question; its general status is unsure. No general efficient solution follows from small K, small rank or low mutual information.

Evidence for: exact Gaussian moments, simple half-space truncations and low-dimensional special cases.

Evidence against: curved pullbacks, complicated input cones, rare cells and expensive conditional expectations.

Cheapest test: implement just the probability/baseline calculation for the candidate representation and time it at the final requested precision. This can reject the proposed advantage before a full estimator is built.

6.5. Tail control when using typical-network estimates

CONJECTURE H_tail.

If G is the event on which a proposed approximation theorem holds, its error outside G satisfies

  E[error(W)^2 1_{G^c}] <= eta eps^2 E V(W)

for the allocated error fraction eta.

Conditional proof. Add this contribution to the proved good-event error.

Known open problem? Model-specific; unsure.

Evidence for: some finite-depth concentration results.

Evidence against: the exact mean-square/typical-Jacobian discrepancy, rare events in K1, and the infinite stationary second moment in Model S.

Cheapest test: report cumulative contributions to squared error from increasingly extreme network and trajectory quantiles. Finding a substantial tail contribution can disprove a claimed finite-n bound. Failure to observe one is not a tail proof.


7. Relevant literature

- Kushilevitz and Nisan, “Communication Complexity”: cut reductions, INDEX lower bounds and the distinction between one-way and interactive protocols.
- Woodruff, “Sketching as a Tool for Numerical Linear Algebra”: precise restrictions under which linear-sketch lower bounds apply.
- Cover and Thomas, “Elements of Information Theory”: Gaussian rate-distortion, water filling and mutual-information lower bounds.
- Graf and Luschgy, “Foundations of Quantization for Probability Distributions”: finite-codebook quantization and its dependence on distribution geometry.
- Traub, Wasilkowski and Woźniakowski, “Information-Based Complexity”: why integration complexity depends on the permitted information operations.
- Novak, “Deterministic and Stochastic Error Bounds in Numerical Analysis”: worst-case and randomized integration complexity under function-class assumptions.
- Giles, “Multilevel Monte Carlo Path Simulation”: telescoping estimators and optimal variance-cost sample allocation.
- Owen’s scrambled-net work: rigorous gains over MC under regularity assumptions; interaction alone does not imply MC optimality.
- Oseledets’ multiplicative ergodic theorem: almost-sure Lyapunov exponents, without the required annealed moment or integration-complexity conclusions.
- Furstenberg and Kesten, “Products of Random Matrices”: foundational asymptotics for random products, subject to hypotheses that must be checked for gated products.
- Cho and Saul, “Kernel Methods for Deep Learning”: the arc-cosine kernel and angular geometry of ReLU features.
- Poole et al., “Exponential Expressivity in Deep Neural Networks Through Transient Chaos,” and Schoenholz et al., “Deep Information Propagation”: mean-field correlation and sensitivity recursions.
- Hanin and Nica, “Products of Many Large Random Matrices and Gradients in Deep Neural Networks”: depth/width effects and fluctuations of random matrix products relevant to finite-width gradients.
- Bach, “On the Equivalence between Kernel Quadrature Rules and Random Feature Expansions”: spectral characterizations and constructive quadrature under kernel/RKHS assumptions; it supplies no unrestricted lower bound for readable networks.
