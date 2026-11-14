codex
**Q1. Smoothness**

**PROVEN.** A transverse line integration improves a finite continuous piecewise-linear function to \(C^{1,1}\). It does **not** generally produce \(C^2\), and monotonicity along the line is unnecessary for this improvement.

Here is a quantitative statement. Write the nonzero slope-jump facets of the fan as \(F_j\), choose unit normals \(a_j\), and let the Jacobian jump across \(F_j\) be
\[
A_j^+-A_j^-=v_j a_j^\top .
\]
This rank-one form follows from continuity: the two linear maps agree on the tangent space of the facet. Put
\[
P=I-uu^\top,\qquad \alpha_j=a_j\cdot u,\qquad
M=\max_{\text{cones }C}\|A_C\|_{\rm op}.
\]
Assume every \(\alpha_j\ne0\).

For a smooth integrable weight \(p\), define
\[
H_p(y)=\int_{\mathbb R}f(y+tu)p(t)\,dt,\qquad y\in u^\perp.
\]
For the weights in the question, the integral exists because \(f\) has at most linear growth.

The distributional Hessian of a continuous piecewise-linear function is
\[
D^2f=\sum_j v_j\,a_j\otimes a_j\,
             \mathcal H^{d-1}\!\restriction F_j.
\]
There are no additional terms on lower-dimensional intersections: this formula comes from differentiating the piecewise-constant first derivative, whose jumps occur across facets.

Set
\[
t_j(y)=-\frac{a_j\cdot y}{\alpha_j}.
\]
Integrating the facet measure in the \(u\)-direction gives, almost everywhere,
\[
D^2H_p(y)=
\sum_j
 \frac{v_j\,(Pa_j)\otimes(Pa_j)}{|\alpha_j|}
 p(t_j(y))
 \mathbf 1_{\{y+t_j(y)u\in F_j\}}.                 \tag{1}
\]
Indeed, the supporting hyperplane has equation
\(a_j\cdot y+\alpha_jt=0\); integrating its delta function contributes
\(1/|\alpha_j|\).

Consequently,
\[
\|\nabla H_p\|_\infty\le M\|p\|_1,
\qquad
\|D^2H_p\|_\infty\le B_p,
\]
where
\[
B_p=
\|p\|_\infty
\sum_j\frac{\|v_j\|\,\|Pa_j\|^2}{|\alpha_j|}.       \tag{2}
\]
A bounded distributional Hessian makes the gradient Lipschitz, so
\(H_p\in C^{1,1}\cap W^{2,\infty}_{\rm loc}\).

For the classic Gaussian integration, \(\|p\|_1=1\) and
\(\|p\|_\infty=(2\pi)^{-1/2}\).

**PROVEN.** The line-plus-radius weight in the statement is correctly normalized as an integration weight, although it is not a probability density:
\[
w(s)=\frac{k}{\sqrt{2\pi}}(1+s^2)^{-(k+2)/2},
\qquad
\int w(s)\,ds=\mathbb E\chi_k,\qquad k=d-1.
\]
To verify it, write \(T=\rho s\). The Jacobian contributes \(\rho\), and homogeneity contributes another \(\rho\). Thus the radial integral is
\[
\frac{1}{2^{k/2-1}\Gamma(k/2)\sqrt{2\pi}}
\int_0^\infty
 \rho^{k+1}e^{-\rho^2(1+s^2)/2}\,d\rho
=
\frac{k}{\sqrt{2\pi}}(1+s^2)^{-(k+2)/2}.
\]

Let \(G\) denote the resulting function restricted to \(S^{d-2}\).
Equation (2) applies with
\[
\|w\|_1=\mathbb E\chi_{d-1},\qquad
\|w\|_\infty=\frac{d-1}{\sqrt{2\pi}}.
\]
For unit tangent vectors on the sphere,
\[
\|\nabla_S^2G\|
\le B_w+M\mathbb E\chi_{d-1}.                     \tag{3}
\]
The extra term is the second fundamental form: restricting an ambient function \(H\) to the unit sphere replaces its Hessian by
\(D^2H-(y\cdot\nabla H)I\) on tangent vectors.

**PROVEN.** These functions have the following isotropic Sobolev regularity:

- \(f\in H^s_{\rm loc}\) for every \(s<3/2\).
- Under transversality, \(g\in H^s_{\rm loc}\) and \(G\in H^s(S^{d-2})\) for every \(s<5/2\).

For \(f\), its first derivative is piecewise constant. For \(H_p\), formula (1) makes its second derivative piecewise smooth, with finitely many polyhedral interfaces. If \(A\) is such a bounded piecewise-smooth function on a compact set, then
\[
\|A(\cdot+h)-A\|_2^2
\le C\bigl(D^2|h|^2+B^2S|h|\bigr),
\]
where \(B\) bounds its size, \(D\) bounds its derivatives within pieces, and \(S\) bounds interface area. The crossing region has volume \(O(S|h|)\); outside it, the ordinary mean-value estimate applies.

