# bit-accounting-arc: pre-registration

Each part is hashed (sha256) with its time in prereg_hashes.txt before any of its evaluation runs. Lane bead
pool-qxszj1.26; design notes notes/QUESTIONS.md, notes/DESIGN.md (sections 1-6, plus the v2 alignment below).

## Part P1: per-layer bits-vs-accuracy curves on ARC 256 x 32 and narrow-deep 8 x 256 (registered before any
## evaluation-net run of this lane's code)

### Disclosure
- Dev nets only before this hash: ARC seed 9100, narrow-deep seed 111, toy seed 9 (k = 16). Seen: v1 dev runs (design
  superseded: identity init, factorised prior; runs/bitarc-1/DEV), v2 smoke runs (300 steps) and v2 dev runs in
  progress (runs/bitarc-1/DEV2), throughput benchmarks (runs/bitarc-2/BENCH*). On dev ARC 9100: the learned output
  code sits far below the Gaussian bound (94 bits at nMSE 0.010 against ~170), the plain unrestricted decoder at l = 0
  stalls at nMSE 0.07-0.15 while its output-space head reaches 0.005 and the preimage refinement 0.04 after 300 steps.
- From other lanes (read before this hash): the sibling lane's ARC A1 fixed-budget counts on nets 4000-4003 (local
  > 256 bits at l <= 4 for nMSE 0.1, 135 at l = 8, 43 at l = 16, ~25 at l >= 24; output Gaussian bound 19-39 bits),
  the relevance lane's N(l, eps) table (medians of 4 nets), the bits-bounds formula table for seed 4000 (its 3.6).
- Design aligned with the sibling lane's phase-1 method after its dev lessons (notes/DESIGN.md "v2" below).

### Nets, layers, classes
- ARC 256 x 32 (W_l = st.W_layer(seed, 256, l), x ~ N(0, I_256), noiseless), seeds 4000-4003; layers
  l in {0, 2, 4, 8, 12, 16, 20, 24, 28, 31} and the output l = 32.
- Narrow-deep 8 x 256 (nd.make_weights('plain', seed, 8, 256), rescaled per layer, nMSE-invariant), seeds 203, 216,
  217, 220, 221, 223; layers {0, 8, 16, 32, 64, 128, 192, 255} and the output l = 256.
