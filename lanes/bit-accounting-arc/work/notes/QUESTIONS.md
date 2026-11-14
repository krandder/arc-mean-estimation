# bit-accounting-arc: assumptions and open questions (leaf pool-qxszj1.26.1, 2 November 2026, 03:10Z)

Lane: per-layer bits-vs-accuracy curves on ARC 256 x 32 (seeds 4000-4003) and narrow-deep 8 x 256 (seeds 203, 216,
217, 220, 221, 223); phase 1 only. Sibling lane work/bit-accounting/ (small nets, controls) uses the same method; its
FORMAL.md sections 1 and 4 are the theory used here (cited as BA-FORMAL).

Each item: the assumption or question, why it matters, how it is checked.

Q1. What the unrestricted class sees. An unrestricted encoder is any function of h_l; the future g_l is one, so the
encoder is an MLP (width 4n, depth 3) on the whitened h_l and the whitened exact output a = g_l(h_l) (the sibling's
'unres'). A plain MLP of h_l cannot compute 32 layers, so without a the class could not reach the optimum.
Check: certificate 1 (unrestricted curve against the output's own curve at every layer).

Q2. The decoder is unrestricted in both classes (MLP to a state at layer l, then the real future). Its job at early
layers is to find preimages (g_l is many-to-one; reachable outputs A_l = g_l(R^n), BA-FORMAL 1.2 and 4.1). If it
cannot invert the future to the needed precision, BOTH classes are inflated at early layers, not only the
unrestricted one. Check: certificate 1 at l = 0 measures exactly this (the encoder there sees a, so any shortfall is
decoder inversion plus the bounded reachability term); a centroid test (output-space regression E[a | z] on held-out
codes, free reconstructions) at a few lambdas bounds what a better decoder could gain for the same encoder.

Q3. The rate. z = mu(h, lambda) + eps, eps ~ N(0, I_K) fixed; rate = E[log2 q(z|h) - log2 p(z|lambda)], p a learned
factorised mixture. This is an upper bound on I(h_l; z) (gap = KL(true marginal || p)), so a learned curve is an upper
bound on the class's information rate-distortion curve twice over (prior gap and optimisation gap).
Checks: fresh-prior refit on held-out codes (certificate 4); a Gaussian-copula total-correlation estimate of what a
non-factorised prior could save (reported, not a certificate).

Q4. One lambda-conditioned model per (net, layer, class) must be as good as separately trained models.
Check: dedicated fixed-lambda models at 3 lambdas per spot-checked cell; the variable-rate model must not be worse
(within restart noise).

Q5. "Seed noise" = the spread of a curve over training restarts (init and data seeds) on the same net. The spread over
the four ARC nets (six narrow-deep nets) is network variation, reported separately. Check: 3 restarts per checked cell;
2x capacity and 2x steps must lie within that spread (certificate 3).

Q6. Known answers available (noiseless nets): (i) the output's own curve is at most Gaussian reverse water-filling over
eig Cov(a) (the linear analog scheme attains it for any source with that covariance), so a learned output code above it
is a training failure (certificate 2); (ii) the unrestricted curve equals the output's curve at every layer up to the
reachability term (certificate 1); (iii) a planted future of k known directions on a width-256 Gaussian state has the
exact Gaussian rate over its k-dim spectrum, attainable inside our model class (certificate 5).

Q7. Precision. nMSE targets down to 1e-3 need the forward pass of the real net in full fp32 (TF32 rounding over 32
layers would add an nMSE floor of order 1e-4 to 1e-3 on ARC, where V / E|a|^2 ~ 0.07). Check: TF32 off for the fixed
net; evaluation re-run in float64 at a few points.

Q8. Range. ARC needs lambda down to ~1e-6 (rates of hundreds of bits at nMSE 1e-3, slope = number of resolved
dimensions); narrow-deep needs far less. K latents: ARC 256 (= n, enough to describe h_l or a to any precision
linearly), narrow-deep 16. Check: per-latent rates at the smallest lambda (no saturation of K), and the 2x capacity
variant doubles K.

Q9. Slope. Bits per halving of output RMS error = 2 dR / d log2(1 / nMSE); for a Gaussian source at high resolution it
is the number of active dimensions, so the slope is the curve's own count of resolved dimensions, comparable with
N(l, eps) of the relevance lane and with the effective dimension d_l of the bits-bounds formula (section 3.5:
N ~ (d_l/p) log2(D_l(1)/eps^2) gives slope 2 d_l / p). Check: computed from the interpolated curves with restart
error bars.

Q10. The local class (one ReLU layer of width n, then affine) contains h_l -> h_{l+1} (BA-FORMAL 3.1) and, for l >= 1,
the identity (h_l >= 0); at l = 0 it cannot represent a full-rank linear map of x (that needs 2n units). So l = 0 local
is "a code of h_1". Check: stated in the report; the local encoder is initialised at h_{l+1} (h_l itself at l = 31 is
not needed: h_32 = a).

Q11. Narrow-deep states synchronise to a ray from layer 16-32 on (relevance lane), so from there the output is one
number times a fixed vector: the curves should be (1/2) log2(1/nMSE) plus coding loss for both classes. Check: slope
near 1 bit per halving of RMS error; the output curve against Gaussian water-filling.

Q12. Comparisons asked for: relevance lane's N(l, eps) (runs/eval_arc_n256_L32_seed400x.json, layers 0, 4, 8, 16, 24,
28, 31; narrow-deep eval_nd_*), the water-filling prediction over the degree-1 relevance spectrum (R1_evals, top 96)
and over the active-subspace spectrum; the bits-bounds formula (outbox/bits-bounds-2026-11-01.md section 3.5; inputs
PR_l and D_R(1) from work/bits-bounds/results/compare_bitacc.json for seed 4000, recomputed with its code elsewhere).
Check: each comparison names its source file and whether it is a prediction or post hoc.
