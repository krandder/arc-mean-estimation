# Bit accounting: definitions and the facts that hold for every encoder (v1, 1 November 2026, 22:45Z)

Lane: bit accounting and the scrambling test (bead pool-qxszj1.25). Labels: PROVEN, NUMERICAL, MEASURED, HEURISTIC,
CONJECTURE. Provenance: [C] Claude; [BB] the bits-bounds lane (work/bits-bounds/FORMAL.md); [R] the relevance lane
(work/relevance/DEFINITIONS.md, FORMAL.md).

## 0. Setting

Noiseless He-ReLU nets (sigma = 0): h_0 = x ~ N(0, I_n), h_k = relu(W_k h_{k-1}), output a = h_L in R^n, W_k iid
N(0, 2/n), no biases. Nets: ARC 256 x 32 (st.W_layer, seeds 4000-4003), narrow-deep 8 x 256 (nd.make_weights 'plain',
seeds 203, 216, 217, 220, 221, 223). Layer l, future g_l = layers l+1..L, a = g_l(h_l), V = tr Var(a) (the same at
every layer). Relative loss of a reconstruction a_hat: nMSE = E|a_hat - a|^2 / V.

## 1. The per-layer bottleneck

### 1.1 Definitions
- A b-bit layer-l scheme is a pair (e, d): an encoder e: R^n -> {0,1}^b (any measurable map of h_l) and a decoder
  d: {0,1}^b -> R^n (a state at layer l). Its loss is D_l(e, d) = E|g_l(d(e(h_l))) - a|^2. D_l*(b) = inf over schemes;
  b_l(eps) = min{b : D_l*(b) <= eps V}.
- A capacity-C channel scheme: encoder u = e(h_l) in R^K with E u_i^2 <= 1, channel y_i = u_i + nu_i, nu_i ~
  N(0, 1/SNR_i) independent, C = (1/2) sum_i log2(1 + SNR_i), decoder d(y) a state at layer l. C_l(eps) = least C
  reaching eps V.
- Output-space versions (layer L): the same with h_l replaced by a and g_l by the identity, reconstructions
  restricted to a set A: D_out^A(b). A = R^n (free) or A = supp(a).
- Encoder classes. Unrestricted: any measurable e (in particular e may contain the future net). Local depth-k class
  L_k(w): e is an MLP with k hidden layers of width w applied to h_l alone (no access to a, to later states or to
  the future weights except through training), decoder an MLP of the same size followed by the fixed future g_l;
  both are trained on the output loss, so they depend on the future through training only. The experiments use
  k = 2, w = 512 for the sweeps and k in {1, 2, 4}, w in {256, 512, 1024} on a subset. Look-ahead class: an MLP that
  sees (h_l, a) (it contains the future net), the unrestricted optimum's learned stand-in.

### 1.2 Every layer needs the output's bits (PROVEN [C]; the information version is [BB] Prop 3.6)
Let A_l = g_l(R^n), the outputs reachable from layer l. Then for every b and every l,
  D_out^{R^n}(b) <= D_l*(b) <= D_out^{A_l}(b),   supp(a) = A_0 subset A_1 subset ... subset A_{L-1} = R_+^n,
