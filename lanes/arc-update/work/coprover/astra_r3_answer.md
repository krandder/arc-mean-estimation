# gpt-6-astra round 3 answer (extracted from astra_r3.raw; model line gpt-6-astra; r3 exit 0 06:39:17Z)

**PROVEN:** Matching the true radius marginal eliminates \(M_0\), but leaves first-layer cubic angular defects.  
**PROVEN UNDER a transfer hypothesis:** Those defects give an \(n^{-2}\) error floor at depth \(\alpha n\), hence a ceiling \(p\le2\) at matrix cost. A full-recursion exponent remains unproved.  
**PROVEN:** Tightness of \(c_K\alpha^K\) implies declining fixed-order efficiency, but does **not** imply a positive floor over all orders.

I checked the requested files and the attribution/spectrum scripts, read-only, on 2026-11-02. Below, normalization is
\[
\mathcal R=\frac{\mathbb E_W\|\widehat\mu-\mu\|^2}{\mathbb E_W V(W)}.
\]
The previously established \(\mathbb E_WV(W)=\Theta_\alpha(1)\) at \(L=\alpha n\) lets us transfer absolute-error exponents to this normalization. This is different from averaging per-net nMSE.

**1. A concrete radial closure, its first-layer gain, and its ceiling**

Definitions: write \(h=Ru\), with \(R=\|h\|\) and \(u\in S^{n-1}\). Consider the reconstruction
\[
Q(m,C,\nu)=\mathcal L\!\left(R\,\frac G{\|G\|}\right),
\qquad G\sim N(m,C),\quad R\sim\nu,\quad R\perp G.
\tag{38}
\]
Thus the direction is projected Gaussian, while the radius has a separately represented law. Initialize with \(G\sim N(0,I)\) and \(R\sim\chi_n\), which reconstructs the input exactly.

Here is a minimal, explicit update. Under the current model, let
\[
Y=\operatorname{relu}(WH),\qquad
m'=\mathbb EY,\quad C'=\operatorname{Cov}Y,\quad
q=\mathbb E\|Y\|^2,\quad v=\operatorname{Var}(\|Y\|^2).
\]
Fit the new radius by
\[
R'^2=e^\xi,\qquad
\xi\sim N\!\left(\log q-\frac{\sigma^2}{2},\,\sigma^2\right),
\qquad
\sigma^2=\log(1+v/q^2),
\tag{39}
\]
and reconstruct \(Q'=Q(m',C',\mathcal L(R'))\). Handle \(q=0\) by the point mass at zero. At the final layer, return the deducted mean before projection.

**PROVEN:** This is a deduction-projection closure with a non-Gaussian amplitude law. Its projection generally changes the vector mean and covariance: fitting \(m',C'\) before radial normalization does not make it an order-2 moment-matching projection. That qualification matters.

**PROVEN UNDER a fixed quadrature budget:** Its update has matrix cost. For example,
\[
\begin{aligned}
\mathbb EY_i
 &=\mathbb ER\,
   \mathbb E_G\frac{(WG)_i^+}{\|G\|},\\
\mathbb EY_iY_j
 &=\mathbb ER^2\,
   \mathbb E_G\frac{(WG)_i^+(WG)_j^+}{\|G\|^2},\\
\mathbb E\|Y\|^4
 &=\mathbb ER^4\sum_{ij}
   \mathbb E_G\frac{((WG)_i^+)^2((WG)_j^+)^2}{\|G\|^4}.
\end{aligned}
\tag{40}
\]
Use
\[
\|G\|^{-p}
=\frac1{\Gamma(p/2)}
  \int_0^\infty s^{p/2-1}e^{-s\|G\|^2}\,ds.
\]
Exponential tilting leaves a Gaussian, with
\[
C_s=(I+2sC)^{-1}C,\qquad m_s=(I+2sC)^{-1}m.
\]
At each quadrature node, computing \(WC_sW^\top\) costs \(O(n^3)\); the remaining expectations are univariate or bivariate truncated-Gaussian moments. With \(J\) nodes, the update costs \(O(Jn^3)\), using \(O(n^2)\) storage. At the first layer, ordinary Gaussian/ReLU formulas directly supply the required moments.

