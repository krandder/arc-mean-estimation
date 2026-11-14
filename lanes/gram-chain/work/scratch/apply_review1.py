"""Apply GPT-6 review round 1 findings to the document parts (notes/*.md) and fills."""
import json
N = '/home/agent/workspaces/mats/work/gram-chain/notes/'


def rep(fn, pairs):
    p = N + fn
    s = open(p).read()
    for a, b in pairs:
        if a not in s:
            if b in s:
                continue
            raise SystemExit('NOT FOUND in %s: %s' % (fn, a[:80]))
        s = s.replace(a, b)
    open(p, 'w').write(s)


# ---------------- summary (head template) ----------------
rep('head_template.md', [
    ("""weight-averaged theory that the exact chain confirms to within a few percent and real nets confirm once each net's
radius is used. At layer L - t of a stationary net, the state's direction decides a fraction 1 - Y((t - 1)/T*) of the
output direction's variance""",
     """weight-averaged theory: the exact chain confirms its relevance curves to within a few percent and its other laws to
within 10-30%, and real nets follow it once each net's radius is used. At layer L - t of a stationary net, the state
decides a fraction 1 - Y((t - 1)/T*) of the output direction's variance"""),
    ("""What the chain provably cannot
give is which directions: about k(n - k) log2(1/eps) bits per layer of net-specific orientation that no weight-averaged
or forward-only theory can supply. Per net, the scale of all of this is set by the net's radius, which does not
self-average; dividing by the radius law removes 88-97% of the across-net variance of the cloud's size.""",
     """What the chain cannot give is which
directions: it is invariant under rotations of the layer that fix the replicas, so it carries no orientation
information; describing a k-dimensional relevant subspace to precision eps takes about k(n - k) log2(1/eps) bits, which
annealed theory does not supply (this is a description length, not a proven cost for estimating the mean). Per net, the
scale of all of this is set by the net's radius, which does not self-average; the radius law predicts a net's cloud size
with R^2 = 0.88-0.93 at n = 64-256."""),
    ("""   radius-independent 1/k shape cannot do this. {{PA9_SUMMARY}} With the relevance horizon below: PR_C x T* = 3n/2 at
   every radius.""",
     """   radius-independent 1/k shape cannot do this. {{PA9_SUMMARY}} With the relevance horizon below: PR_C x T* = 3n/2 at
   every radius to leading order (1.28n, 1.40n, 1.46n at the median radius for n = 64, 256, 1024)."""),
    ("""   The closed relevance of the direction is 0.877, 0.666, 0.377, 0.126 at t = 2, 4, 8, 16 for n = 256 against the mean""",
     """   The closed relevance of the state at layer L - t for the output direction is 0.877, 0.666, 0.377, 0.126 at
   t = 2, 4, 8, 16 for n = 256 against the mean"""),
    ("""   n-independent): the chain's ratio of means is 0.375, 0.349, 0.354 at n = 64, 256, 1024, and on real nets the per-net
   radial share follows rho of the net's own radius (median deviation 12%, 11%, 5% at n = 64, 128, 256; PC7 hit).""",
     """   n-independent; HEURISTIC, a small-fluctuation variance proxy, not a Sobol share): the chain's ratio of means is 0.375,
   0.349, 0.354 at n = 64, 256, 1024, and on real nets the per-net radial share follows rho of the net's own radius
   (median deviation 12%, 11%, 5% at n = 64, 128, 256; PC7 hit)."""),
    ("""   c ~ 1.3-1.6 (closed version) instead of the frozen-gate 2. At n = 256 the closed relevance at t = 1, 2, 4, 8, 16 spans 39, 30, 24, 16, 9 effective
   directions. The future's own spectrum is exactly the free-probability one (tangent chain: n/(2t) to within 3-5% for
   t = 2-16).""",
     """   c ~ 1.1-1.6 (closed version) instead of the frozen-gate 2. At n = 256 the closed relevance at t = 1, 2, 4, 8, 16 has
   variance-weighted participation ratios 39, 30, 24, 16, 9 (annealed moment ratios; the median net's is about 0.7 of
   these, section 5). The future's second spectral moment matches free probability (tangent probes within 3-5% of
   n/(2t) at t = 2-16)."""),
    ("""   layer l is n (1 - c_l)^2 / Var D_l -> 1.5 n/l: chain 166, 62, 18.8, 12.1, 6.1 at l = 1, 4, 16, 32, 64 (n = 256) against the
   recursion's 167, 62, 19, 10.3, 5.3 and the input-bits nets' 159, 57, 17, 9.6, 6.1.""",
     """   layer l follows a 1/n vertex recursion that tends to 1.5 n/l: chain 166, 62, 18.8, 12.1, 6.1 at l = 1, 4, 16, 32, 64
   (n = 256) against the recursion's 166, 61, 18.7, 10.2, 5.4 and the input-bits nets' 159, 57, 17, 9.6, 6.1."""),
    ("""   radius after about 8 layers and 63% of inputs die in all-off layers.""",
     """   radius after about 8 layers (PR 1.1-1.4 at l = 16-128, among chains whose four inputs all survive) and 63% of inputs
   die in all-off layers."""),
    ("""7. **Annealed versus quenched** (MEASURED on 136 nets, n = 8-256; PC1, PC2, PC3, PC5, PC6, PC7 hit, PC4 missed). The""",
     """7. **Annealed versus quenched** (MEASURED on 168 nets, n = 8-256; PC1, PC2, PC3, PC5, PC6, PC7 hit, PC4 missed). The"""),
    ("""   0.68); divided by delta*(Qbar) the CV falls to 0.14-0.20, so the net's radius explains 88-97% of the scatter. Per-net""",
     """   0.68); divided by delta*(Qbar) the CV falls to 0.14-0.20 (squared CV cut by 87-97%; the radius law alone predicts a
   net's cloud size with R^2 = 0.88, 0.92, 0.93 at n = 64, 128, 256). Per-net"""),
    ("""   nets), births,""", """   nets: 168 nets), births,"""),
])