so D_l*(b) is non-increasing in l and b_out^{free}(eps) <= b_{L-1}(eps) <= ... <= b_0(eps) <= b_out^{supp}(eps).
Proof. Lower bound: from (e, d) at layer l build an output-space scheme with the same joint law of (a, a_hat): given a,
draw h_l from its conditional law and send e(h_l); reconstruct g_l(d(.)). For a fixed codebook the nearest-codeword
deterministic encoder is at least as good as any randomised one, so D_out^{R^n}(b) <= D_l(e, d). Upper bound: from an
output-space scheme (e', d') with codewords in A_l pick for each codeword c a state h_c with g_l(h_c) = d'(c); then
e = e' o g_l, d(c) = h_c reproduce it exactly. The inclusions: A_l = g_{l+1}(relu(W_{l+1} R^n)) subset g_{l+1}(R^n) =
A_{l+1}; A_{L-1} = relu(W_L R^n) = R_+^n because W_L is invertible; A_0 = F(R^n) = supp(a) since x has full support.
The same holds for channel schemes (the randomised construction keeps the channel; the composition keeps C).
Consequence. With unrestricted encoders the bit count is a property of the output distribution only: it is the same at
every layer up to the reachability term (between free and supp-restricted output reconstructions). Bounds on the
reachability term: D_out^{supp}(b) <= 4 D_out^{R^n}(b) (reconstruct with the cell's sample nearest its centroid).
Any layer dependence in a learned b_l(eps) therefore measures what the encoder (or the decoder's search for a
reachable state) cannot compute, not information.

### 1.3 What the two rates count (PROVEN, standard)
- A b-bit code carries at most b bits: I(h_l; code) <= H(code) <= b.
- Channel: for any encoder with E u_i^2 <= 1, I(h_l; y) <= sum_i I(u_i; y_i) <= C (independent noise, Gaussian
  maximises the per-channel mutual information under the power constraint). So the loss at capacity C is at least
  the information distortion-rate function at rate C.
- Both learned counts are upper bounds on the information needed: b_l(eps) >= R_l(eps V) and C_l(eps) >= R_l(eps V),
  R_l the information rate-distortion function of h_l under the distortion |g_l(h) - g_l(h_hat)|^2, which by 1.2
  lies between the output's free and supp-restricted information rate-distortion functions.

### 1.4 The Gaussian reverse water-filling predictions (PROVEN where stated)
R_G(D; lam) = sum_k max(0, (1/2) log2(lam_k / theta)), sum_k min(lam_k, theta) = D.
- Output covariance, lam = eig Cov(a). (i) R_out(D) <= R_G(D; eig Cov a) for the free output-space problem
  (Gaussian sources are the hardest for squared error at a given covariance). (ii) Achievability for channels: the
  linear analog scheme (send the whitened principal components with SNR_k = lam_k/theta - 1, decode by linear MMSE)
  has loss exactly sum_k min(lam_k, theta) for any source with that covariance, so the free output-space channel
  count satisfies C_out(eps) <= R_G(eps V; eig Cov a) exactly. This is the layer-free prediction for unrestricted
  (look-ahead) encoders.
- Degree-1 relevance spectrum at layer l (the brief's "output-relevant spectrum"; [R] uses the Gaussian convention, here
  the true law): lam = eig K_1, K_1 = Cov(a, h_l) Sigma_l^+ Cov(h_l, a), the covariance of the best linear predictor of
  a from h_l; V_1 = tr K_1 = s_1 V. Any code that describes only linear features leaves at least V - V_1; reported
  as R_G(eps V_1; K_1) (the linear part to relative precision eps) and R_G(eps V - (V - V_1); K_1) (a linear code's
  total, defined only when eps V > V - V_1).
- Active-subspace spectrum at layer l: lam = eig E[Sigma^{1/2} J^T J Sigma^{1/2}], J the Jacobian of g_l at cloud
  points: the high-resolution price of a local scheme whose reconstruction error e is small (first order:
  E|J e|^2). Its trace is D_l V (D_l the mean Hermite degree [R]), so it overprices errors larger than the future's
  linearity scale; HEURISTIC as a prediction for local encoders, exact only as eps -> 0 for smooth pieces.

## 2. The chain

### 2.1 The degenerate chain (PROVEN [C])
For unrestricted encoders, an optimal family of per-layer codes can be chosen equal at every layer: c_l = e'(a) for the
output's optimal code e', decoded at layer l by the preimage construction of 1.2. Then c_{l+1} = c_l, the transitions
are the identity, and the chain run from c_0 = e'(F(x)) reproduces the output with the optimal loss at every layer.
So the information-theoretically correct codes never get scrambled, because nothing moves: the whole difficulty sits in
the first encoder, which must compute the net. Scrambling is therefore a property of computation: it only has content
for encoders that cannot compute the future, which is why part B uses the local class L_k(w).

### 2.2 What part B measures
Codes c_l = sign(E_l(h_l)) with E_l in L_k(w) at a common rate b; transitions T_l: {+-1}^b -> {+-1}^b (or every k
layers); trained jointly on (i) each layer's bottleneck loss, (ii) consistency T_l(c_l) = c_{l+1} (cross-entropy per
bit), (iii) the chain loss: decode the code obtained by running T from c_0 and push it through the future. Complexity
of T_l: Walsh-Fourier degree profile of each output bit (via noise stability Stab_rho = sum_k rho^k W^k), total
influence, number of relevant input bits; fidelity of restricted T (each output bit reads at most s input bits; bounded
width/depth). Baselines at the same b: random XOR/permutation networks and random dense ReLU nets on the codes
(scrambled), sparse and linear threshold maps (unscrambled). Basis freedom: joint training with restricted T, plus
statistics that do not depend on the code's labelling (conditional entropy, noise sensitivity on rho-correlated
inputs).

