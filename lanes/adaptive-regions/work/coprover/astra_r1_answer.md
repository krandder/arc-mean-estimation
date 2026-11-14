codex
**Summary.** Plain stratification cannot have a positive asymptotic \(\beta\) uniformly in width for these random nets: with high probability, their output laws contain components of dimension proportional to \(n\). This does **not** rule out useful gains over a finite budget range, or gains from control variates.  
Full gate-region enumeration is particularly unfavorable: at \(n=256\), even the best selection of \(4096\) full gate regions covers at most about \(2.9\times10^{-29}\) of input mass **in ensemble expectation**.  
Gate changes are not a lower bound on prediction error. Coarse cells with cheap probabilities and fitted linear control variates remain plausible, but K1–K6 do not determine their numerical gains.

I read only the statement from this lane. I use K1–K5 where indicated; K6 is supporting empirical evidence, not a proof.

Throughout, fix \(W\), put \(F=f(X)\), and assume
\[
V=\operatorname{tr}\operatorname{Cov}(F)>0.
\]
For a partition \(C\in\{1,\ldots,K\}\), write
\[
p_k=P(C=k),\qquad
\sigma_k^2=\operatorname{tr}\operatorname{Cov}(F\mid C=k),
\]
and define
\[
T=\sum_kp_k\sigma_k,\qquad A=T^2,\qquad B=\sum_kp_k\sigma_k^2.
\]
Thus oracle Neyman and proportional allocation have MSE \(A/N\) and \(B/N\), respectively, ignoring integer allocation and construction costs.

These formulas require exact cell probabilities and independent conditional samples. Those requirements are material here.

---

**Q1. Ceilings**

**(a) PROVEN, using K1: its ensemble obstruction applies to weight-independent stratification.**

With deterministic allocation fractions \(q_k>0\), \(\sum q_k=1\), the variance coefficient is
\[
C_q(W)=\sum_k\frac{p_k^2\sigma_k(W)^2}{q_k}.
\]
The estimator is a rule linear in sampled values, with points and coefficients chosen independently of \(W\). K1 therefore applies after averaging over the random conditional samples.

In particular, in the stated range \(K\le N\le n/2\),
\[
\boxed{\mathbb E_W C_q(W)\ge \frac1{4\pi^2}\approx0.02533.}
\]

The harmonic obstruction in K1 is more informative when expressed relative to the energy in its obstructed components. If those components retain a nonvanishing fraction of ensemble variance, then the variance coefficient cannot decay as \(K^{-\beta}\), with a positive width-independent \(\beta\), throughout the corresponding sample-size range.

Three qualifications matter:

* This is an **ensemble** conclusion, not a lower bound for every realized network.
* \(\mathbb E C_q/\mathbb E V\) and \(\mathbb E(C_q/V)\) are different quantities. K1 alone does not interchange them.
* The measured \(0.17\) even-degree-\(\ge6\) angular fraction in K3 is not automatically \(0.17\) of total variance. Converting it requires the angular/total variance ratio and the precise spectrum to which K1 applies.

There is a useful, separate per-network rotation statement.

**PROVEN: a Haar-rotation bound for proportional allocation.**

Fix a network and a partition, and rotate the partition by a Haar-random \(U\in O(n)\). Expand the centered homogeneous function into its angular harmonic components. Let \(E_\ell\) denote their Gaussian \(L^2\) energies. The rotationally invariant component is
\[
(R-\mathbb ER)\,\mathbb E g,
\]
with energy \(E_0\). For \(\ell\ge1\), the harmonic-space dimension is
\[
d_\ell=\binom{n+\ell-1}{\ell}
       -\binom{n+\ell-3}{\ell-2}.
\]
Then there are numbers \(a_\ell\in[0,1]\) satisfying
\[
a_0+\sum_{\ell\ge1}d_\ell a_\ell\le K-1
\]
such that
\[
\boxed{\mathbb E_U B_U=\sum_{\ell\ge0}(1-a_\ell)E_\ell.}
\]
Consequently,
\[
\boxed{\mathbb E_U B_U
\ge
\sum_{\ell\ge1}
\left(1-\frac{K-1}{d_\ell}\right)_+E_\ell.}
\]

**Proof.** Conditional expectation onto cellwise constants is an orthogonal projection. After removing constants, its rank is \(K-1\). Average its conjugates over rotations. On each irreducible harmonic subspace, the averaged operator is a scalar \(a_\ell I\). Positivity and contraction give \(0\le a_\ell\le1\); its trace on the mutually orthogonal harmonic subspaces is at most \(K-1\). Applying the averaged projection to each output coordinate proves the identity and bound. The radial factor \(R\) is the same for every basis function within a given positive-degree harmonic subspace, so it does not change this argument. ∎

For example,
\[
d_1=n,\qquad d_2=\frac{(n-1)(n+2)}2.
\]
At \(n=256\), \(d_2=32895\). With \(K=4096\), the displayed bound retains at least \(87.55\%\) of the degree-2 energy.

