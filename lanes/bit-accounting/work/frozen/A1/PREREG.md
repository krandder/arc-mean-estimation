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
