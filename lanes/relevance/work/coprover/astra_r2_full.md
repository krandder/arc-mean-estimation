**PROVEN:** the population projection bounds survive, but the proposed generic-capture argument does not establish the M1 conclusion. The most consequential implementation errors are the noisy gate subtraction, uncertified eigenvalue “debiasing,” and omission of Part 2’s uncertainty rule.

**NUMERICAL:** checked against the directory snapshot at **2026-11-01 21:58 UTC**. Neither score JSON nor any `runs/p2_*.json` existed then. The frozen hashes match; `accounting.py` differs only by the disclosed `cloud_evals_perp` addition. Existing tests pass. No files were changed.

**T1. Theory audit**

References below are to [FORMAL.md](/home/agent/workspaces/mats/work/relevance/FORMAL.md).

1. **PROVEN UNDER the stated independent Gaussian-weight model:** Theorem 1, lines 9–18, is correct. Condition on the past, choose its measurable frame, and use right-orthogonal invariance of \(M\). It requires independence of future noise from the weights and past. Its \(m\ne0\) assumption excludes the exact input cloud at \(l=0\); there the appropriate invariance is full \(O(n)\).

2. **PROVEN:** Corollary 1a is false for “any functional.” A functional depending only on a particular covariance entry supplies a counterexample. Require simultaneous rotation invariance:
   \[
   \Phi(R_\#\mu,F)=\Phi(\mu,F\circ R).
   \]
   Natural basis-free relevance quantities satisfy this.

   Its list of Gaussian orbit invariants is also incomplete. Writing the covariance in radial/angular blocks as
   \[
   \begin{pmatrix}a&b^\top\\b&C\end{pmatrix},
   \]
   one needs the position of \(b\) relative to the eigenspaces of \(C\), equivalently its spectral measure \(b^\top f(C)b\). The norm of \(b\) and spectrum of \(C\) alone are insufficient.

3. **PROVEN:** Corollary 1b’s displayed conditional expectation has a random right-hand side. The correction is
   \[
   \mathbb E[\|Ju\|^2\mid\mathcal F_l,\mathcal G]
   =\frac{\mathbb E[\|JB\|_F^2\mid\mathcal F_l,\mathcal G]}{n-1}
   =\frac2n\|K\|_F^2.
   \]
   Alternatively, additionally condition on the angular singular values. The singular frame is Haar with the usual qualifications about signs and degenerate eigenspaces.

   **PROVEN UNDER nondegenerate two-sided Oseledets hypotheses:** the distinction between past Gram–Schmidt vectors and future-dependent covariant vectors is appropriate. Equal amplification in expectation does not imply equal amplification in one realization.

4. **PROVEN UNDER an independently Haar-oriented angular operator:** the finite-dimensional random-congruence model in Corollary 1c is valid for that operator. Extending it to the cloud-averaged Jacobian remains **HEURISTIC**. Radial/angular cross-covariance must also be handled before identifying an angular block of the whitened relevance matrix.

   **PROVEN:** asymptotic freeness describes the bulk spectral law under appropriate convergence assumptions; it does not establish the claimed top-eigenvalue approximation. Take \(S=I\) and nonconstant \(\Lambda\): the product’s eigenvalues are those of \(\Lambda\), not all \(\operatorname{tr}\Lambda/(n-1)\). The stated fluctuation estimate concerns a random quadratic form, not general product eigenvalues. A low-rank backward subspace with concentrated compressed covariance would justify a restricted approximation.

5. **PROVEN UNDER Gaussian input and square-integrable weak gradients:** Section 2’s Mehler, Stein, and gradient-energy identities are correct, interpreting covariance as its trace and using \(V^\gamma_l\) consistently.

   **PROVEN:** the frozen-linear variance formula needs a noise convention. For the noise-averaged attribution, the relevant matrix is \(\mathbb E_\Xi J^m_\Xi\); averaging \(\operatorname{tr}(J^m_\Xi\Sigma J^{m\top}_\Xi)\) instead includes future-noise variation. The frozen-at-mean comparison with \(DV\) remains **HEURISTIC**.

6. **PROVEN UNDER a fixed-depth concentrating-kernel limit:** Section 3a’s noiseless kernel calculation is correct. “Norms concentrate” alone does not ensure the stated deterministic cosine. One also needs concentration of inner products and mean–fluctuation cross terms; sufficient conditions involve
   \[
   \frac{\operatorname{tr}\Sigma^2}{(\|m\|^2+\operatorname{tr}\Sigma)^2}\to0,
   \qquad
   \frac{m^\top\Sigma m}{(\|m\|^2+\operatorname{tr}\Sigma)^2}\to0.
   \]
   These assumptions are restrictive for a strongly anisotropic cloud.

   **PROVEN UNDER the displayed continuum small-angle overlap law:** \(s_1=(1+x)^{-1}\) and \(D=(1+x)^2\) follow. They are asymptotic model identities, not exact finite-angle, discrete-depth identities.

7. **PROVEN:** Section 3a’s stationary conclusion “\(s_1\ge0.9\) at every \(t\)” does not follow and conflicts with the later angular-sector limit. The independent-noise recursion is the appropriate model, but its long-time normalized shape need not become linear. The \(0.715,0.179,1.5\) limits require the frozen-\(Q\), large-\(Q\) continuum assumptions from round 1.

8. **PROVEN:** Section 3b incorrectly turns positive homogeneity into first Gaussian chaos. Homogeneity holds for positive scaling; a homogeneous nonlinear function can have substantial higher chaos. Radius \(\|X\|\) is not a linear Gaussian coordinate. Exact linear radial dependence holds on a fixed positive ray; a thin cloud permits a local approximation using \(e^\top X\).

   **PROVEN:** \(\mathbb E\log A=-5/(2n)\) is not an exact finite-width identity. For a noiseless layer, \(A=0\) has probability \(2^{-n}\), so its unconditional logarithmic expectation is \(-\infty\). The quoted value is a large-width expansion ignoring extinction. Its use for stationary response remains **HEURISTIC**.

9. **PROVEN:** Section 3c’s \(B(c)\), including \(B(1)=5\) and \(B(0)=0\), is the correct covariance coefficient for squared gains. Turning it into a log-amplitude covariance uses an expansion; the additive decomposition
   \(K_{\rm dir}+K_{\rm amp}+K_{\rm rad}\) requires neglected cross terms and normalization corrections.

   **PROVEN:** if \(c_0\) denotes the initial correlation, the gain sum uses \(j=0,\ldots,t-1\). The code uses this indexing; the displayed \(j=1,\ldots,t\) needs correction or an explicit shifted definition.

10. **PROVEN:** Section 4b does not follow from Theorem 1. Rotational invariance of a tensor’s law does not determine its covariance across trace and traceless components, nor make its coefficients uniformly distributed over symmetric tensors.

    For isotropic clouds, three examples already differ:

    - \(H=I\): degree-2 capture is \(k/r\).
    - One Haar-oriented rank-one \(H=uu^\top\): expected capture by a fixed \(P\) is \(k(k+2)/(r(r+2))\), while a future-informed rank-one \(P\) captures everything.
    - Isotropic coefficients in the full symmetric-matrix space: the \(h_2\) model gives \(k(k+1)/(r(r+1))\).

    Thus neither the \(h_d\) formula nor optimality of cloud PCA follows from Haar orientation alone.

11. **PROVEN:** Section 4c combines captures achievable in different subspaces without demonstrating a common \(k\)-dimensional subspace. Optimizing each chaos separately can produce an unattainable combined capture. Reserving the union of the required subspaces gives a legitimate upper-bound construction, with its actual dimension charged.

    **PROVEN:** \(s_{\ge2}>\varepsilon\) alone implies no large-dimensional lower bound. A high-degree ridge function needs one direction. Conversely, when nonlinear variance is negligible, the first-chaos tolerance is approximately \(\varepsilon/s_1\), measured against \(V_1\).

12. **PROVEN:** Section 4d establishes \(N_{\rm sc}\le1\) when \(s_{\ge2}\le\varepsilon\), for a nonzero first-chaos component. Its “forward-limited otherwise” conclusion is unsupported. Also, \(N_1=1\) requires nonzero first chaos; it is zero when that component vanishes.

13. **PROVEN UNDER the Gaussian convention:** v2.1’s population first-chaos lower bound and conditional Poincaré upper bound are correct. Its numerical eigenvalue correction does not provide a rigorous lower bound; see T4.

    **PROVEN:** \(n/P\) is approximately the noise-trace fraction relative to \(V\), not generally \(V_1\). Relative to \(V_1\), the corresponding approximation is \(n/(Ps_1)\). At ARC input, \(s_1\approx0.294\), so this distinction is substantial.

14. **PROVEN:** v2.2 should not describe the channel totals as exact facts about the Gaussian-convention network. The total true-law noiseless variance is independent of the cut; Gaussianization at different cuts need not preserve it. The displayed channel decomposition is an approximation with nonorthogonal components.

    At \(l=0\), \(m=0\), and input-radius variation is principally degree two under the Gaussian input, not a radial linear coordinate. The \((1/2)/n\) radius term itself is an asymptotic chi-radius calculation. Downgrade the network claim to **HEURISTIC**, retaining exact identities only inside an explicitly specified surrogate.

15. **PROVEN UNDER noiseless future, independent fresh weights, and differentiability:** v2.3’s annealed criticality identity is correct. Its consequence is
    \[
    \frac{\mathbb E_W J(1)}{\mathbb E_W V},
    \]
    a variance-weighted annealed mean degree, not \(\mathbb E_W[J(1)/V]\), and not an exact quenched formula. The claim “every fixed \(x,v\)” needs an exception at nondifferentiable \(x=0\).

    **PROVEN UNDER the stated kernel singularity:** the \(d^{-5/2}\) tail envelope explains slow convergence of the truncated derivative sum. It does not repair the missing tail in the count predictions automatically.

16. **PROVEN:** v2.4 contains two separate errors. Wick’s identity gives
    \[
    \frac{\mathbb E(a^\top Pa)^2}{\mathbb E(a^\top a)^2}
    =
    \frac{(\operatorname{tr}\Sigma_P)^2+2\operatorname{tr}\Sigma_P^2}
         {(\operatorname{tr}\Sigma)^2+2\operatorname{tr}\Sigma^2},
    \]
    but
    \[
    h_2(\lambda)=\tfrac12\big[(\operatorname{tr}\Sigma)^2+
                                  \operatorname{tr}\Sigma^2\big].
    \]
    These ratios are different.

    Moreover, a ReLU gate with preactivation \(b+a^\top Z\), \(s=\|a\|\), has second-chaos matrix
    \[
    H=\frac{\phi(b/s)}s\,aa^\top.
    \]
    The coefficient depends on the normal and cannot generally be discarded when averaging energies. For a transverse-only normal, its covariance also needs the transverse projector rather than unrestricted \(\Sigma\).

17. **NUMERICAL:** v2.5 overstates the current stationary measurements; see T6. Its angular limiting constants are **PROVEN UNDER the frozen-radius continuum model**, while identifying and assigning an exponent to the full slow mode remains **CONJECTURE**.

18. **PROVEN:** v2.6’s probability \(n2^{-n}\) concerns a single fixed nonzero input. A single-active-unit mean trajectory does not prove the whole cloud passes through that same bottleneck. The proposed finite-width Lyapunov gap needs an additional hypothesis.

    **NUMERICAL:** “exact to \(10^{-6}\ldots10^{-29}\) on all six nets by \(l=32\)” is inaccurate. The true-law radial residual ratios at \(l=32\) include \(8.63\times10^{-6}\), \(2.25\times10^{-6}\), and \(1.87\times10^{-6}\). Earlier exact-synchronization claims are also too strong.

19. **HEURISTIC:** v2.7 improves a surrogate but still assumes alignment of amplitude/radial output directions and compatibility of their input directions with the angular subspace. The implementation allocates \(k-1\) directions to angular first chaos but \(k\) to angular higher chaos without exhibiting their common subspace.

    **PROVEN UNDER an exactly one-coordinate slow response and a two-exponential variance decomposition:** v2.8’s threshold follows. Without that one-coordinate hypothesis, an irreducible slow-response residual remains; see T6.

**T2. Measurement estimators**

References: [rel.py](/home/agent/workspaces/mats/work/relevance/lib/rel.py), [accounting.py](/home/agent/workspaces/mats/work/relevance/lib/accounting.py), [gates.py](/home/agent/workspaces/mats/work/relevance/lib/gates.py).

- **PROVEN:** `pair_sq`, `v_l`, Gaussian pick-freeze residuals, and `total_var` use the correct noise sharing and factors. Shared noise *within* each difference reduces variance; independent noise *between* the two differences removes future-noise variance. Gaussian residuals require the factor \(1/2\); the true-law plug-in prediction error correctly does not.

- **PROVEN:** `ustat_sq` is unbiased for iid **uncentered or independently centered** rows. All important callers instead subtract the same sample mean. For Gaussian \(Z\), with \(P\) iid rows, its expectation is exactly
  \[
  \mathbb E\widehat V_1
  =\left(1-\frac2P+\frac{2}{P^2}\right)V_1.
  \]
  Thus “unbiased” is false as implemented, although the bias is small at these sample sizes. Divide by that factor or use independent centering.

  **NUMERICAL:** a scalar linear check at \(P=16\) gave \(0.88357\pm0.00194\), against the exact factor \(0.8828125\).

  **PROVEN:** the jackknife leaves the original centering fixed rather than redoing the complete statistic. It is not an exact uncertainty calculation for the implemented estimator. It is an asymptotic approximation away from degenerate first chaos. The block divisibility requirement happens to hold for the registered sample sizes.

- **PROVEN:** `mehler_curve` correctly estimates \(D(\rho)=V-K(\rho)\), not \(K(\rho)\). The negative-\(\rho\) construction is valid. The measurements called “Stein” use output–input moments, not averaged gradients; equivalence holds under the Gaussian convention.

- **PROVEN:** vector and scalar active-subspace matrices have the correct normalization. The common output cotangent and independent future-noise pair correctly estimate the product of noise-averaged Jacobians. Their finite-sample matrices can be indefinite; sampled eigenvalue tails are not certified Poincaré bounds.

- **PROVEN:** Gaussian residual evaluations are independent of their learned candidate bases. Most true-law projection evaluations also use held-out cloud samples. However, `res_ASt_true` learns and evaluates its basis on the same `Xe`; it is an in-sample diagnostic.

  The reconstruction is a valid predictor from the chosen linear feature, so its population MSE upper-bounds the optimal true-law residual. It need not equal that residual.

- **PROVEN:** the implementation measures a fitted Gaussian cloud, not the Gaussian with exact population moments. Report covariance-fitting and burn-in uncertainty separately. At \(l=0\), the sample mean invents an arbitrary “radial” direction although the exact mean is zero. `res_radial_*` measures the linear feature \(e^\top X\), not \(\|X\|\). `AS1_radial_overlap` stores the **squared** overlap.

  **PROVEN:** `mean_gap_nmse` has positive sampling bias from both estimated means, especially with noisy future outputs.

- **PROVEN:** the pathwise decomposition and first-order hinge recursion are correct. `parts_shares` is biased by its covariance normalization. For one component with noise-averaged variance \(V_f\) and conditional-noise variance
  \(W_f=\mathbb E_X\operatorname{Var}_\Xi f(X,\Xi)\),
  \[
  \mathbb E\widehat V_f
  =(1-1/P)V_f-\frac{W_f}{2P}
  \quad(\sigma>0).
  \]
  For \(\sigma=0\), the factor is simply \(1-1/P\). Use cross-realization sample covariance,
  \[
  \frac1{P-1}\sum_i(f_{i1}-\bar f_1)^\top(f_{i2}-\bar f_2).
  \]

- **PROVEN:** the mixed gate pass implements Part 2’s switched-versus-frozen network. It includes interactions among selected gates; it is not the first-order sum of single-gate hinges originally described in DEFINITIONS.

  The registered importance \(s^2\psi(\tau)\) is an uncentered hinge second moment. The hinge variance subtracts its squared mean; its degree-\(\ge2\) variance additionally subtracts its first-chaos energy:
  \[
  s^2\left[
    \psi(\tau)-(\phi(\tau)-\tau\bar\Phi(\tau))^2-\bar\Phi(\tau)^2
  \right].
  \]
  The code matches Part 2’s explicit importance formula, but not the original “own variance” definition.

- **PROVEN:** the noisy gate estimator has a persistent subtraction error. Let \(d_\xi=g_{\rm full,\xi}-g_{G,\xi}\) and \(B_\xi=\mathbb E_Z[d_\xi Z^\top]\). Its variance term uses cross-realization covariance correctly. Its first-chaos subtraction uses the average of two realizations, however:
  \[
  \mathbb E\left\|\frac{B_\xi+B_{\xi'}}2\right\|_F^2
  =
  \|\mathbb E B_\xi\|_F^2+
  \frac12\mathbb E\|B_\xi-\mathbb E B_\xi\|_F^2.
  \]
  Consequently the reported nonlinear residual is biased **downward**, even as \(P\to\infty\).

  Replace it with a cross-realization U-statistic, for independently centered \(d_1,d_2\):
  \[
  \frac{
  \langle d_1^\top Z,d_2^\top Z\rangle_F
  -\sum_i(d_{1i}^\top d_{2i})\|Z_i\|^2
  }{P(P-1)}.
  \]
  This targets the cross first-chaos product.

  **PROVEN:** two noise realizations shared across all \(P\) inputs do not provide \(P\) independent future-noise replicates. Uncertainty must include the outer noise dimension. Realizations beyond the first two are currently ignored by the subtraction calculation.

- **PROVEN:** gate ranking also uses spreads estimated from the evaluation inputs themselves. That makes the selected mixed map data-dependent. Compute those spreads analytically from the frame or on independent training inputs. Interactions can make the gate-residual curve nonmonotone; the first successful geometric-grid point is only a tested count, not a bracket on the minimum over all counts.

- **PROVEN:** the nonlinear active-subspace population identity
  \[
  R_{\ge2}(P)=R_{\rm total}(P)-\|B(I-P)\|_F^2
  \]
  is correct. Its implementation uses training-sample \(V_1\) and a different holdout sample for captured first chaos. At \(k=n\), their difference can remain nonzero even though the true residual is exactly zero. Estimate the entire first-chaos complement directly on the same holdout sample.

  The learned nonlinear matrix also includes error from estimating \(B\); it is not an unbiased estimate of the ideal nonlinear active-subspace matrix. It can still propose a basis, provided evaluation is independent.

  **PROVEN:** the required residual standard errors are discarded, so the registered “residual \(+2\,\mathrm{SE}\)” decision cannot be reconstructed.

- **PROVEN:** `n1_split` correctly separates basis training from evaluation and avoids evaluating captured energy on the training basis sample. Its centering retains the small bias above. It estimates residuals for a learned basis; neither the thresholded count nor the population optimal \(N_1\) is an “unbiased count.”

**T3. Scoring and independent recomputation**

**PROVEN:** [score_part1.py](/home/agent/workspaces/mats/work/relevance/scratch/score_part1.py) implements the advertised numerical bands for P1–P8 substantially as written, including the interval-intersection rule for P7/P8. It does not implement a complete, uncertainty-certified preregistration:

- `n1_meas` stores only 96 eigenvalues and returns 96 even when the target was not reached. Such cases need a censored result.
- The global “unresolved cells are not scored” rule is not applied to P9a–d, P10, and P11a. If intended as exceptions, state that explicitly.
- P9 net-level conclusions do not check that all registered layers and nets are present. A partially completed net can satisfy an `all(...)` condition.
- P11b also scores unregistered \(n=32\), and does not mark missing registered widths as pending.
- P11a combines errors with `hypot`, ignoring covariance from common past trajectories. It is not necessarily the SE of the difference.
- No registered-net whitelist or completion manifest prevents accidental inclusion or premature final scoring.

**PROVEN:** some problems precede scoring. The theory code drops chaos above degree 60 in its \(N\) residual while the P6 calculation effectively leaves that missing mass uncaptured. On ARC seed 4000, \(l=0\), the omitted predicted mass is **0.0546872**, already larger than the 1% target. The code also gives radial/amplitude first chaos two directions in v1, whereas the written rule does not clearly specify that allocation.

**PROVEN:** [score_part2.py](/home/agent/workspaces/mats/work/relevance/scratch/score_part2.py) has these departures:

- `Nge2` explicitly uses point values despite the registered \(+2\,\mathrm{SE}\) requirement.
- PG1 can score incomplete nets; missing layers must not satisfy a universal statement.
- PG2 silently excludes \(G=0\) cases. That exclusion was not registered.
- PS1 pools the already-seen small widths with the prospective large widths, obscuring the prospective test.
- PS2 fits all later points above \(10^{-3}\), rather than stopping at the **first** threshold crossing. It can include a later rebound. Insufficient fit points are coded as failure rather than “rate unresolved.”
- The gate-estimator error in T2 invalidates noisy PG results regardless of scorer correctness.

**NUMERICAL:** independent arithmetic from the raw runs gave:

| Check | Recomputed result |
|---|---:|
| ARC seed 4000, \(l=0\): \(s_1,\ D\) | \(0.2938678105,\ 16.09991783\) |
| Same cell: vector grid counts at \(0.1,0.01,0.001\) | \(192,\ 256,\ 256\) |
| ARC seed 4000, \(l=31\): vector/scalar grid counts | vector \(12,48,96\); scalar \(1,3,24\) |
| Available stationary snapshot: P4 | \(32/44=72.73\%\), below the registered 90% |

Sources: [ARC seed 4000](/home/agent/workspaces/mats/work/relevance/runs/eval_arc_n256_L32_seed4000.json) and the stationary run files.

**NUMERICAL:** snapshot PS1 results were \(11/13\) for one-direction capture at 90%, \(0/6\) at 99%, and zero radial-feature successes at either tolerance. These are provisional, mostly post hoc small-width results. No Part 2 gate or synchronization verdict was available.

**T4. First-chaos tail correction and a valid confidence bound**

**PROVEN:** subtracting \(\operatorname{tr}\operatorname{Var}(a)/P\) from every eigenvalue is not the general correction.

With an independently centered observation \(Y=a-c\), define
\[
T=YZ^\top,\qquad B=\mathbb ET,\qquad C_1=B^\top B.
\]
For the uncentered sample average \(\widehat B\),
\[
\mathbb E[\widehat B^\top\widehat B]
=C_1+\frac1P\left[
\mathbb E(\|Y\|^2ZZ^\top)-C_1
\right].
\]
The bracket is generally anisotropic. Even for \(Y=BZ\),
\[
\mathbb E[\widehat B^\top\widehat B]
=C_1+\frac1P\left[(\operatorname{tr}C_1)I+C_1\right].
\]
Sorted eigenvalues introduce an additional nonlinear estimation problem. Clipping corrected eigenvalues and filling omitted tails from another noisy estimate does not create coverage.

**PROVEN UNDER a certified second-moment bound:** a conservative bound can be built around the sample-centered cross-covariance already used by the runs.

Let
\[
\widetilde B=\frac{P}{P-1}\widehat B,\qquad
H_{ij}=\frac12(a_i-a_j)(Z_i-Z_j)^\top.
\]
Then \(\widetilde B\) is the order-two U-statistic with kernel \(H\), and \(\mathbb E\widetilde B=B\). For even \(P\), if
\[
\mathbb E\|H\|_F^2\le M,
\]
then
\[
\Pr\!\left(\|\widetilde B-B\|_F>
\sqrt{\frac{2M}{P\alpha}}\right)\le\alpha.
\]
Write \(\delta=\sqrt{2M/(P\alpha)}\). If the stored eigenvalues are \(\widehat\lambda_1,\ldots,\widehat\lambda_m\), \(m\le96\), then simultaneously for \(k<m\),
\[
\boxed{
\sum_{j>k}\lambda_j(C_1)\ge
\left[
\frac{P}{P-1}
\sqrt{\sum_{j=k+1}^{m}\widehat\lambda_j}
-\delta
\right]_+^2 .
}
\]
This follows from the Lipschitz property of distance to the set of rank-\(k\) matrices. Missing eigenvalues merely weaken this bound.

**PROVEN UNDER fixed noiseless network weights:** a usable-in-principle moment certificate is
\[
M\le L_F^2(n+2)\operatorname{tr}\Sigma,\qquad
L_F=\prod_j\|W_j\|_{\mathrm{op}}.
\]
It follows by applying the Lipschitz bound to \(a_i-a_j\) and evaluating a Gaussian fourth moment. It is computable with the stored trace and known weights, but will usually be extremely conservative at depth.

**PROVEN:** the existing scalar SE of \(V_1\) cannot certify eigenvalue tails. For a useful bound, store independent matrix-estimation batches or sample/block sufficient statistics, the fitted frame, and enough information for a justified matrix error radius. Direct averaged-Jacobian estimation is worth considering. To conclude \(N>k\), compare the tail lower bound against \(\varepsilon\) times an **upper** confidence bound for \(V^\gamma_l\). These certificates remain conditional on the fitted cloud unless frame error is covered separately.

**T5. Higher-degree lower bounds, including future-informed projections**

**PROVEN:** many rank-one terms and Haar orientation alone are insufficient. One dominant weight gives a ridge function. Correlated terms can remain rank one. With sufficiently many iid normals and weights allowed to depend on them, signed combinations can be chosen to produce a rank-one matrix.

**PROVEN UNDER iid Haar normals, nonnegative diffuse weights, and an isotropic \(r\)-dimensional cloud:** the requested Wishart argument does work for a coherent scalar quadratic component.

Let
\[
f_2(Z)=Z^\top HZ-\operatorname{tr}H,\qquad
H=\sum_{g=1}^G\beta_g u_gu_g^\top,
\]
where \(Z\sim N(0,I_r)\), \(u_g\) are independent uniform unit vectors, and \(\beta_g\ge0\) are fixed independently of the normals.

For every orthogonal projection \(P\),
\[
\operatorname{Var}(f_2)=2\|H\|_F^2,\qquad
\operatorname{Var}(\mathbb E[f_2\mid PZ])=2\|PHP\|_F^2.
\]
The optimal rank-\(k\) projection uses the largest eigenvalues of \(H\), giving
\[
\inf_{\operatorname{rank}P=k}
\frac{\mathbb E|f_2-\mathbb E[f_2\mid PZ]|^2}
     {\operatorname{Var}(f_2)}
=
\frac{\sum_{j>k}\lambda_j(H)^2}{\sum_j\lambda_j(H)^2}.
\]
This optimization already allows \(P\) to know every future gate.

Put \(W=\sum_g\beta_g\), \(\mu=W/r\). Matrix Chernoff gives, for \(0<\delta<1\),
\[
\Pr\!\left((1-\delta)\mu I\preceq H\preceq(1+\delta)\mu I\right)
\ge1-2r\exp\!\left(-\frac{\delta^2W}{3r\beta_{\max}}\right).
\]
On this event,
\[
\frac{R_2(P)}{V_2}
\ge
\left(1-\frac kr\right)
\left(\frac{1-\delta}{1+\delta}\right)^2.
\]
Thus achieving residual fraction \(\varepsilon'\) requires
\[
\boxed{
k\ge r\left[
1-\varepsilon'
\left(\frac{1+\delta}{1-\delta}\right)^2
\right].
}
\]
For small \(\delta\), this is approximately \((1-\varepsilon')r\).

**PROVEN UNDER the same assumptions:** a sufficient condition is
\[
\frac{W}{\beta_{\max}}
\gtrsim r\,\delta^{-2}\log(r/\alpha).
\]
For equal-weight Gaussian normals, ordinary Wishart singular-value bounds sharpen this: eigenvalues concentrate when \(G\gg r+\log(1/\alpha)\), without the extra \(\log r\) factor. Raw \(G\) is irrelevant if only a few weights carry the mass.

**PROVEN:** there is also a useful vector-output formulation. Write the quadratic chaos matrices as \(H_o\), and define
\[
S_2=\sum_o H_o^2.
\]
Then
\[
R_2(P)
=2\sum_o\big(\|H_o\|_F^2-\|PH_oP\|_F^2\big)
\ge2\operatorname{tr}((I-P)S_2)
\ge2\sum_{j>k}\lambda_j(S_2).
\]
Consequently, a lower spectral bound
\[
S_2\succeq(1-\delta)\frac{\operatorname{tr}S_2}{r}I
\]
implies
\[
R_2(P)/V_2\ge(1-\delta)(1-k/r)
\]
uniformly over future-informed \(P\). If degree two carries share \(\eta=V_2/V\), substitute \(\varepsilon'=\varepsilon/\eta\).

**PROVEN:** anisotropic clouds change the answer. In the coherent positive-weight case, whitening physical isotropic normals produces \(H\) approximately proportional to \(\Sigma\); the relevant tail is then the squared covariance spectrum. An unspecified “effective dimension” or covariance participation ratio cannot replace a flat-spectrum hypothesis.

**CONJECTURE:** actual deep-network gate tensors satisfy a sufficiently strong concentration property of this kind. The current work does not establish it: pulled-back normals are dependent, sensitivities have signs and correlations, and boundary coefficients depend on the normals. This is the missing theorem behind the claimed nonlinear obstruction.

**T6. Stationary slow mode**

**PROVEN:** the observed top active-subspace direction is not automatically the top right singular vector of the mean Jacobian. In whitened coordinates those matrices are
\[
C_{\rm AS}=\mathbb E[J_g(Z)^\top J_g(Z)],
\qquad
C_1=(\mathbb EJ_g(Z))^\top(\mathbb EJ_g(Z)).
\]
They agree in direction only under additional structure.

**PROVEN UNDER a dominant scalar-response approximation:** suppose
\[
g_t(m+\Sigma^{1/2}z)-\mathbb Eg_t
\approx A_t v_t\psi_t(z).
\]
Then the best linear-response direction is
\[
q_t\propto\mathbb E\nabla_z\psi_t,
\]
equivalently the leading right singular vector of the **whitened noise-averaged Jacobian**
\[
(\mathbb E_\gamma\nabla_x g_t)\Sigma^{1/2}.
\]
The AS direction instead comes from
\(\mathbb E[\nabla\psi_t\nabla\psi_t^\top]\). They coincide if the gradients are approximately parallel. Output rank one alone does not supply that condition.

**CONJECTURE:** the appropriate theoretical object is the leading nonconstant response function of the backward Markov-operator product. Its gradient supplies a direction when that response is approximately a ridge function. Calling it the “slow amplitude response” is reasonable; identifying it with radius is not justified.

**PROVEN:** for any chosen direction \(q\), the exact Gaussian residual is
\[
R(q)=
\|B(I-qq^\top)\|_F^2+
\|h_{\ge2}-\mathbb E[h_{\ge2}\mid q^\top Z]\|_{L^2}^2.
\]
Under a two-channel approximation, let \(p_t\) be the fraction of slow-response variance left after conditioning on \(q^\top Z\). Then
\[
\frac{R(q)}{V_t}
\approx
\frac{p_tV_{\rm slow}(t)+R_{\rm angular}(t)}
     {V_{\rm slow}(t)+V_{\rm angular}(t)}.
\]
The v2.8 exponential residual follows only when \(p_t\) is negligible. Otherwise there is a slow-response residual floor.

**NUMERICAL:** the 21:58 snapshot contains 16 resolved stationary cells with \(t\ge16\). Seven have point-estimated capture at least 95%; none reaches 99%. Examples:

| \(n\), seed, \(t\) | Residual after top AS direction | Residual after radial feature |
|---|---:|---:|
| 64, 1000, 16 | 0.1049 | 0.152 |
| 64, 1000, 32 | 0.0644 | 0.327 |
| 64, 1001, 16 | 0.2172 | 0.512 |
| 64, 1001, 32 | 0.0580 | 0.227 |
| 32, 1002, 32 | 0.1643 | 0.531 |

Thus the premise “95–99% on most nets at \(t\ge16\)” needs narrowing. The radial-feature failure is supported. The stored overlaps are squared overlaps with \(\Sigma^{1/2}e/\|\Sigma^{1/2}e\|\).

**NUMERICAL:** applying the registered resolved-window regression gives:

- \(n=32\): median rate \(0.0640148\), versus \(5/n=0.15625\).
- Available \(n=64\) seeds: rates \(0.0481181,\ 0.0934003,\ 0.0240887\); median \(0.0481181\), versus \(5/n=0.078125\).

Each \(n=64\) fit currently uses only \(t=16,32\). Adding the third available seed changes the median from \(0.0707592\) to \(0.0481181\). These are not stable measurements of an asymptotic exponent.

**HEURISTIC:** \(5/n\) and \(5/(2n)+1/Q\) are candidate radial-response models, not established exponents of \(V_l\). Quenched \(Q\) varies greatly across the stored cuts. The available runs do not identify either constant.

**PROVEN:** in the annealed critical noisy model,
\[
\mathbb E\|h_{k+1}\|^2=\mathbb E\|h_k\|^2+n.
\]
Therefore an annealed stationary law cannot have a finite second moment. A typical quenched radius cannot be substituted into an annealed stationary variance calculation without addressing this distinction.

**T7. Gate-count scaling**

**HEURISTIC UNDER a thin cloud and comparable gate sensitivities:** a gate is within \(T\) cloud standard deviations of its boundary with probability approximately
\[
p_T\approx \frac{T\theta_{\rm pair}}{\sqrt\pi}.
\]
The number of potentially relevant future gates is therefore approximately
\[
H_T(l,L)
\approx\frac{nT}{\sqrt\pi}
\sum_{j=0}^{L-l-1}\theta_{l+j}.
\]
Using \(\theta_j\approx3\pi/(j+6)\),
\[
H_T(l,L)\approx
3\sqrt\pi\,nT\log\frac{L+6}{l+6},
\]
capped by \(n(L-l)\). When the angle changes little, this reduces to the registered \(nT(L-l)\theta_l/\sqrt\pi\) estimate.

**HEURISTIC:** the hinge tail suggests \(T_\varepsilon\) grows roughly as \(\sqrt{\log(A/\varepsilon)}\), with \(A\) depending on sensitivity-weighted gate energy relative to \(V_l\). This predicts many eligible gates at early and middle ARC cuts, with fewer near the output. It is a scaling model for eligible gates, not a theorem for the measured \(G\); interactions and the chosen ordering can change the count substantially.

**PROVEN:** \(G>n\) does not itself explain large \(N\). Many gates may all depend on one direction. Large \(N\) requires their aggregate nonlinear energy to remain spread across directions, as measured by a tensor contraction such as \(S_2\) in T5.

**CONJECTURE:** early/mid ARC has many gates spanning a broad set of directions, with redundancy because there are more gates than input dimensions. The current snapshot contains no Part 2 runs to distinguish this from a smaller set of dominant gates. Near the output, vector relevance can remain large because of first chaos even when the nonlinear gate share is small.

**T8. Red team of the M1 conclusion**

- **PROVEN:** a lower bound on predictive projection dimension is not a lower bound on integration cost. For one Gaussian-input ReLU layer,
  \[
  \mathbb E\operatorname{ReLU}(w^\top X)
  =s\phi(\eta)+(w^\top m)\Phi(\eta),
  \quad
  s^2=w^\top\Sigma w,\quad
  \eta=w^\top m/s.
  \]
  This gives an exact sample-free mean regardless of relevance dimension. A spread quadratic such as \(\sum_i(Z_i^2-1)\) gives an even simpler counterexample: large projection dimension, exactly known mean.

- **PROVEN:** the AS count is an upper bound on the optimum. Failure of a candidate basis to compress does not establish that no future-informed basis can compress. Theorem 1’s restriction on past-measurable alignment does not constrain the future-informed projections allowed in \(N\).

- **PROVEN:** the present higher-degree argument supplies neither a uniform lower bound over projections nor the required concentration theorem. The expected fixed-PCA capture formula cannot fill that gap.

- **PROVEN:** the numerical first-chaos “lower bound” is not certified; the nonlinear count omits its registered uncertainty test; the noisy gate count has persistent downward bias. These cannot support an impossibility conclusion.

- **PROVEN:** “the obstruction is degree \(\ge2\)” is too broad. Near-output vector relevance can need many directions while almost all variance is first chaos. Gaussian-convention results also need not transfer to the true hidden-state law.

- **PROVEN:** no equal-compute comparison with sampling, multilevel sampling, quadrature, or fitted control variates is supplied by these diagnostics. Future-noise variance and the cost of learning/integrating a reduced model must be included.

**NUMERICAL, proposed replacement claim:** “At the tested ARC cuts, the evaluated linear subspaces often require many coordinates for 99% predictive capture under a fitted Gaussian cloud. Early-cut nonlinear variance is substantial. Whether it admits better future-informed compression, or an integration method beating sampling at equal compute, remains untested.”
136,815
**PROVEN:** the population projection bounds survive, but the proposed generic-capture argument does not establish the M1 conclusion. The most consequential implementation errors are the noisy gate subtraction, uncertified eigenvalue “debiasing,” and omission of Part 2’s uncertainty rule.

**NUMERICAL:** checked against the directory snapshot at **2026-11-01 21:58 UTC**. Neither score JSON nor any `runs/p2_*.json` existed then. The frozen hashes match; `accounting.py` differs only by the disclosed `cloud_evals_perp` addition. Existing tests pass. No files were changed.

**T1. Theory audit**

References below are to [FORMAL.md](/home/agent/workspaces/mats/work/relevance/FORMAL.md).

1. **PROVEN UNDER the stated independent Gaussian-weight model:** Theorem 1, lines 9–18, is correct. Condition on the past, choose its measurable frame, and use right-orthogonal invariance of \(M\). It requires independence of future noise from the weights and past. Its \(m\ne0\) assumption excludes the exact input cloud at \(l=0\); there the appropriate invariance is full \(O(n)\).

2. **PROVEN:** Corollary 1a is false for “any functional.” A functional depending only on a particular covariance entry supplies a counterexample. Require simultaneous rotation invariance:
   \[
   \Phi(R_\#\mu,F)=\Phi(\mu,F\circ R).
   \]
   Natural basis-free relevance quantities satisfy this.

   Its list of Gaussian orbit invariants is also incomplete. Writing the covariance in radial/angular blocks as
   \[
   \begin{pmatrix}a&b^\top\\b&C\end{pmatrix},
   \]
   one needs the position of \(b\) relative to the eigenspaces of \(C\), equivalently its spectral measure \(b^\top f(C)b\). The norm of \(b\) and spectrum of \(C\) alone are insufficient.

3. **PROVEN:** Corollary 1b’s displayed conditional expectation has a random right-hand side. The correction is
   \[
   \mathbb E[\|Ju\|^2\mid\mathcal F_l,\mathcal G]
   =\frac{\mathbb E[\|JB\|_F^2\mid\mathcal F_l,\mathcal G]}{n-1}
   =\frac2n\|K\|_F^2.
   \]
   Alternatively, additionally condition on the angular singular values. The singular frame is Haar with the usual qualifications about signs and degenerate eigenspaces.

   **PROVEN UNDER nondegenerate two-sided Oseledets hypotheses:** the distinction between past Gram–Schmidt vectors and future-dependent covariant vectors is appropriate. Equal amplification in expectation does not imply equal amplification in one realization.

4. **PROVEN UNDER an independently Haar-oriented angular operator:** the finite-dimensional random-congruence model in Corollary 1c is valid for that operator. Extending it to the cloud-averaged Jacobian remains **HEURISTIC**. Radial/angular cross-covariance must also be handled before identifying an angular block of the whitened relevance matrix.

   **PROVEN:** asymptotic freeness describes the bulk spectral law under appropriate convergence assumptions; it does not establish the claimed top-eigenvalue approximation. Take \(S=I\) and nonconstant \(\Lambda\): the product’s eigenvalues are those of \(\Lambda\), not all \(\operatorname{tr}\Lambda/(n-1)\). The stated fluctuation estimate concerns a random quadratic form, not general product eigenvalues. A low-rank backward subspace with concentrated compressed covariance would justify a restricted approximation.

5. **PROVEN UNDER Gaussian input and square-integrable weak gradients:** Section 2’s Mehler, Stein, and gradient-energy identities are correct, interpreting covariance as its trace and using \(V^\gamma_l\) consistently.

   **PROVEN:** the frozen-linear variance formula needs a noise convention. For the noise-averaged attribution, the relevant matrix is \(\mathbb E_\Xi J^m_\Xi\); averaging \(\operatorname{tr}(J^m_\Xi\Sigma J^{m\top}_\Xi)\) instead includes future-noise variation. The frozen-at-mean comparison with \(DV\) remains **HEURISTIC**.

6. **PROVEN UNDER a fixed-depth concentrating-kernel limit:** Section 3a’s noiseless kernel calculation is correct. “Norms concentrate” alone does not ensure the stated deterministic cosine. One also needs concentration of inner products and mean–fluctuation cross terms; sufficient conditions involve
   \[
   \frac{\operatorname{tr}\Sigma^2}{(\|m\|^2+\operatorname{tr}\Sigma)^2}\to0,
   \qquad
   \frac{m^\top\Sigma m}{(\|m\|^2+\operatorname{tr}\Sigma)^2}\to0.
   \]
   These assumptions are restrictive for a strongly anisotropic cloud.

   **PROVEN UNDER the displayed continuum small-angle overlap law:** \(s_1=(1+x)^{-1}\) and \(D=(1+x)^2\) follow. They are asymptotic model identities, not exact finite-angle, discrete-depth identities.

7. **PROVEN:** Section 3a’s stationary conclusion “\(s_1\ge0.9\) at every \(t\)” does not follow and conflicts with the later angular-sector limit. The independent-noise recursion is the appropriate model, but its long-time normalized shape need not become linear. The \(0.715,0.179,1.5\) limits require the frozen-\(Q\), large-\(Q\) continuum assumptions from round 1.

8. **PROVEN:** Section 3b incorrectly turns positive homogeneity into first Gaussian chaos. Homogeneity holds for positive scaling; a homogeneous nonlinear function can have substantial higher chaos. Radius \(\|X\|\) is not a linear Gaussian coordinate. Exact linear radial dependence holds on a fixed positive ray; a thin cloud permits a local approximation using \(e^\top X\).

   **PROVEN:** \(\mathbb E\log A=-5/(2n)\) is not an exact finite-width identity. For a noiseless layer, \(A=0\) has probability \(2^{-n}\), so its unconditional logarithmic expectation is \(-\infty\). The quoted value is a large-width expansion ignoring extinction. Its use for stationary response remains **HEURISTIC**.

9. **PROVEN:** Section 3c’s \(B(c)\), including \(B(1)=5\) and \(B(0)=0\), is the correct covariance coefficient for squared gains. Turning it into a log-amplitude covariance uses an expansion; the additive decomposition
   \(K_{\rm dir}+K_{\rm amp}+K_{\rm rad}\) requires neglected cross terms and normalization corrections.

   **PROVEN:** if \(c_0\) denotes the initial correlation, the gain sum uses \(j=0,\ldots,t-1\). The code uses this indexing; the displayed \(j=1,\ldots,t\) needs correction or an explicit shifted definition.

10. **PROVEN:** Section 4b does not follow from Theorem 1. Rotational invariance of a tensor’s law does not determine its covariance across trace and traceless components, nor make its coefficients uniformly distributed over symmetric tensors.

    For isotropic clouds, three examples already differ:

    - \(H=I\): degree-2 capture is \(k/r\).
    - One Haar-oriented rank-one \(H=uu^\top\): expected capture by a fixed \(P\) is \(k(k+2)/(r(r+2))\), while a future-informed rank-one \(P\) captures everything.
    - Isotropic coefficients in the full symmetric-matrix space: the \(h_2\) model gives \(k(k+1)/(r(r+1))\).

    Thus neither the \(h_d\) formula nor optimality of cloud PCA follows from Haar orientation alone.

11. **PROVEN:** Section 4c combines captures achievable in different subspaces without demonstrating a common \(k\)-dimensional subspace. Optimizing each chaos separately can produce an unattainable combined capture. Reserving the union of the required subspaces gives a legitimate upper-bound construction, with its actual dimension charged.

    **PROVEN:** \(s_{\ge2}>\varepsilon\) alone implies no large-dimensional lower bound. A high-degree ridge function needs one direction. Conversely, when nonlinear variance is negligible, the first-chaos tolerance is approximately \(\varepsilon/s_1\), measured against \(V_1\).

12. **PROVEN:** Section 4d establishes \(N_{\rm sc}\le1\) when \(s_{\ge2}\le\varepsilon\), for a nonzero first-chaos component. Its “forward-limited otherwise” conclusion is unsupported. Also, \(N_1=1\) requires nonzero first chaos; it is zero when that component vanishes.

13. **PROVEN UNDER the Gaussian convention:** v2.1’s population first-chaos lower bound and conditional Poincaré upper bound are correct. Its numerical eigenvalue correction does not provide a rigorous lower bound; see T4.

    **PROVEN:** \(n/P\) is approximately the noise-trace fraction relative to \(V\), not generally \(V_1\). Relative to \(V_1\), the corresponding approximation is \(n/(Ps_1)\). At ARC input, \(s_1\approx0.294\), so this distinction is substantial.

14. **PROVEN:** v2.2 should not describe the channel totals as exact facts about the Gaussian-convention network. The total true-law noiseless variance is independent of the cut; Gaussianization at different cuts need not preserve it. The displayed channel decomposition is an approximation with nonorthogonal components.

    At \(l=0\), \(m=0\), and input-radius variation is principally degree two under the Gaussian input, not a radial linear coordinate. The \((1/2)/n\) radius term itself is an asymptotic chi-radius calculation. Downgrade the network claim to **HEURISTIC**, retaining exact identities only inside an explicitly specified surrogate.

15. **PROVEN UNDER noiseless future, independent fresh weights, and differentiability:** v2.3’s annealed criticality identity is correct. Its consequence is
    \[
    \frac{\mathbb E_W J(1)}{\mathbb E_W V},
    \]
    a variance-weighted annealed mean degree, not \(\mathbb E_W[J(1)/V]\), and not an exact quenched formula. The claim “every fixed \(x,v\)” needs an exception at nondifferentiable \(x=0\).

    **PROVEN UNDER the stated kernel singularity:** the \(d^{-5/2}\) tail envelope explains slow convergence of the truncated derivative sum. It does not repair the missing tail in the count predictions automatically.

16. **PROVEN:** v2.4 contains two separate errors. Wick’s identity gives
    \[
    \frac{\mathbb E(a^\top Pa)^2}{\mathbb E(a^\top a)^2}
    =
    \frac{(\operatorname{tr}\Sigma_P)^2+2\operatorname{tr}\Sigma_P^2}
         {(\operatorname{tr}\Sigma)^2+2\operatorname{tr}\Sigma^2},
    \]
    but
    \[
    h_2(\lambda)=\tfrac12\big[(\operatorname{tr}\Sigma)^2+
                                  \operatorname{tr}\Sigma^2\big].
    \]
    These ratios are different.

    Moreover, a ReLU gate with preactivation \(b+a^\top Z\), \(s=\|a\|\), has second-chaos matrix
    \[
    H=\frac{\phi(b/s)}s\,aa^\top.
    \]
    The coefficient depends on the normal and cannot generally be discarded when averaging energies. For a transverse-only normal, its covariance also needs the transverse projector rather than unrestricted \(\Sigma\).

17. **NUMERICAL:** v2.5 overstates the current stationary measurements; see T6. Its angular limiting constants are **PROVEN UNDER the frozen-radius continuum model**, while identifying and assigning an exponent to the full slow mode remains **CONJECTURE**.

18. **PROVEN:** v2.6’s probability \(n2^{-n}\) concerns a single fixed nonzero input. A single-active-unit mean trajectory does not prove the whole cloud passes through that same bottleneck. The proposed finite-width Lyapunov gap needs an additional hypothesis.

    **NUMERICAL:** “exact to \(10^{-6}\ldots10^{-29}\) on all six nets by \(l=32\)” is inaccurate. The true-law radial residual ratios at \(l=32\) include \(8.63\times10^{-6}\), \(2.25\times10^{-6}\), and \(1.87\times10^{-6}\). Earlier exact-synchronization claims are also too strong.

19. **HEURISTIC:** v2.7 improves a surrogate but still assumes alignment of amplitude/radial output directions and compatibility of their input directions with the angular subspace. The implementation allocates \(k-1\) directions to angular first chaos but \(k\) to angular higher chaos without exhibiting their common subspace.

    **PROVEN UNDER an exactly one-coordinate slow response and a two-exponential variance decomposition:** v2.8’s threshold follows. Without that one-coordinate hypothesis, an irreducible slow-response residual remains; see T6.

**T2. Measurement estimators**

References: [rel.py](/home/agent/workspaces/mats/work/relevance/lib/rel.py), [accounting.py](/home/agent/workspaces/mats/work/relevance/lib/accounting.py), [gates.py](/home/agent/workspaces/mats/work/relevance/lib/gates.py).

- **PROVEN:** `pair_sq`, `v_l`, Gaussian pick-freeze residuals, and `total_var` use the correct noise sharing and factors. Shared noise *within* each difference reduces variance; independent noise *between* the two differences removes future-noise variance. Gaussian residuals require the factor \(1/2\); the true-law plug-in prediction error correctly does not.

- **PROVEN:** `ustat_sq` is unbiased for iid **uncentered or independently centered** rows. All important callers instead subtract the same sample mean. For Gaussian \(Z\), with \(P\) iid rows, its expectation is exactly
  \[
  \mathbb E\widehat V_1
  =\left(1-\frac2P+\frac{2}{P^2}\right)V_1.
  \]
  Thus “unbiased” is false as implemented, although the bias is small at these sample sizes. Divide by that factor or use independent centering.

  **NUMERICAL:** a scalar linear check at \(P=16\) gave \(0.88357\pm0.00194\), against the exact factor \(0.8828125\).

  **PROVEN:** the jackknife leaves the original centering fixed rather than redoing the complete statistic. It is not an exact uncertainty calculation for the implemented estimator. It is an asymptotic approximation away from degenerate first chaos. The block divisibility requirement happens to hold for the registered sample sizes.

- **PROVEN:** `mehler_curve` correctly estimates \(D(\rho)=V-K(\rho)\), not \(K(\rho)\). The negative-\(\rho\) construction is valid. The measurements called “Stein” use output–input moments, not averaged gradients; equivalence holds under the Gaussian convention.

- **PROVEN:** vector and scalar active-subspace matrices have the correct normalization. The common output cotangent and independent future-noise pair correctly estimate the product of noise-averaged Jacobians. Their finite-sample matrices can be indefinite; sampled eigenvalue tails are not certified Poincaré bounds.

- **PROVEN:** Gaussian residual evaluations are independent of their learned candidate bases. Most true-law projection evaluations also use held-out cloud samples. However, `res_ASt_true` learns and evaluates its basis on the same `Xe`; it is an in-sample diagnostic.

  The reconstruction is a valid predictor from the chosen linear feature, so its population MSE upper-bounds the optimal true-law residual. It need not equal that residual.

- **PROVEN:** the implementation measures a fitted Gaussian cloud, not the Gaussian with exact population moments. Report covariance-fitting and burn-in uncertainty separately. At \(l=0\), the sample mean invents an arbitrary “radial” direction although the exact mean is zero. `res_radial_*` measures the linear feature \(e^\top X\), not \(\|X\|\). `AS1_radial_overlap` stores the **squared** overlap.

  **PROVEN:** `mean_gap_nmse` has positive sampling bias from both estimated means, especially with noisy future outputs.

- **PROVEN:** the pathwise decomposition and first-order hinge recursion are correct. `parts_shares` is biased by its covariance normalization. For one component with noise-averaged variance \(V_f\) and conditional-noise variance
  \(W_f=\mathbb E_X\operatorname{Var}_\Xi f(X,\Xi)\),
  \[
  \mathbb E\widehat V_f
  =(1-1/P)V_f-\frac{W_f}{2P}
  \quad(\sigma>0).
  \]
  For \(\sigma=0\), the factor is simply \(1-1/P\). Use cross-realization sample covariance,
  \[
  \frac1{P-1}\sum_i(f_{i1}-\bar f_1)^\top(f_{i2}-\bar f_2).
  \]

- **PROVEN:** the mixed gate pass implements Part 2’s switched-versus-frozen network. It includes interactions among selected gates; it is not the first-order sum of single-gate hinges originally described in DEFINITIONS.

  The registered importance \(s^2\psi(\tau)\) is an uncentered hinge second moment. The hinge variance subtracts its squared mean; its degree-\(\ge2\) variance additionally subtracts its first-chaos energy:
  \[
  s^2\left[
    \psi(\tau)-(\phi(\tau)-\tau\bar\Phi(\tau))^2-\bar\Phi(\tau)^2
  \right].
  \]
  The code matches Part 2’s explicit importance formula, but not the original “own variance” definition.

- **PROVEN:** the noisy gate estimator has a persistent subtraction error. Let \(d_\xi=g_{\rm full,\xi}-g_{G,\xi}\) and \(B_\xi=\mathbb E_Z[d_\xi Z^\top]\). Its variance term uses cross-realization covariance correctly. Its first-chaos subtraction uses the average of two realizations, however:
  \[
  \mathbb E\left\|\frac{B_\xi+B_{\xi'}}2\right\|_F^2
  =
  \|\mathbb E B_\xi\|_F^2+
  \frac12\mathbb E\|B_\xi-\mathbb E B_\xi\|_F^2.
  \]
  Consequently the reported nonlinear residual is biased **downward**, even as \(P\to\infty\).

  Replace it with a cross-realization U-statistic, for independently centered \(d_1,d_2\):
  \[
  \frac{
  \langle d_1^\top Z,d_2^\top Z\rangle_F
  -\sum_i(d_{1i}^\top d_{2i})\|Z_i\|^2
  }{P(P-1)}.
  \]
  This targets the cross first-chaos product.

  **PROVEN:** two noise realizations shared across all \(P\) inputs do not provide \(P\) independent future-noise replicates. Uncertainty must include the outer noise dimension. Realizations beyond the first two are currently ignored by the subtraction calculation.

- **PROVEN:** gate ranking also uses spreads estimated from the evaluation inputs themselves. That makes the selected mixed map data-dependent. Compute those spreads analytically from the frame or on independent training inputs. Interactions can make the gate-residual curve nonmonotone; the first successful geometric-grid point is only a tested count, not a bracket on the minimum over all counts.

- **PROVEN:** the nonlinear active-subspace population identity
  \[
  R_{\ge2}(P)=R_{\rm total}(P)-\|B(I-P)\|_F^2
  \]
  is correct. Its implementation uses training-sample \(V_1\) and a different holdout sample for captured first chaos. At \(k=n\), their difference can remain nonzero even though the true residual is exactly zero. Estimate the entire first-chaos complement directly on the same holdout sample.

  The learned nonlinear matrix also includes error from estimating \(B\); it is not an unbiased estimate of the ideal nonlinear active-subspace matrix. It can still propose a basis, provided evaluation is independent.

  **PROVEN:** the required residual standard errors are discarded, so the registered “residual \(+2\,\mathrm{SE}\)” decision cannot be reconstructed.

- **PROVEN:** `n1_split` correctly separates basis training from evaluation and avoids evaluating captured energy on the training basis sample. Its centering retains the small bias above. It estimates residuals for a learned basis; neither the thresholded count nor the population optimal \(N_1\) is an “unbiased count.”

**T3. Scoring and independent recomputation**

**PROVEN:** [score_part1.py](/home/agent/workspaces/mats/work/relevance/scratch/score_part1.py) implements the advertised numerical bands for P1–P8 substantially as written, including the interval-intersection rule for P7/P8. It does not implement a complete, uncertainty-certified preregistration:

- `n1_meas` stores only 96 eigenvalues and returns 96 even when the target was not reached. Such cases need a censored result.
- The global “unresolved cells are not scored” rule is not applied to P9a–d, P10, and P11a. If intended as exceptions, state that explicitly.
- P9 net-level conclusions do not check that all registered layers and nets are present. A partially completed net can satisfy an `all(...)` condition.
- P11b also scores unregistered \(n=32\), and does not mark missing registered widths as pending.
- P11a combines errors with `hypot`, ignoring covariance from common past trajectories. It is not necessarily the SE of the difference.
- No registered-net whitelist or completion manifest prevents accidental inclusion or premature final scoring.

**PROVEN:** some problems precede scoring. The theory code drops chaos above degree 60 in its \(N\) residual while the P6 calculation effectively leaves that missing mass uncaptured. On ARC seed 4000, \(l=0\), the omitted predicted mass is **0.0546872**, already larger than the 1% target. The code also gives radial/amplitude first chaos two directions in v1, whereas the written rule does not clearly specify that allocation.

**PROVEN:** [score_part2.py](/home/agent/workspaces/mats/work/relevance/scratch/score_part2.py) has these departures:

- `Nge2` explicitly uses point values despite the registered \(+2\,\mathrm{SE}\) requirement.
- PG1 can score incomplete nets; missing layers must not satisfy a universal statement.
- PG2 silently excludes \(G=0\) cases. That exclusion was not registered.
- PS1 pools the already-seen small widths with the prospective large widths, obscuring the prospective test.
- PS2 fits all later points above \(10^{-3}\), rather than stopping at the **first** threshold crossing. It can include a later rebound. Insufficient fit points are coded as failure rather than “rate unresolved.”
- The gate-estimator error in T2 invalidates noisy PG results regardless of scorer correctness.

**NUMERICAL:** independent arithmetic from the raw runs gave:

| Check | Recomputed result |
|---|---:|
| ARC seed 4000, \(l=0\): \(s_1,\ D\) | \(0.2938678105,\ 16.09991783\) |
| Same cell: vector grid counts at \(0.1,0.01,0.001\) | \(192,\ 256,\ 256\) |
| ARC seed 4000, \(l=31\): vector/scalar grid counts | vector \(12,48,96\); scalar \(1,3,24\) |
| Available stationary snapshot: P4 | \(32/44=72.73\%\), below the registered 90% |

Sources: [ARC seed 4000](/home/agent/workspaces/mats/work/relevance/runs/eval_arc_n256_L32_seed4000.json) and the stationary run files.

**NUMERICAL:** snapshot PS1 results were \(11/13\) for one-direction capture at 90%, \(0/6\) at 99%, and zero radial-feature successes at either tolerance. These are provisional, mostly post hoc small-width results. No Part 2 gate or synchronization verdict was available.

**T4. First-chaos tail correction and a valid confidence bound**

**PROVEN:** subtracting \(\operatorname{tr}\operatorname{Var}(a)/P\) from every eigenvalue is not the general correction.

With an independently centered observation \(Y=a-c\), define
\[
T=YZ^\top,\qquad B=\mathbb ET,\qquad C_1=B^\top B.
\]
For the uncentered sample average \(\widehat B\),
\[
\mathbb E[\widehat B^\top\widehat B]
=C_1+\frac1P\left[
\mathbb E(\|Y\|^2ZZ^\top)-C_1
\right].
\]
The bracket is generally anisotropic. Even for \(Y=BZ\),
\[
\mathbb E[\widehat B^\top\widehat B]
=C_1+\frac1P\left[(\operatorname{tr}C_1)I+C_1\right].
\]
Sorted eigenvalues introduce an additional nonlinear estimation problem. Clipping corrected eigenvalues and filling omitted tails from another noisy estimate does not create coverage.

**PROVEN UNDER a certified second-moment bound:** a conservative bound can be built around the sample-centered cross-covariance already used by the runs.

Let
\[
\widetilde B=\frac{P}{P-1}\widehat B,\qquad
H_{ij}=\frac12(a_i-a_j)(Z_i-Z_j)^\top.
\]
Then \(\widetilde B\) is the order-two U-statistic with kernel \(H\), and \(\mathbb E\widetilde B=B\). For even \(P\), if
\[
\mathbb E\|H\|_F^2\le M,
\]
then
\[
\Pr\!\left(\|\widetilde B-B\|_F>
\sqrt{\frac{2M}{P\alpha}}\right)\le\alpha.
\]
Write \(\delta=\sqrt{2M/(P\alpha)}\). If the stored eigenvalues are \(\widehat\lambda_1,\ldots,\widehat\lambda_m\), \(m\le96\), then simultaneously for \(k<m\),
\[
\boxed{
\sum_{j>k}\lambda_j(C_1)\ge
\left[
\frac{P}{P-1}
\sqrt{\sum_{j=k+1}^{m}\widehat\lambda_j}
-\delta
\right]_+^2 .
}
\]
This follows from the Lipschitz property of distance to the set of rank-\(k\) matrices. Missing eigenvalues merely weaken this bound.

**PROVEN UNDER fixed noiseless network weights:** a usable-in-principle moment certificate is
\[
M\le L_F^2(n+2)\operatorname{tr}\Sigma,\qquad
L_F=\prod_j\|W_j\|_{\mathrm{op}}.
\]
It follows by applying the Lipschitz bound to \(a_i-a_j\) and evaluating a Gaussian fourth moment. It is computable with the stored trace and known weights, but will usually be extremely conservative at depth.

**PROVEN:** the existing scalar SE of \(V_1\) cannot certify eigenvalue tails. For a useful bound, store independent matrix-estimation batches or sample/block sufficient statistics, the fitted frame, and enough information for a justified matrix error radius. Direct averaged-Jacobian estimation is worth considering. To conclude \(N>k\), compare the tail lower bound against \(\varepsilon\) times an **upper** confidence bound for \(V^\gamma_l\). These certificates remain conditional on the fitted cloud unless frame error is covered separately.

**T5. Higher-degree lower bounds, including future-informed projections**

**PROVEN:** many rank-one terms and Haar orientation alone are insufficient. One dominant weight gives a ridge function. Correlated terms can remain rank one. With sufficiently many iid normals and weights allowed to depend on them, signed combinations can be chosen to produce a rank-one matrix.

**PROVEN UNDER iid Haar normals, nonnegative diffuse weights, and an isotropic \(r\)-dimensional cloud:** the requested Wishart argument does work for a coherent scalar quadratic component.

Let
\[
f_2(Z)=Z^\top HZ-\operatorname{tr}H,\qquad
H=\sum_{g=1}^G\beta_g u_gu_g^\top,
\]
where \(Z\sim N(0,I_r)\), \(u_g\) are independent uniform unit vectors, and \(\beta_g\ge0\) are fixed independently of the normals.

For every orthogonal projection \(P\),
\[
\operatorname{Var}(f_2)=2\|H\|_F^2,\qquad
\operatorname{Var}(\mathbb E[f_2\mid PZ])=2\|PHP\|_F^2.
\]
The optimal rank-\(k\) projection uses the largest eigenvalues of \(H\), giving
\[
\inf_{\operatorname{rank}P=k}
\frac{\mathbb E|f_2-\mathbb E[f_2\mid PZ]|^2}
     {\operatorname{Var}(f_2)}
=
\frac{\sum_{j>k}\lambda_j(H)^2}{\sum_j\lambda_j(H)^2}.
\]
This optimization already allows \(P\) to know every future gate.

Put \(W=\sum_g\beta_g\), \(\mu=W/r\). Matrix Chernoff gives, for \(0<\delta<1\),
\[
\Pr\!\left((1-\delta)\mu I\preceq H\preceq(1+\delta)\mu I\right)
\ge1-2r\exp\!\left(-\frac{\delta^2W}{3r\beta_{\max}}\right).
\]
On this event,
\[
\frac{R_2(P)}{V_2}
\ge
\left(1-\frac kr\right)
\left(\frac{1-\delta}{1+\delta}\right)^2.
\]
Thus achieving residual fraction \(\varepsilon'\) requires
\[
\boxed{
k\ge r\left[
1-\varepsilon'
\left(\frac{1+\delta}{1-\delta}\right)^2
\right].
}
\]
For small \(\delta\), this is approximately \((1-\varepsilon')r\).

**PROVEN UNDER the same assumptions:** a sufficient condition is
\[
\frac{W}{\beta_{\max}}
\gtrsim r\,\delta^{-2}\log(r/\alpha).
\]
For equal-weight Gaussian normals, ordinary Wishart singular-value bounds sharpen this: eigenvalues concentrate when \(G\gg r+\log(1/\alpha)\), without the extra \(\log r\) factor. Raw \(G\) is irrelevant if only a few weights carry the mass.

**PROVEN:** there is also a useful vector-output formulation. Write the quadratic chaos matrices as \(H_o\), and define
\[
S_2=\sum_o H_o^2.
\]
Then
\[
R_2(P)
=2\sum_o\big(\|H_o\|_F^2-\|PH_oP\|_F^2\big)
\ge2\operatorname{tr}((I-P)S_2)
\ge2\sum_{j>k}\lambda_j(S_2).
\]
Consequently, a lower spectral bound
\[
S_2\succeq(1-\delta)\frac{\operatorname{tr}S_2}{r}I
\]
implies
\[
R_2(P)/V_2\ge(1-\delta)(1-k/r)
\]
uniformly over future-informed \(P\). If degree two carries share \(\eta=V_2/V\), substitute \(\varepsilon'=\varepsilon/\eta\).

**PROVEN:** anisotropic clouds change the answer. In the coherent positive-weight case, whitening physical isotropic normals produces \(H\) approximately proportional to \(\Sigma\); the relevant tail is then the squared covariance spectrum. An unspecified “effective dimension” or covariance participation ratio cannot replace a flat-spectrum hypothesis.

**CONJECTURE:** actual deep-network gate tensors satisfy a sufficiently strong concentration property of this kind. The current work does not establish it: pulled-back normals are dependent, sensitivities have signs and correlations, and boundary coefficients depend on the normals. This is the missing theorem behind the claimed nonlinear obstruction.

**T6. Stationary slow mode**

**PROVEN:** the observed top active-subspace direction is not automatically the top right singular vector of the mean Jacobian. In whitened coordinates those matrices are
\[
C_{\rm AS}=\mathbb E[J_g(Z)^\top J_g(Z)],
\qquad
C_1=(\mathbb EJ_g(Z))^\top(\mathbb EJ_g(Z)).
\]
They agree in direction only under additional structure.

**PROVEN UNDER a dominant scalar-response approximation:** suppose
\[
g_t(m+\Sigma^{1/2}z)-\mathbb Eg_t
\approx A_t v_t\psi_t(z).
\]
Then the best linear-response direction is
\[
q_t\propto\mathbb E\nabla_z\psi_t,
\]
equivalently the leading right singular vector of the **whitened noise-averaged Jacobian**
\[
(\mathbb E_\gamma\nabla_x g_t)\Sigma^{1/2}.
\]
The AS direction instead comes from
\(\mathbb E[\nabla\psi_t\nabla\psi_t^\top]\). They coincide if the gradients are approximately parallel. Output rank one alone does not supply that condition.

**CONJECTURE:** the appropriate theoretical object is the leading nonconstant response function of the backward Markov-operator product. Its gradient supplies a direction when that response is approximately a ridge function. Calling it the “slow amplitude response” is reasonable; identifying it with radius is not justified.

**PROVEN:** for any chosen direction \(q\), the exact Gaussian residual is
\[
R(q)=
\|B(I-qq^\top)\|_F^2+
\|h_{\ge2}-\mathbb E[h_{\ge2}\mid q^\top Z]\|_{L^2}^2.
\]
Under a two-channel approximation, let \(p_t\) be the fraction of slow-response variance left after conditioning on \(q^\top Z\). Then
\[
\frac{R(q)}{V_t}
\approx
\frac{p_tV_{\rm slow}(t)+R_{\rm angular}(t)}
     {V_{\rm slow}(t)+V_{\rm angular}(t)}.
\]
The v2.8 exponential residual follows only when \(p_t\) is negligible. Otherwise there is a slow-response residual floor.

**NUMERICAL:** the 21:58 snapshot contains 16 resolved stationary cells with \(t\ge16\). Seven have point-estimated capture at least 95%; none reaches 99%. Examples:

| \(n\), seed, \(t\) | Residual after top AS direction | Residual after radial feature |
|---|---:|---:|
| 64, 1000, 16 | 0.1049 | 0.152 |
| 64, 1000, 32 | 0.0644 | 0.327 |
| 64, 1001, 16 | 0.2172 | 0.512 |
| 64, 1001, 32 | 0.0580 | 0.227 |
| 32, 1002, 32 | 0.1643 | 0.531 |

Thus the premise “95–99% on most nets at \(t\ge16\)” needs narrowing. The radial-feature failure is supported. The stored overlaps are squared overlaps with \(\Sigma^{1/2}e/\|\Sigma^{1/2}e\|\).

**NUMERICAL:** applying the registered resolved-window regression gives:

- \(n=32\): median rate \(0.0640148\), versus \(5/n=0.15625\).
- Available \(n=64\) seeds: rates \(0.0481181,\ 0.0934003,\ 0.0240887\); median \(0.0481181\), versus \(5/n=0.078125\).

Each \(n=64\) fit currently uses only \(t=16,32\). Adding the third available seed changes the median from \(0.0707592\) to \(0.0481181\). These are not stable measurements of an asymptotic exponent.

**HEURISTIC:** \(5/n\) and \(5/(2n)+1/Q\) are candidate radial-response models, not established exponents of \(V_l\). Quenched \(Q\) varies greatly across the stored cuts. The available runs do not identify either constant.

**PROVEN:** in the annealed critical noisy model,
\[
\mathbb E\|h_{k+1}\|^2=\mathbb E\|h_k\|^2+n.
\]
Therefore an annealed stationary law cannot have a finite second moment. A typical quenched radius cannot be substituted into an annealed stationary variance calculation without addressing this distinction.

**T7. Gate-count scaling**

**HEURISTIC UNDER a thin cloud and comparable gate sensitivities:** a gate is within \(T\) cloud standard deviations of its boundary with probability approximately
\[
p_T\approx \frac{T\theta_{\rm pair}}{\sqrt\pi}.
\]
The number of potentially relevant future gates is therefore approximately
\[
H_T(l,L)
\approx\frac{nT}{\sqrt\pi}
\sum_{j=0}^{L-l-1}\theta_{l+j}.
\]
Using \(\theta_j\approx3\pi/(j+6)\),
\[
H_T(l,L)\approx
3\sqrt\pi\,nT\log\frac{L+6}{l+6},
\]
capped by \(n(L-l)\). When the angle changes little, this reduces to the registered \(nT(L-l)\theta_l/\sqrt\pi\) estimate.

**HEURISTIC:** the hinge tail suggests \(T_\varepsilon\) grows roughly as \(\sqrt{\log(A/\varepsilon)}\), with \(A\) depending on sensitivity-weighted gate energy relative to \(V_l\). This predicts many eligible gates at early and middle ARC cuts, with fewer near the output. It is a scaling model for eligible gates, not a theorem for the measured \(G\); interactions and the chosen ordering can change the count substantially.

**PROVEN:** \(G>n\) does not itself explain large \(N\). Many gates may all depend on one direction. Large \(N\) requires their aggregate nonlinear energy to remain spread across directions, as measured by a tensor contraction such as \(S_2\) in T5.

**CONJECTURE:** early/mid ARC has many gates spanning a broad set of directions, with redundancy because there are more gates than input dimensions. The current snapshot contains no Part 2 runs to distinguish this from a smaller set of dominant gates. Near the output, vector relevance can remain large because of first chaos even when the nonlinear gate share is small.

**T8. Red team of the M1 conclusion**

- **PROVEN:** a lower bound on predictive projection dimension is not a lower bound on integration cost. For one Gaussian-input ReLU layer,
  \[
  \mathbb E\operatorname{ReLU}(w^\top X)
  =s\phi(\eta)+(w^\top m)\Phi(\eta),
  \quad
  s^2=w^\top\Sigma w,\quad
  \eta=w^\top m/s.
  \]
  This gives an exact sample-free mean regardless of relevance dimension. A spread quadratic such as \(\sum_i(Z_i^2-1)\) gives an even simpler counterexample: large projection dimension, exactly known mean.

- **PROVEN:** the AS count is an upper bound on the optimum. Failure of a candidate basis to compress does not establish that no future-informed basis can compress. Theorem 1’s restriction on past-measurable alignment does not constrain the future-informed projections allowed in \(N\).

- **PROVEN:** the present higher-degree argument supplies neither a uniform lower bound over projections nor the required concentration theorem. The expected fixed-PCA capture formula cannot fill that gap.

- **PROVEN:** the numerical first-chaos “lower bound” is not certified; the nonlinear count omits its registered uncertainty test; the noisy gate count has persistent downward bias. These cannot support an impossibility conclusion.

- **PROVEN:** “the obstruction is degree \(\ge2\)” is too broad. Near-output vector relevance can need many directions while almost all variance is first chaos. Gaussian-convention results also need not transfer to the true hidden-state law.

- **PROVEN:** no equal-compute comparison with sampling, multilevel sampling, quadrature, or fitted control variates is supplied by these diagnostics. Future-noise variance and the cost of learning/integrating a reduced model must be included.

**NUMERICAL, proposed replacement claim:** “At the tested ARC cuts, the evaluated linear subspaces often require many coordinates for 99% predictive capture under a fitted Gaussian cloud. Early-cut nonlinear variance is substantial. Whether it admits better future-informed compression, or an integration method beating sampling at equal compute, remains untested.”
