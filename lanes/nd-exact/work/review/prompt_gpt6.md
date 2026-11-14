You are a rigorous, independent reviewer (read-only). Review the research report `nd-exact.md` in this directory
(work/nd-exact/) and the code and data behind it. Be adversarial: look for wrong claims, unfair comparisons, hidden
setup cost, bias, bugs in code that change conclusions, overclaiming, and missing alternatives that would change the
verdict. Check numbers against the run files.

Context (the brief this lane was given): for plain ReLU nets of width 8 and depth 256 without biases (W iid N(0, 2/8),
x ~ N(0, I_8), sigma = 0, healthy seeds 203, 216, 217, 220, 221, 223), find a sample-free (deterministic) estimate of
E[a] (a = the 256th layer's output, an 8-vector) that beats Monte Carlo and randomized QMC at equal compute, or give a
precise account of where it cannot. Kelvin's question: "Maybe we can use that to 'solve' things exactly for the narrow
deep networks that we can afford to do (much less than 40 bits)?", referring to the earlier finding that the layer-32
state is nearly a ray. Suggested route: reduce to the radius; measure how the sphere's mass splits over activation
regions; integrate region by region if few; otherwise test coarse deterministic codes and report their slope in bits
per halving of error against sampling's 2. The coordinator later relayed Kelvin's framing: regions are gate patterns,
each contributing exact Gaussian mass times the linear map at its conditional mean; merge what the downstream treats
alike; carry mass and moments per class; compose linear maps where gates are constant; report error against the
number of classes; optionally an unbiased version with an MC correction.

Files: `PREREG.md` and `prereg_hashes.txt` (registration times; check they precede the runs they cover, using file
times in runs/ and logs/), `frozen/` (the code that produced the scored runs), `lib/` (ndx.py, cubesphere.py, cs2.py,
cs2tree.py), `tests/`, `scratch/` (census.py, truth.py, baselines.py, run_cs2.py, region_code.py, run_unbiased.py,
depth1_rate*.py, preimage.py, kink_distance.py, score.py, score_a1.py, report_tables.py), `runs/` (JSON results),
`results/` (scores.json, scores_a1.json, tables.md, census_table.md), `logs/`. Earlier lanes' reports for context:
/home/agent/workspaces/mats/outbox/relevance-accounting-2026-11-01.md (sections 8-9),
/home/agent/workspaces/mats/outbox/narrow-deep-m1-2026-10-30.md.

Please check in particular:
1. The exactness claims: homogeneity reduction; E[a] = J_c E[h_c] under a single live downstream class; that
   certified cells in cs2.py are truly exact (interval arithmetic in gnomonic coordinates; factored maps; the tail cone
   K and the containment test); the Gaussian cone moments (one-dimensional integral formulas, quadrature accuracy).
2. The cost accounting (1 mv = 128 FLOPs): is anything uncharged or overcharged in a way that would change a verdict
   (setup, moments, lookups, inverse-normal transforms, the 9 mv per region for the region code)?
3. Fairness of the comparisons: RQMC, RQMCJ (c = 48 chosen from the census), RADQ; replicate counts; interpolation;
   truth accuracy (about 1e-9 nMSE) relative to the errors scored.
4. The region-code bound: is the held-out construction sound, is calling it optimistic for exact methods justified,
   and does it support the claim that region-by-region exact solution cannot beat RQMCJ here?
5. Whether the deterministic code is a fair attempt (refinement rules, cell shapes, the stuck-cell issue fixed in
   Amendment 1), and whether a clearly better deterministic method exists that the report should have tested.
6. The explanation (dimension: 7 angular dimensions, distance to the nearest kink, one-layer width study) and whether
   the report overstates it.
7. The registered tests T1-T6: scoring code matches the text; verdicts as reported.
Give a verdict (accept / minor revision / major revision), then numbered findings, each with severity, evidence
(file and line or numbers) and the fix. State the model you are running on in your first line.
