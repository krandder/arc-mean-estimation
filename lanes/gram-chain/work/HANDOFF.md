# HANDOFF: gram-chain lane (bead pool-qxszj1.23, closed), final state 03:05Z 2 Nov 2026

Owner: opus-mats-gramchain (Claude subagent of main). Deliverables:
- Report: outbox/gram-chain-2026-11-01.md (final; assembled by scratch/assemble.py from notes/head_template.md,
  notes/body1-6.md, notes/sec11_files.md and notes/fills.json; edit those, then rerun assemble.py, never the outbox file).
- Explainer: outbox/gram-chain-explainer-2026-11-01.md (gpt-6-astra-checked; updated with the n^{2/3} correction).
- Theory: FORMAL.md (v1 frozen 21:14:08Z in coprover/FORMAL_v1_as_written.md; section 7 = v2 additions and the review
  corrections 7.13). Provenance: coprover/PROVENANCE.md.
- Registration: PREREG.md (Parts A, B, C, Amendments A1, C1), prereg_hashes.txt; deviations in logs/deviations.log.
- Scores: results/partA_scores.json, partB_scores.json, partC_scores.json; figures figs/fig1-5.
- Reviews: review/review_gpt6_r1.md (major, 14 findings), review_gpt6_r2.md (residuals); all applied (report section 10).

Scorecard: 16 hits (PA9 counted as the verdict for the n^{2/3} law), 7 misses, 1 incomplete (PA7: two widths dropped);
15 hits / 8 misses with PB1 as first analysed.

Nothing running. Open questions worth a next lane (not started): the stationary cloud's spectral shape beyond its PR
(the third-moment ratio grows slower than 1/k); the per-net residual scatter beyond the radius (CV 0.14-0.20, falling with
n?); a derivation of the gate-switching coefficient c ~ 1.1-1.6 in PR_rel = n/(n/PR_C + c t); the conditional angle tilt
E[delta/delta*(Q) | q] ~ n^{-1/2}.
