# Bit-accounting lane: pre-registration

Each part is hashed (sha256) with its time in prereg_hashes.txt before any of its evaluation runs. Definitions:
FORMAL.md v1 (section 1). Code: lib/bitlib.py, lib/lincodes.py, lib/rwf.py, scratch/train_bn2.py,
scratch/lin_codes.py, scratch/theory_spectra.py (hashed with each part).

## Part A1: per-layer bottlenecks on ARC 256 x 32 (registered before any evaluation run of A1)

Disclosure (development, dev seed 9100 only): theory spectra at all seven layers (logs/theory_arc_9100.log); linear
codes at layers 0 and 2 (both fail to reach eps = 0.1 within 256 bits); learned runs at layer 31 only (a first,
non-initialised model that stalled at nMSE 0.15, and 20-step smoke runs of the linear-initialised model: the linear
start gives C(0.1) = 27, C(0.01) = 163, FSQ b(0.1) = 36, b(0.01) = 215, sign codes do not reach 0.1). The theory
spectra of the evaluation nets are computed before their learned runs; they are predictions, not outcomes.

### Cells
ARC 256 x 32, seeds 4000-4003 (input-bits and relevance lanes' evaluation nets), layers l in {0, 2, 4, 8, 16, 24, 31}
and the output space (l = 32, future = identity).

### Measurements
- M1 (linear codes, every cell): lin_codes.py, P_fit = 16384, P_eval = 4096 (fixed seeds), bases 'as' and 'lin',
  kinds 'gauss' (analog, water-filled) and 'bin' (Lloyd-Max FSQ, greedy bits). b_l^lin(eps), C_l^lin(eps) = the
  better basis's interpolated crossing. Rates up to 256; "> 256" if not reached.
- M2 (learned local codes, class L_2(512), FORMAL.md 1.1): train_bn2.py, 3000 steps, batch 256, Adam 3e-4, started at
  the linear code of the basis whose M1 'gauss' nMSE at C = 64 is lower on that cell. Kinds 'gauss' and 'fsq' on all
  four nets at l in {0, 4, 16, 31, 32}; at l in {2, 8, 24} on as many nets as compute allows in order 4000, 4001,
  4002, 4003 (reported with the count). Sign codes ('bin', K = 256 nested bits) at l in {16, 31, 32} on nets 4000,
  4001. Learned counts use P_eval = 8192 held-out inputs (fixed seed per net).
- M3 (encoder size and training, seed 4000, l in {0, 16}, 'gauss'): width 1024, depth 4, 6000 steps.
- M4 (nested against dedicated, seed 4000, l = 16, 'gauss'): dedicated single-rate models at C in {16, 64, 128}.
- Theory (every layer): R_G(eps V) over eig Cov(a) (layer-free), over K_1 (degree-1, true law) and over the
  active-subspace spectrum (theory_spectra.py, P = 16384).
- Comparison: the relevance lane's N(l, eps) (runs/eval_arc_n256_L32_seed*.json, measured grid counts) at the layers
  both lanes have (0, 4, 8, 16, 24, 31).

### Predictions (scored by scratch/score_A1.py, written before the scoring and hashed separately)
Notation: C^loc_l(eps), b^loc_l(eps) = learned local counts (gauss, fsq); C_out, b_out = the same at l = 32;
R_out(eps) = R_G(eps V; eig Cov a).
- A1.1 (calibration of training, FORMAL 1.4). C_out(eps) <= 1.05 R_out(eps) + 1 at eps = 0.1 and 0.01 on all four
  nets (the linear analog code attains R_out exactly; a learned code started there must not be worse).
- A1.2 (every layer needs at least the output's bits, FORMAL 1.2). min(C^loc_l, C^lin_l)(eps) >= 0.9 C_out(eps) - 2
  at every layer and eps in {0.1, 0.01} where both are reached (a violation would be a bug).
- A1.3 (local codes at the input). Neither the linear nor the learned local code reaches eps = 0.1 within 256 bits at
  l = 0 (both kinds) on >= 3 of 4 nets.
- A1.4 (local codes near the output). At l = 31: C^loc_31(eps) <= 1.25 C_out(eps) and b^loc_31(eps) <= 1.25 b_out(eps)
  at eps = 0.1 and 0.01 on >= 3 of 4 nets.
- A1.5 (profile). C^loc_l(0.1) (learned, gauss; "> 256" counted as 257) is non-increasing in l up to 10% + 2 bits
  between consecutive measured layers on >= 3 of 4 nets.
- A1.6 (binary against channel). b(eps)/C(eps) in [1.0, 1.7] for the learned codes of the same cell at eps = 0.1 and
  0.01 where both are reached, on >= 75% of such cells.
- A1.7 (sign bits are an inefficient binary code). b^sign(0.1) >= 1.5 b^fsq(0.1) (or sign unreached) on >= 75% of the
  cells where both were run and FSQ reaches 0.1.
- A1.8 (learning helps little where the future is nearly linear and a lot only if the encoder can compute it).
  At l = 31: learned C^loc(0.01) >= 0.85 C^lin(0.01) on >= 3 of 4 nets (little to gain). At l = 16: reported, no
  band.
- A1.9 (theory). R_G over the active-subspace spectrum at layer l is >= the learned local C_l(0.1) at l <= 8 where the
  latter is reached (the linearised price overcharges large errors) on >= 75% of such cells; R_out(0.1) and
  R_out(0.01) predict C_out within 10% (implied by A1.1 from above; from below reported).
- A1.10 (against the linear-feature count). b^loc_l(0.1) / N(l, 0.1) in [1.5, 8] at l in {16, 24, 31} on >= 75% of
  (net, l) cells where both are defined.
- A1.11 (mean error). Where nMSE <= 0.1, the squared error of the output mean |mean(a_hat - a)|^2 / V is below
  nMSE / 10 on >= 80% of (cell, rate) points with a resolved mean error (above 3 times its noise floor).
All misses reported with their cells.

## Part S1: per-layer bottlenecks on small nets (plan changed by main 23:05Z; registered before any S1 evaluation run)

Disclosure: no small-net result has been seen (one 30-step CPU smoke run on dev seed 9100 at 16 x 4, meaningless by
design). ARC Part A1 runs on seed 4000 are in progress on CPU (linear codes done, three learned runs training); their
outcomes are not used here except as stated.

### Cells
Plain critical ReLU nets, Gaussian inputs, W_k = st.W_layer(seed, n, k): 16 x 4, 16 x 16, 32 x 8, 32 x 32, evaluation
seeds 5000, 5001, 5002 (dev seed 9100 runs in the same job and is reported separately). Layers l in {0, L/4, L/2,
3L/4, L-1} and the output space. Rates b, C in {1, 2, 3, 4, 6, 8, 12, 16, 24, 32}.

### Measurements (gpu_src/scripts/run_curves.py, gpu_src/lib/smallnets.py; one dedicated model per rate)
Encoder classes (FORMAL.md 1.1, precise): 'local' = z = A2 relu(A1 x + b1) + b2 with A1 of width n (one ReLU layer of
width n, then linear; x the whitened h_l); 'linear' = z = A x + b; 'unres' = MLP with 3 hidden GELU layers of width 256
on (whitened h_l, whitened exact output a = g_l(h_l)), an encoder that contains the future net. Decoder: MLP with 3
hidden layers of width 256 -> state at layer l -> fixed future. Binary: b sign bits (2^b cells). Channel: water-filled
Gaussian channel with C = (1/2) sum log2(1 + SNR_i). 6000 steps, batch 1024, Adam 1e-3, cosine. Held-out P = 32768.
Counts b_l(eps), C_l(eps): interpolated crossings on the rate grid; unreached = "> 32".

### Predictions (scored by gpu_src/scripts/score_S1.py, written before scoring and hashed separately)
- S1.1 (the unrestricted class needs the output's own bits at every layer, FORMAL 1.2). |C^unres_l(eps) -
  C_out(eps)| <= max(0.15 C_out(eps), 1.5) and the same for b, at eps in {0.1, 0.01}, on >= 75% of (net, layer, eps,
  kind) cells with future depth L - l <= 8 where C_out (b_out) is reached. Deeper futures (L - l >= 12) reported, with
  the expectation that the decoder's inversion of the future fails first at l = 0 of 16 x 16 and 32 x 32.
- S1.2 (local codes at the input of the L = n nets). C^local_0(0.1) >= 1.5 C_out(0.1) or unreached, on >= 5 of the
  6 evaluation nets of 16 x 16 and 32 x 32.
- S1.3 (local codes at the last hidden layer). C^local_{L-1}(eps) <= 1.25 C_out(eps) + 1 at eps in {0.1, 0.01} where
  C_out is reached, on >= 75% of evaluation nets.
- S1.4 (profile). C^local_l(0.1) (unreached counted as 33) is non-increasing in l up to 10% + 1 bit between
  consecutive layers on >= 75% of evaluation nets.
- S1.5 (local against linear). C^local_l(eps) <= 1.1 C^linear_l(eps) + 1 at eps in {0.1, 0.01} where the linear count
  is reached, on >= 75% of cells.
- S1.6 (binary against channel). b(eps)/C(eps) in [1.0, 2.5] for the same (net, layer, class) at eps = 0.1 where both
  are reached, on >= 75% of such cells.
- S1.7 (mean error). Where nMSE <= 0.1, |mean(a_hat - a)|^2 / V < nMSE / 10 on >= 80% of the points whose mean error
  is resolved (above 3 times its noise floor).

## Part S2: the scrambling test on small nets (registered before any S2 run, including dev)

Code: gpu_src/scripts/run_chain.py (hashed below). Nets and layers as in S1 (dev seed 9100 reported separately).
Codes of b in {4, 8, 12, 16} sign bits, encoder classes 'local' and 'unres' (S1 definitions), jointly trained chains
(per-layer reconstruction + chain-from-c_0 reconstruction + transition consistency; 6000 steps).
Basis freedom: (i) joint training (the codes adapt so the next code is predictable); (ii) statistics invariant to
relabelling bits and flipping their signs: coverage, H(c_{i+1} | c_i), accuracy of the best degree-d polynomial threshold
fit (d = 1, 2, 3) and of the best s-junta (s <= 6, b <= 12) to the data majority map on the reachable codes;
(iii) the exact Walsh spectrum of the learned T over all 2^b codes (it includes T's extrapolation to unreachable codes,
reported with the coverage). Baselines with the same b on the same reachable codes: random permutation, random
invertible XOR map, random 2-juntas, dense random LTF.

### Predictions (scored by gpu_src/scripts/score_S2.py, written before scoring and hashed separately)
- S2.1 (local codes are not scrambled). The data majority map of local chains has degree-1 PTF accuracy >= 0.9 on
  >= 75% of (net, b, transition) cells, and its degree-1 accuracy is closer to the LTF baseline's than to the
  permutation baseline's on >= 90% of cells.
- S2.2 (low-degree transitions). The learned T of local chains has Walsh weight at degree <= 2 at least 0.8 on >= 75%
  of cells; the permutation and XOR baselines have at most 0.1 at b >= 8 (sanity).
- S2.3 (unrestricted codes do not move). For 'unres' chains the learned T's mean number of relevant inputs per output
  bit (influence > 0.01) is <= 2 on >= 75% of cells (T close to a relabelled identity, FORMAL 2.1).
- S2.4 (non-determinism). H(c_{i+1} | c_i) reported per cell; no band.
- S2.5 (the chain works). For local chains the chain-run nMSE at l = L-1 is <= 1.5 x the direct code's nMSE at L-1 on
  >= 75% of (net, b) cells.
