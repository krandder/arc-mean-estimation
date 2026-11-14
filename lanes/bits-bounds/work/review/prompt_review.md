You are an adversarial reviewer (fresh session; you have not worked on this lane). Read-only sandbox; do not modify
files. Review the report /home/agent/workspaces/mats/outbox/bits-bounds-2026-11-01.md and its support in this directory:
FORMAL.md (theory v2), PREREG.md and prereg_hashes.txt, scratch/run_eval.py, scratch/run_ml.py, scratch/score_prereg.py,
scratch/score_ml.py, scratch/posthoc.py, scratch/tables.py, lib/bb.py, lib/chain3.py, lib/meanfield.py, tests/test_bb.py,
results/ (scores and tables), runs/ (raw JSON/NPZ), coprover/ (co-prover answers and PROVENANCE.md).

Check, and report numbered findings (each: severity major/minor, location, what is wrong, the fix):
1. Every claim labelled PROVEN: is the proof correct and are all hypotheses stated? Especially Thm 7.1-7.5,
   Prop 7.7-7.8, Thm 5.1-5.2, Prop 5.3, Thm 4.2, Lemma 4.3, Prop 9.1.
2. Every number in the report: does it match results/ and runs/? Recompute at least six headline numbers from the raw
   files (e.g. the PR law fit, a D_best value, a bias ratio, an E3 ideal ratio, an F1 gain, a P1 slope).
3. Pre-registration: were the hashes recorded before the runs (compare file times in logs/queue.log, logs/queue_ml.log
   with prereg_hashes.txt)? Are deviations disclosed? Is each prediction scored as registered?
4. Overclaims: is any statement stronger than its evidence (labels, quantifiers, n-dependence claims from few sizes,
   per-net versus annealed quantities, optimistic in-sample selections)?
5. Code: bugs that would change a number (frozen merges, assignment of test points, the cost accounting of the
   two-level and multilevel samplers, the best-subset selection, normalisation by V_ang).
6. The hash section: is the model of Proposition 9.1 stated exactly, and are the true/false statements precise?
7. Anything missing that a careful reader needs (e.g. what is not covered by any bound).

Verdict: accept / minor revision / major revision. Be concrete and concise. Write everything to stdout.
