
## Amendment S3-S4 (Kelvin's two schemes, relayed by main 23:4xZ; registered before any S3 or S4 run)

### S3: Kelvin's curriculum autoencoder (gpu_src/scripts/run_kelvin.py)
Per net (the four S1 configs, seeds 5000-5002), layers as S1, one code per layer (32 nested sign bits; encoder = MLP
with 3 hidden layers of width 256 on h_l only); decoders self (h_l), next (h_{l+1 on the grid}), out (a); losses recon,
next, out, fwd (decode to h_l, run the true net), fwdnext (decode to the next grid layer, run the true net). Schedule:
A (20%) recon only; B (50%) recon weight from 1 to the floor, the four other weights from 0 to 1; C (30%) bit budget
from 32 to 8. Floors 0 and 0.05 trained side by side. 4000 steps, batch 1024. Evaluated at the end of A, B, C at
b in {1..32}. Transitions T_i = sign(E_{i+1}(next_i(c_i))) analysed as in S2 (b = 4, 8, 12, 16).
- S3.1 (the shortcut without a floor). Phase-C recon nMSE of h_l at b = 32 is >= 2 x its phase-A value for floor 0 at
  >= 75% of (net, layer) cells with L - l <= 8; the same ratio is smaller with floor 0.05 than with floor 0 on >= 75%
  of those cells.
- S3.2 (fwd reaches the output's count where the encoder can compute the future). Phase-C fwd b_l(0.1) (floor 0) is
  within max(25%, 2 bits) of the S1 output-space b_out(0.1) of the same net at cells with L - l <= 4, on >= 75% of
  them; reported for deeper futures.
- S3.3 (horizons). Phase-C b^out_l(0.1) <= b^fwd_l(0.1) + 1 (floor 0) on >= 75% of cells where both are reached.
- S3.4 (separately learned bases look more scrambled). The degree-1 PTF accuracy of the data majority map of T_i is
  below that of the S2 jointly trained local chain at the same (net, b, transition) on >= 60% of matched cells.
- S3.5 (against the local arm). At l = 0 of 16 x 16 and 32 x 32, phase-C fwd b_0(0.1) (floor 0.05) <= 0.8 x the S1
  local b_0(0.1), or the local count is unreached while S3's is reached, on >= 4 of 6 nets.

### S4: the noisy regime with common random numbers (gpu_src/scripts/run_noisy.py)
Model S nets with input: h_0 = x ~ N(0, I_n), sigma = 1 on hidden layers, output noiseless; 16 x 16 and 32 x 32,
seeds 5000-5002; layers as S1 and the output space; classes local and unres (unres sees h_l and an 8-draw average of
the future output, not the future noise); 10 binary and 10 channel models per cell; 1500 steps x batch 2048; training
loss = the CRN score. Scores: crn (per-sample output match under the shared noise, primary), dist (Gelbrich W2^2
between output laws), mean (error of the output mean), avg (noise-averaged distortion |g(h_hat) - g(h)|^2); memory share
M_l by pick-freeze.
- S4.1 (nested scores; exact). mean <= dist <= crn and avg <= crn on every (cell, kind, rate) point, up to 1% + 3 SE
  (a violation is a bug).
- S4.2 (the shared-noise score blocks the shortcut). For unres, max_l C^crn_l(0.1) / min_l C^crn_l(0.1) >= 1.5 over the
  five hidden layers (a layer unreached while another is reached counts as >= 1.5) on >= 4 of 6 nets. Direction
  reported, not scored.
- S4.3 (local needs at least as much). C^crn,local_l(0.1) >= C^crn,unres_l(0.1) - 1 (or local unreached) on >= 75% of
  (net, layer) cells.
