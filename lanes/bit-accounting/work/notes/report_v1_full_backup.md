# How many bits each layer needs, and whether they get scrambled (bit-accounting lane, 1-2 November 2026)

Status: REPORT v1 (02:50Z). Plan changed at 02:55Z (Kelvin): phase 1, the best bits-vs-accuracy curve of every
layer (one lambda-conditioned variable-rate code per layer and class, with certificates on every curve), is now the
only priority; it is registered as PREREG Part P1 and running on the small nets and the controls. The phase-1 results
will replace sections 1-3 below; the scrambling and estimation parts (4-7) wait for phase 2. Round-1 review (theory,
code) applied; round-2 review pending.

Lane: bit accounting and the scrambling test, target M1 (bead pool-qxszj1.25). Work directory work/bit-accounting/:
FORMAL.md (theory; v1.2 corrections after review), PREREG.md + prereg_hashes.txt (13 registered parts), notes/
DEVIATIONS.md, GPU-LOG.md, results/ (tables and scores), runs/ (raw JSON), figs/. Labels: PROVEN, MEASURED, HEURISTIC.

## Summary for Kelvin

1. **With an encoder that can compute anything, every layer needs exactly the output's own bits, and the bits do not
   move between layers.** The output is a fixed function of the state at any layer, so such an encoder can compute
   the output, compress it and send that (PROVEN; MEASURED: with the encoder choosing its own bits, the unrestricted
   code at the input layer of 16 x 16 and 32 x 32 uses 2.6 and 2.0 bits for 10% error, against 3.0 and 1.9 for the
   output itself). This is the shortcut: it counts the output, and all the work sits in the encoder.
2. **Without the shortcut, early layers need many more bits than the output has.** With an encoder that can do one
   layer's work (one ReLU layer as wide as the net), ARC 256 x 32 needs more than 256 bits at l <= 4 for 10% error,
   135 at l = 8, 43 at l = 16 and about 25 from l = 24 on, where the output itself needs 19-39. Narrow-deep 8 x 256:
   15 bits at the input against 1.7 from layer 8-32 on. The L = n small nets: more than 32 bits at the input against
   2-3. Near the output a local description costs what the output costs.
3. **The compressed bits are not scrambled.** In chains of codes trained jointly across layers, whatever part of a
   next-layer bit the current code predicts at all, a linear threshold function of the current bits predicts (a median
   96% of the predictable part, held out; 9-27% after randomly relabelling the same codes). Real-valued codes: the
   layer-to-layer maps are 74-98% linear (degree-1 share; a random sine map scores 2%). On ARC the output-relevant
   coordinates of consecutive layers are related almost linearly (R^2 0.72 to 0.995 from l = 8 to the output).
   [Positive controls (chaotic tanh, Feistel circuit) through the same pipeline: pending in v2; until they light up,
   "not scrambled" means "the tests found low degree", not yet "the tests could have found high degree".]
4. **But every step is lossy, and the loss is information, not noise.** The next code is predictable from the current
   one only 8-37% of the time as a whole (at 16 bits). It knows things the current code does not (its encoder sees one
   more layer), and translating the current code into the next code's cells loses part of what the current code had.
5. **Your curriculum autoencoder** recovers the output's bits from layer L/4 on (6.5-10 bits); at the input layer the
   autoencoder stage is useless for the output (error 0.96-2.4) and the encoder never learns the shortcut; without the
   reconstruction floor the code drifts away from describing the state.
6. **Noisy nets scored with the same future noise:** the shortcut is blocked, and the count follows the layer's memory
   (16 x 16: 1, 2, 7, 10, 19 bits at l = 0, 4, 8, 12, 15). Matching each sample's path costs far more than the mean
   needs.
7. **Estimation:** propagating code laws through these chains leaves a bias of about 1e-3 to 1e-4 (in units of the
   output variance) that does not fall with more bits or points; plain MC passes it within 10^4 samples and RQMC far
   sooner. A compressed linear-Gaussian simulator gives the mean to ~1e-4 with 256 cheap evaluations (better than MC
   at that budget) and then stops improving. The obstacle is point 4, not scrambling.
