I treated the supplied measurements as evidence, not as verified asymptotic laws. I read the three requested files and permitted ARC material, read no other future-aware files, and modified no files.

Throughout, \(e\) denotes **normalized squared error**. I use \(q>1\) for an error-reduction factor, \(q=e_K/e_{K+1}\).

## Q1. The future-weighted cumulant ladder

### A precise hierarchy

**PROVEN UNDER positive-definite covariance at each reconstruction.** A projected cumulant hierarchy can retain
\[
\mu_\ell,\quad S_\ell,\quad
C_{\ell,r}\in\operatorname{Sym}^r(\mathbb R^k),\qquad 3\le r\le K.
\]
For feature matrix \(A_\ell\in\mathbb R^{n\times k}\), define
\[
U_\ell=S_\ell A_\ell(A_\ell^\top S_\ell A_\ell)^{-1},
\qquad \Pi_\ell=U_\ell A_\ell^\top.
\]
Then \(A_\ell^\top U_\ell=I_k\), \(\Pi_\ell^2=\Pi_\ell\), and the represented higher cumulants are
\[
\widehat\kappa_{\ell,r}=U_\ell^{\otimes r}C_{\ell,r}.
\]

One concrete signed reconstruction has moment-generating function
\[
M_\ell(z)=
e^{\mu_\ell^\top z+\frac12z^\top S_\ell z}
\left[
\exp\!\left(
\sum_{r=3}^K
\frac{C_{\ell,r}:(U_\ell^\top z)^{\otimes r}}{r!}
\right)
\right]_{\deg\le K}.
\]
The bracket is a polynomial. Multiplying a Gaussian moment-generating function by a polynomial corresponds to a finite linear combination of Gaussian-density derivatives, hence a finite signed measure.

Its cumulants through degree \(K\) are the stated ones: the logarithm of the truncated exponential agrees with its exponent through degree \(K\).

Push this reconstruction through \(h\mapsto\operatorname{ReLU}(Wh)\), compute its full mean and covariance, and retain
\[
C_{\ell+1,r}
=\kappa_r\!\left(A_{\ell+1}^{\top}\operatorname{ReLU}(Wh)\right).
\]
Reconstruction then replaces the pushed cumulant by
\[
\Pi_{\ell+1}^{\otimes r}\kappa_r.
\]
This formalizes the projection in (c). It also specifies what is discarded: higher cumulants involving directions outside \(\operatorname{range}(U_{\ell+1})\).

A signed push can have an indefinite covariance; the construction above therefore requires the stated positivity hypothesis or an additional covariance-repair rule.

### What a dedicated implementation must compute

**PROVEN.** The linear step need not materialize an \(n^r\) tensor. It sends
\[
\mu\mapsto W\mu,\qquad S\mapsto WSW^\top,\qquad U\mapsto WU.
\]
Under schoolbook arithmetic these cost
\[
O(n^2),\qquad O(n^3),\qquad O(n^2k),
\]
respectively. A subsequent \(k\times k\) change of coordinates applied in all modes of a dense order-\(r\) core costs \(O(rk^{r+1})\).

The nonlinear step has three contributions:

1. propagated higher cumulants;
2. fresh cumulants of a correlated rectified Gaussian;
3. mixed terms involving incoming higher cumulants and the nonlinearity.

The second and third contributions remain necessary when all retained tensors are small.

**PROVEN.** In particular, the fresh Gaussian contribution is
\[
G_{r,a_1\ldots a_r}
=
\sum_{i_1,\ldots,i_r=1}^n
A_{i_1a_1}\cdots A_{i_ra_r}
\operatorname{cum}\bigl(Z_{i_1}^{+},\ldots,Z_{i_r}^{+}\bigr),
\qquad Z\sim N(m,\Sigma).
\]
It is generally dense before projection. The law of \(A^\top Z^+\) is not obtained by rectifying a \(k\)-dimensional Gaussian.

A direct dedicated computation can generate its \(O(n^r)\) distinct-index entries and contract them successively. Apart from Gaussian-moment evaluation, the contraction cost is
\[
O\!\left(
n^rk+n^{r-1}k^2+\cdots+nk^r
\right).
\]
This is an implementation bound, **not a lower bound requiring every algorithm to enumerate those entries**.

