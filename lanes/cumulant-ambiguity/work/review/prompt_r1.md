You are a rigorous co-prover. Check the statements below. For each, say PROVEN (give or fix the proof), FALSE (give a counterexample), or UNCLEAR (say what is missing). Be terse, precise, and do not pad. Files for context (read-only): lw.py, gamma1d.py, oned_bound.py in this directory.

Setting. Bias-free ReLU MLP with width n: h_0 = x in R^n, h_l = relu(W_l h_{l-1}) for l = 1..L-1, output pre-activations t = W_L h_{L-1} in R^n, scalar output f = sum_i a_i relu(t_i). (In ARC's convention, arXiv:2605.05179, the network output is a linear readout of the last activation layer, so its mean is E[h_L] read out linearly.) P0 = N(0, I_n) (or an N-point sample of it). For an order d >= 1, the ambiguity set is
  A_d(S) = { probability laws Q on R^n : E_Q p(h_l(x)) = E_P0 p(h_l(x)) for every polynomial p of degree <= d in the coordinates of h_l, for every l in S },
with S = {0..L-1} ("all"), {L-1} ("last") or {0} ("input"). gap_d(S) = sup_{Q in A_d(S)} E_Q f - inf_{Q in A_d(S)} E_Q f.

Claim 0. If S also contained the layer L (h_L = relu(t)), gap = 0 for d >= 1. Hence "cumulants agree at every layer up to the output" can only mean up to h_{L-1}.

Claim 1 (last-layer reduction). gap_d(all) <= gap_d(last) <= sum_i |a_i| Gamma_d(mu_i), where mu_i is the law of t_i under P0 and Gamma_d(mu) = sup - inf of E_nu relu over laws nu on the range of t_i with the same first d moments as mu. In particular the bound depends on depth only through the laws mu_i.

Claim 2. For each fixed net, Gamma_d(mu_i) -> 0 as d -> infinity (mu_i has Gaussian-type tails, hence is moment-determinate; relu has linear growth; fixing the second moment gives uniform integrability). Rate unspecified.

Claim 3 (Markov / propagation class). Any estimator of the form S_{l+1} = Phi_{l+1}(S_l, W_{l+1}), S_0 = order-<=d moments of x, output = function of S_L, has worst-case error >= gap_d(input)/2 over A_d(input). So for propagation-type methods (ARC's kprop being one), the relevant ambiguity is the input-only one, and the "all layers known exactly" oracle class is strictly more informative.

Claim 4 (interpretation). The worst-case 2x counterexample (127-wise independent sign-parity law at width 256, f = relu(prod sign(x_i) min |x_i|)) matches only the INPUT law's low-order statistics; by Claim 1 it cannot survive matching of the internal layers' order-d moments beyond Gamma_d of the last pre-activation law. So a parity-type construction can defeat input-only (equivalently, propagation-type) methods but not the layer-wise oracle.

Questions. (a) Check Claims 0-4. (b) Is there any matching LOWER bound gap_d(all) >= c * Gamma_d(mu) for a single last-layer unit (a = e_i), e.g. when L = 1 (t Gaussian) or generally? Our measurements at n=4 show gap(all) close to gap(last), and for L=1 the LP reaches the 1D Gaussian Gamma_d (about 1.4/d in sd(relu t) units), but for L=2 at d=3 the LP gives 0.30 against the 1D bound 0.77. (c) For the 1D Gaussian case, give the cleanest provable rate for Gamma_d (Markov-Krein / Gauss-Radau quadrature: is it Theta(1/d)?). (d) Can Gamma_d(mu_L) grow with depth for random He-ReLU nets at fixed width (the law of t gets heavier tails as L/n grows: log-normal-like norm)? State what is provable.
Label every answer PROVEN / FALSE / CONJECTURE / HEURISTIC.
