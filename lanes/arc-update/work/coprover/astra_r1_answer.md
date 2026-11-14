# gpt-6-astra round 1 answer (extracted from astra_r1.raw lines 2513-3325; model line: gpt-6-astra; r1 05:00:57Z exit 0)

**PROVEN:** A nontrivial lower bound is available for a specified Gaussian replacement, and conditionally for repeated Gaussian closure. It does not establish a lower bound for all ARC estimators or future-aware deductive methods.

I use
\[
\mathcal R(\widehat\mu)=
\frac{\mathbb E_W\|\widehat\mu-\mu\|^2}{\mathbb E_W V(W)},
\qquad F=2n^2L,\qquad N=C/F.
\]
Thus plain MC has annealed risk \(1/N\). Definitions below are definitions; mathematical assertions carry proof-status labels.

I read the statement, the estimator fact sheet, and relevant portions of the cited bits-bounds and unrestricted-estimators reports. I did not inspect this lane’s other files, modify files, run network experiments, or independently audit the cited implementations. Numerical evaluations below are scalar calculations, not new network measurements.

## 1. Computational model

**PROVEN UNDER the estimator descriptions in the statement and fact sheet:** The following computational model contains all the named families.

Use a uniform arithmetic/bit RAM with:

- Explicit access to the weights. Loading a dense row costs \(n\) scalar reads; arithmetic, storage, comparisons, and numerical special-function evaluation are charged.
- Arbitrary finite records: tensors, factorizations, Gaussian components, polyhedral cells, Boolean codes, circuits, particles, and certificates.
- Arbitrarily many passes, with all work charged.
- Either forward-only access, where the state after layer \(\ell\) depends only on \(W_{\leq\ell}\), or unrestricted access to all weights.
- A specified precision convention. The usual FLOP comparison is its ideal arithmetic version; a bit-complexity version also charges precision.

It contains basic, augmented, and factorized cumulant propagation; exact Gaussian closure; Gaussian mixtures and gate splits; deduction-projection; quantized-state propagation; cell merging and enumeration; symbolic branch-and-bound; and their future-aware versions. It also contains MC, RQMC, and multilevel sampling. The inclusion follows by storing each method’s actual state and executing its stated updates.

It excludes free integration or optimization oracles, free advice depending on the realized weights, free exponentially large tables, and extracting arbitrarily many bits from a real number at unit cost. Row-granular access excludes cheaper scalar-probing algorithms unless their access is charged separately.

**PROVEN:** This broad model admits a small but genuine input-access lower bound, proved in Question 2. It does **not** presently give the desired lower bound at budgets of hundreds or thousands of forward passes.

The substantive lower bounds below require additional restrictions:

1. A specified law-propagation closure.
2. An explicitly restricted information interface, such as moment summaries or point queries.
3. A specified representation and contraction procedure, such as a bounded-width graphical model.

Those restrictions are part of the theorem, not consequences of being “deductive.”

**PROVEN:** A probability-law model alone does not automatically contain ARC’s general cumulant algorithms.

A finite collection of cumulants, followed by a truncated diagram update, specifies an algorithm on tensors. It does not by itself specify a probability measure whose exact pushforward reproduces that update. Therefore, a theorem about propagating Gaussian mixtures or signed measures transfers to cumulant propagation only after supplying and checking such a reconstruction.

For exact Gaussian closure there is an explicit reconstruction. For basic \(K=2\), the first-layer reconstruction used below can also be written explicitly. I have not supplied a reconstruction for every augmented or higher-order variant.

**HEURISTIC:** This is the central limitation of a broad computational-model answer: making the model sufficiently expressive to include future-aware symbolic methods also makes its lower bounds computational-complexity questions. Restricting it until an information or representation lower bound becomes easy can remove precisely the methods the question asks us to cover.

## 2. Lower bounds, cancellation, and cumulant exponents

### 2.1 An unconditional normalization bound

The following preliminary bound makes the deep-regime normalization explicit.

**PROVEN:** For every \(n,L\),
\[
n-m_n^2\ \leq\ \mathbb E_W V(W),
\qquad
m_n=\mathbb E\|X\|,
\]
and, writing
\[
c_0=\frac{2\sqrt2}{3\pi},\qquad
b_n=\left(\frac{m_n^2}{n}\right)^{-1/2},
\]
we have
\[
\mathbb E_W V(W)
\leq
n-m_n^2+
2\sum_{j=0}^{L-1}(b_n+c_0j/2)^{-2}
+n(b_n+c_0L/2)^{-2}.                                    \tag{1}
\]
Consequently, for every fixed \(\alpha>0\),
\[
\frac12\leq
\liminf_{n\to\infty}\mathbb E V
\leq
\limsup_{n\to\infty}\mathbb E V
\leq C_*:=\frac52+3\sqrt2\pi<15.829
\]
when \(L=\alpha n+O(1)\).

*Proof.* Positive homogeneity and \(X=RU\), with \(R,U\) independent, give
\[
V(W)=m_n^2\operatorname{tr}\operatorname{Var}_U a(U)
 +(n-m_n^2)\mathbb E_U\|a(U)\|^2.
\]
Critical He initialization preserves expected squared norm, so averaging gives the lower bound.

For the upper bound, propagate two independent Gaussian inputs through the same weights. At layer \(j\), let their norms be \(r_j,s_j\), their cosine be \(c_j\), and set
\[
D_j=\mathbb E[r_js_j(1-c_j)].
\]
Terms with zero norm contribute zero.

