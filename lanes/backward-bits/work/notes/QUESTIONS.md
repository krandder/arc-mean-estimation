# Backward bits: assumptions and open questions (leaf pool-qxszj1.27.1, 2 Nov 2026 ~12:40Z)

Lane: backward-bits (bead pool-qxszj1.27), target M1. Kelvin's ask of 2 Nov ~12:15Z (verbatim in the brief) and
main's formalisation. Each item: the assumption or question, and how it gets checked.

## A. The model and the objects

A1. Net. Model S as in the bit-accounting S4 runs: h_0 = x ~ N(0, I_n); h_l = relu(W_l h_{l-1}) + sigma xi_l for
    l = 1..L-1; output a = relu(W_L h_{L-1}) with no noise; W_l = st.W_layer(seed, n, l) (the small nets of the
    bit-accounting lane). Check: the code reproduces bit-accounting run_noisy.py's sampler at sigma = 1 on one
    seed (same weights, same law of a).
A2. "The last layer" is the output code: a K-cell vector quantiser c_L = Q(a) (k-means, Lloyd to convergence, best of
    several restarts). Because a is a deterministic function of h_{L-1}, the code at L-1 is c_L itself (no erasure
    between L-1 and L). Check: Lloyd convergence (relative change of the distortion < 1e-6), restarts agree.
A3. Bits = Shannon information in bits. Rate of a deterministic code = its entropy H(c_l); what it carries about the
    next code = I(c_l; c_{l+1}). Check: both are plug-in/Rao-Blackwellised estimates on held-out points with
    bias corrections; doubling M and N must not move them by more than the registered tolerance.

## B. Main's formalisation, item by item

B1. "What layer l-1 must carry is I(h_{l-1}; c_l) = H(c_l) - E H(c_l | h_{l-1})." CORRECT as the ceiling: no
    function of h_{l-1}, deterministic or random, carries more about c_l (data processing), and it equals Kelvin's
    "R_l minus the bits the noise destroys" with R_l = H(c_l) and destroyed bits E_l = E H(c_l | h_{l-1}).
    Check: estimator against an exact 1-D case (tests/), M-doubling on the nets.
B2. "Converged when its rate reaches the target within tolerance AND its prediction of c_l is near the limit."
    SUSPECTED WRONG: with Gaussian noise between the layers every code value of c_l has positive probability given
    any h_{l-1}, so a non-constant deterministic code at l-1 can never be a function of c_l: H(c_{l-1} | c_l) > 0,
    hence I(c_{l-1}; c_l) < H(c_{l-1}) strictly. A code with rate = target therefore carries strictly less than the
    target, and a code that carries the whole target needs a sufficient statistic, which (analyticity of the
    Gaussian-smoothed posterior) has no countable version: its rate is infinite. Check: proof in FORMAL.md; measure
    the rate-relevance (information-bottleneck) curve at every layer: relevance at rate = target, and the rate
    needed to come within eps of the target.
B3. Which of the two does Kelvin mean? "converges to exactly or less [than] the layer l, minus the amount of info
    destroyed": a rate budget (rate <= target) or a relevance goal (relevance -> target)? Both are run: chain K
    (Kelvin's rule: rate <= T) and chain R (relevance >= T - eps, rate as needed). Check: report both; flag where
    chain R's rate exceeds its successor's.
B4. Is the recursion's target the right count for the OUTPUT? T_{l-1} = I(h_{l-1}; c_l) is information about the
    next CODE. If c_l were sufficient for the output code, T_{l-1} >= I(h_{l-1}; c_L) (it would over-count: it also
    pays for c_l's own resolution bits); with a lossy c_l it can under-count. The truth I(h_l; c_L) is computable
    directly on small nets (Monte Carlo over the whole future noise). Check: per layer T_l, I(h_l; c_L),
    I(c_l; c_L) and the chain's own prediction of c_L; accumulated error = I(h_l; c_L) - I(c_l; c_L).
B5. "H(c_l | h_{l-1}) is computable near-exactly for b <= 16 by sampling xi many times." Plausible for the
    per-point posterior when few codes have mass given h (small noise), but the plug-in entropy from M draws is
    biased low by about (m - 1)/(2 M ln 2) bits (m = codes seen). Check: Miller-Madow correction, M in {256, 1024,
    4096} on a subset, exact 1-D case; report the M at which the estimate stops moving.
B6. "Warm-start the l-1 encoder from c_l composed with the noisy layer map." The composition with the noise set to
    zero, c_l(relu(W_l h)), is Kelvin's "use the last encoding". Its rate is about R_l, not R_l - E_l. Check: report
    its rate and relevance at every step as the "reuse" baseline.
B7. Shared future noise. The S4 count (per-sample reproduction with the same future noise) is a different quantity:
    given xi_l the code needs H(c_l | xi_l) = I(h_{l-1}; c_l) + I(h_{l-1}; xi_l | c_l) >= T. Check: FORMAL.md
    (identity); measured as the shared-noise output distortion of each code with a per-cell decoder.

## C. Open design questions (decided in dev on seed 9100, registered before scored runs)

C1. sigma per width so that the noise erases 0.5-2 bits of the output code at the first backward step.
C2. Output code size K_L (distortion of the output code; posterior vectors of length K_L must stay small enough
    for exact counting; b <= 8 planned).
C3. N (points) and M (noise draws) for targets and evaluations; tolerance on T and on the rates.
C4. Encoder class: posterior predictor (MLP, depth 2) followed by deterministic-IB clustering of the predicted
    posteriors; "look-ahead" control clusters the Monte Carlo posteriors themselves (exact posterior, not a cheap
    function). Deeper encoders: depth 1, 2, 4 at every layer.
C5. eps for chain R; the tolerance for "rate reached".
C6. Gaussian-channel comparison: rate I(h; z) by the Kolchinsky-Tracey pairwise bounds (upper with KL, lower with
    Bhattacharyya) on the empirical mixture, relevance by the mixture-posterior plug-in; feasible for d <= 8?
    Check in dev: the two bounds must be close (gap < 0.2 bit) for the comparison to be called reliable.
C7. Forward-trained comparison: codes trained directly on the output code at each layer (same machinery, target
    c_L, posterior over the whole future), and codes trained on the shared-noise output distortion (S4's score).

## D. Things that would make the lane's answer wrong (checked as the work goes)
D1. Overfitting: codes fitted and evaluated on the same draws (optimistic relevance). All evaluations use held-out
    points with fresh noise draws.
D2. A layer whose target exceeds the successor's rate: impossible in truth (data processing), so it flags an
    estimation error.
D3. A code that beats the target: impossible in truth; flags bias.
