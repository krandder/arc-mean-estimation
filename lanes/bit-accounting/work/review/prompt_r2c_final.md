You are an adversarial reviewer (fresh session). Read-only sandbox; do not modify files. Final check of the phase-1
report bit-accounting.md (Summary and sections 1-3) after your round-2b review (review/review_r2b.raw). Since then:
r2b findings were applied (see the Process section and notes/DEVIATIONS.md), and the amendment P1-A post-pass finished
on 55 cells (runs/P1X/X_*.json: explorer local restarts with gates inside the data cloud, a width-n encoder with a
wide decoder, a residual output-space centroid). Scores: results/P1_scores.json, results/P1_table.md (from
gpu_src/scripts/score_P1v2.py); the summary numbers are filled by scratch/summary_fill.py.
Report numbered findings (severity, location, what is wrong, fix), concisely:
1. Recompute at least six summary numbers involving the post-pass (explorer savings by layer position, the width-n /
   wide-decoder difference, the residual-centroid statement, a local count that now comes from an explorer code).
2. Was each r2b finding applied or stated as a limit? List any that were not.
3. Any remaining overclaim, especially about how sure the counts are and about the controls.
Verdict: accept / minor revision / major revision. Write everything to stdout.
