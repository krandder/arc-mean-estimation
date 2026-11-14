# Deviations from PREREG.md (registered 2026-11-02T14:17:41Z)

D1 (14:20-14:23Z, infrastructure only). The first scored launch (queue 20_scored.sh) ran next to the dev 3 queue
(8x8 dev seed): 11 processes at about 2 GB each exhausted the L4's 22 GB, and most scored chain jobs died with CUDA
out-of-memory at their first step (logs runs_gpu/logs/scored/job_scored_chains_*.log). The pool runner also logged
rc=0 for failed jobs (the date substitution reset $?). Both queues were stopped by PID at 14:21Z. Relaunch as
21_scored.sh: dev 3 dropped, 6 parallel workers instead of 7, PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,
pool.sh v2 (exit code captured first). The registered science code (lib/bb.py, run_*.py, the job files) is unchanged;
chains resume from completed steps, and steps are deterministic given their seeds, so no result depends on the crash.
New hashes: prereg_hashes.txt, amendment A1.

D2 (14:28-14:40Z, procedure; amendment A2). Kelvin's procedure reads "either use the last encoding, or do something to
train the encoding at l-1". The registered candidate set (PREREG section 2) left out the first option: the noise-free
composition c_{l+1}(relu(W_{l+1} h)) was only reported as the "reuse baseline". The first scored steps showed why this
matters: on 8x16 seed 5000 the noise erases 0.017 bit at the first step (sigma was calibrated on the dev 8x16 net; the
8-wide nets' state norms differ a lot between seeds), the posterior is then nearly a sharp partition, the smooth
predictor fits it poorly (excess cross-entropy 0.15 bit) and the best trained code carries 5.08 of T = 5.33 bits,
while the reuse code carries 5.30 within the rate rule. Change: the reuse code is a selectable candidate in every chain
(main and certificate fits), under the same rules; a selected reuse code is saved as a composition and rebuilt
recursively (stacked reuses are encoders one layer deeper per reuse, Kelvin's "deeper encoders as needed"); C2 does not
apply to a selected reuse code (it uses no predictor). Checked on CPU: at sigma = 1e-4 (8x8 dev) every step selects
reuse (shortfall about 0.005 bit) while the trained predictor's excess cross-entropy grows from 0.26 to 0.52 bit toward
the input. The scored chains restart from scratch into /root/runs/scored2 (runs_gpu/scored2); the first launch's partial
output (/root/runs/scored, runs_gpu/scored: first steps only) is superseded and not scored. Sizes, rules, tolerances
and predictions B1-B14 are unchanged.

D3 (noted 15:00Z, clarification). PREREG section 3 says the Gaussian-channel comparison runs at "every step" of chain K;
the registered job file (scored_extra.txt / scored2_extra.txt, hashed with the registration) runs it, like the
forward-trained codes, at the five layers L-2, floor(3(L-1)/4), floor((L-1)/2), floor((L-1)/4), 0. The job file is what
runs; B13 and B14 are scored on those layers.

D4 (15:01Z, infrastructure; amendment A3). The scored2 pool (two phases, 6 workers: evaluations only after all 48 chain
jobs) is replaced by a dependency scheduler (gpu_src/scripts/sched.py, 8 workers) running the same registered command
lines (gpu_src/queue/scored2_dag.json, generated from the hashed scored2_*.txt files by scripts/mkjobs_dag.py): a net's
truth pass starts when its four chains are done, the Gaussian and convergence jobs after its chain K, the forward-trained
codes at once. The running pool was stopped by PID; chains resume from completed steps (in-progress steps are redone).
The later-VM resume queue (30_resume.sh) uses the same scheduler.

D5 (15:25-15:35Z, code fixes after the round-1 review; amendment A4). gpt-6-astra's audit of FORMAL, PREREG and the code
(review/review_r1.raw, 22 findings, before any scored outcome was assessed by it) found errors in the chain driver that
change selections: the output-target chains (P, PR) took their select-set entropy correction from the test set at the
wrong M (test leakage, under-correction); Kmax was set from the test-set target; cell tables could keep all-zero rows
for cells without test points; the 2-cell family returned a centroid/threshold pair that did not produce its stated
assignment, and crashed if its 2-cell seed collapsed; there was no 0-bit candidate; the target's SE covered only the
conditional-entropy term. Fixed (lib/bb.py, scripts/run_chain.py), plus the evaluation scripts (run_truth.py: the direct
comparator now also gets every chain's code and the reuse of the layer-above direct codes, rate budgets from the select
set, bootstrap SE of I*; run_gauss.py: N/2 check of the relevance plug-in) and the scorer (missing certificate evidence
is "incomplete", not a pass; B2/B3 decided only on codes that reached the 95% target or whose largest candidate already
bounds the needed rate; B14 by linear interpolation along the measured curve, layers not bracketed unresolved; checks of
PREREG section 6; provisional verdicts on incomplete data). All scored chains restart from scratch into
/root/runs/scored3 (runs_gpu/scored3). Before the restart, partial scored2 steps (targets and rates of the first 2-8
steps on four nets) had been looked at; no prediction, rule or tolerance was changed.
Also disclosed (review finding 3): the budgets in the PREREG text (N_tr 2^17, 4000 predictor steps, 3 restarts, DIB from
{3, 8, Kmax} with 2 restarts, certificate depths 1 and 4, 400 decoder steps) are those of the first dev run; the code
hashed at registration (14:17:41Z), which is what ran, uses the reduced budgets adopted at 14:10Z for GPU time (N_tr 2^16,
2500 steps, 2 restarts, DIB from {8, Kmax} with 1 restart, depth 4 only, 200 decoder steps). The restart and depth-4
certificates measure whether these budgets bind.

D6 (15:30-19:40Z, infrastructure only). The spot VM backbits-1 was preempted at about 15:30Z (6 minutes into scored3);
scripts/launch_vm2.sh resumed the run on backbits-2 at 15:37Z from the state pulled at 15:28Z (same registered command
lines; chains and evaluations resume from completed steps and layers; in-progress steps are recomputed). A misreading on
my side sent a TERM to backbits-2's local gpu-run process at 15:39Z; bash defers the trap until the remote command ends,
so the run continued and the trap acts as the normal end-of-run cleanup. Later VMs are launched by
scripts/launch_chain.sh (three consecutive empty listings before a launch). The scheduler runs its jobs in list order,
so the evaluation passes started only after the last chain job had started (18:50Z); this changes timing only.

D7 (19:40-20:05Z, infrastructure only). backbits-3 could not be created (spot stockout); a relaunch as backbits-4 was first
refused by the group budget check (the failed VM's $4 reserve was still counted; a $0 COST-AUDIT line records that it
never existed); backbits-4 (spot, us-central1-a) was preempted 6 minutes after start, during setup. The rest of the
run resumes on backbits-5, provisioned on demand (STANDARD) for reliability, budgeted at the same $0.87/h ceiling
(total stays within the $10 cap: about $1.57 + $3.50 + $0.10 + at most $3.48).

D8 (20:05Z, scope of three comparisons; registered science code for the chains and truth unchanged). After the chains
finished, 41 evaluation jobs remained (5 truth passes, 12 Gaussian, 12 forward-trained, 12 convergence), several GPU
hours after two preemptions and a stockout. The registered Gaussian comparison was also uninformative as configured: on
the 16-wide nets every value of its rate price gives a saturated rate (about 14 bits = log2 of the 16384 evaluation
points; the batch KL penalty has no gradient once the batch points separate), so its curve never brackets T (B14
unresolved). Changes: the 5 truth passes run unchanged; the convergence checks and the forward-trained codes run on seed
5000 of each config (the forward-trained codes at layers L-2, floor((L-1)/2), 0); the Gaussian comparison is replaced by
power-constrained codes (the encoder output scaled to a fixed per-dimension SNR, grid 0.03-4, cross-entropy only; rate
by the same Monte Carlo mixture estimates), seed 5000 of each config, the same 3 layers (scripts/run_gauss.py --powers,
output chainK/gauss_p.json). B13 and B14 are scored on these points. The 4 Gaussian jobs of the registered configuration
that ran partially on backbits-2 are not used.

D9 (21:00Z, found by the round-2 review; disclosed, not rerun). Two remaining paths in the truth pass's direct comparator
(registered code as run): (a) its Kmax was set from the test-set truth (e.g. 8x8 seed 5000, l = 2: 128 cells instead of
256), so its candidate set depended on test data; (b) on resume, completed layers' direct encoders were not restored, so
the reuse-of-the-layer-above candidates were missing below the resume point (8x16 seed 5000 from l = 1, seed 5002 from
l = 8). Both affect only the direct comparator (B9, the direct columns and the empirical bracket), never the chains or
the truth. Fixed in scripts/run_truth.py for future runs (Kmax from the select set); not rerun (VMs deleted, budget).
Also from round 2: the truth-monotonicity check in score.py used 0.01 + 3 SE instead of the registered 0.01; with 0.01
alone two layers exceed it by 0.0008 and 0.0017 bit (reported in the report, section 4.1).