For the signed reconstruction above, a conservative mixed-term implementation evaluates each output moment using incoming correction tensors of total degree at most \(K\). It uses \(O_K(k^K)\) arithmetic per output-index tuple, plus Gaussian derivative-moment evaluations. Thus an explicit, loose implementation bound is
\[
O_K\!\left(n^3+n^Kk^K+kn^K\right),
\]
with the numerical cost and accuracy of the Gaussian integrals charged separately. Projection alone does not establish a \(k\)-based order ladder.

**PROVEN UNDER a specified contractible diagram approximation.** A more favorable implementation is possible if the retained Gaussian-source and mixed diagrams admit contractions whose largest covariance-edge interface has at most \(K-1\) feature indices. If there are \(D_K\) such diagrams, a sufficient per-layer cost bound is
\[
F_K=
O\!\left(
n^3+n^2k+
D_K\bigl[n^2k^{K-1}+nk^K+Kk^{K+1}\bigr]
\right).
\tag{1}
\]
The terms follow directly from multiplying a dense \(n\times n\) covariance into arrays with up to \(k^{K-1}\) columns, assembling neuron-indexed feature tensors, and transforming dense cores.

For example, a third-order Gaussian tree contribution of the form
\[
T_{ijk}=a_i b_j b_k\Sigma_{ij}\Sigma_{ik}
+\text{two permutations}
\]
can be projected by first computing \(V=\Sigma\operatorname{diag}(b)A\), then accumulating
\[
\sum_i a_i A_{ia}V_{ib}V_{ic}.
\]
Its cost is \(O(n^2k+nk^3)\). This demonstrates the saving for that contribution; it does not identify the complete rectified-Gaussian cumulant with its tree approximation.

For fixed \(K\), \(k\le n\), and controlled diagram count, (1) gives
\[
F_K=O_K(n^3+n^2k^{K-1}),\qquad
C_K=O_K(n+k^{K-1})
\tag{2}
\]
in forward-pass units for a full sweep.

**HEURISTIC.** Equation (2) is a plausible favorable cost model for a suitably truncated projected diagram implementation. I have **not checked that every diagram in ARC’s “simple” update admits this contraction bound**, nor that its omitted diagrams preserve ARC’s error law. The timings of “compute the full tensor, then project” would not settle this question.

Feature construction, pilot states, VJPs, and any repeated fitting must also be included in \(C_K\).

### The exponent and the exact rate criterion

**PROVEN UNDER uniform geometric error and cost laws.** Suppose, for the orders actually used,
\[
e_K=E q^{-(K-K_0)},\qquad
C_K=A+B k^{K-K_0},\qquad k>1.
\tag{3}
\]
Then
\[
\gamma=\frac{\log q}{\log k}.
\]
Indeed, the largest affordable order satisfies
\[
K-K_0=
\left\lfloor
\log_k\frac{C-A}{B}
\right\rfloor,
\]
so
\[
E\left(\frac{C-A}{B}\right)^{-\gamma}
\le e_{\rm best}(C)
<
qE\left(\frac{C-A}{B}\right)^{-\gamma}.
\tag{4}
\]

Consequently:

- matching MC’s squared-error exponent requires \(q\ge k\);
- strict improvement of the exponent requires \(q>k\);
- matching MC’s constant additionally requires favorable prefactors.

An \(n^2\) multiplicative overhead, or an additive \(K\)-independent covariance cost, does not change this **fixed-\(n\), increasing-precision exponent**. It can dominate the affordable orders and determine whether any useful budget window exists.

**PROVEN.** The more general exact condition is
\[
\boxed{\sup_K C_K e_K<\infty.}
\tag{5}
\]
Under a geometric ladder, this is the condition for an \(O(C^{-1})\) error envelope, up to the bounded spacing between adjacent costs. At an individual step, efficiency improves exactly when
\[
\boxed{\frac{e_K}{e_{K+1}}>\frac{C_{K+1}}{C_K}.}
\tag{6}
\]
This is the correct finite-order comparison when overhead is substantial.

If \(C_K\asymp K^a k^K\), then \(q=k\) matches the exponent but incurs a logarithmic loss; it does not satisfy (5) when \(a>0\).

**PROVEN.** Therefore \(\gamma^*=\log q/\log k\) is conditional, not a consequence of projected tensor storage. It can fail because:

- exact Gaussian-source evaluation retains an \(n^K\) cost;
- diagram counts introduce additional order dependence;
- the error approaches a projection floor;
- the assumed cost is only a fixed-\(K\) bound with uncontrolled constants.

For example, if \(e_K=e_\infty+Eq^{-K}\), the exponent describes only excess error above \(e_\infty\).