In particular, if \(K=o(n)\), a Haar-rotated fixed partition captures only \(o(1)\) of the angular variance, whatever the network’s output covariance rank.

This theorem concerns \(B\), not oracle \(A\). For another fixed allocation,
\[
C_q\ge \left(\min_k\frac{p_k}{q_k}\right)B.
\]
Without control of allocation imbalance, the proportional bound cannot simply be transferred to \(A\).

---

**(b) PROVEN: there is no ceiling depending only on \(K\).**

This remains true within continuous, positively homogeneous ReLU networks.

Consider the scalar output
\[
F_M=(X_1-M|X_2|)_+.
\]
It is implemented by three first-layer units and one second-layer unit, and can be embedded in the stipulated widths and greater depths.

Partition into \(F_M=0\) and \(F_M>0\). The active probability is
\[
p_M=\frac{\arctan(1/M)}{\pi}\longrightarrow0.
\]
If \(m_M\) and \(s_M^2\) are the conditional mean and variance on the active cell, then
\[
A=p_M^2s_M^2,\qquad
V=p_Ms_M^2+p_M(1-p_M)m_M^2.
\]
Therefore
\[
\boxed{\frac VA
=\frac1{p_M}+\frac{(1-p_M)m_M^2}{p_Ms_M^2}
\ge \frac1{p_M}\longrightarrow\infty}
\]
with only two cells.

This is not merely an isolated zero-probability weight configuration: for each finite target gain, continuity in the weights gives a neighborhood retaining a large gain, and the Gaussian weight distribution gives that neighborhood positive probability.

A useful ceiling must therefore involve the output law, additional regularity, or restrictions on partitions.

**PROVEN: output quantization gives a general ceiling.**

Let
\[
e_{K,1}(P_F)=\inf_{a_1,\ldots,a_K}
\mathbb E\min_j\|F-a_j\|.
\]
For every partition, including one selected with full knowledge of \(W\),
\[
\boxed{A\ge e_{K,1}(P_F)^2.}
\]

**Proof.** Taking \(a_k=\mathbb E[F\mid C=k]\),
\[
\mathbb E\min_j\|F-a_j\|
\le \mathbb E\|F-a_C\|
\le \sum_kp_k\sqrt{\mathbb E[\|F-a_k\|^2\mid C=k]}
=T.
\]
Now minimize over centers. ∎

A sharper information bound is available for an absolutely continuous \(d\)-dimensional output or orthogonal output projection \(Z\).

**PROVEN UNDER finite differential entropy:**
\[
\boxed{
A\ge \frac d{2\pi e}
\exp\!\left(\frac{2(h(Z)-H(C))}{d}\right)
\ge \frac d{2\pi e}e^{2h(Z)/d}K^{-2/d}.
}
\]

**Proof.** Gaussian maximal entropy and the arithmetic–geometric mean inequality give
\[
h(Z\mid C=k)
\le \frac d2\log\!\left(\frac{2\pi e\,\sigma_k^2}{d}\right).
\]
Average and use \(\sum p_k\log\sigma_k\le\log T\). Also,
\[
h(Z\mid C)=h(Z)-I(Z;C)\ge h(Z)-H(C).
\]
Rearranging proves the result. ∎

For \(Z\sim N(0,I_d)\), this becomes
\[
\boxed{A\ge dK^{-2/d},\qquad V/A\le K^{2/d}.}
\]

Atoms and singular components require conditioning, rather than assigning an ambient differential entropy to the entire output law. If an event \(H\), of probability \(p>0\), supports a \(d\)-dimensional continuous output component, then
\[
T\ge p\,T_H,
\]
because conditional variance within a cell dominates the corresponding within-\(H\) variance times \(P(H\mid C)\). Thus the same bound applies with an additional factor \(p^2\).

**PROVEN: input information gives another ceiling.**

If the cell label is determined by \(Z=P_SX\), define
\[
\tau(z)^2=\operatorname{tr}\operatorname{Cov}(F\mid Z=z).
\]
Then
\[
\boxed{A\ge \bigl(\mathbb E\tau(Z)\bigr)^2,\qquad
B\ge\mathbb E\tau(Z)^2.}
\]

Indeed, total conditional variance gives
\(\sigma_C^2\ge\mathbb E[\tau(Z)^2\mid C]\), and
\(\sqrt{\mathbb E[\tau^2\mid C]}\ge\mathbb E[\tau\mid C]\).

This is the relevant structural quantity for a restricted family of input directions. Gradient participation ratio alone does not determine it.

**PROVEN: depth-\(D\) hyperplane trees have a particularly clear bound for linear targets.**

