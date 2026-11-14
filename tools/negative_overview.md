# Negative results

Every approach in this repository that failed: what was tried, why it failed, and what the failure rules out. The
first part is a map by theme. The second part lists every failed approach lane by lane (286 entries), followed by the
lane's registered predictions that failed and the claims it corrected or withdrew.

How to read it:

- These are **restricted negatives**. Each one says that a method, as built and tested, lost to the best sampler or
  missed its registered criterion on the nets tested. None is an impossibility proof unless the entry says "proven",
  and the proofs here were written and checked by AI models only; no proof has been checked by a human
  (`OPEN-DECISIONS.md`).
- The baseline matters. Early lanes compared with plain Monte Carlo (MC). From 31 October the bar is the best sampler:
  randomised quasi-Monte Carlo (RQMC, scrambled Sobol), a Kerdock design, or a multilevel sampler.
- "Registered" means the prediction or kill test was written and hashed before the run. "Exploratory" and "post hoc"
  mean it was not.
- The per-lane entries were extracted on 14 November 2026 by reading each lane report in full. Nothing was re-run.
  The extraction itself has not been reviewed; the lane report is the authority, and each entry names its section.
- Contest participants are not named here (`OPEN-DECISIONS.md`).

## Map by theme

### 1. ARC's own cumulant hierarchy, at depth proportional to width

- At the contest shape (width 256, depth 32) ARC's order 2 beats RQMC by about 2x only near 450 forward passes, on 4
  of 5 nets. Order 3 loses 5-30x at its own cost. At the contest budget (about 65,000 passes) RQMC is 7-40x more
  accurate than any ARC variant that fits. Registered. Lane `arc-update`.
- Along depth = width/8 each step up the hierarchy buys a factor 4-8 (order 2 to 3) or 2-4 (3 to 4) in error and
  costs about width/4 to 3 x width times more. The two-level error-cost slope is 0.23-0.52 against sampling's 1.
  `arc-update`. At 512 x 64 order 2 falls below RQMC (0.84x). `future-aware`.
- An earlier, independent measurement: order 2's gain over plain MC shrinks from 2-8 to about 0.7-1.1 by width 1024,
  and factorised order 3 falls behind as width grows. Exploratory and unreviewed. `hardness` section 6.3.
- With small noise on every activation: no win at depth 32 at the primary noise levels, for means or for tails.
  `arc-noisy`.
- Exact Gaussian moments do no better than ARC's cheaper truncation. `arc-update`, `arc-noisy`, `bits-bounds`.
- This is not a negative about deduction in general. At the contest's Phase-2 shape (1024 x 16) the ladder is steep
  (slope 0.83) and order 3 is far more accurate than full-budget RQMC at 1.5x the budget. `scale-mode` section 7.

### 2. Stronger deductive closures and descriptions

- The public "scale mode" closure: 2.5x better than RQMC at its own cost (688 passes) at 256 x 32, caught at about
  2.3x that cost, 33-65x behind at the budget. Both registered escape criteria failed. `scale-mode`.
- Future-aware truncation (keep the third cumulant only where the future reads it): loses to RQMC 6-200x as
  implemented; a win of 2.4-3.0x exists only under a cost no implementation reached. `future-aware`.
- Radius-corrected Gaussian closure: error near L/n^2 (a post hoc observation), but as run it costs at least about
  255x what MC needs for that error. No deductive version exists. `arc-update`.
- Boundary-aware cell families: failed both registered development kill tests; cells built from the weights stay at
  order 2's level. `boundary-family`.
- Fully non-Gaussian families (independent components, cells, joint blocks, attractor transfer, learned code): none
  was shown to scale with depth; re-projecting at every layer accumulates error. `nongauss-family`.
- Sparse dictionaries and transcoders: no sparse structure found at the noise precision beyond the gate pattern;
  transcoder closures lose to neuron-level order 2. `sparse-codes`.
- Mode-cumulant, scale-mixture and recursive-moment closures; copula codes; meet in the middle. `arc-noisy`.
- Gate-pattern merging: none found on random depth-32 nets at width 128 or more; a family that lists gate classes
  for 256 x 32 would need about 2^25 classes at the last layer (a factored discrete part is not excluded).
  `gate-entropy`.