Also, symmetric order-\(K\) tensors have \(\binom{k+K-1}{K}\) independent entries, not \(k^K\). At fixed \(k\), this is polynomial in \(K\). Thus the ordered-index cost law must be an explicit implementation hypothesis when extrapolating to arbitrarily large \(K\).

### What (c) establishes, and the order-four test

**PROVEN UNDER the reported error measurements.** Writing \(q_3=e_2/e_3\), the projected improvement factor is exactly
\[
\boxed{
q_{3,\mathrm{proj}}
=\frac{1}{1-R+R/q_3}.
}
\tag{7}
\]
This follows by rearranging the definition of \(R\).

For the second \(256\times32\) net, \(q_3=17\) gives:

| Projection | \(R\) | \(q_{3,\mathrm{proj}}\) |
|---|---:|---:|
| Future, \(k=64\) | 0.96 | 10.37 |
| PCA, \(k=64\) | 0.85 | 5.00 |
| Future, \(k=16\) | 0.56 | 2.11 |
| PCA, \(k=16\) | 0.43 | 1.68 |

Thus “retains 96% of the improvement” does not mean “retains 96% of the 17-fold factor.”

**HEURISTIC.** The measurements support useful compression of the order-three correction, sometimes with improved error after projection. They do not establish \(q_4\), a dedicated implementation cost, or a uniform-in-width law. Values \(R>1\) concern the final squared error; they are not fractions of orthogonal cumulant energy and can reflect cancellation or removal of harmful approximation terms.

**PROVEN UNDER (2) as a two-sided cost law and \(k=cn\).** The third- and fourth-order costs scale as
\[
C_3=\Theta(n^2),\qquad C_4=\Theta(n^3).
\]
Therefore order four improves efficiency over order three only if
\[
q_{4,\mathrm{proj}}>\frac{C_4}{C_3}=\Theta(n).
\tag{8}
\]
A bounded \(q\), including ARC’s \(q\approx n/L=1/\alpha\), does not meet that requirement as \(n\) grows.

For an MC comparison, the order-four estimator beats sampling on
\[
[C_4,\,1/e_4).
\]
Its **multiplicative** budget window grows without bound exactly when
\[
C_4e_4\longrightarrow0.
\tag{9}
\]
Under this cost law that requires \(e_4=o(n^{-3})\). More generally,
\[
G_4=G_3\,\frac{q_{4,\mathrm{proj}}}{C_4/C_3}.
\]
This states precisely what order four must accomplish without assuming an unmeasured width exponent.

## Q2. Dimension of the nonlinear reading

### Definitions and scope

**PROVEN.** Several different quantities are called “effective” or “stable” rank. For a positive semidefinite matrix \(H\), distinguish
\[
r_{\rm PR}(H)=\frac{(\operatorname{tr}H)^2}{\operatorname{tr}(H^2)},\qquad
r_{\rm tr/op}(H)=\frac{\operatorname{tr}H}{\|H\|_{\rm op}},
\qquad
r_{\rm stable}(H)=\frac{\operatorname{tr}(H^2)}{\|H\|_{\rm op}^2}.
\tag{10}
\]
A participation-ratio result alone does not establish either operator-norm-based result. Eigenvalues \((\sqrt n,1,\ldots,1)\) give \(r_{\rm PR}=\Theta(n)\) but \(r_{\rm stable}=\Theta(1)\).

**PROVEN UNDER homogeneous independent gates.** I first take \(P=pI\), with fixed \(0<p<1\), and independent square Gaussian weights. This is a specified version of the proposed mean-field model. No universal answer follows for unrestricted \(p_i\): if all \(p_i=1\), the gate-fluctuation part is zero.

Write \(W=\sqrt2X\), with \(X_{ij}\sim N(0,1/n)\), and normalize \(R_t\) by its mean growth factor \((2p)^t\). The normalized recursion is
\[
R_t=X_t^\top\bigl[pR_{t-1}+(1-p)\operatorname{diag}R_{t-1}\bigr]X_t,
\qquad R_0=I.
\tag{11}
\]
The normalized mean-Jacobian contribution is
\[
T_t=pX_t^\top T_{t-1}X_t,\qquad T_0=I.
\tag{12}
\]
Thus the nonlinear part \(N_t=R_t-T_t\) satisfies
\[
N_t=pX_t^\top N_{t-1}X_t
 +(1-p)X_t^\top\operatorname{diag}(R_{t-1})X_t,
\tag{13}
\]
and \(0\preceq N_t\preceq R_t\).

