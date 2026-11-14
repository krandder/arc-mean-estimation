You are an adversarial reviewer (fresh session). Read-only sandbox; do not modify files. Review the phase-1 method and
code of this lane before its results are final.

Question being answered (the lead's words): "We need to really understand the bits of each layer, and we need to know
and be confident the representation is as good as reasonably possible, that is not a matter of low encoder capacity
or undertraining. So let us first individually encode each layer as well as possible. Ideally with a curve of how
many bits are needed for each level of accuracy at each layer." Plus: one lambda-conditioned variable-rate encoder per
layer; spot-check it against separately trained per-lambda models (it must not be worse); both encoder classes
(unrestricted, local = one ReLU layer of width n then affine); certificates on every curve; slopes (bits per halving of
the output error); an identity anchor annealed upward in lambda; a linear analytic reference (water-filled powers on
the cloud-averaged future-weighted Jacobian spectrum, linear MMSE decoding) that a learned code must match or beat.

Files: PREREG.md (Part P1 and P2.0 at the end; hashes in prereg_hashes.txt), gpu_src/scripts/run_vr.py (trainer and
all certificates), gpu_src/scripts/score_P1.py (scorer), gpu_src/lib/smallnets.py (nets, frames), notes/DEVIATIONS.md
(design history), notes/DESIGN.md (section "Phase 1 method"), runs/P1/*.json (12 finished cells), runs/P1_dev2/
(dev runs of the previous version), results/P1_table.md.

Report numbered findings (each: severity major/minor, file:line, what is wrong, the fix). In particular:
1. Is the rate a valid upper bound on the information I(h_l; z) and is it estimated correctly (one-draw KL with the
   conditional prior; the standardisation by sqrt(a~^2 + 1) and its Jacobian term; the triangular map)? Any way the
   reported bits could be too LOW?
2. Is the distortion measured correctly (held-out, through the real rest of the net, normalisation)? Any leakage
   between training and evaluation samples, or between the refit/centroid halves?
3. Does the local encoder stay in the registered class L^1(n) for every fixed lambda (FiLM, gain a~(t), wide variant)?
4. The analytic anchor and linear reference (theta = lambda V / (2 ln 2), gains, MMSE decoder, capacity-formula rate):
   correct? Is the linear reference evaluated fairly (same held-out data, real net)?
5. The certificates (C1-C7, KA1-KA3) and the scorer: do they test what they claim; any bug in score_P1.py (crossings,
   envelopes, the C6 fallback, tolerances)?
6. Anything that makes a curve worse than it needs to be (optimisation, lambda normalisation, anneal, capacity) that a
   cheap change would fix; and anything that would make the conclusion "as good as reasonably possible" an overclaim.
Verdict: sound / fixable issues / unsound. Be concrete and concise. Write everything to stdout.