# ---------------- body1 ----------------
rep('body1.md', [
    ("""- Integrability (FORMAL 1.5; NUMERICAL check): E Q = infinity and the radius ratio between replicas does not shrink at
  large Q, so annealed second moments of raw states are infinite (n = 64: the top 1% of chains by radius carry 82% of the
  sample mean of |h1 - h2|^2, 94% of it radial). Every annealed quantity here uses scale-free observables (the direction
  u = h/|h| or a/|a|, and log radii). This is also why the numerics lane's annealed D_h was "too noisy".""",
     """- Integrability (FORMAL 1.5; NUMERICAL check): E Q = infinity and the radius ratio between replicas does not shrink at
  large Q, so the annealed second moments of raw-state differences are infinite (n = 64: the top 1% of chains by radius
  carry 82% of the sample mean of |h1 - h2|^2, 94% of it radial). The annealed quantities here use the direction
  u = h/|h| or a/|a| and log radii. Both need a convention on the all-off event (a = 0, probability 2^-n per layer for a
  noiseless output layer): the code floors |a|^2 at 1e-300 (Part B) or |a| at 1e-300 (Part C), so log|a| moments are
  regularised estimands. At n >= 64 the event never occurred in these runs; at n = 16 it did and the log channel is not
  used. This is also why the numerics lane's annealed D_h was "too noisy"."""),
    ("""2.3 Noise sharing (A-share; NUMERICAL). The mean field depends only on E S_12 = t, so Gaussian correlation t (Hermite
degrees), per-coordinate sharing (ANOVA over scalar coordinates) and per-layer sharing (ANOVA over layer blocks) share
C(t) = 1 - E delta_t / E delta_0 -> 1 - (1 - t)^{2/3} = 0.175, 0.370, 0.603 at t = 0.25, 0.5, 0.75 [A, input-bits round 1].

| n | correlation | per coordinate | per layer | finite-eps mean order G(0.01)/0.01: corr / coord / layer | antithetic E delta(-1)/E delta(0) (2^{2/3} = 1.587) |
|---|---|---|---|---|---|
| 16 | 0.181, 0.386, 0.630 | 0.185, 0.389, 0.632 | 0.192, 0.406, 0.654 | 2.80 / 2.54 / 1.90 | 1.604 |
| 64 | 0.180, 0.384, 0.616 | 0.184, 0.383, 0.618 | 0.187, 0.389, 0.629 | 3.45 / 3.44 / 2.60 | 1.582 |
| 256 | 0.177, 0.361, 0.601 | 0.164, 0.367, 0.606 | 0.168, 0.373, 0.609 | 4.10 / 4.11 / 3.38 | 1.605 |""",
     """2.3 Noise sharing (A-share; NUMERICAL). The mean field depends only on E S_12 = t, so Gaussian correlation t (Hermite
degrees), per-coordinate sharing (ANOVA over scalar coordinates) and per-layer sharing (ANOVA over layer blocks) share
C(t) = 1 - E delta_t / E delta_0 -> 1 - (1 - t)^{2/3} = 0.175, 0.370, 0.603 at t = 0.25, 0.5, 0.75 [A, input-bits round 1].
Values below use the registered baseline (E delta_0 from the A-r2 run at the same n). Deviations from the registration:
the sharing runs used a 2n burn-in and 4n recorded layers (registered: 6n and 8n), n = 1024 omits t = 0.9 and 0.99, and
the first scorer used each sharing run's own independent-noise baseline (at n = 256 that gave coordinate C(0.25) = 0.164
and an antithetic ratio 1.605 instead of 0.173 and 1.587; every PA5 clause passes either way).

| n | correlation | per coordinate | per layer | finite-eps mean order G(0.01)/0.01: corr / coord / layer | antithetic E delta(-1)/E delta(0) (2^{2/3} = 1.587) |
|---|---|---|---|---|---|
| 16 | 0.182, 0.386, 0.630 | 0.186, 0.389, 0.632 | 0.193, 0.406, 0.654 | 2.80 / 2.54 / 1.90 | 1.603 |
| 64 | 0.179, 0.383, 0.616 | 0.183, 0.383, 0.617 | 0.187, 0.389, 0.629 | 3.45 / 3.44 / 2.60 | 1.583 |
| 256 | 0.186, 0.368, 0.606 | 0.173, 0.374, 0.610 | 0.177, 0.380, 0.613 | 4.10 / 4.11 / 3.38 | 1.587 |"""),
    ("""lane's nets (0.17-0.26). Antithetic noise multiplies the stationary angle by 2^{2/3} to within 0.3-1.1% (1.582-1.605;
the even share of the direction is then 0.198-0.209, gain 2.4-2.5; nets 0.23-0.27).""",
     """lane's nets (0.17-0.26). Antithetic noise multiplies the stationary angle by 2^{2/3} to within 0.0-1.0% (1.583-1.603;
the even share of the direction is then 0.198-0.209, gain 2.4-2.5; nets 0.23-0.27)."""),
    ("""- One time scale (HEURISTIC, FORMAL 7.10 [C]): T* = (Q + 1) delta* = 1.5 tau and PR_C = n/tau at leading order, so
  PR_C x T* = 3n/2 at every radius: a large-radius net has a smaller, longer-lived cloud and a small-radius net a larger,
  shorter-lived one.""",
     """- One time scale (HEURISTIC, FORMAL 7.10 [C]): T* = (Q + 1) delta* = 1.5 tau and PR_C = n/tau at leading order, so
  PR_C x T* = 3n/2 at every radius to leading order (with the finite-Q definitions 1.28n, 1.40n, 1.46n at the median radius
  for n = 64, 256, 1024): a large-radius net has a smaller, longer-lived cloud and a small-radius net a larger,
  shorter-lived one."""),
])