8. **How the bits are counted matters less than how the encoder is trained.** With the encoder choosing its own bits
   (fixed-noise real codes, information rate), counts are close to the output's Gaussian bound; rounded integer codes
   with an entropy model need 3-5 times more; Bernoulli bits leave unneeded bits at p = 0.5 at zero cost, as you
   expected, but train less well; joint (vector) binary codebooks need no more bits than the Gaussian channel count,
   so the earlier binary overhead was encoder limitation (your correction confirmed). Fixed-budget sign-bit training
   is unreliable (a planted 8-bit target needs 12 learned bits; codes die at random rates), which is why every count
   is shown with the best code found and its certificate.

## 1. What is counted

- Nets: noiseless critical He-ReLU stacks, no biases, Gaussian inputs: ARC 256 x 32 (st.W_layer, seeds 4000-4003),
  narrow-deep 8 x 256 (the six healthy seeds), small nets 16 x 4, 32 x 8, 16 x 16, 32 x 32 (seeds 5000-5002), layers
  0, L/4, L/2, 3L/4, L-1 and output space; noisy Model S versions (sigma = 1) of 16 x 16 and 32 x 32; controls (S11).
- A bottleneck at layer l: encoder -> code -> decoder -> a state at layer l -> the real rest of the net -> output;
  nMSE = E|a_hat - a|^2 / tr Var(a); the output-mean error |mean(a_hat - a)|^2 / tr Var(a) is reported too (it is
  below nMSE/10 on 99.5% of 937 resolved points, S1.7).
- Primary count (your decision, 02:00Z/02:10Z): the encoder chooses its bits. A real-valued code with fixed unit
  Gaussian noise and an encoder-chosen scale; loss = forward-propagated nMSE + lambda x rate, rate = information
  estimate E[log2 q(z|h) - log2 p(z)] with a learned prior; the average bits used at 10% (1%) error is the count.
  Arms on the same cells: Bernoulli bits costed by H(mean p) - mean H(p); rounded integers with an entropy model;
  VIB. Earlier fixed-budget counts: sign bits, a water-filled channel with the capacity formula, multi-level scalar
  (FSQ) codes, explicit codebooks (VQ), and untrained linear transform codes.

## 2. The shortcut, in plain words

The output of a noiseless net is a fixed function of the state at any layer. So an encoder at layer l that may run the
rest of the net can compute the output, compress it, and send that; the decoder then only has to find some state at
layer l with that output. This always works and costs the bits the output itself needs, whatever l is (PROVEN, FORMAL
1.2 and 4.1: the best loss at layer l equals the output's best loss with reconstructions restricted to outputs
reachable from layer l). In that world nothing gets scrambled, because nothing moves: one code can serve every layer
(FORMAL 4.2); training does not find that identity chain by itself (section 4.1).
That count is right, but it describes the output, not layer l: the whole net's work has moved into the encoder. To ask
what layer l itself carries, the encoder must not be able to run the rest of the net. Two ways:
1. restrict the encoder to one ReLU layer as wide as the net ("local"); it can compute the next layer exactly but not
   two in general; the decoder stays unrestricted;
