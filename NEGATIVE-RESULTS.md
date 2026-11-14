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

## Lane by lane

Order: the 2-3 November lanes at the contest shape first, then exact and narrow-deep methods, the first week's
families, theory, and bit accounting. Jump to a lane:

[`arc-update`](#arc-update) [`scale-mode`](#scale-mode) [`future-aware`](#future-aware) [`preint`](#preint) [`randomness`](#randomness) [`adaptive-regions`](#adaptive-regions) [`phase1-board`](#phase1-board) [`cumulant-ambiguity`](#cumulant-ambiguity) [`moment-matching`](#moment-matching) [`nd-exact`](#nd-exact) [`unrestricted`](#unrestricted) [`narrow-deep`](#narrow-deep) [`narrow-deep-m1`](#narrow-deep-m1) [`arc-noisy`](#arc-noisy) [`algzoo-noisy`](#algzoo-noisy) [`boundary-family`](#boundary-family) [`nongauss-family`](#nongauss-family) [`sparse-codes`](#sparse-codes) [`cm-interp-R`](#cm-interp-r) [`estimability`](#estimability) [`hardness`](#hardness) [`lyapunov-dimension`](#lyapunov-dimension) [`random-phases`](#random-phases) [`gate-entropy`](#gate-entropy) [`cut-rank`](#cut-rank) [`cut-rank-ext`](#cut-rank-ext) [`kstar-frames`](#kstar-frames) [`tractable-gates`](#tractable-gates) [`stationary`](#stationary) [`stationary-numerics`](#stationary-numerics) [`input-bits`](#input-bits) [`gram-chain`](#gram-chain) [`relevance`](#relevance) [`bits-bounds`](#bits-bounds) [`bit-accounting`](#bit-accounting) [`bit-accounting-arc`](#bit-accounting-arc) [`backward-bits`](#backward-bits) [`arc-deep-networks-note`](#arc-deep-networks-note) [`synthesis-draft`](#synthesis-draft)

### arc-update

Report: `arc-update-2026-11-02.md` (lanes/arc-update/). Final state: 2026-11-02 13:50Z (status line: final 10:30Z, update by main 13:50Z; outbox file and log entry are stamped 13:29Z).

Headline: At 256x32 ARC's order 2 beats RQMC about 2x only near 450 passes (4 of 5 nets), order 3 loses 5-30x, and at the 6.5e4-pass budget RQMC is 7-40x better. A restricted negative for the tested methods, not a proof.

Status: **negative result**. registered benchmark of ARC's code (40 scorecard rows: 31 hold, 4 fail, 1 partial, 4 undetermined); restricted to the tested methods; GPT-6 reviewed once plus a short re-check, final text not re-reviewed; theory by the lane author and the AI co-prover, not human-checked

Failed approaches (8):

1. **ARC order 3 (k3f) at the Phase-1 shape**
   - Tried: ARC's mlp_kprop factorised order 3 on five 256 x 32 nets (200-204), 49,097 passes by ARC's flop counter, against scrambled-Sobol RQMC (8 scrambles per size)
   - Outcome: nMSE 0.6-2.8e-4; gain over RQMC at its own cost 0.035-0.18 (loses 5-30x); RQMC reaches its error at 2,300-6,400 passes
   - Why it failed: each order costs ~n/4 to ~3n times more and buys only a factor 4-8 in error
   - Rules out: ARC's order 3 as implemented beating RQMC at 256 x 32. Does NOT exclude engineered order-3 implementations, order 4 at 256 x 32 (not run), or other closures.
   - Evidence: registered. Source: sections 4.1, 4.2
2. **ARC's hierarchy at the contest budget**
   - Tried: best ARC variant affordable within 6.5e4 passes at 256 x 32 against RQMC at the same budget, 5 nets
   - Outcome: RQMC 6.7x, 39.8x, 17.8x, 34.1x, 21.6x more accurate (median 22x)
   - Why it failed: the ladder: error-cost exponent 0.30 against sampling's 1
   - Rules out: the tested ARC variants (k1, k2, k2a, k3f) at the Phase-1 budget; not methods outside the hierarchy
   - Evidence: registered (the stricter prediction P4, >= 10x on every net, failed on net 200). Source: section 4.2
3. **ARC order 4 along L = n/8**
   - Tried: k4 / k4f at n = 32, 64, 128 (8 nets each), not at 256
   - Outcome: loses to MC by 20-200x at n >= 64; gain over RQMC 0.016 at 64 x 8 and 0.002 at 128 x 16
   - Why it failed: cost grows like n^{K-1} while the error improves 2-4x from order 3 to 4
   - Rules out: order 4 as implemented at n <= 128; untested at 256
   - Evidence: registered. Source: section 4.1
4. **Exact Gaussian recursion**
   - Tried: exact Gaussian moments propagated layer by layer at 256 x 32 (1,184 passes), 5 nets
   - Outcome: nMSE 1.0-2.0e-3; gain over RQMC 0.31-0.62
   - Why it failed: the error is accumulated closure error, the same as ARC's cheaper k2 (median 1.2e-3)
   - Rules out: that exact Gaussian moments fix order 2; says nothing about non-Gaussian closures
   - Evidence: registered (P10 holds). Source: section 4.2
5. **k3fa (factorised augmented order 3) at 256 x 32**
   - Tried: net 200 only (net 201 registered but not run), run after the scoring
   - Outcome: nMSE 9.5e-5 at 4.0e5 passes against k3f's 6.2e-5 at 4.9e4; gain over RQMC 0.016
   - Why it failed: not explained
   - Rules out: k3fa as a better order-3 variant at this shape, on one net
   - Evidence: registered design, one net, scored late. Source: section 4.1
6. **Radius-corrected Gaussian closure as a method**
   - Tried: finite-sample stochastic recursion, 2^19 samples of its own state per layer, rank transport in batches of 2^14, two replicates, n = 64, 128, 256 along L = n/8
   - Outcome: error 1.9e-3, 9.2e-4, 4.9e-4, but cost >= 5.2e5 passes per replicate, at least ~255x what plain MC needs for that error
   - Why it failed: it is a measurement of the closure's error, not a method; no deductive version was built and its quadrature cost J is unknown
   - Rules out: nothing as a method. A deductive version would need < ~5 order-2 steps per layer to beat MC (2-3.5 for RQMC); whether that is reachable is open.
   - Evidence: registered (P24-P28); cost comparison is arithmetic. Source: section 4.4(c)
7. **Radial recursion with a pilot-CDF radius transport (Amendment 5)**
   - Tried: radius mapped through a fresh 2^16-sample pilot CDF at every layer, 256 x 32
   - Outcome: stopped after one net: replicate noise variance 1.8e-3 (Gaussian closure: 1.7e-5); P20-P23 undetermined
   - Why it failed: the pilot's error shifts all radii coherently by ~0.1% per layer, a random walk over 32 layers
   - Rules out: that transport only; replaced by rank transport (Amendment 6)
   - Evidence: registered, run stopped. Source: section 4.4(c)
8. **Exact-mean control variates inside sampling (ANOVA and analytic controls)**
   - Tried: acceptance criterion eta < (0.40/a)(1 - B/N) applied to residual shares from prior lanes (eta ~0.5-0.7 at 256 x 32)
   - Outcome: none qualifies; best measured samplers ~2-2.5x over MC
   - Why it failed: residual share too large against the cost
   - Rules out: the shared-trajectory controls of prior lanes at 256 x 32; not new controls
   - Evidence: PROVEN arithmetic on prior-lane measurements. Source: section 6 item 3

Our own registered predictions that failed (5):

- P4: at 6.5e4 passes RQMC >= 10x below the best affordable ARC variant on 5 of 5 nets; measured 6.71, 39.8, 17.8, 34.1, 21.6 (fails on net 200)
- P7 (second clause): single-cut Gaussian defect at l = 16 >= 0.2 x k2 total; measured 0.15
- P9b: third-cumulant PR <= 4 at l >= 16 on every net; 4.05 on net 200
- P12: e_3/e_2 >= 0.2 at n = 64, 128, 256; measured 0.143 at n = 64 (the dev calibration had used k3f, not the best order-3 variant)
- P19 partial (1 of 5 nets, run stopped); P20-P23 undetermined (run stopped, noise-dominated)

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (11):

- Corrected by independent adversarial adjudication (a Fable 5.1 board agent, relayed by main): Reframed from 'ARC should update' to a benchmark plus a restricted negative; scorecard count 28 -> 29 holds; P9 on 3 of 5 nets; P14 stated as a factor 1.85 below the law at n = 128, not 'within 1.5'; early radial reductions restated (81-92% by median; 74% at l = 2 by ratio of medians); 'Theorem A' renamed a pricing identity; order-2 win stated per variant (k2a loses on net 203) (report section 9; log 2026-11-02 10:16Z, 10:24Z, 10:34Z)
- Withdrawn; own earlier claim: The radial closure's gain claim ('constant ~5/J gain') is withdrawn: it charged 393 passes to a measurement that used >= 5.2e5; replaced by its measured cost and a break-even cost. 'astra r4 proves L/n^2 order' relabelled a consistency decomposition. L/n^2 no longer called a 'floor'. (report section 9; log 10:24Z, 10:34Z)
- Withdrawn; own earlier claim: 'a precision floor min_K c_K alpha^K' was wrong (c_K >= c_* > 0 does not give a positive infimum); the conclusion is restated without it (report section 2.5 [A r3])
- Withdrawn; own earlier claim: v1 claim that future-awareness 'changes which statistics are carried, not how many' is withdrawn; no lower bound for future-aware layer-wise methods (report section 2.6)
- Corrected by GPT-6 review (gpt-6-astra, 17 findings): Negative restricted to tested methods; ARC-law argument made conditional; degree statements labelled infinite-width; oracle projections are benchmarks not ceilings; full recursions labelled finite-sample; 'neither grows polynomially' withdrawn; the k3fa claim withdrawn; RQMC comparisons below 256 points labelled extrapolations; literal scoring corrections for P1/P5 and P3 (no outcome changes) (report section 9)
- Corrected by co-prover round 2 (gpt-6-astra): FORMAL items A3, B1, B3, C2, F3 corrected and CHECK-1 narrowed; the lane author's truncated FFT had understated the mean degree (report sections 2.3, 9)
- Corrected by main's 13:29-13:50Z update: Scorecard regenerated after the last rank runs and k3fa on net 200: 29/3/4/4 became 31 hold / 4 fail / 1 partial / 4 undetermined; P9b now fails; k3fa on net 200 is worse than k3f in error and cost (report status line and section 4.1; log 13:29Z)
- Corrected by scale-mode (scale-mode-2026-11-02.md): The public 'scale-mode' counter-claim, named untested at 10:30Z, was tested at orders 2 and 3: a constant factor in a window, no escape (report status line, Summary 6)
- Corrected by scale-mode (extractor's reading; neither report flags it): Tension, not a refutation: arc-update conjectures that going below L/n^2 needs higher angular structure. The scale-mode estimator, a different Gaussian closure with one fitted scale parameter at order-2 cost, errs 6.7e-4, 6.0e-4, 3.6e-4 at n = 64, 128, 256 on the same nets, against L/n^2 = 2.0e-3, 9.8e-4, 4.9e-4. The scale-mode report notes only that it is '1.35x below arc-update's finite-sample radial closure'. (arc-update sections 4.4(c), 6 item 7; scale-mode section 5 table)
- Corrected by phase1-board (FINDINGS.md): The report reads the public board as 'best sampling-based entries do ~10-50x better than plain MC'; the later board note attributes the #1 score to fitting the public nets (INFERRED for the final run) and puts unfitted runs at ~6x MC at equal charged cost. The report text was not updated. (report sections 1, 4.2, 7 item 1; phase1-board/FINDINGS.md Verdict; log 15:33Z)
- Corrected by future-aware (section 4.5): Extends the ladder to 512 x 64: ARC K = 2 falls below RQMC (0.84x) and order 3 improves on order 2 only 2.95x. Not a contradiction, but the ladder's per-order factor is not stable in width. (future-aware-2026-11-02.md section 4.5)

Not finished: K = 4 not run at 256 x 32; k3fa on net 201 registered but not run; P20-P23 undetermined; no convergence study of the finite-sample radial recursion; the one-step-defect Gram test of the L/n^2 mechanism not run; finite-width price spectrum beyond b_0 unmeasured; scrambled positive controls for the layer-to-layer transition tests pending in other lanes; no unconditional lower bound.

Could not be determined when extracting: The status line says the update was made at 13:50Z, but the outbox file and the log entry are stamped 13:29Z; which is right I could not tell. Whether the bit counts quoted from the bit-accounting-arc lane (sections 3, 5) were later certified is outside this batch.

### scale-mode

Report: `scale-mode-2026-11-02.md` (lanes/scale-mode/). Final state: 2026-11-02 13:24Z.

Headline: Neither registered escape criterion was met: the scale-mode author's estimator is 2.5x better than RQMC at its own cost (688 passes) at 256x32, RQMC catches up at ~2.3x that cost, and its two-level exponent equals ARC's there (0.30).

Status: **negative result**. registered (45 prediction rows: 40 hold, 5 fail; decision rows D1, D2, D all fail = no escape); the scale-mode author's code run unchanged; GPT-6 reviewed (major, 9 findings; follow-up check, 6 leftovers), final text not re-reviewed; intervals are exploratory bootstraps

Failed approaches (5):

1. **Scale-mode order-2-cost estimator as an escape from the ladder (registered route D2 and the L = n/8 window)**
   - Tried: the scale-mode author's code unchanged; nets 200-204 at 256 x 32 and 8 nets per width at 32 x 4, 64 x 8, 128 x 16; against RQMC (8 scrambles) and ARC's variants; costs by ARC's counter plus 1 flop per ndtr
   - Outcome: a constant factor in a window: 2.5x RQMC at 688 passes at 256 x 32, window closes at ~2.3x its cost (~1,600 passes, 2.5% of the budget); gain over MC falls with width (exponent -0.28, CI -0.49 to -0.06); at the budget RQMC is 33-65x more accurate
   - Why it failed: its error falls only like n^-0.31 while its cost grows like n^0.59; the precision it reaches is a floor at each width (~4-7e-4)
   - Rules out: an escape at orders 2 and 3 for n <= 256 along L = n/8. Does NOT exclude higher orders (SL4 not run on these nets), larger widths, or other methods.
   - Evidence: registered. Source: sections 5, 8
2. **Scale-law order-3 level (SL3) as an escape (registered route D1)**
   - Tried: ARC's factored K = 3 with the scale removed, same nets
   - Outcome: D1 fails: two-level exponent 0.52 at n = 128 and 0.30 at n = 256 (needed >= 0.9); beats RQMC on 0 of 5 nets at 256 x 32; loses 4-20x at its own cost
   - Why it failed: SL3's error is flat in width (7-10e-5) while its cost grows like n^1.8
   - Rules out: the two-level scale-law ladder at these sizes; orders above 3 untested
   - Evidence: registered. Source: sections 5, 8
3. **Scale-mode estimator on its own diagonal L = n/4**
   - Tried: 8 fresh nets per width, 64 x 16 to 1024 x 256 (partly on a rented GPU with parity gates)
   - Outcome: D2 fails: median gain over RQMC below 1 at three of five widths (0.79, 0.73, 1.2, 0.43, 2.0); SL3 improves on it by only 5x, 1.6x, 1.8x for 34x, 76x, 179x the cost (exponent 0.45, 0.11, 0.11) and loses to RQMC by ~10-100x
   - Why it failed: not explained beyond the flat ladder; net-to-net spread ~10x
   - Rules out: 'beats sampling at every width tested' when sampling means RQMC. Does NOT settle the trend with width (undecided).
   - Evidence: registered; intervals exploratory. Source: section 6
4. **'Covariance propagation decisively beats sampling in Phase 2' (topic 18198) as a statement about raw accuracy**
   - Tried: the starter-kit baseline (= ARC K = 2 'simple') on 12 public 1024 x 16 nets with 1e9-sample truths
   - Outcome: raw MSE 4.5e-6 at 2,049 passes; full-budget RQMC (7.5e-7) beats it ~6x on every net; it wins the contest's compute-adjusted score (4.5e-7 against full-budget MC's 1.2e-6)
   - Why it failed: the contest multiplies error by the fraction of budget used (floored at 10%), which rewards cheap methods
   - Rules out: the claim as a statement about full-budget raw accuracy at order 2. It does not establish a general Phase-2 negative: order 3 beats full-budget RQMC ~19x at 1.5x the budget.
   - Evidence: registered (P8, N2). Source: section 7
5. **Scale-mode estimator at Phase 2's shape**
   - Tried: LVTV2 on the 12 public 1024 x 16 nets
   - Outcome: raw MSE 1.4e-6, worse than ARC k2a (1.1e-6) on 12 of 12 nets
   - Why it failed: as its author says; not explained further
   - Rules out: it as the best order-2 method at the wide, shallow shape
   - Evidence: registered. Source: section 7

Our own registered predictions that failed (5):

- C1 (transfer of the claim, L = n/4): beats naive MC in every cell; 0.89 at 512 x 128 (point estimate; bootstrap interval 0.57-1.63)
- C2 at 128 x 32: order-3 level below order-2 level on >= 80% of nets; 6 of 8
- C6: the claim's margin over naive MC narrows with width; measured slope +0.20 (-0.05 to +0.65), does not reproduce
- P7a: the claim's margin replicates within 2x at every diagonal width; median 4.1 at 1024 x 256 against the claimed 1.21
- P7b: median gain over RQMC < 1.5 at every diagonal width >= 256; 2.0 at 1024 x 256 (the estimator did better than predicted)

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (2):

- Corrected by GPT-6 review (gpt-6-astra, 9 findings) and follow-up check (6 leftovers): The scale-separation argument restated as a conjecture; no promotion of failed escape criteria to an asymptotic negative; the two-level exponent called steeper than ARC's at small widths; the 10% floor's direction corrected (it limits the reward for cheap methods); the link to arc-update's radial closure narrowed; 'exactly' replaced by 'to the printed precision'; extrapolated entries marked (report section 9)
- Corrected by main (log 13:29Z): Main's 13:03Z relay corrected: the Phase-2 baseline is also 6x better than RQMC at equal compute (log 2026-11-02 13:29Z)

Not finished: The order-4 scale-law level (SL4) was not run on the lane's nets; the scale-mode author's graded contest entry (a fitted engine) was not tested; the width trend against RQMC on the diagonal is undecided (more nets needed); full contest-meter pricing not done.

### future-aware

Report: `future-aware-2026-11-02.md` (lanes/future-aware/). Final state: 2026-11-02 20:05Z (Part 1 final 17:46Z; n = 512 results and review round 5 added by 20:05Z).

Headline: Negative for the future-aware extensions tested (n = 64-512): backward directions help by constant factors, the deductive member loses to RQMC 6-200x as implemented, and the hybrid is near unity (1.00-1.03x RQMC at 6.5e4 passes).

Status: **negative result**. registered Part 1 + Amendment 1 (13 rows: 8 hold and 5 fail as scored by the hashed scorers; two of the five hold after disclosed corrections); the headline hybrid score and the window ledgers are post hoc; GPT-6 reviewed in five rounds; mechanism labelled HEURISTIC; proofs by the lane author and the AI co-prover, not human-checked

Failed approaches (9):

1. **Backward-informed closure carried by particles**
   - Tried: law kept exactly in k = n/2 future directions (from vector-Jacobian products), Gaussian elsewhere, 2^18 particles, n = 64, 128, 256 along L = n/8, scored at its flop-counted cost
   - Outcome: 1.7e6-2.6e6 passes per replicate for nMSE 5.0e-5, 1.7e-5, 7.9e-6: 83x, 33x, 21x worse than plain MC; RQMC 45-250x better (RQMC extrapolated 40-120x beyond its measured range)
   - Why it failed: carrying the kept law by particles is sampling with ~6 passes of extra work per sample
   - Rules out: this particle implementation; it does not rule out a deterministic representation of the joint law in ~n/4 future directions (the stated open route)
   - Evidence: registered (P5 holds). Source: section 4.2
2. **Future-weighted cumulant truncation (ARC order 3 with the third cumulant kept only in k future directions), as implemented**
   - Tried: k = n/8, n/4, n/2 and fixed k = 16; VJP and deductive mean-field directions; n = 64, 128, 256 (and 512)
   - Outcome: 0.12x, 0.056x, 0.036x of RQMC at its cost at n = 64, 128, 256 (loses 6-200x by variant medians; 150-400x at 512)
   - Why it failed: errors stay at order-3 level (n x error does not fall: 0.034, 0.040, 0.068) while the implementation pays full order 3 plus projection and backward work
   - Rules out: this implementation. Under the registered hypothetical cost it would be a 2.4-3.0x window, which shrinks to 0.5-0.7x once the pilot and the dense direction extraction are charged; a cheaper extraction is not excluded, nor established.
   - Evidence: registered (P7 under the pre-scoring NaN rule); ledgers post hoc. Source: sections 4.2, 4.4
3. **Same truncation on half the directions (k = n/2), and on n/4 at n = 512**
   - Tried: registered runs; post hoc rank guard
   - Outcome: 8 of the k = n/2 runs returned NaN (1 of 5 succeeded at 256); with the guard 3 of the 8 rescued runs at 256 diverge or lose badly; at 512 all k = n/4 runs NaN, guard diverges on 2 of 3 nets
   - Why it failed: ARC's order-3 state covariance becomes indefinite after a few layers, so whitening a wide feature block divides by ~0
   - Rules out: the projected order 3 at large k as a usable method as implemented
   - Evidence: registered runs; guard post hoc. Source: sections 4.2, 4.5
4. **A fixed number of future directions (k = 16)**
   - Tried: benchmark and deductive member at n = 64, 128, 256
   - Outcome: benchmark gain 5.2x, 2.3x, 1.4x; retained factor 0.86, 0.46, 0.28
   - Why it failed: the future's relevance spreads over a number of directions that grows with width (top-16 share 0.80, 0.59, 0.39, 0.25)
   - Rules out: fixed-dimension future-aware sketches at these widths
   - Evidence: registered (P2 holds). Source: sections 4.1, 4.2
5. **Hybrid: future-built control variates with closure means, RQMC on the residual**
   - Tried: linear controls (exact mean Jacobian, mean-field Jacobian, least-squares) and quadratics in 16 future directions, means from the exact Gaussian recursion or ARC k2, 8 scrambles, N up to 2^16, n = 64, 128, 256
   - Outcome: near unity: 1.00-1.03x RQMC at 6.5e4 passes, 0.86-0.95x at 1e4 passes (same scrambles)
   - Why it failed: controls with exactly known means remove what scrambled Sobol already integrates; deeper controls inherit the closure's bias (7e-5 to 3e-4, above RQMC's error at 2^14 points)
   - Rules out: these control families; uncertainty was not quantified, so 'near unity' is not a measured tie
   - Evidence: registered design, scored post hoc. Source: section 4.3
6. **Independent exact one-dimensional marginals in the future directions**
   - Tried: n = 64, 8 nets, single cuts, k = 16 and 32
   - Outcome: leaves a median 0.72 of the Gaussian's error against 0.003-0.19 for the joint law; joint law better in 32 of 32 cells
   - Why it failed: most of what the future reads is dependence between the kept directions
   - Rules out: coordinate-wise marginals; oblique features or a few mixed moments untested
   - Evidence: exploratory. Source: section 5
7. **Gaussian mixture in the future directions**
   - Tried: EM-fitted mixtures at single cuts (one net per width) and as a particle recursion at n = 64 (4 nets, M = 8-32)
   - Outcome: best recovered fraction of the joint law's gain 0.78, 0.69, 0.54 at n = 64, 128, 256; as a recursion 2.8e-4 to 2e-3 where RQMC is at 1.0-1.7e-4 (3-20x worse)
   - Why it failed: no sign a fixed number of components suffices as n grows; EM fit noise confounds larger M
   - Rules out: fitted mixtures here; not what a propagated mixture could do
   - Evidence: exploratory. Source: section 5
8. **Exact-mean controls of growing complexity (asymptote route)**
   - Tried: linear plus quadratics in top-k future directions at layer 1, one net per width
   - Outcome: residual share ~k^-0.25 at n = 64 and ~k^-0.09 at n = 128; 0.55 at n = 256 with no gain over RQMC
   - Why it failed: the residual gains little on top of scrambled Sobol; the decay shrinks with width
   - Rules out: a width-uniform positive decay in this family is not established (one net per width)
   - Evidence: exploratory. Source: section 5
9. **Carrying the ladder to order 4 by truncation**
   - Tried: third and fourth cumulants projected on k future directions, n = 32 (5 nets) and n = 64 (3 nets)
   - Outcome: order-4 precision needed the third cumulant on about half the directions or more (half left 2.1-7.8x at n = 32)
   - Why it failed: the number of directions the lower-order structure needs grows with target precision (HEURISTIC)
   - Rules out: cheap truncated order 4 at these small widths
   - Evidence: exploratory. Source: section 5

Our own registered predictions that failed (5):

- P1: median future/PCA single-cut ratio <= 0.5 at >= 3 of l = 4, 8, 16, 24 at n = 256; measured 0.284, 0.0897, 0.552, 0.909 (noise-dominated at l = 16, 24)
- P7 as originally worded: every deductive variant has gain over RQMC < 0.2; fails on 8 NaN runs (holds under the NaN rule: max 0.181 over 57 runs)
- P8 as scored: fails because of a scorer name bug (holds post hoc: 2.37 <= 3)
- P11 (n = 512): no data, every k = n/4 run returned NaN (its other half holds: 2.06 < 2.34)
- P12 (n = 512): no data, same NaN failure

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (7):

- Corrected by GPT-6 review rounds 2-4 (gpt-6-astra): Hybrid score. Registered score (a sum that omitted a cross term and counted the reference error): best gain 0.8-1.0x of RQMC (medians 0.78/0.98, 0.93/0.93, 0.91/0.83 at 1e4/6.5e4 passes for n = 64/128/256; an earlier log line said 0.8-1.1). Final, scored directly against the truth on the same scrambles with the sum-based ledger: 1.00-1.03x at 6.5e4 passes and 0.86-0.95x at 1e4 passes (0.96-0.98x and 0.83-0.87x with the registered and expanded ledgers). 'Tie' replaced by 'near unity ... statistical uncertainty not quantified'. (report Summary 3, section 4.3, section 8; log 12:15Z, 15:29Z, 17:46Z)
- Corrected by GPT-6 review rounds 2-3 (gpt-6-astra): Deductive window. Earlier headline: 'best-case window ~2.4-3x' (registered hypothetical cost: 2.6, 3.0, 2.4x over RQMC at n = 64, 128, 256, up to nMSE 5.9e-4, 3.1e-4, 2.2e-4, windows ending at 0.6, 1.6, 2.8 thousand passes). Final: 1.8, 2.2, 1.75x with the separate K = 2 pilot charged; 0.5, 0.7, 0.5x with the dense per-layer direction extraction actually used; 1.3, 1.5, 1.3x only under an assumed ~2n-pass extraction whose feasibility is not established; as implemented 0.12x, 0.056x, 0.036x. 'All its work charged' withdrawn. At 512 the n/4 version fails numerically and the n/8 version gives 1.05x hypothetical, 0.74x with the pilot, 0.21x with dense extraction. (report Summary 3, sections 4.4, 4.5, 8; log 15:29Z, 17:46Z, 20:05Z)
- Corrected by own bug fix (verified in review round 5): Single-cut mixture results had a sampling bug; corrected recovery of the joint law's gain is 0.78, 0.69, 0.54 at n = 64, 128, 256 (report section 5; log 20:05Z)
- Withdrawn; own earlier theory: The coordinate-additive ('ridge') reading (FORMAL E10) is withdrawn; FORMAL E12 withdrawn and replaced by a moment-model statement; 'q <= n/L' and the old 'no unconditional extension' wording superseded (FORMAL E15) (report sections 2.3, 5, 8)
- Corrected by disclosed scoring deviations: P7 fails as originally worded (8 NaN runs) and holds under a NaN-exclusion rule written before scoring; P8 fails as scored because the hashed scorer looked up a misspelled variant name, and holds post hoc (2.37 <= 3) (report section 4, Reading the scorecard)
- Superseded by scale-mode (final 13:24Z): Section 7 still calls the public scale-mode estimator 'UNVERIFIED' with 'no RQMC comparison'; the scale-mode lane had already tested it. Stale sentence in the final. (report section 7; scale-mode-2026-11-02.md)
- Corrected by co-prover round 4 (20:06-20:24Z, after the final report): First-layer relevance participation ratio Theta(n) proven for every fixed depth for the actual gates, but open at depth proportional to width; two of the lane author's own claims (E16) are false as stated. Not in the report. (work/future-aware/FORMAL.md E17; log 20:25Z)

Not finished: No dedicated implementation of the projected order 3 (its cost is a hypothesis); no stable formulation at large k; particle and pilot convergence checked only at n = 64; widths beyond 512; mixed moments, oblique features and implicit descriptions untested; the post-report co-prover round 4 is not in the report.

Could not be determined when extracting: The summary gives the k = 128 benchmark gain as 'about 200x'; the scorecard says 204 and the results table 236x on 4 of 5 nets. All three appear in the report; I recorded each with its source.

### preint

Report: `preint-2026-11-02.md` (lanes/preint/). Final state: 2026-11-02 17:28Z.

Headline: No for pre-integration as built: it raised the fitted exponent only at input dimension 4-8 (by 0.1-0.3) and lost at equal compute at every common budget (at least 21-1,410x on the L = n/8 ladder up to 256x32). The wider question stays open.

Status: **negative result**. registered (11 tests: 7 hold, 4 fail); GPT-6 reviewed in three rounds (major, major, minor); barrier theorems by the lane author, audited and repaired by the AI co-prover, not human-checked; matched-sample-count analyses are post hoc

Failed approaches (6):

1. **Exact pre-integration along a line, then RQMC over the rest, on wide nets**
   - Tried: exact line + radius integrals on 2^p Sobol-based lines, random direction or active-subspace direction, window mode; ladder L = n/8 at n = 32, 64, 128 (3 nets each) and four 256 x 32 nets; 8 replicates; against RQMC at equal counted cost
   - Outcome: worse than RQMC at every common cost on all 13 nets: at least 21-26x (n = 32), 108-128x (64), 308-386x (128), 647-1,410x (256)
   - Why it failed: a line costs like L sqrt(n) (window) to nL (full) passes while staying worth about one point
   - Rules out: pre-integration as built at these shapes and budgets. Does NOT exclude pruned-vertex variants, other directions, or asymptotic exponent gains (matched-sample-count slopes show no consistent difference: inconclusive).
   - Evidence: registered (P3a holds 13 of 13). Source: section 4.3
2. **Pre-integration on narrow-deep nets (8 x 256) with an exact tail map**
   - Tried: lines through 48 layers then the tail map (PIJ), 6 nets, against RQMC with the same tail (RQMCJ)
   - Outcome: worse at every common cost by at least 15-91x; exponents agree within 0.3
   - Why it failed: about 1e5 activation regions over 7 angles, every quadrature cell holds many kinks; a line costs 15-36 passes against 0.2 per point
   - Rules out: PIJ at this shape; exact under the tail lane's empirical premise only
   - Evidence: registered (P5a, P5b hold). Source: section 4.2
3. **Pre-integration at tiny input dimension (n = 4, 6, 8; L = n/2)**
   - Tried: 9 nets, 16 replicates, no truths (replicate variance)
   - Outcome: exponent higher by 0.1-0.3, but 1.8-2.2x worse at n = 4, 3-7x at n = 6, 7-13x at n = 8 at the largest common budget (1e5-1e6 passes)
   - Why it failed: constants: a line costs 46-89 passes, mostly cdf and bookkeeping; the exponent gain shrinks like ~2/d
   - Rules out: a win at any budget tested; a crossover beyond the tested budgets is not excluded (extrapolated near 1e7 passes at n = 4, HEURISTIC)
   - Evidence: registered (exponents) and measured (equal-cost). Source: section 4.1
4. **Exponent of pre-integration on the wider nets**
   - Tried: registered exponent tests P3b, P3c over each curve's top-60% budget window; post hoc matched-sample-count slopes
   - Outcome: registered tests fail (they compare fits over different sample ranges); at matched counts no consistent sign
   - Why it failed: the registered comparison was flawed: pre-integration's window sits at much smaller sample counts
   - Rules out: nothing about asymptotes; not an equivalence test
   - Evidence: registered tests failed; analysis post hoc. Source: section 4.3
5. **Two-level shared-trajectory sampler (MLMC) at 8 x 256**
   - Tried: r = 32, allocation pilot charged
   - Outcome: 7-28x worse than RQMC with the exact tail at 8,192 passes; 3-33x better than pre-integration
   - Why it failed: not explained here (pilot dominates small budgets)
   - Rules out: it as the best sampler at this shape and budget
   - Evidence: registered runs (P8 on its exponents fails). Source: section 4.2
6. **Infinite-width (NNGP) proxy for the barrier's size**
   - Tried: registered check P6 of RQMC against proxy numbers on 13 nets
   - Outcome: fails on 1 of 13 (measured/bound 0.96 on one 256 x 32 net)
   - Why it failed: the co-prover showed the proxy is unreliable at L = alpha n
   - Rules out: quoting proxy-based ceilings (the earlier ~3-5.5x figure)
   - Evidence: registered (failed). Source: section 5, section 7

Our own registered predictions that failed (4):

- P3b: pre-integration's best exponent <= RQMC's + 0.15 on >= 5 of 7 nets at n >= 128; 4 of 7
- P3c: active-subspace variant steeper by > 0.1 on >= 2 of 3 nets at n = 32 and <= 1 of 3 at n = 64; got 3 and 2
- P6: RQMC N x nMSE >= the infinite-width proxy bound on all 13 nets; 12 of 13 (min ratio 0.96)
- P8: multilevel sampler exponent in [0.8, 1.2] on all nets; 11 of 19

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (4):

- Withdrawn; own earlier claim (FORMAL E1(c); relayed in log 14:14Z; listed as PROVEN in the synthesis draft, row A29): The claim that about nL evaluations (8,192 at 256 x 32) identify the net, so that information bounds for nonlinear algorithms end at N ~ nL, is WITHDRAWN: finitely many evaluations can miss an arbitrarily narrow activation cone (co-prover counterexample). What remains: the all-algorithm bound is proved only for Gaussian or scale-mixture surrogates. (report Summary 6, section 5; work/preint/FORMAL.md E5(d); log 17:05Z, 17:28Z)
- Corrected by co-prover round 2 and GPT-6 review rounds 1-3 (gpt-6-astra): Barrier narrowed. Earlier form (FORMAL v1 F7; synthesis section 3): for any rule linear in f (weighted points or line integrals) independent of the weights, E nMSE >= (c/2 - o(1))/N under an even-energy hypothesis, with infinite-width proxy numbers 0.34-0.18. Final form: three separate statements (absolute bound for N <= n/2 points or n/4 lines; relative (c/2)/N bound for point rules only under a measured, unproven spectral share; LP certificate only for line rules). F7(f) was false as stated (a signed rule on 3d - 2 nodes integrates every degree-4 harmonic exactly) and was repaired for the ensemble. The infinite-width proxy is not a safe proxy along L = alpha n. (report Summary 5, section 5; coprover/PROVENANCE.md round 2; log 14:51Z, 16:17Z)
- Withdrawn; own earlier draft: A ceiling of about 4x on what a design can gain is withdrawn; 'an outer design changes only the constant' is removed (not tested); 'escaping needs information from the weights' is removed (report section 6; review/RESPONSE.md)
- Corrected by co-prover round 2: The Gaussian all-algorithm extension needs scalar outputs or separable output covariance (it holds channel by channel, quantitative bound not derived); a kurtosis diagnostic remark was wrong (work/preint/FORMAL.md E5(c), (e))

Not finished: Vertex pruning not tried; the surrogate candidate (nested-dictionary residual test) not run; combination with structured designs not run; multilevel combination not built; the follow-up to P3b stopped after one extra budget on one net (machine load); the small nets have no truths.

### randomness

Report: `randomness-2026-11-02.md` (lanes/randomness/). Final state: 2026-11-02 ~16:20Z (status line; log and file stamp 16:12Z).

Headline: No structured sampler was shown to beat RQMC's exponent (fits 1.0-1.13 at 256x32); gains are constants (best: Kerdock 5-design, 2.9x over MC at 2^16 passes); on random weights runtime randomness is not what separates estimators.

Status: **negative result**. registered (32 predictions: 25 hold, 7 fail); GPT-6 reviewed once (7 major + 3 minor, applied; final text not re-reviewed); theorems by the lane author and the AI co-prover, the main new limit theorem only structure-checked by the lane author; no human check

Failed approaches (9):

1. **White-box gate-aligned frame (scrambled Sobol in the polar frame of the first layer)**
   - Tried: 256 x 32 nets 200-204 at 2^14 and 2^16 points; ladder at 2^14; 512 x 64 at 2^12; unbiased, O(n^3) setup not charged
   - Outcome: 1.31x better than standard RQMC at 2^14, gone at 2^16 (ratios 0.93-1.15); worse at 512 x 64 (1.68x vs 2.36x over MC); exponent difference -0.002 [-0.036, 0.032]
   - Why it failed: first-layer structure matters less as depth grows; the frame moves the constant by a few tens of percent either way
   - Rules out: this frame as a reliable constant or an exponent change at L = n/8. Does NOT cover other weight-dependent point sets (no bound proven for them).
   - Evidence: registered (PC1 fails; PW1, PW2 hold). Source: sections 4.1, 4.2, 4.6
2. **Structured weight-independent samplers as an exponent improvement**
   - Tried: scrambled Sobol, fixed Sobol, Korobov lattices, Kerdock / simplex / cross-polytope designs, N = 2^8..2^18 at 256 x 32
   - Outcome: all fitted exponents 1.0-1.13 with overlapping intervals; no randomised sampler reaches 4x over MC on any net at 2^16
   - Why it failed: the spectrum point sets fight sits in accumulated norm fluctuations; a point set acts on harmonic degrees <= 5 (proven cap on the exponent: 1.008-1.012)
   - Rules out: weight-independent positive rules as a route to a better asymptote (proven); weight-dependent structure is only conjectured not to help
   - Evidence: registered + proven. Source: sections 2, 4.1, 4.2
3. **Design aligned to the first-layer frame (Kerdock in the polar frame)**
   - Tried: randomised only by signed permutations, and fixed, at 256 x 32
   - Outcome: badly biased: nMSE x m = 54-195 (fixed: 53-204)
   - Why it failed: flat +-1/16 coordinates are atypical inputs to the first layer; signed permutations do not make the points Gaussian conditional on the weights
   - Rules out: aligned designs that are not exactly Gaussian conditional on the weights
   - Evidence: registered (PW3 holds). Source: section 4.6
4. **Bounded-independence (k-wise) designs**
   - Tried: polynomial-hash families over GF(q), k = 2, 3, 4, N = q^k, n = 32-256
   - Outcome: MC-like at their own size where resolved; pairwise design at 256 x 32 has nMSE x N 0.55-4.0 (median 1.9, worse than MC)
   - Why it failed: matching moments to degree k does not cancel the harmonic degrees of the homogeneous output; rigid algebraic structure aliases higher degrees
   - Rules out: these constructions at the resolved budgets; high-k cells mostly unresolved (k = 4 rests on 2 of 8 and 1 of 8 nets)
   - Evidence: registered (PQ3 holds). Source: section 4.5
5. **Korobov lattice rules**
   - Tried: centred or baker-transformed, generator searched by a weighted criterion, 2^14 points
   - Outcome: MC-like to 2x at 256 x 32
   - Why it failed: lattices need a periodic, smooth integrand
   - Rules out: these lattices; not all lattice constructions
   - Evidence: registered (PQ4 holds). Source: section 4.5
6. **Multilevel prefix-norm controls (shared trajectories) at L = n/8**
   - Tried: best two-level gain over radius-exact MC on the ladder, at 256 x 32 and 512 x 64
   - Outcome: 0.83, 0.86, 0.94, 0.99 at n = 32-256; 0.96-1.03 at 256 x 32; 1.00-1.07 at 512 x 64
   - Why it failed: the control's residual at the best prefix depth stays ~0.9 of the variance
   - Rules out: a multilevel gain at depth = width/8 up to n = 512; it grows only when depth reaches about the width
   - Evidence: registered (PW4 holds). Source: sections 4.3, 4.6
7. **Exact linear tail (one common tail mask) at 256 x 32**
   - Tried: 4,096 inputs per net, gates of the last two layers
   - Outcome: 16 of 4,096 inputs on one net match the majority pattern in the last layer, none in the last two
   - Why it failed: the common-tail structure of narrow-deep nets is absent
   - Rules out: one common mask; not every algebraic simplification of the tail
   - Evidence: exploratory (descriptive). Source: section 4.6
8. **First-layer controls with closed-form means**
   - Tried: regression of the output on first-layer features, one dev net
   - Outcome: explains 0.39 of the variance, nearly all harmonic degree 1 and 2, which a 2-design already cancels
   - Why it failed: redundant with what designs cancel (approximately)
   - Rules out: little: one net, HEURISTIC
   - Evidence: exploratory. Source: section 4.6
9. **Zero-random-bit fixed point sets as a free lunch**
   - Tried: centred Sobol (standard and polar frame) and unrotated Kerdock at 2^16
   - Outcome: same medians as randomised versions (2.07x, 2.68x) but 0.8x to 5.5x per net, with no error bar
   - Why it failed: a fixed set is right only on average over nets
   - Rules out: per-net reliability of fixed sets
   - Evidence: registered (PC5 holds). Source: sections 4.2, 4.7

Our own registered predictions that failed (7):

- PC1: polar-frame RQMC gain >= 2.0 on >= 4 of 5 nets and >= 1.2x standard RQMC on >= 4 of 5 at 2^16; polar 2.64, 1.83, 2.22, 2.47, 1.87 against standard 2.77, 1.97, 2.13, 2.15, 1.95
- PN2: per-layer gate surface area within [0.5, 1.3] x n/sqrt(2 pi) on every layer of every 256 net; range 0.329-1.313
- PN4: output noise-sensitivity slope within [0.4, 1.5] x n/V on every 256 net; 2.089 on one net
- PA5 (512 x 64, the co-prover's band): median share of degrees <= 2 in [0.45, 0.60]; 0.405
- PA6 (512 x 64): median odd share in [0.55, 0.59]; 0.542
- PA7 (512 x 64): simplex gain in [1.8, 2.6] and cross-polytope gain in [2.0, 2.8]; 1.71 and 2.11
- PA8 (512 x 64): n / mean V in [35, 45]; 48.4

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (2):

- Corrected by GPT-6 review (gpt-6-astra, 10 findings): 'No structured sampler beats RQMC' became 'none was shown to'; the 9.6-18.8x 'ceiling' relabelled an estimate; 'nothing reaches 4x on any net' was false for fixed point sets (5.5x, 4.4x on single nets) and corrected; zero-randomness statements qualified (existential; exact primitives); bounded-independence conclusion limited to the tested constructions; Amendment 1's 'before any evaluation result was read' is wrong; several numbers corrected; 'no full-net PRG exists' became 'none was found' (report section 8)
- Withdrawn; own first reading: The layer-state noise-sensitivity slope '~ 1 + l/2' is not the law; the annealed slope is exactly n / E V (report section 4.4)

Not finished: No statement for weight-dependent point sets; widths beyond 256 (the 3-net 512 x 64 test missed the finite-size bands); the k = 3 bounded-independence design at 256 x 32 was stopped unfinished; error bars beyond 5 nets; the proposed next step (a norm-profile control) was not started.

Could not be determined when extracting: The summary quotes Kerdock as 2.9x (2.2-3.9, against the truth at 66,048 points) and section 4.3 as 3.0x (2.4-4.7, from rotation variances); these are two measurements of the same design, both reported.

### adaptive-regions

Report: `adaptive-regions-2026-11-03.md` (lanes/adaptive-regions/). Final state: 2026-11-03 ~05Z (status line; log gives 05:19Z).

Headline: Exploratory, small nets only (depth 4, widths 4-8): exact cells win where cells are few; merging saves a constant 2-3x that does not improve with width; pattern-indexed chains stay 100x+ behind MC; learned experts show no stable gain.

Status: **negative result**. nothing preregistered (every measurement exploratory), 3 nets per width; GPT-6 reviewed twice with items still open; learned-experts results before 2 Nov 18:56Z were ruled not to count; the learned-experts part was not rerun with accurate truths; lane closed by redirection, not by conclusion

Failed approaches (9):

1. **Pattern-indexed chains (state per gate pattern)**
   - Tried: depth 4, widths 4-8, 3 nets each, 2^20 paths; states: means (order 1, order 2), means with the whole past history, one Gaussian per pattern, Gaussian mixtures (K = 8), and one Gaussian per pattern path (~20x more states than cells)
   - Outcome: errors 5e-4 to 0.2 against MC's 9.5e-7 at every width and state count
   - Why it failed: within a cell the state is a truncated linear image of a Gaussian, and which next gates open depends on the position inside the cone; the exact state is the cone itself (HEURISTIC)
   - Rules out: the tested state types at widths 4-8. Does NOT rule out other pattern-indexed representations.
   - Evidence: exploratory. Source: section D
2. **Cone tree: merging similar regions**
   - Tried: depth 4, widths 4, 5, 6, 3 nets each; cells from 2^20 advice paths with exact maps and exact first moments; greedy splits on the gate that changes the merged map most
   - Outcome: leaves needed for MC's error: 51, 167, 737 (geometric means) against 157, 468, 1,827 cells (32%, 36%, 40%); 56-100% of cells for the exact-cell error
   - Why it failed: merged maps are very similar (dispersion 3e-4 to 2e-3) but the number of groups grows as fast as the number of cells
   - Rules out: this greedy tree giving more than a constant 2-3x; other merge rules untested; the tree reduces maps, not moment computations
   - Evidence: exploratory. Source: section A
3. **Exact cells as width grows**
   - Tried: depth 4, widths 4-16, 2^20 advice paths
   - Outcome: at 6 x 4 RQMC with the same paths (5.6e-10 to 4.1e-9) beats the exact-cell estimate (1.4e-8 to 1.5e-7); at 12 x 4 the seen cells cover 74-81% of held-out paths, at 16 x 4 18-25%
   - Why it failed: cell count grows 3-4x per unit of width; unseen cells (and partly the 32-node quadrature) limit the error
   - Rules out: listing every region beyond width ~8-12 at depth 4 with a million paths
   - Evidence: exploratory. Source: sections A, B
4. **Hybrid: exact over listed cells plus sampling over the rest**
   - Tried: 4 x 4, one net, top 58 cells, 2^8-2^20 residual paths
   - Outcome: 100-1000x below MC, but RQMC on the whole input wins from 2^12 paths on
   - Why it failed: the residual indicator breaks QMC's smoothness
   - Rules out: little: one net, cell listing not charged, wider runs stopped
   - Evidence: exploratory. Source: section B
5. **Learned experts A4 (isotropic Gaussian bumps)**
   - Tried: 4 x 4 (3 nets, 1.56M advice paths, K = 4-256, trained with early stopping and a doubling check); 32 x 4 (one net, 1M advice paths, 1,200 fixed steps)
   - Outcome: 4 x 4 net 9701: 2.2e-5, 3.1e-7, 1.3e-6, 8.2e-7 at K = 4, 16, 64, 256 against MC 6.4e-7, reweighted advice 1.3e-6, RQMC 1.05e-8; doubling check moves 27-192%; at 32 x 4 held-out error rises with K above 64
   - Why it failed: smooth bumps blur cone boundaries (HEURISTIC); runs not converged; the 32 x 4 trend was judged undertraining and not rerun
   - Rules out: no stable advantage shown; an advantage is not excluded (A4 did land between MC and RQMC at single K values on two nets)
   - Evidence: exploratory. Source: section C
6. **Learned experts A5 (plain product of experts with learned variances)**
   - Tried: 4 x 4 net 9701 (1.02M advice paths, K = 4, 16, 64); 32 x 4 on a GPU (K = 16-1,024, 300 fixed steps)
   - Outcome: 4 x 4: 2.3e-3, 2.1e-3, 7.0e-4 against MC 1.0e-6; 32 x 4: N(0,I) error 0.013, 0.022, 0.046, 0.066 at K = 16-1,024 against MC 3e-8 to 9e-6; error bars miscalibrated
   - Why it failed: soft gates plus a Gaussian re-fit at every layer (HEURISTIC); cause of miscalibration not identified
   - Rules out: this model at these sizes; 4 x 4 runs on two of three nets were paused and ended
   - Evidence: exploratory. Source: section C
7. **Certified-linear backward probe**
   - Tried: exact suffix gate-pattern pieces (five 256 x 32 nets, 2^17 paths) and eps-certified pieces by own IBP and CROWN with boxes, slices and pins (nets 200-201); ladder 32 x 4, 64 x 8, 128 x 16
   - Outcome: >= 50% coverage only at the last hidden layer; one layer back the 1,000 most common exact pieces cover 0.1-7.6%; two layers back 0
   - Why it failed: 57-113 units switch at the last two layers; an unpinned switching unit costs a gap comparable to the output's RMS
   - Rules out: these particular checks. The report says they are not limits on certification.
   - Evidence: exploratory. Source: sections 3-5
8. **Step-4 experts before the 18:56Z ruling (not counted)**
   - Tried: gate-pattern composed experts at 32 x 4 to 256 x 32; oracle experts and hard-cell oracle at 32 x 4
   - Outcome: residual MSE 0.50-1.29 at the input, flat in the number of zones; oracle 1.9 down to 0.20 at K = 256
   - Why it failed: ruled not to count (wrong confidence/fusion); constructions, not ceilings
   - Rules out: nothing
   - Evidence: exploratory, withdrawn by ruling. Source: section 6; log 18:56Z
9. **Stratification by regions chosen without the weights**
   - Tried: theorem
   - Outcome: proportional gain stays below about 2 for K up to n^2/2 at every width
   - Why it failed: the averaged projection onto cellwise constants has trace at most K - 1 on each harmonic space
   - Rules out: weight-blind trees; not learned control variates or exact understanding of regions
   - Evidence: proven (lane author and AI co-prover). Source: section 2

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (6):

- Withdrawn; ruling relayed by main (log 2026-11-02 18:56Z): All learned and oracle expert estimates made before 18:56Z do not count (wrong confidence/fusion). Facts independent of fusion stand: gate-pattern counts per layer, certified-linear coverage steps 1-2, integration and additivity tests. (log 18:56Z; work/papers/arc-negative.md open question 7; report section 6 (oracle row only))
- Corrected by accounting changes (log 17:45Z, 20:41Z): Training compute made non-counting (17:45Z); headline changed to N(0,I) error against MC with the same number of training samples (20:41Z). Under it the earlier A4 K = 16 result is ~40x worse than the mean of its own training paths (4.5e-4 vs 1.2e-5). (log 17:45Z, 20:41Z; report section C)
- Corrected by main (log 16:44Z): Early step-4 numbers were pointwise residuals, not population-mean errors; main had overstated them as 'negative where it matters' (log 16:44Z)
- Corrected by GPT-6 review 1 (gpt-6-astra, 18 findings): Certification coverages are those of particular checks, not limits; 'leftover variance' is MSE; the collision rule is not a distribution-free bound; oracle and hard cells are constructions, not ceilings; A4 at K = 16 did beat the recorded MC on two held-out widths (report section 7)
- Corrected by GPT-6 review 2 (gpt-6-astra, 15 findings): The script's 'iff' for chain exactness was wrong (sufficient, not necessary); the 'agrees with Genz to 1e-9' quadrature check does not hold uniformly (one 5 x 4 net moved from 2.2e-9 to 1.3e-9 with 256 nodes); effective vs algebraic rank; collapse is sample-based, not certified; plain-MC truths and unmatched RQMC budgets in section C; A5 hold-out leakage (report sections A, C, D, 7)
- Withdrawn; own plan: The scored beta diagnostic (gain over MC against the number of regions) was cancelled by the pivot and never run (report section 1)

Not finished: Looks unfinished. The learned-experts question was paused, not concluded: no converged runs, A5 at 4 x 4 ended on two of three nets, the 32 x 4 converged rerun was not done, section C not rerun with accurate truths and matched budgets. Also: five review-1 items open (including a split-mass bug whose test fails); cone-library caches not recomputed after bug fixes; hybrid at 6 x 4 stopped; the beta diagnostic never run; the eps-certified step ran on two nets only.

Could not be determined when extracting: The report does not state the 18:56Z ruling itself (only the oracle row is marked 'not decisive'); I took the cut from the lane's step-4 log and the dated log. Whether the A4 full-bump K = 16 result (launched ~18:27Z, reported 19:00-19:13Z) counts under the ruling is not stated. The title says 2 November; the final state is 3 November.

### phase1-board

Report: `work/phase1-board/FINDINGS.md (no outbox report)` (lanes/phase1-board/). Final state: 2026-11-02 (fetches 14:41-15:25Z; file saved 15:33Z).

Headline: No: the #1 entrant's final run is 93% metered, so the cost rule does not explain it. Its score is attributed to fitting the 50 public nets (verified for runs of 5-6 Aug, inferred for the final run); unfitted runs are ~6x plain MC.

Status: **unverified**. read-only desk research by a subagent from public pages, no code run, no review; mechanism VERIFIED for earlier runs and INFERRED for the final run; would be settled only by the private re-evaluation on fresh nets

Failed approaches (1):

1. **Explaining the #1 score by the Phase-1 cost rule (cheap off-meter sampling)**
   - Tried: read the submission telemetry, the rules, the organisers' posts and the entrant's 83 graded runs; no code run
   - Outcome: the final run is 93% metered; off-meter sampling at the grader's rate would need 5.9x the budget
   - Why it failed: after 3 Aug participant code runs on one core, at or below the priced rate
   - Rules out: the cost rule as the explanation of the final-board #1 score. Does NOT exclude it for runs before 3 Aug, and does not establish the fitting explanation for the final run (INFERRED).
   - Evidence: read from public pages (verdict 1); post hoc desk research. Source: FINDINGS.md Verdict 1, Key numbers

Not finished: Not obtained: grader CPU model, the entrant's code, holdout per-net scores, attachments. Entries #2-#5 not tested for fitting. The note's own forecast (the #1 run at ~2-3e-7 raw on fresh nets) awaits the private re-evaluation (~15 Nov).

Could not be determined when extracting: Whether the private re-evaluation has been published since 2 November (not checked; read-only on these sources). Verdict 1 carries no explicit VERIFIED label in the note.

### cumulant-ambiguity

Report: `cumulant-ambiguity-2026-11-03.md` (lanes/cumulant-ambiguity/). Final state: 2026-11-03 09:21Z.

Headline: Oracle form of the conjecture is false: exact order-<=d moments of every hidden layer nearly pin the mean (PROVEN). ARC's ladder at L = n/8 matches the sum of typical per-step closure errors (MEASURED); the lower-bound theorem is open.

Status: **numerical evidence**. the intended restricted-negative theorem is OPEN (a CONJECTURE); the typical-case measurements are exploratory, 3 nets per shape, run after the two co-prover rounds and not reviewed; the bounds are proved or checked by the AI co-prover gpt-6-astra, not human-checked

Failed approaches (4):

1. **Oracle form of the conjecture (ambiguity left by exact low-order moments of every layer explains the difficulty)**
   - Tried: proof plus finite-support LPs at n = 4
   - Outcome: false: the residual ambiguity is at most a 1-D moment problem, ~1.69/d sd; LP at n = 4, L = 2, d = 2: all/input = 0.60/1.03 sd
   - Why it failed: the output mean is linear in the first moment of the last activation layer
   - Rules out: the oracle form. It does not address what a closure can compute without the true moments.
   - Evidence: proven (AI co-prover checked). Source: sections 1, 2
2. **Worst-case closure ambiguity as the source of ARC's error**
   - Tried: exact first-step spread; propagated LP at n = 4; comparison with ARC's nMSE along L = n/8
   - Outcome: true but vacuous: ~1 sd over depth at n = 4 against ARC's actual 0.01-0.03 sd (14-30x smaller)
   - Why it failed: real nets are far from the worst case; the bound is law-agnostic and does not hold under the Gaussian promise
   - Rules out: a negative built on this framing
   - Evidence: proven spread; measured comparison. Source: section 3
3. **Amplification of mis-propagated higher cumulants as the cause of the ladder at L = n/8**
   - Tried: cut experiment: start ARC's recursion from true cumulants at layer c, 32 x 4 to 128 x 16, 3 nets
   - Outcome: recursion = 1.0-2.2x the per-step sum at L = n/8; amplification (5-300x) only at L/n >= 1/4
   - Why it failed: the errors add incoherently at this depth ratio
   - Rules out: amplification as the mechanism at L = n/8 on these small shapes
   - Evidence: exploratory. Source: section 4
4. **Maximum-entropy closure at order 4**
   - Tried: 1-D reduction, same nets
   - Outcome: 2-3x worse than the Edgeworth closure
   - Why it failed: not explained
   - Rules out: max-ent as a better order-4 local rule here
   - Evidence: exploratory. Source: section 4

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (3):

- Withdrawn; own interim hypothesis (log 2026-11-03 03:46Z): 'Ladder slowness comes from higher-cumulant closure errors in early layers amplified downstream' was refuted at L = n/8 by the cut experiment: the recursion error is about the incoherent sum of per-step errors; amplification appears only at L/n >= 1/4 (log 09:11Z; report section 4)
- Corrected by co-prover round 1 (gpt-6-astra): The blanket parity claim is false; 'strictly' more informative is false in general; 1.4/d is a small-order fit (the constant is 1.686); an LP support bug and a wrong zero in the 1-D code were found (fixed; runs before the fix are marked) (work/cumulant-ambiguity/review/review_r1_answer.md; report Files)
- Corrected by co-prover round 2 (gpt-6-astra): The lane's numerical constants for the first-step spread were wrong (exact values 0.856, 0.362); 'unavoidable error' wording false (minimax error is half the spread, and neither is a bound at the Gaussian law); a universal bound prop <= C x input is false; the proposed causal conclusion from worst-case ambiguity is false (work/cumulant-ambiguity/review/review_r2_answer.md)

Not finished: The Gaussian-promise lower bound is the open theorem. The 64 x 8 order-4 cut was pending when the report was saved; run files in the work dir were written at 09:47Z, after the report, and are not in it. The 1-D sweep to n = 256 was not run. Two discrepancies with ARC's ladder are 'not explained' (the 2->3 ratio rising with width; ARC's order-4 rung ~4x the per-step sum).

Could not be determined when extracting: Whether 'numerical evidence' or 'unverified' is the better label: the proved parts were AI-checked, the measured headline was not reviewed. Whether the late order-4 cut changes anything (not read into a report).

### moment-matching

Report: `moment-matching-2026-11-03.md` (lanes/moment-matching/). Final state: 2026-11-03 11:37Z.

Headline: Matching Gaussian input moments to degree d leaves E f undetermined by at least 0.21 sd at every degree run (n = 4-8, depth 1-8, d up to 8); the gap falls roughly like 1/d (extrapolated: d ~20-60 for 10% of sd).

Status: **unverified**. exploratory and unreviewed; 3 nets per shape (one net at n = 6, d = 6); highest-degree runs stopped early so those values are lower bounds; the report is a 19-line note saved by main from the lane's message

Failed approaches (1):

1. **Pinning the mean by input moments alone**
   - Tried: LP over a growing point set for the range of E f over input laws matching all Gaussian moments up to degree d; bias-free random ReLU nets n = 4, 6, 8, L = 1-8, d = 2-8, 3 nets
   - Outcome: gap/sd (medians) e.g. n = 4, L = 4: 1.18, 0.63, 0.45, 0.30 at d = 2, 4, 6, 8; n = 8, L = 8: 2.60, 1.58 at d = 2, 4; never below 0.21
   - Why it failed: not explained beyond the 1-D ReLU moment problem; odd degrees add almost nothing
   - Rules out: estimators whose only information about the input is its moments to degree <= 8 on these tiny nets, in the worst case over the ambiguity set. Does NOT give a lower bound for an estimator that knows the input is Gaussian, nor for layer-wise statistics.
   - Evidence: exploratory. Source: report table and bullets

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (1):

- Corrected by cumulant-ambiguity (cumulant-ambiguity-2026-11-03.md): Context, not a retraction: this is the input-only class. The cumulant lane's co-prover notes that an input-moment gap is a worst case over all laws in the ambiguity set and 'does not establish an error lower bound when inputs are promised to be Gaussian'; with layer-wise oracle statistics the mean is nearly pinned. (log 2026-11-03 11:37Z; work/cumulant-ambiguity/review/review_r1_answer.md, claim 3)

Not finished: Highest-degree runs were stopped early; n = 6 has d = 6 on one net only; n = 8 stops at d = 4; nothing at realistic widths.

Could not be determined when extracting: What the parity control was expected to show at d = n (the note only says it 'does not drop').

### nd-exact

Report: `nd-exact-2026-11-02.md` (lanes/nd-exact/). Final state: 2026-11-02 (report states no time; dated log marks it final at 05:55Z).

Headline: Not with the exact methods built: the certified cell code is 23-106x worse than RQMC (0 of 6 nets pass) and an integrate-and-drop region code loses to the best sampler by 7-1,222x even at an assumed 9 mv per region.

Status: **negative result**. registered (T1, T2 fail 0 of 6; T4 holds 6 of 6); three gpt-6-astra review rounds (major, major, minor), last four minor edits not re-reviewed; about the methods tested, explicitly not an impossibility proof

Failed approaches (5):

1. **Certified deterministic cell code (CS2) in Kelvin's framing: classes = input cones with exact Gaussian mass and mean, gates certified constant by interval arithmetic, exact composed linear maps, certified tail merge at layer 32, surplus-driven refinement**
   - Tried: Plain He-ReLU, width 8, depth 256, sigma = 0; 6 evaluation nets (203, 216, 217, 220, 221, 223); 2^16 to 2^26 mv, up to 445,000 open leaf cells; against RQMC and RQMCJ at equal nominal FLOPs; also CS2b (child mass floor) and post-hoc CS2c (root floor)
   - Outcome: At its best point 23-106x worse than RQMC and 108-910x worse than RQMCJ (T1, T2: 0 of 6). Certified cells: 9 cells with 5.8e-6 of the probability on net 220, none on the other five. 3.6-8.5 bits per halving of error (CS2c 3.3-4.3) against 2 for MC and 1.3-2.1 for RQMC/RQMCJ. CS2c at 2^26 mv is still 6,000-30,000x RQMCJ's error
   - Why it failed: The regions are thin in 7 angular dimensions (median distance to the nearest boundary 0.0034-0.0063 at depth 32); cells that resolve that scale isotropically would number 10^16 to 10^18 (HEURISTIC). The code fails already on one layer at width 8
   - Rules out: This cell code at 8 x 256 at every precision measured (nMSE 0.3 to 1e-7), and on single layers from width 4. Does NOT rule out cells shaped to the regions, or 'a way to integrate a union of regions without resolving it, which is the original problem'.
   - Evidence: registered (T1, T2, T1b, T2b); CS2c and the one-layer study post hoc. Source: sections 6, 7, 10, 11
2. **Integrate regions exactly, largest first, and drop the rest**
   - Tried: Regions of layers 1..32 ranked on a sample of 2^22 inputs, top R integrated at an assumed 9 mv each, dropped part measured on a held-out 2^22 sample; R from 2^10 to all regions found (125k-221k)
   - Outcome: At every resolved R the dropped part leaves 7-1,222x RQMCJ's error at cost 9R mv (by net: 143-600, 13-211, 7-93, 11-25, 80-1,222, 30-622). The held-out curve floors where the sample's regions run out (1-2% of fresh inputs land in unseen regions). Against plain MC the same accounting wins 2.5-14x on four nets
   - Why it failed: Coverage, not entropy: a long tail of rare regions
   - Rules out: This one strategy even at an optimistic cost (true cone moments need 7- and 8-dimensional orthant integrals). Does NOT cover approximating the remainder, integrating unions of regions, or sharing work between regions; not a lower bound.
   - Evidence: registered (T4 holds 6 of 6). Source: section 5
3. **Unbiased version: cell code as a control, RQMC correction of the within-cell residual**
   - Tried: Base estimate at 2^20 mv plus 2^12 to 2^16 scrambled-Sobol correction points, 8 replicates; post-hoc paired ablation with 32 replicates per (net, M)
   - Outcome: Ratio to RQMCJ 0.21-1.35 (T5 fails 0 of 6). Without the cells the estimated error is lower in all 18 comparisons (1.6-3.3x at 2^16 points; paired intervals exclude zero in 10 of 18) and 2^20 mv is saved
   - Why it failed: Untested hypothesis in the report: the residual jumps at every cell boundary, and RQMC integrates jumps worse than the kinks of f itself
   - Rules out: These cells as a control variate under RQMC on these nets (under plain MC they do halve the variance).
   - Evidence: registered (T5); ablation post hoc. Source: section 9
4. **Fixed unscrambled Sobol point set (deterministic, no random numbers) with the sampler's tail map**
   - Tried: N = 2^6 to 2^16 on all six nets against 64 scramblings of the same rule (66 cells)
   - Outcome: Beats RQMCJ's mean error in 42 of 66 cells and its median in 32; share of scrambled runs better than it averages 0.51 (0.25 to 0.69 by net); error moves by up to 1,100x between neighbouring budgets; no error estimate
   - Why it failed: Not explained (inconsistent across nets and budgets)
   - Rules out: Reading it as a systematic gain or as equivalent to sampling. It is deterministic but not exact, and in the earlier lanes' definition not sample-free.
   - Evidence: post hoc (the reviewer's baseline). Source: section 8
5. **The same cell code on one ReLU layer at widths 4-8**
   - Tried: One layer (closed-form mean) at widths 2, 3, 4, 6, 8, against RQMC at equal cost
   - Outcome: Exact at width 2; 92-170x better than RQMC at width 3; RQMC/code = 0.0034-0.0038 at width 4, 6e-5 at width 6, 2e-5 at width 8; certified mass 0.66-0.67 at width 4 and 0.00 at widths 6 and 8
   - Why it failed: Angular dimension: the crossover sits between 2 and 3 angular dimensions
   - Rules out: The cell code from width 4 even on one layer. Deep nets at width 2-3 were not tested.
   - Evidence: post hoc. Source: section 7

Our own registered predictions that failed (1):

- T6: predicted the unbiased version would NOT beat full-depth RQMC by 3x on 4 of 6 nets; it did on 5 of 6 (ratios 2.75-13.7). The post-hoc ablation traces the gain to the truncated tail, not the cells

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (2):

- Corrected by gpt-6-astra review rounds 1-3 (work/nd-exact/review/): Round 1 (critical): a deterministic baseline was missing; a fixed Sobol rule beat RQMCJ at N = 4096 on four nets; section 8 added. T4 rephrased from a bound to one strategy under an assumed cost. The tail identity rests on a sampled premise. 'Certified' and 'exact' are numerical. The distance argument is a rough model, not a necessary condition. Amendment 1 did not fix root cells. Certification covered a negligible mass, not none (9 cells on net 220). The cost ledger is nominal; an unsupported 'under 10%' was removed. Round 2 rejected the author's first reading of the Sobol baseline ('one RQMC run with the randomness fixed', 'ties sampling'); now 'competitive but inconsistent'. The ablation 'supports, rather than settles' that the cells add nothing. Round 3: four minor items. (report section 12)
- Corrected by the lane's own deviations log (work/nd-exact/logs/deviations.txt, 04:45Z): A root face cell whose centroid output is zero got priority zero and was never split, in CS2, CS2b and the unbiased version's base estimate, on nets 203 and 217. Registered results are kept as scored; the post-hoc CS2c fixes it (6.7x better final error on 203, 3.7x on 217); registered verdicts unchanged. (report section 6; logs/deviations.txt item 1)

Not finished: Exact integration along lines (pre-integration) was not tried here; the dated log shows a later lane (preint, final 2 Nov 17:28Z) testing it at 8 x 256 and losing to RQMCJ by 15-716x. Deep nets at width 2-3 not tested. Region count for 99.9% of the mass unresolved. The boundary-jump mechanism is an untested hypothesis. A method that integrates a union of regions without resolving it remains open.

### unrestricted

Report: `unrestricted-estimators-2026-10-31.md` (lanes/unrestricted/). Final state: 2026-10-31 (final after GPT-6 review B, 14:15Z-14:21Z; dated log marks it final at 14:28Z).

Headline: The certified branch-and-bound fails as a deductive method (its bounds-only estimate never beats RQMC, best ratio 0.18); determinism is no restriction on random weights; plain MC is not optimal at depth (a multilevel sampler beats it).

Status: **negative result**. branch-and-bound negative is registered and GPT-6-reviewed twice (both 'major revision'; final text not re-reviewed). Theory is largely by the AI co-prover gpt-6-astra; the multilevel-sampler gain is PROVEN UNDER cost hypotheses with its two key inequalities not checked by the lane author; its measured gains are post hoc and optimistic. Nothing human-checked

Failed approaches (8):

1. **Certified branch-and-bound over input cones (exact on certified-stable cells, symbolic linear bounds elsewhere, gap-driven refinement), centre-point estimate**
   - Tried: 72 census nets (3 healthy seeds per configuration), widths 3, 4, 6, 8, 16, 32, depths 4-64, 126 net-arm runs, up to 2^22-2^23 forward passes, against scrambled-Sobol radius-exact RQMC and radius-exact MC at equal FLOPs
   - Outcome: Width 3: parity at 1e6-4e6 passes (both near nMSE 1e-12), resolved wins of 3.8-18x in 4 of 24 runs, all at depth 16-32; under a 2x cost change one of five stays above 3x. Width 4: 33x-2e5x worse than RQMC. Widths 6-8: 10^4-10^6x worse than RQMC and 10^3-10^4x worse than radius-exact MC. Widths 16-32: accuracy of 2-30 MC samples after 4e6 passes, 10^5-10^6x behind RQMC. Passes to nMSE 1e-4 grow about 10x per unit of width
   - Why it failed: Cells must resolve the kink geometry in n - 1 dimensions and a cell costs 46-170 forward passes; symbolic bounds through unstable units compound with depth
   - Rules out: This family beyond width 3 at the sizes run; reaching 10M+ parameters is ruled out only by extrapolation (HEURISTIC, 'no large model was run'). The width-3 wins concern the noiseless mean only. Does not rule out all partition methods (the report keeps that as conjecture C2).
   - Evidence: registered (P2, P3, P6, P8 hit; P4 hit under a substituted rule; P1 refuted). Source: sections 2.2, 2.3, 6
2. **Deductive estimate proper: midpoint of the certified bounds, and the certificate itself**
   - Tried: Same runs
   - Outcome: Best resolved ratio to RQMC over all runs and budgets 0.18 (width 3, depth 8); median nMSE 0.5 to 4e34 at widths 6-32; no cell ever certified exact at widths >= 6; certificate nMSE about 1 at depth 4 growing to 1e16-1e34 at depth 32-64
   - Why it failed: Vacuous bounds wherever units stay unstable on a cell
   - Rules out: This bound-propagation certificate as a deductive estimator beyond width 3.
   - Evidence: registered (P5 hit); midpoint statistics post hoc. Source: sections 2.2, 2.3
3. **Fixed deterministic designs (centred unscrambled Sobol, spherical 2-designs) as a route to a growing gain**
   - Tried: Deterministic Sobol against scrambled Sobol on 54 nets of widths 3-8 at N = 2^10, 2^14, 2^18; harmonic profile on 3 nets per width at L = n/4 up to width 256; astra's positive-design bound
   - Outcome: Deterministic Sobol was 2.7-4.5x better than scrambled, but it is sampling at fixed points. The heuristic 2-design ceiling falls from about 7 (width 16) to about 2 (widths 64-256), 1.7 at 256 x 32; positive-weight designs are capped near 4x in the mean-field limit
   - Why it failed: The gain of a design is capped by the low-degree content of the net's angular function, which falls as width and depth grow together
   - Rules out: A width-growing gain from positive-weight designs with polynomially many points, in the infinite-width mean-field limit (at finite width this is conjecture C3). The plug-in caps are not bounds.
   - Evidence: proven in the mean-field limit [A]; measurements registered (M2; P11 refuted on its second clause) and post hoc. Source: sections 2.2, 3.5, 5
4. **Polynomials of low degree in the weights as estimators**
   - Tried: Noise-stability measurement on 48 net pairs per configuration at n = 32 (and 16), L = 4, 16, 32
   - Outcome: Plug-in ceilings at n = 32: degree 4 worth at most about 2.3 (L = 16) and 1.2 (L = 32) MC samples; degree 8 about 14.5 and 5.7; at n = 16, L >= 16 the estimates are unresolved
   - Why it failed: The mean's Hermite degree grows with depth (finite-difference proxies about 2, 7, 17 at depths 4, 16, 32)
   - Rules out: Low-degree weight polynomials as competitive estimators at depth 16-32, as estimates only ('These are estimates, not established bounds').
   - Evidence: registered measurement (M1; P10a refuted, P10c valid only in part); post-hoc normalisation. Source: section 3.5, section 6
5. **Methods that integrate selected first-layer gate cells exactly and drop the rest**
   - Tried: Theory (astra): mass covered by any K first-layer cells chosen after reading the weights
   - Outcome: Expected mass at most sqrt(K kappa_n) with kappa_n exponentially small; such a method has risk of order n at L = alpha n for polynomial K
   - Why it failed: Exponentially little mass per cell
   - Rules out: Select-and-drop methods on first-layer cells. The partition bounds are 'upper bounds, not limits on all partition methods'.
   - Evidence: proven [A] (AI co-prover; review A lists 'selected-cell mass/error bounds' among arguments that survive). Source: section 3.5
6. **The lane's own optimality conjecture C0 (plain radius-exact MC is optimal up to a constant at depth proportional to width)**
   - Tried: Red-team by the co-prover; post-hoc numerical check of the counterexample sampler on 4 fresh nets per cell
   - Outcome: False under the stated cost hypotheses; estimated ideal gains of the counterexample 1.5x at L = n = 128 up to 15x at 8 x 256, break-even at L <= n/4
   - Why it failed: Input directions merge with depth, so late layers can be shared through one reference trajectory
   - Rules out: 'Nothing beats plain MC' statements. Does NOT show the sampler beats RQMC, nor that it gains at ARC's 256 x 32 (1.01).
   - Evidence: proven under hypotheses [A]; measurements post hoc. Source: sections 3.7, 5
7. **An unrestricted impossibility proof, and transfer of hardness from known problems (threshold-circuit derandomisation, convex-body volume, spin glasses)**
   - Tried: Analysis with the co-prover
   - Outcome: No proof in reach: it would be a super-linear time lower bound for an explicit problem; worst-case barriers do not reach random weights; the interpolation route needs a polynomial estimand; analogies give 'no transfer'
   - Why it failed: On random weights determinism is free in the idealised model, and ARC's mean is the additive, infinite-temperature end that sampling already reaches
   - Rules out: Using these known results as evidence of average-case hardness for ARC's mean. The 'no technique' statement is HEURISTIC.
   - Evidence: proven (logical) in parts; HEURISTIC; several literature facts from memory. Source: sections 3.3, 3.4, 4
8. **Full dyadic multilevel version and the multilevel sampler at ARC's shape**
   - Tried: Post-hoc measurement, 4 nets per cell
   - Outcome: The full dyadic version is worse than two levels at these sizes (1.1-2.2 variance-times-cost ratio at L <= n, i.e. a loss); at L <= n/4 the two-level ratio is 0.91-1.29, 1.01 at 256 x 32
   - Why it failed: A direction-mismatch term of order n / L^2 keeps the gain near 1 at L <= n/4
   - Rules out: A practical gain from this sampler at ARC's 256 x 32.
   - Evidence: post hoc. Source: section 3.7, section 8

Our own registered predictions that failed (8):

- P1 refuted: at width 3, depth 4-8, B&B beats RQMC by >= 3x on 0 of 6 nets (predicted >= 4 of 6)
- P7 refuted: deterministic-Sobol / scrambled-Sobol nMSE 0.30, 0.22, 0.37, outside the predicted band [1/3, 3]; its rationale was wrong
- P10a refuted: noise-stability slope 0.84-1.00 (predicted 0.5-0.8)
- P11 refuted on its second clause: the median 2-design ceiling fell from 7.0 to 2.2 (factor 3.2; predicted < 2x)
- P12 refuted: (kappa_L'')^-1/2 is not concave from L = 9 (predicted concave at every depth)
- P13 refuted: region counts at width 3 do not grow with depth (medians 22, 23, 18, 15; predicted log-log slope 1-3)
- P4 could not be scored under the registered rule (RQMC run only to 2^20 at widths 16-32); hit only under a substituted rule
- P10c 'hit as registered' but one cell (n = 16, L = 16) is not valid evidence

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (4):

- Corrected by gpt-6-astra co-prover round 3, red-team of C0 (same lane; coprover/astra_r3_answer.md): C0, as made precise after review A, claimed that for fixed alpha every uniform estimator family of cost T_n at L = alpha n has risk at least c V_sph / m(T_n), i.e. nothing beats radius-exact MC with the best allowed batching by more than a constant. It is false: a multilevel sampler sharing the late layers through one reference trajectory has gain Omega(n / log^2 n) (PROVEN UNDER layerwise cost hypotheses that schoolbook costs satisfy). It was replaced by C0*: same model and window, but the baseline is the best multilevel reference-trajectory sampler B*(T), and the claim is that no uniform estimator family beats B* by a factor growing polynomially in n. C0* is a CONJECTURE 'with little evidence'; the report notes 'the multilevel sampler itself shows how unsafe such conjectures are'. (report sections 3.7 and 5; coprover/PROVENANCE.md round 3; overnight-report-2026-10-29.md 31 Oct 12:41Z)
- Corrected by gpt-6-astra co-prover round 2 (audit of theory v1 and lib/bnb.py): Nine corrections accepted: the Chebyshev remark was wrong; the partition-rate exponent in v1 was wrong; 'deterministic = all algorithms' lacked a simulation argument (repaired by the author); 'not provable' relabelled HEURISTIC; spin-glass hypotheses; the certificate does not enclose the quadrature error and certifies the bound midpoint, not the point estimate; two FLOP undercounts (at most a factor 2); P7's rationale was wrong. (report section 7; coprover/PROVENANCE.md round 2)
- Corrected by GPT-6 review A (sections 1, 3-5; 'major revision', 16 findings): The deterministic simulation is now PROVEN UNDER its primitives and noted impossible with finitely many bits; the digit-seed result is restricted to Gaussian weights; the threshold-circuit match was withdrawn (n free bits are too few); mean-field agreement figures corrected (5% only at L = 4; -21% to +29% deeper); degree-D numbers called plug-in estimates; the spin-glass condition fails at depth 9, about a Gaussian surrogate only; analogy verdicts softened to 'no transfer established'; one [C+A] provenance tag corrected. (report section 7; review/review_gpt6_A.md)
- Corrected by GPT-6 review B (whole report; 'major revision', 11 findings): The summary called the method deductive while the tables showed the centre-point (sampling) estimate; the deductive midpoint never beats RQMC. The 4.1x design cap at 256 x 32 was a plug-in estimate, not a bound. P3 and P4 were scored with dropped or substituted budgets, now declared. Multilevel figures are estimated ideal gains with prefix selection on the same data. The reusable allocator could exceed its budget (fixed). Several ranges corrected. (report section 7; review/review_gpt6_B.md)

Not finished: A fully charged run of the multilevel sampler (pilot and allocation included) against RQMC; the noisy case sigma = 1e-3; finite-precision derandomisation; the 2/3 law (C1) at finite width; the design kernel test (C3) at width 256; spin-glass depths 3, 5, 7 and the algorithmic threshold for tails; RQMC beyond 2^20 at widths 16-32. Listed as next steps: a control for the first layers' amplitude variation, several reference trajectories, RQMC within levels.

Could not be determined when extracting: The multilevel sampler's gain at L = n is quoted differently across lanes (here, post hoc: 1.06, 1.12, 1.5 at n = 32, 64, 128; input-bits Part 2: 1.29, 1.60, 1.87 at n = 64, 128, 256; bits-bounds as quoted in synthesis-draft-2026-11-02.md item A36: 1.21, 1.41, 1.58, 2.43 at n = 32-256). Nets and estimators differ and all are ideal or pilot-based; I did not reconcile them. The author's model is given in coprover/PROVENANCE.md as Claude Opus 5.5 on 31 October, so the 9-10 November rule does not apply.

### narrow-deep

Report: `narrow-deep-2026-10-29.md` (lanes/narrow-deep/). Final state: 2026-10-30 (sections 1-9: runs ended 01:04Z on 30 Oct; section 10 follow-up ran 01:14Z-02:18Z on 30 Oct; the report states no finalisation time).

Headline: Plain narrow-deep nets synchronise, so only the first ~n ln(1/tol) layers are hard; on random residual nets a sample-free Gaussian closure beats the samplers tried only at 18-35 paths' cost; it fails on trained nets. No M1/M3 advance.

Status: **numerical evidence**. MEASURED on 1-64 nets per result; the residual-closure headline is exploratory (only its depth scaling, P10, was registered, and after the first residual results); one GPT-6 review of sections 1-9 ('major revision') and one of section 10 ('revise'), revised text not re-reviewed; section 10 is a registered refutation; the report's own M1/M3 verdict is 'no major advance'

Failed approaches (10):

1. **Gate-free bound on the relevant directions from the weights alone (unmasked product W_L...W_{c+1}; random Bernoulli(1/2) masks)**
   - Tried: Plain He-ReLU nets, n=8 and 16, L=64 and 256, sigma=1e-3, 4 nets per configuration, k=1 direction at cuts 4-128; 1,024 random mask sequences; score = share of sensitivity tr M captured
   - Outcome: lin and rand capture 4-28% (chance is 6% at n=16) against 52-93% for the optimum; random-mask top directions spread over 7 of 8 and 13 of 16 dimensions; the largest of 1,024 random-mask gains exceeds the real paths' median gain by e^5 to e^14; product of operator norms is e^30 to e^260 above
   - Why it failed: A real path's masks are tied to its own state (ReLU(W h) = D W h with D chosen so the result is nonnegative); random masks drop that tie and most of their sequences are not realisable (report's interpretation)
   - Rules out: These two natural constructions on random plain nets. Does NOT rule out every weight-derived construction (report: 'This does not prove that no weight-derived construction can work'). Exception found: in the noise-trained RNN a random-mask average of W_hh captures 96-100% of the single relevant direction.
   - Evidence: registered (P5: miss as worded on tr S, hit on the Amendment-1 score tr M); numbers changed after a post-review code fix. Source: sections 2.4, 4.2, 6
2. **K2 Gaussian closure from the input on plain narrow-deep nets**
   - Tried: Plain nets n=16, L=256 (4 nets) and n=8, sigma=1e-3; also a variance-only closure
   - Outcome: nMSE 0.016-1.0 at n=16 and 2-27 at n=8 (1.2e7 on a net whose output is mostly noise); dropping correlations gives 16-218
   - Why it failed: The collapsed state is close to a ray with widely spread radius; a Gaussian with the same mean and covariance puts mass at negative radius
   - Rules out: A single Gaussian closure through the shallow, pre-synchronisation block of plain nets. Does not rule out other sample-free descriptions of that block.
   - Evidence: registered (P8 hit). Source: section 3.2
3. **Explicit enumeration of activation cells for the shallow block of plain nets**
   - Tried: Count of distinct joint gate histories among 2^20 inputs, n=8 (sigma=0) and n=16
   - Outcome: n=8: 77,000-82,000 at layer 8 and 90,000-116,000 from layer 16 (about half seen once, so the true count is higher); n=16: about 1,000,000 by layer 8; each cell also needs a Gaussian integral over a polyhedral cone in 8-16 dimensions
   - Why it failed: Too many cells before synchronisation stops further splitting
   - Rules out: Naive cell-by-cell enumeration. The report says it 'is not a lower bound for every exact method: distinct histories can share a map or be aggregated'.
   - Evidence: exploratory (MEASURED). Source: section 3.2
4. **Hybrid: Monte Carlo through the shallow layers, deterministic deep part per radius bin**
   - Tried: Plain n=16, L=256, seed 0 only (one net), budgets 256-16,384 paths; and residual nets
   - Outcome: Plain: 2-4x over the best simple sampler at 256-1,024 paths, 1.6x at 4,096, nothing at 16,384 (deep-part bias about 1e-5). Residual: HYB loses to RQMC by 10-100x at every budget (bias 4e-5 to 1e-4 for HYB-st, 0.05-0.4 for HYB-lin)
   - Why it failed: Plain: the deep-part bias shows at large budgets. Residual: without synchronisation the radius-binned deep part is biased
   - Rules out: A growing or large-budget gain from this hybrid on the nets tested (one plain net). Does not rule out hybrids with an unbiased deep part.
   - Evidence: registered (P7: hit against MC at 256-4,096 paths, miss at 16,384); the comparison with the best sampler is on one net. Source: sections 3.1, 3.2
5. **Sample-free K2 closure on random residual nets at larger budgets**
   - Tried: Residual 1/sqrt(L) nets, n=8 and 16, L=16-1024, 24 nets; K2-Stein and exact-moment K2 against RQMC up to 16,384 paths
   - Outcome: K2's error is a bias floor of nMSE 2e-5 to 4e-4; RQMC matches it at about 100-1,000 paths and reaches 1e-7 to 1e-6 at 16,384; exact-moment K2 costs 15-23x more for the same accuracy, so it only ties RQMC at n=16 and loses 2-4x at n=8
   - Why it failed: The closure error is a bias, not variance (no refinement parameter)
   - Rules out: K2 matching sampling beyond about 100-1,000 paths' compute on these nets. Does not rule out a closure whose bias vanishes (K >= 3 or mixtures), which the coordinator declined to test on random residual nets.
   - Evidence: exploratory (MEASURED). Source: section 3.1, section 5
6. **Gaussian-closure tail probabilities (M3)**
   - Tried: P(\|output\| > t) at the 1e-3 and 1e-4 quantiles from K2's output Gaussian (Imhof), random nets n=8 and 16; four trained nets in section 10
   - Outcome: Random nets: 3-77x too small at n=16, 400-60,000x too small at n=8. Trained nets: wrong by 40-900x on three of four
   - Why it failed: The non-Gaussian, roughly quadratic part of the map makes the true tails heavier (random nets)
   - Rules out: Gaussian-closure tails as tail estimates or bounds on these nets; nothing here is a certified bound.
   - Evidence: registered in part (Part 2 P15 partial: miss on the noisy RNN, 24-31% low); otherwise exploratory. Source: sections 3.3, 10.1, 10.4
7. **K2 / K2-Stein closure on trained narrow-deep nets**
   - Tried: Six trained nets (plain sorter L=16, residual sorters L=64 at sigma 0 and 0.01, RNNs T=32 and T=64), best seed per configuration
   - Outcome: Floor of nMSE 0.013-0.22; within 2x of plain MC at K2-Stein's own budget of 23-45 paths (up to 5x worse on the noise-trained RNN); 110-1,800x worse than the best sampler at 1,024 paths
   - Why it failed: Not isolated in sections 1-9 ('consistent with' a non-Gaussian, partially sorted state); section 10 finds the error spread over layers in the sorters and made at the last steps or over the whole run in the RNNs
   - Rules out: The Gaussian closure as an estimator on these trained nets beyond its own tiny budget.
   - Evidence: registered (P9: 'K2 loses to MC' hit). Source: sections 4.3, 10.1
8. **Gate-aligned Gaussian-mixture closure: split at the k worst-gate units**
   - Tried: Four trained nets (residual sorters width 16 depth 64, RNNs width 16 T=64, sigma 0 and 0.01); k = 1, 2, 4, 8 splits chosen by accumulated error (S1), one-step error (S2) or at random (S0); exact and Stein-linearised moments; scored against a 2^21-path truth and against RQMC at equal FLOPs; after review an oracle with exactly conditioned pieces
   - Outcome: Best gain over the same closure without splits 1.13x (random splits 0.92-1.08x) against a 3x criterion; at equal FLOPs every closure loses to RQMC, by >= 93x with exact moments and 4-51x with Stein moments at k=1-2; oracle: at most 1.13x on the RNNs at any layer, at most 1.6x over K2 at sorter layers 2-8, up to 10.5x at sorter layer 48 but only on top of exact moments up to there
   - Why it failed: HEURISTIC in the report: in the sorters the gate error is spread over hundreds of (layer, unit) pairs; in the RNNs the worst-gate units sit at the first steps and correcting those does not remove the output error
   - Rules out: Gaussian-plus-few-splits closures on these four nets: sequential re-Gaussianising splits at k <= 8, and (not pre-registered) exactly conditioned single-layer splits on the RNNs and early sorter layers. The report says 'It is not a proof against all closures'; late sorter layers do carry useful gate structure.
   - Evidence: registered (PREREG Part 2, P13 hit: refuted as predicted); oracle post hoc. Source: section 10.2, 10.4, 10.5
9. **Training plain (no skip) width-16 MLPs at depth 64 on sorting**
   - Tried: Plain He-ReLU width 16, L=64, Adam, 2^15 steps, 2 seeds plus one
   - Outcome: nMSE 0.81 and 1.14 (predicting the mean scores 1); one run diverged (2e18); the residual sorter at L=16 also misses the 0.05 criterion (0.07-0.09)
   - Why it failed: The failed net is synchronised like a random one (gate disagreement 0.000 from layer 16; output depends almost only on \|x\|)
   - Rules out: This recipe only ('In these recipes'); consistent with the literature finding no trained plain net of width <= 16 and depth >= 64.
   - Evidence: registered (trainability prediction hit). Source: sections 4.1, 4.2
10. **Exact radius integration (positive homogeneity) for task-relevant tail events on trained nets**
   - Tried: Four trained nets, events: large sorting error and RNN confident wrong answer, q = 1e-3 and 1e-4, 2^20 directions, 2^22-path truth
   - Outcome: Variance gain over MC 2.9-3.8x (sorting error) and 1.5-1.8x (RNN margin); the 310,000-390,000x gain for \|output\| on sorters is called trivial (a sorter nearly preserves the norm)
   - Why it failed: These events depend mostly on the input's direction, which the estimator still samples
   - Rules out: Large gains from radius integration alone on task-relevant tails. It remains a better estimator for norm-like events; not a certified bound.
   - Evidence: registered (P16 partial; miss for the RNN margin, 1.8x against a predicted 3x). Source: section 10.3, 10.4

Our own registered predictions that failed (11):

- P3 partial: mean k*_F(M) after synchronisation is 2.5-4.5 (n=16) and 2.8-3.8 (n=8), above the predicted 3 at 7 of 13 cuts; single nets reach 8
- P4 (second clause) miss: residual N_surv(e^-1) falls to ~0.35 n at L' >= 192 (predicted >= n/2 at every L')
- P5 miss as worded: on tr S every candidate captures nearly everything where the state is one-dimensional
- P6 miss on the 3 near-dead nets; the sigma = 0 arm was not run
- P7 miss at 16,384 paths (1.6x; predicted >= 0.5 L/l0)
- P9 miss for RNNs: gates settle to 3-7% disagreement (predicted >= 10%)
- Trainability: T = 32 >= 50% missed (38-40%); 'T = 64 below T = 32' missed (best 44% vs 40%)
- Part 2 P12: worst 4 units carry 46.8% (< 50%) of accumulated gate error on the noisy RNN
- Part 2 P14 partial: Stein closures at k = 1-2 lose to RQMC by only 4-8x on three nets (predicted >= 30x)
- Part 2 P15 partial: the noisy RNN's closure tail is only 24-31% low (predicted wrong by > 2x on every net)
- Part 2 P16 partial: RB gain for the RNN margin is 1.8x (predicted >= 3x); sorting error 2.3-2.9x at q = 1e-3

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (4):

- Corrected by narrow-deep section 10 (same report, added 30 Oct 01:14Z-02:18Z, PREREG Part 2): Sections 1-9 ended by proposing, as the concrete next step, a closure with K >= 3 or Gaussian mixtures split along the few non-quadratic directions, and said of the trained-net failure 'we did not isolate it'. Section 10 tested the trained-net version (gate splits at k <= 8 worst units, plus an exactly conditioned oracle) and refuted it (best 1.13x against the 3x criterion; loses to RQMC at equal FLOPs by >= 93x with exact moments). It also added trained-net tails (K2 wrong by 40-900x on 3 of 4 nets) and changed section 5 and Summary items 7-8 to say the failure is spread out and gate splits do not fix it. No number in sections 1-9 was retracted by it. (narrow-deep-2026-10-29.md Summary items 7-8, section 5, section 10; overnight-report-2026-10-29.md 30 Oct 02:22Z)
- Corrected by GPT-6 review of sections 1-9 (work/narrow-deep/review/review_gpt6.md, 'major revision'): Earlier draft claims replaced: (1) the sensitivity matrix M excluded paths that had once died (83-99% of the sensitivity on two n=8 nets); fixed, every plain run redone, n=8 k*_F(M) rose to 2.8-3.8 and the avg/att captures fell. (2) 'No gate-free bound exists' narrowed to the constructions tested. (3) gap_1 used inconsistent conditioning; recomputed, and the n=8 'excess' rate disappeared. (4) random-mask participation ratio counted zero products: n=8 PR is 6.9-7.0, not 2.2-3.8. (5) worst-case gain evidence had used an upper bound as a lower bound. (6) 'one trajectory's gates' narrowed. (7) the radius-integration check had claimed 2% agreement; one point is 12.6% apart. (8) Euler's identity does not identify the top input direction. (9) prereg scoring: P3 now partial, P5 restated. (10) two table values were mistranscribed; '0.4% of paths die at n=16' was the prediction, not the measurement. (report section 8)
- Corrected by GPT-6 review of section 10 (work/narrow-deep/review/review_gpt6_r2.raw, 'revise before finalizing'): The split closure re-Gaussianises each piece, so the result refutes that implementation, not accurately conditioned gate mixtures (oracle added; it extends the refutation for the RNNs and early sorter layers and shows late sorter layers carry useful gate structure). 'Early errors do not matter' was too strong. The radius-integration column for noisy nets was variance, not MSE. The largest RQMC ratios are unresolved, not lower bounds. Budgets count propagation only and gate selection uses a sampled oracle. (report section 10.6)
- Corrected by narrow-deep-m1 (narrow-deep-m1-2026-10-30.md): This lane's hybrid and its binned K2-Stein deep part did not carry over to fresh width-8, depth-256 nets: 'The previous lane's binned K2-Stein deep part (inside HYB) diverges on 4 of 6 evaluation nets (nMSE 5 to 1e4)'; HYB floors at 1.4e-3 on net 203 and works only on net 221. This qualifies Summary item 5 (deep part reaches 1e-7 to 2e-5, measured as a paired oracle on five healthy nets, hybrid on one n=16 net). (narrow-deep-m1-2026-10-30.md sections 4 and 5)

Not finished: Second plain-net seed for the sampler comparison dropped for time; sigma = 0 arm of P6 not run; MLP at L = 128 stopped to free the GPU; truths used 2^20-2^22 paths, not the registered 2^24; near-dead plain nets not checked for the radius-integration estimator; the noisy RNN's Imhof tails at q = 1e-4 failed numerically, so its other configurations' tails are not validated; 'We did not test why small late-step errors matter so much for the output'; a bias-free closure (K >= 3 or mixtures) on random residual nets was proposed and declined by the coordinator, so it is untested.

Could not be determined when extracting: Report section 8 lists 20 review items; the review file has 24 numbered findings and the dated log says '24 findings addressed'. I did not map them one to one. Whether the lyapunov lane's Theorem C (basis of every PROVEN item here) was reviewed is outside this batch.

### narrow-deep-m1

Report: `narrow-deep-m1-2026-10-30.md` (lanes/narrow-deep-m1/). Final state: 2026-10-31 about 01:55Z (runs from 22:25Z on 30 Oct to about 01:55Z on 31 Oct).

Headline: No major advance: the two-sided and the backward-only sample-free estimators each beat RQMC by 3x on only 2 of 6 healthy nets, through cancellations or a closure that happens to land close; the registered M1 tests (P5) fail.

Status: **negative result**. registered (P5 'not met', as predicted); gpt-6-astra reviewed twice (major revision, then minor revision); round-2 edits not re-reviewed; the report calls its limits 'floors of the methods we built, not proven lower bounds'

Failed approaches (8):

1. **Two-sided sample-free estimator (TS): forward description to a cut at layer 2, 4 or 8, deterministic noiseless downstream**
   - Tried: Plain He-ReLU, width 8, depth 256, sigma = 1e-3; 6 healthy evaluation nets (seeds 203, 216, 217, 220, 221, 223); forward = gate-pattern Gaussian mixture (tau 1e-3, 1e-4) or exact-moment Gaussian closure K2X; scored against RQMC at equal FLOPs with a 2^24-path truth
   - Outcome: Typical nMSE 1e-3 to 1e-2. Beats RQMC by >= 3x at some ladder point on 2 of 6 nets (217: K2X 54x at 28 paths, mixture 7.4x, 5.1x, 3.1x; 221: K2X 10x at 32 paths); on the other four the best point is 2.3x or below and RQMC is 1.2-5,000x better at most ladder points
   - Why it failed: Forward descriptions are poor beyond cut 2; the cut-2 meet has no accurate deterministic integration rule (needs 4-8 directions); the noise effect (5e-5 to 5e-3) is omitted. The wins are cancellations of opposite-sign biases or a fixed closure that lands close on that net; no rule picks the winning configuration in advance
   - Rules out: These TS constructions as an M1 estimator at width 8. Does NOT prove a lower bound; a single removed floor 'would not bring these arms to RQMC beyond about 2^11 paths on most nets' is the report's reading of its own methods.
   - Evidence: registered (P5(a), P5(b) not met, as predicted). Source: sections 5, 9, 10
2. **Backward-only estimator (BO): radius exact, deterministic product rule over k directions at the input**
   - Tried: Same 6 nets; k = 2-6 directions, m = 4-16 points per angle; reviewer refined the k = 4 rule to m = 32 and 64
   - Outcome: Beats RQMC >= 3x on 2 of 6 nets (220: 10x at 335 paths; 221: 14x at 228 paths), 0.16-1.7x elsewhere. Both wins are at coarse rules: refining raises the error on 221 from 9e-5 to 6.4e-3 and on 220 from 8e-5 to 3e-4
   - Why it failed: The value function needs 6-7 of 8 input directions under this rule; the rule's error is as large as the projection error and changes sign with m; the noise effect is omitted
   - Rules out: This quadrature at the input as an M1 estimator at width 8 (the report notes BO sits close to QMC, and that cost is exponential in n under its rule, HEURISTIC). Not a lower bound.
   - Evidence: registered (P9 hit: BO wins on at most 2 of 6). Source: sections 5, 8, 10
3. **ARC's cumulant propagation (kprop) carried to layers 5-8 at width 8**
   - Tried: K = 2 simple and augmented, K = 3 factorized and factorized augmented, K = 4 factorized, on 4 nets; errors on E[a_c] and two oracle meets (Gaussian, and the registered polynomial meet)
   - Outcome: Exact at layer 1; 3e-5 to 2.3e-2 at layer 2; augmented variants and K = 3 diverge from layers 3-5, up to 2.2e4 by layer 8; K = 4 factorized is 0.2-2.8 by layer 8. The registered polynomial meet extrapolates badly (e.g. 290 where the Gaussian meet scores 3.8e-4)
   - Why it failed: ARC's power counting is in 1/n, which is not small at n = 8 (K = 2's layer-2 error is 2-20x smaller at n = 16 and 32)
   - Rules out: ARC's method as the forward half beyond layer 2 at width 8. Says nothing against ARC's result at width 256.
   - Evidence: registered (P1 first clause hit; second clause only diagnostic support). Source: section 3, section 10
4. **Gate-pattern Gaussian mixture (GHM) as forward description**
   - Tried: 1.9k to 60k Gaussian components (tau 1e-3 to 1e-4), split one unit at a time, re-Gaussianised, Stein moments for straddling units; cuts 2, 4, 8
   - Outcome: Floors at 1e-3 to 1e-2 on E[a_c]; 30x more components change the error by at most 2x; starting from empirical layer-1 piece moments still leaves 5e-4 at layer 2 and 7e-3 to 1e-2 at layer 8
   - Why it failed: Review-narrowed: Stein cross-covariances instead of exact ReLU covariances, forced gates leaving negative post-ReLU means, pruning that stops splitting, besides the Gaussian piece shapes; the test does not separate these causes
   - Rules out: This implemented approximation. Does not rule out exact gate-pattern pieces (only a naive cost estimate, HEURISTIC, was made for those).
   - Evidence: registered ladder; cause analysis post hoc. Source: section 3
5. **Grid of the value function V_8 on a few directions with multilinear interpolation**
   - Tried: Dev net 103; k = 2-6 directions, 8-32 points per dimension, several box sizes, radius exact
   - Outcome: Errors 2.5e-5 to 1.9 depending on the grid
   - Why it failed: V_8's linear pieces have kinks that defeat the interpolation
   - Rules out: This interpolation scheme (replaced by direct noiseless passes, Amendment 2).
   - Evidence: exploratory (dev net). Source: section 4
6. **Deterministic treatments of the per-layer noise in the deep part**
   - Tried: Dev net 103: K2-Stein and exact-bivariate K2 tables from point masses; a Gaussian-sum filter (coordinator's suggestion); the previous lane's binned K2-Stein deep part on the evaluation nets
   - Outcome: K2-Stein gives relative effects 204 and 9.2 where MC gives 64 and 2.0 (exact moments worse: 255 and 11.5); as tables they made the deep part 1,000-5,000x worse on three of four dev nets. Gaussian-sum filter: 1.8-3.6x off at small radii, costs 6.9e4-4.9e5 paths, leaves 1.3e-4 to 2.4e-4. Binned K2-Stein diverges on 4 of 6 evaluation nets
   - Why it failed: For small-radius paths the noise dominates outright; the tables are proxies whose residuals mix several approximations (report)
   - Rules out: These three treatments; consequently every deterministic arm here is noiseless downstream and inherits a bias of nMSE 5e-5 to 5e-3.
   - Evidence: exploratory (dev net); P3 and P10 registered around it. Source: section 4
7. **Sampling layers 1-8 with RQMC, deterministic downstream (SH)**
   - Tried: 6 nets, 2^9 to 2^17 paths
   - Outcome: 4.6-6.2x over RQMC at 2^9 on nets 203 and 221; at most 2.0x at 2^11; behind on every net by 2^13 (0.003x-0.35x)
   - Why it failed: It plateaus at the omitted noise effect
   - Rules out: This hybrid beyond small budgets. It is not sample-free in any case.
   - Evidence: registered (P6 miss). Source: section 5, section 10
8. **Deterministic arms on secondary nets (dead-noise net, sigma = 1e-2, intermediate net)**
   - Tried: Net 200 (dead-noise), nets 203 and 216 at sigma = 1e-2, net 202 (intermediate)
   - Outcome: Dead-noise: every deterministic arm returns exactly 0 (nMSE 4.3e-3, equal to MC at about 230 paths). sigma = 1e-2: every deterministic arm loses (noise effect 7e-3 and 0.56). Net 202: BO's 66x at a coarse rule disappears when the rule is refined
   - Why it failed: The noiseless net carries no signal on dead nets; at sigma = 1e-2 the omitted noise dominates
   - Rules out: The noiseless-downstream design outside the healthy, small-noise case.
   - Evidence: registered as descriptive (P8, no pass/fail). Source: section 7

Our own registered predictions that failed (5):

- P3 miss: the noiseless downstream on the exact law at c = 8 is off 5.5e-5 to 5.1e-3 on all 6 nets (predicted 1e-5 with k <= 5 at <= 1,000 paths on >= 5 of 6)
- P4: diagnostics oppose the prediction (the best forward description at cut 2 is within 10x of RQMC or better on all 4 nets; predicted >= 10x worse on >= 5 of 6); formal equal-compute condition not established
- P6 miss: SH at most 1.97x in 2^11-2^17 (predicted >= 3x on >= 4 of 6)
- P10 second clause missed on net 217: TS wins 3.1x at 15,391 paths (cancellation-assisted)
- P1 second clause only diagnostic support (nominal downstream cost), not a completed equal-compute test

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (2):

- Corrected by gpt-6-astra review round 1 (work/narrow-deep-m1/review/review_gpt6.raw, 'major revision'): Earlier draft claims replaced: (1) a 330x TS win on net 217 violated the registered truth-resolution rule (nMSE 9e-8 < 6e-7) and is now 'unresolved, not claimed'; 'its neighbours lose' was false. (2) 'The wins are cancellations' went too far: K2X's win on 221 is not a cancellation. (3) 'Every error is one signed scalar' was false. (4) The direction oracle used C^1/2 V where it should use C^-1/2 V; fixed and rerun on all 6 nets, counts at cuts 1-5 dropped by 1-3. (5) The direction count had been switched to a 'stable' criterion after registration; the registered statistic is now reported. (6) The mixture's floor is attributed to this implementation, not to piece shape. (7) 'Every operation is charged' was false. (8) P1 and P4 had been scored with an unregistered Gaussian meet; 'P4 holds at cuts 4-8' was removed. (9) The exact-piece cost is a naive estimate, not a bound. (report section 12)
- Corrected by gpt-6-astra review round 2 (review_gpt6_r2.raw, 'minor revision'): Removed the universal line 'RQMC wins above 2^13'; P1, P3 and P4 are now scored as diagnostics rather than completed tests, P9 as an endpoint comparison, P10 under a stated pointwise reading (second clause missed on 217); the registered polynomial meet beats the nominal comparator on 3 nets, not 1; K2X's win on 217 noted as cancellation-assisted; K2X's losses at c = 2 (10-31x) added. (report section 12)

Not finished: Estimator scaling arm with width not run (conditional on P5(a)); k = 24 at n = 32 not run; kprop's x1.3 cost sensitivity not run; forward study on 4 of the 6 nets; RQMC replicates 8 and 2 at 2^17 and 2^20 instead of the registered 16 and 4; 'Shared computation, adaptive integration and other representations were not examined' for exact pieces. Later lanes on the same nets: nd-exact (exact methods, sigma = 0) and unrestricted section 3.7 (multilevel sampler, estimated 15x over radius-exact MC at 8 x 256, noiseless, not compared with RQMC).

### arc-noisy

Report: `arc-noisy-deep-2026-10-29.md` (lanes/arc-noisy/). Final state: 2026-10-29 ~14:05Z (Part 1 final 04:56Z, Part 2 complete 10:07Z, Part 3 complete 12:12Z, Part 3b scored 13:55Z and checked 13:57Z; file mtime 14:05Z).

Headline: No win at depth 32 at sigma<=0.003 (means or tails). Depth 8: a kprop+Kerdock hybrid gains 1.04-1.76x over the better entry; a saddlepoint readout of ARC's augmented K=3 puts +0.32 more 1e-8 events within 50% (fresh nets).

Status: **negative result**. mixed lane, chosen by the depth-32 headline (the lane's target shape): depth 32 negative; depth-8 and tail wins are registered numerical evidence. GPT-6 (Codex) code and claims reviews per part; text edited after each last review was not re-reviewed; no human check.

Failed approaches (21):

1. **Exact Gaussian closure (full bivariate-normal ReLU moments instead of ARC's truncated expansion)**
   - Tried: 256-wide He-ReLU dev nets, sigma 0.001, nMSE at depth 8, 16, 32 against kprop K=2
   - Outcome: 1.63e-4 vs 1.63e-4 at depth 8; 7.6e-4 vs 6.2e-4 at depth 32: no gain
   - Why it failed: not explained beyond 'no gain' (closure errors at depth are 69-84% orthogonal to the mean direction)
   - Rules out: This closure as an improvement on K=2. Does not exclude other closures.
   - Evidence: exploratory (development nets, before PREREG). Source: Part 1 section 4
2. **C1 recursive moment control (Gaussian closure with non-Gaussian corrections from particles of the true net)**
   - Tried: depths 8 and 32; 2^10-2^14 iid particles; Kerdock particles; dev net 100
   - Outcome: layer 1 is 30x below MC, but 2-3x over MC on the same particles at depth 8 (below the Kerdock sampler once its extra cost is counted), no gain at depth 32, none on Kerdock particles
   - Why it failed: correction noise and covariance bias accumulate with depth
   - Rules out: This control scheme at depth. Killed before PREREG, so not a registered test.
   - Evidence: exploratory (killed before PREREG). Source: Part 1 sections 4 and 7
3. **C2 homogeneous scale-mixture closure (carry the norm mode as an exact scale)**
   - Tried: dev nets, depth 32, sigma 0.001
   - Outcome: 9% better than our Gaussian closure but 11% worse than K=2 at depth 32
   - Why it failed: closure errors at depth are 69-84% orthogonal to the mean direction, so fixing the scale does not fix them
   - Rules out: Scale as the main source of closure error at 256 x 32.
   - Evidence: exploratory (killed by the >= 2x rule, seen before PREREG). Source: Part 1 sections 4 and 7
4. **C3 mode-cumulant closure (Edgeworth readout with cumulants from the top-k covariance modes)**
   - Tried: one-step readout with true moments at layers 16 and 31, 3 dev nets; gate >= 5x with k <= 8
   - Outcome: top-8 modes give 1.9-4.1x; per-neuron cumulants of the next pre-activations give 19-120x. Failed the gate; not built
   - Why it failed: the missing information is per-neuron and fourth-order, not in the collapse modes
   - Rules out: Low-mode cumulant closures with k <= 8. Carrying per-neuron cumulants by ARC's K=4 costs about 1e14 FLOPs (a cost for that algorithm, not a lower bound).
   - Evidence: registered gate, oracle test on 3 dev nets. Source: Part 1 sections 4, 5, 7
5. **Neuron/copula code at depth**
   - Tried: layer 24 replaced by empirical per-neuron marginals (2^18 paths) with Gaussian dependence, then the real layers; dev net
   - Outcome: nMSE 2.3e-4 at depth 32, no better than a Gaussian with the true moments (2.1e-4)
   - Why it failed: the depth-32 means depend on non-Gaussian dependence at intermediate layers
   - Rules out: Marginals + Gaussian copula at a cut (for the replacements tested); 'not every possible description'.
   - Evidence: exploratory oracle. Source: Part 1 sections 4 and 5
6. **Meet in the middle, sample-free side (Gaussian description up to layer m, exact network after)**
   - Tried: Gaussian with the true mean and covariance at m = 8, 16, 24, then real layers (2^20 paths), 3 dev nets
   - Outcome: nMSE 8.0e-5 to 5.0e-4 at depth 32, 12-75x the Kerdock sampler's error at the Phase-1 budget
   - Why it failed: non-Gaussian joint structure at intermediate layers
   - Rules out: Gaussian replacements at those layers; not every description.
   - Evidence: exploratory oracle. Source: Part 1 sections 4 and 5
7. **H1 / C4: Kerdock sampler + linear control at layer m with a kprop mean**
   - Tried: 24 evaluation nets, depth 32, sigma 0.001, measured equal budgets 5e10-3e11, factorized K=3 mean at m = 4..24
   - Outcome: 0.03-0.9x of the Kerdock sampler at every m (oracle with exact layer-m mean: 1.6-2.0x at m = 16, 4.1-5.5x at m = 24). Killed. Depth 8: 1.07-1.13x at three budgets, 0.34-0.95x elsewhere, below H2 everywhere
   - Why it failed: the bias of ARC's K3f mean at layer m turns the control into a loss; a control mean would need about 1e-6 accuracy at depth >= 16
   - Rules out: Linear controls fed by ARC's closures at depth 32. Does not exclude controls with a better mid-depth description (that is ARC's open problem).
   - Evidence: registered (kill test: >= 1.5x with CI above 1). Source: Part 1 sections 4, 5, 7
8. **H2 hybrid at depth 32, primary noise levels**
   - Tried: 24 evaluation nets, sigma 0.001 and 0.003, 1e9-3e11 FLOPs
   - Outcome: 0.84-1.06x of the Kerdock sampler; predicted gain at 1e9-5e9 not significant
   - Why it failed: kprop's depth-32 error (2.2e-4 for K3f at 2.06e11 FLOPs) is far above the sampler's
   - Rules out: Output-level combination of kprop and a sampler at depth 32 at sigma <= 0.003.
   - Evidence: registered. Source: Part 1 sections 4, 6, 7
9. **C6 antithetic noise on the Kerdock design at sigma <= 0.03**
   - Tried: 24 evaluation nets, sigma 0.01 and 0.03, depths 8 and 32
   - Outcome: 0.47-0.88x (a loss)
   - Why it failed: noise is under 30% of the output variance at those levels
   - Rules out: Using the noise as a variance-reduction resource at low noise.
   - Evidence: registered (amendment 1). Source: Part 1 sections 3, 4, 7
10. **Monte Carlo with the last noise integrated per neuron**
   - Tried: 24 evaluation nets, sigma <= 0.01
   - Outcome: 1-3% worse than plain MC
   - Why it failed: its readout costs more than the variance it removes
   - Rules out: Last-layer Rao-Blackwellisation as a gain at low noise.
   - Evidence: registered (C5 prediction). Source: Part 1 sections 3 and 7
11. **Two-level sampling over depth with a sampled coarse level**
   - Tried: modelled cost x variance for three splits (m = 8, 16, 24) from measured G(m)
   - Outcome: 39.6, 46.2, 47.4 against 32 for one level: worse
   - Why it failed: the coarse level carries most of the variance at m/32 of the cost
   - Rules out: Only these three modelled splits under their assumptions; with a free exact coarse expectation the gain would be G (reviewer). Not a rejection of multilevel sampling.
   - Evidence: modelled arithmetic, corrected after review. Source: Part 1 section 5 item 3; section 8
12. **U4: Gaussian importance sampling over x fitted to splitting particles in the event**
   - Tried: depth 4, 1e-8, dev nets 102-105, 0/3/10 expanded directions
   - Outcome: median relative variance per sample 656-3,650 (bar 100). Killed
   - Why it failed: working hypothesis (not established): the conditional law given the event spreads over many input directions
   - Rules out: These Gaussian input proposals at depth 4. Not every backward function.
   - Evidence: registered kill test. Source: Part 2 P2.2, P2.6
13. **U5: layer-wise twisted SMC (prior x, noise twisted)**
   - Tried: noise-leverage diagnostic r on dev nets 102-103 at every (depth, sigma)
   - Outcome: per-net median r 0.46-1.1 (bar 0.1); single events as low as 0.10. Killed
   - Why it failed: at sigma <= 0.01 the event is decided mostly by x, so twisting the noise has little leverage
   - Rules out: Typical gains for estimators that keep prior input draws at low noise; no uniform bound; the SMC itself was not run.
   - Evidence: registered kill test (diagnostic only). Source: Part 2 P2.2, P2.6
14. **U1: splitting on the top mode of the last hidden layer (one run for all outputs)**
   - Tried: depth 32, 20 evaluation nets, three sigma
   - Outcome: passed its kill test 17/32 only through near-zero estimates; no evaluation win under both reach rules; one run within 50% for 49% of events at 1e-4, 13% at 1e-8, 3% at 1e-12
   - Why it failed: helps only outputs aligned with the top mode
   - Rules out: Top-mode splitting as an all-outputs tail estimator at depth 32.
   - Evidence: registered (amendment 3). Source: Part 2 P2.2, P2.3, P2.6
15. **U2: saddlepoint readout of ARC's plain K=3 description (depth 8 bar)**
   - Tried: kill test on dev nets 102-105; confirmatory on 20 fresh nets 24-43, depths 4 and 8
   - Outcome: +0.12 (kill) and +0.14 (confirmatory) at depth 8, 1e-8, against a +0.20 bar; depth 4 met it (+0.47, +0.24)
   - Why it failed: Part 3 exploration: ARC's plain K3f keeps only a radial fourth-order component (excess-kurtosis correlation 0.21 with MC at depth 8)
   - Rules out: A claim at the registered effect size at depth 8. Does not exclude a smaller real gain (positive pointwise CIs at every level).
   - Evidence: registered (kill test and confirmatory test both failed). Source: Part 2 P2.2, P2.5, P2.10
16. **U3 (MC moments + saddlepoint) per event and at depth 32**
   - Tried: 20 evaluation nets, 2^20-2^22 paths
   - Outcome: per event 0.009-0.065x of splitting at depth 4 (loses everywhere); at depth 32 within 50% for 56% at 1e-4 and under 20% below; no win
   - Why it failed: 2^20 paths cost more than one splitting run; consistent with information lost by a four-moment description at depth 32 (not isolated)
   - Rules out: U3 without output/threshold sharing, and at depth 32.
   - Evidence: registered. Source: Part 2 P2.3, P2.6
17. **Kerdock design and plain Monte Carlo for tails beyond 1e-4; MC moments + Edgeworth (ARC's baseline)**
   - Tried: 20 evaluation nets, depths 4/8/32
   - Outcome: Kerdock 'never' at 1e-6 (0.23-0.26 reach); Edgeworth within 50% for 57% at 1e-6 and 22% at 1e-8 at depth 4
   - Why it failed: not explained (samplers run out of samples; Edgeworth behaves like ARC's Hermite expansion)
   - Rules out: These baselines in the deep tail at the tested budgets.
   - Evidence: registered competitors. Source: Part 2 P2.3
18. **Any moment-based deductive readout at depth 32 (ARC's heaviside on K3f and K3fa, our chi-mixture saddlepoint on K3fa and on K3f)**
   - Tried: 20 evaluation nets, sigma 0.001, part 2 truths
   - Outcome: none beats zero at any level; ours 0.356 within 50% at 1e-4 (median error 0.79 [0.67, 1.00]); on plain K3f 0.13 with fallbacks for 72% of events
   - Why it failed: four-moment approximations remain inaccurate for many depth-32 events; not isolated whether better moments would rescue it
   - Rules out: The moment-based readouts tested. Does NOT exclude non-moment families (boundary-aware, backward from the event), which were not tested; sigma 0.003/0.01 and depth 16 not run.
   - Evidence: registered (Part 3b primary 1 failed). Source: Part 3b
19. **Normal-inverse-Gaussian fit to four cumulants (and its chi mixture); RAD3 (no fourth cumulant); higher moments from ARC's K3f**
   - Tried: dev nets 100-101, depth 8
   - Outcome: NIG 0.25-0.30 within 50% at 1e-8 (saddlepoint 0.33-0.55); dropping the fourth cumulant under 0.05; K3f implies k5 = 0 and an artifact k6
   - Why it failed: not explained
   - Rules out: These alternative four-moment readouts on two dev nets.
   - Evidence: exploratory. Source: Part 3 P3.1; LEDGER item 23
20. **Elliptical-slice moves in splitting; directional (radial) Rao-Blackwellisation**
   - Tried: exploration before the tails prereg
   - Outcome: ESS worse per evaluation than tuned pCN; radial share of a 1e-12 event is only about e^2 in 256 dimensions
   - Why it failed: as stated in outcome
   - Rules out: nothing beyond these two tries
   - Evidence: exploratory (LEDGER only, not in the report). Source: work/arc-noisy/LEDGER.md item 21
21. **Noise extrapolation of kprop at depth 32**
   - Tried: reviewer's affordable sigma pairs on evaluation nets
   - Outcome: no tested depth-32 pair passed (+4% at depth 8 only)
   - Why it failed: not explained
   - Rules out: Only the pairs the reviewer tried; family is listed as open and untested by the author.
   - Evidence: exploratory (reviewer, not pre-registered). Source: Part 1 section 4; review_claims.md finding 2

Our own registered predictions that failed (9):

- C4/H1: predicted best m gives 1.1-1.4x at depth 32; result 0.03-0.9x at every m (Part 1 section 7).
- H2: predicted 1.0-1.2x at 2.72e11-3e11 at depth 8; 3e11 gave 0.97-0.99x. Predicted > 1 at depth 32 for 1e9-5e9; not significant (0.94-1.06x point estimates).
- C6: predicted 0.9-1.2x at sigma 0.03 (got 0.88x) and about 1.0x at depth 8, sigma 0.1 (got 1.29x); depth-32 sigma 0.1 predicted 2-5x, got 2.11x (lower end).
- Tails: 'U2 passes its kill test; sample-free win at L = 4 and 8' was wrong (failed at L = 8, +0.12 vs +0.20).
- Tails: ARC's K3f predicted better than zero to about 1e-6 at L = 8; only 1e-4.
- Tails: 'U1 fails its kill test' was wrong by the written rule (17/32).
- Tails: splitting B50 at 1e-12, L = 32 predicted about 1e12; 4.2e12.
- Confirmatory (P2.10): joint +0.20 primary failed (depth 8 +0.14); U2 better than zero at depth 8 predicted to 1e-10, reached 1e-8.
- Part 3b primary 1 (readout beats zero at depth 32, 1e-4) failed: 0.79 [0.67, 1.00].

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (11):

- Corrected by GPT-6 claims review of Part 1 (arc-noisy-review-2026-10-29/review_claims.md, finding 1): Earlier depth-32 headline 'no win up to sigma 0.03' was false: H2 wins by 1-6% at sigma 0.03 and 2% at sigma 0.01 (6.8e10). Headline restricted to the primary noise levels and the wins reported. (report Part 1 section 8; progress log 04:39-04:56Z)
- Corrected by GPT-6 claims review of Part 1, finding 2: The author's arithmetic rejection of noise extrapolation was 'not a test'; reviewer's exploratory check found +4% at depth 8. Family relabelled untested/open. (report Part 1 sections 4 and 8)
- Corrected by GPT-6 code review of Part 1 (review_code.md, 11 findings, 2 high): Kerdock rotation setup was undercharged at small budgets and H1's equal-cost comparison was a 1/N rescaling, not a measurement. Fixed: sampler v2 with 48 measured checkpoints, per-block setup, OLS fit charged, exact ARC-counter closure costs, sigma=0 forwarding bug. (report Part 1 section 8; progress log 02:55-03:02Z)
- Withdrawn; self (LEDGER item 10): The claim that the active-subspace spectrum caps description-guided RQMC at 1.4x was withdrawn (derivative-energy shares do not bound variance shares); description-guided RQMC is untested, not refuted. (report Part 1 section 8; work/arc-noisy/LEDGER.md item 10)
- Corrected by GPT-6 claims review of Part 1, findings 3-6: Multilevel argument reworded (it assumed a sampled coarse level; with a free exact coarse expectation the expression is below 32); 'exact' copula marginals are empirical quantiles; sampler not exact for degree-5 polynomials; HSC is 9% better than the Gaussian closure but 11% worse than K=2 (report had said better than K=2); survival 'within 16%' not 15%; mean-shift table redone on all 24 nets; H2's 3e11 prediction marked missed. (report Part 1 section 8)
- Corrected by GPT-6 code review of Part 2 (arc-noisy-review2-2026-10-29/review_code.md, finding 1, critical): Kill-test code used relative MSE < 0.999 instead of the registered < 1; under the written rule mode splitting (U1) passes 17/32, not 15/32, reversing its kill verdict. Amendment 3: U1 scored under both rules; no win under both. (report P2.8 code review item 1)
- Corrected by GPT-6 claims review of Part 2 (review_claims.md, 7 major + 5 minor): Depth-4 1e-12 win removed from the headline (median-convention dependent); '2^20 paths' rows relabelled as smallest successful budget; smallest-p table split into pre-registered and larger tested budgets; 'backward functions have no leverage' and 'r >= 0.46: at most ~2x' narrowed to the candidates tested (single-event minimum r 0.10); 'its error is relative' and the four-moment limit reworded as not established; 'splitting is the only accurate method at depth 32' reworded; ARC's depth-32 cost per threshold vector 2.6e11 -> 2.1e11. (report P2.8 claims review items 1-12)
- Corrected by GPT-6 follow-up review of Part 2 (review_claims2.md, finding 1): Confirmatory section had said 'The primary test passes at depth 4 and fails at depth 8', 'confirms a positive difference' and 'reliably more accurate'; replaced by 'The registered joint primary test failed'. (report P2.10; progress log 10:07Z; review_claims2.md)
- Corrected by GPT-6 claims review of Part 3 (review_claims3.md, finding 1 major): Exploration claimed an information limit of K3f ('no readout of it can individualise the tail beyond what three cumulants allow') and a four-moment accuracy ceiling; reworded as measured correlations and scores. Correlations are of excess kurtosis, not the fourth cumulant. 'Untouched until scoring' replaced by the exact sequence (truths started 10:12Z, prereg 10:33Z). (report P3.5)
- Corrected by GPT-6 quick check of Part 3b (review_claims3b.md, finding 1 major): The inference that better moments would not rescue the depth-32 readout confused two metrics (Part 2's MC moments + saddlepoint did beat zero at 1e-4 and 1e-6); replaced by 'does not isolate'. One CI end 0.98 -> 0.97. (report P3b.1)
- Corrected by Kelvin (via overnight log): Kelvin challenged the depth-32 tails conclusion; the claim in the overall summary was narrowed to 'none of the moment-based deductive readouts we tested'; non-moment families (boundary-aware, backward from the event) stated as not tested. This started the boundary-family lane. (overnight-report-2026-10-29.md, progress log ~14:25Z; report Overall summary bullet 'Depth 32 tails')

Not finished: Open ideas, none tested (Handoff): noise extrapolation of kprop; description-guided RQMC; Priority 2 (readouts of Monte Carlo moments beyond order four; not run, CPU budget); Part 3b at sigma 0.003 and 0.01; depth-16 tails (no truths). Not run: factorized K=3 augmented at depth 32 for means; factorized K=4 (outside budget); augmented K=3 at depth 8, sigma 0.01 (stopped, row missing); bit-based scoring of families; contest sample-free entries (not public, quoted unreproduced). Reporting gaps after the Part 2 follow-up review: fraction CIs only for U3/U2/ARC at depths 4 and 8, median-error CIs not printed, Kerdock not evaluated at the registered fixed budgets. No sigma = 0 comparison.

Could not be determined when extracting: Whether 'negative result' or 'numerical evidence' is the better single label: the lane is mixed and I chose by the depth-32 headline. Which model wrote the report (reviewer notes the author's model family was not exposed). I read the review copies in the repo clone; the originals in /tmp/arcn_review* were not checked against them.

### algzoo-noisy

Report: `algzoo-noisy-2026-10-29.md` (lanes/algzoo-noisy/). Final state: 2026-10-29 16:47Z (summary final 05:01Z; section 9 added 06:04Z; section 10 and handoff 16:47Z).

Headline: Every deductive description built for M_{16,10}, M_{4,3} and the wide noisy models loses to Monte Carlo by 1e2-1e5 at equal FLOPs; only the 10-parameter M_{2,2} closed form wins (~1e6x). Widths 32/64 tolerate sigma 0.01.

Status: **negative result**. registered (PREREG parts 1-2 and Amendments 1-10, hashed); six GPT-6 review rounds; kill tests K1 and K2 fired; most structure results rest on one model or one seed per configuration; side results positive (width rescues the noise criterion; M_{2,2} closed form)

Failed approaches (14):

1. **Noise robustness at ARC's widths (fine-tunes and from-scratch training with activation noise)**
   - Tried: M_{16,10} example and zoo seed 2, M_{4,3}, M_{2,2}; sigma 0.001-0.1; fine-tunes 2^16-2^18 steps; from scratch at ARC's full 2^30 sequences (width 16)
   - Outcome: only the example at sigma 0.001 passes; sigma 0.003 fine-tune +8.3% loss; from scratch +27% (best seed); sigma 0.01 +175%; M_{2,2} and M_{4,3} pass at no sigma >= 0.001
   - Why it failed: at 1% noise half of all inputs have a margin under 1.45 noise s.d.; M_{2,2}'s errors become noise-dominated (about 0.32 sigma)
   - Rules out: Noise >= 0.003 at width 16 under the single-draw criterion. Under a marginal-loss criterion the example would pass at 0.003 (not the criterion fixed in advance).
   - Evidence: registered (Amendment 1; P1' missed). Source: section 2, 5.1
2. **Question-driven flip DAG (sparse surrogate by mean ablation)**
   - Tried: T16, 2,480 edges, saliency prefix + greedy pass, 2^13 fit / 2^15 held-out inputs
   - Outcome: 85% of edges at held-out flip <= 1% (prediction <= 25%); K1 fired
   - Why it failed: decisions depend on low-variance directions through gate thresholds and the argmax, which second-order saliency does not see
   - Rules out: Sparse surrogates findable by this heuristic. 'A better search, another ablation ... or another basis could find sparser surrogates.'
   - Evidence: registered (D1 missed, K1 fired). Source: section 3.3, 8
3. **Average-targeted DAGs (error-rate and loss targets)**
   - Tried: T16, tolerances at N_ref 2^10, 2^14, 2^18, 13 strata
   - Outcome: 82-92% of edges, 13-15 directions; L1 2/3 missed
   - Why it failed: simplifications flip answers both ways but raise the error rate on net, so targeting the average adds little slack
   - Rules out: Extra sparsity from targeting the average under these tolerances. Block-greedy pruning was stopped unfinished.
   - Evidence: registered (Amendments 4, 4b). Source: section 3.4
4. **Descriptions relative to the algorithm (ablate to algorithm-conditional means)**
   - Tried: T16, W32, W64
   - Outcome: 58% (T16), 60% (W32), 30.4% of all edges (W64, sigma 0.01); C1 (<= 40% / <= 30%) missed
   - Why it failed: not explained
   - Rules out: The registered sparsity levels; W64 is a near miss on one seed.
   - Evidence: registered (Amendment 6). Source: sections 3.6, 5.2, 7
5. **Question subspaces (low-rank per-step state)**
   - Tried: T16 and wide models, Fisher-weighted directions, 2^16 held-out inputs
   - Outcome: 13 of 16 directions (9-13 from step 4); W32 22 of 32; W64 25-32 of 64
   - Why it failed: second-order question variance is concentrated (4-6 directions hold 98%) yet answers need 13: thresholds on low-variance directions
   - Rules out: 'Much below 9-13 directions at the late steps only for this family of linear projections.'
   - Evidence: registered (L2, W3). Source: section 3.3, 8
6. **Fitted Gaussian-residual families (G, AC, CL, CL3, CLX) as predictors of the error rate**
   - Tried: T16, least-squares fits on 2^18 sequences
   - Outcome: predicted error 0.106-0.900 against true 0.041 (2.6x to 22x off)
   - Why it failed: the 2-7% residual is not Gaussian and not independent of the decision; spread as a Gaussian it crosses decision boundaries the network respects
   - Rules out: These least-squares members (not optimised for the error rate).
   - Evidence: exploratory. Source: section 3.1
7. **Deductive Gaussian-mixture chain (ADF) and meeting in the middle**
   - Tried: T16 (k = 0, 2, 4 gates; up to 209 components, 4e7-1.2e9 FLOPs), M_{2,2}, M_{4,3}, wide models
   - Outcome: predicts 71-75% against 4.1% (T16); 10.6% vs 0.008% (M_{2,2}); 30% vs 1.5% (M_{4,3}); 65-91% on wide models; one backward step from exact states already gives 0.18
   - Why it failed: Gaussian closure misplaces probability across the decision thresholds; fails within a single step
   - Rules out: Moment-matched Gaussian-mixture closures of this kind for threshold questions.
   - Evidence: registered (E1, K2, W4, L4). Source: sections 3.1, 3.2, 4
8. **Algorithm-indexed Gaussian description on ARC's bar (column a)**
   - Tried: T16, W32, W64 (two sigma), 16 weight-perturbed copies each, last step recomputed per copy
   - Outcome: MSE 2.4e-3 (T16, bias +4.0 points), 1.0e-4 to 4.5e-3 (wide); 1.7e3 to 6e4 times worse than MC at equal FLOPs; worse than the oracle constant
   - Why it failed: per-cell Gaussian residual spreads the logits across the decision boundary; the bias is already present on the base model, not caused by unseen copies
   - Rules out: This description as a deductive estimator.
   - Evidence: registered (C2, C3, W5). Source: sections 3.6, 4, 5.2
9. **Column (b) hybrids: Neyman allocation / control variate from the ADF; two-level estimator with the dp surrogate; control variate from the algorithm-indexed description**
   - Tried: T16 and wide models, 1,024-16,384 sequences
   - Outcome: at most 1.2x per sequence; 6-9x worse at the smallest budget, about equal at the largest; two-level 1.3-2.5x worse; wide models 2.5-85x worse at equal FLOPs
   - Why it failed: predictions barely correlate with the errors; deductive setup cost buys nothing; the surrogate is only 18% cheaper per sequence
   - Rules out: These hybrids. L3's plug-in estimator was not run as registered.
   - Evidence: registered (B2, C3). Source: section 4
10. **TOP3: deductive estimator with exact quadrature over the top-3 values and positions**
   - Tried: T16 and W64 (sigma 0.01), budgets 2,880 to 1.47 million nodes
   - Outcome: column (a) loses by 64-4,400x at equal FLOPs; column (b) no clear gain at equal FLOPs (0.93-1.08x T16, 1.16-1.28x W64 at 2^16)
   - Why it failed: quadrature converges slowly (error probability is close to a step function); per-point model bias 10-27% (predicts 8% where the 2nd max is negative, true 77%)
   - Rules out: This quadrature and per-point model. Even with exact integration a 10-27% bias is far from the 3-5% needed.
   - Evidence: registered (Amendment 7; E7.2 hit). Source: section 9
11. **Forward-only (path-KL) description and forward saliency ranking**
   - Tried: T16
   - Outcome: path KL 4.5e6-5.7e6 nats for surrogates ablating 370-550 edges; forward ranking flips 6.1% at 2,048 edges vs 1.2% for the question ranking
   - Why it failed: at sigma 0.001 a forward-only description scored by path KL would have to keep nearly everything
   - Rules out: Path-KL-scored forward descriptions at this precision.
   - Evidence: registered (D3 half). Source: section 3.3
12. **Certified bounds for T16**
   - Tried: none attempted beyond the fitted families (66+ bits per step unexplained)
   - Outcome: no non-vacuous certificate; M_{2,2} only a one-sided upper bound (8.7e-4 vs truth 3.3e-4), lower bound vacuous
   - Why it failed: Gaussian-residual costs are tens of bits per step; union bound counts every gate flip
   - Rules out: nothing beyond what was attempted
   - Evidence: registered (E3). Source: sections 3.1, 4, 7
13. **Width as a route to sparsity for the M1 target**
   - Tried: 27 models, widths 16-128, noisy and noiseless, three training series
   - Outcome: every width-16 model analysed is dense (85-96%); kept-edge count grows 2.3-3.4x per width doubling (about 2,200 -> 94,000-100,000); width 128 keeps 63-66% (prediction <= 40%); noise not needed (W8.6 missed); no disjoint DAG in the complement (R9.1 missed)
   - Why it failed: what falls with width is a share; the share tracks loss more than width
   - Rules out: 'Sparsity in wider models therefore does not make M_{16,10} itself easier.' Confounded design; not proven minima.
   - Evidence: registered (Amendments 8-10). Source: section 10
14. **CPU from-scratch width-16 runs on a shortened schedule (2^28 sequences)**
   - Tried: seeds 0-4, sigma 0 and 0.003
   - Outcome: schedule too short even without noise (controls +24% to +127%); 'these runs say nothing about noise'
   - Why it failed: undertrained
   - Rules out: nothing; replaced by the full-length GPU runs
   - Evidence: exploratory. Source: section 5.1

Our own registered predictions that failed (9):

- P1 / P1': predicted M_{16,10} passes at sigma 0.01-0.03; it passes only at 0.001 (example), seed 2 at none, M_{4,3} at none.
- D1: flip-DAG <= 25% of edges; got 85%. D2, D3, D4 half held (neuron 2 not largest out-degree; forward ranking needs only 1.2x the edges; no neurons dropped at steps 2-3).
- S5 (>= 1.3x, got 1.26x) and S6 (last position easier <= 0.5p, got 1.25p, wrong direction).
- L1: average-targeted DAG <= 50% / <= 75% at N_ref 2^10 / 2^14; got 82% / 86%.
- B1 bias clause (>= 10 points) missed for the algorithm-indexed description (0.8-6.6 points).
- W2 mixed (W32 75-80%, W64 seed 0 58% against <= 50%); W3 half (W32 22 of 32).
- C1 missed (58%, 60%, 30.4%); C2 wide clause missed (W32 7.1% vs 3.1%; W64 3.2% vs 2.07%).
- Amendment 7: Y1, Y4 missed (higher than predicted), Y3 T16 missed, Y5 missed (F3 0.41 against >= 0.60), E7.3 W64 missed, E7.4 equal-FLOP clause not met on T16.
- Sweep: W8.2 clause 'width 128 at <= 40%' missed (63-66%); W8.6 missed (+0 to +2.5 points, predicted >= 10); R9.1 missed (complement fails at every width).

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (5):

- Corrected by GPT-6 review 1: First version concluded errors are NOT decided at algorithmic events (used all-step base rates); step-matched rates reverse it (about 2x chance). First version attributed the sigma 0.01 gap to gate flips (top competitor only); all-competitor linear response shows gate flips add almost nothing. A 37% algorithmic-state information figure was an in-sample artefact (cross-fitted: a few percent). (report progress log 02:37Z; sections 2, 3.2)
- Corrected by GPT-6 review 2: 'No cancellations' withdrawn (0.30% corrected, 0.41% broken); column (b) equal-FLOP comparisons corrected; M_{2,2} column (b) 1e4-1e6x -> 1,200-2,100x; three DAG sizes that missed their held-out targets corrected; L3 scored as not run as registered. (report progress log 03:40Z; sections 3.4, 4, 5.2, 7)
- Corrected by GPT-6 reviews 3-4: C1 scored on the registered edge set (near miss 30.4%); B1 split into its two clauses; overstatements about advice transfer and deductive misses corrected; DAG sizes counted only where the held-out target is met (W32 75-80%, W64 43% and 58%); untested rank 21 no longer counted. (report progress log 04:00Z, 05:01Z)
- Corrected by GPT-6 review 5: TOP3's 'exact' own integral relabelled a sampled estimate; attribution of the earlier descriptions' bias to the closure withdrawn (TOP3 also changes the residual model); column (b) given against both MC baselines. (report progress log 06:04Z; section 9)
- Corrected by GPT-6 review 6: Redundancy claim narrowed to the complement test; width-16 claims restricted to models analysed; M1 implications made conditional; random-order figure corrected. (report progress log 16:47Z)

Not finished: Lane stopped at the coordinator's request (16:47Z); the AlgZoo atlas was cancelled by Kelvin (overnight log 15:59Z). Not done: the program's per-step coverage cost and waste (need log Kq; not computed); block-greedy pruning for the dp DAG (stopped after 45 min); L3 plug-in estimator as registered; per-seed analysis of the wide models (one seed per configuration); twins at widths 16 and 32, two width-128 twin seeds, series-S width 16 and width 256 (Amendment 10 scope cut). 'What the results point to (not tested)': a conditional-linear description with exact quadrature over the algorithmic variables; boundary-locating quadrature for TOP3.

Could not be determined when extracting: Whether the review outputs agree with the report's summary of them (I checked only that six review sets exist, not their contents).

### boundary-family

Report: `boundary-family-2026-10-29.md` (lanes/boundary-family/). Final state: 2026-10-29 17:00Z (report header); section 7 dated 17:35Z, file mtime 17:27Z.

Headline: The prototypes failed both pre-registered development kill tests, so no evaluation run was made; cells built from the weights stay at K=2's level at 256 x 32 (6.7e-4, 1.0e-3), 2-7x worse than ARC's K3f.

Status: **negative result**. two registered kill tests (K1', K-F) on development nets 101-102 only; rest exploratory; GPT-6 design critique and claims review; sections 6-7 written after the claims review and not reviewed; verdict limited to the prototypes tested

Failed approaches (10):

1. **Factored models F3, F8, F3C (exact low-dim PCA latent + conditionally independent Gaussian residuals)**
   - Tried: 256 x 32, nets 101 and 102, one exact push from layers 16, 24, 31
   - Outcome: variance error 1.6-10% (G 1.5-2.1%); mean nMSE 0.84-8.2x G's; bar (<= 1/3 of G with <= 2% variance error) not met
   - Why it failed: a diagonal residual misses W (off-diagonal) W^T: second-order structure along W
   - Rules out: These factored models. 'Not every conditionally independent model.'
   - Evidence: registered (K-F). Source: section 2.3
2. **IND: product of the exact marginals**
   - Tried: same setting
   - Outcome: 29-65% variance error, mean nMSE 2.5e-3 to 7.3e-3
   - Why it failed: drops all dependence
   - Rules out: Fully independent neuron codes for one-step propagation.
   - Evidence: exploratory. Source: section 2.3
3. **Fitted cells at a cut (PCA3 64 cells; also AS3, GATE6) as a representation**
   - Tried: fit to 2^18 true paths at layer 24, exact propagation to 32; nets 100 (exploration), 101, 102 (registered); ten nets 101-110 in section 7
   - Outcome: net 102 8.1e-5 (bar <= 2e-5 and <= 1/10 of G); ten-net median gain over G 4.8x; GATE6 1.0e-4 / 3.7e-5 / 1.5e-4; AS3 worse than PCA3
   - Why it failed: what the cells miss is joint structure outside their axes; less collapsed nets gain less
   - Rules out: 64 cells on 3 axes as a sufficient representation on the typical net. Does not rule out 'M1 or broader cell families'.
   - Evidence: registered (K1') plus exploratory extension. Source: sections 2.1, 7
4. **SPLIT3: splitting the fitted Gaussian into 27 cells (deductive control)**
   - Tried: net 101, layer 24
   - Outcome: representation error 7.0e-5 vs 6.8e-5 for one Gaussian; total push nMSE 9.7e-5 vs 1.5e-4
   - Why it failed: splitting a Gaussian does not create the missing information
   - Rules out: Gaussian splits as a source of within-cell structure.
   - Evidence: exploratory. Source: Summary; section 2.1
5. **Deductive latent-conditional Gaussian with re-binned cells built from the weights**
   - Tried: 64 x 16 (4/16/64 cells) and 256 x 32 (16 cells), nets 500, 100, 101
   - Outcome: 1.65e-3 at 64 x 16 (MC at similar estimated cost about 8e-5); 6.7e-4 and 1.0e-3 at 256 x 32 vs K3f 3.2e-4 and 1.5e-4
   - Why it failed: within-bin distributions grow more non-Gaussian with depth (kurtosis 0.045 at layer 8, 0.27 at 31)
   - Rules out: This construction. Costs are estimates, not counted.
   - Evidence: exploratory. Source: section 2.4
6. **Other deductive mixtures at width 64 (moment-preserving latent splits, exact boundary splits with forced gates, one grid split)**
   - Tried: 64 x 16, net 500, 3-81 cells
   - Outcome: 2.5e-3 to 3.9e-3 (Gaussian closure 3.5e-3)
   - Why it failed: not explained
   - Rules out: These split rules at width 64.
   - Evidence: exploratory. Source: section 2.5
7. **Gate compression (co-switching groups, downstream-effect groups, prediction from the latent)**
   - Tried: 64 x 8, 128 x 16, 256 x 32; layers 6-31
   - Outcome: no merges by co-switching at \|phi\| 0.5-0.95 (one exception); downstream grouping at 0.8 merges at most 136 -> 111; latent predicts 26-68% of gate signs (no baseline)
   - Why it failed: near-boundary gates are nearly uncorrelated pairwise
   - Rules out: Compression by these pairwise criteria; joint structure is left to the gate-entropy census.
   - Evidence: registered descriptive measurement (no rule). Source: section 2.2
8. **Fitted Gaussian mixtures for depth-32 tails**
   - Tried: net 102, layer 31, 8 outputs x 5 thresholds
   - Outcome: median underestimate at 1e-6 of 7.5x (64 cells), 3.7x (16 bins), 240x (one Gaussian)
   - Why it failed: not explained
   - Rules out: 'This is one net and one fit, not a proof that every Gaussian-cell family must fail.'
   - Evidence: exploratory. Source: section 2.6
9. **Log-radial (scale) chart at 256 x 32**
   - Tried: net 100
   - Outcome: 9.0e-4 vs 7.6e-4 for the Gaussian closure: no gain (2.5x gain at 64 x 16)
   - Why it failed: at 256 x 32 the size is not where the error is; mechanism not isolated
   - Rules out: Scale correction as the fix at 256 x 32.
   - Evidence: exploratory. Source: section 2.7
10. **Exact near-boundary marginals inside cells (PCA3NB) and a fourth cell axis (PCA4, 256 cells)**
   - Tried: ten nets 101-110, cut 24
   - Outcome: PCA3NB changes the layer-32 error by a median 1.12x; PCA4 improves it 1.41x; 256 cells still a median 6.8x above the fit floor
   - Why it failed: the loss is not in per-neuron shapes at near-boundary neurons
   - Rules out: Per-neuron shape corrections as the missing piece (for this oracle).
   - Evidence: exploratory. Source: section 7

Our own registered predictions that failed (2):

- K1' prediction (G 2-3e-4; best family 1.2-2e-4; AS3 no better than G; GATE6 within 30% of G) missed in the favourable direction: 'the families did better than predicted, and the kill came from net 102'.
- K-F prediction (all factored models fail) held.

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (4):

- Corrected by GPT-6 claims review (work/boundary-family/review/claims_review.md, 16 findings: 13 major, 3 minor): 'No push rule can do better' withdrawn (representation is a reference, not a bound); 'merges nothing at 0.8' corrected (downstream-effect groups 136 -> 111 etc.); pairwise statistics no longer read as joint independence; 'nearly isotropic' relevance matrix withdrawn; verdict narrowed to the prototypes tested; 'perfect' cells renamed fitted; FLOPs labelled estimates; tail conclusion narrowed; log-radial PSD bug fixed and rerun. (report section 3)
- Corrected by GPT-6 design critique (16 findings, 3 critical): Two forced-gate bugs fixed; paired oracles relabelled; representation-versus-push split added. (report section 3)
- Withdrawn; self: An early latent-split run that reached 9e-4 at 64 x 16 is withdrawn: its split rule shrank the variance by 4.5% per split and the gain came from cancelling the closure's scale overestimate; output not archived. (report section 2.5)
- Corrected by self (section 7, exploratory rerun): The K1' pass on net 101 (4.8e-6 vs 6.8e-5) does not hold with an independent 2^19-path fit set (1.0e-5 vs 7.2e-5): 'With this fit set it would not pass.' Summary now says 'well on one net in three ... only within fit-set variation'. (report section 7 and Summary)

Not finished: No evaluation run. Candidate B (backward functions) not built; output moments and tails not run deductively. Untested proposal: a polynomial closure from a cumulant description at a switch layer (section 4); heavier-tailed components or backward refinement for tails. Kelvin's item 2 (fully non-Gaussian families) handed to the nongauss-family lane.

### nongauss-family

Report: `nongauss-family-2026-10-29.md` (lanes/nongauss-family/). Final state: 2026-10-29 ~20:05Z (lane 16:55Z to about 20:30Z per header; overnight log: final after GPT-6 review at 20:05Z).

Headline: None of the fully non-Gaussian families built was shown to scale on depth; only 64-128-dimensional empirical joint blocks reach the fit floor in single cuts, and re-projecting at every layer accumulates error.

Status: **negative result**. registered (PREREG + 4 amendments, hashed); oracle fits only (no sample-free estimator, no costs claimed); GPT-6 design critique and claims review (1 critical: a registered verdict was corrected); several verdicts are 'inconclusive' or unresolved; one sigma, one L/n, at most 4 nets

Failed approaches (9):

1. **Independent principal components with exact non-Gaussian marginals (I, PI) and two-point components (PR)**
   - Tried: 256 x 64, nets 113-116, cuts 32 and 48, 2^20 fit paths, 2^21 samples
   - Outcome: R(32;64) 1.8e-4 (PI), 2.6e-4 (I), 3.4e-4 (PR) against G 2.8e-4; floor 7e-7
   - Why it failed: non-Gaussian marginals buy only 1.2-1.7x; what matters is how much joint law is carried
   - Rules out: Marginal shape as the missing ingredient at these cuts.
   - Evidence: registered (T1: I fails, PI and PR inconclusive but above 1e-5 on every net). Source: section 2
2. **Cells with exact-marginal, two-point or Gaussian residuals (PC3I, PC3R, PCA3, PC3G)**
   - Tried: same setting
   - Outcome: R(32;64) 1.9e-5 to 6.7e-5; composition 2.8e-4 / 3.1e-4 at L = 64
   - Why it failed: error grows 5-10x after a deep cut and accumulates under re-projection
   - Rules out: These cell families as depth-scaling representations.
   - Evidence: registered (T1 fail for PCA3, PC3G, PC3I; T3 unbounded for PC3I). Source: sections 2, 3
3. **Joint blocks of at most 32 principal components (PB2-PB32)**
   - Tried: same setting; widths 128-512
   - Outcome: R(32;64) 1.9e-4 (k = 2) to 1.6e-5 (k = 32); PB16 chain 2.2e-4 / 7.7e-4
   - Why it failed: block too small; error falls only as the jointly carried block grows
   - Rules out: Subspaces of at most 32 directions chosen by variance.
   - Evidence: registered (T1 inconclusive by interval; T3 unbounded for PB16). Source: sections 2, 3
4. **Attractor shape transfer (ATT8, ATT16 from earlier layers; ATTX from another net)**
   - Tried: same setting
   - Outcome: R(32;64) 2.1e-4 to 4.2e-4: at G's level
   - Why it failed: the direction law's shape keeps changing with depth (no stationary shape by depth 64)
   - Rules out: This PCA-based shape transfer; 'does not exclude an attractor at larger depth'.
   - Evidence: registered (ATTX fails, ATT8/16 inconclusive; P6 held). Source: sections 2, 5
5. **Blocks on sensitivity or bidirectional directions (PBA, PBS, PBW)**
   - Tried: k = 8-32, cuts 32 and 48
   - Outcome: PBW_k 1.1-1.7x better than PB_k; PBW32 still grows 1.9e-6 -> 9.0e-6 after cut 32; H1 not supported
   - Why it failed: consistent with gate flips being nonlinear (not isolated)
   - Rules out: Families exact in the top 32 directions chosen by variance, sensitivity or both. Growth tests inconclusive by the rule's intervals.
   - Evidence: registered (Amendments 1-2). Source: sections 2, 4
6. **Re-projecting at every layer (composition), all families including large blocks**
   - Tried: 256 x 64 layers 32-64 and 128 x 32, nets 113/114, 2^21 particles
   - Outcome: G/PG/PI 4e-4 and 2.3-2.8e-3; PB64 5.7e-5 / 3.2e-5 (20-40x its single-cut error); PB128 1.4e-6 / 1.2e-5; MC and bootstrap at or below 7e-6
   - Why it failed: a chain projects distributions that are already approximate; errors are not additive
   - Rules out: Single-cut scores as a predictor of composed error (understate it 5-40x). Large-block asymptotic bias near 1e-5 unresolved.
   - Evidence: registered (T3; Amendment 4 inconclusive). Source: section 3
7. **Polar chart alone (PG vs G)**
   - Tried: same setting
   - Outcome: at most 1.7x; PG worse at cut 48
   - Why it failed: 77-91% of the error is orthogonal to the mean direction: not a scale error
   - Rules out: Removing the scale as the fix.
   - Evidence: registered (P2 held). Source: section 2
8. **Linearised sum of single-cut errors as a model of the chain (R4)**
   - Tried: net 113 only (stopped for the $5 cap)
   - Outcome: predicts 7e-2 (G) and 6e-3 (PB16) against measured 4.5e-4 and 2.2e-4 (155x and 27x off)
   - Why it failed: the chain projects approximate distributions, not the true ones
   - Rules out: Additive error accounting for re-projection.
   - Evidence: registered run, one net. Source: section 3
9. **Learned code at the earlier cut and for mean bias**
   - Tried: 256 x 64, cut L/2; MLP codes k <= 64
   - Outcome: pathwise 1.05% at k = 64 (misses 1%); no MLP code reaches 1e-5 shuffled-residual bias
   - Why it failed: not explained
   - Rules out: A 16-64-dim MLP code as sufficient at L/2 under this training.
   - Evidence: registered (T6). Source: section 4

Our own registered predictions that failed (6):

- P3: PI predicted 2-5x better than G; only 1.5x.
- P5: PC3I predicted the best fully non-Gaussian family; PB32 is slightly better.
- P7: predicted errors flat or growing with width at fixed L/n; every approximate family's error falls with width.
- A1: PB64 predicted 3-5e-6 at cut 48 (got 7.5e-7); PB128 predicted above 5e-6 at cut 32 (at the floor).
- A2: T5a predicted 'sublinear' (got 'few', 1.4-1.5x); T5b N_surv predicted 3-8 (13 at L'/n = 1/32); T6 predicted no k <= 64 reaches 1% pathwise, channel floor 1e-5 to 1e-4, k_bias grows: missed on all three.
- A4: predicted PB128 bounded and useful, PB64 at 128 bounded: all inconclusive (noisy extrapolation).

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (3):

- Corrected by GPT-6 claims review (work/nongauss-family/review/claims_review.md, finding 1, critical): The H3 analysis clipped a negative floor (max(mean floor, 0) instead of the registered 3 x mean floor + 2e-6), giving k* = 128 at 3L/4 and the label 'sublinear'. Corrected: literal verdict 'about linear in n' (k* = 64 / 64 / 256), stated as unresolved at 512. (report section 7 item 1; section 4; overnight-report-2026-10-29.md 20:05Z ('Correction relayed to Kelvin'))
- Corrected by GPT-6 claims review, findings 2-12: Headline and 'For M1' overstated failure and necessity (reworded to 'none was shown to pass'); 'the scale drops out exactly' false with noise; polar families are ambient approximations; compressor 'under 0.5%' wrong at 128 (0.84%); concentration of the sensitivity spectrum is not self-correction; growth claim too universal (exceptions PBS16, PBA16, late decline after cut 16); 'PB128 carries 128 joint coordinates'; the linear-sum explanation and 'rising layer by layer' were wrong. (report section 7)
- Corrected by GPT-6 design critique (15 findings, 4 critical): Missing ReLU in the exploration gate census; gnomonic chart replaced by the sphere chart; PEMP added as homogeneity control; weighted fits and family-specific floors; MC and bootstrap controls for composition; no claim of a deductive push. (report section 7)

Not finished: R4 stopped after net 113 (GPU cap). Unresolved: k* at width 512 (between 64 and 256); asymptotic bias of large-block chains. Not tried: a learned code whose latent law is pushed exactly; other noise levels and L/n ratios. NPZ files keep means only (no second moments); spectrum and compressor files keep summaries, not models.

### sparse-codes

Report: `sparse-codes-2026-10-29.md` (lanes/sparse-codes/). Final state: 2026-10-29 ~19:27Z (instance list checked empty 19:26Z; overnight log 'lane done' 19:28Z).

Headline: No route to M1 through sparse codes on the tested random nets: no TopK dictionary reaches the noise at L0<=n/4 (KT1 fires), couplings hold 36-69% of the variance, and transcoder closures lose to neuron K=2 (KT5 fires).

Status: **negative result**. registered (PREREG + 6 amendments, hashed); GPT-6 design critique and a GPT-6 claims review of a draft; results that arrived after the review were added unreviewed; single weight seeds (seed 66 replicate at width 64 only), fixed depth 32, sigma 0.01; oracle tests KT2-KT4 and KT6 do not fire; 'not impossibility results'

Failed approaches (7):

1. **TopK sparse dictionaries (SAEs) at the noise precision**
   - Tried: ARC He-ReLU n = 64, 128, 256, depth 32, sigma 0.01; F = n..16n, k = n/16..n/2, 2^18 states per layer, 30 epochs; chaotic tanh n = 64, 128
   - Outcome: best error at L0 <= n/4 in noise units, layers 1..31: 465, 356, 166, 56, 17, 3.7, 4.2 (n = 256); chaotic tanh 1,200-1,900; at sigma 0.001 (n = 64) 38-52,000
   - Why it failed: the exact sparse code of a ReLU layer is the neuron code (124-133 of 256 active); a larger dictionary barely helps (16n is 0.7-1.1x of n)
   - Rules out: TopK SAEs as trained. Deep cells at n = 64-128 (1.05-3.3 units) unresolved. OMP, JumpReLU SAEs and more data not tried. 'Optimisation, not existence.'
   - Evidence: registered (KT1). Source: section 2, 7
2. **Factored (independent-feature) model of sparse features**
   - Tried: n = 256 SAEs (mean origin, F >= 4n, k <= n/4), layers 8/16/24; independent product pushed to depth 32
   - Outcome: next-layer variances move by a median 35-69%; independent product without recolouring 5.4e-4 to 1.2e-2 at depth 32 (G 1.7e-4 to 1.3e-3)
   - Why it failed: atoms of an overcomplete dictionary overlap, so off-diagonal covariances carry 36-69% of the variance
   - Rules out: 'Weak pairwise couplings among sparse features do not license a factored model.'
   - Evidence: measured; independent product is the analytic case of the coordinator's first retarget. Source: section 3
3. **Fitted marginals-plus-covariance models of the latent (SPARSECOP, SPARSEIND, NEUCOP)**
   - Tried: cuts 8, 16, 24; n = 64 (two seeds), 128, 256; pushed through real layers to depth 32
   - Outcome: copula 2.0e-5 to 3.8e-4, 1-2 orders of magnitude above the exact latent (at most 3.6e-6); at n = 256 only 2.3-2.7x better than one Gaussian and no better than an exact dense latent of n/8-n/4 PCA coordinates
   - Why it failed: most of what the sparse latent buys lies beyond its marginals and covariance (for this construction)
   - Rules out: One fitted copula construction. 'Another family with the same marginals and covariance could do better.'
   - Evidence: registered (E5, amendment 4); KT6 does not fire. Source: section 3, 7
4. **Transcoders as a propagation rule**
   - Tried: one TopK/JumpReLU transcoder per layer, F = n and 4n, k = n/8..n/2, n = 64 and 256; deductive feature-covariance closure; std, shift and aniso input laws
   - Outcome: no transcoder reaches the noise (1.5 and 5.4 noise units per layer; path KL 5.5e3 and 8.4e4 bits); on the shift law at depth 8 the closure gives 1.8e-3 vs K=2 1.1e-3 (n = 64) and 2.6e-3 vs 1.5e-4 (n = 256; K3f 4.0e-6)
   - Why it failed: on the training law the chains' biases memorise per-layer means; at n = 256 the chain itself is the error, at n = 64 the closure's own error
   - Rules out: These learned transcoders under two shifted laws. The aniso law is a weak test. No replicate.
   - Evidence: registered (KT5 fires). Source: section 6
5. **PCA at the noise precision**
   - Tried: ARC n = 256, layers 1-31
   - Outcome: components needed to get below the noise: 256, 254, 238, 214, 182, 147, 149
   - Why it failed: at noise precision the state stays high-dimensional even where its participation ratio is 5
   - Rules out: Low-rank linear codes at sigma 0.01.
   - Evidence: measured baseline. Source: section 2
6. **Sparse latent against a dense (PCA) latent at equal bits, small width**
   - Tried: n = 64, seed 65, bracketing by latent size in bits
   - Outcome: PCA latents of about the same size are as good or 2-5x better (e.g. 4.9e-8 at 72 bits vs 2.2e-7 at 70 bits)
   - Why it failed: much of the sparse latent's edge at equal L0 is the information its support carries
   - Rules out: A sparse-basis advantage per bit at n = 64 (descriptive comparison; at n = 256 sparse wins 1.4-10x against linear-mean PCA latents).
   - Evidence: descriptive (post hoc). Source: section 4
7. **ARC's K3f at small width and large depth (competitor)**
   - Tried: width 64, depth 32, seeds 65 and 66
   - Outcome: 6.1e-2 and 0.28, worse than K=2 (1.1e-2); diverges (16) on the shift law
   - Why it failed: not explained ('unstable at width 64 and depth 32 on these nets')
   - Rules out: nothing about ARC's method at width 256
   - Evidence: measured side observation. Source: sections 5, 6

Our own registered predictions that failed (4):

- The report has no predictions-against-results table. Reading PREREG.md's predictions against the report's numbers (my reading, not the report's scoring): P2 'KT2 fires: sparse is no better than dense at matched k' failed (KT2 does not fire, 19 of 24 cells).
- P3 'DENSEQ(16) and SPARSE(k = 32) at cut 24 give about 5e-5, comparable ... Sparse is not better than dense' failed (8.1e-6 vs 6.6e-7).
- Amendment 4 prediction 'KT6 fires' and 'SPARSECOP lands within 2x of G' failed (0 of 9 cells; copula 2.3-34x better than G).
- P2 'one-step mean nMSE of G between 1e-4 and 1e-3 at layers 8-31' missed low at n = 256 (2.3-5.1e-5).

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (3):

- Corrected by GPT-6 claims review of a draft (work/sparse-codes/review/claims_review.md, 12 findings; finding 1 marked critical in the review file): 'No sparse structure' / 'no compression beyond the gate pattern' and 'that law is a dense object' restricted to the tested models ('we found none with TopK dictionaries'); the M1 paragraph now says the experiments do not exclude a route. (report section 8 (findings 1 and 10))
- Corrected by GPT-6 claims review, findings 2-9, 12: E5 described as a fitted copula matching second order only to 0.4-3.1%; floor-level ratios against the exact latent removed; E4 attribution split by width; an unregistered floor in KT6's rule removed; bits comparison called bracketing; neuron phi recomputed on the true ReLU gates (first draft used above-mean indicators); chain debiasing caveat; 'exact Gaussian closure' -> '60-term Mehler series'. (report section 8)
- Corrected by self (amendments 1, 3, 5) and GPT-6 design critique (18 findings, 3 critical; amendment 2): E4 memorisation leak; E4 Hermite overflow; E3 dense-latent late-binding bug (dense rows rerun); fit/selection/scoring sets separated; zero-origin SAEs and training-length controls added. (report header and section 8)

Not finished: Incomplete nets (GPU memory, amendment 6): ordered tanh at n = 64 (layers 1-4 only) and n = 256; chaotic tanh at n = 256 (layer 1 only); n = 256 at sigma 0.001 dropped. Convergence of deep-cell dictionaries at n = 64-128 unresolved. Not tried: OMP on a learned dictionary, JumpReLU SAEs, more data, other copula families. Depth growing with width (M1's regime) not tested; no replication at n = 128 or 256; E4 unreplicated.

Could not be determined when extracting: The report does not score its registered predictions P1-P4; the failed_predictions entries are my comparison of PREREG.md text with the report's tables.

### cm-interp-R

Report: `cm-interp-random-2026-10-28.md` (lanes/cm-interp-R/). Final state: 2026-10-29 ~03:27Z (first version 2026-10-28 ~23:23Z; revised after the GPT-6 review; work-dir STATUS: fixes done, checked 03:35Z).

Headline: The forward chain works as an estimator and fails as a certifier: per-layer coverage cost grows linearly with width for the three families measured at every width, and every certified bound is vacuous.

Status: **negative result**. mixed, chosen by the certification half of the verdict (the program's distinctive aim); estimator-side results are numerical evidence on 11 LN networks, mostly one seed. Registered (PREREG-R + 2 amendments, hashed). One GPT-6 (Codex) review of the 28 Oct version; the 29 Oct revision was not re-reviewed. Nets differ from ARC's (LayerNorm, noise, bias for tanh); ARC's factorized K = 3/4 was not run.

Failed approaches (12):

1. **Certified rare-event bounds from the forward chain (rigorous eps from the envelope)**
   - Tried: LN MLPs, tanh (three gains) and ReLU, d = 8-256, L = 4, sigma 0.3, events 2^-10 to 2^-60
   - Outcome: envelope eps is 141 bits over three layers at d = 8 and about 4,000 at d = 256: every bound is 1 (vacuous)
   - Why it failed: the coverage cost cannot be certified tractably (needs a supremum over R^d of an intractable mixture ratio)
   - Rules out: Every certificate the lane could compute. Event-specific backward certificates are untested.
   - Evidence: registered (R9 held); envelope is a rigorous bound. Source: Task 1 Theory checks; Task 2
2. **The program's tightness bound D_inf(q_L \|\| p_L) <= sum of D_inf wastes**
   - Tried: any Gaussian-tailed family
   - Outcome: the D_inf waste is infinite (log2 q/Kq +52 bits at twice the LN radius, +222 at three times)
   - Why it failed: Kq is confined to a noise-width shell around the LN sphere while coverage forces q's tails wider than sigma
   - Rules out: This bound for Gaussian-tailed families; tightness must be measured event by event.
   - Evidence: registered (R7 held); argument plus numerics. Source: Task 1 Theory checks
3. **[last] bound with an uncertified coverage estimate (search eps on the same chain)**
   - Tried: critical tanh d = 8, 16, 32; chaotic and ReLU d = 16
   - Outcome: loses about eps (15, 20-21, 36 bits; 42 chaotic, 44 ReLU); beats the sampling certificate only below 2^-29, 2^-34, 2^-51; not at all to 2^-60 for chaotic and ReLU; SMC cost (100-1000x the chain) not counted
   - Why it failed: joint divergences add up per-neuron errors; eps grows with width (at least 95-122 bits over three layers at d = 256, critical)
   - Rules out: Useful certificates on these Gaussian chains at width; a lower bound on eps alone does not prove vacuity for every event.
   - Evidence: registered (R10 first half held); search eps is an optimistic lower estimate of a supremum. Source: Task 2 Bounds
4. **[qL] bound (Gaussian output tail)**
   - Tried: d = 16
   - Outcome: adds +3 bits at 2^-10 to +47 at 2^-60
   - Why it failed: the defensive component's wide tail and the Gaussian tail both ignore the LN cap on y
   - Rules out: Output bounds that do not treat the last layer exactly.
   - Evidence: registered (R11). Source: Task 2 Bounds
5. **Copula code (Gaussian copula over exact per-neuron marginals) as the best family**
   - Tried: SMC to d = 32, one seed; rare-event bounds d = 8-64
   - Outcome: R4 failed: waste grows (2.2 / 3.6 / 8.0), coverage cost worse than the Gaussian's for tanh (12 vs 7.5, 31 vs 21), only 1.3-1.7x below in KL; [last] bound loses 23-28 bits, 5-8 more than the Gaussian's; vacuous for chaotic tanh
   - Why it failed: copula tails too thin for tanh; joint law of saturated gates is not Gaussian-copula-shaped
   - Rules out: The copula code as a certifying family at d <= 32. Its width behaviour beyond 32 is open.
   - Evidence: registered (R4 failed; R10 second half failed). Source: Task 1; Task 2; Predictions
6. **Product code (independent exact marginals) and know-nothing reference**
   - Tried: d = 8-256, three seeds
   - Outcome: product code pays the total correlation, 0.31 bits per neuron critical (80 bits per layer at d = 256); know-nothing 100
   - Why it failed: pairwise dependence adds up linearly in width
   - Rules out: Factored neuron codes as cheap descriptions at width.
   - Evidence: registered (R3, R5 held). Source: Task 1 width scaling
7. **Black-box learned psi (iterated auxiliary particle filter), most-likely-path twists, mean-shift importance sampling**
   - Tried: critical tanh d = 16, 64; chaotic and ReLU d = 64
   - Outcome: fail beyond about 2^-15 to 2^-20; mean-shift IS inside the chain step under-estimated by up to 41 bits at d = 64
   - Why it failed: with LN and no bias the input enters only through its direction, so the most likely path is degenerate in x
   - Rules out: These guides on LN nets; R13's 'tail-anchored psi best; learned psi within 3x' failed.
   - Evidence: registered (R13 mostly failed). Source: Task 3 rare events
8. **Twisted SMC with the chain's linear-probit psi in the extreme tail**
   - Tried: to 2^-60
   - Outcome: stops at 2^-30 (d = 16) to 2^-40 (d = 64) for critical tanh, 2^-20 chaotic, 2^-10 ReLU; only splitting reaches 2^-50 to 2^-60 and is heavy-tailed there for ReLU and chaotic
   - Why it failed: not explained beyond 'linear-probit psi stops working'
   - Rules out: The chain psi as a guide for extreme tails.
   - Evidence: measured. Source: Task 3; Where it breaks (3)
9. **Gaussian output tails without LN (control) and last-layer-exact for ReLU at d = 16**
   - Tried: ReLU without LN d = 16, 64; ReLU with LN d = 16
   - Outcome: without LN K = 2 under-estimates by up to 20 bits at d = 16 and last-layer-exact does not help; fitted chain over-estimates by up to 34 bits; with LN at d = 16 the chain is off by 1.3-11 bits
   - Why it failed: ReLU products make every layer heavy-tailed; the error is already in q_3
   - Rules out: 'Neither version of a Gaussian output tail is reliable on its own.'
   - Evidence: measured control. Source: Task 3 rare events
10. **Sample-fitted chain for E[output]; K = 2 at small width and depth 8**
   - Tried: 2^12 draws per layer; d = 16, L = 8
   - Outcome: fitted chain MSE 2e-4 to 3e-2 against 1.8e-4 to 2.4e-4 for plain sampling at the same FLOPs; K = 2 loses to sampling in 3 of 12 runs at d = 16 (all at L = 8)
   - Why it failed: the fitted chain adds sampling noise and a projection bias
   - Rules out: The chain as an estimator of averages beyond K = 2.
   - Evidence: registered (R12). Source: Task 3 E[output]
11. **Donsker-Varadhan bounds from K = 2's linear surrogate; low-rank surrogate; control variate for ReLU and chaotic tanh**
   - Tried: 36 configurations, d = 16-256, L = 2-8, one seed
   - Outcome: DV intervals 37-1,850x wider than sampling's CI (38-26,500x for E[y^2/2]); low-rank surrogate worse everywhere; SUR 0.75-1.7x for ReLU/chaotic
   - Why it failed: whole-path KL would need to be below about 2/N nats; coupled paths decorrelate (rho 0.4-0.8)
   - Rules out: KL-based bounds built on these surrogates; control variates for ARC's default (ReLU).
   - Evidence: registered (amendment 1; S3 failed for ordered, S4 partly). Source: Addition: surrogate chains
12. **Free LN-cap bound**
   - Tried: d = 8-64
   - Outcome: loses 26 bits at 2^-56 (d = 8), 44 at 2^-60 (d = 16); vacuous from d = 32
   - Why it failed: thresholds sit below the cap at larger width
   - Rules out: nothing beyond this bound
   - Evidence: measured. Source: Task 2 Bounds

Our own registered predictions that failed (7):

- R4 failed: copula code not the best by >= 3x; its waste grows and its coverage cost is worse than the Gaussian's for tanh.
- R10 second half failed (copula bound loses 23-26 bits at 2^-30, beats sampling only below about 2^-36 to 2^-40); before the review it was scored 'held at d = 8'.
- R12 half: 'not at d = 16' failed for L <= 4 (K = 2 wins 9 of 12 runs at d = 16).
- R13 mostly failed: bulk psi beat the tail-anchored psi at every level; learned psi failed beyond about 2^-15; K = 2 tail off by only 0.7 bits at d = 256.
- R14 half: no family makes certified bounds useful.
- R8 only partly tested (end-to-end depth dependence not measured).
- Amendment S1: critical rate 0.18 nats per neuron, not >= 0.5. S2: QUAD cuts the critical KL 1.9-2.4x, not >= 3x. S3 failed for the ordered regime. S4: chaotic rho 0.35-0.74, not >= 0.8. S5: critical skip-merge 0.84 bits, not > 5.

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (5):

- Corrected by GPT-6 (Codex) review, work/cm-interp-R/review_gpt6/review.md, point 1 (high): 'Rigorous lower bounds' (a sample mean and an in-sample maximum on one seed) replaced by 95% lower confidence bounds on three seeds; eps now measured on the chain whose (K q_3)(A) is used, not transferred from another fit. Withdrawn: 'no valid certificate ... is non-vacuous for any event more likely than 2^-119' at d = 256. (report 'Changes after the review' item 1; overnight-report-2026-10-29.md 03:10Z)
- Corrected by GPT-6 review, point 2 (high): Splitting reference values re-estimated with frozen tuning (the old pCN scale was adapted on each run's own particles): 74 of 77 levels moved by at most 1 bit, three by 1.0-1.6 bits; 24 now provisional. 'Within 0-5 bits of the truth from 2^-10 to 2^-60' -> '-0.2 to +2.6 bits at the 42 corroborated levels'. Twisted SMC 60-1,400x -> 56-1,800x; at d = 256 splitting reaches 2^-30, not 2^-40. ('Changes after the review' item 2)
- Corrected by GPT-6 review, point 3: 'Reproduces ARC's result, 13-810x' -> shows ARC's K = 2 pattern on different nets, 12.6-283x with the default K = 2 (13-810x only for the variant without the LN correction, which the report had shown alone while analyze.py used the other); 'beats sampling in every configuration' -> 9 of 12 runs at d = 16. ('Changes after the review' item 3)
- Corrected by GPT-6 review, points 4-6: Width/depth statements limited to the families and seeds measured; 'depth is benign' narrowed; surrogate-KL upper bound now a path-level bootstrap; copula sampler given exact tails (its table stopped at 8 sd), which moved the copula [last] bound from '14-16 and 19-20 bits, at most 3 bits less than the Gaussian's' to 23-25 and 26-28 bits, 5-8 bits more; R10's second half changed from 'held at d = 8' to failed. ('Changes after the review' items 4-6)
- Superseded by sparse-codes-2026-10-29.md (one assumption only): 'Sparse codes were not run: random layers have no sparse structure for them to use' was an assumption; the sparse-codes lane measured it. (report Setup; overnight-report-2026-10-29.md 16:05Z)

Not finished: Open: whether the copula code escapes linear width growth beyond d = 32; end-to-end depth dependence; ReLU and ordered regimes and other families beyond four layers. Not run: sparse codes, random transformer blocks, d = 128, ARC's factorized K = 3 and 4, ARC's own nets (no LN, no noise) beyond two no-LN controls, the copula search at d = 32 after the fix, the d = 256 tanh rare-event run. 24 of 77 reference levels provisional.

Could not be determined when extracting: Whether 'negative result' or 'numerical evidence' is the better single label for a verdict that states both halves; I chose the certification half.

### estimability

Report: `estimability-penalty-2026-10-27.md` (lanes/estimability/). Final state: 2026-10-27 (file mtime 05:19Z).

Headline: Registered verdict SUCCESS: every penalty arm cuts estimation error >=5x (9-191x) within the 0.005-nat tolerance, but at a significant task cost (+0.003-0.004 nats) and the propagator still loses to sampling at matched compute by 15-50x.

Status: **unverified**. registered measurement (PREREG with two pre-result amendments, code hashes), 3 seeds, one small model and task; no review by another model or a human is recorded in the report or work dir, so by the brief's rule it is unverified rather than numerical evidence; the report itself attaches two qualifications to the word SUCCESS

Failed approaches (4):

1. **Cumulant propagation (K = 2 and structured K = 4) as an estimator on a small transformer, against sampling at matched compute**
   - Tried: pre-norm transformer, width 32, 2 heads, GELU, LayerNorm, depths 1-8; exact Gaussian-mixture input law; MC truth 2^20-2^22
   - Outcome: at init N_eff 690-27k against a propagation cost of 38k-94k forward passes; after the penalty sampling still wins by 15-50x on E[NLL]
   - Why it failed: error compounds with depth; error floor is attention (the a.v product and LayerNorm's joint non-Gaussianity)
   - Rules out: This propagator at this size. 'A stronger propagator could change both the costs and the gains.'
   - Evidence: registered. Source: Validation at init; Main results; Caveats
2. **Structured K = 4 ('source' form) as an improvement over K = 2**
   - Tried: same models, init and all arms
   - Outcome: K = 4 no better than K = 2 as an estimator in every arm; neither predicts the residual stream's marginal skew or kurtosis (error equals the observed rms)
   - Why it failed: the source form cannot represent the joint 3rd/4th cumulants that matter (LayerNorm cross-feature and cross-token non-Gaussianity)
   - Rules out: This structured K = 4, not ARC's full K = 4 (not tractable here).
   - Evidence: registered. Source: Validation at init; Caveats
3. **Penalty with no task cost**
   - Tried: lambda 0.3, 3, 30 (K = 4), lambda 3 (K = 2); 3 seeds; depths 4 and 8; penalty every 8th step
   - Outcome: every arm pays +0.003 to +0.004 nats, 9-40 se
   - Why it failed: not explained
   - Rules out: A free estimability gain on this task; under a relative tolerance (10% of the gap) every arm would be a trade-off.
   - Evidence: registered (verdict SUCCESS only under the absolute tolerance). Source: Verdict
4. **Simple product closure for LayerNorm; applying the penalty at every step**
   - Tried: propagator development; timing on an L4
   - Outcome: product closure 10-60% off (replaced by a Laplace-integral form); a penalty step costs 3-8 s, so it was applied every 8th step with weight 8 x lambda
   - Why it failed: as stated
   - Rules out: nothing beyond these implementation choices
   - Evidence: exploratory / registered budget rule. Source: Setup; What the propagator keeps and drops

Our own registered predictions that failed (1):

- PREREG.md predicted the penalty would be met mostly by 'higher attention entropy, fewer curved GELU units, more Gaussian residual marginals' and that 'strong lambda drifts toward the random-features baseline's loss'. Result: attention entropy barely changes, GELU inputs sit in the curved zone about 98% of the time in every arm, and the cost hardly grows with lambda (random features is 20x worse); only the more-Gaussian residual marginals held. (My comparison of PREREG.md with the report; the report has no predictions table.)

Not finished: Parked by Kelvin on 2026-10-27 (about 14:47-15:00Z), after this report. His direction for any future version: not Gaussianising activations; instead make activations behave like symbolic variables following known rules (expectation-maximization analogy). The parking is recorded in outbox/OPUS-MATS-CONTEXT.md (14:47Z line) and outbox/pending-discussion-kelvin.md, not in the report. Nothing was running when the report was written (all VMs deleted).

Could not be determined when extracting: Whether any review happened outside the files I checked. If a registered, hashed measurement without review counts as 'numerical evidence' for the README, that is the alternative label.

### hardness

Report: `hardness-mean-estimation-2026-10-29.md` (lanes/hardness/). Final state: 2026-10-29 (report states no time; dated log marks it final at 19:48Z).

Headline: Black-box: sampling is optimal up to ~4x (proven). White-box worst case: no deterministic estimator matches sampling under #NSETH. For random He-ReLU nets at depth ~ width no general lower bound is possible with current tools.

Status: **proved**. proved only for black-box and worst-case settings (white-box part under #NSETH / cited IKW theorem); for the actual target (random nets, average case) the result is 'no bound, open'. Proofs AI-written, audited by Gemini 4 Argon and GPT-6 (gpt-6-astra), not human-checked. Measured section 6.3 unreviewed and not pre-registered.

Failed approaches (6):

1. **Proving an average-case lower bound for random He-ReLU nets**
   - Tried: Deep math/TCS attempt across black-box, white-box worst-case, cryptographic and average-case formulations
   - Outcome: No general lower bound; Proposition 3.5 shows a hard-coded input set is a deterministic estimator matching sampling on average over the weights
   - Why it failed: an impossibility needs a formal definition of 'mechanistic'; determinism is no restriction on average over random weights; worst-case barriers do not apply to random nets
   - Rules out: Excludes a proof of hardness for 'deterministic' or 'sample-free' estimators as such on random nets. Does NOT exclude lower bounds for a formally restricted class, and does not show estimation is easy.
   - Evidence: proven. Source: Summary; sections 3.5, 9
2. **ARC factorized K = 3 cumulant closure at depth proportional to width**
   - Tried: ARC's own code, widths 32-256, depth = width/8 and width/4, 8 seeds (3 at width 256), sigma = 0, exact FLOP counts, against plain MC at equal cost
   - Outcome: gain 2.16 / 0.80 / 0.38 / 0.08 at widths 32 / 64 / 128 / 256 at depth = width/8; 0.031 / 0.038 / 0.011 / 0.004 at depth = width/4 (a loss of 27-247x); cost 14-251x that of K = 2
   - Why it failed: not explained by a derivation; the report points to the mechanisms of 6.6-6.11 and 7.2 as a conjecture (6.A)
   - Rules out: Excludes the cumulant hierarchy's next order matching sampling at these sizes at depth proportional to width. Does NOT exclude other estimators, sigma > 0, or fixed depth.
   - Evidence: exploratory. Source: section 6.3 (second table)
3. **ARC K = 2 closure keeping an advantage as width grows at depth proportional to width**
   - Tried: ARC's K = 2 'simple', widths 32-1024, depth = width/8, /4, /2, 16 seeds (4 at width 1024), sigma = 0, against plain MC at K = 2's own cost
   - Outcome: geometric-mean gain falls from 2-8 at widths 32-128 to 0.65-1.1 at width 1024 (intervals include 1); slopes of log nMSE against log n are -0.4 to -0.8 against Monte Carlo's -1
   - Why it failed: not explained
   - Rules out: Excludes a growing K = 2 advantage on these data. Does NOT show K = 2 loses: it stays within about 3x of plain MC either way; one budget point, plain MC not the best sampler.
   - Evidence: exploratory. Source: section 6.3 (first table)
4. **Low-degree method as hardness evidence**
   - Tried: Logical analysis of whether the low-degree method applies to mu(W)
   - Outcome: It cannot give hardness evidence here
   - Why it failed: the target is computable to inverse-polynomial precision in randomized polynomial time, so there is no threshold to predict; efficient algorithms are not low-degree polynomials of W
   - Rules out: Excludes using low-degree failure as evidence of hardness for this problem. Does NOT exclude a fine-grained analogue, which the report calls 'exactly the open problem'.
   - Evidence: proven. Source: section 7, Proposition 7.1
5. **Pseudorandomness or standard cryptography as the source of hardness**
   - Tried: Propositions 3.1-3.4, Corollary 3.3, section 7
   - Outcome: Pseudorandom functions have predictable means; undetectable planting cannot change the distribution of the mean; sampling is polynomial at every inverse-polynomial precision
   - Why it failed: pseudorandomness makes means easy, not hard
   - Rules out: Excludes polynomial-versus-superpolynomial hardness at inverse-polynomial precision and 'deep critical nets act like PRFs' as a mechanism. Does NOT exclude fine-grained hardness from structured long-range dependence.
   - Evidence: proven. Source: sections 3, 5 (intro), 7
6. **Restricted layer-local descriptions on random He-ReLU nets (ignore early layers; per-layer surrogates of fixed accuracy; fixed-order gain expansions; independent-neuron closures)**
   - Tried: Theorem 6.5, Lemma 6.10, Proposition 7.2, Proposition 6.11
   - Outcome: Each loses a constant fraction or is worth O(1) samples at depth proportional to width, for a specific observable
   - Why it failed: the output scale fluctuates multiplicatively and is shared across inputs; scale errors never contract in bias-free ReLU nets
   - Rules out: Excludes these specific classes for the quadratic output-scale observable. Does NOT transfer to ARC's per-neuron means (the report says no transfer is proven) and is not an impossibility proof.
   - Evidence: proven. Source: sections 6.1-6.2, 7; section 8 table

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (3):

- Withdrawn; self (after Gemini and GPT-6 reviews): Retracted or narrowed: a claimed parameter-count ceiling on black-box hardness (false, a 4-unit family suffices); 'advice independent of the context carries no information' (false); a per-scale summation assumption (replaced by joint JSH); the accumulation corollary stated as proven (now Heuristic 6.9'); an O(sigma^2) noise claim in 6.7 (false, O(sigma) near kinks); relative-RMS noise extension of 4.1(c) (removed); explicit-design claim in 3.5 (removed); extension of 6.5 to estimators seeing cheap early-layer statistics (removed); '1-3 samples' in 6.5 is now a measured upper bound. (report Summary 'Changed after review' and section 10)
- Corrected by bits-bounds-2026-11-01.md: The K = 2 slopes of section 6.3 describe ARC's truncated 'simple' recursion (linear off-diagonal covariance term only), not the exact Gaussian closure; they are not evidence about closures in general. (bits-bounds-2026-11-01.md, review summary ('from round 3, the hardness lane's K = 2 slopes ... describe ARC's truncated recursion') and its section 9 notes)
- Corrected by unrestricted-estimators-2026-10-31.md: Narrows the baseline, not a theorem: plain MC is not the best sampler at depth proportional to width (a multilevel shared-trajectory sampler gains Omega(n/log^2 n) under cost hypotheses), so the measured comparisons of 6.3 against plain MC understate the bar. The hardness report already lists 'plain Monte Carlo, not the best black-box sampler' as a limit. (overnight-report-2026-10-29.md 14:28Z (31 Oct); unrestricted-estimators section 3.7; summary-2026-10-31.md)

Not finished: Whether any polynomial-time estimator beats sampling by a factor growing with width at depth proportional to width; a proof that ignoring the last layers fails; a quantitative version of 5.2(1); whether JSH holds for any standard construction; a bound when the estimator also sees cheap statistics of the early layers; narrow nets uniform in depth.

Could not be determined when extracting: The report does not name the model that wrote the proofs. I could not tell from file times alone whether the final first table of 6.3 (16 seeds) matches what any reviewer saw.

### lyapunov-dimension

Report: `lyapunov-dimension-2026-10-29.md` (lanes/lyapunov-dimension/). Final state: 2026-10-29 ~21:20Z.

Headline: Per input path the count is small (about 24 directions at 256x64, not the heuristic 75), but one block for all inputs cannot use it; 'the best we can hope for' is not established.

Status: **numerical evidence**. Theorems A-D proven (AI-written; reviewed by GPT-6 and Gemini; not human-checked), but the headline counts at depth proportional to width are measured; oracle addendum pre-registered; the composition test was refuted by its written rule and left unresolved.

Failed approaches (6):

1. **One fixed block for all inputs using per-path Lyapunov concentration**
   - Tried: 256x64, net 113 (and 114), cuts 32 and 48, 2048 paths: tail of the input-averaged sensitivity M against the single-path tail
   - Outcome: 185 of ~195 live directions needed to leave 1e-4 of the energy outside, against 25 for one path
   - Why it failed: different inputs switch 6-10% of the gates differently per layer, so each input amplifies different directions; paths stay coherent for only about 6 layers
   - Rules out: Excludes a fixed linear block exploiting per-path Lyapunov structure. Does NOT exclude nonlinear codes, backward or observable-specific approximations.
   - Evidence: proven direction (Theorem D), measured size (exploratory). Source: section 5
2. **Input-dependent blocks per class**
   - Tried: 256x64, cut 32, nets 113-114, 8192 Jacobians, 64 classes by k-means on top-8 PCs, 4x4x4 cells, sign pattern of 6 uncertain gates, k-means on masks of 8 layers; cross-fitted
   - Outcome: tail at k = 24: 0.22 / 0.15 against 0.25 / 0.19 for one block (14-17% gain; 30% in-sample, biased) against 1.3e-4 for one path
   - Why it failed: within-class gate disagreement stays at 4-7% per layer; half-coherence over 32 layers would need about 2.5%
   - Rules out: Excludes the classings tried up to 64 classes. Does NOT exclude much finer classes (the 4e7-class figure is an illustration, not a claim).
   - Evidence: exploratory. Source: section 7
3. **Lyapunov (Newman) heuristic for the per-path count**
   - Tried: Gaussian products and ARC nets at n = 128-512, L'/n = 1/8-1/2
   - Outcome: heuristic 75 against measured ~24 at 256x64, L' = 32; Newman over-counts about 3x
   - Why it failed: at N < n the top singular value sits at the free-probability edge; ReLU halves the effective width
   - Rules out: Excludes Newman's large-depth formula in this regime. Does NOT prove the Fuss-Catalan count at depth proportional to width (measured only).
   - Evidence: exploratory. Source: sections 3, 4
4. **Composition: re-projecting the optimal block at every layer**
   - Tried: 256x64, nets 113-114, layers 32 to 63, PBO and PB at k = 32, 64, one chain per family at 2^20 and 2^21 particles
   - Outcome: T-E refuted by the written rule (net 113, k = 32: B_PBO32 = 2.5e-4 against B_PB32 = -6.9e-5); PBO64 composed sits at 1.8-3.6e-5, above 1e-5; raw errors lower for PBO in 8 of 8 comparisons
   - Why it failed: bias estimate dominated by chain-to-chain noise (EMP control -7.2e-5, -1.4e-5); 'likely but not verified'
   - Rules out: Excludes nothing firmly: unresolved. Does NOT show whether a larger block reaches 1e-5 when composed.
   - Evidence: registered. Source: section 13 (Composition)
5. **Representations of a k-dimensional joint law (particles, grids, moments, cells)**
   - Tried: survey of what this and sibling lanes ran
   - Outcome: none beats sampling
   - Why it failed: particles are sampling in k dimensions; grids cost exponentially in k; moment closures accumulate error at the critical point
   - Rules out: Excludes the representations tried. Does NOT bound algorithms: 'the cost of those schemes, not a lower bound'.
   - Evidence: post hoc. Source: section 10.2
6. **Pathwise linear response for family scrambles**
   - Tried: 256x64, cut 32, net 113, 256 paths, perturbations eps = 1e-3 to 3e-1 along residual PCs
   - Outcome: median pathwise nonlinearity 0.17 at eps = 1e-2 and 0.76 at 3e-1, while PB_k scrambles move paths by eps ~ 0.2-0.6
   - Why it failed: gate flips re-route each path's response
   - Rules out: Excludes pathwise linearisation at the families' scale. Does NOT test the second half of approximation (A1).
   - Evidence: exploratory. Source: section 8

Our own registered predictions that failed (1):

- T-E (pre-registered, composition): REFUTED by the written rule at net 113, k = 32 (B_PBO32 = 2.5e-4 against B_PB32 = -6.9e-5); the report judges the estimate noise-dominated and the question unresolved.

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (1):

- Withdrawn; self (after GPT-6 and Gemini reviews): Counts at L' proportional to n were presented as proven, now MEASURED; a first fix claimed the radial row has \|r\|^2 = O(1), it is about L' + 1; section 10 and the summary no longer say that nothing beats sampling, and a QMC argument was removed; the mechanism reading of beta ~ 1 was dropped; 'O(1)' in width replaced by 'roughly stable over 128-512'; in the addendum an overclaim that composition 'needs more than 64' directions was removed. (report section 12)

Not finished: Several composition chains per family (to settle T-E); an amplitude sweep; per-net bootstrap and held-out validation of the association; a trace-weighted single-path tail for net 114; a joint-limit theorem for counts at L' proportional to n; a bound on s_1(J)/s_1(Jhat). A CPU replicate was stopped after two families.

Could not be determined when extracting: The report does not name the model that wrote the proofs. On the exp(c k*) chain: this lane supplies the count k* = N_surv ~ n G/(2 L') that the premise is stated in (cut-rank section 3 and kstar-frames P1 use it), but it does not state the premise itself; its only exponential-in-k remark is that grids cost exponentially in k, 'the cost of those schemes, not a lower bound' (section 10.2). So no correction entry is recorded here for that chain.

### random-phases

Report: `random-net-phases-2026-10-29.md` (lanes/random-phases/). Final state: 2026-10-29 (runs finished and checked 16:21Z per work/random-phases/STATUS.txt).

Headline: Chaotic nets: the last 24-40 layers fix E[output], so a backward Gaussian stand-in works. Critical He-ReLU (ARC's family) barely forgets by depth 64 and an input-independent backward stand-in fails (nMSE 0.07-57).

Status: **numerical evidence**. registered predictions, one GPT-6 review of the width-256 snapshot; single nets, one or two seeds, depth <= 64; width-64 results added after the review; several registered thresholds missed.

Failed approaches (7):

1. **Input-independent backward description at the critical point (mean-field Gaussian stand-in)**
   - Tried: He-ReLU width 256, depth 64, seed 0; N(m 1, v I) with mean-field moments placed k layers before the output and pushed by 2^14 paths through the real layers; sigma = 0, 0.001, 0.01, 0.1; also rescaled to the true layer RMS (MFr)
   - Outcome: nMSE 0.07-57 at sigma <= 0.01 for k up to 62 (rescaled: 0.09-8.1); only the depth-1 stand-in (k = 63) reaches 1e-4
   - Why it failed: the finite-width overall gain is remembered through positive homogeneity; rescaling removes up to 13x of the error but not all, so scale is only part of what is missing
   - Rules out: Excludes an input-independent backward description for critical He-ReLU at these sizes. Does NOT exclude a weight-dependent one (oracle moments reach <= 1.3e-3).
   - Evidence: registered. Source: section 3
2. **Backward stand-in for critical tanh**
   - Tried: critical tanh, width 256, depth 64, sigma 0-0.1
   - Outcome: no k below 63 reaches 1e-3 at sigma <= 0.01; at sigma = 0.1 only k* = 62
   - Why it failed: critical nets barely forget
   - Rules out: as above, for critical tanh
   - Evidence: registered. Source: section 3 table
3. **ARC K = 2 at the critical point against plain MC at equal cost**
   - Tried: width 256, depth 64, one seed, ARC FLOP count
   - Outcome: He-ReLU gain 1.26x (0.94x raw) at sigma = 0.01 with error growing from 8.3e-4 (depth 32) to 2.1e-3 (64); critical tanh 0.38x; at width 64 critical tanh 0.17-0.19x
   - Why it failed: closure errors are not contracted away at the critical point (they saturate after ~16 layers in chaotic nets)
   - Rules out: Excludes K = 2 as a clear win at the critical point at these sizes. Does NOT fix exponents: 'Two widths and one seed cannot fix exponents'.
   - Evidence: registered. Source: sections 3 (deductive version), 6
4. **K = 2 started from the mean-field stand-in on He-ReLU**
   - Tried: width 256, depth 64, MF start 40 layers before the output
   - Outcome: nMSE 13.8-13.9
   - Why it failed: the stand-in itself is wrong at the critical point
   - Rules out: Excludes this start. Not run with the rescaled stand-in at sigma = 0.1.
   - Evidence: registered. Source: section 3 (deductive table)
5. **Backward stand-in in the ordered phase without noise**
   - Tried: tanh sw2 = 1, sigma = 0, width 256
   - Outcome: mean vector right to 1.4% with 32 layers to go, but nMSE 4.8e3 because output variance is 4e-8 of its mean square
   - Why it failed: the output variance collapses, so the normalised metric explodes
   - Rules out: Excludes meeting ARC's nMSE metric there. Does NOT mean the mean is badly estimated in absolute terms.
   - Evidence: registered. Source: summary item 3; section 3
6. **Small noise as a way to shorten ARC's problem**
   - Tried: He-ReLU, sigma 0.001-0.1, depth 64
   - Outcome: 98-100% input share kept to depth 64 at sigma <= 0.003; only sigma ~ 0.1 gives forgetting (L* = 13), where noise is most of the output variance
   - Why it failed: no contraction at the critical point
   - Rules out: Excludes small-noise forgetting for ARC's family up to depth 64. Does NOT cover depth > 64.
   - Evidence: registered. Source: sections 2.2, 6
7. **Test of a power law in 1/sigma for critical forgetting (P3)**
   - Tried: sigma grid 0.001-0.1
   - Outcome: not testable: one finite increment for He-ReLU, none for critical tanh
   - Why it failed: L* exceeds depth 64 at most sigma values
   - Rules out: nothing
   - Evidence: registered. Source: section 5

Our own registered predictions that failed (10):

- P6 ordered with noise: predicted k*(1e-3) >= 40 at sigma = 0.1 and beyond 64 at sigma <= 0.01; got 36 and 56.
- P7 He-ReLU MF nMSE >= 1e-2 for every k <= 63: missed at k = 63 (8.9e-5 at sigma = 0.01, 1.0e-4 at 0) and at sigma = 0.1 from k = 56 (3.6e-3).
- P7 critical tanh reaches 1e-2 only at sigma = 0.1 if at all: missed (2.4e-3 at k = 63 at sigma = 0 and 0.01).
- P7b MFr lowers MF's error >= 3x at k >= 32, sigma <= 0.01: missed (0.93x at k = 48, 2.2x at 56).
- P8 ordered, sigma = 0.01: K = 2 from MF wins >= 10x at some k: missed (0.12x at k = 40; larger k not run).
- P8 chaotic within a factor 3 either way: missed in kprop's favour (6.0x and 87x at k = 40).
- P8 full K = 2 >= 1e-3 at depth 64 for chaotic and critical: chaotic missed (3.3e-4, 4.5e-5); critical missed at sigma = 0.1 (tanh 9.4e-4, He-ReLU 1.7e-4).
- P9 participation ratio 2-4 at depth 32: narrowly missed (4.04-4.17); near-boundary fraction at width 64, depth 64: 0.08 against 0.12.
- P4 TV_G >= 0.5 wherever R >= 0.01: missed for He-ReLU at sigma = 0.1 (threshold 6.7%).
- P3 He-ReLU R(0 -> 32) at sigma = 0.1 in 0.15-0.25: mixed (seed 0 gives 0.105, outside).

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (2):

- Withdrawn; self (after the GPT-6 review): Full-law forgetting was overstated (a noiseless tanh net with square Gaussian weights is injective): claims now cover only E[output] and output variances. M1 conclusions rewritten as hypotheses. The k = 63 point had been excluded after the fact and is now scored as a miss of P7. 'Relative error' was the squared relative error (1.4%, not 0.02%). '11-19 layers' corrected to 11-28. MM was not <= 3e-5 everywhere. The oracle MM numbers below about 1e-4 should not be read as exact. (report section 7)
- Superseded by hardness (hardness-mean-estimation-2026-10-29.md section 6.3): My reading; neither report says 'superseded'. The two-point, one-seed statement that He-ReLU K = 2 'only keeps pace' with plain sampling along depth = width/4 (1.6x at 64x16, 1.3x at 256x64) is replaced by a 16-seed sweep to width 1024 with a slowly shrinking gain. (hardness report section 6.3; this report section 2.4)

Not finished: Cross-fitted oracle moments (independent paths) not done. Whether a weight-dependent backward description works at the critical point is open. Runs trimmed by Amendments 2, 4, 5 (width 64: one seed; backward runs at sigma = 0 and 0.01 only).

### gate-entropy

Report: `gate-entropy-2026-10-29.md` (lanes/gate-entropy/). Final state: 2026-10-29 15:51Z.

Headline: AlgZoo RNNs need only 2.3-7.4 merged gate bits per step. Random depth-32 MLPs have gate entropy proportional to width (28-40 bits at layer 32, width 256) and no merging was found at width >= 128.

Status: **numerical evidence**. registered census, one GPT-6 review before the final claims; achieved sizes and estimated brackets, not bounds; one weight seed per random-MLP configuration; no family was built.

Failed approaches (6):

1. **Merging gate patterns by a greedy decision tree on random depth-32 MLPs**
   - Tried: ARC He-ReLU and chaotic tanh, widths 128-256, sigma = 0.01, one layer at a time with the rest exact, 1,024-4,096 tree samples, tolerance 1% of answers changed (10% of output spread)
   - Outcome: not reached at width >= 128; at width 256 the tree still changed 92-100% of answers at 8.0-8.4 bits and bias nMSE stayed >= 6e-3 at 8 bits
   - Why it failed: 'the tree ran out of samples or budget'; the report gives no structural reason
   - Rules out: Excludes this tree within 8-10 bits. Does NOT exclude other mergings or a factored discrete part.
   - Evidence: registered. Source: summary item 3; section 4
2. **Merging on the Phase B PFN**
   - Tried: L2_s0.05, layers 1 and 2, 1,024 tree samples, tolerance 0.0063 on the predictive mean
   - Outcome: layer 1: 90% of answers still change at 8.4 bits (428 leaves); layer 2: 18% at 8.3 bits (393 leaves)
   - Why it failed: merging preserves the population average but not the per-episode deviation from Bayes
   - Rules out: Excludes a small merged discrete part at this tolerance with this tree. Does NOT bound other methods.
   - Evidence: registered. Source: section 3
3. **Merging at late steps of the wide AlgZoo RNNs, and at ARC's 0.2% bar**
   - Tried: W32 steps 9-10, W64 steps 7-10 at 1%; W32 steps 5-10 and W64 steps 4-10 at 0.2%; 8,192 tree samples
   - Outcome: stopped with 1.0-2.5% of answers changed at 8.5-9.6 bits
   - Why it failed: the tree ran out of its 8,192 training samples
   - Rules out: nothing; unmeasured within the budget
   - Evidence: registered. Source: section 2
4. **Merging under larger noise**
   - Tried: ARC width 64, sigma = 0.1, depth 32
   - Outcome: E3(1%) not reached at any layer (48-99% of answers changed at 10 bits)
   - Why it failed: the noise-driven part of the pattern is large
   - Rules out: Excludes this tree at 10 bits. Not a bound.
   - Evidence: registered. Source: section 4
5. **A boundary-exact family that lists gate classes for ARC's 256x32 target**
   - Tried: arithmetic from the measured entropies and the conditional Fano illustration
   - Outcome: about 2^25 classes at layer 32 and 2^170 at layer 1; 2^25 x 256^2 is about 2e12 FLOPs per layer against ARC's 2.7e11
   - Why it failed: class count, if nothing merges much better
   - Rules out: Conditionally excludes a class list. Does NOT exclude a factored discrete part (an autoregressive-logistic model fits layer 1 within 24-28% of the lower estimate).
   - Evidence: post hoc. Source: summary (implications)
6. **Capacity bound C_l = (d/2) log2(1 + 1/sigma^2) as a limit on gate entropy**
   - Tried: all nets
   - Outcome: 159-2,214 bits, above the gate count m in every net
   - Why it failed: it bounds only the input-driven part and is loose; geometry, not capacity, keeps RNN entropies low
   - Rules out: Excludes the capacity formula as a useful bound here.
   - Evidence: registered. Source: summary item 4

Our own registered predictions that failed (8):

- P2: H(G\|X) < 1 bit everywhere: miss for W32 (steps 2-4) and W64 (steps 2-5), up to 3.5 bits.
- P3: W32 D within 50-95% of m only at steps 2-5; W64 within 30-90% only at steps 2-3 ('mostly a miss: the wide nets are not sparser').
- P6: H(G\|X) at layer 32 below 0.5 bit at sigma 0.001: miss (0.59).
- P7: ordered H(G) < 1 bit at every layer: miss at layers 1-2 (11.8, 8.9); ordered D <= 5: miss at layers 24 and 32 (37 and 128).
- P1: covariance bound below m for ARC width 64, sigma 0.1 at depth >= 16: only partly (79 at layer 16).
- P5: 'k(agree) above k(var)' fails where they are equal (step 1 everywhere, T16 step 2).
- Amendment 1: E3(0.2%) <= H(G) - 0.3 at most steps: 6 of 10.
- P8: layer-1 lower bound >= 20 rests on the approximate collision bound (27*); the plug-in gives 15. E3(1%) <= 8 for layer 2 unmeasured.

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (1):

- Withdrawn; self (after the GPT-6 review): E3 checkpoints had been chosen on the held-out set that measured them (now re-evaluated on fresh samples); the claim that this establishes an affordable boundary-exact family for AlgZoo was removed; 'E3 grows linearly' replaced by what was measured; brackets relabelled as estimated; 'Capacity never binds' was wrong; D had been presented as boundary proximity; the layer-1 bound had been called rigorous; chaotic noise dominance marked unresolved. (report section 7)

Not finished: Whether a factored discrete part can be propagated layer to layer; two width-256 sigma points and four low-priority nets were dropped (Amendments 2, 3); chaotic-tanh mean merging not re-checked on fresh samples; nothing about rare-event accuracy.

Could not be determined when extracting: summary-2026-10-31 says a claim that 'noise bits are rare' was wrong; I could not find whether that claim came from this lane (this report itself says the noise-driven part grows with depth).

### cut-rank

Report: `cut-rank-lower-bound-2026-10-30.md` (lanes/cut-rank/). Final state: 2026-10-31 (report title 30-31 October; dated log marks it final at 00:39Z).

Headline: Premise 'a linearly read front summary needs exp(c k*) numbers' is false: the count is polynomial in width at fixed depth and eps. Proven instead: r(eps) = Theta(eps^(-2(n-1)/3)) at fixed architecture, with tiny constants.

Status: **negative result**. the refutation and the replacement law are themselves labelled PROVEN, but only for one-way linear summaries; key proofs by AI co-prover gpt-6-astra, checked by the lane agent (Claude Opus 5.5) and reviewed by gpt-6-astra in a fresh session; not human-checked; measurements registered, their main reading post hoc.

Failed approaches (9):

1. **Lower bound r(eps) >= exp(c0 k*) for one-way linear summaries (target T1)**
   - Tried: proof attempt with gpt-6-astra as co-prover, three rounds
   - Outcome: false as a law: r(eps) <= C(n+m, m) with m ~ 1/(eps^2 Vbar), polynomial in width at fixed depth and eps, while k* ~ n G/(2L') grows with width
   - Why it failed: the back's weight law is rotation invariant, so averaged over backs only a 1-D kernel remains and truncating it at fixed harmonic degree gives a polynomial-size protocol
   - Rules out: Excludes exp(c k*) as a universal law for one-way linear summaries. Does NOT refute every narrower version of the premise, does NOT cap the rank at 256x32, and says nothing about running time.
   - Evidence: proven. Source: section 3
2. **The lane agent's own registered predictions on depth, width and front depth (P1, P2, P4)**
   - Tried: 17 configurations, n = 8-64, 256-512 fronts, raw in-sample estimator
   - Outcome: P1: ratio 9.9 against a predicted <= 2; P2: r = 27, 60, 23, 30 (flat) against a predicted growth >= 4; P4: raw r = 9, 15, 3 at c = 2, 8, 64
   - Why it failed: partly the raw estimator's energy undersampling; scale-normalised (post hoc) P4 becomes monotone as predicted
   - Rules out: The data support 'rank falls with back depth and is flat in width at fixed depth/width' at eps = 0.1. Does NOT describe the population operator past synchronisation.
   - Evidence: registered. Source: section 5
3. **Raw registered estimator in synchronised (merged) configurations**
   - Tried: five configurations such as (8,64,8), (8,64,64), (16,128,16)
   - Outcome: sample energy E a^2 = 8e-12 to 2e-3 against an ensemble value of 1; only 2-16 fronts and 1-8 backs carry energy; P3 cannot be scored validly
   - Why it failed: network energy is heavy tailed and the samples missed the rare high-energy networks
   - Rules out: Excludes reading the raw ranks there as population values; the 'collapse' is withdrawn.
   - Evidence: post hoc. Source: section 5 (Energy sampling), section 7
4. **Seeing the asymptotic eps-exponent at resolvable precision**
   - Tried: secant exponents from eps = 0.3 to 0.03
   - Outcome: 0.4-1.5 raw, about 0.6-0.7 scale-normalised at F = 2048, slower than 1/eps^2; ranks at eps = 0.1 are below the 100 samples they replace except in four configurations
   - Why it failed: 'Theorem 4(c)'s exponent belongs to eps far below what we can resolve'
   - Rules out: At practical precision the measured linear summaries are not larger than sampling. Does NOT contradict the asymptotic theorem.
   - Evidence: registered. Source: section 5 (Reading)
5. **exp(c k*) as a fit to the measured ranks**
   - Tried: log r(0.1) over 17 configurations
   - Outcome: R^2 0.56 for exp(c k*) against 0.95 for a power law in depth ratios
   - Why it failed: not explained beyond Theorem 1
   - Rules out: k* is a poor descriptor of the measured ranks. Raw estimator, post hoc fit.
   - Evidence: post hoc. Source: section 5 (Reading)
6. **Crux lemma: the back's value function on the k* relevant directions has exp(c k*) independent components**
   - Tried: 256 backs, k-dimensional slices through a cut state at (16,8,8) and (32,8,8), top-k relevant against random directions
   - Outcome: counts fit C(k+D, k) with D = 3.2-5.4 at eps = 0.1, exponential in k only while k < D; relevant and random slices similar at k <= 4 (for example 60 against 67)
   - Why it failed: a slice inside one activation cell is affine, so its rank is at most k+1
   - Rules out: No sign that relevance adds structure at k <= 4. Does NOT show that it adds none (comparison not dimension-matched at larger k).
   - Evidence: registered design, post hoc reading. Source: section 6
7. **Cap fronts as a toy for an exponential in k**
   - Tried: exact spectrum, k = 2-12, spreads 0.03 and 0.1, eps = 0.1
   - Outcome: fixed spread and fixed eps give no exponential in k
   - Why it failed: such fronts approach uniform as k grows (co-prover, PROVENANCE round 2)
   - Rules out: Excludes this toy as support for exp(k).
   - Evidence: proven. Source: section 4(d)
8. **Linear readouts of Monte Carlo first moments at the cut**
   - Tried: least squares on held-out fronts, n = 8-64
   - Outcome: leaves 8-9% of Vbar at n = 8 and 21-74% at n = 16-64
   - Why it failed: not explained
   - Rules out: First moments read linearly are not enough. The comparison with ARC's K = 2 ('15-70x') is withdrawn as unmatched.
   - Evidence: registered (P6) plus post hoc. Source: section 10
9. **'Almost always for a fixed net'**
   - Tried: quantifier analysis with the co-prover
   - Outcome: 'on most nets every summary chosen after seeing the net fails' is false; 'for every predetermined summary, most nets defeat it' needs an unproven small-ball condition
   - Why it failed: an ensemble bound only controls the mean of the per-net error
   - Rules out: Excludes the strong per-net form. The weak form stays a conjecture (C4).
   - Evidence: proven (first clause), conjecture (second). Source: section 8

Our own registered predictions that failed (4):

- P1 (back depth): predicted r(L'=4)/r(L'=32) <= 2; got 9.9 on the registered raw estimator (3.8 scale-normalised, post hoc, inconclusive).
- P2 (width at fixed depth/width): predicted growth >= 4 from n = 8 to 32; got r = 27, 60, 23, 30 at n = 8, 16, 32, 64 (ratio 0.85).
- P4 (front depth, n = 8, L' = 8): raw r = 9, 15, 3 at c = 2, 8, 64: refuted (scale-normalised 22, 44, 54 is monotone, but post hoc).
- P3 (synchronisation): 4 of 5 raw ranks <= 5, 'collapse' by the rule, but the measurement fails the energy-sampling check, so it cannot be scored validly.

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (3):

- Corrected by cut-rank-ext (cut-rank-ext-2026-10-31.md): Narrowed, not corrected: the theorem r(eps) = Theta(eps^(-2(n-1)/3)) for one-way linear summaries stands unchanged. The extension shows it cannot be extended: on the rare ray event that carries the genuine-ensemble bound, mean propagation with n numbers is exact; Lipschitz / C^k readouts need a number of reals that does not grow with 1/eps; two real-valued rounds are exact. So the exponent belongs to linear and bounded-degree readouts only. (cut-rank-ext report, summary items 1-4 and section 2)
- Withdrawn; self (draft of 00:21Z, after the final GPT-6 review): Withdrawn: the collapse of the rank after synchronisation (raw criterion was dominated by rare high-energy networks the samples missed); the '15-70x' comparison of ARC's K = 2 with the best linear readout (not matched). Corrected: 'k* averages out' (only per-path orientations vanish; k* alone does not determine the rank); 'top-k relevant directions = random ones' (now: no sign of a difference at k <= 4); 'D ~ eps^-2/3' (no such law established); Lemma C's rank bound and Theorem 1's normalisation (FORMAL.md erratum). (report sections 5, 7, 10, 12; overnight-report 00:21Z against 00:39Z; summary-2026-10-31.md 'Two draft cut-rank claims were withdrawn')
- Corrected by kstar-frames (kstar-frames-2026-10-30.md): Section 8 here quotes the kstar-frames lane as 'under about 2.5% of gates differ, i.e. angle about 0.08 rad': that is the lane's pre-data surrogate. Its final measurement is about 1.4/L' rad for 90% sensitivity (0.09-0.11 rad at 16 layers to go) with 2-7% of gates differing per layer. (kstar-frames report section 4; overnight-report 23:46Z)

Not finished: 'The post-hoc F = 2048 identical-front control is still running' (Handoff). Conjecture C1 (precision window with uniform constants) untested; independent ensemble replications with rare-event weighting not done; eps = 0.01 unresolved; held-out ranks exhausted ('+') in five configurations.

Could not be determined when extracting: tractable-gates re-measured ReLU ranks at the same (n, c, L') with a different design (per-layer normalised nets, 256 columns) and got raw r_in(0.1) = 9 at (8,4,4) and 37 at (16,8,8) against 27 and 60 here; neither report reconciles the two.

### cut-rank-ext

Report: `cut-rank-ext-2026-10-31.md` (lanes/cut-rank-ext/). Final state: 2026-10-31 (re-check 12:27-12:30Z; dated log marks it final at 12:33Z).

Headline: No, as stated: the law survives only for bounded-degree readouts and as bit counts; Lipschitz / C^k readouts and real-valued two-round protocols need counts that do not grow with 1/eps, so size bounds cannot cover ARC's closures.

Status: **negative result**. the breaking constructions and surviving bounds are labelled PROVEN; many are by AI co-prover gpt-6-astra, checked by the lane agent (Claude Opus 5.5) and reviewed by gpt-6-astra in a fresh session; not human-checked; all asymptotic in eps at fixed architecture.

Failed approaches (8):

1. **Extending the (1/eps)^Theta(n) lower bound to nonlinear readouts**
   - Tried: proof attempt over a ladder of decoder classes (polynomial, analytic, C^k, Lipschitz, continuous, bits)
   - Outcome: fails for every finite smoothness: Lipschitz needs between n(n+1)/2 and n^2 c numbers, independent of eps; a continuous decoder needs 1
   - Why it failed: the kink functions form an n-dimensional curved family whose linear span is infinite-dimensional; only dimension, not rank, survives a nonlinear readout
   - Rules out: Excludes any precision-power size bound for nonlinear readouts. Does NOT exclude a running-time lower bound in an explicit model.
   - Evidence: proven. Source: summary items 1, 4; section 2
2. **Extending the bound to bounded back-and-forth**
   - Tried: real-valued multi-round protocols
   - Outcome: two rounds are exact: the back sends its n^2 d weights and the front returns the n answers
   - Why it failed: real numbers carry the weights
   - Rules out: Excludes real-number round bounds. Bit bounds (n log2(1/eps)) and non-branching polynomial protocols survive.
   - Evidence: proven. Source: section 3
3. **Covering ARC's ReLU cumulant propagation by a size bound**
   - Tried: coverage map of ARC's published estimators against the four classes
   - Outcome: not covered: only linear deduction-projection estimators are; for cumulant propagation only the exact-input bias floor and conditional dimension bounds apply
   - Why it failed: ARC's ReLU updates are neither polynomial nor uniformly Lipschitz, and unrestricted communication defeats any precision-power separation
   - Rules out: Excludes an information-theoretic separation between ARC's real method and sampling from these tools. 'What is left is running time.'
   - Evidence: proven plus sourced table. Source: summary item 8; section 7
4. **ARC's K = 2 closure fed estimated cut mean and covariance on merged fronts**
   - Tried: (n, c, d) = (8, 64, 8), 256 test fronts (211 alive), 32 backs, 8,192 input directions per front
   - Outcome: leaves 0.71 Vbar (median 0.11) against 0.00018 for mean propagation with 8 numbers and 0.091 for the in-sample best linear estimate with 9; inside the window ARC2 loses to a held-out linear readout at width 8
   - Why it failed: not separated: fed the same mean with zero covariance the same code is mean propagation; moment-estimation effects not fully excluded
   - Rules out: Excludes K = 2 from sample-estimated cut moments on these merged fronts. Does NOT concern ARC's full algorithm on its own inputs.
   - Evidence: registered (unit-scaled rerun is Amendment 1). Source: section 6, NC1
5. **ARC's K = 3 closure with the fourth-cumulant trace**
   - Tried: same fronts, rerun under Amendment 2
   - Outcome: unstable: median per-pair errors 9.5 to 7.7e6 Vbar; 32-88% of (front, back) pairs above 100 Vbar
   - Why it failed: 'Whether the closure or amplified moment-estimation noise causes this is not separated.'
   - Rules out: nothing firm
   - Evidence: post hoc. Source: section 6, NC1
6. **Identifiability of front weights from back-observed means (NC3)**
   - Tried: (n, c) = (4,2), (4,3), (6,2), (6,3); 64 backs; 65,536 inputs
   - Outcome: inconclusive: only 7-8 of 22, 3-6 of 34, 11-16 of 51 and 8-12 of 81 directions resolved at 10x the noise; spectra fall smoothly with no gap
   - Why it failed: Monte Carlo precision
   - Rules out: nothing; the lane's conjecture on generic rank was separately shown false by the co-prover
   - Evidence: registered (P7 failed). Source: section 6, NC3
7. **Decoders with budgets fixed in advance**
   - Tried: amplitude or Lipschitz constant and radius fixed independently of eps
   - Outcome: every message size leaves an error floor
   - Why it failed: the target is unbounded under Gaussian weights
   - Rules out: Excludes fixed-budget classes as meaningful; all bounds need budgets that grow subpolynomially.
   - Evidence: proven. Source: section 1 (Budgets)
8. **'Nothing beats sampling' as a black-box time statement at fixed width**
   - Tried: literature (Bakhvalov; Novak)
   - Outcome: false: randomised cubature for Lipschitz integrands has error N^(-1/2-1/m)
   - Why it failed: standard cubature rates
   - Rules out: Excludes the black-box fixed-n form. For white-box methods a time lower bound needs a complexity assumption.
   - Evidence: cited. Source: section 9

Our own registered predictions that failed (4):

- P2 (window: Err_MF >= 0.1): failed in all three configurations (0.031-0.059); mean propagation is better than expected.
- P3 (window: ARC2 < LIN2 in at least 2 of 3): failed, 1 of 3 (only (16,8,8)).
- P7 (every non-symmetry direction resolved at 10x noise): failed in all four configurations.
- P6 (48 bits reach the target) held only after the post hoc correction: with the registered code it was not a 48-bit protocol.

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (1):

- Withdrawn; self (after the co-prover and the final review): Lane agent's analytic rate (log/loglog) was wrong, corrected to log(1/eps); its conjecture I1 on generic rank is false almost everywhere; its C^k construction gives only C^(k-1,1); the analytic upper bound was restricted to radius ratio 1/2; the registered NC2 code used an uncounted front scale and was not a true bit protocol (rerun, same numbers); the registered ARC3 runs omitted the fourth cumulant (rerun: unstable); 'exact moments' corrected to estimates; ARC2 on merged fronts was 1.5e9 Vbar before Amendment 1 (variance-floor artifact), 0.71 after. Milestone figures changed: Lipschitz lower end from n-1 to n(n+1)/2; 'ARC K=2 with exact covariance' is in fact fed estimated moments. (report sections 2, 6, 11; overnight-report 11:05Z, 11:50Z against 12:33Z)

Not finished: L1 a computational lower bound in an explicit model (not yet a precise target); L2 a polynomial bias rate for ARC's closure; L3 from exact inputs to the full ARC algorithm; L4 a chart of dimension above n(n+1)/2; L5 sharp widths; L6 typical-network failure; L7 an explicit moment order. NC3 inconclusive. ARC3 instability unexplained.

### kstar-frames

Report: `kstar-frames-2026-10-30.md` (lanes/kstar-frames/). Final state: 2026-10-31 03:23Z.

Headline: Per input the k* frame follows the inverse-transpose layer map but is set by future weights. Across inputs a learned map recovers 93-99% of sensitivity, yet no method cleared the registered gate and no estimator was built.

Status: **negative result**. registered gate failed (Q3 not run); Propositions 1-2 proven for the noiseless net (AI-written, GPT-6 reviewed, not human-checked); measurements registered, GPT-6 reviewed twice; partial positive: a polynomial-size learned map captures most sensitivity.

Failed approaches (7):

1. **Push-forward transport of the frame by the layer Jacobian (covariant-Lyapunov recipe)**
   - Tried: He-ReLU, widths 32-128, depth 16 and 32, three nets each, 512 paths, sigma = 1e-3
   - Outcome: overlap 0.44-0.80 after one step and chance after eight (0.02 above chance on average)
   - Why it failed: push-forward converges to the past's expanding directions; the frame belongs to the future (Proposition 1c)
   - Rules out: Excludes forward transport by the Jacobian. Proven non-covariant for generic weights.
   - Evidence: registered (P2, P3 held) and proven. Source: section 2
2. **Any frame computed from the forward pass alone**
   - Tried: Proposition 2; forward QR frame on the noisy nets
   - Outcome: at most chance plus one direction (the state's own); measured at chance to within 0.01 on average
   - Why it failed: the future weights are rotation invariant given the past
   - Rules out: Excludes past-measurable rules. Does NOT cover rules that use future weights (marginal gates, stored inputs, learned maps, backward passes) or two-way protocols.
   - Evidence: proven (sigma = 0), registered (P4 held). Source: section 2
3. **Dual (inverse-transpose) transport over several layers**
   - Tried: same nets, 1 and 8 steps
   - Outcome: 0.99 per step when the active count does not grow, 0.81-0.89 when it grows (about half the steps); 0.05 above chance after 8 steps
   - Why it failed: newly active units put part of the frame in the null space of B_c^T; later steps do not recover it
   - Rules out: Excludes carrying a frame forward more than a few layers; each input's frames need its own backward pass.
   - Evidence: registered (P5 failed). Source: section 2
4. **Fixed frames and marginal-gate products across inputs**
   - Tried: 2048 held-out inputs per net, layer L/2
   - Outcome: captured sensitivity 0.87-0.90 (overlap 0.65-0.74) for the fixed frame, 0.80-0.87 for marginal gates; 9-16% of sensitivity left outside against 0.01% for the input's own frame
   - Why it failed: frames are input-specific
   - Rules out: Excludes one shared frame at the precision of the own frame.
   - Evidence: registered. Source: section 3
5. **Learned state-to-frame map**
   - Tried: MLP with two hidden layers of width 4n (41 thousand to 2.6 million parameters), up to 16,384 training inputs (8192 at n = 128), 2 nets per configuration
   - Outcome: captured sensitivity 0.93-0.99 but overlap 0.75-0.85; leaves 1.4-7% outside; passes the gate only at width 64, depth 16 (0.98 / 0.83); error falls like N^-0.1 to N^-0.25; four times more epochs changed nothing
   - Why it failed: overlap shortfall sits in the weak directions near the 1% cutoff; trained on captured sensitivity only
   - Rules out: Did not clear the registered gate (overlap >= 0.8 at widths 64 and 128, both depths). Does NOT exclude other objectives or architectures (not tried), and how the residual enters an estimator's error was not measured.
   - Evidence: registered. Source: sections 3, 6
6. **Atlas of stored frames**
   - Tried: 8,192-16,384 stored inputs, 90% captured sensitivity, layer L/2
   - Outcome: ball mass falls about tenfold per doubling of width (0.09, 0.013, 0.0012); at width 128, 13-92% of new inputs have no fitting frame among 8,192 (66-99% with 8 layers to go); heuristic count 10^5.7-10^6.05 (depth 32) and 10^9.2-10^10.1 (depth 16) at width 128 against a gate of 10^4
   - Why it failed: frames agree only within about 1.4/L' rad of state angle and the states' local dimension grows with width
   - Rules out: Excludes random finite stores of this size. These are 'not optimised atlases; an empirical zero is unresolved, not a population zero'. Does NOT decide exponential against polynomial growth.
   - Evidence: registered (finite stores) and heuristic (counts). Source: section 5
7. **Q3: an estimator in the moving frame**
   - Tried: pre-registered gate PREDICTABLE and COHERENT
   - Outcome: gate failed on both counts; not run
   - Why it failed: no method reached overlap 0.8 at width 128; atlas not resolved below 10^4
   - Rules out: Nothing about such an estimator's accuracy: it was never built.
   - Evidence: registered. Source: section 6

Our own registered predictions that failed (5):

- P5 (dual transport: 1 step O >= 0.85 and CS >= 0.97; 8 steps O >= 0.70 and CS >= 0.93): failed in 68 of 90 and 48 of 48 cells.
- P8 (fixed frames: O <= 0.65 marginal gates, <= 0.70 averaged-sensitivity frame): failed narrowly in all four configurations (O 0.66-0.74).
- P9 (learned map no better than the fixed frame + 0.05 CS, O <= 0.75): failed, better than predicted (paired gain +0.07 to +0.10 CS; O 0.77-0.83).
- P11 (two-replica formula within x1.5): failed in 2 of 144 cells.
- P13(b) (heuristic atlas >= 10^6 at width 128): held as scored (10^6.05) but not robustly at depth 32 (10^5.70-10^5.98 under other binnings or per-net radii).

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (2):

- Corrected by cut-rank-ext (cut-rank-ext-2026-10-31.md): Narrows the use of Proposition 2: it 'does not constrain two-way protocols, because the back can send the frame'. (cut-rank-ext report section 3)
- Withdrawn; self (after GPT-6 review): Covering scores had a float32 bug (captured sensitivity above 1; one case 2.155 against an exact 0.267), recomputed in float64; 'no predictable, shared map' replaced by 'none of the tested methods cleared the gate'; 'a few dozen frames cover 99% at every width' removed as unsupported; the scorecard had tested each net instead of net means (P2 now holds; P5 fails 68 of 90 and 48 of 48); P13(b) at depth 32 does not hold robustly; interim claim that the frame is 'carried exactly' by the inverse transpose is now 'exact when the downstream Jacobian has rank k*, approximate on the nets'. (report section 10; overnight-report 00:09Z, 01:16Z)

Not finished: Q3 estimator not run. Not done (declared in Amendment 2): the kernel-smoothed-reference diagnostic; learned maps at c = 8, 24 on net 401. Error amplification of dual transport not measured. Other training objectives and architectures not tried.

Could not be determined when extracting: The report does not name the model that wrote it.

### tractable-gates

Report: `tractable-gates-2026-10-31.md` (lanes/tractable-gates/). Final state: 2026-10-31 (second review ended 04:57Z; dated log marks it final at 05:01Z).

Headline: Asymptotically smooth gates need only polylog(1/eps) summary numbers (one back layer, scale conditions), but at tested sizes smoothness is not the main factor and the tested closure beat MC and RQMC on 0 of 45 trained nets.

Status: **negative result**. the asymptotic positive part is PROVEN UNDER scale conditions for one back layer only; author Claude Opus 5.5 (opus-mats-gates); theory checked by co-prover gpt-6-astra (7 claims of v1 wrong) and two gpt-6-astra reviews; last fixes not re-reviewed; registered, 8 of 15 predictions refuted in whole or part; not human-checked.

Failed approaches (9):

1. **Gaussian closure K2 on trained sorting nets**
   - Tried: 45 trained nets (free single-gate, pinned and noisy arms; width 16, 16 layers, 3 seeds), same network-evaluation budget, against MC and scrambled-Sobol RQMC
   - Outcome: beat both baselines on 0 of 45; beat MC alone on 6; RQMC more accurate by 6-31x (free gates) and 12-92x (pinned), medians
   - Why it failed: not explained
   - Rules out: Excludes the tested closure on these trained nets. Does NOT cover other estimators or summary sizes of trained nets (cut rank of trained nets not measured).
   - Evidence: registered (P11 first part). Source: section 5
2. **A gate that both learns like ReLU and gives a deductive win**
   - Tried: ReLU, softplus 1-16, GELU, SiLU, tanh, smooth step, noisy ReLU, pinned softplus ladder
   - Outcome: none: gates that learn like ReLU (GELU 0.91, SiLU 0.97, softplus16 0.99) leave the closure 1.4-3.8x behind MC and 13-31x behind RQMC; the only free gate whose closure beats MC on the median net (softplus1, 0.84) learns sorting 1.9x worse
   - Why it failed: lowering sharpness trades learnability for closure accuracy (11.7x to 1.3x against 1.0x to 1.5x loss)
   - Rules out: Excludes the tested family with the tested closure at 8k-19k parameters. Does NOT establish anything at 10M+ scale.
   - Evidence: registered (P12, P15 hold). Source: section 6
3. **Smoothness lowering practical cut ranks on random nets**
   - Tried: grid C at (8,4,4) and (16,8,8), 512 fronts, 256 columns, eps = 0.1
   - Outcome: softplus16 and smoothstep1 within 25% of ReLU on scale-normalised ranks; differences go with phase (chaotic GELU / SiLU 2.5-4x fewer, ordered softplus1 2x more, tanh 2.5x more); secant exponents 0.4-1.1 for every gate
   - Why it failed: below degree about (beta s / 2 pi)^2 a softplus is indistinguishable from ReLU; asymptotics not visible
   - Rules out: Excludes smoothness alone as the main factor at eps = 0.1. Phase was not isolated from splicing or scale.
   - Evidence: registered. Source: section 3 (grid C)
4. **Asymptotic advantage of smooth gates at usable precision**
   - Tried: computed ray-front ranks, widths 8 and 16, eps 0.1 to 1e-6
   - Outcome: at width 16 softplus, GELU, SiLU, SwiGLU and noisy ReLU lose to sampling at every resolved eps down to 1e-6; at width 8 only the softest gates win everywhere
   - Why it failed: 'The constants are large'
   - Rules out: Excludes a practical gain from the asymptotic exponent in this model. Numbers are not certified and some entries did not converge.
   - Evidence: computed. Source: summary item 2; section 2
5. **Closure on deep random nets**
   - Tried: grid K, widths 16-64, depths 2-16, 4 nets per cell
   - Outcome: at depth 16 only soft ordered gates win by the registered rule, with outputs nearly input-independent (variance 1e-5 of mean energy for softplus1)
   - Why it failed: the winning nets are nearly constant
   - Rules out: Excludes a non-degenerate deductive win at depth 16 at these widths.
   - Evidence: registered. Source: section 3 (grid K)
6. **SwiGLU and bilinear GLU without a pre-norm**
   - Tried: sorting MLP, registered recipe
   - Outcome: NaN: the residual stream explodes at initialisation; with a pre-norm 1.20x and 1.28x a pre-norm ReLU, and the pre-norm itself hurts sorting (0.134 against 0.103)
   - Why it failed: bilinear variance map is unstable (proven for bilinear only; SwiGLU's divergence is observed)
   - Rules out: These arms are not scored on trained nets (no closure through RMSNorm or GLU products).
   - Evidence: registered, then Amendment 3. Source: section 4
7. **Soft gates staying soft under training**
   - Tried: PFN Bayes task, 3 seeds, one L4
   - Outcome: softplus1's gate inputs grow 4-6x and softplus4's 2.2x against measured initial scale (post hoc); softplus1 has 2x GELU's KL
   - Why it failed: training sharpens soft gates
   - Rules out: On sorting the growth is modest (1.2-1.6x) and tanh's inputs shrink, so this is not general.
   - Evidence: post hoc (registered statistic scored separately). Source: summary item 6; section 4
8. **Smoothed ReLU under a heavy-tailed input scale**
   - Tried: the final review's counterexample, radius tail P(R > r) = r^(-5/2)
   - Outcome: noisy ReLU's geometric decay becomes k^-4 and the width-8 ray rank eps^(-7/3)
   - Why it failed: radial averaging destroys the fast spectral decay
   - Rules out: Excludes the polylog claim without scale conditions.
   - Evidence: proven (reviewer's counterexample). Source: section 2
9. **Bias-free tanh arm**
   - Tried: registered arm
   - Outcome: degenerate: odd net, E[output] = 0 exactly
   - Why it failed: symmetry
   - Rules out: Replaced by tanh with biases (Amendment 1) before data.
   - Evidence: registered amendment. Source: sections 1, 8

Our own registered predictions that failed (8):

- P1: no arm with sharpness >= 5 below 2/3 of ReLU's raw r_in(0.1): refuted at width 16 (SiLU 9, GELU 15 against 24.7).
- P5: (a) no K2 win at depth 16, width <= 16: softplus1 wins 3/4 at width 16; (b) K2/MC spread < 3x: spread >= 3x in 16/16 cells.
- P6: RQMC gain at N_eq >= 1.5x ReLU's for softplus1, GELU, SiLU at width 8: pooled 2.20, 0.51, 0.34; and gains >= 2 at widths 32-64.
- P8: pre-norm SwiGLU within 20% of pre-norm ReLU: 1.2002x, refuted by 0.0002 (within seed noise); the registered SwiGLU arm diverged.
- P9: training sharpens softplus1 and softplus4 on sorting by >= 1.5x: softplus4 1.41 (fails), softplus1 1.51.
- P10: PFN arms within 20-30% of GELU and sharpening < 1.5: KL means 1.62, 1.26, 1.54, 1.38 and 2.02 x GELU; softplus1 layer statistic 2.05-2.72.
- P11 second part: smooth arms' tail share at degree 8 >= 0.5x ReLU's: refuted for softplus4, SiLU, tanh, softplus1.
- P13 second part: pinned softplus1 >= 1.5x pinned ReLU: 1.497x, refuted by 0.003.

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (1):

- Withdrawn; self (after the co-prover and two GPT-6 reviews): Seven theory claims of v1 were wrong; the ray table was called exact (now convergence-checked, not certified); Hermite degree tails recomputed; tanh-with-bias phase mislabelled 1.34 (about 1.17); broad frontier and scale conclusions rewritten; the 10M+ sentence replaced; the registered comparison had costed ReLU's closure about 6x dearer, and with equal machinery (post hoc) ReLU does as well as or better than GELU, SiLU and softplus4. Milestone statements at 02:02Z ('exact worst-case ray-front model'; 'K2 loses to MC at depth >= 4 for every gate except softplus1') do not match the final tables. (report sections 2, 3, 8, 9; overnight-report-2026-10-29.md 02:02Z)

Not finished: Cut rank of trained nets (the missing 'trained summary' test); a closure through RMSNorm and GLU products; an error-matched closure comparison; whether smooth-front densities are square-integrable on average; unresolved entries of the constants table (softplus16 at fine eps, softplus4 at 1e-6).

Could not be determined when extracting: This lane builds on cut-rank (its eps-rank and ReLU law) without correcting it, so no correction entry links them. Why the ReLU ranks here (9 at (8,4,4), 37 at (16,8,8)) differ from the cut-rank lane's (27 and 60) beyond the stated design differences; the report calls the width-8 value anomalous (two backs carry 80% of the energy).

### stationary

Report: `stationary-regime-2026-10-31.md` (lanes/stationary/). Final state: 2026-10-31 (revised after the GPT-6 review of 14:18Z-14:25Z; dated log marks it final at 14:40Z).

Headline: The stationary state exists, is unique, sigma is a pure scale and the radius is an exact 1-D chain (proven with an AI co-prover); it is not easier to estimate: structure buys 2-8x constants that do not grow with width.

Status: **numerical evidence**. characterisation: PROVEN by the Claude author with the gpt-6-astra co-prover, not human-checked; estimation verdict: MEASURED and registered (HB 'no width-growing gain' holds; about 30 sub-predictions missed) on 2 nets per width; one GPT-6 review ('major revision', 14 findings applied), revision not re-reviewed

Failed approaches (8):

1. **Structured sampling for a width-growing gain in the stationary regime (RQMC on recent noise, antithetic noise, Gaussian-surrogate control variate, final-noise Rao-Blackwellisation)**
   - Tried: Model S, n = 8-256, seeds 1000 and 1001 (2 nets per width); antithetic to n = 1024; RQMC to N = 2^16 at n <= 32; gains as variance ratios at matched burn-in 8n, setup excluded
   - Outcome: Best gain 7.0, 4.4, 4.1, 3.0, 2.4, 2.4 at n = 8..256 (3.5, 3.1, 4.1, 0.8, 1.2, 2.4 if the structured runs are charged their actual burn-in). RQMC 4.1-8.0x at n = 8 falling to 2.1-2.6x at n = 128; antithetic 1.9-2.4x; control variate 1.3-2.0x flat; Rao-Blackwellisation 1.01-1.07x at n >= 64
   - Why it failed: Report's reading: the state is made by noise over about n layers with interaction order 2-4, and the 20-27% of variance that is even in the noise does not shrink with width. (The input-bits lane later attributes the RQMC decline to the growing number of coordinates, not to interaction order.)
   - Rules out: A width-growing gain from the measured methods. 'nothing is proven'; whether the absence is fundamental is left open.
   - Evidence: registered (HB holds; PB3 refuted; PB5, PB6 missed). Source: section 3.1
2. **RQMC rate improvement in the stationary regime**
   - Tried: Scrambled Sobol in recency order, N = 2^6 to 2^16 at n = 8-32 (Amendment B2)
   - Outcome: Variance exponent 1.19-1.22, 1.13, 1.10-1.12 over 2^6..2^12 falls to 1.04-1.06, 1.09-1.11, 1.03-1.10 over 2^10..2^16; the gain saturates (n = 8: 7.6, 8.0, 12.5, 7.7)
   - Why it failed: The higher early exponents were pre-asymptotic
   - Rules out: A better-than-1/compute rate from this RQMC at n <= 32 (fitted exponents carry about +-0.1; n = 256 not run).
   - Evidence: registered (PB10 hit). Source: section 3.1
3. **Burn-in multilevel (optimal finite-level allocation) to remove the burn-in cost**
   - Tried: 12 nets, n = 8-256, bias^2 <= 1e-6
   - Outcome: K = 4.7n-14n mv against MC's 4n-8n: worse than MC on 10 of 12 nets, better on both n = 256 nets (1,667 and 1,991 against 2,049)
   - Why it failed: The log it removes matters only at very small bias targets
   - Rules out: A practical gain at these bias targets below n = 256. The unbiased random-level version was not measured.
   - Evidence: registered (PB1 hit). Source: section 3.1
4. **K2 Gaussian closure (deterministic) for the stationary mean**
   - Tried: n = 8-256
   - Outcome: A bias floor of about 0.12/n (nMSE 1.6e-3 to 1.1e-2 at n = 8-16 down to 3.8-7.7e-4 at n = 256)
   - Why it failed: A floor falling like 1/n (the CLT) while MC at the closure's own cost also gives O(1/n)
   - Rules out: The closure beyond a constant 3-8x window near its own cost.
   - Evidence: registered (PB4 missed on one n = 256 net). Source: section 3.1
5. **Tail estimation by a radial tilt of the noise**
   - Tried: P(\|a\| > t) with p about 1e-2
   - Outcome: 0-2x over MC, often biased low; the code also had a likelihood-ratio bug at all-off layers (fixed; reruns reproduce the numbers). A fixed gradient tilt gives 3.1-9.5x instead
   - Why it failed: Heavy weights
   - Rules out: The radial tilt; the gradient tilt is a constant-factor gain with no width trend.
   - Evidence: registered (PB8 missed at n = 16 only). Source: section 3.1
6. **The coordinator's Lyapunov covariance formula for the cloud and per-direction memories**
   - Tried: Cloud eigenvalues and age profiles at n = 8-256
   - Outcome: Wrong size: 1.2x too small at n = 8, 5-8x at n >= 64, 14-160x for the radial direction; principal directions' information ages are nearly flat in k (n = 256: 32, 28, 28, 29, 24 layers against a predicted 89, 44, 22, 11, 6)
   - Why it failed: A covariance formula from Lyapunov exponents needs coefficients fixed independently of the noise, which gates are not [A]
   - Rules out: The linear (frozen-gate) picture of the cloud.
   - Evidence: registered (PA6 hit; PA5, PA10c missed). Source: sections 2.5, 2.7
7. **A few-bits (enumerable) regime, log-additive or radius-first coordinates for the stationary state**
   - Tried: Gate births, bit cascade and Sobol-type interaction statistics at n = 16-256
   - Outcome: 0.5-0.6 sqrt(n) flips per layer and a 1.6n-4.5n cascade per injection; radial noise carries 3-12% of the effect; log-radius has order 1.9-3.3 and the direction 2.4-3.0
   - Why it failed: Gate switching couples injections (HEURISTIC reading)
   - Rules out: Enumeration of bits and a product-of-factors description in Model S.
   - Evidence: registered (PA9, PI3 hit; PA13b missed). Source: sections 2.6, 2.10
8. **Stationary-regime variance reduction at ARC's own point (256 x 32, sigma = 1e-3)**
   - Tried: Part C grid, n = 32-256
   - Outcome: The noise is negligible there (input share 0.9992); antithetic noise is a loss where the input dominates (pair ratio 2.0); RQMC over the input gives 2.1x; the multilevel reference sampler gains nothing (1.01, from the unrestricted lane)
   - Why it failed: ARC's point is input-dominated, far from the stationary regime
   - Rules out: Transfer of the stationary-regime tricks to ARC's shape at sigma = 1e-3.
   - Evidence: registered (PC5a hit; PC5b1, PC5c missed). Source: section 4

Our own registered predictions that failed (5):

- Part A: PA1 (10% agreement everywhere fails at n = 128-256), PA2 monotone approach, PA5 (slope band), PA8 (worst bins at n <= 32), PA10c, PA10e, PA11 (radial non-Gaussianity fades with width), PR2
- A2 bit cascade: PA13a (first-layer flips scatter with the radius), PA13b (cascade 3.8-4.5 n > 3 n at n = 256)
- Part B: PB2 (two widths below the band), PB3 refuted (control-variate residual flat at about 1/3), PB4 (one n = 256 net at 7.7e-4), PB5 (RQMC still 2.1-2.6x at n = 128), PB6 (Rao-Blackwell ratio above 0.9 at n >= 64), PB8 (n = 16 only)
- Part C: PC1a (20 of 21), PC2 (24 of 26), PC3 (19 of 26), PC4 (gate-entropy clause), PC5b1 (13 of 20), PC5c (12 of 21), PC6, PC7c (16 of 17)
- Part I: PI2, PI4 iii (0.66 on one net), PI5 (no growth of the isolated mechanisms), PI6 (monotonicity), PI7 (one long-memory net), PI8 (2.06 > 2)

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (4):

- Corrected by stationary-numerics (stationary-numerics-2026-10-31.md), same day: CONTRADICTS: (1) this lane's theory conjecture that near-floor layers have probability about exp(-0.4 n) is refuted; the rate is 0.3107 n (0.3109 from the exact solver at n = 1024). (2) The registered band for this lane's scalar-chain quantiles (within 1%) is missed at q90 for n = 128, 256 (1.6-2.4%; attributed to this lane's correlated sampler). (3) The annealed interaction order could not be matched to this lane's (too noisy). RESOLVES what this lane left 'unresolved': with one estimator on 8 nets per width the interaction order of h_0 grows 1.41 to 3.87 from n = 8 to 256 (this lane: 2.5, 2.1, 3.1 on 2 nets per width, different estimator and noise coordinates, 'not directly comparable'). CONFIRMS: the exact radius chain and median (quantiles within 0.4% at q10/q50), C_n = 2n/5 + 13/75 (next term 529/(2250 n) added), the finite-angle law (exact replica chain 1.12x at n = 8 to 1.00x at 1024), births (0.62-0.63 sqrt(n) against 0.48-0.64), the cascade (networks 4-20% above the exact chain), the rank-conditioned exponents (median ratio 1.04), and gate switching as the source of interactions (within intervened models). The 5-8x cloud excess is explained only given an assumed 1/k shape, and both registered tests of that (G7, G8) missed. (stationary-numerics-2026-10-31.md sections 1.5, 1.6, 2.4, 2.5, 2.8, 3.1, 5.1, 8; work/stationary/FORMAL.md line 54)
- Corrected by input-bits (input-bits-2026-10-31.md): (1) 'The radius carries the input' is right only for the amplitude \|h_l\| and only beyond about 2 sqrt(n) layers; the input radius \|x\| carries 3-9%, and at ARC's 256 x 32 half the input variance is in the output direction. (2) The input regime (noise below 1% of the variance) ends near L of n/2 to n at sigma = 1e-3, not at T_mem of about 4n. (3) This lane's reading that the interaction structure 'matches RQMC's gains shrinking with width' is not supported: the registered verdict there is REFUTED (low-order shares are flat; the gain falls with the number of coordinates). (4) The 38 gate bits at layer 31 are confirmed as the low end of the net-to-net scatter (39-56; kernel 44.6). (input-bits-2026-10-31.md Summary items 1, 2, 5; sections 2.3, 3, 6.2, 6.6)
- Corrected by GPT-6 review (work/stationary/review/review_gpt6.md, 'major revision', 14 findings): Gains had been compared with MC at a different burn-in; now stated at matched burn-in, with the alternative accounting 3.5, 3.1, 4.1, 0.8, 1.2, 2.4. PA1 rescored as missed. Burn-in multilevel now 'worse on 10 of 12 nets'. Gains relabelled asymptotic constants with setup excluded. Part C input share renormalised (the first version gave shares up to 1.015). The 'coarse-grid artifact' claim was withdrawn and the width trend called unresolved. Radius numbers corrected (0.577 n is the chain's simulation plus a proven limit). Mechanisms relabelled HEURISTIC. A likelihood-ratio bug in the radial tilt was fixed. (report section 6)
- Corrected by gpt-6-astra co-prover round 2 (audit of theory v1 and of the Part A scoring): 12 corrections to v1 (e.g. true infinite-time exponents are all -infinity; the coordinator's sqrt(2/pi) counts units in a band, not flips); PA3 and PA10b rescored under the registered median rule; undeclared deviations found (2 seeds instead of 4; 2 paths x 40,000 layers). (report sections 2.4, 2.6, 6)

Not finished: Not done: third-order Sobol indices; the exact one-dimensional final-noise integration for the tail; RQMC at n = 256; the unbiased random-level multilevel estimator. Part of the cloud excess is unexplained. Residual directional information of the input was not measured. Open questions stated: an estimator that uses the finite-angle law without paying for the gate interactions; whether the absence of a width-growing gain is fundamental.

Could not be determined when extracting: Which of the co-prover's round-2 corrections map to which statements (the provenance file was not updated for round 2). I did not read FORMAL.md beyond the line that labels the exp(-0.4 n) statement a CONJECTURE.

### stationary-numerics

Report: `stationary-numerics-2026-10-31.md` (lanes/stationary-numerics/). Final state: 2026-10-31 (third review round at 17:35Z; dated log marks it final at 17:39Z).

Headline: The stationary radius law is solved exactly at every width (numerically, with closed-form 1/n and 1/n^2 corrections); a noisy-kernel fixed point delta* ~ 2.23 Q^(-2/3) gives the replica angle; interaction order grows with width.

Status: **numerical evidence**. three gpt-6-astra review rounds, each 'major revision', no fourth round (dated log: 'the report has not passed review'); 17 of 35 registered predictions hit, 17 missed, 1 unscorable; proofs written by the Claude lane itself (no co-prover), spot-checked by the reviewer, not human-checked; several headline items are HEURISTIC models

Failed approaches (7):

1. **Roberts-Yaida finite-width effective theory (kernel + four-point vertex recursion) with a per-layer noise source, for one input**
   - Tried: Analysis of the recursion in Model S
   - Outcome: No fixed point: the kernel grows by one noise unit per layer and the normalised four-point vertex diverges (the stationary mean of \|h\|^2 is infinite)
   - Why it failed: The stationary radius lives at aspect ratio l/n = O(1), where the 1/n expansion is not uniform
   - Rules out: A one-input moment recursion for the stationary state. Does not rule out the replica Gram chain (which has a fixed point), and one input does have a stationary law.
   - Evidence: proven (P-G2; lane's own proof, AI-reviewed). Source: section 2.2
2. **Closures for the radial variance between replicas at the fixed point**
   - Tried: Closure law 2.23 X^(1/3)/n + 1/(2n) and a post-hoc AR(1) closure, against the exact replica chain at n = 8-1024
   - Outcome: The closure law is 3.7, 2.5, 2.0, 1.7, 1.4, 1.2, 1.14, 1.10 times the exact value at n = 8..1024; the AR(1) closure overshoots by 1.99 to 1.10 at n = 16..512
   - Why it failed: Both closures freeze Q and delta during a radial relaxation that takes about Q/2 layers
   - Rules out: These two closures at reachable widths; their large-n agreement is 'suggestive, not shown'.
   - Evidence: registered (G3 miss); AR(1) post hoc. Source: section 2.4
3. **Explaining the cloud's 5-8x excess over the Lyapunov formula by delta*(Q) spread over an assumed 1/k spectrum**
   - Tried: G8: 12 new nets (n = 64, 128, 256), registered before the runs; G7: the stationary lane's 10 fresh nets
   - Outcome: G8: measured/predicted 0.86-1.41 on 11 nets and 0.56 on one large-radius net (missed, one net on each clause); radial 0.38-1.19. G7: missed on 2 of 10 nets (radial clause); radial eigenvalue 0.31-1.70
   - Why it failed: Not explained for the outlier beyond its large radius; the 1/k shape is assumed, not derived
   - Rules out: The model as a registered, per-net law. The later gram-chain lane refutes the 1/k shape itself as a global law.
   - Evidence: registered (G8 prospective; G7 not prospective, files predate the registration). Source: section 2.5, 2.6, 8
4. **Annealed (replica-chain) estimate of the interaction order of h_0**
   - Tried: Exact replica chain, n up to 1024
   - Outcome: Too noisy to use: 6.7 +- 3.9 at n = 256
   - Why it failed: Not explained in the report (the later gram-chain lane attributes it to an infinite annealed cloud trace)
   - Rules out: Annealed raw-state statistics as a check of the per-net interaction order.
   - Evidence: registered (G4b, G4d miss). Source: sections 6, 8
5. **Registered causal-intervention predictions on the direction observable**
   - Tried: Margin-limited, age-limited and radius-clamped variants on 4 nets per width
   - Outcome: I2b, I2c, I2d missed (recent-layer shares 1.5-3.1 instead of 0.3-0.9; clamp/true 0.68 at n = 64)
   - Why it failed: The frozen baseline of the direction observable is not 1 because normalising h_0 is nonlinear (an unsuitable registered observable, per the report)
   - Rules out: The registered quantitative allocation of interactions; the post-hoc h_0 version is limited to statements about the intervened models.
   - Evidence: registered (miss). Source: section 3.2, 8
6. **Response-kernel collapse along covariant Lyapunov vectors**
   - Tried: 4 nets per width, n = 8-256, finite-difference and tangent responses
   - Outcome: Rank loss destroys the vectors on 63-79% of paths at n = 8 and 46-70% at n = 16; finite-difference responses hit a double-precision floor; D1 unscorable (0.57-0.68 decades against 0.5), D2 missed (16 of 72 pairs outside 25%), D3 missed (amplitude exponent 0.12 against 0.5-1.2)
   - Why it failed: At finite n every infinite-time tangent exponent is -infinity; the vectors are finite-window, warm-up dependent and not validated
   - Rules out: The registered collapse claims; what remains is an empirical description at n >= 64 on unvalidated directions.
   - Evidence: registered (miss / unscorable); tangent redo post hoc. Source: section 5, 8
7. **Registered small-width claims: non-Gaussianity falls with width; the Gaussian is badly off at gate boundaries on most units**
   - Tried: Exact grid densities for 6 nets at n = 2, 4 nets at n = 3, one net at n = 4
   - Outcome: S2-S4 missed: two n = 2 nets are near-Gaussian (TV 0.005, 0.040); TV to the Gaussian does not fall with n (0.198 on the n = 4 net) and tracks the layer's radius; the Gaussian is off by more than 20% on only 4 of 12 units; the n = 4 grid misses its accuracy band (S1)
   - Why it failed: Non-Gaussianity follows the radius, not the width
   - Rules out: A width-ordered small-n picture. n = 6 is out of reach for dense grids.
   - Evidence: registered (miss). Source: section 4, 8

Our own registered predictions that failed (10):

- R6 (two-term median off by > 1% at n = 2): miss, 0.6%
- R8b (stationary lane's chain quantiles within 1%): miss, q90 1.6-2.4% at n = 128, 256; q99 5-6%
- G3 (radial CV^2 within 1.5x of the closure at n >= 64): miss, 0.60 at n = 64
- G4b, G4d (annealed interaction order): miss, too noisy (6.7 at n = 256)
- G5 (births within 5% of the kernel model): miss, up to 10.2% above at n = 16
- G7 (cloud excess on the stationary lane's fresh nets): miss on the radial clause, 2 of 10 nets
- G8 (same, prospective, 12 new nets): miss, one net per clause (0.56 on a large-radius n = 64 net)
- I2b, I2c, I2d (causal shares on the direction observable): miss
- S1 (n = 4 refinement TV 0.051 against 0.05), S2, S3, S4: miss
- D2 (16 of 72 pairs outside 25%), D3 (plateau exponent 0.12): miss; D1 unscorable as registered

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (3):

- Corrected by gram-chain (gram-chain-2026-11-01.md; overnight-report-2026-10-29.md entry of 2 Nov 01:10Z): The assumed 1/k cloud spectrum, and with it a (log n)^2 cloud dimension, is refuted as a global law: in a registered width test the exact chain's participation ratio is 114.7 at n = 1024 against 110.4 from an n^(2/3) law and 65.8 from 1/k (slope 0.614 against 0.34). The log calls this a correction of the numerics lane's 1/k spectrum, 'relayed earlier as a measured result'. The cloud's size via delta*(Q) stands. The same lane explains why the annealed D_h here was too noisy (the annealed raw-state cloud trace is infinite). (gram-chain-2026-11-01.md lines 49-54, 436, 502; dated log 1 Nov 21:03Z and 2 Nov 01:10Z)
- Corrected by gpt-6-astra review round 1 ('major revision', 13 findings): Replica statistics had been binned by one replica's own final radius, which breaks the estimands; all replica comparisons are now unconditional and the milestone agreement figures changed. 'Establishes 1/k' became 'consistent with 1/k'. The interaction-order estimator is consistent, not unbiased. Lyapunov-vector results restricted to n >= 64 (rank loss at n = 8, 16). Finite-difference 'linear' responses hit a double-precision floor; redone by tangent propagation, D1 and D2 reported as missed. The universal and radial readings of the response plateau were withdrawn. The lower-bound argument about the sibling lane's numbers was removed. The causal variants were overinterpreted and their registered misses had not been shown. An undisclosed fallback in the flip protocol was disclosed. G7 was not prospective; a prospective test G8 was registered, run, and missed. (report section 9)
- Corrected by gpt-6-astra review rounds 2 and 3 (both 'major revision' per the review files): Round 2: nine more corrections (per-net spread of tangent fits; medians with medians; censored lifetimes; D1, D2, D4, D5 rescoring; 'refinement diagnostics'; exploratory label for n = 4; exact boundary densities with S4 rescored; bias diagnostic; corrected numbers for G5, S2, G8 outlier). Round 3: label the Lyapunov vectors unvalidated; state populations and actual sampled times; stop lifetime curves at 2n; count D1 as unscorable (17 hits, 17 misses, 1 unscorable). (report section 9; review/review_gpt6_r2.md, review_gpt6_r3.md)

Not finished: Open per the report: a derivation of the angular spectrum; the radial variance at the fixed point; per-net versus annealed statistics; whether the response plateau is the radial mode. Lyapunov vectors not validated against a second horizon; k = 5, 7 not simulated; the eps-refresh estimator was not run on the same nets, so the difference from the stationary lane's numbers is not attributed; n = 6 densities infeasible with dense grids.

Could not be determined when extracting: Whether each proof in notes/proofs.md was checked line by line by the reviewer (round 1 says the radius independence argument, Gram transition, eps lower bound and frozen-gate proof 'check out'; I did not read notes/proofs.md or the raw review transcripts).

### input-bits

Report: `input-bits-2026-10-31.md` (lanes/input-bits/). Final state: 2026-10-31 (third review round 20:31Z-20:34Z; dated log marks it final at 20:36Z).

Headline: Input variance splits exactly into radius + amplitude + direction (\|x\| carries only 3-9%); 'growing interaction order explains shrinking RQMC gains' is REFUTED as registered; structured samplers buy 2-7x constants, no rate gain.

Status: **numerical evidence**. registered (Part 1: 12 of 20 hit; Part 2: 5 of 5 plus three REFUTED verdicts; amendments 10 of 11; Part 3: 2 of 5); theory proofs largely by the AI co-prover gpt-6-astra; GPT-6 review in three rounds (major, major, minor), last label fixes not re-reviewed; 2-4 nets per cell; not human-checked

Failed approaches (8):

1. **Hypothesis: a growing interaction order (operationally, a declining additive share) explains why RQMC gains shrink with width**
   - Tried: Noise regime: stationary nets n = 8-128 (4 nets per width), N = 2^10; input regime: n = 64-256 along L = 32 and L = n/2 (4 nets per cell), N = 2^8 to 2^12
   - Outcome: REFUTED in both regimes: noise-regime first-order share changes +0.03 (0.59 to 0.62) from n = 16 to 128 while the gain falls 1.54x; input-regime S1 0.30, 0.31, 0.27 while the gain falls 1.9 to 1.25
   - Why it failed: The gain falls because the number of coordinates grows at fixed N, lowering the pair efficiency rho_2(N/d); the same integrand moved to poor Sobol dimensions loses its gain (about 8x to about 3x)
   - Rules out: A declining low-order share as the cause. Does NOT rule out variance moving between high orders mattering (the rule 'cannot see variance moving between high orders'); the surrogate assumes RQMC leaves high orders at MC efficiency, 'an assumption, not a measurement'.
   - Evidence: registered (H2.6 verdict rule; Amendment 2A hit). Source: sections 6.2, 6.3, 6.6
2. **RQMC over the input for a rate improvement**
   - Tried: RQMC, radius-exact RQMC and rotated RQMC, n = 64-256, L = 32 to 2n, N = 2^6 to 2^12, R = 10 scrambles, 2 fresh nets per cell
   - Outcome: Fitted exponents 0.92-1.38 (medians 1.05-1.16); gains 1.6-5x falling with width (radius-exact RQMC at L = 32: 5.0, 2.9, 1.6 at n = 64, 128, 256; 1.6-2.1x at ARC's 256 x 32)
   - Why it failed: Order-2 removal needs N far above the number of coordinates
   - Rules out: A robust rate improvement at N <= 4,096 ('measurements to 4,096 points cannot establish a limiting gain or rule out a better eventual rate').
   - Evidence: registered (P3.1, P3.2 hit; P3.6 declared 'PROGRESS' on two cells, which the author attributes to noise). Source: sections 7.1, 7.3
3. **Quadratic control variate with exactly zero Gaussian mean, fitted from a pilot**
   - Tried: 32-term quadratic from a pilot of 8,192 inputs (16,384 at n = 256), n = 64-256
   - Outcome: Fails at n >= 128: residual variance 1.0-1.45 of V (gains 0.7-0.9); removes 37-47% at n = 64
   - Why it failed: The fitted quadratic adds more fitting noise than it removes (HEURISTIC; predicted by the co-prover)
   - Rules out: Pilot-fitted quadratic controls at these pilot sizes; not controls with exactly computable coefficients.
   - Evidence: registered (P3.3 missed). Source: section 7.1
4. **Learned rotation of the input to the pilot's degree-2 eigenbasis before RQMC**
   - Tried: Same pilots; 9 cells with L >= n/2; Part 1 test of the first-order share after rotation
   - Outcome: Beat radius-exact RQMC by >= 1.2x in only 3 of 9 cells; at n = 256 the first-order share rises only 0.32 to 0.35 and the off-diagonal share falls 11-13% (registered: 40%)
   - Why it failed: A pilot of 8-16 thousand inputs cannot estimate the n^2/2 matrix entries at n >= 128 (HEURISTIC; 'a mismatched proxy is another' possible reason)
   - Rules out: The rotation at these pilot sizes; a pilot growing like n^2 is untested.
   - Evidence: registered (P1.16, P3.4 missed). Source: sections 4.2, 7.1
5. **Pilot-based samplers with the pilot charged**
   - Tried: Registered pilots (2-4 times the measured budget of 4,096 passes); post-hoc accounting at each method's largest budget
   - Outcome: Every pilot-based method is unaffordable at the 4,096-pass budget. At larger budgets multilevel-RQMC exceeds 1 in 5 of 11 cells (1.8-2.9) and is at or below 1 at L = 32 and at n = 256 (0.4-1.0); two-level, dyadic multilevel and the quadratic control never exceed 1; pilot-free RQMC wins in every cell (1.6-5.0)
   - Why it failed: Pilot cost
   - Rules out: A net gain from the pilot methods at these budgets, at n = 256 and at ARC's depth.
   - Evidence: registered rule (implemented after the hash, labelled); larger-budget accounting post hoc. Source: section 7.2
6. **Antithetic input pairs (x and -x) in the input regime**
   - Tried: All Part 1 cells
   - Outcome: Even share 0.38-0.51, gain 1/(2 s_even) = 1.0-1.3
   - Why it failed: Flipping the input flips every first-layer gate, and the two inputs then behave almost independently
   - Rules out: Input antithetics as a variance reduction for these nets.
   - Evidence: registered (P1.15 hit). Source: section 4.2
7. **Multilevel shared-trajectory sampler at fixed depth L = 32 (ARC's shape) and two-level growth at L = 2n**
   - Tried: n = 64-256, 4 nets (Part 2) and 2 nets (Part 3) per cell, pilot-estimated ideal allocation
   - Outcome: At L = 32: 1.08, 1.02, 0.93 (Part 2); at ARC's 256 x 32 two-level 1.0 and dyadic 0.5 (Part 3). At L = 2n the two-level version is flat (2.6, 2.9, 2.7); only the dyadic version grows, slowly (1.6, 1.9, 2.5)
   - Why it failed: At fixed L the direction residual (about n/L^2) dominates and needs a full pass
   - Rules out: A gain at ARC's shape from this sampler. The dyadic growth is 'a pilot-based risk prediction on two nets per cell, not a validation' of the n/log^2 n law.
   - Evidence: registered (H2.5 hit; P3.5 'increasing' clause missed). Source: sections 6.5, 7.1
8. **The author's predicted decrease of the order generating function with width**
   - Tried: C(t) by Bernoulli coordinate sharing, 4 nets x 8,192 pairs per width, n = 8-128
   - Outcome: C(0.75)/C(1) goes 0.598 to 0.607 from n = 16 to 128 (predicted a decrease of >= 0.04)
   - Why it failed: C(t) at t <= 0.75 resolves only low orders; a high-order tail moves it by t^k of its mass
   - Rules out: A detectable shift in the low-order part of the order distribution. The tail's mass (order fits give 10-22%) is not established.
   - Evidence: registered (A2B.2 missed). Source: section 6.4

Our own registered predictions that failed (11):

- P1.2 (kernel prediction of V_dir/V_amp): missed on 1 of 16 cells (256 x 512, at a floor)
- P1.5 (annealed chain vs 4 nets): 6 of 12 cells
- P1.6 (noise < 1% of the input variance): 57 of 72; 15 cells over 1%
- P1.7 (bit decay: kernel 113 of 116 layers, chain 341 of 472): missed on both clauses
- P1.13: 2 of 48 nets fail one clause
- P1.16 (rotation at n >= 128): missed
- P1.19 (Gamma band): 6 of 14 as registered with the bug, 13 of 14 on the fixed rerun
- P1.20 (radial share >= 0.9): 14 of 16
- A2B.2 (decrease of C(0.75)/C(1)): not detected
- P3.3 (quadratic control), P3.4 (rotation, 3 of 9), P3.5 (two-level multilevel increasing at L = 2n): missed
- P3.6 fired 'PROGRESS' as registered on two exponent cells; the author attributes it to noise (R = 10 scrambles)

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (2):

- Corrected by gpt-6-astra co-prover round 2 (audit): Three real bugs: tangent vectors normalised along the wrong axis (one statistic 4x too large at n = 256; fixed and rerun); a multilevel cell needed by a registered prediction was never generated (fixed before any run); Part 3's registered scorer did not implement its predictions and extrapolated pilot-charged gains below the pilot's own cost (rules implemented after the hash and labelled; such gains now 'UNAFFORDABLE'). Also: the registered verdict rule H2.6 tests only a declining additive share. (report section 9; coprover/PROVENANCE.md round 2)
- Corrected by GPT-6 review rounds 1-3 (major, major, minor): Round 1: 'The whole ANOVA-order distribution is the same' overstated three values of C(t); now 'no detected shift at the measured t'. The RQMC surrogate had been presented as a mechanism. Finite-budget gains had been called asymptotic constants. The multilevel-RQMC figure is an oracle envelope over three allocations. A sensitivity ratio had been called a mean ANOVA dimension although it exceeds n. 'Every pilot method still loses at its largest budget' was wrong. Round 2: section 6.7 compared quantities with mismatched conditioning (fixed by registered Amendment 2E); 'growth confined to a ~10% tail' was only consistent with the data, now 'a possible reconciliation'. Round 3: narrower labels. (report section 10)

Not finished: Open per the handoff: pilot-limited rotations and quadratic controls (need pilots of order n^2); a validated (not plug-in) multilevel risk at larger L; the order distribution's tail (C(t) near t = 1); per-net versus annealed statistics under heavy tails. P1.17 and P1.18 were evaluated on power-of-two layers only. Gains are measured only to N = 4,096.

### gram-chain

Report: `gram-chain-2026-11-01.md` (lanes/gram-chain/). Final state: 2026-11-02 03:00Z.

Headline: Weight-averaged theory of what a layer's state decides: the exact chain matches its closed-relevance curves within 0.003-0.014 at n = 256-1024 and its other laws within 10-30%; it cannot say which directions.

Status: **numerical evidence**. tool PROVEN, laws HEURISTIC, checked on the exact chain and on 168 nets; registered: 16 hit / 7 miss / 1 incomplete (15 / 8 / 1 with PB1 as first analysed); two GPT-6 reviews, both 'major revision', applied; last runs scored after round 2 and not re-reviewed; proofs by Claude and gpt-6-astra only, no human check

Failed approaches (7):

1. **1/k spectrum for the stationary cloud (numerics lane's assumed shape, (log n)^2 dimension)**
   - Tried: Exact 4-replica chain, n = 16-1024 (8000 chains at n <= 64 down to 500 at n = 1024); registered PA8 (1/k moments within 25%) and PA9 (slope of PR_w between n = 256 and 1024).
   - Outcome: PA8 missed: radius-normalised PR 27% below the 1/k value at n = 64. PA9: slope 0.614 (90% interval 0.599-0.629) against 0.34 for 1/k; PR_w = 114.7 at n = 1024 against 65.8 (1/k) and 110.4 (1.0865 n^(2/3)).
   - Why it failed: A radius-independent 1/k shape cannot produce the measured radius dependence of PR (3.5x fall from q = 0.2 to 10 at n = 256); the four-point balance gives n theta*/pi.
   - Rules out: 1/k as a global law over n = 256-1024. Does NOT prove the n^(2/3) exponent or fix the spectral shape; top-k eigenvalue ratios (k = 2-8) were not computed; third-moment evidence is noisy.
   - Evidence: registered (Amendment A1 hashed after the n = 256 run had started, before its result; n = 1024 prospective). Source: sections 2.4, 9
2. **Linear (frozen-gate) free-product count of relevant directions, n/(n/PR_C + 2t)**
   - Tried: Exact chain, n = 64 and 256, t = 1-32, closed PR (10-replica four-future design) and total PR.
   - Outcome: 9-16% low at t = 1, 22-58% low at t = 2-4; PB3 missed on 1 of 12 clauses (total PR at n = 64, t = 4 is 1.58x); 'For t of order n the formula fails altogether'.
   - Why it failed: Gates switching across the cloud spread relevance over more directions (empirical c ~ 1.1-1.6 instead of 2); c is not derived.
   - Rules out: The frozen-gate formula as a count beyond a couple of layers. Not excluded: the fitted form n/(n/PR_C + c t), which is empirical.
   - Evidence: registered. Source: section 3.3
3. **Annealed variance-weighted participation ratio as the typical net's dimension**
   - Tried: 168 real nets (n = 8-256), 256 noise replicas each, against the chain's PR_w.
   - Outcome: Median per-net PR is 0.67 and 0.71 of PR_w at n = 128 and 256; PC4 (25% band) missed.
   - Why it failed: PR_w weights nets by (tr C)^2 ~ Q^(-4/3), i.e. small-radius nets with bigger clouds; limit ratio 1.35.
   - Rules out: Reading annealed moment ratios as per-net dimensions without the weighting correction. Per-net scatter beyond the radius (CV 0.14-0.20) stays unexplained.
   - Evidence: registered. Source: section 5
4. **Angle level prediction (PA3)**
   - Tried: Median of delta/delta*(Q) in [0.97, 1.03] at n >= 64 and n^(2/3)(mean - 1) constant within 2x.
   - Outcome: Median 0.962 and 0.969 at n = 64 and 128; mean - 1 falls faster than n^(-2/3).
   - Why it failed: A finite-n conditional tilt of order n^(-1/2); the co-prover's second-order coefficient (+0.077 n^(-2/3)) is far smaller; 'not derived'.
   - Rules out: The registered finite-n level; not the limit (median 0.989, mean 1.000 at n = 1024).
   - Evidence: registered. Source: sections 2.2, 9
5. **Registered bands that missed narrowly or on resolution (PA6, PB1 as registered, PB4, PB5)**
   - Tried: 1/e lag of the log radius >= 0.8n; closed-relevance half-life and area within 30%; log\|a\| relevance above the direction's at every t >= 8; perturbation survival within 30% of mean field.
   - Outcome: PA6: 0.78n at n = 1024. PB1 as registered: half-life read 8 against 6 on a coarse grid, full-grid area -1.28 at n = 256 and 66.7 at n = 1024. PB4: fails where both relevances are near zero (n = 64 at t = 160-192, n = 256 at t = 1024; standard errors not saved). PB5: 98 of 100 clauses (1.32-1.33x at eps = 0.1, n = 64, t = 20-24).
   - Why it failed: Report: 'bands that did not allow for noise or grid resolution'.
   - Rules out: Nothing substantive per the report; PB1's 'hit' exists only under an analysis chosen after seeing data.
   - Evidence: registered (PB1 revision post hoc). Source: sections 3.1, 3.2, 3.4, 9
6. **Radius-normalised third-moment estimator of the cloud spectrum (PA8 r3 clause)**
   - Tried: Six replicas, n = 16-128 (n = 256 dropped; half the registered chain budget).
   - Outcome: Too noisy to use (1.72, 1.96, 3.50, 2.31).
   - Why it failed: Estimator noise.
   - Rules out: Nothing; 'The spectrum's shape beyond its participation ratio remains open.'
   - Evidence: registered, incomplete. Source: section 2.4
7. **Annealed raw-state second moments in the stationary regime**
   - Tried: Annealed moments of raw-state differences (n = 64 check).
   - Outcome: Infinite: the top 1% of chains by radius carry 82% of the sample mean of \|h1 - h2\|^2.
   - Why it failed: E Q is infinite and the radius ratio does not shrink at large Q.
   - Rules out: Annealed raw-variance quantities; direction and log-radius versions are used instead.
   - Evidence: proven (integrability) with a numerical check. Source: sections 1, 7

Our own registered predictions that failed (9):

- PA3: median delta/delta* in [0.97, 1.03] at n >= 64: 0.962, 0.969 at n = 64, 128
- PA6: log-radius 1/e lag in [0.8n, 3.2n]: 0.78-0.80 n (under 3% short)
- PA8: cloud moments of a 1/k spectrum within 25%: radius-normalised PR 27% below 1/k at n = 64; r3 clause 3.50 against 1.91
- PB1 as registered: half-life and area within 30% of mean field: missed (hit only under the revised analysis)
- PB3: PR within 1.5x of the free product: 11 of 12 clauses (1.58x at n = 64, t = 4)
- PB4: log\|a\| relevance above the direction's at every t >= 8: fails at n = 64, t = 160-192 and n = 256, t = 1024
- PB5: perturbation survival within 30%: 98 of 100 clauses
- PC4: median per-net PR within 25% of the chain's PR_w: 0.67, 0.71 at n = 128, 256
- PA7 incomplete, not failed: in band at the 5 widths run; n = 512, 1024 dropped

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (3):

- Withdrawn; self (after GPT-6 review r1): The first vertex recursion interpolated a Monte Carlo source on a 201-point grid and wrongly collapsed at depth; section 4.1 had attributed the deep-layer gap to a breakdown of the 1/n expansion. Recomputed by quadrature: tends to 1.5 n/l. (report sections 4.1 and 10 (change 2, deviation 9))
- Withdrawn; self (after GPT-6 reviews r1 and r2): Narrowed: 'annealed raw quantities do not exist' to the divergent moments; the direction theorem to layer-l perturbations with matched Gram relations ('or the mean direction' removed); the orientation bit count to a conditional description length with no implication for estimators; V_P described as explaining the conditional mean of the output direction, not E[a]; scorecard tallies corrected; PB1 marked 'revised analysis' wherever it says hit. (report section 10)
- Withdrawn; self (explainer v1 -> v2): gpt-6-astra check of explainer v1: 27 findings, 13 errors (overreach on stationary constants, replica observables, ANOVA and symmetry); the layer-block tail claim was withdrawn. (explainer section 7; report section 10)

Not finished: Dropped: PA7 at n = 512 and 1024, PA8 third moment at n = 256, sharing runs at t = 0.9 and 0.99 for n = 1024. Not done: top-k eigenvalue ratios, spectral shape beyond PR, derivation of the gate-switching coefficient c, the conditional angle tilt, per-net residual scatter. HANDOFF.md: 'Nothing running'.

Could not be determined when extracting: Whether the applied state satisfies the reviewer: both rounds returned 'major revision' and no round confirms the final text. The dated log (03:05Z) says '1/k refuted'; the report body says favoured and not proved. I did not open the raw review files.

### relevance

Report: `relevance-accounting-2026-11-01.md` (lanes/relevance/). Final state: 2026-11-02 (final scoring 02:36-02:38Z; round-3 review 02:43-02:53Z applied; outbox copy 03:03Z).

Headline: A heuristic accounting built on one theorem predicts tested-subspace counts within 2x on 55-56 of 56 prospective ARC cells; variance budget and mean degree less reliably; both registered per-net mean-degree tests missed.

Status: **numerical evidence**. heuristic model with registered prospective tests (counts hit; pooled budget miss; mean-degree tests B1 and C1 missed); Theorem 1 PROVEN [C+A] by AI only; three GPT-6 review rounds (major, minor, minor), applied; counts are point estimates for exhibited subspaces, not certified; no human check

Failed approaches (9):

1. **Annealed mean-degree prediction (theory v2, R = 1) on fresh ARC nets**
   - Tried: Amendment 3A: ARC 256 x 32 nets 4004-4005, 14 layer cells, registered before the nets were run.
   - Outcome: Q3 mean degree 8/14 and Q2 degree-1 share 10/14: both missed. Measured mean degree at l <= 8 is 1.6-2.2x the model (31.6 against 16.0 at the input).
   - Why it failed: A per-net gain factor R (0.61-2.4 at l <= 8 over ten nets) that the annealed theory sets to 1.
   - Rules out: Predicting the mean degree from (n, l, L, sigma) alone. Does not rule out per-net prediction with a measured budget.
   - Evidence: registered. Source: sections 3, 3a, 10
2. **Per-net corrected mean degree: forward-only R estimate times the annealed budget (v3.3 [C], test B1; v3.4 [A], test C1)**
   - Tried: Four fresh ARC nets 4006-4009, 28 cells; criterion: in [0.75, 1.33] on >= 22 of 28 and on >= 9 of 12 cells at l <= 8.
   - Outcome: B1: 21/28 and 6/12, missed. C1: 22/28 (met) and 7/12 (missed), joint criterion missed. v2's own prediction did better on these nets (25/28).
   - Why it failed: The annealed budget has its own per-net error, correlated with R (net 4008: budget 0.70-0.72 of the model while R is predicted within 1-5%).
   - Rules out: R estimate times annealed budget as a per-net mean-degree predictor. Not ruled out: the R estimates themselves (median error 3.5-5.1%); with the measured budget D is within [0.91, 1.19] on all 28 cells, 'a consequence of the R accuracy, not a separate test'.
   - Evidence: registered (3B before the nets were run; 3C during the runs, 'before output inspection according to the author; reads were not logged'). Source: section 3a, 10
3. **Annealed variance budget (v2 Q1) on the freshest nets**
   - Tried: Nets 4006-4009, budget within 20% on >= 24 of 28 cells.
   - Outcome: 19/28, missed; pooled over eight prospective nets 45/56 against a scaled threshold of 48 (not separately registered).
   - Why it failed: Per-net error (net 4008 at 0.70-0.72 of the model at l = 0-16), associated with R post hoc.
   - Rules out: The budget as a reliable per-net prediction; it held on nets 4002-4005 (26 of 28).
   - Evidence: registered. Source: sections 3, 10
4. **Free-product count of linear directions N_1 (P1) and generic capture of the cloud-axes basis (P6)**
   - Tried: 123 cells (ARC, stationary n = 32-256, narrow-deep), within 2x on >= 75%.
   - Outcome: P1: 87/123 (70.7%) at eps = 0.1 and 52/123 (42%) at eps = 0.01, missed; a post hoc alternative count gives 82% and 68%. P6: 49/119 (41%), missed.
   - Why it failed: P1: the registered eigenvalue count is biased low by sampling noise (about 21% of V_1 at ARC's input). P6: not explained beyond the withdrawal of generic capture as a consequence of Theorem 1 (E9-E10).
   - Rules out: The registered N_1 measure and generic capture as tested. The post hoc recount still misses at eps = 0.01.
   - Evidence: registered (alternative count post hoc). Source: section 10
5. **Stationary regime: one direction or the radius as a sufficient description, and a 5/n memory rate**
   - Tried: n = 32-256, sigma = 1; PS1 on cells with t >= 2 n^(1/3) ln(1/eps); P11b late-rate window [n/4, n]; Q6 beyond t_1.
   - Outcome: One direction leaves at most 1% of V on 1 of 15 cells (10% on 25 of 29); the radial feature within 10% on 0 of 16 and 5 of 13; Q6 one direction beyond t_1 on 10/14 (target 75%); late decay rate 0.047, 0.017, 0.005 against 5/n = 0.078, 0.039, 0.020 (missed at every width); per-net rates spread 10x.
   - Why it failed: The slow coordinate is the top active-subspace direction, not the radial feature, 'not proven optimal and not identified theoretically'; no tested rate model (5/n, 5/(2n) + 1/Q, B(c*)/n) follows per net.
   - Rules out: 'Radius suffices' and the 5/n rate as written. One direction at 10% holds (PS1(a) hit at eps = 0.1).
   - Evidence: registered. Source: sections 7, 10
6. **Gate-based descriptions of the nonlinear part**
   - Tried: ARC 256 x 32, four nets, importance and margin orderings on a 40-point grid; PG2 (first-order count within 2x), PG3 (G >= 3N).
   - Outcome: 1,950-4,900 gates (8-19 times the width) to bring the nonlinear residual within 1% of V at l = 8-16; PG2 9/24 and PG3 9/16 missed.
   - Why it failed: Which gates flip depends on the sample; PG2/PG3 fail where the nonlinear share is already below eps.
   - Rules out: The tested orderings as compact descriptions. 'G is a tested count for the stated ordering, not a minimum over all gate sets.'
   - Evidence: registered. Source: section 6
7. **Low-dimensional control variate on tested active-subspace features at ARC 256 x 32**
   - Tried: Exact conditional mean on the top k = 1, 16, 64, 128 features at the input, four nets.
   - Outcome: Gain at most 1.05x, 1.33x, 1.80x, 3.11x before the cost of the k-dimensional conditional mean; deeper layers look better only under the Gaussian replacement, which itself moves the mean by 1.6e-4 to 2.7e-3 nMSE.
   - Why it failed: The tested subspaces need many coordinates (N(0, 0.01) = 256).
   - Rules out: These tested features as a route to beating sampling. Does NOT bound optimal features or integration methods that do not resolve the state ('N bounds predictive dimension, not integration cost').
   - Evidence: measured, post hoc. Source: sections 9, Summary item 4
8. **Synchronisation at the Lyapunov-gap rate (PS2(b)) and scalar counts (P8 at eps = 0.01)**
   - Tried: n = 16 and 32 nets at L = 256 and 512; P8 scalar N within 2x on >= 70%.
   - Outcome: PS2(b): two fits outside the band, two unresolved; 'the second [part of the mechanism] is not supported'. P8 at eps = 0.01: 81/123 (65.9%).
   - Why it failed: The residual falls irregularly while 0.2-2 gates per layer still differ; P8 not explained.
   - Rules out: Decay at rate 2/n as registered.
   - Evidence: registered. Source: sections 8, 10
9. **First-chaos eigenvalue-tail numbers used as lower bounds**
   - Tried: Noise-corrected first-chaos estimates on all cells.
   - Outcome: At n = 256, t >= 64 they exceed the measured counts (7-8 against 1 at eps = 0.1): 'there they are not lower bounds (E12)'.
   - Why it failed: Noise-dominated at small memory share.
   - Rules out: Treating these numbers as certified bounds anywhere.
   - Evidence: post hoc. Source: sections 5, 7

Our own registered predictions that failed (13):

- P1 free-product N_1 within 2x (>= 75%): 87/123 at eps 0.1, 52/123 at eps 0.01
- P4 stationary degree-1 share >= 0.85 on >= 90%: 80/95 (84%); claim retracted
- P6 generic capture of the cloud-axes basis (>= 75%): 49/119 (41%)
- P8 scalar N within 2x at eps 0.01 (>= 70%): 81/123 (65.9%)
- P11(b) late rate within 1.6x of 5/n: 0.047, 0.017, 0.005 against 0.078, 0.039, 0.020
- PG2 first-order gate count within 2x: 9/24; PG3 G >= 3N: 9/16
- PS1(a) at eps 0.01: 0/8 and 1/7; PS1(b) radius suffices: 0/16 and 5/13; PS2(b): two fits outside, two unresolved
- Amendment 3A: Q2 degree-1 share 10/14; Q3 mean degree 8/14
- Pooled Part 3 over four nets: Q3 mean degree 19/28 (>= 22; pooled threshold not separately registered)
- Q6 one direction beyond t_1: 10/14 (target 75%)
- Amendment 3B: B1 mean degree 21/28 and 6/12 (needs >= 22 and >= 9); v2 Q1 budget 19/28 (>= 24)
- Amendment 3C: C1 mean degree 22/28 met, 7/12 early missed (joint criterion missed)
- v2 budget over eight prospective nets: 45/56 against a scaled threshold of 48 (threshold not separately registered)

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (7):

- Corrected by bits-bounds (gpt-6-astra round 2 for that lane): Corollary 1b as written equated a conditional expectation with a random trace; replaced by statements (i)-(ii) of erratum E1. The conclusion (no per-direction alignment) was kept. (work/relevance/FORMAL.md E1; report sections 2 and 11; work/bits-bounds/coprover/PROVENANCE.md (B11))
- Corrected by gram-chain (gram-chain-2026-11-01.md): Qualification of Corollary 1c: the degree-1 count follows the backward spectrum only once c t exceeds n/PR_C (about t > 3 at n = 256). The gram-chain report also says the free-product formula does not apply in the input regime, while this report applies it to the degree-1 part on ARC cells (post hoc). (gram-chain report sections 8 and 4.1)
- Corrected by bit-accounting-arc (bit-accounting-arc-2026-11-02.md): Says N(l, eps) and its codes' active latents are different quantities, and that this lane's water-filling numbers (top 96 eigenvalues, linearised distortion) are not comparable where N > 96 (layers 0-8); its full-spectrum closed form 'replaces them'. (bit-accounting-arc report section 5)
- Withdrawn; self (co-prover round 2 audit, errata E2-E17): Two theory steps withdrawn: generic capture as a consequence of Theorem 1, and the v2.4 lemma. The 'at least 29' first-chaos lower bound relayed earlier is a point estimate, not certified. (report section 11; dated log 22:12Z 1 Nov)
- Withdrawn; self: v1 claim that the stationary degree-1 share is >= 0.85 everywhere (P4 missed, 80 of 95; E6). (report sections 7 and 10)
- Withdrawn; self: v3.3 claim that the variance budget does not respond to R: withdrawn (FORMAL E19); post hoc correlation 0.67, slope 0.30 over 70 dependent cells. (report Summary item 2 and section 3a; dated log 03:04Z 2 Nov)
- Withdrawn; self (after GPT-6 reviews r1-r3): M1 headline replaced by the reviewer's wording (many coordinates for tested subspaces; better methods unresolved); 'interactions dominate' removed; first-chaos numbers relabelled uncertified estimates; B1 and C1 restated as missing their registered joint criteria; 'D is forward-predictable' reduced to a statement about the tested cells; budget error restated as down to 0.70 of the model (a 42.6% model error), not 'up to 30%'. (report section 12)

Not finished: Stationary gate counts are PROVISIONAL (re-estimation with independent outer noise pairs outstanding). Two registered n = 256, t = 256 cells dropped. Sampling uncertainty of the degree surrogates not quantified. Narrow-deep estimator has no confidence intervals. Missing: a certified nonlinear lower bound for these networks and a computational-cost argument.

Could not be determined when extracting: Amendment 3C's 'before output inspection' rests on the author's statement only. I did not open runs/est_nd.json; the dated log (22:12Z 1 Nov) had marked the narrow-deep gain as not yet checked on disk at that time.

### bits-bounds

Report: `bits-bounds-2026-11-01.md` (lanes/bits-bounds/). Final state: 2026-11-01 23:47Z.

Headline: Heuristic formula N_l(eps) ~ (d_l/p) log2(D_l(1)/eps^2), d_l ~ n/l: it separates cuts needing many bits from those needing none, intermediate counts only within ~2x; bounds hold for restricted classes only.

Status: **numerical evidence**. HEURISTIC formula; main registration 3 hit / 8 missed of 11; Amendment 5 6 of 6 with bands calibrated post hoc; lower-bound version proved only for an idealised source whose hypotheses fail for nets; two fresh gpt-6-astra reviews (both 'major revision'), sections 3.5-3.6 audited only by the co-prover (same model); several proofs [A]-only; no human check; the cross-lane match with learned codes is post hoc on one net and was weakened by bit-accounting-arc

Failed approaches (6):

1. **Exact single-Gaussian closure (matched Gaussian ReLU moments at every layer) against sampling**
   - Tried: 76 nets in eleven configurations from 16 x 8 to 256 x 256, Gaussian inputs, at its matrix-product cost of 2n passes (registered Amendments 3-4; B3-B4 registered after B1-B2 were seen).
   - Outcome: Median gain over MC at L = n: 0.38, 0.28, 0.63, 3.26, 0.87, 1.02 for n = 16, 32, 64, 128, 192, 256; at L = n/2: 2.28, 0.59, 0.80, 0.89, 0.40. At the estimated implementation cost configuration medians are below 0.4 everywhere.
   - Why it failed: Gaussianisation discards the third and fourth cumulants and raises the mean radius by 9/(16 sqrt n) at the first layer; that defect survives any later suffix of depth alpha n (PROVEN for one step [A]; for the full recursion only UNDER the conjecture H_R).
   - Rules out: A gain above about 3x for this recursion up to n = 256. Does NOT rule out corrected closures (higher order, mixtures, gate splits); the peak is 'favoured, not established' (1.7-1.9 SE, 4 nets at n = 192 and 256).
   - Evidence: registered (trend analysis post hoc). Source: Summary item 10; sections 8, 9
2. **Merge / cell constructions (k-means cells with frozen or radial merges) at ARC 256 x 32**
   - Tried: The registered E1 nets at 256 x 32 (seeds from 100; the report does not give the count for this configuration), cuts l = 8, 16, 24, 28, up to 256 reference cells.
   - Outcome: 256 cells do not bring the merge residual to eps^2 = 0.1 at l = 8, 16, 24 (D_best(256) = 1.05, 0.62, 0.25); decay exponent 0.01-0.14.
   - Why it failed: The whole net sits in the early, rough regime (l/n <= 1/8): cloud PR 13-33 and a long rough future.
   - Rules out: The lane's k-means construction up to 256 cells. Not a lower bound for other cell constructions (the lower-bound theorem does not apply to nets).
   - Evidence: registered. Source: sections 3.4, 7
3. **Multilevel shared-trajectory samplers at ARC 256 x 32**
   - Tried: One-reference multilevel; M = 4-256 shared reference trajectories; 256 forward-only references (registered E3 and Amendment 1).
   - Outcome: One reference: 0.99 (no gain). Several reference trajectories: 0.49-0.65 (lose). 256 forward-only references: 2.0-2.2 times MC's variance x cost (worse). Gains exist elsewhere: 1.21-2.43 at L = n, 2.2-3.9 at L = 4n.
   - Why it failed: Same early rough regime; with many references level 1 carries the full variance.
   - Rules out: These samplers at 256 x 32 in ideal propagation-only accounting. Hierarchies were chosen on the test split (optimistic).
   - Evidence: registered. Source: sections 5, 7; Summary item 8
4. **Lower bound on bits for actual nets from the cell rate-distortion argument**
   - Tried: Rough-regime analogue of Cor 7.2 under a linear minorant of the future-averaged radial distortion and a small-ball condition.
   - Outcome: Both hypotheses fail globally for nets: rho(phi) <= phi^2 at small angles and the layer-l angular law has atoms.
   - Why it failed: The distortion is quadratic at small angles; single-neuron input cones map onto coordinate rays.
   - Rules out: Using the formula as a lower bound for nets. A window-restricted minorant and a bulk small-ball bound are listed as next steps, not started.
   - Evidence: proven (co-prover round 4 audit). Source: section 3.5
5. **Wrong expectations and narrow bands in the main registration**
   - Tried: P1-P11, A1-A3, G1, B1-B2 on 64 + 8 + 12 + 76 nets.
   - Outcome: P11: bits at L/2 of L = n nets do not stay above 8 as width grows (43% against >= 75%). P2: nets' cubic coefficient within [1/3, 3] of the chain's on 47%. P5: 17 groups pass, 10 fail. P6: two-sided cells <= 0.8 x forward-only on 56% (needs 60%). P9: multi-reference below one-reference on 50% (needs 70%). A3: several reference trajectories do not beat one on 65% (needs 75%). Narrow: P1 79% (80%), P4 89% (90%), P10 85% (90%), A2 2.01x (2.0x), G1 2.04x (2x). B1 and B2 missed at L = n (slope -2.05; gain 0.38 -> 3.26).
   - Why it failed: Report: bands set too narrow, the P2 output-normalisation problem, and two wrong expectations (P11; the closure's fast decline over n = 16-128).
   - Rules out: The specific registered expectations; the report says the qualitative claims held.
   - Evidence: registered. Source: section 8
6. **Kelvin's hash argument as stated**
   - Tried: Checked against the lane's theorems and measurements.
   - Outcome: F1: the count is not exp(k*). F2: final layers are the easiest (at most 1.7 bits at 7L/8 for L >= n at eps^2 = 0.01). F3: 'hash implies hard to average' is false for a random hash with a known ensemble mean (gain at least 4(K-1)/K). F4: 'nothing beats sampling' is false (the multilevel sampler beats plain MC).
   - Why it failed: The past gives d_l ~ n/l directions and the future a ratio rho_l; averaging methods integrate kinks analytically.
   - Rules out: The exp(k*) count and the unqualified hash claims. Keeps S1 (under the Gaussian surrogate) and S2 (cell class, averaged over futures).
   - Evidence: proven (Prop 9.1) and measured (F2). Source: section 6

Our own registered predictions that failed (13):

- P1 cubic exponent in [2.4, 3.6] on >= 80%: 79%
- P2 nets' cubic coefficient within [1/3, 3] of the exact chain's: 47%
- P4 first clause (frozen worse at L/4 on >= 90%): 89%
- P5 decay exponents in registered bands: 17 groups pass, 10 fail
- P6 two-sided cells <= 0.8 x forward-only on >= 60%: 56%
- P9 multi-reference below one-reference on >= 70%: 50%
- P10 first clause (eigenvalue log-slope band on >= 90%): 85%
- P11 first clause (more than 8 bits at L/2 for L = n on >= 75%): 43%
- A2 gain grows 1.0-2.0x from n = 32 to 256: 2.01x
- A3 several reference trajectories do not beat one on >= 75%: 65%
- G1 stability within 2x: 2.04x
- B1 at L = n (closure nMSE slope in [-1, 0]): -2.05; B2 at L = n (gain grows at most 2x): 0.38 -> 3.26, 8.6x
- P8 misses under the hashed scorer's stricter reading (61%), counted as a hit as worded

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (6):

- Corrected by bit-accounting-arc (bit-accounting-arc-2026-11-02.md): Section 3.6 compared the formula with d = PR (224 / 112 / 45 bits at l = 4 / 8 / 16, net 4000, nMSE 0.1) with interim learned counts 230 / 104 / 34-52 and called it within 3-8% at l = 4 and 8. The later variable-rate counts on the same net are 192 / 82 / 27 (look-ahead start; 236 / 100 / 32 from the reference start), so the formula is 1.2 / 1.4 / 1.7 times the registered count (P1.7, within 2x: pass). Those later counts are themselves upper bounds (layer 16 at 10%: 24 bits with 8x steps). Layer 0, '>256' here, was resolved to 575 bits (net 4000). (bit-accounting-arc report sections 5, 6 (P1.7), 4.1)
- Corrected by bit-accounting (bit-accounting-2026-11-02.md and work/bit-accounting/results/A1_table.md): The counts used in 3.6 were an interim relay for net 4000. The final table gives medians over four nets of >256 (l = 4), 135 (l = 8), 43-46 (l = 16), 25 (l = 24), 24 (l = 31), output 25; and at l = 8 and l = 24 only the linear transform code was run ('C learned' is empty there), so '104 at l = 8' is a linear-code count, not a learned one. (bit-accounting report section 4.1; A1_table.md (eps = 0.1 table))
- Withdrawn; self (co-prover round 2 audit of v1): Finite-width '1.7-3.3x enhancement' of the cubic law was a normalisation artifact; the forward-only / two-sided separation holds averaged over futures, not for a fixed net; the hash proposition's smallest gain is 4(K-1)/K, not 'at least 4'. (report Summary ('Corrections made today'), sections 3.2, 10)
- Withdrawn; self (fresh reviews 1 and 2): 'References are samples' is an upper bound, not a lower bound; the point-method rate is conjectural without the surrogate; the closure cost describes one implementation; the 'best' merge is not forward-only; 'the error stops falling, the gain peaks, the lead is closed' softened to moderate evidence for a peak and 'weakened, not closed'; Prop 7.7's sign corrected; C_V recomputed (13.481). (report section 10)
- Withdrawn; self (co-prover round 3): The hardness lane's K = 2 slopes, cited as evidence on closures, describe ARC's truncated recursion, not the exact Gaussian closure. (report Summary ('Corrections made today'), section 9)
- Withdrawn; self (co-prover round 4): Martingale needs the frozen-at-death convention; profile constants came from a truncated sum (10.63, 0.058) and a wrong approximation 5.5/(l + 5.5), now 10.65, 0.060 and 8.3/(l + 9); the lower bound is a theorem for an idealised source only; the 88% agreement on old nets mostly counts censored and zero-bit cases (23 of 64 resolved); the enumeration comparison is not a necessary condition for beating sampling. (report section 10 (round 4); dated log 23:48Z 1 Nov)

Not finished: C4 open; (H_R) untested; which d applies to nets open; C5 open; the registered cross-lane test 'on more nets and widths' that would settle d = PR was not run; HANDOFF.md next steps 'none started'; the PREREG phrase 'without the samplers' noise' left uncorrected.

Could not be determined when extracting: The scorer was hashed after the first evaluation outputs existed; the report says timestamps cannot verify that no output was read first. Whether each interim learned count used in 3.6 came from a learned or a linear code, beyond what A1_table.md shows for l = 8 and 24.

### bit-accounting

Report: `bit-accounting-2026-11-02.md` (lanes/bit-accounting/). Final state: 2026-11-03 01:43Z (REPORT v4; the status line carries no time; time from the outbox file and the dated log).

Headline: Unrestricted codes need about the output's own bits at every layer; local one-ReLU-layer codes need more bits the closer the layer is to the input (32x32: 41.3 vs 1.9 at 10% error). Best-found curves, not certified optima.

Status: **numerical evidence**. MEASURED on small nets (16x4 to 32x32, 3 seeds) plus one-seed controls; the report itself says best-found upper bounds, not certified; the one-model requirement is not met everywhere; P1.1 (certificates) still 'pending' with extra certificates on 55/159 cells; phase 2: H1-H5, U1, U2, B1 missed; gpt-6-astra reviews r1, r2a-c, r3; Part U-c and the code-map v2 rerun came after r3 and were not re-reviewed; no human check

Failed approaches (10):

1. **Kelvin's near-identity hypothesis P2.0 (identity-anchored codes stay near identity, so code maps separate ordered from chaotic nets)**
   - Tried: Phase-1 codes of all 159 cells (part 1, CPU); codes at l and l+1 on 56 pairs, lambda = 0.01, held-out inputs (parts 2-4, v2 rerun); chaotic tanh control, one seed.
   - Outcome: H1 missed (tanh linear share 0.52-1.0, registered below 0.5). H2 missed (ReLU 36/36 at >= 0.8, but tanh 0.91-1.0, registered < 0.5). H3 missed (26/36, registered >= 75%). H4 reversed (ReLU median 0.31, tanh 0.82).
   - Why it failed: Anchored local codes are linear on every net because their gates never enter the data cloud; the chaotic control's one-step maps are as predictable, as affine and as close to the layer map as ReLU's.
   - Rules out: One-step code-map simplicity as a discriminator of ordered from chaotic dynamics. Does not rule out differences in how bit counts grow with depth (seen), or results with more than one control seed.
   - Evidence: registered. Source: sections 3.1, 3.2
2. **Unscrambling cost as a relative discriminator (Part U, rerun U-c)**
   - Tried: Joint fine-tune of pairs (l, l+1) with a penalty forcing the next code to be an affine (or identity-up-to-scale) function of this one; ReLU 24 pairs (16x16, 32x32, 3 seeds), tanh 4 pairs (one seed); mu = 0.1-3; lambda 0.01 and 0.1.
   - Outcome: U1 missed 7/18 (Lagrangian rises by more than 2% on 8 of 18). U2 missed 0/4 (tanh Lagrangian rises 1.3-2.8%, registered > 5%). In absolute bits tanh exceeds every ReLU pair from L/4 on at mu >= 1 (e.g. 1.10 against at most 0.73), not at mu <= 0.3 and not at the input pair.
   - Why it failed: The tanh codes carry about 4 times more bits, so the same fraction; the registered contrast was relative.
   - Rules out: The registered relative contrast. The absolute contrast rests on one tanh seed and was not a registered prediction.
   - Evidence: registered (rescored unchanged on the corrected rerun). Source: section 3.3
3. **One shared code map across layers in noisy nets (H5)**
   - Tried: Shared-noise codes at six consecutive layers of noisy 16x16 and 32x32 nets, 3 seeds, 36 cells; map fitted at l applied at l+k after Procrustes alignment.
   - Outcome: H5 missed 0 of 3; MLP fit below 0 on 43 of 60 transfers; affine fit at l+4 0.34-0.55 on 32x32.
   - Why it failed: Report: failed transfer under this alignment; codes at different layers can have different numbers of active directions.
   - Rules out: Transfer under Procrustes alignment. 'It is not proof that no shared dynamics exist'.
   - Evidence: registered. Source: section 3.5
4. **One variable-rate model for all prices (Kelvin's requirement) and anchored local starts**
   - Tried: lambda-conditioned model per layer and class against three separately trained single-price models (477 spot checks); three restarts from the same analytic anchor.
   - Outcome: Within 3% on 390/477 (443/477 for the 2x-steps model); worse by up to 27%. Anchored local encoders stay affine; a local encoder twice as wide needs fewer bits on 35% of points (C3_local 65%).
   - Why it failed: Training refines the anchor; the anchor's gates sit outside the data cloud.
   - Rules out: The requirement holding everywhere; the anchored codes as best-in-class at early layers.
   - Evidence: registered. Source: Summary items 5-6; section 3
5. **Convergence of input-layer local counts (B1) and coverage**
   - Tried: P1-B: six extra restarts and 12000-step explorers on 13 of 53 early-layer local cells.
   - Outcome: B1 missed 9/13; input-layer counts fall 4-9% with twice the training (32x8 seed 5000: 29.4 to 27.1 bits). 40 cells not run; P1.1 pending.
   - Why it failed: Spot preemptions and stockouts cut the part short; counts not converged.
   - Rules out: Treating the early-layer counts as converged values.
   - Evidence: registered. Source: section 3.4
6. **Deductive estimation of the mean by propagating codes (binary chains; linear-Gaussian compressed simulator S10)**
   - Tried: Exact pushforward over all 2^b codes, b = 4-16 (local class); closed-form code law with the last decoder integrated over 8 dims on 16x16 and 32x32.
   - Outcome: Chains: error 6e-4 to 0.1 with no downward trend in b; loses to MC by 60-5000x at b = 16 and by more at equal compute. Simulator: bias floor 8e-5 and 1.1e-4, flat from 256 to 65536 points; MC matches at about 1e4 samples, RQMC at about 1e3.
   - Why it failed: Report: 'not scrambling': no step can add what the next layer's code knows and each translation loses part of what the current code had (cells do not nest).
   - Rules out: These code-propagation estimators on these small nets. A deductive estimator 'would need an input code that already holds the output's bits, which is the problem itself'.
   - Evidence: registered (S2, S10.2 hit as a predicted bias floor). Source: section 5.7
7. **Kelvin's curriculum autoencoder (S3)**
   - Tried: 16x16 (3 nets) and 32x32 (2 nets): plain autoencoder of h_l with 32 bits, weight moved to far horizons, budget shrunk 32 -> 8 bits.
   - Outcome: Autoencoder stage useless for the output at the input layer (output nMSE 0.96-2.4); with far-horizon weight 6.5-10 bits from L/4 on against an output count of 2-3; at the input still more than 32 bits; shrinking the budget does not lower counts. S3.1, S3.2, S3.4, S3.5 missed.
   - Why it failed: The input-layer encoder sees only x and never learns the shortcut; drift toward the shortcut is weaker than registered.
   - Rules out: This curriculum at these sizes and step counts.
   - Evidence: registered. Source: section 5.5
8. **Sign-bit (binary) training and jointly trained chains as identities**
   - Tried: Planted toy with k = 2, 4, 8 sign bits; unrestricted chains; exact Walsh spectra over all 2^b codes.
   - Outcome: S5.1 missed: the one-ReLU-layer encoder plateaus at nMSE 0.08, 0.17, 0.61. S5.4 missed: counts vary by more than 1.5 bits between restarts on 3 of 5 cells. S2.3 missed: unrestricted chains did not become identities. S2.2 missed: Walsh weight 0.8 at degree <= 2 on only 39% of cells.
   - Why it failed: Optimisation overhead of sign-bit training; the Walsh spectrum includes arbitrary behaviour on unreachable codes.
   - Rules out: Sign-bit counts as converged; in-sample Walsh degree as the scrambling statistic.
   - Evidence: registered. Source: sections 4.2, 5.1, 6
9. **B-ARC: near-linear transitions of ARC's output-relevant coordinates and no avalanche**
   - Tried: ARC nets 4000 and 4001 (dev 9100), consecutive and multi-step pairs from l = 16; sign flips under input correlation 0.999.
   - Outcome: BA.1 missed (16 -> 20 on net 4001 at 0.885; the report gives 0.80-0.88 for the multi-step pairs and MLP gains up to 0.08, while results/BARC_scores.json has 0.756 for 16 -> 32 on net 4001 with an MLP gain of 0.112). BA.3 missed narrowly: 2.02x and 2.29x against 2x.
   - Why it failed: Multi-step maps from layer 16 are less linear; the flip growth is 'gradual, not an avalanche' but above the band.
   - Rules out: The registered thresholds; BA.2 (threshold-like sign transitions) held.
   - Evidence: registered. Source: sections 5.3, 6; results/BARC_scores.json
10. **Unrestricted codes and real-valued codes on hard cells**
   - Tried: Unrestricted class at input layers; chaotic tanh; Feistel circuit.
   - Outcome: Nine exceptions where the unrestricted code needs far more than the output's bits (32x8 l = 0 at 1%: up to 100.3 against 23.1); tanh unrestricted codes follow the output's curve only down to an error that grows toward the input; Feistel l <= 8 unreached at 10% error.
   - Why it failed: Trained decoders did not find precise enough preimages.
   - Rules out: Nothing about the class: 'these gaps are observations, not proofs that the shortcut fails'.
   - Evidence: registered runs, descriptive reading. Source: Summary items 2, 7

Our own registered predictions that failed (10):

- H1: tanh linear share below 0.5: 0.52-1.0
- H2: tanh agreement below 0.5: 0.91-1.0 (ReLU part 36/36 held)
- H3: compression makes the map more linear on >= 75%: 26/36
- H4: reversed (ReLU median 0.31, tanh 0.82)
- H5: map fitted at l scores R^2 >= 0.8 at l+4 on noisy 32x32: 0 of 3
- U1: 7/18; U2: 0/4 (tanh Lagrangian rise 1.3-2.8% against a registered > 5%)
- B1: 9 of 13
- BA.1 missed; BA.3 missed narrowly (2.02x, 2.29x against 2x)
- Before phase 1: A1.2 (mis-specified), A1.4, A2.1 (3 of 6 nets), S1.1, S1.3, S1.6, S2.2 (39% of cells), S2.3, S2.5, S3.1, S3.2, S3.4, S3.5, S5.1, S5.4, S6.2 (missed in the favourable direction)
- Not scored: P1.1 pending; S7, S8, S10.1 pending; S11 deferred

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (8):

- Superseded by bit-accounting-arc (bit-accounting-arc-2026-11-02.md): Section 4.1's fixed-budget ARC local counts (>256 / 135 / 43 / 25 / 24 bits at layers 0 / 8 / 16 / 24 / 31 for 10% error; 210 / 119 / 135 at layers 16 / 24 / 31 for 1%; capped at 256 bits) are replaced by variable-rate counts 630 / 111 / 39 / 21 / 19 and 205 / 103 / 95: 0.7-1.0 of the old ones from layer 8 on, and layer 0 resolved. The later lane calls the two 'different upper bounds'. (bit-accounting-arc report section 5)
- Corrected by backward-bits (backward-bits-2026-11-02.md): Reinterpretation of the S4 shared-noise counts (section 5.6): with the future noise shared 'nothing is erased', so that count is at least H(c_{l+1} \| xi) >= T_l and is a different quantity from 'next layer's bits minus erased bits'. Forward-trained codes of the S4 kind carried less than chain codes at equal rate and collapsed to about 0 bits at the input layers. (backward-bits report section 2 point 5, section 5)
- Corrected by bits-bounds (bits-bounds-2026-11-01.md): Reinterpretation, post hoc on one net: interim ARC local counts read as PR_l log2(D_l(1)/eps^2) at rough layers and as the output's own ~19 bits at smooth layers. It used interim net-4000 values (230 / 104 / 34-52), not this report's final medians, and the l = 8 value is a linear-code count. (bits-bounds report section 3.6; work/bit-accounting/results/A1_table.md)
- Withdrawn; self (first Part U run, superseded by rerun U-c): Review r3 found the penalty's variance normaliser detached from the gradient, which rewards shrinking the next code. Old costs ReLU 0.07 / 0.24 / 0.38 / 0.56 and tanh 0.25 / 0.58 / 1.64 / 4.89 bits; corrected 0.03 / 0.19 / 0.38 / 0.42 and 0.18 / 0.40 / 1.08 / 2.25. Scores U1 6/18 -> 7/18, U2 1/4 -> 0/4. (report section 3.3; dated log 23:42Z 2 Nov and 01:43Z 3 Nov)
- Withdrawn; self (code maps v1 -> v2, after review r3): Late 32x32 local affine R^2 of 0.72-0.79 were near-singular regressions (0.997-1.000 with rank truncation). 'Local codes predict every next-layer gate' held only for noise-free code means; on the codes as received the share falls to the base rate. (report section 3.2; dated log 23:42Z 2 Nov ('CORRECTION to my relay'))
- Withdrawn; self (review-driven post-pass P1-A): 'Input-layer local code no better than linear' was wrong: registered local encoders all start affine and end near the linear reference; encoders started from the net's own next-layer gates need fewer bits. Early-layer counts are best-found, not certified. (report Summary item 5; dated log 12:44Z 2 Nov)
- Withdrawn; self (earlier fixed-budget runs): Learned sign/channel codes at 1500 steps were undertrained (S1.1, S1.3, S1.6 missed); the binary overhead b/C ~ 1.3-1.4 was encoder limitation, not a law (S6; main's '0.25 bit/dim' explanation was wrong). (report sections 4.2, 6; dated log 01:43Z 2 Nov)
- Withdrawn; self (review r3): B1 rescored as registered: 9/13, missed. (report section 7; prereg_hashes.txt 23:39:24Z)

Not finished: Part U-c FINISHED: 84 of 84 runs (84 files runs/U/Uc_*.json; results/Uc_scores.json written 01:41Z 3 Nov; HANDOFF.md 01:50Z 'U-c 84/84'), and the report reflects it (section 3.3, Summary item 8), keeping the first run as superseded. Unfinished: P1.1 pending (extra certificates 55/159 cells; controls' local cells and all unrestricted cells not reached); P1-B 13 of 53 cells, 40 not relaunched; S7, S8, S10.1 pending; S11 deferred; each control (tanh, Feistel, linear) has one seed only.

Could not be determined when extracting: Why the report's BA.1 range (0.80-0.88, MLP gain up to 0.08) differs from results/BARC_scores.json for net 4001 (0.756, gain 0.112); the file is dated 03:17Z 2 Nov. Section 4.2 says early-layer local counts are 'set by the restriction, not by optimisation' while Summary item 5 and B1 show they fall with better starts and longer training; the report does not reconcile the two.

### bit-accounting-arc

Report: `bit-accounting-arc-2026-11-02.md` (lanes/bit-accounting-arc/). Final state: 2026-11-02 17:05Z.

Headline: ARC 256x32 local codes need 630 / 111 / 39 / 19 bits for 10% error at layers 0 / 8 / 16 / 31 (median of 4 nets): steep fall over ~16 layers, then the output's curve. Upper bounds; only layer 0 converged.

Status: **numerical evidence**. MEASURED, registered (Part P1, amendments A1-A22); the report itself calls the counts upper bounds: by its registered rule only layer-0 local (net 4000) is converged and layers 16 and 31 at 1% error still fall 3-5% per doubling; three gpt-6-astra rounds ('fixable issues'); the 8x-steps round finished after review r3; no human check

Failed approaches (6):

1. **Kelvin's backward curriculum (train the last layer's code first, warm-start each earlier layer from the next)**
   - Tried: Net 4000: layer 31's best code (depth 6, 4x steps) composed with the layer map and distilled into the one-ReLU-layer class for layer 28, then 24, 20 (chain stopped by a spot preemption); one-step variant at layers 16 and 0 (A21).
   - Outcome: Against the better of the other two starts at 10% error: +1% (layer 28), +16% (24), +116% (20), +3% (16); no 1% error reached at layers 24, 20, 16; at layer 0 no better than 60% error at any rate.
   - Why it failed: Candidate reason, HEURISTIC: the latents become features of ever later layers, so the decoder must invert more layers. Also an approximate projection, from source codes not converged at 1%.
   - Rules out: This projected warm start. 'cannot rule out an exact curriculum from converged later codes'. The rest of the chain (16 to 0) was never run.
   - Evidence: registered (A19; two 300-step smoke tests before the hash are disclosed pilots). Source: section 4.2
2. **Converging the counts by more steps, depth and other starts**
   - Tried: Net 4000, layers 0, 16, 31, both classes, 2x / 4x / 8x steps and depth 6; registered rule: each last doubling < 3% with a matched partner and no start lower by 3% or more.
   - Outcome: Only layer 0 local converged. Layer 16 local at 1%: 170 -> 164 -> 157 -> 150. Layer 31 local at 1%: 90 -> 78 -> 75. Unrestricted at 1%: 111 -> 85 -> 81 and 88 -> 73 -> 70. Registered 1% counts are 14-37% above the lowest found at layers 16 and 31.
   - Why it failed: Still falling 3-5% per doubling at 8x steps; matched depth and width partners lost with a preempted VM or not run.
   - Rules out: Reading the 1% counts at layers 16-31, or any count on nets 4001-4003, as converged. Converged values are below the lowest found 'by an amount we cannot bound from these runs'.
   - Evidence: registered. Source: Summary item 6; section 4.1
3. **Single variable-rate encoder as a substitute for dedicated models**
   - Tried: Net 4000, layer 0 local at six bit prices; layer 31 local and unrestricted at three prices; narrow-deep net 203 layer 0.
   - Outcome: Cheap end of layer 0 (40-73% error): 4 of 7 checks fail, by up to 10x (4 bits dedicated against 43 at 73% error), and dedicated models disagree with each other (20 and 121 bits for nMSE 0.69). Layer 31 at 12000 steps: +6 to +21% (registered verdict: fail); within -1% to +5% at 48000 steps.
   - Why it failed: Undertraining of the variable-rate model at the registered budget; the low-rate region is not certified for any start.
   - Rules out: Trusting the curves above about 30% error at layer 0, where 'the true cost there may be several times below our curves'.
   - Evidence: registered. Source: section 4.5
4. **Unrestricted codes at early ARC layers**
   - Tried: Net 4000, layers 0, 8, 16, 24, 31; MLP width 1024, depth 3, sees h_l and the exact output.
   - Outcome: Layer 0 never reaches 1% error; base counts rise toward the input (17.8 -> 15.5 bits at 10%) and sit 5-21% (10%) and 20-163% (1%) above the best-known envelope. At 260-355 bits the output head reaches nMSE 0.003-0.004 while the plain decoder gives 0.055-0.11.
   - Why it failed: 'the information is there; turning it back into a layer-0 state through 32 layers is what fails'; could also be a structural reachability limit.
   - Rules out: Using these unrestricted counts as the class optimum at early layers.
   - Evidence: registered runs; decoder diagnostic post hoc. Source: sections 4.3, 4.8
5. **Search from random starts (and the registered random-start planted toy)**
   - Tried: Random starts with 10-33x encoder learning rate at ARC layers 0, 8, 16 and narrow-deep layer 0; planted toy k = 4, 16, 64 with the registered random local start.
   - Outcome: At ARC layer 0 random starts reach nothing (nMSE > 0.5 at every price) and never reach 1% error anywhere; at >= 20% error they find 25-35% cheaper codes at layer 8. Toy: 7.8 / 36.3 / 203 bits at nMSE 0.1 against known 6.5 / 25.2 / 80.1, and no nMSE 0.01 (P1.12 fails).
   - Why it failed: 'training refines a start and does not search the local class'.
   - Rules out: Random-start training as a search method here; also shows the informed-start counts at low precision are search-limited.
   - Evidence: registered (P1.12); A15/A17 runs do not enter the registered count. Source: sections 4.6, 4.7
6. **Layer-31 local code close to the analytic linear reference (P1.8 second part)**
   - Tried: Four ARC nets at nMSE 0.1 and 0.01.
   - Outcome: 0 of 4 within 10%: the learned code is 25-35% below the reference.
   - Why it failed: 'one layer of future is not "nearly linear" for a sparse nonnegative output'.
   - Rules out: The registered expectation; the miss is in the favourable direction for the learned code.
   - Evidence: registered. Source: section 6

Our own registered predictions that failed (4):

- P1.8: layer 31 local within 10% of the gram reference on >= 3 of 4 nets: 0 of 4 (C6 part passes, 555 of 557)
- P1.12: planted toy passes for both classes at k = 4 and 16 with the registered random local start: fail under every scorer
- P1.10: fail under the registered scorer v1 and v2 (sync_hits 0 of 6: cells cut by A8/A18 count as failures); pass on the measured combinations only under v3
- P1.4 and P1.5: fail under scorer v2 only (missing cells)

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (2):

- Withdrawn; self (amendments A1-A3 before most runs): SNR cap 256 stopped narrow-deep codes at nMSE 0.004 (raised to 65536); TF32 rounding raised the initial nMSE from 1.6e-4 to 0.033 (fp32 forced); reference-started local encoders were effectively affine (look-ahead start added). (report section 7)
- Withdrawn; self (review rounds 2 and 3, amendment A20): Common normalisation, convex-hull time-sharing, named output baselines, scorer v3 and matched doubling partners; 'no table cell moved by more than 5%, but several claims were narrowed'; round 3 removed convergence wording beyond the checks and stale numbers. (report section 7)

Not finished: Backward chain below layer 20 not rerun; width partners at 4x lost with bitarc-7, depth and width partners at 8x not run; unrestricted class not run at layers 2, 4, 12, 20, 28 (A8); layers 2-8 at 1% not checked for convergence; convergence verdicts exist for net 4000 only; narrow-deep cells cut by A18; layer 4's saved model lost. results/certified_curves.json marks 183 cells certified = false and 3 true.

Could not be determined when extracting: Minor inconsistencies I could not resolve from the report: section 7 says 'Nineteen amendments' and lists A1-A20 while the header and PREREG show A1-A22; the Summary gives 630 bits at layer 0 and section 5 gives 629. Who checked the PROVEN lower-bound statement is not stated.

### backward-bits

Report: `backward-bits-2026-11-02.md` (lanes/backward-bits/). Final state: 2026-11-02 21:00Z (as the status line states; the outbox file's mtime is 20:51Z).

Headline: The target (next code's bits minus erased bits) is the right ceiling (proved), but no fixed encoding carries its own rate's worth of it and the chain drifts: Kelvin's rule keeps a median 26% of the truth at the input.

Status: **negative result**. registered (B1-B12: 6 hit, 6 missed; B13-B14 amended after the outcome, not registered outcomes); propositions proved by the Claude lane agent, checked by Claude main and by gpt-6-astra (r1: Props 1, 2, 6 pass, Prop 3 restricted; r2: Prop 7's induction correct); no human check; conditional on one fixed 64-cell output quantiser per net and one noise level per config; two leaks in the direct comparator disclosed and not rerun

Failed approaches (6):

1. **Kelvin's rule as written (chain K: code rate at most the target T_l = next code's bits minus erased bits)**
   - Tried: 12 Model S nets (8x8 sigma 0.01, 8x16 sigma 3e-4, 16x8 sigma 0.2, 16x16 sigma 0.1; seeds 5000-5002), 64-cell k-means output code; at each step a posterior-predictor MLP plus the best partition of predicted distributions, or the reuse code; certificates at every step.
   - Outcome: At the input the chain's code knows 2-24% of the truth I*_0 on the 16-wide nets and 27-74% on the 8-wide ones (median 26% over 12 nets); each step keeps 28-89% of its target on 16-wide nets (median 65%); targets end at 0.1-0.6 bit against a truth of 0.13-1.58. It meets the registered 'certified all the way' criterion on no config. Exact 1-D chain: 27% at the input.
   - Why it failed: Prop 2: no informative code carries its own rate about the next code when Gaussian noise sits between the layers, so a code at rate T carries less than T (51-78% at the first step with real erasure), and the shortfall compounds.
   - Rules out: Deterministic partition codes at rate equal to the target, on these 12 small nets with a fixed 64-cell output quantiser and one noise level per config. Does NOT rule out stochastic re-simulation codes with shared randomness (Prop 7; 'Possible next step (not started)'), other quantisers or noise levels, or larger nets.
   - Evidence: registered (B4, B7 hit: the failure was predicted) and proven (Prop 2). Source: Summary items 3-4; sections 2, 4.2, 4.3, 7.2
2. **Carry 95% of the next code (chain R)**
   - Tried: Same nets; rate as needed to carry at least 95% of the target.
   - Outcome: Never compresses: codes of 5-9 bits at every layer, above the output code's own rate; targets at the input 4.1-7.9 bits against a truth of 0.13-5.2 (exceeds the truth on 11 of 12 nets). It keeps 90-99% of the truth only because it never compresses. On 7 of the 9 nets with real erasure no candidate tried reached 95% at the first step (84-94%).
   - Why it failed: Prop 6: the target also pays for the next code's own resolution (over-count); Prop 3: carrying all of T takes unbounded rate.
   - Rules out: This rule as a way to get per-layer counts of output-relevant bits. The unreached cases show only 'that the search did not find a code'.
   - Evidence: registered (B6 hit; B2 missed 9 of 12). Source: Summary item 5; sections 4.2, 4.3
3. **Output code as fixed target with the rate rule (chain P) and with the 95% rule (chain PR)**
   - Tried: Same nets; target carried back one noisy layer per step through the codes' cell tables.
   - Outcome: P: 0% of the truth at the input on 11 of 12 nets. PR: 74-91% (median 83%) at 1.2-7.5 bits; B5 missed (>= 80% on 7 of 12, needed 9); 17 of 132 steps did not reach 95%; 'no layer exceeds its successor' fails at the first step on 9 of 12 nets; B8 missed (8 of 12).
   - Why it failed: P: the cell tables blur the target and every step compresses. PR: its target, computed through the chain's cell tables, undercounts the truth ('exact cell averages are not sufficiency').
   - Rules out: P entirely on these nets. PR is the best fixed-encoding variant found but meets the registered criterion only on 16x8 (with 8x16 R and 8x8 R: 3 of 16 config-rule pairs), partly as 'a stable fallback, not attainment of 95%'.
   - Evidence: registered. Source: Summary item 6; section 4.3
4. **Real-valued Gaussian-channel codes instead of partitions**
   - Tried: z = u(h_l) + N(0, I_8) trained for the next code; registered rate price, then power-constrained codes (D8), seed 5000 of each config, 3 layers.
   - Outcome: At information rate T the analog code carries 44-82% of T, about the same as the partition; better by >= 0.1 bit at 2 of 12 points (B14 missed, 17% against 75%); worse on the near-noiseless 8x16 net. The registered rate price saturated at about 14 bits.
   - Why it failed: Prop 2 applies to any code: 'the gap is not about discreteness'.
   - Rules out: Discreteness as the cause of the per-step gap. Amended comparison, one seed per config.
   - Evidence: post hoc (amended after the registered version's outcome). Source: section 6
5. **Forward-trained codes on the shared-noise output distortion (bit-accounting S4 style)**
   - Tried: K-cell codes (K = 2-64), MLP encoder with straight-through assignment, seed 5000, 3 layers per config.
   - Outcome: Carry less about the output code than the chains' codes at similar rate (16x16, l = 14: 2.67 bits at rate 4.83 against 3.47 at 4.76) and collapse to about 0 bits at the input layers.
   - Why it failed: Training collapse at the input layers; mechanism not explained.
   - Rules out: 'forward training of this kind is not a usable baseline at the input'. Does not test other forward objectives.
   - Evidence: exploratory comparison (B12 registered and hit for PR against K). Source: section 5
6. **Learned posterior predictors on low-noise 8-wide nets, and full certification**
   - Tried: Depth-2 and depth-4 predictor MLPs; look-ahead control clustering exact Monte Carlo posteriors.
   - Outcome: Excess cross-entropy up to 1.1 bits toward the input; depth 4 beats depth 2 at up to 12 of 45 steps (B10 missed, 88%); clustering exact posteriors beats the learned code beyond 0.03 bit at 32 of 66 8-wide K steps; all certificates pass on 66-68% of steps (B11 missed, 67% against 90%); B1 missed (73%: 33 of 45 8x16 steps are within 10% of target).
   - Why it failed: Where the noise is tiny the posterior is almost a sharp partition that the predictor cannot fit; there the exact reuse composition keeps the bits.
   - Rules out: Depth-2 learned encoders as sufficient everywhere; the per-step gap prediction on near-noiseless nets.
   - Evidence: registered. Source: sections 4.2, 4.4, 8

Our own registered predictions that failed (7):

- B1: rate-rule deficit >= 10% of T at >= 90% of noisy steps: 73%
- B2: 95% rule needs >= T + 1 bit at the first step on >= 10 of 12: 9 of 12
- B5: PR keeps >= 80% at the input on >= 9 of 12: 7 of 12 (74-91%)
- B8: PR's kernel chain predicts >= 90% of what its code knows on >= 9 nets: 8 of 12
- B10: depth 4 never beats depth 2 beyond tolerance at >= 90% of steps: 88%
- B11: every certificate passes at >= 90% of K and PR steps: 67%
- B14 (amended, not a registered outcome): Gaussian code beats the partition by >= 0.1 bit at >= 75%: 17%

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (2):

- Withdrawn; self (gpt-6-astra r1, before scored outcomes): Errors fixed and scored chains restarted from scratch: test leakage in P/PR selection, zero rows in cell tables, a crash path, a scorer that counted missing certificates as passes; Prop 3 restricted to noisy steps. The registered candidate set also lacked Kelvin's 'use the last encoding' option (added as A2, chains restarted). (report section 9 (D2, D5); dated log 15:24Z 2 Nov)
- Withdrawn; self (gpt-6-astra r2 on the report): 'Best partition at rate T carries 61%' was false (67% by a four-interval partition); 'certified at every layer' became 262 of 264; the '7 hit, 7 missed' headline became 6/6 registered plus 1/1 amended; unreached '>X' entries relabelled as searches that found no code; 'only for those codes' reduced to sufficiency in section 7.3; several summary numbers corrected. (report sections 3, 4.1, 7.1, 8, 9; review/review_r2.raw)

Not finished: Not run: the recursion with stochastic re-simulation codes compressed by channel simulation (Prop 7). D9 not rerun, so B9, the 'direct' columns and the empirical bracket carry the leak. Last evaluations and B13-B14 reduced to seed 5000 per config. The rate-constrained frontier in the 1-D chain is not fully enumerated.

Could not be determined when extracting: The status line says round 2 was applied at 21:00Z while the outbox file was last written 20:51Z. I did not check whether every r2 finding was applied beyond the ones named here; the Summary's 'exact only for' wording survives finding 4.

### arc-deep-networks-note

Report: `arc-deep-networks-2026-10-29.md` (reports/literature/arc-deep-networks-2026-10-29.md). Final state: 2026-10-28 23:50Z (stated in the note; file mtime 23:59Z; the file name carries 29 October).

Headline: ARC's cumulant propagation loses to sampling as depth grows at fixed width (ARC's own statements); the note's untested arithmetic puts the crossover depth at about sqrt(n) and gives about 5% that anything of ours beats ARC at depth 16-32.

Status: **unverified**. literature note with no experiments: statements about ARC are citations (read status per source in section 6); derivations marked 'mine' are untested; contest-participant numbers are third-party and not reproduced; no review recorded; it reads phase R in its pre-review state

Failed approaches (1):

1. **Our noisy-channel approach against ARC's depth problem (assessment, no new experiment)**
   - Tried: desk comparison of phase R and phase B results with ARC's six difficulties
   - Outcome: 'Nothing in our current approach improves on this for ARC's problem': our only sample-free mean estimate is K = 2; the control variate brings no reliable gain on ReLU nets; the KL chain rule, Donsker-Varadhan and Hoelder bounds and layer-wise twisted SMC need per-layer noise and are undefined or vacuous on ARC's noiseless nets
   - Why it failed: the approach changes the object (noise, LayerNorm), not the method
   - Rules out: Nothing by measurement: this is the author's reading of earlier lanes, partly of phase R's pre-review numbers.
   - Evidence: post hoc assessment. Source: note Summary; section 2.1

Our own registered predictions that failed (1):

- None scored in the note. Its predictions P1-P5 and kill tests (section 3) were written for an experiment on ARC's noiseless nets (O0); the arc-noisy lane ran a different design (noise on for everyone, sigma >= 0.001; noiseless nets as code controls only), so P1-P5 were not scored as written.

Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (2):

- Corrected by cm-interp-random-2026-10-28.md (revision of 29 October, 'Changes after the review'): Section 2.1 repeats pre-review phase R claims: 'the lower bound rules out useful certificates on these chains beyond width about 64' (withdrawn in the revision); costs 'grow linearly in n for every family tried (Gaussian, product, copula)' (copula measured only to d = 32, open); flat per-layer costs (revision: does not establish depth-flat end-to-end costs). The note's section 2.3 already narrows '13-810x' and '47 bits' in the same way the review later did. (note section 6 (phase R read at 'final, 23:23Z'); phase R 'Changes after the review' items 1, 3, 4)
- Corrected by boundary-family-2026-10-29.md section 6: The (l/L)^3 survival law was measured for mean shifts; distributional errors do not follow it (grow 4.5x from layer 24 to 32 instead of shrinking to 0.42). (boundary-family report section 6)

Not finished: The proposed 'cleanest experiment' on ARC's exact noiseless family (O0, with noise arms O_sigma and U1/U2/U3) was not run as designed. Two questions for Kelvin (which claim to aim at; whether U2 is worth running) are left open in section 5. Unverified in the note: the paper's venue ('NeurIPS 2026' unverified).

Could not be determined when extracting: Whether later lanes outside my batch (hardness-mean-estimation, lyapunov-dimension, arc-update) tested or corrected the sqrt(n) crossover and the noise forgetting depth; the hardness report cites this note and has a proposition on one-step survival of mean errors, which I did not read. The brief's direction list has no 'tested_by', so partial tests by arc-noisy are recorded in component notes.

### synthesis-draft

Report: `synthesis-draft-2026-11-02.md` (reports/synthesis-draft-2026-11-02.md). Final state: 2026-11-02 14:15-14:40Z (from lane files as they stood at ~14:25Z).

Headline: No positive: every deductive method tested at 256x32 wins at most a constant factor in a budget window; at the budget RQMC beats those that fit by 7-65x. A restricted negative. Several inputs were interim and later changed.

Status: **superseded**. unreviewed draft; superseded where later finals differ: preint final (17:28Z), randomness final (~16:20Z), future-aware final (20:05Z), phase1-board note (15:33Z); the later paper note work/papers/arc-negative.md (Appendix A) uses the finals


Claims of this lane that a review or a later lane corrected, qualified, withdrew or superseded (5):

- Superseded by preint final (preint-2026-11-02.md): Rows A28, A29, A38 and the F7/F9 statements of section 3: '~nL evaluations identify W' withdrawn; barrier narrowed; dev '25-500x worse' replaced by registered 21-1,410x (minimum over common budgets) (work/papers/arc-negative.md Appendix A; preint report Summary 5-6)
- Superseded by randomness final (randomness-2026-11-02.md): Pending items of section 3 and rows A32-A35: registered exponents (1.045, 1.058) and constants (Kerdock 2.89x); 'random bits are free' qualified as existential / under exact primitives (work/papers/arc-negative.md Appendix A; randomness report Summary)
- Superseded by future-aware final (future-aware-2026-11-02.md): TL;DR and rows A23, A24, A43: hybrid 0.8-1.0x became 1.00-1.03x at 6.5e4 passes; deductive window 2.4-3.0x 'best case' became 0.5-0.7x with pilot and dense extraction (as implemented 0.04-0.12x); 270x became 204x / 236x (work/papers/arc-negative.md Appendix A; future-aware report Summary 3, section 4.4)
- Superseded by phase1-board (FINDINGS.md): C10 and row A2: the board gap is attributed to public-set fitting (INFERRED for the final run) (log 2026-11-02 15:33Z)
- Superseded by work/papers/arc-negative.md (draft v2, 3 Nov): The paper note replaces the draft as the cross-lane synthesis and cites it only for the 'super-linear time lower bound' heuristic, the metric caveat and one conjecture (work/papers/arc-negative.md Appendix A, B)

Not finished: Never finalised; pending markers remain in the text for the randomness, preint, future-aware, bit-accounting and backward-bits lanes.

Could not be determined when extracting: C9 (bit counts) depends on lanes outside this batch. The draft's own negative results are those of the lanes and are recorded under each lane, not repeated here.