- Classes: local (one ReLU layer of width n, then affine; every lambda's encoder is exactly in the class), unrestricted
  (residual FiLM MLP of width 4n = 1024 for ARC and 256 for narrow-deep, 3 blocks, on the whitened h_l and the
  whitened exact output), out (the output's own code at l = L). Decoder in every class: residual FiLM MLP (same width)
  + linear path -> state at layer l -> the real future (out: clipped at 0, a >= 0).
- Toy (certificate 5): h ~ N(0, I_256), future a = G_4 G_3 G_2 G_1 Q' Q^T h, Q, Q' random 256 x k orthonormal, G He-scaled
  Gaussian (linear, rank k): its rate-distortion function is exactly reverse water-filling over its k-dimensional
  spectrum. k in {4, 16, 64}, evaluation seed 1; both classes.

### Method (code: gpu_src/lib/vrlib.py, gpu_src/scripts/run_vr.py, gpu_src/scripts/ref_curve.py; hashed below)
- Code z = g(t) nu(h; t) + eps, eps ~ N(0, I_K) fixed (K = 256 ARC and toy, 16 narrow-deep), t = log10 lambda in
  [-6, 0]. g = a(t) + c(t): a = the analytic water-filled gain over the anchor spectrum, capped at SNR 256, c learned.
  Rate = E log2 q(z|h) - E log2 p(z|t), prior = unit lower-triangular map + factorised 8-Gaussian mixture on the
  standardised code, all lambda-dependent parameters piecewise-linear in t (13 anchors; local encoder weights 7).
- Init (analytic anchor): local = the linear reference code on the eigen-directions of G = E[J^T J] (J = d a / d y,
  whitened state, true law; hidden layer relu(y + 8), exact for y > -8); unrestricted and out = the output's linear
  analog code (PCA-whitened output on the linear path); toy local = random hidden layer. Reference-anchored decoders
  add a lambda-dependent offset frac(t) y* + delta(t) (y* the state whose output is nearest E a, frac the analytic
  fraction of the anchor spectrum not sent at t, delta learned), so the zero-rate reconstruction is not the mean
  state (whose output is far from E a in a deep ReLU net; dev: nMSE 1.1-1.4 at the largest lambdas without it).
- Training: per step 32 lambda groups per model, stratified log-uniform on [t_min, t_hi], t_hi annealed from
  t_min + 0.5 to 0 over the first 30% of steps (Kelvin 03:20Z), newly used anchors warm-started from the next-lower
  lambda; loss per group (R + D / lambda) / running mean in its t bin; output-space head on the detached code trained
  beside it (own normalised MSE). Adam (0.9, 0.99), lr 1e-3 (linear paths, MLP output layers and the local encoder
  3e-5: on dev 9100, l = 0, 1e-4 / 3e-4 raised the high-budget nMSE from 0.06 to 0.2-0.4 within 500 steps, 3e-5 kept
  it at 0.07-0.10), 2% warm-up, cosine to 1%, clip 10 per model, TF32 in the MLPs only (the fixed net in fp32).
  Base: 12000 steps; batch 1024 (ARC, toy) and 2048 (narrow-deep, CUDA graphs for the fixed net); fresh inputs every
  step.
- Evaluation: held-out P = 32768 inputs per net (the same for every process and variant), t grid -6..0 step 0.25.
  Per point: rate (trained prior), three fresh-prior refits (cross-fitted halves: the trained family, factorised only,
  full Gaussian), copula total correlation after the triangular map, nMSE (plain decoder), output-space head nMSE
  (free reconstruction from the code: the centroid test), nMSE after preimage refinement of the decoded state toward
  the head's output (150 Adam steps on 8192 inputs, every second t), output-mean error with its noise floor.
- The rate of a point = the lowest of the trained and the three refitted rates (each an honest held-out upper bound on
  I(h; z)); its nMSE = the plain decoder's, or the refined one where refinement ran and is lower (both are decoders of
  the same code). Curves R(eps): monotone lower envelope, log-linear interpolation (lib/vra.py). Slope = bits per
  halving of output RMS error = 2 dR / dlog2(1/eps) between adjacent eps of EPS = {0.5, 0.3, 0.2, 0.1, 0.05, 0.03,
  0.02, 0.01, 0.005, 0.003, 0.002, 0.001}.

### Runs (in priority order; each process trains seeds x restarts of one (family, layer, class, variant))
1. References (ref_curve.py) for every net and layer: the realised linear reference codes on three spectra ('gram'
   E[J^T J], 'mean' E[J]^T E[J] true law, 'gauss' E[J]^T E[J] under the relevance lane's Gaussian convention).
2. Base: every (net, layer, class), restarts r0, r1 (ARC M = 8 per process, narrow-deep M = 12).
3. Toy: k in {4, 16, 64}, both classes, restarts r0-r2.
4. Certificates on ARC 4000 and narrow-deep 203, every layer and class: r2 (third restart), steps2 (24000 steps),
   cap2 (MLP depth 6, twice the parameters of the unrestricted parts); unrestricted with the 'refu' init (the
   reference code of h_l on the linear path) as an init check.
5. Dedicated fixed-lambda models (spot check) at t in {-2, -3.5, -5} (ARC 4000: l = 0, 16, 31, both classes) and
   t in {-1, -2.5, -4} (narrow-deep 203: l = 0, 64, both classes).
6. If compute remains: r2 on the other nets.
Compute: at most 2 L4s, $25 cap at list price (GPU-LOG.md). If compute runs short, later items are cut in reverse order
and the report says which.

### Certificates (scored by scratch/score_P1.py, written and hashed before scoring; flags per curve)
Notation: R_c(eps) = mean over restarts of the cell's R(eps); spread = max - min over restarts.
- C1 (noiseless: the unrestricted curve reaches the output's own). Shortfall Delta_l(eps) = R_unres,l(eps) - R_out(eps)
  at eps in {0.1, 0.03, 0.01, 0.003, 0.001} where both are reached; flag if Delta > max(0.05 R_out, 1 bit) + spread.
- C2 (output against Gaussian water-filling over eig Cov a). Flag if R_out(eps) > R_G(eps) + max(0.02 R_G, 0.5 bit).
- C3 (capacity, steps, restarts). For each variant v in {r2, steps2, cap2}: flag if R_v(eps) < min over base restarts
  of R(eps) - max(spread, 0.03 R, 0.5 bit) (the base is limited by capacity or training).
- C4 (prior). Flag a point (rate >= 5 bits) if the best refitted rate < 0.97 x the trained rate; reported per curve
  (fraction of flagged points) with the copula total correlation.
- C5 (toy). Flag if |R(eps) - R_known(eps)| > max(0.05 R_known, 1 bit) at eps in {0.1, 0.01, 0.001}.
- C6 (Kelvin's analytic reference). R_ref(eps) = the lowest of the three realised references (information rate);
  flag if R_c(eps) > R_ref(eps) + max(0.02 R_ref, 0.5 bit) (the learned code is worse than the linear code).
- C7 (variable rate against dedicated). Flag if a dedicated model's point (R_f, D_f) lies below the variable-rate
  envelope by more than max(spread, 0.03 R, 0.5 bit) in rate at D_f.
- C8 (decoder). Reported per curve: the head (centroid) nMSE against the plain and refined decoders; a point where the
  head is below the best layer-l decoder by more than 20% is labelled decoder-limited (only the reachability term and
  the inversion separate them).

### Predictions (scored by scratch/score_P1.py)
- P1.1 (shortcut). C1 passes (no flag) on >= 75% of (net, layer, eps) cells with L - l <= 8 (ARC l >= 24, narrow-deep
  l >= 255) where both curves are reached; deeper futures reported.
- P1.2 (local at the input). ARC local R(0.1) at l in {0, 2, 4} >= 4 x R_out(0.1) or unreached, on 4 of 4 nets.
- P1.3 (local near the output). ARC local R(eps) at l = 31 within 15% of R_out(eps) at eps in {0.1, 0.01} on >= 3 of 4
  nets.
- P1.4 (profile). ARC local R(0.1) non-increasing in l up to 10% + 1 bit between consecutive layers on >= 3 of 4 nets;
  the same for narrow-deep on >= 5 of 6.
- P1.5 (slopes). ARC local slope near eps = 0.01 (between 0.02 and 0.005) larger at l = 0 than at l = 31 on 4 of 4
  nets; narrow-deep slopes at eps <= 0.01 for l >= 32 (both classes) in [0.8, 1.6] bits per halving on >= 5 of 6 nets.
- P1.6 (relevance lane). ARC local slope near eps = 0.01 within [0.5, 2] x the relevance lane's N(l, 0.01) at
  l in {16, 24, 28, 31} on >= 75% of (net, layer) cells (both lanes measured on nets 4000-4003).
- P1.7 (bits-bounds 3.5). ARC net 4000 local R(0.1) within a factor 2 of the formula's (d = PR) values at
  l in {4, 8, 16} (its table 3.6).
- P1.8 (reference). C6 passes on >= 90% of (net, layer, class, eps) cells; at l = 31 (ARC) the local curve is within
  10% of the 'gram' reference at eps in {0.1, 0.01} on >= 3 of 4 nets (one layer of future is nearly linear).
- P1.9 (non-Gaussian output). C2 passes on all nets; R_out(0.01) <= 0.8 R_G(0.01) on >= 3 of 4 ARC nets.
- P1.10 (narrow-deep synchronisation). Both classes at l >= 32 within max(0.5 bit, 10%) of R_out(eps) at eps in {0.1,
  0.01} on >= 5 of 6 nets; local R(0.1) at l = 0 >= 3 x R_out(0.1) on >= 5 of 6.
- P1.11 (mean). Where nMSE <= 0.1, the output-mean error < nMSE / 10 on >= 90% of points with a resolved mean error.
- P1.12 (toy). C5 passes for both classes at k = 4 and 16; at k = 64 reported.
All misses are reported with their cells; flagged counts are shown as upper bounds with the flag.

## notes/DESIGN.md v2 (aligned with the sibling lane, 2 Nov 04:30Z; supersedes DESIGN sections 2-3 where different)
- Gains: analytic water-filled gain over the anchor spectrum (capped at SNR 256) plus a learned correction, instead of
  free log-gains; prior on the standardised code with a unit lower-triangular map (the sibling found ~9% of the rate
  left by a factorised prior at high rate); init at the linear reference code on E[J^T J] (Kelvin's identity anchor at
  high budget); lambda annealed upward with continuation; per-lambda loss normalisation; Adam betas (0.9, 0.99).
- Differences kept, with reasons: wider lambda range (ARC needs ~1e-6 for nMSE 1e-3); unrestricted init on the
  output's analog code (the class optimum is the output's code; the reference-code init 'refu' is run as a check);
  12000 base steps (the sibling: 6000 on small nets; doubling helped by up to 27% there, so steps2 is a certificate
  on every layer of one net per family); an output-space head and preimage refinement (dev: the plain unrestricted
  decoder cannot invert 32 layers precisely); decoder reconstructions may leave the data's span (dead units).

## Amendment A1 (2 Nov 04:44Z, before any evaluation-net result; registered with its hash)
The analytic gain cap AMAX = 16 (SNR 256, ~4 bits per direction) bounds the reachable rate: at most ~4 bits per
anchor direction (narrow-deep: one direction from l >= 32, so nMSE could not fall below 1/257 = 0.004; ARC local at
l = 0: ~1030 bits, nMSE >= ~0.05 on dev 9100). Seen before this amendment: the dev 9100 learning-rate check
(runs/bitarc-2/LRCHK) and the training logs (not evaluations) of the first 5-25% of three evaluation processes (ARC
l = 31 local, ARC output, narrow-deep l = 255 local, whose training batches sat at ~3.5-4 bits and nMSE ~0.005 at the
smallest lambdas). Those three processes were stopped and every evaluation run restarts with AMAX = 256 (SNR 65536,
8 bits per direction; the learned correction can add more). Nothing else changes. Queue: gpu_src/queue/11_eval.sh
(same commands as 10_eval.sh), 12b_vm1_early.sh, 13_vmB_milestone.sh.

## Amendment A2 (2 Nov 04:50Z, before any evaluation-net result)
TF32 rounding in the precision-critical matmuls: the linear decoder of the unrestricted code at l = 31 contains
W_32^{-1}, which amplifies the TF32 rounding by its condition number; on dev 9100 the initial nMSE at the smallest
lambda was 0.033 with TF32 against 1.6e-4 in fp32 (runs/bitarc-4/TF32CHK). From A2 on, every precision-critical
matmul runs in full fp32 (linear paths of encoder and decoder, whitening frames, the MLP output layers, the local
encoder, the prior's triangular map); TF32 only inside the MLP hidden layers (fp32 verified to give the same initial
nMSE, 1.65e-4). Seen before A2: training logs (not evaluations) of the first minutes of the A1 processes. All
evaluation processes restart (queue 21_eval.sh, 22_vm1_early.sh, 23_vmB_milestone.sh: the same commands).

## Amendment A3 (2 Nov 05:01Z, before any evaluation-net result; an added variant, nothing else changes)
The gpt-6-astra code review of the sibling lane (work/bit-accounting/review/review_r2a.raw) found its reference-started
local encoders effectively affine (every ReLU threshold > 7 SD from the data): the nonlinear part of the local class was
not explored. The same holds here by construction (relu(y + 8), encoder lr 3e-5). Added variant 'h1': the local encoder
starts at the exact one-layer look-ahead (hidden layer = relu(W_{l+1} h_l) = h_{l+1}, code = the reference code of
h_{l+1} on G_{l+1}, decoder = its MMSE inverse pulled back through W_{l+1}^{-1}); ARC net 4000 at every layer, and all
six narrow-deep nets at every layer (queue 24_h1.sh). The local count of a cell is the lower envelope over its 'ref'
restarts and 'h1' (both are codes of the class); the report gives both and flags cells where they differ by more than
the restart spread. Dev 9100 (init only, before training): at l = 16 'h1' starts with a high-budget floor near nMSE
0.003 (ref 1.6e-4) and matches 'ref' within ~15% at 100-250 bits.

## Amendment A4 (2 Nov, after the gpt-6-astra code review r1 (review/review_r1.raw, 05:11Z); before any evaluation
## result was scored or inspected beyond one training log line)
Measurement changes (reruns of the affected cells):
- r1 #1: the Jacobian statistics G = E[J^T J] and E[J] are taken through the data-span frame S^{1/2} (not the
  full-rank decoder frame), so the anchor and reference coordinates have unit variance on the data's span (pre-A4 the
  dead-unit null directions carried spurious future weight). Affected and rerun: every reference-anchored and 'h1'
  local code and every reference curve; unrestricted and output codes (anchored on Cov a) are unaffected and keep
  running (outputs pre-A4 kept in /root/runs/P1_superseded_A4, not used).
- r1 #13: the output head (trained on detached codes) is clipped separately from the main model.
Scoring changes (scratch/score_P1_v2.py, hashed before scoring; the registered score_P1.py is run too and both are
reported):
- r1 #2: the rate of a point is the trained prior's held-out rate (no selection among priors); refits are reported
  as diagnostics (C4), not used in the counts.
- r1 #3: the refined decoder is scored on its own subset against the plain decoder on the same subset (no
  extrapolation); the decoder of a cell is fixed per class in advance: plain for local, the better of plain and refined
  per point for unrestricted (two decoders, 8192 inputs; the selection is reported).
