You are an adversarial reviewer (fresh session). Read-only sandbox; do not modify files. Review the phase-2 parts of
the report bit-accounting.md: Summary point 8 and sections 3.1-3.5 (P2.0 parts 1-5, the unscrambling Part U, the P1-B explorers), plus
the P1-B explorer outcome where the summary reports it. Support: PREREG.md (Parts P2.0, P2.0-a, P2.0-b, U, P1-B at the
end) and prereg_hashes.txt; scripts scratch/p2_identity.py, scratch/p2_maps.py, scratch/report_P2_maps.py,
gpu_src/scripts/run_unscr.py, scratch/report_U.py, gpu_src/scripts/run_vr_noisy.py, scratch/p2_noisy_maps.py,
gpu_src/scripts/run_vr_cert3.py, gpu_src/scripts/score_P1v2.py; results in results/P2_identity_table.md,
results/P2_maps_table.md + P2_maps_all.json, results/U_table.md + U_scores.json, results/P2_noisy_maps.json +
P2_noisy_scores.json, results/P1_scores.json; raw runs/P2a, runs/U, runs/N, runs/P1Y.
Context: the lead's question is whether correctly compressed bits get scrambled from layer to layer, asked in two
forms: (Kelvin) "comparing these two transformations (actual activations l -> l+1) and (bit-optimal encoding l -> l+1)"
and "only later we try to unscramble ... we're forcing them not to be [scrambled]". The coordinator asked for results
in "certified-linear" terms (cost of a linear piece; saving of a learned mixture of linear pieces) and the unscrambling
result led by the price of forcing per mu, ReLU against the chaotic tanh control.
Report numbered findings (severity, location, what is wrong, fix), concisely:
1. Recompute at least eight numbers in these sections from the raw files (e.g. an affine R^2 of a code map, a gate
   tracking share, a rotation cos^2, a price of forcing at mu = 1 and 3 for ReLU and tanh, a U-score count, the H5
   count, a P1-B saving).
2. Is "price of forcing = change in Lagrangian / lambda" a fair reading of extra bits at fixed distortion here? Any
   bug in run_unscr.py (penalty, normalisation, control) or report_U.py that changes the conclusion?
3. Overclaims: especially that one-step simplicity does not separate ordered from chaotic nets while the price does
   (one tanh seed; few active directions at late layers); anything about Kelvin's hypothesis.
4. Pre-registration: scripts hashed before reading results; predictions scored as registered.
Verdict: accept / minor revision / major revision. Write everything to stdout.
