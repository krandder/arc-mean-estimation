You are a rigorous, independent reviewer (read-only), round 2. In round 1 (file review/review_gpt6.md in this
directory, work/nd-exact/) a reviewer gave the report `nd-exact.md` a major revision with 10 findings. The report has
been revised; section 12 lists the changes. Check, adversarially:
1. Whether each of the 10 findings is actually addressed in the text (not just listed), and whether any revised claim
   is still stronger than the evidence.
2. The new post-hoc analyses: section 8 (fixed unscrambled Sobol rule against 64 scramblings per (net, N);
   scratch/posthoc_dsob.py, runs/posthoc_dsob_s*.json) and the paired ablation in section 9
   (scratch/posthoc_unb_ablation.py, runs/posthoc_unb_ablation_s*.json); also CS2c (runs/posthoc_cs2c_s*.json,
   lib/cs2.py face_floor). Are the statistics right (the "share of scrambled runs better" statistic, its null of 0.5 and
   standard error, the interpretation "one RQMC run with the randomness fixed"), and are the conclusions supported?
3. Numbers in the summary and sections against the run files and results/tables.md.
4. Anything in the revised headline or plain statement (section 10) that a careful reader would find misleading.
Give a verdict (accept / minor revision / major revision), then numbered findings with severity, evidence and fix.
State the model you are running on in your first line.