- r1 #4: R(eps) used for counts interpolates linearly in nMSE between evaluated points (time-sharing, achievable);
  the log-linear value is reported beside it as descriptive.
- r1 #5, #6, #8: the 'h1' envelope and flag of A3 are implemented; base = restarts 0-1, the certificate restart = 2;
  missing, unreached, pass and fail are distinguished against the expected-cell inventory.
- r1 #9 (scope, correcting the Runs list): 2x steps and 2x capacity run on ARC 4000 at l = 0, 8, 16, 24, 31 and the
  output, and on all six narrow-deep nets at l = 0, 64, 255 and the output; the third restart on every ARC-4000 cell
  and every narrow-deep cell. Cells without the steps/capacity checks are reported as "not checked for steps and
  capacity", not as certified.
- r1 #7: fixed-lambda jobs use --fixlam=...; r1 #10-#12, #14 are disclosed in the report (C4/C8 are diagnostics, not
  tightness certificates; D_lin for the Gram spectrum is not a distortion prediction; backward matmuls may use TF32).

## Amendment A5 (2 Nov 05:28Z; process and diagnostics only, before any evaluation-net result)
The prior refits (a diagnostic since A4) cost ~50 s per (model, lambda) for K = 256 on a shared L4, ~2.7 h per 8-model
ARC process. From A5: refits every 4th lambda point (7 points), 40 EM iterations, on the first 16384 held-out codes;
references: lambda step 0.5 (13 points), information rate = min(factorised refit, capacity formula) (both upper-bound
the information of a linear Gaussian-channel code). The ARC 8-model processes that had started with the old
evaluation (l = 31 local and unrestricted, the output cell) are stopped and rerun (queue 35_rerun_a5.sh and the
31_eval.sh chain). The primary rate (trained prior, 32768 inputs) and every training detail are unchanged.

