# gram-chain lane: assumptions, open questions, and how each is checked (1 Nov 2026, 21:00Z)

Model S: h_l = relu(W_l h_{l-1}) + sigma xi_l, W_l iid N(0, 2/n), xi_l iid N(0, I); sigma = 1 in the stationary regime
(pure scale). Input regime: sigma = 0 (or small), several inputs x ~ N(0, I) at layer 0, depth L; ARC 256 x 32 and
narrow-deep 8 x 256.

## A. Premises in the brief, checked
A1. "One input has no stationary law." Wrong as stated for Model S: the radius has a stationary law (Kesten perpetuity,
    numerics lane P-R1), with infinite mean (P-G2). What fails is the moment (kernel/vertex) recursion. At sigma = 0 there
    is no stationary law (Q -> 0 a.s.). Check: P-G2, P-R1 (proven). Fixed in the explainer (section 3).
A2. "Annealed quantities are exact; per-net ratios are not replica quantities." Correct; but joint moments of numerator
    and denominator across nets are replica quantities (2k replicas for k-th moments), so the across-net scatter of any
    polynomial quenched quantity is computable. Check: construction in FORMAL; numerical check against nets (part C).
A3. "Perturbation at layer l along a random direction" (brief, item 3). Annealed, every direction orthogonal to the
    replicas' span is equivalent (rotation invariance of the future given the past), so an annealed count "of directions
    whose perturbations survive" is degenerate: all or none. A count needs second spectral moments (tr M^2 with 2
    perturbation replicas, or tr C^2 with 4 cloud replicas) or a per-net spectrum. Check: proof in FORMAL; numerically,
    the annealed survival of perturbations along different past-measurable directions (radial excluded) must agree.
A4. Annealed tangent survival is trivial: E_W |J u|^2 = |u|^2 at every depth (criticality, exact), while the typical value
    decays like exp(-2.5 t/n). So the relevant survival must be finite-size (Gram surgery) or typical (medians, per-net).
    Check: tangent chain test.

## B. The stationary law (brief item 2)
B1. R = 2: does the normalised Gram (delta, radius ratio) given Q follow the mean-field fixed point delta*(Q) with
    corrections of relative order n^{-2/3}? Check: exact chain, n = 8..1024, long runs, batch-mean errors; the exact
    chain's mean ratio E delta / L0 was 1.12 (n = 8) to 1.00 (n = 1024) (numerics lane), slope about n^{-0.6}.
B2. Is the angle slaved to the radius (relaxation ~1.5 Q^{1/3} layers) and the radius ratio a slow variable of size
    n^{-1/3} that forms a joint diffusion with q = Q/n on the time scale s = t/n? Check: derive the diffusion limit and its
    stationary second moment; compare with the chain at n = 64..1024 (n^{1/3} SD of the ratio should converge).
B3. Sharing patterns: noise correlation c (Gaussian), per-layer Bernoulli sharing p, per-coordinate sharing t. Mean field
    predicts delta*(c) ~ (1 - c)^{2/3} for correlation and coordinate sharing, and a different law for Bernoulli layer
    sharing at small refresh rates. Check: chain at several c, p, t.
B4. R = 3, 4 (independent noise): the triangle spread ~ 1.46 sqrt(2/PR) and the 4-replica PR of the cloud; does PR grow
    like (H_n - 1)^2/(pi^2/6 - 1) (a 1/k spectrum)? Check: chain PR at n = 16..1024 against that law and against
    alternatives (PR ~ n^a).
B5. Mixing times: radius (spectral gap of the q-diffusion dq = ds + sqrt5 q dW, essential spectrum from 5/8 per n layers),
    radius ratio (~Q layers), angle (~Q^{1/3}). Check: autocorrelation functions from stationary chain runs.

## C. Relevance at layer l (brief item 3); t = L - l
C1. Closed relevance of the past V_P(t) = Var(E[f | everything before l]) / V: 2 replicas sharing the past and not the
    future. Mean field: angular part decays on ~1.5 Q^{1/3} layers (the angle of two replicas started together grows to
    delta*), radial part on ~n layers. Check: chain at n = 16..1024 against the mean-field curve.
C2. Total relevance of the past T_P(t) = E|f - f'|^2/(2V), replicas with independent pasts and a shared future. Mean field:
    the cloud angle decays under shared noise, algebraically on ~4.5 Q^{1/3} layers, then exponentially. T_P - V_P is the
    past-future interaction. Check: chain; nets.
C3. Dimension: participation ratios of the output covariance due to the past, total version (4 replicas, shared future)
    and closed version (8 replicas: 4 pasts x 2 independent futures). Free-probability prediction in the linear regime:
    1/PR = 1/PR_cloud + 1/PR_response - 1/n (cloud and future sensitivity in free position, by rotation invariance).
    Check: chain against this; per-net PR on nets.
C4. Perturbation survival: Gram surgery at layer l (relative size eps, random direction orthogonal to the state), shared
    noise afterwards; 3 replicas for the response's PR. Check: chain against the finite-angle law and the tangent limit.
C5. Input regime (sigma = 0, replicas = inputs): the share of the output variance carried by the direction of h_l vs its
    radius (Gram surgery: same radius, other direction), and the PR of the input cloud at layer l and at the output,
    at 256 x 32 and 8 x 256; sigma > 0 small: how the future noise erodes the layer-l relevance. Check: chain against nets.

## D. Annealed vs quenched (brief item 4)
D1. Which per-net quantities self-average at large n? Hypothesis: per-net quantities depend on the net mainly through its
    radius history (O(1) across nets, n^{-1/3} within a net); given the radius they self-average. Check: chain moments
    (Var_W) and per-net measurements, n = 8..256.
D2. Where the annealed count misleads: rare nets dominating annealed means (heavy radius tail; tangent means); per-net
    concentration of relevance in few directions (per-net PR vs annealed PR). Check: per-net PR distribution vs chain.

## E. What the chain explains (brief item 5)
E1. Cloud size (5-8x over Lyapunov); E2. gate-flip rates (0.62 sqrt n births); E3. interaction order 1.4 -> 3.9 and the
    flat low-order shares (C(t) = 1 - (1 - t)^{2/3}); E4. the input regime's amplitude/direction split (0.49/0.47 nets vs
    0.60/0.36 chain); E5. the 3n/l decay of differing gates. Check: one table, chain value vs measured value, with the
    mechanism and its label.
