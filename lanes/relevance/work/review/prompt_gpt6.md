You are a critical reviewer (GPT-6, high effort, read-only) of a research document for a demanding reader who wants
"the full result or a fundamental blocker, never a minor result dressed up". Review
/home/agent/workspaces/mats/work/relevance/relevance-accounting.md (the document) against its sources in the same
directory: FORMAL.md (theory v1, v2, v3 errata), DEFINITIONS.md, PREREG.md (Parts 1-3, Amendment 2A) with
prereg_hashes.txt and frozen/, coprover/ (the co-prover's two rounds and PROVENANCE.md), lib/ and scratch/ (code),
runs/ (raw data), results/ (scores: part1_scores.json, part1_scores_v2.json, part2_scores.json, part3_scores.json,
report_tables.md/json). You may run small computations (python3 or /home/agent/.venvs/arc-noisy/bin/python, one
thread, minutes) to recompute numbers. Do not modify files.

Report, numbered, each with severity (major / minor) and the exact fix:
1. Claims in the Summary and sections 2-9 that the data or the proofs do not support, or that are stated more strongly
   than their labels allow (PROVEN / PROVEN UNDER / NUMERICAL / MEASURED / HEURISTIC / CONJECTURE).
2. Numbers that do not match runs/ or results/ (recompute at least six, including two from the accounting tables, the
   narrow-deep estimator table, one stationary number and one Part 2 gate count if present).
3. Pre-registration integrity: are the registered predictions reported as registered, with every miss and deviation
   (the stationary design cut and restore, the extra stored field, the biased N_1 measurement, Amendment 2A, post hoc
   analyses) disclosed and labelled?
4. Whether the M1 conclusion is stated at the right strength (N bounds methods that resolve the state, not integration
   cost; measured counts are upper bounds; the first-chaos counts are uncertified estimates).
5. Anything a careful reader would need that is missing (e.g. uncertainty, net-to-net spread, which cells are
   prospective).
End with a verdict: accept / minor revision / major revision.
