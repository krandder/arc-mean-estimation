The major corrections are E12’s random-sign model, E11’s claim that a full joint law is necessary, and E9’s omitted hypotheses. E10’s ideal projection identity survives.

**PROVEN (file audit):** I read the requested files and all 16 specified run files, recomputed summaries in memory, and modified no files. Checked 2026-11-02, 13:11 UTC. Below, “PROVEN (file audit)” describes saved results, not population or asymptotic conclusions.

**1. E10: the projection and Hermite identity**

**PROVEN UNDER exact arithmetic, positive-definite \(S\), and the exact pseudoinverse:** [CondProjector](/home/agent/workspaces/mats/work/future-aware/lib/fa.py:165) implements the stated whitened split.

Write
\[
B=S^{1/2}A,\qquad
\Pi=B(B^\top B)^\dagger B^\top,\qquad
z=S^{-1/2}(h-\mu).
\]
The code’s regression matrix and residual covariance satisfy
\[
S^{-1/2}SA(A^\top SA)^\dagger A^\top S^{1/2}=\Pi,
\]
\[
S^{-1/2}S_{\rm res}S^{-1/2}=I-\Pi.
\]
Consequently,
\[
\boxed{z_Q=\Pi z+\eta,\qquad
\eta\sim N(0,I-\Pi),\quad \eta\perp z.}
\]

The kept subspace in whitened coordinates is \(\operatorname{range}(S^{1/2}A)\). Its dimension is \(\operatorname{rank}(S^{1/2}A)\), which need not equal the requested \(k\).

**Minor — concrete fix:** State those hypotheses and the effective rank. For singular \(S\), work on its covariance support, assuming the target law is supported there. The implemented `pinv(..., rcond=1e-12)`, eigenvalue clipping, and float32 sampling make literal numerical exactness a separate question.

**PROVEN UNDER \(\mu=E_Ph\) and \(S=\operatorname{Cov}_P(h)\):** Both \(P\) and \(Q\), after whitening, have mean zero and covariance identity. Thus every positive-degree normalized Hermite moment through degree two vanishes.

**Major — the experiments do not meet these hypotheses exactly.** In [run_cut.py](/home/agent/workspaces/mats/work/future-aware/scratch/run_cut.py:70), \(\mu\) comes from a finite reference run; \(S\) is estimated from another \(2^{17}\)-sample cloud. The samples supplying retained features come from further batches. E10’s algebraic split still describes the ideal arithmetic of this fitted projector, but exact matching to the population’s first two moments does not follow.

For arbitrary fitted \(\mu,S\), let \(m_z=E_Pz\) and \(C_z=\operatorname{Cov}_Pz\). Then
\[
E_Qz=\Pi m_z,\qquad
\operatorname{Cov}_Qz=\Pi C_z\Pi+I-\Pi.
\]
These generally differ from \(m_z,C_z\).

**Concrete fix:** Separate the population theorem from its fitted implementation. Retain degree-one and degree-two defect terms unless moment-matching discrepancies have been checked.

**PROVEN UNDER the following convergence hypotheses:** Define
\[
\psi_\alpha(z)=\frac{\operatorname{He}_\alpha(z)}{\sqrt{\alpha!}},
\qquad
\widehat g_\alpha=E_\gamma[g\psi_\alpha].
\]
In an orthonormal basis adapted to \(\Pi\), write \(\alpha=(\alpha_1,\alpha_2)\). Then
\[
E_Q\psi_\alpha
=E_P\psi_{\alpha_1}(z_1)\mathbf1_{\{\alpha_2=0\}}.
\]
If the moments are matched,
\[
\boxed{
\int g\,d(Q-P)
=-\sum_{\substack{\alpha_2\ne0\\|\alpha|\ge3}}
\widehat g_\alpha E_P\psi_\alpha.
}
\]

