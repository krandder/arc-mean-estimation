You are reviewing a research lane (read-only). Directory: the current working directory (work/backward-bits).
Context: Kelvin proposed a backward recursion for small noisy ReLU nets (Model S: h_l = relu(W_l h_{l-1}) + sigma xi_l,
noiseless output): train the output layer's code to convergence; compute near-exactly how many bits of layer l-1 the
noise erases; train the code at l-1 until it carries "the bits of layer l minus the erased bits"; recurse toward the
input. The lane formalised this (FORMAL.md), registered a design (PREREG.md, amendments in notes/DEVIATIONS.md) and
implemented it (lib/bb.py, scripts/run_chain.py, scripts/run_truth.py, scripts/run_gauss.py, scripts/run_fwd.py,
scripts/conv_check.py, scripts/score.py, scripts/exact_1d.py, scripts/exact_chain_1d.py; tests in tests/test_bb.py with
output tests/test_output.txt). Scored runs are in progress; do not judge results, judge the reasoning and the code.

Please check, and report findings as a numbered list, each with severity (error / major / minor), the file and line or
section, what is wrong, and the fix:
1. FORMAL.md: are Propositions 1, 2, 3 and 6 and the section 5 claims correct as stated? Check hypotheses (full-support
   noise, positive-probability cells, analyticity on linear regions, densities), the stochastic-code version of Prop 2,
   the chain-rule identities, and the cited one-shot channel-simulation bound (Li and El Gamal 2018: is the constant
   log2(I+1)+5 for one-shot simulation with unlimited common randomness right?). Is the Pinsker-spectral lower bound in
   section 4 valid (Pinsker constant in bits; the k-means spectral relaxation with K cells)?
2. Estimators (lib/bb.py, run_chain.py, run_truth.py): Miller-Madow and Grassberger per-point entropies; the pooled
   cell-posterior relevance with the split-half Richardson correction; the Richardson correction for the output-target
   chains (P, PR), whose per-point rows are mixtures (counts / M) @ Q; held-out discipline (train / select / test sets
   and independent noise draws); any leakage of test data into selection.
3. The chain logic in run_chain.py: target rows for P/PR (counts over the next code times the next code's cell table),
   the cell table Qcell, the reuse candidate (noise-free composition) and the recursive loader bb.load_code, the
   selection rules (rate rule H_sel <= T_sel + 0.02; relevance rule I_sel >= 0.95 T_sel), the certificate fits, the
   look-ahead control, the lower bound (only for next-code targets).
4. run_truth.py: the chain's own prediction of the output code (product of kernels for K/R, table for P/PR), the
   direct codes and their selection, the shared-noise output distortion (common random numbers, V), the optimised
   decoder.
5. run_gauss.py: are the Kolchinsky-Tracey bounds and the Monte Carlo mixture information (with and without
   leave-one-out) correct estimators of I(h; z) for z = u(h) + N(0, I)? Is the mixture-posterior relevance plug-in
   correct? What biases remain?
6. score.py: do the certificate flags and the predictions B1-B14 implement PREREG.md section 4-5 as written?
7. exact_1d.py and exact_chain_1d.py: are the dynamic programs (optimal interval partitions; the entropy-penalised
   version with the rate term -n log2 n additive over cells) and the exact posteriors right?
8. Anything in the design that could make the lane's eventual answer ("does the backward recursion give certified bit
   counts all the way to the input; where does it break") wrong or misleading.
Be concrete and terse. Begin your answer with the line "REVIEW r1".
