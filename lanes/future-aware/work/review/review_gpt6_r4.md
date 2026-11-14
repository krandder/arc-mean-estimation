**Verdict: minor revision.** The substantive round-3 corrections are implemented and the revised gains reproduce. Remaining issues concern ledger precision, aggregation labels, and claims of a tie.

Checked read-only at **2026-11-02 17:40 UTC**, report SHA-256 `e309100d…`. Regenerated `hyb_direct.json`, `hyb_direct.md`, and `d1_ledger.json` **byte-for-byte in memory**; no files modified.

| Round-3 item | Status | Finding |
|---|---|---|
| D1 Cholesky extraction scenario | **Resolved** | Explicitly hypothetical; indefinite states, missing feasibility work, and untested accuracy are disclosed. “All work charged” is withdrawn. |
| H1 obsolete evaluation charges, duplicate closure, wrong mean-source cost | **Partly resolved** | All three identified defects are corrected. The sum ledger remains an approximate per-control accounting, with omissions below. |
| Closing half-width recommendation | **Resolved** | Uses completed guarded medians, including mean-field **0.92** at 256, and discloses failures. |
| Best fixed versus best per net | **Partly resolved** | Correct distinction introduced, but the following sentence still attributes best-per-net gains to the fixed control. |
| Sensitivity range at 64 | **Resolved** | Now separately reports **0.12**, without extrapolation. |
| D1 loss range | **Resolved** | **6–200×** identifies variant medians; **2.3–340×** identifies individual projected runs. |
| Retained factor 1.13 | **Resolved** | Corrected. |
| Order-4 ratio 1.65 | **Resolved** | Corrected in report and FORMAL addendum. |
| Six successful reruns | **Resolved** | Explicitly limited to the six checked successes. |
| Comparator-noise wording | **Resolved** | Observed range is distinguished from a confidence interval. The separate tie claim remains too strong. |

The inherited measurement-uncertainty item remains **partly resolved**: additional particle/pilot replicates and uncertainty estimates remain absent and acknowledged. I found no regression in the other carried-forward theoretical qualifications.

The sum ledger correctly replaces repeated control matrix products with accumulation plus a final application. Gaussian closure is reused for `jacmf`; choosing a `k2` mean adds the K2 charge while retaining the Gaussian work needed to construct that Jacobian.

However, it should be labelled an **approximate cost for one selected control**, not a literal count of everything v2 executes:

- [Scorer line 97](/home/agent/workspaces/mats/work/future-aware/scratch/score_hyb_direct.py:97) charges the final control application, but v2 separately computes `cQ` at [runner line 115](/home/agent/workspaces/mats/work/future-aware/scratch/run_hyb_direct.py:115). For linear controls, that is another approximately \(2n^2\) flops unless explicitly fused.
- Quadratic evaluation omits centering and counts triangular feature products, whereas `qfeat` constructs the full \(qk^2\) outer product before selecting its triangle. Its feature-extraction allowance also does not separately reconcile both eigensolves and dense products.
- Diagnostic work and construction of competing controls are excluded, reasonably for deployment costing, but that boundary should be explicit.

These limitations do **not** restore the round-3 accounting objection or materially change the winning linear control’s rounded gains.

For **n=256**, the recomputed §4.3 best-per-net medians are:

| Budget | Registered | Expanded | Sum |
|---|---:|---:|---:|
| 10,000 | 0.849640 | 0.825520 | 0.855191 |
| 65,000 | 0.977130 | 0.974314 | 0.997531 |

For fixed `1/jacmf`, the sum ledger gives \(B=1680.03125\), \(a=1.00006103516\), and gains **0.845165 / 0.997531**. Thus [§4.3’s prose](/home/agent/workspaces/mats/work/future-aware/future-aware.md:381) should identify **0.86** as best-per-net; the fixed-control value rounds to **0.85**.

Two final wording corrections:

- “Not distinguishable from a tie” implies an uncertainty analysis that is not supplied. Say **“near unity at 65,000 passes; statistical uncertainty was not quantified.”** At 10,000 passes, the reported median gains indicate approximately **5–15% losses**.
- [§4.4’s “every method … loses”](/home/agent/workspaces/mats/work/future-aware/future-aware.md:426) needs the H1 qualification: near unity against paired RQMC, approximately **1.02** against ARC’s curve.

Otherwise, the summary appropriately limits methods, widths, exploratory findings, descriptive trends, and assumed costs. **“No major positive demonstrated for the tested methods and widths” remains supported.**