- Frames of the directions that matter: set by the weights still to come; no method cleared the registered gate, and
  no estimator was built. `kstar-frames`. One block for all inputs cannot use the small per-path count.
  `lyapunov-dimension`.
- Forward-chain certificates on random noisy nets: every certified bound is vacuous; coverage cost grows linearly
  with width. `cm-interp-R`.
- Layer-wise closures in general: the oracle form of "low-order statistics leave the mean ambiguous" is false, the
  worst-case form is true but far larger than ARC's actual error, and the lower bound on typical per-step closure
  error is open. `cumulant-ambiguity`.

### 3. Exact, regional and pattern-based methods

- Certified branch-and-bound over input cones: the bounds-only estimate never beats RQMC (best ratio 0.18, at width
  3); cost grows about 10x per unit of width. `unrestricted`.
- Certified cell code at width 8, depth 256: 23-106x worse than RQMC, 0 of 6 nets pass. Integrate the top regions and
  drop the rest: 7-1,222x worse even at an optimistic cost. `nd-exact`.
- Two sample-free estimators at width 8, depth 256 (two-sided, backward-only): each beats RQMC 3x on only 2 of 6
  healthy nets; the registered tests fail. `narrow-deep-m1`. The earlier hybrid from `narrow-deep` diverges on 4 of 6
  of those nets.
- Depth-4 nets of width 4-8: exact cells win only where cells are few; merging regions saves a constant 2-3x that
  does not improve with width; chains indexed by gate patterns stay more than 100x behind MC; learned linear experts
  show no stable gain. All exploratory, and the lane was redirected before it concluded. `adaptive-regions`.
- Input moments alone: matching Gaussian moments to degree d leaves the mean undetermined by at least 0.21 standard
  deviations at every degree run. Exploratory, unreviewed. `moment-matching`.

### 4. The sampling side: constants, not rates

- No structured sampler was shown to beat RQMC's fitted exponent (about 1.05 at 256 x 32). Designs buy constants:
  the best, a Kerdock 5-design, gives 2.9x over MC at 2^16 passes. White-box frames, lattice rules, k-wise designs,
  fixed point sets: no exponent gain. `randomness`.
- Pre-integration along a line: raised the fitted exponent only at input dimension 4-8, and lost at equal compute on
  every net (21-1,410x on the ladder). `preint`.
- RQMC over the input, quadratic controls, learned rotations, antithetic pairs: constants of 2-7x, no robust rate
  gain. `input-bits`. In the stationary regime structure buys 2-8x that does not grow with width. `stationary`.
- Multilevel shared-trajectory sampling: about break-even at 256 x 32 (0.99-1.01). Its gain is proven only under cost
  hypotheses and should pay only at depths in the hundreds. `unrestricted`, `bits-bounds`, `randomness`, `preint`.
- Rare events: Gaussian importance sampling, twisted SMC and mode splitting failed their registered kill tests.
  `arc-noisy`. Learned and most-likely-path guides fail beyond about 2^-15 to 2^-20 on normalised nets.
  `cm-interp-R`.

### 5. Hybrids of deduction and sampling

- Exact-mean controls plus RQMC: parity with RQMC at the budget (1.00-1.03x), scored post hoc. `future-aware`.
- ARC propagation plus a Kerdock design on noisy nets: a registered win at depth 8 (1.2-9.9x over the best sampler,
  1.04-1.76x over the better of its two ingredients), none at depth 32 at the primary noise levels (0.84-1.06x).
  `arc-noisy`.
- Cell code as a control with an RQMC correction: the cells add nothing. `nd-exact`.
- Low-dimensional control variates on active-subspace features. `relevance`. First-layer controls. `randomness`.

### 6. Theory that did not go through

- "A front-half summary read out linearly needs exp(c k*) numbers": refuted as a law. The count is polynomial in the
  width at fixed depth and precision. `cut-rank`.
- The replacement law, (1/eps)^(2(n-1)/3) numbers for one-way linear summaries, cannot be extended to nonlinear
  readouts or to back-and-forth with real numbers, so size bounds of this kind cannot cover ARC's closures.
  `cut-rank-ext`.