For \(F=AX\), let \(\lambda_1\ge\cdots\ge\lambda_n\) be the eigenvalues of \(A^TA\). Every leaf of a depth-\(D\) hyperplane tree depends on at most \(D\) linear forms. Hence, even when different leaves use different normals,
\[
\boxed{A_{\rm strat}\ge\sum_{j>D}\lambda_j.}
\]

**Proof.** On a leaf, let \(S\) span its queried normals. Conditioning on that leaf leaves the independent Gaussian component in \(S^\perp\) unchanged. Its contribution to conditional output variance is
\[
\operatorname{tr}A(I-P_S)A^T
\ge\sum_{j>D}\lambda_j.
\]
Every leaf standard deviation exceeds the square root of this common lower bound; averaging and squaring proves the claim. ∎

For \(F=X\),
\[
\boxed{V/A\le n/(n-D).}
\]
At \(n=256,D=12\), this is \(1.0492\).

This covers coordinate, first-layer-normal, and arbitrary hyperplane trees **for a linear target**. Extending it to the nonlinear network requires control of the conditional uncertainty above; K4 is not such a theorem.

---

**(c) PROVEN: the actual random networks have an asymptotic obstruction stronger than covariance participation ratio suggests.**

For almost every network, a full-dimensional gate cell with linear map of rank \(r\) and positive probability implies
\[
\boxed{A(K)\ge c(W,\text{cell})K^{-2/r}}
\]
for every partition into \(K\) cells, with \(c>0\).

**Proof.** Condition on that gate cell. The output is \(AX\). Project onto the \(r\)-dimensional image of \(A\). Its conditional density is bounded above by the corresponding nonsingular Gaussian density divided by the cell probability. It has finite second moment and finite differential entropy. Apply the preceding entropy bound conditionally and then \(T\ge pT_H\). ∎

Now fix one nonzero deterministic input. Before extinction, each layer’s active count is binomial \(\operatorname{Bin}(n,1/2)\). Hoeffding and a union bound give
\[
P\{\text{every layer has at least }n/4\text{ active units}\}
\ge1-Le^{-n/8}.
\]
Almost surely, the linear map on its gate cell has rank equal to the minimum active count: failure of the relevant generic matrix-product rank is an algebraic null event. Strict gate inequalities give a neighborhood of the input, hence a cell of positive Gaussian mass.

Therefore, with the displayed probability,
\[
\boxed{\beta_{\rm asymptotic}\le 8/n.}
\]
More sharply, along \(L=n/8\), the minimum active count at this fixed input is \((1/2-o(1))n\) with high probability, giving
\[
\boxed{\beta_{\rm asymptotic}\le(4+o(1))/n.}
\]

The constant \(c(W,\text{cell})\) can be extremely small. This is an **all-\(K\) asymptotic obstruction**, not a prediction of gains at \(K\le4096\).

**PROVEN: width-uniform positive exponents are possible for specially structured networks.**

Take \(F=(X_1)_+e_1\) at every width and depth. Allocate one cell to \(X_1\le0\), \(K-2\) equal intervals on
\([0,\sqrt{6\log K}]\), and one tail cell. Using interval midpoints as candidate conditional predictors,
\[
B\le O(\log K/K^2),
\]
because the bounded-interval squared error is at most one quarter of the squared interval width, and
\[
\mathbb E[X_1^2;X_1>t]=t\phi(t)+1-\Phi(t).
\]
Thus every fixed \(\beta<2\) holds uniformly in width.

The needed property is a genuinely small-dimensional output law, or a uniformly small-dimensional residual after a known-mean model is removed. A participation ratio near two is insufficient: a fixed residual variance spread across increasingly many directions preserves a high-dimensional asymptotic obstruction.

---

**Q2. Neyman versus proportional allocation**

**PROVEN:**
\[
\frac BA
=\frac{\mathbb E_p\sigma^2}{(\mathbb E_p\sigma)^2}
=1+\operatorname{CV}_p(\sigma)^2.
\]
Also,
\[
A\ge p_{\min}B.
\]
Thus equal-probability cells give \(B/A\le K\); arbitrary cell probabilities give no ceiling depending only on \(K\).

The rare-wedge example above has only one variable cell, so
\[
\boxed{B/A=1/p_M.}
\]
This is a concrete non-Gaussian, white-box mechanism for a large allocation advantage.

For the random networks, the relevant empirical question is whether a small amount of input probability carries a large fraction of **conditional residual variance**. Large activation amplitudes, conditional amplification, or sparse active pathways could cause this. K2’s kurtosis is over networks at a fixed input; it does not establish this within-network property.

Moreover, a fixed finite network satisfies
\[
\|f(x)\|\le H_W\|x\|,
\qquad H_W\le\prod_\ell\|W_\ell\|_{\rm op}.
\]
Its input-induced output tails are therefore Gaussian-controlled, although the constant may be large. Ensemble kurtosis should not be read as evidence of arbitrarily heavy input tails.

**PROVEN: homogeneity largely settles the purely radial question.**

