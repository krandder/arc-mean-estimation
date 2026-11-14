You are an adversarial reviewer (fresh session). Read-only sandbox; do not modify files. Round 2 (review/review_r2.raw,
14 findings, verdict "fixable issues") reviewed an earlier draft of this lane's report; its fixes are amendment A20 in
PREREG.md (with A21). Check the final report bit-accounting-arc.md against the generated tables and the run files:

1. Were the round-2 findings fixed as A20 says (common normalisation in lib/vra.py; convex-hull time-sharing in
   lib/vrb.py R_lin; named output baselines; scorer v3 scratch/score_P1_v3.py; matched doubling partners in
   scratch/conv_subset.py; export statuses in scratch/export_curves.py; the wording changes)? Name any finding that is
   not fixed or fixed wrongly.
2. Spot-check at least ten numbers in the summary, the converged-count table (section 4.1, from results/conv_subset.md)
   and the backward-curriculum table (section 4.2) against the generated files (results/P1_tables_final.md,
   results/conv_subset.md, results/c7_table.md, results/consistency.md, results/scorecard.md) and the run JSON
   (runs/bitarc-*/P1/VR_*.json; loaders dedupe by file name).
3. Does every "converged" / "not converged" / "unverified" verdict follow the registered A18 rule with A20's matched
   partners? Does any summary sentence claim more than the verdicts allow?
4. Anything still overclaimed or missing that a careful reader needs.
Round 2 of the convergence subset (A22, four 8x-steps runs) is still running; numbers marked [pending] will be filled
from results/conv_subset.md when it ends. Judge everything else.
Verdict: sound / fixable issues / unsound. Be concrete and concise. Write everything to stdout.