## Amendment A6 (2 Nov, before any toy run; an added variant)
The registered toy uses a random local start; the nets use the analytic reference start. With the low encoder
learning rate (3e-5, set for precision), a random start may not find the k directions within 12000 steps, which would
test the start rather than the code, prior and decoder. Added: the toy local class with the nets' 'ref' start
(variant 'toyref', restarts 0-2, k = 4, 16, 64; queue 36_toyref.sh). For a linear Gaussian future the reference code is
the optimum, so 'toyref' checks that training, the prior and the rate estimate keep the known rate (it is a weaker test
than the random start, which is still scored as registered).

## Amendment A7 (2 Nov 06:36Z; an added variant, before its runs)
Seen: on ARC net 4000 the 'h1' start beats the reference start at l = 0 (575 against 642 bits at nMSE 0.1; 273
against 375 at 0.3; 4% at 0.01) and ties at l = 31. Added: 'h1' on ARC nets 4001-4003 at l = 0, 2, 4, 8 (queue
38_h1_more.sh), so the early-layer local counts use both starts on every ARC net. The local count of a cell stays the
better of its starts (A3); cells with only one start are marked as such.

## Amendment A8 (2 Nov 08:39Z; reduced plan for the remaining compute, before the affected runs)
Three spot preemptions cost ~2 GPU-hours, and the registered queue projected to finish after 18:00Z. From A8:
- ARC local base for the layers not yet run: restart 0 only (all four nets per process); restarts 0-1 stay where they
  ran (layer 31) and restart 2 on net 4000 at layers 0, 16, 31. The restart spread is reported where it was measured.