Write \(X=RU\), with \(R\perp U\), and define
\[
a_n=\mathbb ER=\sqrt2\,\frac{\Gamma((n+1)/2)}{\Gamma(n/2)},\quad
v_n=n-a_n^2,
\]
\[
m=\mathbb Eg(U),\qquad s^2=\operatorname{tr}\operatorname{Cov}(g(U)).
\]
Then
\[
V=ns^2+v_n\|m\|^2.
\]
For a radial interval \(I\),
\[
\sigma_I^2
=\mathbb E[R^2\mid I]s^2+\operatorname{Var}(R\mid I)\|m\|^2.
\]
In the limit of fine radial strata, when \(s>0\),
\[
B_{\rm rad}\to ns^2,\qquad A_{\rm rad}\to a_n^2s^2.
\]
Hence the limiting Neyman/proportional advantage is only
\[
\boxed{n/a_n^2.}
\]

| \(n\) | Radial Neyman/proportional advantage |
|---:|---:|
| 32 | 1.01575 |
| 64 | 1.00784 |
| 128 | 1.00391 |
| 256 | 1.00196 |

If \(s=0\), the function is purely radial and radial stratification can instead solve the main variation.

For angular strata,
\[
\sigma_k^2
=n\operatorname{tr}\operatorname{Cov}(g\mid k)
+v_n\|\mathbb E[g\mid k]\|^2.
\]
Even arbitrarily fine angular strata retain radial sampling noise.

The clean improvement is to integrate radius analytically:
\[
\boxed{\mu=a_n\,\mathbb E_U g(U).}
\]
This removes radial randomness without a tree.

---

**Q3. “Understanding” a region**

**PROVEN: the required integration is a solid-angle problem, not just linear algebra.**

For a full gate cone \(C\),
\[
\mathbb E[F;C]=A_C\,\mathbb E[X;C].
\]
Knowing \(A_C\) does not give the latter vector.

For a polyhedral cone with irredundant facets and inward unit normals \(u_j\),
\[
\boxed{
p_Cc_C
=\frac1{\sqrt{2\pi}}\sum_j u_j\,p_j^{\rm facet},
}
\]
where \(p_j^{\rm facet}\) is the standard \((n-1)\)-dimensional Gaussian probability of that facet within its supporting hyperplane.

**Proof.** Since \(\nabla\phi_n(x)=-x\phi_n(x)\), the divergence theorem gives
\[
\int_Cx\phi_n(x)\,dx=-\int_{\partial C}\phi_n(x)\nu(x)\,dS.
\]
The outward normal is \(-u_j\), and the Gaussian density normal to a hyperplane through the origin contributes \(1/\sqrt{2\pi}\). ∎

Thus the centroid reduces to additional lower-dimensional solid-angle integrals. It does not generally eliminate integration.

I do not claim a formal complexity classification without specifying the numerical accuracy and computational model. What is explicit is that direct indicator Monte Carlo estimates \(p\) with relative RMS error
\[
\sqrt{\frac{1-p}{Mp}},
\]
requiring order \(1/(p\varepsilon^2)\) proposals for relative precision \(\varepsilon\). Rejection sampling a conditional point costs \(1/p\) proposals on average.

**PROVEN: very little mass can be covered by a modest number of full gate regions.**

Let \(p_s(W_1)\) be first-layer sign-cell probabilities and define
\[
\mathcal C_n=\mathbb E_{W_1}\sum_sp_s(W_1)^2.
\]
Two independent Gaussian inputs have angle \(\Theta\), and a random row agrees in sign with probability \(1-\Theta/\pi\). Therefore
\[
\boxed{
\mathcal C_n=
\frac{\Gamma(n/2)}{\sqrt\pi\,\Gamma((n-1)/2)}
\int_0^\pi
(1-\theta/\pi)^n\sin^{n-2}\theta\,d\theta.
}
\]
Deep gate cells refine first-layer cells, so their sum of squared probabilities is no larger.

For any selection of \(K\) full gate cells, including the optimal selection after seeing \(W\), Cauchy–Schwarz and Jensen give
\[
\boxed{
\mathbb E_W[\text{covered mass}]
\le\sqrt{K\mathcal C_n}.
}
\]

Numerical evaluation of this exact bound gives:

| \(n\) | \(\mathcal C_n\) | Expected mass bound for \(K=4096\) |
|---:|---:|---:|
| 32 | \(2.63\times10^{-8}\) | \(1.04\times10^{-2}\) |
| 64 | \(6.77\times10^{-16}\) | \(1.67\times10^{-6}\) |
| 128 | \(4.50\times10^{-31}\) | \(4.30\times10^{-14}\) |
| 256 | \(1.99\times10^{-61}\) | \(2.86\times10^{-29}\) |

This bound already follows from the first layer. It does **not** apply to unions of many gate cells that share a useful model, or to coarse cells on which a model is merely accurate.