Equation (13) displays the source of broad rank: every step injects a fresh positive covariance contribution.

### A finite-width result through depth proportional to width

**PROVEN UNDER (11)–(12).** At \(t=\lfloor\beta n\rfloor\), for fixed \(\beta>0\),
\[
\boxed{r_{\rm PR}(N_t)=\Theta_{\mathbb P}(n).}
\tag{14}
\]
Here the notation means that, for every fixed confidence \(1-\delta\), a positive constant \(c_\delta\) bounds \(r_{\rm PR}/n\) below with at least that confidence for sufficiently large \(n\). It does not assert a particular limiting constant.

Here is a finite-\(n\) proof.

Set
\[
U_t=\mathbb E(\operatorname{tr}R_t)^2,\qquad
V_t=\mathbb E\operatorname{tr}(R_t^2).
\]
Every \(R_t\) is orthogonally invariant because the current Gaussian matrix is right-orthogonally invariant. Therefore
\[
\mathbb E\sum_i(R_t)_{ii}^2
=\frac{U_t+2V_t}{n+2}.
\tag{15}
\]
To verify (15), condition on the eigenvalues and use
\[
\mathbb E(u^\top Hu)^2
=\frac{(\operatorname{tr}H)^2+2\operatorname{tr}(H^2)}{n(n+2)}
\]
for a uniform unit vector \(u\), then sum over diagonal entries.

For fixed symmetric \(A\), Gaussian pairings give
\[
\mathbb E(\operatorname{tr}X^\top AX)^2
=(\operatorname{tr}A)^2+\frac2n\operatorname{tr}(A^2),
\]
\[
\mathbb E\operatorname{tr}\bigl((X^\top AX)^2\bigr)
=\left(1+\frac1n\right)\operatorname{tr}(A^2)
+\frac1n(\operatorname{tr}A)^2.
\tag{16}
\]
For instance, the first formula follows by writing the trace as a sum of independent Gaussian quadratic forms. In the second, distinct columns contribute \(\operatorname{tr}(A^2)/n^2\); equal columns contribute \(((\operatorname{tr}A)^2+2\operatorname{tr}(A^2))/n^2\).

Consequently, with
\[
H_t=p^2V_t+(1-p^2)\frac{U_t+2V_t}{n+2},
\]
the exact recurrences are
\[
U_{t+1}=U_t+\frac2nH_t,\qquad
V_{t+1}=\frac1nU_t+\left(1+\frac1n\right)H_t.
\tag{17}
\]

Normalize \(u_t=U_t/n^2\), \(v_t=V_t/n\). Then
\[
h_t:=H_t/n=a_nv_t+(1-a_n)u_t,
\quad
a_n=p^2+\frac{2(1-p^2)}{n+2}<1,
\]
\[
u_{t+1}=u_t+\frac{2h_t}{n^2},\qquad
v_{t+1}=u_t+(1+1/n)h_t.
\tag{18}
\]
For sufficiently large \(n\), the coefficient \((1+1/n)a_n\) is bounded below one. Iterating the second recurrence therefore gives \(v_t\le C_pu_t\), since \(u_t\) is nondecreasing. The first then gives
\[
u_t\le \exp(C_pt/n^2).
\]
For \(t\le\beta n\),
\[
U_t=n^2+O(n),\qquad V_t=O(n).
\tag{19}
\]
Also \(\mathbb E\operatorname{tr}R_t=n\). Thus
\[
\operatorname{tr}R_t/n\to1
\]
in probability.

Meanwhile
\[
\mathbb E\operatorname{tr}T_t=np^t,
\]
so positivity and Markov’s inequality imply \(\operatorname{tr}T_t/n\to0\) at \(t=\beta n\). Hence
\[
\operatorname{tr}N_t/n\to1,\qquad
\mathbb E\operatorname{tr}(N_t^2)\le V_t=O(n).
\]
Markov’s inequality applied to the second relation proves the lower bound in (14); \(r_{\rm PR}\le n\) proves the upper bound.

**PROVEN UNDER the same model.** Restriction to the \((n-1)\)-dimensional transverse space preserves (14), even for a chosen transverse direction. Removing one direction changes the trace by at most
\[
\|N_t\|_{\rm op}\le\sqrt{\operatorname{tr}(N_t^2)}
=O_{\mathbb P}(\sqrt n),
\]
and cannot increase the squared Frobenius norm of the compression. The trace remains \(n(1+o_{\mathbb P}(1))\), and the preceding proof applies.

