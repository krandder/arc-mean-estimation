# Update against results/P1_tables_partial.md as of 11:33Z (the table Kelvin has)

Generated 13:45Z by scratch/table_diff.py: the 11:33Z table reconstructed exactly (run files written before 11:33Z,
the pre-A20 analysis code; results/P1_tables_as_of_1133Z_reconstructed.md) against today's tables (all runs so far,
A20 analysis; results/P1_tables_A20_now.md). Full cell list: results/table_diff_1133Z_to_now.md.

1. The A20 corrections alone (same runs, new analysis) move no table cell by more than 5%: the largest is ARC
   layer-0 unrestricted at 10% error, 22 -> 21 bits (-5%); nothing changes between a number and not reached. They do
   change the single-encoder check at the cheap end of layer 0 (C7, not in the table): at nMSE 0.73 the
   reference-start curve needs 43 bits, not 117 (time-sharing over the convex hull); of the seven cheap-end checks
   (nMSE 0.40-0.73) three become passes (t = -2.5 for both starts, t = -2.75 for the reference start) and four remain
   failures (as large as 4 bits for a dedicated model against 43 for the curve at nMSE 0.73).
2. Every cell that moved by more than 5% did so because new runs arrived: ARC layers 12 and 20 now have the
   reference-start base on all four nets (at 11:33Z their medians were net 4000's look-ahead start alone):
   - layer 12, local count: 44 -> 74 [44-97] bits at 10% error (+68%), 128 -> 176 at 3%, 244 -> 289 [244-333] at 1%
     (+18%), 399 -> 437 at 0.3%; x output at 10%: 2.9 -> 3.3;
   - layer 20: 19.6 -> 27 [20-42] at 10% (+38%), 59 -> 73 at 3%, 125 -> 148 [125-203] at 1% (+18%), 232 -> 253 at
     0.3%; x output 1.3 -> 1.5 (10%), 1.5 -> 1.6 (1%);
   - so the cross-net spread at mid layers is wide (net 4001 needs about twice net 4000's bits) and net 4000 is the
     cheapest net.
   Newly measured since 11:33Z: the reference-start base at ARC layers 12 and 20 (all nets) and narrow-deep layer-16
   unrestricted (it equals the output's curve).
3. Status changes:
   - certified (export): unchanged, narrow-deep layer-0 unrestricted on nets 216, 217, 221; no ARC cell.
   - converged (A18 subset, new since 11:33Z): none yet. Layer 0 local moves -0% / -2% with 2x steps at 10% / 1% but
     its matched depth partner is still running (unverified); layers 16 local, 16 and 31 unrestricted and 31 local
     are still falling 4-5% per doubling (not converged); layer-0 unrestricted never reaches 1% error.
   - predictions: P1.2 not evaluable -> pass; P1.5 not evaluable -> pass; P1.7 not evaluable (2 of 3 layers) ->
     pass; P1.10 fail -> pass (the 11:33Z scorer counted cut cells as failures; v3 scores the cells that ran);
     P1.4 not evaluable (ARC layers 4 and 28 base still running); P1.8 (layer-31 part) and P1.12 (random-start toy)
     remain misses.
Still running: ARC layers 4 and 28 base, the convergence subset round 2 and the backward chain; the final tables will
be diffed the same way.
