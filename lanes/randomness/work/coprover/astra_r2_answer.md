codex
**PROVEN:** The positive-rule lower bound survives the audit. It does **not** imply exponent exactly \(1\) at fixed width. A stronger finite-width calculation does establish a different statement: along \(L=\alpha n\), the best positive, weight-independent rule has ensemble risk \(\Theta(N^{-1})\) for polynomial budgets \(N\le n^p\).

**PROVEN:** The same calculation identifies the missing finite-width mechanism: persistent differences in activation norms. It gives
\[
\lim_{\substack{n\to\infty\\L/\sqrt n\to\infty}}\mathbb E_W V(W)
=\frac12+S(0),
\]
where an explicit convergent series below gives \(S(0)\approx10.6505\). It also gives limiting low-degree shares and design gains close to the ladder.

I read the requested files and their measurement definitions; checks completed on 2026-11-02 at 14:23 UTC. No files were modified. Numerical measurements and extrapolations below are labelled **HEURISTIC**, separately from mathematical results.

**PROVEN / PROVEN UNDER the qualifications stated below: audit of T1–T11.**

| Item | Verdict |
|---|---|
| **T1** | **Correct identity.** For iid points, \(A_d=1/m\) holds **in expectation**, not for each realised set. Independent rotations give the stated \(1/R\) variance reduction. The measurement consequence needs correction: design variances are weighted spectral sums, not exactly the named partial sums. |
| **T2** | **Correct.** The design, including its randomisation, must be independent of \(W\). |
| **T3** | **Correct existential ensemble-risk statement.** It does not supply an efficient construction or short description. Weight-derived randomness requires the round-1 exact-transform hypotheses. A deterministic estimator is not conditionally unbiased given the complete \(W\), unless it is exact. |
| **T4** | **Correct per-degree inequality; needs qualifications for the tail formulation.** Sum over all degrees satisfying the minimum condition, or prove that every subsequent even degree satisfies it. The antipodal ceiling loses a factor of two at the stated threshold. Power coefficients and Gegenbauer coefficients cannot be interchanged. |
| **T5** | **Wrong as a fixed-\(n\), \(\epsilon\to0\) conclusion.** The tail in its lower bound depends on \(m\) and can vanish. The lower bound also requires positive weights. Moreover, \(\log_2m\) is support-index length, not runtime randomness. |
| **T6** | **Correct identity and algebraic inequalities.** “Pins the tail” overstates their strength: the lower bound can be zero or negative. Gaussian OU sensitivity and fixed-angle spherical sensitivity are different observables. |
| **T7** | **Correct first-layer result; wrong literal later zero-set formulation.** Later zero sets contain open dead regions. Gate perimeter has the round-1 exact formula. The small-noise asymptotic does not prove disagreement is near one once its first-order expression exceeds one. |
| **T8** | **Correct Hermite identity; wrong constants in the kink asymptotic and cumulative tail.** The corrected constants are \(J_{\rm kink}/\sqrt\pi\) and \(J_{\rm kink}/(3\pi)\), respectively. The proposed \(J_{\rm kink}\sim0.8nL\) and crossover scale remain heuristic. |
| **T9** | **Correct polar decomposition and asymptotic diagonal-energy calculation.** Full product-uniform point marginals restore unbiasedness; individual coordinate marginals alone do not. Signed permutations do not restore it. The “few hundred atypical points are harmless” sentence is unsupported. |
| **T10** | **Wrong if interpreted as exact redundancy with a 2-design.** \(|z_i|\), \(\operatorname{relu}(z_i)\), \(z_i|z_i|\), and \(\|h_1\|^2\) have higher harmonics. The measured approximate redundancy can stand as a heuristic. |
| **T11** | **Needs an explicit capacity hypothesis for the vanishing construction.** The exponential lower bound and threshold-circuit hardness transfer are not proved here. “Known PRGs cover depth-1 structure only” and “none bears on the average-case problem” are too strong. |