Thus \(O(n^3)\) is a valid **fixed-accuracy arithmetic cost**. Uniform accuracy as \(n,L,\varepsilon^{-1}\) grow requires charging \(J\) and controlling its error. I have not proved that stronger claim.

A Gaussian-copula extension replaces independence in (38) by jointly Gaussian \((Z,G)\), with \(R=F_\nu^{-1}(\Phi(Z))\). This gives a precise richer model class. Cheap, accurate updates of its copula parameters remain an additional problem.

**PROVEN: the oracle radius correction kills \(M_0\) exactly.** If its radius marginal is the true one, then
\[
M_0(Q-P)=\mathbb E_QR-\mathbb E_PR=0.
\tag{41}
\]
This applies to both an independent-radius construction and the ideal monotone transport used in the experiment. Their radius-direction couplings differ.

For the implementable lognormal-radius projection, put \(S=\|Y\|^2\). Equation (39) gives
\[
\mathbb E R'
=\sqrt q\,(1+v/q^2)^{-1/8}.
\]

**PROVEN UNDER radial extensivity and Taylor-remainder control:** Suppose
\[
q\asymp n,\quad v=O(n),\quad
\kappa_3(S)=O(n),\quad \kappa_4(S)=O(n),
\]
with sufficiently controlled fifth absolute moments and annealed integrability. Then
\[
\boxed{
M_0(Q'-P_Y)
=
\frac{3v^2/q-\kappa_3(S)}{16q^{5/2}}
+o(n^{-3/2}).
}
\tag{42}
\]
Indeed,
\[
\mathbb E\sqrt S
=\sqrt q-\frac{v}{8q^{3/2}}
+\frac{\kappa_3(S)}{16q^{5/2}}
-\frac{15v^2}{128q^{7/2}}
+o(n^{-3/2}),
\]
whereas the fitted radius has \(9v^2/(128q^{7/2})\) as its corresponding fourth-order contribution.

Consequently, this projection cancels the \(n^{-1/2}\) radius defect and leaves \(O(n^{-3/2})\), with that order attained only if the displayed coefficient is nonzero. Concentration alone gives a weaker remainder; it does not establish this coefficient.

**PROVEN:** This explains the positive lead. Ordinary first-layer Gaussianization has the \(9/(16\sqrt n)\) mean-radius error from round 1. Matching the first two moments of squared radius cancels its leading source. Matching the entire radius marginal eliminates the feature altogether.

The angular features require separate treatment.

**PROVEN:** For the independent-radius reconstruction, finite Taylor expansions give
\[
\begin{aligned}
M_d(Q)
&=r\,q^{-d/2}
 \sum_{j=0}^{J}
 \binom{-d/2}{j}q^{-j}
 \mathbb E\!\left[G^{\otimes d}(\|G\|^2-q)^j\right]
 +\mathrm{Rem}_Q,\\
M_d(P)
&=q^{(1-d)/2}
 \sum_{j=0}^{J}
 \binom{(1-d)/2}{j}q^{-j}
 \mathbb E\!\left[Y^{\otimes d}(S-q)^j\right]
 +\mathrm{Rem}_P,
\end{aligned}
\tag{43}
\]
where \(r=\mathbb ER\). The remainders must be bounded absolutely.

For \(d=2\), matching the unnormalized second moment cancels the leading polynomial term, but the two radius-weighted correction terms differ. Matching radius does not generally cancel \(M_2\). The identity
\[
\operatorname{tr}M_2=M_0
\]
only cancels its trace.

For \(d\ge3\), a simpler obstruction survives even without evaluating those correction terms.

Let
\[
a=\frac1{\sqrt\pi},\qquad
\gamma_3=\kappa_3(\sqrt2\,Z_+)
=a+2a^3>0.
\tag{44}
\]
The first-layer true coordinates have this limiting third cumulant, while the moment-matched Gaussian coordinates have zero third cumulant.

For the following asymptotics, use the explicit hypothesis \(H_{\rm shell}\): the true radius, Gaussian radius, and replacement radius divided by \(\sqrt n\) converge to one; the normalized coordinate products are uniformly integrable; and fixed collections of distinct first-layer rows have their usual limiting independent-coordinate laws. This is a first-layer shell hypothesis, not a growing-depth Gaussian approximation.

**PROVEN UNDER \(H_{\rm shell}\):**
\[
n\,\mathbb E_{W_1}
  [M_3(Q-P)]_{iii}\longrightarrow-\gamma_3.
\]
Jensen therefore gives
\[
\boxed{
\liminf_{n\to\infty}
 n\,\mathbb E_{W_1}\|M_3(Q-P)\|_F^2
 \ge\gamma_3^2.
}
\tag{45}
\]
The argument applies to the independent-radius model, its lognormal version, and the oracle monotone transport: multiplying a coordinate by a factor tending to one cannot remove its order-one marginal skewness.

More generally, consider tensor entries with one index occurring three times and the remaining \(d-3\) indices distinct. Their limiting raw-moment discrepancy is \(-\gamma_3a^{d-3}\). Counting those entries gives, for each fixed \(d\ge3\),
\[
\boxed{
\liminf_n n\,\mathbb E\|M_d(Q-P)\|_F^2
\ge
\binom d3\gamma_3^2a^{2d-6}.
}
\tag{46}
\]

**HEURISTIC:** Standard fixed-degree contraction counting suggests angular feature norms of order \(n^{-1/2}\), including generically \(M_2\). Equations (45)–(46) prove the needed lower order under the stated hypotheses; I am not claiming a complete matching upper bound for every feature.

There is a useful finite-width pricing lemma that makes this obstruction consequential.

Define
\[
\rho_n(Z)=\left(\frac2n\sum_i(Z_i^+)^2\right)^{1/2},
\qquad a_n=\mathbb E\rho_n.
\]

**PROVEN:** For \(t\ge2\),
\[
b_d^{(n,t)}
\ge
\frac{a_n^{2(t-2)}}{\pi}
\|\operatorname{Proj}_d\rho_n\|_{L^2(\gamma_n)}^2.
\tag{47}
\]
To prove it, average A2’s \(G(Z)\) over the remaining \(t-1\) layers:
\[
\mathbb E_{F'}G(Z)
=\frac{a_n^{t-2}}{\sqrt{\pi n}}\,
  \rho_n(Z)\mathbf1.
\]
Jensen applied separately to its Hermite coefficients gives (47).

**PROVEN:** The cubic energy is
\[
\|\operatorname{Proj}_3\rho_n\|_2^2
=\frac1{3\pi n}+o(n^{-1}).
\tag{48}
\]
Indeed,
\[
\rho_n
=1+\frac1n\sum_i\bigl((Z_i^+)^2-\tfrac12\bigr)
  +O_{L^2}(n^{-1}),
\]
and, for the normalized cubic Hermite,
\[
\mathbb E\!\left[
 Z_+^2\frac{Z^3-3Z}{\sqrt6}
\right]=\frac1{\sqrt{3\pi}}.
\]
Also, homogeneity and permutation symmetry give the exact bound
\[
b_2^{(n,t)}
\ge\frac{a_n^{2t-2}}{2\pi n}.
\tag{49}
\]

Since \(a_n=1-5/(8n)+o(n^{-1})\), at \(t/n\to\beta>0\),
\[
\boxed{
b_3^{(n,t)}
\ge
\frac{e^{-5\beta/4}+o(1)}{3\pi^2n}.
}
\tag{50}
\]

**PROVEN UNDER \(H_{\rm shell}\):** Combining (45), (50), and A2 gives the first-layer single-replacement bound
\[
\liminf_n n^2
 \mathbb E\left\|\int g\,d(Q_1-P_1)\right\|^2
\ge
\frac{e^{-5\beta/4}\gamma_3^2}{3\pi^2}>0.
\tag{51}
\]
Thus the remaining angular obstruction gives **\(p\le2\)** for this single-cut error. The radial calculation alone would misleadingly suggest \(p=3\), or no radial obstruction at all for the oracle.

**PROVEN UNDER a full-recursion transfer hypothesis:** If this \(n^{-2}\) floor transfers to a matrix-cost repeated closure, round-2 equation (34), with cost exponent \(K=2\), gives
\[
G_{\rm multilevel}=O(\log^2n).
\]
It permits no polynomial advantage. A matching \(p=2\) upper bound has not been proved.

**PROVEN:** The transfer qualification cannot be omitted. A single-cut defect is not a lower bound on total error when the suffix approximation can cancel it. A5, a suitable noncancellation statement, or another full-recursion argument is still required.

The amplitude-propagation obstruction is exact and easy to state. Define
\[
A_W(u)=\|\operatorname{relu}(Wu)\|,
\qquad
T_W(u)=\frac{\operatorname{relu}(Wu)}{A_W(u)}.
\]
Then
\[
R'=R\,A_W(U),\qquad U'=T_W(U).
\tag{52}
\]

**PROVEN:** The next radius law depends on the joint law of \(R,U\), and on nonlinear gate-dependent functions of \(U\). A radius marginal and finitely many covariances do not generally determine it.

There is an even smaller exact object relevant to this problem:
\[
\nu_P(du)=\mathbb E[R\mid U=u]\,P_U(du).
\]
Every positively homogeneous query depends only on \(\nu_P\), and
\[
\nu_{P'}(B)
=\int A_W(u)\,
  \mathbf1_{\{T_W(u)\in B\}}\,
  \nu_P(du).
\tag{53}
\]
Thus full amplitude-law propagation is more information than the output mean requires, while its marginal alone is insufficient.

**PROVEN UNDER the same first-layer hypotheses:** Equations (45) and (48) also show how angular error regenerates radius error: the next mean-radius discrepancy has squared size at least order \(n^{-2}\) over a fresh layer. The Gaussian direction model misses the gate-dependent gain even after the current radius is corrected.

**2. Mid-layer angular error and fixed order**

**PROVEN:** A2 alone gives
\[
D_{\rm ang}
=\sum_{d\ge2}b_d^{(n,t)}
 \left\|
   \int u^{\otimes d}\,d(\nu_Q-\nu_P)
 \right\|_F^2.
\tag{54}
\]
Prices without the feature discrepancies do not determine an error exponent. Moreover, a radial transport can change \(M_1\), so its residual is not automatically the \(d\ge2\) sum.

**PROVEN:** E6’s infinite-width spectrum cannot be transferred uniformly to \(t=\beta n\). Its total nonconstant mass eventually behaves as \(O(t^{-2})=O(n^{-2})\), whereas (50) gives finite-width cubic mass \(\Omega(n^{-1})\). The two limits differ materially.

**HEURISTIC:** A natural dangerous mid-layer scale is nMSE \(n^{-1}\), if a non-Gaussian angular profile survives on the shrinking angular scale. Here is the precise conditional version.

Assume \(H_{\rm cap}\):

- Typical radii are order \(\sqrt n\), while directions occupy a cap of angular width \(1/n\).
- In tangent coordinates, the radius-weighted discrepancy divided by \(\sqrt n\) has a limiting signed profile \(\sigma\), with \(\int d\sigma=0\).
- At suffix depth \(\beta n\), the kernel on that cap satisfies
  \[
  \kappa_{n,\beta n}(u_n(z)\cdot u_n(z'))
  =1-\frac{\Psi_\beta(z,z')}{n^2}+o(n^{-2}),
  \]
  with convergence sufficient for the signed double integrals.
- Its limiting discrepancy
  \[
  B=-\iint\Psi_\beta(z,z')\,d\sigma(z)d\sigma(z')
  \]
  is positive.

**PROVEN UNDER \(H_{\rm cap}\):**
\[
D_{\rm ang}=\frac Bn+o(n^{-1}).
\tag{55}
\]
The constant kernel cancels because \(\sigma\) has zero mass; the radius weights contribute \(n\), and the nonconstant kernel contributes \(n^{-2}\).

This gives a plausible \(p=1\) mid-layer obstruction, potentially worse than the first-layer \(p=2\) obstruction after radial correction. **Neither the supplied measurements nor E6 proves \(H_{\rm cap}\), particularly \(B>0\).** A vanishing limiting discrepancy could yield faster decay.

**PROVEN:** No fixed finite collection of polynomial moments determines all the features in (54) for arbitrary clouds. Even on a common sphere, distinct measures can match every moment through degree \(K\) while differing in a positively priced higher feature.

**PROVEN UNDER a persistent limiting angular discrepancy:** A fixed-order moment closure leaves a nonzero coefficient in (55) unless its retained information happens to determine the relevant limiting profile.

**CONJECTURE:** The observed mid-layer radial-Gaussian residual reflects such a persistent profile. The current evidence does not prove that every fixed-order closure fails on these random networks. High-degree price mass alone is insufficient for that universal conclusion.

The discriminating measurement is width scaling of the radius-corrected single-cut defect at fixed \(\ell/n,t/n\), together with finite-width prices. The one-width residuals establish a promising diagnostic, not its exponent.

**3. What ARC’s own tight law actually implies**

Suppose, for each fixed order,
\[
e_K(n)\asymp c_K\alpha^K,
\qquad
C_K(n)\asymp d_K n^{K-1},
\qquad L=\alpha n,
\tag{56}
\]
with positive constants independent of \(n\).

**PROVEN UNDER (56):**
\[
\boxed{
G_{{\rm MC},K}(n)
=\frac1{C_K(n)e_K(n)}
\asymp
\frac{n^{-(K-1)}}{d_Kc_K\alpha^K}.
}
\tag{57}
\]
Every fixed \(K\ge2\) loses gain as width increases. Its error remains order one in \(n\), while its cost grows.

The proposed all-order precision floor needs correction.

**PROVEN:** For \(0<\alpha<1\), \(c_K\ge c_*>0\) does **not** imply
\[
\inf_K c_K\alpha^K>0.
\]
The counterexample \(c_K=1\) has infimum zero. There need not even be a minimizing finite order.

**PROVEN UNDER a uniform lower error law:** A positive floor follows if
\[
\delta_*=\inf_{K\ge2}c_K\alpha^K>0.
\tag{58}
\]
This holds for a fixed finite order cap, or, for example, when the positive sequence \(c_K\) grows superexponentially. Mere boundedness below is insufficient. Fixed-\(K\) asymptotics alone also do not justify interchanging the width limit and an infimum over growing orders.

There is a stronger useful cost conclusion that does not require a positive floor. Assume uniformly over all orders being used that
\[
e_K(n)\ge a\,c_*\alpha^K,
\qquad
C_K(n)\ge d_*n^{K-1},
\tag{59}
\]
where \(a,c_*,d_*>0\) do not depend on \(K\).

**PROVEN UNDER (59):** At budget \(C\), any affordable order satisfies
\[
K\le1+\frac{\log(C/d_*)}{\log n}.
\]
Therefore the best affordable hierarchy error obeys
\[
\boxed{
e_{\rm best}(C)
\ge
a c_*\alpha\,(C/d_*)^{-\gamma_n},
\qquad
\gamma_n=\frac{\log(1/\alpha)}{\log n}.
}
\tag{60}
\]
For \(n>1/\alpha\), equivalently \(L>1\), \(\gamma_n<1\). Its ratio to MC’s \(C^{-1}\) error grows at least as \(C^{1-\gamma_n}\). Hence the hierarchy cannot match MC at all precisions under these uniform laws, **even when its all-order precision floor is zero**.

Along \(L=\alpha n\), \(\gamma_n\to0\). This is the cleanest conditional negative: increasingly expensive orders buy increasingly little precision. An upper bound \(e_K\le c_K\alpha^K\) alone cannot establish it; the assumed tightness or a lower bound is essential.

**HEURISTIC, interpreting the supplied measurements:** At \(\alpha=1/8\),
\[
\frac{c_3}{c_2}
\approx\frac{0.12\text{--}0.15}{1/8}
=0.96\text{--}1.20,
\]
and
\[
\frac{c_4}{c_3}
\approx\frac{0.25\text{--}0.55}{1/8}
=2.0\text{--}4.4.
\]
These are consistent with a tight \((L/n)^K\) ladder and increasing higher-order constants. They do not establish uniformity over arbitrarily large orders.

**PROVEN arithmetic:** Combining the supplied error ratios with a \(50\)–\(150\)-fold cost increase gives efficiency losses of approximately \(6\)–\(22.5\) for order \(2\to3\), and \(12.5\)–\(82.5\) for \(3\to4\).

**4. Brief audit of E1–E8**

- **E1 — HEURISTIC interpretation needs narrowing.** The measured decline of raw third-cumulant participation ratio contradicts the proposed growth picture on that net. It does not establish an asymptotic rank law. “The compression price is therefore large only in early layers” is too strong: participation ratio alone does not determine tensor magnitude, trace-sector price, approximation cost, or future relevance.

- **E2 — PROVEN.** The cancellation example and the two replacement arguments are valid. This remains essential for assessing the radial closure.

- **E3 — PROVEN logical correction; HEURISTIC empirical interpretation.** Preserve those numbers as a dev-net record. They do not override the new multi-net best-error ratios, and best-gain variants need not be best-error variants. The superasymptotic floor remains a separate conjecture; it does not follow from \(c_K\ge c_*>0\).

- **E4 — PROVEN under its budget model.** The budget-window arithmetic is sound, with strict versus non-strict endpoint conventions clarified. The family-level conclusion needs precision coverage and uniform order assumptions; fixed-order ratios alone do not supply them.

- **E5 — PROVEN UNDER the recorded hypotheses, with one wording caution.** A lower bound \(\liminf n^2\mathcal R>0\) rules out faster decay. Calling the scaling “tight” additionally requires a matching upper bound.

- **E6 — PROVEN corrections are needed.** For the infinite-width composition,
  \[
  \sum_d d\,b_d=\kappa_t'(1)=1,
  \qquad
  \mathbb E[d\mid d\ge2]
  =\frac{1-b_1}{1-b_0-b_1}.
  \tag{61}
  \]
  Thus the truncated FFT understates mean degree: the identity gives approximately \(17.24\) at \(t=16\) and \(42.27\) at \(t=31\), versus \(16.74\) and \(39.92\) in the file. Small missing mass can carry substantial first moment. Also, the infinite-width asymptotics are
  \[
  1-b_0\sim\frac{9\pi^2}{2t^2},\qquad b_1=\Theta(t^{-3}),
  \]
  so the conditional mean degree eventually grows as \(2t^2/(9\pi^2)\). The reported roughly linear finite-depth degree scales are not an asymptotic law or a hard degree cutoff. The finite-width exponential-decay sentence remains wrong and is withdrawn by E7.

- **E7 — PROVEN UNDER its explicitly retained hypotheses.** It accurately preserves the important round-2 qualifications. Its radial exponent table still cannot be inserted into the full-algorithm comparison without angular and propagation control. Equations (47)–(51) add a finite-width angular obstruction that the radial table does not capture.

- **E8 — HEURISTIC attribution is overstated.** Radial transport changes every \(M_d\), potentially including the mean. The before/after error difference is not an orthogonal “radial share,” especially for one fixed future. The exact-update sign test uses states reached by `simple`, so it does not cover every state reached by the exact Gaussian recursion. The later cuts also demonstrate the limitation: at \(\ell=31\), the supplied log has radial-Gaussian error \(1.89\times10^{-5}\), above the oracle Gaussian’s \(5.98\times10^{-6}\). Finally, E6’s infinite-width \(b_0\) at the early cuts’ long suffixes is around \(0.97\), not \(0.7\)–\(0.9\); the finite-width value was not measured there.
