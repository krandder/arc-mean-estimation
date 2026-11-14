All mathematical claims below carry a status label. The reported measurements are treated as supplied evidence; I have not rerun them. I read no other file in the future-aware directory and modified no files.

## Q1. Conditional pricing and ARC’s sketching rule

**PROVEN — conditional pricing.** Let \(\mathcal A\) be the past, \(\mathcal H=\mathcal A\vee S\), and suppose that the signed defect \(\Delta\) is \(\mathcal H\)-measurable. Subject to square integrability,
\[
\boxed{\;
\mathbb E\!\left[\left\|\int g(h)\,d\Delta(h)\right\|^2\mid\mathcal H\right]
=\iint K_S(h,h')\,d\Delta(h)d\Delta(h'),
\;}
\]
where
\[
K_S(h,h')=\mathbb E[g(h)\cdot g(h')\mid\mathcal H].
\]

Indeed, expand the squared norm as a double integral and take the conditional expectation. Conditional measurability allows the two copies of \(\Delta\) to be held fixed. Conditional Fubini is justified, for example, by
\[
\int \sqrt{K_S(h,h)}\,d|\Delta|(h)<\infty.
\]
The first-moment assumption in Theorem A suffices here when the relevant conditional squared Lipschitz constant is finite.

This identity remains valid for a future-aware defect. What changes is the kernel. Using the unconditional kernel while holding a future-dependent defect fixed is generally invalid.

