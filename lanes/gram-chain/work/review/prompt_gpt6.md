You are a GPT-6 reviewer (gpt-6-astra) of a research lane report. Fresh session; read-only; do not edit files. Be a
rigorous critic: find errors, overstatements, missing caveats, mislabelled evidence, and numbers that do not match the
files. Reproduce key numbers from the saved outputs where you can (small single-threaded computations only, a few
minutes each, /home/agent/.venvs/arc-noisy/bin/python).

Report under review: /home/agent/workspaces/mats/outbox/gram-chain-2026-11-01.md
Lane directory: /home/agent/workspaces/mats/work/gram-chain/ (FORMAL.md theory v2 with v1 frozen in coprover/;
PREREG.md with hashes in prereg_hashes.txt and hashed copies in coprover/PREREG_*_as_hashed.md; lib/gc2.py and
tests/test_gc2.py; scratch/ (run and scoring scripts); runs/ (JSON/NPZ outputs); results/ (scores); logs/
(including deviations.log); coprover/ (gpt-6-astra rounds, PROVENANCE.md); figs/).
Background: outbox/gram-chain-explainer-2026-11-01.md, outbox/stationary-numerics-2026-10-31.md,
outbox/input-bits-2026-10-31.md, outbox/kstar-frames-2026-10-30.md, work/relevance/FORMAL.md.

Check in particular:
1. Every summary claim: does the cited file support it, with the stated label (PROVEN / NUMERICAL / MEASURED /
   HEURISTIC / CONJECTURE) and provenance ([C], [A], [C+A])?
2. The pre-registration: were predictions hashed before their runs (compare hash times with run file times and the
   logs)? Are hits and misses scored as registered, with every deviation disclosed (logs/deviations.log)?
3. The scaling claims (angle n^{-1/3} fluctuations, radius ratio 1.887 n^{-1/3}, cloud participation ratio ~ n^{2/3}
   vs 1/k, relevance horizon ~ n^{1/3}, PR_rel = n/(tau + 2t), input-cloud PR ~ 1.5 n/l): are they supported by the
   ranges actually run, and are the asymptotic statements kept separate from the finite-n evidence?
4. Annealed vs quenched: are ratios of annealed means ever presented as per-net quantities? Are integrability issues
   (infinite raw-state moments) respected?
5. The "what the chain cannot account for" section: is the direction argument correctly scoped (perturbations at a
   layer, rotations about the replicas' span; not output coordinates)?
6. Anything a careful reader would be misled by.
Output: numbered findings with severity (major / minor / fine), each with the file evidence; then a one-line verdict
(accept / minor revision / major revision). Under 2,000 words.
