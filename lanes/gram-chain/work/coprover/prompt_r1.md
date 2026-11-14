You are a co-prover and red team (gpt-6-astra) for a research lane on the replica Gram chain of random critical ReLU
networks with additive noise. Work independently: derive, compute, and say plainly what is PROVEN, what is HEURISTIC,
what is a CONJECTURE, and what fails. Do NOT read the directory /home/agent/workspaces/mats/work/gram-chain/ (it holds
my own independent attempt; this round must stay independent). Do not edit any file.

Background you may read: /home/agent/workspaces/mats/outbox/gram-chain-explainer-2026-11-01.md (what is known, already
checked by you in another session), /home/agent/workspaces/mats/outbox/stationary-numerics-2026-10-31.md,
/home/agent/workspaces/mats/outbox/stationary-regime-2026-10-31.md, /home/agent/workspaces/mats/outbox/input-bits-2026-10-31.md,
/home/agent/workspaces/mats/outbox/kstar-frames-2026-10-30.md, /home/agent/workspaces/mats/work/stationary-numerics/notes/proofs.md,
/home/agent/workspaces/mats/work/stationary-numerics/lib/gram_chain.py, and the sibling lane's definitions
/home/agent/workspaces/mats/work/relevance/DEFINITIONS.md. You may run small numerical computations (python3 or
/home/agent/.venvs/arc-noisy/bin/python, numpy/scipy; single thread; a few minutes each at most).

## Setting
Model S: h_l = relu(W_l h_{l-1}) + sigma xi_l, W_l iid N(0, 2/n) entries, xi_l iid N(0, I_n), no biases; output
a = relu(W_L h_{L-1}) (no output noise). Stationary regime: sigma = 1 (pure scale), infinite past. Input regime: sigma = 0,
h_0 = x ~ N(0, I_n); ARC's point n = 256, L = 32, and narrow-deep n = 8, L = 256. R replicas share all weights; their
noise is shared according to a pattern (or correlated with correlation c). G_ab = h^(a).h^(b)/n is an exact Markov chain
(explainer section 2). Q = G_aa, delta = 1 - cos(angle), ell = log|h1| - log|h2|. Layer l = L - t (t layers to go,
counting the output layer).

## Questions (number your answers Q1..Q8; give formulas, then numbers at n = 64, 256, 1024 where asked)
Q1. Large-n limit of the two-replica stationary law (independent noise). (a) Derive the scaling of delta and ell with n
    and the leading-order joint law of (Q/n, n^{2/3} delta, n^{1/3} ell): which variables are fast and slaved, which
    form a limiting diffusion on the time scale of n layers, with which drift and diffusion coefficients. (b) The
    leading correction to E[delta | Q] beyond the mean-field fixed point delta*(Q) (explainer section 3): its order in n
    and its coefficient (or an algorithm that gives it). (c) E[ell^2 | Q/n] and E[ell^2] at large n (the exploratory
    chain gives SD(ell) ~ 1.5-1.8 n^{-1/3} at n = 16-256, rising with Q/n).
Q2. Mixing. The spectral gap (or relaxation rates) of the limiting radius diffusion and of the joint radius / radius-ratio
    diffusion, in units of layers; the relaxation of the angle. What does "mixing time of the normalised Gram" mean when
    the radius has a 1/x tail, and which observable mixes slowest?
Q3. Relevance at layer l, stationary regime, direction observable u = a/|a| (scale free). (a) The closed relevance
    V_P(t) = Var(E[u | all noise up to layer l]) / Var(u) (replicas identical at layer l, independent noise after) and
    (b) the total relevance T_P(t) = E|u - u'|^2 / (2 Var u) with u, u' having independent noise up to l and shared noise
    after: mean-field curves, their time scales in n, and their large-t behaviour. (c) The block total effect of the
    noise of layers [l - b, l). Which of these should define "the bits that matter at layer l" for estimating E[a] of a
    fixed net, and why?
Q4. Dimension. Define a participation ratio of the part of the output that depends on the layer-l state (closed and
    total versions), as a weight average computable by a finite number of replicas (say how many and with which sharing
    pattern). Predict it: e.g. in a linear approximation with the cloud covariance C and the future sensitivity in free
    position (rotation invariance of the future given the past), 1/PR = 1/PR_C + 1/PR_M - 1/n; is that right, and what
    are PR_C (the stationary cloud's spectrum: is a 1/k shape derivable? its moments tr C^m are 2m-replica quantities)
    and PR_M as functions of n and t? Where does the linear approximation fail (finite-angle gate switching)?
Q5. Input regime (sigma = 0). (a) The participation ratio of the input cloud Cov_x(h_l) at layer l: at infinite width the
    kernel makes iid inputs equicorrelated (isotropic cloud), so the anisotropy is a 1/n (four-point vertex) effect.
    Derive the large-n PR(l) from the vertex recursion and compare with the measured finite angular PR 159, 57, 17, 9.6,
    6.1, 3.6, 1.9 at l = 1, 4, 16, 32, 64, 128, 256 for n = 256 (input-bits lane). (b) How much of Var_x(a) (or of the
    output direction's variance) is carried by the radius |h_l| versus the direction h_l/|h_l| at layer l, as a function
    of l and L (an exact replica construction exists by rescaling one replica's radius); values at 256 x 32 and 8 x 256.
    (c) With small sigma > 0, how does the future noise erode the layer-l relevance?
Q6. Annealed versus quenched. Which fixed-weight quantities self-average as n grows (the across-net CV -> 0) and which
    do not? Hypothesis: they depend on the net mainly through its radius history (O(1) across nets, n^{-1/3} within a
    net). Predict the across-net CV of the fixed-weight variance of the direction u at a stationary layer, and of V_P(t).
    Where would annealed counts mislead (rare nets dominating; per-net relevance concentrated in a few net-specific
    directions)?
Q7. Perturbation survival. A replica perturbed at layer l by a vector of relative size eps orthogonal to the state (Gram
    surgery), all noise shared afterwards: E|u - u'|^2 as a function of t and eps (finite-angle versus tangent regimes,
    crossover eps), and what the annealed tangent identity E_W |J v|^2 = |v|^2 implies and does not imply.
Q8. Red team: what in this programme is ill-posed, circular, or likely to fail, and what single computation would most
    efficiently refute the main predictions?

Keep the answer under 4,000 words. Label every claim.