The fractional \(H^\beta\) seminorm therefore converges for \(\beta<1/2\), since its interface contribution is proportional to
\[
\int_0^1 r^{-2\beta}\,dr.
\]
Applying this to \(Df\) or \(D^2H_p\) proves the assertions. For (1), one may take a within-piece derivative bound
\[
D\le
\|p'\|_\infty
\sum_j\frac{\|v_j\|\,\|Pa_j\|^3}{|\alpha_j|^2}.
\]
Thus the constants depend explicitly on slope jumps, inverse transverse angles, and projected interface areas.

**PROVEN.** The \(C^{1,1}\) conclusion is sharp. In coordinates \((a,t)\), take
\[
f(a,t)=\max(0,a+t,a-t)=(a+|t|)_+.
\]
Every facet is transverse to the \(t\)-direction. Nevertheless,
\[
g''(a)=
\begin{cases}
2\phi(a),&a<0,\\
0,&a>0.
\end{cases}
\]
To obtain this, for \(a<0\) differentiate
\(2\int_{-a}^{\infty}(a+t)\phi(t)\,dt\); for \(a>0\),
\(g(a)=a+\mathbb E|T|\).
The first derivative matches at zero, but the second does not. Adding an unused perpendicular coordinate gives the same failure on a positive-dimensional sphere.

If transversality fails, even \(C^1\) can fail: \(f(y+tu)=|a\cdot y|\), with \(a\perp u\), is unchanged by classic pre-integration. Some tangent facets can cancel or be irrelevant, so transversality is sufficient rather than necessary.

**PROVEN.** None of this supplies high-order dominating mixed smoothness. A generic oblique kink in \(f\) has a measure-valued mixed second derivative. A generic oblique jump in \(D^2G\) can make a mixed third derivative measure-valued. Thus, in sufficiently many coordinates, the full collection of square-integrable mixed first derivatives required by smooth scrambled-net theorems need not exist.

The Gilbert–Kuo–Sloan monotonicity condition is therefore unnecessary for the finite-fan \(C^{1,1}\) result above. It cannot be replaced by the stronger claim that arbitrary pre-integration gives all the mixed smoothness needed for an \(N^{-3}\) MSE bound.

---

**Q2. Rates for a fixed net**

**PROVEN UNDER the standard bounded-gain scrambled-net variance formula.** For each fixed net and fixed dimension, ideal nested-uniformly scrambled Sobol integration has
\[
\operatorname{MSE}=o(N^{-1})
\]
for both the original and pre-integrated integrands, provided the cube-to-input map is measure-preserving.

The precise hypotheses used here are
\[
\operatorname{Var}(\widehat I_N)
=\frac1N\sum_\lambda \Gamma_{\lambda,N}\sigma_\lambda^2,
\qquad
0\le\Gamma_{\lambda,N}\le C_d,
\]
where the Haar energies satisfy
\(\sum_\lambda\sigma_\lambda^2<\infty\), and every fixed finite collection of Haar components is eventually integrated exactly.

Given \(\varepsilon>0\), choose a finite collection leaving tail energy below \(\varepsilon\). For sufficiently large \(N\), only the tail contributes, giving
\(N\operatorname{Var}(\widehat I_N)\le C_d\varepsilon\).
This proves the little-\(o\) statement.

Both integrands are square-integrable: the Gaussian one has linear growth, and the spherical ones are bounded. The specific scrambling implementation and its gain properties have not been checked here.

**PROVEN UNDER bounded mixed-derivative hypotheses for the cube pullback.** The familiar stronger bound is
\[
\operatorname{MSE}
=O\!\left(N^{-3}(\log N)^{s-1}\right)
\]
in \(s\) cube coordinates. Its mechanism is that first mixed derivatives give Haar energies decaying like \(2^{-2|\kappa|}\); summing the unresolved levels \(|\kappa|\gtrsim\log_2N\), with \(O(|\kappa|^{s-1})\) level combinations, and multiplying by \(N^{-1}\), gives the displayed rate.

Q1 does not establish these hypotheses. Inverse-normal maps and normalization of Gaussian vectors also introduce coordinate singularities.

**PROVEN.** For randomized point-query integration over bounded smoothness classes on an \(m\)-dimensional compact domain,
\[
\begin{array}{c|c}
\text{class, with a fixed norm bound}&
\text{minimax MSE order}\\ \hline
\text{Lipschitz}&N^{-1-2/m}\\
C^{1,1}&N^{-1-4/m}.
\end{array}                                                     \tag{4}
\]

