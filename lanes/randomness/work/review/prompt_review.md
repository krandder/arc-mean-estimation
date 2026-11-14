You are gpt-6-astra, giving a fresh, adversarial review of the randomness lane's report before it goes to Kelvin.
Read-only sandbox; do not modify files. In /home/agent/workspaces/mats/work/randomness read randomness.md (the report),
then check it against FORMAL.md (theory, v1 + E1 + E2), PREREG.md (registered predictions, Amendments 1-2),
prereg_hashes.txt, results/scorecard.md, results/rates.md, results/score_a2.json, results/tables.md,
results/tradeoff.json, logs/deviations.txt, coprover/PROVENANCE.md, notes/LITERATURE.md, and the code that produced the
numbers (lib/rnd.py, scratch/structure.py, combo.py, noise.py, detqmc.py, rates.py, rate_fit.py, score.py,
score_a2.py, report_tables.py). Runs are JSON files in runs/.
Check, and report findings ranked by severity (critical / major / minor), each with the exact sentence or number at
fault and the fix:
1. Every number in the summary and section 4 against the result files (recompute where cheap).
2. Every claim's label (PROVEN / PROVEN UNDER / MEASURED / HEURISTIC / CONJECTURE): is anything stated more strongly
   than FORMAL.md or the data support? In particular the exponent statements, the black-box ceiling numbers
   (9.6-18.8x), the "constant ~3" limit claims, the claims about random bits being free, and the verdict.
3. Registration hygiene: were scored predictions hashed before their data were seen (times in prereg_hashes.txt vs
   run start times in logs/queue.log and file mtimes)? Are failed predictions reported as failures?
4. Code bugs that could change a conclusion (estimators, unbiasedness, aliasing, truth handling, exponent fits).
5. Anything the report should say but does not, and any sentence that would mislead a reader who only reads the
   summary.
Write everything to stdout. Be concrete; prefer a few correct findings to many speculative ones.
