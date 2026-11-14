codex
**PROVEN:** the signed rank lemma, its LP combination, and the finite-width crossing law are correct with the qualifications below. The rank method also removes the positivity restriction from my round-1 bound (17).
**PROVEN:** F7(f) needs an additional argument; E1’s \(nL\)-evaluation identifiability assertion is false as stated, and its Gaussian extension needs care with vector outputs.
**CHECKED-NUMERICALLY:** the available degree measurements do not yet establish the requested per-net barrier through \(N=N(d,2)\).

I used the supplied files read-only. Results were changing during the audit; numerical statements below identify the snapshot used.

**PROVEN. F1 is correct for \(d\ge2\).**

Put \(k=d-1\), \(X=\rho\widehat Y+Tu\), where \(\rho\sim\chi_k\), \(T\sim N(0,1)\), and \(\widehat Y\) are independent. Positive homogeneity and the substitution \(T=\rho s\) give
\[
\mathbb E[f(X)\mid\widehat Y]
=\int_{\mathbb R}f(\widehat Y+su)
 \left[\int_0^\infty \rho^2\phi(\rho s)p_{\chi_k}(\rho)\,d\rho\right]ds.
\]
The bracket is
\[
\frac{k}{\sqrt{2\pi}}(1+s^2)^{-(k+2)/2}=w(s),
\]
by the gamma integral in F1. Integrating the bracket first in \(s\) gives
\[
\int w(s)\,ds=\mathbb E\rho.
\]
With \(s=\tan\psi\), homogeneity contributes \(\sec\psi\), the Jacobian contributes \(\sec^2\psi\), and \(w(\tan\psi)\) contributes \(\cos^{k+2}\psi\). This proves the stated \(\cos^{k-1}\psi\) formula.

Finally,
\[
\mathbb E[f(X)\mid\widehat Y]
=\mathbb E\!\left[\mathbb E[f(X)\mid Y]\mid\widehat Y\right].
\]
Conditional expectation contracts \(L^2\), proving the variance comparison with classic pre-integration.

**PROVEN UNDER exact arithmetic and the stated cost convention. F2 is correct.**

On an existing cone, every preactivation is linear. Along its chord it is therefore the linear interpolation of its endpoint values. Opposite strict signs give exactly one interior zero, at the stated \(\lambda\); otherwise there is no interior sign change. Inserting all these zeros makes every activation mask constant on each resulting subcone. ReLU then preserves linearity there, completing the induction.

Positive homogeneity turns each cone into an affine segment of \(s\mapsto f(\widehat Y+su)\). The two unbounded pieces have slopes \(-f(-u)\) and \(f(u)\). Integrating their affine formulas uses only
\[
\int_a^b w(s)\,ds,\qquad
\int_a^b s\,w(s)\,ds,
\]
with the Student-\(t\) CDF and the displayed elementary primitive.

The qualifications are:

- \(\sum_\ell V_{\ell-1}/L\) is the **matvec-equivalent** pass count. The FLOP counter also charges sign tests, new-vertex interpolation, integration, and setup.
- `_propagate` also sorts crossings. Thus the stated arithmetic count is not a complete wall-clock complexity bound.
- Full mode is exact in real arithmetic. Window mode uses a random tail correction and is unbiased, rather than an exact full-line evaluation.

**PROVEN UNDER a weight-independent input arc. F3(a), the corrected F3(b), and E2(c) are consistent.**

