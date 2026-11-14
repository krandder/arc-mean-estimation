# Backward bits: pre-registration (lane pool-qxszj1.27)

Registered before any scored run (seeds 5000-5002). Hashes of this file and of the code that produces and scores the
runs are in prereg_hashes.txt, with the UTC time of registration. Definitions and proofs: FORMAL.md.

## 0. What was seen before registration (dev seed 9100 only)
- CPU calibration (runs_dev/calib*.json): first-step erasure and the output-code information I(h_l; c_L) at a few layers
  for sigma grids and K_L in {16, 64}.
- CPU smoke runs (8x8, sigma 0.05, K_L = 16, tiny sizes; runs_dev/smoke): chain K and chain PR end to end, the truth pass,
  certificates, the Gaussian-channel and forward-trained scripts.
- GPU dev runs (seed 9100, full sizes; runs_gpu/dev, runs_gpu/dev2;
  stopped after the first steps to free the GPU). Output codes K_L = 64: nMSE 6.7% (16x16), 7.2% (16x8), 2.1% (8x8),
  0.4% (8x16); H(c_L) 5.4-5.8 bits. First backward step l = L-2: T = 4.85 (16x16), 4.83 (16x8), 4.09 (8x8), 3.72 (8x16)
  bits, erased 0.92-1.73. Rate rule there (chains K, P): the best code with H <= T carries 3.33-3.52 of 4.85 (16x16),
  3.16 of 4.09 (8x8), 2.78 of 3.72 (8x16), a deficit of 23-31% of T; restart and depth-4 codes agree within 0.05-0.09 bit
  (16x16). Chain P (16x16): target 4.85, 2.90, 1.60, 0.86, 0.44 bits at l = 14..10. Relevance rule (chain R) at l = L-2:
  H = 7.76 bits (256 cells) for I = 4.54 of T = 4.85 (16x16), H = 6.54 (128 cells) for 3.55 of 3.72 (8x16); at l = 13
  chain R's target is 5.33 (16x16) and 3.54 (8x16) against the calibration's I(h_13; c_L) of about 4.2 and 2.9, and
  its code hits the 512-cell cap (H = 8.91). Step times with 7 jobs sharing the GPU: 40-60 s (P), 100-170 s (R),
  about 250 s (K with certificates). A dev 8x8 run (all four chains, then the truth, Gaussian, forward and convergence
  passes) runs alongside the scored runs as a full-size test of the evaluation scripts; it is not scored.
No scored seed has been run or looked at.

## 1. Nets and the output code
Model S (FORMAL section 0): h_0 = x ~ N(0, I_n); h_l = relu(W_l h_{l-1}) + sigma xi_l for l = 1..L-1; a = relu(W_L h_{L-1});
W_l = st.W_layer(seed, n, l). Configs and sigma (chosen on dev so that the first backward step erases 0.5-2 bits of the
output code and the input keeps at least 1 bit; the 8-wide nets contract strongly with depth, so their sigma is small):
  8x8 sigma 0.01 | 8x16 sigma 0.0003 | 16x8 sigma 0.2 | 16x16 sigma 0.1.
Seeds 5000, 5001, 5002 (12 nets). Output code ("the last layer, trained until convergence"): k-means with K_L = 64 cells
on 2^18 outputs, k-means++ seeding, Lloyd to a relative change of 1e-9, best of 8 restarts; the code at L-1 is the
output code composed with the noiseless last layer.