### An explicit participation-ratio formula

**PROVEN UNDER diagonal flattening and joint Gaussian/free trace concentration at the depths considered.** Suppose normalized traces obey the Gaussian-product limiting rule
\[
\tau(X^\top AX\,X^\top BX)
=\tau(AB)+\tau(A)\tau(B)+o(1),
\tag{20}
\]
and \(\operatorname{diag}R\) can be replaced by \(I\) in the required traces. For \(t\) growing with \(n\), these assumptions must hold uniformly sufficiently well; fixed-depth asymptotic freeness alone is insufficient.

Let
\[
v_t=\tau(R_t^2),\qquad w_t=\tau(T_t^2),\qquad z_t=\tau(R_tT_t).
\]
The limiting recurrences are
\[
v_t=p^2v_{t-1}+2-p^2,
\]
\[
w_t=p^2w_{t-1}+p^{2t},
\]
\[
z_t=p^2z_{t-1}+(2-p)p^t,
\]
starting at \(v_0=w_0=z_0=1\).

For example, the first follows by putting \(A=pR+(1-p)I\) in (20):
\[
\tau(A^2)+\tau(A)^2
=p^2v+(1-p^2)+1.
\]
The other two follow by using \(pT\) as one or both factors.

Solving gives
\[
v_t=1+\frac{1-p^{2t}}{1-p^2},\qquad
w_t=(t+1)p^{2t},
\]
\[
z_t=p^{2t}
+\frac{2-p}{1-p}p^t(1-p^t).
\]
Therefore, for \(t\ge1\),
\[
\boxed{
\frac{r_{\rm PR}(N_t)}n
\longrightarrow
\frac{(1-p^t)^2}{v_t+w_t-2z_t}.
}
\tag{21}
\]
As \(t\to\infty\),
\[
\boxed{
\frac{r_{\rm PR}(N_t)}n
\longrightarrow \frac{1-p^2}{2-p^2}.
}
\tag{22}
\]
For \(p=1/2\), this is \(3/7\). The fractions from (21) are approximately \(0.500,0.474,0.442,0.430\) at \(t=1,2,4,8\).

**PROVEN UNDER an additional bounded-operator-norm hypothesis.** If \(\|R_t\|_{\rm op}=O_{\mathbb P}(1)\), then both other ranks in (10) are also \(\Theta_{\mathbb P}(n)\). Indeed, \(\operatorname{tr}N_t\asymp n\), \(\|N_t\|_{\rm op}\le\|R_t\|_{\rm op}\), and
\[
\operatorname{tr}(N_t^2)\ge(\operatorname{tr}N_t)^2/n.
\]
I have not proved this additional uniform operator-norm bound at \(t=\beta n\).

**PROVEN.** The mean-gate linear term (12) has limiting participation ratio \(n/(t+1)\) in this square-Gaussian model. Thus the supplied \(n/(2t+1)\) formula cannot simply be inserted into (21): its factor two requires a different linear/gate ensemble. Both linear formulas describe concentration with depth; the nonlinear conclusion here comes from the explicitly stated recursion.

### Relation to (b)

**PROVEN.** For any positive semidefinite \(H\), every rank-\(k\) projector satisfies
\[
\frac{\operatorname{tr}(PH)}{\operatorname{tr}H}
\le
\sqrt{\frac{k}{r_{\rm PR}(H)}}.
\tag{23}
\]
This follows by maximizing over the leading \(k\) eigenvalues and applying Cauchy–Schwarz.

Thus (14) implies that capturing a fixed fraction of this nonlinear **Jacobian energy** requires \(k=\Omega(n)\), including for future-selected subspaces. Fixed \(k\) captures a vanishing fraction.

**HEURISTIC.** This is consistent with (b), but it does not prove its closure-error trend. The actual gates are correlated with weights and states, and the relevant matrix is covariance-whitened on a non-Gaussian cloud. More fundamentally, derivative energy is not integration error. None of those bridges has been checked here.

## Q3. What representing the \(k\)-dimensional law would require

### A precise worst-case obstruction

**PROVEN.** Consider deterministic algorithms using at most \(M\) adaptive function evaluations to integrate all continuous, piecewise-linear, 1-Lipschitz functions on \([0,1]^k\) under uniform measure. Their worst-case absolute error is at least
\[
\boxed{cM^{-1/k}}
\tag{24}
\]
for an absolute \(c>0\).

