# gram-chain lane: pre-registration

Each part is hashed (sha256 and UTC time in `prereg_hashes.txt`) before any of its runs. Theory: `FORMAL.md` v1 (frozen
21:14:08Z). Library `lib/gc2.py` (tests pass, `logs/test_gc2.log`). Python /home/agent/.venvs/arc-noisy/bin/python,
nice 19, ionice -c3, one BLAS thread, at most 2-3 processes.

## Part A: the stationary law of the normalised Gram (exact chain, sigma = 1)

Disclosure: before this registration I ran exploratory chains (`scratch/quick_r2.py`, `quick_r3.py`,
`quick_radial_tail.py`) at n = 16, 64, 256 (and 64 for the radial tail): median delta/delta*(Q) 1.04, 0.99, 1.00;
SD 0.76, 0.47, 0.28; SD(ell) n^{1/3} 1.52, 1.70, 1.82; triangle range/mean 0.75, 0.56, 0.39; E[ell^2|q] n^{2/3} by q-bin
at n = 64. Predictions PA3, PA4 and PA7 were therefore informed by data at n <= 256; n = 512 and 1024 are unseen.
PA1, PA2 come from the limiting SDE (FORMAL 2.2), PA5 from the mean field, PA6 from FORMAL 2.5.

Runs (`scratch/partA.py`, one JSON per run in `runs/A_*.json`). Start: stationary radius (exact scalar chain, 20 n
steps from the inverse-gamma law), all replicas identical; burn-in 6n layers (8n for R = 2 with c = 0); then T = 8n
recorded layers, samples every n/8 layers (all chains), plus contiguous traces of 4n layers on 200 chains for
autocorrelations. Widths n = 8, 16, 32, 64, 128, 256, 512, 1024. Chains P = 8000 (n <= 64), 4000 (128), 2000 (256),
1000 (512), 500 (1024). Seeds [2026, n, mode]. Error bars: bootstrap over chains (B = 200), so time correlation within
a chain is respected.
- A-r2: R = 2, independent noise. Records q = sqrt(G11 G22)/n, delta, ell.
- A-share: R = 2 with (i) Gaussian noise correlation c = t, (ii) per-coordinate Bernoulli sharing with probability t,
  (iii) per-layer Bernoulli sharing with probability t, for t in {0.25, 0.5, 0.75, 0.9, 0.97, 0.99}; plus c = -1
  (antithetic). n = 16, 64, 256, 1024. Statistic C(t) = 1 - E delta_t / E delta_0 (E delta_0 from A-r2, same n).
- A-r3: R = 3 independent; A-r4: R = 4 independent (tr C_u, tr C_u^2 of the direction cloud u = h/|h|);
  A-r6: R = 6 independent (tr C_u^3), n <= 256 only; moments normalised per chain by delta*_MF(q-bar)^m and also raw.

Statistics and predictions (hit = inside the band):
- PA1 (radius ratio scale): SD(ell) n^{1/3} at n = 1024 in [1.70, 2.05] (limit 1.89) and non-decreasing in n from
  n = 64 to 1024 within 2 bootstrap SE.
- PA2 (radius ratio given radius): at n = 1024, E[ell^2 | q-bin] n^{2/3} within 25% of the limiting-SDE values 2.74,
  3.30, 3.73, 4.14, 4.49, 4.75, 5.13 on bins [0, .3), [.3, .6), [.6, 1.2), [1.2, 2.5), [2.5, 5), [5, 10), [10, inf), in
  every bin with >= 500 samples.