Here is the upper-bound construction. Partition into cells of diameter
\(h\asymp N^{-1/m}\). Construct a local interpolant, integrate it exactly, and estimate its residual with independent samples. A Lipschitz function has residual \(O(h)\); a \(C^{1,1}\) function has residual \(O(h^2)\) after affine interpolation. Summing cell variances gives \(N^{-1}h^2\) or \(N^{-1}h^4\). The interpolation cost per cell is a dimension-dependent constant.

For the lower bound, place \(cN\) disjoint smooth bumps of width
\(h\asymp N^{-1/m}\), with independent random signs and heights \(h\) or \(h^2\). Their respective smoothness norms stay bounded. Each query can discover at most one sign. After \(N\) adaptive queries, order \(N\) independent signs remain unknown. Each bump integral has magnitude order \(h^{m+r}\), where \(r=1\) or \(2\). Their conditional variance is therefore
\[
\Omega\!\left(Nh^{2m+2r}\right)
=\Omega\!\left(N^{-1-2r/m}\right).
\]
Averaging over signs lower-bounds the worst-case risk of every randomized algorithm.

These are minimax results for the specified classes, not lower bounds for the Gaussian-network ensemble.

**PROVEN.** The finite-interface structure gives stronger constructive rates than (4). With suitable local polynomial interpolation plus independent residual sampling:

\[
\begin{array}{c|c|c}
\text{integrand}&\text{intrinsic dimension}&
\text{achievable fixed-net MSE}\\ \hline
\text{radius-exact }f|_{S^{d-1}}&d-1&
O\!\left(N^{-1-3/(d-1)}\right)\\
G\text{ after line and radius integration}&d-2&
O\!\left(N^{-1-5/(d-2)}\right).
\end{array}                                                     \tag{5}
\]

These statements concern a constructed randomized cubature algorithm, not ordinary scrambled Sobol.

For the first row, use affine interpolation. In cells avoiding a kink, the spherical pullback is smooth and the residual is \(O(h^2)\). In cells meeting a kink it is \(O(h)\). There are \(O(h^{-(m-1)})\) boundary cells and \(O(h^{-m})\) cells overall. Their variance contributions are respectively
\[
O(h^{m+3}),\qquad O(h^{m+4}).
\]
For the second row, use quadratic interpolation. Q1 gives \(O(h^2)\) residual everywhere, while within a smooth piece it is \(O(h^3)\). The corresponding contributions are
\(O(h^{m+5})\) and \(O(h^{m+6})\).

A finite smooth atlas and partition of unity reduce spherical integration to this construction. Constants include interpolation costs, chart bounds, interface areas, and the transverse-angle constants of Q1. They need not be remotely uniform in dimension.

An implementation that normalizes \(d-1\) Gaussian variables to sample \(S^{d-2}\) still uses \(d-1\) Sobol coordinates; (5) uses intrinsic dimension and suitable charts.

**PROVEN.** “The optimal randomized rate for this fixed known net” has no unqualified answer. A single-function class permits hardcoding its integral. A meaningful optimality assertion must specify a function class, norm bounds, available information, and computational costs. The constructions in (5) are upper bounds; I have not established matching lower bounds for finite neural fans.

**HEURISTIC.** The observed pre-asymptotic regime can hide the advantage in (5). When essentially every cell crosses interfaces, its boundary-cell estimate reduces to the ordinary Lipschitz or \(C^{1,1}\) estimate. With seven angular dimensions and boundary distance \(\delta\approx0.003\)–\(0.006\), the crude isotropic scale \(\delta^{-7}\) is around \(10^{15}\)–\(10^{18}\) cells. This is not a necessary sample count or a lower bound: integration can improve without resolving every region.

**PROVEN UNDER an isotropic independently marked Poisson-hyperplane model.** The proposed ambient spectrum
\[
S_f(\xi)\asymp |\xi|^{-(d+3)}
\]
is correct, interpreted as the spectrum of an intrinsic random field modulo affine terms.

To see this, let the signed kink amplitudes be independent, centered, and have finite variance. Then
\[
\Delta f(x)=\sum_j A_j\delta(v_j\cdot x-b_j).
\]
Integrating over offsets and uniform orientations gives
\[
\operatorname{Cov}(\Delta f(x),\Delta f(x+h))
=C\int_{S^{d-1}}\delta(v\cdot h)\,d\sigma(v)
=\frac{C_d}{|h|}.
\]
The Fourier transform of \(|h|^{-1}\) is proportional to
\(|\xi|^{-(d-1)}\). This follows, for example, by expressing
\(|h|^{-1}\) as an integral of Gaussians and Fourier transforming each Gaussian. Dividing by the squared Laplacian multiplier \(|\xi|^4\) gives the claim. In dimension one, the corresponding second derivative is white shot noise, giving \(|\xi|^{-4}\).

