# Relevance lane: assumptions and open questions, each with its check (1 Nov 2026, 21:00Z)

Q1. Is the brief's linear route right: "forward variance times backward amplification, per covariant Lyapunov
    direction, with a 1/k forward spread"?
    Suspicion [C]: no. Given the past, the future weights act on the angular part of the state through a Gaussian
    matrix that is independent of the past and right-rotation invariant (the kstar-frames Prop. 2 argument, applied to
    the whole future). So the future's singular frame (and every future gate normal) is Haar-random relative to the
    cloud's principal axes, except the mean direction. The forward 1/k shape then enters the linear relevance spectrum
    only through a free multiplicative convolution, i.e. as O(sqrt(2/PR)) weight fluctuations; N_1 is set by the
    backward singular spectrum (half-width Fuss-Catalan / Lyapunov). CLVs k >= 2 are future-dependent, so their decay
    rates do not price past-measurable directions.
    Check: proof (theory v1) + on nets, the eigenvalues of R_1 against (a) free product of the measured spectra,
    (b) the brief's CLV formula; overlap of the top eigenvectors of Sigma with those of R_1 against Haar.

Q2. Is the Jacobian at the mean (frozen gates) the right linear part?
    Suspicion [C]: only within the coherence radius (kstar-frames: ~1.4/L' rad). The stationary cloud at n = 256 has
    angle ~0.39 rad and the input cloud at layer 16 of 256 x 32 ~0.38 rad, so tr(J^m Sigma J^m^T) should exceed V_l by
    about the mean Hermite degree. The orthogonal linear part is the cloud-averaged Jacobian (Stein).
    Check: measure both, and the cross term of the exact identity.

Q3. Degree spectrum of g_l on the layer-l cloud. Prediction [C, infinite-width annealed, small angles]: with the
    Jacobian-overlap factor (1 - theta/pi) per future layer and the kernel's finite-angle contraction
    theta_{l+tau} = theta_l / (1 + theta_l tau/(3 pi)), J_l(rho) = J_l(1) (1 + x sqrt(1 - rho))^{-3},
    x = theta_l t/(3 pi); hence s_1 = 1/(1 + x), mean degree D = (1 + x)^2, V_l / tr Sigma = (1 + x)^{-2}.
    Input regime (theta_l ~ 3 pi / l at depth): s_1 = l/L. Stationary regime: future noise is independent between the
    two copies inside K_l, so the angle does not contract; separate derivation needed (radial part survives, angular
    part decays at about theta*/pi per layer?).
    Check: K_l(rho) and Stein V_{l,1} on nets, all layers, both regimes; exact-kernel (large-angle) version; finite-width
    amplitude correction.

Q4. How many directions does each degree need? Suspicion: degree 1 ~ (n/(2t)) ln(1/eps) for the vector output (1 for a
    scalar); degree 2 is a sum of rank-one terms over the straddled gates with Haar-random normals, mostly from the
    first ~3 pi/theta future layers, so it spreads over many directions and a k-dim projection keeps only ~(k/r)^2 of
    it. If so, N(l, eps) is small only where the degree >= 2 share is below eps.
    Check: N(l, eps) by pick-freeze on active-subspace bases, per-degree explained shares of the same subspaces.

Q5. Stationary regime: which part of h_l carries V_l at large t? Suspicion: the radius (slow Kesten chain) after the
    angular part is forgotten, so N could fall to ~1 at t >~ (pi/theta*) ln(1/eps) + Q^{1/3}; but V_l / V is then small.
    Check: radial share of V_l against t; N at t = n/8 .. 2n.

Q6. Input regime: the radius |h_l| is an exact factor at sigma = 0; how much does it explain at layer l (past amplitude
    C_l/C_L of the amplitude share plus the |x| share)? Check: S_l(|h_l|) by pick-freeze on the true law (the radius
    can be held fixed exactly by rescaling).

Q7. Gaussian convention fidelity: V_l and E g_l under gamma_l against mu_l. Expected good in the stationary regime at
    n >= 64 (skews <= 0.4), poor in the input regime at small l (atoms at zero). Check: measure both.

Q8. Do the gram-chain lane's annealed counts match the median quenched N? Check: when their numbers exist.

Q9. Consequence for M1: if N(l, eps) is large wherever V_l matters, a hybrid estimator cannot beat sampling by
    resolving a few relevant bits; say so with the numbers. If N is small somewhere (stationary, large t; input, last
    layers), build the hybrid and compare at equal compute.