Also, the fact that a fixed first-layer sign pattern has expected mass \(2^{-n}\) does not mean cells of a realized network have equal mass, or that the cell containing a random input has expected mass \(2^{-n}\). The latter sampling is size-biased; \(\mathcal C_n\) is the relevant quantity.

**PROVEN: useful cheap-probability families exist, with a geometric tradeoff.**

* Boxes in an orthonormal frame have product Gaussian probabilities and explicit truncated-normal centroids.
* Orthant cones in such a frame have \(p=2^{-D}\) and centroid entries \(\pm\sqrt{2/\pi}\).
* A single circular cone has a one-dimensional spherical-cap probability integral and an axial centroid.
* A cell defined using \(D\) arbitrary normals reduces its probability calculation to a \(D\)-dimensional correlated Gaussian problem.

The first two families are cheap to partition and sample. They generally cross many network gates. Small circular cones can be local, but their probabilities become tiny, and intersections used to form a partition lose the single-cap formula.

**PROVEN: a local linear control variate removes exactly a regression projection.**

On cell \(k\), use
\[
h_k(x)=a_k+B_kx
\]
and integrate it through the known \(p_k,c_k\). The residual covariance trace is minimized by
\[
B_k^*=\operatorname{Cov}(F,X\mid k)
       \operatorname{Cov}(X\mid k)^\dagger,
\]
with minimum
\[
\boxed{
\sigma_{k,\rm res}^2
=\sigma_k^2-
\operatorname{tr}\!\left[
\operatorname{Cov}(F,X\mid k)
\operatorname{Cov}(X\mid k)^\dagger
\operatorname{Cov}(X,F\mid k)
\right].
}
\]
This follows by completing the square in the conditional least-squares objective.

For a global linear model under Gaussian input,
\[
B^*=\mathbb E[FX^T]=\mathbb E[J(X)]
\]
by Gaussian integration by parts. It removes the first Hermite component, which for a homogeneous function is its degree-1 angular component.

Using K3, removing \(0.29\) of angular variance would give about
\[
1/(1-0.29)=1.408
\]
gain if angular variance dominated total variance. This is a conditional numerical implication, not a guaranteed fitted-model result.

**PROVEN UNDER a boundary-tube hypothesis:** local models can improve the geometric exponent.

Suppose angular cells have diameter at most \(\delta\), their model is the gate-linear map at a representative, \(f\) is \(H\)-Lipschitz, and the probability of cells intersecting a gate boundary is at most \(C_\partial\delta\). Uncut cells have zero residual. On cut cells, the unit-radius residual is at most \(2H\delta\). Hence
\[
\boxed{B_{\rm res}\le4nH^2C_\partial\delta^3.}
\]
A regular angular mesh with \(K\asymp\delta^{-(n-1)}\) consequently gives a bound of order
\[
K^{-3/(n-1)}.
\]
This is a small-cell result with potentially large constants, not a width-uniform exponent. It also assumes that the model integrals are available.

---

**Q4. Bandit allocation**

**PROVEN UNDER bounded observations, exact cell probabilities and independent conditional sampling:** an explicit pilot-allocation scheme has the familiar worst-case rate
\[
\boxed{
\mathbb E[\mathrm{MSE}]
\le \frac AN
+\widetilde O\!\left(M^2K^{1/3}N^{-4/3}\right),
}
\]
where \(\|F\|\le M\). Here the tilde hides logarithms.

A proof is useful because it separates allocation regret from estimation bias.

Take \(m\) independent pairs per cell and estimate variance using
\[
Z=\tfrac12\|F-F'\|^2.
\]
Then
\[
0\le Z\le2M^2,\qquad \mathbb EZ=\sigma_k^2,\qquad
\operatorname{Var}(Z)\le2M^2\sigma_k^2.
\]
Bernstein’s inequality, followed by taking square roots, gives simultaneously
\[
|\widehat\sigma_k-\sigma_k|
\le \eta,\qquad
\eta=3M\sqrt{\log(2K/\delta)/m},
\]
with probability at least \(1-\delta\).

Allocate fresh estimation samples according to
\[
q_k=\frac{p_k(\widehat\sigma_k+\eta)}
          {\sum_jp_j(\widehat\sigma_j+\eta)}.
\]
On that event,
\[
\sigma_k\le\widehat\sigma_k+\eta\le\sigma_k+2\eta,
\]
and therefore
\[
\sum_k\frac{p_k^2\sigma_k^2}{q_k}
\le T(T+2\eta).
\]
Allowing one sample per cell for rounding, the estimation budget is at least \(N-2Km-K\). The excess over \(A/N\) is bounded by terms of orders
\[
\frac{M^2Km}{N^2},
\qquad
\frac{M^2\sqrt{\log(K/\delta)}}{N\sqrt m},
\qquad
\frac{M^2K}{N^2},
\qquad M^2\delta.
\]
Choosing
\[
m\asymp(N/K)^{2/3}\log(K/\delta)^{1/3}
\]
proves the stated rate. The fresh estimation samples make the estimator conditionally unbiased. ∎

