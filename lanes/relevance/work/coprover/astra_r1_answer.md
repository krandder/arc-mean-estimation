**PROVEN:** the proposed “\(1/k\) forward variance × \(k\)-th backward amplification” is generally the wrong product.  
**NUMERICAL:** low-dimensional relevance does occur, especially late in the narrow network, but precision matters sharply in ARC.  
**Scope:** I did not read `work/relevance/`. Computations below were independent, single-threaded, and exploratory rather than certified numerical bounds.

**Q1. Decoupling**

**PROVEN.** Conditional on the past, the future weights are independent of \((\mu_l,m_l,\Sigma_l)\), and the future random function has input-rotation invariance:
\[
\{g(Rx):x\in\mathbb R^n\}\overset d=\{g(x):x\in\mathbb R^n\},
\qquad R\in O(n).
\]
Replace the first future weight matrix \(W_{l+1}\) by \(W_{l+1}R\). Its distribution is unchanged, including when future noise is averaged.

**PROVEN.** At a fixed nonzero \(m\), the Jacobian and the pulled-back gate normals along its trajectory are jointly invariant under rotations fixing \(m\). Write \(e=m/\|m\|\) and
\[
W_{l+1}=u e^\top+G(I-ee^\top).
\]
The trajectory starting at \(m\), including its future gates, depends on \(u\), subsequent weights and noises, but not on the transverse Gaussian matrix \(G(I-ee^\top)\). Every pulled-back normal has the form
\[
b_j=\alpha_j e+(I-ee^\top)G^\top v_j.
\]
Conditional on the trajectory information, their transverse coordinates are jointly Gaussian and rotationally invariant.

Thus their **joint orientation**, conditional on their internal geometry, is Haar on the appropriate orbit. They are not independent Haar normals. Singular-subspace statements require a spectral gap, or an equivariant convention for ties.

**PROVEN.** This argument does **not** give a Haar frame for
\[
B=\mathbb E_{\gamma_l}\nabla g(H).
\]
The averaging operation uses the cloud. Already for one future layer,
\[
B_{i,:}
=\Phi\!\left(\frac{w_i^\top m}{\sqrt{w_i^\top\Sigma w_i}}\right)w_i^\top.
\]
For \(m\parallel e_1\) and diagonal \(\Sigma\) with unequal transverse eigenvalues, this weighting distinguishes transverse axes. For example, if \(\Sigma_{22}>\Sigma_{33}\), pairing samples with \(w_2,w_3\) exchanged shows
\[
\mathbb E(B^\top B)_{22}<\mathbb E(B^\top B)_{33}.
\]
The squared gate-probability weight decreases when the denominator increases. This is a finite-\(n\) counterexample to transverse isotropy of the averaged Jacobian.

**PROVEN.** Even an unwhitened Haar frame becomes anisotropic after multiplication by \(\Sigma^{1/2}\). Consequently, neither independence of future weights nor pointwise frame invariance identifies the spectrum of
\[
C_1=\Sigma^{1/2}B^\top B\Sigma^{1/2}.
\]

**PROVEN.** At input layer \(l=0\), \(m=0\). A nonzero bias-free ReLU network is generally not differentiable there. “The Jacobian at the mean” is therefore not an available linearization at this cut; the Gaussian-averaged Jacobian remains well defined.

---

**Q2. The linear part**

**PROVEN.** Put \(F(Z)=g(m+\Sigma^{1/2}Z)\), with \(Z\) standard Gaussian on the covariance support. Its first chaos is
\[
F_1(Z)=AZ,\qquad A=B\Sigma^{1/2}.
\]
If \(\lambda_1\ge\lambda_2\ge\cdots\) are the eigenvalues of \(A^\top A\), then
\[
N_1(\varepsilon)
=\min\left\{k:\sum_{j>k}\lambda_j
\le\varepsilon\sum_j\lambda_j\right\}.
\]
For a scalar readout, \(A\) is one row: **\(N_1=1\)** whenever its linear variance is nonzero. This says nothing comparable about the full \(N\).

**PROVEN.** Multiplying ordered covariance eigenvalues by ordered Lyapunov amplifications requires simultaneous directions and appropriate orthogonality. Neither is supplied here. Covariant Lyapunov vectors are generally nonorthogonal and depend on the future; covariance principal axes are determined by the past.

For an independent Haar eigenframe \(U\), the appropriate matrix is
\[
\Sigma^{1/2}U\Lambda U^\top\Sigma^{1/2},
\]
not \(\operatorname{diag}(\lambda_k(\Sigma)\lambda_k(\Lambda))\). In particular,
\[
\mathbb E_U[\Sigma^{1/2}U\Lambda U^\top\Sigma^{1/2}]
=\frac{\operatorname{tr}\Lambda}{n}\Sigma.
\]
The backward amplification averaged along each fixed cloud axis is the same, rather than the \(k\)-th amplification.

**HEURISTIC.** In a genuinely coherent linearization, a random-matrix product, with the actual covariance inserted, is a reasonable surrogate. If its surviving subspace sees approximately isotropic compressed covariance, an exponentially spaced singular spectrum gives
\[
N_1(\varepsilon)\asymp
\min\left(n,\;1+\frac{n}{2ct}\log\frac1\varepsilon\right).
\]
The extra \(1/k\) factor is not justified. More importantly, this predicts a pointwise linear surrogate only when replacing \(B\) by that Jacobian is accurate.

**HEURISTIC.** The supplied coherence radius requires roughly
\[
t\,\theta_{\rm cloud}\ll1.
\]
This means \(t\ll n^{1/3}\) for the stationary cloud, and approximately \(t\ll l\), with a restrictive constant, in the deep input regime. Applying the pointwise Lyapunov spectrum throughout \(t=O(n)\) crosses this validity boundary.

**NUMERICAL.** For the ARC realization used below, the exact one-layer formulas at \(l=31\), evaluated on its fitted Gaussian cloud, give
\[
s_1=0.99042,\qquad
N_1(0.1,0.01,0.001)=(7,37,79).
\]
This is an explicit example of a nearly linear map whose vector-output linear relevance still needs many directions at high precision.

**PROVEN.** Useful bounds for the full problem are
\[
\sum_{j>k}\lambda_j(C_1)
\le \inf_{\dim P=k}\mathbb E\|F-\mathbb E[F\mid PZ]\|^2,
\]
and, by conditional Gaussian Poincaré,
\[
\mathbb E\|F-\mathbb E[F\mid PZ]\|^2
\le \operatorname{tr}((I-P)M),\qquad
M=\mathbb E[(\nabla F)^\top\nabla F].
\]
These give lower and upper dimension bounds from two different matrices. Confusing \(C_1\) with \(M\) loses the distinction between average response and sensitivity.

---

**Q3. Degree spectrum**