# ---------------- body2 ----------------
rep('body2.md', [
    ("""The closed relevance agrees with the mean field averaged over the radius law to within 0.003-0.014 at n = 256-1024 and
the curves collapse in (t - 1)/T* (fig 2); the total relevance's tail is 1.2-1.6 times the mean field at t = 4T*, the
slower tail gpt-6-astra attributes to unequal radii under shared noise. Scoring note: the half-life was scored by linear
interpolation between recorded t and the area truncated at 8 T* (where the mean field is below 1e-3); the scorer's first
version read the first recorded t below 0.5 (8 at n = 256, where t = 7 is not recorded: a miss against 6) and integrated
noise out to t = 4n; both changes were made after seeing the n = 256 curve (`logs/deviations.log`). Scaling: the
direction of the state at layer L - t matters for the output's mean for about 0.8 T* ~ 1.6 n^{1/3} layers in total and
falls below 10% after about 2-3 n^{1/3}.""",
     """The closed relevance agrees with the mean field averaged over the radius law to within 0.003-0.014 at n = 256-1024 and
the curves collapse in (t - 1)/T* (fig 2); the total relevance's tail is 1.2-1.6 times the mean field at t = 4T*, the
slower tail gpt-6-astra attributes to unequal radii under shared noise. V_P copies the whole state, so it is the closed
relevance of the full layer-l state for the output direction (its angular part dominates; the radial part is 3.2).
PB1 scoring, both ways: the registered analysis missed (the first recorded t below 0.5 is 8 at n = 256, against 6,
because t = 7 is not recorded; the full-grid area integrates noise out to t = 4n and gives -1.28 at n = 256 and 66.7 at
n = 1024); the revised analysis (linear interpolation between recorded t, area truncated at 8 T*, where the mean field is
below 1e-3) hits; the revision was made after seeing the n = 256 curve (`logs/deviations.log`). Scaling: the layer-l state
matters for the output direction's mean for about 0.8 T* ~ 1.6 n^{1/3} layers in total, and its relevance falls below 10%
after about 2-3 n^{1/3} layers."""),
    ("""sample, make the log channel unusable). PB4 missed as registered: at t >= 160 both relevances are zero within their
standard errors and the strict clause "log above direction at every t >= 8" fails on noise at n = 64 and 256; the""",
     """sample, make the log channel unusable). PB4 missed as registered: the strict clause "log above direction at every
t >= 8" fails where both relevances are near zero (n = 64 at t = 160-192, n = 256 at t = 1024; log-channel standard errors
were not saved); the"""),
    ("""(scale-normalised) output variance is rho(q) = m(q)/(m(q) + 2A q^{-2/3}) (FORMAL 7.11 [C], with A's m):""",
     """(scale-normalised) output variance, measured by the small-fluctuation proxy Var(log|a|)/(Var(log|a|) + tr Cov(u)) (a
variance-component ratio, not a Sobol share), is rho(q) = m(q)/(m(q) + 2A q^{-2/3}) (FORMAL 7.11 [C], with A's m;
HEURISTIC):"""),
    ("""- The future's own spectrum is exactly the free-probability one: two orthonormal tangent probes read
  (tr M)^2/(tr M^2 - (tr M)^2/n) = n/(p - 1), and the exact tangent chain gives 125.8, 63.6, 32.7, 15.2, 7.9 at t = 1, 2, 4,
  8, 16 (n = 256) against n/(2t) = 128, 64, 32, 16, 8 (`results/prM_tangent.json`, post hoc).""",
     """- The future's second spectral moment matches free probability: two orthonormal tangent probes read, up to
  finite-dimensional corrections (the probes live in the n - 1 transverse dimensions) and a ratio-of-means weighting,
  (tr M)^2/(tr M^2 - (tr M)^2/n) = n/(p - 1); the exact tangent chain gives 125.8, 63.6, 32.7, 15.2, 7.9 at t = 1, 2, 4, 8,
  16 (n = 256) against n/(2t) = 128, 64, 32, 16, 8 (`results/prM_tangent.json`, post hoc). This checks one moment ratio,
  not the whole spectral law."""),
    ("""  The formula is within 9-16% at t = 1 (and t = 2 at n = 256) and 22-58% low at t = 2-4 (PB3's single failing clause:
  total PR at n = 64, t = 4, 1.58 times). Writing PR = n/(n/PR_C + c t), the chain gives c ~ 1.3-1.6 for the closed
  version and c ~ 1.0-1.4 for the total version at t <= 16, between the soft-gate value 1 (each layer acting like a
  Gaussian matrix on differences whose gates differ) and the frozen-gate 2. So at n = 256 the state at layer L - t
  carries the output's mean through about 39, 30, 24, 16 and 9 effective directions at t = 1, 2, 4, 8, 16; at t > n the
  formula fails altogether (the future saturates at one direction).""",
     """  The formula is 9-16% low at t = 1 (and t = 2 at n = 256) and 22-58% low at t = 2-4 (PB3's single failing clause:
  total PR at n = 64, t = 4, 1.58 times). Writing PR = n/(n/PR_C + c t), the chain gives c ~ 1.1-1.6 for the closed
  version and c ~ 1.0-1.6 for the total version at t <= 16, between the soft-gate value 1 (each layer acting like a
  Gaussian matrix on differences whose gates differ) and the frozen-gate 2. So at n = 256 the closed relevance of layer
  L - t has variance-weighted participation ratios of about 39, 30, 24, 16 and 9 at t = 1, 2, 4, 8, 16. These are annealed
  moment ratios, not per-net dimensions: Part C finds the median net's cloud PR at about 0.7 of the variance-weighted
  value. For t of order n the formula fails altogether (the future saturates at one direction)."""),
])