For the original unbounded Gaussian input, this bounded theorem does not directly apply. Radial integration makes the angular integrand bounded for each fixed network, but its envelope-to-variance ratio need not be uniform in \(n\).

If \(A/V\asymp K^{-\beta}\), \(K\asymp N^a\), and the constants remain controlled, this guarantee gives
\[
\mathrm{nMSE}\lesssim
N^{-(1+a\beta)}
+\widetilde O\!\left(N^{-(4-a)/3}\right).
\]
Thus the guaranteed exponent is
\[
\boxed{\min\{1+a\beta,(4-a)/3\}.}
\]
Balancing the terms gives
\[
a=\frac1{1+3\beta},\qquad
\boxed{\text{exponent}=1+\frac{\beta}{1+3\beta}.}
\]

This is a worst-case guarantee, not a universal \(4/3\) ceiling on adaptive integration. More favorable variance structure can permit faster allocation learning.

A further caution: the usual MC-UCB quantity
\[
\sum_kp_k^2\sigma_k^2/N_k
\]
is an allocation **pseudo-risk**. If the same observations choose stopping counts and form sample means, actual MSE does not automatically equal that expression. Independence, a suitable unbiased construction, or an additional theorem is required.

---

**Q5. Settling regions**

**PROVEN: an unbounded cone generally has infinite raw output range.**

If \(f(u)\ne0\) somewhere in a cone, then \(f(ru)=rf(u)\). Thus finite upper/lower output ranges over the entire cone do not exist in the relevant nonzero coordinates.

One must first integrate radius, truncate it with a controlled tail, or certify the integral directly.

**PROVEN: Lipschitz bounds are available, but are not necessarily sharp.**

Let
\[
H=\sup_x\|J(x)\|_{\rm op}\le\prod_{\ell=1}^L\|W_\ell\|_{\rm op}.
\]
On a spherical cap of radius \(\delta\le\pi/2\), every unit output projection has range at most
\[
\boxed{2H\sin\delta.}
\]
This follows from the cap’s Euclidean diameter and Lipschitz continuity.

**HEURISTIC numerical scale:** a He Gaussian matrix has operator norm near \(2\sqrt2\). The product bound then behaves like
\[
(2\sqrt2)^L,
\]
which at \(L=32\) is \(2^{48}\approx2.8\times10^{14}\). This is the scale of a crude certificate, not a claim about typical local sensitivity.

For interval propagation, interval-width vectors satisfy
\[
w_\ell\le |W_\ell|w_{\ell-1}.
\]
The expected absolute row sum is exactly
\[
\mathbb E\sum_j|W_{\ell,ij}|=2\sqrt{n/\pi}.
\]
At \(n=256\), that is about \(18.05\) per layer. Repeated absolute-value propagation can therefore become extremely loose. It does not prove that the true range is large.

CROWN-style methods can exploit stable gates and correlations. K5 does not provide a lower bound on their certificate widths: many gate changes can have negligible output effect.

**PROVEN: small-cap settlement encounters angular covering dimension.**

For a cap of radius \(\delta\),
\[
p_{\rm cap}(\delta)
=c_n\int_0^\delta\sin^{n-2}\theta\,d\theta
\le \frac{c_n}{n-1}\delta^{n-1},
\]
where
\[
c_n=\frac{\Gamma(n/2)}
          {\sqrt\pi\,\Gamma((n-1)/2)}.
\]
If each settled cell lies in such a cap and the settled mass is \(s\), then
\[
\boxed{K\ge s/p_{\rm cap}(\delta).}
\]

For a method requiring uniformly small Lipschitz widths, achieving absolute integral error \(\varepsilon\) therefore leads to a covering cost on the scale
\[
K\gtrsim (a_nH/\varepsilon)^{n-1},
\]
up to geometric constants. This is conditional on that settlement criterion; special functions or stronger certificates can do better.

Also, small cell masses cannot each be counted as a full error budget. The deterministic total error is controlled by
\[
\sum_kp_k\,\text{width}_k.
\]
For equal masses and equal widths, increasing \(K\) does not reduce this sum.

**PROVEN: settling in a deep state does not remove the probability problem.**

Write \(Z=h_d(X)\), \(F=T(Z)\). Even suppose the downstream conditional means \(m_k\) are known exactly. If probabilities are estimated from \(M\) independent prefix samples,
\[
\widehat\mu=\sum_k\widehat p_km_k
\]
has MSE
\[
\boxed{
\frac1M\operatorname{tr}\operatorname{Cov}(m_{C(Z)}).
}
\]
If the downstream function is constant within each state cell, this is \(V/M\): all integration difficulty has moved into cell probabilities.

