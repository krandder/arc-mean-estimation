# Bit-accounting lane: assumptions and open questions (leaf pool-qxszj1.25.1, 1 November 2026, 22:30Z)

Each item: the assumption or question, why it matters, and how it is checked.

## A. The per-layer bottleneck (part A)

A1. In a noiseless net (ARC 256 x 32, narrow-deep 8 x 256) the information about the output carried by h_l is that
of the output itself at every layer (bits-bounds lane FORMAL.md Prop 3.6, PROVEN [C+A] there). For bottlenecks this
gives a sandwich: with unrestricted encoders, b_out(eps) <= b_l(eps) <= b_out^supp(eps) at every l, where b_out is the
bit count for compressing the output a itself with free reconstructions and b_out^supp the same with reconstructions
restricted to actual outputs; b_l(eps) is non-increasing in l.
Check: proof written in FORMAL.md section 1 (to be reviewed by gpt-6-astra); measured with 'ahead' encoders (they see
a = g_l(h_l), so they contain the future net) at every layer against the output-space bottleneck.
Consequence if true: any layer dependence of a learned b_l(eps) measures what the encoder cannot compute, not
information. Kelvin's "it doesn't need to be small" taken literally makes b_l flat.

A2. Reachability: the decoder must output a state whose future reproduces the output. Reconstructions reachable from
layer l form A_l = g_l(R^n); A_0 = supp(a) is a union of polyhedral pieces of dimension about min_k #active units
(~110 of 256 at ARC), A_{L-1} = R_+^n. Question: does restricting reconstructions to A_l cost bits?
Check: 'ahead' b_0 against output-space b_out on the same net (difference = the reachability cost plus training
error).

A3. The learned count is an upper bound on the true b_l(eps) (training is imperfect). Question: how far above?
Check: (i) a bigger encoder/decoder and longer training on a subset of cells; (ii) nested (one model for all rates)
against dedicated single-rate models at a few rates; (iii) for channel codes in output space, the linear analog scheme
attains C = R_G(D) exactly (Gaussian reverse water-filling over eig Cov(a); FORMAL.md 1.4), so a learned output-space
channel code must reach at least that; if it does not, the training is the problem.

A4. What C counts. With unit-power channel inputs and independent Gaussian noise, I(h_l; y) <= C = (1/2) sum_i
log2(1 + SNR_i) (channel capacity), and by data processing the distortion at capacity C is at least the information
distortion-rate function D(C). A binary code of b bits carries at most b bits. Both are upper bounds on the information
needed; C is the tighter one at high rate (no space-filling loss), b the one that counts discrete states (what a
deductive estimator must track).
Check: stated with proof references in FORMAL.md 1.3; the comparison of C(eps) and b(eps) on the same cells.

A5. Which theory spectrum. The brief's "reverse water-filling over the output-relevant spectrum at layer l" has three
candidates: (a) the output covariance Cov(a) (the layer-free prediction for unrestricted encoders, achievable in
output space by the linear analog scheme); (b) the degree-1 relevance spectrum R_1 = Sigma^{1/2} B^T B Sigma^{1/2}
(the relevance lane's; it prices only the linear part, s_1 V, so it cannot go below the nonlinear share 1 - s_1:
1 - s_1 = 0.7 at ARC l = 0); (c) the active-subspace spectrum C_l = E[Sigma^{1/2} grad g^T grad g Sigma^{1/2}] (the
high-resolution price for an encoder that describes h_l with small errors, i.e. a local encoder; its trace is D V,
D the mean Hermite degree, so it overprices large errors).
Check: all three computed per layer with split-sample (debiased) estimators; compared with learned 'ahead' and 'local'
curves. Expected: (a) predicts 'ahead' at every layer; (c) bounds 'local' at small eps; (b) matches only where s_1 ~ 1.

A6. Relative loss. nMSE = E|a_hat - a|^2 / tr Var(a) over the output vector, the earlier lanes' convention; the error
of the output mean reported as |mean(a_hat - a)|^2 / tr Var(a) on the same held-out inputs with its noise floor.
Check: evaluation code (lib/bitlib.evaluate) on 16384 held-out inputs with a fixed seed per net.

A7. Narrow-deep: the state is a ray from layer 16-32 (relevance lane, MEASURED), so the output is (nearly) a scalar
times a fixed vector and the output's bit count is that of one scalar: about (1/2) log2(1/eps) plus a coding loss.
Question: is it flat across layers for local encoders too (an 8-dimensional input is easy for an MLP to compute the
future of)?
Check: local and ahead runs at all seven layers on the six nets.

## B. The scrambling test (part B)

B1. Degenerate chain. With unrestricted encoders the optimal codes can be the same at every layer (c_l = the output's
code), so T_l = identity and nothing is scrambled; all the work sits in E_0, which must compute the net. So the
scrambling question is not a question about information; it is about computation: how complex must the maps be when
each encoder only sees its own layer and cannot compute the future.
Check: proof in FORMAL.md 2.1; the chain experiment therefore uses local encoders (they see h_l only, bounded MLPs) and
reports the dependence on the encoder size; 'ahead' chains are run once to show T = identity is what training finds.

B2. Basis freedom. Codes trained separately are arbitrary up to relabelling; a relabelling of {0,1}^b can make any map
look scrambled. Joint training with a restricted T (s-sparse, bounded width/depth) searches over bases: if some basis
makes T simple, the restricted chain reaches the same fidelity. Basis-invariant statistics used besides: conditional
entropy of c_{l+1} given c_l (is there a map at all), and noise sensitivity measured on actual inputs (rho-correlated
x, x'), which does not depend on the labelling of the code words.
Check: chain fidelity against s; Walsh spectra measured on the uniform measure (noise stability Stab_rho at several
rho, inverted to the degree profile) and on the code distribution itself.

B3. Baselines at the same code size: a random XOR/permutation network (scrambled), a random dense ReLU net on the codes
(scrambled-ish), a sparse or linear threshold map (unscrambled). Their Walsh profiles and restricted-T fidelities
define the scale on which the learned transitions are placed.

B4. Rate for the chain: where part A gives eps ~ 0.01. Question: is there such a rate below 256 bits for local
encoders at early ARC layers? If not, the chain is run on the layers where it exists, and the early layers are
reported as "no local code below 256 bits reaches eps = 0.01".

## C. Estimation (part C)

C1. A deductive estimator propagating factorized code laws is possible only if (i) the input code's law is known
(local E_0 of a Gaussian), (ii) transitions are sparse, (iii) the code law stays near-factorized, (iv) the readout is
low degree in the code. Each is measured on the chain; cost and error estimated against MC, RQMC and the multilevel
sampler numbers of the earlier lanes (same nets).