A sufficient condition is
\[
g\in L^2(\gamma;\mathbb R^m),\qquad dP/d\gamma\in L^2(\gamma).
\]
Indeed, \(dQ/d\gamma\) is the Gaussian conditional expectation of \(dP/d\gamma\) onto the retained coordinates, hence also belongs to \(L^2\). Cauchy–Schwarz justifies the coefficient pairing. For polynomial \(g\), finite moments through its degree suffice.

**Major — applicability limitation:** A post-ReLU law generally has positive mass on coordinate faces, so it need not even be absolutely continuous with respect to a nonsingular Gaussian. The stated \(L^2\)-density hypothesis therefore does not justify the infinite expansion for these experiments. E10 acknowledges this formally, but its “exact” interpretation should preserve that limitation.

**Concrete fix:** Use the following series-free identity as the primary theorem:
\[
T_\Pi g(z)=E_\eta g(\Pi z+\eta),\qquad
\boxed{\int g\,d(Q-P)=E_P[(T_\Pi-I)g].}
\]
**PROVEN UNDER integrability:** This holds directly from the sampling construction. The finite ReLU future has linear growth, so finite first moments suffice here. The Hermite formula is its polynomial or justified-series representation.

**Minor — interpretation:** “Removes exactly the modes entirely inside the span” is correct in that representation. It does **not** imply monotone reduction of squared integration error: retained and discarded contributions can previously have cancelled. Also, `sample()`’s comment `base = E[h | a]` should say “Gaussian linear-regression mean”; it is generally not the true cloud’s conditional mean.

**2. E11: what the permutation experiment establishes**

**PROVEN (implementation):** [run_ridge.py](/home/agent/workspaces/mats/work/future-aware/scratch/run_ridge.py:148) independently permutes the columns of the whitened feature batch. Before radial transport:

- Each column’s empirical marginal, mean, and variance is preserved.
- Empirical cross-covariances are changed.
- The regression mean is recomputed from the shuffled features.
- The residual uses the same projector and the same Gaussian noise array as `cond`.

Thus the Gaussian residual is independent of the features in the population construction. The true discarded coordinates and their dependence on the features are absent from **both** reconstructions.

**Minor — covariance wording:** Independent permutations make centered empirical cross-covariances zero **in expectation over permutations**, not identically zero. They do not preserve an arbitrary original empirical covariance. For batch size \(m\), with centered empirical variances \(v_i,v_j\),
\[
\operatorname{Var}_{\rm perm}(\widehat C_{ij})
=\frac{v_iv_j}{m-1}
\]
when covariance uses denominator \(m\). At \(m=32768\), unit-variance columns give standard deviation about \(0.0055\). Whitening was fitted on a separate cloud.

**Concrete fix:** Report first- and second-moment discrepancies and repeat the paired comparison over permutation and sampling seeds. Conditional on the batch, a row averaged over permutations has the product of the empirical marginals; the full shuffled batch is not an IID sample from the population product law.

**PROVEN UNDER ideal population marginals and a fixed Gaussian residual:** Let \(U\) be the retained coordinates and define the smoothed future
\[
\bar g(u)=E_\eta[g(u,\eta)].
\]
The comparison is exactly
\[
E_{P_U}\bar g(U)
\quad\text{versus}\quad
E_{\otimes_jP_{U_j}}\bar g(U).
\]
If
\[
\bar g(u)=c+\sum_{j=1}^k f_j(u_j),
\]
these expectations agree. This is the precise coordinate-additivity hypothesis the experiment addresses.

**Major — E11 overstates the conclusion.** A discrepancy supports dependence-sensitive integration in the **chosen coordinates**, under the regenerated-residual construction. It does not establish that:

- the unsmoothed future is intrinsically \(k\)-dimensional;
- no other ridge basis works;
- the entire joint law must be represented;
- all useful mixed information requires a large representation.

For example, one oblique ridge \(f(a^\top u)\) can be sensitive to coordinate shuffling. A reading depending on one mixed polynomial moment requires that moment, not the whole joint distribution.