For one fresh layer, the expected inner product is
\[
rs\,\kappa(c),\qquad
\kappa(c)=\frac{\sqrt{1-c^2}+(\pi-\arccos c)c}{\pi}.
\]
The expected product of norms is \(rs\,a(c)\), where \(a(c)\leq1\) by Cauchy–Schwarz. Moreover,
\[
\kappa(c)-c
=\frac1\pi\int_c^1\arccos u\,du
\geq c_0(1-c)^{3/2}.
\]
Weighted Jensen and \(\mathbb E r_js_j\leq n\) therefore give
\[
D_{j+1}\leq D_j-\frac{c_0}{\sqrt n}D_j^{3/2}.
\]
Since \(D_0=m_n^2\), applying
\((1-z)^{-1/2}\geq1+z/2\) yields
\[
D_j/n\leq(b_n+c_0j/2)^{-2}.                               \tag{2}
\]

To control radial separation, put
\[
g(Z)=\sqrt{2/n}\,\|Z_+\|,\qquad Z\sim N(0,I_n).
\]
Then \(\mathbb Eg^2=1\) and
\[
\mathbb E\|\nabla g\|^2=\frac2n(1-2^{-n})\leq\frac2n.
\]
For correlated Gaussian vectors with coordinate correlation \(c\), a Hermite expansion and \(1-c^k\leq k(1-c)\) imply
\[
1-a(c)=\tfrac12\mathbb E(g(Z)-g(Z'))^2
\leq\frac{2}{n}(1-c).
\]
Thus the expected squared radial separation increases by at most \(4D_j/n\) per layer. Finally,
\[
\mathbb EV=\tfrac12\mathbb E(r_L-s_L)^2+D_L.
\]
Combining this identity with (2) proves (1). The asymptotic bound follows from
\[
n-m_n^2\to\tfrac12,\qquad
\sum_{j\geq0}(1+c_0j/2)^{-2}\leq1+2/c_0.
\]
∎

**PROVEN, with numerical constants evaluated approximately:** At \(256\times32\), (1) gives
\[
0.4995107<\mathbb EV<20.13891.                            \tag{3}
\]
These are ensemble bounds, not bounds on every individual network.

### 2.2 A lower bound covering the broad model, but only at very small cost

**PROVEN UNDER row-granular weight access:** Even granting the entire prefix for free, an algorithm that reads at most \(q\) rows of the last weight matrix satisfies
\[
\mathbb E\|\widehat\mu-\mu\|^2
\geq
(n-q)\frac{m_n^2a_n^{\,2(L-2)}}{2\pi n},
\qquad L\geq2,                                           \tag{4}
\]
where
\[
a_n=\mathbb E\sqrt{\frac2n\sum_{i=1}^n(Z_i)_+^2}.
\]

*Proof.* Conditional on the prefix, let \(H=h_{L-1}(X)\) and \(m=\mathbb EH\). For an unread row \(w\),
\[
f(w)=\mathbb E_H(w\cdot H)_+,
\qquad
f(w)-f(-w)=w\cdot m.
\]
Its odd part is \(w\cdot m/2\). Odd and even functions are orthogonal under the centered Gaussian row distribution, hence
\[
\operatorname{Var}_w f(w)\geq
\mathbb E(w\cdot m/2)^2=\frac{\|m\|^2}{2n}.
\]
Adaptive reading of other rows does not reveal an unread independent row. Sum its conditional variance over unread rows.

For a prefix of depth \(L-1\), each coordinate of its weight-averaged mean is
\[
\frac{m_na_n^{L-2}}{\sqrt{\pi n}}.
\]
Jensen therefore gives
\(\mathbb E\|m\|^2\geq m_n^2a_n^{2(L-2)}/\pi\), proving (4). ∎

**PROVEN, numerical evaluation:** At \(256\times32\), the bound is approximately
\[
\mathbb E\|\widehat\mu-\mu\|^2\geq0.137153(256-q).
\]
At cost \(C\), \(q\leq\lfloor C/n\rfloor\).

**PROVEN:** This bound becomes vacuous after reading the last matrix. It is not evidence of difficulty at ARC’s actual budgets.

### 2.3 A radius obstruction for Gaussian replacement

Define
\[
P_1=\mathcal L(\operatorname{relu}(W_1X)\mid W_1),
\]
and let \(Q_1\) be its exactly moment-matched Gaussian. Write
\[
\rho_1(W_1)=\mathbb E_{Q_1}\|H\|-\mathbb E_{P_1}\|H\|.
\]

**PROVEN:** The first Gaussian replacement has
\[
\mathbb E_{W_1}\rho_1
=\frac{9}{16\sqrt n}+o(n^{-1/2}).                         \tag{5}
\]

Here is a derivation, including the coefficient.

Let \(w_i=r_i u_i\) be the first-layer rows, and \(c_{ij}=u_i\cdot u_j\). The Gaussian replacement has
\[
m_i=\frac{r_i}{\sqrt{2\pi}},\quad
C_{ii}=r_i^2\frac{\pi-1}{2\pi},\quad
C_{ij}=r_ir_j f(c_{ij}),
\]
where
\[
f(c)=\frac{\sqrt{1-c^2}+(\pi-\arccos c)c-1}{2\pi}
=\frac c4+\frac{c^2}{4\pi}+O(c^4).
\]
Independent uniform directions satisfy
\(\mathbb Ec_{ij}=0\), \(\mathbb Ec_{ij}^2=1/n\), and
\(\mathbb Ec_{ij}^4=O(n^{-2})\). Independent row lengths satisfy
\(\mathbb Er_i^2=2\), \(\mathbb Er_i^4=4+O(n^{-1})\). Consequently,
\[
\frac1n\mathbb E\operatorname{tr}C^2
=\left(1-\frac1\pi\right)^2+\frac14+o(1),
\]
and
\[
\frac1n\mathbb E m^\top Cm
=\frac1\pi-\frac1{2\pi^2}+o(1).
\]
The expansion of \(f\) can be used on \(|c|\leq1/2\); the complementary event has exponentially small probability and \(f\) is bounded.

For \(G\sim N(m,C)\),
\[
\operatorname{Var}(\|G\|^2\mid W_1)
=2\operatorname{tr}C^2+4m^\top Cm.
\]
Also
\(\mathbb E(\|G\|^2\mid W_1)=\frac12\|W_1\|_F^2\), whose variance is \(2\). Hence
\[
\mathbb E\|G\|^2=n,\qquad
\operatorname{Var}_{W_1,G}(\|G\|^2)=\frac52n+o(n).          \tag{6}
\]

The Taylor remainder is controlled rather than merely formal. For \(s\geq0\),
\[
\left|\sqrt s-\left(1+\frac{s-1}{2}-\frac{(s-1)^2}{8}\right)\right|
\leq\frac38|s-1|^3.                                      \tag{7}
\]
To verify (7), put \(q=\sqrt s\); the remainder is
\((q-1)^3(q+3)/8\), and
\((q+3)/(q+1)^3\leq3\).

Gaussian Poincaré gives \(C\preceq\|W_1\|_{\rm op}^2I\). Gaussian linear/quadratic moment bounds then give
\[
\mathbb E\left|\|G\|^2-n\right|^3=O(n^{3/2}).
\]
Indeed, conditional on \(W_1\), the centered quantity is a Gaussian linear form plus a centered quadratic form; their third absolute moments are bounded by constants times
\((m^\top Cm)^{3/2}\) and \((\operatorname{tr}C^2)^{3/2}\). Gaussian matrix operator norms have bounded fixed moments, while \(\|W_1\|_F^2\) has moments of order \(n^p\). Applying (7) to (6) gives
\[
\mathbb E\|G\|
=\sqrt n-\frac5{16\sqrt n}+o(n^{-1/2}).
\]

For the true first-layer output, averaging over \(W_1\) conditional on \(X\) gives the exact identity
\[
\mathbb E\|H\|=m_na_n.
\]
The squared gain defining \(a_n\) has mean \(1\) and variance \(5/n\). Applying the same Taylor bound,
\[
a_n=1-\frac5{8n}+o(n^{-1}),\qquad
m_n=\sqrt n-\frac1{4\sqrt n}+o(n^{-1/2}).
\]
Thus
\[
\mathbb E\|H\|
=\sqrt n-\frac7{8\sqrt n}+o(n^{-1/2}),
\]
which proves (5). ∎

**PROVEN:** Gaussianizing once after layer 1 and then applying the exact remaining network gives
\[
\liminf_{n\to\infty}
n\,\mathbb E\|\widehat\mu-\mu\|^2
\geq \frac{81}{256\pi}e^{-5\alpha/4}
\]
at \(L=\alpha n+O(1)\). In normalized form,
\[
\liminf_{n\to\infty} n\mathcal R
\geq
c_G(\alpha):=
\frac{81e^{-5\alpha/4}}{256\pi C_*}.                       \tag{8}
\]

*Proof.* For an independent suffix of depth \(t\geq1\),
\[
\mathbb E_{\rm suffix}g_t(h)
=\frac{a_n^{t-1}}{\sqrt{\pi n}}\|h\|\,\mathbf1.
\]
The first suffix layer has coordinate mean
\(\|h\|/\sqrt{\pi n}\), and each preceding norm propagation multiplies expected radius by \(a_n\).

Conditional Jensen therefore gives
\[
\mathbb E_{\rm suffix}\left\|\int g_t\,d(Q_1-P_1)\right\|^2
\geq\frac{a_n^{2(t-1)}}{\pi}\rho_1(W_1)^2.
\]
Average over \(W_1\), apply Jensen once more, use (5), and note
\(a_n^{2(L-2)}\to e^{-5\alpha/4}\). Equation (1) gives the normalization in (8). ∎

**PROVEN, numerical evaluation of asymptotic constants:**
\[
c_G(1/8)\approx0.00544243,\qquad
c_G(1)\approx0.00182299.
\]
These are limiting constants, not finite-\(n\) guarantees.

### 2.4 Repeated closure and cancellation

Let \(Q_\ell\) be an actual reconstructed law, \(T_\ell\) the exact layer pushforward, and
\[
\delta_\ell=Q_\ell-T_\ell Q_{\ell-1}.
\]
Suppose its final readout is \(\int h\,dQ_L\), with all relevant integrals finite.

**PROVEN:** Its error telescopes as
\[
e=\widehat\mu-\mu
=\sum_{\ell=1}^L\int g_\ell\,d\delta_\ell,                 \tag{9}
\]
where \(g_\ell\) is the exact suffix after layer \(\ell\).

*Proof.* The \(\ell\)-th term is
\(\int g_\ell\,dQ_\ell-\int g_{\ell-1}\,dQ_{\ell-1}\);
sum and cancel adjacent terms. ∎

For a forward-only, mean-preserving reconstruction, put
\[
\rho_\ell=\int\|h\|\,d\delta_\ell.
\]

**PROVEN:** The signed radius defects give the exact mean-error identity
\[
\mathbb E_W e
=\frac{\mathbf1}{\sqrt{\pi n}}
\sum_{\ell=1}^{L-1}a_n^{L-\ell-1}\mathbb E\rho_\ell,
\]
and hence
\[
\mathbb E\|e\|^2
\geq\frac1\pi
\left(
\sum_{\ell=1}^{L-1}a_n^{L-\ell-1}\mathbb E\rho_\ell
\right)^2.                                               \tag{10}
\]
This follows by conditioning each term of (9) on its past, using the suffix expectation above, and applying Jensen. The final defect has zero first moment.

Define the hypothesis
\[
(H_R):\quad
\mathbb E_W\!\left[
\mathbb E_{\Gamma(T_WQ)}\|h\|-\mathbb E_{T_WQ}\|h\|
\right]\geq0
\]
for every Gaussian input law \(Q\), where \(\Gamma\) is exact Gaussian moment matching.

**PROVEN UNDER \(H_R\):** Repeated exact Gaussian closure satisfies (8).

*Proof.* Conditional on its past, \(Q_{\ell-1}\) is Gaussian and \(W_\ell\) is fresh. Thus \(H_R\) makes every \(\mathbb E\rho_\ell\) nonnegative. Retain only the first term of (10) and apply the preceding proof. ∎

**CONJECTURE:** \(H_R\) holds for every Gaussian input law. I have not proved it. A pointwise assertion for every fixed \(W\) is stronger and is not needed here.

**PROVEN:** Independence of future weights does not exclude cancellation between general closure defects.

For example, take \(Q_1=P_1+\eta\) for a nonzero admissible signed perturbation, then set \(Q_2=P_2\). This gives
\[
\delta_1=\eta,\qquad \delta_2=-T_2\eta,
\]
and their suffix-tested contributions cancel exactly. Both choices are forward-only; the second may be computationally expensive. Thus forward-only access alone does not supply a noncancellation theorem.

Two valid alternatives are:

- **PROVEN UNDER a Gram bound:** If \(e_\ell=\int g_\ell\,d\delta_\ell\) and the matrix
  \[
  G_{\ell j}=
  \frac{\mathbb E\langle e_\ell,e_j\rangle}
       {\sqrt{\mathbb E\|e_\ell\|^2\,\mathbb E\|e_j\|^2}}
  \]
  has \(\lambda_{\min}(G)\geq\eta>0\), then
  \[
  \mathbb E\Big\|\sum_\ell e_\ell\Big\|^2
  \geq\eta\sum_\ell\mathbb E\|e_\ell\|^2.
  \]
  This is the quadratic-form bound with coordinates
  \(\sqrt{\mathbb E\|e_\ell\|^2}\).

- **PROVEN:** Expanding the total error in orthonormal Hermite polynomials of all weights gives
  \[
  \mathbb E\|e\|^2=\sum_\nu\|\widehat e_\nu\|^2.
  \]
  A verified nonzero coefficient yields a lower bound. Contributions from different layers to the *same* coefficient must first be summed; they can cancel.

The second approach is a concrete route to an actual cumulant-algorithm lower bound.

### 2.5 What this establishes about order \(K\)

**PROVEN:** A matching \(c(L/n)^K\) lower bound cannot hold for every fixed \(L\): with one ReLU layer, an estimator retaining the exact Gaussian mean and covariance computes the mean exactly.

**PROVEN:** There is a nonzero fixed-depth lower bound for basic \(K=2\) at \(L=2\), using the “simple” covariance rule specified in the fact sheet:
\[
\liminf_{n\to\infty}n^2\mathcal R_{\mathrm{basic}\ K=2,L=2}
\geq0.1099902.                                           \tag{11}
\]

*Proof.* At the first layer this rule has the exact mean and diagonal covariance, but off-diagonal covariance
\[
C^{\rm s}_{ij}=r_ir_jc_{ij}/4.
\]
This is a valid covariance matrix:
\[
C^{\rm s}
=\tfrac14W_1W_1^\top+
\left(\frac{\pi-1}{2\pi}-\frac14\right)
\operatorname{diag}(r_i^2)\succeq0.
\]
In the calculation proving (5), the leading \(\operatorname{tr}C^2/n\) is unchanged, while the \(1/(2\pi^2)\) off-diagonal contribution to \(m^\top Cm/n\) disappears. Its Gaussian radius defect is therefore
\[
\mathbb E\rho_1^{\rm s}
=\frac{c_{\rm s}}{\sqrt n}+o(n^{-1/2}),
\qquad
c_{\rm s}=\frac9{16}+\frac1{4\pi^2}\approx0.5878303.
\]
At \(L=2\), the final estimated mean is exactly the Gaussian expectation under this reconstructed law. The one-suffix-layer argument gives absolute squared error at least
\(c_{\rm s}^2/(\pi n)+o(n^{-1})\). Since \(\mathbb EV\leq n\),
\[
\liminf n^2\mathcal R\geq c_{\rm s}^2/\pi\approx0.1099902.
\]
∎

**PROVEN:** Equation (11) covers the specified basic rule. It does not establish the same coefficient for augmented \(K=2\), other depths, or higher orders.

**CONJECTURE:** For specified nondegenerate fixed depths and specified ARC variants, the first surviving weight-chaos coefficient often gives normalized error \(\Theta(n^{-K})\). I have not checked that coefficient for \(K\geq3\), and therefore do not claim tightness.

**PROVEN:** Fixed-depth asymptotics do not determine the exponent at \(L=\alpha n\). Their constants and remainders can depend on \(L\), and substituting \(L=\alpha n\) into a fixed-\(L\) expansion is unjustified.

There is also a normalization issue: if ARC’s conjecture is expressed as **per-coordinate** MSE, then
\[
\mathcal R=\frac{n\,\mathrm{MSE}_{\rm coordinate}}{\mathbb EV}.
\]
By (1), \(\mathbb EV=\Theta(1)\) at \(L=\alpha n\), so this conversion contributes a factor of order \(n\). The convention must be fixed before interpreting a depth-width exponent.

**PROVEN UNDER \(H_R\):** For exact Gaussian closure, an asymptotic normalized power \(\mathcal R=n^{-p+o(1)}\), if it exists, has \(p\leq1\). This is only an upper bound on the possible decay exponent; it does not prove \(p=1\).

**HEURISTIC:** Neither the product-law exponent \(2\lfloor K/2\rfloor-1\) nor the reported finite-width slopes identify the exponent of the actual general hierarchy.

### 2.6 Comparison with samplers and finite budgets

**PROVEN UNDER the stated cost and multilevel-risk hypotheses:** Suppose a method costs
\(N_K=\Theta(n^{K-1})\) forward passes at \(L=\alpha n\), as both stated fixed-\(K\) cost formulas do, and has
\(\mathcal R_K\geq b_Kn^{-p_K}\). Then
\[
\operatorname{gain}_{\rm MC}
=O(n^{p_K-K+1}),
\]
and, using the cited multilevel upper bound
\(\mathcal R_{\rm ML}=O(\log^2 n/(nN_K))\),
\[
\operatorname{gain}_{\rm best\ sampler}
\leq O(\log^2n\,n^{p_K-K}).                               \tag{12}
\]
Divide the comparator’s upper bound by the method’s lower bound. A better RQMC comparator can only reduce this gain.

Thus a polynomial advantage over that multilevel sampler requires \(p_K>K\) within this fixed-\(K\), power-law scenario.

**PROVEN UNDER \(H_R\), the cited multilevel theorem, and cost \(N=\beta n(1+o(1))\):** Exact Gaussian closure has bounded gain over MC and gain \(O(\log^2n/n)\) over the best sampler. For \(\beta=2\), (8) gives limiting MC-gain upper bounds approximately \(91.9\) at \(\alpha=1/8\) and \(274.3\) at \(\alpha=1\). These constants are loose.

**PROVEN:** At \(256\times32\), the one-replacement finite-width bound is
\[
\mathcal R_{\rm one\ replacement}
\geq0.0136473\,(\mathbb E\rho_1)^2.                       \tag{13}
\]
Indeed, \(a_{256}\approx0.9975558464\), so the absolute-error multiplier is
\(a_{256}^{60}/\pi\approx0.2748421\); divide by (3). Equation (13) still requires the actual finite-width radius defect.

**HEURISTIC, using the supplied measurements without rerunning them:** The reported costs imply:

| Method | Equivalent passes | Reported nMSE | Gain over plain MC | Gain if comparator achieves \(0.40/N\) |
|---|---:|---:|---:|---:|
| \(K=2\) augmented | \(452.995\) | \(1.4\times10^{-3}\) | \(1.577\) | \(0.631\) |
| Factorized \(K=3\) | \(49{,}114.2\) | \(2.2\times10^{-4}\) | \(0.0925\) | \(0.0370\) |

The measurements used noise \(\sigma=0.001\); they are not a proof for the exact noiseless setting. The final column also assumes the reported design efficiency persists at those budgets.

**PROVEN, arithmetic:** At these costs, beating a \(0.40/N\) comparator requires errors below \(8.83\times10^{-4}\) and \(8.14\times10^{-6}\), respectively.

## 3. Forward-only versus future-aware, and “factorises”

Let \(A\) denote the prefix weights, \(B\) the independent suffix, and
\[
T(A)(B)=\int g_B(h)\,dP_A(h).
\]

**PROVEN:** The exact information object relevant to a forward-only cut is the function \(T(A)\) in the Hilbert space \(L^2(B;\mathbb R^n)\).

For a forward-only summary \(S=S(A)\), its best unrestricted decoder has risk
\[
\inf_r\mathbb E\|T(A)(B)-r(S,B)\|^2
=
\mathbb E\|T(A)(B)-\mathbb E[T(A)(B)\mid S,B]\|^2.          \tag{14}
\]

*Proof.* Conditional expectation is the orthogonal projection onto functions measurable with respect to \((S,B)\). Expanding the squared error gives the projection error plus the nonnegative squared distance of any other decoder from that projection. ∎

**PROVEN:** Equation (14) does not require the summary to reconstruct trajectories, the entire cloud, or every higher cumulant. It requires retaining the equivalence class of the cloud under the relevant future mean queries.

For two cloud laws, the squared distance between their query functions is precisely the future-averaged kernel discrepancy. Rotational invariance constrains this kernel; it does not force the state to use any particular representation of the cloud.

**PROVEN:** A future-aware method can, information-theoretically, retain only the answer \(\mu(A,B)\), using \(n\) real numbers. This follows by defining its state to equal that answer. The difficulty is computing the state, so this observation supplies no efficient algorithm.

Therefore a theorem that both kinds of method must carry a large joint law cannot hold without a computational or representational restriction.

Here is one precise sufficient meaning of “factorises.”

**PROVEN UNDER a supplied finite factorization and tree decomposition:** Suppose the relevant latent variables have alphabet size \(q\), their joint law and deterministic transitions are products of supplied local factors, and the required output is a sum of supplied local observables. If the resulting factor graph has elimination width \(w\), its mean can be computed in
\[
O(Tq^{w+1})
\]
table operations, where \(T\) bounds the number of factors and elimination steps.

*Proof.* Eliminate variables successively. By the width assumption, every intermediate factor contains at most \(w+1\) variables. Each factor multiplication and summation therefore uses \(O(q^{w+1})\) entries. The partition function and observable-weighted contractions give the mean. ∎

This formulation charges constructing the factors and finding the decomposition. Gaussian cell probabilities are not free supplied numbers.

**PROVEN:** Large high-order dependence alone does not contradict efficient factorization. For example,
\[
P_\theta(z)=2^{-b}\left(1+\theta\prod_{i=1}^bz_i\right),
\qquad z_i\in\{-1,1\},
\]
has every proper marginal uniform, yet
\(\mathbb E\prod_i z_i=\theta\), computable from one parameter.

**PROVEN:** “Both pay unless it factorises” becomes a valid restricted statement if “pay” means the intermediate-table cost of a specified variable-elimination algorithm and “factorises” means bounded elimination width in its allowed representation. It is not a lower bound against arbitrary arithmetic programs, alternative encodings, or analytic identities.

**HEURISTIC:** A more useful research target is a factorization of the **law–future pairing**. Complexity in the law can be harmless if the future ignores it, and complexity in the future can be harmless under a distribution allowing analytic integration.

## 4. “Whether the bits get scrambled when correctly compressed”

### 4.1 Formalization A: does the compressed state admit a cheap update?

Fix an input distribution and fixed weights. Let
\[
Z_\ell=c_\ell(H_\ell),\qquad
Z_{\ell+1}=c_{\ell+1}(T_{\ell+1}H_\ell).
\]

**PROVEN:** An exact deterministic update
\(Z_{\ell+1}=\tau_\ell(Z_\ell)\) exists almost surely iff
\[
H(Z_{\ell+1}\mid Z_\ell)=0.                               \tag{15}
\]
Equivalently, the next code is almost surely constant on each current-code fiber.

*Proof.* A deterministic update makes every conditional distribution a point mass. Conversely, if every conditional distribution is a point mass, choose its supported value as \(\tau_\ell(z)\). ∎

**PROVEN:** The smallest one-step code-prediction error is
\[
e_\ell^*
=1-\mathbb E\max_{z'}P(Z_{\ell+1}=z'\mid Z_\ell).
\]
For \(M\) possible next codes, Fano’s inequality gives
\[
e_\ell^*\geq
\frac{H(Z_{\ell+1}\mid Z_\ell)-1}{\log_2M}.
\]
The first formula follows by choosing the most probable conditional label; Fano follows by conditioning on whether that choice was wrong and bounding the remaining label entropy by \(\log_2(M-1)\).

This turns information loss into a checkable condition. Computational scrambling requires a second quantity: the cost of representing and evaluating \(\tau_\ell\), including construction.

**PROVEN:** Even an exact, cheap transition does not imply cheap propagation of the code’s probability law. Computing
\[
P(Z_{\ell+1}=z')
=\sum_{z:\tau_\ell(z)=z'}P(Z_\ell=z)
\]
can require summing a complicated set of inputs.

**PROVEN:** Conversely, a future-aware “correct compression” can avoid information scrambling trivially:
\[
c_\ell(h)=Q(g_\ell(h))
\]
for a fixed output quantizer \(Q\). Then
\(c_{\ell+1}(T_{\ell+1}h)=c_\ell(h)\), so the transition is the identity. Its encoder may cost an entire suffix evaluation.

Thus the useful hypothesis is joint:

> The codes preserve the required query to the target accuracy; their encoders and transitions are cheap; and their probability laws admit cheap contraction.

**CONJECTURE:** The reported near-linear code transitions satisfy the second condition over substantial late-layer ranges. They do not yet establish the third condition.

### 4.2 Formalization B: does omitted joint information remain essential for integration?

**PROVEN UNDER a moment-summary-only interface:** Let a summary retain all Boolean moments of degree at most \(K<b\). The two laws
\[
P_\pm(z)=2^{-b}(1\pm\theta\chi(z)),\qquad
\chi(z)=\prod_{i=1}^bz_i,\quad0<\theta\leq1,
\]
have identical summaries. For
\(f(z)=(1+\chi(z))/2\), every summary-based estimator has worst-case squared mean error at least \(\theta^2/4\).

*Proof.* Every nonconstant character of degree below \(b\) is orthogonal to both \(1\) and \(\chi\) under the uniform cube law, so the summaries agree. The two target means are \((1\pm\theta)/2\). Any common estimate is at distance at least \(\theta/2\) from one of them. ∎

This is an exact higher-order-information obstruction. It is not an actual-network lower bound: the pair of laws must be realizable in the intended model, and the algorithm must really have only the stated summary.

For a more literal hash interpretation, a nuisance matters.

**PROVEN:** An iid, known-zero-mean random table does not imply a \(1/q\) integration lower bound. For a table with \(M\) independent unit-variance entries, the estimate zero already has mean-squared error \(1/M\) for its table average.

A sampling lower bound requires an unknown mean component.

**PROVEN UNDER an unknown-bias table oracle:** Let \(\theta\sim\mathrm{Uniform}[0,1]\), and conditional on \(\theta\), let \(M\) table entries be iid Bernoulli\((\theta)\). An algorithm may query \(q\) distinct entries adaptively and must estimate the realized table mean. Its optimal Bayes risk is exactly
\[
\frac{(M-q)(M+2)}{6M^2(q+2)}.                            \tag{16}
\]
The expected variance of a uniformly selected entry from the realized table is \((M-1)/(6M)\). Hence its normalized optimal risk is
\[
\frac{(M-q)(M+2)}{M(M-1)(q+2)}
\sim\frac1{q+2}\quad(q\ll M).                             \tag{17}
\]

*Proof.* After \(s\) successes, the posterior is
\(\theta\mid\text{data}\sim\mathrm{Beta}(s+1,q-s+1)\). The unqueried entries remain exchangeable, so adaptivity gives no additional information. Writing \(r=M-q\), the conditional variance of their sum is
\[
r\,\mathbb E[\theta(1-\theta)\mid\text{data}]
+r^2\operatorname{Var}(\theta\mid\text{data}).
\]
Average over the data:
\[
\mathbb E\theta(1-\theta)=1/6,\qquad
\mathbb E\operatorname{Var}(\theta\mid\text{data})
=\frac1{6(q+2)}.
\]
Divide by \(M^2\) to obtain (16). Directly computing
\(\mathbb E[\bar F(1-\bar F)]\) gives the stated variance and (17). ∎

**CONJECTURE:** A suitable residual of a compressed random network behaves like such an unknown-bias oracle after all inexpensive structural deductions.

That is a precise possible hardness conjecture. It is unproved: a white-box weight description can reveal information that the table oracle conceals.

## 5. Strong positive possibilities

### 5.1 Analytically integrate the first radial control

There is a concrete deductive calculation that can replace one part of the multilevel sampler.

Let
\[
H=\operatorname{relu}(W_1X),\quad S=\|H\|^2,\quad
s=\mathbb ES=\tfrac12\|W_1\|_F^2,\quad v=\operatorname{Var}S,
\]
and define
\[
A(W_1)=\sqrt s-\frac{v}{8s^{3/2}}.
\]

**PROVEN:** For \(s>0\),
\[
\left|\mathbb E\|H\|-A(W_1)\right|
\leq\frac{3\,\mathbb E|S-s|^3}{8s^{5/2}}.                \tag{18}
\]
This is (7), rescaled and averaged; the linear term has zero expectation.

**PROVEN UNDER \(\|W_1\|_{\rm op}\leq B\) and \(s\asymp n\):** The error in (18) is \(O_B(n^{-1})\).

*Proof.* The function \(R(X)=\|\operatorname{relu}(W_1X)\|\) is \(B\)-Lipschitz. Gaussian concentration gives bounded fixed moments of \(R-\mathbb ER\). Since
\[
S-s=2(\mathbb ER)(R-\mathbb ER)
 +(R-\mathbb ER)^2-\operatorname{Var}R
\]
and \(\mathbb ER\leq\sqrt s=O(\sqrt n)\),
\(\mathbb E|S-s|^3=O_B(n^{3/2})\). Substitute in (18). ∎

**PROVEN UNDER unit-cost evaluation of the requisite bivariate Gaussian moments:** \(s,v\) are computable in \(O(n^3)\) arithmetic work: form \(W_1W_1^\top\), then sum
\[
\mathbb E(Z_i)_+^2(Z_j)_+^2
-\mathbb E(Z_i)_+^2\,\mathbb E(Z_j)_+^2
\]
over all pairs. These are bivariate Gaussian moments; this step does not require deeper-network integration.

For the reference-trajectory control
\[
G_1(X)=s_1\|h_1(X)\|q_L,
\]
its mean is therefore approximated deductively by
\(s_1A(W_1)q_L\).

**PROVEN UNDER the preceding moment condition:** This introduces squared bias \(O(s_1^2n^{-2})\), at setup cost \(O(n^3)\). At \(L=\alpha n\), that setup is \(O(1)\) forward passes. Over independent suffix weights, \(\mathbb Es_1^2=1\), by expected squared-norm preservation.

**HEURISTIC:** This is a credible component of a practical hybrid: compute early radial expectations analytically and sample or otherwise integrate only their corrections. Removing one coarse sampled level does not itself improve the multilevel asymptotic exponent.

**CONJECTURE:** Similar analytic treatment of a growing number of useful prefix controls, without cost exploding with prefix depth, could produce a deductive improvement over the existing multilevel construction. The unresolved part is computing those deeper radial moments cheaply.

### 5.2 Low-order or factorized controls, with an explicit budget test

**PROVEN:** Suppose a computable function \(g(X)\) has a known exact mean, construction cost \(B\) forward passes, and
\[
\operatorname{tr}\operatorname{Var}(a(X)-g(X))=\eta V(W).
\]
If evaluating the residual costs \(a\) forward passes, then at total budget \(N>B\), independent residual sampling gives
\[
\mathrm{nMSE}=\frac{\eta a}{N-B},
\]
ignoring integer allocation.

*Proof.* Add the exact mean of \(g\) to the sample average of \(a-g\). The estimator is unbiased, and the variance of an average divides by its sample count. ∎

**PROVEN:** Against a comparator achieving \(0.40/N\), this construction wins exactly when
\[
\eta<\frac{0.40}{a}\left(1-\frac BN\right).                \tag{19}
\]
This is a useful acceptance criterion for ANOVA, shallow-ReLU, factorized-code, or radial controls.

**PROVEN:** “Captures \(99\%\) of predictive variance” alone does not meet this criterion: one must compute the control’s mean. In particular, an orthogonal projection onto a function space containing constants already contains the unknown target mean in its constant coefficient. Treating that coefficient as given would make the proposed estimator circular.

**CONJECTURE:** At \(256\times32\), a future-aware shallow control with analytically computable mean and residual variance below roughly \(0.3V\), at near-forward evaluation cost and modest setup, is a more plausible first win than increasing a dense cumulant order. I have not constructed or tested one achieving that threshold.

### 5.3 Fixed architecture and arbitrarily high precision

**PROVEN UNDER fixed finite weights, exact polyhedral preprocessing, and charged high-order quadrature:** For each fixed network with \(V(W)>0\), there is a deterministic integration algorithm with cost polynomial in \(\log(1/\varepsilon)\), with constants and polynomial degree depending on the fixed architecture and weights. Consequently it eventually beats the \(\varepsilon^{-2}\) sampling rate as \(\varepsilon\to0\).

*Proof.* Enumerate activation patterns. Each feasible pattern defines a polyhedral cone on which the network is a linear map \(A_Cx\). Intersect with input coordinate orthants, making each cone pointed. Section each cone by
\(\sum_i|x_i|=1\), and triangulate the resulting compact polytope.

For a simplicial cone, write
\[
x=r\,u(\lambda),\qquad
u(\lambda)=\sum_{i=1}^n\lambda_i v_i,\qquad
\lambda_i\geq0,\quad\sum_i\lambda_i=1,
\]
where each \(v_i\) lies in the same signed coordinate simplex. In particular,
\(\|u(\lambda)\|\geq n^{-1/2}\).

The radial Gaussian integral is explicit:
\[
\int_0^\infty r^n e^{-r^2\|u\|^2/2}\,dr
=
2^{(n-1)/2}\Gamma((n+1)/2)\,\|u\|^{-(n+1)}.
\]
Thus the cone’s vector mean reduces, up to a known determinant and normalization factor, to
\[
\int_{\Delta_{n-1}}
\frac{A_Cu(\lambda)}{\|u(\lambda)\|^{n+1}}\,d\lambda.
\]
A polynomial simplex-to-cube map gives an analytic integrand on a complex neighborhood of a compact cube: the denominator stays away from zero on the real domain and therefore on a sufficiently small neighborhood.

Tensor-product high-order quadrature consequently has error \(O(e^{-cm})\) using \(m^{n-1}\) nodes. Choose \(m=O(\log(1/\varepsilon))\), accounting for the finite number of cones and desired vector accuracy. Computing nodes and arithmetic precision adds polynomial-logarithmic overhead. The finite geometric preprocessing is independent of \(\varepsilon\). ∎

**PROVEN:** This is not a uniform \(O(\varepsilon^{-2}F)\) theorem with useful architecture-independent constants. It does show that an unrestricted impossibility statement covering every precision at fixed architecture must confront analytic region integration.

**HEURISTIC:** Its crossover at \(256\times32\) is likely unusably large. I have not bounded or measured it.

## 6. Falsifiable quantitative predictions and cheapest tests

1. **PROVEN prediction: ensemble variance interval.**  
   At \(256\times32\),
   \[
   0.4995107\leq\mathbb EV\leq20.13891.
   \]
   **Cheapest test:** use independent input pairs and average
   \(\frac12\|a(X)-a(X')\|^2\) over weights and inputs. No ground-truth mean is needed. A statistically convincing violation would indicate an error in the proof, implementation, or setting.

2. **PROVEN asymptotic prediction; CONJECTURE for the finite band.**  
   The exact first Gaussian replacement satisfies
   \[
   \sqrt n\,\mathbb E\rho_1\longrightarrow0.5625.
   \]
   I predict a finite band \(0.50\)–\(0.62\) at \(n=32,64,128,256\).  
   **Cheapest test:** only the first layer is needed. Its true annealed radius is exactly \(m_na_n\); estimate the matched-Gaussian radius, using the Taylor polynomial in squared radius as a control variate. Failure of the finite band alone would not refute the asymptotic theorem.

3. **CONJECTURE \(H_R\), quantitative sign test.**  
   For Gaussian states encountered by exact closure,
   \[
   \mathbb E_{W_\ell}\rho_\ell\geq0.
   \]
   Consequently the weighted total in (10) is at least
   \(a_n^{L-2}\mathbb E\rho_1\).  
   **Cheapest test:** save a few closure states, especially early and middle ones, and draw fresh independent layers. A confidence interval entirely below zero for one fixed state refutes \(H_R\). Testing only encountered states cannot prove its universal form.

4. **PROVEN conditional prediction: one-replacement error floor.**  
   At \(256\times32\), if a verified estimate establishes
   \(\sqrt{256}\,\mathbb E\rho_1\geq0.53\), then
   \[
   \mathcal R_{\rm one\ replacement}\geq1.49\times10^{-5}.
   \]
   **Cheapest test:** propagate paired true-law and matched-Gaussian inputs through a common exact suffix and estimate their mean difference. Use independent batches for an unbiased cross-product estimate of squared bias. This tests the one-replacement theorem, not the full ARC recursion.

5. **CONJECTURE: sharper accuracy of the analytic radial control.**  
   For random first layers, I expect
   \[
   \mathbb E_W\left|
   \mathbb E_X\|h_1(X)\|-A(W_1)
   \right|^2=\Theta(n^{-3}),
   \]
   sharper than the \(O(n^{-2})\) bound above. A practical prediction is a squared-error ratio between \(0.06\) and \(0.25\) when width doubles in the \(64\)–\(256\) range.  
   **Cheapest test:** first-layer computations only, using the exact second-order control to reduce reference noise. This conjecture fails if \(n^3\) times the squared bias grows systematically.

6. **CONJECTURE: cheap code transitions need a separate law-complexity test.**  
   For the reported late-layer codes, I predict a threshold-map decoder can achieve below \(2\%\) held-out bit error at some cuts \(\ell=16,24\), while a product approximation to the code law can still miss more than \(1\%\) of output variance.  
   **Cheapest test:** reuse encoded trajectories, fit the transition on one split, and compare true-law versus product-law decoded future means on another. This directly separates cheap bit updates from cheap expectation propagation. It is a finite experimental prediction, not a theorem about the best possible code.

The two strongest conclusions I would retain are:

- **Negative — PROVEN:** One exact Gaussian replacement after layer 1 leaves normalized annealed error at least \(c_G(\alpha)/n\) at \(L=\alpha n\). **PROVEN UNDER \(H_R\):** repeated exact Gaussian closure inherits this obstruction and cannot have growing gain over MC at its \(O(n)\)-pass cost. No corresponding general higher-order or future-aware lower bound has been established here.

- **Positive — PROVEN at fixed architecture; CONJECTURE at useful budgets:** Region integration eventually gives a deductive high-precision win. The more practical possibility is to integrate early radial or factorized controls analytically and retain only inexpensive corrections; (18) supplies one concrete component, while computing enough deeper controls cheaply remains open.
