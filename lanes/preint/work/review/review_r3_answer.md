codex
**Verdict: minor revision.** The measured compute disadvantage survives. Checked **2026-11-02 17:24 UTC**, read-only: reran all five requested scripts in memory using the documented patterns; all six generated outputs, including `preint.md`, were byte-identical.

1. **R2-1: partly; minor.** Point/line scope and the untested-design qualification are fixed. However, [the summary](/home/agent/workspaces/mats/work/preint/preint.md:28) says ≥c/N for spectral share c; section 5 gives `(c/2 − corrections)/N`. **Fix:** preserve that coefficient or say “a constant depending on c.” Remove “only” from the claim that fitted exponents increased only on tiny nets; the wider raw fits also show increases.

2. **R2-2: resolved.** Registered MLMC filtering reproduces **P8 = 11/19** and **3 flags in 888 cells**. Tables agree; the deviation is recorded.

3. **R2-3: partly; minor.** Equivalence/asymptotic caveats are fixed. The actual follow-up is **seed 302, one additional N=512 row, eight replicates**; seed 304 is absent. [RESPONSE](/home/agent/workspaces/mats/work/preint/review/RESPONSE.md:50) incorrectly claims both seeds reached 512–1024. Section 4.3 correctly discloses the stoppage. Its fitted slope changes **1.15078 → 1.02573**, versus RQMC **0.97144**, as the fitting window shifts **16–256 → 32–512**. This is consistent with the proposed explanation, but does not establish it. **Fix:** reconcile RESPONSE, qualify the interpretation, and label **487× as PI_as**, not PI generally: best PI remains **386×**. The added row lies beyond RQMC’s cost range, so it adds no equal-cost comparison.

4. **R2-4: partly; minor.** All **56 records**, registered comparators and SVD scenario reproduce. Maximum exponent movements are **0.016887 / 0.026326 / 0.032532**; PI loses in every scenario. But [“charging what the line code does”](/home/agent/workspaces/mats/work/preint/preint.md:82) still overstates a model assigning **20 FLOPs per vertex** for sorting/ray work. **Fix:** call it an allowance-based sensitivity scenario; change the strict 0.026 ceiling to approximately 0.026 or ≤0.027.

5. **R2-5: resolved.** Section 3 disclaims an established SciPy scrambling guarantee, states the window’s `Cε/N` floor, and labels constructive rates as another algorithm’s bounds.

6. **R2-6: partly; minor.** Missing-method probes now produce PENDING; endpoint-only and one-replicate inputs fail completeness. However, [complete()](/home/agent/workspaces/mats/work/preint/scratch/score.py:54) still accepts missing replicate metadata, incorrect N and NaN variances; `alpha()` still fits four rows containing only three valid observations. **Fix:** validate metadata and finite observations before scoring, require four valid fit points, and withdraw “scorer completeness resolved.” Current saved rows pass these checks, so present results remain valid.

7. **R2-7: resolved as disclosure.** The t₇ comparison is illustrative, the tail magnitude is explicitly unmeasured, and the narrow-deep heading qualifies its empirical premise. These changes resolve the overclaims, not the underlying validation gaps.

8. **R2-8: partly; minor.** Current file comparisons confirm the stated equality/unused-option difference; historical loaded-module hashes remain unavailable. **Fix:** replace section 8’s “byte-identical for the code it used” with “current files match retrospectively”; freeze and record dependencies for future runs.

9. **R2-9: partly; minor.** The requested surrogate condition, cost range, reference names and exponent-gain labels are corrected. A remaining [headline ambiguity](/home/agent/workspaces/mats/work/preint/preint.md:24): **2–13×** describes small-net PI_as at the largest common budget; **15–91×** and **21–1,410×** summarize per-net minima. They are not ranges across every tested budget. **Fix:** name those summaries explicitly; observed best-PI ratios across all common budgets span approximately **1.16–110×, 14.6–716× and 21.3–2,956×**, respectively.
