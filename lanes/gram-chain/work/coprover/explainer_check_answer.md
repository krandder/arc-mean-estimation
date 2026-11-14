1. **[fine] CORRECT — §1 definitions.** The definitions of \(G,Q,\rho,\delta\) are correct when both radii are positive. Setting \(\sigma=1\) is valid for \(\sigma>0\), provided initial states are also rescaled. \(Q\) is squared norm per coordinate; \(\delta\) is an angular discrepancy, not the angle itself.

2. **[fine] CORRECT — §2 exact transition.** The iid Gaussian preactivations, rank-one-sum transition, displayed \(\kappa\), conditional mean, and covariance divided by \(n\) are exact. Require \(S\succeq0\), \(S_{aa}=1\), and fresh noise independent of weights and past. General Gaussian correlations are mathematically valid, although the supplied implementation supports sharing partitions only.

3. **[imprecision] CORRECT with qualifications — §2 consequences.** Same-layer rotation-invariant observables and their Gram-path laws are preserved. \(n\arccos(\rho)/\pi\) is the exact expected next-layer disagreement count. Cost is generally \(O(R^3+nR^2)\), versus \(O(n^2R)\); the stated cost is appropriate for small \(R\). The kernel/vertex expansion is a finite-depth expansion, not automatically uniform in stationary depth.

4. **[error] WRONG — §3 stationary constants presented as exact.** The stationary law exists, but
   \[
   \operatorname{med}(Q)\sim0.5770780164\,n,\qquad
   P(Q>x)\sim C_n/x,\quad C_n=\frac1{E[A\log A]},
   \]
   where \(A=(2/n)\chi^2_M,\ M\sim\mathrm{Bin}(n,1/2)\). Here \(C_n=2n/5+13/75+O(n^{-1})\). The perpetuity is the auxiliary \(r\); \(Q=(\chi_n^2/n)r\) with independent factors.