Deep-state settlement can save downstream evaluation cost, support a control variate, or help when the pushforward law is otherwise tractable. Low covariance participation ratio by itself supplies neither exact probabilities nor low support dimension. Moreover, a late prefix already costs approximately \(d/L\) of a forward pass.

---

**Q6. Branch similarity**

**PROVEN, using K5:** for two fixed input directions separated by \(\theta\),
\[
\boxed{
P_W(\text{all first-layer signs agree})=(1-\theta/\pi)^n.
}
\]
At subsequent layers, while both states are nonzero, conditional expected disagreements are exactly \(n\theta_{\ell-1}/\pi\).

**HEURISTIC:** if angles remain close to \(\theta\), and rare disagreements behave roughly like a Poisson process,
\[
P(\text{same full branch})\approx e^{-nL\theta/\pi}.
\]
The order-one-change scale is consequently
\[
\theta\asymp\pi/(nL).
\]
For \(256\times32\), this is \(3.83\times10^{-4}\). At input correlation \(1-10^{-6}\), \(\theta\approx1.414\times10^{-3}\), giving exponent \(3.69\) and approximately \(97.5\%\) probability of a change. This matches the stated K5 observation at that setting; it is not a proof of independence.

At the radius \(\delta=\pi/(nL)\), the cap bound gives the following approximate lower bounds on the number of caps needed to cover the sphere:

| \(n,L\) | \(\delta\) | \(\log_2 K\), lower bound |
|---|---:|---:|
| \(32,4\) | \(2.45\times10^{-2}\) | 170 |
| \(64,8\) | \(6.14\times10^{-3}\) | 467 |
| \(128,16\) | \(1.53\times10^{-3}\) | 1192 |
| \(256,32\) | \(3.83\times10^{-4}\) | 2899 |

The geometric bound is rigorous for the chosen radius. Interpreting that radius as branch similarity is heuristic.

A cap on which **every** point has the same gates is more demanding than agreement with one random nearby point. Already in the first layer, for a random unit normal \(v\),
\[
P\{|v\cdot u|\le\sin\delta\}
\sim\sqrt{2n/\pi}\,\delta.
\]
Thus the first-layer all-gates-stable cap scale is \(n^{-3/2}\), rather than the \(n^{-1}\) scale for a random pair.

**PROVEN: gate disagreement does not imply large linear prediction error.**

Let \(A_x\) be the gate-linear map at \(x\). Since \(A_xx=f(x)\),
\[
\boxed{\|f(y)-A_xy\|\le2H\|y-x\|.}
\]
More informatively,
\[
f(y)-A_xy
=\int_0^1[J(x+t(y-x))-J(x)](y-x)\,dt.
\]
Errors depend on changed Jacobians and margins, not merely on how many gates changed.

There is an exact one-layer example. For unit \(x,y\) at angle \(\theta\), with one He-initialized ReLU layer,
\[
\boxed{
\mathbb E_W\|f(y)-A_xy\|^2
=\frac2\pi(\theta-\sin\theta\cos\theta)
=\frac4{3\pi}\theta^3+O(\theta^5).
}
\]

**Proof.** For each row, the residual is \(w\cdot y\), up to sign, precisely when the two preactivations disagree in sign. In the two-dimensional Gaussian plane, these events form two wedges of angle \(\theta\). Polar integration gives
\[
\mathbb E[Z_y^2;\text{disagreement}]
=\frac{\theta-\sin\theta\cos\theta}{\pi}.
\]
Multiplying by row variance \(2/n\) and summing \(n\) rows gives the formula. ∎

Thus the expected number of changed gates is order \(n\theta\), while tangent prediction MSE is order \(\theta^3\). An argument that treats every branch change as loss of predictive similarity is false.

---

**Q7. Predictions for the measurements**

K1–K6 do not identify unique numerical gains for these algorithms. Split thresholds, tree balance, training budget, conditional-probability computation, and the relation between gradient directions and value variation are unspecified.

The following separates exact benchmarks from conditional forecasts.

**PROVEN benchmark: balanced sign splits of an isotropic linear target.**

Take \(F=X\), and split \(D=\log_2K\) distinct orthonormal coordinates at zero. Every leaf has the same conditional variance, so Neyman and proportional allocation coincide:
\[
\boxed{G(K)=\frac1{1-(2/\pi)D/n}.}
\]

| \(n\) | \(K=16\) | \(K=256\) | \(K=4096\) | Effective \(\beta\), 16 to 4096 |
|---:|---:|---:|---:|---:|
| 32 | 1.086 | 1.189 | 1.314 | 0.0342 |
| 64 | 1.041 | 1.086 | 1.136 | 0.0156 |
| 128 | 1.020 | 1.041 | 1.063 | 0.00747 |
| 256 | 1.010 | 1.020 | 1.031 | 0.00366 |

