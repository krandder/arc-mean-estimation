codex
**NUMERICAL:** A forward-only predictor matches the implied fixed-net factor with **2.7% median error and 16.8% maximum error** across all 42 cells. **PROVEN:** the input-radius contribution has zero first chaos. **HEURISTIC:** correcting that bookkeeping gives input \(s_1\approx0.238\), explaining most—but not all—of the systematic overprediction.

1. **PROVEN: the exact fixed-net correction.**

Write
\[
q=\mathbb E|X|^2,\qquad q_a=\mathbb E|g(X)|^2,\qquad
b=\frac{V}{q_a},\qquad \alpha=\frac{\operatorname{tr}\Sigma}{q}.
\]
Define the **quenched tangent-to-forward gain ratio**
\[
\boxed{\Gamma=
\frac{J(1)/\operatorname{tr}\Sigma}{q_a/q}.}
\]
Then, exactly,
\[
\boxed{D=\Gamma\,\frac{\alpha}{b}},
\qquad
\boxed{\frac{D}{D_{\rm v2}}=\Gamma\,\frac{b_{\rm v2}}b}.
\]

**PROVEN:** annealed criticality establishes
\[
\mathbb E_W J(1)=\operatorname{tr}\Sigma,\qquad
\mathbb E_W q_a=q.
\]
It does not establish \(\Gamma=1\) for a fixed net, or \(\mathbb E_W\Gamma=1\).

**NUMERICAL convention:** the supplied table’s \(E|a|^2\) is under the true input law. I therefore compare against
\[
\Gamma_{\rm data}
=\frac{J1\,(\mathrm{trS}+\mathrm{m2})}{\mathrm{trS}\,\mathrm{Ea2}}.
\]
The same algebra remains exact with this reference normalization. In my fresh runs, Gaussianized and true output energies differed by at most about \(1.3\%\).

2. **PROVEN UNDER conditioning on one forward trajectory: a computable conditional predictor.**

For a future trajectory \(h_0=X,h_1,\ldots,h_t\), record only
\[
q_j=|h_j|^2,\quad
a_j=q_j/q_{j-1},\quad
k_j=\#\{(W_jh_{j-1})_i>0\}.
\]
Set
\[
u_j=\frac{2(k_j-1)}{na_j},\qquad
v_j=\frac{2}{na_j},\qquad
T_0=1,\quad T_j=\prod_{i=1}^j u_i,
\]
and
\[
H_t=T_t+\sum_{j=1}^t v_jT_{j-1}.
\]

To derive this, split a tangent’s energy into components parallel and perpendicular to the current state. Conditional on the forward preactivations, the remaining transverse weight components are independent Gaussians. If \(R_j,U_j\) denote their conditional expected energies, then
\[
R_j=a_jR_{j-1}+\frac2nU_{j-1},\qquad
U_j=\frac{2(k_j-1)}nU_{j-1}.
\]
The \(2/n\) term accounts for transverse energy entering the next radial direction.

For initial tangent covariance \(\Sigma\), put
\[
r(X)=\frac{X^\top\Sigma X}{|X|^2}.
\]
Consequently,
\[
\boxed{
\mathbb E_W\!\left[
\operatorname{tr}(J\Sigma J^\top)\mid X,\text{forward trajectory}
\right]
=
\frac{q_t}{q_0}
\left[r(X)+(\operatorname{tr}\Sigma-r(X))H_t\right].
}
\]

**HEURISTIC:** for a particular net, replace its Jacobian energy by the forward-cloud average of this conditional expression:
\[
\widehat J=
\mathbb E_X\!\left[
\frac{q_t}{q_0}
\{r(X)+(\operatorname{tr}\Sigma-r(X))H_t\}
\right],
\qquad
\boxed{\widehat\Gamma=\frac{q\,\widehat J}
{\operatorname{tr}\Sigma\,q_a}}.
\]
This averages over the unobserved transverse weights in the derivation. Their actual fixed-net realization remains a source of error; conditioning on one trajectory is weaker than conditioning on an entire cloud.

**NUMERICAL:** I used 16,384 forward pilot inputs to fit each later-layer Gaussian, then 4,096 Gaussian forward trajectories per cell; layer \(0\) used \(N(0,I)\). No Jacobians, tangent propagation, gradient samples, or measured \(D\) entered the predictor. Entries are **prediction / data-implied factor**.

