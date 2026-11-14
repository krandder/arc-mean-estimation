You are gpt-6-astra, co-prover on the randomness lane (round 2: audit and lemma exchange). Read-only sandbox; do not
modify files. Read in /home/agent/workspaces/mats/work/randomness: coprover/STATEMENT_r1.md (the setting),
coprover/astra_r1_answer.md (your round-1 answer, lines 1-800), FORMAL.md (my v1, frozen at 13:32Z before I read your
answer), results/ladder_table_partial.txt (MEASURED: medians [min, max] over nets of design shares and gains along
L = n/8; 8 nets per width at n = 32, 64, 128, only 3 of 5 nets so far at 256 x 32; definitions in scratch/structure.py
and scratch/ladder_table.py), results/noise_summary.txt (MEASURED noise sensitivity and gate GSA, all evaluation
nets; scratch/noise.py), runs/tail_check_n256_L32.json (no exact linear tail at 256 x 32), PREREG.md.
Label every claim PROVEN / PROVEN UNDER <hypothesis> / HEURISTIC / CONJECTURE; prefer a correct weaker statement.
Tasks:
1. Audit FORMAL v1 items T1-T11 one by one: correct / wrong (with counterexample) / needs a hypothesis. Reconcile with
   your round 1 (e.g. my T4 in Gegenbauer form with |min P_d| vs your power-series form with tau_2s; my T6 spherical
   noise-sensitivity sandwich; my T7-T8 vs your exact perimeter and kink-strength results).
2. Exponents. (a) For positive-weight rules chosen independently of W (fixed designs, Haar-randomised designs, and
   scrambled Sobol / any RQMC whose randomisation is independent of W), prove or refute: at fixed n the ensemble risk
   satisfies risk(N) >= (m_n^2 / (2N)) sum_{s: tau_2s <= 1/(2N)} b_2s, so the error-vs-N exponent on the ensemble is 1
   up to the decay of the even power tail; give the two regimes (degree d* ~ 2 log N / log n while d << n, and the
   cubature regime d >> n) and what exponent each allows, with constants at n = 256 and N = 2^8..2^18. (b) Unions of R
   independently Haar-rotated copies of one design have exponent exactly 1 (my T1 corollary): confirm. (c) What can
   and cannot be said about the exponent of scrambled Sobol in a W-dependent (polar or SVD) frame?
3. Finite-width low degrees. Measured (ladder table): the degree-1 share E_1 is 0.3-0.5 and degree-2 0.15-0.3 of the
   angular variance at L = n/8 for n = 32-256, odd share 0.57-0.63, even >= 4 share rising 0.09 -> 0.22, and every
   design gain falling with n (simplex 4.5 -> 2.0, cross-polytope 5.5 -> 2.4, scrambled Sobol at 2^14 5.3 -> 2.2 from
   n = 32 to 256), while in your mean-field kernel the degree-1-2 share is O(1/L). Identify the finite-width mechanism
   that puts ~half the angular variance in degrees <= 2 at L = n/8 (fixed-net fluctuation of the output's mean
   direction? the per-net Jacobian E_x J?), and predict its scaling along L = alpha n: does the black-box design gain
   tend to 1, to a constant, or grow? A falsifiable prediction for n = 512 at L = 64 would be ideal.
4. Measured law: the noise-sensitivity slope (mean Hermite degree) of the layer-l state is ~1 + l/2 at every width
   n = 32-256 (l <= 32), and n / V ~ 1 + L/2 along L = n/8 (noise_summary.txt). With your identity
   E sum_k k H_k = n, this says V_l ~ 2n/(l + 2) at finite width. Derive or bound this at finite width (L <= n), or
   say why it cannot hold uniformly; contrast with the infinite-width 1 - K_L ~ 9 pi^2/(2 L^2).
5. White-box. The polar frame of W_1 improved scrambled Sobol by ~1.15-1.2x at every width (medians at 2^14), the
   SVD frame by 1.75x at n = 32 and not at n >= 128; Kerdock aligned to the polar frame with only signed permutations
   was biased (nMSE x m = 19-400 on dev nets). Explain these, and say whether any W-dependent frame or cheap white-box
   structure could change the exponent (not the constant) at L = alpha n.
6. Verdict support: list the statements in FORMAL v1 + your round 1 + these that you would sign as PROVEN, and the
   single most important open question for the sampling direction.
Write everything to stdout.