## 3. Additions v1.1 (1 November 2026, 23:30Z, with the small-net plan; nothing above edited)

### 3.1 The restricted class used for the small nets (S1, S2)
Local class L^1(n): z = A2 relu(A1 x + b1) + b2 with A1 in R^{n x n} (one ReLU layer of width n, the width of the net),
x the whitened layer-l state, followed by the bottleneck. Linear class L^0: z = A x + b. Unrestricted: an MLP with three
hidden layers of width 256 that sees x and the exact output a = g_l(h_l). The decoder is unrestricted in every class
(MLP, three hidden layers of width 256, then the fixed future).
Proposition 3.1 (what one ReLU layer buys; PROVEN [C]). L^1(n) contains x -> h_{l+1} (A1 = W_{l+1} Sigma_l^{1/2},
b1 = W_{l+1} m_l), so a local encoder at layer l can send any linear code of h_{l+1}; with W_{l+1} invertible, every
nonnegative reconstruction of h_{l+1} is reachable from layer l (h_l = W_{l+1}^{-1} h_hat_{l+1}). Hence
b_l^{L1}(eps) <= b_{l+1}^{L0, nonneg}(eps): one ReLU layer of look-ahead is worth one layer of depth. It cannot
compute two future layers in general, so for L - l >= 2 the local class cannot reach the layer-free count unless the
future is close to linear on the cloud.
Why L^1(n) answers Kelvin's question: the code is a function of the layer's own state of the same complexity as one
layer of the net. "The bits at layer l" in this class are the bits a description of h_l needs when it may not run the
future; their dependence on l is then the cost of not having computed the remaining layers.