Here
\[
\beta_{\rm eff}
=\frac{\log(G(4096)/G(16))}{\log256}.
\]
This displays a \((\log K)/n\) benefit, rather than a width-independent power.

**HEURISTIC forecast for random-frame sign splits.**

Assume:

1. K3’s degree-1 and degree-2 fractions, \(0.29,0.21\), approximate each width;
2. angular variance dominates total variance;
3. higher-degree capture is negligible over these depths;
4. within-cell standard deviations are sufficiently homogeneous that Neyman adds little.

The exact rotation-averaged capture fractions for these two homogeneous harmonic components are
\[
a_1=\frac{2D}{\pi n},
\]
\[
a_2=
\frac{\binom D2}{d_2}
\frac{4(n+2)a_n^2}{\pi^2n^2}.
\]
For degree 1, this follows from \(\mathbb E[X_i\mid\operatorname{sign}X_i]=
\sqrt{2/\pi}\operatorname{sign}X_i\). For degree 2, only off-diagonal sign products survive conditioning; their normalized conditional means have squared magnitude \(4(n+2)a_n^2/(\pi^2n^2)\).

The two-component forecast is
\[
G\approx(1-0.29a_1-0.21a_2)^{-1}.
\]

| \(n\) | \(K=16\) | \(K=256\) | \(K=4096\) | \(\beta_{\rm eff}\) |
|---:|---:|---:|---:|---:|
| 32 | 1.025 | 1.054 | 1.087 | 0.0107 |
| 64 | 1.012 | 1.025 | 1.039 | 0.00473 |
| 128 | 1.006 | 1.012 | 1.018 | 0.00222 |
| 256 | 1.003 | 1.006 | 1.009 | 0.00107 |

These are explicit model predictions, not established network gains. Extrapolating the measured spectrum to \(n=32\) is particularly uncertain. The table concerns sign splits, not optimally placed repeated thresholds.

**SVD and gradient frames: conditional prediction, no proven ordering.**

For the global linear component \(B=\mathbb E J(X)\), define
\[
s_D(Q)=
\frac{\sum_{i=1}^D\|Bq_i\|^2}{\|B\|_F^2}.
\]
Its captured fraction under sign splits is exactly \((2/\pi)s_D\).

The gradient frame helps this component only if leading directions of \(\mathbb E[J^TJ]\) align with \(B^TB\). K4 does not establish that alignment. Likewise, the SVD frame of \(W_1\) need not rank directions by their contribution to the final value function.

For an explicitly optimistic alignment model,
\[
s_D\approx\min(4D/n,1).
\]
At \(n=256\), capturing only the stated degree-1 energy then predicts gains
\[
\boxed{1.012,\quad1.024,\quad1.036}
\]
at the three requested \(K\)’s. These numbers illustrate the alignment hypothesis; they are not consequences of participation ratio \(n/4\).

**First-layer gate-sign splits: HEURISTIC.**

Without local models, I expect diminishing gains with width for \(D=4,8,12\), unless importance ordering finds unusually concentrated value or residual-variance contributions.

With local models, such splits have a genuine advantage: they remove selected first-layer kinks exactly. But unqueried first-layer gates and downstream gates remain. Neither K4 nor K5 determines how much residual energy these selected kinks carry, so a numerical gain for the deep networks cannot be extracted from the supplied facts.

**Greedy CART: HEURISTIC.**

A well-trained tree can outperform fixed frames by finding nonzero thresholds, interactions, and heteroscedastic cells. My working prediction is:

* Plain CART’s finite-range \(\beta\) decreases with width; it does not settle to a positive width-independent exponent.
* Local linear models produce a useful initial gain, potentially comparable to the approximately \(1.4\) global-linear benchmark at \(256\times32\).
* Additional per-cell modeling gains are likely to be constrained by fitting cost before small-cell geometric asymptotics become visible.

There is no theorem here that orders CART, the SVD frame, and the gradient frame on each realized network.

**PROVEN budget warning for local affine fits.**

An unrestricted affine fit in \(n\) input variables needs at least \(n+1\) affinely independent training points per cell to identify its coefficients. Thus \(K=4096\) requires at least

| \(n\) | Training evaluations |
|---:|---:|
| 32 | 135,168 |
| 64 | 266,240 |
| 128 | 528,384 |
| 256 | 1,052,672 |

All exceed \(2^{16}\), before fresh estimation samples. At \(n=256,K=256\), the minimum is already \(65,792\).

Shared models, regularization, restricted input dimension, or weight-derived Jacobians can change this cost, but then their assumptions and computational costs must be included.

For the measurements, the most revealing quantities are separately
\[
\boxed{B/V,\qquad A/B,\qquad A_{\rm residual}/V,}
\]
alongside total forward-equivalent cost. They distinguish variance explained by the partition, gains from allocation, and gains from modeling. A constant control-variate gain should not be mistaken for a positive partition-growth exponent.