**Concrete fix:** Replace the final inference with:

> **HEURISTIC:** In these tested coordinates, replacing the retained joint distribution by its coordinate marginals loses most of the joint-marginal projector’s accuracy. Some dependence information is useful. The necessary representation and its dimension remain unresolved.

**Major — the radial comparison does not preserve the tested marginals.** `radius_scale` rescales the **whole** sample. Consequently `rridge` changes the feature marginals and reintroduces dependence. It cannot cleanly identify information “beyond the shared radius.”

**Concrete fix:** Treat radial transport as a separate intervention. Do not apply E10’s feature-exact theorem to `radg`, `rridge`, or `rcond`.

**PROVEN (file audit):** The eight evaluation networks give these medians of raw, signed `b2`; no negative estimates were clipped:

| Cut | Gaussian | Joint \(k=16\) | Shuffled \(k=16\) | Joint \(k=32\) | Shuffled \(k=32\) |
|---:|---:|---:|---:|---:|---:|
| 1 | \(4.10\,10^{-4}\) | \(7.66\,10^{-5}\) | \(3.20\,10^{-4}\) | \(1.54\,10^{-5}\) | \(3.30\,10^{-4}\) |
| 2 | \(7.31\,10^{-4}\) | \(9.16\,10^{-5}\) | \(5.98\,10^{-4}\) | \(7.97\,10^{-6}\) | \(6.09\,10^{-4}\) |
| 4 | \(6.93\,10^{-4}\) | \(5.45\,10^{-5}\) | \(5.27\,10^{-4}\) | \(2.52\,10^{-6}\) | \(5.36\,10^{-4}\) |
| 6 | \(5.21\,10^{-4}\) | \(2.92\,10^{-5}\) | \(3.80\,10^{-4}\) | \(1.61\,10^{-6}\) | \(3.81\,10^{-4}\) |

`cond` has lower saved error than `ridge` in all 32 seed/cut cells at both values of \(k\). However:

- Median `ridge16/gauss` is \(0.724\): the coordinate marginals retain a measurable benefit.
- Median `rridge16/radg` is \(0.825\), and `rridge16` is lower in 28/32 cells.
- Median `ridge32/ridge16` is \(1.003\), supporting the reported plateau.
- Common variants in the cut and ridge files are numerically identical. They are not independent replications.

**HEURISTIC:** These results strongly support withdrawing the specific coordinate-additive interpretation. They support a narrower claim than “one-dimensional laws carry almost nothing” or “a genuinely \(k\)-dimensional law is necessary.”

**3. E12: random-sign pricing**

**Major — independence of the signs from \(V\) alone is insufficient.**

**PROVEN:** To discard cross terms, the relevant condition is conditional orthogonality of the moments **after conditioning on the future coefficients, selected frame, and magnitudes**. Independent signs that also affect \(\widehat g_\alpha\) need not eliminate cross terms.

Moreover, independence in one Hermite basis does not survive a rotation. An adapted-basis sign model is a substantive additional hypothesis.

**PROVEN (implementation):** The parenthetical claim that `futnl` uses only the future and the cloud’s first two moments is false. [run_cut.py](/home/agent/workspaces/mats/work/future-aware/scratch/run_cut.py:77) evaluates Jacobians on true cloud samples and estimates their mean on another true sample cloud. Gate statistics depend on higher distributional structure.

`futv` and `futmf2` use Gaussian-state or moment-based approximations, but that does not prove independent symmetric signs for the true higher Hermite moments.

**Concrete fix:** Delete “true when … as … essentially are.” State conditional moment assumptions explicitly and label their applicability to the implemented networks **CONJECTURE**, or simply unestablished.

**Major — the Hadamard tensor is basis-dependent.**