- PA3 (angle level): median of delta/delta*_MF(q-bar n) in [0.97, 1.03] at every n >= 64 (delta*_MF: exact mean-field
  fixed point at the pair's geometric-mean radius); mean ratio - 1 > 0 at every n >= 64, and n^{2/3}(mean ratio - 1)
  varies by at most a factor 2 over n = 64-1024.
- PA4 (angle fluctuations): SD(delta/delta*_MF) n^{1/3} in [1.5, 2.4] at every n >= 64, with max/min over n = 64-1024
  at most 1.4.
- PA5 (sharing curves): coordinate sharing C(0.25), C(0.5), C(0.75) within 0.03 of 0.175, 0.370, 0.603 at n = 64, 256,
  1024; Gaussian correlation within 0.02 of coordinate sharing at every t <= 0.75 and n >= 64; per-layer Bernoulli
  sharing within 0.05 of coordinate sharing at t <= 0.75, n >= 64; antithetic: E delta(c = -1)/E delta_0 within 10% of
  2^{2/3} = 1.587 at n >= 256.
- PA6 (mixing): from the contiguous traces, the lag at which the autocorrelation of log q first drops below 1/e lies in
  [0.8 n, 3.2 n] (theory 1.6 n) at n = 64-1024; for ell in [0.5, 2] x (Q_med + 1); for delta/delta*_MF(q) in [0.5, 2] x
  1.49 Q_med^{1/3} (Q_med = 0.577 n).
- PA7 (triangle): mean (max - min)/mean of the three angles within 25% of 1.46 sqrt(2/PR_u) with PR_u = (E tr C_u)^2 /
  E tr C_u^2 from A-r4 at the same n, n = 16-1024.
- PA8 (cloud spectrum, a test of the 1/k conjecture): the radius-normalised ratio r3 = m3 m1 / m2^2 of the direction
  cloud's moments (A-r6) within 25% of the 1/k value 1.40, 1.64, 1.91, 2.21, 2.52 at n = 16, 32, 64, 128, 256; and the
  radius-normalised PR within 25% of the 1/k value 9.7, 15.2, 22.3, 30.8, 41.0, 52.6, 65.8 (n = 16 ... 1024).
Scoring: `scratch/score_A.py`, hits counted per prediction (all clauses must hold); no prediction is re-banded after
the data.

## Part B: relevance at layer l (exact chain)

Registered after Part A runs had started (r2 at n <= 32 and r4 at n <= 32 seen; no Part B data). Mean-field numbers
from `scratch/predB.py` (`results/predB_meanfield.json`, `logs/predB.log`): ratio of means over the stationary radius
law, radius frozen along each curve. Script `scratch/partB.py`; runs `runs/B_*.json`. Observable: the output direction
u = a/|a| (one exact sample of the noiseless output layer per recorded t); also log|a|. t counts the output layer.
Runs: curves at n = 16, 64, 256, 1024 (P = 8000, 8000, 4000, 1000; t <= 4n); pr at n = 16, 64, 256 (R = 8; t <= 256);
pert at n = 16, 64, 256, 1024; input at (n, L) = (256, 128), (64, 64), (8, 256) with sigma = 0, and descriptive runs at
(256, 32) and (8, 256) with sigma = 1e-3, 1e-2, 1e-1.
- PB1 (closed relevance): the first t with V_P(t) < 0.5 within +-30% of the mean field 3, 4, 6, 10 and the area
  sum_t V_P(t) within +-30% of 2.98, 4.85, 7.87, 12.74 at n = 16, 64, 256, 1024 (both clauses at n >= 64; n = 16
  reported).
- PB2 (total relevance): the first t with T_P(t) < 0.5 within +-30% of 4, 6, 9, 14; T_P at t = 15, 27, 45, 73 (4 T*_med)
  within a factor 2 of 0.063, 0.071, 0.082, 0.089 (n >= 64 scored).
- PB3 (dimension, linear regime): closed and total PR at t = 1, 2, 4 within a factor 1.5 of [1/PR_C + 2t/n]^{-1}, PR_C
  = PR_4rep of the hidden direction cloud from Part A (same n), at n = 64, 256. For t > 4 the formula is not expected to
  hold; reported.
- PB4 (radius memory): V_P for log|a| exceeds V_P for the direction at every recorded t >= 8 at n >= 64, and is > 0.2 at
  t = n/2.
- PB5 (perturbation survival, shared noise): hidden-direction survival E delta_t / E delta_0 within 30% of the mean field
  (predB, survival lists) at every recorded t where the mean field is >= 0.1, for eps = 0.1 and 0.3, n >= 64; and at
  eps = 1e-3 the survival at t = n/4 is at least 2x that at eps = 0.3 (mean field: 2.2x, 8x, 64x at n = 64, 256, 1024).
- PB6 (input-cloud dimension, sigma = 0): 4-replica PR of the direction cloud at n = 256 within 20% of the vertex
  recursion 167, 62, 19, 10.3, 5.3 at l = 1, 4, 16, 32, 64, and at n = 64 within 20% of 41.7, 15.4, 4.7 at l = 1, 4, 16.
- PB7 (what carries the input at layer l, sigma = 0, n = 256, L = 32 run as the first 32 layers of the L = 128 chain... no:
  a separate L = 32 run): E_W Var_x(log|h_l|) / E_W Var_x(log|a|) within 25% of (1/2 + C_l)/(1/2 + C_L) = 0.19, 0.30,
  0.46, 0.66, 0.85, 0.94, 0.99 at l = 1, 2, 4, 8, 16, 24, 31 (kernel C_l, C_32 = 8.55).
- PB8 (extinction, n = 8, L = 256, sigma = 0): the per-replica alive fraction within 3 SE of (1 - 2^-8)^l at l = 64, 128,
  255 (PROVEN identity; a code check).
Scoring `scratch/score_B.py`; all clauses must hold.

## Part C: annealed versus quenched on real nets (stationary, sigma = 1)

Registered 21:25Z, before any Part C run on evaluation seeds (a smoke test used seeds 9900-9901 at n = 16, M = 64,
discarded). Script `scratch/partC.py` (per-net statistics defined in its docstring), runs `runs/C_*.json`. Nets: seeds
5000-5031 at n = 8, 16, 32, 64 (32 nets), 5000-5023 at n = 128 (24), 5000-5015 at n = 256 (16); M = 256 replicas from
h = 0 at layer -8n. Chain comparators come from Part A (r4) and Part B (curves) at the same n; the mean-field per-net
curve V_P^MF(t; Q) is the predB recursion at the net's own median radius.
- PC1 (the cloud size does not self-average): across-net CV of trC_u(W) within 30% of the chain's
  sqrt(E[T^2]/(E T)^2 - 1) = sqrt(PR_4rep/PR_ratio_of_means - 1) (Part A r4) at n = 16, 32, 64, 128, 256; and the
  chain's value increases with n toward 0.68.
- PC2 (level): the chain's E_W tr C_u (Part A r4, mean of x11/2) lies within 2.5 standard errors of the nets' mean of
  trC_u(W) at every n.
- PC3 (radius hypothesis H-rad): the across-net CV of trC_u(W)/delta*_MF(Qbar(W)) is at most half the CV of trC_u(W) at
  n = 64, 128, 256.
- PC4 (the shape self-averages): median over nets of the per-net PR_u(W) within 25% of the chain's PR_4rep at every n;
  across-net CV of PR_u(W) below 0.35 at n >= 64 (it includes per-net sampling noise).
- PC5 (closed relevance per net follows the net's radius): Spearman correlation between Qbar(W) and V_P(8; W) above 0.5
  at n = 64, 128, 256; median over nets of |V_P(t; W) - V_P^MF(t; Qbar(W))| below 0.12 at t = 4 and 8, n >= 64.
- PC6 (where the annealed curve misleads): the chain's annealed V_P(t) (Part B curves, ratio of means) is below the
  median over nets of V_P(t; W) at t = 4 and 8 for n = 64 and 256.

### Amendment A1 (competing laws for the cloud's dimension; registered after r4 at n <= 128 was seen, before n = 256, 512, 1024)
gpt-6-astra round 1 (returned 21:31Z, after FORMAL v1 was frozen) predicts from the four-point balance (source 8 delta^2/n,
damping ~ n^{-1/3}) that the angular cloud's participation ratio grows like n^{2/3}, PR_w = E_W(tr C)^2 / E_W tr C^2
~ 1.0865 n^{2/3} (43.8, 69.5, 110.4 at n = 256, 512, 1024); the numerics lane's 1/k conjecture gives (log n)^2 growth
(41.0, 52.6, 65.8). Seen so far (PR_4rep, the estimator of PR_w): 10.0, 14.8, 21.7, 32.1 at n = 16, 32, 64, 128 (local
log-log slopes 0.56, 0.56, 0.56; the 1/k slopes over the same steps are 0.65, 0.55, 0.47).
- PA9: the log-log slope of PR_4rep between n = 256 and 1024 is above 0.50 (favouring the n^{2/3} law; 1/k predicts 0.34
  there) -- scored as "n^{2/3} favoured" if > 0.50 with its bootstrap 90% interval above 0.42, "1/k favoured" if < 0.50
  with the interval below 0.58, otherwise unresolved.

### Amendment C1 (registered before any Part C evaluation run; theory FORMAL v2.2 section 7.11)
- PC7 (radial share per net): with rho_rad(W) = (logQa_var/4) / (trC_a + logQa_var/4) (per-net variance of log|a| and
  trace variance of the output direction, from `scratch/partC.py`), the median over nets of
  |rho_rad(W) / rho_rad_theory(Qbar(W)/n) - 1| is below 0.3 at n = 64, 128, 256, with rho_rad_theory(q) =
  m(q)/(m(q) + 2 A q^{-2/3}) (m the closed form of FORMAL 7.1); and the Spearman correlation of rho_rad(W) with Qbar(W) is
  above 0.6 at each of these n.