# ---------------- body3 ----------------
rep('body3.md', [
    ("""PB6 hit). At infinite width independent inputs are equicorrelated at every layer (correlation c_l, the kernel iterate), so
the infinite-width cloud is isotropic and the kernel says nothing about its dimension. Its anisotropy is a 1/n effect: for
four inputs the double difference D = (u1 - u2).(u3 - u4) has no radial term at linear order and obeys
D' = kappa'(c_l) D + zeta_l with Var zeta_l = E[(relu z1 - relu z2)^2 (relu z3 - relu z4)^2] (four equicorrelated unit
Gaussians). The angular participation ratio is PR(l) = 4n(1 - c_l)^2 / Var D_l, and at depth (theta_l ~ 3 pi/l,
Var zeta ~ 2 theta^4, kappa' ~ 1 - theta/pi) PR(l) ~ 1.5 n/l.""",
     """PB6 hit). At infinite width independent inputs are equicorrelated at every layer (correlation c_l, the kernel iterate), so
the infinite-width cloud is isotropic and the kernel says nothing about its dimension. Its anisotropy is a 1/n effect: for
four inputs the scaled double difference D = sqrt(n) (u1 - u2).(u3 - u4) has no radial term at linear order and obeys
D' = kappa'(c_l) D + zeta_l, Var zeta_l = E[(relu z1 - relu z2)^2 (relu z3 - relu z4)^2] (four equicorrelated Gaussians of
unit radius), Var D_0 = 4. The angular participation ratio is PR(l) = 4n(1 - c_l)^2 / Var D_l, and at depth
(theta_l ~ 3 pi/l, Var zeta ~ 2 theta^4, kappa' ~ 1 - theta/pi) PR(l) ~ 1.5 n/l. Correction after review: the first
numerical recursion interpolated a Monte Carlo source on a 201-point grid in c, which near c = 1 turns its quadratic
vanishing into linear and wrongly made the recursion collapse at depth; with the source by quadrature
(`scratch/vertex_exact.py`) the recursion tends to 1.5 n/l (PR/n = 0.650, 0.240, 0.0732, 0.0397, 0.0211, 0.0110, 0.0057 at
l = 1, 4, 16, 32, 64, 128, 256). The registered PB6 targets came from the first version; they differ from the corrected
values by under 2% at l <= 64."""),
    ("""| vertex recursion, n = 256 | 167 | 107 | 62 | 34 | 18.9 | 10.3 | 5.3 | 2.0 |""",
     """| vertex recursion (quadrature), n = 256 | 166 | 107 | 61 | 34 | 18.7 | 10.2 | 5.4 | 2.8 |"""),
    ("""| vertex recursion, n = 64 | 41.7 | 26.8 | 15.4 | 8.6 | 4.7 | 2.6 | - | - |""",
     """| vertex recursion (quadrature), n = 64 | 41.6 | 26.7 | 15.3 | 8.5 | 4.7 | 2.5 | - | - |"""),
    ("""The leading-order vertex is within 1-3% of the exact chain up to l = 16 and within 15-17% at l = 32-64; it fails at
l ~ n/2, where PR = O(1) and the 1/n expansion is invalid. So at ARC's 256 x 32""",
     """The leading-order vertex is within 1-3% of the exact chain up to l = 16 (n = 256) and 11-27% below it at l = 32-127
(n = 256) and l = 16-32 (n = 64): the finite-width corrections grow as the PR falls toward O(1). So at ARC's 256 x 32"""),
    ("""Collapse: the input cloud's angular PR is 5.2, 2.3, 1.5, 1.3 at l = 1, 4, 8, 16 and about 1.1-1.4
afterwards, so after about 8 layers the input is one direction plus the radius (the relevance lane's N = 1 there).""",
     """Collapse: among chains whose four inputs all survive, the input cloud's angular PR is 5.2, 2.3, 1.5, 1.3 at
l = 1, 4, 8, 16, about 1.1-1.4 for l = 16-128 and 2.0 at l = 255, so after about 8 layers the input is about one direction
plus the radius (the relevance lane's N = 1 there)."""),
])

