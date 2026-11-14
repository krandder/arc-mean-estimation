You are an adversarial reviewer (fresh session; you have not worked on this lane). Read-only sandbox; do not modify
files. This is round 1 (theory only); the report comes later. Review FORMAL.md in this directory (bit-accounting lane:
learned per-layer bottlenecks for fixed random ReLU nets, and a "scrambling" test on chains of codes), together with
QUESTIONS.md and DESIGN.md in notes/, PREREG.md, and the code it refers to (lib/bitlib.py, lib/lincodes.py, lib/rwf.py,
gpu_src/lib/smallnets.py, gpu_src/scripts/run_curves.py, run_chain.py, run_kelvin.py, run_noisy.py).

Context: the question (from the project lead) is how many bits a learned bottleneck at layer l needs so that decoding
and running the rest of the fixed net reproduces the output to relative error eps, and whether these correctly
compressed bits get scrambled from layer to layer. FORMAL.md claims that with unrestricted encoders every layer of a
noiseless net needs the output's own bits (a sandwich between free and support-restricted output-space codes), that
the optimal chain is then the identity, and that the question only has content for restricted encoders (one ReLU layer
of the net's width) or under shared future noise (common random numbers) in the noisy regime.

Check, and report numbered findings (each: severity major/minor, location, what is wrong, the fix):
1. Every claim labelled PROVEN: correct? hypotheses complete? In particular section 1.2 (the sandwich, the inclusions
   A_0 subset ... subset A_{L-1} = R_+^n, the factor-4 reachability bound, the channel version with randomised
   encoders and an average power constraint), 1.3 (what C counts), 1.4 (Gaussian worst case; the linear analog scheme
   attaining R_G exactly for any source), 2.1 (the degenerate chain), 3.1 (one ReLU layer of width n contains h_{l+1}).
2. Is the definition of the restricted class precise enough to make "bits at layer l" a well-defined quantity? Is
   there a cleaner restriction that answers the question as asked? Is the claim that shared-noise scoring blocks the
   shortcut correct (the noisy future F_l(h, Xi) depends on noise the encoder cannot see)? State exactly what the
   shared-noise count measures.
3. The scrambling test: are the basis-invariant statistics (polynomial-threshold degree and juntas on reachable codes,
   H(c_{i+1} | c_i), coverage) invariant under the stated group? Is anything more invariant and still informative?
   Is the comparison with baselines (random permutation, invertible XOR, 2-juntas, dense LTF) on the same reachable
   codes fair? What can the exact Walsh spectrum over all 2^b codes (including unreachable ones) mislead about?
4. The nested scores in run_noisy.py: mean <= Gelbrich W2^2 <= crn and avg <= crn. Are they exact? Is the avg
   estimator unbiased? Is the Gelbrich formula implemented correctly?
5. Code bugs that would change a number (water-filling, straight-through estimators, masks, the evaluation of nMSE and
   of the mean error, the deductive estimator in run_chain.py, the decoder initialisation, whitening).
Verdict: accept / minor revision / major revision. Be concrete and concise. Write everything to stdout.
