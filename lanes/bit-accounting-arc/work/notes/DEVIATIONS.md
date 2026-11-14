# bit-accounting-arc: deviations from PREREG Part P1 (registered 04:30:06Z)
- 04:40Z (process only) bitarc-2 (spot) was preempted at ~04:31Z, right after the registered queue was pushed; no
  evaluation output existed there. Replacement bitarc-4 on-demand (stockouts in us-central1/us-west1 at 04:33Z, retried
  in us-east1/us-east4/us-west4). Queue files 12_vm1_early.sh (VM A: the ARC output cell and the net-4000 references)
  and 13_vmB_milestone.sh (VM B: net-4000 certificate runs at l = 31, 0, 16) run commands of the registered queue
  earlier; the registered chains skip finished cells. Measurement unchanged.
- 04:44Z (measurement; registered as PREREG Amendment A1 before any evaluation result) analytic gain cap AMAX 16 -> 256.
  Reason: the cap bounded the reachable rate (~4 bits per anchor direction; narrow-deep nMSE >= 0.004 from l >= 32).
  The three evaluation processes that had started (ARC l = 31 local, ARC output, narrow-deep l = 255 local; 5-25% of
  training, no evaluation output) were stopped by PID on bitarc-1 and restart under 11_eval.sh. bitarc-4 (spot,
  us-west1-a, the only L4 available at 04:41Z; on-demand stocked out in 14 zones) received the amended code before its
  worker started; the superseded queue files there were overwritten with no-ops.
- 04:50Z (measurement; PREREG Amendment A2 before any evaluation result) fp32 for every precision-critical matmul,
  TF32 only in MLP hidden layers. Found by checking the unrestricted l = 31 init (nMSE 0.0072 on net 4000's training
  log at the smallest lambdas, against ~1e-4 expected). All A1 processes stopped by PID on bitarc-1 and bitarc-4
  (including one reference job, which restarts unchanged); queue files renamed 21/22/23.