- An average-case lower bound for random nets at depth proportional to width: not possible with current tools; the
  low-degree method and standard cryptographic assumptions do not supply one. `hardness`.
- An unrestricted impossibility proof, and the lane's own optimality conjecture for plain MC (C0, replaced by C0*).
  `unrestricted`.
- "Smooth gates are more tractable": true asymptotically for one back layer under conditions, not the main factor at
  the sizes tested; the Gaussian closure beat both samplers on 0 of 45 trained nets. `tractable-gates`.
- Finite-width effective theory with noise has no fixed point for one input; several closures for the stationary
  cloud missed their registered tests. `stationary-numerics`.
- The hash argument as stated (the count is not exp(k*); "hash implies hard to average" is false for a random hash
  with a known ensemble mean), and a lower bound on bits for actual nets from the cell rate-distortion argument
  (proved only for an idealised source whose hypotheses fail for nets). `bits-bounds`.

### 7. Bit accounting ("do correctly compressed bits get scrambled between layers?")

- The code-based test does not discriminate: learned codes look simple from layer to layer, but so does the chaotic
  control. Several registered hypotheses of the lane missed. `bit-accounting`.
- The rule "next code's bits minus erased bits" is the right ceiling (proved), but no fixed encoding carries its own
  rate's worth of it and the backward chain drifts: a median 26% of the truth survives at the input.
  `backward-bits`.
- Deductive estimation of the mean by propagating codes on small nets: loses to MC by 60-5,000x. `bit-accounting`.
- Counts are best-found upper bounds, not certified. At 256 x 32 only the layer-0 count is converged by the lane's
  own rule. `bit-accounting-arc`.
- The heuristic formula for the counts is right only within about 2x at intermediate cuts; its match with learned
  codes "within 3-8%" used interim numbers and did not survive. `bits-bounds`, corrected by `bit-accounting-arc`.
- Both registered per-net mean-degree tests missed. `relevance`. The free-product count of relevant directions
  failed in two lanes. `gram-chain`, `relevance`.

### 8. Trained networks

- AlgZoo RNNs with noise: every deductive description built loses to Monte Carlo by 1e2-1e5 at equal compute, except
  the 10-parameter closed form for the smallest model. `algzoo-noisy`.
- A penalty that makes a small transformer easier to estimate cut the propagation error 9-191x, at a task cost, and
  propagation still lost to sampling by 15-50x. Registered, never reviewed, parked. `estimability`.
- Gaussian closures on trained narrow-deep nets: 110-1,800x worse than the best sampler at 1,024 paths, and
  splitting a few gates does not fix it (registered refutation). `narrow-deep`. On 45 trained sorting nets the
  closure never beat both MC and RQMC. `tractable-gates`.

### 9. Our own claims that were later corrected or withdrawn

Cross-lane corrections are in the `README.md` table (both rows). The main ones:

- The cut-rank lower bound was narrowed by its extension (stands for one-way linear summaries only).
- The synthesis draft of 2 November is superseded by four lane finals: the claim that about nL evaluations identify
  the net was withdrawn, the hybrid score and the deductive window were corrected, and the leaderboard gap was
  re-attributed.
- The stationary lane's "the radius carries the input" was corrected by `input-bits`; its near-floor rate and one
  band were contradicted by `stationary-numerics`, whose assumed cloud spectrum was in turn refuted by `gram-chain`.
- The fixed-budget bit counts for 256 x 32 in `bit-accounting` were replaced by the variable-rate counts in
  `bit-accounting-arc`.
- The literature note on ARC's deep networks repeats claims about certificates that the phase-R lane withdrew after
  review, and a survival law that `boundary-family` later found to hold for mean shifts only.
- Learned-experts results before 2 November 18:56Z were ruled not to count. `adaptive-regions`.
- The first reading of the public leaderboard (best samplers 10-50x better than plain MC) is not a method frontier:
  the top score is attributed, by inference for the final run, to fitting the public nets. `phase1-board`.

Within lanes, the reviews changed many claims; those are listed under each lane below.

