### 5.1 Binary codes in jointly trained chains (S2: 44 local and 12 unrestricted transition cells, held out)
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

### 5.2 Real-valued codes (S9, 16 x 16 local chain so far)
Each learned map between consecutive layers' codes is 74-98% linear (degree-1 share in the Gaussian convention; fit
R^2 0.86-0.97), and each output coordinate depends on 3-8 of the 8 inputs: dense and smooth. Baselines: random linear
map 0.99-1.0, random sine map 0.02 (S9.1, S9.2 hit). The fixed isotropic noise pins the code coordinates up to
rotations and shifts, and these statistics are invariant to both.

### 5.3 ARC's output-relevant coordinates (B-ARC; dev net 9100, nets 4000 and 4001)
Between consecutive layers the whitened output-relevant coordinates map almost linearly: R^2 of the best linear map
from l = 20 on is 0.91-0.997 on nets 4000 and 4001 (0.92-0.995 on the dev net); 16 -> 20 is 0.885-0.914, and the
multi-step pairs 16 -> 24 and 16 -> 32 are 0.80-0.88, where an MLP adds up to 0.08 (BA.1 missed). Their sign bits
follow threshold maps within 0.03 of an MLP on every pair from l = 16 (BA.2 hit). Under an input perturbation of
correlation 0.999 the fraction of flipped sign bits grows from about 0.04 at l = 8 to 0.09-0.10 at l = 31 (factor
2.0-2.3; BA.3 registered at most 2, missed narrowly): gradual, not an avalanche (results/BARC_scores.json).

### 5.4 The loss is information, not noise
At 16 bits the whole next code is predictable from the current one only 8-37% of the time (82-93% per bit). One-step
decoding separates two losses (results/S2_posthoc_table.md, 14 transitions):
- the next code knows more than the current one (median gain 0.019 nMSE, up to 0.17: 0.35 -> 0.18 on 32 x 8's first
  step), because its encoder sees the state one layer later;
- the best prediction of the next code from the current one decodes worse than the current code itself (median loss
  0.034, 0.007-0.084): the two codes' cells do not nest, so each translation loses part of what the current code had.
The next code is a deterministic function of the state, so none of this is randomness; if the unpredictable bits were
output-irrelevant (training noise), the predicted code would decode about as well as the true next code, and it
decodes worse than even the current code.

### 5.5 Your curriculum autoencoder (S3: 16 x 16 three nets, 32 x 32 two nets)
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

### 5.6 Noisy nets scored with the same future noise (S4; 16 x 16 and 32 x 32, sigma = 1, three seeds)
The decoded state runs through the real future with the same noise as the original. The count becomes layer-dependent
for the unrestricted encoder too, in the direction of memory: 16 x 16: 1, 1.8, 7.1, 10.4, 18.9 bits for 10% error at
l = 0, 4, 8, 12, 15 (output 18.6), tracking the memory share 0.00, 0.04, 0.16, 0.55, 0.99; 32 x 32: 1, 1, 2.1, 15.6 at
l = 0, 8, 16, 24 (S4.2 hit). The local encoder needs more at l >= L/2 (S4.3 hit). The three scores are exactly nested
on all 1240 points (S4.1 hit): the per-sample shared-noise error is 3-30x the noise-averaged error of the same code, and
the output law (Gelbrich distance <= 0.01) and the output mean (error 1e-6 to 2e-4) are matched far better. So the
shared-noise score blocks the shortcut, but it asks for each sample's path, which is much more than the mean needs.

### 5.7 What it means for estimation
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
- The reason is section 5.4, not scrambling: the transitions are simple, but no step can add what the next layer's code
  knows and each step loses some of what it had. A deductive estimator would need an input code that already holds
  the output's bits, which is the problem itself; local input codes need far more bits than the output has (4.1).
- In the noisy regime the mean depends on the early state only through the noise-averaged map, whose error is tiny at
  low rates, so for the mean the relevant count is the noise-averaged one, not the shared-noise one (section 5.6).

