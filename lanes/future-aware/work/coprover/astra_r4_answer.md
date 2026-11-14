**Summary.** **PROVEN:** for every fixed \(L\ge2\), the actual network satisfies \(\operatorname{PR}(M)=\Theta(n)\) with probability tending to one, after specifying the Jacobian at zero. **OPEN here:** the corresponding assertion at \(L=\lfloor\alpha n\rfloor\), and a deterministic spectral limit at that depth. The operator-norm route is sufficient, but strictly stronger than a participation-ratio bound.

Throughout, “OPEN” means that I neither prove nor refute the stated Gaussian-network assertion. Counterexamples below refute specific proposed implications; they do not refute the depth-\(\alpha n\) conjecture.

**A necessary definition — PROVEN.**

The supplied definition \(J(h)=Dg(h)\), “a.e. defined,” needs a convention: Lebesgue-a.e. differentiability is insufficient for the law of \(h_1\).

Almost surely \(W_1\) is invertible, and
\[
a(W_1):=\Pr_x(W_1x\le0)>0.
\]
Thus \(h_1\) has an atom at zero. A positively homogeneous function differentiable at zero must be linear: for every \(v\),
\[
g(v)=\lim_{t\downarrow0}\frac{g(tv)-g(0)}t=Dg(0)v.
\]
Because this network has nonnegative outputs on all of \(\mathbb R^n\), such a linear function must be identically zero. Hence every nonzero future map is nondifferentiable at zero.

I therefore use the usual backpropagation convention
\[
D_j(h)=\operatorname{diag}\mathbf1_{\{\text{preactivation at layer }j>0\}},
\qquad
J(h)=D_LW_L\cdots D_2W_2,
\tag{1}
\]
including \(J(0)=0\). All results below concern this precise definition. For almost every choice of future weights, it agrees with the genuine derivative at law-\(h_1\)-almost every nonzero \(h\): for a fixed nonzero input, preactivations are nonzero until a layer dies; a layer with all strictly negative preactivations makes the subsequent map locally zero. Fubini then gives the assertion.

Although \(\mathbb E_{W_1}a(W_1)=2^{-n}\), its smallness does not eliminate the need to specify \(J(0)\).

With (1), the denominator is positive with high probability even at \(L=O(n)\). Indeed, starting the future map at \(v=(1,\ldots,1)\), each surviving layer dies with conditional probability \(2^{-n}\). Consequently,
\[
\Pr(g(v)\ne0)=(1-2^{-n})^{L-1}.
\]
On this event, \(J(v)v=g(v)\ne0\), and \(J\) is nonzero on a neighborhood of \(v\). The law of \(h_1\) has positive density throughout the open positive orthant, while \(J(0)=0\) on an atom of positive mass. Therefore \(J\) is not almost surely constant, and \(M\ne0\), since \(S\) is positive definite. In particular,
\[
\Pr(\operatorname{tr}M=0)\le (L-1)2^{-n}.
\tag{2}
\]

---

**Q1 — PROVEN for every fixed \(L\ge2\); OPEN for \(L=\lfloor\alpha n\rfloor\).**

Here is a fixed-depth theorem for the actual, dependent gates.

> For each fixed integer \(L\ge2\), there is a deterministic \(c_L>0\) such that
> \[
> \Pr\!\left(c_Ln\le \operatorname{PR}(M)\le n\right)\longrightarrow1.
> \tag{3}
> \]
> The constants in this proof deteriorate exponentially with \(L\); this does not establish a uniform linear lower bound at growing depth.

The proof has three ingredients.

**1. The first-layer covariance is uniformly well-conditioned — PROVEN.**

There are absolute constants \(c_S,C_S>0\) such that
\[
\Pr(c_SI\preceq S\preceq C_SI)\longrightarrow1.
\tag{4}
\]

Write the rows of \(W_1\) as \(d_i u_i^\top\), where \(\|u_i\|=1\), and put \(\rho_{ij}=u_i^\top u_j\).

