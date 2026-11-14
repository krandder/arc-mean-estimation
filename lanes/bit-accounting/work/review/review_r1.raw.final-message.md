<!-- Extracted: the reviewer/co-prover model's final message only. The full session dump (prompt echo, tool calls, intermediate output) is not in this repo. Source file: work/bit-accounting/review/review_r1.raw -->

**Verdict: major revision.** Checked 2026-11-02, 00:14 UTC. Read-only review; existing bitlib tests passed, and targeted counterexamples reproduced the issues below.

The deterministic sandwich, factor-4 bound, information bound, and free-output Gaussian analog construction are fundamentally sound. Several stronger conclusions and implemented statistics are not.

1. **Major — [FORMAL.md §2.1](/home/agent/workspaces/mats/work/bit-accounting/FORMAL.md:78): the identity chain need not be optimal at every layer.**  
   Free-output codewords need not belong to every \(A_l\). For example, \(W_1=I\), \(W_2=\begin{pmatrix}1&-2\\-2&1\end{pmatrix}\) gives \(A_0\) equal to the two nonnegative coordinate rays, while \(A_1=\mathbb R_+^2\). The output mean has both coordinates positive: zero-bit optimal distortion is \(V\) at layer 1 but strictly greater at layer 0. **Fix:** claim an identity chain achieving the *support-restricted* output optimum, or assume a common reachable optimal codebook. Existence also does not imply training finds identity.

2. **Minor — [FORMAL.md §1.2](/home/agent/workspaces/mats/work/bit-accounting/FORMAL.md:32): complete the hypotheses and channel argument.**  
   The finite-code proof actually establishes \(D_l^*(b)=D_{\rm out}^{A_l}(b)\), which proves monotonicity. Full input support gives the *closure* of the image; closedness here follows because a finite ReLU network has finitely many polyhedral pieces. State invertibility almost surely, finite second moments, and \(V>0\). The factor-4 bound is valid. For channels, explicitly allow stochastic encoder kernels: sampling \(h_l\mid a\) preserves average power, but the finite-code nearest-neighbour derandomization does not establish this under a power constraint. Continuous-output lifting also needs a measurable right inverse.

3. **Major — [FORMAL.md §1.4, linear relevance](/home/agent/workspaces/mats/work/bit-accounting/FORMAL.md:66): the residual floor is false for linear-feature codes.**  
   Sending all coordinates of \(h_l\) uses linear features; a nonlinear decoder/fixed future can then recover \(a\) arbitrarily accurately. Already \(a=\operatorname{ReLU}(h)\) has a positive linear-regression residual despite this. **Fix:** restrict the assertion to affine prediction of \(a\), or explicitly study compression of the linear predictor. \(V-V_1\) is not a lower bound for the implemented linear encoders.

4. **Major — [FORMAL.md §1.4, active subspaces](/home/agent/workspaces/mats/work/bit-accounting/FORMAL.md:71): the Hermite identity uses the wrong measure.**  
   \(\operatorname{tr}E[\Sigma^{1/2}J^\top J\Sigma^{1/2}]=DV\) requires the Gaussian reference law and its Hermite decomposition. Actual hidden ReLU states are generally non-Gaussian. Nor does first-order distortion make reverse water-filling of the *averaged* Jacobian metric asymptotically exact. **Fix:** call this true-law gradient energy; reserve the Hermite identity for Gaussian sampling and retain only the local Taylor approximation without additional coding assumptions.

5. **Major — [FORMAL.md §3.1](/home/agent/workspaces/mats/work/bit-accounting/FORMAL.md:99), [smallnets.py](/home/agent/workspaces/mats/work/bit-accounting/gpu_src/lib/smallnets.py:56): the restricted quantity and implemented decoder differ.**  
   A fixed three-layer MLP is not unrestricted. Truncated whitening additionally forces reconstructions into \(m+\operatorname{range}(S^{1/2})\), and discarding positive eigenvalues loses encoder information. Consequently the inverse-\(W\) construction need not be admissible. The one-ReLU containment itself is correct with lossless whitening and an admissible decoder; inability to compute a generic two-layer future does **not** prove inability to attain its optimal distortion.  
   **Fix:** define the encoder, quantizer, preprocessing and decoder classes explicitly in \(b_l^{\mathcal E,\mathcal D}\). An affine encoder is a cleaner computational restriction. If “describe the state” is intended, add a state-reconstruction requirement or specify a future-independent encoder.

