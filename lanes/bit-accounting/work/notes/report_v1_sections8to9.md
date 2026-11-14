## 6. Pre-registration scorecard (parts before phase 1)
- A1 (ARC): A1.1, A1.3, A1.5, A1.6, A1.7, A1.8, A1.9, A1.10, A1.11 hit; A1.2 missed (mis-specified: a layer-24/31
  code can beat a learned output-space code, which is not a bug, FORMAL 4.8); A1.4 missed.
- A2 (narrow-deep): A2.2 hit; A2.1 missed (3 of 6 nets have a layer >= 32 more than 0.6 bit above the one-number
  value: heavy-tailed radius, Gaussian quantiser design).
- S1: S1.2, S1.4, S1.5, S1.7 hit; S1.1, S1.3, S1.6 missed (learned sign/channel codes undertrained at 1500 steps).
- S2: S2.1 hit; S2.2, S2.3, S2.5 missed (see 4.1, 4.4).
- S3: S3.3 hit; S3.1, S3.2, S3.4, S3.5 missed (section 5).
- S4: S4.1, S4.2, S4.3 hit.
- S5-S10 (partial): S5.2, S5.3, S5.5, S6.1, S6.3, S9.1, S9.2, S10.2 hit; S5.1, S5.4, S6.2 missed; S7, S8, S10.1 pending.
- B-ARC (nets 4000, 4001; results/BARC_scores.json): BA.2 hit (sign-bit transitions within 0.03 of an MLP for every
  pair from l = 16 on); BA.1 missed (consecutive pairs from l = 20 on have linear R^2 0.91-0.997, but 16 -> 20 on net
  4001 is 0.885 and the multi-step pairs 16 -> 24 and 16 -> 32 are 0.80-0.88, with MLP gains up to 0.08); BA.3 missed
  narrowly (sign flips at rho = 0.999 grow by 2.02x and 2.29x from l = 8 to 31: gradual, but above the registered 2x).
- S11: deferred to phase 2 (plan change 02:55Z); S11 S7 reference rates are in runs/S11_*.

## 7. Process
- Plan changes by main/Kelvin during the night: small nets on a GPU first (23:05Z); Kelvin's curriculum (S3, 23:4xZ);
  shared-noise scoring (S4); convergence certificates (S5) and joint quantisation (S6, 01:3x-01:4xZ); the encoder
  chooses its bits (S7, 02:00Z, real-valued at 02:10Z) with Bernoulli and real-valued scrambling arms (S8, S9);
  simple-dynamics simulator (S10, 02:25Z); net-level controls (S11, 02:40Z); then phase 1 (02:55Z: the best curve
  per layer, one lambda-conditioned model per layer, certificates; 03:20Z: identity anchor annealed upward, the
  linear analytic reference, SNR equivalence) and Kelvin's near-identity hypothesis for phase 2 (registered P2.0).
  Each was registered before its runs; S9, S10 and the S11 spectra were stopped at 02:57Z (phase 2).
- Deviations (notes/DEVIATIONS.md): training steps cut (6000 -> 3000 -> 1500) for GPU time; two spot preemptions
  (results restored); CUDA OOM with 16 processes (jobs rerun with a memory gate); some unrestricted chains skipped for
  seeds 5001-5002; the straight-through surrogate standardised after dead codes; analysis on the monotone envelope.
- Compute: CPU at nice 19 (ARC, narrow-deep, linear codes, analyses). GPU: L4s only, one at a time until 02:55Z,
  then at most two: bitacct-1 to -4 (spot; two preempted), bitacct-5 to -9 (on-demand), $13.52 for VMs 1-6 and at
  most about $10.5 for VMs 7-9 at list price (GPU-LOG.md); cap $25 (raised from $15 at 02:55Z).
- Reviews (gpt-6-astra, model line verified each time): round 1 on FORMAL and the code (16 findings, applied in
  FORMAL 4.1-4.8 and the code). Round 2a on the phase-1 code (review/review_r2a.raw, 12 findings): the Feistel
  decoder squash and Jacobian were fixed before any Feistel run; the scorer was rewritten (conservative crossings,
  single model and best code, every error level with not-covered separated, one candidate set, pending until
  complete, KA2 relabelled empirical); the post-pass of amendment P1-A adds explorer restarts with gates inside the
  data cloud, the encoder width separated from the decoder width, a residual output-space centroid, held-out powers
  for the linear reference and gate activity; the one-model requirement (finding 5) is reported as not met
  everywhere. Round 2b on this report (review/review_r2b.raw, 9 findings): the provisional framing, the unrestricted
  exceptions, the single-model column, measured uncertainty only, counts instead of rounded percentages, the
  coverage table, softer control wording, the C5v2 convergence rule, correct source attribution and the same
  candidates for the log-linear secondary are applied; the explorer initialisation now uses pilot samples (cells
  finished before 12:28Z used evaluation samples for that initial fit only). Scorer v2 was test-run on the 12 cells
  already inspected before its first hash; each later change is hashed and logged.
  Round 2c (review/review_r2c.raw, final check after the post-pass, 'major revision' on wording): applied: R* is
  called an envelope over several models with the single model r0 beside it (median r0 - R* gaps given); the
  certificates are said to test the anchored models, not the explorer codes; the centroid result is stated as
  measured; the decoder-width attribution is softened; post-pass comparisons use the primary crossings; coverage
  is derived from the manifest (55 of 57 ReLU local cells); measured extrema replace rounded claims (prior refit up
  to 13%, 70 points above the linear reference within tolerance, linear control within 0.12 bit).
  Round 3 (review/review_r3.raw, phase 2, 'major revision'): applied: the unscrambling cost is called a
  Lagrangian-equivalent cost and split into rate and distortion; the detached-normalisation flaw of Part U is stated
  (a corrected rerun needs GPU budget); B1 rescored as registered (9/13, missed); the noisy transfers are reported
  for both fits; the code-map statistics are stated as empirical fits of the code means, with the numerical and
  noisy-code caveats (v2 rerun: scratch/p2_maps_v2.py); the ordered/chaotic contrast is softened (one tanh seed).
  Provenance: scratch/p2_identity.py and report_P2_identity.py were run before they were hashed;
  report_P2_maps.py was written after the analysis output existed (both recorded in prereg_hashes.txt).