**PROVEN:** In one fixed adapted frame, “\(\alpha\) entirely inside \(V\)” is exactly the projection \(P_V^{\otimes d}\) on the degree-\(d\) symmetric tensor space. That identification is sound.

However, coefficientwise multiplication of the future coefficients and cloud moment magnitudes is not equivariant under rotations. Generally,
\[
\mathcal R_d(a\odot b)
\ne(\mathcal R_da)\odot(\mathcal R_db).
\]
Thus a tensor constructed by multiplying coefficients in a fixed reference frame cannot be silently reused after rotating to the \(V\)-adapted frame.

**PROVEN — counterexample to that interpretation:** Take \(n=2,d=3\),
\[
v=(e_1+e_2)/\sqrt2,\qquad V=\operatorname{span}(v),\qquad G=v^{\otimes3},
\]
and random cloud moment tensor
\[
M=\varepsilon_1e_1^{\otimes3}+\varepsilon_2e_2^{\otimes3},
\]
with independent symmetric signs. The signs are independent of the fixed future and \(V\).

The cubic future lies entirely in \(V\), so its conditional projection defect is identically zero. But the reference-frame coefficient-product tensor is
\[
H=\frac{e_1^{\otimes3}+e_2^{\otimes3}}{2\sqrt2},
\qquad
\|H\|_F^2=\frac14,\qquad r_\infty(H)=2.
\]
Applying the proposed bound to this fixed \(H\) gives
\[
E|D_V|^2\ge(1-1/2)\frac14=\frac18,
\]
contradicting zero.

This does not contradict a correctly stipulated adapted-frame sign theorem: the transformed moment coordinates in this example no longer have independent signs.

**Major — normalization must be specified.**

**PROVEN:** For \(|\alpha|=d\), let
\[
E_\alpha=\sqrt{\frac{d!}{\alpha!}}\,
\operatorname{Sym}(e_1^{\otimes\alpha_1}\otimes\cdots\otimes e_n^{\otimes\alpha_n}),
\]
where `Sym` averages over permutations. These tensors are orthonormal.

The correctly normalized coefficient-product tensor is
\[
H_d=\sum_{|\alpha|=d}\widehat g_\alpha\mu_\alpha E_\alpha.
\]
Its ordered-index entry for a tuple with multiplicities \(\alpha\) is
\[
(H_d)_{i_1\ldots i_d}
=\sqrt{\frac{\alpha!}{d!}}\widehat g_\alpha\mu_\alpha.
\]
Therefore
\[
\|H_d\|_F^2=\sum_{|\alpha|=d}\|\widehat g_\alpha\|^2\mu_\alpha^2.
\]

An ordinary entrywise product of two full normalized tensors has different multiplicity factors.

**Concrete fix:** Define \(H_d\) by the orthonormal symmetric-tensor basis. For vector output, flatten **one input index** against all other input indices and the output index.

**PROVEN:** My round-1 flattening inequality applies to every such correctly defined tensor. Its application does not require \(H_d\) itself to be a physical moment tensor:
\[
\|P_V^{\otimes d}H_d\|_F^2
\le\operatorname{tr}(P_VA_d)
\le\sum_{i=1}^k\lambda_i(A_d),
\qquad A_d=H_{d,(1)}H_{d,(1)}^\top.
\]
The problem is identifying the appropriate \(H_d\), not the flattening inequality.

A correct local repair is:

