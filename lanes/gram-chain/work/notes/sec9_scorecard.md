## 9. Pre-registration scorecard

Registrations and hashes: `PREREG.md`, `prereg_hashes.txt`, copies `coprover/PREREG_*_as_hashed.md`. Scorers
`scratch/score_A.py`, `score_B.py`, `score_C.py`; results in `results/part{A,B,C}_scores.json`.

| id | prediction (short) | result |
|---|---|---|
| PA1 | SD(ell) n^{1/3} -> 1.887: in [1.70, 2.05] at n = 1024, non-decreasing | {{PA1}} |
| PA2 | E[ell^2 | q] n^{2/3} within 25% of the limit per radius bin, n = 1024 | {{PA2}} |
| PA3 | median delta/delta* in [0.97, 1.03] at n >= 64; mean ratio - 1 > 0 scaling like n^{-2/3} | {{PA3}} |
| PA4 | SD(delta/delta*) n^{1/3} in [1.5, 2.4], flat within 1.4x over n = 64-1024 | {{PA4}} |
| PA5 | sharing curves: coordinate within 0.03 of 1 - (1 - t)^{2/3}; correlation within 0.02 of it; per-layer within 0.05; antithetic within 10% of 2^{2/3} | {{PA5}} |
| PA6 | 1/e lags: log q in [0.8n, 3.2n], ratio in [0.5, 2] x (Q + 1), angle in [0.5, 2] x 1.49 Q^{1/3} | {{PA6}} |
| PA7 | triangle spread within 25% of 1.46 sqrt(2/PR) | {{PA7}} |
| PA8 | cloud moments match a 1/k spectrum (r3 and PR within 25%) | {{PA8}} |
| PA9 (A1) | PR_w slope 256 -> 1024 above 0.50 (n^{2/3}) or below (1/k) | {{PA9}} |
| PB1 | closed relevance: half-life and area within 30% of mean field | {{PB1}} |
| PB2 | total relevance: half-life within 30%, value at 4 T* within 2x | {{PB2}} |
| PB3 | closed and total PR at t = 1, 2, 4 within 1.5x of [1/PR_C + 2t/n]^{-1} | {{PB3}} |
| PB4 | log|a| relevance above the direction's at every t >= 8, and > 0.2 at t = n/2 | {{PB4}} |
| PB5 | perturbation survival within 30% of mean field (eps = 0.1, 0.3); tangent survival >= 2x finite | {{PB5}} |
| PB6 | input-cloud PR within 20% of the vertex recursion | hit (8 of 8; within 1-17%) |
| PB7 | radius share of log-amplitude within 25% of the kernel, 256 x 32 | hit (7 of 7; within 4%) |
| PB8 | extinction at 8 x 256 equals (1 - 2^-8)^l within 3 SE | hit (code check) |
| PC1 | across-net CV of the cloud size within 30% of the chain's, rising to 0.68 | {{PC1}} |
| PC2 | chain's annealed cloud size within 2.5 SE of the nets' mean | {{PC2}} |
| PC3 | normalising by delta*(Qbar) at least halves the across-net CV | {{PC3}} |
| PC4 | median per-net PR within 25% of the chain's PR_w; per-net PR CV < 0.35 | {{PC4}} |
| PC5 | per-net V_P(8) tracks the net's radius (Spearman > 0.5); within 0.12 of the per-radius mean field | {{PC5}} |
| PC6 | the chain's annealed V_P is below the nets' median at t = 4, 8 | {{PC6}} |
| PC7 (C1) | per-net radial share within 30% of rho(q); Spearman with the radius > 0.6 | {{PC7}} |
{{SCORETOTAL}}