After integrating along one direction with a nonzero \(L^2\) weight \(p\), the spectrum in the remaining \(d-1\) dimensions is
\[
S_g(\eta)
=\frac1{2\pi}\int_{\mathbb R}
 |\widehat p(\tau)|^2 S_f(\eta,\tau)\,d\tau
\asymp |\eta|^{-(d+3)}.                           \tag{6}
\]
For the asymptotic equivalence, factor out \(|\eta|^{-(d+3)}\) and use dominated convergence against \(|\widehat p|^2\).

Thus the original field has mean-square Sobolev regularity \(s<3/2\), while the integrated field has \(s<2\): **only half a derivative is gained in this ensemble model**.

**PROVEN.** This does not contradict Q1. The Poisson model averages over arbitrarily near-parallel hyperplanes. For a single smoothed hinge with transverse angle parameter \(\alpha\), the Hessian has height \(O(|\alpha|^{-1})\) and transverse width \(O(|\alpha|)\). Its squared \(L^2\) norm is therefore \(O(|\alpha|^{-1})\). Averaging over orientations with nonzero density at \(\alpha=0\) diverges. Every finite transverse realization can be smoother than its orientation-averaged Sobolev estimate.

**HEURISTIC.** Transferring (6) to the neural fan, or to its spherical restriction, requires a separate model justification. A stationary Poisson process with random offsets is not the homogeneous neural fan.

---

**Q3. Cost**

**PROVEN.** In the fixed-depth GP limit, the expected number of sign changes of a preactivation on a half great circle is one.