For a deterministic previous hidden curve \(h(t)\ne0\), define
\[
v(t)=\frac{\|h(t)\wedge h'(t)\|}{\|h(t)\|^2}.
\]
For a fresh Gaussian row, \(Z(t)=w\cdot h(t)\). Conditional Gaussian regression gives
\[
p_{Z(t)}(0)\,\mathbb E\bigl[|Z'(t)|\mid Z(t)=0\bigr]
=\frac{v(t)}{\pi}.
\]
Indeed, the conditional variance of \(Z'\) is the squared norm of the component of \(h'\) perpendicular to \(h\), times the weight variance; that variance cancels the corresponding factor in \(p_Z(0)\).

Integrating on the finitely many smooth pieces proves
\[
\mathbb E[\text{new strict sign changes per row}\mid\text{past}]
=\frac{\Lambda_{\ell-1}}{\pi}.
\]

The word **new** is essential. On a dead interval, \(Z\equiv0\); its number of zeros is infinite, but it creates no new strict sign changes. Similarly, an inherited vertex with \(h=0\) is a deterministic zero. Thus F3(b)’s claim that zeros at existing vertices have probability zero needs the qualification \(h\ne0\).

For the finite-width expectation, resolve
\[
h'=\beta h+\|h\|v\,e,\qquad e\perp h,\quad\|e\|=1.
\]
A fresh Gaussian matrix sends the normalized value and transverse derivative to independent standard Gaussian vectors \(a,b\). Conditional on \(K\) positive entries of \(a\), the next angular speed divided by \(v\) has distribution
\[
\frac{\chi_{K-1}}{\chi_K},\qquad K\ge2,
\]
with independent numerator and denominator. The numerator is the length of the Gaussian derivative projected perpendicular to the active value vector. The denominator is the active value-vector length.

For \(K\ge2\),
\[
\mathbb E\chi_{K-1}\,\mathbb E\chi_K^{-1}
=
\left(\sqrt2\frac{\Gamma(K/2)}{\Gamma((K-1)/2)}\right)
\left(\frac1{\sqrt2}\frac{\Gamma((K-1)/2)}{\Gamma(K/2)}\right)=1.
\]
For \(K=1\), the output lies on one ray; for \(K=0\), it is zero. Both have zero angular speed. Hence
\[
\mathbb E[v_{\ell}(t)\mid\text{past}]=q_n v_{\ell-1}(t),
\qquad q_n=1-\frac{n+1}{2^n}.
\]
Tonelli’s theorem applies because speeds are nonnegative. For a fixed arc \(A\),
\[
\mathbb E\Lambda_\ell(A)=q_n^\ell |A|,
\qquad
\mathbb E\Delta V_\ell
=\frac{n|A|}{\pi}q_n^{\ell-1}.                 \tag{1}
\]

Thus E2(c)’s count \(nq_n^{\ell-1}\) is the **half-circle** specialization, not the count for an arbitrary-length arc.

The endpoints \(\pm u\) cause no problem. The input arc need only be independent of the weights. Its hidden image is allowed to depend on all previous layers; the next layer remains independent. Sharing those endpoints among multiple lines changes their dependence, but not each line’s expectation.

For retained vertices starting at \(V_0=3\),
\[
\mathbb EV_\ell=3+n\sum_{j=0}^{\ell-1}q_n^j,
\]
and therefore
\[
\frac1L\sum_{\ell=1}^L\mathbb EV_{\ell-1}
=3+\frac nL\sum_{j=0}^{L-2}(L-1-j)q_n^j.       \tag{2}
\]
This proves the cost law in its matvec-equivalent convention. It does not apply unchanged to a direction selected using the network, such as `PI_as`.

**CHECKED-NUMERICALLY.** Formula (2) gives \(3971\) at \(256\times32\) and \(205.2743\) at \(8\times256\). These are ensemble expectations, not predictions for the particular three narrow-deep networks in `pieces.md`.

**PROVEN UNDER transversality. F4 and E2(a) are correct after local/global and genericity qualifications.**

Choose unit facet normals \(a_j\) and write the Jacobian jump as
\[
A_j^+-A_j^-=v_j a_j^\top.
\]
Continuity implies this form because the two linear maps agree on the facet’s tangent space. Distributionally,
\[
D^2f=\sum_j v_j\,a_j\otimes a_j\,
                  \mathcal H^{d-1}\!\restriction F_j.
\]
There are no extra ridge terms: this differentiates a piecewise-constant first derivative.

Let \(P=I-uu^\top\), \(\alpha_j=a_j\cdot u\ne0\), and
\[
t_j(y)=-\frac{a_j\cdot y}{\alpha_j}.
\]
Integrating a facet measure along \(u\) contributes \(1/|\alpha_j|\), so
\[
D^2H_p(y)=
\sum_j
 \frac{v_j(Pa_j)\otimes(Pa_j)}{|\alpha_j|}
 p(t_j(y))
 \mathbf1_{\{y+t_j(y)u\in F_j\}}                 \tag{3}
\]
almost everywhere, where \(H_p(y)=\int f(y+tu)p(t)\,dt\). Consequently,
\[
\|D^2H_p\|_\infty
\le \|p\|_\infty
 \sum_j\frac{\|v_j\|\|Pa_j\|^2}{|\alpha_j|}.
\]
This proves a globally Lipschitz gradient.

On each cell avoiding projected ridges, the crossed facets and their order are fixed. Their crossing parameters are affine, and the relevant Gaussian or Student primitives are real analytic. This proves F4(i). Formula (3) proves F4(ii)–(iv), including the piecewise-linear fold assertion.

Two corrections:

1. On all of \(u^\perp\), write \(W^{2,\infty}_{\mathrm{loc}}\), with bounded first and second derivatives. The function itself can grow linearly and need not belong to global \(W^{2,\infty}\) or global unweighted \(H^s\).
2. F4(v)’s unconditional “has a kink” is too strong. A parallel facet **can** leave a kink; contributions can also cancel. For example,
   \[
   f(y,t)=\operatorname{clip}(t,-|y|,|y|)
   \]
   is continuous, piecewise linear, homogeneous, and has facets parallel to the \(t\)-direction. It is odd in \(t\), so integration against an even weight is identically zero.

**PROVEN.** The sharpness example \(f(a,t)=(a+|t|)_+\) gives
\[
g''(a)=2\phi(a)\mathbf1_{\{a<0\}},
\]
so \(C^{1,1}\) cannot generally be strengthened to \(C^2\).

For a fixed finite transverse fan, (3) is piecewise smooth with finitely many interfaces. A bounded piecewise-smooth function \(A\) satisfies, locally,
\[
\|A(\cdot+h)-A\|_2^2=O(|h|).
\]
The interface-crossing region has volume \(O(|h|)\); away from it the contribution is \(O(|h|^2)\). The fractional Sobolev integral consequently converges for orders below \(1/2\). Applying this to \(Df\) and \(D^2H_p\) proves
\[
f\in H^{3/2-}_{\rm loc},\qquad
H_p\in H^{5/2-}_{\rm loc},
\]
and the corresponding compact-sphere statements in E2(a).

**PROVEN UNDER the constructed cubature algorithm. E2(b)’s achievable exponents are correct.**

In intrinsic dimension \(D\), use cells of diameter \(h\), with \(N\asymp h^{-D}\). There are \(O(h^{-(D-1)})\) cells intersecting interfaces.

For the original spherical function, affine interpolation leaves residual \(O(h)\) in interface cells and \(O(h^2)\) elsewhere. Independent residual sampling gives total variance
\[
O(h^{D+3})+O(h^{D+4}).
\]
For the integrated function, quadratic interpolation leaves residual \(O(h^2)\) in interface cells and \(O(h^3)\) elsewhere, giving
\[
O(h^{D+5})+O(h^{D+6}).
\]
This proves the two stated achievable rates. Their constants depend on dimension and the fan.

These are upper bounds for that construction, not optimality claims or established exponents for the implemented Sobol method. My round-1 \(o(N^{-1})\) proof assumed the bounded-gain variance formula and eventual elimination of every fixed finite collection of components. `lib/est.py` uses SciPy LMS scrambling plus a digital shift; applying that proof to this implementation requires its corresponding scrambling theorem.

---

**PROVEN. F7(a)–(c) are correct for network-independent scalar-weight rules with finite second moments.**

The kernel is positive definite because
\[
\sum_{i,j}c_ic_jK(x_i,x_j)
=\mathbb E_W\left\|\sum_i c_i f_W(x_i)\right\|^2\ge0.
\]
Input rotation invariance follows from the law of \(W_1Q\), and homogeneity supplies the radial factors. The positive spherical harmonic coefficients then follow from the spectral decomposition of the positive, rotation-invariant kernel operator.

The error identity follows by expanding the squared norm and applying Fubini. Every nonconstant harmonic integrates to zero against uniform spherical measure, proving the displayed expansion.

For the following proofs, normalize the radially pushed rule by \(m=\mathbb E\chi_d\). Let its signed spherical measure be \(\eta\), with mass \(s\). Then
\[
\mathcal R
=m^2\left[a_0(1-s)^2+\sum_{k\ge1}a_kQ_k\right],
\qquad
Q_k=\iint P_k(x\cdot y)\,d\eta(x)d\eta(y)\ge0.   \tag{4}
\]
This is the same normalization as F7, with its \(v_i\) divided by \(m\).

The independence qualification excludes active-subspace directions or other designs chosen from the network unless a separate argument is supplied.

**PROVEN. F7(d) and E2(f) are correct for signed weights.**

Write \(D_j=N(d,j)\). The addition formula gives
\[
\phi_j(x)\cdot\phi_j(y)=D_jP_j(x\cdot y),
\qquad \|\phi_j(x)\|^2=D_j.
\]
For
\[
A=\sum_{i=1}^Nw_i\phi_j(x_i)\phi_j(x_i)^\top,
\]
we have
\[
\operatorname{rank}A\le N,\quad
\operatorname{tr}A=D_js,\quad
\|A\|_F^2=D_j^2\sum_{i,i'}w_iw_{i'}P_j(x_i\cdot x_{i'})^2.
\]
If \(\lambda_1,\ldots,\lambda_r\) are its nonzero eigenvalues, ordinary Cauchy–Schwarz gives
\[
\left(\sum_{\ell=1}^r\lambda_\ell\right)^2
\le r\sum_{\ell=1}^r\lambda_\ell^2.
\]
No eigenvalue sign assumption appears.

The kernel \(P_j^2\) is positive definite because it is the feature kernel of \(\phi_j\otimes\phi_j\). Its Gegenbauer expansion therefore has nonnegative coefficients. Parity and degree give support on even degrees at most \(2j\); evaluation at \(1\) gives total coefficient mass \(1\); orthogonality gives
\[
\pi^{(j)}_0=\int P_j(x\cdot y)^2\,d\sigma(y)=\frac1{D_j}.
\]
Consequently,
\[
\sum_{k\ge1}\pi^{(j)}_kQ_k
\ge s^2\left(\frac1N-\frac1{D_j}\right)_+.       \tag{5}
\]
The positive part is legitimate because the left side is nonnegative.

**PROVEN. The line rank bound is correct, and a common direction gives a refinement.**

Restrict a homogeneous degree-\(j\) polynomial to a two-dimensional plane. It is a linear combination of the \(j+1\) monomials
\[
a^j,a^{j-1}b,\ldots,b^j.
\]
Thus the vectors \(\phi_j(x)\) along that plane span at most \(j+1\) dimensions. An integral of their outer products, with either sign of measure, has range inside that span. For \(N\) line measures,
\[
r_j\le N(j+1).
\]
Radius integration changes the measure, not the supporting plane or this rank argument.

If all lines share \(u\), their feature spans all contain \(\phi_j(u)\). Hence the stronger bound
\[
r_j\le 1+Nj                                                   \tag{6}
\]
is available. Replace \(1/N\) in (5) by \(1/r_j\). For \(j=1\), (6) recovers \(r_1\le N+1\).

**PROVEN. F7(e)’s LP and minimization are correct.**

For any feasible nonnegative \(\alpha_j\),
\[
\sum_{k\ge1}a_kQ_k
\ge\sum_j\alpha_j\sum_{k\ge1}\pi^{(j)}_kQ_k
\ge Bs^2,
\]
where
\[
B=\sum_j\alpha_j\left(\frac1{r_j}-\frac1{D_j}\right)_+.
\]
The first inequality uses both coefficient feasibility and \(Q_k\ge0\). Minimizing
\[
a_0(1-s)^2+Bs^2
\]
gives \(s=a_0/(a_0+B)\) and
\[
\boxed{\mathcal R\ge m^2\frac{a_0B}{a_0+B}.}                   \tag{7}
\]
When the rule has mass one, the stronger bound is simply \(\mathcal R\ge m^2B\). Interpret the expression as zero if \(a_0=B=0\).

**PROVEN. My round-1 bound (17) also holds for signed point weights.**

This corrects my round-1 positivity restriction.

Use the tensor feature
\[
\psi_j(x)=x^{\otimes j},\qquad \|\psi_j(x)\|=1,
\]
and the symmetric matrix
\[
T_j=\int\psi_j(x)\psi_j(x)^\top\,d\eta(x).
\]
For \(N\) points, \(\operatorname{rank}T_j\le N\) and \(\operatorname{tr}T_j=s\). Therefore
\[
\iint(x\cdot y)^{2j}\,d\eta(x)d\eta(y)
=\|T_j\|_F^2\ge \frac{s^2}{N}.
\]
Let
\[
\mu_{2j}=\int(x\cdot y)^{2j}\,d\sigma(y)
=\frac{(2j-1)!!}{d(d+2)\cdots(d+2j-2)}.
\]
The discrepancy for the kernel \(t^{2j}\) consequently satisfies
\[
\mathcal E_{2j}(\eta)
\ge
s^2\left(\frac1N-\mu_{2j}\right)
+\mu_{2j}(1-s)^2.                               \tag{8}
\]
For \(s=1\), summing (8) against nonnegative power coefficients gives
\[
\boxed{
\mathcal R\ge
m^2\left(\sum_{j\ge r}b_{2j}\right)
\left(\frac1N-\mu_{2r}\right).
}                                                               \tag{9}
\]
Thus (17) extends to signed weights exactly as hoped, using tensor features.

For lines, the same tensor restriction argument gives \(r_j\le N(j+1)\), or \(1+Nj\) with common \(u\). One must retain that \(j\)-dependence when summing a tail.

**PROVEN by counterexample. F7(f) does not follow from aggregate high-even spherical energy alone.**

Here is an explicit obstruction even for mass-one signed rules.

For \(d\ge11\), take the \(3d-2\) nodes
\[
e_1,\quad e_i,\quad \frac{e_1+e_i}{\sqrt2},\quad
\frac{e_1-e_i}{\sqrt2}\qquad (i=2,\ldots,d),
\]
with weights
\[
w(e_1)=\frac{7-d}{2(d+2)},\qquad
w(e_i)=-\frac1{2(d+2)},\qquad
w\!\left(\frac{e_1\pm e_i}{\sqrt2}\right)=\frac1{d+2}.
\]
They sum to one. Expanding fourth powers gives
\[
\sum_iw_i(x_i\cdot z)^4
=\frac3{d+2}\|z\|^2z_1^2.                       \tag{10}
\]
Every degree-4 harmonic has a symmetric traceless coefficient tensor. Contracting such a tensor with the right side of (10) is zero because of the factor \(\|z\|^2\). Hence this rule integrates **every degree-4 harmonic exactly**.

Now take
\[
\kappa(t)=a_0+a_4P_4(t),\qquad a_0,a_4>0.
\]
The quadrature error is zero, while all its nonconstant energy is in degree \(4\). Moreover,
\[
D_2=\frac{(d+2)(d-1)}2\ge 2(3d-2)
\]
for \(d\ge11\). This satisfies the proposed high-even dimension condition.

This disproves the deduction from harmonic energy alone. It is not a counterexample to the Gaussian-network ensemble, which has additional power-series structure.

**PROVEN UNDER the normalized \(H_{\rm even}\) hypothesis, fixed polynomial budget exponent, and \(N\to\infty\). F7(f) can be repaired for the actual finite-width ensemble.**

The extra ingredient is
\[
\kappa(t)=\sum_{\ell\ge0}b_\ell t^\ell,\qquad
b_\ell\ge0,\quad \sum_\ell b_\ell=1,\quad b_0\ge1/\pi.
\]
These are the finite-width facts used in E2(e).

Let
\[
r=\min\{j:D_j\ge2N\},\qquad N\le d^p
\]
for fixed \(p\). Then \(r\) stays bounded as \(d\to\infty\). Define
\[
A_{\ge2r}^{\rm even}=\sum_{j\ge r}a_{2j},\qquad
B_{\ge2r}^{\rm even}=\sum_{j\ge r}b_{2j}.
\]
Nonnegative monomial-to-Gegenbauer coefficients imply
\[
B_{\ge2r}^{\rm even}\ge A_{\ge2r}^{\rm even}.                  \tag{11}
\]

To handle the threshold power \(t^{2r}\), write
\[
t^r=\gamma_rP_r(t)+h(t),
\qquad
\gamma_r=\prod_{\ell=0}^{r-1}
 \frac{d-2+\ell}{d-2+2\ell}=1-O_p(d^{-1}).
\]
The remaining kernel \(h\) has nonnegative Gegenbauer coefficients. Therefore
\[
t^{2r}-\gamma_r^2P_r^2=2\gamma_rP_rh+h^2
\]
is positive definite. Its discrepancy is nonnegative, and (5) gives
\[
\mathcal E_{2r}(\eta)\ge
\frac{\gamma_r^2s^2}{2N}.
\]
For every higher even power, (8) gives
\[
\mathcal E_{2j}(\eta)
\ge s^2\left(\frac1N-\mu_{2r+2}\right),\qquad j\ge r+1.
\]
Since
\[
N\mu_{2r+2}\le \frac{D_r}2\mu_{2r+2}=O_p(d^{-1}),
\]
the entire even power tail contributes at least
\[
\left(\frac12-O_p(d^{-1})\right)
\frac{s^2B_{\ge2r}^{\rm even}}N.                 \tag{12}
\]
Add \(b_0(1-s)^2\) and minimize over \(s\). Because \(b_0\ge1/\pi\), the mass-relaxation factor is \(1-O(1/N)\).

Thus, with the dimensionally consistent hypothesis
\[
m^2A_{\ge2r}^{\rm even}\ge c\,\overline V,
\qquad
\overline V=\mathbb E_W\operatorname{trVar}_X f_W,
\]
we obtain
\[
\boxed{
\frac{\mathbb E_W\|\mathrm{error}\|^2}{\overline V}
\ge
\frac{c/2-O_p(d^{-1})-O(N^{-1})}{N}.
}                                                               \tag{13}
\]

This repairs the point-rule corollary in the actual ensemble. It uses more than F7(d)–(e), and it concerns a ratio of ensemble expectations. It is not automatically a result about \(\mathbb E_W[\mathrm{MSE}_W/V_W]\), medians, individual networks, or arbitrary line rules.

**PROVEN. E2(d) and the explicit finite-width lower bounds in E2(e) survive.**

For completeness, the coefficient facts have short proofs.

Condition on the downstream weights and view the output as a homogeneous function \(F(Z)\) of a standardized first-layer Gaussian vector. Orthogonal Hermite expansion and
\[
\mathbb E[H_\alpha(Z)H_\beta(Z')]
=\mathbf1_{\alpha=\beta}\rho^{|\alpha|}
\]
give nonnegative \(b_j\). He initialization preserves expected squared norm, giving \(\sum b_j=1\).

The first layer has \(\kappa(0)=1/\pi\). A fresh layer replaces a conditional correlation \(c\) by \(C(c)\ge c\), so \(b_0=\kappa(0)\ge1/\pi\).

Writing \(Z=R\Theta\) and using \(\mathbb ER^3=(n+1)\mathbb ER\),
\[
\mathbb E\!\left[
F(Z)\frac{\|Z\|^2-n}{\sqrt{2n}}
\right]
=\frac{\mathbb EF(Z)}{\sqrt{2n}}.
\]
This radial degree-2 Hermite coefficient gives \(b_2\ge b_0/(2n)\). Jensen gives
\[
\|\mathbb EF(Z)\|^2
\le\frac{m_n^2}{n}\mathbb E\|F(Z)\|^2,
\]
hence \(b_0\le m_n^2/n\).

Since
\[
t^2=\frac1n+\frac{n-1}{n}P_2(t),
\]
we have \(a_2\ge b_2(n-1)/n\). The \(j=1\) rank bound therefore supplies
\[
B\ge\frac{b_0}{2n}\left(\frac1r-\frac1n\right).
\]
For \(r\le n/2\), \(B\le b_0\), and (7) yields
\[
\mathcal R\ge
\frac{m_n^2b_0}{4n}\left(\frac1r-\frac1n\right)
\ge\frac1{4\pi^2r}.
\]
Here \(m_n^2/n\ge2/\pi\) follows by taking expectations in
\(\sum_i|Z_i|\le\sqrt n\|Z\|\).

Taking \(r=N\) or \(r=2N\) proves the quoted point and line constants. The normalized conclusion still needs its stated variance hypothesis and normalization distinction.

E2(d)’s GP warning is also correct: its \(b_0\) is a **power-series coefficient**, not the spherical coefficient \(a_0\). The finite-width inequality \(1-b_0\gtrsim1/(2n)\) conflicts with the GP composition’s \(O(n^{-2})\) behavior along \(L=\alpha n\).

---

**PROVEN UNDER a Gaussian prior, squared loss, continuous linear information, and fixed cardinality. The central mathematical assertion in E1(a) is correct.**

For fixed observations \(Y\) and target \(S\), joint Gaussianity gives
\[
\mathbb E[S\mid Y]
=\mathbb ES+\operatorname{Cov}(S,Y)
 \operatorname{Cov}(Y,Y)^\dagger(Y-\mathbb EY).
\]
The conditional mean minimizes squared error, so the optimal algorithm is affine, or linear after subtracting the known mean.

For adaptive linear observations, apply Gaussian conditioning sequentially. The posterior covariance depends on the realized list of functionals, not additionally on their observed values. For every realized list, its residual risk is at least the minimum over deterministic lists of the same cardinality. Averaging proves that adaptive selection cannot beat the optimal nonadaptive design.

Point evaluations are not continuous functionals on bare \(L^2\). One can formulate this problem on continuous functions on the sphere, with the homogeneous extension supplying Gaussian-input integration. Point and line functionals are then bounded.

I have not verified the full cited papers, so I would use this explicit theorem rather than an unrestricted citation-based claim about all orthogonally invariant measures. “Orthogonally invariant” also requires the covariance-adapted meaning; a general Gaussian measure is not invariant under arbitrary ordinary rotations of its ambient coordinates.

**PROVEN UNDER an independent scalar scale mixture of a centered Gaussian prior. The fixed-cardinality result extends to that mixture.**

Let \(f=AG\), with \(A\ge0\), \(A\) independent of centered Gaussian \(G\), and \(\mathbb EA^2<\infty\). Conditional on \(A\), the Gaussian regression coefficient is unchanged by scaling. Thus the conditional mean remains the same linear regression in the observations.

For an adaptive realized list \(\mathcal L\), posterior risk is
\[
\mathbb E[A^2\mid\text{data}]\,r_G(\mathcal L).
\]
Since \(r_G(\mathcal L)\ge\inf_{\mathcal L'}r_G(\mathcal L')\), averaging proves the same nonadaptivity result.

This does not establish that the actual random-network prior is such a scale mixture. A roughly lognormal norm distribution is insufficient.

**PROVEN. Varying cardinality needs a separate budget statement.**

With a hard cap \(N\), padding unused observations reduces the problem to fixed cardinality.

For a Gaussian prior under an **expected** cardinality budget, let \(e_N^2\) be the optimal fixed-cardinality squared error. Any variable-cardinality procedure has risk at least \(\mathbb E[e_M^2]\). Independent randomization between fixed-cardinality optimal designs attains the lower convex envelope of the sequence \(e_N^2\). Thus convexity of the squared-error sequence is the relevant sufficient condition for no improvement.

For a scale mixture, the factor \(\mathbb E[A^2\mid\text{data}]\) can correlate with the chosen cardinality. The preceding convexity argument does not transfer unchanged.

**PROVEN by counterexample. E1(b) cannot extend the scalar trace-kernel bound to every vector-valued Gaussian algorithm without an additional covariance argument.**

Optimal Gaussian regression can use **matrix-valued output weights**, whereas F7 controls common scalar weights.

For example, let
\[
f(r\theta)=r\,(Z,H_2(\theta)),
\]
where \(Z\) is Gaussian and \(H_2\) is an independent isotropic Gaussian degree-2 harmonic. Its trace kernel is
\[
\kappa(t)=a_0+a_2P_2(t),\qquad a_0,a_2>0.
\]
One vector evaluation reveals \(Z\), and the integral is exactly \((mZ,0)\). Thus a matrix-weight linear algorithm has zero error after one evaluation. The common-scalar-weight rank bound is positive.

A sufficient repair is scalar output, or separable covariance
\[
C(x,x')=k(x,x')\Sigma,
\]
for which the optimal componentwise regression uses common scalar spatial weights. Otherwise, analyze the full matrix-valued covariance, for example by output covariance channels. Subtracting the known mean correctly changes only the trace kernel’s degree-0 coefficient, but does not resolve this issue.

**PROVEN. E1(c)’s identifiability conclusion is wrong as stated.**

Parameter counting supplies necessary local dimension conditions, not injectivity.

Even before additional degeneracies, hidden-unit positive rescalings remove \(n(L-1)\) continuous dimensions, giving the nominal quotient count
\[
n^2L-n(L-1).
\]
Permutations are discrete. But one evaluation does not generally supply \(n\) independent local equations: at an output coordinate with strictly negative final preactivation, ReLU returns zero throughout an open parameter neighborhood. That observation supplies an inequality and has zero local derivative. Approximately half the final coordinates are inactive in the nondegenerate symmetric model.

There are also open parameter sets with dead hidden units or dead layers. For instance, an all-negative matrix after a ReLU layer kills every nonnegative hidden vector. Such nonidentifiability is not removed by the usual scaling/permutation quotient.

More decisively, finitely many evaluations can miss an arbitrarily narrow activation cone. For any finite nonzero sample set, choose \(b\) with \(b\cdot x_i\ne0\), then choose \(a,K\) so that
\[
g(x)=\bigl(a\cdot x-K|b\cdot x|\bigr)_+
\]
vanishes strictly at those samples but is positive somewhere. This has a width-3, two-layer realization:
\[
g(x)=
\operatorname{ReLU}\!\left(
\operatorname{ReLU}(a\cdot x)
-K\operatorname{ReLU}(b\cdot x)
-K\operatorname{ReLU}(-b\cdot x)\right).
\]
The strict inequalities persist under small parameter perturbations. Additional outputs can be dead, and additional layers can transmit the surviving ray. Therefore an open family of networks agrees at all sampled points while having different integrals.

The same construction applies to the finite query list encountered along an adaptive algorithm’s all-zero transcript.

Consequently, neither “\(nL\) generic evaluations identify \(W\)” nor “all nonlinear information lower bounds end at \(N\sim nL\)” follows. A recovery theorem would need visibility, nondegeneracy, query-design, and injectivity hypotheses. This correction does not itself prove a \(c/N\) nonlinear lower bound.

**CHECKED-NUMERICALLY. E1(d)’s measurements are descriptive; one claimed diagnostic interpretation needs correction.**

At the 14:50Z read, the larger runs reported scaled one-point-error excess kurtoses approximately \(5.68,7.57,6.05,8.76\) at widths \(32,64,128,256\). Their reported log-norm variances were about \(0.67\)–\(0.73\).

**PROVEN.** Dividing by a network’s own spatial RMS does **not** make a pure Gaussian scale mixture have zero excess kurtosis. For the Gaussian process \(G(x)=Zg(x)\), with \(g\) centered spatially, that normalization leaves a fixed multiple of \(\operatorname{sign}Z\) at a fixed input, whose excess kurtosis is \(-2\). Thus the corresponding comment in `scratch/nongauss.py` is false.

Also, exact finite-width ReLU networks have positive probability of a zero norm. Unconditional \(\log\|h_L\|^2\) then takes the value \(-\infty\). The script measures a clipped log norm; theoretical log-norm assertions require a survival or regularization qualification.

---

**PROVEN. The per-net rotation theorem is exact, but it requires the LP certificate rather than just an even-energy total.**

Fix a network and write \(F(\theta)=f(\theta)\). Let
\[
a_k=\|\operatorname{Proj}_{\mathcal H_k}F\|_{L^2(\sigma)}^2,
\qquad
V_{\rm ang}=\sum_{k\ge1}a_k,\qquad
a_0=\|\mathbb E_\sigma F\|^2.
\]
Haar averaging the kernel \(F(Rx)\cdot F(Ry)\) eliminates cross-degree terms. Within each degree, rotation invariance makes the coefficient covariance a scalar multiple of the identity; its trace is \(a_k\). The addition formula therefore gives
\[
\mathbb E_R[F(Rx)\cdot F(Ry)]=\sum_k a_kP_k(x\cdot y).
\]
Consequently, (4)–(7) hold exactly for this fixed net and a rule subjected to an independent Haar rotation.

The base rule must be fixed before that rotation. Selecting nodes or weights from evaluations of the rotated integrand is outside this identity.

For normalization,
\[
V_{\rm plain}
=dV_{\rm ang}+(d-m^2)a_0,\qquad
V_{\rm RB}=m^2V_{\rm ang}.                       \tag{14}
\]
For a mass-one rule,
\[
\boxed{
\mathbb E_R[\mathrm{nMSE}]
\ge \frac{m^2B}{V_{\rm plain}}.
}                                                               \tag{15}
\]
For arbitrary mass, use (7) instead.

A fixed net’s rotation-averaged kernel need not have nonnegative **power-series** coefficients. Thus the ensemble repair (13) does not automatically transfer to individual networks.

**PROVEN. Degrees \(1,2,\text{odd},\text{even}\ge4\) do not suffice to certify the requested range through \(N=D_2\).**

For \(j=2\),
\[
P_2^2=
\frac{2}{(d-1)(d+2)}P_0
+\frac{4(d-2)}{(d-1)(d+4)}P_2
+\frac{d^2(d+1)}{(d-1)(d+2)(d+4)}P_4.
\]
Thus one may take
\[
\alpha_2=
\min\!\left(
 \frac{a_2}{\pi^{(2)}_2},
 \frac{a_4}{\pi^{(2)}_4}
\right).
\]
This needs **degree 4 itself**, not the aggregate \(\sum_{k\ge4,\ k\text{ even}}a_k\).

Moreover, its rank gain vanishes at \(N=D_2\). To cover that endpoint using the next test kernel requires \(j=3\), hence individual energies \(a_2,a_4,a_6\). Higher tests may be needed if one of those coefficients is a bottleneck.

**CHECKED-NUMERICALLY. The 14:53:37Z artifact snapshot was:**

| \(n\) | Seed | Degree 1 / \(V_{\rm ang}\) | Degree 2 / \(V_{\rm ang}\) | Odd / \(V_{\rm ang}\) | Even \(\ge4\) / \(V_{\rm ang}\) |
|---:|---:|---:|---:|---:|---:|
| 32 | 302 | .5200 | .2826 | .6416 | .0759 |
| 32 | 303 | .5078 | .2679 | .6418 | .0942 |
| 64 | 302 | .4800 | .2536 | .6355 | .1085 |
| 64 | 303 | .3636 | .2400 | .5907 | .1725 |
| 128 | 302 | .3579 | .2329 | .5856 | .1719 |
| 128 | 303 | .2143 | .1888 | .5432 | .2637 |
| 256 | 201 | .3263 | .4464 | .5562 | −.0030 |
| 256 | 202 | .2545 | −.1206 | .5662 | .5593 |

All these files reported \(M=16384\). Files were being overwritten with revised estimates during this audit; the JSON does not identify the estimator version.

The negative entries cannot be true energies. They demonstrate unresolved estimator noise, not negative spectrum. The total even-energy estimates, roughly \(0.36\)–\(0.45\), suggest substantial even angular variation on these nets. These data do not resolve the individual degree-4/6 energies or establish a width-uniform lower bound.

**PROVEN. The degree-energy formulas in `scratch/degrees.py` are correct.**

Let
\[
C_1=\mathbb E[F(U)U^\top],\qquad
C_2=\mathbb E\!\left[F(U)(UU^\top-I/d)\right].
\]
Then
\[
a_1=d\|C_1\|_F^2,\qquad
a_2=\frac{d(d+2)}2\|C_2\|_F^2.                  \tag{16}
\]
The first identity follows from \(\mathbb EUU^\top=I/d\). For symmetric trace-free matrices,
\[
\mathbb E[(U^\top AU)(U^\top BU)]
=\frac{2\operatorname{tr}(AB)}{d(d+2)},
\]
which follows by contracting the sphere’s fourth-moment tensor. This gives the second identity.

The original independent-half products were unbiased for these energies. Their ratios to an estimated variance are not exactly unbiased, and energy differences can be negative.

**PROVEN. The revised cross-centering has a tiny upward bias, despite its “keeps unbiasedness” comment.**

The version read at 14:54Z centers half \(A\) with half \(B\)’s output mean, and vice versa. Let \(h(U)\) be any zero-mean feature, \(C=\mathbb E[Fh^\top]\), and let both halves have size \(m_h\). Write
\[
\widehat C_A=T_A-\overline F_B\overline h_A^\top,\qquad
\widehat C_B=T_B-\overline F_A\overline h_B^\top.
\]
Expanding their inner product, the two mixed terms have zero expectation because the independent feature mean has expectation zero. The final term has expectation \(\|C\|_F^2/m_h^2\), since
\[
\mathbb E[\overline F_A\overline h_A^\top]=C/m_h.
\]
Therefore
\[
\mathbb E\langle\widehat C_A,\widehat C_B\rangle
=(1+m_h^{-2})\|C\|_F^2.                         \tag{17}
\]
At \(m_h=8192\), this relative bias is only \(1.49\times10^{-8}\). It does not explain the large fluctuations.

A simple exact correction is division by \(1+m_h^{-2}\). A cleaner alternative is an independently centered coefficient estimate within each half:
\[
\widetilde C_A=
\frac1{m_h-1}\sum_{i\in A}
 (F(U_i)-\overline F_A)h(U_i)^\top.
\]
Its expectation is \(C\), and the two halves remain independent.

Use \(F_{\rm odd}\) for degree 1 and \(F_{\rm even}\) for degree 2 to eliminate irrelevant parity noise.

**PROVEN. The following estimator supplies the missing higher-degree measurements.**

For independent uniform \(U,V\),
\[
a_k=D_k\,\mathbb E\!\left[
F(U)\cdot F(V)P_k(U\cdot V)
\right].                                                       \tag{18}
\]
This is the addition formula followed by orthogonality. For even \(k\), replace \(F\) by its even part. For \(k\ge1\), subtract any fixed vector, or a vector from an independent pilot, without changing the expectation.

Thus the practical measurement specification is:

1. Estimate \(a_2,a_4,a_6\) separately with independent blocks, using coefficient products or the kernel U-statistic (18).
2. Report block uncertainty and estimator version; do not clip negative point estimates and treat them as evidence.
3. Feed simultaneous lower confidence bounds for the individual energies into the LP.
4. Evaluate \(Nm^2B_N/V_{\rm plain}\) over the intended \(N\)-range.

The higher-degree estimator can be noisy because of \(D_k\). Its unbiasedness does not guarantee a useful sample size.

For a fully rigorous, though generally loose, alternative, use independent pairs in (18). If \(\|F-c\|\le M_c\), each summand is bounded in absolute value by \(D_kM_c^2\), so Hoeffding bounds provide simultaneous lower confidence bounds. A deterministic bound is available from the product of layer operator norms. This specifies a valid certificate even when the resulting confidence interval is too wide to be useful.

---

**PROVEN UNDER its stated cost and approximation hypotheses. E2(g), including route (18), is correct.**

Conditional on an independently constructed surrogate,
\[
\widehat\mu=\mu(p_q)+\frac1N\sum_{i=1}^N(f(X_i)-p_q(X_i))
\]
is unbiased and has MSE \(\operatorname{trVar}(f-p_q)/N\). Construction cost \(O(q^a)\), bounded residual-evaluation cost, and residual variance \(O(q^{-b})\) give the stated exponent \(1+b/a\).

The bounded evaluation-cost assumption matters. If residual evaluation costs \(O(q^\gamma)\), the same allocation instead gives
\[
\mathrm{MSE}=O\!\left(T^{-1-(b-\gamma)/a}\right)
\]
when this allocation is feasible; an improvement requires \(b>\gamma\).

**PROVEN. The first-layer control is valid, but expanding only linear combinations of squared hinges cannot supply the desired family.**

For
\[
S(U)=\sum_i(w_i\cdot U)_+^2,
\]
symmetry gives
\[
\mathbb ES=\frac{\|W_1\|_F^2}{2d}.
\]
The square-root Taylor remainder identity in round 1 is exact, so its variance bound remains valid.

However,
\[
\frac{(a\cdot U)_+^2+(-a\cdot U)_+^2}{2}
=\frac12(a\cdot U)^2.
\]
Hence any surrogate made from constants, linear functions, and arbitrary linear combinations of squared hinges has no even harmonic components of degree at least 4. For every such surrogate,
\[
\|F-p_q\|_{L^2}^2\ge
\sum_{\substack{k\ge4\\k\ {\rm even}}}a_k.        \tag{19}
\]
Adding more squared-hinge controls cannot remove this floor. This is a concrete obstruction to turning the single proposed control into an exponent-improving family.

**HEURISTIC. I do not currently have evidence for an affordable family with a width-uniform positive \(b\) at \(L=n/8\).**

The most concrete broader family worth a bounded test is a fitted collection of **biased Gaussian ridge controls**
\[
p_q(x)=a+Bx+\sum_{r=1}^qv_r(a_r\cdot x-t_r)_+.
\]
Choose candidate normals using first-layer rows and sampled input-space gate normals from the known weights, then fit vector coefficients. Nonzero thresholds allow both parities and higher even degrees. Every control has a known Gaussian integral:
\[
\mathbb E(a_r\cdot X-t_r)_+
=\sigma_r\phi(t_r/\sigma_r)
-t_r\Phi(-t_r/\sigma_r),
\qquad \sigma_r=\|a_r\|.
\]
Thus the integral of the fitted surrogate is analytic.

A width-uniform approximation rate for this family would require a substantive approximation-norm bound. Depth proportional to width gives no evident bound of that kind.

**HEURISTIC. The cheapest useful falsification test is a nested-dictionary residual test, before running integration curves.**

Fit a doubling sequence of dictionary sizes on one training pool, evaluate on an independent held-out pool, and charge feature construction, fitting, and evaluation. Estimate residual variance without a truth integral using
\[
\frac12\mathbb E\|r_q(X)-r_q(X')\|^2
=\operatorname{trVar}(r_q).
\]
Test a specified \(C,b\) across the width ladder, in both absolute and normalized units. A persistent floor or evaluation cost that consumes the variance improvement rejects that proposed useful law. Finite experiments cannot rule out every arbitrarily slow asymptotic \(b>0\).

---

**PROVEN. The main interpretive issue in D is that the reported “line worth” is a variance ratio, not an equivalent point count.**

`scratch/posthoc_matched.py` computes
\[
r(N)=\frac{\mathrm{MSE}_{\rm point}(N)}
           {\mathrm{MSE}_{\rm line}(N)}.
\]
If point error is \(AN^{-\alpha}\), the equivalent number of points is
\[
N_{\rm equiv}=N\,r(N)^{1/\alpha},
\]
not \(Nr(N)\), unless \(\alpha=1\).

Also compare charged costs with the actual reference point cost. A `RQMCJ` point costs less than a full-network pass; small-net inverse-normal overhead can make an ordinary RQMC point cost several nominal passes.

**CHECKED-NUMERICALLY. The 14:50Z read of `results/posthoc_matched.json` contained 47 rows and gave these ranges:**

| Group | Matched-\(N\) variance ratio | Passes per line | PI slope against \(N\) | Reference slope |
|---|---:|---:|---:|---:|
| \(n=32,64\) | 0.894–1.948 | 40.58–146.84 | 1.035–1.355 | 1.120–1.303 |
| \(8\times256\), PIJ | 0.866–17.037 | 14.96–35.92 | 1.103–1.369 | 0.815–1.404 |
| \(n=4,6\) | 3.060–36.311 | 58.98–89.60 | 1.504–1.974 | 1.377–1.757 |

The quoted \(n=32,64\) summary matches this snapshot approximately. The narrow-deep and small-net ranges in the question do not describe this complete snapshot; they may describe earlier or restricted results.

**PROVEN by inspection of the fitting code. Some “matched-range” slope comparisons use different actual ranges.**

The lower endpoint is selected from the PI curve. The reference slope then uses whatever reference points exist above that endpoint. For example, PI may be fitted from \(N=16\), while the point curve begins at \(64\). The variance ratios themselves use genuinely matched \(N\), but the two slopes need not.

Use the intersection of the available ranges for both fits. The `NaN` reference slope in the partial \(128\)-width result reflects insufficient points.

**HEURISTIC. The measurements support a practical cost disadvantage in the tested wider nets, but not the stronger asymptotic conclusions.**

In particular:

- An ensemble lower bound need not hold on every individual network. F7(g)’s “as they must be” should be removed.
- An NNGP illustrative bound is not a certified finite-width bound.
- Finite-budget slopes neither establish nor refute the fixed-fan asymptotic constructions.
- `PI_as` uses network-dependent information and is outside the unconditional F7 design-independence hypothesis.
- PIJ and RQMCJ variance comparisons measure MSE only under the stated exact-tail premise.
- Retained vertex counts include inherited boundaries that can become redundant. Their saturation is not, by itself, a certified statement about the minimal final fan.

The useful next measurement is individual degree-4 and degree-6 energy with uncertainty, followed by the per-net LP certificate (15). The existing aggregate even-energy measurements cannot supply that certificate.