## 2. The backward chains (scripts/run_chain.py)
Step l = L-2 .. 0. Target: K and R the next code c_{l+1}; P and PR the output code carried back one noisy layer
(rows P~_l(h) = E_xi Q_{l+1}[c_{l+1}(h_{l+1})], Q_{l+1} the cell table of step l+1, exact at L-1).
Target estimate T_l = H(target) - E_h H(target | h_l): N_te = 2^16 fresh points, M_te = 1024 draws of xi_{l+1} (two halves
of 512); Miller-Madow per point (K, R; Grassberger reported) or Richardson 2 H(M) - mean H(M/2) (P, PR).
Encoder class: posterior predictor (MLP, 2 hidden GELU layers of width 256, standardised input; soft-label cross-entropy,
Adam one-cycle lr 3e-3, 4000 steps, batch 8192) on N_tr = 2^17 points with M_tr = 64 draws each; then deterministic
IB quantisation of the predicted posteriors: candidates = KL-k-means over the K grid {2, 3, 4, 5, 6, 8, ..., 256}
up to Kmax (3 restarts each), the entropy-constrained 2-cell threshold family, and annealed DIB paths from 3, 8 and
Kmax cells (2 restarts, beta 1e4 -> 0.3 by x0.8, dominated solutions pruned on the training rows). Kmax = 2^(ceil T + 2)
<= 256 for the rate rule and 2^(ceil T + 3) <= 512 for the relevance rule.
Selection on a separate select set (N_sel = 2^15, M_sel = 256):
  rate rule (K, P):      the most relevant candidate with H_sel <= T_sel + 0.02;
  relevance rule (R, PR): the cheapest candidate with I_sel >= 0.95 T_sel (if none, the most relevant; flagged).