**PROVEN:** The spectral proxies in `scratch/ladder_table.py` have small systematic aliasing errors, in addition to replicate noise. Write \(e_d=E_d/\Lambda\). For ONB,
\[
nA_d=1+(n-1)P_d(0),
\]
so its reported degree-2 proxy is
\[
\widehat e_2^{\,\mathrm{population}}
=e_2-\sum_{\substack{d\ge4\\d\text{ even}}}(n-1)P_d(0)e_d.
\]
In particular,
\[
\left|\widehat e_2^{\,\mathrm{population}}-e_2\right|
\le \frac{3}{n+1}\sum_{\substack{d\ge4\\d\text{ even}}}e_d.
\]
For the simplex,
\[
(n+1)A_d=1+nP_d(-1/n),
\]
and its reported degree-\(\le2\) share is
\[
e_1+e_2-n\sum_{d>2}P_d(-1/n)e_d.
\]
The cross-polytope proxy is
\[
\widehat e_{\mathrm{even}\ge4}^{\,\mathrm{population}}
=\sum_{\substack{d\ge4\\d\text{ even}}}
[1+(n-1)P_d(0)]e_d.
\]
Thus T1 provides exact pricing, while the columns use approximations to that pricing.

**HEURISTIC:** These deterministic aliasing corrections are too small to explain the whole finite-width discrepancy with mean field. Replicate uncertainty matters more at \(n=256\): there are only three completed structure nets, and the negative reported degree-2 estimate is direct evidence of estimation noise.

---

**PROVEN: the requested positive-rule bound, with its precise scope.**

Let
\[
\mathcal R_N=\mathbb E_{W,S}\left\|\sum_{i=1}^Nw_iG_W(u_i)-\mu(W)\right\|^2,
\qquad w_i\ge0,\quad \sum_iw_i=1,
\]
where the complete spherical rule is independent of \(W\). Random weights and nodes are allowed.

The finite-width kernel has the expansion
\[
k_{n,L}(t)=\mathbb E_W\langle g_W(u),g_W(v)\rangle
=\sum_{r\ge0}b_rt^r,\qquad b_r\ge0,\qquad \sum_rb_r=1.
\]
Conditioning on all layers after the first proves this: the two first-layer Gaussian preactivation vectors have coordinatewise correlation \(t\), and their downstream map has a Gaussian Hermite expansion.

For
\[
\tau_{2s}=\mathbb E(U\cdot V)^{2s}
=\frac{(2s-1)!!}{n(n+2)\cdots(n+2s-2)},
\]
the even-degree moment defect is
\[
\left\|\sum_iw_i u_i^{\otimes 2s}
-\mathbb E U^{\otimes2s}\right\|_F^2
=\sum_{i,j}w_iw_j(u_i\cdot u_j)^{2s}-\tau_{2s}.
\]
Positivity gives
\[
\sum_{i,j}w_iw_j(u_i\cdot u_j)^{2s}
\ge\sum_iw_i^2\ge\frac1N.
\]
Consequently,
\[
\boxed{\displaystyle
\mathcal R_N\ge
\frac{m_n^2}{2N}
\sum_{\tau_{2s}\le1/(2N)}b_{2s}.}
\]
Conditioning on the rule’s random seed proves it equally for fixed designs, Haar-randomised designs, and independently randomised RQMC.

**PROVEN:** This displayed formula is for normalised spherical rules, including the radius-exact Sobol implementation here. Ordinary Gaussian cubature with varying radii has a different, radius-weighted moment defect; the formula should not be transferred unchanged.

**PROVEN:** The relationship to T4 is
\[
t^r=\sum_{\substack{d\le r\\d\equiv r\!\!\!\pmod2}}
c_{r,d}^{(n)}P_d^{(n)}(t),
\qquad c_{r,d}^{(n)}\ge0,
\]
and hence
\[
\lambda_d=m_n^2\sum_{r\ge d}b_r c_{r,d}^{(n)}.
\]
The power tail and harmonic tail are different at finite \(n\). The power proof avoids negative off-diagonal terms because \(t^{2s}\ge0\); a Gegenbauer polynomial does not have that property.

**PROVEN:** T4’s safe unconditional statement is
\[
\mathcal R_N\ge
\frac1{2N}
\sum_{\substack{d\ge2\ \mathrm{even}\\
-\min P_d\le1/(2N)}}\lambda_d.
\]
For \(N=2M\) antipodal points, compress to the \(M\) unoriented lines. At the threshold \(-\min P_d\le1/(2M)\), this gives
\[
\mathcal R_N\ge \frac1N\sum_{\text{qualifying }d}\lambda_d,
\]
so the gain ceiling is \(\bar\Lambda/\text{tail}\). The stronger ceiling
\(\bar\Lambda/(2\,\text{tail})\) requires \(M|\min P_d|=o(1)\).

