You are an adversarial reviewer (fresh session). Read-only sandbox; do not modify files. Review the phase-1 report
bit-accounting.md in this directory (sections Summary, 1-3 are new; sections 4-7 are earlier work kept as background)
and its support: PREREG.md (Parts P1, P2.0, amendment P1-A at the end) + prereg_hashes.txt, notes/DEVIATIONS.md,
results/P1_table.md and results/P1_scores.json (from gpu_src/scripts/score_P1v2.py), runs/P1/*.json (main cells) and
runs/P1X/*.json (amendment certificates), gpu_src/scripts/run_vr.py and run_vr_cert2.py, scratch/build_report.py and
scratch/summary_fill.py (they write the summary numbers), review/review_r2a.raw (your earlier review of the code; check
that each finding was answered).

The lead's request: "really understand the bits of each layer ... be confident the representation is as good as
reasonably possible, that is not a matter of low encoder capacity or undertraining ... a curve of how many bits are
needed for each level of accuracy at each layer"; one lambda-conditioned encoder per layer, spot-checked against
per-lambda models; both encoder classes; certificates on every curve; slopes.

Report numbered findings (each: severity major/minor, location, what is wrong, the fix):
1. Recompute at least eight numbers in the Summary and sections 2-3 from runs/ or results/ (e.g. a local count at the
   input layer, an unrestricted-vs-output gap, a slope, a linear-reference comparison, a certificate pass rate, a
   control-net number).
2. Overclaims: anything stronger than the evidence (e.g. "as good as reasonably possible" given the certificate pass
   rates and the not-covered points; statements about all nets from some seeds; the controls).
3. Were review r2a's findings answered (fixed, or stated as limits)?
4. Pre-registration: P1 / P1-A predictions scored as registered; deviations disclosed; scorers hashed before scoring.
5. Bugs in score_P1v2.py, build_report.py or summary_fill.py that change a reported number.
6. Is the answer to the lead's question plain and correct; is anything missing that a careful reader needs?
Verdict: accept / minor revision / major revision. Be concrete and concise. Write everything to stdout.
