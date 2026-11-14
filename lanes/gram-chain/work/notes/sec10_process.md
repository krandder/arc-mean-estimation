## 10. Process

- Co-prover gpt-6-astra (`coprover/PROVENANCE.md`; every raw log shows "model: gpt-6-astra"). Explainer check
  (20:51-20:56Z, high effort): 27 findings, 13 errors, all applied to the explainer. Round 1 (21:07-21:31Z, xhigh,
  independent: told not to read this lane's directory): agreed independently on the scaling limit, the 1.887 n^{-1/3}
  radius ratio, the 5/8 spectral gap, the relevance curves, the free-position formula and the input vertex recursion; new
  from it: the closed form m(q), the second-order angle coefficient, the n^{2/3} cloud dimension (the most consequential
  addition; I re-derived it and registered it against 1/k in Amendment A1 before the decisive runs), the radius-ratio
  floor under shared noise, and the tau^{-3} vs tau^{-5} annealed/quenched contrast. My theory v1 was frozen at 21:14:08Z,
  before its answer existed.
- Pre-registration: Parts A (21:15:54Z), B (21:21:14Z), C (21:24:21Z), Amendments A1 (21:33:29Z) and C1 (21:51:59Z), each
  hashed before the runs it covers (`prereg_hashes.txt`; copies `coprover/PREREG_*_as_hashed.md`). Disclosed before Part A:
  exploratory runs at n <= 256 informed PA3, PA4, PA7.
- Deviations (`logs/deviations.log`), none hidden: (1) partB.py's input-mode alive flag was always true (fixed 21:30Z;
  affected only the n = 8 extinction field and n = 8 direction statistics; the buggy output is kept); (2) the registered
  R = 8 closed-PR design shared futures across the two past pairs, which biases the closed estimator; replaced by a
  10-replica four-future design before any pr run (registered copy kept); (3) queues restructured to respect the
  two-process limit under load 20-34: r6 at n = 256 and r3 at n = 512, 1024 dropped, share at n = 1024 run last; (4) an
  inputVP mode (small-sigma closed relevance in the input regime) was added after registration and is descriptive;
  (5) Part C's header time was typed one minute ahead of its hash.
- Compute: CPU only, nice 19, ionice -c3, at most two heavy processes (the machine's load was 20-34 throughout), one BLAS
  thread; no GPU.
