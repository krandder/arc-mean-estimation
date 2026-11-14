# Handoff: bit-accounting lane (pool-qxszj1.25), state at 23:55Z 2 November 2026

Owner: opus-mats-bitacct (subagent of main). Work dir: /home/agent/workspaces/mats/work/bit-accounting/ (all paths
below are relative to it). Report: bit-accounting.md (REPORT v1, 02:50Z; Summary for Kelvin first).

## PLAN CHANGE at 02:55Z (Kelvin via main): phase 1 is the only priority
Phase 1 = for every layer, the best possible bits-vs-accuracy curve:
- S7-style real-valued codes (fixed unit noise, information rate with a learned prior), ONE lambda-conditioned
  variable-rate model per (net, layer, class): lambda is an input (conditional variable-rate compression). Spot-check
  against separately trained per-lambda models at 3 points (must not be worse).
- Both classes (unres = sees h_l and the exact output; local = one ReLU layer of width n then affine).
- Full certificates on every curve: known answers (output curve vs Gaussian bound and Shannon lower bound; unres(l)
  vs the output curve; the linear net, where R(D) is exactly Gaussian reverse water-filling), centroid test
  (output-space regression E[a|z] on held-out codes), 2x capacity, 2x steps, 3 restarts, fresh-prior refit.
- Slope of each curve: bits per halving of output error, per layer.
- Scope: small nets 16x4, 32x8, 16x16, 32x32, seeds 5000-5002, layers {0, L/4, L/2, 3L/4, L-1} + output; and the S11
  controls (tanh4, feistel, linear; 16x16 s5000).
- A sibling lane does ARC 256x32 and narrow-deep 8x256 with the same method; it may read lib/bitlib.py, notes/ and
  gpu_src/ but not edit them.
Phase 2 (later, only after phase 1 is final): S9/S10, the S11 spectra/price parts, the unscrambling loss (a
reparametrisation at fixed rate; it must not raise the bits).
GPU: cap $25 (spent ~$5 at list price by 04:41Z), up to 2 L4s at once; GPU-LOG.md; delete VMs when done; on-demand OK.

## 01:50Z 3 Nov state: OPEN 1-3 DONE, REPORT v4 built, no VM running (gcloud list: 0 bitacct VMs)
- U-c 84/84 (bitacct-16/17 on-demand, deleted 01:40Z). Section 3.3 rewritten (notes/report_p2_U.txt): price per mu ReLU
  0.03/0.19/0.38/0.42, tanh 0.18/0.40/1.08/2.25 bits; cost = extra rate, pair distortion ~flat; tanh > every ReLU pair
  from L/4 on at mu >= 1 (one tanh seed), not in relative terms (U2 0/4, U1 7/18, U3/U4 hit). Summary point 8 updated.
- GPU: $35.72 audited of the $39.4 cap. P1-B remains 13/53 (not relaunched).

## 00:12Z 3 Nov state (successor agent; read this first)
- OPEN 1 DONE: v2 merged -> results/P2_maps_v2_all.json, scored by scratch/report_P2_maps_v2.py (copy of the registered
  scorer with v2 paths + noisy/base gate columns; hashed) -> results/P2_maps_v2_table.md; notes/report_p2_maps.txt updated.
- OPEN 2 DONE: bitacct-14 and bitacct-15 both PREEMPTED (00:01-00:02Z; COST-AUDIT lines). Noisy 36/36 cells -> section
  3.5 rerun; P1-B still 13/53 (rescored, unchanged; not relaunched).
- OPEN 3 RUNNING: U-c relaunched on ON-DEMAND bitacct-16 (jobs_uc_1) + bitacct-17 (jobs_uc_2), 2.2 h from 00:06Z,
  scratch/launch_uc2.sh, pull loops. Then: python3 scratch/report_U.py Uc; python3 scratch/report_U_split.py Uc
  (rate/distortion split) -> rewrite notes/report_p2_U.txt; rebuild. Audited spend $33.02 + these two (<= $3.83).