| Net | \(l=0\) | 4 | 8 | 16 | 24 | 28 | 31 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 4000 | 1.081 / 1.080 | 1.047 / 1.020 | 1.126 / 1.131 | 1.323 / 1.376 | 1.152 / 1.124 | .982 / .980 | .952 / .924 |
| 4001 | 1.701 / 1.620 | 1.925 / 1.762 | 1.713 / 1.602 | 1.220 / 1.111 | 1.321 / 1.292 | 1.153 / 1.112 | .957 / .940 |
| 4002 | .861 / .850 | 1.074 / 1.049 | 1.011 / .987 | 1.322 / 1.366 | 1.164 / 1.210 | 1.126 / 1.180 | .945 / .967 |
| 4003 | 1.422 / 1.437 | 1.369 / 1.334 | 1.219 / 1.238 | .863 / .846 | .983 / .958 | 1.122 / 1.120 | 1.024 / 1.046 |
| 4004 | 1.936 / 2.132 | 2.109 / 2.375 | 1.772 / 1.932 | .961 / 1.065 | 1.102 / 1.155 | 1.059 / 1.066 | .995 / 1.016 |
| 4005 | 2.383 / 2.089 | 2.249 / 2.007 | 1.943 / 1.664 | 1.386 / 1.265 | 1.333 / 1.280 | 1.321 / 1.340 | .999 / 1.018 |

**HEURISTIC:** the simpler approximation is
\[
\widehat\Gamma_{\rm simple}
=\frac{q}{q_a}\prod_{j=1}^t\frac{2\mathbb E_Xk_j}{n}.
\]
It treats tangent energy as diffuse and neglects radial alignment and transfer.

**NUMERICAL:** its median/max errors were \(6.8\%/30.8\%\), versus \(2.7\%/16.8\%\) for the conditional predictor. The correction substantially accounts for the early discrepancies, while residual variance-budget error still affects \(\widehat D=\widehat\Gamma D_{\rm v2}\).

3. **PROVEN UNDER the single-ray proxy: its logarithmic law.**

Along one nonzero forward ray, independently across layers,
\[
K_j\sim\operatorname{Binomial}(n,\tfrac12),\qquad
S_j\mid K_j\sim\chi^2_{K_j},
\]
and the forward squared-norm gain is \(2S_j/n\). The gate-count gain is \(2K_j/n\). Thus the simplest ratio is
\[
G_t=\prod_{j=1}^t\frac{K_j}{S_j}.
\]
Condition on survival, \(K_j>0\). Define
\[
m(k)=\log k-\psi(k/2)-\log2.
\]
Its exact log moments are
\[
\boxed{\mathbb E\log G_t=t\,\mathbb E m(K)},
\]
\[
\boxed{\operatorname{Var}(\log G_t)
=t\left[\mathbb E\psi_1(K/2)+\operatorname{Var}m(K)\right]}.
\]

**PROVEN UNDER this proxy, as \(n\to\infty\):**
\[
\mathbb E\log G_t=\frac{2t}{n}+O(t/n^2),\qquad
\operatorname{Var}(\log G_t)=\frac{4t}{n}+O(t/n^2).
\]
The forward gain has leading log drift \(-5/(2n)\); the gate-count gain has drift \(-1/(2n)\). Their difference produces \(2/n\).

**NUMERICAL:** exact conditional-mixture log moments at width 256:

| Future depth \(t\) | \(\mathbb E\log G_t\) | \(\operatorname{Var}\log G_t\) |
|---:|---:|---:|
| 32 | .25165 | .50596 |
| 28 | .22019 | .44271 |
| 24 | .18874 | .37947 |
| 16 | .12582 | .25298 |
| 8 | .06291 | .12649 |
| 4 | .03146 | .06324 |
| 1 | .00786 | .01581 |

**PROVEN UNDER the conditional-ray model:** the refined quantity above has the distributional recursion
\[
H_0=1,\qquad
\boxed{H_{t+1}\overset d=
\frac{(K-1)H_t+1}{S}},
\]
with independent fresh \(K,S\). This specifies its law, including radial transfer.

**NUMERICAL:** 300,000 draws of this recursion at \(n=256,t=32\) gave
\[
\mathbb E\log H_{32}\approx .246,\qquad
\operatorname{Var}\log H_{32}\approx .406.
\]

**HEURISTIC:** a lognormal approximation describes the core multiplicative fluctuations, but the cloud-averaged \(\Gamma\) also includes radial weighting and correlations between trajectories. A leading thin-cloud calculation makes that distinction explicit. For pair cosine \(c\), \(\theta=\arccos c\), define
\[
A(c)=\frac2\pi\arcsin c,\qquad
M(c)=\frac2\pi(\pi-\theta+c\sin\theta)-1,
\]
with \(B(c)\) as in v2. For the simple cloud predictor,
\[
\mathbb E\log\widehat\Gamma_{\rm simple}
\approx\frac1{2n}\sum_j[B(c_j)-A(c_j)],
\]
\[
\operatorname{Var}\log\widehat\Gamma_{\rm simple}
\approx\frac1n\sum_j[A(c_j)+B(c_j)-2M(c_j)].
\]
This assumes thin radii and deterministic kernel cosines, omitting radial-transfer corrections.

**NUMERICAL:** using \(c_j=\kappa^{(j)}(0)\) over ARC’s 32 layers gives approximately **.203 and .353**. Thus the single-ray values are useful scales, not established log moments of the actual quenched factor.

