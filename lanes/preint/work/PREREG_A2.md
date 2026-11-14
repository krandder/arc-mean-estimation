# preint PREREG Amendment 2 (15:35Z, 2 November 2026)

Reason: under the machine's load the 256 x 32 runs are about three times slower than when Amendment 1 was written
(net 201's PI_as_w at 2^6 lines took more than 30 minutes; 2^7 would take about 70 more, and PI_rand_w at 2^1..2^7
about 60). Net 201 is brought to the same PI budget as nets 202-204; no prediction, pass rule, method or replicate
count changes.
- Net 201: PI_as_w keeps its completed budgets 2^1..2^6 (2^7 dropped: its process is killed by PID once 2^6 is
  written); PI_rand_w runs at 2^1..2^5 and MLMC_16 at the registered budgets, in a separate process writing
  runs/s3_arc_n256_L32_s201_b.json (the scorer merges methods per net).
- Nets 203 and 204 run in two processes in parallel (queue E's shell is stopped after net 202; at most two heavy
  processes at any time).