## 23:55Z state (read this first): PHASE 2 REPORTED (REPORT v3), three items still open
- Report: bit-accounting.md = REPORT v3 (sections 3.1-3.5 = phase 2), rebuilt by
  python3 gpu_src/scripts/score_P1v2.py runs/P1 runs/P1X runs/P1Y && python3 scratch/build_report.py "<status>".
  Review r3 (gpt-6-astra, review/review_r3.raw, major revision) applied to the text (Process section lists it).
- OPEN 1: code-map v2 rerun on the CPU (scratch/p2_maps_v2.py, 2 processes, started 23:4xZ, ~1.5 h):
  outputs results/P2_maps_v2_part0/1.json. Then merge them (as P2_maps_all.json was made), run
  scratch/report_P2_maps.py on the merged v2 file (edit its input path), and update notes/report_p2_maps.txt:
  rank-truncated affine R^2 at late 32x32, rescored H3/H4, gate tracking on the noisy codes (tracked_frac_noisy)
  and the base rate (tracked_frac_base); rebuild the report.
- OPEN 2: VM bitacct-14 (spot, us-east4-c, until ~01:16Z, queue 80_rest.sh: noisy cells then the remaining P1-B
  cells); its pull loop runs. When it ends (or is preempted: add a COST-AUDIT line), rerun
  python3 scratch/p2_noisy_maps.py (16x16 nets complete) and the P1-B scoring, update notes/report_p2_noisy.txt
  (cell counts), rebuild. If it vanished without a DELETE line: COST-AUDIT at 0.87 x hours.
