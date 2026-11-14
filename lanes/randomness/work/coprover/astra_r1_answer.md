codex
**PROVEN:** ARC’s ensemble-average MSE criterion alone cannot force a positive random-bit budget: a suitable fixed, weight-independent \(N\)-point rule achieves the average risk of \(N\)-sample radius-exact MC. Finding and representing that rule efficiently remains a computational problem.

I read only `coprover/STATEMENT_r1.md` within this lane, the cited reports, and permitted code. No files were modified. Reported experiments below are evidence, not mathematical guarantees; unchecked literature is marked **UNVERIFIED**.

## 1. Formalising randomness complexity

Write
\[
F_W(u)=m_n f_W(u),\qquad u\in S^{n-1},
\]
where evaluating \(f_W\) on the sphere means evaluating \(g_W\). Define
\[
A(W)=\operatorname{tr}\operatorname{Var}_u F_W(u),\quad
A=\mathbb E_W A(W),\quad
\bar V=\mathbb E_W V(W).
\]

An appropriate complexity specification includes:

- \(R\): fresh random bits used at run time.
- \(T\): construction, preprocessing, point generation, network evaluation, and aggregation cost.
- \(D\): stored advice or point-set description length.
- Numerical precision, including the representation of weights and points.

The three risks are:

\[
\mathcal R_{\rm obl}(Q)
=\frac{\mathbb E_{W,S}\|Q_S(F_W)-\mu(W)\|^2}{\bar V},
\]
for weight-independent rules;

\[
\mathcal R_{\rm wb}(B)
=\frac{\mathbb E_{W,S}\|B(W,S)-\mu(W)\|^2}{\bar V},
\]
for algorithms reading \(W\); and, for example,
\[
\mathcal R_{\rm worst}(B)
=\sup_{W\in\mathcal C:V(W)>0}
\frac{\mathbb E_S\|B(W,S)-\mu(W)\|^2}{V(W)}.
\]

The worst-case model must separately specify whether weight adaptation is allowed.

**PROVEN — support size, seed length, and runtime randomness are different quantities.** A generator indexed by a uniform \(r\)-bit string has at most \(2^r\) outputs. Enumerating all its outputs uses zero runtime random bits and up to \(2^r\) evaluations. Thus \(r=\log_2 N\) describes an index into an equal-weight support, not the randomness used by the enumerating estimator. Arbitrary weighted rules need an additional description of their weights.

**PROVEN — nonuniform derandomisation already works in the oblivious model.** Let \(U_1,\ldots,U_N\) be independent uniform directions. Conditional on \(W\),
\[
\mathbb E_U\left\|\frac1N\sum_iF_W(U_i)-\mu(W)\right\|^2
=\frac{A(W)}N.
\]
To see this, expand the squared norm: each diagonal term contributes \(A(W)\), and every off-diagonal term vanishes by independence and centering. Averaging over \(W\) gives \(A/N\). Consequently, at least one fixed tuple \((u_1,\ldots,u_N)\), independent of \(W\), has ensemble risk at most \(A/N\).

Moreover,
\[
V(W)=A(W)+(n-m_n^2)\mathbb E_u\|g_W(u)\|^2\ge A(W).
\]
This follows by writing \(X=RU\), with \(R,U\) independent, and applying total variance to \(Rg_W(U)\). Hence \(N\ge\epsilon^{-2}\) suffices for an existential deterministic rule.

This proof gives neither an efficient construction nor a short description of its coordinates.

**PROVEN UNDER exact factorisation, probability-transform, and digit-splitting primitives — white-box derandomisation can also be uniform.** Write
\[
W_1=H Q,\qquad H=(W_1W_1^\top)^{1/2}.
\]
Right orthogonal invariance of a Gaussian matrix implies that \(Q\) is Haar and independent of \(H\). The remaining layers are also independent of \(Q\). Input rotation preserves \(\mu\), \(V\), and \(A\).

Under the stated primitives, the nonatomic Haar variable supplies independent uniform bits. These can generate samples for the canonical network with first layer \(H\). For simulation of an arbitrary randomised algorithm, split them into an independent Haar \(Q'\) and algorithmic seed \(S\); run the algorithm on first layer \(HQ'\). This reconstructed network has the original distribution, the seed is independent of it, and its mean equals the original network’s mean. Therefore its average risk is unchanged.

The factorisation costs \(O(n^3)\); exact random-variable transformations are part of the hypothesis. Finite-precision weights do not provide an unlimited source of independent bits.

**PROVEN — the same seed-fixing argument does not preserve a worst-case guarantee.** In general,
\[
\sup_W\mathbb E_S L(W,S)
\ne
\mathbb E_S\sup_W L(W,S).
\]
For example, two instances and two seeds can have loss matrix
\[
\begin{pmatrix}0&1\\1&0\end{pmatrix}.
\]
A uniform seed has worst-case expected loss \(1/2\), whereas either fixed seed has worst-case loss \(1\). Additional class structure is needed to fix a seed uniformly.

**PROVEN — fresh randomness buys conditional unbiasedness and observable replication variance.** If \(Z_1,Z_2\) are independent, conditionally unbiased estimates of \(\mu(W)\), with equal conditional risk \(v(W)\), then
\[
\mathbb E\!\left[\frac{\|Z_1-Z_2\|^2}{2}\,\middle|\,W\right]=v(W).
\]
Expand \(Z_1-Z_2=(Z_1-\mu)-(Z_2-\mu)\); independence and centering eliminate the cross term.

This is an unbiased variance estimate, not automatically a valid confidence interval. Reliable coverage additionally needs a concentration argument, a known bound, or appropriate moment assumptions. Fixing the seed preserves an ensemble-risk statement but removes this conditional replication experiment.

**PROVEN — few bits suffice for MC’s variance calculation on a finite input grid.** Suppose each coordinate uses \(s\) bits, so an entire input has \(ns\) bits. Choose
\[
b\ge \max\{ns,\lceil\log_2 N\rceil\}.
\]
For distinct \(t_i\in\mathrm{GF}(2^b)\), draw uniform \(a,c\) and set
\[
Y_i=at_i+c.
\]
For \(i\ne j\), the map \((a,c)\mapsto(Y_i,Y_j)\) is invertible. Thus the \(Y_i\) are pairwise independent and uniform. Decode \(ns\) bits into the coordinate grid and apply coordinatewise quantile transforms.

This uses \(2b\) random bits and gives exactly the MC variance \(V_{\rm grid}/N\) for the discretised target. Degree-three polynomials give four-wise independence with \(4b\) bits. Exact continuous Gaussian sampling requires an unbounded bit stream; the grid bias must be accounted for separately.

Pairwise independence also makes the usual sample variance unbiased. It does not by itself make that variance estimate concentrate.

**PROVEN — Carathéodory’s observation is correct but computationally incomplete.** The continuous image \(F_W(S^{n-1})\subset\mathbb R^n\) is compact, and its mean lies in its convex hull. Any convex representation using more than \(n+1\) points has an affine dependence. Adjust the coefficients along that dependence until one becomes zero, preserving their sum, nonnegativity, and represented vector. Repeating leaves at most \(n+1\) weighted points.

Finding those points can require essentially solving the original integration problem.

**HEURISTIC — corrected hypothesis.** The useful question is whether an explicit, inexpensive rule exploits the output’s structure well enough to improve error per compute. Output noise sensitivity can help describe that structure. It cannot, by itself, establish a runtime-randomness lower bound under ARC’s ensemble criterion.

## 2. Black-box designs and point-count bounds

Let
\[
F_W=\sum_{d\ge0}F_{W,d}
\]
be its spherical-harmonic expansion, and put
\[
E_d(W)=\|F_{W,d}\|_{L^2(\sigma)}^2,\qquad
a_d=\mathbb E_WE_d(W).
\]
Then \(A=\sum_{d\ge1}a_d\).

Let \(P_d^{(n)}\) be the zonal harmonic normalised by \(P_d^{(n)}(1)=1\). For
\[
Q=\sum_{i=1}^Nw_i\delta_{u_i},\qquad \sum_iw_i=1,
\]
define
\[
B_d(Q)=\sum_{i,j}w_iw_jP_d^{(n)}(u_i\cdot u_j).
\]

**PROVEN — exact spectral pricing.**
\[
\boxed{\mathbb E_W\|QF_W-\mu(W)\|^2
=\sum_{d\ge1}a_dB_d(Q).}
\]
Also, for any fixed \(W\) and independent Haar rotation \(O\),
\[
\boxed{\mathbb E_O\|Q(F_W\circ O)-\mu(W)\|^2
=\sum_{d\ge1}E_d(W)B_d(Q).}
\]

For proof, choose an orthonormal basis \(Y_{d,r}\), \(1\le r\le h_d\), of degree-\(d\) harmonics. The addition formula is
\[
\sum_rY_{d,r}(u)Y_{d,r}(v)=h_dP_d^{(n)}(u\cdot v).
\]
Rotational averaging kills cross terms between different degrees and averages the coefficient covariance within degree \(d\) to \(E_d(W)I/h_d\). Substituting the addition formula gives the second identity. The Gaussian weight ensemble is input-rotation invariant, giving the first.

In particular, \(B_d\ge0\). For positive weights, \(B_d\le1\), since \(|P_d|\le1\).

A fixed net’s energy spectrum alone does not determine its error on an unrotated design: the orientations of its harmonic coefficients also matter.

**PROVEN — general upper bounds.**
\[
N(\epsilon)\le
\left\lceil\frac{A}{\epsilon^2\bar V}\right\rceil
\]
existentially, by Question 1.

A positive spherical \(t\)-design satisfies \(B_d=0\) for \(1\le d\le t\), and therefore
\[
\mathbb E_W\|QF_W-\mu(W)\|^2\le\sum_{d>t}a_d.
\]
The last bound is a tail bound, not a tail divided by \(N\).

Positive weighted \(t\)-designs with at most
\[
D_t=\binom{n+t-1}{t}+\binom{n+t-2}{t-1}
\]
points exist. Apply the convex-hull argument to a basis of restricted polynomials of degree at most \(t\); because the constant coordinate is fixed, at most \(D_t\) points suffice.

**PROVEN — exact polynomial cancellation costs many points.** Any rule exact through degree \(2s\) has
\[
N\ge D_s
=\binom{n+s-1}{s}+\binom{n+s-2}{s-1}.
\]
Otherwise some nonzero restricted polynomial \(p\) of degree at most \(s\) vanishes at every node. Exactness applied to \(p^2\) would give
\[
0=Q(p^2)=\int p^2\,d\sigma>0,
\]
a contradiction. For fixed \(s\), the leading order is \(n^s/s!\).

This is a lower bound for polynomial exactness, not for fooling one network ensemble.

**PROVEN — a finite-width lower bound for positive oblivious rules.** Define
\[
k(t)=\mathbb E_W\langle g_W(u),g_W(v)\rangle,\qquad u\cdot v=t.
\]
Then
\[
k(t)=\sum_{r\ge0}b_rt^r,\qquad b_r\ge0,\qquad \sum_rb_r=1.
\]

