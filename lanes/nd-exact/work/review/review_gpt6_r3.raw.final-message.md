<!-- Extracted: the reviewer/co-prover model's final message only. The full session dump (prompt echo, tool calls, intermediate output) is not in this repo. Source file: work/nd-exact/review/review_gpt6_r3.raw -->

Model: GPT-6. **Verdict: minor revision.**

Checked read-only at **2026-11-02 05:48 UTC**. R2 findings **1, 2, 4–7 and 10 are fixed**; **3, 8 and 9 retain minor issues below**. Sobol statistics, CS2c slopes/improvements, certification counts, and all 18 paired means/intervals reproduce. `results/tables.md` matches regeneration in memory.

1. **Minor — R2 #9: setup charge still mismatches the text.** [Section 9](/home/agent/workspaces/mats/work/nd-exact/nd-exact.md:367) claims NOCELL pays **3,200–3,800 mv**, but the implementation charges only `K['flops']/128`: **1,055–1,694 mv**. It omits the direction-selection probes, including **512 forward mv**. **Fix:** charge the necessary setup and report that amount; the conclusion should survive.

2. **Minor — R2 #8: section 10 mixes checkpoints.** [The width-8 claim](/home/agent/workspaces/mats/work/nd-exact/nd-exact.md:386) combines **131,000 cells** with a **50,000×** loss. The measured **46,122–50,074×** comparison is at **8,192 cells**; the 131,072-cell checkpoint exceeds RQMC’s measured cost range. **Fix:** separate those observations.

3. **Minor — R2 #3: the probability statement remains too categorical.** [Section 2](/home/agent/workspaces/mats/work/nd-exact/nd-exact.md:128) presents **7e-7** as a 95% upper bound despite selecting the cut using that census. **Fix:** call it a fixed-cut zero-event benchmark, without post-selection coverage guaranteed.

4. **Minor — section 10 still generalizes beyond the evidence.** “[No unit-wise shortcut](/home/agent/workspaces/mats/work/nd-exact/nd-exact.md:384)” at depth 2 is not established; “[sampling … rate … does not depend on dimension](/home/agent/workspaces/mats/work/nd-exact/nd-exact.md:392)” applies to normalized plain-MC MSE, not generally RQMC. **Fix:** say no shortcut was demonstrated here and scope the rate claim to MC.
