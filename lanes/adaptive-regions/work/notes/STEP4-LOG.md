# Step 4 log (learned / oracle linear experts), newest last. MEASURED (exploratory) unless marked.

- 16:25-17:05Z gate-pattern composed experts (scratch/step4b.py; spec before SPEC-learned-experts.md): Var(f-g)/Var f at
  the input, p_deep = 2, flat from 1 to 1,024 input zones: 32x4 0.50-0.71, 64x8 0.64-0.80, 128x16 0.93-1.29, 256x32
  0.96-1.28 (2 nets each). Unbiased control-variate estimate ties MC, loses to RQMC 2-4x at equal compute with training
  charged; model-only biased (nMSE 0.07-0.5). More deep zones (p_deep 6, 10) make the input leftover worse (> 1).
- 16:25-17:15Z centroid zones, freely regressed (scratch/step4.py, 256x32 net 200, 16k paths): pointwise nMSE from
  h_l: 0.013 (l=31), 0.016 (30), 0.025 (28), 0.047 (24), 0.11 (16), 0.22 (8), 0.74 (1), 0.92 (input) at K = 1;
  K = 16 slightly better; K = 256 overfits. Landing approximations 30->31: 1.3e-5 / 5.4e-5 nMSE; 0->1: 0.11 / 1.5e-4.
  Mixture closure from an oracle start at l = 24 (sampling moment matching): nMSE 1.2e-3, 2.7e-4, 1.0e-4, 1.2e-4 at
  K = 1, 4, 16, 64 (saturates near the 16k-path start's own error).
- 16:35-16:50Z GMM mixture of experts (lib/gmoe.py) and population trainer (lib/popmoe.py), dev nets 9500: relayed to
  main 16:50Z (population-mean errors 0.45-1.5 per-sample, 0.56 trained at 64x8; N(0,I) worse than MC on its batch).
- 16:58Z SPEC v1+A1+A2 hashed (61790d5b); lib/lmle.py; T1-T5 pass after the pointwise-MC propagation fix
  (logs/test_lmle.log); component-level product fusion fails T2 (1.21) by construction; forced splits err 0.07 (T2).
- 17:20Z dev 32x4 seed 9601 (K=8, d=16): held-out output population-mean error 0.18/0.17/0.12 (per-sample) vs
  0.28/0.27/0.27 (population-trained, overfits 19 populations); 68/95% coverage 1.00/1.00 vs 0.67/0.89; estimand
  nMSE 1.3e-2 / 7.7e-3.
- 17:30Z A3 oracle ceiling 32x4 seed 9611 (exact local Jacobians at K K-means centres, Gaussian gates): estimand nMSE
  d=16: 1.9/1.1/0.35/0.18/0.22, d=32: 1.9/1.6/0.59/0.63/0.20 at K = 1/4/16/64/256; integration error 0-0.016 (one
  0.075) vs approximation 0.16-6; additivity exact.
- 17:44Z hard-cell oracle 32x4 seed 9611 (scratch/step4h.py): 65,470/60,514/44,210/28,811 distinct layer patterns among
  65,536 paths; P = 1..4,096 kept patterns: nMSE 1.93; all patterns (model = net): 1.5e-3 = single-Gaussian re-fit.
- 17:45-17:50Z 64x8 oracle (seed 9612): d=16: 3.6/2.2/1.5/.. ; d=32: K=16 1.29, K=64 1.04, K=256 0.37; d=64 running.
- 17:50Z new rules from main: advice (training) free, held-out populations only, mixtures of expert-indexed components
  (never one Gaussian), focus 32x4 seed 9611, report every ~45 min.
- 18:00Z big-K soft oracle, 32x4 seed 9611, d = 32, 2^17 pilot (scratch/step4c.py): N(0,I) estimand nMSE 0.48 / 0.29 /
  0.28 at K = 16 / 64 / 256; its mixture-rule limit (exact integral of the pointwise model) 0.41 / 0.17 / 0.10; K = 1,024
  and 4,096 runs died (memory; fixed later, not rerun).
- 18:20-19:00Z fusion rules: tempered gPoE (fuse_tempered) and then Kelvin's final plain PoE with learned,
  input-dependent diagonal variances (precision = exp(-logsig) beta^cgate), trained by the fused NLL. Toys pass
  (logs/test_fusion.log, logs/test_poe.log); T1-T5 pass for gpoe, mix, tgpoe, poe.
- 19:00Z A4 full bumps, K = 16, advice accounting, held-out populations (scratch/step4f.py): leftover 0.39; model-only
  error vs MC at the same estimation compute (520 passes): 0.28 vs 4.6e-5 (s=0.1), 0.16 vs 3.8e-4 (0.3), 4.8e-2 vs
  1.1e-3 (0.6), 6.0e-3 vs 1.8e-3 (0.9), 4.5e-4 vs 1.9e-3 (N(0,I), RQMC ~4-5e-4 there); control variate 3-6x worse
  than MC at equal cost (g costs ~8 passes per evaluation). RQMC slopes on these held-out populations over N = 16-1,024:
  1.21-1.34.
- 19:15Z full-bump K >= 64 stopped (closed form costs ~32 passes per bump at d = 32); isotropic bumps (O(d) closed form,
  8.8 passes at K = 16) sweep K = 16-4,096 launched; A5 dev (plain PoE, K = 16) running at ~6-14 s per step.