- ARC unrestricted: all four nets at layers 0 and 31 (run or running); net 4000 restart 0 at layers 8, 16, 24; the
  other layers are not run (the unrestricted curve tests decoder inversion, which these five depths bracket).
- Narrow-deep unrestricted at layers 0, 8, 16, 64, 255 (local at every layer, as registered).
- Steps/capacity certificates: ARC net 4000 at layers 0, 16, 31 and the output (both classes); narrow-deep (all six
  nets) at layers 0 and 255 and the output. Fixed-lambda checks: ARC net 4000 layers 0 and 31 (local), 31
  (unrestricted); narrow-deep 203 layer 0 (local). Everything else as registered (A3/A7 'h1' runs, the random-start
  toy, references). Queue: gpu_src/queue/51_A.sh, 51_B.sh (the 41_eval.sh, 33 and 35 chains are stopped; jobs that
  were already running continue).

## Amendment A9 (2 Nov 09:17Z; an added convergence check, before its run)
Seen: C3 (2x steps) fails at ARC net 4000 layer 31 local: 24000 steps give 84 / 161 / 265 bits against the base's
90 / 181 / 299 at nMSE 0.01 / 0.003 / 0.001 (up to 12% fewer); 2x steps changes layer 0 by < 1% and layer 16 by
1-5%. Added: 4x steps (48000) at layer 31 local (variant steps4, queue 53_A_steps4.sh), to see whether 24000 steps
converged. The report quotes the base counts with this flag and the best certificate-run counts beside them.