# ---------------- body4 ----------------
rep('body4.md', [
    ("""136 fresh nets (seeds 5000+: 32 at n = 8-64, 24 at n = 128, 16 at n = 256),""",
     """168 fresh nets (seeds 5000+: 32 at each of n = 8, 16, 32, 64, 24 at n = 128, 16 at n = 256),"""),
    ("""  noisy-kernel fixed point at that net's radius, cuts the CV to 0.14-0.20 at n = 64-256: the net's radius explains 88-97%
  of the across-net variance. The normalised cloud size is 1.01-1.16 (median) at every n: per net, the cloud is the
  fixed point at the net's own radius (fig 5, left: 136 nets collapse on A q^{-2/3} n^{-2/3}).""",
     """  noisy-kernel fixed point at that net's radius, cuts the CV to 0.14-0.20 at n = 64-256 (the squared CV falls by 87%,
  89%, 97%); used directly as a predictor, delta*(Qbar(W)) has R^2 = 0.88, 0.92, 0.93 for the per-net cloud size at
  n = 64, 128, 256 (0.92-0.95 with one fitted scale factor 1.06-1.11). The normalised cloud size is 1.01-1.16 (median) at
  every n: per net, the cloud is the fixed point at the net's own radius (fig 5, left: 168 nets collapse on
  A q^{-2/3} n^{-2/3})."""),
    ("""| cloud size: two noise replicas at angle 2.23 X^{-2/3}, nets measured/law 0.87 (0.72-1.24) (stationary lane, A3) | exact chain: median delta/delta*(Q) 0.96-0.99 at n = 64-1024; per net, cloud size / delta*(Qbar) = 1.01-1.16 (median), CV 0.14-0.20 | explained: the noisy-kernel fixed point at each net's own radius; nets scatter because their radii do |""",
     """| cloud size: two noise replicas at angle 2.23 X^{-2/3}, nets measured/law 0.87 (0.72-1.24) (stationary lane, A3) | exact chain: median delta/delta*(Q) 0.96-0.99 at n = 64-1024; per net, cloud size / delta*(Qbar) = 1.01-1.16 (median), R^2 0.88-0.93 | explained: the noisy-kernel fixed point at each net's own radius; nets scatter because their radii do |"""),
])