2. put noise in the future layers and score with the same noise for the original and the decoded state (your "same
   random seeds"): there is then no single answer the encoder could compute and send.

## 3. Bits per layer

### 3.1 The encoder chooses its bits (S7, primary; 16 x 16 and 32 x 32, first cells of seed 5000)
| net | l = 0 local | l = 0 unrestricted | L/4 local | output's own (Gaussian bound / VQ / Shannon-type lower bound) |
|---|---|---|---|---|
| 16 x 16 | > 25 (nMSE 0.15 at 25 bits) | 2.6 | 3.4 | 3.0 / 3.2 / 1.4 |
| 32 x 32 | > 26 (nMSE 0.27 at 26 bits) | 2.0 | 2.3 | 1.9 / [v2] / 1.6 |
At 1% error: 32 x 32 unrestricted 8.4 bits at l = 0 (Gaussian bound 6.0). Checks: a fresh prior refitted on held-out
codes lowers the rate by 1-7% (median 2%); the code scale chosen by the encoder grows from 0.03-0.06 at the largest
lambda to 2.7-2.8 at the smallest. Arms at the same cells, bits for 10% error: Bernoulli (information cost) does not
reach 10% within its sweep (it peaks at 6.5 bits of information, nMSE 0.28); VIB 1.9-3.2 (same as the fixed-noise
code); rounded integers with an entropy model 9.6-13.9 (3-5x more). [v2: all layers, three seeds, the small nets.]

### 3.2 Fixed budgets, all nets: without the shortcut early layers need many more bits (MEASURED)
Best local code found for nMSE 0.1 (channel bits, median over nets; results/A1_table.md, S1_best.md):

| net | l = 0 | L/4 | L/2 | 3L/4 | L-1 | output's own count |
|---|---|---|---|---|---|---|
| ARC 256 x 32 (l = 0, 8, 16, 24, 31) | >256 | 135 | 43 | 25 | 24 | 25 |
| narrow-deep 8 x 256 (l = 0, 64, 128, 192, 255) | 15 | 1.6 | 1.7 | 1.6 | 1.7 | 1.7 |
| 16 x 4 | 22 | 15 | 12 | 10 | (= 3L/4) | 10 |
| 32 x 8 | >32 | 21 | 11 | 8 | 8 | 9 |
| 16 x 16 | 27 | 6 | 4 | 3 | 3 | 3 |
| 32 x 32 | >32 | 5 | 2 | 2 | 2 | 2 |

ARC also needs > 256 bits at l = 2 and 4. At 1% error ARC needs > 256 bits at every l <= 8, about 210 at l = 16, 119 at
l = 24, 135 at l = 31; the best codes at l = 24-31 beat the Gaussian bound on the output (median 170), so the output's
own count at 1% is at most about 114-168 bits on these nets; at 0.1% every ARC layer needs > 256 (Gaussian bound
404-500). Narrow-deep: the state is a ray from layer 8-32 on, so the output is one number times a fixed vector: 1.7,
3.3, 5.0 bits for 10%, 1%, 0.1%. An unrestricted encoder (shown the exact output) needs the same bits at every layer
of the small nets up to training (flat curves in figs/bits_by_layer.png; 1500 steps 4.6-5.9, 3000 steps 2.4-3.5 against
the output's 1.9-3.0).
Comparisons asked for in the brief:
- The relevance lane's linear-feature count N(l, 0.1) on ARC (208, 96, 56, 20, 12, 12 at l = 0, 4, 8, 16, 24, 31):
  about 2 bits per direction at l >= 16, many more where linear features are not enough.
- Gaussian reverse water-filling over the output covariance gives the output-space channel count exactly (19-39 bits
  at 10%, four ARC nets; learned output codes within 1-2%, A1.1). Over the true-law gradient-energy spectrum of layer
  l (the local high-resolution price) it predicts the local count within a factor 1.3 at l >= 8 and overprices early
  layers (334-770 bits where the measured count is > 256) (HEURISTIC, FORMAL 4.4). The degree-1 relevance spectrum
  prices only the linear part (FORMAL 4.3).

### 3.3 Are the counts converged? (certificates)
- Known answers. (i) Output codes against the Gaussian bound: ARC learned output codes match it within 1-2%; the
  small-net learned output codes (no linear start) sit 0.5-2.4 bits above it (training). (ii) Unrestricted against
  the output's count: flat but 1.5-2.5x high at 1500 steps, within 0.5-1 bit at 3000 steps or with the S7 objective.
  (iii) Planted toy (a target that depends on exactly k sign bits): sign-bit training measures 2, 4-6 and 12 bits for
  k = 2, 4, 8 (unrestricted); the one-ReLU-layer encoder, which can represent the answer exactly, plateaus at nMSE
  0.08, 0.17 and 0.61 (S5.1 missed). Sign-bit training has real optimisation overhead.
- Quantiser optimality (S5, l = 0 and 4/8 so far): the per-code centroid improves on the learned decoder by <= 2% on
  97% of points (decoders are optimal for their encoders); one unrestricted Lloyd step cuts the error a lot (by > 20%
  on 93% of points, 6-30x at 8-16 bits), but re-training the local encoder to emit those codes recovers less than half
  of that on 94% of points (S5.5). So at early layers the local count is set by the restriction, not by optimisation.
  Restarts: sign-bit counts vary by more than 1.5 bits between restarts on 3 of 5 cells (dead codes at random rates,
  S5.4 missed).
- Joint quantisation (S6; 2^b-vector codebooks): b_VQ(10%) = 5.6, 7.5, 8.2 (16 x 4), 7.9, 6.7, 8.0 (32 x 8), 3.2
  (16 x 16) against Gaussian bounds 6.3, 12.3, 10.2, 8.7, 7.0, 10.4, 3.0: a joint binary index needs no more bits than
  the Gaussian channel count (below it on 6 of 8 nets; S6.2 missed in that direction). The earlier binary overhead (b/C
  ~1.3-1.4 for per-coordinate codes, 2-3x for learned sign bits) was encoder limitation; reachable codebooks (actual
  outputs as reconstructions) cost < 0.5 bit more on 6 of 8 nets.
- Bounds on the output's own rate (results/bounds_small.json): Shannon-type lower bound from the top 1-3 principal
  projections and the Gaussian upper bound: 16 x 16 1.2-1.4 <= R(10%) <= 1.9-3.4; 32 x 32 1.5-1.6 <= R <= 1.7-2.8;
  16 x 4 1.7-3.0 <= R <= 6.3-12.3; 32 x 8 2.4-3.4 <= R <= 7.0-10.4.

## 4. Do the bits get scrambled?

### 4.1 Binary codes in jointly trained chains (S2: 44 local and 12 unrestricted transition cells, held out)
- Whatever part of a next-code bit the current code predicts at all, a linear threshold function of the current
  code's bits predicts: it captures a median 96% (88-100% on non-degenerate cells) of the gap between the constant
  predictor and the Bayes limit. After a random relabelling of the same codes (same joint statistics, geometry
  destroyed) the same kind of map captures 27% (local) and 9% (unrestricted). Degree-2 maps add almost nothing; 3-input
  juntas come close but stay below: each next bit is a dense, smooth (threshold) function of many current bits.
- Registered in-sample statistics: degree-1 threshold accuracy >= 0.9 on 100% of cells and closer to the threshold
  baseline than to the permutation baseline on 99% (S2.1 hit). The exact Walsh spectrum over all 2^b codes reaches 0.8
  weight at degree <= 2 on only 39% of cells (S2.2 missed): it includes the transition's arbitrary behaviour on
  unreachable codes (coverage 0.2-14% at 16 bits), which the held-out statistics exclude.
- Unrestricted chains did not become identities (S2.3 missed): training does not find the identity chain that exists
  (FORMAL 4.2); their transitions are threshold-like too.

### 4.2 Real-valued codes (S9, 16 x 16 local chain so far)
Each learned map between consecutive layers' codes is 74-98% linear (degree-1 share in the Gaussian convention; fit
R^2 0.86-0.97), and each output coordinate depends on 3-8 of the 8 inputs: dense and smooth. Baselines: random linear
map 0.99-1.0, random sine map 0.02 (S9.1, S9.2 hit). The fixed isotropic noise pins the code coordinates up to
rotations and shifts, and these statistics are invariant to both.

### 4.3 ARC's output-relevant coordinates (B-ARC; dev net 9100 complete, 4000 partial, 4001 [v2])
Between consecutive layers the whitened output-relevant coordinates map almost linearly: R^2 of the best linear map
0.82 (8 -> 12), 0.87, 0.90, 0.92, 0.97, 0.97, 0.98, 0.99 (30 -> 31) on the dev net, 0.87-0.91 for the first pairs on
net 4000; an MLP adds at most 0.09. Their sign bits follow threshold maps (within 0.01-0.015 of an MLP) and mostly one
to one. Under an input perturbation of correlation 0.999 the fraction of flipped sign bits grows from 0.038 at l = 8
to 0.10 at the output: gradual, not an avalanche (B-ARC registered predictions scored in v2).

### 4.4 The loss is information, not noise
At 16 bits the whole next code is predictable from the current one only 8-37% of the time (82-93% per bit). One-step
decoding separates two losses (results/S2_posthoc_table.md, 14 transitions):
- the next code knows more than the current one (median gain 0.019 nMSE, up to 0.17: 0.35 -> 0.18 on 32 x 8's first
  step), because its encoder sees the state one layer later;
- the best prediction of the next code from the current one decodes worse than the current code itself (median loss
  0.034, 0.007-0.084): the two codes' cells do not nest, so each translation loses part of what the current code had.
The next code is a deterministic function of the state, so none of this is randomness; if the unpredictable bits were
output-irrelevant (training noise), the predicted code would decode about as well as the true next code, and it
decodes worse than even the current code.

## 5. Your curriculum autoencoder (S3: 16 x 16 three nets, 32 x 32 two nets)
Phase A plain autoencoder of h_l with 32 bits; phase B weight moves to the far horizons; phase C the budget shrinks
from 32 to 8 bits; reconstruction floors 0 and 0.05 (results/S3_table.md).
- The autoencoder stage alone is useless for the output at the input layer: 32 bits reconstruct x to 52-75% error in
  its own metric, and the output from the decoded x is worse than predicting the mean (nMSE 0.96-2.4).
- Moving the weight to the far horizons fixes this from l = L/4 on: 6.5-10 bits for 10% error (the output's own count
  is 2-3). At the input layer the encoder (it sees only x) never learns the shortcut: still > 32 bits.
- Shrinking the budget at the end does not lower the counts.
- Without the floor the code drifts away from describing the state (reconstruction error 0.12 -> 0.31 at l = 4, 0.20
  with the floor); that drift is toward the shortcut, which it does not reach at these depths (S3.1 missed: the drift
  is weaker than registered).
- Its transitions are threshold-like on reachable codes too (degree-1 accuracy 0.95-1.0 against 0.58-0.95 for a random
  permutation on the same codes).

## 6. Noisy nets scored with the same future noise (S4; 16 x 16 and 32 x 32, sigma = 1, three seeds)
The decoded state runs through the real future with the same noise as the original. The count becomes layer-dependent
for the unrestricted encoder too, in the direction of memory: 16 x 16: 1, 1.8, 7.1, 10.4, 18.9 bits for 10% error at
l = 0, 4, 8, 12, 15 (output 18.6), tracking the memory share 0.00, 0.04, 0.16, 0.55, 0.99; 32 x 32: 1, 1, 2.1, 15.6 at
l = 0, 8, 16, 24 (S4.2 hit). The local encoder needs more at l >= L/2 (S4.3 hit). The three scores are exactly nested
on all 1240 points (S4.1 hit): the per-sample shared-noise error is 3-30x the noise-averaged error of the same code, and
the output law (Gelbrich distance <= 0.01) and the output mean (error 1e-6 to 2e-4) are matched far better. So the
shared-noise score blocks the shortcut, but it asks for each sample's path, which is much more than the mean needs.

## 7. What it means for estimation
- Code propagation through the binary chains (local class; exact pushforward over all 2^b codes from the exact or
  factorised law of the input code): error of the mean 6e-4 to 0.1 at b = 4-16 with no downward trend in b
  (results/S2_table.md). Plain MC at the same number of evaluations has error 2^-b (measured N x error 0.3-1.6): the
  deductive estimate wins only at b = 4 and loses by 60-5000x at b = 16, and by more at equal compute (each code
  evaluation runs MLPs costing 30-400 MC samples).
- Compressed simulator with linear-Gaussian code dynamics (S10): the code law propagates in closed form and the last
  decoder is integrated over 8 dims; error 8e-5 (16 x 16) and 1.1e-4 (32 x 32) already at 256 points and flat to 65536
  (a bias floor, S10.2 hit). MC on the net reaches the same error at about 1e4 samples and RQMC (scrambled Sobol,
  2-22x better than MC on these nets) at about 10^3. Its per-layer fit costs little relative to free (MLP) dynamics:
  final nMSE 0.29 against 0.23 (16 x 16) and 0.48 against 0.41 (32 x 32), dominated by the 12-bit linear input code.
- The reason is section 4.4, not scrambling: the transitions are simple, but no step can add what the next layer's code
  knows and each step loses some of what it had. A deductive estimator would need an input code that already holds
  the output's bits, which is the problem itself; local input codes need far more bits than the output has (3.2).
- In the noisy regime the mean depends on the early state only through the noise-averaged map, whose error is tiny at
  low rates, so for the mean the relevant count is the noise-averaged one, not the shared-noise one (section 6).

## 8. Pre-registration scorecard (v1; final in v2)
- A1 (ARC): A1.1, A1.3, A1.5, A1.6, A1.7, A1.8, A1.9, A1.10, A1.11 hit; A1.2 missed (mis-specified: a layer-24/31
  code can beat a learned output-space code, which is not a bug, FORMAL 4.8); A1.4 missed.
- A2 (narrow-deep): A2.2 hit; A2.1 missed (3 of 6 nets have a layer >= 32 more than 0.6 bit above the one-number
  value: heavy-tailed radius, Gaussian quantiser design).
- S1: S1.2, S1.4, S1.5, S1.7 hit; S1.1, S1.3, S1.6 missed (learned sign/channel codes undertrained at 1500 steps).
- S2: S2.1 hit; S2.2, S2.3, S2.5 missed (see 4.1, 4.4).
- S3: S3.3 hit; S3.1, S3.2, S3.4, S3.5 missed (section 5).
- S4: S4.1, S4.2, S4.3 hit.
- S5-S10 (partial): S5.2, S5.3, S5.5, S6.1, S6.3, S9.1, S9.2, S10.2 hit; S5.1, S5.4, S6.2 missed; S7, S8, S10.1 pending.
- B-ARC (nets 4000, 4001; results/BARC_scores.json): BA.2 hit (sign-bit transitions within 0.03 of an MLP for every
  pair from l = 16 on); BA.1 missed (consecutive pairs from l = 20 on have linear R^2 0.91-0.997, but 16 -> 20 on net
  4001 is 0.885 and the multi-step pairs 16 -> 24 and 16 -> 32 are 0.80-0.88, with MLP gains up to 0.08); BA.3 missed
  narrowly (sign flips at rho = 0.999 grow by 2.02x and 2.29x from l = 8 to 31: gradual, but above the registered 2x).
- S11: deferred to phase 2 (plan change 02:55Z); S11 S7 reference rates are in runs/S11_*.

## 9. Process
- Plan changes by main/Kelvin during the night: small nets on a GPU first (23:05Z); Kelvin's curriculum (S3, 23:4xZ);
  shared-noise scoring (S4); convergence certificates (S5) and joint quantisation (S6, 01:3x-01:4xZ); the encoder
  chooses its bits (S7, 02:00Z, real-valued at 02:10Z) with Bernoulli and real-valued scrambling arms (S8, S9);
  simple-dynamics simulator (S10, 02:25Z); net-level controls (S11, 02:40Z). Each was registered before its runs.
- Deviations (notes/DEVIATIONS.md): training steps cut (6000 -> 3000 -> 1500) for GPU time; two spot preemptions
  (results restored); CUDA OOM with 16 processes (jobs rerun with a memory gate); some unrestricted chains skipped for
  seeds 5001-5002; the straight-through surrogate standardised after dead codes; analysis on the monotone envelope.
- Compute: CPU at nice 19 (ARC, narrow-deep, linear codes, analyses); GPU: spot L4s bitacct-2 (1.17 h, preempted),
  bitacct-3 (preempted before ready), bitacct-4 (4 h); cost so far about $5 at list price (GPU-LOG.md), cap $15.
- Review: gpt-6-astra round 1 on FORMAL and the code (major revision, 16 findings, all applied or answered in FORMAL
  4.1-4.8 and the code); round 2 on this report pending.
