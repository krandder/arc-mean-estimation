# gpt-6-astra round 2 answer (extracted from astra_r2.raw; model line gpt-6-astra; r2 exit 0 05:41:36Z)

**PROVEN:** A2’s finite-width identity is correct, and its radius coefficient satisfies the stronger bound \(b_0^{(n,t)}\ge 1/\pi\) for every \(t\ge1\).  
**PROVEN:** A5 needs no cross-layer noncancellation assumption, but applying it to ARC requires correcting CHECK-1: `augment` is not Gaussian, `avg_metric=True` breaks the proposed reconstruction, and the code also floors variances.  
**PROVEN UNDER a `simple`-specific radius hypothesis:** the obstruction extends to actual K = 2 `simple`. A polynomial floor for actual `augment`, or a general exponent \(p_K\), remains unproved.

Definitions below are definitions; assertions carry the requested labels. I use the annealed normalization
\[
\mathcal R=\frac{\mathbb E_W\|\widehat\mu-\mu\|^2}{\mathbb E_W V(W)}.
\]
This differs from \(\mathbb E_W[\mathrm{nMSE}(W)]\). I read all six requested files and the relevant ARC implementation. No files were modified.

**1. Claim-by-claim audit**

**A1 — correct. PROVEN.** The telescoping identity holds for finite signed measures with the necessary integrability. For the more general “linear functional” formulation, its domain must contain every function used in the telescope.

**A2 — main identity correct; two qualifications and one substantive correction. PROVEN.**

