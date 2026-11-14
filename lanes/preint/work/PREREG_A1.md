# preint PREREG Amendment 1 (15:10Z, 2 November 2026), before any 256 x 32 run on nets 202-204

Reason: at 256 x 32 an active-subspace window line takes about 2.1 s of wall time on the loaded machine (about 1,340
passes per line), ten times my estimate; the registered budget (2^1..2^7 lines, two PI variants, 8 replicates, 4 nets)
would take about 6.5 process-hours. Net 201 keeps the registered budget (its run is in progress: RQMC and RQMCRB done,
PI_as_w at 2^6). Nets 202, 203, 204 change as follows; nothing else changes (methods, replicates, fit protocol,
predictions, pass rules).
- PI_as_w and PI_rand_w: 2^1..2^5 lines (was 2^1..2^7). RQMC, RQMCRB, MLMC_16 unchanged.
- They run in a second process, in parallel with net 201 (two heavy processes in total). Queue B is stopped after
  net 201 by killing its shell by PID (the running net-201 Python process is left to finish).
- With five budgets the top-60% fit uses the frozen rule's minimum of four points.
Expected effect on the tests: none on P1, P2 (they use the largest PI budget's vertex counts and variance ratios),
P3a (equal-cost ratios over the shared range), P6, P7; P3b's PI exponents at 256 x 32 come from a smaller N range
(2^2..2^5 lines) for nets 202-204.