- OPEN 3 RUNNING: corrected Part U (amendment U-c, approved; cap now $39.4): VM bitacct-15 (spot, us-east1-c, 2.6 h
  from 23:44Z), queue 55_unscr_c.sh, 84 jobs (lambda 0.01 linear first), outputs runs/U/Uc_*.json (pull loop started by
  scratch/launch_uc.sh). When done: python3 scratch/report_U.py Uc -> results/Uc_table.md, Uc_scores.json; rewrite
  notes/report_p2_U.txt leading with the cost per mu, ReLU vs tanh, with rate and distortion changes per layer and mu
  shown separately (main's request), keep the flawed run as superseded; rebuild; note to main. If preempted:
  COST-AUDIT, copy finished Uc JSONs to gpu_src/prior/U and add a restore line (run_unscr.py skips existing outputs).
- (old) OPEN 3 (needs main's budget decision): Part U rerun with a scale-invariant penalty (do not detach the variance in
  run_unscr.py; register as an amendment first), about $3; the current U numbers mix simplification with loss of
  signal (stated in section 3.3).
- GPU spend: $31.65 audited + bitacct-14 (<= $2.2) of the $35.9 cap.

## 15:45Z state (superseded)
- All GPU work done; all VMs deleted (GPU-LOG.md; total $23.95 of the $25 cap). 159/159 main cells (runs/P1),
  amendment post-pass on 55 cells (runs/P1X: 55 of the 57 ReLU local cells; controls' local cells and unrestricted cells
  not reached within budget).
- Report: bit-accounting.md = REPORT v2 (phase 1 final), built by scratch/build_report.py. Key finding added late:
  explorer local encoders (gates inside the data cloud) need ~31% fewer bits at the input and L/4 than the anchored
  ones (10% error), so early-layer local counts are best-found, not certified optimal.
- Reviews: r2a (code), r2b (report), r2c (final check after the post-pass) by gpt-6-astra; all findings applied or
  stated as limits (report Process section, notes/DEVIATIONS.md). Beads: pool-qxszj1.25 and all leaves closed.
- P2.0 part 1 DONE on the CPU (approved by main): results/P2_identity_table.md, report section 3.1; registered H1
  missed (anchored local codes are linear on every net).
- PHASE 2 APPROVED by main (~16:0xZ): all four parts, lane cap +$12 (total cap $35.9; gpu_launch.sh uses 35.9).
  Order: (a) P2.0 parts 2-4 -> (b) unscrambling (Part U) -> (c) explorer restarts -> (d) P2.0 part 5 (noisy).
  Message main at (a) done, (b) design (SENT 16:1xZ), and the end. Report in certified-linear terms (linear-piece cost
  ratio and learned-mixture ratio per layer, as in results/P2_identity_table.md).
  (a) DONE 18:2xZ (report section 3.2; results/P2_maps_table.md; H2-H4 missed). Note to main sent.
  (b) DONE 19:55Z: report section 3.3 (notes/report_p2_U.txt), results/U_table.md; U3, U4 hit, U1, U2 missed.
  (c)+(d): the spot VMs were PREEMPTED at ~20:02Z (P1-B lost, no finished cell; COST-AUDIT 2 x $1.51; spent now
      $29.67 of $35.9). Relaunch loop scratch/launch_retry.sh (queues 60_p1b.sh + 70_noisy.sh only, 2.6 h, on-demand /
      spot alternating; L4 stockouts) running since 20:40Z.
  (b)+(c)+(d) RUNNING since 18:18Z on SPOT L4s bitacct-12 (136.70.165.108) and bitacct-13 (us-east4-c), timeout 4.2 h,
      chained queues 50_unscr.sh -> 60_p1b.sh -> 70_noisy.sh (each waits for the previous .done; 70 touches STOP);
      outputs /root/runs/U, /root/runs/P1Y, /root/runs/N; pull loops started by scratch/launch_retry.sh.
      On preemption: copy runs/U, P1Y, N JSONs into gpu_src/prior/ (queues skip finished outputs only if restored:
      add restore lines) and relaunch with scratch/launch_retry.sh. Budget: spent $26.65 before these; cap $35.9.
      Analysis scripts READY and hashed: scratch/report_U.py (Part U table, price of forcing, U1-U4),
      scratch/p2_noisy_maps.py (P2.0 part 5 + H5), score_P1v2.py now reads runs/P1Y (B1, B2):
      python3 gpu_src/scripts/score_P1v2.py runs/P1 runs/P1X runs/P1Y. Report: add notes/report_p2_U.txt,
      notes/report_p2_noisy.txt (and the P1-B outcome) into scratch/build_report.py like report_p2_maps.txt.
      (old note:) Analysis to write: Part U table (lead with the price of forcing per mu, ReLU vs tanh4: extra bits = change in
      Lagrangian / lambda per layer; predictability lin/diag/mlp) and U1-U4 scores; P1-B (B1, B2) via score_P1v2
      extension (Y_ files as more explorer curves); P2.0 part 5 analysis script (Procrustes transfer of T, H5) to be
      written AND hashed before reading runs/N.
  (a, old) RUNNING: PREREG amendment P2.0-a; l+1 cells via run_vr.py --groups G1 --certs 0 (queue gpu_src/staged/40_p2a.sh,
      lists queue_lists/jobs_p2a_1/2.txt by hostname) on bitacct-10 (16:15Z, 2 h) and bitacct-11 (16:10Z, 2 h);
      output runs/P2a. Then: CPU analysis scratch/p2_maps.py (hashed): 2 processes, e.g.
      python scratch/p2_maps.py 0 2 results/P2_maps_part0.json (and 1 2 ...part1.json); table + H2-H4 scores to write.
  (b) READY: PREREG Part U + gpu_src/scripts/run_unscr.py (hashed). Jobs: per pair (kind_nxL_sSEED_lL_local) and
      lam in {0.01 (linear and diag maps), 0.1 (linear)}: python scripts/run_unscr.py --pair ... --p1 /root/runs/P1
      --p2a /root/runs/P2a --out /root/runs/U --lam ... --smap ...; needs P1 and P2a .pt files on the VM (P1 .pt are in
      runs/P1 locally, 1.7 GB: copy only the needed l-cells into gpu_src/prior/P1, the P2a ones into prior/P2a).
  (c), (d): not started; (d) needs a noisy (Model S) version of run_vr.py.

## 12:35Z state (superseded)
- Phase 1 main cells: 159/159 done (runs/P1). Scores: python3 gpu_src/scripts/score_P1v2.py runs/P1 runs/P1X ->
  results/P1_scores.json + P1_table.md. Report: python3 scratch/build_report.py "<status>" assembles bit-accounting.md
  from results/P1_scores.json, notes/report_v2_head.txt, notes/report_v2_summary.txt (placeholders filled by
  scratch/summary_fill.py), notes/report_p1_method.txt, notes/report_v2_certs.txt and the v1 sections in notes/.
  Figures: /home/agent/.venvs/arc-noisy/bin/python scratch/report_P1.py.
- Reviews: r2a (code) and r2b (report) by gpt-6-astra applied (see the Process section and notes/DEVIATIONS.md).
- Post-pass (amendment P1-A, run_vr_cert2.py -> runs/P1X): VM 7 (until 13:26Z, forward order) and VM 8 (until 14:48Z,
  reversed order via /root/soup/rev_p1x.sh; its worker is SIGSTOPped and released by that script). VM 9 (1.9 h,
  post-pass only) launches automatically when VM 7 ends (scratch/launch_next.sh bitacct-7 bitacct-9 a 1.9h).
  Budget: $13.52 spent on VMs 1-6; VMs 7-9 at most ~$10.5; cap $25. No further VMs within the cap.
- When the post-pass ends (or VM 9 ends): pull (scratch/gpu_pull.sh bitacct-8 / bitacct-9), score, build the report
  with status "REPORT v2 (phase 1 final)", update the summary's CERT2 text with the explorer / wdec / centroid2 outcome
  (summary_fill.py has CERT2), close beads .20 .21 .13 .14 .22, note to main.
- Phase 2: P2.0 measurement (1) script ready (scratch/p2_identity.py, CPU, saved models). The other P2.0 parts need
  GPU training of codes at l+1: needs budget beyond $25 -> ask main.

## 05:10Z additions
- Review r2a (gpt-6-astra, review/review_r2a.raw, model verified): 'fixable issues', 8 major. Responses registered as
  amendment P1-A (PREREG end): post-pass gpu_src/scripts/run_vr_cert2.py (explorer local restarts with gates inside the
  cloud, width-n encoder + wide decoder, output-space residual centroid, held-out-power linear reference, gate
  activity) via queue gpu_src/staged/32_p1x.sh; scorer v2 gpu_src/scripts/score_P1v2.py (conservative crossings, R_r0
  and R*, not-covered vs fail, pending until complete). Feistel fix (clip to [-1, 1]) pushed before any feistel run.
- Follow-up VMs are automatic: scratch/launch_next.sh bitacct-5 bitacct-7 a 5h and bitacct-6 bitacct-8 b 5h (running in
  background): each waits for the old VM to vanish, runs scratch/prep_next.py (prior/P1 .json+.pt, prior/P1X, list
  reduced to unfinished jobs, stages 30_p1.sh + 32_p1x.sh), launches on-demand, un-stages, starts its pull loop.
- Final: python3 gpu_src/scripts/score_P1v2.py runs/P1 runs/P1X; python3 scratch/report_P1.py (update it to read
  score_P1v2 output: it reads results/P1_scores.json cells[...]['R'] which v2 also writes); report; round-2 review of
  the report (update review/prompt_r2_report.md for phase 1).

## Phase-1 status (04:50Z): RUNNING on VM 5 (list a, ends 08:23Z) and VM 6 (list b, started 04:43Z, ends ~09:43Z)
- VM 4 deleted 04:42Z ($3.50). 12 cells finished (relu 16x16 s5000 and s5001 local + output). Interim certificates on
  them: C1 restarts, C2 2x steps, C4 refit, C5 centroid, C7 linear reference all pass; C3_local (2x width) fails at
  l = 4-8 (width-n restriction binds); C6 (single-price models better by > 3%) fails on 20% of points -> registered
  fallback (R* includes the fixed points) is applied by score_P1.py.
- Monitors: scratch/pull_loop.sh bitacct-5 / bitacct-6 pull every 4 min into runs/P1/.
- When VM 5 ends (08:23Z): cells of list a not finished -> launch VM 7 (on-demand, GPU_PROVISIONING=STANDARD bash
  scratch/gpu_launch.sh bitacct-7 3h) with those jobs: copy runs/P1/*.json to gpu_src/prior/P1/, write
  gpu_src/queue_lists/jobs_a.txt with the unfinished jobs, add '*bitacct-7*) LIST=queue_lists/jobs_a.txt' to the case in
  gpu_src/staged/30_p1.sh, copy it into gpu_src/queue/ for the launch and move it back after the RUN line appears.
- Report v2 drafts: notes/report_v2_head.txt, notes/report_p1_method.txt; v1 sections 4-9 kept as background.
- Review prompt for round 2: update review/prompt_r2_report.md for the phase-1 report, then bash review/run_r2.sh.

## Phase-1 status (04:18Z, superseded): REGISTERED (PREREG Part P1 + P2.0, 04:01:43Z) and RUNNING
- VM 4 (spot, ends 04:41Z): list jobs_vm4 (relu 16x16/32x32 s5000); ~21 min per cell with 6 slots, so only the first
  cell of each job finishes; scratch/launch_vm6.sh (running, PID in logs) waits for VM 4 to disappear, runs
  scratch/prep_vm6.py (finished cells -> gpu_src/prior/P1; VM 4's unfinished jobs first in jobs_b), launches VM 6
  (on-demand, 5 h) and its pull loop.
- VM 5 (on-demand, 03:23Z, 5 h -> 08:23Z): list jobs_a (relu 16x16/32x32 s5001-5002, 32x8 all seeds; 77 cells at
  ~17 cells/h: a few may be cut at 08:23Z -> rerun them on a later VM; run_vr.py skips finished cells).
- After everything: python3 gpu_src/scripts/score_P1.py (-> results/P1_table.md, P1_scores.json), python3
  scratch/report_P1.py (-> results/P1_summary.md, figs/P1_curves_*.png), then the report (notes/report_v2_head.txt +
  notes/report_p1_method.txt are drafts of the new top).

## Phase-1 status (03:35Z, superseded)
- run_vr.py revised per Kelvin 03:20Z (identity anchor, upward lambda anneal, per-lambda loss normalisation, correlated
  prior, linear analytic reference = certificate C7). Dev check (seed 9100, 4 cells) running on VM 4 in
  /root/runs/P1_dev2 (first version's dev results in runs/P1_dev: the variable-rate model was 13-67% worse than the
  fixed-lambda models -> fixed by the normalisation). If C6 passes on dev2: append notes/P1_prereg_draft.txt to
  PREREG.md, hash PREREG.md + run_vr.py + score_P1.py, then push gpu_src/staged/30_p1.sh into the VMs' queue
  (scratch/gpu_pull.sh <run-id> gpu_src/staged/30_p1.sh) with run_vr.py and queue_lists/ (gpu_push.sh).
- VM 5 (on-demand, soup-gpu-bitacct-5, IP 35.247.82.21, timeout 5 h -> ~08:23Z) is up with an EMPTY queue (worker
  idles until a queue file arrives); list jobs_a. VM 4 list jobs_vm4 (until 04:41Z). VM 6 (list jobs_b) only after
  VM 4 ends (max 2 VMs). pull loops: scratch/pull_loop.sh bitacct-4 and bitacct-5 running.
- Phase 2 (registered with P1 as Part P2.0, Kelvin's near-identity hypothesis) runs only after phase 1 is final.

- Design + code: gpu_src/scripts/run_vr.py (to write: FiLM-conditioned encoder/decoder/prior on t = log10 lambda,
  per-example lambda log-uniform in [1e-4, 1], loss d/lambda + rate; evaluation on a 17-point lambda grid; variants
  base r0-r2 (batched), wide (2x widths), long (2x steps), fixed-lambda models at 0.1, 0.01, 0.001; refit prior;
  output-space centroid regressor at 3 lambdas; slopes). Register as PREREG Part P1 (hash in prereg_hashes.txt)
  BEFORE any evaluation run; CPU smoke on dev seed 9100 only.
- Per-lambda references already running/finished: S7 runs (runs/S_ent/E_*.json, gfix arm = fixed-lambda models at
  7 lambdas) for 16x16/32x32 s5000; S11 gfix-only S7 runs for tanh4/feistel/linear (runs/S11_*/E_*.json).