# ---------------- body5 (cannot) ----------------
rep('body5.md', [
    ("""- Which directions (PROVEN, FORMAL 1.3; relevance lane Theorem 1). Given the past, the future is invariant under
  rotations of layer l that fix the replicas (sharper: fix the cloud's mean direction), so every annealed relevance
  quantity is the same for every direction outside the replicas' span. The relevant k-frame at layer l is Haar-random
  relative to everything past-measurable except the state's own direction (the kstar-frames lane's Proposition 2 is the
  same fact seen from the past). Specifying a k-dimensional subspace of R^n to precision eps takes about
  k(n - k) log2(1/eps) bits; the chain supplies O(k) numbers (the spectrum's moments). In the stationary regime,
  k ~ n/(tau + 2t) ~ n^{2/3} near the output, so about n^{5/3} log2(1/eps) bits per layer are per-net information that no
  annealed theory and no forward-only computation can supply; only a backward pass through the specific weights (or a
  learned map, which the kstar-frames lane found recovers 93-99% of the sensitivity weight) can.""",
     """- Which directions. PROVEN (FORMAL 1.3; relevance lane Theorem 1 is the sharper form): given the past, the joint law of
  the future responses to perturbations of layer l depends on the perturbations only through their Gram relations with
  the replicas (rotations of layer l fixing the replicas, or the mean direction, leave it unchanged). So the chain, which
  only sees Gram matrices, carries no information about which directions of layer l are relevant; and the frozen
  Jacobian's transverse singular frame is Haar given the past (relevance lane Corollary 1b, PROVEN). That the frame of the
  full nonlinear, cloud-averaged relevance operator is Haar relative to the cloud is HEURISTIC (it is the free-product
  assumption of 3.3). None of this applies to output coordinates (E[h' | h] is along the all-ones vector).
  Size of what is missing (interpretation, not a bound): describing a generic k-dimensional subspace of R^n to precision
  eps takes about k(n - k) log2(1/eps) bits, while the chain supplies O(k) numbers (spectral moments). With k taken of the
  order of the participation ratio, n^{2/3} near the output in the stationary regime, that is of order n^{5/3}
  log2(1/eps) bits per layer. A participation ratio is not the rank needed to capture 1 - eps of the variance (the
  spectrum's tail is not measured here), and nothing here shows that estimating a mean requires encoding that subspace;
  the kstar-frames lane found a polynomial-size learned map recovering 93-99% of the sensitivity weight."""),
])

