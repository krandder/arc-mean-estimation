# bit-accounting-arc: design choices (leaf pool-qxszj1.26.2, 2 November 2026, 03:20Z)

Fixed by the brief: real-valued code with fixed unit Gaussian noise and an encoder-chosen scale; rate =
E[log2 q(z|h) - log2 p(z)] with a learned mixture prior; one variable-rate model per (net, layer, class) with lambda as
an input; classes unrestricted (width >= 4n, depth >= 3) and local (one ReLU layer of width <= n, then affine);
distortion = forward-propagated output nMSE. Choices below, each with the options considered.

## 1. How lambda enters (t = log10 lambda)
Options: (a) FiLM (per-unit scale and shift from t) everywhere; (b) gain units only (one shared encoder, per-latent
gains interpolated in t; Cui et al. 2021); (c) separate heads per lambda on a grid; (d) a hypernetwork for all weights.
Chosen: piecewise-linear anchors in t ("hat" interpolation) for every lambda-dependent parameter, which makes each
parameter an arbitrary continuous piecewise-linear function of t:
- local encoder: A1, b1, A2, b2 at 7 anchors (one per decade): for each fixed lambda the encoder is exactly one ReLU
  layer of width n then affine (in the class), and different lambdas may use different features (FiLM on a shared A1
  could not);
- latent gains log g_k(t) and the prior's mixture parameters at 13 anchors (half a decade);
- unrestricted encoder and the decoders: residual GELU MLPs whose blocks are FiLM-modulated by anchored scales/shifts.
Spot-check against dedicated fixed-lambda models at 3 lambdas (QUESTIONS Q4).

## 2. Code and prior
z = g(t) * nu(h; t) + eps, eps ~ N(0, I_K). The encoder outputs a roughly unit-scale nu; the gain g carries the SNR.
Prior per latent in the same normalised coordinate: p(z_k | t) = sum_j pi_kj N(z_k; g_k m_kj, g_k^2 s_kj^2 + 1),
J = 8 components, anchored in t. This is exact when nu_k is a Gaussian mixture, keeps all prior parameters O(1) at
every lambda (a prior in raw z would need means of +-100 at the smallest lambda, out of reach of Adam), and makes an
unused latent (g -> 0) cost exactly 0 bits. Options rejected for training: autoregressive (MADE) or hyperprior
models (tighter but slower and harder to certify); a non-factorised check is reported instead (Gaussian-copula
total correlation of the held-out codes). E log2 q(z|h) = -(K/2) log2(2 pi e) is used exactly (no MC noise).
Decoder input: the per-latent MMSE scaling z * g / (1 + g^2) (unit scale at every lambda) plus t through FiLM.

## 3. Initialisation (known achievable points, no use of the answer)
- Local at layer l: A1 = W_{l+1} S_l^{1/2}, b1 = W_{l+1} m_l, so the hidden layer is h_{l+1} exactly; A2 = PCA
  whitening of h_{l+1}; the decoder's linear path is the exact linear decoder of h_{l+1} pulled back through
  W_{l+1}^{-1}. At init the model is the linear code of h_{l+1} (BA-FORMAL 3.1); at l = L - 1 that is the output's
  linear analog code.
- Unrestricted and output: a linear path nu = MLP + PCA-whitened output coordinates (MLP last layer zero), so at init
  the code is the output's linear analog code; at l = L the decoder's linear path is the exact linear decoder.
- Gains: reverse water-filling over eig Cov(a) at each anchor's lambda (theta = lambda V / (2 ln 2)).
- Decoder bias: the whitened sample state whose output is nearest E a (as the sibling lane).
- Toy (certificate 5): random encoder init (the toy future has no ReLU, so the h_{l+1} init does not apply).

## 4. Loss balancing across lambda
Each step draws G = 32 lambda groups per model, stratified log-uniform on [t_min, t_max]. Per group L = R + D / lambda
(bits), divided by a running mean of L in its t bin (24 bins). Dividing a group's Lagrangian by a constant leaves its
minimiser unchanged; the normalisation only stops the high-rate groups (L ~ hundreds of bits) from drowning the
low-rate ones (L ~ a few bits) in the shared parameters.

## 5. Batching and compute
One process trains M models of one (family, layer, class, variant): seeds x restarts (models are independent: batched
weights with a leading M axis, per-model gradient clipping, Adam is elementwise). The fixed net runs as one batched
matmul per layer over seeds. MLP matmuls in TF32; the fixed net's forward pass in full fp32 (Q7); evaluation in fp32.
Fresh Gaussian inputs every step (no data reuse). Adam 1e-3, 2% warm-up, cosine to 1e-5, clip 10 per model.
Sizes: ARC K = 256, MLP width 1024 (= 4n), 3 residual blocks; narrow-deep K = 16, width 256 (>= 4n), 3 blocks.
Variants: base (restarts r0-r2), cap2 (2x width and 2x K), steps2 (2x steps), fixlam (dedicated models at 3 lambdas).

## 6. Evaluation
Held-out inputs (fixed seed per net, P = 32768) at a t grid of step 0.25; per point: rate under the trained prior and
under a fresh prior refitted on half the codes and scored on the other half (both halves), nMSE with SE, error of the
output mean with its noise floor, per-latent rates, copula total correlation. Curves R(eps) by log-linear
interpolation in (rate, log nMSE) on the monotone lower envelope; slope = 2 dR/dlog2(1/nMSE) (bits per halving of
the output RMS error).