## GPU now: spot L4 soup-gpu-bitacct-4 (us-west1-b, IP 136.70.30.224), gpu-run timeout 4 h -> ends 04:41Z
- The worker (PID 1981 on the VM) is held with SIGSTOP so it cannot exit early (jobs run outside it); timeout ends
  the run at 04:41Z, then gpu-run.sh syncs runs/ and deletes the VM. To end earlier: ssh and `sudo kill -CONT 1981`
  after all jobs finished (worker then exits -> sync -> delete).
- Running there: S7 relu 16x16 + 32x32 seeds 5000-5002 all arms (PIDs 11063, 11254; s5000 first), VQ 32x32 (11284),
  S11 gfix-only S7 tanh4 (15795), feistel (15799), linear (15797).
- scratch/pull_loop.sh bitacct-4 pulls /root/runs every 4 min into runs/.
- SSH: ssh -i infra/state/soup_ed25519 soup@<IP> (sudo for /root). Push files: scratch/gpu_push.sh <ip> "" <paths
  relative to gpu_src>. Launch a VM: GPU_PROVISIONING=STANDARD bash scratch/gpu_launch.sh bitacct-5 4h (worker runs
  gpu_src/queue/*.sh; restore earlier JSONs from gpu_src/prior/<dir>/ as in queue/20_vm5.sh; every run script skips
  cells whose JSON exists). gpu_src/queue/20_vm5.sh is the OLD (pre-phase-1) plan: rewrite it for phase 1.

## CPU (nice 19, ionice -c3, <= 3 heavy processes)
- scratch/queue_arc_extra.sh: ARC sign codes (A1.7) 4000 l16 bin running, then 4001 l32/31/16 bin.
- chain_B.py arc 4000 (B-ARC) running, then 4001. Scorer scratch/score_BARC.py (hashed); dev: BA.2 hit, BA.1/BA.3 miss.
- scratch/posthoc_loop.sh (S2 chains), scratch/posthoc_s11.sh (S11 chains; those jobs were stopped, so it idles and
  exits after 3 h).

## Scorers (all hashed in prereg_hashes.txt before scoring)
scratch/score_A1.py, gpu_src/scripts/score_S1.py, score_S2.py, score_S34.py, score_S5to10.py (run from the work dir;
handles gfix-only cells), scratch/score_S11.py (S11.1-S11.5; S11.1/S11.2/S11.5 need phase-2 runs now deferred),
scratch/score_BARC.py. Report tables: scratch/report_*.py -> results/*.md.

## Deviations, review, beads
- notes/DEVIATIONS.md is complete up to 02:57Z (incl. the plan change and the jobs stopped).
- Review: round 1 done (review/review_r1.raw, model gpt-6-astra verified). Round 2 (review/run_r2.sh) to run on the
  phase-1 report; check the "model:" line in stderr; never fall back silently.
- Beads: lane pool-qxszj1.25; add phase-1 leaves under it (plan split), close each with one artifact.

## Next steps (in order)
1. Write run_vr.py + PREREG Part P1 + scorer; CPU smoke on dev seed 9100; hash; push to VM 4 and start the 16x16 /
   32x32 / controls cells there (kill the S7 all-arm jobs once s5000 is complete, by PID).
2. Launch VM 5 (and VM 6 if needed, 2 at once allowed) on-demand with a phase-1 queue covering all 12 nets + controls.
3. Score, tables (curves per layer, slopes, certificate flags), figure; update the report (phase 1 first).
4. Round-2 review; apply; note to main (3-5 lines); update this file.