6. **Major — [PREREG.md S4](/home/agent/workspaces/mats/work/bit-accounting/PREREG.md), [run_noisy.py](/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/run_noisy.py:1): qualify what shared-noise bits measure.**  
   The count is rate-distortion under
   \[
   d_l(h,\hat h)=E_\Xi\|F_l(h,\Xi)-F_l(\hat h,\Xi)\|^2,
   \]
   equivalently compression of the random response function \(F_l(h,\cdot)\) in \(L^2(P_\Xi)\), with state-constrained reconstructions. Encoding the conditional mean generally loses information relevant to this metric. But noise alone does not guarantee a harder problem: for \(F(h,\Xi)=f(h)+Z(\Xi)\), noise cancels completely; at \(L-1\), no future noise remains. **Fix:** present shortcut blocking and the 1.5× spread as contingent hypotheses. The eight-draw side input is a randomized approximation, not exact \(E[a\mid h]\).

7. **Major — [smallnets.py:159](/home/agent/workspaces/mats/work/bit-accounting/gpu_src/lib/smallnets.py:159), [bitlib.py:287](/home/agent/workspaces/mats/work/bit-accounting/lib/bitlib.py:287): reported channel capacity lacks an enforced evaluation power constraint.**  
   Running normalization statistics do not guarantee \(E u_i^2\le1\) after training. Small-net evaluation does not even report power. Thus nominal \(C\) need not upper-bound transmitted information. **Fix:** freeze and calibrate normalization independently, validate power, and/or report the bound \(\frac12\sum_i\log_2(1+P_i\mathrm{SNR}_i)\). The theoretical §1.3 information inequality is otherwise correct.

8. **Major — [run_chain.py:136](/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/run_chain.py:136): the reported “best” fits are not the stated invariant optima.**  
   Optimal PTF and junta accuracies are invariant under independent input/output signed bit permutations. The implemented junta search is greedy: for \(Y=x_2x_3\), placing irrelevant \(x_1\) first gives two-junta accuracy **0.5**; permuting relevant bits first gives **1.0**. Logistic regression also does not maximize classification accuracy, and finite optimization supplies no optimality certificate. Majority ties forced to \(+1\) introduce another equivariance problem. **Fix:** enumerate subsets at these small widths, label PTF results as fitted lower bounds, and score conditional label probabilities or handle ties equivariantly.

9. **Major — [FORMAL.md §3.2](/home/agent/workspaces/mats/work/bit-accounting/FORMAL.md:114), [run_chain.py:369](/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/run_chain.py:369): matched input support is insufficient to establish scrambling.**  
   Baselines use the same observed codes and weights, which is useful, but differ in output bias, entropy and merging. A nearly constant learned bit can score highly without meaningful predictability. Uniform Walsh spectra can be dominated by arbitrary behaviour on unreachable codes; empirical coverage also misses rare reachable codes.  
   **Fix:** report constant-predictor accuracy, output entropy, held-out predictive performance and matched-output nulls. Full-bijection invariants include whole-code Bayes prediction accuracy, collision/fibre statistics and singular values of the normalized joint-probability matrix, not only entropy. They characterize dependence, not geometric circuit complexity. Hamming noise sensitivity is not invariant under arbitrary relabelling; whole-code disagreement probability is.

10. **Minor — [PREREG.md S2.2](/home/agent/workspaces/mats/work/bit-accounting/PREREG.md): the baseline sanity threshold is incorrect at \(b=8\).**  
    Expected Walsh mass at degrees \(\le2\), for either a random permutation output bit or a random invertible XOR row, is
    \[
    \frac{8+\binom82}{2^8-1}=\frac{36}{255}\approx0.1412,
    \]
    already above 0.1. **Fix:** use the dimension-dependent null distribution and its sampling variation.

