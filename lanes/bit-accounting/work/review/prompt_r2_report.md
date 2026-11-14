You are an adversarial reviewer (fresh session). Read-only sandbox; do not modify files. Review the report
bit-accounting.md in this directory and its support: FORMAL.md (v1.2 section 4 lists the corrections made after your
round-1 review, review/review_r1.raw), PREREG.md + prereg_hashes.txt, notes/DEVIATIONS.md, GPU-LOG.md, results/
(tables and score files), runs/ (raw JSON), scratch/ and gpu_src/ (code), figs/.

Context: the lead asked how many bits a learned bottleneck at layer l needs so that decoding and running the rest of the
fixed net reproduces the output (sign bits or a noisy channel), and whether these correctly compressed bits get
scrambled from layer to layer. The report says: (1) with unrestricted encoders every layer needs the output's own bits
(shortcut); (2) restricted (one ReLU layer) encoders need many more bits at early layers; (3) jointly trained local code
chains are not scrambled (threshold maps reach the Bayes limit; relabelled null at the constant predictor) but lossy;
(4)-(6) the lead's curriculum autoencoder, the noisy regime with shared future noise, and estimation.

Check, and report numbered findings (each: severity major/minor, location, what is wrong, the fix):
1. Every number in the Summary and in sections 3-7: recompute at least eight from runs/ or results/ (e.g. an ARC
   linear-code count, a narrow-deep count, a small-net unrestricted and local count, a post-hoc threshold accuracy and
   its null, a one-step decoding nMSE, a deductive-estimator error, an S4 shared-noise number).
2. Overclaims: statements stronger than the evidence (the "not scrambled" conclusion given fitted lower bounds, few
   seeds, small code sizes, held-out vs in-sample; "the loss is information, not noise"; layer-dependence claims in the
   noisy regime; anything about ARC that was only measured on small nets).
3. Pre-registration: each prediction scored as registered? deviations disclosed? scorer hashes before scoring?
4. Whether the round-1 findings were actually applied (compare FORMAL v1.2 and the code with review_r1.raw).
5. Code bugs that would change a reported number (scratch/chain_posthoc.py, chain_onestep.py, report_*.py,
   gpu_src/scripts/*.py).
6. Is the answer to the lead's question stated plainly and correctly? Is anything missing that a careful reader needs?
Verdict: accept / minor revision / major revision. Be concrete and concise. Write everything to stdout.
