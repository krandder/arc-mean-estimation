You are an adversarial reviewer (fresh session). Read-only sandbox; do not modify files. Review the phase-1 method and
code of this lane while its evaluation runs are in progress (results will be judged later; find problems now).

Question being answered (the lead's words): "We need to really understand the bits of each layer, and we need to know
and be confident the representation is as good as reasonably possible, that is not a matter of low encoder capacity
or undertraining. So let us first individually encode each layer as well as possible. Ideally with a curve of how
many bits are needed for each level of accuracy at each layer." Nets: ARC 256 x 32 (noiseless He-ReLU, Gaussian
inputs) and narrow-deep 8 x 256. One lambda-conditioned variable-rate code per (net, layer, class); classes local (one
ReLU layer of width n, then affine) and unrestricted (MLP of width 4n on h_l and the exact output); real-valued code
with fixed unit Gaussian noise and an encoder-chosen gain; rate = E[log2 q(z|h) - log2 p(z)] with a learned prior;
distortion = output nMSE after decoding to a layer-l state and running the real rest of the net; certificates on every
curve; an analytic linear reference (water-filled powers on a future-weighted Jacobian spectrum, linear MMSE decoding)
that learned codes must match or beat.

Files: PREREG.md (Part P1 and amendments A1-A3; hashes in prereg_hashes.txt), gpu_src/lib/vrlib.py (nets, frames,
model, training, evaluation, refits, refinement), gpu_src/scripts/run_vr.py (driver), gpu_src/scripts/ref_curve.py
(analytic references), scratch/score_P1.py (scorer, registered), lib/vra.py (curve analysis), notes/DESIGN.md,
notes/QUESTIONS.md, notes/DEVIATIONS.md, gpu_src/queue/21_eval.sh (what runs). Dev outputs: runs/bitarc-2/LRCHK,
runs/bitarc-1/DEV2 (dev nets only).

Report numbered findings (each: severity major/minor, file:line, what is wrong, the fix). In particular:
1. Is the rate a valid upper bound on I(h_l; z), estimated correctly (exact E log q = -(K/2) log2(2 pi e); the
   standardisation z / sqrt(g^2 + 1) and its Jacobian; the unit lower-triangular map; the mixture; the refits in
   refit_rates and the choice of the minimum of four held-out estimates)? Any way the reported bits could be too LOW?
2. Is the distortion measured correctly (held-out inputs, the real net in fp32, nMSE normalisation, the output-cell
   clipping at 0, the refined decoder and its use as min(plain, refined) on a subset)? Any leakage?
3. Does the local encoder stay in its class for every fixed lambda (anchored weights interpolated in t; the relu(y + 8)
   start; the 'h1' start)? Does the unrestricted class contain what it should?
4. The analytic anchor: gains a = min(256, sqrt(ev/theta - 1)) with theta = lambda V / (2 ln 2), the MMSE decoder
   input scaling z g / (1 + g^2), the decoder offset frac(t) y*; the references in ref_curve.py (three spectra; is the
   comparison fair: same held-out data, real net, same rate estimator?).
5. Training: lambda annealing with anchor continuation, per-lambda loss normalisation, learning rates, per-model
   clipping, the output head on detached codes, CUDA graphs: bugs or choices that make curves worse than necessary.
6. The certificates and scorer: do C1-C8 test what they claim; bugs in score_P1.py / vra.py (envelopes, interpolation,
   tolerances, the use of restarts)? Anything that would make "as good as reasonably possible" an overclaim.
Verdict: sound / fixable issues / unsound. Be concrete and concise. Write everything to stdout.
