You are an adversarial reviewer (fresh session). Read-only sandbox; do not modify files. Review the near-final report
of this lane and the analysis behind it. Round 1 (review/review_r1.raw) reviewed the method and training code; its
fixes are amendment A4. Focus now on whether the report's claims follow from the evidence.

The lead's question (his words): "We need to really understand the bits of each layer, and we need to know and be
confident the representation is as good as reasonably possible, that is not a matter of low encoder capacity or
undertraining. So let us first individually encode each layer as well as possible. Ideally with a curve of how many
bits are needed for each level of accuracy at each layer." And: "we should train a single encoder that can use more
or less bits! By receiving an input of what precision/bit tradeoff we're targeting!" The bar set for this lane: the
lead wants confidence that each count is limited by the network, not by our encoder; say plainly where that cannot be
certified.

Files: bit-accounting-arc.md (the report), PREREG.md (Part P1 and amendments A1-A19; hashes and times in
prereg_hashes.txt), notes/DEVIATIONS.md, results/ (generated tables: P1_tables*.md, P1_scores_v2*.json,
conv_subset*.md, conv_table*.md, c7_table*.md, consistency*.md, spectrum_table*.md, certified_curves.json = export
for another lane, diag/). Analysis code: lib/vra.py, lib/vrb.py, scratch/score_P1.py (registered scorer),
scratch/score_P1_v2.py (A4 scorer), scratch/report_tables.py, scratch/export_curves.py, scratch/conv_table.py,
scratch/c7_table.py, scratch/conv_subset.py (A18 convergence rule), scratch/consistency.py (A19 flags),
scratch/spectrum_table.py, scratch/perturb_exponent.py, scratch/fig_curves.py, scratch/fig_conv.py;
training/evaluation code gpu_src/lib/vrlib.py, gpu_src/scripts/run_vr.py (including the A19 backward-curriculum
start, bwd_init), gpu_src/scripts/ref_curve.py, gpu_src/scripts/refine_posthoc.py; raw results
runs/bitarc-*/P1/VR_*.json (one per model; the loaders dedupe by file name). Numbers marked [pending] in the report
are still being computed; judge the rest.

Report numbered findings (each: severity major/minor, where, what is wrong, the fix). In particular:
1. Every number in the summary and tables: does it match the generated tables and JSON (spot-check at least ten)?
   Are medians, ranges, "n=1" cells and the better-of-two-starts rule applied as stated?
2. Claims of certification: does each certified/not-certified statement follow from the certificate runs that exist
   (which nets, layers, accuracies)? Any overclaim, e.g. extrapolating a check from one net or layer, or calling a
   count converged where a check failed or did not run?
3. The definition of "the output's curve" as the lower envelope of every code of a net (each code of h_l is also a
   code of a = f(h_l), with rate >= I(h_l; z) >= I(a; z)): correct? Does it bias the ratios or C1?
4. The C7 check of the variable-rate encoder (results/c7_table.md, scratch/c7_table.py): fair comparison? Is the
   "gap" reading of the t = -2 failure right?
5. The slope interpretation (bits per halving above the input dimension; the perturbation-exponent diagnostic): sound,
   or an overreach?
6. The comparisons (relevance lane N(l, eps), the analytic reference, the Gaussian bound, the bits-bounds formula,
   the sibling lane): apples to apples?
7. Pre-registration: were amendments made before the runs they affect (compare amendment times in PREREG.md with
   prereg_hashes.txt and the result files' times)? Is every registered prediction scored as registered, with misses
   reported?
8. The convergence subset (A18) and the backward curriculum (A19): is the convergence rule implemented as registered
   (scratch/conv_subset.py)? Is the backward start (bwd_init in gpu_src/scripts/run_vr.py) a fair implementation of
   "initialise layer l's code from layer l+1's converged code composed with the one-layer map", given that the local
   class has one ReLU layer? Any bug in it (frames, anchors, gains, prior copy, decoder init)?
9. Anything a careful reader would need that the report omits (e.g. cells not run, flagged cells, compute cuts).
Verdict: sound / fixable issues / unsound. Be concrete and concise. Write everything to stdout.
