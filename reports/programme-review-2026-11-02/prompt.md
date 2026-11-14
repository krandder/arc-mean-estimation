You are reviewing a research programme for Kelvin, a MATS fellow. Read-only. Be a critical, constructive peer: give
insights, objections, and better ideas, not a summary.

Problem: ARC's estimation challenge. Given a random He-init ReLU MLP (width n = 256, depth L = 32, no biases, input
x ~ N(0, I)), estimate every output neuron's mean at better error-per-compute than sampling, or argue convincingly that
this is hopeless so ARC should update.

Read, in /home/agent/workspaces/mats/ (paths below):
- outbox/synthesis-draft-2026-11-02.md (state of evidence, both sides; its conflicts list; note C10 is now resolved by
  work/phase1-board/FINDINGS.md: the top public entry was public-set fitting; honest frontier ~6x MC).
- outbox/arc-update-2026-11-02.md (summary + sections 6-8), outbox/scale-mode-2026-11-02.md (summary),
  outbox/randomness-2026-11-02.md (TL;DR), work/preint/preint.md (summary), work/future-aware/future-aware.md (summary).
- outbox/overnight-report-2026-10-29.md, entries from 2026-11-02 13:00Z onward (latest direction and lane results).
- work/adaptive-regions/SPEC-learned-experts.md (the experiment Kelvin now wants: a layered, Gaussian-mixture-style
  mixture of linear experts, trained on populations of inputs, with confidence-weighted fusion, skip-layer experts and
  propagated "final joint confidence"; Kelvin accepts it may be far worse than sampling at small budgets and hopes it
  scales better at large compute).

Answer, in this order, at most ~1,200 words:
1. The single strongest objection to the learned-experts plan, and whether a cheap test could kill or rescue it.
2. What the spec gets wrong or leaves underdetermined (definitions, loss, accounting, the scaling-slope headline).
3. Can anything in this family have a better error-vs-compute exponent than sampling for a fixed net? Give the
   argument either way (information, approximation rates, the "W identifiable after ~nL evaluations" point).
4. Ideas we have not tried that you think are more promising, for the positive or for a convincing negative.
5. Anything in the evidence you think is wrong or overstated.
