# ARC mean estimation at $256 \times 32$: what beats sampling, and why almost nothing does

<!--
DRAFT for Kelvin to edit. Written 2026-11-03 by an agent from the lane reports listed in Appendix A. No new
experiments were run and no lane file was edited. Each number carries a source key in an HTML comment
(keys in Appendix A); Appendix B maps the main claims to files.

Decisions this draft needs from Kelvin (nothing below is decided):
 D1. Audience and venue: a post addressed to ARC, a workshop paper, or an internal MATS write-up. Length and tone follow.
 D2. Authors and credit: how to credit the agent lanes and the co-prover (gpt-6-astra) that produced the proofs.
 D3. Section 3.7 discusses a named public leaderboard entry and our inference that it fits the public MLPs.
     That concerns another person; decide whether to name, anonymise, or drop it until the private re-evaluation (~15 Nov).
 D4. Section 1, "why it matters for alignment": the sources state ARC's estimation goal but not its alignment
     rationale. The paragraph there is a placeholder for your framing.
 D5. Whether to show ARC a copy before anything is public.
 D6. Whether to wait for the learned-experts lane (your current direction, still running) before circulating.
-->

**Draft, 3 November 2026. Authors: [to be decided].**

## Abstract

ARC's Phase-1 estimation problem asks for the output means of a random bias-free He-ReLU network of width 256 and
depth 32 under Gaussian input, at a budget of about 65,000 forward passes. We benchmark deductive and sampling
estimators on five registered networks of this shape and along a ladder with depth equal to width/8. ARC's own
cumulant propagation beats randomised quasi-Monte Carlo (RQMC) only in a window near 450 passes (median 2.0x, 4 of 5
nets); at the budget RQMC is 7-40x more accurate. The best deductive estimator we measured, a public "scale-mode"
closure, wins 2.5x at 688 passes and loses 33-65x at the budget. Between orders 2 and 3 the measured error-cost
exponent is 0.23-0.52, against 1 for sampling. Structured sampling designs buy constants of 2-3x over Monte Carlo and
no tested sampler changes the exponent; for positive-weight rules chosen without the weights we prove the exponent is
within 0.012 of 1 at this width. Pre-integration, region codes, branch-and-bound and future-aware hybrids also lose.
This is a restricted negative: measured for the methods tested, proven only for restricted classes. An unconditional
lower bound would be a super-linear time lower bound, which no known technique gives.

## 1 Introduction

ARC asks for estimators of a network's expected output that are "mechanistic" and still compete with sampling: error
at most $\varepsilon^2$ times the output variance in time $O(\varepsilon^{-2})$ forward passes, for every
$\varepsilon$ (the matching sampling principle; "mechanistic" has no formal definition, and the working test is that
the estimator "avoids any random or pseudorandom sampling").
<!-- AU §1; HM §1.5 -->
Their test case is a random bias-free He-ReLU MLP with Gaussian input. Their paper proves results at fixed depth for
polynomial activations, conjectures that order-$K$ cumulant propagation errs by at most $c_K (L/n)^K$, and concedes
that "this depth scaling is worse than Monte Carlo sampling"; depth growing linearly with width is listed as open.
<!-- AU §1 (Wu et al. 2026, Sec. 5, App. D, Sec. 7.3; Hilton blog) -->
The public contest built on this problem fixes Phase 1 at width $n = 256$, depth $L = 32$ and a budget of
$2.72 \times 10^{11}$ flops, about 64,850 forward passes. The organisers report that Phase 1's best methods "tended to
be based on variations of sampling". <!-- SM §2; AU §1 -->

**Question.** At this shape, and along depth proportional to width, can any estimator beat the best sampler (not plain
Monte Carlo) at equal compute? Can any reach an error-vs-compute exponent above sampling's 1 that survives as the
width grows?