**PROVEN:** At \(n=256\),
\[
\tau_2=\frac1{256},\qquad
\tau_4=\frac1{22016},\qquad
\tau_6=\frac1{1144832},
\]
and
\[
\tau_8\approx2.33375353\times10^{-8}.
\]
Thus:

| Budget | Power-tail cutoff in the displayed bound |
|---|---:|
| \(N=2^8,\ldots,2^{13}\) | even degrees \(\ge4\) |
| \(N=2^{14},\ldots,2^{18}\) | even degrees \(\ge6\) |

The transition budgets are \(11008\) and \(572416\). Also,
\[
m_{256}^2\approx255.500489,\qquad
\frac{m_{256}^2}{2N}\approx\frac{127.750245}{N}.
\]
For normalised ensemble risk, divide this prefactor by \(\bar V=\mathbb E V\), not by a per-net median.

**HEURISTIC, numerical verification:** Solving for the stationary points reproduces T4’s quoted Gegenbauer minima:
\[
|\min P_4|\approx9.04977\cdot10^{-5},\quad
|\min P_6|\approx5.80389\cdot10^{-6},\quad
|\min P_8|\approx6.15064\cdot10^{-7}.
\]
Their half-diagonal budget thresholds are approximately \(5525,\ 86149,\ 812924\). In particular, the later prose extending the **harmonic degree-6** threshold to \(5\times10^5\) does not follow from T4.

**PROVEN:** There are two different degree regimes.

For \(d=2s\ll n\),
\[
\log\tau_d
=-\frac d2\log\frac{en}{d}
+O\!\left(1+\frac{d^2}{n}\right).
\]
Therefore the cutoff approximately solves
\[
\frac{d_*}{2}\log\frac{en}{d_*}\simeq\log(2N).
\]
The simpler expression
\[
d_*\sim\frac{2\log N}{\log n}
\]
needs the additional condition \(\log d_*=o(\log n)\); \(d_*\ll n\) alone is insufficient.

At fixed \(n\), as \(d\to\infty\),
\[
\tau_d\sim C_n d^{-(n-1)/2},
\qquad
C_n=\frac{2^{(n-1)/2}\Gamma(n/2)}{\sqrt\pi},
\]
so
\[
d_*\sim(2C_nN)^{2/(n-1)}.
\]
At \(n=256\), the latter expression is approximately
\[
94.5771\,N^{2/255},
\]
but it is outside its useful asymptotic regime at the experimental budgets. Indeed,
\[
\tau_n=2^{1-n},
\]
so \(d_*=n\) corresponds to \(N=2^{n-2}=2^{254}\).

**PROVEN:** A \(1/N\) lower bound multiplied by a decreasing tail does not establish exponent exactly one.

For a fixed finite-width, finite-depth ReLU ensemble, the even power tail satisfies
\[
\sum_{\substack{r>D\\r\text{ even}}}b_r
\sim C_{n,L}D^{-3/2},
\qquad 0<C_{n,L}<\infty.
\]
One way to prove this is to apply the kink-tail result below to the **even part of the downstream function of first-layer Gaussian preactivations**. This is the function whose Hermite energies are \(b_r\). It is not the input-space Hermite spectrum \(H_k(W)\).

Combining this with the large-\(d\) formula for \(\tau_d\) gives
\[
\boxed{\mathcal R_N\ge c_{n,L}N^{-1-3/(n-1)}
\quad\text{for sufficiently large }N.}
\]
Thus a genuine fixed-width power exponent must satisfy
\[
p\le1+\frac3{n-1}.
\]
At \(n=256\), this is \(p\le1.0117647\).

**PROVEN:** Exponent exactly one is actually false as a universal fixed-width optimum. Partition the sphere into \(N\) equal-area cells of diameter \(O_n(N^{-1/(n-1)})\), and independently sample one point per cell. The network is Lipschitz and its squared Lipschitz constant has finite ensemble expectation. Stratification therefore gives
\[
\mathcal R_N=O_{n,L}\!\left(N^{-1-2/(n-1)}\right).
\]
At \(n=256\), this attainable exponent is \(1.0078431\). The construction is positive and independent of \(W\).