4. **PROVEN: \(\Gamma\) alone does not determine \(s_1\).**

There is an additional Jacobian-coherence quantity:
\[
\mathcal C=
\frac{\|\mathbb E[J]\Sigma^{1/2}\|_F^2}
{\mathbb E\|J\Sigma^{1/2}\|_F^2},
\qquad
\boxed{s_1=\mathcal C D}.
\]
Predicting the denominator’s gain does not predict the squared mean Jacobian. There is consequently no justified rule \(s_1\mapsto s_1/\Gamma\), or a common multiplier for all three channels.

**PROVEN:** at the population input, \(X=RU\), with \(R=|X|\) independent of its direction \(U\). Positive homogeneity gives
\[
g(X)=R f(U).
\]
Its pure radius component is \(R\,\mathbb E_Uf(U)\). This is even in \(X\), so its first chaos is exactly zero. Its nonconstant chaos is even-degree; the radius is not exactly a quadratic polynomial.

**NUMERICAL:** at \(n=256\),
\[
\operatorname{Var}R=.4995108,\qquad
\frac{\operatorname{Var}R}{\mathbb ER^2}=.0019512.
\]
V2 instead uses approximately \(1/256=.0039063\), and assigns it entirely to degree one.

**HEURISTIC:** retaining v2’s direction and amplitude channels, a principled radial-only correction is
\[
b_{\rm corr}
=b_{\rm v2}-\frac{\mathrm{radvar}}q+\frac{\operatorname{Var}|X|}{q},
\]
\[
\boxed{
s_{1,\rm corr}=
\frac{
b_{\rm v2}(s_{1,\rm dir}+s_{1,\rm amp})
+\|\mathbb E[|X|Z]\|^2/q
}{b_{\rm corr}},
\quad X=m+\Sigma^{1/2}Z.
}
\]
Here
\[
\mathbb E[|X|Z]=\Sigma^{1/2}\mathbb E[X/|X|]
\]
is an exact Gaussian identity. Applying this norm channel to the network remains heuristic: its scale and cross terms with angular amplitude are approximated.

**NUMERICAL:** the resulting **radial-only correction / measured \(s_1\)** is:

| Net | \(l=0\) | 4 | 8 | 16 | 24 | 28 | 31 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 4000 | .237 / .294 | .469 / .588 | .629 / .718 | .816 / .787 | .938 / .921 | .954 / .921 | .993 / 1.002 |
| 4001 | .238 / .210 | .488 / .408 | .609 / .536 | .718 / .682 | .887 / .831 | .942 / .930 | .976 / .966 |
| 4002 | .237 / .234 | .485 / .528 | .602 / .635 | .811 / .805 | .918 / .924 | .957 / .962 | .984 / .960 |
| 4003 | .238 / .209 | .464 / .438 | .585 / .594 | .746 / .762 | .903 / .921 | .974 / .933 | .986 / .982 |
| 4004 | .238 / .235 | .495 / .468 | .620 / .506 | .717 / .753 | .897 / .898 | .957 / .986 | .989 / .983 |
| 4005 | .238 / .201 | .466 / .372 | .611 / .540 | .766 / .785 | .902 / .847 | .952 / .956 | .979 / .994 |

**NUMERICAL:** on nets 4001–4005, the mean input overprediction falls from approximately **.076 to .020**. Net 4000 is then underpredicted by .057. This correction therefore explains most of the common input bias, but does not complete the channel theory; early-layer errors remain as large as .12.

**NUMERICAL:** net 4002 is particularly informative: its input \(\Gamma_{\rm data}=.850\), yet it shares the input \(s_1\) overprediction. A large gain ratio cannot be the sole explanation.

5. **PROVEN: budget accuracy and degree accuracy test different features.**

For the centered Gaussian covariance kernel,
\[
K(\rho)=\sum_{d\ge1}\rho^dV_d,
\]
one has
\[
V=K(1)=\int_0^1K'(\rho)\,d\rho,\qquad
J(1)=K'(1),\qquad
V_1=K'(0).
\]
Thus the variance budget measures an integral, \(D\) measures its endpoint slope, and \(s_1\) measures its initial slope. Moving a small amount of variance to high degrees can substantially change \(D\) while preserving \(V\).

**HEURISTIC:** coherent forward amplitude fluctuations largely cancel in \(V/\mathbb E|a|^2\), while gate-controlled local sensitivity need not track that amplitude. This supports the observed budget robustness. There is no general invariance of the budget to \(\Gamma\); a common output rescaling actually cancels from both the budget and \(\Gamma\).

- **PROVEN:** the missing fixed-net quantity is the tangent-to-forward gain ratio; input radius has zero first chaos.
- **NUMERICAL:** the forward conditional predictor achieves 2.7% median and 16.8% maximum factor error.
- **HEURISTIC:** multiplicative gain laws explain the fluctuation scale; radial correction explains most input \(s_1\) bias, while a full fixed-net channel correction remains unresolved.