**PROVEN UNDER a selected adapted frame, conditional diagonal second moments, and justified convergence:** Condition on a sigma-algebra \(\mathcal F\) fixing \(g,V\), the adapted frame, and \(\mu_\alpha\). Assume
\[
E[h_\alpha\mid\mathcal F]=0,\qquad
E[h_\alpha h_\beta\mid\mathcal F]
=\delta_{\alpha\beta}\mu_\alpha^2
\]
for all relevant degrees \(\ge3\). Independent conditional Rademacher signs suffice but are stronger than necessary. For polynomial readings, or a justified infinite expansion,
\[
E[\|D_V\|^2\mid\mathcal F]
=\sum_d\bigl(\|H_{d,V}\|_F^2-\|P_V^{\otimes d}H_{d,V}\|_F^2\bigr).
\]
Hence, writing \(e_d=\|H_{d,V}\|_F^2\),
\[
\boxed{
E[\|D_V\|^2\mid\mathcal F]
\ge\sum_d e_d\left(1-\min\{1,k/r_\infty(H_{d,V})\}\right).
}
\]
The subscript \(V\) matters: this construction does not supply one common tensor family for comparisons across arbitrary frames.

**Minor — concrete fix:** Ignore zero tensors, use an infimum over infinitely many degrees, truncate lower bounds at zero, and state \(k<r\) before asserting the improvement-factor bound \(1/(1-k/r)\).

A stronger, basis-independent formulation is available:

**PROVEN UNDER a conditional coefficient-covariance model:** Let \(M_d\in\operatorname{Sym}^d(\mathbb R^n)\) denote the normalized cloud moment tensor, \(G_d\) the future’s coefficient map to the output, and \(\Pi_d=P_V^{\otimes d}\). Assume the centered \(M_d\) are conditionally uncorrelated across degrees, with covariance operators \(C_d\). Then
\[
\boxed{
E[\|D_V\|^2\mid\mathcal F]
=\sum_d\operatorname{tr}
\!\left[G_d(I-\Pi_d)C_d(I-\Pi_d)G_d^\ast\right].
}
\]
Nonzero conditional means and cross-degree covariances contribute their corresponding additional terms. This formula does not require diagonal covariance in the adapted frame.

If \(C_d\) commutes with \(\Pi_d\), a removed-energy identity follows using the coefficient tensor of \(G_dC_d^{1/2}\). Without commutation, the proposed norm-difference formula generally fails.

**PROVEN UNDER conditionally isotropic moment covariance:** A particularly clean sufficient assumption is
\[
C_d=\sigma_d^2I.
\]
This requires isotropic second moments, not a rotation-invariant full distribution. Then
\[
E[\|D_V\|^2\mid\mathcal F]
=\sum_d\sigma_d^2
\left(\|G_d\|_F^2-\|P_V^{\otimes d}G_d\|_F^2\right).
\]
Define the aggregate input-mode Gram matrix
\[
A_*=\sum_d\sigma_d^2G_{d,(1)}G_{d,(1)}^\top,
\qquad B_0=\operatorname{tr}A_*.
\]
For any \(\mathcal F\)-measurable rank-\(k\) choice,
\[
\boxed{
E[\|D_V\|^2\mid\mathcal F]
\ge B_0-\sum_{i=1}^k\lambda_i(A_*)
\ge
\left(1-\frac{k\|A_*\|_{\rm op}}{B_0}\right)_+B_0.
}
\]
This avoids the weakest-degree bottleneck and allows future-selected spans under explicit conditional assumptions.

**CONJECTURE:** Those covariance assumptions describe the actual non-Gaussian clouds sufficiently well to price these experiments. Neither the files nor the earlier answers establish that. Arbitrary signed coefficient models also require a realizability argument before being interpreted as probability laws.

**4. E9: fidelity to round 2**

