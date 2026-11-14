# ARC mean estimation: lanes, proofs and negative results

Public since 14 November 2026. `OPEN-DECISIONS.md` lists what is still undecided for the paper draft.

This collects Kelvin's research on the Alignment Research Center's (ARC) mean-estimation problem, from 26 October to
3 November 2026: 37 research lanes with their reports, proofs, code and small result files, the cross-lane
write-ups, and the negative results. It was assembled on 14 November 2026 as a snapshot. No experiment was re-run and
no source file was edited.

## The question

ARC asks for a "mechanistic" estimate of a network's expected output that is at least as good as sampling for the
same compute: squared error of eps^2 times the output variance in about 1/eps^2 forward passes, without drawing
samples. Their test case is a random ReLU network with He-initialised weights, no biases and Gaussian input, where the
estimand is the mean of every output neuron for one fixed draw of the weights. ARC's cumulant propagation beats
sampling when the network is wide and shallow. ARC themselves state that its depth scaling is worse than sampling and
list depth growing with width as open. The public contest built on the problem fixes width 256, depth 32 and a
budget of about 65,000 forward passes ("Phase 1").

Kelvin's target for this work ("M1" in `reports/context/cm-interp-program-2026-10-28.md`): a sample-free estimator
that matches or beats sampling on deep random networks at depth growing with width, for example 256 x 32, or a
strong argument for why that is hopeless. Two sub-questions run through the lanes:

1. Does any deductive, layer-wise method keep pace with sampling as the width grows at depth proportional to width?
2. At 256 x 32 and the contest budget, does anything beat the best sampler, which is randomised quasi-Monte Carlo
   (RQMC), not plain Monte Carlo (MC)?

A third thread asks why it is hard: which information about the input a layer must keep for the output mean ("the
bits that matter"), whether that information is scrambled from layer to layer, and what can be proved. Kelvin's own
conjecture on this, the pseudorandom-code conjecture, is in `reports/wiki-copies/`.

## Where it stands

- **No positive result at the target shape.** Every deductive method tested at 256 x 32 wins at most a constant
  factor, in a budget window that closes below about 3-5% of the contest budget. At the budget RQMC is 7-65x more
  accurate than the deductive methods that fit, and hybrids reach parity with RQMC.
- **The negative is restricted.** It is measured for the methods tested. It is proved only for restricted classes
  (rules chosen without looking at the weights; one-way linear summaries; black-box and worst-case settings), and
  conditionally for ARC's hierarchy if ARC's own error law is tight. There is no lower bound for all algorithms on
  random networks; a heuristic argument in the lanes says none is reachable with current techniques.
- **No proof here has been checked by a human.** Proofs were written by the lane agents or by a co-prover model and
  checked by models. "Proved" below always carries that limit.
- **Positives that stand**, all outside the target: a hybrid of ARC's propagation and a Kerdock design on noisy nets
  at depth 8; a sample-free tail readout at depth 8; a multilevel sampler that beats plain MC at large depth under
  cost hypotheses. ARC's own ladder is steep at the wide, shallow Phase-2 shape (1024 x 16).
- The best single account is the paper draft `reports/paper-draft-arc-negative/arc-negative.md` (v2, 3 November). It
  is a draft with twelve open decisions.

`NEGATIVE-RESULTS.md` lists every failed approach (286 entries), what was tried, why it failed and what it rules out.

## Status words

Each row has exactly one status, taken from what the lane's report says about itself and what its own checks show.

- **proved**: the headline is a theorem the report labels proven. Written and checked by AI models only.
- **numerical evidence**: the headline is a measurement or computation supporting a positive or descriptive claim.
- **negative result**: the headline is that an approach failed, lost to the baseline, or a conjecture was refuted.
- **superseded**: a later report replaces the headline; the row says which.
- **unverified**: never reviewed, never passed review, an untested derivation, or a relay the source itself marks as
  inferred.

Most lanes are mixed: a negative headline with proved lemmas and measured side results. The status follows the
headline and the bracket says what the rest rests on. "Registered" means predictions were written and hashed before
the run. "Reviewed" means a fresh session of another model (GPT-6 through Codex, sometimes Gemini) reviewed the
report; in several lanes the final text was edited after the last review and not re-reviewed.

## Lanes

Dates are the report's final state (UTC). Paths are under `lanes/`. Each lane directory has `report/` (the lane
report), `work/` (the snapshot of its work directory) and `PROVENANCE.md` (original path, dates, what was left out).

