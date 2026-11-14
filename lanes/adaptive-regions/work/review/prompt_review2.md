You are an independent, rigorous reviewer (read-only). Review sections D, E, A, B, C and Summary point 0 of
/home/agent/workspaces/mats/work/adaptive-regions/adaptive-regions.md, against the code and outputs they cite:
scratch/pattern_chain.py, scratch/gauss_chain.py, scratch/depth_saturation.py, scratch/cone_tree.py, scratch/exact_cells.py,
scratch/cells_scaling.py, scratch/exact_hybrid.py, scratch/step4m.py, scratch/step5m.py, lib/cones.py, tests/test_cones.py,
results/pattern_chain.md, results/cone_tree.md, runs/*.json, logs/*.log.
Check: (1) is each claim supported by the cited numbers (spot-check tables against runs/ and logs/)? (2) are the
mathematical statements correct (facet formula for E[x 1_C], Plackett orthant identity with arcsine substitution,
the claim that the chain is exact iff E[h_l 1{s_l=s,s_l+1=t}] = T(t|s) m_l(s), the 2^n first-layer claim)? (3) code
bugs that would change a conclusion (chain recursion, order-k chains, entropy estimates, transition rank, freeze test,
Gaussian-closure split, cone moments, truth/RQMC baselines)? (4) overclaims or labels (MEASURED/PROVEN/CONJECTURE)
that need narrowing. Give numbered findings, each with severity (blocker/major/minor), evidence (file:line or
numbers) and a concrete fix. End with a one-paragraph verdict. Do not write files.