For the upper bound, Gaussian Poincaré gives, for every \(b\in\mathbb R^n\),
\[
b^\top Sb
=\operatorname{Var}_x\!\left(b^\top\operatorname{ReLU}(W_1x)\right)
\le
\mathbb E_x\|W_1^\top D_1(x)b\|^2
\le \|W_1\|_{\rm op}^2\|b\|^2.
\tag{5}
\]
Poincaré applies to these Lipschitz functions; it also follows by expanding in Gaussian Hermite chaoses, since differentiation weights chaos \(r\) by \(r\ge1\).

For the lower bound, let \(H_4(z)=z^4-6z^2+3\). Direct integration gives
\[
\mathbb E[Z_+H_4(Z)]=-\frac1{\sqrt{2\pi}},
\qquad
\mathbb E H_4(Z)^2=24.
\]
The degree-four term in the Hermite covariance expansion therefore yields
\[
S\succeq
\frac1{48\pi}\,
\operatorname{diag}(d_i)
\,[\rho_{ij}^{\,4}]_{ij}
\,\operatorname{diag}(d_i).
\tag{6}
\]
To justify the PSD inequality, every degree-\(r\) contribution is a nonnegative coefficient times
\[
\operatorname{diag}(d_i)[\rho_{ij}^{\,r}]\operatorname{diag}(d_i),
\]
and \([\rho_{ij}^{\,r}]\) is the Gram matrix of \(u_i^{\otimes r}\).

Gaussian row-norm and spherical-coordinate tails, followed by union bounds, give with probability tending to one
\[
1\le d_i^2\le3,\qquad
\max_{i\ne j}|\rho_{ij}|
\le A\sqrt{\frac{\log n}{n}}.
\tag{7}
\]
For example, representing a uniform direction by \(Z/\|Z\|\) bounds a coordinate tail by
\[
2e^{-nt^2/4}+e^{-cn};
\]
taking \(t=A\sqrt{\log n/n}\) and sufficiently large \(A\) handles all pairs.

The off-diagonal row sums of \([\rho_{ij}^4]\) are consequently at most
\[
A^4\frac{(\log n)^2}{n}=o(1).
\]
Gershgorin gives \([\rho_{ij}^4]\succeq I/2\) eventually, so (6) gives \(S\succeq I/(96\pi)\).

Finally, \(\|W_1\|_{\rm op}\le B\) with probability tending to one for an absolute \(B\). An elementary proof uses \(1/4\)-nets of the two unit spheres: their combined size is at most \(81^n\), each bilinear form is \(N(0,2/n)\), and \(B=10\) suffices. Together with (5), this proves (4).

An immediate consequence, valid regardless of future depth, is
\[
\left(\frac{c_S}{C_S}\right)^2\operatorname{PR}(R_{\rm nl})
\le \operatorname{PR}(M)
\le
\left(\frac{C_S}{c_S}\right)^2\operatorname{PR}(R_{\rm nl})
\tag{8}
\]
on the event (4), whenever these ratios are defined. Indeed, the eigenvalues of the congruence \(S^{1/2}R_{\rm nl}S^{1/2}\) lie between \(c_S\) and \(C_S\) times the corresponding eigenvalues of \(R_{\rm nl}\), by applying the min–max principle to \(R_{\rm nl}^{1/2}SR_{\rm nl}^{1/2}\).

Thus first-layer whitening preserves participation-ratio order with high probability.

**2. At \(L=2\), the nonlinear Jacobian variance has trace of order \(n\) — PROVEN.**

Let \(w_i^\top\) be row \(i\) of \(W_2\), and define
\[
p_i=\Pr_h(w_i^\top h>0),\qquad q_i=p_i(1-p_i).
\]
Here there is an exact formula, without independent-gate assumptions:
\[
\overline J=\operatorname{diag}(p_i)W_2,
\qquad
R_{\rm nl}=W_2^\top\operatorname{diag}(q_i)W_2.
\tag{9}
\]
Consequently,
\[
\operatorname{tr}R_{\rm nl}
=\sum_i q_i\|w_i\|^2.
\tag{10}
\]

I claim that, for an independent Gaussian row \(w\),
\[
q(W_1):=\mathbb E_w[p(w)(1-p(w))]
\longrightarrow
q_*:=\frac{\arccos(1/\pi)}{2\pi}>0
\quad\text{in probability}.
\tag{11}
\]