11. **Minor — [run_noisy.py:86](/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/run_noisy.py:86): population inequalities are exact; the reported estimators are not.**  
    Population mean \(\le\) Gelbrich \(\le W_2^2\le\) CRN and mean \(\le\) avg \(\le\) CRN hold. The Gelbrich matrix formula is correct, but `torch.cov` uses \(N-1\), while CRN uses \(N\): for \(X=\{-1,1\}\), \(Y=2X\), the code gives Gelbrich **2**, CRN **1**. Use population-normalized empirical covariances for an exact empirical coupling bound.  
    The `avg` cross-product numerator is unbiased because reconstruction is held fixed across independent future noises; division by random `Ve` is not exactly unbiased. Report its own/paired SE. The pooled-mean pick-freeze estimator at line 125 also has finite-sample downward bias; use unbiased cross-covariance.

12. **Major — [run_chain.py:252](/home/agent/workspaces/mats/work/bit-accounting/gpu_src/scripts/run_chain.py:252): the deductive comparison understates both uncertainty and cost.**  
    `exact0` is exactly an empirical average of chain predictions over the reach sample. Its error against that same sample’s output mean has floor \(\operatorname{tr}\operatorname{Cov}(\hat a_{\rm chain}-a)/(PV)\), not generally \(1/P\). The factorized variants also estimate their initial law from this sample. `mc_equal_cost=2^-b` ignores law estimation, encoding and transition enumeration; even `mf` enumerates all \(2^b\) states. **Fix:** separate population bias from paired sampling error and compare measured, explicitly amortized computation costs.

13. **Major — [lincodes.py:44](/home/agent/workspaces/mats/work/bit-accounting/lib/lincodes.py:44): high-bit quantizer distortion is wrong.**  
    Above nine bits the code uses a uniform quantizer on \([-6,6]\), but supplies the high-resolution distortion constant for an optimal nonuniform Gaussian quantizer. Numerical integration gives approximately **4.41×** the tabulated distortion at both 10 and 12 bits. This changes greedy allocations and FSQ initialization. **Fix:** compute distortion for the actual quantizer, including tails, or implement the corresponding nonuniform quantizer.

14. **Major — [PREREG.md A1.2](/home/agent/workspaces/mats/work/bit-accounting/PREREG.md:40), [smallnets.py:188](/home/agent/workspaces/mats/work/bit-accounting/gpu_src/lib/smallnets.py:188): learned crossings are being used as theoretical bounds.**  
    A learned output count is an upper bound on its optimum; a layer code beating it is not necessarily a bug. Interpolated crossings are not demonstrated feasible rates, especially fractional binary counts. **Fix:** retain achieved integer/grid rates and uncertainty separately from interpolation. The Gaussian analog construction exactly attains the Gaussian distortion curve for any finite-covariance source, with enough channels; it does not prove that curve optimal for non-Gaussian sources. Likewise, asymptotic Gaussian successive refinement does not guarantee lossless finite nested neural codes.

15. **Minor — [smallnets.py:157](/home/agent/workspaces/mats/work/bit-accounting/gpu_src/lib/smallnets.py:157) and other sign quantizers: zero creates a third symbol.**  
    `torch.sign(0)==0`. This need not be a measure-zero event: \(z=\operatorname{ReLU}(x_1)-\operatorname{ReLU}(x_2)\) produces \(-1,0,+1\) on positive-probability regions. Analysis later maps zero to a binary index inconsistently. **Fix:** use one explicit binary threshold convention everywhere while retaining the intended surrogate gradient.

16. **Minor — [rwf.py:18](/home/agent/workspaces/mats/work/bit-accounting/lib/rwf.py:18), [bitlib.py:186](/home/agent/workspaces/mats/work/bit-accounting/lib/bitlib.py:186): numerical boundary handling changes answers.**  
    `rwf_rate([1], 0)` returns **100.5**, instead of infinity. A single float32 channel at \(C=64\) overflows SNR and produces NaNs. **Fix:** handle zero/negative distortion explicitly and compute channel reliability/noise scaling directly from \(2^{-2C_i}\), avoiding enormous SNRs.

Ordinary water-filling, active-set gradients, masks, nonzero-sign STE gradients, decoder initialization, nMSE reductions and the reported paired mean-error floor passed the inspected checks. No files were modified.
