You are GPT-6 (gpt-6-astra) acting as a fresh, adversarial reviewer. Read-only sandbox; do not modify files. You have not
seen this work before. Review the report /home/agent/workspaces/mats/work/scale-mode/scale-mode.md and the files it
cites in /home/agent/workspaces/mats/work/scale-mode: PREREG.md and prereg_hashes.txt (frozen copies in frozen/),
logs/deviations.txt and the queue logs, notes/SOURCES.md (the claims verbatim and the contest specification),
notes/AUDIT.md (the audit of the third-party repository thirdparty/scale-separation), scripts/ (smlib.py adapter,
run_cell.py runner, score.py and score_predictions.py, the hashed scorer; the evalq_*.sh queues and the stop/split
scripts listed in logs/deviations.txt), gpu_src/ (the GPU runner for the 1024 x 256 cell, PREREG Amendment 1),
scripts/gpu_gates.py and GPU-LOG.md, runs/ (runs/gpu/ is the GPU output) and runs_dev/, and results/
(results/score.json is the hashed scorer's output; tables.md and figs/ are formatting only; explore_fs.py is exploratory). The companion lane's report is
/home/agent/workspaces/mats/outbox/arc-update-2026-11-02.md (its ladder and RQMC numbers are inputs here).

The report tests two public counter-claims to the claim that deductive estimators lose to sampling on ARC's deep random
ReLU MLPs when depth grows with width: forum topic 18298 (a "scale mode" law that, its author says, restores the
convergence of cumulant propagation and beats sampling at every width tested) and topic 18198 ("covariance propagation
decisively beats sampling in Phase 2"). Check, and report as numbered findings with severity (major / minor) and a
concrete fix:
1. Fairness to the claims: is the third-party estimator run as its author ran it (frozen numerics, rules, FLOP
   accounting)? Check the reproduction of the author's own 64x16 number and 1024x256 identity check (logs/dev_claimB.log,
   runs_dev/claimI0.json), the adapter (scripts/smlib.py) against thirdparty/scale-separation/estimator/lv2.py and
   arc_ladder/sl_fac.py, and whether the transferred predictions (PREREG 5.1) are fair readings of the claim.
2. Every number in the summary and tables: recompute a sample from runs/ and results/ (state which), and check the
   prereg verdicts against PREREG.md's exact wording, including the decision rule (section 6, D1/D2/N2).
3. Whether the measurements answer the questions: equal-compute comparisons (cost conventions: ARC's counter, the
   claim's ndtr count, flopscope prices; RQMC interpolation and extrapolation), the error-cost exponent gamma between
   ladder levels, width exponents from few widths, truth noise (cross-half scoring, truth sizes), RQMC replicate noise.
4. Whether the conclusions follow (does either claim "escape the ladder"? does the negative apply at Phase 2?), anything
   overstated or missing, and whether the claims are quoted fairly (compare with notes/SOURCES.md and the downloads/).
5. Pre-registration hygiene and deviations: anything undisclosed.
Give a verdict (accept / minor revision / major revision) and write everything to stdout.