**PROVEN:** These asymptotic bounds do not constrain a fitted slope over \(2^8\)–\(2^{18}\) to lie below \(1.0118\). A finite-range slope can exceed the eventual exponent while the risk remains above its lower bound.

**PROVEN:** T1’s repeated-block corollary does give exponent exactly one. If a fixed \(M\)-point design has Haar-rotation risk \(v_D(W)>0\), then averaging \(R\) independent rotations gives
\[
\mathbb E\|\widehat\mu-\mu\|^2
=\frac{\mathbb E v_D(W)}R
=\frac{M\,\mathbb E v_D(W)}N,\qquad N=MR.
\]
The qualification is that the base design stays fixed. If its risk is zero, there is no nonzero \(N^{-1}\) law to fit.

---

**PROVEN: a finite-width norm-covariance calculation resolves tasks 3–4 at the ensemble level.**

For two fixed unit inputs with inner product \(t\), write
\[
r_j=\|h_j(u)\|,\quad r'_j=\|h_j(v)\|,\quad
c_j=\frac{\langle h_j(u),h_j(v)\rangle}{r_jr'_j},
\]
with products involving a dead state defined as zero. Set
\[
B_j(t)=\mathbb E[r_jr'_j],\qquad
k_j(t)=\mathbb E[r_jr'_jc_j],\qquad
T_j(t)=B_j(t)-k_j(t).
\]
There is an exact decomposition
\[
\boxed{1-k_j(t)=[1-B_j(t)]+T_j(t).}
\]
The first term is half the expected squared difference of activation norms. The second measures directional mismatch.

Let
\[
\kappa(c)=\frac{\sqrt{1-c^2}+(\pi-\arccos c)c}{\pi}
\]
and, for correlated standard Gaussian vectors \(Z,Z'\),
\[
a_n(c)=\mathbb E\!\left[
\sqrt{\frac2n\sum_i Z_{i,+}^2}\,
\sqrt{\frac2n\sum_i Z_{i,+}'^{\,2}}
\right].
\]
Conditioning on the prefix gives the exact recursions
\[
B_{j+1}=\mathbb E[r_jr'_j a_n(c_j)],
\qquad
k_{j+1}=\mathbb E[r_jr'_j\kappa(c_j)].
\]

**PROVEN:** Two bounds make this recursion uniform in depth.

First,
\[
0\le1-a_n(c)\le\frac2n(1-c).
\]
To see this, the function
\[
R(Z)=\sqrt{2/n}\,\|Z_+\|
\]
has \(\mathbb ER^2=1\) and
\[
\mathbb E\|\nabla R\|^2=\frac2n(1-2^{-n}).
\]
Its Hermite expansion and \(1-c^r\le r(1-c)\) give the inequality.

Second,
\[
\kappa(c)-c\ge a(1-c)^{3/2},
\qquad a=\frac{2\sqrt2}{3\pi}.
\]
Since \(B_j\le1\), weighted Jensen gives
\[
T_{j+1}\le T_j-aT_j^{3/2},
\]
and consequently
\[
\boxed{
T_j(t)\le
\left((1-t)^{-1/2}+\frac{\sqrt2}{3\pi}j\right)^{-2}
\le\frac{9\pi^2}{2j^2}.}
\]
Meanwhile,
\[
0\le B_j-B_{j+1}\le\frac2nT_j.
\]

**PROVEN:** These bounds already give the finite-width estimate
\[
\bar V_L
\le n-m_n^2+
\frac{m_n^2}{n}(2+3\sqrt2\,\pi)
+\frac{9\pi^2m_n^2}{2L^2}.
\]
Thus
\[
\bar V_L=O(1+n/L^2)
\]
uniformly in width and depth. No \(2n/(L+2)\) closure was used.

**PROVEN:** The limiting constant can also be identified.

Define
\[
M(c)=\mathbb E[Z_+^2Z_+'^{\,2}]
=\frac{(1+2c^2)(\pi-\arccos c)+3c\sqrt{1-c^2}}{2\pi},
\]
\[
\eta(c)=\frac32-M(c),
\qquad K_j=\kappa^{\circ j},\quad K_0(t)=t.
\]
A second-order expansion of the two empirical squared norms gives
\[
n[1-a_n(c)]\longrightarrow\eta(c).
\]
For each fixed number of layers, the usual finite-dimensional law of large numbers gives \(c_j\to K_j(t)\) and \(r_j,r'_j\to1\).

The previous uniform bounds allow the depth limit to follow:
\[
n(1-B_L(t))
\longrightarrow
S(t):=\sum_{j=0}^\infty\eta(K_j(t))
\]
whenever \(n\to\infty\) and \(L\to\infty\). The omitted tail is bounded uniformly by
\[
2\sum_{j\ge J}T_j=O(J^{-1}).
\]
If also \(L/\sqrt n\to\infty\), then \(nT_L\to0\). Therefore
\[
\boxed{
n[1-k_{n,L}(t)]\longrightarrow S(t).}
\]

**PROVEN:** This establishes
\[
\boxed{
\bar\Lambda_{n,L}\longrightarrow S(0),\qquad
\bar V_{n,L}\longrightarrow S(0)+\frac12
\quad (L/\sqrt n\to\infty).}
\]
The extra \(1/2\) is the limiting radial variance \(n-m_n^2\).

This mechanism is absent from the infinite-width recurrence. Taking width to infinity first sets \(a_n(c)=1\), removes every accumulated norm-loss term, and leaves only directional mismatch:
\[
1-K_L(t)\sim\frac{9\pi^2}{2L^2}.
\]
At finite width, each norm-loss term is \(O(1/n)\). Their sum leaves an \(O(1)\) output variance after multiplication by \(m_n^2\sim n\).

**PROVEN:** The calculation determines the fixed low degrees as well. Define
\[
A(t)=S(0)-S(t)
=\sum_{j=0}^\infty\left[M(K_j(t))-M(K_j(0))\right]
=\sum_{r\ge1}A_rt^r.
\]
All \(A_r\ge0\), and
\[
\sum_{r\ge1}A_r=S(0).
\]
Positivity of the finite-width power coefficients, convergence of their generating functions, and convergence of their total mass give
\[
nb_r^{(n,L)}\to A_r
\]
with convergence of the total positive-degree mass. For every fixed harmonic degree,
\[
\boxed{\lambda_d^{(n,L)}\to A_d.}
\]
Here the power-to-Gegenbauer conversion tends to the identity on each fixed finite degree as \(n\to\infty\).

**HEURISTIC, numerical evaluation of these proven series:**
\[
S(0)\approx10.6505,\quad
A_1\approx3.09504,\quad
A_2\approx2.21579,\quad
A_4\approx0.59011.
\]
The corresponding ensemble limits are:

| Quantity | Limiting value |
|---|---:|
| \(\bar V\) | \(11.1505\) |
| \(\bar\Lambda/\bar V\) | \(0.9552\) |
| Degree-1 angular share | \(0.2906\) |
| Degree-2 angular share | \(0.2080\) |
| Degree-\(\le2\) angular share | \(0.4986\) |
| Odd angular share | \(0.5704\) |
| Even angular share | \(0.4296\) |
| Even \(\ge4\) angular share | \(0.2215\) |
| Even \(\ge6\) angular share | \(0.1661\) |

**PROVEN:** The parity formula is particularly simple:
\[
S(-1)=S(0)+\frac32,
\]
because \(K_j(-1)=K_{j-1}(0)\) for \(j\ge1\). Hence
\[
\Lambda_{\rm odd}\to\frac{S(0)+3/2}{2},\qquad
\Lambda_{\rm even}\to\frac{S(0)-3/2}{2}.
\]

**HEURISTIC:** The agreement with the measured odd share, even \(\ge4\) share, radial gain and roughly one-half low-degree share is substantial evidence for this explanation. It does not convert medians of per-net ratios into ratios of ensemble expectations.

**PROVEN:** The proposed Jacobian observable is exactly the right degree-1 diagnostic. Gaussian integration by parts and homogeneity give
\[
B(W):=\mathbb E_XJ_f(X)=\mathbb E_X[f(X)X^\top],
\]
\[
\boxed{E_1(W)=\frac{m_n^2}{n}\|B(W)\|_F^2.}
\]
Thus the persistent degree-1 energy is precisely persistent energy in the per-net mean Jacobian. Fluctuations of the output’s input-independent mean are degree zero and cannot themselves contribute to \(E_1\) or \(E_2\).

**PROVEN:** Fixed-strength design gains therefore tend to constants. The residual aliasing factors for simplex, cross-polytope and maximal real-MUB Kerdock designs converge uniformly on their surviving degrees to \(1/N,\ 2/N,\ 2/N\), respectively. Consequently their gains over plain MC tend to
\[
\begin{aligned}
g_{\rm simplex}
&\to\frac{S(0)+1/2}{S(0)-A_1-A_2},\\
g_{\rm cross}
&\to\frac{S(0)+1/2}{S(0)-3/2-2A_2},\\
g_{\rm Kerdock}
&\to\frac{S(0)+1/2}{S(0)-3/2-2A_2-2A_4}.
\end{aligned}
\]
The Kerdock limit is along dimensions admitting the stated complete real MUB construction.

**HEURISTIC, numerical evaluation:** These gains are approximately
\[
\boxed{2.09,\qquad2.36,\qquad3.15}
\]
over plain MC, or \(1.99,\ 2.26,\ 3.01\) over RB-MC.

**PROVEN:** More generally, no positive oblivious rule can obtain a gain diverging with \(n\) at a fixed polynomial budget exponent. For \(N\le Cn^p\), choose an even \(d>2p\). Then \(N\tau_d\to0\), and
\[
\liminf_{n\to\infty}N\mathcal R_N
\ge\sum_{\substack{r\ge d\\r\text{ even}}}A_r>0.
\]
The existential MC comparison supplies the matching \(O(1/N)\) upper bound. This proves the opening \(\Theta(1/N)\) statement in the **joint wide/deep, polynomial-budget limit**.

**PROVEN:** The measured linear noise-slope law cannot hold uniformly along \(L=\alpha n\). The annealed slope is
\[
\operatorname{NS}_{\rm ann}'(0)=\frac n{\bar V},
\]
so the result above gives
\[
\frac n{\bar V}\sim\frac n{S(0)+1/2}.
\]
Along \(L=n/8\), its asymptotic slope per layer is therefore approximately \(0.7175L\), rather than \(0.5L\). Along \(L=n\), the proposed variance \(2n/(L+2)\to2\) conflicts directly with the proven limit \(S(0)+1/2\approx11.15\).

**PROVEN:** The per-net slope is
\[
\frac{D(W)}{V(W)},\qquad
D(W)=\mathbb E_X\|J_f(X)\|_F^2,
\]
and only \(\mathbb E_WD(W)=n\) is guaranteed. A median of \(D/V\), a median of \(n/V\), and \(n/\mathbb EV\) are different statistics. The supplied summary does not establish the asserted annealed law.

**CONJECTURE, falsifiable prediction for \(512\times64\):** With adequate replicate precision, the degree-\(\le2\) share remains around \(0.45\)–\(0.60\), the odd share around \(0.55\)–\(0.59\), simplex gain over MC around \(1.8\)–\(2.6\), and cross-polytope gain around \(2.0\)–\(2.8\). I expect an ensemble noise slope around \(35\)–\(45\), drifting toward the asymptotic \(512/11.1505\approx45.9\). These finite-\(512\) ranges are extrapolations; the theorem establishes the limits, not that this rung has reached them.

---

**PROVEN: the remaining noise and boundary corrections.**

T6’s spherical identity is exact:
\[
\operatorname{NS}_{\rm sph}(\rho)
=\sum_{d\ge1}e_d[1-P_d(\rho)].
\]
Its displayed upper and lower tail inequalities follow by bounding the multipliers separately below and above the cutoff. Clip the resulting bounds to \([0,1]\).

**PROVEN:** A two-sided constant-factor identification of a hard tail does not follow. For a pure degree-1 spherical harmonic,
\[
\operatorname{NS}_{\rm sph}(\rho)=1-\rho>0,
\]
while every tail above degree one is zero. The Gaussian OU version has multipliers \(1-\rho^k\), with Gaussian Hermite energies, rather than \(1-P_d(\rho)\).

**PROVEN:** For T7, retain the round-1 formulas. With
\[
c_0=(2\pi)^{-1/2},\quad
s_n=1-2^{-n},\quad
\beta_n=1-(n+1)2^{-n},
\]
\[
\mathbb E S^{\rm regular}_{\ell,i}
=c_0\beta_n^{\ell-1},\qquad
\mathbb E\operatorname{Per}_\gamma\{z_{\ell,i}>0\}
=c_0s_n^{\ell-1}.
\]
They distinguish fresh regular surfaces from inherited boundaries of dead regions.

The literal set \(\{z_{\ell,i}=0\}\), for \(\ell\ge2\), contains the open cone \(\{W_1x<0\}\). Its weighted \((n-1)\)-dimensional Hausdorff measure is therefore not the finite perimeter being estimated by gate flips.

**PROVEN:** For fixed finite architecture,
\[
\Pr(\text{gate history changes})
\sim
\frac{\sqrt2\,n}{\pi}
\left(\sum_{j=0}^{L-1}\beta_n^j\right)\sqrt\delta
\quad(\delta\downarrow0),
\]
and the corresponding crossing-count expression supplies an upper bound, capped at one. Neither statement supplies a near-one lower bound at \(\delta\gg(nL)^{-2}\).

**HEURISTIC:** The measured near-certain disagreement at \(256\times32\) is useful empirical evidence. It is stronger than the conclusion available from T7’s small-noise asymptotic alone.

**PROVEN:** For a fixed continuous piecewise-linear map, merge coincident facets and define
\[
J_{\rm kink}
=\sum_S\int_S\|[J_f]\|_F^2\,d\gamma_S.
\]
Then
\[
\frac12\mathbb E\|J_f(X)-J_f(Y)\|_F^2
=\sum_{k\ge1}k(1-\rho^{k-1})H_k
\sim\frac{J_{\rm kink}}{\sqrt\pi}\sqrt\delta.
\]
The factor \(1/2\) on the left is what removes the extra factor two in T8.

The nonnegative-coefficient Tauberian consequence is
\[
\boxed{\sum_{k>K}H_k
\sim\frac{J_{\rm kink}}{3\pi}K^{-3/2}.}
\]
Indeed, the weighted tail satisfies
\[
\sum_{k>K}kH_k\sim\frac{J_{\rm kink}}{\pi}K^{-1/2},
\]
and partial summation gives the factor \(1/3\). This is a cumulative-tail result; individual coefficients can vanish on an entire parity.

Equivalently, with \(D=\sum kH_k\),
\[
V\operatorname{NS}(\delta)
=D\delta-\frac{2J_{\rm kink}}{3\sqrt\pi}\delta^{3/2}
+o(\delta^{3/2}).
\]

**HEURISTIC:** Multiplying bare perimeter by an unconditional “typical jump squared” does not compute \(J_{\rm kink}\). The boundary conditioning changes the gradient distribution. The proposed \(0.8nL\), crossover \(K\asymp L^2\), and concentration of relevant energy in degrees \(3\)–\(50\) remain unsupported quantitative claims.

---

**PROVEN / HEURISTIC: white-box interpretation and exponent limits.**

**PROVEN:** Polar alignment has a persistent first-layer coordinate advantage:
\[
\frac{P_{ii}^2}{(P^2)_{ii}}
\longrightarrow
\left(\frac8{3\pi}\right)^2\approx0.7205.
\]
It preserves total harmonic energy but changes which coordinate subsets carry it.

**HEURISTIC:** The norm-covariance mechanism explains why this can remain useful at large width. Early-layer norm fluctuations have substantial low-degree energy, and polar alignment puts much of each first-layer gate into one coordinate. Sobol’s coordinate stratification can then reduce integration variance by a constant. This is consistent with the reported \(1.15\)–\(1.2\times\) improvement.

**PROVEN:** An SVD frame does not make individual gates coordinatewise:
\[
W_1V=U\Sigma.
\]
Also, the Gaussian square-matrix singular spectrum does not concentrate a constant fraction of its energy into \(O(1)\) singular directions: the top \(k\) directions carry only \(O(k/n)\) for \(k\ll n\).

**HEURISTIC:** Sorting singular directions can help Sobol at \(n=32\), where the effective number of important coordinates is still modest. It supplies no dimension-independent reduction to a few coordinates, which is consistent with the disappearing SVD gain at \(n\ge128\).

**PROVEN:** Signed permutations of Kerdock points preserve a finite collection of coordinate-magnitude patterns. They do not produce spherical-uniform point marginals, so conditional bias can remain.

A concrete warning is \(f(x)=\operatorname{relu}(x)\). Take a complete real MUB set containing the coordinate basis. Every other basis is flat, with coordinate magnitudes \(1/\sqrt n\). For its antipodal rule, the estimated mean of each output tends to
\[
\frac12,
\]
whereas the Gaussian mean is
\[
\frac1{\sqrt{2\pi}}\approx0.3989.
\]
Thus a spherical 5-design can retain substantial bias in an aligned frame. The overwhelming flat portion of the design already causes the problem; a small fraction of coordinate-axis points is not a sufficient explanation.

**HEURISTIC:** The reported \(19\)–\(400\) values of \(m\,\mathrm{nMSE}\) are consistent with this orbit bias. Replicate variance under signed permutations does not measure the missing squared bias.

**PROVEN:** If an independent scramble or shift makes each transformed cube point jointly uniform, then after the Gaussian-to-sphere map,
\[
U_i=Q(W)\frac{Z_i}{\|Z_i\|}
\]
is uniform conditional on \(W\). This restores unbiasedness while retaining the chosen frame. Finite-bit software implements a finite-grid version; exact continuous unbiasedness is an idealised statement.

**PROVEN:** The oblivious power-kernel lower bound does not apply to polar- or SVD-adapted points. Independence between the scramble seed and \(W\) does not make the final nodes independent of \(W\).

**PROVEN UNDER a scrambling scheme with uniformly bounded variance gains and eventual exactness on every fixed resolution:** For each fixed dimension and fixed net, the usual finite-resolution approximation argument gives
\[
\operatorname{Var}(\widehat\mu)=o(1/N).
\]
It applies equally after conditioning on a \(W\)-dependent frame. It does not guarantee a power \(N^{-1-\eta}\) for any fixed \(\eta>0\), and it supplies no dimension-uniform constant. I am not identifying the finite-bit LMS implementation with every hypothesis of that asymptotic theorem.

**PROVEN:** A fixed control variate followed by ordinary MC still has risk
\[
\frac{\operatorname{Var}(\text{residual})}{N}.
\]
It changes the constant unless the residual vanishes or the control construction itself improves with \(N\).

**CONJECTURE:** Polar or SVD alignment alone will not produce a substantial dimension-uniform exponent improvement at \(L=\alpha n\). They preserve a substantial residual containing many kink orientations. The present measurements do not prove this conjecture.

**PROVEN:** No universal white-box impossibility follows. Weight adaptation can radically improve special networks, and unrestricted adaptive positive rules have the Carathéodory exact-representation escape. Their construction cost is the unresolved issue.

**HEURISTIC:** The tail-check file rules out a useful common sampled tail gate mask on these nets. Gate-mask variation alone is not a general proof that every possible algebraic tail simplification is absent.

---

**PROVEN: statements I would sign after these corrections.**

- **FORMAL T1–T3:** exact spectral pricing, ensemble rotation invariance, and existential zero-runtime-randomness MC matching, with the qualifications above.
- **FORMAL T4 and round 1:** the qualifying-degree Gegenbauer bound and the positive power-tail bound. Neither establishes fixed-width exponent exactly one.
- **FORMAL T6 and round 1:** exact spherical and Gaussian noise identities, their valid tail inequalities, and the distinction between the two spectra.
- **Round 1:** the annealed Jacobian identities, exact regular-surface and gate-perimeter formulas, corrected kink-strength expansion, exact control means, and optimal multilevel allocation formula.
- **PROVEN UNDER their stated hypotheses:** weight-derived exact derandomisation and the round-1 multilevel gain theorem. Those hypotheses must remain visible.
- **This round:** the norm-covariance recursion; the uniform \(O(1+n/L^2)\) variance bound; the limiting series for \(L/\sqrt n\to\infty\); its fixed-degree spectrum; constant limits for simplex, cross-polytope and Kerdock gains; and \(\Theta(1/N)\) optimal positive oblivious risk at polynomial budgets in the joint wide/deep limit.

**CONJECTURE / OPEN:** The most important sampling question is whether an inexpensive weight-dependent construction can predict and integrate the persistent **scalar norm fluctuations** well enough that its residual angular variance tends to zero, with preprocessing and control costs included. Cancelling degrees one and two explains a constant gain; exploiting the full norm profile is the plausible route to escaping the proven oblivious ceiling.