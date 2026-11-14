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