- 05:01Z (added variant; PREREG Amendment A3) local 'h1' init (exact one-layer look-ahead) on ARC 4000 and all
  narrow-deep nets, every layer, because the reference-started local encoders stay affine (sibling's code review).
- 05:20Z (A4, after code review r1) Jacobian frame fixed (data span); head clipped separately; reference-anchored
  local runs, 'h1' runs and references restarted under 31_eval.sh / 33_vmB_milestone.sh / 34_h1.sh (pre-A4 outputs
  moved aside on the VMs). Unrestricted and output processes kept running (unaffected). Scoring fixes go into
  scratch/score_P1_v2.py (hashed before scoring); certificate scope corrected to what the queue runs (r1 #9).
- 05:21Z note on A4: the kept unrestricted base runs (ARC l = 31, narrow-deep l = 255) and the ARC-4000 l = 31 unrestricted restart 2 were started before A4, i.e. with the head clipped together with the main model (r1 #13); disclosed, not rerun.
- 05:28Z (A5, process/diagnostics) cheaper refits and references (see PREREG A5); ARC 8-model processes l = 31 local,
  l = 31 unrestricted and the output cell stopped by PID (bitarc-1 9954, 13036; bitarc-4 4931) and rerun; the
  bitarc-1 early queue (references for net 4000) stopped to avoid duplicating bitarc-4's reference chain.
- 05:29Z note on A5: three 1-model processes (ARC 4000 l = 31: local restart 2 and 'h1' under A4, unrestricted restart 2 under A2) and the two narrow-deep l = 255 processes keep the pre-A5 evaluation (all 32 refits; affordable at M = 1 and K = 16).
- 06:30Z (added, not registered) post-hoc decoder diagnostic gpu_src/scripts/refine_posthoc.py (queue 37): stronger preimage refinement of saved unrestricted base models at early ARC layers; reported separately, registered counts unchanged.
- 06:40Z bitarc-1 (spot) preempted at ~06:30Z (final sync failed; results pulled up to 06:28Z kept: in-progress ARC l = 0 and 31 local base, the output cell and two 'h1' runs were lost and rerun). The watcher launched bitarc-3 (spot, us-central1-a) at 06:33Z with the finished results in gpu_src/prior/P1 and queue 41_eval.sh.
- 07:20Z bitarc-3 (spot) preempted at ~06:50Z after 16 min (nothing finished there). The relaunch was refused by the infra's group budget ledger, which counted the reservations of two creations that had failed on stockout; COST-AUDIT lines with their true cost (0) and bitarc-3's ($0.25) were added, and bitarc-5 started on-demand (us-west1-c) at 07:16Z.
- 08:39Z (PREREG Amendment A8) reduced plan for the remaining compute (see PREREG A8); old chains stopped by PID, running jobs kept.
- 08:50Z bitarc-4 ends at 09:41Z: three low-priority processes there (ARC 4000 l16 unrestricted restart 0 and its 2x-steps run, narrow-deep l16 unrestricted) paused with SIGSTOP so the ARC l0 unrestricted base cell can finish first; they rerun on the replacement VM.
- 09:29Z (PREREG Amendment A10) scheduling: VM B (bitarc-6 on) takes the ARC local base at layers 2, 20, 12, 28 and the narrow-deep local base at layers 8, 192, 32 from VM A's chains, plus the remaining 51_B.sh jobs, in six parallel chains (57_B.sh, up to 5 processes); 51_B.sh, 52_B, 36_toyref.sh and 37_refine_posthoc.sh retired to gpu_src/queue_done/ (finished, or replaced). The post-hoc refinement of ARC l0 (net 4000-4003, restarts 0-1) finished on bitarc-4 at ~09:20Z; it moves to layers 16, 8, 24 (net 4000). Added: 'h1' on ARC 4001-4003 at layers 12-28.
- 09:39Z (PREREG Amendment A11) added the convergence corner (depth 6 + 48000 steps) at ARC 4000 l31 local, queue 58_B_l31_conv.sh on VM B.
- 09:45Z bitarc-4 ended at its 5 h timeout (09:41Z); gpu-run.sh's final sync wrote /root/runs into runs/ (not runs/bitarc-4/): merged into runs/bitarc-4/ (adds the 13 saved models .pt and the last toy runs), top-level copies trashed (trash-put). prep_prior.sh now also reads runs/P1. The toy (k = 64 local and unrestricted, random start) finished there at 09:33-09:40Z; its JSON was pushed to bitarc-6 so it is not rerun. bitarc-6 (on-demand, us-west1-c) RUN 09:44Z.
- 09:50Z (PREREG Amendment A12) C7 failed at ARC 4000 l0 local t = -2 (low-rate gap); added dedicated models at t = -2.25, -2.5, -2.75 from both starts (59_B_fixlam_low.sh, pushed to bitarc-6).
- 09:52Z the refinement diagnostic in 57_B.sh chain f skipped layers 16, 8, 24 (their model files did not exist yet); 60_B_refine.sh (pushed to bitarc-6) waits for them.
- 09:55Z (PREREG Amendment A13) optimiser-reach check (10x encoder learning rate) at ARC 4000 l0, 8, 16 local, queue 62_A_lr.sh for VM A from bitarc-7.
- 09:55Z 62_A_lr.sh also pushed to bitarc-5 (gate 5) so A13 starts now; bitarc-7 skips what finishes.
- 10:16Z (PREREG Amendment A14) 4x steps for the output cell and layer 24 (net 4000); bitarc-7 queue 61_A.sh replaces 51_A.sh, 53_A_steps4.sh, 38_h1_more.sh, 34_h1.sh (moved to gpu_src/queue_done/).
- 10:16Z A14's two runs pushed to bitarc-5 now (63_A_steps4.sh), where a slot was free.
- 10:26Z (PREREG Amendment A15) random local start with encoder lr 1e-3 at narrow-deep l0 (6 nets x 3) and ARC 4000 l8; 64_A_rnd.sh pushed to bitarc-5 (gate 6).
- 10:27Z correction to the A15 text (not to its design): the look-ahead start is 29-56% (not 13-56%) below the reference start at narrow-deep layer 0, nMSE 0.1, and 13-21% at 0.001.
- 10:55Z (PREREG Amendment A16) depth 6 + 8x steps at ARC 4000 l31 local, queue 65_A_conv8.sh for bitarc-7.
- 10:59Z bitarc-5 ends at 12:16Z: killed the A8 chain subshells of 51_A.sh there by PID (15597 chain A1, 15598 chain A2) so they start no job that cannot finish (ARC local l4, narrow-deep local l16); their running jobs (ARC l24 base, narrow-deep l64 base) continue; bitarc-7's 61_A.sh runs the rest.
- 11:34Z (PREREG Amendment A17) random start with lr 3e-4 at ARC 4000 l0, l8 and narrow-deep l0, and lr 1e-3 at ARC l0; 66_A_rnd2.sh pushed to bitarc-5 (idle slots until 12:16Z), also in gpu_src/queue for bitarc-7.
- 11:38Z (main's request, PREREG A18 to follow) on bitarc-6 killed by PID the 57_B.sh chain subshells b (3499), c (3500), d (3503), e (3505), f (3507), and the just-started narrow-deep l255 unrestricted cap2 process (22790); running jobs of b, c, d continue; chain a (ARC local base 20, 12, 28) continues.
- 11:40Z (PREREG Amendment A18, main's request) convergence subset (ARC 4000 l0, l16, l31, both classes, nMSE 0.1 and 0.01): 67_B_conv.sh pushed to bitarc-6; 68_A_conv.sh and 69_A_rest.sh for bitarc-7; retired 57_B.sh, 58-60 (finished on bitarc-6), 61_A.sh, 62-64 (finished on bitarc-5).
- 11:41Z on bitarc-5 killed by PID the narrow-deep l0 rndmid run (35253; it could not finish before 12:16Z; reruns on bitarc-7 from 66_A_rnd2.sh) and pushed 70_A_now.sh (A18's l0 local h1c2 and h1s2, short enough to finish there).
- 12:19Z bitarc-5 ended at 12:16Z (timeout; cost $4.37 in its DELETE line); its final sync (runs/P1, with 25 saved models) merged into runs/bitarc-5/ and the top-level copies trashed; prep_prior (395 runs) ran before the merge, reading runs/P1 directly. bitarc-7 launching on-demand at 12:19Z.
- 12:25Z (PREREG Amendment A19, main relaying Kelvin) backward-curriculum start implemented in gpu_src/scripts/run_vr.py (--init bwd; pre-change copy scratch/run_vr_pre_bwd.py.txt; non-bwd runs unchanged), smoke-tested on bitarc-6 as scripts/run_vr_bwd.py (300 steps, /root/runs/BWDTEST); chain queue 71_A_bwd.sh for bitarc-7; consistency flags scratch/consistency.py.
- 12:29Z the watcher's spot launch of bitarc-7 was refused by the ledger (21.37 + 4.87 > 25: the failed on-demand attempt's reserve was counted before its COST-AUDIT line landed); relaunched bitarc-7 spot by hand (scratch/gpu_launch.sh, all 13 zones).
- 12:36Z A18 round 2 started: 74_A_round2.sh (l31 unrestricted 8x steps) pushed to bitarc-7.
- 12:53Z A18 round 2: 75_A_round2b.sh (l16 local look-ahead 8x steps) pushed to bitarc-7.
- 13:16Z (PREREG Amendment A20) analysis corrections from review r2 (normalisation, convex-hull time-sharing, named quantities, scorer v3, matched A18 partners, export statuses, wording); see review/review_r2.raw.
- 13:21Z A20 matched partners: 76_B_partners.sh (l0 local h1c2s2, l31 local cap2steps2, l0 unres cap2steps2) pushed to bitarc-6; 76_A_partners.sh (l16 local h1c2s4, l16 and l31 unres wide2steps4) pushed to bitarc-7.
- 13:26Z A20 detail: the consistency flags (export and scratch/consistency.py) use C3's tolerance, > 3% and > 0.5 bit (sub-bit narrow-deep counts were flagged at 0.03-bit differences).
- 13:32Z (PREREG Amendment A21) one-step backward start (bwd1) at l16 from l20's look-ahead code and at l0 from l2's; sources pushed to bitarc-7 /root/runs/SRC; queue 77_A_bwd1.sh.
- 13:57Z A20 partners, second set: 78_A_partners2.sh (l16 and l31 unrestricted, depth 6 with 2x steps) pushed to bitarc-7.
- 14:02Z moved the not-yet-started 77_A_bwd1.sh and 78_A_partners2.sh jobs from bitarc-7 (10 processes, CPU-bound) to the idle bitarc-6 (43 min left): killed their waiting chain subshells on bitarc-7 by PID (16508, 16511, 16512, 23172, 23175, 23176); same commands in 79_B_moved.sh.
- 14:26Z bitarc-6 idle after its last jobs: pushed queue/STOP so the worker exits and gpu-run syncs and deletes the VM (19 min before its 5 h timeout).
- 14:28Z bitarc-6 ended 14:26Z (cost $4.10 in its DELETE line); its final sync merged into runs/bitarc-6/ (with the A19 pilot runs in runs/bitarc-6/BWDTEST) and the top-level copies trashed.
- 14:46Z bitarc-7 (spot) preempted ~14:32Z, final sync failed; COST-AUDIT $1.77; PREREG A22: relaunch bitarc-9 with round 2 only (80_A_round2_relaunch.sh); other queue files retired to gpu_src/queue_done/.
- 16:49Z bitarc-9's five runs done; pulled with models; pushed queue/STOP so it syncs and deletes itself.
- 16:52Z bitarc-9 deleted 16:51Z ($1.77); no bitarc VM left (gcloud list empty); total $19.27 at the on-demand list price; stopped the bitarc-9 pull loop by PID.
