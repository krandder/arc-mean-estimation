# Cumulant ambiguity: what order-d layer statistics can and cannot pin down (random He-ReLU MLPs)

Lane cumulant-ambiguity, bead pool-ttdzrk.19, 2026-11-03. Saved by main from the lane's final message (the lane could not
write report files). PROVEN = checked by co-prover gpt-6-astra (review/review_r1_answer.md, review_r2_answer.md);
MEASURED = runs listed at the end; HEURISTIC / CONJECTURE = reading, not proven.

## TL;DR
1. Exact internal statistics nearly pin down the mean. If the true order-<=d moments of every hidden layer are known, the
   remaining ambiguity is at most a 1D ReLU moment problem at the last pre-activation (PROVEN); for a Gaussian
   pre-activation about 1.69/d sd (PROVEN). Depth matters only through that 1D law; parity constructions defeat
   input-only matching, not this oracle.
2. The worst case over all consistent laws is large but irrelevant to ARC: one step can move a next-layer mean by
   Gamma_d(Gauss) = 0.86 sd at d=2-3, 0.36 sd at d=4-5, any width (PROVEN); over depth at n=4 about 1 sd (MEASURED);
   ARC's actual total error is 0.01-0.03 sd, 14-30x smaller, so this framing cannot carry a negative.