| Claim | Status and severity | Concrete fix |
|---|---|---|
| \(\sup_K C_Ke_K<\infty\) is the exact rate criterion | **PROVEN UNDER bounded adjacent-cost spacing; minor omission.** Without it, this controls listed budget points but need not give an \(O(C^{-1})\) envelope at intervening budgets. | Restore the geometric-ladder/bounded-spacing qualification from round 2. |
| Per-step efficiency improves iff \(e_K/e_{K+1}>C_{K+1}/C_K\) | **PROVEN.** Faithful. | Specify positive errors and fully charged costs. |
| Contractible-diagram cost bound | **PROVEN UNDER the stated diagram hypothesis.** Faithful, including the admission that ARC’s complete update was not checked. | Preserve fixed-\(K\) constants, diagram counts, integration costs, and feature-construction costs. |
| Registered cost is a proven optimistic bound | **HEURISTIC; major if promoted to a guarantee.** Being smaller than one sufficient implementation upper bound does not make it a lower bound on every implementation. | Call it the preregistered hypothetical cost model. |
| Formula converting retained improvement \(R\) into \(q_{3,\mathrm{proj}}\) | **PROVEN.** Faithful; the numerical examples agree. | Apply the same distinction consistently in E8. |
| \(r_{\rm PR}(N_t)=\Theta(n)\) at \(t=\beta n\) | **PROVEN UNDER the homogeneous independent-gate Gaussian recursion, in probability.** | Write \(\Theta_{\mathbb P}(n)\), with the confidence-dependent interpretation from round 2. |
| Limit fraction \(3/7\) follows from that same theorem | **Major misrepresentation.** Round 2 separately assumed diagonal flattening and joint trace concentration, uniformly through the relevant depths. | Separate the finite-width rank-order theorem from the conditional limiting-constant calculation. |
| Rank-\(k\) capture is at most \(\sqrt{k/r_{\rm PR}}\) | **PROVEN.** Faithful for PSD derivative-energy matrices. | Preserve the distinction from closure-error capture. |
| Lipschitz/PWL worst-case obstruction | **PROVEN in the specified oracle/universal-law model.** Faithful. | Preserve absolute versus squared error and the explicit-weight limitation. |
| Owen gain-coefficient formula | **PROVEN UNDER the scrambling hypotheses; minor omission.** Round 2 explicitly specified nested uniform scrambling of a digital net. | Restore that hypothesis or verify the corresponding identity for the implemented scramble. |
| Strong negative exponent conclusion | **PROVEN UNDER uniform cost and error laws.** Broadly faithful. | State the uniform lower error law and fully charged geometric cost law; finite-order data do not establish them. |
| Cheap correction with \(e_n=o(1/n)\) | **CONJECTURE** for existence; **PROVEN UNDER \(C_n=O(n)\)** for growing MC advantage. Faithful. | Testing the error scaling alone does not test the required implementation cost. |

**5. Other inconsistencies and qualifications in E1–E12**

**Major — E1’s blanket acceptance of section 3 is too broad.**  
**PROVEN:** Round 1 explicitly restricted its sharp information bound to a fixed past-measurable defect and an interface-measurable additive correction. It did not prove that bound for every interface-dependent reconstruction. E1 correctly states the restricted formula, but “Section 3 … PROVEN as written” also endorses the broader original consequence.

**Concrete fix:** Accept the conditional kernel identity and the restricted fixed-defect theorem separately. Define \(P=VV^\top\) locally; the original section 3 used \(P\) for the complementary projector.

**Major — E4 still conflates several spectra.**  
**PROVEN:** Participation ratio does not imply the operator-norm stable-rank bound used in E12. Also, subtracting the mean Jacobian removes linear Gaussian chaos under a Gaussian reference, while the residual derivative energy still includes quadratic chaos. A mean-and-covariance-matched integration defect cancels quadratic readings as well. On a non-Gaussian cloud, that Gaussian-chaos identification needs further justification.

**Concrete fix:** Keep E4’s closure-error conclusion **HEURISTIC**. Use the proven participation-ratio capture bound for the specified gate model, and do not substitute its matrix for the future-times-cloud tensors without another theorem.

**Major — E7 asserts an unsupported universal cubic cost lower bound.**  
**PROVEN UNDER \(C_n\ge cn\) and bounded RQMC gain:** A growing multiplicative budget window requires \(e_n=o(1/n)\). But carrying covariance-level information does not by itself prove every algorithm must perform schoolbook cubic matrix multiplication.