**PROVEN UNDER the fixed-depth concentrating-kernel limit.** Define
\[
\kappa(c)=\frac{\sqrt{1-c^2}+(\pi-\arccos c)c}{\pi},
\qquad f_t=\kappa^{\circ t},\qquad c_l=\kappa^{\circ l}(0).
\]
For the input regime’s Gaussian convention, the leading kernel prediction is
\[
C_l(\rho)
=n\left[f_t(c_l+(1-c_l)\rho)-f_t(c_l)\right].
\]
Consequently,
\[
s_d=
\frac{(1-c_l)^d f_t^{(d)}(c_l)}
{d!\,[1-c_L]},
\quad
s_1=\frac{(1-c_l)f_t'(c_l)}{1-c_L},
\quad
D=\frac{1-c_l}{1-c_L}.
\]

**NUMERICAL, evaluating this kernel model.**

| ARC layer \(l\) | \(t\) | \(s_1\) | \(s_2\) | \(D\) |
|---:|---:|---:|---:|---:|
| 0 | 32 | 0.110 | 0.096 | 39.56 |
| 8 | 24 | 0.363 | 0.184 | 6.55 |
| 16 | 16 | 0.582 | 0.190 | 2.79 |
| 24 | 8 | 0.792 | 0.127 | 1.56 |
| 31 | 1 | 0.974 | 0.019 | 1.05 |

**PROVEN UNDER the large-depth kernel asymptotics.** When both \(l,L\) are large,
\[
s_1\simeq \frac lL,\qquad
s_2\simeq \frac{3lt}{4L^2},\qquad
D\simeq\left(\frac Ll\right)^2.
\]
A substantial first-chaos share can therefore coexist with a large mean degree.

**NUMERICAL.** Finite-width corrections are already leading-order for ARC. An independent exact two-replica Gram-chain calculation at \(n=256,L=32,l=0\), using 16,384 chains, gave
\[
\mathbb E_W V\simeq13.21\quad(\mathrm{SE}\ 0.14),
\]
\[
\mathbb E_W V_1\simeq3.41\quad(\mathrm{SE}\ 0.09),
\qquad
\frac{\mathbb E_W V_1}{\mathbb E_W V}\simeq0.258.
\]
Here \(V_1\) used a coupled finite difference at \(\rho=\pm0.01\). The kernel alone predicts \(V=6.47\) and \(s_1=0.110\). The missing amplitude contribution materially changes the answer.

**PROVEN.** At the Gaussian input of a noiseless critical network,
\[
\mathbb E_W\mathbb E_X\|\nabla a(X)\|_F^2=n.
\]
Thus the **variance-weighted annealed mean degree**, not the mean quenched ratio, is \(n/\mathbb E_WV\). The calculation above gives about \(19.38\), rather than \(39.56\).

**PROVEN UNDER the concentrating-kernel approximation with independent future noises.** For the noisy value function, initialize
\[
q_0=\frac{\|m\|^2+\operatorname{tr}\Sigma}{n},
\qquad
z_0(\rho)=\frac{\|m\|^2+\rho\operatorname{tr}\Sigma}{n}.
\]
Propagate
\[
z_j(\rho)=q_{j-1}\kappa\!\left(\frac{z_{j-1}(\rho)}{q_{j-1}}\right),
\]
with \(q_j=q_{j-1}+1\) at hidden layers and no added variance at the output. There is **no \(+1\) in the cross-covariance recursion**. Then
\[
C(\rho)=n[z_t(\rho)-z_t(0)],\qquad
s_d=\frac{z_t^{(d)}(0)}{d![z_t(1)-z_t(0)]},
\qquad
D=\frac{z_t'(1)}{z_t(1)-z_t(0)}.
\]
Shared future noises would compute a different observable.

**HEURISTIC.** For a stationary angular-sector approximation, freeze \(Q\), put \(a=Q/(Q+1)\), and iterate \(c\mapsto a\kappa(c)\) around its fixed point \(c_*=1-\delta_*\). Its relaxation factor is
\[
\alpha=a\kappa'(c_*)
=1-\frac{\sqrt{2\delta_*}}{\pi}+o(Q^{-1/3}),
\]
giving a variance decay rate approximately
\[
0.672\,Q^{-1/3}\simeq0.808\,n^{-1/3}.
\]

**PROVEN UNDER this frozen-radius angular model and its large-\(Q\) continuum limit.** At long scaled times, its normalized degree spectrum does not become purely linear:
\[
s_1\longrightarrow
\frac{e^{\pi/(2\sqrt3)}}{2\sqrt3}=0.71494,\qquad
s_2\longrightarrow0.17874,\qquad
D\longrightarrow\frac32.
\]
To derive this, scale the correlation deficit by \(\delta_*\). Its dynamics becomes
\[
\dot y=1-y^{3/2}.
\]
The asymptotic amplitude of \(1-y\), started at \(y=0\), is
\(2\sqrt3e^{-\pi/(2\sqrt3)}\); differentiating this amplitude with respect to the initial condition gives the numbers above.

**HEURISTIC.** These are angular-sector predictions, not the full stationary answer. Radial fluctuations contribute at the same small-variance order being measured, and \(Q\) varies substantially across quenched environments. Simply substituting its median cannot recover that contribution.

**NUMERICAL.** The narrow network is far outside the useful fixed-depth kernel approximation. Among four surviving realizations, the input-layer scalar-amplitude mean degree ranged from approximately \(3.6\) to \(92.5\). At later cuts a one-dimensional Gaussian support could suffice even when its first-chaos share was small. Degree and projection dimension are genuinely different diagnostics.

---

**Q4. Gates and degree two**

**PROVEN.** For output coordinate \(a\), define
\[
H_a=\mathbb E[F_a(Z)(ZZ^\top-I)].
\]
Equivalently, \(H_a=\mathbb E\nabla^2F_a\), interpreting the Hessian distributionally. Then
\[
V_2=\frac12\sum_a\|H_a\|_F^2,\qquad
V_2(P)=\frac12\sum_a\|PH_aP\|_F^2.
\]

**PROVEN.** For fixed future noise, the distributional Hessian can be expanded over gate boundaries:
\[
\nabla_Z^2F_a
=\sum_{j=1}^{t}\sum_{i=1}^{n}
J_{j\to t,ai}\,
\delta(z_{ji})\,b_{ji}b_{ji}^{\top},
\qquad b_{ji}=\nabla_Zz_{ji}.
\]
The normals and downstream coefficients vary between facets. Taking expectations over \(Z\) and future noise gives \(H_a\).

Hence
\[
V_2=\frac12\sum_a
\left\|\sum_{j,i}H_{a,ji}\right\|_F^2.
\]
This includes cross terms between gates and layers. There is no general additive “variance per gate” accounting.

**PROVEN.** For one future layer, put \(a_i=\Sigma^{1/2}w_i\), \(s_i=\|a_i\|\), and \(\eta_i=w_i^\top m/s_i\). Then
\[
H_i=\frac{\phi(\eta_i)}{s_i}a_i a_i^\top,\qquad
V_2=\frac12\sum_i s_i^2\phi(\eta_i)^2.
\]
This is an exact gate sum because distinct gates are distinct output coordinates.

**PROVEN UNDER the kernel model.** The layer contributions to its second derivative are
\[
f_t''(q)=
\sum_{j=1}^{t}
\left[\prod_{b=j+1}^{t}\kappa'(c_{b-1})\right]
\kappa''(c_{j-1})
\left[\prod_{a=1}^{j-1}\kappa'(c_{a-1})\right]^2.
\]
All future layers contribute. In the deep input asymptotics their weights are approximately proportional to \((l+j)^{-2}\): early future layers dominate when \(t\gg l\), while contributions are more uniform when \(t\ll l\). In the stationary frozen-radius angular model, weights decrease approximately geometrically, so the first \(O(n^{1/3})\) future layers dominate.

**HEURISTIC.** A cloud of angular radius \(\theta\) encounters approximately \(O(n\theta)\) significant gate margins per layer. This gives \(O(n/l)\) in the deep input regime and \(O(n^{2/3})\) for the stationary cloud. The latter differs from the \(O(\sqrt n)\) flips caused by just the newest noise. There are \(nt\) neuron labels, potentially many more pulled-back facets, and their normals are correlated.

**PROVEN.** There is no universal captured fraction determined by \(k,n,V_2\):

- A rank-one quadratic tensor is captured completely in one dimension.
- For \(H\propto I_p\), the fraction captured is \(k/p\).
- For a rank-one tensor with a uniform normal, a fixed independent \(k\)-subspace captures, on average,
  \[
  \mathbb E\|Pu\|^4=\frac{k(k+2)}{p(p+2)}.
  \]

**HEURISTIC.** The often-suggested \((k/n)^2\) law needs sufficiently spread, incoherently combined normals and a projection that cannot exploit a few dominant tensors. Optimizing the projection using the future can violate it substantially.

---

**Q5. Predictions and numerical dimensions**

**PROVEN.** \(n,t,\varepsilon\) do not determine quenched \(N\). Gaussian weights have positive probability of neighborhoods giving nearly one-coordinate dependence, and neighborhoods giving broad coordinatewise dependence. A typical prediction additionally needs an ensemble statistic and assumptions about the cloud and nonlinear tensors.

**NUMERICAL.** I tested explicit projections using Gaussian conditional copies. If
\[
Z'=PZ+(I-P)\widetilde Z,
\]
then the residual is estimated directly from squared output differences. Candidate frames used gradients, with a mean-gradient direction included. These are estimated achievable dimensions, not optimized minima or confidence-certified upper bounds.

For one ARC net, weight seed 25600, Gaussian clouds fitted from 8,192 input trajectories, the results were:

| \(l\) | Vector: 90%, 99%, 99.9% | One independent isotropic scalar readout: 90%, 99%, 99.9% |
|---:|---:|---:|
| 0 | 189, 231, 246 | 189, 231, 246 |
| 8 | 39, 114, 163 | 35, 112, 162 |
| 16 | 13, 61, 115 | 10, 58, 114 |
| 24 | 8, 33, 74 | 2, 25, 68 |
| 31 | 8, 39, 83 | 1, 3, 20 |

The input Gaussian at \(l=0\) was exact. Evaluation used 2,048 conditional pairs for the vector and 4,096 for the scalar. The scalar readout used independent seed 25601; another readout can give different results.

**PROVEN UNDER the fitted Gaussian at ARC \(l=31\).** Exact first-chaos calculations give lower bounds
\[
N(0.1)\ge7,\qquad N(0.01)\ge37,\qquad N(0.001)\ge79.
\]
Capturing sufficient linear variance alone also proves \(N(0.1)\le8\). Thus the first entry is tightly located, and the numerical high-precision entries are close to their linear lower bounds.

**NUMERICAL.** For \(8\times256\), ten independently generated nets were screened with 8,192 inputs. Six had zero output on every screened input. This is sampled extinction, not a proof that their maps vanish everywhere. For the four survivors, achievable dimension ranges were:

| \(l\) | 90% | 99% | 99.9% |
|---:|---:|---:|---:|
| 0 | 3–6 | 7 | 7–8 |
| 8 | 1–2 | 2–4 | 3–6 |
| 32 | 1 | 1 | 1 |
| 128 | 1 | 1 | 1 |
| 255 | 1 | 1 | 1 |

These used weight seeds 8001, 8003, 8005 and 8007. From layer 32 onward, the fitted clouds were effectively rays. Generic scalar readouts inherit this compression.

**PROVEN.** If \(V=0\), the stated explained-share ratio is undefined. Calling \(N=0\) requires an explicit convention.

**NUMERICAL.** For one stationary-width-64 example, a 12\(n\)-layer burn-in and 4,096 paths produced a fitted cloud with \(Q=16.85\). A paired-start diagnostic had relative state RMS \(8.7\times10^{-5}\). Using independent future-noise groups:

| \(t\) | Estimated \(V_g\) | Candidate dimensions: 90%, 99%, 99.9% |
|---:|---:|---:|
| 1 | 313.6 | 19, 39, 51 |
| 8 | 80.2 | 14, 37, 50 |
| 32 | 3.32 | insufficient precision for reliable thresholds |
| 64 | 0.104, after additional averaging | one mean-gradient projection captured about 71% |
| 128 | unresolved | unresolved |

**CONJECTURE.** For stationary widths 32–256, near-output vector relevance will generally require many dimensions at 99–99.9% precision. At long horizons, output variation may become dominated by one response function, but that function can still depend nonlinearly on many input directions. I would not predict \(N=1\), or supply a numerical grid through \(2n\), from the stated constants alone.

**HEURISTIC.** The practical forecast supported here is: ARC has useful compression late at 90%, considerably less at 99.9%; the surviving narrow networks have strong late compression; stationary long-horizon compression remains an unresolved question about the slow response function.

---

**Q6. Stationary channels and decay**

**PROVEN.** Shared-noise contraction bounds the value-function variance:
\[
V_g
\le \frac12\mathbb E_{H,H',\xi}
\|a(H,\xi)-a(H',\xi)\|^2.
\]
Equality need not hold. Therefore the supplied tangent decay
\[
\exp[-2c(k+1/4)t/n]
\]
does not establish the decay rate of \(V_g\).

**HEURISTIC.** There are two candidate scales:

1. Angular correlation relaxation, with rate \(O(n^{-1/3})\), as derived in Q3.
2. A slower amplitude response, potentially with rate \(O(n^{-1})\).

A frozen-radius approximation illustrates why the amplitude rate can differ from the tangent rate. If \(R'\) follows one noisy radial step,
\[
\mathbb E_\xi R'
\approx \sqrt A\,R+\frac{n-1}{2\sqrt A\,R}.
\]
Differentiating gives an additional contraction of amplitude differences. The squared-response rate is approximately
\[
\frac{5}{2n}+\frac1Q.
\]
At \(Q=0.577n\), this is approximately \(4.23/n\). This is a model calculation, not a proved quenched exponent; the actual radius history matters.

**PROVEN UNDER a one-dominant-response-function hypothesis.** If
\[
g_t(h)-\mathbb Eg_t\approx v_t\,\psi(h),
\]
the output is approximately rank one, but
\[
N_g(\varepsilon)\approx N_\psi(\varepsilon).
\]
A scalar output direction does not imply a scalar linear input coordinate.

**NUMERICAL.** In the width-64 experiment at \(t=64\), using 64 future trajectories per input in each of two independent groups, a future-informed mean-gradient projection captured approximately 71% of \(V_g\). The linear projection along the cloud mean captured approximately 30%. Thus “the radius carries the surviving information” is too strong even in this modest test.

**CONJECTURE.** The correct slow coordinate is a future-dependent amplitude response \(\psi(h)\), rather than necessarily \(\|h\|\) or \(m^\top h\). Determining its residual after the best linear projection is the central missing stationary calculation. Neither its output rank nor the top Lyapunov exponent answers that question.

---

**Q7. Estimation**

**PROVEN.** Suppose \(q(PZ)\) approximates \(f(PZ)=\mathbb E[g(Z)\mid PZ]\), and its Gaussian integral \(I_q\) is available. Then
\[
\widehat I
=I_q+\frac1M\sum_{i=1}^M[g(Z_i)-q(PZ_i)]
\]
is unbiased, and its trace variance is
\[
\frac1M\left[
V(1-S(PZ))+\operatorname{tr}\operatorname{Cov}(f-q)
\right].
\]
With exact conditional integration and residual share \(\varepsilon\), the ideal gain is \(1/\varepsilon\), before setup and evaluation costs.

**HEURISTIC.** Where \(k\) is small, fit or quadrature-resolve the \(k\)-dimensional conditional mean, integrate it accurately, and sample the residual. This is plausible for the late narrow-network cuts and some scalar ARC cuts. The Gaussian fit, frame construction and conditional-mean fitting must all be charged.

**PROVEN.** If evaluations use noisy outputs \(a\), rather than exact \(g\), the residual also contains future-noise variance:
\[
\operatorname{tr}\operatorname{Var}(a-q)
=
\mathbb E\operatorname{tr}\operatorname{Var}(a\mid H)
+\operatorname{tr}\operatorname{Var}(g-q).
\]
A small \(N\) for a very small \(V_g\) can therefore provide little improvement for estimating the full output mean.

**HEURISTIC.** At equal compute:

- Plain MC is the baseline with no frame-learning cost.
- RQMC can improve the low-dimensional resolved part, but \(N\) alone does not establish its convergence rate.
- Multilevel shared-trajectory sampling should be compared using its level differences. With optimal allocation, its variance-cost factor is proportional to
  \[
  \left(\sum_j\sqrt{V_jC_j}\right)^2.
  \]
  Low relevance of a level difference can be more useful than low relevance of the whole output.

**PROVEN.** Large \(N\) does not rule out a sample-free estimator. Under the Gaussian convention with one layer remaining,
\[
\mathbb E[\operatorname{ReLU}(w_i^\top H)]
=s_i\phi(\eta_i)+(w_i^\top m)\Phi(\eta_i),
\]
exactly, however large the relevance dimension is.

**PROVEN.** Consequently, these diagnostics cannot prove that ARC lacks a sample-free estimator beating sampling at growing depth. Such a lower bound needs a computational or information-access model. Predicting a random output accurately and computing its expectation are different tasks.

---

**Q8. Red team and a better “bits” definition**

**PROVEN.** The framing has several consequential weaknesses.

1. **The denominator changes under Gaussianization.** \(V^\mu\) and \(V^\gamma\) must be distinguished. Hermite accounting sums to \(V^\gamma\); it cannot use the original \(V^\mu\) denominator.
2. **Gaussianization changes support and reachable branches.** A noiseless hidden state is nonnegative. Its Gaussian replacement need not be. For a cloud concentrated on a positive ray, Gaussianization can introduce a negative-ray branch with a different future gain.
3. **Degree does not determine dimension.** A high-degree function of one Gaussian coordinate has \(N=1\). Conversely, \(\sum_i(Z_i^2-1)\) has degree two and needs approximately \((1-\varepsilon)n\) linear coordinates.
4. **Output rank does not determine input relevance.** A rank-one output can encode a complicated scalar function of all coordinates.
5. **Means omit other predictive objectives.** \(g=\mathbb E[a\mid H]\) is appropriate for squared-error prediction of the output mean, but does not characterize conditional tails or the full output law.

**PROVEN.** The exact flip identity is algebraically valid with a consistent binary gate convention and the reference trajectory driven by the same future noise. Its interpretation needs care:

- Its frozen Jacobian is not generally \(B\).
- Flip terms are correlated and have nontrivial cross terms.
- Pulled-back flips are nonlinear functions of the initial state.
- The noisy reference trajectory is not the trajectory of conditional means.
- At the noiseless zero mean, the all-zero reference gates make the identity largely tautological.

Thus the identity organizes the difference, but does not itself provide an orthogonal variance decomposition.

**PROVEN.** Counting arbitrary real-valued statistics is also insufficient: without regularity or coding restrictions, a single real statistic can measurably encode an entire vector.

**PROVEN.** A literal bit-based alternative is predictive rate-distortion:
\[
R_l(\varepsilon)=
\inf_{p(T\mid H)}
I(H;T)
\quad\text{subject to}\quad
\mathbb E\|g(H)-\mathbb E[g(H)\mid T]\|^2
\le\varepsilon V.
\]
Use base-two information units. This counts information needed for the specified prediction task, rather than coordinates. Encoder computation must be recorded separately, since computing \(g\) and then quantizing it can be expensive.

**HEURISTIC.** A useful empirical counterpart is a cross-fitted curve of residual predictive variance against code length and encoder cost. Compare linear projections, radius/amplitude features and quantized nonlinear encoders. For Gaussian projections, the exact diagnostic is
\[
1-S(PZ)
=\frac{\mathbb E\|g(Z)-g(PZ+(I-P)\widetilde Z)\|^2}{2V}.
\]
When \(g\) is unavailable, use independent future-noise groups to estimate the product of conditional differences, with shared noise within each difference to reduce variance. This is the measurable quantity used in the stationary checks above.
109,548
**PROVEN:** the proposed “\(1/k\) forward variance × \(k\)-th backward amplification” is generally the wrong product.  
**NUMERICAL:** low-dimensional relevance does occur, especially late in the narrow network, but precision matters sharply in ARC.  
**Scope:** I did not read `work/relevance/`. Computations below were independent, single-threaded, and exploratory rather than certified numerical bounds.

**Q1. Decoupling**

**PROVEN.** Conditional on the past, the future weights are independent of \((\mu_l,m_l,\Sigma_l)\), and the future random function has input-rotation invariance:
\[
\{g(Rx):x\in\mathbb R^n\}\overset d=\{g(x):x\in\mathbb R^n\},
\qquad R\in O(n).
\]
Replace the first future weight matrix \(W_{l+1}\) by \(W_{l+1}R\). Its distribution is unchanged, including when future noise is averaged.

**PROVEN.** At a fixed nonzero \(m\), the Jacobian and the pulled-back gate normals along its trajectory are jointly invariant under rotations fixing \(m\). Write \(e=m/\|m\|\) and
\[
W_{l+1}=u e^\top+G(I-ee^\top).
\]
The trajectory starting at \(m\), including its future gates, depends on \(u\), subsequent weights and noises, but not on the transverse Gaussian matrix \(G(I-ee^\top)\). Every pulled-back normal has the form
\[
b_j=\alpha_j e+(I-ee^\top)G^\top v_j.
\]
Conditional on the trajectory information, their transverse coordinates are jointly Gaussian and rotationally invariant.

Thus their **joint orientation**, conditional on their internal geometry, is Haar on the appropriate orbit. They are not independent Haar normals. Singular-subspace statements require a spectral gap, or an equivariant convention for ties.

**PROVEN.** This argument does **not** give a Haar frame for
\[
B=\mathbb E_{\gamma_l}\nabla g(H).
\]
The averaging operation uses the cloud. Already for one future layer,
\[
B_{i,:}
=\Phi\!\left(\frac{w_i^\top m}{\sqrt{w_i^\top\Sigma w_i}}\right)w_i^\top.
\]
For \(m\parallel e_1\) and diagonal \(\Sigma\) with unequal transverse eigenvalues, this weighting distinguishes transverse axes. For example, if \(\Sigma_{22}>\Sigma_{33}\), pairing samples with \(w_2,w_3\) exchanged shows
\[
\mathbb E(B^\top B)_{22}<\mathbb E(B^\top B)_{33}.
\]
The squared gate-probability weight decreases when the denominator increases. This is a finite-\(n\) counterexample to transverse isotropy of the averaged Jacobian.

**PROVEN.** Even an unwhitened Haar frame becomes anisotropic after multiplication by \(\Sigma^{1/2}\). Consequently, neither independence of future weights nor pointwise frame invariance identifies the spectrum of
\[
C_1=\Sigma^{1/2}B^\top B\Sigma^{1/2}.
\]

**PROVEN.** At input layer \(l=0\), \(m=0\). A nonzero bias-free ReLU network is generally not differentiable there. “The Jacobian at the mean” is therefore not an available linearization at this cut; the Gaussian-averaged Jacobian remains well defined.

---

**Q2. The linear part**

**PROVEN.** Put \(F(Z)=g(m+\Sigma^{1/2}Z)\), with \(Z\) standard Gaussian on the covariance support. Its first chaos is
\[
F_1(Z)=AZ,\qquad A=B\Sigma^{1/2}.
\]
If \(\lambda_1\ge\lambda_2\ge\cdots\) are the eigenvalues of \(A^\top A\), then
\[
N_1(\varepsilon)
=\min\left\{k:\sum_{j>k}\lambda_j
\le\varepsilon\sum_j\lambda_j\right\}.
\]
For a scalar readout, \(A\) is one row: **\(N_1=1\)** whenever its linear variance is nonzero. This says nothing comparable about the full \(N\).

**PROVEN.** Multiplying ordered covariance eigenvalues by ordered Lyapunov amplifications requires simultaneous directions and appropriate orthogonality. Neither is supplied here. Covariant Lyapunov vectors are generally nonorthogonal and depend on the future; covariance principal axes are determined by the past.

For an independent Haar eigenframe \(U\), the appropriate matrix is
\[
\Sigma^{1/2}U\Lambda U^\top\Sigma^{1/2},
\]
not \(\operatorname{diag}(\lambda_k(\Sigma)\lambda_k(\Lambda))\). In particular,
\[
\mathbb E_U[\Sigma^{1/2}U\Lambda U^\top\Sigma^{1/2}]
=\frac{\operatorname{tr}\Lambda}{n}\Sigma.
\]
The backward amplification averaged along each fixed cloud axis is the same, rather than the \(k\)-th amplification.

**HEURISTIC.** In a genuinely coherent linearization, a random-matrix product, with the actual covariance inserted, is a reasonable surrogate. If its surviving subspace sees approximately isotropic compressed covariance, an exponentially spaced singular spectrum gives
\[
N_1(\varepsilon)\asymp
\min\left(n,\;1+\frac{n}{2ct}\log\frac1\varepsilon\right).
\]
The extra \(1/k\) factor is not justified. More importantly, this predicts a pointwise linear surrogate only when replacing \(B\) by that Jacobian is accurate.

**HEURISTIC.** The supplied coherence radius requires roughly
\[
t\,\theta_{\rm cloud}\ll1.
\]
This means \(t\ll n^{1/3}\) for the stationary cloud, and approximately \(t\ll l\), with a restrictive constant, in the deep input regime. Applying the pointwise Lyapunov spectrum throughout \(t=O(n)\) crosses this validity boundary.

**NUMERICAL.** For the ARC realization used below, the exact one-layer formulas at \(l=31\), evaluated on its fitted Gaussian cloud, give
\[
s_1=0.99042,\qquad
N_1(0.1,0.01,0.001)=(7,37,79).
\]
This is an explicit example of a nearly linear map whose vector-output linear relevance still needs many directions at high precision.

**PROVEN.** Useful bounds for the full problem are
\[
\sum_{j>k}\lambda_j(C_1)
\le \inf_{\dim P=k}\mathbb E\|F-\mathbb E[F\mid PZ]\|^2,
\]
and, by conditional Gaussian Poincaré,
\[
\mathbb E\|F-\mathbb E[F\mid PZ]\|^2
\le \operatorname{tr}((I-P)M),\qquad
M=\mathbb E[(\nabla F)^\top\nabla F].
\]
These give lower and upper dimension bounds from two different matrices. Confusing \(C_1\) with \(M\) loses the distinction between average response and sensitivity.

---

**Q3. Degree spectrum**

**PROVEN UNDER the fixed-depth concentrating-kernel limit.** Define
\[
\kappa(c)=\frac{\sqrt{1-c^2}+(\pi-\arccos c)c}{\pi},
\qquad f_t=\kappa^{\circ t},\qquad c_l=\kappa^{\circ l}(0).
\]
For the input regime’s Gaussian convention, the leading kernel prediction is
\[
C_l(\rho)
=n\left[f_t(c_l+(1-c_l)\rho)-f_t(c_l)\right].
\]
Consequently,
\[
s_d=
\frac{(1-c_l)^d f_t^{(d)}(c_l)}
{d!\,[1-c_L]},
\quad
s_1=\frac{(1-c_l)f_t'(c_l)}{1-c_L},
\quad
D=\frac{1-c_l}{1-c_L}.
\]

**NUMERICAL, evaluating this kernel model.**

| ARC layer \(l\) | \(t\) | \(s_1\) | \(s_2\) | \(D\) |
|---:|---:|---:|---:|---:|
| 0 | 32 | 0.110 | 0.096 | 39.56 |
| 8 | 24 | 0.363 | 0.184 | 6.55 |
| 16 | 16 | 0.582 | 0.190 | 2.79 |
| 24 | 8 | 0.792 | 0.127 | 1.56 |
| 31 | 1 | 0.974 | 0.019 | 1.05 |

**PROVEN UNDER the large-depth kernel asymptotics.** When both \(l,L\) are large,
\[
s_1\simeq \frac lL,\qquad
s_2\simeq \frac{3lt}{4L^2},\qquad
D\simeq\left(\frac Ll\right)^2.
\]
A substantial first-chaos share can therefore coexist with a large mean degree.

**NUMERICAL.** Finite-width corrections are already leading-order for ARC. An independent exact two-replica Gram-chain calculation at \(n=256,L=32,l=0\), using 16,384 chains, gave
\[
\mathbb E_W V\simeq13.21\quad(\mathrm{SE}\ 0.14),
\]
\[
\mathbb E_W V_1\simeq3.41\quad(\mathrm{SE}\ 0.09),
\qquad
\frac{\mathbb E_W V_1}{\mathbb E_W V}\simeq0.258.
\]
Here \(V_1\) used a coupled finite difference at \(\rho=\pm0.01\). The kernel alone predicts \(V=6.47\) and \(s_1=0.110\). The missing amplitude contribution materially changes the answer.

**PROVEN.** At the Gaussian input of a noiseless critical network,
\[
\mathbb E_W\mathbb E_X\|\nabla a(X)\|_F^2=n.
\]
Thus the **variance-weighted annealed mean degree**, not the mean quenched ratio, is \(n/\mathbb E_WV\). The calculation above gives about \(19.38\), rather than \(39.56\).

**PROVEN UNDER the concentrating-kernel approximation with independent future noises.** For the noisy value function, initialize
\[
q_0=\frac{\|m\|^2+\operatorname{tr}\Sigma}{n},
\qquad
z_0(\rho)=\frac{\|m\|^2+\rho\operatorname{tr}\Sigma}{n}.
\]
Propagate
\[
z_j(\rho)=q_{j-1}\kappa\!\left(\frac{z_{j-1}(\rho)}{q_{j-1}}\right),
\]
with \(q_j=q_{j-1}+1\) at hidden layers and no added variance at the output. There is **no \(+1\) in the cross-covariance recursion**. Then
\[
C(\rho)=n[z_t(\rho)-z_t(0)],\qquad
s_d=\frac{z_t^{(d)}(0)}{d![z_t(1)-z_t(0)]},
\qquad
D=\frac{z_t'(1)}{z_t(1)-z_t(0)}.
\]
Shared future noises would compute a different observable.

**HEURISTIC.** For a stationary angular-sector approximation, freeze \(Q\), put \(a=Q/(Q+1)\), and iterate \(c\mapsto a\kappa(c)\) around its fixed point \(c_*=1-\delta_*\). Its relaxation factor is
\[
\alpha=a\kappa'(c_*)
=1-\frac{\sqrt{2\delta_*}}{\pi}+o(Q^{-1/3}),
\]
giving a variance decay rate approximately
\[
0.672\,Q^{-1/3}\simeq0.808\,n^{-1/3}.
\]

**PROVEN UNDER this frozen-radius angular model and its large-\(Q\) continuum limit.** At long scaled times, its normalized degree spectrum does not become purely linear:
\[
s_1\longrightarrow
\frac{e^{\pi/(2\sqrt3)}}{2\sqrt3}=0.71494,\qquad
s_2\longrightarrow0.17874,\qquad
D\longrightarrow\frac32.
\]
To derive this, scale the correlation deficit by \(\delta_*\). Its dynamics becomes
\[
\dot y=1-y^{3/2}.
\]
The asymptotic amplitude of \(1-y\), started at \(y=0\), is
\(2\sqrt3e^{-\pi/(2\sqrt3)}\); differentiating this amplitude with respect to the initial condition gives the numbers above.

**HEURISTIC.** These are angular-sector predictions, not the full stationary answer. Radial fluctuations contribute at the same small-variance order being measured, and \(Q\) varies substantially across quenched environments. Simply substituting its median cannot recover that contribution.

**NUMERICAL.** The narrow network is far outside the useful fixed-depth kernel approximation. Among four surviving realizations, the input-layer scalar-amplitude mean degree ranged from approximately \(3.6\) to \(92.5\). At later cuts a one-dimensional Gaussian support could suffice even when its first-chaos share was small. Degree and projection dimension are genuinely different diagnostics.

---

**Q4. Gates and degree two**

**PROVEN.** For output coordinate \(a\), define
\[
H_a=\mathbb E[F_a(Z)(ZZ^\top-I)].
\]
Equivalently, \(H_a=\mathbb E\nabla^2F_a\), interpreting the Hessian distributionally. Then
\[
V_2=\frac12\sum_a\|H_a\|_F^2,\qquad
V_2(P)=\frac12\sum_a\|PH_aP\|_F^2.
\]

**PROVEN.** For fixed future noise, the distributional Hessian can be expanded over gate boundaries:
\[
\nabla_Z^2F_a
=\sum_{j=1}^{t}\sum_{i=1}^{n}
J_{j\to t,ai}\,
\delta(z_{ji})\,b_{ji}b_{ji}^{\top},
\qquad b_{ji}=\nabla_Zz_{ji}.
\]
The normals and downstream coefficients vary between facets. Taking expectations over \(Z\) and future noise gives \(H_a\).

Hence
\[
V_2=\frac12\sum_a
\left\|\sum_{j,i}H_{a,ji}\right\|_F^2.
\]
This includes cross terms between gates and layers. There is no general additive “variance per gate” accounting.

**PROVEN.** For one future layer, put \(a_i=\Sigma^{1/2}w_i\), \(s_i=\|a_i\|\), and \(\eta_i=w_i^\top m/s_i\). Then
\[
H_i=\frac{\phi(\eta_i)}{s_i}a_i a_i^\top,\qquad
V_2=\frac12\sum_i s_i^2\phi(\eta_i)^2.
\]
This is an exact gate sum because distinct gates are distinct output coordinates.

**PROVEN UNDER the kernel model.** The layer contributions to its second derivative are
\[
f_t''(q)=
\sum_{j=1}^{t}
\left[\prod_{b=j+1}^{t}\kappa'(c_{b-1})\right]
\kappa''(c_{j-1})
\left[\prod_{a=1}^{j-1}\kappa'(c_{a-1})\right]^2.
\]
All future layers contribute. In the deep input asymptotics their weights are approximately proportional to \((l+j)^{-2}\): early future layers dominate when \(t\gg l\), while contributions are more uniform when \(t\ll l\). In the stationary frozen-radius angular model, weights decrease approximately geometrically, so the first \(O(n^{1/3})\) future layers dominate.

**HEURISTIC.** A cloud of angular radius \(\theta\) encounters approximately \(O(n\theta)\) significant gate margins per layer. This gives \(O(n/l)\) in the deep input regime and \(O(n^{2/3})\) for the stationary cloud. The latter differs from the \(O(\sqrt n)\) flips caused by just the newest noise. There are \(nt\) neuron labels, potentially many more pulled-back facets, and their normals are correlated.

**PROVEN.** There is no universal captured fraction determined by \(k,n,V_2\):

- A rank-one quadratic tensor is captured completely in one dimension.
- For \(H\propto I_p\), the fraction captured is \(k/p\).
- For a rank-one tensor with a uniform normal, a fixed independent \(k\)-subspace captures, on average,
  \[
  \mathbb E\|Pu\|^4=\frac{k(k+2)}{p(p+2)}.
  \]

**HEURISTIC.** The often-suggested \((k/n)^2\) law needs sufficiently spread, incoherently combined normals and a projection that cannot exploit a few dominant tensors. Optimizing the projection using the future can violate it substantially.

---

**Q5. Predictions and numerical dimensions**

**PROVEN.** \(n,t,\varepsilon\) do not determine quenched \(N\). Gaussian weights have positive probability of neighborhoods giving nearly one-coordinate dependence, and neighborhoods giving broad coordinatewise dependence. A typical prediction additionally needs an ensemble statistic and assumptions about the cloud and nonlinear tensors.

**NUMERICAL.** I tested explicit projections using Gaussian conditional copies. If
\[
Z'=PZ+(I-P)\widetilde Z,
\]
then the residual is estimated directly from squared output differences. Candidate frames used gradients, with a mean-gradient direction included. These are estimated achievable dimensions, not optimized minima or confidence-certified upper bounds.

For one ARC net, weight seed 25600, Gaussian clouds fitted from 8,192 input trajectories, the results were:

| \(l\) | Vector: 90%, 99%, 99.9% | One independent isotropic scalar readout: 90%, 99%, 99.9% |
|---:|---:|---:|
| 0 | 189, 231, 246 | 189, 231, 246 |
| 8 | 39, 114, 163 | 35, 112, 162 |
| 16 | 13, 61, 115 | 10, 58, 114 |
| 24 | 8, 33, 74 | 2, 25, 68 |
| 31 | 8, 39, 83 | 1, 3, 20 |

The input Gaussian at \(l=0\) was exact. Evaluation used 2,048 conditional pairs for the vector and 4,096 for the scalar. The scalar readout used independent seed 25601; another readout can give different results.

**PROVEN UNDER the fitted Gaussian at ARC \(l=31\).** Exact first-chaos calculations give lower bounds
\[
N(0.1)\ge7,\qquad N(0.01)\ge37,\qquad N(0.001)\ge79.
\]
Capturing sufficient linear variance alone also proves \(N(0.1)\le8\). Thus the first entry is tightly located, and the numerical high-precision entries are close to their linear lower bounds.

**NUMERICAL.** For \(8\times256\), ten independently generated nets were screened with 8,192 inputs. Six had zero output on every screened input. This is sampled extinction, not a proof that their maps vanish everywhere. For the four survivors, achievable dimension ranges were:

| \(l\) | 90% | 99% | 99.9% |
|---:|---:|---:|---:|
| 0 | 3–6 | 7 | 7–8 |
| 8 | 1–2 | 2–4 | 3–6 |
| 32 | 1 | 1 | 1 |
| 128 | 1 | 1 | 1 |
| 255 | 1 | 1 | 1 |

These used weight seeds 8001, 8003, 8005 and 8007. From layer 32 onward, the fitted clouds were effectively rays. Generic scalar readouts inherit this compression.

**PROVEN.** If \(V=0\), the stated explained-share ratio is undefined. Calling \(N=0\) requires an explicit convention.

**NUMERICAL.** For one stationary-width-64 example, a 12\(n\)-layer burn-in and 4,096 paths produced a fitted cloud with \(Q=16.85\). A paired-start diagnostic had relative state RMS \(8.7\times10^{-5}\). Using independent future-noise groups:

| \(t\) | Estimated \(V_g\) | Candidate dimensions: 90%, 99%, 99.9% |
|---:|---:|---:|
| 1 | 313.6 | 19, 39, 51 |
| 8 | 80.2 | 14, 37, 50 |
| 32 | 3.32 | insufficient precision for reliable thresholds |
| 64 | 0.104, after additional averaging | one mean-gradient projection captured about 71% |
| 128 | unresolved | unresolved |

**CONJECTURE.** For stationary widths 32–256, near-output vector relevance will generally require many dimensions at 99–99.9% precision. At long horizons, output variation may become dominated by one response function, but that function can still depend nonlinearly on many input directions. I would not predict \(N=1\), or supply a numerical grid through \(2n\), from the stated constants alone.

**HEURISTIC.** The practical forecast supported here is: ARC has useful compression late at 90%, considerably less at 99.9%; the surviving narrow networks have strong late compression; stationary long-horizon compression remains an unresolved question about the slow response function.

---

**Q6. Stationary channels and decay**

**PROVEN.** Shared-noise contraction bounds the value-function variance:
\[
V_g
\le \frac12\mathbb E_{H,H',\xi}
\|a(H,\xi)-a(H',\xi)\|^2.
\]
Equality need not hold. Therefore the supplied tangent decay
\[
\exp[-2c(k+1/4)t/n]
\]
does not establish the decay rate of \(V_g\).

**HEURISTIC.** There are two candidate scales:

1. Angular correlation relaxation, with rate \(O(n^{-1/3})\), as derived in Q3.
2. A slower amplitude response, potentially with rate \(O(n^{-1})\).

A frozen-radius approximation illustrates why the amplitude rate can differ from the tangent rate. If \(R'\) follows one noisy radial step,
\[
\mathbb E_\xi R'
\approx \sqrt A\,R+\frac{n-1}{2\sqrt A\,R}.
\]
Differentiating gives an additional contraction of amplitude differences. The squared-response rate is approximately
\[
\frac{5}{2n}+\frac1Q.
\]
At \(Q=0.577n\), this is approximately \(4.23/n\). This is a model calculation, not a proved quenched exponent; the actual radius history matters.

**PROVEN UNDER a one-dominant-response-function hypothesis.** If
\[
g_t(h)-\mathbb Eg_t\approx v_t\,\psi(h),
\]
the output is approximately rank one, but
\[
N_g(\varepsilon)\approx N_\psi(\varepsilon).
\]
A scalar output direction does not imply a scalar linear input coordinate.

**NUMERICAL.** In the width-64 experiment at \(t=64\), using 64 future trajectories per input in each of two independent groups, a future-informed mean-gradient projection captured approximately 71% of \(V_g\). The linear projection along the cloud mean captured approximately 30%. Thus “the radius carries the surviving information” is too strong even in this modest test.

**CONJECTURE.** The correct slow coordinate is a future-dependent amplitude response \(\psi(h)\), rather than necessarily \(\|h\|\) or \(m^\top h\). Determining its residual after the best linear projection is the central missing stationary calculation. Neither its output rank nor the top Lyapunov exponent answers that question.

---

**Q7. Estimation**

**PROVEN.** Suppose \(q(PZ)\) approximates \(f(PZ)=\mathbb E[g(Z)\mid PZ]\), and its Gaussian integral \(I_q\) is available. Then
\[
\widehat I
=I_q+\frac1M\sum_{i=1}^M[g(Z_i)-q(PZ_i)]
\]
is unbiased, and its trace variance is
\[
\frac1M\left[
V(1-S(PZ))+\operatorname{tr}\operatorname{Cov}(f-q)
\right].
\]
With exact conditional integration and residual share \(\varepsilon\), the ideal gain is \(1/\varepsilon\), before setup and evaluation costs.

**HEURISTIC.** Where \(k\) is small, fit or quadrature-resolve the \(k\)-dimensional conditional mean, integrate it accurately, and sample the residual. This is plausible for the late narrow-network cuts and some scalar ARC cuts. The Gaussian fit, frame construction and conditional-mean fitting must all be charged.

**PROVEN.** If evaluations use noisy outputs \(a\), rather than exact \(g\), the residual also contains future-noise variance:
\[
\operatorname{tr}\operatorname{Var}(a-q)
=
\mathbb E\operatorname{tr}\operatorname{Var}(a\mid H)
+\operatorname{tr}\operatorname{Var}(g-q).
\]
A small \(N\) for a very small \(V_g\) can therefore provide little improvement for estimating the full output mean.

**HEURISTIC.** At equal compute:

- Plain MC is the baseline with no frame-learning cost.
- RQMC can improve the low-dimensional resolved part, but \(N\) alone does not establish its convergence rate.
- Multilevel shared-trajectory sampling should be compared using its level differences. With optimal allocation, its variance-cost factor is proportional to
  \[
  \left(\sum_j\sqrt{V_jC_j}\right)^2.
  \]
  Low relevance of a level difference can be more useful than low relevance of the whole output.

**PROVEN.** Large \(N\) does not rule out a sample-free estimator. Under the Gaussian convention with one layer remaining,
\[
\mathbb E[\operatorname{ReLU}(w_i^\top H)]
=s_i\phi(\eta_i)+(w_i^\top m)\Phi(\eta_i),
\]
exactly, however large the relevance dimension is.

**PROVEN.** Consequently, these diagnostics cannot prove that ARC lacks a sample-free estimator beating sampling at growing depth. Such a lower bound needs a computational or information-access model. Predicting a random output accurately and computing its expectation are different tasks.

---

**Q8. Red team and a better “bits” definition**

**PROVEN.** The framing has several consequential weaknesses.

1. **The denominator changes under Gaussianization.** \(V^\mu\) and \(V^\gamma\) must be distinguished. Hermite accounting sums to \(V^\gamma\); it cannot use the original \(V^\mu\) denominator.
2. **Gaussianization changes support and reachable branches.** A noiseless hidden state is nonnegative. Its Gaussian replacement need not be. For a cloud concentrated on a positive ray, Gaussianization can introduce a negative-ray branch with a different future gain.
3. **Degree does not determine dimension.** A high-degree function of one Gaussian coordinate has \(N=1\). Conversely, \(\sum_i(Z_i^2-1)\) has degree two and needs approximately \((1-\varepsilon)n\) linear coordinates.
4. **Output rank does not determine input relevance.** A rank-one output can encode a complicated scalar function of all coordinates.
5. **Means omit other predictive objectives.** \(g=\mathbb E[a\mid H]\) is appropriate for squared-error prediction of the output mean, but does not characterize conditional tails or the full output law.

**PROVEN.** The exact flip identity is algebraically valid with a consistent binary gate convention and the reference trajectory driven by the same future noise. Its interpretation needs care:

- Its frozen Jacobian is not generally \(B\).
- Flip terms are correlated and have nontrivial cross terms.
- Pulled-back flips are nonlinear functions of the initial state.
- The noisy reference trajectory is not the trajectory of conditional means.
- At the noiseless zero mean, the all-zero reference gates make the identity largely tautological.

Thus the identity organizes the difference, but does not itself provide an orthogonal variance decomposition.

**PROVEN.** Counting arbitrary real-valued statistics is also insufficient: without regularity or coding restrictions, a single real statistic can measurably encode an entire vector.

**PROVEN.** A literal bit-based alternative is predictive rate-distortion:
\[
R_l(\varepsilon)=
\inf_{p(T\mid H)}
I(H;T)
\quad\text{subject to}\quad
\mathbb E\|g(H)-\mathbb E[g(H)\mid T]\|^2
\le\varepsilon V.
\]
Use base-two information units. This counts information needed for the specified prediction task, rather than coordinates. Encoder computation must be recorded separately, since computing \(g\) and then quantizing it can be expensive.

**HEURISTIC.** A useful empirical counterpart is a cross-fitted curve of residual predictive variance against code length and encoder cost. Compare linear projections, radius/amplitude features and quantized nonlinear encoders. For Gaussian projections, the exact diagnostic is
\[
1-S(PZ)
=\frac{\mathbb E\|g(Z)-g(PZ+(I-P)\widetilde Z)\|^2}{2V}.
\]
When \(g\) is unavailable, use independent future-noise groups to estimate the product of conditional differences, with shared noise within each difference to reduce variance. This is the measurable quantity used in the stationary checks above.