### Measured at the contest shape (2-3 November)

| Lane | Claim | Status | Corrects / corrected by | Date | Path |
|---|---|---|---|---|---|
| arc-update | ARC's own code at 256 x 32: order 2 beats RQMC about 2x only near 450 passes (4 of 5 nets), order 3 loses 5-30x, and at the budget RQMC is 7-40x better. Slope between orders 2 and 3 along depth = width/8 is 0.23-0.52 against sampling's 1. | **negative result** (registered benchmark, 31 of 40 scorecard rows hold; restricted to the methods tested; reviewed once, final text not re-reviewed; theory AI-only) | Its "untested public counter-claim" was tested by `scale-mode`. Its reading of the public leaderboard (best samplers 10-50x better than MC) is corrected by `phase1-board`. `future-aware` extends its ladder to 512 x 64, where order 2 falls below RQMC. | 2026-11-02 | `arc-update/` |
| scale-mode | A contest participant's public "scale mode" closure, run unchanged: 2.5x better than RQMC at its own cost (688 passes), caught at about 2.3x that cost, 33-65x behind at the budget. Neither registered escape criterion was met. | **negative result** (registered, 40 of 45 rows hold; reviewed, final text not re-reviewed; intervals exploratory). See `OPEN-DECISIONS.md` D12. | Corrects `arc-update` (claim now tested). A sentence in `future-aware` still calls the estimator unverified; this lane's final supersedes it. | 2026-11-02 | `scale-mode/` |
| future-aware | Using a backward pass to find where the future reads a closure's error helps by constant factors only. The deductive member loses to RQMC 6-200x as implemented; the hybrid is at parity (1.00-1.03x RQMC at the budget). | **negative result** (registered; 8 of 13 rows hold as scored; the hybrid score and cost ledgers are post hoc; five review rounds; a co-prover round after the report found two of the author's claims false, recorded only in `work/FORMAL.md`) | Corrects the `synthesis-draft` (hybrid 0.8-1.0x became 1.00-1.03x; deductive window 2.4-3.0x "best case" became 0.5-0.7x with all costs charged). Its stale sentence on scale mode is superseded by `scale-mode`. | 2026-11-02 | `future-aware/` |
| preint | Exact pre-integration along a line raised the fitted exponent only at input dimension 4-8 and lost at equal compute on every net (21-1,410x along the ladder up to 256 x 32). A barrier for point rules chosen without the weights is proved under a measured hypothesis. | **negative result** (registered, 7 of 11 tests hold; three review rounds; barrier theorems by the lane author, audited and repaired by the co-prover; not human-checked) | Its final withdraws "about nL evaluations identify the net", which the `synthesis-draft` had labelled proven, and narrows the barrier. | 2026-11-02 | `preint/` |
| randomness | No structured sampler was shown to beat RQMC's exponent (fits 1.0-1.13 at 256 x 32). Designs buy constants; the best is a Kerdock 5-design at 2.9x over MC. For weight-independent positive rules the asymptotic exponent is within [1.008, 1.012] at width 256 (proved, AI-only). | **negative result** (registered, 25 of 32 hold; reviewed once, final text not re-reviewed; the main limit theorem was only structure-checked, and its one registered test failed narrowly) | Corrects the `synthesis-draft`'s pending numbers and a relayed "3-5.5x" ceiling. | 2026-11-02 | `randomness/` |
| adaptive-regions | Depth-4 nets of width 4-8: exact cells win only where cells are few; merging saves a constant 2-3x that does not improve with width; chains indexed by gate patterns stay 100x+ behind MC; learned experts show no stable gain. | **negative result** (exploratory throughout, nothing registered, 3 nets per width; reviewed twice with items open; lane closed by redirection, not by conclusion) | Learned-experts results before 2 Nov 18:56Z were ruled not to count; the report does not say so everywhere. | 2026-11-03 | `adaptive-regions/` |
| phase1-board | The top public Phase-1 score is not explained by the cost rule. It is attributed to fitting the 50 public nets (verified for earlier runs of the same entrant, inferred for the final run); unfitted runs are about 6x plain MC. | **unverified** (desk research on public pages, no code run, no review). See `OPEN-DECISIONS.md` D3, D11. | Corrects the leaderboard reading in `arc-update` and the `synthesis-draft` (conflict C10), and an earlier wall-time hypothesis. | 2026-11-02 | `phase1-board/` |
| cumulant-ambiguity | The oracle form of the pseudorandom-code conjecture is false: exact low-order moments of every hidden layer nearly pin the mean. ARC's ladder at depth = width/8 matches the sum of typical per-step closure errors. The lower-bound theorem is open. | **numerical evidence** (the refutation and bounds are proved, checked by the co-prover only; the typical-case measurements are exploratory, 3 nets per shape, run after the checks and never reviewed) | Puts `moment-matching` in context (an input-moment gap is no error bound once the input is known to be Gaussian). | 2026-11-03 | `cumulant-ambiguity/` |
| moment-matching | Matching the Gaussian input's moments to degree d leaves the output mean undetermined by at least 0.21 standard deviations at every degree run (widths 4-8, depth 1-8, d up to 8). | **unverified** (exploratory, unreviewed, 3 nets per shape, top-degree runs stopped early; the report is a short note saved from the lane's final message) | Qualified by `cumulant-ambiguity`. | 2026-11-03 | `moment-matching/` |

