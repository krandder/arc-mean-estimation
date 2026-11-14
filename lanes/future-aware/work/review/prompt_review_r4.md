You are GPT-6 (gpt-6-astra) acting as a fresh, adversarial reviewer (round 4, verification). Read-only sandbox; do not
modify files. Working directory: /home/agent/workspaces/mats/work/future-aware. Round 3 (review/review_gpt6_r3.md)
gave a major revision concentrated in cost accounting: (1) the optimistic D1 extraction scenario assumed Cholesky on
indefinite states; (2) H1's "full ledger" charged per-sample matrix-vector products that the sum-based rerun does not
perform (plus a double-charged closure for jacmf and a mean-source mismatch for k2); (3) the closing half-width
recommendation ignored the completed guarded results; (4) smaller items (best fixed control vs best per net, the
sensitivity range at n = 64, D1 loss range as variant medians, 1.13, 1.65, "six reruns", comparator-noise wording).
The report future-aware.md has been revised; section 8 lists how each round-3 item was handled (deviations item 14).
Changed artifacts: scratch/score_hyb_direct.py (three ledgers: reg, exp, sum; results/hyb_direct.md), scratch/d1_ledger.py
(results/d1_ledger.json), FORMAL.md (E14 addendum 2 ratio).
Check:
1. For each round-3 item: resolved, partly resolved, or not resolved, with the specific remaining problem.
2. The sum-based ledger in score_hyb_direct.py: is it a fair accounting of what run_hyb_direct.py v2 computes (per-sample
   and one-time work, closure charged once for the mean used)? Recompute the section 4.3 gains for one width.
3. Any new error introduced by this revision, and whether the summary stays within what is shown (tested methods,
   widths, labels, descriptive vs asymptotic, scenario vs measured cost).
Be concise: a verdict (accept / minor revision / major revision), then the findings. Write everything to stdout.