## Amendment A10 (2 Nov 09:29Z; scheduling of the A8 jobs, and an added variant, before the affected runs)
Seen: on one VM the A8 chains are sequential and project to finish after 18:00Z (chain A1, nine 4-net local
processes, ~6 h; chain A2, the narrow-deep local layers with 3 restarts, ~8 h). Changed (scheduling only, same jobs):
from bitarc-6, VM B runs the ARC local base at layers 2, 20, 12, 28 and the narrow-deep local base at layers 8, 192, 32
(VM A's chains reach these last), and the remaining 51_B.sh jobs, in six parallel chains of at most 5 processes
(gpu_src/queue/57_B.sh; 51_B.sh and 52_B are retired). The post-hoc decoder diagnostic (not registered) moves to the
layers whose unrestricted models this VM saves (16, 8, 24). Added: the 'h1' start on ARC nets 4001-4003 at layers 16,
24, 12, 20, 28 (lowest priority, after everything else on VM B), so that every ARC net and layer has both local starts
(A7 covered layers 0-8); cells without both starts remain marked.

## Amendment A11 (2 Nov 09:39Z; an added convergence check, before its run)
Seen (scorer v2 on the finished certificate runs): at ARC net 4000 layer 31 local both C3 variants beat the base at
nMSE <= 0.03: 2x steps 84 / 161 / 265 bits, 2x depth 85 / 167 / 281, base 90 / 181 / 299 at nMSE 0.01 / 0.003 /
0.001 (at layer 0 neither moves by more than 0.5%). Added: depth 6 with 48000 steps together (variant cap2steps4, one
restart, queue 58_B_l31_conv.sh), the corner of the two checks; with A9's 4x steps it shows whether the late-layer
high-precision counts are still moving. The report quotes the base counts, flagged, with the lowest certificate-run
count beside them.

## Amendment A12 (2 Nov 09:50Z; added fixed-lambda checks, before their runs)
Seen: C7 at ARC net 4000 layer 0 local passes at t = -3.5 and -5 (dedicated models 1.1% and 0.9% below the
variable-rate curve, within tolerance) and fails at t = -2: the dedicated model reaches nMSE 0.73 with 4.0 bits, where
the variable-rate curve (reference start) has a gap (3.3 bits at nMSE 0.785, then 116 bits at 0.734); the look-ahead
start's variable-rate curve reaches nMSE 0.72 with 1.8 bits. Added: dedicated models at t = -2.25, -2.5, -2.75 (the
variable-rate curve's nMSE 0.3-0.7) from the reference start (variant fixlamlo) and from the look-ahead start (variant
fixlamh1), queue 59_B_fixlam_low.sh. They are compared with the variable-rate curve of the same start, and the report
marks the low-rate end of the early-layer local curves as uncertified where a dedicated model is better.

## Amendment A13 (2 Nov 09:55Z; an added optimiser check, before its runs)
Seen: from the registered random start the local class misses the planted toy by far (k = 64: 203 against 80 bits at
nMSE 0.1; unreached below 0.03), while from the reference start it is within 2.4%; the two informed starts differ by
10-27% at nMSE 0.1-0.3 on the nets. The local encoder's weights train at lr 3e-5 (set for precision), so training
refines its start rather than searching the class. Added: the look-ahead start with a 10x encoder learning rate (3e-4,
linear paths unchanged) at ARC net 4000 layers 0, 8, 16 (variant h1lr) and the reference start with it at layer 8
(variant reflr), queue 62_A_lr.sh (VM A from bitarc-7). A run with fewer bits than both starts at some accuracy lowers
the local count there (better of all starts) and marks that region as optimiser-limited.

## Amendment A14 (2 Nov 10:16Z; added convergence checks and VM A's remaining queue, before their runs)
Seen: at ARC net 4000 layer 31 local, 4x steps lowers the count by 10% at nMSE 0.01 and 18% at 0.001 and is still
falling (2x -> 4x: a further 4-8%); dedicated fixed-lambda models (C7) need 6-17% fewer bits than the 12000-step
variable-rate model, and the 48000-step one is within -1% to +5% of them. Added: 4x steps for the output cell and for
layer 24 local (net 4000, variant steps4), so the report can say how far the late-layer high-precision counts may still
fall. VM A's remaining jobs (the A8 chains' leftovers and A10's look-ahead runs from the other end) are in
gpu_src/queue/61_A.sh for bitarc-7, which replaces 51_A.sh, 53_A_steps4.sh, 38_h1_more.sh and 34_h1.sh (retired).

## Amendment A15 (2 Nov 10:26Z; an added search check, before its runs)
Seen: at narrow-deep layer 0 the look-ahead start needs 13-56% fewer bits than the reference start at nMSE 0.1 (12-21%
at 0.001; restarts of each start agree within 0.3 bit), and a 10x encoder learning rate from the look-ahead start
does not lower ARC layers 0 and 8 (+2 to +7%; A13). Added: a random local start with the encoder learning rate at the
MLP's (1e-3) at narrow-deep layer 0 (six nets, restarts 0-2) and ARC net 4000 layer 8 (variant rndhi; queue
64_A_rnd.sh). A run below both informed starts at some accuracy lowers the local count there and marks it
search-limited; a run above them is reported as such.

## Amendment A16 (2 Nov 10:55Z; an added convergence check, before its run)
Seen: at ARC net 4000 layer 31 local, depth 6 with 4x steps (A11) lowers the count by 14 / 22 / 24% at nMSE 0.01 /
0.003 / 0.001 (4x steps alone 10 / 17 / 18%), and the output cell with 4x steps (A14) by 17 / 19 / 18%. Added: depth 6
with 8x steps (96000) at layer 31 local (variant cap2steps8, queue 65_A_conv8.sh, VM A from bitarc-7), to see whether
the late-layer high-precision counts level off and where.

