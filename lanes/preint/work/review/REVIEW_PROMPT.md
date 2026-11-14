# Review request (lane preint): report and code

You are gpt-6-astra, the independent reviewer for the preint lane (read-only sandbox; do not modify files). Review
the report preint.md (assembled from notes/preint_template.md by scratch/assemble_report.py) and the code behind it in
this directory. NOTE: the ARC 256 x 32 scored runs (nets 201-204, runs/s3_arc_n256_L32_s*.json) are still running;
placeholders in capitals (EQCOST_256, LINE_256, P3B_COUNT, MATCHED_256, PLATEAU_256, P7_COUNT, P6_FAIL, ...) will be
filled from the same scripts when they finish. Review everything else, and the partial 256 x 32 files as they stand.
Review as a critical referee whose job is to find what is
wrong, overstated, unsupported or missing. Read: preint.md; PREREG.md and prereg_hashes.txt (check the hashes of
PREREG.md and frozen/*.py with sha256sum, and the chronology of runs/s*.json against the hash time 14:03:47Z);
FORMAL.md (v1 + E1-E3); coprover/ (both rounds); lib/line.py, lib/est.py, lib/nets.py, tests/test_line.py and
logs/test_line.log; scratch/curves.py, fit.py, score.py, report_tables.py, posthoc_matched.py, degrees.py,
nongauss.py, kernel_bound.py, pieces.py; runs/, results/ (scorecard.md, scores.json, tables.md, pieces.md,
kernel_bound.json, posthoc_matched.json); logs/deviations.txt.

Check in particular:
1. Correctness of the exact line + radius algorithm (lib/line.py): vertex insertion, segment bookkeeping, the closed
   forms (Student-t cdf, end rays), window mode and its unbiased tail estimate; whether the tests would catch errors.
2. Honest compute: are all costs counted (pilots, bases, inverse normals, cdfs, sign tests, interpolations,
   end vertices)? Any place where the comparison favours a method unfairly?
3. Scoring: rerun scratch/score.py and scratch/report_tables.py and confirm the numbers in the report and the
   scorecard; check the fit protocol against PREREG; check the replicate-variance MSE and the bias checks.
4. Claims: every statement in the Summary and sections 2-6 against its evidence and label. Flag overclaims (e.g. about
   all sampling schemes, the asymptote as width grows, the IBC extension, identifiability) and anything stated as
   PROVEN that is not.
5. The theory: F7 (rank lemma with signed weights, line version), E2's corrections, E3's per-net version; whether the
   report's reading of the degree-energy measurements follows.
6. What is missing that a referee would demand before accepting the conclusion "no better asymptote from the sampling
   side as width grows; pre-integration helps only at tiny input dimension".
Give a verdict (accept / minor revision / major revision) and a numbered list of findings, each with severity
(critical / major / minor), the evidence (file and line or command), and the fix. Write everything to stdout.