### Exact methods and narrow-deep networks (29 October - 2 November)

| Lane | Claim | Status | Corrects / corrected by | Date | Path |
|---|---|---|---|---|---|
| nd-exact | Width 8, depth 256: the certified cell code is 23-106x worse than RQMC (0 of 6 nets pass); integrating the top regions and dropping the rest loses 7-1,222x even at an optimistic cost. | **negative result** (registered; three review rounds, last minor edits not re-reviewed; about the methods tested, not an impossibility proof) | Re-runs the `relevance` lane's radius estimator with its setup charged. | 2026-11-02 | `nd-exact/` |
| unrestricted | Certified branch-and-bound fails as a deductive method (never beats RQMC; best ratio 0.18). Determinism is no restriction on random weights. Plain MC is not optimal at depth: a multilevel sampler beats it (about break-even at 256 x 32). | **negative result** (registered and reviewed twice, both "major revision", final text not re-reviewed; the multilevel gain is proved under cost hypotheses with two key inequalities unchecked by the author; its measured gains are post hoc) | Replaced its own conjecture C0 (plain MC optimal) by C0*. Changes the baseline for earlier lanes, including `hardness` section 6.3. | 2026-10-31 | `unrestricted/` |
| narrow-deep | Plain narrow-deep nets synchronise, so only the first ~n ln(1/tol) layers are hard. On random residual nets a Gaussian closure beats the samplers tried only at 18-35 paths' cost. It fails on trained nets. No advance on the target. | **numerical evidence** (measured; the residual-closure headline is exploratory; two reviews, "major revision" and "revise", revised text not re-reviewed) | `narrow-deep-m1` found its hybrid and deep part do not carry over to fresh nets (diverges on 4 of 6). | 2026-10-30 | `narrow-deep/` |
| narrow-deep-m1 | Width 8, depth 256: the two sample-free estimators built each beat RQMC 3x on only 2 of 6 healthy nets; the registered target tests fail. | **negative result** (registered; reviewed twice; limits are "floors of the methods we built, not proven lower bounds") | Corrects `narrow-deep` (above). A draft 330x win broke the registered rule and was withdrawn. | 2026-10-31 | `narrow-deep-m1/` |

### First families on ARC's benchmarks (27-29 October)

