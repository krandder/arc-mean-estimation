# CHECK-1: is ARC's final step an expectation under a w-independent model? (05:25Z)

Needed by FORMAL A5 (last-layer bottleneck): est_i = int relu(w_i . h) dQ_{L-1}(h) with Q_{L-1} not depending on the
last layer's row w_i.

K = 2, kind 'simple' (ARC's Alg. 2): NUMERICAL, exact. tests/test_au.py: on a 16 x 4 net the final means equal
E relu(N(w_i . m_3, w_i^T S_3 w_i)) computed from ARC's own layer-3 state (m_3, S_3) to 2.2e-16. So Q_{L-1} is the
Gaussian N(m_{L-1}, S_{L-1}) and A5 holds exactly for ARC's K = 2 simple estimator.

K >= 3 and augmented kinds: by code reading (src/mlp_kprop/kprop_harmonic.py, nonlin_kprop; read 05:15Z), the mean of
neuron i after the last nonlinear step is a Wick (Hermite) expansion around N(mu_i, var_i), mu_i and var_i the model's
mean and variance of z_i, whose terms are products of DIAGONAL cumulant entries kappa_x(z_i, ..., z_i) selected by a
rule that depends only on the block orders x (vec_block_cost; budget k_max - 1 + augment). Diagonal entries are the
probes <w_i^{tensor x}, kappa_x(h_{L-1})> of the layer-(L-1) model tensors. A fixed order-only truncation of the
Edgeworth/Gram-Charlier series commutes with linear projection, so the per-neuron formula equals
int relu(w_i . h) dQ(h) for the n-dimensional truncated Gram-Charlier signed measure Q built from the model tensors.
Caveat: with avg_metric = True (ARC's default, used in arc-noisy and here) the trace (identity) parts of the tensors are
pushed through the AVERAGE metric E[W W^T] = 2 I rather than W W^T, so the probes of trace components use |w_i|^2 = 2
instead of the actual |w_i|^2 (relative difference O(n^{-1/2})); with avg_metric = False the identity is exact.
Status: structural (code reading), not numerically verified for K >= 3; A5 is stated for K >= 3 with this caveat.
