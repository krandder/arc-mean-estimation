You are reviewing the final report of a research lane (read-only). Directory: the current working directory
(work/backward-bits). Report: backward-bits.md. Support: FORMAL.md (v1.2, with Proposition 7 added after registration),
PREREG.md + prereg_hashes.txt (registration 14:17:41Z, amendments A1-A4), notes/DEVIATIONS.md (D1-D5), results/
(scores.json, tables.md, summary.md, layers.md, exact_*.json), scripts/ (run_chain.py, run_truth.py, run_gauss.py,
run_fwd.py, score.py, report_tables.py, exact_1d.py, exact_chain_1d.py, exact_gauss_chain.py), runs_gpu/scored3/ (raw
JSON per net and chain), review/review_r1.raw (your round-1 audit of the code and FORMAL, and the fixes in D5).
The question the lane answers for Kelvin: does his backward bit recursion (output code trained to convergence; at each
step the code of layer l-1 trained to carry "the bits of layer l minus the bits the noise erases"; recurse to the input)
give certified bit counts all the way to the input on small noisy nets, and where does it break?

Please check, and report findings as a numbered list with severity (error / major / minor), location, what is wrong and
the fix:
1. Does every number in the report match results/ and the raw JSON? Spot-check at least 15 numbers across sections
   (tables, summary, exact checks).
2. Are the claims supported by the evidence and labelled correctly (PROVEN / CITED / MEASURED / HEURISTIC)? Flag
   overreach, especially in the summary and the verdict, and any claim that depends on the fixed 64-cell output
   quantiser or on candidate-set limits without saying so.
3. Is Proposition 7 (re-simulation codes make the recursion's targets equal I(h_l; c_L)) correct, and is its use in the
   report (the "simulation sense" in which the recursion is exact) correctly stated?
4. Are the round-1 findings correctly fixed or disclosed? Is anything still leaking test data into selection?
5. Are the pre-registered predictions B1-B14 scored as registered (thresholds, sets, provisional flags), and are the
   deviations honestly reported?
6. Is the report clear for a busy reader: does the summary say plainly whether the recursion gives certified bit counts
   all the way to the input and where it breaks?
Be concrete and terse. Begin your answer with the line "REVIEW r2".