| Lane | Claim | Status | Corrects / corrected by | Date | Path |
|---|---|---|---|---|---|
| arc-noisy | ARC's nets with small activation noise: no win at depth 32 at the primary noise levels, for means or tails. At depth 8 a propagation + Kerdock hybrid beats the best sampler 1.2-9.9x, and a sample-free tail readout improves on ARC's (+0.32 more 1e-8 events within 50%). | **negative result** at the target depth (registered; the depth-8 results are registered numerical evidence; reviewed per part, text edited after the last reviews; its summary's "every claim was pre-registered" overstates) | An earlier depth-32 headline was false and was corrected at review. Its survival law is narrowed by `boundary-family` (holds for mean shifts only). | 2026-10-29 | `arc-noisy/` |
| algzoo-noisy | ARC's AlgZoo RNNs with noise: every deductive description built loses to Monte Carlo by 1e2-1e5 at equal compute; only the 10-parameter closed form for the smallest model wins. Widths 32/64 tolerate noise 0.01. | **negative result** (registered, kill tests fired; six review rounds; most structure results rest on one model or seed) | "Wider is sparser" reads stronger in its summary than in section 10 (the kept-edge count grows 2.3-3.4x per width doubling). | 2026-10-29 | `algzoo-noisy/` |
| boundary-family | Boundary-aware cell families failed both registered development kill tests, so no evaluation run was made; cells built from the weights stay at order 2's level at 256 x 32. | **negative result** (two registered kill tests on development nets only; the rest exploratory; sections 6-7 written after the review) | Corrects the survival law used in `arc-noisy` and the literature note. | 2026-10-29 | `boundary-family/` |
| nongauss-family | None of the fully non-Gaussian families built was shown to scale with depth; only 64-128-dimensional joint blocks reach the fit floor at single cuts, and re-projecting at every layer accumulates error. | **negative result** (registered; oracle fits only; one registered verdict flipped at review from "sublinear" to "about linear" and is unresolved) | The log line "compact structure exists" predates that review. | 2026-10-29 | `nongauss-family/` |
| sparse-codes | No sparse structure found at the noise precision beyond the gate pattern: no dictionary up to 16x width reaches the noise; transcoder closures lose to neuron-level order 2. | **negative result** (registered; design and claims reviews; results added after the review are unreviewed; single seeds; "not impossibility results") | Replaces an assumption of `cm-interp-R` ("random layers have no sparse structure") with a measurement. | 2026-10-29 | `sparse-codes/` |
| cm-interp-R | "Phase R": on random noisy normalised MLPs the forward chain works as an estimator and fails as a certifier; coverage cost grows linearly with width and every certified bound is vacuous. | **negative result** (registered; one review of the first version; the 29 October revision, with new numbers, was not re-reviewed; nets differ from ARC's) | Its revision withdrew claims that the literature note `arc-deep-networks` still repeats. | 2026-10-29 | `cm-interp-R/` |
| estimability | Training a small transformer with a penalty on the gap between propagated and sampled cumulants cut the estimation error 9-191x at a task cost, and propagation still lost to sampling by 15-50x. | **unverified** (registered measurement with a "SUCCESS" verdict the report itself qualifies twice; no review recorded; parked by Kelvin on 27 October) | - | 2026-10-27 | `estimability/` |

### Theory: hardness and what a layer must keep (29-31 October)

| Lane | Claim | Status | Corrects / corrected by | Date | Path |
|---|---|---|---|---|---|
| hardness | Using only runs of the net, sampling is optimal up to about 4x. With the weights, in the worst case no deterministic method matches sampling under #NSETH. For random nets at depth ~ width no general lower bound is possible with current tools. | **proved** for the black-box and worst-case settings only (AI-written; audited by Gemini and GPT-6; not human-checked). For the actual target the result is "no bound, open". The measured section 6.3 is unreviewed and not registered. | `bits-bounds`: the order-2 slopes of 6.3 are for ARC's truncated recursion, not Gaussian closures in general. `unrestricted`: plain MC is not the right baseline at depth. Its 16-seed sweep replaces a two-point observation in `random-phases`. | 2026-10-29 | `hardness/` |
| lyapunov-dimension | Along one input path few directions matter (about 24 at 256 x 64, not the heuristic 75), but one block for all inputs cannot use this. "The best we can hope for" is not established. | **numerical evidence** (theorems A-D proved, AI-only, reviewed by GPT-6 and Gemini; the headline counts are measured; its composition test was refuted by its own rule) | - | 2026-10-29 | `lyapunov-dimension/` |
| random-phases | Chaotic nets forget their input, so a backward description works. Critical He-ReLU nets (ARC's family) barely forget by depth 64, and an input-independent backward stand-in fails there. | **numerical evidence** (registered, several thresholds missed; one review of the width-256 part only; single nets) | Its "order 2 only keeps pace with sampling" is replaced by the sweep in `hardness` 6.3. | 2026-10-29 | `random-phases/` |
| gate-entropy | AlgZoo RNNs need only 2.3-7.4 merged gate bits per step. Random depth-32 MLPs have gate entropy proportional to width, and no merging was found at width 128 or more. | **numerical evidence** (registered census; one review; achieved sizes, not bounds; one seed per configuration) | - | 2026-10-29 | `gate-entropy/` |
| cut-rank | The premise "a linearly read front summary needs exp(c k*) numbers" is false as a law. Proved instead: the count grows like (1/eps)^(2(n-1)/3) at fixed architecture, with tiny constants; not a running-time bound. | **negative result** (the refutation and the replacement law are proved for one-way linear summaries; key proofs by the co-prover, reviewed by the same model in a fresh session; the genuine-ensemble theorem was checked by the lane agent only) | Narrowed by `cut-rank-ext`. Quotes a pre-data number from `kstar-frames` that the final measurement replaced. | 2026-10-31 | `cut-rank/` |
| cut-rank-ext | The cut-rank law does not survive nonlinear readouts or back-and-forth with real numbers, so size bounds of this kind cannot cover ARC's closures. It survives for bounded-degree readouts and as bit counts. | **negative result** (proved by construction, AI-only; asymptotic in eps at fixed architecture; six partly fixed review items, not re-reviewed) | Narrows `cut-rank` (which stands for one-way linear summaries) and the use of `kstar-frames` Proposition 2. | 2026-10-31 | `cut-rank-ext/` |
| kstar-frames | Along one input the frame of relevant directions follows the inverse-transpose layer map but is set by the weights still to come. A learned map recovers 93-99% of sensitivity, yet no method cleared the registered gate and no estimator was built. | **negative result** (registered gate failed; propositions proved for the noiseless net, AI-only; reviewed twice) | Corrects the stale number quoted in `cut-rank`. Proposition 2's reach is narrowed by `cut-rank-ext`. | 2026-10-31 | `kstar-frames/` |
| tractable-gates | Smooth gates need fewer summary numbers asymptotically (one back layer, under scale conditions), but at tested sizes smoothness is not the main factor, and the Gaussian closure beat both samplers on 0 of 45 trained nets. | **negative result** (registered, 8 of 15 predictions refuted in whole or part; the asymptotic part is proved under conditions; the co-prover found 7 claims of the first version wrong; the second review still said "major revision") | Its raw ranks differ from `cut-rank`'s at the same shapes under a different design; neither report reconciles them. | 2026-10-31 | `tractable-gates/` |
| stationary | The stationary state of a critical ReLU stack with noise exists, is unique, scales with the noise, and its radius is an exact one-dimensional chain. It is not easier to estimate: structure buys 2-8x constants that do not grow with width. | **numerical evidence** (the characterisation is proved with the co-prover; the estimation verdict is measured and registered, about 30 sub-predictions missed; one review, "major revision", revision not re-reviewed) | `stationary-numerics` contradicts its near-floor rate (0.31 n, not 0.4 n) and one band. `input-bits` corrects "the radius carries the input" and where the input regime ends. | 2026-10-31 | `stationary/` |
| stationary-numerics | The stationary radius law solved at every width with closed-form corrections; a noisy-kernel fixed point for the replica angle; interaction order grows with width. | **unverified** (three review rounds each ended "major revision" and the log says the report has not passed review; 17 of 35 registered predictions hit; several headline items are heuristic models) | Corrects `stationary` (above). Its assumed 1/k cloud spectrum is refuted by `gram-chain`. | 2026-10-31 | `stationary-numerics/` |
| input-bits | The input variance splits exactly into radius, amplitude and direction; the input radius carries only 3-9%. "Growing interaction order explains shrinking RQMC gains" is refuted as registered. Structured samplers buy 2-7x constants, no rate gain. | **numerical evidence** (registered; three review rounds; theory largely by the co-prover; 2-4 nets per cell) | Corrects `stationary`; confirms one finding of `stationary-numerics`. | 2026-10-31 | `input-bits/` |

### Bits: what must be kept, and is it scrambled (1-3 November)

| Lane | Claim | Status | Corrects / corrected by | Date | Path |
|---|---|---|---|---|---|
| gram-chain | A weight-averaged theory of what a layer's state decides: the exact chain matches its closed curves within 0.003-0.014 at widths 256-1024 and its other laws within 10-30%. It cannot say which directions. | **numerical evidence** (the tool is proved, the laws heuristic; registered 16 hit / 7 miss; two reviews, both "major revision", applied; last runs not re-reviewed) | Refutes the cloud spectrum assumed in `stationary-numerics`. Qualifies `relevance` Corollary 1c. | 2026-11-02 | `gram-chain/` |
| relevance | A heuristic accounting predicts the counts of tested subspaces within 2x on 55-56 of 56 prospective cells of fresh ARC nets; the variance budget and mean degree less reliably. Both registered per-net mean-degree tests missed. | **numerical evidence** (heuristic model with registered tests; one theorem proved, AI-only; three review rounds; counts are for exhibited subspaces, not certified) | Corollary 1b corrected through `bits-bounds`; 1c qualified by `gram-chain`; `bit-accounting-arc` says its numbers are not comparable at early layers. | 2026-11-02 | `relevance/` |
| bits-bounds | A heuristic formula for the bits a cut needs separates cuts needing many bits from those needing none; intermediate counts only within about 2x. Bounds hold for restricted classes only. | **numerical evidence** (heuristic; main registration 3 hit / 8 missed; both reviews "major revision"; the lower bound is proved only for an idealised source whose hypotheses fail for nets) | Its "within 3-8%" match with learned codes used interim counts and is corrected by `bit-accounting-arc` (1.2-1.7x off). Corrects `relevance` 1b and qualifies `hardness` 6.3. | 2026-11-01 | `bits-bounds/` |
| bit-accounting | On small nets, unrestricted codes need about the output's own bits at every layer; codes local to one ReLU layer need more the closer the layer is to the input. Codes look simple from layer to layer, but so does the chaotic control, so the test does not discriminate. | **numerical evidence** (best-found upper bounds, not certified optima; several registered hypotheses missed; the last rerun and code-map numbers came after the final review) | Its fixed-budget counts for 256 x 32 are superseded by `bit-accounting-arc`. Its shared-noise counts are reinterpreted by `backward-bits`. | 2026-11-03 | `bit-accounting/` |
| bit-accounting-arc | At 256 x 32, local codes need 630 / 111 / 39 / 19 bits for 10% error at layers 0 / 8 / 16 / 31 (median of 4 nets): a steep fall over about 16 layers, then the output's own curve. | **numerical evidence** (registered; upper bounds; by the lane's own rule only the layer-0 count is converged; three review rounds; the last runs finished after the final review) | Supersedes the 256 x 32 counts in `bit-accounting`; corrects `bits-bounds` and `relevance`. | 2026-11-02 | `bit-accounting-arc/` |
| backward-bits | "Next code's bits minus erased bits" is the right ceiling (proved), but no fixed encoding carries its own rate's worth of it and the backward chain drifts: a median 26% of the truth survives at the input. | **negative result** (registered, 6 hit / 6 missed; propositions proved and checked by models; two leaks in a comparator disclosed and not rerun) | Reinterprets the shared-noise counts of `bit-accounting`. | 2026-11-02 | `backward-bits/` |

## Cross-lane reports and context

Paths are under `reports/`.

| Item | What it is | Status | Date | Path |
|---|---|---|---|---|
| Paper draft "Deduction vs sampling at depth proportional to width" | The consolidated restricted negative, with a claim ledger and theorem provenance. v2 answers two referee reports; v2 itself was not re-reviewed. v1 is kept beside it. | **negative result** (draft; held behind decisions D1-D12) | 2026-11-03 | `paper-draft-arc-negative/` |
| Synthesis draft | First cross-lane synthesis, written while four lanes were interim. | **superseded** by the `preint`, `randomness` and `future-aware` finals, the `phase1-board` note and the paper draft | 2026-11-02 | `synthesis-draft-2026-11-02.md` |
| Summary of 31 October | The coordinating agent's summary of the theory lanes. Two of its lines read stronger than the lane reports ("the exp(c k*) premise is refuted" is refuted as a law; "ARC's closure is biased at every fixed order" is proved for the basic truncation on one event). | **unverified** (not reviewed) | 2026-10-31 | `summary-2026-10-31.md` |
| Pseudorandom-code conjecture | Kelvin's conjecture for why ARC's plan may be hard: if the map from input to a late layer's code is pseudorandom and the code-conditional means vary, nothing computes the mean much faster than sampling. A copy of the wiki page. | **unverified** (a conjecture, not a theorem; the page marks itself as an inferred relay; its worst-case witness came from the co-prover unchecked). `cumulant-ambiguity` found its oracle form false; `moment-matching` and the pattern chains in `adaptive-regions` bear on it. | 2026-11-03 | `wiki-copies/arc-pseudorandom-code-conjecture.md` |
| ARC's matching-sampling bar | What ARC's bar is and what has met it. A copy of the wiki page. | **unverified** (an inferred relay of two literature notes) | 2026-11-02 | `wiki-copies/arc-matching-sampling-bar.md` |
| ARC on deeper networks | Literature note with the author's own untested arithmetic (crossover depth about sqrt(width)). | **unverified** (no review; corrected by the `cm-interp-R` revision and by `boundary-family`; its proposed experiment was never run as designed) | 2026-10-28 | `literature/arc-deep-networks-2026-10-29.md` |
| ARC's work on random networks | Literature search with quotes from ARC's paper and posts. | **unverified** (no review) | 2026-10-26 | `literature/arc-random-networks-search-2026-10-26.md` |
| Careful read: wind tunnels, TabPFN, AlgZoo | Reading notes; the AlgZoo part is the ARC-relevant one. | **unverified** (no review) | 2026-10-26 | `literature/careful-read-wind-tunnels-tabpfn-algzoo-2026-10-26.md` |
| Dense networks and tangledness | Literature check on whether dense networks can be interpreted; a model fact-check was applied (in `lit-tangledness-review/`). | **unverified** (citations, not results of ours) | 2026-10-29 | `literature/lit-tangledness-architectures-2026-10-29.md` |
| Width and sparsity | Literature check for one `algzoo-noisy` finding; kept in that lane's `report/`. | **unverified** (no review) | 2026-10-29 | `../lanes/algzoo-noisy/report/` |
| Programme review | A reviewer model's critique of the programme and of the learned-experts plan (prompt and final message). | **unverified** | 2026-11-02 | `programme-review-2026-11-02/` |
| Digests of 9 November | Two digests of the ARC and bits lanes written by subagents on 9 November. Untrusted: read the lane reports instead. | **unverified** | 2026-11-09 | `unverified-opus-digests-2026-11-09/` |
| Programme definition | The agreed targets M1-M3 and Kelvin's bar ("a major advance"). Context, not a result. | - | 2026-10-28 | `context/cm-interp-program-2026-10-28.md` |
| Dated log, ARC extract | The ARC entries of the coordinating agent's log, 29 October - 3 November. An extract; see its header. | - | 2026-11-03 | `dated-log-arc-extract-2026-10-29.md` |

## Lanes that may still change

No ARC lane had a file modified in the 24 hours before the snapshot; the newest source file in any of them is dated
3 November 2026 11:37 UTC. So none looked in progress by that test. By their own reports these were left unfinished:

- `adaptive-regions`: redirected before concluding; five review items open; the learned-experts part was not rerun
  with accurate truths.
- `cumulant-ambiguity`: the intended theorem is open; run files written after the report are not in it.
- `moment-matching`: top-degree runs were stopped early.
- `bit-accounting`: one registered item (certificates) is still "pending".
- `estimability`: parked.

The owning agent may add to any lane after this snapshot. `PROVENANCE.md` in each lane records the snapshot time.

## Layout

- `README.md`, `NEGATIVE-RESULTS.md`, `OPEN-DECISIONS.md`, `EXCLUDED.md`.
- `lanes/<lane>/`: `report/`, `work/` (code, registrations, proofs under `FORMAL.md` and `coprover/`, reviews under
  `review/`, small result files), `PROVENANCE.md`.
- `reports/`: the cross-lane items above.
- `records/lane-records.json`: the per-lane extraction records behind the tables here and `NEGATIVE-RESULTS.md`
  (claim, status, evidence quotes, components, corrections, failed approaches, failed predictions). Written on
  14 November 2026 by reading each report in full; not reviewed.
- `tools/`: the scripts that made the snapshot, the log extract, the exclusion list and the secret scan.

Not in the repository: model weights and arrays, files over 5 MB, third-party code and downloads, session
transcripts, GPU infra state. `EXCLUDED.md` gives the list, the reasons and where third-party code can be fetched.
