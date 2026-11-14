codex
**PROVEN UNDER one local hypothesis \((H_R)\): the specified recursion satisfies the requested bound with \(a=1\).**  
**PROVEN:** its first Gaussianization creates a radius defect \(9/(16\sqrt n)+o(n^{-1/2})\), which survives an exact suffix of depth \(\alpha n\).  
**CONJECTURE:** the local hypothesis preventing cancellation remains unproved. Thus the full recursion’s lower bound is conditional.

**PROVEN — exact defect decomposition.** Write
\[
P_\ell^\star=T_\ell\#\nu_{\ell-1},\qquad
\nu_\ell=\mathcal G(P_\ell^\star),\qquad
\Delta_\ell=\nu_\ell-P_\ell^\star,
\]
where \(\mathcal G\) denotes Gaussian moment matching and \(\nu_0=N(0,I_n)\). Define
\[
d_\ell=\int g_\ell(h)\,\Delta_\ell(dh).
\]
Every \(\Delta_\ell\) annihilates polynomials of degree at most two. In particular, \(d_L=0\). The first step has exact mean and covariance, but \(\Delta_1\ne0\): its Gaussianization can affect later means.

FORMAL Thm. 4.2 gives
\[
m_L-\mu(W)=\sum_{\ell=1}^{L-1}d_\ell,
\]
and therefore
\[
\boxed{
R_{n,L}:=\mathbb E_W|m_L-\mu(W)|^2
=\sum_{\ell<L}D_\ell+2\sum_{\ell<k<L}C_{\ell k},
}
\tag{1}
\]
with
\[
D_\ell
=\mathbb E\iint K_{n,L-\ell}(h,h')\,
                 \Delta_\ell(dh)\Delta_\ell(dh').
\tag{2}
\]
For \(\ell<k\), push the earlier signed defect to layer \(k\):
\[
\Delta_{\ell\to k}
=(T_k\circ\cdots\circ T_{\ell+1})\#\Delta_\ell.
\]
Conditioning on the entire prefix through \(k\), Prop. 4.4 gives
\[
\boxed{
C_{\ell k}
=\mathbb E\iint K_{n,L-k}(h,h')\,
           \Delta_{\ell\to k}(dh)\Delta_k(dh').
}
\tag{3}
\]
These cross terms have no automatic sign or orthogonality. The Minkowski certificate supplies only
\[
\sqrt{R_{n,L}}\le\sum_{\ell<L}\sqrt{D_\ell}.
\]

**PROVEN — a radius component of the future kernel survives at depth proportional to width.** Define
\[
\mathcal R(P)=\int |h|\,P(dh),\qquad
\rho_\ell=\mathcal R(\nu_\ell)-\mathcal R(P_\ell^\star),
\qquad u=\frac{\mathbf1}{\sqrt n}.
\]
For a fresh He layer, put
\[
a_n=\mathbb E\sqrt{\frac2n\sum_{i=1}^n(Z_i)_+^2}
=1-\frac5{8n}+O(n^{-2}).
\tag{4}
\]
Rotational invariance and homogeneity give, exactly,
\[
\mathbb E_W|T_W(h)|=a_n|h|,
\qquad
\mathbb E_W T_W(h)=\frac{|h|}{\sqrt\pi}u.
\]
Consequently, for a suffix of \(t\ge1\) layers,
\[
\mathbb E g_t(h)=\frac{a_n^{t-1}}{\sqrt\pi}|h|u.
\tag{5}
\]
Thus the kernel has the decomposition
\[
K_{n,t}(h,h')
=\frac{a_n^{2(t-1)}}{\pi}|h||h'|+K_{n,t}^{\,c}(h,h'),
\tag{6}
\]
where \(K^c\) is a positive-semidefinite covariance kernel. In particular,
\[
\boxed{
D_\ell\ge
\frac{a_n^{2(L-\ell-1)}}{\pi}\,\mathbb E\rho_\ell^2.
}
\tag{7}
\]
At \(t=\alpha n+O(1)\), the coefficient tends to \(e^{-5\alpha/4}/\pi>0\).

**PROVEN — the first radius defect has the required scale.**
For the actual first random layer,
\[
\boxed{
\mathbb E\rho_1=\frac9{16\sqrt n}+o(n^{-1/2}),
\qquad
\mathbb E\rho_1^2=\Theta(n^{-1}).
}
\tag{8}
\]
This identifies a component of the first kernel-tested defect whose squared size is \(\Theta(n^{-1})\). It does not determine the entire \(D_1\), or the orders of \(D_\ell\) at \(\ell=\Theta(n)\).

Here is the calculation. Let
\[
H=\operatorname{ReLU}(WX),\qquad
G\mid W\sim\mathcal G(\operatorname{law}(H\mid W)).
\]
Both have annealed second moment \(n\). The true fourth radial moment is exactly
\[
\mathbb E|H|^4
=(n^2+2n)(1+5/n)
=n^2+7n+10.
\tag{9}
\]
For \(G\), write \(s_i=|W_{i,:}|\) and \(r_{ij}\) for the cosine between rows. Its conditional moments satisfy
\[
\mathbb E[G_i^4\mid W]
=s_i^4\left(\frac34-\frac1{2\pi^2}\right),
\]
and, for \(i\ne j\),
\[
\mathbb E[G_i^2G_j^2\mid W]
=s_i^2s_j^2
\left[\frac14+\frac12\kappa(r_{ij})^2-\frac1{2\pi^2}\right].
\]
Using
\[
\mathbb E r_{ij}^2=\frac1n,\qquad
\mathbb E\kappa(r_{ij})^2
=\frac1{\pi^2}
+\frac{1/4+1/\pi^2}{n}+O(n^{-2}),
\]
gives
\[
\mathbb E|G|^4=n^2+\frac52n+O(1).
\tag{10}
\]
Expansion of the square root around \(n\) now yields
\[
\mathbb E|H|
=\sqrt n-\frac7{8\sqrt n}+o(n^{-1/2}),
\qquad
\mathbb E|G|
=\sqrt n-\frac5{16\sqrt n}+o(n^{-1/2}),
\]
which proves the coefficient \(9/16\). The remainders follow from third absolute moments of the squared-radius fluctuations of order \(O(n^{3/2})\).

For the upper bound in \(\mathbb E\rho_1^2=\Theta(n^{-1})\), use the exact identity
\[
\sqrt q-\mathbb E R
=\frac{\mathbb E(R-\sqrt q)^2}{2\sqrt q},
\qquad q=\mathbb E R^2.
\tag{11}
\]
Conditional Gaussian Poincaré bounds give squared-radius variances at most \(4\|W\|_{\rm op}^2q\) for both laws. Standard Gaussian-matrix moments then give \(\mathbb E\rho_1^2=O(n^{-1})\); its mean supplies the matching lower bound.

**PROVEN — what non-Gaussianity produces this term.** For a law with mean \(m\), covariance \(S\), and centered cumulants \(\kappa^{(3)},\kappa^{(4)}\),
\[
\operatorname{Var}_P|H|^2-
\operatorname{Var}_{\mathcal G(P)}|H|^2
=
4\sum_{i,j}m_i\kappa^{(3)}_{ijj}
+\sum_{i,j}\kappa^{(4)}_{iijj}.
\tag{12}
\]
The corresponding leading radius defect is
\[
\mathcal R(\mathcal G(P))-\mathcal R(P)
\approx
\frac{
4\sum_{i,j}m_i\kappa^{(3)}_{ijj}
+\sum_{i,j}\kappa^{(4)}_{iijj}
}{8q^{3/2}}.
\tag{13}
\]
At the first layer, the numerator has annealed expectation
\[
\frac92n+O(1),
\]
while \(q\asymp n\). The discarded third and fourth cumulants therefore create a radius error of order \(n^{-1/2}\), despite exact matching of the first two moments.

**PROVEN — defects have a potentially coherent component.** Put \(b_\ell=\mathbb E\rho_\ell\). Equation (5) implies
\[
\mathbb E d_\ell
=\frac{a_n^{L-\ell-1}b_\ell}{\sqrt\pi}u.
\]
Hence
\[
C_{\ell k}
=
\frac{a_n^{2L-\ell-k-2}}{\pi}b_\ell b_k
+\mathbb E[(d_\ell-\mathbb Ed_\ell)\cdot(d_k-\mathbb Ed_k)].
\tag{14}
\]
All ensemble-mean components point along \(u\). When their scalar signs agree, they add coherently. The centered cross terms remain uncontrolled; neither independent weights nor moment matching makes the defects martingale differences.

**PROVEN — an unconditional one-defect toy on the actual ensemble.** Gaussianize after layer one and integrate the remaining suffix exactly:
\[
\widetilde\mu_L=\int g_1(h)\,\nu_1(dh).
\]
Then \(\widetilde\mu_L-\mu=d_1\), so at \(L=\lfloor\alpha n\rfloor\),
\[
\boxed{
\liminf_{n\to\infty}
n\,\mathbb E|\widetilde\mu_L-\mu|^2
\ge
\frac{81}{256\pi}e^{-5\alpha/4}.
}
\tag{15}
\]
This proves that an early Gaussianization defect survives a long genuine He suffix. Later Gaussianizations, and their possible cancellation, are the only additional issue for this argument.

**CONJECTURE — the single local hypothesis needed for the full recursion.**

\[
\boxed{
(H_R)\quad
\mathbb E_W\mathcal R\!\left(
\mathcal G(T_W\#N(m,S))
\right)
\ge
a_n\,\mathcal R(N(m,S))
\quad\text{for every }m,\ S\succeq0.
}
\tag{16}
\]

The right-hand side is exactly
\(\mathbb E_W\mathcal R(T_W\#N(m,S))\).
Thus \((H_R)\) says that **Gaussianization does not decrease radius on average over a fresh He layer**. It is a one-layer inequality, with no error exponent or long-depth conclusion assumed. Requiring it only for states encountered by this recursion would suffice.

I have not proved \((H_R)\).

**PROVEN UNDER \((H_R)\) — the requested full-recursion lower bound.** Let
\[
r_\ell=\mathbb E\mathcal R(\nu_\ell),\qquad
m_n=\mathbb E|X|.
\]
Fresh-layer averaging gives the exact scalar recursion
\[
r_\ell=a_nr_{\ell-1}+b_\ell,\qquad r_0=m_n.
\]
Also,
\[
\mathbb E(m_L-\mu)
=
\frac{u}{\sqrt\pi}
\sum_{\ell=1}^{L-1}a_n^{L-\ell-1}b_\ell.
\]
Consequently,
\[
\boxed{
R_{n,L}\ge
\frac1\pi
\left(
\sum_{\ell=1}^{L-1}a_n^{L-\ell-1}b_\ell
\right)^2.
}
\tag{17}
\]
Under \((H_R)\), every \(b_\ell\ge0\). Keeping the first term proves
\[
\boxed{
\liminf_{n\to\infty}nR_{n,\lfloor\alpha n\rfloor}
\ge\frac{81}{256\pi}e^{-5\alpha/4}.
}
\tag{18}
\]
This proof permits arbitrary centered correlations between defects.

**PROVEN — the normalization is bounded at \(L=\alpha n\).** With
\[
\overline V_{n,L}=\mathbb E_W V(W),
\]
one has
\[
\overline V_{n,\lfloor\alpha n\rfloor}=\Theta(1).
\tag{19}
\]
A sufficient explicit upper bound uses the deterministic sequence
\[
c_0=0,\qquad c_{j+1}=\kappa(c_j),\qquad
C_V=1+2\sum_{j=0}^\infty(1-c_j)<\infty.
\tag{20}
\]
For every fixed \(\alpha>0\), eventually \(\overline V_{n,\lfloor\alpha n\rfloor}\le C_V\).

For completeness, take independent uniform unit inputs \(U,U'\), and define
\[
A_j=\mathbb E|h_j(U)||h_j(U')|,\quad
C_j=\mathbb E[h_j(U)\cdot h_j(U')],\quad D_j=A_j-C_j.
\]
Gaussian interpolation for \(f(z)=\sqrt{2/n}\,|z_+|\), whose gradient norm is at most \(\sqrt{2/n}\), gives
\[
0\le A_j-A_{j+1}\le\frac2nD_j.
\]
Weighted Jensen applied to the convex function \(\kappa\) gives
\[
D_j\le1-c_j.
\]
Since \(1-c_j=O((j+1)^{-2})\),
\[
\overline V_{n,L}
=n-m_n^2C_L
\le
(n-m_n^2)+2\sum_{j<L}(1-c_j)+n(1-c_L).
\tag{21}
\]
The lower bound \(\overline V_{n,L}\ge n-m_n^2\to1/2\) follows from \(C_L\le1\).

**PROVEN UNDER \((H_R)\) — explicit answer to question (2).** Combining (18)–(21), for all sufficiently large \(n\),
\[
\boxed{
\mathbb E_W|m_L-\mu(W)|^2
\ge
c(\alpha)\,\mathbb E_WV(W)\,n^{-1},
\qquad
c(\alpha)=
\frac{81e^{-5\alpha/4}}{512\pi C_V}>0.
}
\tag{22}
\]
Thus \(a=1\). At its \(\Theta(n)\)-forward-pass cost, the specified recursion has at most a constant-factor advantage over plain Monte Carlo under this hypothesis.

**PROVEN — the stronger pointwise radius hypothesis is false.** It would be incorrect to replace \((H_R)\) by positivity for every realized Gaussian preactivation law. Let
\[
H_M=((M+Z)_+,\,(-Z)_+),\qquad Z\sim N(0,1),
\]
and let \(G_M\) be its moment-matched Gaussian. As \(M\to\infty\),
\[
\boxed{
\mathbb E|G_M|-\mathbb E|H_M|
=-\frac{1}{2\sqrt{2\pi}\,M^2}+O(M^{-3})<0.
}
\tag{23}
\]
To see the sign, put \(B=(-Z)_+\) and \(b=\mathbb EB=1/\sqrt{2\pi}\). Ignoring exponentially small clipping of \(M+Z\),
\[
\operatorname{Cov}(Z,B)=-\frac12,\qquad
\mathbb E[ZB^2]=-2b.
\]
For the matched Gaussian pair, the corresponding mixed moment is \(-b\). Expanding
\[
|(M+Z,B)|
=M+Z+\frac{B^2}{2M}-\frac{ZB^2}{2M^2}+O(M^{-3})
\]
proves (23). Fresh-weight averaging in \((H_R)\) is therefore substantive.

**PROVEN — cost accounting for question (3).** Under the stipulated dense cost \(n^{K+1}\) per layer, at \(L=\alpha n\):

| Quantity | Order |
|---|---:|
| Scalar operations | \(n^{K+2}\) |
| Total matrix-vector units | \(n^K\) |
| Equivalent full forward passes | \(n^{K-1}\) |
| Plain MC normalized MSE at that cost | \(n^{-(K-1)}\) |

Accordingly:

- \(a_K\le K-1\) suffices to prevent a polynomial advantage over **plain MC at the method’s own cost**.
- The weaker \(a_K\le K\) suffices for the round-2 target \(C_{\rm closure}\ge n^{\max(1,q)-o(1)}\), provided the bounds are uniform over the allowed methods and orders.

Indeed, a method reaching normalized error \(n^{-q}\) must have \(q\le a_K\), while its total cost exponent is \(K\).

**PROVEN — the radius projection extends to specified higher-order closures, but does not itself supply \(a_K\).** Equations (5), (17), and the signed radius recursion require only well-defined measure/functionals and preservation of the mean. Higher moment matching can eliminate the leading radius defect. A finite cumulant list alone does not specify how to evaluate radius or nonlinear push-forwards.

**PROVEN UNDER a product-law toy — a concrete higher-order exponent.** Let
\[
P_n=P^{\otimes n},\qquad Q_n=Q^{\otimes n},
\]
where the coordinate laws match moments through order \(K\ge2\), have positive second moment \(v\), and have sufficiently light tails. Put \(s=\lfloor K/2\rfloor\), and suppose
\[
\Delta=\mathbb E_Q X^{2s+2}-\mathbb E_P X^{2s+2}\ne0.
\]
Then
\[
\boxed{
\mathcal R(Q_n)-\mathcal R(P_n)
=
\binom{1/2}{s+1}v^{-s-1/2}\Delta\,
n^{1/2-s}
+o(n^{1/2-s}).
}
\tag{24}
\]
One proof expands the Laplace transforms in
\[
\mathbb E\sqrt Z
=\frac1{2\sqrt\pi}\int_0^\infty
(1-\mathbb Ee^{-tZ})t^{-3/2}\,dt.
\]
Matching the first \(s\) moments of \(X^2\) cancels the first \(s\) terms; the first discrepancy is additive over coordinates.

Testing this single defect against a suffix of depth \(\alpha n\) gives the radius-based squared-error exponent
\[
\boxed{
a_K^{\rm toy}=2\lfloor K/2\rfloor-1
=
\begin{cases}
K-1,&K\text{ even},\\
K-2,&K\text{ odd}.
\end{cases}
}
\tag{25}
\]
This meets the own-cost MC criterion. It transfers to an actual cumulant recursion only after controlling joint cumulants, establishing a nonzero coefficient, and preventing cancellation. No such transfer is proved here.

**PROVEN — what must happen if the requested \(1/n\) floor is false.** Define
\[
B_n=\sum_{\ell<L}a_n^{L-\ell-1}b_\ell.
\]
Since \(\overline V=\Theta(1)\), an error \(R_{n,L}=o(n^{-1})\) necessarily requires
\[
B_n=o(n^{-1/2}).
\]
Using the proved first-layer coefficient, this means
\[
\boxed{
\sum_{\ell=2}^{L-1}a_n^{L-\ell-1}b_\ell
=
-\frac9{16\sqrt n}a_n^{L-2}
+o(n^{-1/2}).
}
\tag{26}
\]
Later negative radius defects must cancel the initial positive one. Equation (23) shows that negative local defects are possible. Cancellation of this scalar component is necessary but insufficient; the centered error must also become \(o(n^{-1/2})\) in \(L^2\).

**HEURISTIC — a possible failure mechanism.** As the cloud concentrates near a positive ray, much of its higher-cumulant structure becomes irrelevant to homogeneous, nearly linear futures. Exact covariance propagation could then leave only a small radius correction. If successive Gaussianizations cancel that correction to leading order, the recursion could beat \(1/n\). The existing identities do not exclude this.

**PROVEN — the reported ARC slopes concern a different implementation.** The report uses ARC’s `K=2, kind='simple'`. Its nonlinear step truncates the off-diagonal covariance expansion; it does not compute the exact bivariate Gaussian ReLU covariance required here. For centered unit-variance preactivations with correlation \(1/2\),
\[
\operatorname{Cov}_{\rm exact}(Z_+,Z'_+)
=0.1453439474\ldots,
\qquad
\operatorname{Cov}_{K=2,\rm simple}=0.125.
\]
This follows from the diagram budget in [kprop_harmonic.py](/home/agent/workspaces/mats/work/arc-noisy/ext/mlp_cumulant_propagation/src/mlp_kprop/kprop_harmonic.py:52). The measured slopes are useful context, but they do not establish the scaling of the specified exact-moment recursion. Also, averages of per-net nMSE differ from the requested ratio \(\mathbb E[\text{error}^2]/\mathbb EV\).

**HEURISTIC — cheapest useful numerical tests.**

1. Test the remaining hypothesis locally. Along exact-Gaussian closure trajectories, estimate signed radius defects using
   \[
   \rho_\ell=
   \frac{
   \mathbb E_{P_\ell^\star}(|H|-\sqrt{q_\ell})^2
   -
   \mathbb E_{\nu_\ell}(|G|-\sqrt{q_\ell})^2
   }{2\sqrt{q_\ell}},
   \quad
   q_\ell=\mathbb E|H|^2=\mathbb E|G|^2.
   \tag{27}
   \]
   This avoids subtracting two radii of order \(\sqrt n\). Accumulate their signed, weighted ensemble means to estimate \(B_n\). No true suffix simulations are needed for this diagnostic.

2. At one fixed \(\alpha\), start with widths \(64,128,256\), using exact bivariate Gaussian moments. For each net, split reference samples into two independent estimates \(\widehat\mu_1,\widehat\mu_2\), and use
   \[
   U_W=(m_L-\widehat\mu_1)\cdot(m_L-\widehat\mu_2),
   \qquad
   \mathbb E[U_W\mid W]=|m_L-\mu(W)|^2.
   \tag{28}
   \]
   Plot \(n\,\overline U/\overline V\), alongside \(\sqrt n\,B_n\). A sustained decline of both would identify the cancellation mechanism to investigate; finite-width slopes alone would not disprove an asymptotic floor.

**PROVEN — scope of completion.** The unconditional result is the one-defect theorem (15); the full specified recursion has exponent \(a=1\) under the single fresh-layer inequality \((H_R)\). Broader C4, including corrected closures and mixtures, remains open. Read-only checks completed at 2026-11-01 22:29 UTC; no files were modified.
