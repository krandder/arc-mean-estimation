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

## Part A2: narrow-deep 8 x 256 linear codes (registered before any A2 evaluation run)

Disclosure: dev seed 111 only (runs_dev/lin_nd_111.json: C^lin(0.1) = 9.3 at l = 0 and 1.6-2.3 bits from l = 8 on).
Nets: nd.make_weights plain, seeds 203, 216, 217, 220, 221, 223 (rescaled per layer by constants, nMSE-invariant).
Measurement: scratch/lin_codes.py nd <seed> 16384 4096 (as M1), layers 0, 8, 32, 64, 128, 192, 255 and the output.
- A2.1 (the state is a ray). For l >= 32, |C^lin_l(eps) - (1/2) log2(1/eps)| <= 0.6 bits at eps in {0.1, 0.01, 0.001} on
  >= 5 of 6 nets (all such layers).
- A2.2 (the input layer is expensive for a local code). C^lin_0(0.1) >= 3 C^lin_32(0.1) on >= 5 of 6 nets.

## Part S1-lin: linear transform codes on the small nets (registered 2 Nov before these runs; one cell seen)

Seen before registration: 16 x 16 seed 5000 (all layers; the linear analog code at l = 15 reaches C(0.1) = 2.9, below the
learned 1500-step unrestricted count 5.4). scratch/lin_codes.py small<n>x<L> <seed> 16384 8192, all S1 nets and seeds.
- S1L.1 (training gap). At l = L-1 and in output space the linear analog code needs fewer bits than the learned
  unrestricted code: C^lin(0.1) < C^unres(0.1) on >= 75% of the 11 unseen nets.
- S1L.2 (input layer). At l = 0 of the L = n nets the linear analog code does not reach nMSE 0.1 within 32 bits on
  >= 5 of 6 nets.
- Reported: the best code found per (net, layer, class) = min(learned, linear transform code) where the linear code
  belongs to the class (local, linear: yes; unrestricted: yes at every layer).

## Part B-ARC: transitions between output-relevant coordinates on ARC (registered before any B-ARC run)

