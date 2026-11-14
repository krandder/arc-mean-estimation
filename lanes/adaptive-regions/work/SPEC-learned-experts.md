# Learned linear experts for internal means: experiment spec (v1 DRAFT, 2026-11-02, for Kelvin's review)

Single source of truth for the step-4 experiment. It supersedes every earlier message about step 4. Nothing scored
runs until (1) Kelvin has reviewed this spec, (2) the known-answer tests in section 6 pass, and (3) an independent
reviewer has checked the code against this spec.

## 1. Goal (Kelvin's words, 2 Nov)
- "a gaussian mixture inspired model for the linear experts": weights of each input to each expert via a distance;
  each expert predicts linearly the internal means of the next layer, with its own confidence.
- "Weighting them by confidence (inverse variance) ... I think this is actually what we need. We need to predict the
  next layer's state, or maybe skipping layers if that is possible to learn effectively."
- "We need to learn the experts in such a way that this actually turns out to be a good approximation ... maybe we
  need to train with batches of inputs, not with inputs."
- "Weights learned from samples of this same net."
Question: can a learned family of linear experts propagate populations of inputs well enough that its estimate of
the output mean for the full input distribution beats sampling at equal compute?

## 2. Nets and data
- ARC's noiseless family: h_0 = x ~ N(0, I_n), h_l = relu(W_l h_{l-1}), W_l iid N(0, 2/n), no biases.
- Dev: 32 x 4 and 64 x 8 (fresh dev seeds). Scored: 128 x 16 ladder nets, then 256 x 32 nets 200-204 (truths:
  2^26-sample noiseless truths via work/arc-update lib/au.py).
- Training data: inputs from N(0, I) and from the population Gaussians below, pushed through the true net; all
  states h_0..h_L stored. Every sample used for training counts as compute in section 5.

## 3. Definitions
- **Population.** A Gaussian over inputs, N(mu, S). Inside propagation, a population at layer l is a list of
  components (mass, mean, covariance) over layer-l states.
- **Internal mean** of a population P at layer l: m_l(P) = E_{x ~ P}[h_l(x)]. The estimand is m_L(N(0, I)).
- **Projection.** Per layer, Pi_l = the top d = 32 directions read by the downstream net (from backward passes on
  training data). Gates and covariances live in this projection plus a diagonal remainder.
- **Expert** e with source layer l and target layer l + s, s in {1, 2, 4, 8}:
  - gate (input fit): g_e(h) = pi_e N(Pi_l h | c_e, C_e) / sum over experts of the same source layer and target
    (a soft nearest-centroid; sums to 1);
  - linear map: prediction A_e h + b_e, with A_e = B_{l,s} + U_e V_e^T (shared base plus rank r <= 32 correction);
  - confidence: R_e = residual covariance of h_{l+s} - (A_e h_l + b_e) on the expert's samples (low rank + diagonal).
- **Fusion at a point** (generalised product of experts, Cao and Fleet 2014): with beta_e = g_e(h),
  precision Lambda = sum_e beta_e R_e^{-1}, mean = Lambda^{-1} sum_e beta_e R_e^{-1} (A_e h + b_e).
  Predictions of the same target layer from different sources (the chain s = 1 and skips s = 2, 4, 8) are fused the
  same way, with each route's weight = its gate weight times a learned route weight (normalised).
- **Propagation of a component** N(m, S) at layer l: for each expert, its overlap w_e = E_{h ~ N(m, S)}[g_e(h)] and the
  gate-reweighted moments (m_e, S_e) of the component; the expert's predicted moments A_e m_e + b_e and
  A_e S_e A_e^T + R_e; fused across experts with beta_e = w_e (normalised). A component whose two largest overlaps both
  exceed 0.2 is split into its gate-reweighted parts; components are merged by moment matching above the cap K_pop.