### 3.2 Basis freedom in the scrambling test (S2)
A code is defined up to a bijection of {+-1}^b; a bijection can turn any transition into a lookup table of any degree.
Three handles: (i) joint training (every encoder receives the transition and chain losses, so the codes adapt to make
the next code predictable from the previous one); (ii) statistics invariant under the hyperoctahedral group (bit
permutations and sign flips), which preserves Hamming geometry and Walsh degree: the degree-d polynomial threshold
accuracy and the s-junta accuracy of the data majority map on the reachable codes, H(c_{i+1} | c_i), coverage;
(iii) baselines on the same reachable codes. A statistic invariant under all bijections (only H(c_{i+1} | c_i) and the
code law's entropy) says whether a transition exists, not how complex it is; complexity is meaningful only relative
to the code's own geometry, which is why (i)-(iii) are reported together.

## 4. Corrections v1.2 after the gpt-6-astra round-1 review (2 November 2026, 00:20Z; review/review_r1.raw)

4.1 (finding 2) Section 1.2 holds with equality, and its hypotheses are: finite second moments, V > 0, finitely many
polyhedral pieces (a finite ReLU net), W_L invertible (true almost surely). The proof shows D_l*(b) = D_out^{A_l}(b)
exactly (the lower bound produces reconstructions g_l(d(c)) in A_l); monotonicity in l follows from A_l subset A_{l+1}.
A_0 = F(R^n) is the support of a because the image of a finite piecewise-linear map is a finite union of polyhedra
(closed). Channel version: encoders are stochastic kernels; drawing h_l given a preserves the average power, and the
composition uses a measurable right inverse of g_l on the codewords; the finite-code derandomisation step is not
needed for the channel statement.
4.2 (finding 1) Section 2.1 is too strong as written. Corrected statement (PROVEN): with unrestricted encoders there is a
chain with identity transitions (the same code at every layer, c_l = e'(a), decoded at layer l by a preimage of the
codeword) that attains the support-restricted output optimum D_out^{supp a}(b) at every layer; by 1.2 this is within
the factor-4 bound of each layer's optimum D_l*(b), and equal to it when an optimal codebook of the free problem lies
in supp(a). Counterexample to the stronger claim (reviewer's): W_1 = I, W_2 = [[1, -2], [-2, 1]] has A_0 = the two
coordinate rays while A_1 = R_+^2, so the zero-bit optimum differs between layers 0 and 1. Existence does not mean
training finds the identity chain; S2's 'unres' chains measure what training finds.
4.3 (finding 3) Section 1.4, degree-1 spectrum: the floor V - V_1 holds only for an affine predictor of a from the
code. A code of linear features followed by a nonlinear decoder and the fixed future can do better (sending all of h_l
recovers a exactly). The quantity "R_G(eps V - (V - V_1); K_1)" (rwf_lin_total in results/theory_*.json) is therefore
not a bound for the implemented linear codes; it is dropped from the report. R_G(eps V_1; K_1) is kept as what it is:
the Gaussian rate of the best linear predictor of a to relative precision eps.
4.4 (finding 4) Section 1.4, active subspace: the identity tr = D V (D the mean Hermite degree) is a Gaussian-reference
identity of the relevance lane. Here the matrix is taken under the true law of h_l, so its trace is the true-law
gradient energy E|J S^{1/2} z|^2 and the comparison with D V is approximate. Reverse water-filling over it is a local
Taylor heuristic for small reconstruction errors, not an asymptotic theorem (HEURISTIC).
4.5 (finding 5) What is measured is b_l^{E,D}(eps): the least rate at which a scheme with encoder class E (after the
stated whitening), quantiser Q and decoder class D reaches eps, as found by training (an upper bound on that class's
optimum). Classes as implemented: whitening by the empirical covariance with eigenvalues below 1e-8 of the largest
dropped (the dropped directions carry at most 1e-8 of the state's variance per direction; reconstructions lie in
m + range(S^{1/2})); E = local: one ReLU layer of width n then affine; linear: affine; unres: MLP 3 x 256 on (h_l,
a); D = MLP 3 x 256 then the fixed future. The containment of h_{l+1} in the local class (3.1) is exact only with
lossless whitening; the inverse-W construction needs the decoder to reach W^{-1} h_hat_{l+1}. "Cannot compute two
future layers" is the motivation for the class, not a theorem about its optimal distortion.
4.6 (finding 6) Shared-noise counts (S4) are rate-distortion counts for the distortion
d_l(h, h') = E_Xi |F_l(h, Xi) - F_l(h', Xi)|^2 with reconstructions restricted to states, i.e. the compression of the
random response function F_l(h, .) in L^2(P_Xi). Sending E[a | h_l] is in general not sufficient for this distortion,
but noise does not always make the problem harder (an additive noise cancels exactly; at l = L - 1 there is no future
noise). That the shared-noise score blocks the shortcut on these nets is a hypothesis tested by S4.2, not a theorem.
The 'unres' side input is an 8-draw Monte Carlo average, not E[a | h_l].
4.7 (finding 7) Capacity counts are nominal: the normalisation uses running statistics, so the evaluation power may
differ from 1. Runs started after 00:27Z (S4, the S1 linear class) record the evaluation power P_i and the corrected
bound (1/2) sum log2(1 + P_i SNR_i); the ARC runs record max and mean power (bitlib.evaluate).
4.8 (finding 14) A learned count is an upper bound on its class's optimum; a layer code that beats a learned
output-space code is not a contradiction of 1.2 (A1.2 was mis-specified as a bug check). Interpolated crossings are
not achieved rates; the report gives the achieved grid rate with the interpolation. The Gaussian analog scheme attains
the Gaussian curve for any source with that covariance; it does not make that curve optimal for non-Gaussian sources.
