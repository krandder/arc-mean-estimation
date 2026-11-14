<!-- Extracted: the reviewer model's final message only. The full session dump is not in this repo. Source file: work/idea-review/gpt6_review.raw -->

1. **The strongest objection: the propagation rule need not integrate the predictor it learns.**

In the [spec](/home/agent/workspaces/mats/work/adaptive-regions/SPEC-learned-experts.md), gate-conditioned experts describe different subpopulations. Their contributions should add according to probability mass. Precision fusion instead treats them as estimates of the same quantity. Two equally probable subpopulations with means 0 and 2 contribute mean 1, regardless of which expert has smaller residual variance.

Confidence fusion can make sense **at the same input**. But integrating that fused predictor generally differs from fusing gate-conditioned means. Consequently, the advertised correction
\[
\widehat\mu_{\rm propagation}+\operatorname{average}(f-g)
\]
retains bias \(\widehat\mu_{\rm propagation}-E[g]\). Fresh residual samples do not remove it.

**Cheap test:** freeze a tiny trained model and independently integrate its pointwise predictor accurately. Compare that integral with propagation; also test population additivity, \(F(pP+(1-p)Q)=pF(P)+(1-p)F(Q)\). Use one-layer examples with exact ReLU means and unequal expert confidences. Measure this discrepancy separately from approximation error while increasing capacity.

A persistent discrepancy kills this propagation rule, not learned experts generally. Rescue requires consistent integration, or an explicitly controlled integration-error term. This is more informative than another expensive training run.

2. **What remains wrong or underdetermined.**

Several choices determine whether the experiment tests the idea fairly:

- **Gaussian gates do not imply Gaussian integrals.** Expectations of normalized Gaussian responsibilities generally lack closed forms; reweighted populations are generally non-Gaussian. Specify the quadrature or approximation, its cost, and its error.
- **“Final joint confidence” is not yet joint.** Routes share training data, inputs and upstream errors. The proposed covariance sum omits cross-covariances and systematic bias. Moreover, \(AEA^\top\) misses sensitivity through changing gates. Distinguish population spread, finite-training uncertainty and approximation bias. Normalizing product-of-experts weights does not establish calibration.
- **Population training needs a precise statistical target.** Specify loss coefficients, normalization near zero variance, batch sizes and treatment of noisy covariance labels. Including \(N(0,I)\) in training permits memorizing its empirical mean. Compare against directly averaging exactly those training evaluations; otherwise apparent learning could merely reorganize sampling noise.
- **Capacity is more than expert count.** Fixed \(d=32\), rank and \(K_{\rm pop}=64\) can become bottlenecks while \(K\) grows. “One million paths” does not establish adequate data for 4,096 experts: uniform occupancy gives only about 244 paths per expert, with fewer in rare regions.
- **Accounting must include optimization.** Charge repeated training passes, backward projections, gate integration, covariance algebra, split/merge operations, model selection and residual-model evaluations. One acquisition of a training path is not its entire training cost.
- **The slope headline needs safeguards.** Define error as MSE, not RMSE. Fit local slopes and a possible bias floor, retain independent training replicates, and evaluate final choices on fresh nets. Two decades can describe an optimization transient. At large budgets, the \(2^{26}\)-sample references’ roughly \(1.5\times10^{-8}\) normalized sampling-error floor also matters.

Accepting an initial compute disadvantage is reasonable. It does not justify extrapolating a transient slope to a crossover.

3. **Can this family beat sampling’s exponent for a fixed net? Yes in principle; useful improvement is unestablished.**

First distinguish ordinary MC from the best sampling method. For a fixed bias-free net, integrate radius analytically and work on the 255-dimensional sphere. The resulting function is Lipschitz. Ideal equal-area, small-diameter stratification gives MSE \(O(N^{-1-2/255})\): already an exponent above one, with dimension-dependent constants. Local experts with residual sampling can exploit related approximation rates. This establishes possibility, not practical superiority over RQMC.

For a learned surrogate, the relevant calculation is
\[
\mathrm{MSE}\approx b_{\rm int}(B)^2+
\frac{\eta(B)c(B)}{C-B},
\]
where \(B\) is construction cost, \(\eta\) residual variance, \(c\) residual-evaluation cost, and \(b_{\rm int}\) integration bias. With exact integration, \(B\) a fixed budget fraction, \(\eta(B)\sim B^{-\delta}\), and \(c(B)\sim B^\gamma\), the exponent is \(1+\delta-\gamma\). **Residual variance must fall faster than evaluation cost rises.** The simpler \(1+\delta\) claim assumes bounded evaluation cost.

High-dimensional approximation can make \(\delta\) tiny; fixed representation bottlenecks can make it zero. Neither possibility proves failure for this particular net.

The “\(W\) identifiable after approximately \(nL\) evaluations” argument is invalid as stated and is explicitly withdrawn in the [final pre-integration report](/home/agent/workspaces/mats/work/preint/preint.md:290). Counting parameters and output coordinates is not an identifiability theorem: finite queries can miss activation regions, and parameter symmetries also exist. Whether typical random nets admit efficient functional recovery needs a separate argument. Here \(W\) is already supplied, so the substantive obstacle is computation, not obtaining its information.

4. **More promising untried directions.**

**Replace normalized gates with analytically integrable expert features.** Try sums of affine functions times *unnormalized* Gaussian bumps, whose Gaussian-input means are computable. This sacrifices probabilistic routing semantics but preserves local linear experts and removes the disputed integration step. Measure residual variance times evaluation cost as capacity grows. It is a cleaner test of whether local experts capture useful structure.

**Learn Gaussian Stein controls.** For sufficiently regular vector fields,
\[
E[\nabla\!\cdot v(X)-X^\top v(X)]=0.
\]
Fit such controls to reduce output residual variance, with independent correction samples. This permits learned nonlinear structure without estimating region probabilities. Use shared, low-rank output structure and charge derivative costs. I found no test of this estimator in the requested evidence; there is no guarantee it escapes the dimensional bottleneck.

**For a convincing negative, target the representation explicitly.** Construct distributions with the same retained moments and projected information but different downstream means. Such a pair bounds what any decoder of that representation can achieve, regardless of training. The difficult, necessary extension is showing that these ambiguities matter for reachable clouds of typical He nets. That would be substantially stronger than another optimizer failing.

5. **What the evidence overstates.**

The synthesis predates material corrections. Its \(nL\)-identification claim should disappear; its sampling bounds must use the final point-versus-line distinctions and ensemble normalization. Infinite-width spectra do not automatically certify finite-width ceilings at \(L=n/8\).

The [board investigation](/home/agent/workspaces/mats/work/phase1-board/FINDINGS.md) resolves C10 operationally: use approximately **6× MC at equal charged cost** as the documented honest frontier. Preserve its distinction between verified earlier public-set fitting and inferred fitting of the final winning entry.

The learned-expert failures so far establish neither a population-mean approximation limit nor a scaling limit. Conversely, exact gate-cell explosion and large code lengths do not establish that soft integration is hard: integration can exploit cancellation.

The defensible update for ARC is narrower: tested closures incur substantial errors and costs at this shape, and new proposals must explain how they avoid them. “Hopeless” remains unsupported.