For a fixed remaining suffix \(F'\), expand the vector-valued function
\[
G_{F'}(z)=g_{F'}\!\left(\sqrt{2/n}\,z_+\right)
\]
in orthonormal multivariate Hermites. Coordinatewise Parseval and Mehler give
\[
\mathbb E_{Z,Z'}[G_{F'}(Z)\cdot G_{F'}(Z')]
 =\sum_{d\ge0}s^d\sum_{|\alpha|=d}
       \|\widehat G_{F',\alpha}\|^2.
\]
Averaging over \(F'\) therefore gives nonnegative coefficients
\[
b_d^{(n,t)}
 =\mathbb E_{F'}\sum_{|\alpha|=d}\|\widehat G_{F',\alpha}\|^2.
\]

The proof’s statement \(\mathbb E_Z\|G_{F'}(Z)\|^2=1\) is generally false with \(F'\) fixed. The correct statement is
\[
\mathbb E_{F',Z}\|G_{F'}(Z)\|^2=1.
\]
That suffices to prove, exactly at finite width,
\[
\boxed{\sum_d b_d^{(n,t)}=1.}
\]
The vector output causes no additional problem. Your absolute-integrability argument justifies interchanging the series and signed integrals.

For \(t=0\), handle the identity map separately: \(b_1=1\), all other coefficients zero. Define the features to be zero at \(h=0\).

**PROVEN: the finite-width radius coefficient does not decay exponentially with depth.** In fact,
\[
\boxed{b_0^{(n,t+1)}\ge b_0^{(n,t)}\ge 1/\pi,\qquad t\ge1.} \tag{20}
\]
To see this, start with independent first-layer Gaussian vectors, corresponding to Mehler correlation \(s=0\), and propagate their ReLU outputs through the same remaining weights. For any two current states \(a,b\),
\[
\mathbb E_W[\operatorname{relu}(Wa)\cdot\operatorname{relu}(Wb)]
 =\|a\|\|b\|\kappa_1(c)
 \ge \|a\|\|b\|c=a\cdot b.
\]
Thus their expected inner product increases with each additional layer. Initially it is \(1/\pi\).

The quantity \(a_n^{2(t-1)}/\pi\) from round 1 is a lower bound obtained from the **mean output over the suffix**. It is not the exact Mehler coefficient \(b_0\). The “finite-width radius feature decays like \(e^{-5t/(4n)}\)” sentence should be dropped.

**HEURISTIC:** “The remaining coefficient mass sits at degrees of order \(t^2\)” needs a stated coefficient-distribution theorem. A characteristic degree inferred from mass and first moment does not alone establish concentration at that scale.

**A3 — wrong as worded; the useful weaker statement is correct. PROVEN.**

Moment matching guarantees \(M_1(\Delta)=0\). It generally does **not guarantee** \(M_d(\Delta)=0\) for \(d\ne1\). But “every \(d>K\) feature survives” is false.

For a unit vector \(v\), take
\[
\Delta=\sum_{j=0}^{K+1}(-1)^j{K+1\choose j}\delta_{(j+1)v}.
\]
It annihilates every polynomial of degree at most \(K\), while
\[
M_d(\Delta)
 =v^{\otimes d}\sum_j(-1)^j{K+1\choose j}(j+1)=0
\]
for **every** \(d\), including \(d=0\). This is a nonzero signed measure invisible to every positively homogeneous query.

Two further corrections matter:

- **PROVEN:** On a common sphere of radius \(r\), \(M_d=r^{1-d}\int h^{\otimes d}\,d\Delta\). Consequently moment matching cancels all \(M_d\) with \(d\le K\) on that sphere.
- **PROVEN:** The features obey
  \[
  \operatorname{tr}M_d=M_{d-2}\qquad(d\ge2).
  \]
  They are not independent statistics.

The shell expansion is valid as a finite Taylor expansion with a controlled remainder. The infinite series is not justified merely by \(u=O_P(n^{-1/2})\), particularly for a signed measure with unbounded support. Nor does moment matching ensure that the first permitted coefficient is nonzero.

The notation
\[
M_d=q^{(1-d)/2}\int h^{\otimes d}\,d\Delta\,(1+O(u))
\]
is unsafe: cancellation can make the displayed leading integral zero while the remainder is nonzero. Use the tensor expansion in part 3 below.

**A4 — identities correct; compression interpretation overstated. PROVEN.**

For symmetric \(T\), the Isserlis formula is correct. In particular,
\[
\begin{aligned}
r=3:\quad&
\sigma^6\left(6\|T\|_F^2+9\|\operatorname{tr}T\|^2\right),\\
r=4:\quad&
\sigma^8\left(24\|T\|_F^2+
72\|\operatorname{tr}T\|_F^2+
9|\operatorname{tr}^2T|^2\right).
\end{aligned}
\]
For a past-measurable **symmetric** reconstruction \(\widehat T\),
\[
\mathbb E_w\langle w^{\otimes r},T-\widehat T\rangle^2
 \ge r!\sigma^{2r}\|T-\widehat T\|_F^2.
\]
This is an expected squared-error statement over a fresh probe, not a lower bound on every realized probe.

The probes do not price all components equally: trace components receive additional positive weight. “Uniform Frobenius lower bound” is accurate.

**PROVEN UNDER a flattening-rank constraint:** If
\(\operatorname{rank}\widehat T_{(1)}\le k\), Eckart–Young gives
\[
\|T-\widehat T\|_F^2\ge\sum_{j>k}\sigma_j(T_{(1)})^2.
\]
A CP-rank-\(k\) approximation satisfies that constraint; so does a Tucker approximation whose first-mode rank is at most \(k\). The relevant implication is
\[
\operatorname{rank}\widehat T_{(1)}
 \le \operatorname{CP\,rank}\widehat T,
\]
not the reverse.

**PROVEN:** With exact centering and independent copies,
\[
(K_3)_{ab}
 =\mathbb E[D_aD'_b(D\cdot D')^2].
\]
A split-sample estimator of this expression is unbiased. The qualifications needed by `lib/au.py` are discussed in part 4.

**A5 — mathematical bound correct; implementation coverage needs substantial correction. PROVEN.**

The reverse triangle inequality gives exactly
\[
\sqrt{\mathbb E_F\|\widehat\mu-\mu\|^2}
 \ge \|Q_\ell-P_\ell\|_{k_t}-\sqrt{e_t(Q_\ell)}.
\]
If squaring the right side, use its positive part. The family-infimum version is valid, although the supremum suffix error can make it vacuous.

**PROVEN:** When the last step is exactly \(Q\mapsto\int\operatorname{relu}(Wh)\,dQ\),
\[
\mathbb E_{W_L}\|\widehat\mu-\mu\|^2
 =\|Q_{L-1}-P_{L-1}\|_{k_1}^2.
\]
This needs no assumption about cross-layer cancellation. Earlier errors have already combined in \(Q_{L-1}-P_{L-1}\).

**PROVEN:** It does not, by itself, prove that this final discrepancy is large. In particular, Gaussian mean radius is freely adjustable, so the radius feature alone cannot lower-bound the infimum over all Gaussians. On a positive ray, every cloud has exactly the same homogeneous queries as the point mass at its mean; the Gaussian-family bottleneck can therefore be zero.

**PROVEN by code inspection:** CHECK-1 misses three distinctions.

1. `K=2, kind='augment'` retains a radial third-cumulant tensor and an isotropic fourth-cumulant tensor. Its last mean includes third- and fourth-derivative corrections. It is not a Gaussian expectation.
2. With `avg_metric=True`, replacing \(\|w\|^2\) by \(2\) breaks linear-projection consistency. Generally there is no fixed signed measure \(Q\) whose ReLU expectations equal the resulting row function.
3. [`relu_wick_coef`]( /home/agent/workspaces/mats/work/arc-noisy/ext/mlp_cumulant_propagation/src/mlp_kprop/wick.py:90) replaces every variance below \(10^{-10}\) by \(10^{-10}\). This also prevents the claimed global identity for `simple`.

For the second point, every fixed-\(Q\) expectation must obey
\[
f(cw)=c f(w),\qquad c>0.
\]
The averaged-metric third-cumulant correction scales as \(c^{-1}\), and the fourth-cumulant correction as \(c^{-3}\), rather than as \(c\). This is a direct obstruction to the proposed reconstruction.

**PROVEN UNDER exact metric propagation, a valid Gaussian base, and no variance flooring:** The order-only truncation of the **last mean formula** can be represented by a multivariate finite Gram–Charlier signed measure. This establishes the last-step identity; it does not establish exact moment matching at earlier projections.

**A6 — algebra correct; measurement claim needs qualifications. PROVEN.**

The decomposition is exact. Its terms can be estimated when the relevant expectations have usable sampling or signed-reweighting representations and finite estimator variances.

For `augment`, `au.arc_kprop(..., keep_states=...)` retains only mean and covariance. Passing those to `gauss_push` does not measure its augmented model’s suffix error. With the default averaged metric, the proposed fixed-\(Q\) attribution needs reformulation altogether.

**B1 — wrong as a computational conclusion. PROVEN.**

A4 prices approximation error when a method replaces \(T\) by \(\widehat T\). It does not prove that retaining or querying \(T\) requires dense storage.

Counterexample:
\[
T=\sum_{i=1}^n e_i^{\otimes r}.
\]
Its flattening has participation ratio \(n\), yet it has an \(O(n)\)-size description and
\(\langle w^{\otimes r},T\rangle=\sum_iw_i^r\) costs \(O(n)\). No Frobenius energy is discarded.

**B2 — HEURISTIC, not a theorem.**

The independent-layer-summand description has not been derived. \(W^{\otimes r}\) is not a Haar orthogonal transformation on symmetric tensors; its singular values matter, and nonlinear cumulant updates couple the existing structure to newly generated terms.

**PROVEN:** The proposed flattening test cannot establish rank growth to generic CP rank. Its rank is at most \(n\), whereas generic order-\(r\) CP rank is of order \(n^{r-1}\). Also, \(Ln\) rank-one factors at \(L\asymp n\) reach the generic factor count for \(r=3\), not for every \(r\). Arithmetic-cost crossover and representation-size crossover should be separated.

**B3 — wrong as an “ONLY way” statement. PROVEN.**

Low-rank approximation is one representation class. Sparse tensors, implicit formulas, symmetry, structured contractions, and algorithms answering only the required queries are alternatives. Top-eight flattening energy is a useful diagnostic, not a general computational lower bound.

**C1 — correct arithmetic under the stated cost convention. PROVEN.**

The measured \(108/6.4\approx16.9\) efficiency loss is the stated arithmetic comparison.

**HEURISTIC, using the supplied measurements:** Its empirical inputs concern the recorded variants and \(\sigma=0.001\), not a proved noiseless error law.

**C2 — needs stronger hypotheses; one ratio is reversed. PROVEN UNDER a uniform error-and-cost ladder.**

If \(a_{K+1}/a_K=r\), then each step reduces error by \(n/(rL)\) and worsens efficiency by \(rL\). After \(m\) steps,
\[
\text{efficiency loss}=(rL)^m,\qquad
m\approx\frac{\log(e_2/\varepsilon^2)}{\log(n/(rL))}.
\]
The displayed \(L/a\) should be \(La\) under FORMAL’s definition of \(a\).

The “every finer precision” conclusion requires the ladder to hold uniformly over all orders needed at that precision, with \(rL>1\). A fixed-\(K\) asymptotic or a few measured orders does not supply that hypothesis.

**C3 — correct conditional theorem for the exact Gaussian recursion; not automatically ARC. PROVEN UNDER \(H_R\).**

The quoted empirical slopes remain **HEURISTIC evidence** for their measured implementations. C-LAD remains a **CONJECTURE**.

**D — correct with the stated hypotheses and consistent annealed normalization. PROVEN UNDER \(H_R,H_{\rm ML}\), and the stated closure cost.**

Extending it to ARC `simple` needs the replacement hypothesis below. Extending it to `augment` needs a separate error-floor theorem. At \(256\times32\), the asymptotic separation provides no useful large numerical factor.

**F1 — correct information-theoretically. PROVEN.**

An unrestricted encoder can encode the quantized future output. This gives an upper bound on required code size, with computation charged separately.

**F2 — identity correct under explicit preservation conditions. PROVEN UNDER \(\langle s,\Delta_\ell\rangle=0\) for every \(s\in S_\ell\).**

Then
\[
\langle g_\ell,\Delta_\ell\rangle
 =\langle g_\ell-\operatorname{proj}_{S_\ell}g_\ell,\Delta_\ell\rangle.
\]
“Original problem at depth \(\ell\)” is imprecise: it is integration through the prefix with the suffix-dependent observable \(g_\ell\).

**F3 — measured quantities and computational conclusions are conflated.**

**PROVEN:** The reported \(N(\ell,0.01)\) cannot mean that a linear predictor captures 99% of variance when the reported first-chaos share is substantially below 99%. Selected input directions with nonlinear readout and linear test functions are different objects.

**HEURISTIC:** The pulled-back-query count and its \(L^2n^3\) cost describe a proposed procedure. Gate-dependent pullbacks are not simply fixed linear directions.

**PROVEN:** “Future-awareness changes which statistics are carried, not how many” is false without restricting the representation and algorithm.

**S1 — correct conditional isotropy; conclusion too broad. PROVEN.**

Fresh Gaussian weights are rotationally invariant relative to past-measurable frames. They do not form a uniformly random isometry of the cloud, and A4 still weights trace sectors differently. Isotropy does not establish computational scrambling.

**S2 — HEURISTIC evidence about the learned codes.**

Near-linear prediction of the predictable component does not establish exact deterministic code updates or cheap law propagation.

**S3 — not established as a general information theorem. PROVEN.**

A later state cannot create information about the input that the full earlier state lacked. A later **code** can retain information discarded by the earlier code.

Observed prediction error of a trained decoder is an upper bound on optimal prediction error, not a lower bound. Calling the loss irreducible requires evidence about conditional distributions or Bayes error.

**S4 — correct unrestricted construction. PROVEN.**

For \(c_\ell(h)=Q(g_\ell(h))\), the code transition is the identity. The encoder computation remains the unresolved work.

**PROVEN:** FORMAL’s concluding inference “S1 plus B2, therefore forward compression is impossible” is unsupported. B2 is a heuristic, and even large tensor rank would not establish that computational conclusion.

**2. Bounds covering K = 2**

**PROVEN: the actual `simple` covariance rule has a valid Gaussian reconstruction.**

Let the incoming model be \(N(m,C)\), put
\[
\nu=Wm,\quad B=WCW^\top,\quad
\bar v_i=\max(B_{ii},\tau),\quad
p_i=\Phi(\nu_i/\sqrt{\bar v_i}),\qquad \tau=10^{-10}.
\]
The code’s `simple` rule has
\[
m'_i=\mathbb E(N(\nu_i,\bar v_i))_+,
\]
\[
C'_{ij}=p_ip_jB_{ij}\quad(i\ne j),\qquad
C'_{ii}=\operatorname{Var}(N(\nu_i,\bar v_i))_+.
\]
This covariance is PSD because
\[
C'=DBD+\operatorname{diag}\bigl(C'_{ii}-p_i^2B_{ii}\bigr),
\]
and the Gaussian Hermite expansion gives
\(C'_{ii}\ge p_i^2\bar v_i\ge p_i^2B_{ii}\).

Call this update \(\Gamma_{s,\tau}(T_WQ)\).

The replacement for \(H_R\) is:

\[
\boxed{
(H_{R,s,\tau}):\
\mathbb E_W\!\left[
\int\|h\|\,d\Gamma_{s,\tau}(T_WQ)
-\int\|h\|\,dT_WQ
\right]\ge0
}
\tag{21}
\]
for Gaussian states \(Q\) reached by the recursion. Requiring it for every Gaussian \(Q\) is stronger than necessary.

**CONJECTURE:** \(H_{R,s,\tau}\) holds. The original \(H_R\), concerning exact covariance matching, does not imply it.

**PROVEN UNDER \(H_{R,s,\tau}\): actual `simple` inherits the radius obstruction.**

Let \(\rho_j\) be its radius projection defect. The final variance floor introduces a coordinatewise nonnegative mean correction \(\eta_L\), since Gaussian ReLU expectation increases with variance. Consequently,
\[
\mathbb E e_L
 =\frac{\mathbf1}{\sqrt{\pi n}}
   \sum_{j=1}^{L-1}a_n^{L-j-1}\mathbb E\rho_j
   +\mathbb E\eta_L.
\]
Under (21), all displayed contributions have the same sign, so
\[
\mathbb E\|e_L\|^2
 \ge\frac{a_n^{2(L-2)}}{\pi}(\mathbb E\rho_1)^2.
\tag{22}
\]

The first-layer result from round 1 is
\[
\mathbb E\rho_1^{s}
 =\frac{c_s}{\sqrt n}+o(n^{-1/2}),
\qquad
c_s=\frac9{16}+\frac1{4\pi^2}.
\]
The variance floor changes this first-layer asymptotic by a negligible small-row contribution. Therefore, with \(C_*=\frac52+3\sqrt2\pi\),
\[
\boxed{
\liminf_{n\to\infty}n\mathcal R_{\rm simple}
 \ge \frac{c_s^2}{\pi C_*}e^{-5\alpha/4},
\qquad L=\alpha n+O(1).
}
\tag{23}
\]
The prefactor before the exponential is approximately \(0.0069488\). At \(\Theta(n)\) passes, this gives bounded gain over MC and, under \(H_{\rm ML}\), gain \(O(\log^2n/n)\) against the multilevel sampler.

**PROVEN: an explicit finite-\(n\) version is available.**

For the *unfloored first-layer* simple Gaussian, write \(S=\|G\|^2\), and set
\[
V_{2,n}=\mathbb E(S-n)^2,\qquad
V_{4,n}=\mathbb E(S-n)^4.
\]
The global Taylor bound from round 1 and Cauchy–Schwarz give
\[
\mathbb E\rho_1^s\ge B_n,
\]
where
\[
B_n=
\sqrt n-\frac{V_{2,n}}{8n^{3/2}}
-\frac{3\sqrt{V_{2,n}V_{4,n}}}{8n^{5/2}}
-m_na_n. \tag{24}
\]
Here
\[
V_{2,n}
=\left(\frac52-\frac2{\pi^2}\right)n
 +\frac{11}{2}-\frac4{\pi^2}.
\]

All constants in (24) are explicit finite moments. One convenient representation for evaluating \(V_{4,n}\) is
\[
G_i=r_i\left[
\frac1{\sqrt{2\pi}}+\frac12u_i\cdot Z+
\sqrt{\frac{\pi-2}{4\pi}}\,\epsilon_i
\right],
\]
where \(r_i^2\sim(2/n)\chi_n^2\), \(u_i\) are independent uniform sphere directions, and \(Z,\epsilon\) are independent standard Gaussians. Conditional on \(\|Z\|^2=t\), the \(G_i\) are independent, and their moments through degree eight follow from
\[
\mathbb E r^{2k}=(2/n)^k\prod_{j=0}^{k-1}(n+2j),\qquad
\mathbb E u_1^{2k}=\frac{(2k-1)!!}{\prod_{j=0}^{k-1}(n+2j)}.
\]
Thus (24) involves only finite sums and products.

For the actual first-layer floor, a conservative perturbation allowance is
\[
\epsilon_{n,\tau}
=\sqrt{\frac{n\tau}{2\pi}}
 \left(\frac{e\tau}{2}\right)^{n/4}.
\]
Indeed, flooring increases the first covariance by a nonnegative diagonal matrix; the possible decrease due to changing the Gaussian mean is bounded by its Euclidean increment. Hence
\[
\mathbb E\rho_1^{s,\tau}\ge B_n-\epsilon_{n,\tau}.
\]
Using the round-1 explicit variance upper bound \(U_{n,L}\),
\[
\boxed{
\mathcal R_{\rm simple}\ge
\frac{a_n^{2(L-2)}}{\pi U_{n,L}}
 [B_n-\epsilon_{n,\tau}]_+^2
\quad\text{under }H_{R,s,\tau}.
}
\tag{25}
\]

**HEURISTIC only as a rounded numerical evaluation:** My scalar calculation gave
\[
V_{2,256}\approx593.218269,\quad
V_{4,256}\approx1{,}090{,}029.413,\quad
B_{256}\approx0.02748798.
\]
Equation (25) evaluates to approximately \(1.03\times10^{-5}\) at \(256\times32\). The exact formula is proved; this decimal was not interval-certified.

**PROVEN: the unconditional one-replacement theorem improves.**

Using (20), rather than the weaker suffix-mean bound, exact Gaussianization once after layer 1 satisfies
\[
\mathbb E\|e\|^2\ge\frac1\pi\mathbb E\rho_1^2
\]
at every remaining depth. Consequently,
\[
\boxed{
\liminf n\mathcal R_{\rm one\ replacement}
 \ge\frac{81}{256\pi C_*}\approx0.00636284
}
\tag{26}
\]
for every fixed \(\alpha>0\). There is no exponential-in-\(\alpha\) attenuation in this bound. This strengthening does not remove cancellation from a repeated closure.

**PROVEN: there is a hypothesis-free last-row bound for both actual implementations.**

Condition on the prefix and its algorithmic state. Write a fresh row as
\[
w=\sqrt2\,R\,U,\qquad R=\chi_n/\sqrt n,\qquad \mathbb ER^2=1.
\]
Let \(f(R,U)\) be the algorithm’s actual last-row output, including metric approximation and variance flooring. The true output mean has the form \(R\,t(U)\). Orthogonal projection onto the span of \(R\) yields
\[
\boxed{
\mathbb E_{W_L}\|e_L\|^2
 \ge n\,\mathbb E_U\left[
 \mathbb E_R f(R,U)^2-
 \bigl(\mathbb E_R[Rf(R,U)]\bigr)^2
 \right].
}
\tag{27}
\]
This is a computable one-dimensional radial-integral certificate. It needs neither a reconstructed measure nor a cancellation hypothesis.

**PROVEN:** For both K = 2 variants, the odd part of the last-row estimate remains \(w\cdot m/2\), including the variance floor. Therefore
\[
\mathbb E_{W_L}\|e_L\|^2\ge\frac12\|m-\mu_{L-1}\|^2.
\tag{28}
\]
Iterating gives an unconditional transfer of any early-layer error, with factor \(2^{-(L-j)}\). This is exponentially weak at \(L=\alpha n\).

**PROVEN UNDER no variance flooring:** For default averaged-metric `augment`,
\[
f(R,U)=R A(U)+R^{-1}B(U)+R^{-3}C(U).
\]
Here \(B,C\) are its third- and fourth-cumulant corrections evaluated at row norm \(\sqrt2\). Equation (27) becomes
\[
\mathbb E_{W_L}\|e_L\|^2
 \ge n\,\mathbb E_U
 \begin{pmatrix}B&C\end{pmatrix}
 J_n
 \binom BC,
\]
where, for \(n>6\),
\[
J_n=
\begin{pmatrix}
\dfrac2{n-2}&
\dfrac{4n}{(n-2)(n-4)}
\\[6pt]
\dfrac{4n}{(n-2)(n-4)}&
\dfrac{8n^2(n-3)}{(n-2)^2(n-4)(n-6)}
\end{pmatrix}. \tag{29}
\]
It is positive definite. Its smallest eigenvalue is asymptotic to \(8/(5n^2)\).

For the actual floor, either use (27) directly or restrict the radial integral to the region where flooring is inactive and replace the moments in (29) by truncated chi moments. That gives a valid bound for the actual code.

**CONJECTURE / unresolved:** A polynomial lower bound on the required penultimate radius defect or on the correction energies in (27)–(29). A5 does not establish it. Thus I do not have a hypothesis-free polynomial separation for full `augment`.

**3. Order \(K\), radial normalization, and \(p_K\)**

**PROVEN: moment matching alone does not determine a first-layer exponent.**

Put \(S=\|h\|^2\), \(q\asymp n\), and \(\Delta=Q-P\). For any finite Taylor order,
\[
M_0(\Delta)
 =\sqrt q\sum_j {1/2\choose j}q^{-j}
       \int(S-q)^j\,d\Delta+\text{remainder}. \tag{30}
\]
Matching moments through degree \(K\) cancels \(j\le\lfloor K/2\rfloor\).

For \(d>0\),
\[
\boxed{
M_d(\Delta)=
q^{(1-d)/2}\sum_j
 { (1-d)/2\choose j}q^{-j}
 \int h^{\otimes d}(S-q)^j\,d\Delta
 +\text{remainder}.
}
\tag{31}
\]
The \(j\)-th integral is a polynomial moment of degree \(d+2j\). For \(d>K\), none is forced to vanish. Equation (31), with an absolute remainder estimate, replaces A3’s relative-error expression.

**PROVEN UNDER an explicit radial extensivity and remainder hypothesis:** Suppose the first unmatched radial moment is \(j=m\), with
\[
\int(S-q)^m\,d\Delta=c_m n+o(n),\qquad c_m\ne0,
\]
and the remainder in (30) is \(o(n^{3/2-m})\). Then
\[
M_0(\Delta)\asymp n^{3/2-m},
\qquad |M_0(\Delta)|^2\asymp n^{-(2m-3)}. \tag{32}
\]
This gives the radial obstruction exponent
\[
p_{\rm rad}=2m-3.
\]
The extensivity and remainder hypotheses are essential; concentration alone does not imply them.

**PROVEN UNDER exact retained cumulants and inclusion of the required Gram–Charlier products:** ARC’s extra traces can cancel additional *polynomial radial moments*.

For example,
\[
\mathbb E\|H\|^4
 =q^2+2\operatorname{tr}C^2+4m^\top Cm
   +4m\cdot\operatorname{tr}\kappa_3
   +\operatorname{tr}^2\kappa_4. \tag{33}
\]

Therefore:

- At K = 3, retaining the scalar fourth-cumulant trace cancels the \(j=2\) radius term that plain degree-three truncation would leave.
- At K = 2, retaining \(\operatorname{tr}\kappa_3\) and \(\operatorname{tr}^2\kappa_4\), together with exact mean and covariance, also cancels that term.
- More generally, for odd \(K\), the extra fully traced cumulant of order \(K+1\) completes the next radial moment.
- For even augmented \(K\), the retained trace sector of order \(K+1\) and scalar trace of order \(K+2\) complete one additional radial moment.

The resulting **conditional radial table**, not an actual-algorithm error table, is:

| Ideal reconstruction | First potentially unmatched \(j\) | \(p_{\rm rad}\) under (32) |
|---|---:|---:|
| Moments through \(K\) only | \(\lfloor K/2\rfloor+1\) | \(2\lfloor K/2\rfloor-1\) |
| `simple`, even \(K\) | \(K/2+1\) | \(K-1\) |
| `simple`, odd \(K\), exact extra trace | \((K+3)/2\) | \(K\) |
| `augment`, even \(K\), exact retained traces | \(K/2+2\) | \(K+1\) |
| `augment`, odd \(K\) | \((K+3)/2\) | \(K\) |

**PROVEN:** This cancellation concerns the leading Taylor term, not exact preservation of \(M_0\). Matching finitely many radial moments does not match mean radius.

**HEURISTIC:** Under suitable extensive contraction estimates, the ideal K = 2 augmented reconstruction should remove the \(n^{-1/2}\) first-layer radius term and leave an \(n^{-3/2}\) term. I have not established this remainder estimate for ARC’s actual diagram-truncated, averaged-metric recursion.

**PROVEN:** The omitted \(M_d\) can remain important after the radius term is canceled. Trace augmentation leaves traceless tensor components. In particular, an augmented K = 2 reconstruction can preserve (33) while retaining a substantial traceless third-cumulant defect.

**HEURISTIC:** If the first omitted order-\(r\) cumulant has Frobenius norm of order \(\sqrt n\), standard fixed-degree counting often gives squared normalized-feature defects of order \(n^{2-r}\). This can be larger than the residual radius defect. Establishing it requires controlling the contractions and the normalization remainder in (31). Pricing it at suffix depth \(\alpha n\) additionally requires bounds on the relevant \(b_d^{(n,t)}\).

**PROVEN:** No unique \(p_K\) for the full ARC algorithm follows from these first-layer calculations. There are three separate gaps: actual projection error, propagation through a growing-depth suffix, and accumulation or cancellation in the repeated recursion.

**PROVEN UNDER a full-algorithm floor \(\mathcal R_K\ge b_Kn^{-p_K}\) and cost \(\Theta(n^{K-1})\) passes:** Round-1 equation (12) gives
\[
G_{\rm MC}=O(n^{p_K-K+1}),\qquad
G_{\rm best\ sampler}
 =O(\log^2n\,n^{p_K-K}). \tag{34}
\]
A floor with \(p_K\le K\) rules out a polynomial advantage over the multilevel sampler. The ideal radial table cannot be inserted into (34) without proving the missing full-recursion transfer.

**4. Correlation growth and the flattening measurement**

**PROVEN:** The proposed quantity
\[
\operatorname{PR}(K_3)=
\frac{(\operatorname{tr}K_3)^2}{\operatorname{tr}(K_3^2)}
\]
is a participation ratio. It differs from the usual stable rank
\(\operatorname{tr}K_3/\|K_3\|_{\rm op}\).

Also, \(\min(\ell n,n)=n\) for every integer \(\ell\ge1\). The proposed bound therefore asserts uniformly large participation ratio, not observable growth with depth.

**PROVEN: replica moments provide an exact target, but not yet the desired estimate.**

With conditionally independent centered replicas \(D_1,\ldots,D_4\),
\[
\operatorname{tr}K_3
 =\mathbb E[(D_1\cdot D_2)^3\mid W],
\]
and
\[
\operatorname{tr}(K_3^2)
 =\mathbb E[
 (D_1\cdot D_2)^2(D_3\cdot D_4)^2
 (D_1\cdot D_4)(D_2\cdot D_3)
 \mid W]. \tag{35}
\]
Centering can be expanded using additional replicas, allowing these annealed quantities to be expressed through a finite replica Gram process.

Cauchy–Schwarz gives
\[
\mathbb E_W\operatorname{PR}(K_3)
 \ge
 \frac{(\mathbb E_W\operatorname{tr}K_3)^2}
      {\mathbb E_W\operatorname{tr}(K_3^2)}. \tag{36}
\]
Set the ratio to zero when \(K_3=0\).

**CONJECTURE, clean but stronger than the requested conclusion:** For a specified depth window and fixed \(\alpha\), there is \(C_\alpha<\infty\) such that
\[
\mathbb E_W\operatorname{tr}(K_{3,\ell}^2)
 \le \frac{C_\alpha}{n}
       \bigl(\mathbb E_W\operatorname{tr}K_{3,\ell}\bigr)^2,
\qquad 1\le\ell\le\alpha n. \tag{37}
\]
Then (36) proves annealed participation ratio at least \(n/C_\alpha\).

I do not have a proof of (37), and would not assume it for the raw tensor without checking coherent radial components. Uniform almost-sure versions fail on degenerate or nearly ray-like networks.

**PROVEN: a suitable falsification measurement is width scaling, not one high-rank plot.**

Measure the annealed numerator and denominator in (36) separately at fixed \(\ell/n\), and measure the distribution of per-network PR. Systematic sublinear PR, or growth of
\[
\frac{n\,\mathbb E\operatorname{tr}(K_3^2)}
 {(\mathbb E\operatorname{tr}K_3)^2},
\]
refutes the corresponding uniform constant claim. At \(256\times32\), reliable top-eight capture above 50% refutes FORMAL’s particular finite-size prediction, but not every possible \(cn\) bound.

**PROVEN by inspection of `lib/au.py`: measurement corrections are needed.**

- With an exact supplied mean, `K1` and `K2` are unbiased, and their cross-product estimates \(\operatorname{tr}(K_3^2)\) unbiasedly.
- The implemented numerator
  \[
  \left((\operatorname{tr}K1+\operatorname{tr}K2)/2\right)^2
  \]
  is upward biased. The product \(\operatorname{tr}K1\,\operatorname{tr}K2\) is unbiased for the squared trace. The resulting ratio is still not unbiased.
- Held-out projected-energy numerators are unbiased conditional on the selected projector; their reported ratios are not.
- A shared estimated center changes the target tensor and can create dependence between estimates. An independent estimated mean alone does not restore exact centering.
- `fro2_direct` and the Gram trace are algebraically the same statistic, not independent checks.
- The split-half sampling routines can assign incorrect half sizes when a chunk straddles \(N/2\); their advertised independent-half calculations require aligned chunks or an explicit boundary split.
- PSD clipping in `gauss_push` changes the input model. Its contribution must be included in attribution.

**5. What follows about Kelvin’s hypothesis**

**PROVEN:** For finite codes, an exact deterministic trajectory update exists iff
\[
H(Z_{\ell+1}\mid Z_\ell)=0.
\]
This criterion does not say that the code’s probability law can be propagated cheaply.

**PROVEN:** Even when that conditional entropy is positive, the exact transition probabilities
\(P(Z_{\ell+1}\mid Z_\ell)\) propagate the current marginal law exactly. The difficulty may instead be constructing or contracting those transition probabilities. Deterministic code update and distribution update are distinct questions.

**PROVEN:** Cheap threshold transitions can coexist with difficult exact law propagation. Under uniform independent Boolean inputs, computing the exact probability of a weighted threshold includes counting knapsack solutions, despite linear-time evaluation of the threshold on one input. This is a separation example, not a hardness reduction for ARC.

**HEURISTIC, from the supplied measurements:** The learned-code results support the narrower picture that transitions among useful codes can be simple, while their joint probability laws remain inadequately approximated by the tested propagation method.

They do not establish that:

- every adequate code needs more than 256 bits;
- the observed whole-code prediction error is Bayes-optimal;
- every probability-law representation has a \(10^{-3}\)–\(10^{-4}\) bias floor;
- cheap code-law propagation is impossible;
- random-network inference behaves like an unknown-bias table oracle.

**PROVEN:** The “computability-versus-slope split” is a useful conditional cost comparison. If \(b=\log_2 M\) and error means RMS error, \(s\) extra bits per halving implies
\[
M\asymp\varepsilon^{-s}.
\]
Thus slopes \(8\)–\(10\) would lose to sampling’s exponent \(2\) for explicit cell enumeration, while slopes \(1\)–\(1.4\) could win if cell masses and contributions were cheaply computable.

If “error” instead means squared error, sampling’s reference slope is one bit per halving. The convention must be stated.

**HEURISTIC:** The provisional measurements suggest that the tested early codes have accessible laws but poor resolution scaling, while the tested late codes have attractive resolution scaling but no demonstrated cheap law integration. Because these runs were explicitly uncertified, this remains a hypothesis about tested constructions. “The law is not computable” should be replaced by “no sufficiently cheap law computation has been demonstrated.”

**6. What I would retain and drop**

**PROVEN: retain A2 together with (20).** It identifies the exact Hilbert-space discrepancy at finite width, and supplies a depth-uniform radius coefficient. This is the strongest new result in FORMAL.

**PROVEN: retain A5 as a terminal-model theorem.** It genuinely removes the need to analyze cross-layer cancellation when a valid exact last-step reconstruction exists. State its implementation conditions explicitly.

**PROVEN: retain A4 as a tensor-reconstruction lemma.** It gives an exact Gaussian-probe norm and a valid restricted-rank approximation bound.

**CONJECTURE: retain the radius-sign hypotheses and replica inequality as separately testable research targets.** The most useful next tests are fresh-layer tests of (21), and corrected replica measurements for (37).

**PROVEN: drop or weaken** the universal “only way to compress” claims, the finite-width exponential decay of \(b_0\), the assertion that every unmatched \(M_d\) survives, the Gaussian identification of K = 2 `augment`, and the claim that rank growth proves forward-compression impossibility. The evidence currently supports precise restricted obstructions, not that general impossibility statement.

Automatic approval review rejected the optional read-only Python interval-certification calculation as suspected Windows filesystem syntax. The scalar evaluation completed; the interval certificate did not, so the finite decimal estimate above is explicitly uncertified.
