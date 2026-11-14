# Co-prover provenance (gpt-6-astra via codex-any; "model: gpt-6-astra" checked in every raw log)

## Round 1 (independent; launched 13:22:22Z from the lemma-free STATEMENT_r1.md, sha c17ce783; exit 14:04:03Z)
- My FORMAL v1 was frozen at 13:32:08Z (sha 67d8e227, notes/formal_hashes.txt) before the answer existed; I first
  read the answer at about 14:10Z. The prompt told astra not to read work/randomness beyond the statement; its raw
  log shows one read in this directory (cat coprover/STATEMENT_r1.md) plus outbox reports, unrestricted/lib/mlmc.py,
  arc-noisy kerdock.py and anet.py, and small numerical checks of its own (piecewise-ray gate counts at n = 2, 4).
- Found by both independently: exact spectral pricing of designs (my T1-T2, astra's boxed identity); a fixed oblivious
  design matches radius-exact MC on average (my T3, astra's "single strongest statement"); the positive-weight
  even-tail lower bound (my T4 in Gegenbauer form, astra's cleaner power-series form); the antipodal cost
  A / (2 A_even); weight-derived seeds through the polar factor of W_1 (astra PROVEN UNDER primitives; my T9 identity);
  fresh randomness buys conditional unbiasedness and a replicate variance, not accuracy; Caratheodory needs compute.
- New from astra: exact annealed gate perimeters E Per{z_{l,i} > 0} = (1 - 2^-n)^{l-1}/sqrt(2 pi) including dead-region
  interfaces (my T7(b) was a heuristic); P(gate history changes) ~ (sqrt 2 n / pi)(sum beta_n^j) sqrt(delta); the
  kink-strength expansion F(delta) = D delta - (2 J_kink / (3 sqrt pi)) delta^{3/2} + o(delta^{3/2}) and Hermite tail
  O(J_kink t^{-3/2}) (my T8 heuristic, now PROVEN for fixed transversal maps); E sum_k k H_k = n exactly; the
  smoothness tail bound sum_{d>t} a_d <= m_n^2 (n - 1)/((t + 1)(t + n - 1)); Gaussian Hermite and spherical degrees
  must not be identified (one-way inequality); a 127-wise independent law fooling no width-256 homogeneous ReLU net's
  mean (off by 2x); the Kerdock aliasing formula; the mean-field statement that degrees 1-2 carry O(1/L) of the
  angular variance; a falsifiable Kerdock prediction (N E err^2 / V in [0.33, 0.50]).
- New from me (not in astra's answer): rotation variances of designs of known aliasing as a truth-free spectrum
  measurement (T1 corollary); the spherical noise-sensitivity sandwich (T6); the explicit d* thresholds at n = 256;
  the polar-frame white-box design and its bias caution (T9), confirmed by the biased polar Kerdock measurement;
  first-layer controls as degree <= 2 (T10, dev regression); the black-box seed-length statement (T5).
- Corrections astra made to me: the literal zero set {z_{l,i} = 0} contains open dead cones for l >= 2, so the object
  is the gate-set perimeter (my T7 wording); Gaussian OU noise sensitivity is a Hermite statement and bounds
  spherical tails only one way (my T6 is stated with spherical pairs, so it stands; the "gauss" NS curves in noise.py
  are Hermite statements).

## Round 2 (audit, exponents, finite-width low degrees; launched 14:06:28Z after reading round 1, exit 14:48:31Z;
model line gpt-6-astra; prompt hashed in statement_hashes.txt; read by me ~14:50Z; applied as FORMAL E2)
- Input: FORMAL v1 + E1, astra's own round 1, the partial ladder table (3 of 5 nets at 256), the noise summary, the
  tail check and PREREG. Its raw log shows reads of the named files plus lib/rnd.py and scratch/*.py (definitions), fleet skill files and one recall query; its numbers come from its own short python checks.
- Audit: T1-T3, T6, T9 correct; T4 correct with qualifications; T5 wrong at fixed n as eps -> 0 (holds at polynomial
  budgets); T7 correct at layer 1, wrong for literal later zero sets (round 1); T8 constants wrong (J/sqrt pi,
  J/(3 pi)); T10 wrong as exact redundancy; T11 too strong. All accepted.
- New from astra: fixed-width black-box exponent window [1 + 2/(n-1), 1 + 3/(n-1)] (stratification attains the
  lower end); the norm-covariance recursion and the finite-width mechanism (accumulated activation-norm fluctuations);
  E V -> 11.15 for L/sqrt n -> infinity; the limiting spectrum and design gains (2.09, 2.36, 3.15), which match the
  measured 256 x 32 values (1.93, 2.39, 3.04); Theta(1/N) for positive oblivious rules at polynomial budgets in the
  joint limit; E_1 = (m_n^2/n)||E J||_F^2; the noise slope n/E V ~ 0.72 L along L = n/8; a 512 x 64 prediction; the
  aligned-MUB bias example for relu; the open question about norm profiles.
- New from me in this round: none (I supplied measurements and questions).