For nonzero \(h,h'\), rotational symmetry gives
\[
\Pr_w(w^\top h>0,\ w^\top h'\le0)
=\frac{\angle(h,h')}{2\pi}.
\tag{12}
\]
Take independent \(x,x'\sim N(0,I_n)\). Their directional correlation tends to zero in probability. Conditional on \(x,x'\), the standardized row projections of \(W_1x,W_1x'\) are iid bivariate standard normals \((Z_i,Z_i')\) with this correlation. Uniform fourth-moment bounds and Chebyshev imply
\[
\frac1n\sum_i(Z_i)_+^2\to\frac12,
\qquad
\frac1n\sum_i(Z_i')_+^2\to\frac12,
\qquad
\frac1n\sum_i(Z_i)_+(Z_i')_+\to\frac1{2\pi}.
\]
For the last convergence, the expectation is continuous in the correlation and equals \(1/(2\pi)\) at zero. Hence
\[
\frac{h_1(x)^\top h_1(x')}
{\|h_1(x)\|\|h_1(x')\|}
\longrightarrow\frac1\pi.
\tag{13}
\]
The probability that either vector is zero is at most \(2^{1-n}\).

The bounded kernel on the left of (12), with its actual values when an argument is zero, therefore converges in \(L^1\) to \(q_*\). Its conditional expectation given \(W_1\) is exactly \(q(W_1)\). Conditional Jensen proves (11).

Conditional on \(W_1\), the \(q_i\) are iid in \([0,1/4]\). Thus (11) and Hoeffding give
\[
\sum_iq_i\ge \frac{q_*}{4}n
\tag{14}
\]
with probability tending to one. Also \(\min_i\|w_i\|^2\ge1\) with probability tending to one. Equation (10) proves
\[
\operatorname{tr}R_{{\rm nl},2}\ge d_2n,
\qquad d_2=q_*/4>0,
\tag{15}
\]
with probability tending to one.

**3. Each fixed additional layer preserves a positive fraction of that variance — PROVEN.**

Fix all weights through layer \(j-1\), where \(j\ge3\). Write
\[
z(h)=h_{j-1}(h),\qquad A(h)=J_{j-1}(h),
\]
and
\[
T=\mathbb E_h\|A-\mathbb E_hA\|_F^2
=\operatorname{tr}R_{{\rm nl},j-1},
\qquad
K=\sup_h\|A(h)\|_{\rm op}.
\]
Under (1), \(z(h)=0\) implies \(A(h)=0\).

A fresh row \(w^\top\) of \(W_j\) produces the Jacobian row
\[
f_w(h)=\mathbf1_{\{w^\top z(h)>0\}}\,w^\top A(h).
\]
For almost every \(w\), as an identity in \(L^2(h)\),
\[
f_w-f_{-w}=w^\top A.
\tag{16}
\]
Indeed, the two strict signs partition \(w^\top z\ne0\); the remaining set contributes zero by Fubini when \(z\ne0\), and by \(A=0\) when \(z=0\).

Let
\[
a(w)=\mathbb E_h\|f_w-\mathbb E_h f_w\|^2.
\]
Centering (16) and using \(\|u-v\|^2\le2\|u\|^2+2\|v\|^2\) yields
\[
a(w)+a(-w)
\ge
\frac12\mathbb E_h\|w^\top(A-\mathbb E_hA)\|^2.
\]
The Gaussian law is symmetric, and \(\mathbb E ww^\top=(2/n)I\). Therefore
\[
\mathbb E_w a(w)\ge\frac{T}{2n}.
\tag{17}
\]

Moreover,
\[
a(w)\le K^2\|w\|^2,
\qquad
\mathbb E_w a(w)^2
\le K^4\,\mathbb E\|w\|^4
\le12K^4.
\tag{18}
\]
The \(n\) new rows are conditionally independent, and their variances sum to the new \(T\). Equations (17)–(18) and Chebyshev imply
\[
\Pr\!\left(
\operatorname{tr}R_{{\rm nl},j}<T/4
\mid W_1,\ldots,W_{j-1}
\right)
\le \frac{192nK^4}{T^2}.
\tag{19}
\]

For fixed \(L\), all \(\|W_j\|_{\rm op}\le B\) with probability tending to one. On that event, \(K\le B^{j-2}\). Starting with (15), induction through the finitely many layers gives
\[
\operatorname{tr}R_{{\rm nl},L}
\ge d_2\,4^{-(L-2)}n
\tag{20}
\]
with probability tending to one: at each induction step, the right side of (19) is \(O_L(1/n)\).

Finally,
\[
0\preceq R_{\rm nl}\preceq R,
\qquad
\|R\|_{\rm op}
\le\sup_h\|J(h)\|_{\rm op}^2
\le B^{2(L-1)}.
\]
Together with (4) and (20),
\[
\operatorname{tr}M\ge c_Sd_2\,4^{-(L-2)}n,
\qquad
\|M\|_{\rm op}\le C_SB^{2(L-1)}
\tag{21}
\]
with probability tending to one. Since
\[
\operatorname{PR}(M)
\ge \frac{\operatorname{tr}M}{\|M\|_{\rm op}},
\qquad
\operatorname{PR}(M)\le n,
\]
this proves (3).

The constants in (19) and (21) explain the limitation: this argument gives no depth-independent \(c>0\) when \(L\) grows.

**What can be proved at depth \(\alpha n\) by direct annealed calculations — PROVEN.**

Let \(t=L-1\), and condition on \(W_1\). Then
\[
\mathbb E_{W_2,\ldots,W_L}R=(1-a(W_1))I.
\tag{22}
\]
For a fixed nonzero input and a current state \(z\ne0\),
\[
\mathbb E_w\!\left[
\mathbf1_{\{w^\top z>0\}}ww^\top
\right]=\frac1nI.
\tag{23}
\]
This follows because \(ww^\top\) is even under \(w\mapsto-w\). Summing the \(n\) independent rows preserves the conditional derivative Gram matrix in expectation. If the state dies, its derivative is zero, so the same induction remains valid. The zero input contributes zero, proving (22).

In particular,
\[
\mathbb E_{\rm future}\operatorname{tr}M
\le (1-a(W_1))\operatorname{tr}S,
\]
and hence
\[
\mathbb E_{\rm all\ weights}\operatorname{tr}M
\le n(1-1/\pi).
\tag{24}
\]
Here
\[
\operatorname{tr}S
=\frac{1-1/\pi}{2}\|W_1\|_F^2.
\]

There is also an explicit second-moment upper bound. Put
\[
U_0=(\operatorname{tr}S)^2,\qquad V_0=\operatorname{tr}(S^2),
\]
and define
\[
V_t=
\frac{U_0+2V_0}{3}\left(1+\frac5n\right)^t
+\frac{V_0-U_0}{3}\left(1-\frac1n\right)^t.
\tag{25}
\]
Then
\[
\mathbb E_{\rm future}\operatorname{tr}(M^2)
\le (1-a(W_1))V_t.
\tag{26}
\]

For completeness, start a fixed-input derivative calculation with \(A_0=S^{1/2}\), and let \(G=A^\top A\). A new row is \(d\,y\), where \(y=w^\top A\) and \(d=\mathbf1_{\{w^\top z>0\}}\). Sign symmetry and Gaussian fourth moments give
\[
\mathbb E[d\,y^\top y]=G/n,
\qquad
\mathbb E[d\,\|y\|^4]
=\frac2{n^2}\left[(\operatorname{tr}G)^2+2\operatorname{tr}(G^2)\right].
\]
Expanding the sums over equal and distinct rows gives the recurrences
\[
U_{r+1}=\left(1+\frac1n\right)U_r+\frac4nV_r,
\qquad
V_{r+1}=\frac2nU_r+\left(1+\frac3n\right)V_r.
\tag{27}
\]
The coefficient matrix has eigenvalues \(1+5/n\) and \(1-1/n\); solving gives (25).

Now set
\[
B_h=S^{1/2}J(h)^\top J(h)S^{1/2},
\qquad K=\mathbb E_hB_h.
\]
Since \(0\preceq M\preceq K\),
\[
\operatorname{tr}M^2
\le\operatorname{tr}K^2
\le\mathbb E_h\operatorname{tr}(B_h^2).
\]
The first inequality follows from
\(\operatorname{tr}(K^2-M^2)=\operatorname{tr}((K-M)(K+M))\ge0\); the second is Jensen in Frobenius norm. Applying (25) to each nonzero \(h\) proves (26).

On the event (4), \(U_0=\Theta(n^2)\) and \(V_0=\Theta(n)\). At \(t\sim\alpha n\), the right side of (25) is of order \(n^2\), rather than \(n\). Thus these exact annealed calculations do not provide the second-moment estimate needed for linear participation ratio. They leave the benefit of averaging over inputs unresolved.

**The earlier \(\Theta_{\mathbb P}(n)\) statement cannot be upgraded automatically — FALSE implication.**

Even
\[
\operatorname{tr}N_n=n,
\qquad
\mathbb E\operatorname{tr}(N_n^2)=O(n)
\]
does not imply a fixed \(c>0\) with
\(\Pr(\operatorname{PR}(N_n)\ge cn)\to1\).

Let \(K\) be an unbounded positive integer with \(\Pr(K=k)=2^{-k}\), put
\[
r_n=\max(1,\lfloor n/K\rfloor),
\]
and let \(N_n\) have \(r_n\) eigenvalues equal to \(n/r_n\), with the rest zero. Then
\[
\operatorname{tr}N_n=n,\qquad
\operatorname{tr}(N_n^2)=\frac{n^2}{r_n}\le2Kn,
\qquad
\operatorname{PR}(N_n)=r_n.
\]
Thus the expected second trace is at most \(4n\), while
\[
\frac{\operatorname{PR}(N_n)}n\longrightarrow\frac1K.
\]
For every fixed \(c>0\), an event of positive probability has \(1/K<c\). The desired fixed-\(c\), probability-tending-to-one conclusion fails.

This is precisely the distinction between the confidence-dependent constants in the earlier mean-field result and the stronger assertion requested here.

---

**Q2 — OPEN for the actual network at \(L/n\to\alpha\).**

Define, on \(\operatorname{tr}M>0\),
\[
Z_n=\frac{M}{\operatorname{tr}M/n},
\qquad
\nu_n=\frac1n\sum_{i=1}^n\delta_{\lambda_i(Z_n)}.
\tag{28}
\]
Thus \(\int x\,d\nu_n=1\).

Neither the fixed-depth proof nor the annealed bounds above establish a deterministic limiting law for \(\nu_n\) at proportional depth.

**A sufficient spectral theorem — PROVEN UNDER explicit moment hypotheses.**

Assume:

1. For every integer \(r\ge2\),
   \[
   m_{r,n}:=\frac1n\operatorname{tr}(Z_n^r)
   \xrightarrow{\mathbb P}m_r<\infty,
   \tag{29}
   \]
   where each \(m_r\) is deterministic.
2. With \(m_0=m_1=1\), these moments specify a unique probability measure \(\nu\) on \([0,\infty)\).

Then
\[
\nu_n\xrightarrow{\mathbb P}\nu
\quad\text{weakly},
\tag{30}
\]
\[
\frac{\operatorname{PR}(M)}n
\xrightarrow{\mathbb P}\frac1{m_2},
\tag{31}
\]
and, for every \(0<k<1\),
\[
s(\lfloor kn\rfloor)
\xrightarrow{\mathbb P}
\int_{1-k}^1Q_\nu(u)\,du,
\tag{32}
\]
where \(Q_\nu\) is the increasing quantile function.

**Proof.** From any subsequence, choose a further subsequence along which all the countably many convergences in (29) hold almost surely. For each such realization, the measures are tight because
\[
\nu_n([A,\infty))\le1/A.
\]
Every weak subsequential limit has all the prescribed moments: boundedness of \(m_{r+1,n}\) gives
\[
\int_{x>A}x^r\,d\nu_n(x)\le \frac{m_{r+1,n}}A,
\]
so truncation permits passage of the \(r\)-th moment through weak convergence. Uniqueness forces every weak subsequential limit to equal \(\nu\). The subsequence criterion proves convergence in probability.

Also,
\[
m_{2,n}
=\frac{n\,\operatorname{tr}(M^2)}{(\operatorname{tr}M)^2}
=\frac n{\operatorname{PR}(M)},
\]
proving (31). The same moment argument gives \(\int x\,d\nu=1\). The quantile argument below proves (32). \(\square\)

These hypotheses concern normalized, quenched trace statistics. They are not established by the independent-gate computation.

**What weak spectral convergence alone says about fractional shares — PROVEN.**

There is a useful subtlety: for fixed \(k>0\), deterministic weak convergence already gives a deterministic limit for \(s(\lfloor kn\rfloor)\), even if some normalized trace mass escapes to arbitrarily large eigenvalues.

Specifically, if \(\nu_n\to\nu\) weakly in probability, then
\[
s(\lfloor kn\rfloor)
\xrightarrow{\mathbb P}
1-\int_0^{1-k}Q_\nu(u)\,du.
\tag{33}
\]
Writing \(m=\int x\,d\nu\le1\), this equals
\[
1-m+\int_{1-k}^1Q_\nu(u)\,du.
\tag{34}
\]

**Proof.** First consider deterministic weak convergence. Quantile functions converge for almost every \(u\in(0,1)\). Since every \(\nu_n\) has mean one,
\[
Q_{\nu_n}(u)\le\frac1{1-u}.
\]
They are therefore uniformly bounded on any interval ending strictly below one. Dominated convergence gives convergence of the bottom \((1-k)\)-fraction integrals. Exactly,
\[
s(\lfloor kn\rfloor)
=
1-\int_0^{\,1-\lfloor kn\rfloor/n}Q_{\nu_n}(u)\,du.
\]
The floor changes this integral by \(O_k(1/n)\), proving (33). The random case follows by the subsequence criterion. Finally, \(\int_0^1Q_\nu=m\), proving (34). \(\square\)

Under a uniform-integrability condition, or the moment hypotheses above, \(m=1\), and (33) becomes the usual upper-quantile integral (32). Without it, the defect \(1-m\) must be retained. For example, \(Z_n=\operatorname{diag}(n,0,\ldots,0)\) has \(\nu_n\Rightarrow\delta_0\), but every fixed positive fractional share tends to one.

**Linear PR, even with a deterministic limiting PR fraction, does not imply a deterministic spectral limit — FALSE implication.**

For \(n\) divisible by \(12\), choose with equal probability between spectra having empirical measures
\[
\nu_A=\tfrac12\delta_0+\tfrac12\delta_2,
\qquad
\nu_B=\tfrac13\delta_0+\tfrac12\delta_1+\tfrac16\delta_3.
\]
Both have first moment one and second moment two. Hence both satisfy
\[
\operatorname{PR}/n=1/2,
\qquad
\|Z_n\|_{\rm op}\le3.
\]
Nevertheless, their empirical spectral measures remain randomly different. Their top-quarter shares are respectively
\[
\frac12,\qquad\frac7{12}.
\]
Thus even a deterministic PR limit and a uniform operator bound do not establish Q2.

---

**Q3 — The operator-norm route is valid; its proportional-depth hypothesis is OPEN.**

For every nonzero PSD matrix,
\[
\operatorname{tr}(M^2)\le\|M\|_{\rm op}\operatorname{tr}M.
\tag{35}
\]
Therefore
\[
\|M\|_{\rm op}\le C'\frac{\operatorname{tr}M}{n}
\quad\Longrightarrow\quad
\operatorname{PR}(M)\ge n/C'.
\tag{36}
\]
This is **PROVEN**, and (21) establishes its premise with a depth-dependent constant for every fixed \(L\).

At \(L=\alpha n\), the available product-of-weight-norms estimate grows exponentially. Its growth establishes only that this estimate is insufficient. I have not proved that the actual normalized operator norm diverges.

**The operator bound is strictly stronger than the PR conclusion — FALSE converse.**

Take
\[
M_n=\operatorname{diag}(\sqrt n,1,\ldots,1).
\]
Then
\[
\operatorname{PR}(M_n)
=\frac{(n-1+\sqrt n)^2}{2n-1}\sim n/2,
\]
but
\[
\frac{\|M_n\|_{\rm op}}{\operatorname{tr}M_n/n}\sim\sqrt n.
\]
Consequently, an actual-network failure of the proposed operator bound would not itself refute Q1.

**What demonstrably fails when transferring the independent-gate proof — PROVEN.**

The missing ingredient is a valid replacement for its independence-based recursion.

For fixed nonzero \(h,h'\), an actual Gaussian row satisfies
\[
\mathbb E_w[
\mathbf1_{\{w^\top h>0\}}
\mathbf1_{\{w^\top h'>0\}}
]
=
\frac12-\frac{\angle(h,h')}{2\pi}.
\tag{37}
\]
This depends on the input pair; it is generally not \(1/4\). Moreover, the gate is dependent on its own weight:
\[
\mathbb E_w[\mathbf1_{\{w^\top h>0\}}w]
=
\frac1{\sqrt{\pi n}}\frac h{\|h\|},
\tag{38}
\]
whereas replacing it by an independent Bernoulli gate would give zero. Equation (38) follows by decomposing \(w\) into its component along \(h\) and its independent orthogonal component.

At deeper layers, the backward matrix inside a gate sandwich also depends on the forward state. For example,
\[
R
=
W_2^\top
\mathbb E_h\!\left[
D_2(h)\,W_3^\top D_3(h)W_3\,D_2(h)
\right]W_2
\]
at \(L=3\). The middle matrix depends on the same input and on \(D_2(h)\). There is no justified independent-gate factorization.

Sign symmetry does preserve the single-input annealed even moments in (23)–(27). The difficult quantities involve shared weights evaluated at multiple inputs. For instance, writing \(C(h)=J(h)-\overline J\),
\[
\operatorname{tr}(M^2)
=
\mathbb E_{h,h'}
\operatorname{tr}\!\left[
S\,C(h)^\top C(h)\,
S\,C(h')^\top C(h')
\right].
\tag{39}
\]
Controlling these correlations at \(L=\alpha n\), relative to \((\operatorname{tr}M)^2\), is precisely the estimate still missing.

**The mean Jacobian is not generally rank one — FALSE claim.**

Already at \(L=2\), (9) gives
\[
\overline J=\operatorname{diag}(p_i)W_2.
\]
Because the law of \(h_1\) has positive density in the open positive orthant, \(p_i>0\) whenever row \(i\) of \(W_2\) has a positive entry. The probability that any row has no positive entry is at most \(n2^{-n}\). Since \(W_2\) is almost surely invertible,
\[
\Pr(\operatorname{rank}\overline J=n)\longrightarrow1.
\]
Thus \(\overline J^\top\overline J\) is not generally a rank-one term.

Centering gives \(0\preceq R_{\rm nl}\preceq R\), but this alone supplies no lower bound on its trace and no bound on its operator norm divided by its average eigenvalue.

**Positive homogeneity does not force a radial null direction — FALSE claim.**

Homogeneity gives
\[
J(th)=J(h),\qquad J(h)h=g(h)
\tag{40}
\]
where differentiable. It does not give \(J(h)h=0\), nor does it put a fixed vector such as \(\mathbb Eh_1\) in the kernel of \(R_{\rm nl}\).

An explicit architectural counterexample makes this clear. Take \(W_1=I\), so
\[
S=\left(\frac12-\frac1{2\pi}\right)I,
\qquad
\mu=\mathbb Eh_1=\frac1{\sqrt{2\pi}}\mathbf1,
\]
and take
\[
g(h)=e_1(w^\top h)_+,
\qquad
w=(n,-1,\ldots,-1),\quad n\ge2.
\]
This is realizable by a ReLU layer. With \(p=\Pr(w^\top h_1>0)\in(0,1)\),
\[
R_{\rm nl}=p(1-p)ww^\top,
\qquad
\operatorname{PR}(M)=1,
\]
and
\[
\mu^\top R_{\rm nl}\mu
=\frac{p(1-p)}{2\pi}>0.
\]
This refutes an architectural or homogeneity-only lower bound. These deterministic weights are not a counterexample to a high-probability theorem under iid Gaussian initialization.

The unresolved proportional-depth question is therefore specific: prove either the normalized operator bound in (36), or the weaker trace estimate
\[
\frac{n\,\operatorname{tr}(M^2)}{(\operatorname{tr}M)^2}\le C
\]
with probability tending to one, while retaining the actual shared-input gate dependence. None of the mean-Jacobian, radial, or independent-gate arguments supplied so far establishes that estimate.