## Amendment A17 (2 Nov 11:34Z; added search checks, before their runs)
Seen (A15): the random local start with encoder learning rate 1e-3 needs 2-3x fewer bits than the better informed
start at 30% error at narrow-deep layer 0 (0.9-2.5 against 2.1-6.3 bits; half at 10% on one net) and 25-35% fewer at
ARC net 4000 layer 8 at 20-30% error (6 / 22 against 9 / 30 bits), but does not reach 10% error on most nets. So the
low-precision local counts at early layers are search-limited. Added: the random start with a moderate rate (3e-4,
variant rndmid) at ARC net 4000 layers 0 and 8 and narrow-deep layer 0 (six nets, restarts 0-2), and the high rate at
ARC layer 0 (rndhi), queue 66_A_rnd2.sh: does the search limit extend to 10% error and to the input layer? The local
count stays the lowest over all runs of a cell at each accuracy, reported with the run that gives it.

## Amendment A18 (2 Nov 11:40Z; a convergence subset, on the coordinator's request, before its runs)
Request (main, relaying the bar): no ARC cell can be certified; rather than spreading compute over all cells, push a
small registered subset to convergence and report the converged counts beside the current upper bounds.
- Subset: ARC net 4000, layers 0, 16, 31, both classes, at nMSE 0.1 and 0.01 (12 numbers).
- Count of a (cell, accuracy): the lowest bits over every run of the cell (any start, variant or dedicated model),
  reported with the run that gives it.
- Converged: along the run that gives the count, doubling the steps changes it by < 3%, and so does doubling the
  depth (unrestricted: also the width); for local cells, in addition, no other search (the other informed start; random
  starts with encoder learning rates 3e-4 and 1e-3) is lower by 3% or more. Otherwise "not converged", with the
  last change per doubling.
- Round 1 (queues 67_B_conv.sh on VM B, 68_A_conv.sh on VM A; with A16 and A17): layer 31 unrestricted 4x steps,
  depth 6 + 4x steps, depth 6; layer 16 unrestricted 4x steps, depth 6 + 4x steps; layer 16 local look-ahead start with
  2x and 4x steps and depth 6, random starts (lr 1e-3, 3e-4); layer 0 unrestricted 4x steps, depth 6 + 4x steps, width
  2048 with 2x steps; layer 0 local look-ahead start with 2x and 4x steps and depth 6; layer 31 local depth 12 + 4x
  steps; the layer-31 unrestricted fixed-lambda check (C7).
- Round 2 rule: where a (cell, accuracy) is not converged after round 1, double again along the axis that moved it
  most (steps to 96000, depth to 12), while the budget allows; the report gives the last change per doubling.
- Cut to make room (cells marked "not run (A18 cut)"): narrow-deep local base at layers 16, 32, 128; narrow-deep
  unrestricted at layer 8; the narrow-deep local, unrestricted (layer 255) and output steps/depth checks not yet run;
  ARC net-4000 output 2x steps and 2x depth (its 4x-steps run exists); A10's look-ahead runs on nets 4001-4003 at
  layers 12-28 not yet started. Kept: ARC local base at every layer (layer 4 in 69_A_rest.sh), the narrow-deep layer-0
  fixed-lambda check. 57_B.sh and 61_A.sh are retired; queues for later VMs hold only A16-A18 work.
- Budget estimate at list price: ~$23 in all (round 1 fits the running VMs; round 2 ~3 h of one more L4); a third
  round would add ~$3-4. Cap $40 (main), with notice before passing $25.

## Amendment A19 (2 Nov 12:25Z; Kelvin's backward curriculum as another start, and consistency flags, before their runs)
Request (main relaying Kelvin): converge the last layer first, then warm-start each earlier layer from the next one's
code composed with the one-layer map (the look-ahead start is the one-step version); register it as another start in
A18, with the same convergence rule (no start lower by 3% or more); report which cells it lowers and by how much; and
flag violations of the noiseless-net orders as undertraining.
- Start 'bwd' (scripts/run_vr.py --init bwd --bwd_pt, local class): the hidden layer computes h_{l+1}; the readout is
  first the least-squares fit of the later code's latents on h_{l+1}, then the whole one-ReLU-layer encoder (every
  encoder anchor) is distilled for 3000 Adam steps onto the later code's signal g * nu (its gains as weights), which
  projects the composed code onto the local class (on the layer-28 test the gain-weighted R^2 is 0.98-1.0 at six of
  seven anchors); gains and prior are copied; the decoder starts at the least-squares linear map from the new latents
  to the layer's state; no lambda annealing (the later code's per-price structure is kept). Smoke tests (300 steps,
  not results) in /root/runs/BWDTEST on bitarc-6.
