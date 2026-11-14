## 6. What the chain explains of what we measured, and what it does not (Part D)

| measured (lane) | value | chain / theory | status |
|---|---|---|---|
| cloud size: two noise replicas at angle 2.23 X^{-2/3} (stationary lane, A3; nets measured/law 0.87, range 0.72-1.24) | 0.87 | exact chain: median delta/delta*(Q) {{MEDS}}; per net (Part C) {{PCSIZE}} | explained: the angle is the noisy-kernel fixed point at each net's radius; nets scatter because radii do (CV 0.68) |
| cloud 5-8x above the Lyapunov formula (stationary lane), "1/k shape" (numerics lane) | 5-8x, 1/k | the trace is 2 delta*(Q) per unit radius (explained); the shape is not 1/k: PR_C = n theta*/pi ~ n^{2/3}, radius dependent (2.4) | trace explained; the 1/k shape is refuted globally; the top-k eigenvalue ratios (k = 2-8) are not computed here |
| births: 0.48-0.64 sqrt(n) gate flips per layer (stationary lane) | 0.48-0.64 | exact chain 0.62-0.63 sqrt(n), mean field n arccos(Q/(Q+1))/pi = 0.59 sqrt(n) (numerics lane) | explained in law; per-net spread from the radius (births ~ (n/Q)^{1/2}) |
| interaction order: direction 1.72 -> 3.97, h_0 1.41 -> 3.87 (n = 8 -> 256; numerics lane) | slope 0.17-0.26 | mechanism: a lone injection decays algebraically while the cloud relaxes on tau, D_u -> 2.99 Q^{1/6} (numerics lane); annealed chain D_u 16-28% above that, nets 8-15% (numerics lane); {{DBLOCK}} | explained in mechanism and scaling (Q^{1/6}); the level within 10-30% |
| flat low-order shares: C(t) = 0.16-0.18, 0.36-0.38, 0.60-0.64 at t = 0.25, 0.5, 0.75, S1 0.59-0.66, flat in n (input-bits) | flat | closure 1 - (1 - t)^{2/3} ([A] input-bits r1): 0.175, 0.370, 0.603, S1 = 2/3; exact chain {{CT}} | {{CTSTAT}} |
| antithetic noise: even share 0.23-0.27 (gain 1.9-2.2) | 0.23-0.27 | closure 0.206 (gain 2.42); exact chain c = -1: {{ANTI}} | {{ANTISTAT}} |
| input regime 256 x 32: amplitude/direction split 0.49/0.47 (per-net medians), 0.60/0.36 (annealed chain; input-bits) | | the gap is annealed vs quenched: the chain's ratio of means weights large-gain nets; in log form the radius share matches the kernel within 4% (4.2) | explained (as an averaging effect); the per-net median split is not a replica quantity |
| 3n/l decay of differing gates (input-bits: 128, 100, 74, 51, 33, 18, 11, 5 at layers 1-128, n = 256) | | exact chain E[n arccos(rho)/pi] = 128, 101.6, 85.8, 66.7, 47.1, 30.1, 17.5, 9.3, 4.6 at l = 0, 1, 2, 4, 8, 16, 32, 64, 128 (gates of layer l + 1; `results/partD_gates.json`); kernel 128, 101.6, 85.9, 67.0, 47.6, 30.8, 18.4, 10.3, 5.5 | explained (kernel; the chain adds the finite-width deficit seen in the nets at depth) |
| input regime: the input's direction lives in ~10 effective directions at 256 x 32 (input-bits) | ~10 | vertex law PR(l) ~ 1.5 n/l: 12.1 at l = 32 (exact chain), 10.3 (recursion) | explained (new) |

What it does not explain: which directions carry the relevance in a given net (section 7); per-net ratios beyond what the
radius fixes (Part C residuals); the top-k shape of the stationary cloud's spectrum (only its participation ratio and
third moment are computed); and anything about estimators, which is the relevance lane's and the estimator lanes' work.