Run the algorithm on the zero function and collect its queried points \(x_1,\ldots,x_M\). Set
\[
f(x)=\min_j\|x-x_j\|_\infty.
\]
This function is continuous, piecewise linear, 1-Lipschitz, and zero at all queried points.

The union of radius-\(r\) cubes around the query points has volume at most \(M(2r)^k\). Choose
\[
r=\tfrac12(2M)^{-1/k}.
\]
At least half the cube has \(f\ge r\), so
\[
\int f\ge r/2\ge\tfrac18M^{-1/k}.
\]
The algorithm receives the same transcript on \(f\) and \(-f\), including under adaptation. Their integrals are opposite, so its error on one is at least \(\int f\). This proves (24).

The same proof applies to a fixed non-Gaussian law whose density is bounded below on a cube, with the corresponding density and scale factors.

**PROVEN.** This is an absolute-error bound. Its squared-error version is \(c^2M^{-2/k}\), to be compared with MC’s \(M^{-1}\) squared-error rate. These exponents should not be mixed.

**PROVEN.** It also gives a representation bound for an \(M\)-atomic law approximation required to integrate **every** 1-Lipschitz reading accurately. The distance to its support integrates to zero under the approximation and at least \(cM^{-1/k}\) under the uniform law, regardless of the chosen atomic weights.

### What it does not establish

**PROVEN.** The proof does not lower-bound an algorithm supplied with the explicit weights of this particular future network and a structured description of its particular layer law. Such an algorithm has information beyond queried function values, and need not work for the adversarial family above.

Likewise, \(M\) real parameters in a representation do not by themselves define an information or arithmetic model. Constructing the parameters and integrating the future against the representation must be charged.

**HEURISTIC.** The observations in (a)–(b) suggest that a useful exact-marginal method retains a substantial fraction of the width. They do not establish an asymptotic necessity theorem, nor a worst-case integration lower bound for these random-network laws.

### Cumulants, mixtures, and lattice rules

**PROVEN.** A fixed finite list of cumulants does not determine the expectation of a general piecewise-linear function over arbitrary laws, even when the laws have bounded positive densities.

Let \(\mathcal P_K\) be the polynomials of total degree at most \(K\) on the cube, and let \(f\) be a continuous piecewise-linear function not in \(\mathcal P_K\). Put
\[
r=f-\operatorname{Proj}_{\mathcal P_K}f.
\]
Then \(r\) is bounded and orthogonal to every polynomial in \(\mathcal P_K\). For sufficiently small \(\epsilon>0\),
\[
d\mu_\pm=(1\pm\epsilon r)\,dx
\]
are positive probability measures. They have identical moments, hence identical cumulants, through degree \(K\), but
\[
\int f\,d\mu_+-\int f\,d\mu_-
=2\epsilon\|r\|_2^2>0.
\]
Thus moment-only information requires an additional approximation-class hypothesis to give a useful guarantee.

**PROVEN UNDER bounded piecewise-linear complexity.** Faster deterministic rates are possible. For example, suppose \(f\) is Lipschitz and affine away from a union of \(H\) hyperplanes, with \(H\) and the Lipschitz constant bounded. Under uniform measure, a tensor midpoint grid with \(M=m^k\) points has
\[
\boxed{\left|Q_Mf-\int f\right|=O_{k,H}(M^{-2/k}).}
\tag{25}
\]

Proof: midpoint integration is exact on every cell where \(f\) is affine. Only \(O_{k,H}(m^{k-1})\) cells meet the hyperplanes. Each such cell contributes error at most its volume times \(O(1/m)\), namely \(O(m^{-(k+1)})\). Summing gives \(O(m^{-2})\).

This is already a deterministic lattice-type rule beating the generic Lipschitz exponent. It does not contradict (24), whose adversarial functions have complexity growing with the information budget.

**PROVEN UNDER known cell masses and first moments.** The same argument extends to a bounded-density non-Gaussian law by replacing each grid cell with its exact mass at its conditional centroid. Affine functions are integrated exactly within each cell. Obtaining those masses and centroids may itself be the difficult computation.

**PROVEN UNDER bounded Hardy–Krause variation and an appropriate low-discrepancy rule.** The discrepancy inequality gives
\[
\left|Q_Mf-\int f\right|
\le V_{\rm HK}(f)D_M^*.
\]
Rules with \(D_M^*=O_k(M^{-1}(\log M)^k)\) therefore give substantially faster rates. Arbitrary high-dimensional piecewise-linear functions do not automatically have bounded Hardy–Krause variation, so this assumption must be checked.

