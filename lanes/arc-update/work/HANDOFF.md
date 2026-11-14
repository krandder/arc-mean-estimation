# arc-update HANDOFF (written 07:10Z, updated 08:11Z, 2 Nov 2026; update before ending a turn)

Lane: arc-update (MATS, target M1) for main (opus-mats); bead pool-ttdzrk.13 (plan tree pool-ttdzrk.13). Brief: the
strongest defensible argument on ARC's 256 x 32 goal (theorem, certified parameters, registered predictions,
steelman, what ARC should update). Rules: labels; PREREG hashed before scored runs; CPU nice 19 + ionice -c3, at most 2
heavy processes; kill by PID only; trash-put only; no AI credit; 3-5 line notes to main at milestones; never message
Kelvin or anyone else; review by gpt-6-astra (codex-any; check the "model:" line; never fall back).

## State (10:34Z): report revised after the adjudication relayed by main and an astra check; copied to outbox
- arc-update.md (sha 7b2cdfb6, 10:34Z; outbox copy identical) revised after the GPT-6 review (major revision, 17 findings, all applied; section
  9) and co-prover round 4 (FORMAL E12). Scorecard final run 10:10Z: 29 hold, 3 fail (P4, P7, P12), 4 partial
  (P9a-c on 3 of 5 nets, P19), 4 undetermined (P20-P23, stopped run). All lane leaves closed; parent pool-ttdzrk.13 left
  open for main.
- Still running (queue X2, PID 3376174): rank runs 203-204 (P9), then k3fa on net 200. When they land:
  python scratch/scorecard.py && python scratch/insert_scorecard.py, then update the P9 text in section 4.3 and the
  k3fa note in 4.1 (both say "not reached / queued").
- Possible next step (not started): measure the radial recursion's own one-step defects and their Gram matrix (astra r4's
  test of the Theta(L/n^2) mechanism), and a convergence check of the finite-sample recursion (2^20 samples, batch
  2^15) at n = 128.
- 13:29Z main: queue X2 results landed and are in: scorecard regenerated (31 hold, 4 fail, 1 partial, 4 undetermined), P9 text updated to 5 nets, k3fa note updated (net 200: worse than k3f in error and cost), and the four 18298 passages cite outbox/scale-mode-2026-11-02.md. Outbox copy refreshed (sha c6bf81ad).