To prove positivity, condition on the layers after the first. The two first-layer Gaussian preactivation vectors have coordinatewise correlation \(t\). Expand the remaining network as a vector-valued Gaussian Hermite series. The identity
\[
\mathbb E[H_\alpha(Z)H_\beta(Z')]
=\mathbf1_{\alpha=\beta}t^{|\alpha|}
\]
follows by expanding the joint Gaussian exponential generating function. Each coefficient of \(t^r\) is consequently a sum of squared Hermite coefficients. Averaging over the remaining weights preserves nonnegativity. He scaling gives \(k(1)=1\).

Let
\[
\tau_{2s}=\mathbb E(U\cdot V)^{2s}
=\frac{(2s-1)!!}{n(n+2)\cdots(n+2s-2)},\qquad
q=\mathbb E k(U\cdot V).
\]
Then \(A=m_n^2(1-q)\). With
\[
M_r(Q)=\int u^{\otimes r}\,dQ(u),
\]
expanding the kernel gives
\[
\mathbb E_W\|QF_W-\mu\|^2
=m_n^2\sum_rb_r\|M_r(Q)-M_r(\sigma)\|_F^2.
\]

For even \(r=2s\), the squared norm on the right is
\[
\sum_{i,j}w_iw_j(u_i\cdot u_j)^{2s}-\tau_{2s}.
\]
With positive weights, off-diagonal terms are nonnegative and
\(\sum_iw_i^2\ge1/N\). Therefore
\[
\boxed{
\mathbb E_W\|QF_W-\mu\|^2
\ge \frac{m_n^2}{2N}
\sum_{\tau_{2s}\le1/(2N)}b_{2s}.
}
\]
This supplies the implicit necessary condition
\[
N\ge
\frac{m_n^2}{2\epsilon^2\bar V}
\sum_{\tau_{2s}\le1/(2N)}b_{2s}.
\]

The argument does not cover signed weights or weight-adapted nodes.

**PROVEN — antipodes have a precise cost.** Use \(M\) independent uniform directions and both signs, so \(N=2M\). Odd harmonics cancel exactly. The remaining estimator is MC on the even part, giving
\[
\mathbb E\|\widehat\mu-\mu\|^2
=\frac{2}{N}\sum_{\substack{d\ge2\\d\ {\rm even}}}a_d.
\]
Thus its gain over radius-exact MC is
\[
\frac{A}{2A_{\rm even}}.
\]
It helps precisely when the even share is below one half. This formula concerns independent antipodal pairs; additional relations between pairs can cancel even degrees too.

**PROVEN — OU sensitivity gives a softened Hermite tail.** Let \(H_k(W)\) denote total Gaussian Hermite energy of \(f_W\) in degree \(k\). With \(\rho=1-\delta\),
\[
\operatorname{NS}_W(\delta)
=\frac1{V(W)}\sum_{k\ge1}(1-\rho^k)H_k(W).
\]
This follows from the same Hermite correlation identity.

Writing \(T_H(t)=\sum_{k>t}H_k\), one obtains
\[
\frac{T_H(t)}V
\le \frac{\operatorname{NS}(\delta)}{1-\rho^{t+1}}.
\]
A useful two-scale lower bound is
\[
\frac{T_H(t)}V\ge
\left[
(1+\rho^{-t})\operatorname{NS}(1-\rho)
-\rho^{-t}\operatorname{NS}(1-\rho^2)
\right]_+.
\]
Indeed, the coefficient of \(H_k/V\) in the bracket is
\[
(1-\rho^k)(1-\rho^{k-t}),
\]
which is nonpositive for \(k\le t\), and between zero and one for \(k>t\).

Also,
\[
(1-e^{-1})\min\{1,k\delta\}
\le1-(1-\delta)^k
\le\min\{1,k\delta\}.
\]
The upper bound is the union/Bernoulli inequality; the lower uses
\((1-\delta)^k\le e^{-k\delta}\).

There is no two-sided constant-factor comparison with a sharp tail at \(t\asymp1/\delta\) without extra assumptions. A purely linear function has zero tail beyond degree one and positive noise sensitivity.

**PROVEN — Gaussian and spherical degrees must not be identified.** The homogeneous extension of a degree-\(d\) spherical harmonic is \(rY_d(u)\). Its Gaussian Hermite expansion occupies degrees
\[
d,d+2,d+4,\ldots,
\]
because Gaussian polynomials decompose into spherical harmonics times radial polynomials. Different angular degrees remain orthogonal. Consequently,
\[
\sum_{d>t}E_d(W)\le\frac{m_n^2}{n}T_H(t).
\]
The factor follows from
\(\mathbb E R^2/m_n^2=n/m_n^2\).

A reverse hard-tail comparison fails: a constant angular function has no nonconstant spherical harmonics, whereas its homogeneous extension \(r\) has nonzero Gaussian Hermite degrees of arbitrarily high even order. Spherical heat noise, with multipliers \(e^{-s d(d+n-2)}\), is the directly diagonal noise operator for spherical harmonics.

**PROVEN — useful finite-width smoothness bounds.**
\[
\mathbb E_W\sum_{k\ge1}kH_k(W)=n,
\qquad
\sum_{d\ge1}d(d+n-2)a_d=m_n^2(n-1).
\]
For the first identity, conditional on a layer input \(h\) and tangent vector \(v\), row symmetry gives
\[
\mathbb E_w\big[\mathbf1_{w\cdot h>0}(w\cdot v)^2\big]
=\frac{\|v\|^2}{n}.
\]
Summing the \(n\) rows preserves squared tangent norm. Iterating and summing over input coordinate directions gives
\(\mathbb E\|J_f\|_F^2=n\). Gaussian differentiation multiplies degree-\(k\) Hermite energy by \(k\).

For the second identity, homogeneity decomposes the Jacobian energy on the sphere into
\[
\|g\|^2+\|\nabla_Sg\|_F^2.
\]
The first term has ensemble expectation one; the total has expectation \(n\). Spherical harmonic degree \(d\) has Laplacian eigenvalue \(d(d+n-2)\), proving the formula. Hence
\[
\sum_{d>t}a_d
\le\frac{m_n^2(n-1)}{(t+1)(t+n-1)}.
\]

These bounds alone do not make high-strength designs affordable.

**PROVEN UNDER the infinite-width kernel model — the limiting low-degree picture differs from the finite-width problem.** In that model,
\[
K_L=\kappa^{\circ L},\qquad
\kappa(t)=\frac{\sqrt{1-t^2}+(\pi-\arccos t)t}{\pi}.
\]
For an angle \(\theta\),
\[
\arccos\kappa(\cos\theta)
=\theta-\frac{\theta^2}{3\pi}+O(\theta^3).
\]
Taking reciprocals and summing gives
\[
\theta_L=\frac{3\pi}{L}+O\!\left(\frac{\log L}{L^2}\right),\qquad
1-K_L(t)\sim\frac{9\pi^2}{2L^2}
\]
for fixed \(t<1\).

Moreover,
\[
K_L'(t)=\prod_{j<L}\left(1-\frac{\theta_j}{\pi}\right)
=\Theta_t(L^{-3}).
\]
The logarithm of the product is \(-3\log L+O(1)\). Higher fixed derivatives are \(O(L^{-3})\) on compact subsets of \((-1,1)\): differentiating the recurrence gives the same homogeneous multiplier; a term involving \(p\ge2\) factors of earlier derivatives is \(O(L^{-p-3})\), whose contribution after division by the \(L^{-3}\) homogeneous solution is summable.

Thus fixed positive power degrees carry \(O(L^{-3})\), against total nonconstant power mass \(\Theta(L^{-2})\). Since
\[
K_L(-1)=K_{L-1}(0),
\]
the even positive-degree power mass is
\[
\frac{1+K_L(-1)}2-K_L(0)
\sim\frac12[1-K_L(0)].
\]
The odd mass has the same asymptotic value.

For the auxiliary mean-field kernel with input dimension \(n\) and \(L=\alpha n\), concentration of \(U\cdot V\) near zero and the derivative bounds imply that spherical degrees one and two have share \(O(1/L)\). The even tail beyond any fixed degree retains asymptotically half the angular variance. The positive-rule bound therefore gives the approximately \(4\times\) ceiling over radius-exact MC for polynomial \(N\).

This is a statement about the mean-field kernel model. It is not a uniform finite-width approximation at \(L=\alpha n\).

**HEURISTIC — finite-width evidence.** The cited reports give a degree-\(1+2\) angular share of \(0.30\)–\(0.43\) at \(256\times32\), and an even input-variance share near \(0.46\). These support moderate constant-factor opportunities. They do not establish an asymptotic ceiling or the finite-width power coefficients needed for a certified lower bound.

## 3. Bounded independence

**PROVEN — independence across coordinates is not independence across samples.** Pairwise independence of entire Gaussian input vectors gives MC’s variance calculation. A single input whose coordinates are merely \(k\)-wise Gaussian need not have the correct expectation under a nonlinear network.

A degree-\((k-1)\) polynomial over \(\mathrm{GF}(q)\), evaluated at distinct coordinate indices, supplies \(k\)-wise independent uniform field elements. Quantile decoding supplies \(k\)-wise independent discretised Gaussian coordinates, not exact continuous Gaussians.

**PROVEN — exact \(k\)-wise Gaussian coordinates match every polynomial of total degree at most \(k\).** Each monomial of total degree at most \(k\) involves at most \(k\) distinct coordinates. Its expectation is therefore the Gaussian one; linearity handles the polynomial.

This does not control a Gaussian \(L^2\) approximation residual under another, potentially singular distribution. A valid sufficient condition is a pointwise polynomial sandwich:
\[
p_-\le f\le p_+,\qquad
\deg p_\pm\le k,\qquad
\mathbb E_\gamma(p_+-p_-)\le\eta.
\]
Matching their expectations immediately bounds the integration error by \(\eta\). No such low-degree sandwich for the stated deep random-net ensemble has been established here.

**PROVEN — even high coordinate independence can fail for a small homogeneous ReLU network.** Let \(m=128\). Draw independent Gaussian magnitudes \(|G_i|\), but draw their signs uniformly subject to
\[
\prod_{i=1}^{m}\operatorname{sign}(X_i)=+1.
\]
Add independent Gaussian coordinates through coordinate 256.

Every subset of at most 127 coordinates has exactly the independent Gaussian law: after fixing fewer than 128 constrained signs, at least one remaining sign can enforce parity, leaving the chosen signs uniform. Magnitudes remain independent.

Consider
\[
f(x)=\operatorname{relu}\!\left(
\prod_{i=1}^{m}\operatorname{sign}(x_i)\,
\min_{i\le m}|x_i|
\right).
\]
This is continuous and positively homogeneous. It has a width-256 ReLU implementation because
\[
\frac{|a+b|-|a-b|}{2}
=\operatorname{sign}(ab)\min\{|a|,|b|\}.
\]
Each binary combination uses four ReLUs to represent the two absolute values. A binary tree starts with 64 combinations, hence 256 units, and uses fewer units thereafter. Seven combination levels and a final ReLU suffice; nonnegative outputs can be copied through the remaining layers.

Under independent Gaussian inputs,
\[
\mathbb E_\gamma f=\frac12\mathbb E\min_{i\le m}|G_i|.
\]
Under the 127-wise independent distribution,
\[
\mathbb E f=\mathbb E\min_{i\le m}|G_i|.
\]
The expectation is wrong by a factor of two.

This is a worst-case counterexample within the architecture, not a lower bound for iid Gaussian weights.

**PROVEN — the natural matching object for homogeneous functions is**
\[
\nu_Q(B)=\mathbb E_Q[R\,\mathbf1_{\{U\in B\}}],
\qquad
\mathbb E_Q f=\int g(u)\,d\nu_Q(u).
\]
Gaussian inputs have \(\nu_\gamma=m_n\sigma\). Ordinary degree-\(d\) moments measure \(R^dU^{\otimes d}\); homogeneous integration requires \(RU^{\otimes d}\).

Thus Gaussian moment matching is sufficient under suitable approximation hypotheses, but is not the intrinsic target. Radius-exact spherical rules address the required measure directly.

**HEURISTIC:** For this lane, increasing coordinate independence is a less targeted route than cancelling measured angular modes. Its advantage would need a finite-width, ensemble-specific theorem or a measured error–cost improvement.

## 4. White-box structure

**PROVEN — first-layer alignment does not diagonalise all first-layer gates.** If
\[
W_1=U\Sigma V^\top,
\]
then \(x=Vy\) gives \(W_1x=U\Sigma y\); individual neurons still use rows of the dense matrix \(U\Sigma\). Similarly, polar alignment gives \(W_1x=Hy\), not a diagonal matrix.

Orthogonal changes preserve total spherical-harmonic energy in every degree. They can redistribute that energy between coordinate ANOVA components, which is relevant to Sobol projections.

**HEURISTIC:** Alignment helps when it concentrates important variation into a few well-stratified coordinate subsets. A first-layer singular basis is not automatically an effective basis for the final output. No growing-in-\(n\) benefit follows from first-layer isotropy or from the oblivious kernel bound.

**PROVEN — an adapted deterministic design need not be unbiased.** Already for \(W_1=I\), the radius-exact coordinate-axis rule gives, per output,
\[
\frac{m_n}{2n},
\]
whereas the Gaussian ReLU mean is \(1/\sqrt{2\pi}\). Selecting a basis using \(W\) removes the rotational averaging that justified an oblivious design’s ensemble calculation.

**PROVEN — an independent cube shift restores conditional unbiasedness while retaining a chosen alignment.** For fixed cube points \(p_i\), independent uniform
\(\Delta\in[0,1)^n\), and an orthogonal \(Q(W)\), set
\[
Z_{ij}=\Phi^{-1}((p_{ij}+\Delta_j)\bmod1),\qquad
U_i=Q(W)\frac{Z_i}{\|Z_i\|}.
\]
Conditional on \(W\), each \(Z_i\) is standard Gaussian and each \(U_i\) uniform on the sphere. Therefore averaging \(F_W(U_i)\) is unbiased.

An exact shift requires continuous randomness. A \(b\)-bit digital shift uses \(nb\) bits per replicate and is exact for its finite grid; discretisation bias remains. Haar rotation also restores unbiasedness, but multiplying an aligned design by a fresh full Haar rotation erases the alignment in distribution. Random signs or permutations alone do not generally make points spherical-uniform.

**PROVEN — first-layer controls have exact means.** For \(z_i=w_i^\top X\), \(X\sim N(0,I)\),
\[
\mathbb Ez_i=0,\qquad
\mathbb E|z_i|=\|w_i\|\sqrt{2/\pi},\qquad
\mathbb E\operatorname{relu}(z_i)=\frac{\|w_i\|}{\sqrt{2\pi}},
\]
\[
\mathbb E\|h_1\|^2=\frac12\|W_1\|_F^2,\qquad
\mathbb E[z^\top Cz]=\operatorname{tr}(CW_1W_1^\top).
\]
These follow respectively from symmetry, the one-dimensional normal absolute moment, and the covariance identity.

On the sphere, \(m_n\operatorname{relu}(w_i^\top U)\) has the same mean as its Gaussian counterpart, by homogeneity. Quadratic sphere means are their Gaussian means divided by \(n\).

For a vector of centered controls \(c\), fixed coefficients \(B\), and independent MC inputs,
\[
\widehat\mu=\frac1N\sum_i[F_W(U_i)-Bc(U_i)]
\]
is unbiased and has risk
\[
\frac1N\operatorname{tr}\operatorname{Var}(F_W-Bc).
\]
The optimal linear coefficients are
\[
B_*=\operatorname{Cov}(F_W,c)\operatorname{Cov}(c)^\dagger,
\]
obtained by completing the square in the quadratic residual variance.

Coefficients fitted on an independent pilot preserve conditional unbiasedness. Reusing the evaluation sample for fitting does not generally do so. For correlated point sets, variance reduction must be assessed using their integration covariance, not solely single-input regression error.

**HEURISTIC:** First-layer features are cheap to observe during a forward pass. A dense \(n\times n\) control readout nevertheless adds \(O(n^2)\) work per point, and estimating it can be pilot-limited. A low-rank readout is a reasonable cheaper experiment. A growing gain requires the unexplained variance to shrink with \(n\), not merely a nonzero explained share.

**PROVEN — multilevel prefix controls have an exact cost criterion.** For controls \(G_j\),
\[
\mathbb EF
=G_0+\sum_{j=1}^{J}\mathbb E(G_j-G_{j-1})
+\mathbb E(F-G_J),
\]
when \(G_0\) is constant. Independently estimate each difference, coupling its two terms on the same input. If its variance and cost are \(V_j,C_j\), the risk and cost are
\[
\sum_j\frac{V_j}{N_j},\qquad \sum_jC_jN_j.
\]
Cauchy–Schwarz gives
\[
\left(\sum_j\frac{V_j}{N_j}\right)\left(\sum_jC_jN_j\right)
\ge\left(\sum_j\sqrt{V_jC_j}\right)^2,
\]
with equality for \(N_j\propto\sqrt{V_j/C_j}\), before integer allocation.

**PROVEN UNDER**
\[
\mathbb E\|F-G_r\|^2\le C(1/r+n/L^2),\quad
C_r\asymp r/L,\quad L=\alpha n,\quad A=\Theta(1):
\]
dyadic levels yield an \(O(\log^2L/L)\) variance–cost product. Indeed, the variance of an increment between \(r\) and \(2r\) is at most twice the sum of their residual second moments, hence \(O(1/r)\); multiplying by cost \(O(r/L)\) gives \(O(1/L)\). There are \(O(\log L)\) levels. This proves a gain \(\Omega(L/\log^2L)\) under these hypotheses.

**HEURISTIC:** The cited measurements show that this asymptotic opportunity has not become an end-to-end advantage at \(256\times32\).

## 5. Gate surface area, gate changes, and output sensitivity

**PROVEN — the literal zero-set question needs a correction.** Almost surely \(W_1\) is invertible. The set
\[
\{x:W_1x<0\}
\]
is therefore a nonempty open cone. On it \(h_1=0\), and every later preactivation is identically zero. Thus, for \(\ell\ge2\), the full set \(\{z_{\ell,i}=0\}\) contains an open set and has infinite Gaussian-weighted \((n-1)\)-dimensional Hausdorff measure.

The useful objects are:

1. Fresh regular zero surfaces, inside regions where the preceding activation is nonzero.
2. The Gaussian perimeter of the gate set \(\{z_{\ell,i}>0\}\), including interfaces with dead regions.

For \(n\ge2\), define
\[
c_0=\frac1{\sqrt{2\pi}},\qquad
s_n=1-2^{-n},\qquad
\beta_n=1-(n+1)2^{-n}.
\]

**PROVEN — exact finite-width surface formulas.**
\[
\boxed{\mathbb E\,S_{\ell,i}^{\rm regular}=c_0\beta_n^{\ell-1}},
\qquad
\boxed{\mathbb E\,\operatorname{Per}_\gamma\{z_{\ell,i}>0\}
=c_0s_n^{\ell-1}}.
\]

Here is a proof that accounts for dead regions.

For a prefix map \(h\), Jacobian \(J\), and standard Gaussian row \(w\), Gaussian conditioning on \(w^\top h=0\) gives
\[
\mathbb E_w[\delta(w^\top h)\|J^\top w\|]
=\frac{1}{\sqrt{2\pi}\|h\|}
\mathbb E_G\|J^\top P_{h^\perp}G\|.
\]
Weight scaling cancels between the delta function and gradient. Matrices \(J^\top P_{h^\perp}\) and \(P_{h^\perp}J\) have the same nonzero singular values, so the last Gaussian norm can equally be written with \(P_{h^\perp}JV\).

For a fixed tangent perturbation \(v\), put
\[
q(h,v)=\frac{\|P_{h^\perp}v\|}{\|h\|}.
\]
After a fresh Gaussian ReLU layer, conditional on having \(K\) active coordinates,
\[
q_{\rm new}=q_{\rm old}\frac{\chi_{K-1}}{\chi_K},
\]
with independent chi variables, when \(K\ge2\). To derive this, decompose \(v\) into its component parallel to \(h\) and an orthogonal component. The Gaussian row projections of the orthogonal component are independent of the projections of \(h\). After restricting to active coordinates, projection away from the new activation removes one Gaussian direction.

For \(K=0,1\), the new projective derivative is zero. For \(K\ge2\),
\[
\mathbb E\chi_{K-1}\,\mathbb E\chi_K^{-1}
=
\frac{\sqrt2\,\Gamma(K/2)}{\Gamma((K-1)/2)}
\frac{\Gamma((K-1)/2)}{\sqrt2\,\Gamma(K/2)}
=1.
\]
Since \(K\sim\operatorname{Bin}(n,1/2)\),
\[
\mathbb E[q_{\rm new}\mid h,v]=\beta_n q_{\rm old}.
\]
Initially, with independent \(X,V\sim N(0,I_n)\),
\[
\mathbb E\frac{\|P_{X^\perp}V\|}{\|X\|}
=\mathbb E\chi_{n-1}\,\mathbb E\chi_n^{-1}=1.
\]
Integrating the conditional surface formula proves the regular-surface identity.

Next consider a newly created boundary of a dead region at layer \(j\). One of its \(n\) preactivations is zero and all other \(n-1\) are negative. Independence of those rows makes its expected area
\[
D_j=n\,2^{-(n-1)}c_0\beta_n^{j-1}.
\]
On the live side near such a facet, \(h_j\) lies on one positive coordinate ray. Each subsequent full layer preserves a nonzero ray with probability \(s_n\); a specified final preactivation is positive with probability \(1/2\). Its contribution to the gate perimeter at layer \(\ell>j\) is therefore
\[
\frac12s_n^{\ell-j-1}D_j.
\]
Adding fresh and inherited surfaces gives
\[
c_0\left[
\beta_n^{\ell-1}
+n2^{-n}\sum_{j=1}^{\ell-1}
\beta_n^{j-1}s_n^{\ell-j-1}
\right]
=c_0s_n^{\ell-1},
\]
because \(s_n-\beta_n=n2^{-n}\). Apart from inherited dead-region interfaces, distinct random facets intersect only in codimension at least two, so they do not add perimeter corrections.

**PROVEN — summed perimeter is approximately linear in neuron count and depth.**
\[
\mathbb E\sum_i\operatorname{Per}_\gamma\{z_{\ell,i}>0\}
=nc_0s_n^{\ell-1},
\]
and summing through layer \(\ell\) gives
\[
nc_0\sum_{j=0}^{\ell-1}s_n^j.
\]
At \(n=256,\ell=32\), the correction from replacing \(s_n^j,\beta_n^j\) by one is negligible.

**PROVEN UNDER the infinite-width kernel model — the corresponding per-neuron regular surface area is \(c_0\).** The kernel satisfies \(K(1)=K'(1)=1\), since \(\kappa'(1)=1\). Thus the variance and local tangential derivative variance used in the preceding Gaussian surface calculation are unchanged. This also agrees with the finite-width formulas as \(n\to\infty\).

**PROVEN — gate-pattern disagreement has a square-root small-noise scale.** Put \(\theta=\arccos\rho\). Along the Gaussian rotation path
\[
X_t=X\cos t+Z\sin t,
\]
\(X_t\) and \(X_t'\) are independent standard Gaussians. Expected boundary crossings per unit \(t\) equal
\[
\sqrt{2/\pi}\,\operatorname{Per}_\gamma.
\]
This follows by conditioning on a boundary point: the expected absolute normal velocity is \(\mathbb E|N(0,1)|=\sqrt{2/\pi}\). Endpoint disagreement is bounded by the number of crossings. Hence
\[
\mathbb P(g_{\ell,i}(X)\ne g_{\ell,i}(Y))
\le\frac{\theta}{\pi}s_n^{\ell-1}.
\]

For fixed finite \(n,\ell\), multiple-boundary crossings are lower order as \(\delta\downarrow0\), so
\[
\mathbb P(g_{\ell,i}(X)\ne g_{\ell,i}(Y))
\sim\frac{\sqrt2}{\pi}s_n^{\ell-1}\sqrt\delta.
\]

For the complete gate history, count each fresh surface once; inherited surfaces already belong to earlier gate boundaries. Thus
\[
\mathbb P(\text{history through }\ell\text{ changes})
\le
\min\left\{1,\frac{n\theta}{\pi}
\sum_{j=0}^{\ell-1}\beta_n^j\right\},
\]
and its small-\(\delta\) asymptotic is
\[
\frac{\sqrt2\,n}{\pi}
\left(\sum_{j=0}^{\ell-1}\beta_n^j\right)\sqrt\delta.
\]
The asymptotic takes \(\delta\to0\) at fixed \(n,\ell\); it is not a uniform order-one approximation.

A lower bound is the probability that the first-layer pattern changes:
\[
\mathbb E_{X,Y}\left[
1-\left(1-\frac{\angle(X,Y)}{\pi}\right)^n
\right].
\]
Conditional on \(X,Y\), independent first-layer rows disagree with probability \(\angle(X,Y)/\pi\), proving this expression.

**PROVEN — output sensitivity is qualitatively different.** The Jacobian identity from Question 2 gives
\[
\boxed{
\operatorname{NS}_{\rm ann}(\delta)
:=\frac{\mathbb E_{W,X,Y}\|f_W(X)-f_W(Y)\|^2}{2\bar V}
\le\frac{n}{\bar V}\delta,
}
\]
with asymptotic equality as \(\delta\downarrow0\). The bound uses
\(1-(1-\delta)^k\le k\delta\); the limit follows by dominated convergence using \(\sum k\,\mathbb EH_k=n\).

Thus gate history changes on a \(\sqrt\delta\) scale while output decorrelation starts linearly in \(\delta\). Counting gate changes does not price their output effect.

**PROVEN — kink strength, rather than bare surface area, controls a high-degree diagnostic.** For a fixed continuous piecewise-linear map, let
\[
J_{\rm kink}
=\sum_{\text{facets }S}
\int_S\|[J_f]\|_F^2\phi_n(x)\,d\mathcal H^{n-1}(x),
\]
where \([J_f]\) is the jump in the full output Jacobian.

A single facet is crossed with leading probability
\((2/\sqrt\pi)\sqrt\delta\) times its Gaussian area. Across it, the squared gradient change is \(\|[J_f]\|_F^2\). Intersections of distinct facets contribute lower-order terms. Therefore
\[
\frac12\mathbb E\|J_f(X)-J_f(Y)\|_F^2
\sim\frac{J_{\rm kink}}{\sqrt\pi}\sqrt\delta.
\]
On the other hand, differentiating Hermite polynomials gives exactly
\[
\frac12\mathbb E\|J_f(X)-J_f(Y)\|_F^2
=\sum_{k\ge1}k[1-\rho^{k-1}]H_k.
\]
Taking \(\delta=1/t\), the multiplier for \(k>t\) is bounded below by a constant times \(t\). Hence
\[
\sum_{k>t}H_k=O(J_{\rm kink}t^{-3/2})
\]
for sufficiently large \(t\), for a fixed map with \(J_{\rm kink}>0\).

If \(D=\sum kH_k\) and \(F(\delta)=V\operatorname{NS}(\delta)\), the same identity says
\[
D-F'(\delta)\sim\frac{J_{\rm kink}}{\sqrt\pi}\sqrt\delta.
\]
Integrating,
\[
F(\delta)
=D\delta-\frac{2J_{\rm kink}}{3\sqrt\pi}\delta^{3/2}
+o(\delta^{3/2}).
\]

An unused hidden gate contributes no output Jacobian jump. Arbitrarily complicated unused subnetworks therefore cannot establish an output-fooling lower bound.

## 6. Worst-case PRGs

**UNVERIFIED literature guide.** I did not check the original papers in this sandbox.

- Meka–Zuckerman: halfspaces and polynomial threshold functions; the commonly quoted halfspace seed bound \(O(\log n+\log^2(1/\eta))\) concerns a specified discrete-input setting. I do not use it here as a Gaussian theorem.
- Kane: Gaussian PTF generators; a conservative remembered bound has the form
  \[
  r=O_d(\log n)\,\eta^{-O(d)}.
  \]
  Exact versions and stronger later bounds are **UNVERIFIED** here.
- Harsha–Klivans–Meka: intersections/polytopes and invariance, with regularity and distribution hypotheses that must be checked.
- O’Donnell–Servedio–Tan and Chattopadhyay–De–Servedio: I have not verified the relevant function class, assumptions, or quantitative seed bounds, so I will not assign them a theorem from memory.
- Hatami–Hoza–Tal–Tell: threshold-circuit results require checking circuit depth, size, input distribution, and whether the result is a PRG or a different derandomisation statement. No transfer is used here.

**PROVEN — individual origin halfspaces are already easy in a purely information-theoretic sense.** Choose \(M\) vectors on a moment curve,
\[
v_j=(1,t_j,\ldots,t_j^{n-1}),
\]
with distinct \(t_j\), and include both signs. A nonzero linear functional vanishes on at most \(n-1\) of the \(v_j\), because it gives a nonzero polynomial of degree at most \(n-1\). Every other antipodal pair contributes exactly one positive point.

Thus the \(N=2M\) point distribution fools every origin halfspace to error at most
\[
\frac{n-1}{N},
\]
relative to its Gaussian probability \(1/2\). Choosing \(N\) a power of two gives index seed
\[
r\le \left\lceil\log_2\frac{n-1}{\eta}\right\rceil+O(1).
\]
This says nothing about joint gate patterns or ReLU values.

**PROVEN — the first-layer cell is covered by an intersection theorem, but the whole output needs substantially more.** A specified first-layer pattern is an intersection of \(n\) origin halfspaces.

For a specified full gate pattern, every activation is a fixed linear function of \(x\). Its consistency region is an intersection of at most \(nL\) origin halfspaces. On that region, output coordinate \(j\) equals \(a_C^\top x\). Therefore
\[
\{f_j(x)>t\}
\]
is a union over feasible cells \(C\) of intersections of at most \(nL+1\) affine halfspaces. The crude cell count is \(M\le2^{nL}\).

Suppose a generator fools each such intersection to error \(\eta\). Since the cell pieces are disjoint, summing their errors bounds the output-threshold error by \(M\eta\).

For a clipped nonnegative output,
\[
\min(f_j,B)=\int_0^B\mathbf1_{\{f_j>t\}}\,dt.
\]
Integrating the threshold-error bound gives
\[
\left|\mathbb E_G\min(f_j,B)-\mathbb E_\gamma f_j\right|
\le BM\eta+\mathbb E_\gamma(f_j-B)_+.
\]
This explicitly exposes the accuracy and truncation requirements. It does not assume that an intersection PRG automatically fools the network.

**PROVEN — short existential support also does not imply a useful explicit PRG.** For a finite class of \(K\) functions taking values in \([0,1]\), \(N\) iid inputs satisfy
\[
\Pr\left(\max_f|\widehat{\mathbb E}f-\mathbb Ef|>\eta\right)
\le2K e^{-2N\eta^2}.
\]
For completeness, a variable in \([0,1]\) has tilted variance at most \(1/4\); integrating the second derivative of its log moment-generating function twice gives
\(\mathbb Ee^{\lambda(Z-\mathbb EZ)}\le e^{\lambda^2/8}\).
Chernoff optimisation gives the scalar bound, and a union bound gives the display.

Hence a fixed support of size \(O(\log K/\eta^2)\) exists. Its index length is only
\[
O(\log\log K+\log(1/\eta)).
\]
For quantised networks, \(K\) can be enormous while this seed remains short. Constructing the support efficiently is the missing issue.

**PROVEN — worst-case results are not categorically irrelevant to ARC.** A valid worst-case PRG covering these outputs with the required normalisation and efficient evaluation would give an average-case upper bound too. What is unsupported is the claim that the named results already meet ARC’s error–compute target.

A seed bound \(r\) produces \(2^r\) evaluations when enumerated. Polynomial dependence on \(1/\eta\) in the seed can become exponential dependence in enumeration cost. “Short seed” is therefore not the needed performance criterion.

## 7. Verdict

**PROVEN:** The proposed implication
\[
\text{large gate-boundary mass or output sensitivity}
\Longrightarrow
\text{many necessary runtime random bits}
\]
fails under the ensemble-average MSE criterion. A fixed oblivious design already matches radius-exact MC existentially.

**PROVEN:** The randomness framing nevertheless supplies useful distinctions and tests:

- Conditional unbiasedness differs from ensemble accuracy.
- Coordinate independence differs from independence between samples.
- Positive oblivious rules have an exact kernel risk and a finite-width even-tail lower bound.
- Gate perimeter and output-weighted kink strength are different observables.
- A generator’s index length must be converted into construction and enumeration cost.

**HEURISTIC:** These distinctions sharpen “precision per compute”; they do not currently establish a new computational obstruction to ARC’s goal. The most useful new geometric fact here is that expected per-neuron gate perimeter stays approximately constant, while continuity makes the output substantially more noise-stable than its gate history.

## Single strongest defensible statement

**PROVEN:**
For every finite \(n,L,N\), there exists a deterministic, weight-independent, positive equal-weight \(N\)-point spherical rule such that
\[
\boxed{
\mathbb E_W\|\widehat\mu(W)-\mu(W)\|^2
\le\frac{A}{N}\le\frac{\bar V}{N}.
}
\]
The proof is the averaging argument in Question 1.

Therefore neither noise sensitivity nor gate-boundary mass can force a positive runtime-randomness budget for ARC’s stated average-risk target. The unresolved restriction is efficient, explicitly describable construction, together with ARC’s exclusion of sampling-style representations.

## Single most promising structured-sampling route at \(256\times32\)

**HEURISTIC — recommendation:** Use complete antipodal Kerdock blocks with exact radius, and independent rotations for conditional error measurement. Charge rotation setup and all evaluations. This has direct prior evidence and an exact geometric prediction.

**PROVEN UNDER the mutually unbiased basis property of the supplied construction:** With \(K=n/2+1=129\) bases, the antipodal set has
\[
M=2Kn=66{,}048
\]
points and is a spherical 5-design.

For proof, the traceless projectors
\(u_{b,j}u_{b,j}^\top-I/n\) from different bases are orthogonal. Each basis spans an \((n-1)\)-dimensional diagonal traceless subspace, and
\[
K(n-1)=\dim\operatorname{Sym}_0(n).
\]
Applying the resulting orthogonal decomposition to
\(xx^\top-\|x\|^2I/n\) gives
\[
\sum_{b,j}(u_{b,j}^\top x)^4=\frac32\|x\|^4.
\]
Dividing by \(Kn=n(n+2)/2\) gives the sphere’s fourth moment
\(3\|x\|^4/[n(n+2)]\). The second moment follows from each orthonormal basis; antipodes cancel odd moments through degree five.

**PROVEN — its residual risk is explicitly testable.** Odd \(B_d\) vanish, and for even \(d\),
\[
B_d=
\frac1{Kn}
+\frac{n-1}{Kn}P_d^{(n)}(0)
+\frac{K-1}{K}P_d^{(n)}(n^{-1/2}).
\]
This follows by counting, relative to one node, its antipode, the orthogonal nodes in its basis, and the mutually unbiased nodes in other bases. In particular, \(B_2=B_4=0\).

Thus one rotated block has ensemble risk
\[
R_{\rm block}=\sum_{\substack{d\ge6\\d\ {\rm even}}}a_dB_d.
\]
Averaging \(B\) independent rotated blocks gives exactly \(R_{\rm block}/B\). Fixed orientation has the same ensemble risk.

Replacing independent radial randomisation by the exact factor \(m_n\) is conditional expectation given the directions, so it cannot increase MSE when the original radii have conditional mean \(m_n\).

**CONJECTURE — falsifiable numerical prediction:** On fresh noiseless \(256\times32\) nets, at \(N=M,2M,4M\), the pooled error constant will satisfy
\[
\frac{N\,\mathbb E\|\widehat\mu-\mu\|^2}{\bar V}
\in[0.33,0.50],
\]
corresponding to a \(2\)–\(3\times\) gain over plain MC. This extrapolates the cited noisy experiment; it is not implied by 5-design exactness. A reliably estimated constant above \(0.50\) falsifies the prediction.

## Measurements that most efficiently test these claims

The following are proposed tests, not completed \(256\times32\) experiments.

1. **Ensemble risk with independent truth estimates.** Pool squared errors and variances separately, matching \(\mathbb E_W\mathrm{error}^2/\bar V\). With independent unbiased truths \(\mu_1,\mu_2\), use
   \[
   (\widehat\mu-\mu_1)^\top(\widehat\mu-\mu_2)
   \]
   to avoid adding reference variance to estimated squared error.

2. **Kerdock’s exact error constant.** Compare full blocks with exact radius, full blocks with the old radial treatment, radius-exact MC, and scrambled Sobol. Use \(66{,}048\) and integer multiples; partial blocks do not retain full degree-five exactness.

3. **The geometry-specific kernel contrasts.** Estimate \(k(-1),k(0),k(\pm1/\sqrt n)\), and \(q\), with \(k(1)=1\). They determine Kerdock risk directly. Use shared randomness or direct block contrasts to avoid subtracting independently estimated quantities close to one.

4. **Parity and low-degree energy.** Measure angular degrees \(1,2,4\), total even energy, and the residual after removing those degrees. Keep spherical energies distinct from Gaussian Hermite energies and power-series coefficients.

5. **Gate crossings versus output change on the same pairs.** Sweep small \(\delta\); measure per-neuron disagreement, full-history disagreement, output squared change, and gradient squared change. Test the \(\sqrt\delta\), \(\delta\), and weighted-kink predictions separately. Small widths are useful for resolving the \(s_n\) versus \(\beta_n\) factors.

6. **Whole-input pairwise independence versus coordinate-wise independence.** Use the same finite Gaussian grid and charge generation cost. The former should reproduce MC’s grid-target variance; the latter has no such guarantee.

7. **Aligned controls with independent pilots.** Before a large integration run, estimate the residual variance–cost product for shifted Sobol in the original, polar, and singular-vector bases, with and without first-layer controls. Include pilot and fitting cost. A favorable regression fit alone is insufficient.
tokens used
76,778
**PROVEN:** ARC’s ensemble-average MSE criterion alone cannot force a positive random-bit budget: a suitable fixed, weight-independent \(N\)-point rule achieves the average risk of \(N\)-sample radius-exact MC. Finding and representing that rule efficiently remains a computational problem.

I read only `coprover/STATEMENT_r1.md` within this lane, the cited reports, and permitted code. No files were modified. Reported experiments below are evidence, not mathematical guarantees; unchecked literature is marked **UNVERIFIED**.

## 1. Formalising randomness complexity

Write
\[
F_W(u)=m_n f_W(u),\qquad u\in S^{n-1},
\]
where evaluating \(f_W\) on the sphere means evaluating \(g_W\). Define
\[
A(W)=\operatorname{tr}\operatorname{Var}_u F_W(u),\quad
A=\mathbb E_W A(W),\quad
\bar V=\mathbb E_W V(W).
\]

An appropriate complexity specification includes:

- \(R\): fresh random bits used at run time.
- \(T\): construction, preprocessing, point generation, network evaluation, and aggregation cost.
- \(D\): stored advice or point-set description length.
- Numerical precision, including the representation of weights and points.

The three risks are:

\[
\mathcal R_{\rm obl}(Q)
=\frac{\mathbb E_{W,S}\|Q_S(F_W)-\mu(W)\|^2}{\bar V},
\]
for weight-independent rules;

\[
\mathcal R_{\rm wb}(B)
=\frac{\mathbb E_{W,S}\|B(W,S)-\mu(W)\|^2}{\bar V},
\]
for algorithms reading \(W\); and, for example,
\[
\mathcal R_{\rm worst}(B)
=\sup_{W\in\mathcal C:V(W)>0}
\frac{\mathbb E_S\|B(W,S)-\mu(W)\|^2}{V(W)}.
\]

The worst-case model must separately specify whether weight adaptation is allowed.

**PROVEN — support size, seed length, and runtime randomness are different quantities.** A generator indexed by a uniform \(r\)-bit string has at most \(2^r\) outputs. Enumerating all its outputs uses zero runtime random bits and up to \(2^r\) evaluations. Thus \(r=\log_2 N\) describes an index into an equal-weight support, not the randomness used by the enumerating estimator. Arbitrary weighted rules need an additional description of their weights.

**PROVEN — nonuniform derandomisation already works in the oblivious model.** Let \(U_1,\ldots,U_N\) be independent uniform directions. Conditional on \(W\),
\[
\mathbb E_U\left\|\frac1N\sum_iF_W(U_i)-\mu(W)\right\|^2
=\frac{A(W)}N.
\]
To see this, expand the squared norm: each diagonal term contributes \(A(W)\), and every off-diagonal term vanishes by independence and centering. Averaging over \(W\) gives \(A/N\). Consequently, at least one fixed tuple \((u_1,\ldots,u_N)\), independent of \(W\), has ensemble risk at most \(A/N\).

Moreover,
\[
V(W)=A(W)+(n-m_n^2)\mathbb E_u\|g_W(u)\|^2\ge A(W).
\]
This follows by writing \(X=RU\), with \(R,U\) independent, and applying total variance to \(Rg_W(U)\). Hence \(N\ge\epsilon^{-2}\) suffices for an existential deterministic rule.

This proof gives neither an efficient construction nor a short description of its coordinates.

**PROVEN UNDER exact factorisation, probability-transform, and digit-splitting primitives — white-box derandomisation can also be uniform.** Write
\[
W_1=H Q,\qquad H=(W_1W_1^\top)^{1/2}.
\]
Right orthogonal invariance of a Gaussian matrix implies that \(Q\) is Haar and independent of \(H\). The remaining layers are also independent of \(Q\). Input rotation preserves \(\mu\), \(V\), and \(A\).

Under the stated primitives, the nonatomic Haar variable supplies independent uniform bits. These can generate samples for the canonical network with first layer \(H\). For simulation of an arbitrary randomised algorithm, split them into an independent Haar \(Q'\) and algorithmic seed \(S\); run the algorithm on first layer \(HQ'\). This reconstructed network has the original distribution, the seed is independent of it, and its mean equals the original network’s mean. Therefore its average risk is unchanged.

The factorisation costs \(O(n^3)\); exact random-variable transformations are part of the hypothesis. Finite-precision weights do not provide an unlimited source of independent bits.

**PROVEN — the same seed-fixing argument does not preserve a worst-case guarantee.** In general,
\[
\sup_W\mathbb E_S L(W,S)
\ne
\mathbb E_S\sup_W L(W,S).
\]
For example, two instances and two seeds can have loss matrix
\[
\begin{pmatrix}0&1\\1&0\end{pmatrix}.
\]
A uniform seed has worst-case expected loss \(1/2\), whereas either fixed seed has worst-case loss \(1\). Additional class structure is needed to fix a seed uniformly.

**PROVEN — fresh randomness buys conditional unbiasedness and observable replication variance.** If \(Z_1,Z_2\) are independent, conditionally unbiased estimates of \(\mu(W)\), with equal conditional risk \(v(W)\), then
\[
\mathbb E\!\left[\frac{\|Z_1-Z_2\|^2}{2}\,\middle|\,W\right]=v(W).
\]
Expand \(Z_1-Z_2=(Z_1-\mu)-(Z_2-\mu)\); independence and centering eliminate the cross term.

This is an unbiased variance estimate, not automatically a valid confidence interval. Reliable coverage additionally needs a concentration argument, a known bound, or appropriate moment assumptions. Fixing the seed preserves an ensemble-risk statement but removes this conditional replication experiment.

**PROVEN — few bits suffice for MC’s variance calculation on a finite input grid.** Suppose each coordinate uses \(s\) bits, so an entire input has \(ns\) bits. Choose
\[
b\ge \max\{ns,\lceil\log_2 N\rceil\}.
\]
For distinct \(t_i\in\mathrm{GF}(2^b)\), draw uniform \(a,c\) and set
\[
Y_i=at_i+c.
\]
For \(i\ne j\), the map \((a,c)\mapsto(Y_i,Y_j)\) is invertible. Thus the \(Y_i\) are pairwise independent and uniform. Decode \(ns\) bits into the coordinate grid and apply coordinatewise quantile transforms.

This uses \(2b\) random bits and gives exactly the MC variance \(V_{\rm grid}/N\) for the discretised target. Degree-three polynomials give four-wise independence with \(4b\) bits. Exact continuous Gaussian sampling requires an unbounded bit stream; the grid bias must be accounted for separately.

Pairwise independence also makes the usual sample variance unbiased. It does not by itself make that variance estimate concentrate.

**PROVEN — Carathéodory’s observation is correct but computationally incomplete.** The continuous image \(F_W(S^{n-1})\subset\mathbb R^n\) is compact, and its mean lies in its convex hull. Any convex representation using more than \(n+1\) points has an affine dependence. Adjust the coefficients along that dependence until one becomes zero, preserving their sum, nonnegativity, and represented vector. Repeating leaves at most \(n+1\) weighted points.

Finding those points can require essentially solving the original integration problem.

**HEURISTIC — corrected hypothesis.** The useful question is whether an explicit, inexpensive rule exploits the output’s structure well enough to improve error per compute. Output noise sensitivity can help describe that structure. It cannot, by itself, establish a runtime-randomness lower bound under ARC’s ensemble criterion.

## 2. Black-box designs and point-count bounds

Let
\[
F_W=\sum_{d\ge0}F_{W,d}
\]
be its spherical-harmonic expansion, and put
\[
E_d(W)=\|F_{W,d}\|_{L^2(\sigma)}^2,\qquad
a_d=\mathbb E_WE_d(W).
\]
Then \(A=\sum_{d\ge1}a_d\).

Let \(P_d^{(n)}\) be the zonal harmonic normalised by \(P_d^{(n)}(1)=1\). For
\[
Q=\sum_{i=1}^Nw_i\delta_{u_i},\qquad \sum_iw_i=1,
\]
define
\[
B_d(Q)=\sum_{i,j}w_iw_jP_d^{(n)}(u_i\cdot u_j).
\]

**PROVEN — exact spectral pricing.**
\[
\boxed{\mathbb E_W\|QF_W-\mu(W)\|^2
=\sum_{d\ge1}a_dB_d(Q).}
\]
Also, for any fixed \(W\) and independent Haar rotation \(O\),
\[
\boxed{\mathbb E_O\|Q(F_W\circ O)-\mu(W)\|^2
=\sum_{d\ge1}E_d(W)B_d(Q).}
\]

For proof, choose an orthonormal basis \(Y_{d,r}\), \(1\le r\le h_d\), of degree-\(d\) harmonics. The addition formula is
\[
\sum_rY_{d,r}(u)Y_{d,r}(v)=h_dP_d^{(n)}(u\cdot v).
\]
Rotational averaging kills cross terms between different degrees and averages the coefficient covariance within degree \(d\) to \(E_d(W)I/h_d\). Substituting the addition formula gives the second identity. The Gaussian weight ensemble is input-rotation invariant, giving the first.

In particular, \(B_d\ge0\). For positive weights, \(B_d\le1\), since \(|P_d|\le1\).

A fixed net’s energy spectrum alone does not determine its error on an unrotated design: the orientations of its harmonic coefficients also matter.

**PROVEN — general upper bounds.**
\[
N(\epsilon)\le
\left\lceil\frac{A}{\epsilon^2\bar V}\right\rceil
\]
existentially, by Question 1.

A positive spherical \(t\)-design satisfies \(B_d=0\) for \(1\le d\le t\), and therefore
\[
\mathbb E_W\|QF_W-\mu(W)\|^2\le\sum_{d>t}a_d.
\]
The last bound is a tail bound, not a tail divided by \(N\).

Positive weighted \(t\)-designs with at most
\[
D_t=\binom{n+t-1}{t}+\binom{n+t-2}{t-1}
\]
points exist. Apply the convex-hull argument to a basis of restricted polynomials of degree at most \(t\); because the constant coordinate is fixed, at most \(D_t\) points suffice.

**PROVEN — exact polynomial cancellation costs many points.** Any rule exact through degree \(2s\) has
\[
N\ge D_s
=\binom{n+s-1}{s}+\binom{n+s-2}{s-1}.
\]
Otherwise some nonzero restricted polynomial \(p\) of degree at most \(s\) vanishes at every node. Exactness applied to \(p^2\) would give
\[
0=Q(p^2)=\int p^2\,d\sigma>0,
\]
a contradiction. For fixed \(s\), the leading order is \(n^s/s!\).

This is a lower bound for polynomial exactness, not for fooling one network ensemble.

**PROVEN — a finite-width lower bound for positive oblivious rules.** Define
\[
k(t)=\mathbb E_W\langle g_W(u),g_W(v)\rangle,\qquad u\cdot v=t.
\]
Then
\[
k(t)=\sum_{r\ge0}b_rt^r,\qquad b_r\ge0,\qquad \sum_rb_r=1.
\]

To prove positivity, condition on the layers after the first. The two first-layer Gaussian preactivation vectors have coordinatewise correlation \(t\). Expand the remaining network as a vector-valued Gaussian Hermite series. The identity
\[
\mathbb E[H_\alpha(Z)H_\beta(Z')]
=\mathbf1_{\alpha=\beta}t^{|\alpha|}
\]
follows by expanding the joint Gaussian exponential generating function. Each coefficient of \(t^r\) is consequently a sum of squared Hermite coefficients. Averaging over the remaining weights preserves nonnegativity. He scaling gives \(k(1)=1\).

Let
\[
\tau_{2s}=\mathbb E(U\cdot V)^{2s}
=\frac{(2s-1)!!}{n(n+2)\cdots(n+2s-2)},\qquad
q=\mathbb E k(U\cdot V).
\]
Then \(A=m_n^2(1-q)\). With
\[
M_r(Q)=\int u^{\otimes r}\,dQ(u),
\]
expanding the kernel gives
\[
\mathbb E_W\|QF_W-\mu\|^2
=m_n^2\sum_rb_r\|M_r(Q)-M_r(\sigma)\|_F^2.
\]

For even \(r=2s\), the squared norm on the right is
\[
\sum_{i,j}w_iw_j(u_i\cdot u_j)^{2s}-\tau_{2s}.
\]
With positive weights, off-diagonal terms are nonnegative and
\(\sum_iw_i^2\ge1/N\). Therefore
\[
\boxed{
\mathbb E_W\|QF_W-\mu\|^2
\ge \frac{m_n^2}{2N}
\sum_{\tau_{2s}\le1/(2N)}b_{2s}.
}
\]
This supplies the implicit necessary condition
\[
N\ge
\frac{m_n^2}{2\epsilon^2\bar V}
\sum_{\tau_{2s}\le1/(2N)}b_{2s}.
\]

The argument does not cover signed weights or weight-adapted nodes.

**PROVEN — antipodes have a precise cost.** Use \(M\) independent uniform directions and both signs, so \(N=2M\). Odd harmonics cancel exactly. The remaining estimator is MC on the even part, giving
\[
\mathbb E\|\widehat\mu-\mu\|^2
=\frac{2}{N}\sum_{\substack{d\ge2\\d\ {\rm even}}}a_d.
\]
Thus its gain over radius-exact MC is
\[
\frac{A}{2A_{\rm even}}.
\]
It helps precisely when the even share is below one half. This formula concerns independent antipodal pairs; additional relations between pairs can cancel even degrees too.

**PROVEN — OU sensitivity gives a softened Hermite tail.** Let \(H_k(W)\) denote total Gaussian Hermite energy of \(f_W\) in degree \(k\). With \(\rho=1-\delta\),
\[
\operatorname{NS}_W(\delta)
=\frac1{V(W)}\sum_{k\ge1}(1-\rho^k)H_k(W).
\]
This follows from the same Hermite correlation identity.

Writing \(T_H(t)=\sum_{k>t}H_k\), one obtains
\[
\frac{T_H(t)}V
\le \frac{\operatorname{NS}(\delta)}{1-\rho^{t+1}}.
\]
A useful two-scale lower bound is
\[
\frac{T_H(t)}V\ge
\left[
(1+\rho^{-t})\operatorname{NS}(1-\rho)
-\rho^{-t}\operatorname{NS}(1-\rho^2)
\right]_+.
\]
Indeed, the coefficient of \(H_k/V\) in the bracket is
\[
(1-\rho^k)(1-\rho^{k-t}),
\]
which is nonpositive for \(k\le t\), and between zero and one for \(k>t\).

Also,
\[
(1-e^{-1})\min\{1,k\delta\}
\le1-(1-\delta)^k
\le\min\{1,k\delta\}.
\]
The upper bound is the union/Bernoulli inequality; the lower uses
\((1-\delta)^k\le e^{-k\delta}\).

There is no two-sided constant-factor comparison with a sharp tail at \(t\asymp1/\delta\) without extra assumptions. A purely linear function has zero tail beyond degree one and positive noise sensitivity.

**PROVEN — Gaussian and spherical degrees must not be identified.** The homogeneous extension of a degree-\(d\) spherical harmonic is \(rY_d(u)\). Its Gaussian Hermite expansion occupies degrees
\[
d,d+2,d+4,\ldots,
\]
because Gaussian polynomials decompose into spherical harmonics times radial polynomials. Different angular degrees remain orthogonal. Consequently,
\[
\sum_{d>t}E_d(W)\le\frac{m_n^2}{n}T_H(t).
\]
The factor follows from
\(\mathbb E R^2/m_n^2=n/m_n^2\).

A reverse hard-tail comparison fails: a constant angular function has no nonconstant spherical harmonics, whereas its homogeneous extension \(r\) has nonzero Gaussian Hermite degrees of arbitrarily high even order. Spherical heat noise, with multipliers \(e^{-s d(d+n-2)}\), is the directly diagonal noise operator for spherical harmonics.

**PROVEN — useful finite-width smoothness bounds.**
\[
\mathbb E_W\sum_{k\ge1}kH_k(W)=n,
\qquad
\sum_{d\ge1}d(d+n-2)a_d=m_n^2(n-1).
\]
For the first identity, conditional on a layer input \(h\) and tangent vector \(v\), row symmetry gives
\[
\mathbb E_w\big[\mathbf1_{w\cdot h>0}(w\cdot v)^2\big]
=\frac{\|v\|^2}{n}.
\]
Summing the \(n\) rows preserves squared tangent norm. Iterating and summing over input coordinate directions gives
\(\mathbb E\|J_f\|_F^2=n\). Gaussian differentiation multiplies degree-\(k\) Hermite energy by \(k\).

For the second identity, homogeneity decomposes the Jacobian energy on the sphere into
\[
\|g\|^2+\|\nabla_Sg\|_F^2.
\]
The first term has ensemble expectation one; the total has expectation \(n\). Spherical harmonic degree \(d\) has Laplacian eigenvalue \(d(d+n-2)\), proving the formula. Hence
\[
\sum_{d>t}a_d
\le\frac{m_n^2(n-1)}{(t+1)(t+n-1)}.
\]

These bounds alone do not make high-strength designs affordable.

**PROVEN UNDER the infinite-width kernel model — the limiting low-degree picture differs from the finite-width problem.** In that model,
\[
K_L=\kappa^{\circ L},\qquad
\kappa(t)=\frac{\sqrt{1-t^2}+(\pi-\arccos t)t}{\pi}.
\]
For an angle \(\theta\),
\[
\arccos\kappa(\cos\theta)
=\theta-\frac{\theta^2}{3\pi}+O(\theta^3).
\]
Taking reciprocals and summing gives
\[
\theta_L=\frac{3\pi}{L}+O\!\left(\frac{\log L}{L^2}\right),\qquad
1-K_L(t)\sim\frac{9\pi^2}{2L^2}
\]
for fixed \(t<1\).

Moreover,
\[
K_L'(t)=\prod_{j<L}\left(1-\frac{\theta_j}{\pi}\right)
=\Theta_t(L^{-3}).
\]
The logarithm of the product is \(-3\log L+O(1)\). Higher fixed derivatives are \(O(L^{-3})\) on compact subsets of \((-1,1)\): differentiating the recurrence gives the same homogeneous multiplier; a term involving \(p\ge2\) factors of earlier derivatives is \(O(L^{-p-3})\), whose contribution after division by the \(L^{-3}\) homogeneous solution is summable.

Thus fixed positive power degrees carry \(O(L^{-3})\), against total nonconstant power mass \(\Theta(L^{-2})\). Since
\[
K_L(-1)=K_{L-1}(0),
\]
the even positive-degree power mass is
\[
\frac{1+K_L(-1)}2-K_L(0)
\sim\frac12[1-K_L(0)].
\]
The odd mass has the same asymptotic value.

For the auxiliary mean-field kernel with input dimension \(n\) and \(L=\alpha n\), concentration of \(U\cdot V\) near zero and the derivative bounds imply that spherical degrees one and two have share \(O(1/L)\). The even tail beyond any fixed degree retains asymptotically half the angular variance. The positive-rule bound therefore gives the approximately \(4\times\) ceiling over radius-exact MC for polynomial \(N\).

This is a statement about the mean-field kernel model. It is not a uniform finite-width approximation at \(L=\alpha n\).

**HEURISTIC — finite-width evidence.** The cited reports give a degree-\(1+2\) angular share of \(0.30\)–\(0.43\) at \(256\times32\), and an even input-variance share near \(0.46\). These support moderate constant-factor opportunities. They do not establish an asymptotic ceiling or the finite-width power coefficients needed for a certified lower bound.

## 3. Bounded independence

**PROVEN — independence across coordinates is not independence across samples.** Pairwise independence of entire Gaussian input vectors gives MC’s variance calculation. A single input whose coordinates are merely \(k\)-wise Gaussian need not have the correct expectation under a nonlinear network.

A degree-\((k-1)\) polynomial over \(\mathrm{GF}(q)\), evaluated at distinct coordinate indices, supplies \(k\)-wise independent uniform field elements. Quantile decoding supplies \(k\)-wise independent discretised Gaussian coordinates, not exact continuous Gaussians.

**PROVEN — exact \(k\)-wise Gaussian coordinates match every polynomial of total degree at most \(k\).** Each monomial of total degree at most \(k\) involves at most \(k\) distinct coordinates. Its expectation is therefore the Gaussian one; linearity handles the polynomial.

This does not control a Gaussian \(L^2\) approximation residual under another, potentially singular distribution. A valid sufficient condition is a pointwise polynomial sandwich:
\[
p_-\le f\le p_+,\qquad
\deg p_\pm\le k,\qquad
\mathbb E_\gamma(p_+-p_-)\le\eta.
\]
Matching their expectations immediately bounds the integration error by \(\eta\). No such low-degree sandwich for the stated deep random-net ensemble has been established here.

**PROVEN — even high coordinate independence can fail for a small homogeneous ReLU network.** Let \(m=128\). Draw independent Gaussian magnitudes \(|G_i|\), but draw their signs uniformly subject to
\[
\prod_{i=1}^{m}\operatorname{sign}(X_i)=+1.
\]
Add independent Gaussian coordinates through coordinate 256.

Every subset of at most 127 coordinates has exactly the independent Gaussian law: after fixing fewer than 128 constrained signs, at least one remaining sign can enforce parity, leaving the chosen signs uniform. Magnitudes remain independent.

Consider
\[
f(x)=\operatorname{relu}\!\left(
\prod_{i=1}^{m}\operatorname{sign}(x_i)\,
\min_{i\le m}|x_i|
\right).
\]
This is continuous and positively homogeneous. It has a width-256 ReLU implementation because
\[
\frac{|a+b|-|a-b|}{2}
=\operatorname{sign}(ab)\min\{|a|,|b|\}.
\]
Each binary combination uses four ReLUs to represent the two absolute values. A binary tree starts with 64 combinations, hence 256 units, and uses fewer units thereafter. Seven combination levels and a final ReLU suffice; nonnegative outputs can be copied through the remaining layers.

Under independent Gaussian inputs,
\[
\mathbb E_\gamma f=\frac12\mathbb E\min_{i\le m}|G_i|.
\]
Under the 127-wise independent distribution,
\[
\mathbb E f=\mathbb E\min_{i\le m}|G_i|.
\]
The expectation is wrong by a factor of two.

This is a worst-case counterexample within the architecture, not a lower bound for iid Gaussian weights.

**PROVEN — the natural matching object for homogeneous functions is**
\[
\nu_Q(B)=\mathbb E_Q[R\,\mathbf1_{\{U\in B\}}],
\qquad
\mathbb E_Q f=\int g(u)\,d\nu_Q(u).
\]
Gaussian inputs have \(\nu_\gamma=m_n\sigma\). Ordinary degree-\(d\) moments measure \(R^dU^{\otimes d}\); homogeneous integration requires \(RU^{\otimes d}\).

Thus Gaussian moment matching is sufficient under suitable approximation hypotheses, but is not the intrinsic target. Radius-exact spherical rules address the required measure directly.

**HEURISTIC:** For this lane, increasing coordinate independence is a less targeted route than cancelling measured angular modes. Its advantage would need a finite-width, ensemble-specific theorem or a measured error–cost improvement.

## 4. White-box structure

**PROVEN — first-layer alignment does not diagonalise all first-layer gates.** If
\[
W_1=U\Sigma V^\top,
\]
then \(x=Vy\) gives \(W_1x=U\Sigma y\); individual neurons still use rows of the dense matrix \(U\Sigma\). Similarly, polar alignment gives \(W_1x=Hy\), not a diagonal matrix.

Orthogonal changes preserve total spherical-harmonic energy in every degree. They can redistribute that energy between coordinate ANOVA components, which is relevant to Sobol projections.

**HEURISTIC:** Alignment helps when it concentrates important variation into a few well-stratified coordinate subsets. A first-layer singular basis is not automatically an effective basis for the final output. No growing-in-\(n\) benefit follows from first-layer isotropy or from the oblivious kernel bound.

**PROVEN — an adapted deterministic design need not be unbiased.** Already for \(W_1=I\), the radius-exact coordinate-axis rule gives, per output,
\[
\frac{m_n}{2n},
\]
whereas the Gaussian ReLU mean is \(1/\sqrt{2\pi}\). Selecting a basis using \(W\) removes the rotational averaging that justified an oblivious design’s ensemble calculation.

**PROVEN — an independent cube shift restores conditional unbiasedness while retaining a chosen alignment.** For fixed cube points \(p_i\), independent uniform
\(\Delta\in[0,1)^n\), and an orthogonal \(Q(W)\), set
\[
Z_{ij}=\Phi^{-1}((p_{ij}+\Delta_j)\bmod1),\qquad
U_i=Q(W)\frac{Z_i}{\|Z_i\|}.
\]
Conditional on \(W\), each \(Z_i\) is standard Gaussian and each \(U_i\) uniform on the sphere. Therefore averaging \(F_W(U_i)\) is unbiased.

An exact shift requires continuous randomness. A \(b\)-bit digital shift uses \(nb\) bits per replicate and is exact for its finite grid; discretisation bias remains. Haar rotation also restores unbiasedness, but multiplying an aligned design by a fresh full Haar rotation erases the alignment in distribution. Random signs or permutations alone do not generally make points spherical-uniform.

**PROVEN — first-layer controls have exact means.** For \(z_i=w_i^\top X\), \(X\sim N(0,I)\),
\[
\mathbb Ez_i=0,\qquad
\mathbb E|z_i|=\|w_i\|\sqrt{2/\pi},\qquad
\mathbb E\operatorname{relu}(z_i)=\frac{\|w_i\|}{\sqrt{2\pi}},
\]
\[
\mathbb E\|h_1\|^2=\frac12\|W_1\|_F^2,\qquad
\mathbb E[z^\top Cz]=\operatorname{tr}(CW_1W_1^\top).
\]
These follow respectively from symmetry, the one-dimensional normal absolute moment, and the covariance identity.

On the sphere, \(m_n\operatorname{relu}(w_i^\top U)\) has the same mean as its Gaussian counterpart, by homogeneity. Quadratic sphere means are their Gaussian means divided by \(n\).

For a vector of centered controls \(c\), fixed coefficients \(B\), and independent MC inputs,
\[
\widehat\mu=\frac1N\sum_i[F_W(U_i)-Bc(U_i)]
\]
is unbiased and has risk
\[
\frac1N\operatorname{tr}\operatorname{Var}(F_W-Bc).
\]
The optimal linear coefficients are
\[
B_*=\operatorname{Cov}(F_W,c)\operatorname{Cov}(c)^\dagger,
\]
obtained by completing the square in the quadratic residual variance.

Coefficients fitted on an independent pilot preserve conditional unbiasedness. Reusing the evaluation sample for fitting does not generally do so. For correlated point sets, variance reduction must be assessed using their integration covariance, not solely single-input regression error.

**HEURISTIC:** First-layer features are cheap to observe during a forward pass. A dense \(n\times n\) control readout nevertheless adds \(O(n^2)\) work per point, and estimating it can be pilot-limited. A low-rank readout is a reasonable cheaper experiment. A growing gain requires the unexplained variance to shrink with \(n\), not merely a nonzero explained share.

**PROVEN — multilevel prefix controls have an exact cost criterion.** For controls \(G_j\),
\[
\mathbb EF
=G_0+\sum_{j=1}^{J}\mathbb E(G_j-G_{j-1})
+\mathbb E(F-G_J),
\]
when \(G_0\) is constant. Independently estimate each difference, coupling its two terms on the same input. If its variance and cost are \(V_j,C_j\), the risk and cost are
\[
\sum_j\frac{V_j}{N_j},\qquad \sum_jC_jN_j.
\]
Cauchy–Schwarz gives
\[
\left(\sum_j\frac{V_j}{N_j}\right)\left(\sum_jC_jN_j\right)
\ge\left(\sum_j\sqrt{V_jC_j}\right)^2,
\]
with equality for \(N_j\propto\sqrt{V_j/C_j}\), before integer allocation.

**PROVEN UNDER**
\[
\mathbb E\|F-G_r\|^2\le C(1/r+n/L^2),\quad
C_r\asymp r/L,\quad L=\alpha n,\quad A=\Theta(1):
\]
dyadic levels yield an \(O(\log^2L/L)\) variance–cost product. Indeed, the variance of an increment between \(r\) and \(2r\) is at most twice the sum of their residual second moments, hence \(O(1/r)\); multiplying by cost \(O(r/L)\) gives \(O(1/L)\). There are \(O(\log L)\) levels. This proves a gain \(\Omega(L/\log^2L)\) under these hypotheses.

**HEURISTIC:** The cited measurements show that this asymptotic opportunity has not become an end-to-end advantage at \(256\times32\).

## 5. Gate surface area, gate changes, and output sensitivity

**PROVEN — the literal zero-set question needs a correction.** Almost surely \(W_1\) is invertible. The set
\[
\{x:W_1x<0\}
\]
is therefore a nonempty open cone. On it \(h_1=0\), and every later preactivation is identically zero. Thus, for \(\ell\ge2\), the full set \(\{z_{\ell,i}=0\}\) contains an open set and has infinite Gaussian-weighted \((n-1)\)-dimensional Hausdorff measure.

The useful objects are:

1. Fresh regular zero surfaces, inside regions where the preceding activation is nonzero.
2. The Gaussian perimeter of the gate set \(\{z_{\ell,i}>0\}\), including interfaces with dead regions.

For \(n\ge2\), define
\[
c_0=\frac1{\sqrt{2\pi}},\qquad
s_n=1-2^{-n},\qquad
\beta_n=1-(n+1)2^{-n}.
\]

**PROVEN — exact finite-width surface formulas.**
\[
\boxed{\mathbb E\,S_{\ell,i}^{\rm regular}=c_0\beta_n^{\ell-1}},
\qquad
\boxed{\mathbb E\,\operatorname{Per}_\gamma\{z_{\ell,i}>0\}
=c_0s_n^{\ell-1}}.
\]

Here is a proof that accounts for dead regions.

For a prefix map \(h\), Jacobian \(J\), and standard Gaussian row \(w\), Gaussian conditioning on \(w^\top h=0\) gives
\[
\mathbb E_w[\delta(w^\top h)\|J^\top w\|]
=\frac{1}{\sqrt{2\pi}\|h\|}
\mathbb E_G\|J^\top P_{h^\perp}G\|.
\]
Weight scaling cancels between the delta function and gradient. Matrices \(J^\top P_{h^\perp}\) and \(P_{h^\perp}J\) have the same nonzero singular values, so the last Gaussian norm can equally be written with \(P_{h^\perp}JV\).

For a fixed tangent perturbation \(v\), put
\[
q(h,v)=\frac{\|P_{h^\perp}v\|}{\|h\|}.
\]
After a fresh Gaussian ReLU layer, conditional on having \(K\) active coordinates,
\[
q_{\rm new}=q_{\rm old}\frac{\chi_{K-1}}{\chi_K},
\]
with independent chi variables, when \(K\ge2\). To derive this, decompose \(v\) into its component parallel to \(h\) and an orthogonal component. The Gaussian row projections of the orthogonal component are independent of the projections of \(h\). After restricting to active coordinates, projection away from the new activation removes one Gaussian direction.

For \(K=0,1\), the new projective derivative is zero. For \(K\ge2\),
\[
\mathbb E\chi_{K-1}\,\mathbb E\chi_K^{-1}
=
\frac{\sqrt2\,\Gamma(K/2)}{\Gamma((K-1)/2)}
\frac{\Gamma((K-1)/2)}{\sqrt2\,\Gamma(K/2)}
=1.
\]
Since \(K\sim\operatorname{Bin}(n,1/2)\),
\[
\mathbb E[q_{\rm new}\mid h,v]=\beta_n q_{\rm old}.
\]
Initially, with independent \(X,V\sim N(0,I_n)\),
\[
\mathbb E\frac{\|P_{X^\perp}V\|}{\|X\|}
=\mathbb E\chi_{n-1}\,\mathbb E\chi_n^{-1}=1.
\]
Integrating the conditional surface formula proves the regular-surface identity.

Next consider a newly created boundary of a dead region at layer \(j\). One of its \(n\) preactivations is zero and all other \(n-1\) are negative. Independence of those rows makes its expected area
\[
D_j=n\,2^{-(n-1)}c_0\beta_n^{j-1}.
\]
On the live side near such a facet, \(h_j\) lies on one positive coordinate ray. Each subsequent full layer preserves a nonzero ray with probability \(s_n\); a specified final preactivation is positive with probability \(1/2\). Its contribution to the gate perimeter at layer \(\ell>j\) is therefore
\[
\frac12s_n^{\ell-j-1}D_j.
\]
Adding fresh and inherited surfaces gives
\[
c_0\left[
\beta_n^{\ell-1}
+n2^{-n}\sum_{j=1}^{\ell-1}
\beta_n^{j-1}s_n^{\ell-j-1}
\right]
=c_0s_n^{\ell-1},
\]
because \(s_n-\beta_n=n2^{-n}\). Apart from inherited dead-region interfaces, distinct random facets intersect only in codimension at least two, so they do not add perimeter corrections.

**PROVEN — summed perimeter is approximately linear in neuron count and depth.**
\[
\mathbb E\sum_i\operatorname{Per}_\gamma\{z_{\ell,i}>0\}
=nc_0s_n^{\ell-1},
\]
and summing through layer \(\ell\) gives
\[
nc_0\sum_{j=0}^{\ell-1}s_n^j.
\]
At \(n=256,\ell=32\), the correction from replacing \(s_n^j,\beta_n^j\) by one is negligible.

**PROVEN UNDER the infinite-width kernel model — the corresponding per-neuron regular surface area is \(c_0\).** The kernel satisfies \(K(1)=K'(1)=1\), since \(\kappa'(1)=1\). Thus the variance and local tangential derivative variance used in the preceding Gaussian surface calculation are unchanged. This also agrees with the finite-width formulas as \(n\to\infty\).

**PROVEN — gate-pattern disagreement has a square-root small-noise scale.** Put \(\theta=\arccos\rho\). Along the Gaussian rotation path
\[
X_t=X\cos t+Z\sin t,
\]
\(X_t\) and \(X_t'\) are independent standard Gaussians. Expected boundary crossings per unit \(t\) equal
\[
\sqrt{2/\pi}\,\operatorname{Per}_\gamma.
\]
This follows by conditioning on a boundary point: the expected absolute normal velocity is \(\mathbb E|N(0,1)|=\sqrt{2/\pi}\). Endpoint disagreement is bounded by the number of crossings. Hence
\[
\mathbb P(g_{\ell,i}(X)\ne g_{\ell,i}(Y))
\le\frac{\theta}{\pi}s_n^{\ell-1}.
\]

For fixed finite \(n,\ell\), multiple-boundary crossings are lower order as \(\delta\downarrow0\), so
\[
\mathbb P(g_{\ell,i}(X)\ne g_{\ell,i}(Y))
\sim\frac{\sqrt2}{\pi}s_n^{\ell-1}\sqrt\delta.
\]

For the complete gate history, count each fresh surface once; inherited surfaces already belong to earlier gate boundaries. Thus
\[
\mathbb P(\text{history through }\ell\text{ changes})
\le
\min\left\{1,\frac{n\theta}{\pi}
\sum_{j=0}^{\ell-1}\beta_n^j\right\},
\]
and its small-\(\delta\) asymptotic is
\[
\frac{\sqrt2\,n}{\pi}
\left(\sum_{j=0}^{\ell-1}\beta_n^j\right)\sqrt\delta.
\]
The asymptotic takes \(\delta\to0\) at fixed \(n,\ell\); it is not a uniform order-one approximation.

A lower bound is the probability that the first-layer pattern changes:
\[
\mathbb E_{X,Y}\left[
1-\left(1-\frac{\angle(X,Y)}{\pi}\right)^n
\right].
\]
Conditional on \(X,Y\), independent first-layer rows disagree with probability \(\angle(X,Y)/\pi\), proving this expression.

**PROVEN — output sensitivity is qualitatively different.** The Jacobian identity from Question 2 gives
\[
\boxed{
\operatorname{NS}_{\rm ann}(\delta)
:=\frac{\mathbb E_{W,X,Y}\|f_W(X)-f_W(Y)\|^2}{2\bar V}
\le\frac{n}{\bar V}\delta,
}
\]
with asymptotic equality as \(\delta\downarrow0\). The bound uses
\(1-(1-\delta)^k\le k\delta\); the limit follows by dominated convergence using \(\sum k\,\mathbb EH_k=n\).

Thus gate history changes on a \(\sqrt\delta\) scale while output decorrelation starts linearly in \(\delta\). Counting gate changes does not price their output effect.

**PROVEN — kink strength, rather than bare surface area, controls a high-degree diagnostic.** For a fixed continuous piecewise-linear map, let
\[
J_{\rm kink}
=\sum_{\text{facets }S}
\int_S\|[J_f]\|_F^2\phi_n(x)\,d\mathcal H^{n-1}(x),
\]
where \([J_f]\) is the jump in the full output Jacobian.

A single facet is crossed with leading probability
\((2/\sqrt\pi)\sqrt\delta\) times its Gaussian area. Across it, the squared gradient change is \(\|[J_f]\|_F^2\). Intersections of distinct facets contribute lower-order terms. Therefore
\[
\frac12\mathbb E\|J_f(X)-J_f(Y)\|_F^2
\sim\frac{J_{\rm kink}}{\sqrt\pi}\sqrt\delta.
\]
On the other hand, differentiating Hermite polynomials gives exactly
\[
\frac12\mathbb E\|J_f(X)-J_f(Y)\|_F^2
=\sum_{k\ge1}k[1-\rho^{k-1}]H_k.
\]
Taking \(\delta=1/t\), the multiplier for \(k>t\) is bounded below by a constant times \(t\). Hence
\[
\sum_{k>t}H_k=O(J_{\rm kink}t^{-3/2})
\]
for sufficiently large \(t\), for a fixed map with \(J_{\rm kink}>0\).

If \(D=\sum kH_k\) and \(F(\delta)=V\operatorname{NS}(\delta)\), the same identity says
\[
D-F'(\delta)\sim\frac{J_{\rm kink}}{\sqrt\pi}\sqrt\delta.
\]
Integrating,
\[
F(\delta)
=D\delta-\frac{2J_{\rm kink}}{3\sqrt\pi}\delta^{3/2}
+o(\delta^{3/2}).
\]

An unused hidden gate contributes no output Jacobian jump. Arbitrarily complicated unused subnetworks therefore cannot establish an output-fooling lower bound.

## 6. Worst-case PRGs

**UNVERIFIED literature guide.** I did not check the original papers in this sandbox.

- Meka–Zuckerman: halfspaces and polynomial threshold functions; the commonly quoted halfspace seed bound \(O(\log n+\log^2(1/\eta))\) concerns a specified discrete-input setting. I do not use it here as a Gaussian theorem.
- Kane: Gaussian PTF generators; a conservative remembered bound has the form
  \[
  r=O_d(\log n)\,\eta^{-O(d)}.
  \]
  Exact versions and stronger later bounds are **UNVERIFIED** here.
- Harsha–Klivans–Meka: intersections/polytopes and invariance, with regularity and distribution hypotheses that must be checked.
- O’Donnell–Servedio–Tan and Chattopadhyay–De–Servedio: I have not verified the relevant function class, assumptions, or quantitative seed bounds, so I will not assign them a theorem from memory.
- Hatami–Hoza–Tal–Tell: threshold-circuit results require checking circuit depth, size, input distribution, and whether the result is a PRG or a different derandomisation statement. No transfer is used here.

**PROVEN — individual origin halfspaces are already easy in a purely information-theoretic sense.** Choose \(M\) vectors on a moment curve,
\[
v_j=(1,t_j,\ldots,t_j^{n-1}),
\]
with distinct \(t_j\), and include both signs. A nonzero linear functional vanishes on at most \(n-1\) of the \(v_j\), because it gives a nonzero polynomial of degree at most \(n-1\). Every other antipodal pair contributes exactly one positive point.

Thus the \(N=2M\) point distribution fools every origin halfspace to error at most
\[
\frac{n-1}{N},
\]
relative to its Gaussian probability \(1/2\). Choosing \(N\) a power of two gives index seed
\[
r\le \left\lceil\log_2\frac{n-1}{\eta}\right\rceil+O(1).
\]
This says nothing about joint gate patterns or ReLU values.

**PROVEN — the first-layer cell is covered by an intersection theorem, but the whole output needs substantially more.** A specified first-layer pattern is an intersection of \(n\) origin halfspaces.

For a specified full gate pattern, every activation is a fixed linear function of \(x\). Its consistency region is an intersection of at most \(nL\) origin halfspaces. On that region, output coordinate \(j\) equals \(a_C^\top x\). Therefore
\[
\{f_j(x)>t\}
\]
is a union over feasible cells \(C\) of intersections of at most \(nL+1\) affine halfspaces. The crude cell count is \(M\le2^{nL}\).

Suppose a generator fools each such intersection to error \(\eta\). Since the cell pieces are disjoint, summing their errors bounds the output-threshold error by \(M\eta\).

For a clipped nonnegative output,
\[
\min(f_j,B)=\int_0^B\mathbf1_{\{f_j>t\}}\,dt.
\]
Integrating the threshold-error bound gives
\[
\left|\mathbb E_G\min(f_j,B)-\mathbb E_\gamma f_j\right|
\le BM\eta+\mathbb E_\gamma(f_j-B)_+.
\]
This explicitly exposes the accuracy and truncation requirements. It does not assume that an intersection PRG automatically fools the network.

**PROVEN — short existential support also does not imply a useful explicit PRG.** For a finite class of \(K\) functions taking values in \([0,1]\), \(N\) iid inputs satisfy
\[
\Pr\left(\max_f|\widehat{\mathbb E}f-\mathbb Ef|>\eta\right)
\le2K e^{-2N\eta^2}.
\]
For completeness, a variable in \([0,1]\) has tilted variance at most \(1/4\); integrating the second derivative of its log moment-generating function twice gives
\(\mathbb Ee^{\lambda(Z-\mathbb EZ)}\le e^{\lambda^2/8}\).
Chernoff optimisation gives the scalar bound, and a union bound gives the display.

Hence a fixed support of size \(O(\log K/\eta^2)\) exists. Its index length is only
\[
O(\log\log K+\log(1/\eta)).
\]
For quantised networks, \(K\) can be enormous while this seed remains short. Constructing the support efficiently is the missing issue.

**PROVEN — worst-case results are not categorically irrelevant to ARC.** A valid worst-case PRG covering these outputs with the required normalisation and efficient evaluation would give an average-case upper bound too. What is unsupported is the claim that the named results already meet ARC’s error–compute target.

A seed bound \(r\) produces \(2^r\) evaluations when enumerated. Polynomial dependence on \(1/\eta\) in the seed can become exponential dependence in enumeration cost. “Short seed” is therefore not the needed performance criterion.

## 7. Verdict

**PROVEN:** The proposed implication
\[
\text{large gate-boundary mass or output sensitivity}
\Longrightarrow
\text{many necessary runtime random bits}
\]
fails under the ensemble-average MSE criterion. A fixed oblivious design already matches radius-exact MC existentially.

**PROVEN:** The randomness framing nevertheless supplies useful distinctions and tests:

- Conditional unbiasedness differs from ensemble accuracy.
- Coordinate independence differs from independence between samples.
- Positive oblivious rules have an exact kernel risk and a finite-width even-tail lower bound.
- Gate perimeter and output-weighted kink strength are different observables.
- A generator’s index length must be converted into construction and enumeration cost.

**HEURISTIC:** These distinctions sharpen “precision per compute”; they do not currently establish a new computational obstruction to ARC’s goal. The most useful new geometric fact here is that expected per-neuron gate perimeter stays approximately constant, while continuity makes the output substantially more noise-stable than its gate history.

## Single strongest defensible statement

**PROVEN:**
For every finite \(n,L,N\), there exists a deterministic, weight-independent, positive equal-weight \(N\)-point spherical rule such that
\[
\boxed{
\mathbb E_W\|\widehat\mu(W)-\mu(W)\|^2
\le\frac{A}{N}\le\frac{\bar V}{N}.
}
\]
The proof is the averaging argument in Question 1.

Therefore neither noise sensitivity nor gate-boundary mass can force a positive runtime-randomness budget for ARC’s stated average-risk target. The unresolved restriction is efficient, explicitly describable construction, together with ARC’s exclusion of sampling-style representations.

## Single most promising structured-sampling route at \(256\times32\)

**HEURISTIC — recommendation:** Use complete antipodal Kerdock blocks with exact radius, and independent rotations for conditional error measurement. Charge rotation setup and all evaluations. This has direct prior evidence and an exact geometric prediction.

**PROVEN UNDER the mutually unbiased basis property of the supplied construction:** With \(K=n/2+1=129\) bases, the antipodal set has
\[
M=2Kn=66{,}048
\]
points and is a spherical 5-design.

For proof, the traceless projectors
\(u_{b,j}u_{b,j}^\top-I/n\) from different bases are orthogonal. Each basis spans an \((n-1)\)-dimensional diagonal traceless subspace, and
\[
K(n-1)=\dim\operatorname{Sym}_0(n).
\]
Applying the resulting orthogonal decomposition to
\(xx^\top-\|x\|^2I/n\) gives
\[
\sum_{b,j}(u_{b,j}^\top x)^4=\frac32\|x\|^4.
\]
Dividing by \(Kn=n(n+2)/2\) gives the sphere’s fourth moment
\(3\|x\|^4/[n(n+2)]\). The second moment follows from each orthonormal basis; antipodes cancel odd moments through degree five.

**PROVEN — its residual risk is explicitly testable.** Odd \(B_d\) vanish, and for even \(d\),
\[
B_d=
\frac1{Kn}
+\frac{n-1}{Kn}P_d^{(n)}(0)
+\frac{K-1}{K}P_d^{(n)}(n^{-1/2}).
\]
This follows by counting, relative to one node, its antipode, the orthogonal nodes in its basis, and the mutually unbiased nodes in other bases. In particular, \(B_2=B_4=0\).

Thus one rotated block has ensemble risk
\[
R_{\rm block}=\sum_{\substack{d\ge6\\d\ {\rm even}}}a_dB_d.
\]
Averaging \(B\) independent rotated blocks gives exactly \(R_{\rm block}/B\). Fixed orientation has the same ensemble risk.

Replacing independent radial randomisation by the exact factor \(m_n\) is conditional expectation given the directions, so it cannot increase MSE when the original radii have conditional mean \(m_n\).

**CONJECTURE — falsifiable numerical prediction:** On fresh noiseless \(256\times32\) nets, at \(N=M,2M,4M\), the pooled error constant will satisfy
\[
\frac{N\,\mathbb E\|\widehat\mu-\mu\|^2}{\bar V}
\in[0.33,0.50],
\]
corresponding to a \(2\)–\(3\times\) gain over plain MC. This extrapolates the cited noisy experiment; it is not implied by 5-design exactness. A reliably estimated constant above \(0.50\) falsifies the prediction.

## Measurements that most efficiently test these claims

The following are proposed tests, not completed \(256\times32\) experiments.

1. **Ensemble risk with independent truth estimates.** Pool squared errors and variances separately, matching \(\mathbb E_W\mathrm{error}^2/\bar V\). With independent unbiased truths \(\mu_1,\mu_2\), use
   \[
   (\widehat\mu-\mu_1)^\top(\widehat\mu-\mu_2)
   \]
   to avoid adding reference variance to estimated squared error.

2. **Kerdock’s exact error constant.** Compare full blocks with exact radius, full blocks with the old radial treatment, radius-exact MC, and scrambled Sobol. Use \(66{,}048\) and integer multiples; partial blocks do not retain full degree-five exactness.

3. **The geometry-specific kernel contrasts.** Estimate \(k(-1),k(0),k(\pm1/\sqrt n)\), and \(q\), with \(k(1)=1\). They determine Kerdock risk directly. Use shared randomness or direct block contrasts to avoid subtracting independently estimated quantities close to one.

4. **Parity and low-degree energy.** Measure angular degrees \(1,2,4\), total even energy, and the residual after removing those degrees. Keep spherical energies distinct from Gaussian Hermite energies and power-series coefficients.

5. **Gate crossings versus output change on the same pairs.** Sweep small \(\delta\); measure per-neuron disagreement, full-history disagreement, output squared change, and gradient squared change. Test the \(\sqrt\delta\), \(\delta\), and weighted-kink predictions separately. Small widths are useful for resolving the \(s_n\) versus \(\beta_n\) factors.

6. **Whole-input pairwise independence versus coordinate-wise independence.** Use the same finite Gaussian grid and charge generation cost. The former should reproduce MC’s grid-target variance; the latter has no such guarantee.

7. **Aligned controls with independent pilots.** Before a large integration run, estimate the residual variance–cost product for shifted Sobol in the original, polar, and singular-vector bases, with and without first-layer controls. Include pilot and fitting cost. A favorable regression fit alone is insufficient.