**Why it matters for alignment.** [Placeholder for Kelvin's framing, decision D4.] What the sources support: if
mechanistic estimation cannot match sampling on random networks once depth grows with width, then the content of
ARC's principle sits in the informal word "mechanistic" and in the average case <!-- HM Summary -->, and any proposed
estimator should state its error-cost law along $L = \alpha n$ against the best sampler, not plain Monte Carlo
<!-- AU §7 -->. Whether the same depth problem appears in trained deep architectures is a conjecture we do not test
<!-- HM §9, labelled CONJECTURE there -->.

**Our bar and what we reached.** We set out to find either a major positive (structure that leads to better
estimation) or a major argument that the problem is hopeless and ARC should update <!-- LOG 04:14 -->. Midway the
target narrowed to any route to a better asymptote per unit of precision, preferably from the sampling side
<!-- LOG 13:00, 13:10 -->. We reached neither. An internal adversarial adjudication of our central benchmark judged it a
restricted negative, not "hopeless, ARC should update", in part because its exponent argument rests on a law ARC
already concedes <!-- LOG 10:24 -->. This paper keeps that classification.

**Contributions.**

1. A registered benchmark of ARC's own code at $256 \times 32$: a winning window of about 2x near 450 passes, a 7-40x
   loss at the budget (section 3.1).
2. The error-cost ladder along $L = n/8$: measured exponents 0.23-0.52 between orders 2 and 3, and a conditional
   theorem that turns ARC's own scaling law, if it is tight, into an exponent $\log(n/L)/\log n \to 0$ (section 3.2).
3. Tests of the strongest deductive variants we know, including a public counter-claim (forum topic 18298): each is a
   constant factor in a window that closes within about 5% of the budget. At Phase 2's shallow $1024 \times 16$
   deduction does win (section 3.3).
4. Where the tested closures make their error (the first ~8 layers, by accumulation), and a pricing identity for how
   a deep future reads a closure's defect (section 3.4).
5. Sampling-side measurements and theorems: structured designs give constants (2.1-2.9x), RQMC exponents 1.045-1.058,
   and for positive-weight rules chosen without the weights the exponent is provably within $[1.008, 1.012]$ at
   $n = 256$ (section 3.5).
6. Negative results for pre-integration, branch-and-bound, exact region codes and future-aware hybrids (sections 3.5,
   3.6), and an account of the public Phase-1 leaderboard that removes an apparent contradiction (section 3.7).

## 2 Setup

**Networks and estimand.** $h_0 = x \sim N(0, I_n)$, $h_l = \mathrm{relu}(W_l h_{l-1})$ for $l = 1, \dots, L$, with
$W_l$ square, entries iid $N(0, 2/n)$, no biases, and a ReLU on the last layer. The estimand is the vector
$Y = \mathbb{E}_x h_L \in \mathbb{R}^n$ for one fixed draw of the weights. <!-- PI §1; SM §2 --> We score
$$\mathrm{nMSE} = \frac{|\hat Y - Y|^2}{\operatorname{tr}\operatorname{Var}(h_L)},$$
so plain Monte Carlo (MC) with $N$ samples scores $1/N$ in expectation. ARC's paper normalises per neuron and the
contest scores raw MSE times $\max(0.1, C/B)$ under its own flop meter, so every comparison with the contest board is
approximate. <!-- AU §1; SM §2; SYN C17 -->

**Cost.** In forward passes, one pass being $2n^2L$ flops; ARC's estimators are charged with ARC's own flop counter.
<!-- AU §4 --> For a method and a competitor, the gain $G$ is the competitor's error at the method's cost divided by the
method's error. A deterministic method with error $e$ at cost $C$ beats a sampler exactly on the budget window from
$C$ to the cost at which the sampler reaches $e$. <!-- AU §4.2 -->

**Nets and truths.** Phase-1 shape: nets 200-204 at $256 \times 32$, noiseless, truths from $2^{26}$ paths. Ladder:
$L = n/8$ at $n = 32, 64, 128$, eight fresh nets per width, truths from $2^{24}$ paths. <!-- AU §4 --> Other lanes use
the same family at the shapes they state: $8 \times 256$ (six nets) <!-- ND §1 -->, widths 3-32 <!-- UE Summary -->,
and $512 \times 64$ (three nets) <!-- FA §4.5 -->.

**Comparators.** RQMC is scrambled Sobol with 8 scrambles per size. <!-- AU §4 --> Also: an antipodal Kerdock
5-design (129 mutually unbiased bases, 66,048 points) <!-- RN §2 -->, and a multilevel sampler that shares the late
layers through one reference trajectory <!-- UE Summary -->.

**Process and labels.** Each lane hashed its predictions and frozen code before its evaluation runs and disclosed
later amendments; proofs were checked by a co-prover model (gpt-6-astra) and reports by fresh-session reviews.
<!-- AU §4, §9; SM status line; PI status line; RN status line --> We label claims PROVEN (with named hypotheses if
conditional), MEASURED-reg (registered), MEASURED-exp (exploratory or post hoc), HEURISTIC, CONJECTURE, and CITED
(external, not verified by us).

## 3 Results

### 3.1 ARC's hierarchy at $256 \times 32$ (MEASURED-reg)

**Table 1.** ARC's estimators against RQMC on nets 200-204. <!-- AU §4.2 -->

| method | cost (passes) | nMSE (5 nets) | gain over RQMC at own cost | RQMC reaches its error at (passes) |
|---|---|---|---|---|
| k1 (means only) | 1 | 0.8-4.3e-2 | 16-90 (extrapolated) | 18-102 (extrapolated) |
| k2 ('simple') | 393 | 0.85-2.4e-3 | 0.83-2.2 | 330-740 |
| k2a ('augment') | 452 | 0.48-2.3e-3 | 0.85-4.6 (median 2.0) | 400-1,800 |
| exact Gaussian recursion | 1,184 | 1.0-2.0e-3 | 0.31-0.62 | 390-730 |
| k3f (order 3, factorised) | 49,097 | 0.6-2.8e-4 | 0.035-0.18 | 2,300-6,400 |

ARC's best order-2 variant wins on 4 of 5 nets (median 2.0x; 0.85x on net 203) at precision about $10^{-3}$, and RQMC
catches up by 400-1,800 passes. Order 3 loses 5-30x at its own cost. At the contest budget RQMC is 7-40x (median 22x)
more accurate than the best ARC variant that fits; the registered prediction of at least 10x on all five nets failed
on net 200 (6.7x). Exact Gaussian moments do no better than ARC's cheaper approximations. <!-- AU §4.2 -->

**Figure 1** (existing file `work/scale-mode/figs/fig1_256x32.png`). Median nMSE against cost on nets 200-204, log-log,
with MC and RQMC lines. ARC's k2, k2a and the scale-mode estimator (section 3.3) sit slightly below RQMC at 400-700
passes; the order-3 points sit near or beyond the budget line, an order of magnitude above where RQMC ends. <!-- SM §5, figs/fig1_256x32.png -->

### 3.2 The ladder along $L = n/8$ (MEASURED-reg; theorem PROVEN UNDER a hypothesis)

**Table 2.** Best variant of each order, median over nets (error in nMSE at cost in passes; $G$ over MC / over RQMC).
<!-- AU §4.1 -->

| $n \times L$ | $K = 2$ (k2a) | $K = 3$ | $K = 4$ | $e_3/e_2$ | $\gamma_{2\to3}$ (ARC's law) |
|---|---|---|---|---|---|
| $32 \times 4$ | 1.1e-3 at 117; 7.6 / 1.7 | 1.4e-4 at 6.8e3 | 3.4e-5 at 3.4e4; 0.86 / 0.18 | 0.12 | 0.52 (0.60) |
| $64 \times 8$ | 1.3e-3 at 164; 4.8 / 1.9 | 1.8e-4 at 2.6e4 | 8.7e-5 at 2.6e5; 0.045 / 0.016 | 0.14 | 0.39 (0.50) |
| $128 \times 16$ | 1.0e-3 at 260; 3.9 / 2.0 | 2.5e-4 at 1.0e5 | 9.5e-5 at 2.1e6; 0.005 / 0.002 | 0.25 | 0.23 (0.43) |
| $256 \times 32$ | 8.4e-4 at 452; 2.6 / 2.0 | 2.0e-4 at 4.9e4; 0.10 / 0.06 | not run | 0.24 | 0.30 (0.375) |

Each order's error stays within a factor of about 2-3 as the width grows eightfold, while each step up the hierarchy
divides the error by 4-8 (order 2 to 3) or 2-4 (3 to 4) and multiplies the cost by about $n/4$ to $3n$. The order-2
gain over MC falls from 8.1 to 2.6 across the ladder; order 3 loses to RQMC by 5-20x from $n = 64$ on. The $n = 32$
and 64 exponents are descriptive (seen before the amendment that registered them). <!-- AU §4.1 --> A registered
extension to $512 \times 64$ (three nets) found ARC's order 2 losing to RQMC at its own cost (0.84x) and order 3
improving on order 2 by only 2.95x. <!-- FA §4.5 --> An independent lane found the same trend for order 2 against
plain MC up to width 1024 (gain 2-8 at widths 32-128, about 0.7-1.1 at 1024). <!-- HM Summary -->

**Proposition 1** (PROVEN UNDER the uniform law; AU §2.5, co-prover round 3). Suppose order $K$ costs
$C_K \ge d_* n^{K-1}$ passes and errs by $e_K \ge a c_* (L/n)^K$, with $a, c_*, d_*$ independent of $K$. Then the best
error affordable at budget $C$ satisfies
$$e_{\text{best}}(C) \;\ge\; a c_* \frac{L}{n} \Big(\frac{C}{d_*}\Big)^{-\gamma}, \qquad \gamma = \frac{\log(n/L)}{\log n}.$$
At fixed depth $\gamma \to 1$ as the width grows, which is ARC's theorem regime. At $L = \alpha n$,
$\gamma = \log(1/\alpha)/\log n \to 0$; at $256 \times 32$, $\gamma = 0.375$. <!-- AU §2.5 -->

ARC state the law as an upper bound with order-dependent constants. The proposition needs it as a lower bound,
uniformly in $K$, and measurements at $K \le 4$ cannot establish that. So the statement is "if ARC's law is tight,
climbing the ladder loses to sampling", not "ARC's law implies the negative". <!-- AU §2.5 -->

### 3.3 Stronger deductive variants: constant factors in windows

**Scale mode (MEASURED-reg).** A participant claimed on the contest forum (topic 18298) that separating a collective
scale mode, carried as a one-parameter law, "restores convergence and beats sampling" with depth growing with width.
<!-- SM §1 --> We ran the author's code unchanged; it reproduced his $64 \times 16$ headline (nMSE 1.517e-3 against his
1.52e-3). <!-- SM Summary -->

**Table 3.** Scale-mode estimator (LVTV2, about order-2 cost) and its order-3 level (SL3) along $L = n/8$, medians.
<!-- SM §5 -->

| $n \times L$ | LVTV2 nMSE at cost | $G$ over RQMC (95% CI) | SL3 nMSE at cost | SL3 $G$ over RQMC | $\gamma$ scale law / ARC |
|---|---|---|---|---|---|
| $32 \times 4$ | 7.2e-4 at 200 | 1.8* (1.1-2.6) | 8.3e-5 at 1.6e3 | 1.5 | 1.0 / 0.54 |
| $64 \times 8$ | 6.7e-4 at 287 | 2.0 (1.7-2.7) | 7.2e-5 at 6.1e3 | 0.73 | 0.72 / 0.37 |
| $128 \times 16$ | 6.0e-4 at 426 | 2.4 (1.7-2.9) | 9.5e-5 at 2.1e4 | 0.19* | 0.52 / 0.28 |
| $256 \times 32$ | 3.6e-4 at 688 | 2.5 (2.0-4.7) | 7.2e-5 at 7.5e4 | 0.067* | 0.30 / 0.31 |

(* uses the RQMC curve extrapolated outside its measured range.) At $256 \times 32$ this is the most accurate
order-2-cost estimator we measured, and RQMC reaches its error at about 2.3x its cost (about 1,600 passes, 2.5% of the
budget). At the budget RQMC is 33-65x more accurate than every scale-law method that fits. Re-pricing its special
functions at the contest meter's rates (exploratory) doubles its cost and cuts its gain to 1.16x. Its order-3 level
costs more than the whole budget. Both registered escape criteria failed: the two-level exponent is 0.52 and 0.30 at
$n = 128$ and 256 (0.9 needed), and on the claim's own diagonal $L = n/4$ the median gain over RQMC was 0.79, 0.73,
1.2, 0.43, 2.0 from $64 \times 16$ to $1024 \times 256$. <!-- SM Summary, §5, §6, §8 -->

**Radius-corrected closure (MEASURED-reg; cost arithmetic).** A Gaussian closure whose amplitude (radius) law is
exactly right, run as a finite-sample recursion, errs by 1.9e-3, 9.2e-4 and 4.9e-4 at $n = 64, 128, 256$, within 6%
of $L/n^2$ (a post hoc observation, with no convergence study in sample size). As run it pushes $2^{19}$ samples per
layer, at least ~255x what MC needs to reach that error. A deductive version, which nobody has built, would beat MC
only if it cost less than about 5 order-2 steps per layer, and RQMC only below 2-3.5. <!-- AU §4.4(c) -->

**Future-aware projections (MEASURED-reg benchmark; cost ledger post hoc).** A backward pass finds where the future
will read a closure's error. Keeping the cloud's law exact in the $k = 64$ directions the future reads most cuts the
Gaussian closure's error at $256 \times 32$ by 19x, but carrying that law by particles is a sampler whose error is
45-250x RQMC's at its cost. ARC's order 3 with its third cumulant kept only in $k = n/4$ future directions would beat
RQMC by 2.6, 3.0, 2.4x ($n = 64, 128, 256$) at a hypothetical dedicated cost. Charging the order-2 pilot it needs gives
1.75-2.2x, and charging the dense direction extraction actually used gives 0.5-0.7x. At $n = 512$ the $n/4$ version
fails numerically. <!-- FA Summary items 1-3 -->

**Phase 2 is different (MEASURED-reg; CITED board).** At Phase 2's $1024 \times 16$ ($L/n = 1/64$) the ladder is
steep (exponent 0.83 between orders 2 and 3) and ARC's unengineered order 3 is 19x more accurate than full-budget RQMC
at 1.5x the budget; engineered order-3 entries on the public board are about 100x below full-budget MC within 12% of
the budget. <!-- SM Summary item 4, §7 --> The negative concerns depth growing with width, not deduction in general.

### 3.4 Where the error is made (MEASURED-reg; PROVEN identities)

**Table 4.** Per-cut attribution at $256 \times 32$, medians over 5 nets: ARC k2's state at layer $l$ pushed through
the true rest of the net, against the moment-matched Gaussian of the true layer-$l$ law put in at a single cut.
<!-- AU §4.3 -->

| cut $l$ | 1 | 2 | 4 | 8 | 16 | 24 | 31 |
|---|---|---|---|---|---|---|---|
| k2 past defect | 1.0e-4 | 1.8e-4 | 5.0e-4 | 7.8e-4 | 9.8e-4 | 1.2e-3 | 1.25e-3 |
| oracle Gaussian, single cut | 6.7e-5 | 1.6e-4 | 2.4e-4 | 2.2e-4 | 1.8e-4 | 1.3e-4 | 3.3e-5 |

By layer 8 the k2 state carries 44-64% (median 59%) of its final error. A single Gaussian cut of the true law loses
only 1.3-2.4e-4 against the recursion's 1.2e-3: the error is accumulated. Where it is made, the true cloud's non-Gaussian structure is high-dimensional: the third-cumulant participation ratio is
114-116 at $l = 1$, 23-28 at $l = 4$, 4-11 at $l = 8$ and 1-4 from $l = 12$ (descriptive). <!-- AU §4.3 -->

**How the future prices a defect (PROVEN).** For a forward layer-wise estimator with reconstructions $Q_l$ and
defects $\Delta_l = Q_l - \Phi_l Q_{l-1}$, $\hat Y - Y = \sum_l \langle g_l, \Delta_l \rangle$, with $g_l$ the map
from layer $l$ to the output. Averaged over the future's weights, a layer-$l$ defect costs
$\sum_d b_d \lVert M_d \rVert^2$ over its radially normalised moment tensors, with $b_d \ge 0$ and $\sum_d b_d = 1$.
This prices a given defect; it bounds no class of representations. <!-- AU §2.1-2.2; SYN §2 --> At infinite width a
future of $t = 31$ layers puts weight $b_0 = 0.97$ on the radius and reads the rest at mean degree 42.3; at finite
width $b_0 = 0.948$ (measured). <!-- AU §3 --> Given the past, the next layer's frame is uniformly random relative to
the cloud's axes (PROVEN). <!-- REL Summary item 1 --> The value function's mean Hermite degree on the layer-$l$
cloud is 21, 7.7, 4.1, 1.9, 1.3, 1.04 at $l = 0, 4, 8, 16, 24, 31$ (MEASURED-reg). <!-- AU §3, from REL -->

**Reading.** Between layers, compressed descriptions move almost linearly (consecutive relevant coordinates have
linear $R^2$ 0.82-0.99; the scrambled positive controls had not been run through the same test, so this reads "the
tests found low degree"). Relative to coordinates where the law is computable, the dependence is of high degree. No layer of $256 \times 32$ offers both a computable law and a low read-out
degree. <!-- AU §5 --> Bit counts of codes do not price estimation: with decoder $\mathbb{E}[a \mid c]$ a code sum is
unbiased at any rate, so the cost sits in computing code probabilities and conditional means. <!-- AU §5 -->

**Gaussian closures have bounded gain (PROVEN UNDER $H_R$).** One exact Gaussianisation after the first layer leaves
an error that no later suffix of depth $\alpha n$ removes. If Gaussianisation never lowers the mean radius on average
over a fresh layer (hypothesis $H_R$, a CONJECTURE that one exploratory test on one net did not contradict), the exact
Gaussian recursion's annealed gain at $L = n$ is bounded by a constant, about 470, two to three decades above what is
measured (at most about 3 up to $n = 256$). <!-- BB Summary item 10; AU §2.4 -->

### 3.5 The sampling side

**Table 5.** Gain over MC at $2^{16}$ passes on nets 200-204, radius exact (MEASURED-reg), and fitted exponents over
$N = 2^8$ to $2^{18}$ (risk $\sim N^{-p}$; MC has $p = 1$). <!-- RN Summary items 1-2, §4.2 Table C -->

| sampler | random bits | median gain (range) | exponent $p$ [95% CI] |
|---|---|---|---|
| scrambled Sobol | 135,168 | 2.13 (1.95-2.77) | 1.045 [1.03, 1.08] |
| scrambled Sobol in $W_1$'s polar frame (white-box) | 135,168 | 2.22 (1.83-2.64) | 1.058 [1.01, 1.08] |
| antipodal Kerdock 5-design, Haar-rotated | 1,044,480 | 2.89 (2.20-3.93) | - |
| pairwise-independent MC | 16,384 | 1.53 (0.40-1.70) | - |
| centred Sobol, fixed (no random bits) | 0 | 2.07 (1.78-5.55) | 1.06-1.13 (fixed sets, wide CIs) |

No randomised structured sampler reached 4x on any net. The white-box frame showed no exponent difference
($-0.002$ [$-0.04$, 0.03]). Fixed point sets win on some nets and lose on others, with no error bar.
<!-- RN Summary, §4.2 --> Random bits do not track accuracy:
across nine orders of magnitude of bits the error at fixed compute does not follow the bit count. <!-- RN Summary
item 3 -->

Theorems for rules chosen without looking at the weights (all PROVEN in the randomness lane with the co-prover):
<!-- RN §2 -->

- The ensemble risk of a point rule $Q$ on the sphere is $\sum_{d \ge 1} a_d B_d(Q)$, with $a_d$ the expected energy at
  spherical-harmonic degree $d$ and $B_d(Q) \ge 0$. Any union of independently rotated copies of a fixed design has
  exponent exactly 1: designs buy constants, never rates.
- The best positive weight-independent rule has exponent between $1 + 2/(n-1)$ and $1 + 3/(n-1)$, that is
  $[1.008, 1.012]$ at $n = 256$.
- Along $L = \alpha n$ with $L/\sqrt n \to \infty$ the fixed-degree spectrum converges, and the gains of the simplex,
  cross-polytope and Kerdock designs converge to 2.09, 2.36 and 3.15 (measured at $256 \times 32$: 1.93, 2.39, 3.04).
  The variance these designs fight is the accumulated fluctuation of activation norms in the early layers. A registered
  test of the finite-size bands at $512 \times 64$ failed narrowly on all four bands, so the limit is proven and the
  speed of approach is not. <!-- RN Summary item 4 -->
- At $n = 256$ every even degree from 6 on is paid in full for $N$ up to $8.6 \times 10^4$. A spherical 7-design needs
  at least $5.66 \times 10^6$ points, 87x the budget. Plugging measured spectra into the ceiling gives an estimated
  10-19x at the budget (an estimate, not a certified bound).

The pre-integration lane proved a matching barrier for signed rules (PROVEN, co-prover audited): averaged over nets,
for nodes and scalar weights chosen independently of the net, <!-- PI §5 -->
$$\frac{\mathbb{E}_W \lVert \text{error} \rVert^2}{\mathbb{E}_W \operatorname{tr}\operatorname{Var} f} \;\ge\; \frac{c/2 - O(1/d) - O(1/N)}{N}$$
for $N \le d^p$, whenever the even angular energy above degree $2r$ carries a fraction $c$ of the averaged variance
($r$ the smallest degree whose harmonic dimension is at least $2N$). The share $c$ is measured on two nets per width,
not proven: the even share above degree 2 grows from 0.08 at $n = 32$ to 0.26 at 256. Without that hypothesis the
bound is absolute and small: $1/(4\pi^2 N)$ for $N \le n/2$ points. <!-- PI Summary item 5, §5 -->

Beyond linear rules: under a Gaussian surrogate prior, adaptive and nonlinear algorithms cannot beat the best
nonadaptive linear rule (classical, re-proved). The real prior is far from Gaussian (excess kurtosis 6.9-9.1 for a
unit's output), so adaptive and nonlinear methods on the true prior are neither excluded nor shown to help.
<!-- PI §5 --> On random weights, determinism is no restriction: some fixed point set matches MC's ensemble risk, and,
under exact-transform primitives, seeds read off the weights simulate a randomised estimator (PROVEN; the first part
is existential). <!-- RN Summary item 3; UE Summary;
HM Summary --> So "sample-free" excludes nothing until "mechanistic" is defined.

**Multilevel sampling.** Sharing the late layers through one reference trajectory beats radius-exact MC by
$\Omega(n/\log^2 n)$ at $L = \alpha n$ (PROVEN UNDER layer-wise cost hypotheses). <!-- UE Summary --> Measured, its
gain is 1.21, 1.41, 1.58, 2.43 at $L = n$ ($n = 32$-256) and 0.99 at $256 \times 32$ <!-- BB Summary item 8 -->; along
$L = n/8$ it is 0.83 to 0.99 from $n = 32$ to 256, and 1.00-1.07 at $512 \times 64$. It pays only at depths in the
hundreds. <!-- RN Summary item 6 -->

**Pre-integration (MEASURED-reg).** Integrating exactly along one line costs about $nL/2$ passes (3,469 at
$256 \times 32$; 752 for a window) and is worth about one RQMC point (0.84-1.29 at $256 \times 32$). It raised the
fitted exponent by 0.1-0.3 only at input dimension 4-8, and lost at equal cost on every net: per-net minima 21-1,410x
along the ladder and at $256 \times 32$, 15-91x at $8 \times 256$. <!-- PI Summary items 1-3 -->

### 3.6 Exact, regional and hybrid methods

**Table 6.** Other method families against the best sampler. <!-- sources per row -->

| family | where tested | result | label | source |
|---|---|---|---|---|
| certified branch-and-bound over input cones | widths 3-32, depths 4-64 (72 nets) | deductive estimate never beats RQMC (best ratio 0.18, width 3); cost ~10x per unit of width; certificate vacuous from width 6 | MEASURED-reg | UE Summary |
| certified deterministic code | $8 \times 256$, 6 nets | 23-106x worse than RQMC | MEASURED-reg | ND Summary 5 |
| integrate top regions, drop rest | $8 \times 256$ | 7-1,222x worse than RQMC with exact tail, at an optimistic 9 mv per region | MEASURED-reg | ND Summary 4 |
| exact-mean controls + RQMC (hybrid H1) | $n = 64$-256, $L = n/8$ | 1.00-1.03x RQMC at 6.5e4 passes, 0.86-0.95x at 1e4 | MEASURED (registered design, scored post hoc) | FA Summary 3 |
| certified-linear backward pieces | nets 200-204 (exact pieces); net 200 ($\varepsilon$-certified) | coverage $\ge 50\%$ only at $l = 31$; one layer back top-1000 exact pieces cover 0.1-7.6%; two back 0 | MEASURED-exp | LOG 16:17 |
| ARC kprop + Kerdock, combined by error models | $256 \times 8$ and $256 \times 32$, noise $\sigma = 10^{-3}$ | depth 8: 1.2-9.9x over the best sampler; depth 32: 0.84-1.06x | MEASURED-reg | AN Summary |

The narrow-deep case shows where the difficulty sits. At $8 \times 256$ the problem past layer 20-48 is linear on every
sampled input, and RQMC with that exact linear tail is 3-15x better than plain RQMC. But the map from the input to that
layer has 1.3-2.2e5 linear regions in 4 million inputs, thin in 7 angular dimensions, with 1-2% of inputs in regions
never seen. <!-- ND Summary items 1, 2, 6 --> Exact integration wins only at widths 2-3. <!-- AU §2.6 -->

For hybrids the criterion is arithmetic: a surrogate with exact mean whose residual variance falls like (construction
cost)$^{-\delta}$ gives MSE $\sim C^{-(1+\delta)}$. <!-- LOG 13:52; PI §6 --> Measured on one net per width
(exploratory), the layer-1 residual share falls like $k^{-0.25}$ at $n = 64$ and $k^{-0.09}$ at $n = 128$, so
$\delta > 0$ uniformly in width is not established. <!-- FA §5 --> The controls remove what scrambled Sobol already
integrates. <!-- FA Summary 3 --> At depth 32 a control mean would have to be right to about $10^{-6}$ at depth 16 or
more before it helps. <!-- AN Summary -->

### 3.7 The public Phase-1 board (decision D3)

The board's best entry has raw final-layer MSE 3.63e-8 at 51% of the budget, which looked 10-50x below full-budget MC
and conflicted with our 2-3x samplers. <!-- AU §1; SYN C10 --> A read-only investigation of the public record found
that the meter explains little (the run is 93% metered) and that the entry's accuracy most likely comes from fitting
the 50 public MLPs using per-MLP errors that every submission page publishes: verified for 5-6 August, inferred for
the final 10 August run. The same participant's unfitted runs score 2.1-2.3e-7, about 6x better than plain MC at equal
charged cost; published Kerdock-cubature write-ups report 5.3-7.1x. The investigation splits that ~6x into 2.4-2.9x
from the design, which matches our Kerdock 2.89x at equal passes, and about 2x from cheaper points (fast
Walsh-Hadamard first layer, antithetic sharing, dropped dead units). <!-- PB Verdict, Key numbers, Accounting --> This
is INFERRED; the Phase-1 private re-evaluation on fresh MLPs would settle it. <!-- PB Accounting -->

## 4 What this does not show

- No lower bound for all algorithms. Proving that no estimator beats sampling on this explicit problem would be a
  super-linear time lower bound, for which no technique is known. <!-- AU §8; UE §3.3 --> Worst-case barriers
  (#NSETH, Impagliazzo-Kabanets-Wigderson) do not reach random weights. <!-- HM Summary; UE Summary -->
- The ladder theorem is conditional on ARC's law holding as a lower bound uniformly in $K$; we measured $K \le 4$
  ($K \le 3$ at $256 \times 32$). <!-- AU §2.5, §4.1 -->
- The sampling theorems cover weight-independent rules, on average over nets. They say nothing about a single net,
  about rules that look at the weights beyond the polar frame, or about adaptive and nonlinear methods under the true
  prior. The point-rule barrier rests on a spectral share measured on two nets per width. <!-- PI §5; RN §2 -->
- Scope: one family (square, bias-free He-ReLU, Gaussian input, noiseless), five nets at the Phase-1 shape, eight
  per ladder width, three at $512 \times 64$. Every width exponent is a descriptive slope over a factor of 4-8 in width.
  Trained networks were not tested. <!-- AU §4, §8; FA §4.5 -->
- Untested routes: implicit representations of the early high-dimensional structure; other radius-direction
  couplings; a deductive radius-corrected closure; scale-law orders 4 and up; non-layer-wise methods.
  <!-- AU §6 item 8, §7 item 5; SM §8 -->
- Metric: our nMSE and ARC's flop counter differ from the contest's raw MSE, utilisation factor and meter.
  <!-- SYN C17 -->
- Bit counts of learned codes are best-found upper bounds, not certified, and price representation only.
  <!-- AU §3, §5 -->

## 5 Related work

All references below are as cited in our lane reports; we have not re-verified each one, and full bibliographic
entries remain to be added.

ARC's program: Wu et al. (2026, arXiv:2605.05179 v2), with the cumulant-propagation estimators, the
$c_K (L/n)^K$ conjecture and the depth concession <!-- AU §1 -->; "Competing with sampling" (Neyman, Lecomte, Wu,
Winer, Hilton, Robinson, ARC blog, November 2025), which states the matching sampling principle <!-- HM §1.5 -->; and
posts by Hilton (23 June 2026) and Christiano (3 June) quoted in AU §1. The contest's forum topics: 18298 (scale
mode), 18198 (covariance propagation in Phase 2), 18147 (Gaussian closures far behind a budget-matched sampler at
Phase 1), 18282 (a never-sampling Phase-2 estimator, unverified), and 18125 (Phase-1 metering).
<!-- SM §1-2; LOG 10:35; AU §1; PB Rules -->

Complexity: Impagliazzo, Kabanets and Wigderson (2002) and Chen and Tell (STOC 2021), used for the worst-case
white-box barriers <!-- HM Summary -->; pseudorandom generators for halfspaces, polynomial threshold functions and
threshold circuits (Meka-Zuckerman, Gopalan-Kane-Meka, Kane, O'Donnell-Servedio-Tan, Kelley-Meka,
Harsha-Klivans-Meka, Chattopadhyay-De-Servedio, Hatami-Hoza-Tal-Tell), which reach only the first ReLU layer, and
Chen-Li-Li-Meka (2022) on why fooling constant-depth ReLU nets would separate $\mathrm{TC}^0$ from $\mathrm{NC}^1$
<!-- RN §3 -->.

Quasi-Monte Carlo and average-case integration: Owen's scrambled nets; He and Wang (2015) on rates for discontinuous
integrands; Traub, Wasilkowski and Woźniakowski (1984) and Wasilkowski and Woźniakowski (1984) on adaption under
Gaussian priors; Novak and Woźniakowski (Vol. II); pre-integration (Griewank-Kuo-Leovey-Sloan; Gilbert-Kuo-Sloan).
<!-- RN §3; PI §5; LOG 13:51 --> Spherical designs: Delsarte-Goethals-Seidel, via Bannai-Bannai. <!-- RN §2 --> Random networks: Hanin-Nica on the lognormal output
scale <!-- PI §5 -->; Hanin-Rolnick, Jonasson-Steif-Zetterqvist and De Palma-Kiani-Lloyd on regions and noise
sensitivity <!-- RN §3 -->.

## 6 Open questions

1. A deterministic $O(n)$-pass representation of the cloud's joint law in its top ~$n/4$ future directions at the
   benchmark's accuracy would open a window that grows with width. None is known. <!-- FA Summary 5; SYN §6 -->
2. A white-box surrogate family with exact means and residual variance $C q^{-b}$ uniformly in width gives an exponent
   above 1 when $b$ exceeds its evaluation-cost exponent. The candidate named (biased Gaussian ridge controls) is
   untested; squared-hinge controls provably cannot touch even degrees $\ge 4$. <!-- PI §6 -->
3. CONJECTURE: the ladder's exponent decay along $L = \alpha n$ and the sampling bound are two consequences of one
   angular-degree spectrum. No source derives the per-order factor from the spectrum. <!-- SYN §5 -->
4. The finite-width price spectrum beyond $b_0$, and a proof of the spectral share $c$ for the ensemble.
   <!-- AU §8; PI §5 -->
5. Does anything beat the best multilevel sampler by a polynomially growing factor at $L = \alpha n$? (Revised
   conjecture C0*, "little evidence" either way.) <!-- UE Summary 5 -->
6. A deductive radius-corrected closure below ~5 order-2 steps per layer, and whether $L/n^2$ is its limit.
   <!-- AU §4.4(c), §8 -->
7. Kelvin's current direction, learned layered mixtures of linear experts trained on populations, is running. Its
   registered headline is the error-vs-total-compute slope over at least two decades against RQMC's ~1.05; small-budget
   losses are not counted as failure. Exploratory runs so far show held-out error not falling with the number of
   experts at $32 \times 4$. <!-- LOG 16:58, 3 Nov 00:17, 01:56 -->

## Appendix A. Source keys

Paths under `/srv/agent-data/home/workspaces/mats/` unless stated. Repo files fetched from
`futarchy-fi/inconsistency-search` at `main` 7a10d6a1 (2026-11-03T01:28Z); each was byte-identical to the outbox copy.

| key | file |
|---|---|
| AU | `outbox/arc-update-2026-11-02.md` (status 13:50Z) |
| SM | `outbox/scale-mode-2026-11-02.md` (final 13:24Z); figure `work/scale-mode/figs/fig1_256x32.png` |
| PI | `outbox/preint-2026-11-02.md` (final) |
| RN | `outbox/randomness-2026-11-02.md` (final ~16:20Z) |
| FA | `outbox/future-aware-2026-11-02.md` (Part 1 final) |
| UE | `outbox/unrestricted-estimators-2026-10-31.md` |
| ND | `outbox/nd-exact-2026-11-02.md` |
| BB | `outbox/bits-bounds-2026-11-01.md` |
| REL | `outbox/relevance-accounting-2026-11-01.md` |
| SYN | `outbox/synthesis-draft-2026-11-02.md` (14:25Z; superseded where the finals above differ) |
| PB | `work/phase1-board/FINDINGS.md` |
| HM | repo `mats/reports/hardness-mean-estimation-2026-10-29.md` |
| CR | repo `mats/reports/cut-rank-lower-bound-2026-10-30.md` |
| AN | repo `mats/reports/arc-noisy-deep-2026-10-29.md` |
| S31 | repo `mats/reports/summary-2026-10-31.md` |
| LOG hh:mm | `outbox/overnight-report-2026-10-29.md`, 2 November entry at that time (two 3 November entries marked) |

Where SYN and a later final disagree we used the final: the preint final withdraws the "~$nL$ evaluations identify
the net" claim and narrows the barrier; the randomness final gives registered exponents and constants that were
pending in SYN; the future-aware final corrects the hybrid score (1.00-1.03x, not 0.8-1.0x) and the deductive window
(0.5-0.7x as implemented). <!-- PI §5; RN Summary; FA Summary 3; LOG 15:29 --> CR (one-way linear summaries need
$(1/\varepsilon)^{2(n-1)/3}$ numbers; not a running-time bound) and S31 were read for context and are not cited above.

## Appendix B. Claim ledger

| claim | label | source |
|---|---|---|
| Phase 1 = $256 \times 32$, $2.72 \times 10^{11}$ flops = 64,850 passes | CITED | SM §2; AU §1 |
| k2a beats RQMC on 4 of 5 nets, median 2.0x, window closes at 400-1,800 passes | MEASURED-reg | AU §4.2 |
| order 3 loses 5-30x at own cost; RQMC 7-40x (median 22x) better at budget; P4 failed on net 200 (6.7x) | MEASURED-reg | AU §4.2 |
| $\gamma_{2\to3}$ = 0.52, 0.39, 0.23, 0.30 vs ARC's law 0.60, 0.50, 0.43, 0.375 | MEASURED-reg ($n \le 64$ descriptive) | AU §4.1 |
| order-2 gain over MC 8.1 to 2.6 along $L = n/8$ | MEASURED-reg | AU §4.1 |
| $512 \times 64$: k2 0.84x RQMC; $e_{k2}/e_{k3}$ = 2.95 | MEASURED-reg (3 nets) | FA §4.5 |
| K = 2 gain over MC about 0.7-1.1 at width 1024 | MEASURED | HM Summary |
| Proposition 1 ($\gamma = \log(n/L)/\log n$) | PROVEN UNDER uniform law | AU §2.5 |
| scale mode: 3.6e-4 at 688 passes, 2.5x RQMC (CI 2.0-4.7), 33-65x behind at budget, 1.16x re-priced | MEASURED-reg (re-pricing exp) | SM Summary, §5 |
| scale-mode escape criteria D1, D2 fail; diagonal gains 0.79, 0.73, 1.2, 0.43, 2.0 | MEASURED-reg | SM §6, §8 |
| radius-corrected closure ≈ $L/n^2$; ≥ ~255x MC's cost as run; break-even < ~5 order-2 steps per layer | MEASURED-reg; arithmetic | AU §4.4(c) |
| future-aware: 19x over Gaussian closure at $k = 64$; particles 45-250x behind RQMC; projected k3 2.6/3.0/2.4x hypothetical, 0.5-0.7x as implemented | MEASURED-reg; ledger post hoc | FA Summary |
| Phase 2: exponent 0.83, k3f 19x below full-budget RQMC at 1.5x budget; board ~100x below MC | MEASURED-reg; CITED | SM §7 |
| 44-64% of k2 error by layer 8; single cut 1.3-2.4e-4 vs 1.2e-3 | MEASURED-reg | AU §4.3 |
| third-cumulant PR 114-116 at $l = 1$ to 1-4 from $l = 12$ | MEASURED-reg (descriptive) | AU §4.3 |
| pricing identity; $b_0$ = 0.97 (inf.), 0.948 (finite) at $t = 31$; mean degree 42.3 | PROVEN; NUMERICAL; MEASURED-exp | AU §2.2, §3 |
| future frame uniformly random relative to past cloud | PROVEN | REL Summary 1 |
| mean Hermite degree 21 ... 1.04 | MEASURED-reg | AU §3 (REL) |
| codes near-linear between layers ($R^2$ 0.82-0.99); tower property | MEASURED; PROVEN | AU §5 |
| Gaussian closure gain bounded (~470) under $H_R$; measured ≤ ~3 | PROVEN UNDER $H_R$; MEASURED | BB Summary 10 |
| sampler gains at $2^{16}$ (Kerdock 2.89, Sobol 2.13, polar 2.22, pairwise 1.53, fixed 2.07) | MEASURED-reg | RN §4.2 |
| exponents 1.045 / 1.058; frame difference -0.002 | MEASURED-reg | RN Summary 1 |
| rotated-copy unions exponent 1; best weight-independent exponent in [1.008, 1.012] | PROVEN | RN §2 |
| design gain limits 2.09/2.36/3.15 vs measured 1.93/2.39/3.04; 512 x 64 bands fail | PROVEN; MEASURED-reg | RN Summary 4, §2 |
| ceiling ~10-19x (estimate); 7-design 87x budget | HEURISTIC; PROVEN | RN Summary 4, §2 |
| point-rule barrier $(c/2)/N$; absolute $1/(4\pi^2 N)$ | PROVEN (co-prover audited) | PI §5 |
| even share > degree 2: 0.08 to 0.26 | MEASURED-exp (2 nets/width) | PI §5 |
| unit output excess kurtosis 6.9-9.1; adaptive/nonlinear open | MEASURED-exp; PROVEN (surrogate) | PI §5 |
| determinism free on random weights | PROVEN (existential) | RN Summary 3; UE Summary; HM Summary |
| multilevel $\Omega(n/\log^2 n)$; 0.99 at $256 \times 32$; 1.21-2.43 at $L = n$ | PROVEN UNDER cost hypotheses; MEASURED-reg | UE Summary; BB Summary 8; RN Summary 6 |
| pre-integration: line ≈ 1 point; 3,469 passes; loses 21-1,410x | MEASURED-reg | PI Summary 1-3 |
| branch-and-bound never beats RQMC | MEASURED-reg | UE Summary |
| $8 \times 256$: certified code 23-106x behind RQMC; 1.3-2.2e5 regions; RQMCJ 3-15x | MEASURED-reg | ND Summary |
| hybrid H1 1.00-1.03x RQMC; residual share $k^{-0.25}$, $k^{-0.09}$ | MEASURED; MEASURED-exp | FA Summary 3, §5 |
| certified-linear pieces survive only at $l = 31$ | MEASURED-exp | LOG 16:17 |
| noisy depth-8 hybrid 1.2-9.9x; depth 32 none | MEASURED-reg | AN Summary |
| Phase-1 #1 explained by public-set fitting; honest frontier ~6x MC at equal charged cost | INFERRED / VERIFIED in part | PB Verdict |
| restricted negative (adjudication) | internal review | LOG 10:24 |