**Concrete fix:** State the result for implementations with the charged cost \(C_n=\Omega(n)\). The general criterion is \(G_nC_ne_n\to0\).

**Major — E8 switches meanings of “retained gain.”**  
**PROVEN (file audit):** On its quoted development network,
\[
e_3=9.5467\,10^{-4},\quad e_4=2.5931\,10^{-5}.
\]
Projecting both cores gives:

| \(k\) | Projected error | Fraction of absolute \(e_3-e_4\) improvement retained | Fraction of full multiplicative factor retained |
|---:|---:|---:|---:|
| 8 | \(5.5533\,10^{-4}\) | \(0.430\) | \(0.0467\) |
| 16 | \(1.0392\,10^{-4}\) | \(0.916\) | \(0.2495\) |

Thus “almost nothing” and “a quarter” refer to multiplicative-factor retention. They are incompatible with E9’s definition of retained absolute improvement if presented as the same quantity.

**Concrete fix:** Print both metrics. The separate-order runs support sensitivity to third-cumulant truncation at higher target precision. “Nearly all directions are necessary” and “this is the mechanism by which truncation fails to change the ladder” remain **HEURISTIC**, not consequences of these few \(k\)-values and widths.

**Minor — E6’s original gain relation should be superseded explicitly.**  
**PROVEN:** If \(\eta\) is the ordinary residual variance ratio and \(\rho\) the RQMC variance ratio, then
\[
G_R/G=\eta/\rho.
\]
When \(\rho\approx1\), this gives \(G_R\approx\eta G\), not automatically \(G_R\approx1\). E9’s corrected identity is the appropriate replacement.

**Minor — E10/E12’s share-law fit needs its filtering stated.**  
**PROVEN (file audit):** There are 384 nominal `cond` cells, but five have nonpositive `b2`. Using the remaining 379,
\[
x=-\log(1-s),\qquad y=\log(b^2_{\rm gauss}/b^2_{\rm cond}),
\]
gives correlation \(0.95949\), slope \(1.18898\) with intercept \(-0.09697\), or slope \(1.15469\) when forced through zero.

**Concrete fix:** State the filtering and fit convention. The correlation is reproducible; its proposed ridge mechanism or identification \(s\sim k/r\) remains **HEURISTIC**. The cells also share networks and baselines.

**Major at high precision — `b2` is not unconditionally unbiased for the ideal population defect.**  
**PROVEN:** Conditional on fitted setup and stored reference \(\widehat Y,\widehat V\), independent halves estimate
\[
E[b2\mid\text{setup}]
=\frac{\|E[\widehat Y_{\rm model}\mid\text{setup}]-\widehat Y\|^2}{\widehat V}.
\]
This differs from an ideal population-projector defect. The reference mean also contributes to fitting, so a simple independent-reference correction is not automatically exact.

**PROVEN (file audit):** Three of the 32 `cond_futnl32` estimates are negative. The recorded `noise` is a half-difference statistic, not a standard error for `b2`.

**Concrete fix:** Label the estimator’s conditional target, retain signed estimates, and use independent reference/replicate error analysis before interpreting tiny errors or their ratios.

**HEURISTIC — E2’s development trends remain evidence, not necessity or width laws.** Its principal quoted development values are consistent with the files checked. Additional evaluation results do not establish the positive scaling conjecture.

**PROVEN (file audit):** At \(k=n/4\), median \(n e_n\) for projected `futv` order three is approximately
\[
0.0336,\quad0.0402,\quad0.0684
\]
at widths \(64,128,256\); for `futmf2` it is
\[
0.0378,\quad0.0392,\quad0.0569.
\]
These finite-width results do not show the required decreasing trend. Several \(k=n/2\) future-feature runs also contain NaNs, so successful rank handling cannot be assumed uniformly.

**Concrete fix:** Preserve the development/evaluation distinction, report failed runs, and keep the all-width and all-representation claims **CONJECTURE**.