**PROVEN — the precise spectral interpretation.** An eigenvalue statement requires a reference measure \(\mu\). On \(L^2(\mu)\), define
\[
(T_Sf)(h)=\int K_S(h,h')f(h')\,d\mu(h').
\]
For a defect \(d\Delta=f\,d\mu\), its conditional price is \(\langle f,T_Sf\rangle\).

If the approximation keeps an \(m\)-dimensional linear subspace of \(L^2(\mu)\), the smallest possible worst-case residual price over \(\|f\|_2\le1\) is
\[
\lambda_{m+1}(T_S).
\]
Keeping the leading eigenfunctions attains this: expand \(f\) in an orthonormal eigenbasis. Conversely, any \(m\)-dimensional retained space has a nonzero orthogonal complement inside the span of the first \(m+1\) eigenfunctions; a unit vector there has price at least \(\lambda_{m+1}\).

Thus ARC’s “largest unused eigenvalue” rule is a minimax statement with a specified norm constraint. It is not directly a statement about arbitrary finite signed measures.

**PROVEN — annealed eigenstructure on a rotationally symmetric reference law.** Write
\[
K(h,h')=rr'\kappa(u\cdot u'),\qquad
\kappa(s)=\sum_{d\ge0}b_ds^d,
\]
with \(h=ru\). Suppose \(\mu=\nu(dr)\sigma(du)\), where \(\sigma\) is uniform probability measure on \(S^{n-1}\), and set \(m_2=\int r^2\,d\nu\).

For every spherical harmonic \(Y_{j,a}\) of degree \(j\), the function
\[
h\longmapsto rY_{j,a}(u)
\]
is an eigenfunction, with eigenvalue
\[
\boxed{\;
\lambda_j=m_2
\sum_{\substack{d\ge j\\d-j\ {\rm even}}}
b_d\,
\frac{d!\,\Gamma(n/2)}
{2^d((d-j)/2)!\,\Gamma((n+d+j)/2)}.
\;}
\]
Other radial dependence is annihilated if it is orthogonal to \(r\).

Here is a derivation of the coefficient. Let \(H_j\) be a homogeneous harmonic polynomial and \(Z\sim N(0,I_n)\). Gaussian translation and harmonicity give
\[
\mathbb E[e^{t u\cdot Z}H_j(Z)]
=e^{t^2/2}H_j(tu).
\]
Comparing coefficients of \(t^d\),
\[
\mathbb E[(u\cdot Z)^dH_j(Z)]
=\frac{d!}{2^{(d-j)/2}((d-j)/2)!}H_j(u)
\]
when \(d-j\) is nonnegative and even, and zero otherwise. Writing \(Z=RU\) and dividing by
\[
\mathbb ER^{d+j}
=2^{(d+j)/2}\frac{\Gamma((n+d+j)/2)}{\Gamma(n/2)}
\]
gives the displayed eigenvalue formula. Harmonic decomposition of polynomials and density of their restrictions on the sphere give the complete angular decomposition.

In particular:

- Harmonic degree \(0\) is the radius feature \(r\).
- Harmonic degree \(1\) consists of the coordinates \(h_i\).
- Higher degrees are radially weighted, trace-free angular polynomials.
- The \(b_d\) are **feature weights, not operator eigenvalues**: traces make different tensor degrees contribute to the same harmonic degree.

The radius is a leading eigenfunction on this rotational reference law. To see this, \(\kappa\ge0\), so the angular operator has constant row sum \(\lambda_0/m_2\); Jensen’s inequality bounds its \(L^2\) operator norm by that row sum.

**PROVEN — realised eigenstructure.** When \(S\) reveals the whole future,
\[
K_S(h,h')=\sum_{i=1}^n g_i(h)g_i(h').
\]
Consequently, \(T_S\) has rank at most \(n\), its range lies in
\[
\operatorname{span}\{g_1,\ldots,g_n\},
\]
and its nonzero eigenvalues equal those of the \(n\times n\) Gram matrix
\[
\int g(h)g(h)^\top\,d\mu(h).
\]
This follows by writing \(T_S=A^*A\), where \(Af=\int gf\,d\mu\), and comparing with \(AA^*\).

**PROVEN — what ARC’s tail-law rule keeps.** Applied with the **law** of the MLP future, ARC’s rule keeps the leading eigenfunctions of the annealed operator, not the realised output functions or realised Jacobian directions. On a rotational reference law, these are the radius and angular harmonic modes, ordered by the eigenvalues above.

On the actual, generally anisotropic layer cloud—or on an input-indexed state \(h(x)\)—one must diagonalise the corresponding kernel operator or its pullback. Spherical harmonics need not remain eigenfunctions. The supplied \(b_d\) values alone do not specify that cloud-dependent ordering.

## Q2. A \(k\)-sketch theorem

**PROVEN — exact conditional Mehler expansion.** Let \(V\) be past-measurable with orthonormal columns, let \(U\) span its orthogonal complement, and write
\[
A=W_{l+1}V,\qquad B=W_{l+1}U,\qquad \sigma=\sqrt{2/n}.
\]
Condition on
\[
S=\sigma(A,W_{l+2},\ldots,W_L).
\]
Then \(B\) remains an independent matrix of \(N(0,2/n)\) entries.

Let \(R\) denote the fixed remaining network, including the ReLU immediately following \(W_{l+1}\), so
\[
g(h)=R(Aa+Bz),\qquad a=V^\top h,\quad z=U^\top h.
\]
Put \(r=|z|\), \(v=z/r\), and expand
\[
R(Aa+\sigma r\xi)
=\sum_{\alpha\in\mathbb N^n}C_\alpha(a,r)H_\alpha(\xi),
\]
where the \(H_\alpha\) are orthonormal Gaussian Hermite polynomials and the \(C_\alpha\) are output vectors.

For two states, \(Bz/(\sigma r)\) and \(Bz'/(\sigma r')\) have cross-covariance \((v\cdot v')I_n\). Mehler’s identity therefore gives
\[
\boxed{\;
K_S(h,h')
=\sum_{\alpha}
C_\alpha(a,r)\cdot C_\alpha(a',r')
(v\cdot v')^{|\alpha|}.
\;}
\]
When \(r=0\), all coefficients of positive degree vanish; this defines the boundary case without choosing \(v\).

Thus every \(S\)-measurable defect has conditional price
\[
\boxed{\;
\sum_{d\ge0}\sum_{|\alpha|=d}
\left\|
\int C_\alpha(a,r)\otimes v^{\otimes d}\,d\Delta(h)
\right\|_F^2.
\;}
\]
The degree-zero term is
\[
\left\|\mathbb E[\langle g,\Delta\rangle\mid\mathcal A,S]\right\|^2;
\]
the positive-degree terms sum to its conditional variance. The passage from the kernel to these squared norms uses
\[
(v\cdot v')^d=\langle v^{\otimes d},v'^{\otimes d}\rangle.
\]

**PROVEN — sharp information bound for correcting a fixed defect.** Now hold a **past-measurable** defect \(\Delta\) fixed, and set
\[
Z=\langle g,\Delta\rangle,\qquad
P=VV^\top,\qquad
M_d=\int |h|(h/|h|)^{\otimes d}\,d\Delta(h).
\]
Among all \(S\)-measurable additive corrections \(a(S)\),
\[
\inf_a\mathbb E_F\|Z-a(S)\|^2
=\mathbb E_F\|Z-\mathbb E[Z\mid S,\mathcal A]\|^2.
\]
Moreover,
\[
\boxed{\;
\mathbb E_F\|\mathbb E[Z\mid S,\mathcal A]\|^2
=\sum_{d\ge0}b_d\|P^{\otimes d}M_d\|_F^2,
\;}
\]
and hence
\[
\boxed{\;
\inf_a\mathbb E_F\|Z-a(S)\|^2
=\sum_{d\ge0}b_d
\bigl(\|M_d\|_F^2-\|P^{\otimes d}M_d\|_F^2\bigr).
\;}
\]

For the first identity, conditional expectation is an orthogonal projection in vector-valued \(L^2\):
\[
\mathbb E\|Z-a\|^2
=\mathbb E\|Z-\mathbb E[Z\mid S]\|^2+
\mathbb E\|\mathbb E[Z\mid S]-a\|^2.
\]

For the second, construct two first-layer matrices sharing their \(V\)-columns and having independent complementary columns; share all later layers. Conditional independence makes their error inner product equal the squared conditional mean. For unit states \(u,u'\), their Gaussian preactivations have cross-covariance
\[
(u^\top Pu')I_n.
\]
The same Mehler calculation as Theorem A gives
\[
\sum_db_d(u^\top Pu')^d.
\]
Integrating twice yields the formula.

The \(d=0\) contribution is completely predictable even at \(k=0\), because this \(S\) reveals all later layers. A radius-matched defect has \(M_0=0\), eliminating that qualification.

**PROVEN — the relevant effective-rank bound.** For a nonzero tensor \(T=M_d\), \(d\ge1\), let
\[
A_d=T_{(1)}T_{(1)}^\top,\qquad
r_\infty(T)=\frac{\operatorname{tr}A_d}{\|A_d\|_{\rm op}}.
\]
Then
\[
\frac{\|P^{\otimes d}T\|_F^2}{\|T\|_F^2}
\le
\frac{\operatorname{tr}(PA_d)}{\operatorname{tr}A_d}
\le
\frac{\sum_{i=1}^k\lambda_i(A_d)}{\operatorname{tr}A_d}
\le \min\{1,k/r_\infty(T)\}.
\]
The first inequality drops \(d-1\) orthogonal projections. The second is the variational characterisation of the leading eigenvalues.

A participation ratio
\[
r_{\rm PR}=\frac{(\operatorname{tr}A_d)^2}{\operatorname{tr}(A_d^2)}
\]
alone gives the weaker bound
\[
\frac{\|P^{\otimes d}T\|_F^2}{\|T\|_F^2}
\le \min\{1,\sqrt{k/r_{\rm PR}}\},
\]
by Cauchy–Schwarz on the leading \(k\) eigenvalues.

Thus \(O(k/n)\) follows from \(r_\infty=\Omega(n)\). It does not follow merely by replacing \(r_\infty\) with a reported participation ratio of order \(n\).

**PROVEN — high rank does not imply \((k/n)^d\).** At degree two, take \(T=I_n\). Its effective rank is \(n\), but
\[
\|PTP\|_F^2/\|T\|_F^2=k/n
\]
for every rank-\(k\) projector.

Even trace-freeness does not fix this for a past-chosen \(V\): take
\[
T=\operatorname{diag}(I_{n/2},-I_{n/2})
\]
and choose \(V\) from its eigenvectors. The same fraction is \(k/n\).

**PROVEN UNDER isotropic tensor orientation independent of \(V\).** If a unit tensor is uniform on the unit sphere of \(\operatorname{Sym}^d(\mathbb R^n)\), then
\[
\mathbb E\|P^{\otimes d}T\|_F^2
=
\frac{\binom{k+d-1}{d}}{\binom{n+d-1}{d}}.
\]
Indeed, \(P^{\otimes d}\) is the orthogonal projection onto \(\operatorname{Sym}^d(V)\), and a uniform unit vector places expected squared norm equal to dimension fraction in every subspace. This behaves like \((k/n)^d\) when \(d\) is fixed and both dimensions are large relative to \(d\).

**PROVEN — low-rank replacement.** The appropriate quantity is the actual multilinear capture
\[
\|P^{\otimes d}M_d\|_F^2/\|M_d\|_F^2,
\]
not an ambient-dimension rule. For \(T=u^{\otimes d}\), one aligned direction captures everything.

**PROVEN — scope limitation.** The sharp information bound concerns predicting and additively correcting a **fixed** defect. An \(S\)-dependent reconstruction can change the defect itself, and its propagated correction can still depend on the unrevealed weights. Such a correction need not be an \(S\)-measurable vector. The displayed bound therefore does not cover every algorithm called a “\(k\)-sketch closure.”

## Q3. Future-chosen subspaces and Haar overlap

**PROVEN — what Theorem 1 supplies.** Conditional on the past, the mean-direction column, and later layers, the transverse block \(M\) is right-orthogonally invariant. This supplies a Haar law for subspaces selected **equivariantly from that invariant block**, when no additional anisotropic object breaks the equivariance.

It does not automatically make the top eigenspace of
\[
\mathbb E_{\text{cloud}}[J(h)^\top J(h)]
\]
Haar. Rotating \(M\) while keeping an anisotropic cloud fixed changes which gates are sampled. The covariance-whitened version also requires a separate invariance argument. The supplied relevance report explicitly treats this extension as heuristic.

**PROVEN UNDER a Haar rank-\(k\) subspace of an \(m\)-dimensional transverse space.** For any fixed tensor \(T\),
\[
\mathbb E\|(P\otimes I^{\otimes(d-1)})T\|_F^2
=\frac{k}{m}\|T\|_F^2,
\]
and therefore
\[
\mathbb E\|P^{\otimes d}T\|_F^2
\le\frac{k}{m}\|T\|_F^2.
\]
This follows from \(\mathbb EP=(k/m)I\). Here \(m=n-1\) for the transverse space in Theorem 1, or \(m=n\) at the centred input. Components along the distinguished mean direction must be accounted for separately.

This is a bound on **Euclidean tensor overlap**, not on the realised output error removed.

**PROVEN — Haar overlap alone cannot bound the removed price.** Consider the rotationally invariant linear future
\[
g_a(h)=b(a^\top h),
\]
where \(b\) is fixed and \(a\sim N(0,I_m)\). Let the fixed defect have first moment \(v\). Its error is
\[
Z=b(a^\top v).
\]
Choose the future-dependent one-dimensional subspace \(V=\operatorname{span}(a)\). Correcting exactly the component \(Pv\), and leaving \((I-P)v\) unchanged, gives
\[
Z_{\rm residual}=b\,a^\top(I-P)v=0.
\]
Yet \(P\) is Haar and
\[
\mathbb E\|Pv\|^2=\|v\|^2/m.
\]

Thus a subspace can capture only \(1/m\) of the defect’s Euclidean energy while removing **all** its realised price. Selection and pricing use the same future.

This is an exact counterexample to an inference from rotational invariance alone. It is not a proof that the stipulated full random ReLU network has a rank-one future or that one direction removes its actual defect.

**PROVEN UNDER an independently Haar-oriented linear future.** More generally, let \(A\) have singular values \(s_1\ge\cdots\), Haar right singular vectors independent of those values, and let \(P\) retain its top \(k\) right singular directions. For fixed \(v\),
\[
\frac{\mathbb E\|APv\|^2}{\mathbb E\|Av\|^2}
=
\frac{\mathbb E\sum_{i\le k}s_i^2}
{\mathbb E\sum_i s_i^2}.
\]
Conditional on the singular values, every squared coordinate of the rotated \(v\) has expectation \(\|v\|^2/m\). Also, \(APv\) and \(A(I-P)v\) are orthogonal, so this is genuinely removed error energy.

The controlling dimension in this example is the **future’s spectral concentration**, rather than the defect’s rank. For anisotropic clouds and nonlinear futures, the interaction of all three structures matters.

**PROVEN — two further qualifications.**

1. A ratio of expected prices and the expectation of a realised-price ratio are different quantities. Near-zero realised errors can make the latter unstable.
2. “Correct one component” need not reduce squared error if the removed and retained components previously cancelled. Its reduction fraction can be negative.

**HEURISTIC — conclusion for the specified MLP.** A useful future-chosen-subspace bound would require a theorem about the joint law of the selected subspace, the future’s amplification, and the defect. Theorem 1 alone does not provide it. I have not established such a theorem for \(256\times32\).

## Q4. Provable computational restrictions, and why they do not extend unconditionally

**PROVEN — an operational restricted-information model.** Suppose the future is accessible only through a transcript \(\mathcal T\), and the algorithm must estimate a square-integrable target \(Z\) from the past and that transcript. Then
\[
\boxed{\;
\inf_{\widehat Z\ {\rm measurable}}
\mathbb E\|Z-\widehat Z\|^2
=\mathbb E\,\operatorname{tr}\operatorname{Cov}(Z\mid\mathcal A,\mathcal T).
\;}
\]
The conditional-expectation orthogonality proof is the same as in Q2. This is sharp and applies to adaptive transcripts.

For Gaussian matrix–vector queries, adaptive orthonormal query directions leave a fresh Gaussian matrix on the unqueried complement. Inductively, the next direction is fixed given the previous transcript; its Gaussian column is independent of the remaining orthogonal columns. Conditioning on that response removes precisely that column.

Consequently, the conditional kernel calculation gives a genuine lower bound for an implementation whose only future access is the stated sketch.

**PROVEN — a concrete MLP oracle example.** Consider one layer, Gaussian input, and access to \(W=\sigma B\) only through \(q\) adaptive orthonormal column queries \(Bv_j\). The exact target is
\[
Y_i=\frac{\sigma}{\sqrt{2\pi}}\|b_i\|.
\]
After the queries, let
\[
a_i=\sum_{j=1}^q(b_i^\top v_j)^2.
\]
Conditional on the transcript,
\[
Y_i\stackrel{\rm law}{=}
\frac{\sigma}{\sqrt{2\pi}}\sqrt{a_i+U_i},
\qquad U_i\overset{\rm iid}{\sim}\chi^2_{n-q}.
\]
Therefore the optimal conditional squared error is exactly
\[
\frac{\sigma^2}{2\pi}
\sum_i\operatorname{Var}_{U_i}\sqrt{a_i+U_i},
\]
strictly positive for \(q<n\). The posterior Gaussian-complement argument proves the distribution; conditional expectation attains the bound.

**PROVEN — why that is not a lower bound for explicit-weight algorithms.** If the entries of \(W\) are available, all row norms above can be computed in \(O(n^2)\) arithmetic. Restricting the number of black-box products can therefore exclude a cheap legal computation in the original problem.

Similarly, counting VJPs alone says little if unrestricted computation on the weights remains free. A valid computational theorem must specify all charged access and operations. Oracle restrictions are meaningful for implicit operators, but their applicability to an explicit-weight MLP must be justified.

**PROVEN — an unconditional annealed-price extension is false, even for one ReLU layer.** Here is an actual counterexample within the stipulated activation and weight model.

Choose \(N>n+r\) fixed, pairwise nonparallel nonzero states \(h_1,\ldots,h_N\), where \(r\) is the number of any desired fixed linear moment constraints. Let
\[
G(W)_{ij}=\operatorname{ReLU}(w_i^\top h_j).
\]
Append the \(r\) constraint rows to \(G(W)\). The resulting matrix has a nontrivial nullspace. Choose measurably a unit vector \(a(W)\) in it and set
\[
\Delta_W=\sum_{j=1}^Na_j(W)\delta_{h_j}.
\]
Then
\[
\langle g_W,\Delta_W\rangle=0
\]
and every appended constraint is satisfied.

Nevertheless, the fixed annealed Gram matrix
\[
K_{ij}=\mathbb E_W[g_W(h_i)\cdot g_W(h_j)]
\]
is strictly positive definite. To prove this, suppose
\[
\sum_jc_j\operatorname{ReLU}(w^\top h_j)=0
\]
Gaussian-almost everywhere. Continuity makes it zero everywhere. On the hyperplane \(w^\top h_j=0\), choose a point lying on none of the other hyperplanes; this is possible because they are distinct and \(n\ge2\). All other terms are locally linear, while the \(j\)-th term has a gradient jump \(c_jh_j\). That jump must vanish, so \(c_j=0\). Thus the ridge functions are linearly independent in Gaussian \(L^2\), proving strict positivity.

It follows that
\[
a(W)^\top Ka(W)\ge\lambda_{\min}(K)>0
\]
although the realised error is zero.

This disproves both the naive annealed identity for adaptive defects and any positive uniform domination of realised adaptive price by that annealed quadratic form. The example can preserve mass and any prescribed finite list of moments.

**PROVEN — unrestricted small reconstructions need not lose the answer.** For a fixed future and a law \(P\), consider
\[
z(h)=(1,g_1(h),\ldots,g_n(h)).
\]
Its expectation lies in the finite-dimensional span of \(\{z(h)\}\): every linear functional annihilating that span also annihilates the expectation. Choose at most \(n+1\) values \(z(h_j)\) spanning it and express \(\mathbb E_Pz(h)\) as their linear combination. The resulting signed atomic measure \(Q\) satisfies
\[
Q(\mathbb R^n)=1,\qquad \int g\,dQ=\int g\,dP.
\]

Such reconstructions can be chosen at every cut, making every propagated defect zero. Their coefficients require the very expectations being sought; this proves an absence of a representation-size obstruction, not an efficient algorithm.

**PROVEN — what survives.** Conditional pricing and telescoping remain exact. Lower bounds for the total estimator additionally need to handle cross-layer cancellation:
\[
\left\|\sum_l\langle g_l,\Delta_l\rangle\right\|^2
\]
cannot generally be lower-bounded by a positive constant times the sum of individual squared prices.

**CONJECTURE — unresolved computational question.** A meaningful running-time lower bound for future-aware algorithms with full access to these random-network weights may exist. Neither the supplied results nor the arguments above establish one. The counterexamples rule out particular information and pricing arguments, not computational lower bounds as a category.

## Q5. Hybrids and exactly integrable controls

**PROVEN — bias and residual-variance decomposition.** Fix the network and condition on all surrogate-fitting randomness. Write
\[
Z=h_L(X),\quad C=c(h_l(X)),\quad R=Z-C,
\]
and define
\[
b=\mathbb E_Qc-\mathbb E_PC.
\]
For
\[
\widehat Y=\mathbb E_Qc+\frac1N\sum_{i=1}^NR(X_i),
\]
assume the fresh randomized sampling rule is unbiased for \(R\), conditional on the fitted surrogate. Then
\[
\widehat Y-Y=b+\varepsilon_N,\qquad
\mathbb E[\varepsilon_N\mid c,Q]=0,
\]
so
\[
\boxed{\;
\mathbb E\|\widehat Y-Y\|^2
=\|b\|^2+\mathbb E\|\varepsilon_N\|^2.
\;}
\]
If fitting is random, average the two conditional terms. Reusing fitting points without a corresponding unbiasedness argument can introduce additional terms.

In particular, increasing \(N\) does not remove a fixed closure error in \(\mathbb E_Qc\).

**PROVEN — equal-cost criterion.** Let

\[
V=\operatorname{tr}\operatorname{Var}(Z),\qquad
\beta=\|b\|^2/V,\qquad
\eta=\operatorname{tr}\operatorname{Var}(R)/V.
\]

Let \(B\) be setup cost, \(a\) the cost per residual sample, and \(C_{\rm tot}\) the total budget, all in full-forward-pass units. Thus
\[
N=\left\lfloor\frac{C_{\rm tot}-B}{a}\right\rfloor.
\]
Define the residual sampler’s gain \(G_R(N)\) by
\[
\mathbb E\|\varepsilon_N\|^2=\frac{\eta V}{NG_R(N)}.
\]
Against a baseline using \(N_0=\lfloor C_{\rm tot}\rfloor\) samples with gain \(G\), the exact criterion is
\[
\boxed{\quad
\beta+\frac{\eta}{NG_R(N)}<\frac1{N_0G}.
\quad}
\]

Ignoring integer rounding, an unbiased hybrid beats that sampler precisely when
\[
\boxed{\quad
\eta<\frac{G_R}{aG}\left(1-\frac B{C_{\rm tot}}\right).
\quad}
\]

For a biased hybrid the criterion becomes
\[
\eta<
\frac{G_R(C_{\rm tot}-B)}a
\left(\frac1{GC_{\rm tot}}-\beta\right),
\]
which requires a positive right-hand side.

Setup must include closure, fitting, pilot trajectories, and backward work. Under the supplied VJP cost model, \(q\) VJPs through a tail of length \(t\) contribute approximately
\[
B_{\rm backward}\simeq (2\text{–}3)\,q\,t/L.
\]
Every residual sample still evaluates the full output, so ordinarily \(a\ge1\), with surrogate evaluation added.

**PROVEN — variance reduction alone does not determine RQMC gain.** The criterion needs \(G_R\), not just \(\eta\). RQMC variance depends on the residual’s structure under the sampling transform; it need not inherit the original integrand’s gain. The formula above follows directly from defining both actual variances and comparing them.

**PROVEN — best controls in an exactly integrable space.** Let \(\mathcal U\) be the closed span of available scalar controls whose means are exactly known, centred to have mean zero. For vector output, apply this space componentwise. The optimal control is
\[
c_*=\Pi_{\mathcal U}(Z-\mathbb EZ),
\]
and the smallest residual variance is
\[
\boxed{\;
V-\|\Pi_{\mathcal U}(Z-\mathbb EZ)\|_{L^2}^2.
\;}
\]
Orthogonal projection proves this by Pythagoras. Knowing the means does not mean that the optimal coefficients are already known; estimating them costs something.

For example, linear controls in \(H=h_1\) have exact centring
\[
\mathbb EH_i=\|w_{1,i}\|/\sqrt{2\pi}.
\]
Writing \(\Sigma_H=\operatorname{Cov}(H)\) and \(B_H=\operatorname{Cov}(Z,H)\), their best explained variance is
\[
\operatorname{tr}(B_H\Sigma_H^\dagger B_H^\top).
\]
This follows by minimising the quadratic regression loss over matrices multiplying \(H-\mathbb EH\).

**PROVEN — chaos version.** For a standard Gaussian variable \(\xi\), write the value function
\[
F(\xi)-\mathbb EF=\sum_{d\ge1}F_d(\xi),\qquad
v_d=\|F_d\|_{L^2}^2.
\]
If the available controls include every Gaussian polynomial of degrees \(1,\ldots,p\), then
\[
\eta_{\rm opt}=\frac{\sum_{d>p}v_d}{\sum_{d\ge1}v_d}.
\]
Different Hermite degrees are orthogonal, and every positive-degree Hermite polynomial has known mean zero.

If controls are restricted to polynomials of \(k\) Gaussian directions \(V\), write \(F_d=I_d(T_d)\) with
\[
\|F_d\|_2^2=d!\|T_d\|_F^2.
\]
Their optimal explained variance is
\[
\sum_{d=1}^p d!\,\|(VV^\top)^{\otimes d}T_d\|_F^2.
\]
Gaussian conditioning retains exactly the tensor components in those directions.

**PROVEN — first-layer-law qualification.** The post-ReLU state \(h_1\) is not Gaussian. A polynomial of its Gaussian preactivation need not be a function of \(h_1\). For controls restricted literally to \(h_1\), the general projection formula applies, but a simple Hermite-degree cutoff requires an additional description of the allowed space.

Moreover, “the law is explicit” does not supply a cheap integration algorithm for every function of \(h_1\). The unrestricted control \(c(h_1)=g_1(h_1)\) has zero residual, but knowing its mean is the original problem. The meaningful opportunity is a restricted family with both cheap, exact means and large explained variance.

## Q6. Width scaling

**PROVEN — the error–cost requirement.** Let a deterministic future-aware closure cost \(C_n\) passes and have normalized squared error \(e_n\). Its gain over MC at that cost is
\[
G_n^{\rm closure}=\frac1{C_ne_n}.
\]
An unbounded gain therefore requires
\[
C_ne_n\longrightarrow0.
\]

Under schoolbook matrix arithmetic, \(O(n^3)\) work per layer costs \(C_n=\Theta(n)\) passes. Such a closure needs
\[
e_n=o(1/n)
\]
for an unbounded gain. An error law \(e_n=\Theta(L/n^2)=\Theta(1/n)\) at \(L=\alpha n\) yields only bounded gain at that cost.

**HEURISTIC — interpretation of the supplied measurements.** The measured radius-corrected trend is consistent with the latter error scale, but it does not prove that asymptotic law, an implementable matrix-cost recursion, or a limitation on future-aware corrections.

**PROVEN — what the mean-degree identity says.** For the input map \(F_W(X)=h_L(X)\), let \(v_d(W)\) be its centred Hermite energies. Gaussian Sobolev orthogonality gives
\[
V(W)=\sum_{d\ge1}v_d(W),\qquad
\mathbb E_X\|J_W(X)\|_F^2=\sum_{d\ge1}d\,v_d(W).
\]

For the random He-ReLU network,
\[
\mathbb E_{W,X}\|J_W(X)\|_F^2=n.
\]
To verify this, condition on a layer input \(h\) and its input Jacobian \(A\). A fresh row \(w\) contributes
\[
\mathbf1_{\{w^\top h>0\}}\|w^\top A\|^2.
\]
The squared norm is even under \(w\mapsto-w\), while the gate selects one half of the Gaussian law. Summing \(n\) rows gives
\[
n\cdot \frac12\cdot\frac2n\|A\|_F^2=\|A\|_F^2.
\]
Starting from \(A=I_n\) proves the identity. On dead regions \(h=0\), the preceding Jacobian is zero almost everywhere, so they cause no exception.

Hence
\[
\boxed{\;
\frac{\sum_d d\,\mathbb E_Wv_d(W)}
{\sum_d\mathbb E_Wv_d(W)}
=\frac n{\mathbb E_WV(W)}.
\;}
\]
This is a variance-weighted annealed mean degree, not the expectation of the per-network ratio.

**PROVEN — a large mean degree does not imply little low-degree variance.** A degree distribution can put mass \(1-1/n\) at degree \(1\) and \(1/n\) at degree \(n^2\). Its mean is \(\Theta(n)\), while degree one captures \(1-o(1)\) of its variance.

This is a logical counterexample to an inference from the first spectral moment alone, not a construction of the specified MLP spectrum. A lower bound against low-degree controls needs actual tail-mass information or stronger moment/concentration assumptions.

**PROVEN — what predictive dimension would imply.** For the true cloud, define
\[
\eta_l(V)=
\frac{\mathbb E\|g_l(H)-\mathbb E[g_l(H)\mid V^\top H]\|^2}
{\operatorname{tr}\operatorname{Var}(g_l(H))}.
\]
Conditional expectation minimises squared prediction error, so every surrogate based only on \(V^\top H\) has residual variance at least \(\eta_l(V)\).

Consequently, a certified bound
\[
\inf_{\dim V\le k_n}\eta_l(V)\ge c>0
\]
would prevent those controls from obtaining a diverging MC variance-reduction factor. It would not by itself lower-bound deterministic integration cost.

**HEURISTIC — scope of the supplied \(N(l,\varepsilon)\) values.** The relevance report identifies these as point estimates for exhibited subspaces on Gaussianised clouds, hence upper bounds on the optimal predictive dimension up to sampling error. They are not certified lower bounds for all future-chosen subspaces, and they do not establish width scaling.

**PROVEN UNDER explicit hybrid scaling hypotheses.** For an exactly centred control, if
\[
B_n/C_n\to0,\qquad a_n=O(1),\qquad \eta_n\to0,
\]
then using ordinary MC on the residual gives gain over ordinary MC
\[
\frac{1-B_n/C_n}{a_n\eta_n}\longrightarrow\infty.
\]
For a biased control, the additional necessary contribution is \(C_n\beta_n\); divergence requires
\[
C_n\beta_n+
\frac{a_n\eta_n}{G_{R,n}(1-B_n/C_n)}
\longrightarrow0.
\]
These are direct consequences of Q5’s error–cost identity.

## Single strongest defensible negative statement

**PROVEN UNDER a fixed-defect, sketch-only additive-correction model.** Suppose \(M_0=0\), and a collection of degrees \(\mathcal D\) carries fraction \(\gamma\) of the forward price. If
\[
r_\infty(M_d)\ge cn\qquad(d\in\mathcal D),
\]
then every correction measurable from
\[
(W_{l+1}V,W_{l+2},\ldots,W_L),
\qquad V\ \text{past-measurable},\quad \dim V=k,
\]
leaves expected squared error at least
\[
\boxed{\;
\gamma\left(1-\frac{k}{cn}\right)_+
\mathbb E_F|\langle g,\Delta\rangle|^2.
\;}
\]
This follows by combining Q2’s exact posterior-risk formula with its tensor-flattening bound. Thus \(k=o(n)\) cannot remove a nonvanishing diffuse share of that fixed defect’s price.

This does **not** bound unrestricted future-dependent reconstructions, future-chosen subspaces, or the total error after cross-layer cancellation.

## Single strongest positive possibility

**CONJECTURE — a future-built control with a cheaply exact mean could give a growing advantage.** A surrogate expressed in analytically integrable input or first-layer features might capture \(1-o(1)\) of the output variance while keeping setup amortizable and evaluation cost bounded in forward-pass units.

**PROVEN UNDER those approximation and cost hypotheses:** the unbiased residual hybrid has unbounded gain over MC by Q6. No annealed-pricing or Haar-overlap argument above excludes it. Whether such a surrogate exists and can be constructed cheaply for \(L=\alpha n\) is not established by the supplied measurements or by this analysis.
