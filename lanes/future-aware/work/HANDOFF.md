# future-aware HANDOFF (updated 20:00Z, 2 Nov 2026; update before ending a turn)

Lane: future-aware (MATS, target M1) for main (opus-mats); bead pool-ttdzrk.14 (open leaf: .18 Amendment 1, close
after review round 5). Brief: test future-aware extensions of ARC's layer-wise estimators at 256 x 32 and along
L = n/8 at equal compute (backward pass counted) vs RQMC / multilevel / ARC K = 2; extend arc-update's Theorem A or say
precisely why not.
Rules: labels; PREREG hashed before scored runs; CPU nice 19 + ionice -c3, <= 3 heavy processes; kill by PID only;
trash-put only; Write tool for files; no AI credit; 3-5 line notes to main; never message Kelvin or anyone else;
review by gpt-6-astra via codex-any (check the "model:" line; no fallback).

## State (20:00Z)
- All runs finished (Part 1, post hoc H1/guard/order-4, Amendment 1 n = 512 nets 500-502, n = 512 relevance spectra,
  corrected mixture runs). No processes of this lane are running except GPT-6 review round 5 (review/run_review_r5.sh
  -> review/review_gpt6_r5.raw, started 19:59:43Z, model line gpt-6-astra checked), which verifies the additions made
  after round 4: section 4.5 (n = 512), the n = 512 relevance spectra, section 5's corrected mixture paragraph.
- Next: extract round 5's answer (last "codex" line to "tokens used") to review/review_gpt6_r5.md, apply fixes, add a
  round-5 line to section 8, record the final sha, close leaf .18 (plan done with a path), note to main (3-5 lines).
- Then: propose one bounded next task to main (none is running).
## Findings (details in future-aware.md)
Negative for the tested methods at n = 64-512: future directions beat PCA (median 2.0-2.9x at k = n/4 in the recursion)
but the needed dimension grows with n (first-layer participation ratio 17.5, 33.3, 67, 128 at n = 64-512; top n/4 hold
~80% at every width); particles lose 45-250x; D1 window 2.4-3.0x hypothetical, 1.75-2.2x with the K = 2 pilot,
0.5-0.7x with the dense direction extraction used; at 512 its n/4 version fails numerically and the n/8 version gives
1.05x hypothetical; ARC's K = 2 falls below RQMC at 512 (0.84x) and k3/k2 drops to 2.95; hybrid near unity (direct
scoring); order-4 needs the third cumulant on about half the directions; fitted Gaussian mixtures recover a falling
share of the joint law's gain (0.78, 0.69, 0.54 at n = 64-256).
