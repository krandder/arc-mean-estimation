# Bits-bounds lane: questions and assumptions (21:15Z, 1 November)

Each item: the assumption or question, and how it gets checked.

## Premises from the brief

P1. "A forward-only sweep must keep everything any future could need; a sweep that reads the future first can keep only
the relevant bits." Check: is there a model in which this is a theorem with a measurable gap? The information-only
version is capped (K2: n^2 l log(1/eps) bits suffice), so the gap must be stated for a representational class.
Check by proof (FORMAL), and by measuring the forward-only (future-averaged) versus two-sided (actual future) residual
on the same clouds (E1).

P2. "Hardness and upper bounds tie to one parameter N(l, eps)." Assumption to test: a single number suffices.
Alternative: two faces (resolution bits for cell/enumeration methods, non-Gaussianity for closures) govern different
families. Check: does any one definition lower-bound all four families? By proof (which classes each bound covers).

P3. Kelvin's hash premise: deep nets collapse to k* dimensions that interact like a hash; final layers are hard to
average. Questions: (a) does a hash over N bits make the MEAN hard (concentration says its mean self-averages)?
(b) is k* the relevant count, or the cloud's dimension, or a two-sided product? (c) where in depth do the bits that
matter live (final layers or intermediate)? Check: proofs for (a); measured profiles for (b), (c).

## Definitions to fix

D1. The past at layer l: the cloud P_l (law of h_l over the input). Its angular spread, its principal spreads s_k(l)
(the "Lyapunov covariances"), its radial spread (amplitude). Check: measure the angular spectrum against the
Lyapunov guess exp(-2 k l / n).

D2. The future at layer l: g_l, piecewise linear. What it "amplifies": its Jacobian J_l (k* directions). Where it is
nonlinear: future gate hyperplanes crossing the cloud. Check: the frozen-gate residual identity
R(h; c) = (J_l(h) - J_l(c)) h (Euler), and its size as a function of the angle phi between h and c and of L'.

D3. Candidate N(l, eps): log2 of the least number of cells (references) at layer l such that freezing the future's
gates at each cell's reference leaves residual <= eps^2 V. Forward-only version: cells chosen without the future,
residual averaged over the future. Two-sided version: the actual future. Check: computable on nets (E1); a
rate-distortion lower bound (FORMAL).

## Questions for the theory

T1. Model: p-pass sweeps with M bits/reals and per-layer work; do the four families fit, with what (p, M, work)?
T2. Streaming reduction to communication: M >= CC_{2p-1}/(2p-1). What do the known CC bounds give? (Polynomial.)
T3. Which restriction makes input/noise bits the lower-bound parameter? Candidates: measure-propagation sweeps
(state = mixture of M components), cell/quantisation sweeps (state = M cells with frozen futures), closures.
T4. Lower bounds in each class in terms of N: rate-distortion/quantisation (cells), kernel quadrature (atoms),
bias floor (closures). Which are PROVEN, PROVEN UNDER a hypothesis, CONJECTURE?
T5. Upper bound: an estimator that samples or enumerates the relevant bits and integrates the rest. Natural candidate:
a multilevel sampler whose merge freezes the future's gates at M references (generalising the one-reference radial
merge of K5), and its deterministic version (cell statistics by closure, future by frozen gates).
T6. When could it beat the best multilevel sampler polynomially? Regimes L < sqrt(n), sqrt(n) < L < n, L ~ alpha n,
L >> n. Needs the scaling of N(l, eps) and of the residual D_l(M) with M.
T7. Formula for N(l, eps) from the past spectrum and the future's linearity scale (a water-filling form?). Check
against measured D_l(M) (E2).

## Numerics needed (pre-register before evaluation runs; dev seeds >= 9000 only calibrate)

E1. D_l(M) profile: residual of M-reference frozen-gate merging, per layer, width, depth; forward-only (references
from the past, residual averaged over resampled futures) versus two-sided.
E2. The residual of one pair (h, c) against the angle phi and L' (cubic law?), and the water-filling prediction of
log2 M* from the cloud's spectrum.
E3. The estimator of T5 against the one-reference multilevel sampler and MC at equal cost, unbiased version, on fresh
nets including ARC's 256 x 32 and L ~ n.

## Coordination

- relevance lane (work/relevance/): defines and measures N; I propose a definition (notes/N_definition.md) and use
  theirs once fixed. Do not duplicate their measurements of per-layer counts.
- gram-chain lane (work/gram-chain/): exact annealed replica quantities, including tangent replicas; the
  forward-only (future-averaged) one-reference residual is a 2-replica + tangent chain quantity, so they could compute
  it exactly. I measure per-net quantities on nets.