5. **[fine] CORRECT — §3 moments.** \(E[Q'|Q]=Q+1\), linear mean growth from finite-mean initialization, infinite stationary mean, and absence of a finite kernel/vertex moment fixed point are correct.

6. **[error] WRONG — “at \(\sigma=0\) there is no stationary law.”** The point mass at zero is stationary. At finite width, extinction occurs almost surely in finite time: each nonzero state has probability \(2^{-n}\) of encountering an all-off layer.

7. **[error] WRONG — normalized quantities automatically have light-tailed laws and a closed recursion.** Angles are bounded; raw radius ratios can have polynomial tails from a near-zero denominator. Log-radius ratios are different. Normalized variables alone are not an autonomous Markov chain because their transitions depend on absolute radii.

8. **[error] WRONG if read as a conditional expectation — §3 correlation update.**  
   \[
   \bar\rho'=\frac{Q\kappa(\rho)+c}{Q+1}
   \]
   normalizes conditional mean Gram entries. It is neither the realized \(\rho'\) nor generally \(E[\rho'|G]\). It is a mean-field closure.

9. **[fine] CORRECT — both expansions.** The \(\delta^{3/2}\) and \(\delta^{5/2}\) coefficients and the displayed two-term fixed-point expansion check algebraically and numerically, for fixed \(c<1\), \(Q\to\infty\). Constants \(2.231\) and \(3.2\) are correctly rounded; the latter is \(3.21856\). The two-term error near \(Q=148,c=0\) is approximately \(0.26\%\), consistent with \(0.3\%\).

10. **[imprecision] CORRECT only asymptotically — noise endpoints.** The \(c=-1\) factor \(2^{2/3}\) is a leading large-\(Q\) ratio, not an exact finite-\(Q\) identity. For \(c=1\), the frozen-radius map converges to zero discrepancy; exact synchronization from distinct initial states requires a separate argument.

11. **[fine] CORRECT as mean-field estimates — §4 timescales.** Angular relaxation is \(1.48728Q^{1/3}\), approximately eight layers at \(Q=0.577n,n=256\). Linearized log-radius-ratio restoration has rate \(1/(Q+1)\). Radius evolution on \(n\) layers is the diffusion scaling, not a universal mixing-time guarantee.

12. **[imprecision] CORRECT numerical reproduction; UNSUPPORTED as established asymptotics.** Rerunning `quick_r2.py` reproduces medians \(1.037,0.994,0.996\), SDs \(0.757,0.465,0.283\), and scaled log-radius SDs \(1.52,1.70,1.82\). Thus \(1.85n^{-1/3}\) and the quoted ranges summarize these runs reasonably. The source reports \(1.123\to0.997\) mean ratios. Burn-in/convergence checks and uncertainty estimates are needed for stationary or asymptotic claims.

13. **[imprecision] CORRECT conditionally — Gaussian-cloud distances.** For iid draws from a fixed Gaussian cloud, squared-distance relative SD is exactly \(\sqrt{2/\mathrm{PR}}\), and shared-endpoint distance correlation is \(1/4\). These are not unconditional across-net identities, nor automatically identities for normalized angles.

14. **[imprecision] UNSUPPORTED as an exact range formula.** The factor \(1.46581\) additionally approximates the three distances as jointly Gaussian and their denominator by its mean. Gaussian *points* alone do not justify that. The numerical ranges reproduce as \(0.754,0.563,0.393\); inserting the cited PRs gives \(0.700,0.495,0.336\). A \(1/k\) spectrum gives \(\mathrm{PR}\asymp(\log n)^2\), hence logarithmically shrinking relative distance fluctuations.

15. **[error] WRONG — a sampled angle ratio equals a total effect.** For direction observables the normalized effect is a ratio of expected discrepancies, with conditioning specified, not the random ratio \(\delta_{12}/\delta_{13}\). For raw states, unequal radii also enter the squared distance.

16. **[imprecision] CORRECT leading approximation — single injection.** The injection \(1/(Q+1)\), algebraic decay, and \(2.98725Q^{1/6}\) sum follow the frozen-radius angular model. However, the exact mean-field shared-noise update is
   \[
   \delta'=\frac{Q}{Q+1}[1-\kappa(1-\delta)].
   \]
   Its omitted linear contraction produces eventual exponential decay. The algebraic formula is intermediate-time; the summed ratio concerns direction variance.

17. **[error] WRONG — §5’s unrestricted “polynomial” criterion.** An observable must be recoverable from the sampled Grams, or from an explicitly augmented transition. Being polynomial in finitely many draws is insufficient. Polynomiality is also unnecessary: bounded measurable Gram observables are accessible.

18. **[fine] CORRECT — cloud identities.** Two independent replicas give the covariance trace; four give \(\operatorname{tr}(C^2)\) through the displayed squared inner product. The latter equality needs conditional noise expectation for fixed \(W\), or \(E_W\) on both sides. Ratios of annealed moments are not mean per-net participation ratios.

19. **[imprecision] CORRECT sharing patterns; specify normalization.** Resampling only \(B\) gives the unnormalized total-effect variance. Sharing only \(B\) gives the closed-effect variance
   \[
   V_B^{\rm closed}=E\langle f,f^{\mathrm{share}\,B}\rangle-\|Ef\|^2.
   \]
   Subtract the independent baseline. Summed total effects divided by variance give mean order for a partition into independent blocks.

20. **[error] WRONG — every across-net second moment needs four replicas.** A quantity represented using \(r\) replicas generally needs \(2r\) for its square. Four suffice for a two-replica total effect; squaring the four-replica covariance-square quantity generally needs eight.

21. **[error] WRONG — identifying sharing probability with Gaussian correlation.** Bernoulli sharing generates ANOVA orders; Gaussian correlation generates Hermite degrees. The closure \(1-(1-t)^{2/3}\) gives the stated \(0.175,0.370,0.603\). The measured ranges are correctly quoted, but concern normalized scalar-coordinate sharing curves with specified window conditioning.

22. **[error] UNSUPPORTED — transferring the closure’s coefficients to layer-block ANOVA.** The formal curve has first coefficient \(2/3\) and coefficients asymptotic to \(2/[3\Gamma(1/3)]\,k^{-5/3}\). For Gaussian correlation these describe Hermite energy. A layer-sharing derivation is needed for ANOVA identification and the \(\sqrt Q\) cutoff; the limiting curve alone supplies no cutoff.

23. **[imprecision] CORRECT scope, overstated closed forms — gates/input regime.** Expected next-layer flips are closed-form; general cascade histories require propagation or augmentation. The noiseless Gram recursion and amplitude homogeneity are exact. The \(3n/l\) gate count is a mean-field asymptotic before finite-width effects/extinction, not an exact finite-width law.

24. **[error] CORRECT tangent chain and mean; WRONG unrestricted typical decay.** Augmented state/tangent Grams close exactly, and \(E_W\|Ju\|^2=\|u\|^2\) holds with nonzero base states. But all-off layers kill tangents almost surely at fixed width. \(\exp(-2.5t/n)\) is a large-width, pre-extinction approximation.

25. **[imprecision] CORRECT representation; WRONG “only through moments.”** For conditionally iid replicas, all finite Gram-array laws determine the random noise measure up to orthogonal transformations. Arbitrary sharing patterns need not be exchangeable. Per-net invariant ratios, medians, and entropy can be approached through growing-replica empirical laws; polynomial moments alone need not determine them.

26. **[error] WRONG — every orthogonal-direction annealed quantity is identical.** Equal-norm orthogonal *input perturbations* have identical future response laws. Arbitrary output projections do not: \(E[h'|h]=\sqrt{Q/\pi}\mathbf1\), so \(E[u\cdot h'|h]\) depends on \(\sum_i u_i\), even with \(u\perp h\).

27. **[error] UNSUPPORTED omissions — §6.** State integrability requirements: stationary raw moments already diverge, invalidating some moment/ratio manipulations. Radius conditioning does not preserve iid replicas conditional on weights, and its claimed correction of annealed weighting is unproved. Finite-replica limitations must be distinguished from limitations of the entire hierarchy.

**Verdict: Major mathematical revision needed; the exact chain and local expansions are sound, but several stationary, replica-observable, ANOVA, and symmetry claims overreach.**