**PROVEN.** A Gaussian-mixture component count alone supports no universal negative statement. A law that is exactly one Gaussian is represented with one component, and the expectation of each known affine ReLU under it is explicit. Conversely, integrating an arbitrary deep piecewise-linear future against even one Gaussian can retain the original difficulty.

The relevant question for mixtures is the combination of approximation error, parameter-construction cost, and integration cost per component.

## Q4. Why the control and RQMC gains need not multiply

### The variance identity

**PROVEN.** Work on the sampling cube after the Gaussian transform, and condition on a fitted control independent of the evaluation randomization. For an unbiased randomized rule \(Q_N\), define
\[
\mathcal B_N(f,g)
=\mathbb E\langle Q_Nf-If,\;Q_Ng-Ig\rangle.
\]
An exactly centered control gives
\[
\operatorname{Var}(Q_N(f-c))
=
\mathcal B_N(f,f)-2\mathcal B_N(f,c)+\mathcal B_N(c,c).
\tag{26}
\]
This is expansion of the squared integration error.

An ordinary \(L^2\) regression minimizes MC variance. It need not minimize the different quadratic form \(\mathcal B_N\), and can increase RQMC variance.

### The scrambled-net statement

**PROVEN UNDER nested uniform scrambling of a digital net.** Let \(f_{u,\kappa}\) denote the orthogonal tensor-Haar detail blocks, indexed by nonempty coordinate subsets \(u\) and resolution levels \(\kappa\). The scrambled-net variance has the form
\[
\boxed{
\operatorname{Var}(Q_Nf)
=\frac1N\sum_{u,\kappa}
\Gamma_{u,\kappa}\|f_{u,\kappa}\|_2^2,
}
\tag{27}
\]
with nonnegative gain coefficients determined by the net.

The mechanism behind (27) is that the joint distribution of two scrambled points is determined by coordinatewise shared-prefix lengths. The resulting covariance operator is a combination of averaging operators on nested digit partitions. These commuting operators are diagonal on tensor martingale-difference spaces, yielding the coefficients \(\Gamma_{u,\kappa}/N\). Orthogonality then gives (27), componentwise for vector outputs.

Consequently,
\[
\boxed{
\operatorname{Var}(Q_N(f-c))
=\frac1N\sum_{u,\kappa}
\Gamma_{u,\kappa}
\|f_{u,\kappa}-c_{u,\kappa}\|_2^2.
}
\tag{28}
\]

If \(c\) removes whole detail blocks, the variance saved is exactly their **gain-weighted** energy. Removing blocks with small or zero \(\Gamma_{u,\kappa}\) can remove substantial ordinary variance while saving almost no RQMC variance.

A polynomial or linear control in hidden activations is not automatically a collection of low-order ANOVA or low-resolution Haar blocks in the original Sobol coordinates.

### The multiplication condition

**PROVEN.** Define
\[
V_f=\|f-If\|_2^2,\qquad V_r=\|f-c-I(f-c)\|_2^2,
\qquad \eta=V_r/V_f,
\]
and the energy-weighted average gains
\[
\overline\Gamma_f
=\frac{\sum\Gamma_{u,\kappa}\|f_{u,\kappa}\|_2^2}{V_f},
\qquad
\overline\Gamma_r
=\frac{\sum\Gamma_{u,\kappa}\|r_{u,\kappa}\|_2^2}{V_r}.
\]
Then
\[
\boxed{
\frac{\operatorname{Var}(Q_Nr)}
{\operatorname{Var}(Q_Nf)}
=
\eta\,\frac{\overline\Gamma_r}{\overline\Gamma_f}.
}
\tag{29}
\]
Thus the ordinary control reduction and the original RQMC gain multiply exactly when
\[
\overline\Gamma_r=\overline\Gamma_f.
\]
They combine at least that favorably when \(\overline\Gamma_r\le\overline\Gamma_f\).

**HEURISTIC.** The natural explanation of (d) is that the control removes components already integrated well by Sobol, leaving a residual with worse average scrambling gains. Numerically, if \(\eta\approx0.6\) but the RQMC variance ratio is approximately one, (29) requires
\[
\overline\Gamma_r\approx \overline\Gamma_f/0.6.
\]
That arithmetic is compatible with the observation. Identifying the responsible ANOVA/Walsh blocks would require a spectral measurement not supplied here.