3. Typical case (the crux): on true layer laws, ARC's per-step closure error explains the ladder at L=n/8 (MEASURED).
   Per-step error of a next-layer mean ~ c_K(l/n)/n; summed over L=n/8 steps it is width-independent: ~1.6e-3, 2.5e-4,
   2.3e-5 for K=2,3,4 (ARC's ladder ~1e-3, 1.4-2.5e-4, 3.4e-5 at n=32). At L=n/8 the full recursion is 1.0-2.2x the
   per-step sum (no amplification). Each order divides per-step error by a roughly width-independent factor (~6-8, then
   ~10) while each order costs ~n times more: precision exponent gamma ~ log q / log n -> 0. Higher cumulants and
   per-step error grow with l/n. At L/n >= 1/4 the recursion is 5-300x above the per-step sum; K=3 diverges at 16x8.
4. For Kelvin's conjecture: the oracle form is false; the binding constraint is the typical per-step closure error,
   which does not worsen with width at fixed L/n but improves only by a constant per order while cost grows ~n per order.
   A Gaussian-promise lower bound (co-prover S5) is the open theorem.

## 1. Setup and correction
h_0 = x ~ N(0,I), h_l = relu(W_l h_{l-1}), W iid N(0,2/n), no bias; output = linear readout of h_L. "Cumulants agree at
every layer up to the output yet means differ" is impossible: the output mean is linear in the order-1 moment of the last
activation layer (PROVEN, Claim 0), so "every layer" stops at h_{L-1}. Classes: oracle (true order-<=d moments of
h_0..h_{L-1}); input-only (worst-case error >= gap(input)/2 over input laws, PROVEN Claim 3, not under the Gaussian
promise); closure/propagation (ARC's kprop).

## 2. Oracle class
- gap(all) <= gap(last) <= sum_i |a_i| Gamma_d(mu_i), mu_i = law of last pre-activation t_i (PROVEN).
- Gamma_d -> 0 for every fixed net (Gaussian-type tails, moment-determinate) (PROVEN).
- Gaussian: Gamma_d/sd(relu T) = 0.856 (d=2,3), 0.362 (d=4,5), ~1.686/d large d (PROVEN); equals the network gap at L=1.
- No general lower bound gap(all) >= c Gamma_d (counterexample, width 2 depth 2) (PROVEN).
- Weight-averaged kurtosis of T_L = 3(1+2/n)(1+5/n)^(L-1); symmetric law Gamma_4 = (sqrt v/2)(1 - kurtosis^-1/2) (PROVEN);
  fixed-weight excess kurtosis grows ~ l/n (HEURISTIC).
- n=4 (finite-support LP, lower bounds): all/input = 0.60/1.03 sd at L=2, d=2; narrow deep nets collapse, gap 0.
- Parity (127-wise law) matches only input statistics; the oracle detects it if the parity is the last pre-activation.

## 3. Worst-case closure ambiguity
- First step: E relu(w.x) ranges over exactly Gamma_d(N(0,|w|^2)) at any width; minimax error half that (PROVEN).
- First hidden layer law is determined by its d>=2 moments, so the Bayes-optimal first step is exact (PROVEN, S5).
- gap(all) <= gap(input) <= prop (exact range of all consistent order-d closures) (PROVEN); no prop <= C input.
- n=4, L=2, d=2: prop 1.05 sd vs input 1.03 sd (unit); 2.14 vs 1.90 sd (readout).
- ARC nMSE along L=n/8: 1e-3/2e-4/9e-5 (K=2/3/4) = rms 0.03/0.014/0.009 sd vs worst-case first-step half-spread
  0.43/0.43/0.18 sd (14-30x). Caveat: prop LP values are lower bounds (co-prover r2).

## 4. Typical case (MEASURED)
Method: true layer laws from 2^20 Gaussian inputs, separate streams for moments and truth (truth noise subtracted).
me1d.py: 1D reduction (Gaussian = ARC's K=2 mean step, Edgeworth K=3,4, max-ent K=4); matches ARC's tensor step on 16x2
(1.4e-3/2.5e-4/2.9e-5 vs 1.6e-3/3.1e-4/4.6e-5). tc.py: ARC's mlp_kprop one step, full recursion, cut experiment
(e(c) = final error starting from true cumulants at layer c).

Per-step error, 1D reduction (mean over steps, median of 3 nets):
| n x L | excess kurtosis first/last | K=2 | K=3 | K=4 Edgeworth | K=4 max-ent | sum K=2/3/4 |
|---|---|---|---|---|---|---|
| 32x4 | 0.28/0.65 | 6.0e-4 | 7.9e-5 | 7.4e-6 | 2.3e-5 | 1.8e-3/2.4e-4/2.2e-5 |
| 64x8 | 0.13/0.73 | 2.3e-4 | 3.7e-5 | 3.2e-6 | 1.0e-5 | 1.6e-3/2.6e-4/2.3e-5 |
| 128x16 | 0.07/0.64 | 1.0e-4 | 1.9e-5 | 1.6e-6 | 4.2e-6 | 1.6e-3/2.9e-4/2.4e-5 |
| 32x32 | 0.28/1.47 | 9.9e-4 | 1.2e-4 | 3.9e-5 | 3.7e-5 | 3.1e-2/3.8e-3/1.2e-3 |
n x per-step at l/n=1/8: K=2 ~0.02, K=3 0.003-0.005, K=4 3-6e-4. Per-order factor 0.13-0.18 (2->3), ~0.09 (3->4).
2^20 -> 2^22 samples: K=2,3 change <5%, K=4 30% (near noise floor at n>=64). Max-ent K=4 2-3x worse than Edgeworth.
n=128 layers 1->15: excess kurtosis 0.07->0.64, K=2 error 1.7e-5->1.4e-4.

ARC recursion vs per-step sum (final nMSE, median 3 nets):
| n x L | K | per-step sum | e(c=0) | e(c=L/2) | last step |
|---|---|---|---|---|---|
| 32x4 | 2 | 1.9e-3 | 2.2e-3 | 1.5e-3 | 9.1e-4 |
| 32x4 | 3 | 2.6e-4 | 5.8e-4 | 1.8e-4 | 1.3e-4 |
| 32x4 | 4 | 2.8e-5 | 2.9e-5 | 2.9e-5 | 1.7e-5 |
| 64x8 | 2 | 1.6e-3 | 2.0e-3 | 1.1e-3 | 3.5e-4 |
| 64x8 | 3 | 2.6e-4 | 2.3e-4 | 1.6e-4 | 7.4e-5 |
| 128x16 | 2 | 1.6e-3 | 2.0e-3 | 1.4e-3 | 1.3e-4 |
| 128x16 (2^18) | 3 | 2.4e-4 | 2.7e-4 | - | - |
| 32x8 | 2 | 8.0e-3 | 5.9e-3 | 5.3e-3 | 2.1e-3 |
| 32x8 | 3 | 1.3e-3 | 6.3e-3 | 1.5e-3 | 2.8e-4 |
| 32x8 | 4 | 2.0e-4 | 1.4e-3 | 1.1e-3 | 7.2e-5 |
| 16x8 | 3 | 4.8e-3 | 1.6 (diverges) | 0.29 | 7.4e-4 |
At L=n/8 recursion = 1.0-2.2x per-step sum. At L/n >= 1/4 amplification of mis-propagated higher cumulants.
Not explained (HEURISTIC): ARC's 2->3 ratio rises 0.12->0.24 over n=32->256 (ours 0.13-0.18; possibly factorised
k3f/k3fa); ARC's K=4 rung at n=64-128 (9e-5) ~4x our per-step sum (64x8 K=4 cut pending).

## 5. Status of the conjecture
- Oracle form: FALSE (PROVEN).
- Worst-case closure form: TRUE but vacuous for ARC (~1 sd, 14-30x ARC's error).
- Typical form: OPEN, the crux. CONJECTURE: no order-d local rule beats c_K(l/n)/n by more than a constant; then every
  such hierarchy's precision exponent -> 0 along L = alpha n.

## Files
lw.py (layer-wise LP), oned_bound.py and gamma1d.py (1D Gamma_d), ps.py (per-step/sequential ambiguity), me1d.py (1D
typical per-step), tc.py (ARC step, recursion, cut), anal.py and anal_tc.py (tables), runs/*.jsonl (runs/*_prefix.jsonl,
runs/n4.jsonl predate the round-1 fix), review/ (co-prover rounds 1-2). gsweep.py (1D sweep n=8-256) not run.