# ---------------- fills ----------------
f = json.load(open(N + 'fills.json'))
f['SCORE_SUMMARY'] = ('Of the 24 registered predictions, 14 hit, 7 missed and 3 are pending with the revised PB1 analysis (13 hits, '
                      '8 misses with PB1 as first analysed); section 9 lists each. GPT-6 review: major revision (round 1); '
                      'all 14 findings applied (section 10).')
f['SCORE_TOTAL'] = ('Totals: 14 hits, 7 misses, 3 pending with PB1 as revised; 13 hits, 8 misses, 3 pending with PB1 as first '
                    'analysed.')
f['PA9_TEXT'] = ("The local slope of PR_w rises from 0.56 (n = 16-128) to 0.61 (128-256), against 0.41 for a 1/k spectrum at "
                 "that step. Amendment A1 was hashed at 21:33:29Z, before the n = 256 result existed but after that run had "
                 "started (21:27:34Z; no output had been seen); n = 512 and 1024 are prospective. Its criterion: slope "
                 "between n = 256 and 1024 above 0.50 with the bootstrap 90% interval above 0.42, i.e. PR_w(1024) > 97.9 "
                 "at the point estimate; even a hit favours the n^{2/3} law over this range without proving the exponent or "
                 "the spectral shape.")
f['PA7'] = 'pending, and at most partial: registered at every width, but the n = 512, 1024 runs were dropped'
f['PA8X'] = '; already a miss on its PR clause, so the third moments cannot reverse it'
json.dump(f, open(N + 'fills.json', 'w'), indent=1)
print('applied')