Code: scratch/chain_B.py (hashed below). Nets: ARC seeds 4000 and 4001 (and dev 9100 first). Codes: the first K_l
active-subspace coordinates at layers 8, 12, 16, 20, 24, 26, 28, 30, 31 and the output PCA (K_l = channels opened by
the layer's linear analog code at the capacity where it reaches nMSE 0.05), sign bits = their signs. Pairs:
consecutive layers and 16->24, 24->32, 16->32, 8->16.
- BA.1 (near-linear real transitions late). Importance-weighted R^2 of the best linear map u_l -> u_l' >= 0.9 for every
  pair with l >= 16, on both nets; the MLP improves it by <= 0.05.
- BA.2 (sign-code transitions are threshold-like). The LTF bit accuracy is within 0.03 of the MLP bit accuracy for
  every pair with l >= 16, on both nets.
- BA.3 (no avalanche). At input correlation rho = 0.999 the fraction of differing sign bits at the output-relevant
  coordinates does not increase by more than a factor 2 from l = 8 to l = 31 on both nets.

## Amendment S5-S6: convergence certificates and joint (vector) quantisation (registered 2 Nov before any S5/S6 run;
## Kelvin's questions relayed by main at 01:3xZ and 01:4xZ)

### S5: per-run convergence certificates (gpu_src/scripts/run_cert.py)
Cells: 16 x 16 and 32 x 32, seed 5000, all grid layers and the output; classes local and unres; sign-bit codes,
b in {1, 2, 3, 4, 6, 8, 12, 16}. Variants: base (as S1), big (width 512, 3000 steps), deep (unres only: width 512,
5 hidden layers, 3000 steps), r1, r2 (base with other seeds). Certificates per model: model nMSE; centroid decoder
(per-code mean output); one nearest-neighbour Lloyd step (unrestricted); within-class Lloyd step (local). Toy known
answer: output-space target that depends on exactly k sign bits (k = 2, 4, 8), classes local and unres.
Known-answer certificates computed for every reported count from existing results: (i) output-space channel code
against the Gaussian bound R_G(Cov a) (the linear analog code attains it exactly); (ii) unrestricted count at layer l
against the best output-space count (equal at the optimum in a noiseless net; the shortfall measures training or
capacity); (iii) training length (1500 vs 3000 steps where both exist).
- S5.1 (toy). The measured count for nMSE 0.001 equals k (within the rate grid: the first grid rate >= k) for both
  classes and every k.
- S5.2 (decoders are near-optimal for their encoders). Centroid nMSE >= 0.8 x model nMSE on >= 75% of (cell, b)
  points with b <= 8.
- S5.3 (encoders are not). One unrestricted Lloyd step lowers nMSE by > 20% (nn < 0.8 centroid) on >= 50% of points
  with b >= 4: the learned encoders are not at a fixed point of the quantiser optimality conditions, so learned counts
  are upper bounds with room.
- S5.4 (seed noise). The three restarts give b(0.1) within 1.5 bits of each other on >= 75% of cells; the big variant
  is within 1.5 bits of base or lower.
- S5.5 (restriction, not optimisation). For local cells at l <= L/4, the within-class Lloyd step recovers less than
  half of the unrestricted Lloyd gain on >= 75% of points with b >= 4.

### S6: does joint quantisation close the binary-vs-channel gap? (gpu_src/scripts/run_vq.py)
All four small nets, seeds 5000-5002: k-means codebooks of 2^b output vectors, b = 1..12 (free reconstructions; and
medoids = nearest actual outputs, reachable from every layer); index entropy.
- S6.1. b_VQ(0.1) <= 1.3 x C_best(0.1) on >= 75% of nets, C_best = min(Gaussian bound, best channel code found) in
  output space (joint coding removes most of the per-coordinate overhead).
- S6.2 (fixed-rate loss in few dimensions). b_VQ(0.1) >= C_best(0.1) on >= 75% of nets (a fixed-rate index in an
  effectively low-dimensional output keeps a gap; the entropy-coded rate H is reported beside it).
- S6.3. The medoid version is within 0.5 bits of the free version at nMSE 0.1 on >= 75% of nets (reachability costs
  little).

## Part S7 (primary measurement from 02:00Z, Kelvin's decision): the encoder decides how many bits it uses
## (registered before any S7 evaluation run; a 30-step smoke run on dev seed 9100 only)

Code: gpu_src/scripts/run_entropy.py. Loss = forward-propagated nMSE + lambda * rate, lambda in {1, 0.3, 0.1, 0.03, 0.01,
0.003, 0.001}; 16 latents; 2000 steps x batch 2048. 'ent': uniform noise in training, rounding at test, rate =
-log2 P(code) under a learned factorised prior (mixture of 3 logistics per latent): the average number of bits actually
used. 'vib': Gaussian noise with encoder-chosen means and scales, rate = KL bound. Cells: 16 x 16 and 32 x 32, seeds
5000-5002, all grid layers and the output, classes local and unres; 16 x 4 and 32 x 8 seed 5000 as time allows.
Count R(eps) = rate at which the lambda-sweep reaches nMSE eps (log-linear interpolation between sweep points; the
bracketing sweep points are reported; "unreached" if the smallest lambda does not reach eps).
- S7.1 (shortcut, flat). Unrestricted ent count R(0.1) within max(25%, 1 bit) of the output-space ent count at every
  layer with L - l <= 8, on >= 75% of such cells.
- S7.2 (restricted, rising). Local ent R(0.1) at l = 0 >= 2 x the output-space ent count, or unreached, on >= 5 of 6
  L = n nets.
- S7.3 (Kelvin's question: is the entropy-coded count better than fixed-noise Gaussian codes with the capacity
  formula?). Reported cell by cell: ent R(0.1) against the S1 channel count C(0.1) and the vib count at the same cell.
  Expectation registered: ent <= 1.2 x min(C_S1, vib) + 1 bit on >= 75% of cells (they agree up to the per-latent
  quantisation gap; the capacity formula overcounts for non-Gaussian code inputs while rounding pays about 0.25 bit
  per active latent at high rate).
- S7.4 (rate checks). A fresh prior refitted on held-out codes lowers the rate by < 5% on >= 90% of ent models; where
  the joint plug-in entropy is computable it is <= the factorised rate + 0.5 bit on >= 90% of them.

## Amendment S7-S9 (Kelvin 02:10Z, relayed by main; registered before any run of these versions; smoke runs only)

S7 (revised; supersedes the S7 primary): run_entropy.py now trains four arms side by side per cell and lambda:
'gfix' (PRIMARY) = real-valued code with fixed unit Gaussian noise and an encoder-chosen scale, rate = information
estimate E[log2 q(z|h) - log2 p(z)] with a learned prior (mixture of 3 Gaussians per latent), NOT the capacity
formula; 'bern' (S8) = Bernoulli bits with encoder-predicted p, straight-through relaxed sampling, rate =
sum_j [H(mean p_j) - mean H(p_j)] (the information each bit carries under the matched prior; unneeded bits cost nothing
at p = 0.5); 'ent' (uniform noise, rounding, entropy-coded) and 'vib' (encoder-chosen variance, N(0, I) prior KL) as
comparisons. S7.1-S7.4 apply to 'gfix' (the S7.4 refit check: a fresh prior fitted on held-out z lowers the rate by
< 5%). Kelvin's question S7.3 is answered by comparing gfix, ent, vib, bern and the S1 capacity-formula channel at
the same cells.
- S8.1 (Bernoulli bits). At the largest lambda most bits sit at p ~ 0.5 (share of samples with |p - 0.5| < 0.05 above
  0.5 for >= 75% of the 16 bits) and carry < 0.1 bit each; at the smallest lambda >= 50% of bits are used
  (information > 0.3 bit). Reported per cell.
- S8.2. bern R(0.1) is within 1.5 x gfix R(0.1) + 1 bit on >= 75% of cells.
S9 (real-valued scrambling, run_chain_real.py): jointly trained chains of fixed-noise real codes (K = 8, lambda in
{0.03, 0.01, 0.003}), 16 x 16 and 32 x 32, seeds 5000 and 5001, classes local and unres. Statistics of each learned
transition in the Gaussian convention: degree-1 share W1, Hermite weights from noise stability, per-input total effects;
baselines: random linear map (W1 = 1) and B sin(3 C u + c) (W1 ~ 0).
- S9.1 (not scrambled, real-valued). W1 of the learned transitions >= 0.7 on >= 75% of (chain, lambda, transition)
  cells; the sine baseline has W1 <= 0.1 (sanity).
- S9.2. Each output coordinate depends on several inputs (total effects > 1% for >= 3 of 8 inputs on >= 50% of
  cells): dense but smooth, the real-valued counterpart of the dense threshold maps of S2.

## Part S10: a compressed simulator with simple code dynamics (Kelvin 02:25Z; registered before any S10 evaluation run,
## smoke runs on dev 9100 only)

Code: gpu_src/scripts/run_sim.py. Nets 16 x 16 and 32 x 32 (noiseless), seed 5000; the noisy (sigma = 1) version is
not run in this lane (time). Linear input encoder (c_0 Gaussian), c_{i+1} = T_i(c_i) + eps along the layer grid, a
decoder at every grid layer, loss = sum of per-layer forward-propagated nMSE + lambda * rate of c_0, lambda in {0.01,
0.001}, K = 8, 2500 steps. Transition classes: mlp, linear, shared (one linear T), sparse2, id10, deg2.
Estimator for linear/shared/sparse T: the Gaussian code law propagated in closed form, the last decoder integrated by
scrambled Sobol over K dims, against plain MC and RQMC on the net with the same N.
- S10.1 (simple dynamics are cheap). The final-layer nMSE of the linear and shared classes is within 0.05 (absolute)
  of the mlp class on both nets at both lambdas.
- S10.2 (the simulator's estimate has a bias floor). The deductive estimate's error does not fall by more than 2x from
  N = 4096 to 65536 points on either net (its error is the simulator's bias), and at N = 65536 it is above plain MC's
  error on the net with the same N on both nets.

## Part S11: net-level controls through the same pipeline (Kelvin 02:40Z; registered before any S11 run; a sensitivity
## check only: relative output change for a 1e-3 input perturbation 1e-5 relu, 2.3e-4 tanh4, ~0 linear; one flipped
## input bit decorrelates the Feistel output completely)

Control nets, 16 x 16, seed 5000, same grid, same scripts with --netkind: tanh4 (bias-free tanh, W ~ N(0, 4/n),
chaotic phase), feistel (16 Feistel rounds on {+-1}^16, g = degree-3 parities: a reversible Boolean mixing circuit),
linear (W ~ N(0, 1/n), no activation). Runs: S7 (run_entropy.py, local and unres, all grid layers and the output),
S9 (run_chain_real.py, local and unres), S10 (run_sim.py: mlp, linear, sparse2), S2 sign-bit chains (run_chain.py,
local; feistel and tanh4) with the post-hoc held-out statistics.
Predicted signatures (if the tests work):
- S11.1 (feistel, Walsh). Held-out degree-1 threshold share of the predictable part <= 0.5 (median over transitions and
  code sizes), i.e. near the relabelled null, against 0.96 on the ReLU nets.
- S11.2 (feistel and tanh4, real-valued). Degree-1 share W1 of the learned S9 transitions <= 0.5 (median), against the
  ReLU nets' values.
- S11.3 (linear). W1 >= 0.95 (median) and the S10 linear class within 0.01 nMSE of mlp at the last layer.
- S11.4 (tanh4, bits by layer). The local gfix count R(0.1) decreases with l faster than on the 16 x 16 ReLU net: the
  ratio R_local(l = 0) / R_local(l = L/2) is larger for tanh4 (unreached counted as 32 bits).
- S11.5 (price of simple dynamics). The S10 gap between the linear class and mlp at the last layer is larger for tanh4
  and feistel than for the ReLU 16 x 16 net.
If S11.1 and S11.2 fail (the tests do not light up on the scrambled controls), the scrambling tests are blind and the
ReLU verdict cannot be trusted; the report will say so plainly.

## Part P1 (phase 1; Kelvin 02:55Z and 03:20Z via main): the best bits-vs-accuracy curve of every layer
## (registered before any P1 evaluation run. Seen before registration: dev seed 9100 runs of two earlier versions
## (3 + 4 cells: the variable-rate model was 4-67% worse in Lagrangian than fixed-lambda models, 2x steps helped by up
## to 27%, and at l = 0 local the linear reference beat every learned code; this version adds the analytic anchor,
## the lambda normalisation and 6000 steps); a CPU check that the untrained model reproduces the linear reference
## (16x4, l = 1: R(0.1) 12.4-12.5 against 12.1); S7-style fixed-lambda gfix reference runs on relu 16x16/32x32 s5000
## and on the S11 controls tanh4/feistel/linear 16x16 s5000)

Code: gpu_src/scripts/run_vr.py (hashed below). One lambda-conditioned variable-rate code per (net, layer, class).
- Code: z = E(x, t) + N(0, I_K), K = n (n >= 16 here); x = whitened h_l. Fixed unit noise with encoder-chosen power is
  the same family as fixed power with chosen noise: only the per-latent SNR matters. Rate = log2 q(z | x) - log2 p(z | t)
  summed over latents (one-draw estimate of KL(q || p) >= I(h_l; z), bits); t = (log10 lambda + 2) / 2.
- Conditioning: FiLM on t in every hidden layer of encoder and decoder (act(g(t) (W x + b) + c(t)); g - 1 and c from
  small MLPs of t, zero at initialisation) and the per-latent gain a~(t) below.
- Classes: unres = MLP 3 x 256 on (whitened h_l, whitened exact output a) plus a linear skip; local = one ReLU layer
  of width n on the whitened h_l, then affine (for every fixed t an element of L^1(n)).
- Anchor (Kelvin 03:20Z: identity at a high budget, shed the least important directions first as the price rises,
  and the linear reference): code y = a~(lambda) * y~(x). y~ is a unit-scale encoder output initialised to U^T x
  (U, g = eigenpairs of the cloud-averaged future-weighted Jacobian Gram G = E[J^T J], J = da/dx); a~ = a + c(lambda)
  with the analytic water-filled gain a_i = min(16, sqrt(max(0, g_i / theta - 1))), theta = lambda V / (2 ln 2) (the
  water level minimising the linearised Lagrangian; the cap 16 = SNR 256 = Kelvin's identity anchor at about 4 bits
  per direction) and a learned correction c (zero at initialisation; it can raise powers or switch on directions the
  linear code leaves off). Decoder input b~ * z with b~ = a~ / (a~^2 + 1) (linear-MMSE scaling), output = MLP + U b~ z
  (MLP zero at initialisation). So at initialisation the code at every lambda is the linear reference code (capped);
  at high budget it reconstructs every direction the output depends on almost perfectly. local: u = relu(x + 8)
  (exact for x > -8), y~ = (u - 8) U, i.e. y = a~ (A2 u + b2): affine in u for every fixed lambda (class L^1(n)).
- Lambda annealed upward (Kelvin 03:20Z): variable-rate models draw log10 lambda ~ U[-4, -4 + 4 r], r rising linearly
  from 0 to 1 over the first quarter of training; fixed-lambda models move from 1e-4 to their lambda on the same
  schedule.
- Loss per example: Lagrangian d + lambda x rate, d = |g_l(h_hat) - a|^2 / tr Var(a), divided by a running mean of the
  Lagrangian in its lambda bin (16 bins), so every lambda counts equally (each lambda's optimum is unchanged).
- Prior p(z | t): on the standardised code z / sqrt(a~^2 + 1): a unit lower-triangular linear map (conditioned on t;
  captures correlations, |det| = 1), then per latent a mixture of 4 Gaussians with parameters = base + MLP(t); plus
  the Jacobian term.
- Decoder: as above, MLP 3 x 256 -> whitened state -> the real rest of the net (feistel: tanh into [-1, 1]^n).
- Training: Adam (lr 1e-3, betas 0.9/0.99), warm-up 2%, cosine to 1%, gradient-norm clip 100, batch 2048, fresh net
  samples every step, S = 6000 steps.
Per cell: G1 (batched): r0, r1, r2 = variable-rate restarts; f1, f2, f3 = separately trained fixed-lambda models at
lambda = 0.1, 0.01, 0.001. G2 wide: widths x 2 (unres 512; local hidden 2n, outside L^1(n)), decoder 512, 8 prior
components. G3 long: base architecture, 2S steps. Evaluation on 32768 held-out samples: every variable-rate model on
17 lambdas (log10 lambda = -4 .. 0 by 0.25): rate, nMSE, output-mean error; fixed models at their lambda; r0's rate
re-measured with fresh priors fitted on half A of the held-out codes and evaluated on half B (factorised 8-Gaussian
mixture; full-covariance Gaussian); r0_refit = the smallest of trained / refits at each lambda; centroid test at
lambda = 0.1, 0.01, 0.001 (output-space regressor E[a | z], MLP 3 x 512, 2000 steps, 98304 fresh samples, against
the model's nMSE on the same held-out codes). Linear analytic reference (Kelvin 03:20Z): G = E[J^T J] (J = da/dx at
the actual states; 16384 samples), reverse-water-filled powers p_i = g_i / theta - 1 on its eigen-directions, unit
noise, linear MMSE decoding, run through the REAL rest of the net on held-out states; rate by the capacity formula
(an upper bound on that code's information); 40 water levels; its linearised prediction is stored too. R_G(D) =
Gaussian reverse water-filling on Cov(a).
Cells: relu 16x4, 32x8, 16x16, 32x32, seeds 5000-5002, layers {0, L/4, L/2, 3L/4, L-1} x {local, unres} and the
output (unres); controls tanh4, feistel, linear 16x16 seed 5000, same cells. Order: relu 16x16/32x32 seed 5000, then
seeds 5001-5002 and the controls, then 16x4 and 32x8.
Counts. R_c(D) for curve c = rate where the monotone envelope of (rate, nMSE) crosses D (log-linear interpolation),
D in {0.3, 0.1, 0.03, 0.01, 0.003, 0.001}; "unreached" if it does not. Slope = bits per halving of the output error,
(R(D2) - R(D1)) / log2(D1 / D2) between consecutive D. Reported count R*(D) = min over the learned codes of the class
(r0, r1, r2, long, r0_refit; wide for unres only; for local, wide is reported separately as the width sensitivity).
The linear reference is reported next to it.
Certificates (per cell, D in {0.1, 0.01}, where reached; a failing cell is flagged, still reported):
- C1 restarts: the rates of r0, r1, r2 within max(0.5 bit, 10% of the median), or their nMSE at the median rate
  within a factor 1.1 (flat curves: a small error difference is a large rate difference).
- C2 steps: R_r0 - R_long <= max(0.5, 10% of R_r0), or r0's nMSE at R_long within 1.1 x long's.
- C3 capacity: the same against wide (unres; for local a failure means the width-n restriction binds).
- C4 prior: the refitted rates >= 0.95 x the trained rate on every lambda with rate > 1 bit (r0).
- C5 centroid: nMSE_model <= 1.1 x nMSE_centroid + 0.002 at the three lambdas.
- C6 spot check (Kelvin's condition): Lagrangian nMSE + lambda x rate of r0 at lambda_j <= 1.03 x that of the fixed
  model f_j. If C6 fails on more than 10% of (cell, lambda) points, the variable-rate design counts as worse: the
  curves are then the lower envelope of the variable-rate curves and the fixed points, and the failure is reported.
- C7 analytic reference: R*(D) <= R_linref(D) + max(0.3, 5%) wherever the linear reference reaches D (else the
  learned code is undertrained there).
Known answers:
- KA1 output: R*_out(D) <= R_G(D) + 0.3 bit at D in {0.1, 0.03, 0.01} on every relu net.
- KA2 shortcut: |R*_unres(l, D) - R*_out(D)| <= max(0.5, 15% of R*_out) at D in {0.1, 0.01} on >= 90% of (net, l).
- KA3 linear net (Gaussian, R(D) = R_G(D) exactly): R*(l, D) within max(0.3, 10%) of R_G(D) at D in {0.1, 0.03,
  0.01} for both classes at every layer.
Predictions:
- P1.1 C1, C2, C3 (unres), C4, C5, C7 each pass on >= 90% of the points where they apply; C6 as above.
- P1.2 local R*(0, 0.1) >= 2 x R*_out(0.1) (or unreached) on >= 5 of the 6 L = n relu nets.
- P1.3 local R*(l, 0.1) is non-increasing in l (within 0.5 bit) on >= 80% of the 12 relu nets.
- P1.4 the output slope between D = 0.1 and 0.01 is smaller on the deeper net of each width (16x16 < 16x4 and
  32x32 < 32x8), for each seed.
- P1.5 controls: tanh4 local R*(l, 0.1) >= R*_out(0.1) + 4 bits (or unreached) for l in {0, 4, 8}; feistel local
  R*(0, 0.1) >= R*_out(0.1) + 2 bits (or unreached); linear: KA3.
Scorer: gpu_src/scripts/score_P1.py (hashed below, before any P1 evaluation result).

## Part P2.0 (phase 2, registered now, run only after phase 1 is final): Kelvin's near-identity hypothesis
## (Kelvin 03:3xZ via main: "Because this encoding/decoding starts near the identity, I at least hope it has some
## inductive bias to remaining somewhat close to it even at high compression ... comparing these two transformations
## (actual activations from l -> l+1) and (bit-optimal encoding from l -> l+1) may be super important")
Codes: the identity-anchored P1 models (r0), plus, for each grid layer l < L - 1, a P1-method code at l + 1 (same
class) so that consecutive layers can be compared; lambda in {0.1, 0.01, 0.001}. All statistics are invariant to
rotations of the code (the fixed isotropic noise leaves an orthogonal freedom): R^2 of fits, principal angles,
subspace comparisons; maps are compared by fit quality, never by coefficients.
(1) Distance from identity: the share of code variance (encoder mean y) that is a linear function of the whitened
    h_l (R^2 of the best linear map, variance-weighted over latents); principal angles between the code's active
    subspace (top-k right singular vectors of that linear map, k = latents with SNR > 1) and the top-k eigenvectors of
    the future-weighted spectrum G (as in the linear reference).
(2) The code map vs the layer map: T_l = best map c_l -> c_{l+1} (linear and MLP fits on code means) against the layer
    map restricted to the code, c -> E_{l+1}(f_{l+1}(D_l(c))); agreement R^2 between the two, and the linear share
    (R^2 of a linear fit) of each; whether the linear share at high compression (lambda = 0.1) is above that at low
    compression (lambda = 0.001), i.e. whether dropping directions removes the gate flips that make the map nonlinear.
(3) Gates: for every unit of layer l + 1, whether the code at l determines its gate (held-out accuracy of predicting
    sign of the pre-activation from c_l, against the base rate), by the unit's distance to its boundary and its
    gradient energy; tracked = accuracy >= 0.95; compared with the relevance lane's gate counts where available.
(4) Rotation: principal angles between the code's active subspace at l + 1 and the image of the active subspace at l
    under the cloud-averaged Jacobian of layer l + 1.
(5) Noisy nets (Model S, sigma = 1, 16x16 and 32x32): whether T_l settles to one shared map with depth (fit T_l on
    layer l, score it on layer l + k; aligned by orthogonal Procrustes on the codes).
Controls: the same on tanh4 (chaotic): Kelvin's hope should fail there.
Predictions (Kelvin's hypothesis, ReLU vs tanh4): on relu 16x16 and 32x32, at lambda = 0.01 and l >= L/4:
- H1 linear share of the code (1) >= 0.8 on >= 75% of (net, l, class); on tanh4 < 0.5 at l <= L/2.
- H2 the code map and the layer map agree (2) with R^2 >= 0.8 on >= 75% of relu (net, l); < 0.5 on tanh4.
- H3 the linear share of T_l at lambda = 0.1 is >= that at lambda = 0.001 on >= 75% of relu (net, l).
- H4 (rotation) the mean cos^2 of the principal angles in (4) is >= 0.7 on relu, < 0.4 on tanh4.
- H5 (noisy) T_l fitted at l scores R^2 >= 0.8 at l + 4 on the noisy 32x32 nets for l >= L/2.
Code and scorer for P2.0: written and hashed before the phase-2 runs.

## Amendment P1-A (responses to review r2a by gpt-6-astra, review/review_r2a.raw; registered before any P1-A run;
## the 12 P1 cells finished by 04:45Z inspected, monitor summary lines of later cells seen)
Extra certificates on every finished P1 cell, by gpu_src/scripts/run_vr_cert2.py (hashed below), run after the main
P1 cells: (1) explorer: 3 local encoders whose ReLU gates start inside the input cloud (hidden = the net's own
next-layer pre-activations, jittered; output fitted by least squares to the anchor's unit-scale code; feistel: random
unit-variance gates), same analytic gains, decoder, prior, schedule, still in L^1(n); (2) wdec: width-n local encoder
with the wide decoder (512) and prior (8 components), separating encoder width from decoder/prior in G2; (3) centroid2:
an output-space residual correction around r0's reconstruction (normalised code input, output MSE, 4000 steps), with
its last-quarter training trend; (4) the linear reference's rate with held-out directional powers; (5) gate activity
(share of hidden units active on 5-95% of inputs) of r0 and the explorers.
Scoring changes (score_P1.py v2, hashed before use): (a) the primary crossing is conservative: time-sharing (linear in
nMSE) between adjacent achieved points of one curve; the registered log-linear crossing is reported as a secondary
estimate; (b) two counts per cell: R_r0 (the single registered model, no selection) and R* (minimum over the class's
codes, now also over explorer and wdec; the selection bias of this minimum is of the order of the evaluation noise,
about 0.05 bit, and is stated); (c) certificates at every D of the grid where the curves reach D, with "not covered"
(the lambda range does not reach D) separated from "fail"; (d) the C6 fallback uses one candidate set (all learned
curves of the class incl. refit, explorer, wdec, and the fixed points), and the table marks where a fixed point sets
R*; C7 is evaluated against the held-out-power linear reference; (e) scores read "pending" until the expected cell
manifest is complete; (f) KA2 is an empirical comparison (decoding at layer l is restricted to reachable outputs), not
a guaranteed known answer; C5 v2 = centroid2: nMSE_model <= 1.05 x nMSE_corrected + 0.002 with the correction
converged (last-quarter loss change < 2%).
C6 (finding 5): reported separately for r0 (6000 steps) and for long (12000 steps) against the fixed models.

## Amendment P2.0-a (implementation of P2.0 parts 2-4; main approved 2 Nov ~16:2xZ, lane cap +$12; registered
## before any run of these cells; P2.0 part 1 results seen)
Cells: P1-method codes (run_vr.py --groups G1 --certs 0: the variable-rate restarts r0-r2 and the fixed-lambda models,
no 2x variants or certificates) at layer l+1 for every grid layer l < L-1: relu 16x16 (l+1 = 1, 5, 9, 13) and 32x32
(1, 9, 17, 25), seeds 5000-5002, and tanh4 16x16 seed 5000; classes local and unres (56 cells; runs/P2a). Analysis
(CPU, scratch/p2_maps.py, hashed before it reads any P2a result) pairs each with the P1 code at l, model r0, lambda in
{0.1, 0.01, 0.001}, on 16384 held-out inputs: (2) code map T_l = best linear and best MLP map from the code mean at l
to the code mean at l+1, against the layer path c -> E_{l+1}(f_{l+1}(D_l(c + noise))); R^2 of each against the true
next code, R^2 between the two, and the linear share (R^2 of a linear fit) of each; (3) gates of layer l+1 predicted
from the code at l (logistic regression, held-out accuracy against the base rate; tracked = accuracy >= 0.95), by
the unit's |pre-activation| / std and its gradient energy; (4) principal angles between the code's active subspace
at l+1 and the image of the one at l under the cloud-averaged Jacobian of layer l+1. Predictions H2-H4 as registered
in P2.0 (scored at lambda = 0.01, l >= L/4 for ReLU; all grid layers for tanh4 as registered). Reported in
certified-linear terms as well: per layer, the linear-piece cost ratio and the learned-mixture ratio (from P1).

## Part U (phase 2b, Kelvin's "only later we try to unscramble"; registered before any run, smoke run on dev 9100 only)
Code: gpu_src/scripts/run_unscr.py (hashed below). Pairs (l, l+1), l a grid layer < L-1: relu 16x16 and 32x32 seeds
5000-5002 and tanh4 16x16 seed 5000, local class. Start: the phase-1 codes (P1 r0 at l, P2a r0 at l+1) at a fixed
lambda (0.01 and 0.1). Both codes are fine-tuned jointly (3000 steps) with
loss = sum_j (d_j + lambda rate_j) / Lag0_j + mu |y_{l+1} - S(y_l)|^2 / tr Var(y_{l+1}),
y_j = code means, S a jointly trained map ('linear' = affine; 'diag' = coordinate-wise affine, i.e. identity up to
scale; 'diag' at lambda = 0.01 only), mu in {0 (control: fine-tuning alone), 0.1, 0.3, 1, 3}. Evaluation (16384
held-out inputs, halves A/B): each layer's rate, nMSE and Lagrangian (extra bits at fixed distortion ~ change in
Lagrangian / lambda); predictability of y_{l+1} from y_l: R^2 of the best affine map (lin), coordinate-wise affine
(diag), and an MLP (mlp: the ceiling of what is predictable at all).
Predictions (lambda = 0.01, mu = 1 against mu = 0 of the same pair):
- U1 ReLU pairs with l >= L/4: lin >= 0.9 x mlp on >= 75% of pairs, with each layer's Lagrangian up by <= 2%.
- U2 tanh4 pairs: lin <= 0.7 x mlp, or a Lagrangian up by > 5%, on >= 75% of pairs.
- U3 mlp rises by <= 0.05 on >= 75% of all pairs (the penalty reparametrises; it does not add predictable information).
- U4 ReLU pairs with l >= L/2, 'diag' map: diag >= 0.8 x mlp on >= 75% of pairs.
Reported against the layer map itself: the linear share of the layer path from P2.0 part 2 for the same pairs.

## Amendment P1-B (phase 2c: more exploration of the local class; registered before any P1-B run, smoke run on dev only)
Code: gpu_src/scripts/run_vr_cert3.py (hashed below). Cells: the local cells at l in {0, L/4, L/2} of the 12 ReLU
nets, the two ReLU local cells without P1-A results (32x8 s5001 l = 6, 7), and the 15 local cells of the controls.
Per cell: 6 explorer restarts (gates at the net's next layer exact, jitter 0.1 x2, jitter 0.3 x2, random gates;
output layer fitted on pilot samples), 6000 steps, and 2 more (exact, jitter 0.1) trained 12000 steps; P1 lambda grid.
R* of a cell becomes the minimum over all codes of the class (P1, P1-A, P1-B).
- B1 the best P1-B code lowers R*(0.1) by <= 5% against the P1-A explorers on >= 75% of the early-layer ReLU cells.
- B2 the 12000-step explorers are within max(0.5 bit, 5%) of the best 6000-step explorer on >= 75% of all cells.

## Amendment P2.0-b (phase 2d: P2.0 part 5 on noisy nets; registered before any run, smoke run on dev only)
Code: gpu_src/scripts/run_vr_noisy.py (hashed below): Model S of S4 (sigma = 1), distortion with common random numbers
(the decoded state runs through the real future with the same noise), local class, the P1 method with 3
variable-rate restarts, consecutive layers 16x16: 8-13, 32x32: 16-21, seeds 5000-5002 (36 cells). Analysis (CPU,
script hashed before it reads results): at lambda = 0.01, T_l = affine and MLP fits between consecutive code means;
T fitted at l scored at l+k (k = 1..4) after orthogonal Procrustes alignment of the codes at l+k onto those at l and
at l+k+1 onto l+1 (fitted on half A, scored on half B). H5 as registered: T fitted at l scores R^2 >= 0.8 at l+4 on
the noisy 32x32 nets for l >= L/2.

## Amendment U-c (corrected Part U rerun; main approved 3 Nov ~00:0xZ, cap +$3.5; registered before any run)
Review r3 found the penalty's variance normaliser detached, which rewards shrinking the next code. run_unscr.py now
(hashed below) keeps the normaliser in the gradient (scale-invariant penalty) and adds a guard
10 x relu(0.5 - Var(y_{l+1}) / Var_start)^2 so the next code cannot shrink below half its starting variance. Same pairs,
mus, lambdas and maps as Part U; outputs Uc_*.json. Reported per mu: rate and distortion of each layer separately,
the Lagrangian-equivalent cost (change in rate + change in distortion / lambda), and an extra-bits-at-matched-
distortion estimate (the rate increase needed on the mu = 0 curve of the same layer to return to its distortion is not
available from one point, so the rate change is reported only where distortion changes by < 5%). U1-U4 rescored
unchanged on the corrected runs; the flawed Part U results stay in the record.
