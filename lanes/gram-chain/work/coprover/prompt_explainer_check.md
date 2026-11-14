You are gpt-6-astra, acting as a mathematical checker for a short explainer on the "replica Gram chain" of random
critical ReLU networks with additive noise. Be strict and concrete: for every equation and every numerical claim, say
CORRECT, WRONG (with the correct statement), or UNSUPPORTED (with what would be needed). Do not rewrite the prose
style; check the mathematics and the logic.

File to check: /home/agent/workspaces/mats/outbox/gram-chain-explainer-2026-11-01.md

Background you may read (read-only):
- /home/agent/workspaces/mats/work/stationary-numerics/notes/proofs.md (P-G1, P-G2, P-R1)
- /home/agent/workspaces/mats/work/stationary-numerics/lib/gram_chain.py (the chain as implemented)
- /home/agent/workspaces/mats/outbox/stationary-numerics-2026-10-31.md (sections 2.2-2.8)
- /home/agent/workspaces/mats/outbox/input-bits-2026-10-31.md (section 6.4, the measured C(t))
- /home/agent/workspaces/mats/work/input-bits/coprover/astra_r1_answer.md (the (1-t)^{2/3} closure, your earlier round)
- /home/agent/workspaces/mats/work/gram-chain/scratch/quick_r2.py, quick_r3.py, quick_l0.py, check_expansion.py (the
  scripts behind the new numbers; you may rerun small parts, single-threaded, a few minutes at most, with
  /home/agent/.venvs/arc-noisy/bin/python if your sandbox allows)

Model S: h_l = relu(W_l h_{l-1}) + xi_l, W_l iid N(0, 2/n) entries, xi_l iid N(0, I_n); sigma = 1 without loss.

Check in particular:
1. Section 2: the exactness argument and the conditional mean E[G'_ab | G] = sqrt(G_aa G_bb) kappa(rho_ab) + S_ab.
2. Section 3: the claims about one input (stationary law exists, infinite mean, no fixed point of the kernel/vertex
   recursion); the expansion 1 - kappa(1 - delta) = delta - c_k delta^{3/2} - delta^{5/2}/(15 sqrt2 pi) + ...; the fixed
   point expansion delta* = eps [1 - (2/(3(1 - c)) + 1/30) eps + O(eps^2)], eps = ((1 - c)/(c_k Q))^{2/3}; 3.2 n^{-2/3}
   at the median radius; the c = -1 statement.
3. Section 4: the time scales (angle relaxes in about 1.5 Q^{1/3} layers in mean field; radius ratio restored at rate
   about 1/Q per layer and of size n^{-1/3}); the 3-replica statement (relative SD sqrt(2/PR), correlation 1/4,
   1.46 sqrt(2/PR) for the mean range of three); the single-injection decay and 2.99 Q^{1/6}.
4. Section 5: each "computes exactly" item (are these really finite-replica quantities, with the stated sharing
   patterns?); the closed-index construction; C(t) = 1 - (1 - t)^{2/3} and the claimed first-order share 2/3 and the
   k^{-5/3} tail cut off near sqrt(Q) for layer blocks; the tangent-replica chain and E_W |J u|^2 = |u|^2 exactly; the
   Gram-de Finetti (Dovbysh-Sudakov) statement.
5. Section 6: is the list of what the chain cannot compute correct and complete? In particular the claim that every
   annealed quantity is the same for every direction orthogonal to the replicas' span.
6. Anything wrong by omission that a careful reader would be misled by.

Output: a numbered list of findings (severity: error / imprecision / fine), then a one-line verdict. Keep it under 1,500
words. Do not edit any file.
