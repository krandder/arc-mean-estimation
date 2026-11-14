# Bottleneck design choices (leaf pool-qxszj1.25.2, 22:50Z)

## 1. One model per rate, or one model for the whole curve
Options: (a) a dedicated model per rate on a grid (about 20 rates x 2 kinds x 7 layers x 10 nets = 2800 trainings);
(b) one nested model per (net, layer, kind): bits beyond b are set to 0 ("unknown") with b drawn per example
(nested dropout, successive refinement), channels opened by water-filling of learned importances with C drawn per
example; (c) a rate-conditioned network (the rate as an input) with free per-rate codes.
Chosen: (b). At about 0.45 core per process (load 30+), (a) is out of reach and (c) costs the same as (b) without the
water-filling structure the theory predicts. Gaussian sources are successively refinable under squared error, so (b)
loses nothing there; the loss elsewhere is measured: dedicated single-rate models at three rates on dev and on a subset
of evaluation cells (QUESTIONS.md A3).

## 2. Binary quantiser
Options: sign with a straight-through tanh gradient; FSQ with 2 levels (identical in the forward pass, a rounding STE
in the backward pass); soft-to-hard annealing; Gumbel-softmax bits.
Chosen: sign of the batch-normalised encoder output with the tanh straight-through gradient. FSQ at 2 levels is the
same quantiser; annealing and Gumbel bits add hyperparameters with no expected gain at these code sizes. The batch
normalisation centres each pre-code so bits start balanced (about one bit of entropy each).

## 3. Channel
Options: per-channel learned SNRs with a Lagrangian penalty on C (rates land where they land); softmax allocation of a
fixed C (one model per C); water-filling C_i = max(0, (1/2) log2(gamma_i / theta)) with sum C_i = C exact.
Chosen: water-filling of learned importances (lib/bitlib.waterfill: exact projection, differentiable inside the active
set, tested against bisection). It is the allocation the Gaussian theory gives, it nests across C, and C is exact,
so C(eps) is read off one curve. Unit power by batch normalisation (running statistics at evaluation). The decoder
receives the MMSE-scaled channel output and the per-channel reliability SNR/(1 + SNR), so closed channels read as 0
exactly as masked bits do.

## 4. Loss balancing across rates
Each example's squared error is divided by the running nMSE of its log-rate bin (24 bins), so the objective is about
the sum of log-distortions over rates and the low-distortion end is not ignored.

## 5. Encoder classes
local L_k(w): MLP(h_l) with k hidden GELU layers of width w; look-ahead: MLP(h_l, a); output space: layer L. Sweeps
use k = 2, w = 512 (cost); the encoder-size check uses k in {1, 2, 4}, w in {256, 512, 1024}.

## 6. Training
Fresh inputs every step (no reuse, no overfitting of the data), batch 256, Adam 1e-3 with 2% warm-up and cosine
decay to 1e-5, gradient clipping 10, 3000 steps (dev decides). Decoder output starts at the sample state whose output
is nearest E a (otherwise the l = 0 decoder starts at x = 0, output 0, nMSE ~ 15). Evaluation on 16384 held-out
inputs with a fixed seed per net (paired across models), nMSE with SE, mean error with its noise floor.

## Phase 1 method (2 Nov 03:3xZ; also for the ARC 256x32 / narrow-deep sibling lane: read, do not edit)
Implementation: gpu_src/scripts/run_vr.py (registered as PREREG Part P1; text in notes/P1_prereg_draft.txt until
appended). One lambda-conditioned variable-rate code per (net, layer, class), S7 family (fixed unit noise, encoder-
chosen power, information rate with a learned prior). Kelvin's additions of 03:20Z, all implemented:
1. Identity anchor: encoder initialised as a scaled identity (y = 16 x on the whitened state; local class: relu(x + 8),
   then 16 (u - 8)), decoder as its inverse (z / 16, via a linear skip); lambda annealed upward from 1e-4 over the
   first half of training, so the code sheds the least important directions first.
2. Analytic reference per layer (certificate C7): G = E[J^T J] with J = d a / d x_w at the actual states (cloud-
   averaged, future-weighted Jacobian Gram in whitened coordinates); reverse-water-filled powers p_i = g_i/theta - 1 on
   its eigen-directions, unit noise, linear MMSE decoding, evaluated through the REAL rest of the net; rate by the
   capacity formula. A learned code must match or beat it (else undertraining). Function linref() in run_vr.py.
3. Fixed noise with chosen power and fixed power with chosen noise are the same thing: only the SNR matters.
Other details that mattered on dev seed 9100: per-example lambda with the loss d/lambda + rate let the smallest lambdas
dominate (the variable-rate model was 13-67% worse in Lagrangian than separately trained fixed-lambda models); the
loss is now the Lagrangian divided by a running mean per lambda bin. A factorised prior left ~9% of the rate on the
table at high rate (correlated latents); the prior now has a unit lower-triangular linear map before the factorised
mixture. Certificates per curve: restarts, 2x steps, 2x width, prior refit (8-mixture and full Gaussian on held-out
codes), output-space centroid regressor, fixed-lambda spot check, the linear reference.