- **Estimate**: the mass-weighted mean of the propagated components at layer L. Model-only first; the unbiased
  variant adds the sampled mean of f(x) - (model's pointwise prediction) on fresh samples.

## 4. Training
1. Warm start: per-sample EM on pairs (Pi_l h_l, h_{l+s}) for every (l, s): gates, maps, confidences.
2. Population loss, end to end through the propagation (gradient descent):
   populations P_b = N(mu_b, sigma_b^2 I) with mu_b ~ N(0, I) and sigma_b in {0.03, 0.1, 0.3, 1}, plus N(0, I);
   empirical moments per layer from M_b fresh samples per population;
   loss = sum_b sum_l [ |m_model - m_emp|^2 / tr Var_l + covariance mismatch (in Pi_l) + calibration NLL of m_emp
   under the model's predicted uncertainty, with m_emp's own sampling noise included ].
3. Curriculum: small sigma_b first, then wider.
4. Size: K experts per (source, target), K in {2^4, ..., 2^12}; ridge strength and rank r chosen on held-out data;
   enough samples that K = 2^12 is not data-limited (1M+ paths at 256 x 32).

## 5. Metrics, in this order
1. Population-mean error (normalised) against population width sigma_b, per layer and at the output, on held-out
   populations; per-sample-trained against population-trained experts at equal K.
2. Error against K per source layer (input, L/4, L/2, 3L/4, L-1): where it saturates.
3. The estimand m_L(N(0, I)): nMSE against the truth, compared with RQMC at equal flop-counted compute, counting all
   training samples and the propagation's cost.
4. Calibration: predicted uncertainty against actual error.
5. Error correction: per-layer errors of local-only against end-to-end trained experts.
6. Pointwise residual Var(f - g) / Var f (secondary).

## 6. Known-answer tests (all must pass before any scored run)
- T1 linear net (no ReLU): K = 1 reproduces the exact mean and covariance at every layer.
- T2 one ReLU layer, n = 4, gates aligned with the four unit hyperplanes: propagated mean within 1e-3 of the exact
  rectified-Gaussian mean (closed form).
- T3 K = 1, one layer: equals the linear regression estimator.
- T4 tiny populations (sigma_b -> 0): population-mean error tends to the pointwise error at the centre.
- T5 planted data from a known 2-piece linear map: the fit recovers it.

## 7. Process
- This spec is frozen and hashed after Kelvin's review; changes go in a dated amendment.
- The implementation is checked against it by an independent reviewer (gpt-6-astra, model line verified) before any
  scored run. Predictions go in a hashed PREREG.
- Reports lead with metric 1, in plain words.

## 8. Defaults Kelvin may change
d = 32; r <= 32; s in {1, 2, 4, 8}; sigma_b grid; split threshold 0.2; K_pop cap 64; K grid; model-only first.

## Amendment A2 (Kelvin, 2026-11-02 ~17:05Z): track the final joint confidence
Kelvin: "for a given (already trained) population of experts, we could distinguish some prediction as high-confidence
or low-confidence ... we are not really keeping track of the 'final joint confidence' of predictions in any way ...
important in case we want to do further sampling of whatever parts we're not fully confident in; or ... we may just
be unable to tell correctly with the right bounds what the mean is, for some classes of input distributions ...
some kind of 'epistemics' of what our model can represent and what our model really cannot."
Also accepted: soft validity zones; gates on the 32 most-read directions as a simplification (to revisit).
- Every propagated component carries, besides its population spread S, an error covariance E of its predicted mean
  (the model's uncertainty about m, not the spread of states). E is propagated: E' = A E A^T + (fusion-weighted expert
  model error, from held-out residuals of the expert's mean predictions) + split/merge error terms.
- Output: for each population, the estimate plus an error bar from E at layer L, and a per-component breakdown
  (which parts of the input population the model is unsure about).
- Uses: (a) a hybrid estimator that spends samples only on the components whose error contribution is largest
  (sampling inputs restricted to those components), compared with RQMC at equal compute; (b) an explicit "cannot
  represent" verdict for populations whose error bar exceeds a threshold.
- Test (new metric 4, replaces the old calibration line): on held-out populations, the fraction of true means inside
  the stated 68% / 95% intervals, and the error bar against the actual error across population widths.

## Amendment A3 (Kelvin + reviews in work/idea-review/, relayed by main ~17:25Z; appended by the lane 17:35Z)
1. Propagation: contributions of sub-populations add by mass; confidence (gPoE) fusion only where experts overlap at
   the same input, and between routes (chain vs skips) for the same population part. Main's answer (same time):
   propagate by Monte Carlo draws through the POINTWISE fused map (confidence fusion at each draw; mass weighting
   across draws comes for free). Model the split error in E or report it separately. Integration test (GPT-6): freeze a
   small model, integrate its pointwise predictor accurately, compare with the propagation; check additivity
   F(pP + (1-p)Q) = pF(P) + (1-p)F(Q).
2. Oracle single-layer experts first (ceiling test): exact local linearisations from W (gates and Jacobians at K
   centres, zero training cost); propagate N(0, I) and the populations; error vs K at 32x4, 64x8, 128x16. Learning by
   sampling is then used for skip experts and composition, and compared against this ceiling.
3. d is a knob: sweep 16 / 32 / 64; report error vs K at each d.
4. Truth floor: the slope headline at 64x8 (and 32x4, 5 sizes; 128x16, 3 sizes), not at 256x32.
5. Price everything (propagation, optimisation), with M_b set explicitly.
6. T2 is a diagnostic if the gate family cannot represent half-spaces.
Also (main's answers): populations N(sqrt(1 - s^2) mu, s^2 I) (s = 1 is N(0, I)); many more training populations
(hundreds, small batches); run the oracle ceiling and the integration test and report them before any training run;
then the PREREG.

## Amendment A4 (Kelvin, relayed by main ~17:35Z): a second variant with an exact mean
Model: g_j(x) = sum_k h_kj exp(-1/2 (x - c_k)^T P_k (x - c_k)) (a_kj . x + d_kj), no normalisation across experts; bump
(c_k, P_k low rank in the downstream-read projection) = which inputs expert k knows; height h_kj = how much it speaks
for output j; per-output error variance s2_kj (held out) = its stated confidence. E_{N(0,I)}[g_j] is closed form.
Estimate = E[g] exactly + the importance-sampled mean of f - g, proposal a mixture of N(0, I) and the bumps of
low-confidence experts weighted by s2, exact density-ratio weights (unbiased, honest error bar).
Loss: fitted END TO END against the true outputs as functions of x (intermediate non-Gaussianity is part of the
function fitted): pointwise residual of f - g, plus a population-mean loss over many input populations, plus, as an
auxiliary teacher only, agreement with the composed layer-by-layer experts.
Report: leftover Var(f - g)/Var f and the estimate's error vs total compute (all training counted) against K, at 32x4,
64x8, 128x16; and the gain of the importance-sampled correction over uniform correction samples. Run after the oracle
ceiling.

## Amendment A5 (Kelvin's architecture, relayed by main ~18:15Z; overrides the Gibbs and accounting messages before it)
1. TRAINING may use sampling freely, Gibbs included, with both terms from the start: (a) a downstream-weighted fit of
   each conditional on real states; (b) samples of the model's joint at layer l, pushed through the real layers, must
   reproduce the true downstream and output means.
2. ESTIMATION is purely deductive: the trained representation (experts, pieces, internal means, confidences) is
   propagated forward with no sampling of the net; it is trained to approximate and to error-correct across layers
   (end-to-end population loss); the deductive internal means are trained to agree with what (b) measures.
3. SAMPLED CORRECTIONS only where the model is uncertain: certain parts get zero samples; uncertain parts get targeted
   correction samples (inputs drawn from the uncertain pieces, exact weights); the correction budget follows the
   propagated uncertainty.
4. Report on 32x4, held-out populations: the deductive estimate's error; the uncertainty's calibration; the error after
   targeted corrections vs estimation-time compute, against MC and RQMC.
Lane note on implementation: with the expert-indexed Gaussian-mixture representation the model's joint at layer l is
sampled directly (reparametrised draws from its components); Gibbs is not needed for it. Training compute is advice
(recorded, not charged); estimation-time compute is charged.
