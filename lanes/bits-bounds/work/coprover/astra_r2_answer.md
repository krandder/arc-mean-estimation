codex
PROVEN: The mean-field cubic law is correct. The reported finite-width enhancement uses a different normalization and does not establish an enhancement of the theorem’s annealed residual. Neither the adopted linear-feature count \(N\) nor \(N_{\rm cell}\) alone lower-bounds mean-estimation cost.

Notation: \(t=L'\), \(\phi\) is the initial angle, and \(D\) denotes absolute squared distortion. I reserve \(N\) for the adopted linear-feature count and rename FORMAL v1’s count \(N_{\rm cell}\). The precision conventions differ: adopted \(N(\ell,\eta)\) uses \(\eta V_\ell\); the cell definition uses \(\varepsilon^2V\).

**1. Claim-by-claim audit**

| Claim | Verdict and status | Required correction or qualification |
|---|---|---|
| Prop. 2.2 | CORRECT AFTER FIX — PROVEN | Separate scalar operations from mv units. Dense Gaussian propagation costs \(O(n^3)\) scalar operations, hence \(O(n)\) mv per layer. Cone descriptions can require \(O(n^2L)\) numbers per cell, and Gaussian cone integration must be charged. “Number of cones” is a component count, not memory in reals. Cumulant-transform costs require specifying the actual implementation. |
| Thm. 3.1 | CORRECT — PROVEN | The sharper crossing count is \(p+\#\{\text{adjacent passes with the same direction}\}\le2p-1\). Alternating directions need only \(p\) crossings. This agrees with my round-1 “about \(2pM\)”. The output must be allowed at the party finishing the last pass; otherwise an additional output transmission may be needed. |
| Cor. 3.2 | CORRECT — PROVEN UNDER K2 | Keep K2’s fixed-\((n,\ell,t)\), high-precision and distributional-error qualifications. It does not provide a uniform bound when \(n,L,\varepsilon\) scale together. |
| Prop. 3.3 | CORRECT AFTER FIX — PROVEN UNDER an annealed error criterion | Quantize weights on expanding bounded sets, control Gaussian tails, and approximate the final integral. For fixed \(n,L\), the leading description length is as stated. This is not a uniform relative-error guarantee over all unbounded Gaussian weight realizations. Final computation is unlimited here and must be charged in a computational model. |
| Def. 4.1 | CORRECT AFTER FIX — PROVEN | A truncated cumulant list is not automatically a finite signed measure, nor does it determine nonlinear push-forwards. Specify a measure-valued closure or a functional calculus with valid pairings. Multilevel cohorts and branch-and-bound bookkeeping also require auxiliary state beyond the aggregate measure. |
| Thm. 4.2 | CORRECT — PROVEN UNDER integrability | The telescoping identity is exact whenever its pairings exist. “Sampling puts all error in the first term” applies to initial particle sampling without later resampling; randomized closures create later defects too. |
| Lemma 4.3 | CORRECT AFTER FIX — PROVEN | Use differentiable reference points, or a specified compatible linear branch on boundaries. Moreover \(r_j=|z_j(h)|\,1_{\{\text{gate disagreement}\}}\ge0\) componentwise. Its propagated contributions need not be orthogonal. |
| Prop. 4.4 | CORRECT — PROVEN UNDER suffix independence and integrability | Condition on the entire past and algorithmic randomness. The identity concerns one defect’s squared norm; it does not eliminate cross terms between defects at different layers. |
| Thm. 5.1 | CORRECT — PROVEN | Require nonzero \(h,c\); handle zero separately. Both residual formulas and their constants are correct. |
| Thm. 5.2 | CORRECT AFTER FIX — PROVEN UNDER fixed-depth infinite width | The Gaussian regression and preserved quantities are correct. Section 2 below proves the cubic law and gives its next term. The reciprocal-angle formula needs an explicit limiting regime: at fixed initial angle and \(t\to\infty\), there is a logarithmic correction, not an additive \(o(1)\). |
| Def. 5.3 | CORRECT AFTER FIX — PROVEN | Rename it \(N_{\rm cell}\). Homogeneity makes reference radius irrelevant. A one-cell optimum need not use the mean, and the mean need not belong to the support. Freeze or explicitly price the choice of merge rule. |
| Thm. 6.1 | CORRECT AFTER FIX — PROVEN | For randomized codebooks, \(H(\widehat X)\le\log M\) can fail. Condition on independent public randomness, as proved below. |
| Cor. 6.2 | CORRECT AFTER FIX — PROVEN UNDER angular-density hypotheses | Its Euclidean lower bound fails for the actual homogeneous distortion: \(h=2c\) gives zero residual. A capped-distance distortion also does not directly admit the displayed Euclidean Shannon-bound proof. Quantize directions under the radius-squared-weighted angular law instead. |
| Thm. 6.3 | WRONG as a fixed-net separation — PROVEN counterargument | Pointwise minimization over past-measurable policies includes every constant codebook, including the realized optimal partition. The valid comparison is future-blind policies averaged over random futures versus future-adaptive policies. That corrected comparison can diverge as \(\varepsilon\to0\); see section 4. Region construction and integration are not free consequences of one backward pass. |
| Prop. 6.4 | CORRECT AFTER FIX — PROVEN UNDER a partition restriction | Require every cell to lie in one specified maximal affine region, and count regions modulo null sets on the cloud. Otherwise one cell may combine disconnected pieces on which the same affine map applies. Counting gate patterns also overcounts gates irrelevant to the output. |
| Prop. 6.5 | CORRECT AFTER FIX — PROVEN UNDER K3 | A Gaussian input permits exact next-layer ReLU integration. The resulting law is generally non-Gaussian. K3 gives fixed-\(n,K\) failure of a specified truncation, not a width-uniform polynomial bias floor, and not a floor for arbitrary Gaussian mixtures. |
| Prop. 6.6 | CORRECT AFTER FIX — PROVEN for the specified oracle families | The unknown-bias table theorem from round 1 supplies a precise example. It does not imply that every useful gain on iid He networks must use weights: structured black-box quadrature and control variates can improve particular problems. |
| Section 7 | CORRECT AFTER FIX — PROVEN for the estimator identities; HEURISTIC for gains | Condition on independently constructed controls before taking level samples. Include the first level’s variance, partition construction, assignment, cell integration, memory and setup. The displayed difference-variance bound is correct. The claimed optimized gain exponent applies to the rough case only; correction below. |
| Section 8 | HEURISTIC, with a specific correction | The covariance participation ratio is not the dimension governing arbitrarily fine quantization. In the frozen-radius noisy mean-field model, \(2.23Q^{-2/3}\) describes \(1-\cos\theta\), not \(\theta\); thus \(\theta\asymp Q^{-1/3}\). Noiseless radial-merge formulas cannot simply be transferred to additive-noise futures. |
| Prop. 9.1 | WRONG literally; CORRECT AFTER FIX — PROVEN | The assumptions imply \(\mathbb EV_{\rm within}=s^2(1-1/K)\), \(K=2^N\), rather than \(s^2\). Partial-enumeration risk is correct for a fixed queried subset. Against actual with-replacement MC, the uniform improvement is approximately four, not always at least four. For \(K=2,T=1\), it is exactly two. |
| Section 10 | CORRECT AFTER FIX — CONJECTURE ledger | C1’s evidence uses the wrong normalization. C2 is at most an ensemble/pre-asymptotic law. C3 needs survival/log regularization and the constant \(6\pi\). C4 remains computationally open and its constant-factor formulation is stronger than “no polynomial gain”. C5 is not established by counting observed gate disagreements. |

PROVEN: Two specific corrections to section 7 and Prop. 9.1 are
\[
C(M)\asymp aM+b\varepsilon^{-2}M^{-p}
\quad\Longrightarrow\quad
C_{\rm opt}\asymp\varepsilon^{-2/(p+1)}.
\]
Thus the idealized gain over \(\varepsilon^{-2}\) is
\[
\varepsilon^{-6/(d+3)}\quad(p=3/d),\qquad
\varepsilon^{-2/(d+1)}\quad(p=1/d).
\]
These statements assume the advertised residual and cost laws, including a computable baseline.

PROVEN: For Prop. 9.1, partial enumeration and with-replacement MC have annealed risks
\[
R_{\rm partial}=\frac{(K-T)s^2}{K^2},
\qquad
R_{\rm MC}=\frac{(K-1)s^2}{KT}.
\]
Their ratio is \(T(K-T)/(K(K-1))\). The qualitative known-bias counterexample survives completely.

**2. The cubic law**

PROVEN UNDER fixed-depth infinite width: The regression in Thm. 5.2 simplifies substantially. Put
\[
s=\cos\phi,\qquad r_j=\cos\phi_j,\qquad q_j=\cos\psi_j,
\qquad
P_j=\prod_{i=0}^{j-1}\left(1-\frac{\phi_i}{\pi}\right).
\]
Then
\[
r_{j+1}=\left(1-\frac{\phi_j}{\pi}\right)r_j+
              \frac{\sin\phi_j}{\pi},
\]
\[
q_{j+1}=\left(1-\frac{\phi_j}{\pi}\right)q_j+
              s\frac{\sin\phi_j}{\pi}.
\]
Consequently,
\[
\boxed{q_t=s\,r_t+(1-s^2)P_t.}
\tag{2.1}
\]
Equivalently, if \(C_t=\kappa^{\circ t}\),
\[
q_t=sC_t(s)+(1-s^2)C_t'(s).
\]
This avoids the ill-conditioned division by \(1-\cos^2\phi_j\) in the current implementation.

PROVEN: To verify the preserved quantities, for centered jointly Gaussian row projections,
\[
2\mathbb E[Z^2 1_{\{Y>0\}}]=\mathbb EZ^2,\qquad
2\mathbb E[YZ1_{\{Y>0\}}]=\mathbb E[YZ].
\]
Sign reversal proves both identities. Conditional laws of large numbers then preserve \(|v_j|^2\) and \(c_j\cdot v_j\) in the fixed-depth infinite-width limit. At finite width these are conditional-expectation identities, not pathwise invariants.

PROVEN UNDER the same mean-field limit: At fixed integer \(t\),
\[
\boxed{
D_F^{\rm MF}(t,\phi)
=
\frac{4t}{3\pi}\phi^3
-\frac{t(t-1)}{\pi^2}\phi^4
+O_t(\phi^5).
}
\tag{2.2}
\]
For \(t=1\), the next nonzero term is \(-4\phi^5/(15\pi)\).

PROVEN: One derivation uses
\[
\phi_{j+1}=\phi_j-\frac{\phi_j^2}{3\pi}
                    -\frac{\phi_j^3}{18\pi^2}+O(\phi_j^4).
\]
Writing \(F_j=2(1-q_j)\),
\[
F_{j+1}
=\left(1-\frac{\phi_j}{\pi}\right)F_j
+\frac2\pi\bigl(\phi_j-s\sin\phi_j\bigr).
\]
Substitute \(\phi_j=\phi-j\phi^2/(3\pi)+O_j(\phi^3)\). The cubic increments sum to \(4t\phi^3/(3\pi)\); the quartic increments sum to \(-t(t-1)\phi^4/\pi^2\). No independence assumption about propagated flips is needed.

PROVEN UNDER the scaling limit \(\phi\downarrow0\), \(x=t\phi/(3\pi)\) fixed:
\[
\phi_t=\frac{\phi}{1+x}+O(\phi^2),\qquad
P_t=(1+x)^{-3}+O(\phi),
\]
and hence
\[
\boxed{
D_F^{\rm MF}
=\phi^2\left[1+\frac1{(1+x)^2}
                 -\frac2{(1+x)^3}\right]+o(\phi^2),
\qquad
D_R^{\rm MF}=\frac{\phi^2}{(1+x)^2}+o(\phi^2).
}
\tag{2.3}
\]
The crossover is therefore
\[
\boxed{t\phi=3\pi(2^{1/3}-1)\approx2.44970.}
\]
For finite \(t=16\), the recursion gives approximately \(t\phi=2.384\).

PROVEN UNDER mean field: For fixed initial \(\phi\) and \(t\to\infty\), \(r_t\to1\), \(P_t\to0\), so \(D_F^{\rm MF}\to2(1-\cos\phi)\). The reciprocal-angle expansion contains
\[
\frac1{\phi_{j+1}}-\frac1{\phi_j}
=\frac1{3\pi}+\frac{\phi_j}{6\pi^2}+O(\phi_j^2).
\]
Its accumulated correction grows logarithmically with \(t\). The additive \(o(1)\) in v1 is therefore inappropriate for this limit.

PROVEN: The finite-width chain returns a different observable:
\[
\mathbb E\frac{|h_t-v_t|^2}{|h_t|^2},
\]
whereas Thm. 5.2 and C1 concern
\[
\frac{\mathbb E|h_t-v_t|^2}{|h_0|^2}.
\]
The code also discards the accumulated common scale during renormalization. Recovering the latter quantity requires retaining that scale.

PROVEN: There is an exact finite-width small-angle result for the raw residual. For \(n\ge2\), fixed finite \(t\), and unit initial vectors, define
\[
\beta_n=1-2^{1-n},\qquad S_{n,t}=\sum_{j=0}^{t-1}\beta_n^j.
\]
Then
\[
\boxed{
\mathbb E|h_t-v_t|^2
=\frac4{3\pi}S_{n,t}\phi^3+o_{n,t}(\phi^3).
}
\tag{2.4}
\]
Thus its cubic coefficient has no positive \(t/n\) correction. For ordinary widths, \(S_{n,t}\) differs from \(t\) only through exponentially small rank-collapse probabilities.

PROVEN, proof of (2.4): Write the finite-width kernel as \(k_{n,t}(r)\). Differentiating its homogeneous extension and using annealed tangent-energy preservation gives
\[
\mathbb E|h_t-v_t|^2
=2\left[1-s\,k_{n,t}(s)-(1-s^2)k_{n,t}'(s)\right].
\tag{2.5}
\]
For one layer, condition on the number \(m\sim{\rm Bin}(n,1/2)\) of reference-active units. For a unit tangent perpendicular to the reference, the next reference norm and perpendicular tangent norm have laws
\[
|c'|=\sqrt{2/n}\,\chi_m,\qquad
|u'_\perp|=\sqrt{2/n}\,\chi_{m-1},
\]
with independent chi variables conditional on \(m\). For \(m\ge2\),
\[
\mathbb E\chi_{m-1}^3\,\mathbb E\chi_m^{-1}=m.
\]
The cubic angular kernel coefficient is therefore multiplied by
\[
\frac2n\mathbb E[m1_{\{m\ge2\}}]=\beta_n.
\]
The one-layer kernel contributes a new coefficient one, giving
\[
k_{n,t}(\cos\phi)
=1-\frac{\phi^2}{2}+\frac{S_{n,t}}{3\pi}\phi^3+o(\phi^3).
\]
The corresponding differentiated expansion in (2.5), or the same single-boundary calculation for the residual, gives (2.4).

PROVEN: The unregularized output-normalized expectation has a more serious problem. With positive probability \(h_t=0\) while \(v_t\ne0\). Already at one layer, take all true preactivations negative and at least one reference preactivation positive. Thus the literal ratio has no finite unconditional expectation. Even conditioning on nonzero output does not generally repair inverse-small-norm moments. The denominator floor and covariance jitter in `chain3.py` regularize this numerically; they do not produce the raw theorem’s observable.

PROVEN UNDER a regularized, surviving-reference calculation, with \(\phi\to0\) first and fixed \(t\): The ordinary large-\(n\) expansion of the normalized cubic coefficient is
\[
\boxed{
\frac{\mathbb E_{\rm reg}[|h_t-v_t|^2/|h_t|^2]}
     {(4/(3\pi))t\phi^3}
=
1+\frac{5t+1}{n}+O_t(n^{-2})+o_\phi(1).
}
\tag{2.6}
\]
Here regularization excludes exponentially unlikely low-active-count reference paths and clips the output denominator relative to the reference norm.

PROVEN UNDER those conditions: The factors behind (2.6) are:

- accumulated angular-cube amplification \(1+6/n+O(n^{-2})\) per preceding layer, from \(\mathbb E[\chi_{m-1}^3/\chi_m^3]=m/(m-3)\);
- a local flip-normalization factor \(1+6/n+O(n^{-2})\);
- subsequent relative tangent-energy amplification \(1+4k/n+O_k(n^{-2})\) over \(k\) remaining layers.

A flip introduced after \(j\) layers consequently contributes the factor
\[
1+\frac{6j+6+4(t-1-j)}n+O_t(n^{-2}).
\]
Averaging over \(j=0,\ldots,t-1\) yields (2.6). The enhancement is largely inverse-reference-norm amplification, including correlations carried along the reference path.

HEURISTIC: Resumming these factors at \(s=t/n=O(1)\) gives
\[
\frac{2e^{6s}-3e^{2s}+1}{6s}.
\]
Its expansion is \(1+5s+O(s^2)\). This is a plausible description of typical regularized means, not a finite value for the unregularized population mean.

HEURISTIC, numerical check rather than proof: A fresh three-replica calculation retaining the discarded scale gave, at \(t=16,\phi=0.01\),

| Width | Raw residual / MF | Observed output-normalized average / MF |
|---:|---:|---:|
| 64 | \(0.988\), SE \(0.017\) | \(3.64\) |
| 128 | \(0.979\), SE \(0.008\) | \(1.90\) |
| 1024 | \(1.001\), SE \(0.005\) | \(1.09\) |

The first two batches had 24,000 chains; the last had 6,000. The normalized columns describe finite batches, not a well-defined unregularized expectation. These results support the normalization explanation.

**3. The rough regime**

PROVEN: Let \(A(u)=|\operatorname{ReLU}(Wu)|^2\) for unit \(u\). For two unit directions at angle \(\theta\),
\[
\mathbb EA=1,\quad \operatorname{Var}(A)=5/n,\quad
\operatorname{Cov}(A(u),A(v))=B(\cos\theta)/n,
\]
where
\[
B(\cos\theta)=\frac2\pi
\left[3\sin\theta\cos\theta+
(\pi-\theta)(1+2\cos^2\theta)\right]-1.
\]
Its expansion is
\[
\boxed{5-B(\cos\theta)=4\theta^2-\frac43\theta^4+O(\theta^5).}
\tag{3.1}
\]
The asymptotic coefficient is four, not 2.9.

PROVEN UNDER log regularization and the fixed-depth large-width limit: The difference of log-*norm* increments is
\[
\Delta_j=\tfrac12(\log A_j(u)-\log A_j(v)).
\]
The two marginal increment laws agree conditionally on the past, so their difference has conditional mean zero. Taylor expansion gives
\[
\operatorname{Var}(\Delta_j\mid\mathcal F_j)
=\frac{5-B(\cos\theta_j)}{2n}+o(n^{-1}).
\tag{3.2}
\]
Different layers’ increments are orthogonal martingale differences. Consequently,
\[
\lim_{n\to\infty}n\operatorname{Var}\!\left(
\log\frac{|g(h)|}{|g(c)|}\right)
=\frac12\sum_{j=0}^{t-1}[5-B(\cos\phi_j)].
\tag{3.3}
\]
The regularization is necessary because finite-width extinction makes literal log norms undefined.

PROVEN UNDER the iterated limits “large width first, then small angle with \(x=t\phi/(3\pi)\) fixed”:
\[
\sum_{j<t}\phi_j^2
=3\pi\phi\,\frac{x}{1+x}+o(\phi),
\]
so
\[
\boxed{
\operatorname{Var}\!\left(\log\frac{|g(h)|}{|g(c)|}\right)
\sim\frac{6\pi}{n}\phi\,\frac{x}{1+x}.
}
\tag{3.4}
\]
Therefore \(c=6\pi\) when \(t\phi\gg1\). For differences of log-*squared* norms, the constant is \(24\pi\).

HEURISTIC, promoted to PROVEN UNDER uniform moment control for the mesoscopic expansion: In the window
\[
\phi\ll1,\qquad 1/\phi\ll t\ll n,
\]
the radial merge has
\[
\boxed{
D_R(t,\phi)\approx
\left(\frac{3\pi}{t}\right)^2+\frac{6\pi}{n}\phi
}
\tag{3.5}
\]
for unit initial radius. The first term is remaining angular separation; the second is gain separation. The requisite control includes the finite-width correction to the angular term being \(O(1/(nt))\), hence smaller than \(\phi/n\). Formula (3.3) is the proved fixed-depth coefficient; uniform extension to \(t=\alpha n\) requires additional estimates.

PROVEN: “Directions merge, leaving only gains” is therefore an approximation with two qualifications: the remaining angular term must be small enough, and at finite width the gain term must dominate it. In (3.5), gain dominance requires roughly \(\phi\gg n/t^2\), stronger than merely \(t\phi\gg1\) in some regimes.

PROVEN UNDER a regular \(d\)-dimensional angular source and uniform comparable variograms: Reference quantization with distortion comparable to \(\phi^p\) has
\[
D(M)\asymp M^{-p/d}.
\]
Thus a cubic frozen distortion gives \(M^{-3/d}\), while a gain variogram comparable to \(\phi/n\) gives \(n^{-1}M^{-1/d}\). The proof is the usual covering upper bound and small-ball-volume lower bound.

HEURISTIC: Applying this to the observed clouds requires proving the variogram bounds and identifying \(d\). Neither \(d\approx2\,{\rm PR}\) nor a quenched rough-field law follows from (3.4). At a fixed finite network, future-adaptive frozen cells eventually become exactly linear, so a positive power law cannot hold for all \(M\to\infty\). Also, a fixed reference has a nonzero gate-coherence neighborhood almost surely; its quenched residual is eventually exactly zero as \(\phi\downarrow0\).

**4. What can be proved using the adopted \(N\), and what concerns the mean**

PROVEN: Relevance’s Theorem 1 is sound. Its Corollary 1b needs a small correction: conditional on \((\mathcal F_\ell,\mathcal G)\), the right side of its energy identity must also be averaged. Equivalently, condition additionally on the singular values. An unaveraged random trace cannot equal a conditional expectation.

PROVEN UNDER a Gaussian angular cloud and a linear future: Let
\[
X=m+B\Lambda^{1/2}Z,\qquad Z\sim N(0,I_d),\qquad d=n-1,
\]
and let the angular future be \(AZ\) after the appropriate covariance factors. More explicitly, write the map on angular coordinates as \(A\), with conditional right-rotation invariance
\[
\mathbb E[A^\top A\mid\mathcal F_\ell,\mathcal G]=aI_d.
\]
For a past-measurable rank-\(k\) feature matrix \(P\), its Gaussian conditional covariance is
\[
C_P=\Lambda-\Lambda P^\top(P\Lambda P^\top)^\dagger P\Lambda.
\]
Then
\[
\mathbb E_{\rm future}R(P)=a\,\operatorname{tr}C_P,
\qquad
\inf_{\operatorname{rank}P=k}\mathbb E_{\rm future}R(P)
=a\sum_{i>k}\lambda_i(\Lambda).
\tag{4.1}
\]
For a future-aware \(P\), the optimum is instead
\[
\sum_{i>k}\lambda_i\!\left(\Lambda^{1/2}A^\top A\Lambda^{1/2}\right).
\tag{4.2}
\]
These are exact Gaussian conditional-expectation and spectral-truncation identities.

PROVEN: For an isotropic angular cloud, a blind \(k\)-feature choice leaves the fraction \(1-k/d\) of annealed linear variance. A future-aware choice needs only \(\operatorname{rank}A\) features for exact linear representation. This gives the clean \(d/r\) separation; a scalar linear readout has \(r=1\). Relevance’s decoupling theorem and round-1 §5.4 justify the random orientation.

PROVEN UNDER a justified local-linear approximation: These statements transfer to the adopted \(N\) only up to the approximation error. They do not establish that forward-only PCA is optimal for the full nonlinear \(g\). In particular, rotational invariance alone does not make nonlinear explained variance proportional to captured cloud variance. Keep the Gaussian-law variance and true-law threshold \(V_\ell\) distinct if they differ.

PROVEN: There is no corresponding general mean-estimation lower bound. Already
\[
g(X)=AX+b
\]
has potentially large representation count and exact mean \(Am+b\). More generally,
\[
\mathbb E\,\mathbb E[g(X)\mid PX]=\mathbb Eg(X)
\]
for every \(P\), including \(P=0\). On an actual one-layer He network with Gaussian input,
\[
\mathbb E_X\operatorname{ReLU}(WX)_i
=\frac{\|W_{i,:}\|}{\sqrt{2\pi}},
\]
despite nontrivial trajectory-feature requirements.

PROVEN: The correct role of representation residual is as a *sufficient error or variance bound*, coupled to an integration mechanism. If a computable control \(a(X)\) has known integral,
\[
\widehat\mu=\mathbb Ea+\frac1m\sum_{i=1}^m[g(X_i)-a(X_i)]
\]
has
\[
\operatorname{MSE}
=\frac{\operatorname{trVar}(g-a)}m
\le\frac{\mathbb E|g-a|^2}{m}.
\tag{4.3}
\]
A lower bound on the last second moment is not automatically a lower bound on the centered variance or on deterministic mean error.

PROVEN: For forward-law mismatch, suppose \(dq/d\mu=1+u\), with
\[
\mathbb E_\mu[u\mid PX]=0.
\]
Writing \(r=g-\mathbb E[g\mid PX]\),
\[
\mathbb E_qg-\mathbb E_\mu g=\mathbb E_\mu[ur],
\qquad
|\mathbb E_\mu[ur]|^2\le\mathbb E_\mu u^2\,\mathbb E_\mu|r|^2.
\tag{4.4}
\]
For scalar output, equality is attained over signed \(L^2\) perturbations by \(u\propto r\). For vector output, the sharp squared coefficient is
\(\lambda_{\max}(\mathbb E rr^\top)\), rather than its trace. Positivity of \(1+u\) adds a restriction. This is a robustness statement against forward-law errors, not an iid-He lower bound on computing the mean. Matching the mean of the forward law removes affine discrepancies, but even \(N_{\ge2}\) is not by itself a computational lower bound.

PROVEN: The randomized rate-distortion correction is straightforward. Conditional on the prefix, let \(R\) be independent public randomness and let \(S\in\{1,\ldots,M\}\) be the cell index. Since \(\widehat X=c_S(R)\),
\[
I(X;\widehat X)
\le I(X;S,R)
=I(X;S\mid R)
\le\log_2M.
\tag{4.5}
\]
Thus Thm. 6.1 survives randomization. References selected using the source realization outside the charged index would violate this model.

PROVEN: For homogeneous merges, put \(H=RU\), \(|U|=1\). The future-averaged distortion has the form
\[
\rho(H,c)=R^2 f_t(\angle(U,c)).
\]
For a fixed codebook, optimal assignment therefore depends only on \(U\). Define the weighted angular law
\[
\widetilde P(du)
=\frac{\mathbb E[R^2\mid U=u]}{\mathbb ER^2}\,P_U(du).
\tag{4.6}
\]
The cell problem reduces exactly to angular quantization under \(\widetilde P\).

PROVEN UNDER a compact regular \(d\)-dimensional angular support, finite differential entropy, and
\(f_t(\theta)\ge a\min(\theta,\theta_0)^3\): The corrected Shannon-type bound is
\[
\boxed{
\log_2M\ge
\frac d3\log_2\frac{\mathbb ER^2}{D}+O(1).
}
\tag{4.7}
\]
Indeed, regular angular-ball volumes imply uniformly in reconstruction \(c\),
\[
\int e^{-\lambda f_t(\angle(u,c))}\,d{\rm vol}(u)
\le C\lambda^{-d/3}.
\]
The entropy variational bound, optimized over \(\lambda\), proves (4.7). Comparable upper bounds follow from coverings when the distortion has a matching cubic upper bound. The relevant dimension is an actual source dimension, not its covariance participation ratio.

PROVEN UNDER those source hypotheses: Fix a prefix and average over iid He suffixes. Every future-blind \(M\)-reference policy has distortion bounded below as in (4.7), whereas a future-adaptive policy can use the finitely many future gate regions and attain zero frozen residual. Since the number of gate patterns is at most \(2^{nt}\), this gives an unbounded high-precision separation in *representation cell count*. It remains valid after averaging over prefixes on any positive-probability set with the required uniform source bounds. This supplies an average-case statement, not a typical-width complexity estimate.

PROVEN: This cell separation still does not imply a mean-estimation separation. A large \(D(Q)\) allows cancellation in \(\mathbb E[g-m_Q]\), and computing exact conditional means makes every partition mean-exact. A robust or representation-preserving cell class can inherit the lower bound; unrestricted cell-based mean computation cannot inherit it without another assumption.

PROVEN: The clean mean-information parameter remains round-1 \(N_{\rm law}\). With independent prefix \(A\) and suffix \(B\), define
\[
T(A)(B)=\mathbb E[g_B(H_A)]
\in L^2(B;\mathbb R^n).
\]
Every \(b\)-bit one-way mean estimator has annealed squared error at least
\[
D_{2^b}(T(A)).
\tag{4.8}
\]
An ideal encoder knowing \(B\) instead faces the conditional quantization problem for \(\mu(A,B)\). This is the correct forward-only versus future-informed mean comparison. Neither decoupling nor the adopted \(N\) evaluates these quantities or pays for the preliminary future information.

**5. The computational bottleneck**

PROVEN: A \(K\)-only bias floor cannot hold for a class containing arbitrary Gaussian mixtures with polynomially many components. Degenerate Gaussian components are particles; arbitrarily narrow Gaussians approximate them. Such mixtures can implement Monte Carlo with any fixed polynomial sample count. Thus “all \(K=2\) Gaussian closures have a \(c/n\) floor” is false for that broad class.

CONJECTURE: For the specific *single-Gaussian* recursion that propagates its mean and covariance by exact Gaussian ReLU formulas and then re-Gaussianizes, a positive annealed bias floor at \(L=\alpha n\) is plausible. I do not have a proof of \(c(\alpha)/n\). The stationary measurement \(0.12/n\) does not establish it for the noiseless input regime.

PROVEN: The normalization must also be specified in stationary Model S. Its fresh-weight stationary annealed law has infinite second moment, as established in round 1. A finite-depth, quenched, truncated, or per-net-normalized stationary measurement is a different object.

PROVEN: K3 is insufficient for a polynomial floor in \(n\). An event with probability exponentially small in \(n^2\) can give positive error for each fixed \(n,K\) while contributing less than every inverse polynomial as \(n\to\infty\). K3 also does not bound all closure variants or mixtures.

PROVEN: Bounded exponents \(a_K\) are unnecessary for a sampling barrier. Suppose a specified order-\(K\) method costs \(n^{\beta_K+o(1)}\) mv units and has nMSE at least \(n^{-a_K-o(1)}\). The relation
\[
a_K\le\beta_K
\tag{5.1}
\]
already prevents an exponent-level advantage at polynomial target precisions, subject to uniformity over admissible choices. Dense Gaussian propagation has total cost \(O(n^2)\) mv at depth \(\alpha n\); a \(1/n\) floor would be consistent with this relation. Allowing \(a_K\) to grow with \(K\) is harmless if its cost grows at least as fast.

CONJECTURE, a sufficient exponent-level target: Specify a uniform closure class, its splitting rules, precision, preprocessing, and allowed residual corrections. At \(L=\alpha n\), require
\[
C_{\rm closure}(n,\varepsilon=n^{-q/2})
\ge n^{\max(1,q)-o(1)}
\tag{5.2}
\]
for every fixed \(q>0\). Under the multilevel hypotheses,
\[
C_{\rm ML}\le O(n+n^q\log^2n),
\]
so (5.2) closes the “no polynomial advantage” claim for that class. This is weaker than demanding a width-independent floor for every fixed order. It is still an unproved computational assertion; merely calling the state a measure or cumulant sequence does not make it accessible to an information lower bound.

HEURISTIC, cheapest useful test: At widths \(16,32,64,128\), fixed \(L/n\), compare the specified single-Gaussian closure, a small sequence of cumulant orders, and a sequence of gate-split mixture sizes. Measure actual charged work and bias separately from sampling noise. For a deterministic closure output \(a\), independent unbiased reference estimates \(\widehat\mu_1,\widehat\mu_2\) give
\[
\mathbb E[(a-\widehat\mu_1)\cdot(a-\widehat\mu_2)]
=|a-\mu|^2.
\]
This avoids mistaking the reference sampler’s variance for a closure floor. Test input and stationary regimes separately, and report tail contributions. A growing gain after including setup would identify a candidate counterexample algorithm; a flat \(n\,{\rm nMSE}\) curve alone would not prove the conjecture.

**6. Strengthenings and corrections to round 1**

PROVEN: The useful additions from Claude’s v1 are the measure-defect identity, Euler residual decomposition and the frozen/radial comparison. They lead to stronger conclusions than the original numerical discussion: the exact mean-field product formula (2.1), the quartic correction (2.2), the crossover constant, and the finite-width raw cubic coefficient (2.4).

PROVEN UNDER forward-only closures and integrability: Combining the defect identity, kernel discrepancy identity and Minkowski yields the certificate
\[
\sqrt{\mathbb E|\widehat\mu-\mu|^2}
\le
\sqrt{\mathbb E\,{\rm MMD}_{K_L}^2(\nu_0-\gamma)}
+\sum_{\ell=1}^L
\sqrt{\mathbb E\,{\rm MMD}_{K_{L-\ell}}^2
       (\nu_\ell-T_\ell\#\nu_{\ell-1})}.
\tag{6.1}
\]
This supplies a valid aggregate upper bound without pretending that layer defects are orthogonal.

PROVEN UNDER the frozen-radius noisy mean-field approximation: The stationary balance gives
\[
1-\cos\theta
\sim \left(\frac{3\pi}{2\sqrt2\,Q}\right)^{2/3},
\qquad
\theta\sim(3\pi/Q)^{1/3}.
\]
Any round-1 heuristic treating \(2.23Q^{-2/3}\) as the angle should be corrected accordingly.

PROVEN: My round-1 “about \(2pM\)” crossing estimate should be sharpened to \((2p-1)M\). Its two-pass multilevel implementation is valid but unnecessarily restrictive: stopped-radius sums and reference products can be accumulated in one forward pass, with suitable bookkeeping and an extinction convention.

PROVEN: Round-1 multilevel cost calculations establish an attainable upper bound under \(H_{\rm ML}\), not an exact asymptotic value of the best multilevel cost. Any reading of “gain is order \(n/\log^2 n\)” as an optimality theorem should be withdrawn.

CONJECTURE: The remaining gap is unchanged: no proved connection turns trajectory relevance, gate entropy, or a rough gain field into an average-case computational lower bound for integrating readable iid He networks.

PROVEN, verification scope: Read-only checks completed on 2026-11-01 at 21:49 UTC; `FORMAL.md` matches the frozen v1 SHA beginning `dbdcb7f7`. No files were modified.
