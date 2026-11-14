# bits-bounds lane: handoff (1 November 2026, 23:48Z)

Report: /home/agent/workspaces/mats/outbox/bits-bounds-2026-11-01.md (final for 1 Nov, sha e9575f7f; reviewed twice by
gpt-6-astra, 30 findings applied or answered, section 10; sections 3.5-3.6 audited by co-prover round 4).
Theory: FORMAL.md v2.3 (sha d284ff62; section 6.6 rewritten after round 4). Beads: pool-ttdzrk.12, leaves .1-.21 all
closed; the parent is left open for the next steps below.

State of the work
- Bits at layer l (FORMAL 6.6, report 3.5): N_l(eps) ~ max(0, (d_l/p) log2(D_l(1)/eps^2)), HEURISTIC. The variance
  profile is the input-bits lane's (frozen log-radius martingale, PROVEN every width; share after l ~8.3/(l + 9)).
  Registered Amendment 5 (12 new nets): Q1-Q6 hit, but Q6's 82/90 is 63 censored (> 8 bits) + 14 zero-bit + 5/13
  resolved counts within 2 bits (1.8x over-prediction). Lower-bound version: abstract theorem only (no global linear
  minorant, rho <= phi^2; angular atoms). Exponential spectrum: bits ~ (n/(2l)) ln^2(D_l(1)/eps^2)/ln 2 [r4-A].
- Cross-lane (report 3.6): on bit-accounting's ARC net, d = PR gives 224, 112, 45 vs learned 230, 104, 34-52 at
  l = 4, 8, 16; water-filling (quadratic law) within 1.6x; smooth layers sit at the output's ~19-bit floor.
- Closure (C4): exact single-Gaussian recursion gained at most ~3x to n = 256; annealed 1/n floor PROVEN UNDER (H_R).

Next steps (none started)
1. A restricted-window minorant for rho_{n,t}(phi) at finite width (exact two-replica chain) and a bulk small-ball
   bound, to turn 6.6(e) into a lower bound for nets on a range of cell sizes.
2. Test the quadratic-log law (r4-A, D6) against the measured cell counts and learned codes (registered).
3. (H_R) diagnostic for the closure (signed radius defects along its trajectories).

Rules in force: CPU only, nice -n 19 ionice -c3, at most 2 heavy processes, uptime first; Python
/home/agent/.venvs/arc-noisy/bin/python; gpt-6-astra only via codex-any (check the model line; never fall back);
pre-register measured parts in PREREG.md with hashes in prereg_hashes.txt before runs; message only main.
