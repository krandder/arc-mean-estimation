You are gpt-6-astra acting as an independent co-prover (not a reviewer) on a mathematics and theoretical computer
science question. Read coprover/STATEMENT_r1.md in this directory (read-only sandbox; do not modify files; do not read
other files or directories: work only from that statement and your own knowledge). It states a setting (critical random
bias-free He-ReLU networks, width n, depth L; estimating the output mean over Gaussian inputs better than sampling), what
earlier lanes proved or measured, and four targets: (1) a computational model of layer-sweep estimators broad enough to
contain ARC-style closures, Gaussian closures with gate splits, branch-and-bound and multilevel shared-trajectory
samplers; (2) a definition of "the bits that matter at layer l", N(l, eps), accounting for the past (the state's law)
and the future (what later layers amplify), and lower bounds on state size or time in terms of it, with the
forward-only versus future-aware distinction; (3) an estimator matching the bound and its comparison with the best
multilevel sampler across depth regimes, with estimates of N(l, eps) for random deep nets; (4) which part of Kelvin's
"hash" argument survives and which fails.

Work independently: I want your own definitions, proofs and constructions, not a review (you have not seen mine).

Deliver, in this order, in plain text with numbered sections:
1. Target 1: the model, precisely, and where each of the four families sits (passes, state, per-layer work).
2. Target 2: your definition(s) of N(l, eps) (say why each is natural and how it accounts for past and future); the
   restriction(s) under which it is the right lower-bound parameter; lower bounds with full proofs (constants and
   hypotheses explicit), including any provable forward-only versus future-aware separation and its size.
3. Target 3: the matching estimator, its cost and error analysis, the comparison with the multilevel sampler, and your
   estimates of N(l, eps) for random deep nets (n, L, l, eps; sigma in the noise regime), each labelled.
4. Target 4: the hash argument, a precise true statement and a precise false one.
5. Any exact structure you find (identities, reductions, tight characterisations) as lemmas with proofs.
6. A conjecture ledger: for each step you cannot prove, the weakest precise conjecture that would close it, the
   conditional proof, whether it is a known open problem (references you are confident of; "unsure" otherwise),
   evidence for and against, and the cheapest numerical experiment that could refute it. Mark the single bottleneck.
7. Literature you are confident is relevant (streaming and communication lower bounds, quantization and rate-distortion,
   information-based complexity, Lyapunov/random matrix products, kernel quadrature, finite-width deep-network theory),
   one line each on what it gives here. Do not invent references; mark uncertain ones.

Be rigorous and concise. Prefer a correct weaker theorem to an incorrect strong one. Write everything to stdout.
