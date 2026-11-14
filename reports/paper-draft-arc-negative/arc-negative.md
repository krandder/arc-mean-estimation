# Deduction vs sampling at depth proportional to width: measurements at ARC's Phase-1 shape

<!--
DRAFT v2 for Kelvin to edit. v1 written 2026-11-03 by an agent from the lane reports in Appendix A; v2 revised
2026-11-03 ~02:45Z against two referee reports (referee 1: source audit; referee 2: framing). v1 is kept as
work/papers/arc-negative.v1.md. No new experiments were run and no lane file was edited. Each number carries a source
key in an HTML comment (keys in Appendix A); Appendix B maps claims to files; Appendix C gives theorem provenance.

Decisions this draft needs from Kelvin (nothing below is decided; the draft takes the reversible default shown):
 D1. Audience and venue: post to ARC, workshop paper, or internal MATS write-up. Length and tone follow.
 D2. Authors and credit: how to credit the agent lanes and the co-prover gpt-6-astra, which authored several of the
     proofs (Appendix C), not only checked them.
 D3. Phase-1 board account (now Appendix D, anonymised): name, anonymise, or drop until the private re-evaluation
     (~15 Nov). The organisers say public-set fitting is allowed under the rules, so the text must not read as an accusation.
 D4. Section 1, "why it matters for alignment": placeholder for your framing.
 D5. Whether to show ARC a copy before anything is public.
 D6. Whether to wait for the overnight lanes started 3 Nov 02:30Z (layer-wise cumulant-ambiguity lane, aimed at a
     restricted negative for ARC's class, which bears directly on Q1; gate-pattern mapping at depth 4). The v1 wording
     ("learned-experts lane, your current direction, still running") was stale; see open question 7.
 D7. Matching or beating: which question the paper answers. Default here: Q1 (ARC's matching question) is the headline,
     Q2 (the contest's beating question) is section 4, supporting. If you choose "matching only", section 4 moves to an appendix.
 D8. One thesis or a compendium. Default here: the thesis in section 1; sections 3.1-3.4 main line, 3.5 mechanism,
     section 4 supporting. Cutting further (section 4 to an appendix table) is your call.
 D9. Proofs: include human-checked proofs (Remark 1, the [1.008, 1.012] exponent bound, the rotated-design exponent-1
     result, the (c/2)/N barrier), or publish with an explicit "AI-authored / AI-checked" label per theorem. Who checks?
 D10. More runs before submission: k4 at 256 x 32, and one K = 3 variant across the whole ladder (CPU). The overnight
     goal of 3 Nov 02:30Z may already cover this; say if you want them held.
 D11. Referee 2 recommends dropping the Phase-1 board account from the paper whatever D3 decides. Default here: moved
     to Appendix D, anonymised, marked for deletion.
 D12. Section 3.3 evaluates an identifiable participant's public claim (forum topic 18298) and finds it fails our
     registered escape criteria: name, anonymise, or notify the author before circulating. Default here: topic number
     kept, no name, neutral pronouns.
-->

**Draft v2, 3 November 2026. Authors: [to be decided, D2].**

## Abstract

ARC's Phase-1 estimation problem asks for the output means of a random bias-free He-ReLU network of width 256 and
depth 32 under Gaussian input, at a budget of about 65,000 forward passes. ARC's matching sampling principle asks
whether a mechanistic estimator can match sampling, error $\varepsilon^2$ times the variance in $O(\varepsilon^{-2})$
time; the contest asks whether anything beats the best sampler. We test the first question on layer-wise deductive
estimators along depth equal to width/8, and the second at the Phase-1 shape. Between orders 2 and 3, ARC's cumulant
propagation has a two-level error-cost slope of 0.23-0.52, against sampling's 1; a public "scale-mode" closure starts
at 1.0 at width 32 and falls to 0.30 at width 256. At $256 \times 32$ ARC's estimators beat randomised quasi-Monte
Carlo (RQMC) in two windows: 16-90x at one pass (means only, precision 1-4e-2, against an extrapolated RQMC curve)
and about 2x near 450 passes (precision about $10^{-3}$, 4 of 5 nets). The scale-mode closure wins 2.5x at 688 passes.
All of these windows close before 3% of the budget, and at the budget RQMC is 7-65x more accurate. At Phase 2's shallow
$1024 \times 16$ the same ladder is steep (slope 0.83), our order-3 run is 19x more accurate than full-budget RQMC at
1.48x the budget, and public entries report wins within the budget; within-budget, every deductive method we ran still
lost to full-budget RQMC. On the sampling side, structured designs buy constants of 2-3x over Monte Carlo; no tested
sampler beat RQMC's fitted exponent (1.045), and for positive-weight rules chosen without the weights the asymptotic,
net-averaged exponent is provably within $[1.008, 1.012]$ at this width. Future-aware hybrids reach parity with RQMC at
the budget; a hybrid of ARC's propagation and a Kerdock design wins 1.2-9.9x on noisy nets at depth 8 but not at depth
32; pre-integration loses on every net, and exact or regional methods lose beyond width 3. This is a restricted negative: measured
for the methods tested, proven only for restricted classes.

## 1 Introduction

ARC asks for estimators of a network's expected output that are "mechanistic" and still compete with sampling: error
at most $\varepsilon^2$ times the output variance in time $O(\varepsilon^{-2})$ forward passes, for every
$\varepsilon$ (the matching sampling principle; "mechanistic" has no formal definition, and the working test is that
the estimator "avoids any random or pseudorandom sampling"). <!-- AU §1; HM §1.5 -->
Their test case is a random bias-free He-ReLU MLP with Gaussian input. Their paper proves results at fixed depth for
polynomial activations, conjectures that order-$K$ cumulant propagation errs by at most $c_K (L/n)^K$, concedes that
"this depth scaling is worse than Monte Carlo sampling", and lists matching sampling at large depth as open
(Wu et al. 2026, Sec. 7.3). Hilton's blog puts the open case as depth growing linearly with width. <!-- AU §1 (Wu et al.
2026, Sec. 5, App. D, Sec. 7.3; Hilton blog) --> The public contest built on this problem fixes Phase 1 at width
$n = 256$, depth $L = 32$ and a budget of $2.72 \times 10^{11}$ flops, about 64,850 forward passes; the organisers
report that Phase 1's best methods "tended to be based on variations of sampling". <!-- SM §2; AU §1 -->

**Two questions.** (Q1, ARC's) Along $L = \alpha n$, does any tested mechanistic (sample-free, layer-wise) family keep
an error-vs-compute slope of 1, that is, match sampling as the width grows? (Q2, the contest's) At $256 \times 32$,
does anything beat the best sampler (RQMC, not plain Monte Carlo) at the Phase-1 budget? Section 3 answers Q1 and is
the main line; section 4 answers Q2 and is supporting (decision D7). On random weights, "sample-free" by itself
excludes nothing: some fixed point set matches Monte Carlo's ensemble risk (section 4.1). So Q1 is a question about
the tested deductive families, not about every algorithm that avoids random numbers.

**Thesis.** At depth proportional to width, the layer-wise moment closures we tested have a two-level error-cost slope
below 1 that shrinks with width, and they beat sampling only in windows below 3% of the Phase-1 budget. At Phase 2's
$L/n = 1/64$ the same ladder is steep. This is what ARC's $(L/n)^K$ law predicts if it is tight; our contribution is to
measure it at the contest's shapes.

**What is new, plainly.** ARC already concede the depth scaling and the organisers already said Phase 1 was won by
sampling. What this paper adds: (i) measured constants and window sizes for ARC's own code at the contest shape and
along a ladder; (ii) a registered test of a public counter-claim (scale mode), which fails our escape criteria at the
Phase-1 shape; (iii) a per-cut attribution showing that the tested closures' error is accumulated in the early layers,
not made at any single step; (iv) for samplers, bounds showing that weight-independent rules have an exponent within
$1 + O(1/n)$ of 1. The conditional exponent statement of section 3.2 (Remark 1) is a line of algebra on ARC's law, not
a contribution.

**Why it matters for alignment.** [Placeholder for Kelvin's framing, decision D4.] What the sources support: if
mechanistic estimation cannot match sampling on random networks once depth grows with width, then the content of
ARC's principle sits in the informal word "mechanistic" and in the average case <!-- HM Summary -->, and any proposed
estimator should state its error-cost law along $L = \alpha n$ against the best sampler, not plain Monte Carlo
<!-- AU §7 -->. Random networks at $L = \alpha n$ are a stress test, not a model of trained networks; whether the same
depth problem appears in trained deep architectures is a conjecture we do not test <!-- HM §9, CONJECTURE there -->.

**Contributions.**

1. ARC's own code at $256 \times 32$ (registered): two winning windows against RQMC, 16-90x at one pass (extrapolated
   RQMC) and about 2x near 450 passes, both closing below 3% of the budget; a 7-40x loss at the budget (section 3.1).
2. The ladder along $L = n/8$: two-level slopes between orders 2 and 3 of 0.23-0.52 for ARC's estimators (section 3.2).
3. Stronger deductive variants, including the public scale-mode claim (forum topic 18298): constant factors in windows
   that close below 3% of the budget at $256 \times 32$ at implemented cost (below about 5% for a future-aware
   variant priced at a hypothetical cost). On the claim's own diagonal $L = n/4$ the only significant
   cells are a loss at $64 \times 16$ and a 2x win at $1024 \times 256$; the width trend is undecided (section 3.3).
4. A control at Phase 2's $1024 \times 16$, where the ladder is steep (section 3.4).
5. Where the tested closures make their error: accumulated over the first ~8 layers (section 3.5).
6. Supporting, for Q2: sampling designs give constants (2.1-2.9x over MC); weight-independent rules have an asymptotic,
   net-averaged exponent within $[1.008, 1.012]$ at $n = 256$; hybrids reach parity with RQMC at the budget; other
   tested families lose (section 4).

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
$C$ to the cost at which the sampler reaches $e$. <!-- AU §4.2 --> Window conclusions with gains below about 3x depend
on the meter: re-pricing the scale-mode closure's special functions at the contest meter's rates (exploratory) halves
its gain from 2.5x to 1.16x, and our order-3 Phase-2 run costs 1.48x the budget on ARC's counter but 2.24x on the
contest's (flopscope). <!-- SM Summary item 5, §7 -->

**Nets and truths.** Phase-1 shape: nets 200-204 at $256 \times 32$, noiseless, truths from $2^{26}$ paths. Ladder:
$L = n/8$ at $n = 32, 64, 128$, eight fresh nets per width, truths from $2^{24}$ paths. <!-- AU §4 --> Other lanes use
the same family at the shapes they state: $8 \times 256$ (six nets) <!-- ND §1 -->, widths 3-32 <!-- UE Summary -->,
and $512 \times 64$ (three nets) <!-- FA §4.5 -->.

**Comparators.** RQMC is scrambled Sobol with 8 scrambles per size. <!-- AU §4 --> Also: an antipodal Kerdock
5-design (129 mutually unbiased bases, 66,048 points, 1.9% over the Phase-1 budget; Table 5 compares at
$2^{16} = 65{,}536$ passes, 1.1% over; the setup of its Haar rotation is not charged) <!-- RN §2, §4.2 -->, and a
multilevel sampler that shares the late layers through one reference trajectory <!-- UE Summary -->.

**Process and labels.** Registered lanes hashed their predictions and frozen code before their evaluation runs and
disclosed later amendments; some cited results are exploratory or post hoc and are labelled so per claim. Proofs were
written by the lane authors ([C], Claude) or by a co-prover model (gpt-6-astra, [A]), and checked to the extent stated
per theorem in Appendix C; no proof has been checked by a human. Lane reports had fresh-session model reviews; the
final revised texts of AU (13:50Z update) and SM were not re-reviewed after their last revisions.
<!-- AU §4, §9; SM status line, §9; PI status line; RN status line --> Labels: PROVEN (with named hypotheses if
conditional), NUMERICAL, MEASURED-reg (registered), MEASURED-exp (exploratory or post hoc), HEURISTIC, CONJECTURE, and
CITED (external, not verified by us).

## 3 Q1: the deductive ladder along depth proportional to width

### 3.1 ARC's hierarchy at $256 \times 32$ (MEASURED-reg)

**Table 1.** ARC's estimators against RQMC on nets 200-204. <!-- AU §4.2 -->

| method | cost (passes) | nMSE (5 nets) | gain over RQMC at own cost | RQMC reaches its error at (passes) |
|---|---|---|---|---|
| k1 (means only) | 1 | 0.8-4.3e-2 | 16-90 (extrapolated) | 18-102 (extrapolated) |
| k2 ('simple') | 393 | 0.85-2.4e-3 | 0.83-2.2 | 330-740 |
| k2a ('augment') | 452 | 0.48-2.3e-3 | 0.85-4.6 (median 2.0) | 400-1,800 |
| exact Gaussian recursion | 1,184 | 1.0-2.0e-3 | 0.31-0.62 | 390-730 |
| k3f (order 3, factorised) | 49,097 | 0.6-2.8e-4 | 0.035-0.18 | 2,300-6,400 |

There are two windows. Means-only propagation (k1, one pass) is 16-90x more accurate than RQMC at one pass, against an
RQMC curve extrapolated below its measured range, at the coarse precision of 1-4e-2. ARC's best order-2 variant wins
on 4 of 5 nets (median 2.0x; 0.85x on net 203) at precision about $10^{-3}$, and RQMC catches up by 400-1,800 passes,
at most 2.8% of the budget. Order 3 loses 5-30x at its own cost. At the contest budget RQMC is 7-40x (median 22x) more
accurate than the best ARC variant that fits; the registered prediction of at least 10x on all five nets failed on net
200 (6.7x). Exact Gaussian moments do no better than ARC's cheaper approximations. <!-- AU §4.2, §6 -->

**Figure 1** (existing file `work/scale-mode/figs/fig1_256x32.png`). Median nMSE against cost on nets 200-204,
log-log, with MC and RQMC lines. k1 sits far below the MC line at one pass. ARC's k2, k2a and the scale-mode estimator
(section 3.3) sit slightly below RQMC at 400-700 passes. k3f sits near the budget line, well above RQMC's error there
(7-40x per net). The plotted k3fa point is net 200 only, despite the figure's "medians" title; it should be flagged in
the caption or the figure regenerated without it. <!-- SM §5, figs/fig1_256x32.png; AU §4.1-4.2 -->

### 3.2 The ladder along $L = n/8$ (MEASURED-reg)

**Table 2.** Error of each order, median over nets (nMSE at cost in passes; $G$ over MC / over RQMC at own cost).
<!-- AU §4.1 -->

| $n \times L$ | $K = 2$ (k2a) | $K = 3$ | $K = 4$ | $e_3/e_2$ | two-level slope $\gamma_{2\to3}$ (ARC's law) |
|---|---|---|---|---|---|
| $32 \times 4$ | 1.1e-3 at 117; 7.6 / 1.7 | 1.4e-4 at 6.8e3 (k3fa)ᵃ; best G 2.8 / 0.64 (k3f) | 3.4e-5 at 3.4e4; 0.86 / 0.18 | 0.12 | 0.52 (0.60)ᶜ |
| $64 \times 8$ | 1.3e-3 at 164; 4.8 / 1.9 | 1.8e-4 at 2.6e4 (k3fa)ᵃ; best G 0.63 / 0.18 (k3f) | 8.7e-5 at 2.6e5; 0.045 / 0.016 | 0.14 | 0.39 (0.50)ᶜ |
| $128 \times 16$ | 1.0e-3 at 260; 3.9 / 2.0 | 2.5e-4 at 1.0e5 (k3fa)ᵃ; best G 0.31 / 0.12 (k3f) | 9.5e-5 at 2.1e6; 0.005 / 0.002 | 0.25 | 0.23 (0.43) |
| $256 \times 32$ | 8.4e-4 at 452; 2.6 / 2.0 | 2.0e-4 at 4.9e4 (k3f)ᵇ; 0.10 / 0.06 | not run | 0.24 | 0.30 (0.375) |

ᵃ k3fa (factorised augmented) had the lowest order-3 error at $n \le 128$, at 4-8x k3f's cost; the $G$ values are
the best order-3 gains, which are k3f's. ᵇ At $256 \times 32$ k3fa ran on net 200 only, after scoring, and was worse
than k3f in error and cost (9.5e-5 at 4.0e5 passes against 6.2e-5 at 4.9e4); so the $K = 3$ cell at 256 is k3f, and
its cost (4.9e4) is not comparable with the k3fa costs above it. A single variant across the ladder was not run (D10).
ᶜ Descriptive: these results were seen before the amendment that registered them. <!-- AU §4.1 -->

$\gamma_{2\to3} = \log(e_2/e_3)/\log(C_3/C_2)$ is a two-level slope from two points per width, not a fitted exponent,
and its four values are not monotone in width; we do not claim a width trend from them. Each order's error stays
within a factor of about 2-3 as the width grows eightfold, which is what $c_K (L/n)^K$ predicts at fixed $L/n$; each
step up the hierarchy divides the error by 4-8 (order 2 to 3) or 2-4 (3 to 4) and multiplies the cost by about $n/4$
to $3n$. k2a's gain over MC falls from 7.6 to 2.6 across the ladder (Table 2). The registered scorer's figures (best
variant's median) are 8.1 to 2.6, and the literal reading of the registered wording (median of each net's best
variant) gives 8.8, 5.1, 4.6, 3.0; all registered predictions on it hold under both. Order 3 loses to RQMC by 5-20x
from $n = 64$ on. <!-- AU §4.1 --> A registered extension to $512 \times 64$ (three nets) found ARC's order 2 losing to
RQMC at its own cost (0.84x) and order 3 improving on order 2 by only 2.95x. <!-- FA §4.5 --> An independent lane found
order 2's gain over plain MC falling from 2-8 at widths 32-128 to about 0.7-1.1 at width 1024, over depth/width ratios
from 1/8 to 1/2. <!-- HM Summary; HM §6.3 -->

**Remark 1** (PROVEN UNDER the uniform law; statement and proof [A, round 3], matching the lane author's arithmetic
[C]). Suppose order $K$ costs $C_K \ge d_* n^{K-1}$ passes and errs by $e_K \ge a c_* (L/n)^K$, with $a, c_*, d_*$
independent of $K$, for $0 < L/n < 1$. Then
$$e_{\text{best}}(C) \;\ge\; a c_* \frac{L}{n} \Big(\frac{C}{d_*}\Big)^{-\gamma}, \qquad \gamma = \frac{\log(n/L)}{\log n}.$$
*Proof.* At budget $C$ the affordable orders satisfy $K - 1 \le \log(C/d_*)/\log n$. Since $L/n < 1$, the error bound
$a c_* (L/n)^K = a c_* (L/n) \cdot (L/n)^{K-1}$ is smallest at the largest affordable $K$, where
$(L/n)^{K-1} \ge (L/n)^{\log(C/d_*)/\log n} = (C/d_*)^{-\log(n/L)/\log n}$. $\square$
At fixed depth $\gamma \to 1$ as the width grows (ARC's theorem regime); at $L = \alpha n$,
$\gamma = \log(1/\alpha)/\log n \to 0$; at $256 \times 32$, $\gamma = 0.375$. ARC state the law as an upper bound with
order-dependent constants. The remark needs it as a lower bound, uniformly in $K$, and measurements at $K \le 4$
cannot establish that. So the statement is "if ARC's law is tight, climbing the ladder loses to sampling", not "ARC's
law implies the negative". <!-- AU §2.5 -->

### 3.3 Stronger deductive variants: constant factors in windows

**Scale mode (MEASURED-reg; decision D12).** A participant claimed on the contest forum (topic 18298) that separating a
collective scale mode, carried as a one-parameter law, "restores convergence and beats sampling" with depth growing
with width. <!-- SM §1 --> We ran the author's code unchanged; it reproduced their $64 \times 16$ headline (nMSE
1.517e-3 against their 1.52e-3). <!-- SM Summary -->

**Table 3.** Scale-mode estimator (LVTV2, about order-2 cost) and its order-3 level (SL3) along $L = n/8$, medians.
<!-- SM §5 -->

| $n \times L$ | LVTV2 nMSE at cost | $G$ over RQMC (95% CI) | SL3 nMSE at cost | SL3 $G$ over RQMC | slope: scale law / ARCᵈ |
|---|---|---|---|---|---|
| $32 \times 4$ | 7.2e-4 at 200 | 1.8* (1.1-2.6) | 8.3e-5 at 1.6e3 | 1.5 | 1.0 / 0.54 |
| $64 \times 8$ | 6.7e-4 at 287 | 2.0 (1.7-2.7) | 7.2e-5 at 6.1e3 | 0.73 | 0.72 / 0.37 |
| $128 \times 16$ | 6.0e-4 at 426 | 2.4 (1.7-2.9) | 9.5e-5 at 2.1e4 | 0.19* | 0.52 / 0.28 |
| $256 \times 32$ | 3.6e-4 at 688 | 2.5 (2.0-4.7) | 7.2e-5 at 7.5e4 | 0.067* | 0.30 / 0.31 |

(* uses the RQMC curve extrapolated outside its measured range. ᵈ Two-level slopes recomputed per net on the same
nets (ARC: k2a to each net's best order-3 variant), medians over nets; this is why the ARC column differs from Table
2's medians-based 0.52, 0.39, 0.23, 0.30.) <!-- SM §5 -->

At $256 \times 32$ this is the most accurate order-2-cost estimator we measured, and RQMC reaches its error at about
2.3x its cost (about 1,600 passes, 2.5% of the budget). At the budget RQMC is 33-65x more accurate than every
scale-law method that fits. Its order-3 level costs more than the whole budget. Neither registered escape criterion was
met. The first asked for a two-level slope near 1 along $L = n/8$ with the order-3 level beating RQMC: the slope is
0.52 and 0.30 at $n = 128$ and 256 (0.9 needed), and the order-3 level beats RQMC on 0 of 5 nets at $256 \times 32$.
The second asked for a gain over RQMC above 1 at every width of the claim's own diagonal $L = n/4$, growing with width.
On that diagonal (8 fresh nets per width, exploratory intervals) the median gain over RQMC was 0.79, 0.73, 1.2, 0.43,
2.0 from $64 \times 16$ to $1024 \times 256$. The only cells whose 95% interval excludes 1 are a loss at $64 \times 16$
and a win at the largest width, $1024 \times 256$ (1.96, interval 1.09-7.4); the trend with width is undecided
(exponent +0.19, 95% CI over nets -0.01 to +0.74; -0.20 without the 1024 cell). Against naive MC it wins in 4 of 5
diagonal cells, as the author claims. <!-- SM Summary, §5, §6, §8 -->

**Radius-corrected closure (MEASURED-reg; cost arithmetic).** A Gaussian closure whose amplitude (radius) law is
exactly right, run as a finite-sample recursion, errs by 1.9e-3, 9.2e-4 and 4.9e-4 at $n = 64, 128, 256$, within 6%
of $L/n^2$ (a post hoc observation, with no convergence study in sample size). As run it pushes $2^{19}$ samples per
layer, at least ~255x what MC needs to reach that error. A deductive version, which nobody has built, would beat MC
only if it cost less than about 5 order-2 steps per layer, and RQMC only below 2-3.5. <!-- AU §4.4(c) -->

**Future-aware projections (MEASURED-reg benchmark; cost ledger post hoc).** A backward pass finds where the future
will read a closure's error. Keeping the cloud's law exact in the $k = 64$ directions the future reads most cuts the
Gaussian closure's error at $256 \times 32$ by 19x, but carrying that law by particles is a sampler whose error is
45-250x RQMC's at its cost. ARC's order 3 with its third cumulant kept only in $k = n/4$ future directions, as
implemented, loses to RQMC by 6-200x at $n = 64$-256 (0.036-0.12x). At a hypothetical dedicated cost it would win
2.6, 3.0, 2.4x ($n = 64, 128, 256$); charging the order-2 pilot it needs gives 1.75-2.2x, and also charging the dense
direction extraction actually used gives 0.5-0.7x (approximate count, post hoc). At $n = 512$ the $n/4$ version fails
numerically. <!-- FA Summary items 1-3, §4.4 -->

### 3.4 Control: Phase 2's $1024 \times 16$ (MEASURED-reg; CITED board)

At Phase 2's shape ($L/n = 1/64$, 12 public MLPs) the registered test N2 holds on 12 of 12 MLPs: full-budget RQMC
beats every deductive method we ran within the budget, including ARC's best order-2 variant (by 1.06-1.9x; the 1.06
margin on MLP 7 is within noise). Beyond the budget the ladder is steep: the two-level slope between orders 2 and 3 is
0.83 (0.76-0.88 over MLPs 0-5), against 0.30 at $256 \times 32$, and ARC's unengineered factorised order 3 is 18.5-20.6x
more accurate than full-budget RQMC at 1.48x the budget on ARC's counter (2.24x on the contest's flopscope meter).
<!-- SM Summary item 4, §7 --> The deductive win inside the budget is external evidence (CITED, not verified by us):
engineered order-3 entries on the public Phase-2 board report about 100x below full-budget MC within about 12% of the
budget. <!-- SM §7 --> Our run is consistent with that but was not engineered into the budget. The negative of
section 3 concerns depth growing with width, not deduction in general.

### 3.5 Mechanism: where the error is made

**Table 4.** Per-cut attribution at $256 \times 32$, medians over 5 nets (MEASURED-reg): ARC k2's state at layer $l$
pushed through the true rest of the net, against the moment-matched Gaussian of the true layer-$l$ law put in at a
single cut. <!-- AU §4.3 -->

| cut $l$ | 1 | 2 | 4 | 8 | 16 | 24 | 31 |
|---|---|---|---|---|---|---|---|
| k2 past defect | 1.0e-4 | 1.8e-4 | 5.0e-4 | 7.8e-4 | 9.8e-4 | 1.2e-3 | 1.25e-3 |
| oracle Gaussian, single cut | 6.7e-5 | 1.6e-4 | 2.4e-4 | 2.2e-4 | 1.8e-4 | 1.3e-4 | 3.3e-5 |

By layer 8 the k2 state carries 44-64% (median 59%) of its final error. A single Gaussian cut of the true law loses
1.3-2.4e-4 at $l = 2$-24 (less at $l = 1$ and 31) against the recursion's 1.2e-3: the error is accumulated. Two
registered predictions here failed: P7's second clause (the single-cut defect at $l = 16$ is 0.15 of k2's total, not
$\ge 0.2$) and, narrowly, P9b (on net 200, third-cumulant participation ratio 4.05 at $l = 16$ against $\le 4$). Where
the error is made, the true cloud's non-Gaussian structure is high-dimensional: the third-cumulant participation ratio
is 114-116 at $l = 1$, 23-28 at $l = 4$, 4-11 at $l = 8$ and 1-4 from $l = 12$ (descriptive). <!-- AU §4.3 --> One
exact Gaussianisation after the first layer already leaves an error that no later suffix of depth $\alpha n$ removes
(PROVEN [A], asymptotic and annealed; constants checked numerically [C]). <!-- BB Summary item 10; AU §2.4 -->

**How the future prices a defect (PROVEN identity).** For a forward layer-wise estimator with reconstructions $Q_l$ and
defects $\Delta_l = Q_l - \Phi_l Q_{l-1}$, $\hat Y - Y = \sum_l \langle g_l, \Delta_l \rangle$, with $g_l$ the map
from layer $l$ to the output. Averaged over the future's weights, a layer-$l$ defect costs
$\sum_d b_d \lVert M_d \rVert^2$ over its radially normalised moment tensors, with $b_d \ge 0$ and $\sum_d b_d = 1$.
This prices a given defect; it bounds no class of representations. <!-- AU §2.1-2.2; SYN §2 --> At infinite width a
future of $t = 31$ layers puts weight $b_0 = 0.97$ on the radius and $b_1 = 0.003$ on degree 1, and reads the degree
$\ge 2$ part at mean degree 42.3 (NUMERICAL, infinite width); at finite width $b_0 = 0.948$ (MEASURED-exp).
<!-- AU §3 --> The value function's mean Hermite degree on the Gaussianised layer-$l$ cloud is 21, 7.7, 4.1, 1.9, 1.3,
1.04 at $l = 0, 4, 8, 16, 24, 31$ (measured in a registered lane, whose registered mean-degree tests missed their joint
criteria). <!-- AU §3, from REL; REL Summary --> (That the next layer's frame is uniformly random relative to the
cloud's axes follows from the rotation invariance of iid Gaussian $W$.) <!-- REL Summary item 1 -->

**Reading.** Between layers, compressed descriptions move almost linearly (consecutive relevant coordinates have
linear $R^2$ 0.82-0.99; the registered test BA.1 missed narrowly, and the scrambled positive controls had not been run
through the same test, so this reads "the tests found low degree"). Relative to coordinates where the law is
computable, the dependence is of high degree. No layer of $256 \times 32$ offers both a computable law and a low
read-out degree. <!-- AU §5, §3 table --> Bit counts of codes do not price estimation: with decoder
$\mathbb{E}[a \mid c]$ a code sum is unbiased at any rate, so the cost sits in computing code probabilities and
conditional means. <!-- AU §5 -->

## 4 Q2: does anything beat RQMC at the budget? (supporting; placement is decision D7)

### 4.1 The sampling side

**Table 5.** Gain over MC at $2^{16}$ passes on nets 200-204, radius exact (MEASURED-reg), and fitted exponents over
$N = 2^8$ to $2^{18}$ (risk $\sim N^{-p}$; MC has $p = 1$). <!-- RN Summary items 1-2, §4.2 Table C -->

| sampler | random bits | median gain (range) | exponent $p$ [95% CI] |
|---|---|---|---|
| scrambled Sobol | 135,168 | 2.13 (1.95-2.77) | 1.045 [1.03, 1.08] |
| scrambled Sobol in $W_1$'s polar frame (white-box) | 135,168 | 2.22 (1.83-2.64) | 1.058 [1.01, 1.08] |
| antipodal Kerdock 5-design, Haar-rotated (66,048 points; rotation setup uncharged) | 1,044,480 | 2.89 (2.20-3.93) | - |
| pairwise-independent MC | 16,384 | 1.53 (0.40-1.70) | - |
| centred Sobol, fixed (no random bits) | 0 | 2.07 (1.78-5.55) | 1.06-1.13 (fixed sets, wide CIs) |

No randomised structured sampler reached 4x on any net. Scrambled Sobol's exponent interval excludes 1 (registered
PA1 holds); the white-box frame showed no exponent difference ($-0.002$ [$-0.04$, 0.03]). Fixed point sets win on some
nets and lose on others, with no error bar. <!-- RN Summary, §4.1-4.2 --> Random bits do not track accuracy: across
nine orders of magnitude of bits the error at fixed compute does not follow the bit count. <!-- RN Summary item 3 -->

**Theorems for rules chosen without looking at the weights.** These hold on average over nets and, where stated,
asymptotically in $N$; provenance in Appendix C. <!-- RN §2 -->

- Exact pricing (PROVEN [C][A]): the ensemble risk of a point rule $Q$ on the sphere is $\sum_{d \ge 1} a_d B_d(Q)$,
  with $a_d$ the expected energy at spherical-harmonic degree $d$ and $B_d(Q) \ge 0$. Consequence: any union of
  independently rotated copies of a fixed design has exponent exactly 1; designs buy constants, never rates.
- Black-box exponent (PROVEN [A], asymptotic in $N$): the best positive weight-independent rule has exponent between
  $1 + 2/(n-1)$ and $1 + 3/(n-1)$, that is $[1.008, 1.012]$ at $n = 256$. This does not constrain a slope fitted over
  $2^8$-$2^{18}$. Over that range the cancellable degree of the bound steps up twice (even degrees from 4 to 6 at
  ~5.5e3 points, to 8 at ~8.6e4), which alone allows an effective slope of at least ~1.04, the size of RQMC's fitted
  excess in Table 5. <!-- RN §2, §4.1 -->
- Design limits (PROVEN [A], proof partly checked: the lane author checked "its structure and its agreement with the
  data, not every step"): along $L = \alpha n$ with $L/\sqrt n \to \infty$ the fixed-degree spectrum converges, and the
  gains of the simplex, cross-polytope and Kerdock designs converge to 2.09, 2.36 and 3.15 (measured at
  $256 \times 32$: 1.93, 2.39, 3.04). The variance these designs fight is the accumulated fluctuation of activation
  norms in the early layers. A registered test of the finite-size bands at $512 \times 64$ failed narrowly on all four
  bands: the limit is proven, the speed of approach is not. <!-- RN Summary item 4 -->
- Black-box ceiling (PROVEN [A] in power form, [C] in harmonic form): at $n = 256$ every even degree from 6 on is paid
  in full for $N$ up to $8.6 \times 10^4$. A spherical 7-design needs at least $5.66 \times 10^6$ points, 87x the
  budget (PROVEN, Delsarte-Goethals-Seidel). Plugging measured spectra into the ceiling gives an estimated 10-19x at
  the budget (HEURISTIC: an estimate, not a certified bound). <!-- RN §2, Summary item 4 -->

The pre-integration lane proved a matching barrier for signed rules (PROVEN [C], audited and repaired by [A]):
averaged over nets, for nodes and scalar weights chosen independently of the net,
$$\frac{\mathbb{E}_W \lVert \text{error} \rVert^2}{\mathbb{E}_W \operatorname{tr}\operatorname{Var} f} \;\ge\; \frac{c/2 - o(1)}{N}$$
for $N$ up to about $n^r/r!$, whenever the even angular energy above degree $2r$ carries a fraction $c$ of the
averaged variance ($r$ the smallest degree whose harmonic dimension is at least $2N$). The share $c$ is measured on two
nets per width, not proven: the even share above degree 2 grows from 0.08 at $n = 32$ to 0.26 at 256. Without that
hypothesis the bound is absolute and small: $1/(4\pi^2 N)$ for $N \le n/2$ points. <!-- PI Summary item 5, §5 -->

Beyond linear rules: under a Gaussian surrogate prior, adaptive and nonlinear algorithms cannot beat the best
nonadaptive linear rule (classical, re-proved). The real prior is far from Gaussian (excess kurtosis 6.9-9.1 for a
unit's output), so adaptive and nonlinear methods on the true prior are neither excluded nor shown to help.
<!-- PI §5 --> On random weights, determinism is no restriction: some fixed point set matches MC's ensemble risk
(PROVEN, existential), and under exact-transform primitives seeds read off the weights simulate a randomised estimator
(PROVEN). <!-- RN Summary item 3; UE Summary; HM Summary --> So "sample-free" excludes nothing until "mechanistic" is
defined.

### 4.2 Multilevel sampling and pre-integration

**Multilevel sampling.** Sharing the late layers through one reference trajectory beats radius-exact MC by
$\Omega(n/\log^2 n)$ at $L = \alpha n$ (PROVEN UNDER layer-wise cost hypotheses). <!-- UE Summary --> Measured as ideal
propagation-only ratios (setup excluded), its gain is 1.21, 1.41, 1.58, 2.43 at $L = n$ ($n = 32$-256) and 0.99 at
$256 \times 32$ <!-- BB Summary item 8, BB sampler note -->; along $L = n/8$ it is 0.83 to 0.99 from $n = 32$ to 256,
and 1.00-1.07 at $512 \times 64$. It should pay only at depths in the hundreds ($L/(2\log^2 L) \gg 1$; HEURISTIC).
<!-- RN Summary item 6 -->

**Pre-integration.** Integrating exactly along one line costs about $nL/2$ passes (3,469 at $256 \times 32$; 752 for a
window) and is worth about one RQMC point (0.84-1.29 at $256 \times 32$; MEASURED-exp, at equal sample counts, post
hoc). It raised the fitted exponent by 0.1-0.3 only at input dimension 4-8, and lost at equal cost on every net
(MEASURED-reg): per-net minima 21-1,410x along the ladder and at $256 \times 32$, 15-91x at $8 \times 256$.
<!-- PI Summary items 1-3 -->

### 4.3 Exact, regional and hybrid methods

**Table 6.** Other method families against the best sampler. <!-- sources per row -->

| family | where tested | result | label | source |
|---|---|---|---|---|
| certified branch-and-bound over input cones | widths 3-32, depths 4-64 (72 nets) | deductive estimate never beats RQMC (best ratio 0.18, width 3); centre-point estimate wins 4-18x in 4 of 24 runs at width 3 (see text); cost ~10x per unit of width; certificate vacuous from width 6 | MEASURED-reg | UE Summary |
| certified deterministic code | $8 \times 256$, 6 nets | 23-106x worse than RQMC | MEASURED-reg | ND Summary 5 |
| integrate top regions, drop rest | $8 \times 256$ | 7-1,222x worse than RQMC with exact tail, at an optimistic 9 mv per region | MEASURED-reg | ND Summary 4 |
| exact-mean controls + RQMC (hybrid H1) | $n = 64$-256, $L = n/8$ | parity at 6.5e4 passes (1.00-1.03x RQMC; per net 0.95-1.15; uncertainty not quantified); 0.86-0.95x at 1e4 | registered design, scored post hoc | FA Summary 3, §4.3 |
| certified-linear backward pieces | nets 200-204 (exact pieces); net 200 ($\varepsilon$-certified) | coverage $\ge 50\%$ only at $l = 31$; one layer back top-1000 exact pieces cover 0.1-7.6%; two back 0 | MEASURED-exp | LOG 16:17 |
| ARC kprop + Kerdock, combined by error models | $256 \times 8$ and $256 \times 32$, noise $\sigma = 10^{-3}$ | depth 8: 1.2-9.9x over the best sampler; depth 32: 0.84-1.06x | MEASURED-reg | AN Summary |

The narrow-deep case shows where the difficulty sits. At $8 \times 256$ the problem past layer 20-48 is linear on every
sampled input, and RQMC with that exact linear tail is 3-15x better than plain RQMC. But the map from the input to that
layer has 1.3-2.2e5 linear regions in 4 million inputs, thin in 7 angular dimensions, with 1-2% of inputs in regions
never seen. <!-- ND Summary items 1, 2, 6 --> Exact integration on one ReLU layer wins only at widths 2-3 (92-170x at
width 3; about 270x worse than RQMC at width 4). <!-- ND §6 --> At depth, the branch-and-bound lane's centre-point
estimate, which evaluates the net's gates at cell centres and so is a form of structured sampling, wins 4-18x in 4 of
24 runs at width 3 (depths 16-32); those wins mostly shrink below 3x if its cost were doubled and concern only the
noiseless mean, and it loses 33x-2e5x at width 4. <!-- UE Summary -->

For hybrids the criterion is arithmetic: a surrogate with exact mean whose residual variance falls like (construction
cost)$^{-\delta}$ gives MSE $\sim C^{-(1+\delta)}$. <!-- LOG 13:52; PI §6 --> Measured on one net per width
(exploratory), the layer-1 residual share falls like $k^{-0.25}$ at $n = 64$ and $k^{-0.09}$ at $n = 128$, so
$\delta > 0$ uniformly in width is not established. <!-- FA §5 --> The controls remove what scrambled Sobol already
integrates. <!-- FA Summary 3 --> At depth 32 a control mean would have to be right to about $10^{-6}$ at depth 16 or
more before it helps. <!-- AN Summary -->

## 5 What this does not show

- No lower bound for all algorithms. An argument in our lane reports (HEURISTIC) says that proving no estimator beats
  sampling on this explicit problem would amount to a super-linear time lower bound, for which no technique is known.
  <!-- AU §8; UE §3.3; SYN §2 --> Worst-case barriers (#NSETH, Impagliazzo-Kabanets-Wigderson) do not reach random
  weights. <!-- HM Summary; UE Summary -->
- Remark 1 is conditional on ARC's law holding as a lower bound uniformly in $K$; we measured $K \le 4$ ($K \le 3$ at
  $256 \times 32$), and the ladder mixes order-3 variants (Table 2). <!-- AU §2.5, §4.1 -->
- The sampling theorems cover weight-independent rules, on average over nets, mostly asymptotically in $N$. They say
  nothing about a single net or about any rule that looks at the weights (the polar-frame rule was only measured), nor
  about adaptive and nonlinear methods under the true prior. The point-rule barrier rests on a spectral share measured
  on two nets per width. <!-- PI §5; RN §2 -->
- Scope: one family (square, bias-free He-ReLU, Gaussian input, noiseless), five nets at the Phase-1 shape, eight
  per ladder width, three at $512 \times 64$. Every width trend is a descriptive slope over a factor of 4-8 in width,
  and uncertainty is mostly reported as ranges over nets. Trained networks were not tested. <!-- AU §4, §8; FA §4.5 -->
- Untested routes: implicit representations of the early high-dimensional structure; other radius-direction
  couplings; a deductive radius-corrected closure; scale-law orders 4 and up; non-layer-wise methods.
  <!-- AU §6 item 8, §7 item 5; SM §8 -->
- Metric: our nMSE and ARC's flop counter differ from the contest's raw MSE, utilisation factor and meter; windows
  below about 3x are meter-dependent (section 2). <!-- SYN C17; SM §5 -->
- Bit counts of learned codes are best-found upper bounds, not certified, and price representation only.
  <!-- AU §3, §5 -->

## 6 Related work

References marked † are as cited in our lane reports; those marked ‡ were added in revision from the reviewer's list
and our own knowledge. None has yet been checked against the source; full bibliographic entries remain to be added.

ARC's program†: Wu et al. (2026, arXiv:2605.05179 v2), with the cumulant-propagation estimators, the $c_K (L/n)^K$
conjecture and the depth concession <!-- AU §1 -->; "Competing with sampling" (Neyman, Lecomte, Wu, Winer, Hilton,
Robinson, ARC blog, November 2025), which states the matching sampling principle <!-- HM §1.5 -->; posts by Hilton
(23 June 2026) and Christiano (3 June) quoted in AU §1. Earlier ARC work‡: Christiano et al., "Formalizing the
presumption of independence" (2022), the motivation for heuristic estimators; Wu and Hilton on estimating
low-probability outputs (2024). The contest's forum topics†: 18298 (scale mode), 18198 (covariance propagation in
Phase 2), 18147 (Gaussian closures far behind a budget-matched sampler at Phase 1), 18282 (a never-sampling Phase-2
estimator, unverified), and 18125 (Phase-1 metering). <!-- SM §1-2; LOG 10:35; AU §1; PB Rules -->

Finite-width theory‡. Roberts, Yaida and Hanin (*The Principles of Deep Learning Theory*, 2022), Yaida (2020) and Hanin
(2023, perturbative hierarchies) expand finite-width networks with depth-to-width ratio $L/n$ as the effective
parameter; non-Gaussianity of order $L/n$ there is the same parameter as ARC's $(L/n)^K$ law, and our section 3 is a
measurement of what that expansion costs an estimator. Li, Nica and Roy (2022, neural covariance SDE) and Hanin and Nica
(2019/2020, products of random matrices; lognormal output scale†) give the $L/n$ scaling limit and the log-norm
fluctuation behind the "scale mode" of section 3.3 and the radius weight $b_0$ of section 3.5. Signal propagation and
the infinite-width limit‡: Poole et al. (2016), Schoenholz et al. (2017), Lee et al. (2018), Matthews et al. (2018).
Whether these works already predict our specific constants has not been checked.

Complexity†: Impagliazzo, Kabanets and Wigderson (2002) and Chen and Tell (STOC 2021), used for the worst-case
white-box barriers <!-- HM Summary -->; pseudorandom generators for halfspaces, polynomial threshold functions and
threshold circuits (Meka-Zuckerman, Gopalan-Kane-Meka, Kane, O'Donnell-Servedio-Tan, Kelley-Meka,
Harsha-Klivans-Meka, Chattopadhyay-De-Servedio, Hatami-Hoza-Tal-Tell), which reach only the first ReLU layer, and
Chen-Li-Li-Meka (2022) on why fooling constant-depth ReLU nets would separate $\mathrm{TC}^0$ from $\mathrm{NC}^1$
<!-- RN §3 -->.

Quasi-Monte Carlo and average-case integration†: Owen's scrambled nets; He and Wang (2015) on rates for discontinuous
integrands; Traub, Wasilkowski and Woźniakowski (1984) and Wasilkowski and Woźniakowski (1984) on adaption under
Gaussian priors; Novak and Woźniakowski (Vol. II); pre-integration (Griewank-Kuo-Leovey-Sloan; Gilbert-Kuo-Sloan).
<!-- RN §3; PI §5; LOG 13:51 --> Spherical designs†: Delsarte-Goethals-Seidel, via Bannai-Bannai. <!-- RN §2 --> Regions
and noise sensitivity†: Hanin-Rolnick, Jonasson-Steif-Zetterqvist, De Palma-Kiani-Lloyd. <!-- RN §3 -->

## 7 Open questions

1. A deterministic $O(n)$-pass representation of the cloud's joint law in its top ~$n/4$ future directions at the
   benchmark's accuracy would open a window that grows with width. None is known. <!-- FA Summary 5; SYN §6 -->
2. A white-box surrogate family with exact means and residual variance $C q^{-b}$ uniformly in width gives an exponent
   above 1 when $b$ exceeds its evaluation-cost exponent. The candidate named (biased Gaussian ridge controls) is
   untested; squared-hinge controls provably cannot touch even degrees $\ge 4$. <!-- PI §6 -->
3. CONJECTURE: the ladder's slope decay along $L = \alpha n$ and the sampling bound are two consequences of one
   angular-degree spectrum. No source derives the per-order factor from the spectrum. <!-- SYN §5 -->
4. The finite-width price spectrum beyond $b_0$, and a proof of the spectral share $c$ for the ensemble.
   <!-- AU §8; PI §5 -->
5. Does anything beat the best multilevel sampler by a polynomially growing factor at $L = \alpha n$? (Revised
   conjecture C0*, "little evidence" either way.) <!-- UE Summary 5 -->
6. A deductive radius-corrected closure below ~5 order-2 steps per layer, and whether $L/n^2$ is its limit.
   <!-- AU §4.4(c), §8 -->
7. Learned and exact region estimators at small width. The learned-layered-experts lane (Kelvin's direction on 2 Nov)
   is paused: its results before 18:56Z were ruled not to count, training compute was made non-counting (17:45Z), its
   headline became N(0,I) error against MC at the same number of training samples (20:41Z), and the exact cone tree
   became the only active task (22:01Z). The last experts result (3 Nov 00:17Z and 01:56Z, exploratory): at
   $32 \times 4$, N(0,I) error does not fall with the number of experts (0.013, 0.022, 0.046, 0.066 at K = 16-1024);
   the lane read a similar K-trend in earlier runs as likely undertraining (20:40Z). The cone tree (widths 4-6, depth 4;
   no independent review) found merging saves a constant 2.5-3x that does not improve with width, and RQMC beats exact
   cells at width 6. Since 3 Nov 02:28Z the lane maps gate patterns at depth 4, $n = 4$-8. Checked at 2026-11-03 02:40Z
   by reading the LOG tail and the process list (the 4x4 experts run `step5m.py` stopped; `pattern_chain.py` running).
   <!-- LOG 17:45, 18:56, 20:40, 20:41, 22:01; 3 Nov 00:17, 01:56, 02:28, 02:30 -->

## Appendix A. Source keys

Paths under `/srv/agent-data/home/workspaces/mats/` unless stated. Repo files fetched from
`futarchy-fi/inconsistency-search` at `main` 7a10d6a1 (2026-11-03T01:28Z); each was byte-identical to the outbox copy.

| key | file |
|---|---|
| AU | `outbox/arc-update-2026-11-02.md` (status 13:50Z) |
| SM | `outbox/scale-mode-2026-11-02.md` (final 13:24Z); figure `work/scale-mode/figs/fig1_256x32.png` |
| PI | `outbox/preint-2026-11-02.md` (final) |
| RN | `outbox/randomness-2026-11-02.md` (final ~16:20Z) |
| FA | `outbox/future-aware-2026-11-02.md` (Part 1 final; n = 512 at 20:05Z) |
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
| LOG hh:mm | `outbox/overnight-report-2026-10-29.md`, 2 November entry at that time (3 November entries marked) |

Where SYN and a later final disagree we used the final: the preint final withdraws the "~$nL$ evaluations identify
the net" claim and narrows the barrier; the randomness final gives registered exponents and constants that were
pending in SYN; the future-aware final corrects the hybrid score (1.00-1.03x, not 0.8-1.0x) and the deductive window
(as implemented 0.04-0.12x; hypothetical-cost ledger with pilot and dense extraction 0.5-0.7x, post hoc).
<!-- PI §5; RN Summary; FA Summary 3, §4.4; LOG 15:29 --> CR (one-way linear summaries need
$(1/\varepsilon)^{2(n-1)/3}$ numbers; not a running-time bound) and S31 were read for context and are not cited above.

## Appendix B. Claim ledger

| claim | label | source |
|---|---|---|
| Phase 1 = $256 \times 32$, $2.72 \times 10^{11}$ flops = 64,850 passes | CITED | SM §2; AU §1 |
| k1 16-90x RQMC at 1 pass (extrapolated RQMC) | MEASURED-reg | AU §4.2, §6 |
| k2a beats RQMC on 4 of 5 nets, median 2.0x, window closes at 400-1,800 passes | MEASURED-reg | AU §4.2 |
| order 3 loses 5-30x at own cost; RQMC 7-40x (median 22x) better at budget; P4 failed on net 200 (6.7x) | MEASURED-reg | AU §4.2 |
| two-level slopes 0.52, 0.39, 0.23, 0.30 vs ARC's law 0.60, 0.50, 0.43, 0.375 (mixed K = 3 variants) | MEASURED-reg ($n \le 64$ descriptive) | AU §4.1 |
| k2a gain over MC 7.6 to 2.6; scorer 8.1 to 2.6; literal 8.8 to 3.0 | MEASURED-reg | AU §4.1 |
| $512 \times 64$: k2 0.84x RQMC; $e_{k2}/e_{k3}$ = 2.95 | MEASURED-reg (3 nets) | FA §4.5 |
| K = 2 gain over MC about 0.7-1.1 at width 1024 (depth/width 1/8-1/2) | MEASURED | HM Summary, §6.3 |
| Remark 1 ($\gamma = \log(n/L)/\log n$) | PROVEN UNDER uniform law [A r3] | AU §2.5 |
| scale mode: 3.6e-4 at 688 passes, 2.5x RQMC (CI 2.0-4.7), 33-65x behind at budget, 1.16x re-priced | MEASURED-reg (re-pricing exp) | SM Summary, §5 |
| scale-mode escape criteria D1 (slope at 128, 256) and D2 (diagonal) fail; diagonal 0.79, 0.73, 1.2, 0.43, 2.0; significant only 64 x 16 (loss), 1024 x 256 (1.96, 1.09-7.4); trend +0.19 (-0.01 to +0.74) | MEASURED-reg; intervals exploratory | SM §6, §8 |
| radius-corrected closure ≈ $L/n^2$ (post hoc); ≥ ~255x MC's cost as run; break-even < ~5 order-2 steps per layer | MEASURED-reg; arithmetic | AU §4.4(c) |
| future-aware: 19x over Gaussian closure at $k = 64$; particles 45-250x behind RQMC; projected k3 as implemented 0.04-0.12x; hypothetical 2.6/3.0/2.4x; with pilot 1.75-2.2x; with dense extraction 0.5-0.7x | MEASURED-reg; ledger post hoc | FA Summary, §4.4 |
| Phase 2: N2 holds 12/12 (RQMC beats every within-budget deductive method, k2a by 1.06-1.9x); slope 0.83; k3f 18.5-20.6x below full-budget RQMC at 1.48x (ARC) / 2.24x (flopscope) budget | MEASURED-reg | SM §7 |
| Phase 2 board: engineered order 3 ~100x below MC within ~12% of budget | CITED | SM §7 |
| 44-64% of k2 error by layer 8; single cut 1.3-2.4e-4 at $l$ = 2-24 vs 1.2e-3; P7 (2nd clause), P9b fail | MEASURED-reg | AU §4.3 |
| third-cumulant PR 114-116 at $l = 1$ to 1-4 from $l = 12$ | MEASURED-reg (descriptive) | AU §4.3 |
| one Gaussianisation after layer 1 leaves an error no suffix removes | PROVEN [A] (asymptotic, annealed) | BB Summary 10; AU §2.4 |
| pricing identity; $b_0$ = 0.97 (inf.), 0.948 (finite) at $t = 31$; mean degree of $b_{\ge 2}$ 42.3 | PROVEN [C, step corrected by A]; NUMERICAL; MEASURED-exp | AU §2.2, §3 |
| mean Hermite degree 21 ... 1.04 on Gaussianised cloud; registered degree tests missed | MEASURED (registered lane) | AU §3; REL Summary |
| codes near-linear between layers ($R^2$ 0.82-0.99; BA.1 missed narrowly); tower property | MEASURED; PROVEN | AU §3, §5 |
| sampler gains at $2^{16}$ (Kerdock 2.89, Sobol 2.13, polar 2.22, pairwise 1.53, fixed 2.07) | MEASURED-reg | RN §4.2 |
| exponents 1.045 / 1.058; PA1 holds; frame difference -0.002 | MEASURED-reg | RN Summary 1, §4.1 |
| rotated-copy unions exponent 1 | PROVEN [C][A] | RN §2 |
| best weight-independent exponent in [1.008, 1.012] (asymptotic, ensemble) | PROVEN [A] | RN §2 |
| finite-range slope ≥ ~1.04 allowed by the bound over $2^8$-$2^{18}$ | arithmetic on PROVEN bound + MEASURED spectrum | RN §4.1 |
| design gain limits 2.09/2.36/3.15 vs measured 1.93/2.39/3.04; 512 x 64 bands fail | PROVEN [A], proof partly checked; MEASURED-reg | RN Summary 4, §2 |
| ceiling ~10-19x (estimate); 7-design 87x budget | HEURISTIC; PROVEN | RN Summary 4, §2 |
| point-rule barrier $(c/2)/N$ up to $N \sim n^r/r!$; absolute $1/(4\pi^2 N)$ | PROVEN [C], audited and repaired [A] | PI Summary 5, §5 |
| even share > degree 2: 0.08 to 0.26 | MEASURED-exp (2 nets/width) | PI §5 |
| unit output excess kurtosis 6.9-9.1; adaptive/nonlinear open | MEASURED-exp; PROVEN (surrogate) | PI §5 |
| determinism free on random weights | PROVEN (existential) | RN Summary 3; UE Summary; HM Summary |
| multilevel $\Omega(n/\log^2 n)$; 0.99 at $256 \times 32$; 1.21-2.43 at $L = n$ (ideal, setup excluded); "pays at depths in the hundreds" | PROVEN UNDER cost hypotheses; MEASURED-reg; HEURISTIC | UE Summary; BB Summary 8; RN Summary 6 |
| pre-integration: line ≈ 1 point | MEASURED-exp (equal sample counts, post hoc) | PI Summary 2 |
| pre-integration: 3,469 passes; loses 21-1,410x | MEASURED-reg | PI Summary 1, 3 |
| branch-and-bound deductive estimate never beats RQMC; centre-point wins 4-18x in 4/24 runs at width 3 | MEASURED-reg | UE Summary |
| one ReLU layer: exact code beats RQMC 92-170x at width 3, loses ~270x at width 4 | MEASURED | ND §6 |
| $8 \times 256$: certified code 23-106x behind RQMC; 1.3-2.2e5 regions; RQMCJ 3-15x | MEASURED-reg | ND Summary |
| hybrid H1 parity 1.00-1.03x RQMC at budget, 0.86-0.95x at 1e4; residual share $k^{-0.25}$, $k^{-0.09}$ | registered design, scored post hoc; MEASURED-exp | FA Summary 3, §4.3, §5 |
| certified-linear pieces survive only at $l = 31$ | MEASURED-exp | LOG 16:17 |
| noisy depth-8 hybrid 1.2-9.9x; depth 32 none | MEASURED-reg | AN Summary |
| "unconditional lower bound = super-linear time lower bound" | HEURISTIC | SYN §2; AU §8; UE §3.3 |
| Phase-1 board account (Appendix D) | INFERRED / VERIFIED in part | PB Verdict, Key numbers |

## Appendix C. Theorem provenance

[C] = the lane author (Claude), [A] = the co-prover gpt-6-astra. No proof below has been checked by a human (D9).

| result | author | what was checked | source |
|---|---|---|---|
| Remark 1 (exponent under ARC's law, uniform) | [A] round 3, eq. 60; same exponent as [C]'s arithmetic | elementary; proof given in section 3.2 | AU §2.5 |
| pricing identity (A2) | [C]; a proof step corrected and strengthened by [A] | [A] audit round 2 | AU §2.1-2.2 |
| one Gaussianisation leaves an unremovable error | [A] | constants checked numerically by [C] | BB 10; AU §2.4 |
| Gaussian-recursion gain bounded (~470) under $H_R$ | [A] | not stated; $H_R$ is a CONJECTURE (pointwise version false), tested once; the 2n-pass cost model is generous | BB 10 |
| exact pricing of point sets; rotated unions exponent 1 | [C][A] | joint | RN §2 |
| black-box exponent $[1 + 2/(n-1), 1 + 3/(n-1)]$ | [A] round 2 | not stated per step | RN §2 |
| design-gain limits 2.09/2.36/3.15 | [A] round 2 | [C] checked "its structure and its agreement with the data, not every step" | RN Summary 4 |
| black-box ceiling | [A] power form; [C] harmonic form | | RN §2 |
| point-rule barrier $(c/2)/N$ | [C] | audited and repaired by [A] | PI §5 |
| multilevel $\Omega(n/\log^2 n)$ | earlier lane (unrestricted estimators) | under layer-wise cost hypotheses | UE Summary |
| general | | AU: "the astra constants I used were rechecked as listed in PROVENANCE.md; some remainders and constants were not" | AU §9 |

## Appendix D. The public Phase-1 board (decisions D3, D11; marked for deletion from the paper)

The board's #1 entry has raw final-layer MSE 3.63e-8 at 51% of the budget: 17.9x below the full-budget MC reference and
35.2x better than plain MC at equal charged cost. It looked inconsistent with our 2-3x samplers. <!-- PB Key numbers -->
A read-only investigation of the public record found that the meter explains little (the run is 93% metered). Its
likely explanation (INFERRED for the final run; the mechanism VERIFIED for earlier runs of 5-6 August) is fitting to
the 50 public MLPs, using the per-MLP errors that every submission page publishes. The organisers state that fitting
the public MLPs "is allowed, but the resulting performance is unlikely to generalize to the post-Phase 1 private
re-evaluation" (forum 18125). So this is an account of the score, not a charge of rule-breaking. The same entrant's
unfitted runs score 2.1-2.3e-7, about 6x better than plain MC at equal charged cost; published Kerdock-cubature
write-ups report 5.3-7.1x. The investigation splits that ~6x into 2.4-2.9x from the design, which matches our Kerdock
2.89x at equal passes, and about 2x from cheaper points (fast Walsh-Hadamard first layer, antithetic sharing, dropped
dead units). <!-- PB Verdict, Rules, Accounting --> Board entries #2-#5 are 8.9-11.4x better than plain MC at equal
charged cost, above that ~6x, and were not tested for public-set fitting; we have no explanation for them.
<!-- PB Board --> The Phase-1 private re-evaluation on fresh MLPs (~15 Nov) would settle both. <!-- PB Accounting -->

## Referee notes not addressed

- Proofs appendix with human-checked proofs (referee 2): only Remark 1's proof is included. The others need a human
  checker and are decision D9; Appendix C states provenance instead.
- Bootstrap CIs over nets and scrambles for Tables 1-3 and 5 (referee 2, minor): needs reruns of the scorers on saved
  outputs; not done in a text-only revision. Extrapolated points are marked in tables and text.
- Convergence check for the $L/n^2$ fit (referee 2, minor): not run; the claim is kept only as a post hoc observation
  in section 3.3, not as a law.
- One K = 3 variant across the ladder, and k4 at $256 \times 32$ (referee 2): need runs (D10). Table 2 footnotes the mix.
- Reporting every window under both meters (referee 2, minor): the contest-meter cost exists only for the scale mode
  and the Phase-2 order 3; section 2 states that windows below ~3x are meter-dependent instead.
- Related-work verification (referee 2): the added references are flagged ‡ and unverified; none was checked against
  the paper, including arXiv:2605.05179 v2.
- Referee 2's proposed cut of sections 3.5 (now 4) and 3.6 to an appendix table: partly done (they are section 4,
  "supporting"); a full move waits on D7 and D8.
- "Why it matters" framing (referee 2): left as a placeholder for Kelvin (D4); only the stress-test sentence was added.
- Figure 1 regeneration without the single-net k3fa point (referee 1): flagged in the text, figure not regenerated.
- Referee 1's figure "about 30x" for k3f above RQMC's end: the text uses AU's per-net 7-40x (median 22x), which is the
  registered number; the 30x reading of the plot was not reproduced.

## What this needs to become a paper

1. Kelvin's decisions D1-D12, above all D7 (matching or beating), D8 (thesis and cuts), D9 (proof checking), D4
   (framing), and the third-party ones (D3, D11, D12).
2. Human-checked proofs of Remark 1, the black-box exponent, the rotated-design exponent-1 result, the design limits
   and the $(c/2)/N$ barrier, with all symbols defined, in an appendix.
3. Runs (D10): one K = 3 variant across the ladder, k4 at $256 \times 32$, bootstrap CIs over nets and scrambles.
4. Verified bibliography, including the finite-width and signal-propagation literature, and a paragraph saying which of
   our findings that literature already predicts.
5. A regenerated Figure 1, and a figure for the ladder (Table 2) and the Phase-2 control.
6. A release of code, frozen predictions and their hashes.
7. A fresh referee pass on this v2, since AU's and SM's final texts and this revision were not re-reviewed.
