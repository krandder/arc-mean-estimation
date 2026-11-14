You are gpt-6-astra, co-prover for the relevance-accounting lane (read-only sandbox). Round 3: an
independent derivation. Work from first principles and from the files listed below only.

Setting. Model S at sigma = 0: h_l = relu(W_l h_{l-1}), W_l iid N(0, 2/n), n = 256, L = 32, input x ~ N(0, I_n), output
a = h_L in R^256. Nets: lib/rel.py, `rel.input_weights(seed, 256, 32)` gives [W_1..W_32] for seeds 4000-4005 (it imports
work/stationary/lib/st.py), and `rel.input_cloud(Ws, l, P, rng)` gives samples of h_l. At layer l the future is
layers l+1..L and g_l = a as a function of h_l. Under the Gaussian convention X ~ N(m_l, Sigma_l) (the layer's fitted
mean and covariance) define V = tr Var a(X), J(1) = E|J(X) Sigma^{1/2}|_F^2 (J the future's Jacobian), the Hermite
(Wiener chaos) split V = sum_d V_d, V_1 = |E[J(X)] Sigma^{1/2}|_F^2, the mean degree D = J(1)/V and the linear share
s_1 = V_1/V. The lane's theory v2 (coprover/r3_inputs/FORMAL_through_v3.2.md, sections v2.1-v2.3 and errata E13-E14)
predicts D by the annealed identity D_v2 = (tr Sigma/E|X|^2)/(V/E|a|^2)_v2 and s_1 from three channels (direction,
amplitude, radial).

Observation (coprover/r3_inputs/per_net_data.md: raw measurements and the v2 predictions per net and layer). The
variance budget V/E|a|^2 is predicted within 20% on nearly every cell, but the measured D at l = 0, 4, 8 is 1.6-2.2
times D_v2 on four of the six nets (about 1.0 on the other two), and on those nets s_1 at l <= 8 is 0.06-0.15 below
s1_v2. At l = 0, s1_v2 = 0.29 while five of six nets measure 0.20-0.235.

Questions (label every claim PROVEN, PROVEN UNDER <hypothesis>, HEURISTIC, NUMERICAL):
1. For a fixed net, write D exactly in terms of quantities that make the gap to the annealed identity explicit, and
   name the per-net factor responsible.
2. Give a predictor of that factor computable from forward quantities of the fixed net only (no Jacobians, no
   gradient samples, no knowledge of D), derive it, state the approximations, and compute it on nets 4000-4005 at
   l = 0, 4, 8, 16, 24, 28, 31 against the factor implied by the measured data.
3. Its law over random nets at width n with t future layers (mean and variance of its logarithm), and the ARC values.
4. What it implies for s_1 and its channels; whether it explains the l = 0 overprediction of s_1 (about 0.07 on five
   nets); give a corrected s_1 if you can, and compute it on the six nets.
5. Why the variance budget is (or is not) insensitive to this factor while D is not.

Rules. Read only: coprover/r3_inputs/, coprover/prompt_r3.md, lib/rel.py, lib/accounting.py, lib/theory_v1.py,
lib/theory_v2.py, work/stationary/lib/. Do NOT read FORMAL.md, PREREG.md, prereg_hashes.txt, lib/theory_v33.py, any
scratch/ file, results/, logs/, frozen/, review/, relevance-accounting.md or other coprover/ files (this keeps the
derivation independent of the lane's own answer). Do not modify files. Small computations are fine: one thread
(OPENBLAS_NUM_THREADS=1), nice -n 19, minutes, Python /home/agent/.venvs/arc-noisy/bin/python. End with a short list of
the results and their labels.