Reported on the test set: H(c_l) (Miller-Madow plug-in), I(c_l; target) (pooled cell posteriors, split-half Richardson
bias correction), deficit T - I, overhead H - T, the reuse baseline (c_{l+1}(relu(W_{l+1} h)), Kelvin's "use the last
encoding"), the Pinsker-spectral lower bound for codes with at most K cells (FORMAL section 4), and every candidate.
Per-step certificate runs (chains K and PR): an independent restart (fresh training points and draws, new seeds) and
predictors of depth 1 and 4; the look-ahead control (clustering the Monte Carlo rows themselves; chain K).

## 3. Output-level evaluation (scripts/run_truth.py, run_gauss.py, run_fwd.py, conv_check.py)
- Truth per layer: I*_l = I(h_l; c_L), N = 2^16 fresh points, M = 1024 draws of the whole future noise (Miller-Madow).
- Per chain and layer: H(c_l), I(c_l; c_L) (best decoder), I_chain = H(c_L) - CE of the chain's own prediction of c_L
  (K, R: product of the per-step cell kernels; P, PR: the step table).
- Direct (output-targeted, forward) codes: the same encoder class trained at each layer on the whole-future posterior of
  c_L, selected at the rate of each chain's code, at rate I*_l, and by the relevance rule against I*_l.
- Shared-noise output distortion crn = E|F_l(h_hat, Xi) - F_l(h, Xi)|^2 / V (same future noise, V = tr Var a) with the
  cell-mean decoder and a crn-optimised decoder (Adam on the cell states, 400 steps), the noise-averaged distortion
  (two independent future draws), and the 0-bit baseline; for every chain's code and the direct codes.
- Forward-trained codes (bit-accounting S4 style; run_fwd.py): K-cell codes trained directly on crn, K in
  {2, 4, 8, 16, 32, 64}, at layers L-2, 3L/4, L/2, L/4, 0: (H, I(c; c_L), crn).
- Gaussian-channel comparison (run_gauss.py, chain K, every step): z = u(h) + N(0, I_8), beta grid; rate by the
  Kolchinsky-Tracey bounds and the Monte Carlo mixture information (with and without leave-one-out, at N and N/2);
  relevance by the decoder bound and the mixture plug-in.
- Estimator convergence (conv_check.py, chain K, l = L-2, L/2, 0): T, H, I, I*, I_out at N in {2^15, 2^16, 2^17} x
  M in {256, 1024, 4096}.

## 4. Certificates and tolerances (per step; scripts/score.py)
C1 estimation: SE(T) <= 0.01 bit and |T_MM - T_Grassberger| <= 0.01 bit (K, R); for P, PR the Richardson correction
   is at most 0.05 bit.
C2 predictor: excess cross-entropy on the test set <= max(0.02 bit, 0.02 T).
C3 restart: rate rule |I_restart - I| <= max(0.03, 0.03 T); relevance rule |H_restart - H| <= max(0.15, 0.05 H).
C4 depth: rate rule I_depth4 - I <= max(0.03, 0.03 T); relevance rule H - H_depth4 <= max(0.15, 0.05 H)
   (a failure means a deeper encoder does better: "deeper encoders needed" at that step).
C5 look-ahead (chain K): the best look-ahead code with H <= H(c_l) + 0.02 carries at most 0.03 bit more.
C6 consistency: T_l <= H(c_{l+1}) + 0.01 and I(c_l; target) <= min(H(c_l), T_l) + 0.01.
A step is certified when every certificate that applies passes. Truth consistency: I*_l <= I*_{l+1} + 0.01.

## 5. Predictions (scored by scripts/score.py; thresholds fixed here)
Notation: I*_l = I(h_l; c_L) (truth); for a chain, T_l its target, H(c_l) its rate, I(c_l; target) its relevance,
I_out = I(c_l; c_L), I_chain = the chain's own prediction of c_L through its kernels. "Noisy steps" = l <= L-2.
Each prediction is scored on the 12 nets (or on all their steps), with the threshold fixed here.
B1 (the gap at Kelvin's rate, FORMAL Prop 2). Chain K: T_l - I(c_l; c_{l+1}) >= 0.1 T_l at >= 90% of noisy steps.
B2 (carrying the target needs extra rate, Prop 3). At l = L-2 (where chains R and PR coincide), the relevance-rule code
   has H(c_l) >= T_l + 1 bit on >= 10 of 12 nets.
B3 ("no layer exceeds its successor" fails for the relevance rule). At l = L-2, the relevance-rule code has
   H(c_l) > H(c_L) + 0.5 bit on >= 9 of 12 nets.
B4 (Kelvin's rule compounds). Chain K at the input: I_out(c_0) <= 0.6 I*_0 on >= 9 of 12 nets.
B5 (the corrected chain tracks the truth). Chain PR at the input: I_out(c_0) >= 0.8 I*_0 on >= 9 of 12 nets.
B6 (the next-code target over-counts under the relevance rule, Prop 6a). Chain R: T_0 >= I*_0 + 0.25 bit on >= 9 of 12.
B7 (the rate rule's targets under-count, Prop 6b). Chain K: T_0 <= I*_0 - 0.25 bit on >= 9 of 12 nets.
B8 (the corrected chain works as a simulator). Chain PR: I_chain(c_0) >= 0.9 I_out(c_0) on >= 9 of 12 nets.
B9 (the rate restriction, not the recursion's target, limits chain K). The direct code at chain K's rate carries at
   most 0.15 bit more about c_L than chain K's code, at >= 80% of (net, noisy layer) pairs.
B10 (deeper encoders are not needed at these sizes). C4 passes at >= 90% of the steps of chains K and PR.
B11 (the per-step numbers are certified). Every applicable certificate (C1-C6) passes at >= 90% of the steps of chains
   K and PR.
B12 (shared-noise distortion follows the output information). At l = 0, chain PR's code has a lower crn (cell-mean
   decoder) than chain K's code on >= 9 of 12 nets.
B13 (the Gaussian-channel information is estimable). For Gaussian codes with Monte Carlo rate <= 6 bits, the estimates
   with and without the source component and at N and N/2 agree within 0.15 bit at >= 90% of points.
B14 (analog codes come closer to Kelvin's target than partitions). At the evaluated steps, the Gaussian code's relevance
   at information rate T_l (linear interpolation along its beta curve, Monte Carlo rate) exceeds chain K's partition code
   relevance (entropy <= T_l) by >= 0.1 bit at >= 75% of (net, layer) points.
Reported without a registered threshold: per-layer erasure profiles; restart spreads; the look-ahead control; the
Pinsker-spectral bound; the forward-trained (crn) codes against the chains' codes on the (rate, crn) and (rate, I_out)
planes; estimator convergence tables.

## 6. What "certified all the way to the input" means here
Per step, "certified" = every applicable certificate of section 4 passes. A chain "gives certified bit counts all the
way to the input" when (i) every step from L-2 to 0 is certified on at least 2 of the 3 seeds of a config, and (ii) its
code at every layer carries at least 80% of the output information that the layer has (I_out(c_l) >= 0.8 I*_l), i.e.
its counts are counts of output-relevant bits. Kelvin's procedure as written is chain K; main's criterion is chain R
(target) plus the relevance rule; chain PR is the corrected procedure proposed in FORMAL section 7.
The certified count of a layer (what the output needs from it) is reported as a bracket: lower end 0.95 I*_l (no code
carrying 95% of I*_l can have less rate), upper end the least rate among certified codes (chain PR, direct) that carry
at least 0.95 I*_l. Where the bracket is wide, the report says which side is loose.