Write the normalized ReLU correlation map as
\[
C(\rho)=
\frac{\sqrt{1-\rho^2}+(\pi-\arccos\rho)\rho}{\pi}.
\]
For layer \(\ell\), the normalized preactivation covariance along the circle is
\[
R_\ell(\theta)=C^{\circ(\ell-1)}(\cos\theta).
\]
Since \(C(1)=C'(1)=1\),
\[
R_\ell(0)=1,\qquad R_\ell'(0)=0,\qquad R_\ell''(0)=-1.
\]
Hence the value and angular derivative are independent standard Gaussians. Rice’s density is
\[
p_{Z(0)}(0)\mathbb E|Z'(0)|=\frac1\pi,
\]
so an interval of length \(\pi\) has expected crossing count one.

The requisite differentiability is consistent with, and follows from, the local covariance expansion
\(R_\ell(h)=1-h^2/2+O(|h|^3)\): the derivative process has increment variance \(O(|h|)\); Gaussian moment bounds and the continuity criterion give a continuous derivative version. Nondegenerate value/derivative marginals give the usual simple-zero Rice formula.

**PROVEN.** There is a stronger exact finite-width calculation. For a fixed input arc independent of the weights, define
\[
q_n=1-\frac{n+1}{2^n}.
\]
The expected number of *new*, non-inherited crossings at layer \(\ell\), across all \(n\) units, is
\[
nq_n^{\ell-1}.                                    \tag{7}
\]

The proof identifies the finite-width correction directly.

Let \(v\) be the angular speed of a nonzero hidden-state curve. For a fresh Gaussian layer, resolve its derivative into radial and transverse components. After rescaling, the preactivation and its transverse derivative are independent standard Gaussian vectors \(a,b\). Let \(K\sim{\rm Binomial}(n,1/2)\) be the number of positive entries of \(a\).

Conditional on \(K\ge2\), the output angular speed divided by \(v\) has conditional expectation
\[
\mathbb E\chi_{K-1}\;\mathbb E\chi_K^{-1}=1,
\]
because
\[
\mathbb E\chi_{K-1}
=\sqrt2\,\frac{\Gamma(K/2)}{\Gamma((K-1)/2)},\qquad
\mathbb E\chi_K^{-1}
=\frac1{\sqrt2}\frac{\Gamma((K-1)/2)}{\Gamma(K/2)}.
\]
For \(K=1\), the output moves on one ray and its angular speed is zero. For \(K=0\), it is dead and remains dead. Therefore each layer multiplies expected angular speed by
\(\Pr(K\ge2)=q_n\).

Conditional on the previous hidden curve, a fresh row’s zero-crossing density is its angular speed divided by \(\pi\). Integrating over the input half circle proves (7). Zeros where the previous state itself is zero are inherited boundaries, not newly introduced crossings.

**PROVEN.** If the algorithm retains all inherited vertices, starts with \(B_0=3\), and charges one matvec per existing vertex per layer, then
\[
\mathbb E B_\ell
=3+n\sum_{j=0}^{\ell-1}q_n^j
\]
and its expected cost in forward passes is
\[
c_{\rm line}
=
3+\frac nL\sum_{j=0}^{L-2}(L-1-j)q_n^j.           \tag{8}
\]
Pruning redundant vertices can reduce this cost.

When \(L(1-q_n)\ll1\), (8) becomes
\[
c_{\rm line}\approx 3+\frac{n(L-1)}2,
\]
giving the proposed \(nL/2\) leading term. For fixed narrow width, it instead saturates at
\(3+n/(1-q_n)\) as \(L\to\infty\).

For example, the exact expectation from (8) is about \(3{,}971\) passes at \(256\times32\), and about \(205\) at \(8\times256\). These are ensemble expectations for retained vertices, not predictions of every measured net or of a pruning implementation. No concentration result has been proved here.

**PROVEN.** Restricting to a predetermined angular window of length \(2\psi_0\) multiplies the new-crossing contribution in (8) by \(2\psi_0/\pi\). Thus the proposed window cost is correct at leading order, under the same assumptions.

The angular form of the integral is
\[
G(v)=\frac{d-1}{\sqrt{2\pi}}
\int_{-\pi/2}^{\pi/2}
 f(\cos\psi\,v+\sin\psi\,u)\cos^{d-2}\psi\,d\psi.
\]
Consequently, truncation outside the window has norm at most
\[
M\frac{d-1}{\sqrt{2\pi}}
\int_{|\psi|>\psi_0}\cos^{d-2}\psi\,d\psi.          \tag{9}
\]
A small omitted weight alone is not a relative-error guarantee; (9) supplies an absolute bound.

**PROVEN UNDER power-law error models.** Suppose point integration costs one pass and has error \(A B^{-p}\), while line integration costs \(c\) passes per line and has error \(A_{\rm PI}N^{-q}\). If \(q>p\), its break-even compute is
\[
B_*=
\left(\frac{A_{\rm PI}}{A}c^q\right)^{1/(q-p)}.    \tag{10}
\]
This follows by substituting \(N=B/c\) and equating errors.

**HEURISTIC.** Substituting the constructive exponents in (5),
\[
p=1+\frac3{d-1},\qquad q=1+\frac5{d-2},
\]
gives
\[
q-p=\frac{2d+1}{(d-1)(d-2)}\sim\frac2d.
\]
With comparable prefactors, (10) is roughly \(c^{d/2}\). Along
\(n=d,\ L=\alpha d\), full-line cost is order \(d^2\), producing an
\(\exp(\Theta(d\log d))\) crossover estimate. A narrow angular window changes the polynomial cost but retains this problematic dimension dependence.

This is not a crossover prediction for ordinary Sobol: its two power exponents and their prefactors have not been established.

---

**Q4. Kernel identity, lower bounds, and plateaus**

**PROVEN.** The kernel identity is correct for scalar-weight quadrature acting componentwise, with nodes and weights independent of the network:
\[
\mathbb E_W\left\|\mu(f_W)-\nu(f_W)\right\|^2
=\iint K(x,x')\,d(\mu-\nu)(x)d(\mu-\nu)(x').       \tag{11}
\]
It is simply expansion of the squared norm followed by Fubini. Randomized rules require an additional expectation over their randomness.

Rotation invariance and positive homogeneity give exactly
\[
K(x,x')=\|x\|\|x'\|\kappa_{n,L}(\widehat x\cdot\widehat x'),
\qquad \kappa_{n,L}(1)=1.
\]
The diagonal normalization follows because each He–ReLU layer preserves expected squared norm.

The finite-width function \(\kappa_{n,L}\) generally differs from
\(C^{\circ L}\).

If the rule selects \(u\), nodes, or weights using the network, (11) with the unconditional kernel is not justified. General matrix-valued output weights also require a matrix-valued kernel rather than this scalar one.

**PROVEN.** Let \(m_d=\mathbb E\chi_d\), and radially push the quadrature measure onto the sphere:
\[
\eta(B)=\frac1{m_d}
 \int \|x\|\mathbf1_{\{\widehat x\in B\}}\,d\nu(x).
\]
The target becomes uniform spherical measure \(\sigma\).

Use the Gegenbauer expansion
\[
\kappa(\theta\cdot\theta')
=\sum_{\ell\ge0}a_\ell P_\ell^{(d)}(\theta\cdot\theta'),
\qquad a_\ell\ge0,\quad \sum_\ell a_\ell=1,
\]
with \(P_\ell^{(d)}(1)=1\). If \(D_\ell\) is the harmonic multiplicity and
\(Y_{\ell j}\) are orthonormal for \(\sigma\), the addition formula gives
\[
\frac{\mathbb E_W\|\mu(f)-\nu(f)\|^2}{m_d^2}
=
a_0(1-\eta(S))^2+
\sum_{\ell\ge1}\frac{a_\ell}{D_\ell}
 \sum_{j=1}^{D_\ell}
 \left|\int Y_{\ell j}\,d\eta\right|^2.           \tag{12}
\]
Every retained term supplies a lower bound. Positivity follows directly from the positive-semidefinite kernel operator.

In particular, for a mass-one rule, put
\(M=\int\theta\theta^\top\,d\eta\).
Since
\[
P_2^{(d)}(t)=\frac{dt^2-1}{d-1},
\]
the degree-two contribution is
\[
m_d^2a_2\,\frac{d\|M\|_F^2-1}{d-1}.
\]
If \({\rm rank}(M)\le r<d\), its real eigenvalues sum to one, so Cauchy–Schwarz gives \(\|M\|_F^2\ge1/r\). Therefore
\[
\mathbb E_W\|\mu(f)-\nu(f)\|^2
\ge m_d^2a_2\frac{d/r-1}{d-1}.                   \tag{13}
\]
This holds for signed weights too.

**PROVEN.** A finite-width coefficient bound makes (13) quantitatively useful. At every width and depth,
\[
\kappa_{n,L}(\rho)=\sum_{j\ge0}b_j\rho^j,
\qquad b_j\ge0,\quad \sum_jb_j=1,
\]
and
\[
b_0\ge\frac1\pi,\qquad
b_2\ge\frac{b_0}{2n},\qquad
b_0\le\frac{m_n^2}{n}.                           \tag{14}
\]

Here are the proofs.

Condition on all layers after the first, and denote their resulting function of a standardized first-layer Gaussian vector by \(F(Z)\). It is positively homogeneous. For two unit inputs of correlation \(\rho\), the corresponding vectors \(Z,Z'\) have coordinatewise Gaussian correlation \(\rho\).

Expand \(F\) in orthonormal multivariate Hermites. The identity
\[
\mathbb E[H_\alpha(Z)H_\beta(Z')]
=\mathbf1_{\{\alpha=\beta\}}\rho^{|\alpha|}
\]
follows by comparing coefficients in the Gaussian exponential generating function. Squared coefficient norms, averaged over the remaining weights, give the nonnegative \(b_j\).

For \(b_0\ge1/\pi\), the first layer gives \(\kappa_{n,1}(0)=1/\pi\).
Moreover \(C(c)\ge c\): its difference from \(c\) decreases to zero at \(c=1\). Conditional application of a fresh layer therefore never decreases expected inner product.

For the degree-two bound, the normalized radial Hermite polynomial is
\[
H_{\rm rad}(Z)=\frac{\|Z\|^2-n}{\sqrt{2n}}.
\]
Write \(Z=R\Theta\). Homogeneity and
\(\mathbb ER^3=(n+1)\mathbb ER\) imply
\[
\mathbb E[F(Z)H_{\rm rad}(Z)]
=\frac{\mathbb EF(Z)}{\sqrt{2n}}.
\]
Its squared norm is part of the degree-two Hermite energy. Averaging proves \(b_2\ge b_0/(2n)\).

Finally,
\[
\|\mathbb EF(Z)\|^2
=m_n^2\|\mathbb E_\Theta F(\Theta)\|^2
\le m_n^2\mathbb E_\Theta\|F(\Theta)\|^2
=\frac{m_n^2}{n}\mathbb E\|F(Z)\|^2.
\]
Average over downstream weights to prove the last inequality.

**PROVEN.** For the actual finite-width ensemble, these facts rule out a dimension-uniform exponent greater than one for **absolute ensemble MSE**, over any budget interval that includes a diverging number of queries below a fixed fraction of \(n\).

This includes arbitrary signed scalar weights and line-plus-radius queries.

To handle weights that do not integrate constants exactly, let
\[
s=\eta(S),\qquad M=\int\theta\theta^\top\,d\eta.
\]
The power-series feature representation and (14) imply, with \(d=n\),
\[
\frac{\operatorname{MSE}}{m_n^2}
\ge b_0\left[(1-s)^2+\frac1{2n}
                    \left\|M-\frac In\right\|_F^2\right].
\]
If \({\rm rank}(M)\le r\), then
\[
\left\|M-\frac In\right\|_F^2
\ge\frac{s^2}{r}-\frac{2s}{n}+\frac1n.
\]
Minimizing this quadratic expression over \(s\) gives
\[
\operatorname{MSE}\ge
\frac{m_n^2b_0}{2n}
\frac{1+1/(2n^2)}{1+1/(2nr)}
\left(\frac1r-\frac1n\right).                    \tag{15}
\]

For \(N\) point queries, \(r\le N\). Each line query is supported in a two-dimensional input plane, so \(N\) line queries give \(r\le2N\). With one common \(u\), the sharper bound is \(r\le N+1\).

Also \(m_n^2/n\ge2/\pi\): use
\(\sum_i|Z_i|\le\sqrt n\|Z\|\) and take expectations.
Combining this with (15) yields the convenient loose bounds
\[
\begin{aligned}
\operatorname{MSE}&\ge\frac1{4\pi^2N},
&&N\le n/2 &&\text{(point queries)},\\
\operatorname{MSE}&\ge\frac1{8\pi^2N},
&&N\le n/4 &&\text{(line queries)}.               \tag{16}
\end{aligned}
\]
These hold at every depth \(L\ge1\), hence along \(L=\alpha n\).
Independent randomization cannot improve them, because the bound holds for every realized rule.

If an upper bound \(C N^{-\gamma}\), with \(C\) independent of \(n\) and \(\gamma>1\), held throughout
\(1\le N\le N_{\max}(n)\), choose
\(N=\min(\lfloor n/4\rfloor,N_{\max}(n))\to\infty\).
Equation (16) contradicts it. This covers polynomial and subexponential upper budget windows.

**PROVEN.** The qualifications to (16) matter:

- It concerns absolute ensemble MSE, not automatically the stipulated per-net nMSE.
- It does not cover network-dependent rules or general nonlinear estimators.
- Its useful query window ends at order \(n\); it does not rule out a faster rate beginning after a dimension-dependent startup budget.
- It does not, by itself, explain the observed plateau at \(N\gg n\).

The exact annealed variance is
\[
\overline V=\mathbb E_W\operatorname{trVar}_Xf_W
=d-m_d^2a_0.
\]
**PROVEN UNDER \(\sup_n\overline V<\infty\) along \(L=\alpha n\).**
Equation (16) gives the same \(c/N\) obstruction for the ratio
\(\mathbb E\|\mathrm{error}\|^2/\overline V\).
I have not independently proved that uniform variance hypothesis here. The actual quantity
\(\mathbb E_W[\|\mathrm{error}\|^2/V_W]\), and medians of per-net nMSE, require a further normalization argument.

**PROVEN.** The GP surrogate cannot safely replace the finite-width kernel in this question. Equation (14) forces
\[
1-b_0\ge1-\frac{m_n^2}{n}
=\frac1{2n}+O(n^{-2}),
\]
whereas the GP composition at depth \(L=\alpha n\) has
\(1-b_0=O(n^{-2})\).

Indeed, the GP surrogate supplies a counterexample to the corresponding absolute-MSE prohibition on a polynomial budget window. Radius-exact MC has risk
\[
\frac{m_d^2(1-a_0)}N
\le \frac{d(1-b_0)}N
=O\!\left(\frac1{dN}\right)
\]
when \(L=\alpha d\). For \(N\le d^p\), this is
\(O(N^{-1-1/p})\), uniformly in \(d\).

The \(L^{-2}\) GP law follows directly from
\[
1-C(1-\delta)
=\delta-\frac{2\sqrt2}{3\pi}\delta^{3/2}
 +O(\delta^{5/2}).
\]
For its iterates, \(\delta_t^{-1/2}\) has increments tending to
\(\sqrt2/(3\pi)\), yielding
\(\delta_t\sim9\pi^2/(2t^2)\).
This GP counterexample and the finite-width lower bound are consistent precisely because the joint limits differ.

**PROVEN.** For larger budgets, a useful restricted bound is available for positive spherical point weights. Define
\[
B_{\ge2r}^{\rm even}=\sum_{j\ge r}b_{2j},\qquad
\mu_{2r}=\mathbb E_{\theta,\theta'}(\theta\cdot\theta')^{2r}
=\frac{(2r-1)!!}{d(d+2)\cdots(d+2r-2)}.
\]
Then
\[
\operatorname{MSE}
\ge m_d^2B_{\ge2r}^{\rm even}
       \left(\frac1N-\mu_{2r}\right).             \tag{17}
\]
For each even degree, nonnegative off-diagonal terms leave at least the diagonal contribution \(\sum_iw_i^2\ge1/N\); its cross term with uniform measure is \(\mu_{2j}\). Sum over \(j\ge r\) and use \(\mu_{2j}\le\mu_{2r}\).

**PROVEN UNDER a nonvanishing high-even-degree energy fraction.**
For \(N\le d^p\), choose a fixed integer \(r>p\). Then
\(N\mu_{2r}\to0\), so (17) gives a normalized \(c/N\) barrier if that even tail carries a fixed fraction of the relevant variance.
That tail hypothesis at finite width and \(L=\alpha n\) has not been proved here. For \(N=\exp(o(n))\), a growing-degree tail estimate would be needed.

**HEURISTIC.** The plateau constants can be interpreted as unresolved spectral energy, but cannot be predicted from the stated degree summaries alone. If a rule eliminates low degrees and its remaining high-degree discrepancies resemble independent sampling, then
\[
N\times\text{normalized error}
\approx\text{fraction of variance left in unresolved modes}.
\]
For a radius-exact mass-one rule the exact annealed expression is
\[
\frac{N\,\operatorname{MSE}}{m_d^2(1-a_0)}
=
\frac{\sum_{\ell\ge1}a_\ell\,N\mathcal E_\ell(\eta)}
     {1-a_0},
\quad
\mathcal E_\ell(\eta)=
\iint P_\ell^{(d)}(\theta\cdot\theta')\,d\eta\,d\eta.
\]
Predicting a plateau needs both the energies \(a_\ell\) and the rule’s transfer factors \(N\mathcal E_\ell\).

Input Hermite degrees, kernel power coefficients \(b_j\), and spherical harmonic energies \(a_\ell\) are different decompositions. In particular, \(b_1=\Theta(L^{-3})\) cannot simply be identified with the measured input degree-one share. Medians of per-net scores additionally require information beyond the averaged kernel.

---

**Q5. Better estimators**

**PROVEN.** The results above do not exclude a dimension-uniform improvement from sampling combined with white-box information. The lower bound (16) specifically applies when the answer is a network-independent scalar linear combination of the queried functionals.

Known integrals of controls, network-dependent adaptations, and nonlinear processing fall outside that proof. Signed weights alone do not escape its quadratic rank obstruction, although the separate high-degree bound (17) does require positivity.

**PROVEN UNDER a uniform approximation-versus-cost hypothesis.** A concrete sufficient condition for an exponent bounded above one is:

1. Construct a surrogate \(p_q\), including its exact integral, for cost \(O(q^a)\).
2. Its residual variance satisfies
   \[
   \operatorname{trVar}(f-p_q)\le Cq^{-b}
   \]
   in the desired normalization, uniformly in width.
3. Evaluating the residual costs a bounded number of forward-pass units.

Then
\[
\widehat\mu=\mu(p_q)+\frac1N\sum_{i=1}^N
                       [f(X_i)-p_q(X_i)]
\]
is unbiased, conditionally on the constructed surrogate, and has MSE at most \(Cq^{-b}/N\). Allocating constant fractions of total compute \(T\) to construction and sampling gives
\[
q\asymp T^{1/a},\qquad N\asymp T,
\qquad
\operatorname{MSE}=O(T^{-1-b/a}).                 \tag{18}
\]
Independent correction samples preserve this statement even when the surrogate was fitted adaptively.

The unresolved ingredient is the width-uniform approximation-versus-cost law, not the correction identity.

**HEURISTIC — the single most promising concrete test.** Add an exact first-layer squared-norm control to the existing multilevel reference-trajectory sampler, keeping its sampling and all other levels unchanged.

There is an inexpensive exact identity behind this test. For uniform \(U\in S^{d-1}\), set
\[
S(U)=\|\operatorname{ReLU}(W_1U)\|^2,\qquad
\bar S=\frac{\|W_1\|_F^2}{2d}.
\]
**PROVEN:** \(\mathbb ES=\bar S\), because symmetry gives
\(\mathbb E(w\cdot U)_+^2=\|w\|^2/(2d)\) row by row.

If the first reference control is \(v\sqrt{S(U)}\), use
\[
p(U)=v\left[\sqrt{\bar S}
                  +\frac{S(U)-\bar S}{2\sqrt{\bar S}}\right],
\qquad
\mathbb Ep=v\sqrt{\bar S}.
\]
**PROVEN:** its residual obeys the exact identity
\[
\sqrt S-\sqrt{\bar S}
-\frac{S-\bar S}{2\sqrt{\bar S}}
=
-\frac{(S-\bar S)^2}
 {2\sqrt{\bar S}(\sqrt S+\sqrt{\bar S})^2},
\]
hence
\[
\operatorname{trVar}(v\sqrt S-p)
\le
\frac{\|v\|^2}{4\bar S^3}\,
       \mathbb E(S-\bar S)^4.                    \tag{19}
\]
It uses values already available from the first prefix and a known integral.

**HEURISTIC.** Test the first-level residual variance and the fully charged error–compute curves across the width ladder. The intended signal is a shrinking residual fraction with width, followed by an improvement in compute slopes rather than only a width-dependent prefactor. This control does not prove that the full quadratic obstruction has been removed, and a successful first-level ablation would still leave the later innovations to analyze.

---

**Single strongest defensible negative — PROVEN.** For the actual Gaussian network ensemble, every network-independent scalar-weight rule using \(N\le n/4\) point or line-plus-radius queries has absolute ensemble MSE at least \(1/(8\pi^2N)\), even with signed weights and independent randomization. Thus no width-uniform exponent \(>1\) holds throughout polynomial or subexponential query-budget windows. The corresponding claim for per-net nMSE, or for a rate beginning beyond order-\(n\) startup cost, is not proved here.

**Single strongest positive possibility — PROVEN UNDER the approximation-versus-cost hypothesis in (18).** An analytically integrated white-box surrogate with a width-uniform residual approximation rate yields a compute exponent \(1+b/a>1\). The first-layer squared-norm control inside multilevel sampling is the concrete test I would prioritize; whether it can support that uniform rate remains unproved.