- Chain (ARC net 4000; queue 71_A_bwd.sh, VM A): layer 31's best code (depth 6, 4x steps; A11) starts layer 28; each
  finished layer starts the next earlier measured layer: 28, 24, 20, 16, 12, 8, 4, 2, 0 (12000 steps each); then 2x
  steps at layers 16 and 0 from the same sources. The measured layers are 4 apart in places, so the composed map spans
  up to four layers; the class projection is what the distillation fits.
- Flags (scratch/consistency.py): any count above the lower envelope of all codes of its net by > 3% where theory says
  it should equal it: the output cell's code, and unrestricted codes at every layer (all equal R_a); and unrestricted
  counts that rise toward the input between consecutive measured layers (R_l <= R_l' for l < l'). Each flag reads as
  undertraining (or, for unrestricted codes at early layers, the decoder's inversion).

## Amendment A20 (2 Nov 13:16Z; analysis corrections from review round 2, before the final scoring)
Review r2 (gpt-6-astra, review/review_r2.raw; verdict "fixable issues", 14 findings) found errors in the analysis, not in
the runs. Corrections, applied to every table from now on (earlier outputs are kept under results/*_partial*):
- Common normalisation: each run's distortion was divided by its own layer's pilot estimate of the output variance
  (different samples per layer; up to 3.6% apart). Every nMSE is rescaled to one variance per net, V_net = the mean of
  that net's pilot estimates over all layers (lib/vra.py at load time).
- Time-sharing: the achievable curve of a run is the lower convex hull of its evaluated (nMSE, rate) points (any two
  codes can be time-shared), not linear interpolation between adjacent Pareto points; where the two differ by > 3% the
  report gives both.
- Named quantities: (i) the registered local count = the better of the reference and look-ahead starts (A3/A7), per
  net and accuracy; (ii) the best individual run of a cell (any start, variant, or dedicated fixed-lambda point with
  nMSE <= eps), reported with the run; (iii) the output's curves: the C1 baseline (the output cell's base), the table
  envelope (base and look-ahead runs of all layers and the output cell) and the best-known envelope (all runs).
- Scorer v3 (scratch/score_P1_v3.py): local predictions use the registered count (i); pass, fail and not evaluable
  (cells cut by A8/A18 or not run) are kept apart; P1.5 checks every evaluated interval between nMSE 0.01 and 0.001.
  The v1 and v2 outputs are kept and reported.
- A18 rule, as registered, with matched partners: the doubling partner of the best run must equal it in every other
  setting (start, depth, width, steps); the change must be < 3% in absolute value; a missing partner leaves that axis
  unverified. Queue 76_conv_partners.sh adds partners for the subset's best runs where they are cheap.
- Export (results/certified_curves.json): separate statuses for the registered certificates, the A18 convergence
  verdict (subset cells), the A19 consistency flags and C7; checks borrowed from net 4000 are labelled as such;
  bits_best_known = the lowest individual run or dedicated point.
- Wording: the unrestricted equality with R_a and the monotonicity across layers need the reconstruction to be
  reachable through the remaining layers (the image of the rest of the net can be nonconvex), so their violations read
  as structural, capacity, prior or optimisation limits, not only undertraining; the spectrum and slope explanations
  are HEURISTIC; local "2x depth" doubles the decoder, not the class's one-layer encoder.

## Amendment A21 (2 Nov 13:32Z; a one-step variant of the backward start, before its runs)
Seen: the A19 chain loses precision as it compounds (layer 28: +1% / +7% at 10% / 1% error against the better
informed start; layer 24: +16%, 1% not reached; layer 20: 42 against 19.7 bits at 10%, 1% not reached). Added: the
backward start from the next measured layer's look-ahead code, one step, no chain (variant bwd1): layer 16 from layer
20, layer 0 from layer 2 (queue 77_A_bwd1.sh). It enters the A18 start comparison like the other starts.

## Amendment A22 (2 Nov 14:46Z; round 2 again after a preemption, before its runs)
bitarc-7 (spot) was preempted at ~14:32Z; its final sync failed, so its unfinished runs are lost (results pulled up to
14:30Z are kept: the layer-4 base, the layer-0 unrestricted 4x-steps run, the backward chain at layers 28, 24, 20, the
narrow-deep fixed-lambda check). Its saved models (.pt) are lost. Relaunched on one L4 (bitarc-9) with round 2 of the
convergence subset only (queue 80_A_round2_relaunch.sh): depth 6 with 8x steps at layer 31 local and at layers 16 and 31
unrestricted, the look-ahead start with 8x steps at layer 16 local, and layer-0 unrestricted depth 6 with 4x steps. Not
rerun: the rest of the backward chain (layers 16 to 0; the one-step variant A21 ran at 16 and 0), the width partners,
the random start on narrow-deep layer 0 at the moderate rate, layer-0 local 4x steps and layer-31 depth 12. They are
reported as not run.