### Bias and equal cost

**PROVEN.** If the control mean has normalized squared bias \(\beta\), setup costs \(B\) forward passes, and residual samples cost \(a\) passes each, then at budget \(C\),
\[
\mathrm{nMSE}_{\rm hybrid}
=
\beta+\frac{\eta}{NG_r(N)},
\qquad
N=\left\lfloor\frac{C-B}{a}\right\rfloor,
\tag{30}
\]
where \(G_r\) is the residual’s actual gain over MC.

The proof is bias–variance decomposition: conditional unbiasedness makes the cross term between the fixed mean error and randomized integration error vanish.

**PROVEN UNDER the reported \(\beta\) values being normalized squared biases.** The deeper-control biases \(1.4\text{–}8.5\times10^{-4}\) alone exceed the reported \(3.5\times10^{-5}\) baseline at \(2^{14}\) points. Those controls cannot beat that baseline there even with zero residual sampling variance.

## Q5. What “dimension changes, nature does not” can mean

**PROVEN.** Neither a broad nonlinear spectrum nor \(k=\Theta(n)\) implies integration hardness by itself. For example,
\[
g(x)=(x_1^+,\ldots,x_n^+),\qquad X\sim N(0,I_n),
\]
has
\[
\mathbb E[J^\top J]-\mathbb E[J]^\top\mathbb E[J]
=\tfrac14I_n,
\]
yet every output expectation is exactly \(1/\sqrt{2\pi}\). Its nonlinear derivative reading has full effective rank and an elementary integral.

Thus the necessary additional hypotheses concern the admissible representation, information access, contraction cost, and error law.

**PROVEN UNDER the respective models above.** Two precise versions of the proposed phrase are available:

- In the projected cumulant ladder, replacing \(n\) by \(cn\) preserves an order-dependent tensor-cost ladder if the retained diagrams still cost a factor \(\Theta(k)\) per order.
- In worst-case deterministic Lipschitz integration, replacing \(n\) by \(cn\) changes the exponent to \(1/(cn)\), while preserving exponential dependence on dimension for fixed target accuracy.

The first needs a uniform cost/error law. The second needs a worst-case function-oracle or universal-law-approximation requirement. Neither is currently a theorem about every estimator for the specified random MLP.

**HEURISTIC.** The new evidence favors investigating projected low-order corrections: (c) preserves much more useful order-three correction than its retained dimension might suggest. The particle experiment establishes approximation potential, while the control experiment shows that ordinary variance reduction is an unreliable proxy for additional RQMC benefit. No supplied experiment yet establishes the dedicated contraction cost needed for a computational conclusion.

## Single strongest defensible negative statement

**PROVEN UNDER the following three hypotheses:** useful projected hierarchies require \(k_n\ge cn\); their errors satisfy a uniform two-sided geometric law with reduction factors \(1<q_n\le Q<\infty\); and their fully charged costs satisfy a uniform geometric law with base \(k_n\).

Then
\[
\boxed{
\gamma_n=\frac{\log q_n}{\log k_n}
\le\frac{\log Q}{\log(cn)}
\longrightarrow0.
}
\]
For every sufficiently large width, this hierarchy fails to match MC’s squared-error rate at arbitrarily fine precision, even if its error tends to zero as order increases.

**Proof:** eliminate order using (3)–(4). Since eventually \(q_n<k_n\), \(C_Ke_K\) grows geometrically with order, violating (5). A constant fractional reduction of width does not change that conclusion.

The uniform lower error law and the dedicated cost law are essential hypotheses; the measurements do not establish them.

## Single strongest positive possibility

**CONJECTURE.** A future-weighted third- or fourth-order correction may admit a structured implementation costing only \(O(n^3)\) per layer, including feature construction, while achieving \(e_n=o(n^{-1})\) along \(L=\alpha n\). This would require exploitable structure in the cumulants and their source/mixed contractions beyond storing an arbitrary dense \(k\)-dimensional core.

**PROVEN UNDER those cost and accuracy hypotheses:** its total cost is \(C_n=O(n)\) forward passes, so
\[
C_ne_n\to0,\qquad
G_n^{\rm MC}=\frac1{C_ne_n}\to\infty.
\]
It would therefore obtain a growing advantage over MC in a finite-precision budget window, even without fixing the all-order exponent.

The retention results in (c) motivate this possibility. They do not yet establish either the required contraction structure or the error scaling.
