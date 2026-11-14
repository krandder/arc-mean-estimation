"""Review round 1, part 2: scorecard and process section (body6.md), FORMAL corrections, fills."""
import json
N = '/home/agent/workspaces/mats/work/gram-chain/notes/'
W = '/home/agent/workspaces/mats/work/gram-chain/'


def rep(path, pairs):
    s = open(path).read()
    for a, b in pairs:
        if a not in s:
            if b in s:
                continue
            raise SystemExit('NOT FOUND in %s: %s' % (path, a[:80]))
        s = s.replace(a, b)
    open(path, 'w').write(s)


rep(N + 'body6.md', [
    ("""| PB1 | closed relevance half-life and area within 30% of the mean field, n = 64-1024 | hit (scored with interpolation; first scorer version would miss at n = 256) |""",
     """| PB1 | closed relevance half-life and area within 30% of the mean field, n = 64-1024 | registered analysis missed (coarse grid; full-grid area integrates noise: -1.28 at n = 256, 66.7 at n = 1024); revised analysis hit (interpolated half-life, area truncated at 8 T*; chosen after seeing n = 256) |"""),
    ("""| PB4 | log|a| relevance above the direction's at every t >= 8, > 0.2 at t = n/2 | miss (noise at t >= 160 at n = 64, 256; holds at n = 1024) |""",
     """| PB4 | log|a| relevance above the direction's at every t >= 8, > 0.2 at t = n/2 | miss (both near zero at n = 64, t = 160-192, and n = 256, t = 1024; holds at n = 1024) |"""),
    ("""- Pre-registration as in section 9. Disclosed before Part A: exploratory runs at n <= 256 informed PA3, PA4, PA7.""",
     """- Pre-registration as in section 9. Disclosed before Part A: exploratory runs at n <= 256 informed PA3, PA4, PA7.
  Amendment A1 (21:33:29Z) was hashed before the n = 256 four-replica result existed but about six minutes after that run
  had started (21:27:34Z); I had not seen its output. Its n = 512 and 1024 tests are prospective."""),
    ("""  (7) Part C's header time was typed one minute ahead of its hash.""",
     """  (7) Part C's header time was typed one minute ahead of its hash; (8) the sharing runs (A-share) used a 2n burn-in and
  4n recorded layers instead of the registered 6n and 8n, omit t = 0.9, 0.99 at n = 1024, and were first scored against
  each run's own baseline instead of the registered A-r2 baseline (rescored with the registered one; every clause
  passes either way at n = 64, 256); the six-replica runs used half the registered chain budget; (9) the input vertex
  recursion first interpolated its Monte Carlo source on a coarse grid in c, which made it collapse at depth; recomputed
  by quadrature (`scratch/vertex_exact.py`), which changes the deep-layer comparison (section 4.1) but not the registered
  targets at l <= 64 by more than 2%; (10) log|a| needs a convention on the all-off output event (floors at 1e-300, which
  differ between Parts B and C); immaterial at n >= 64, fatal for the log channel at n = 16, which is not used."""),
    ("""- Review: {{REVIEW}}""",
     """- Review: GPT-6 (gpt-6-astra, fresh session, high effort, read-only; `review/review_gpt6_r1.md`, 00:10-00:15Z) on the
  near-final draft: verdict major revision, 14 findings (13 major or minor problems, one confirming that the central
  measurements and all 19 tests reproduce). It reproduced the n = 1024 stationary numbers, the four-replica PRs and PB5's
  98 of 100 clauses. Changes made: (1) the log|a| convention is stated and the "annealed raw quantities do not exist"
  claim narrowed to the divergent moments (section 1); (2) the vertex recursion's source is now computed by quadrature
  and section 4.1 no longer attributes its deep-layer gap to a breakdown of the 1/n expansion; (3) the scorecard tallies
  corrected (14 hits, 7 misses, 3 pending; 13 and 8 with PB1 as first analysed) and PB1 reported both ways; (4) Amendment
  A1's timing stated exactly; (5) the sharing-run deviations disclosed and PA5 rescored with the registered baseline;
  (6) the direction theorem restricted to perturbations of layer l with matched Gram relations, the Haar frame of the
  nonlinear relevance operator labelled HEURISTIC, output coordinates excluded (section 7); (7) the orientation bit
  count presented as a description length, with PR not equal to the rank and no claim that an estimator must encode it;
  (8) the tangent check described as one moment ratio, with the probe corrections; (9) V_P described as the full state's
  closed relevance for the output direction, PRs as annealed moment ratios, the radial share as a variance-component
  proxy; (10) "within a few percent" limited to the relevance curves, PR_C T* given at finite Q; (11) the cloud-size
  scatter statistic stated as a squared-CV reduction and R^2 (0.88-0.93); (12) 168 nets, c ranges, PB4's failing
  points, n = 8 PR conditioning, and the vertex normalisation corrected; (13) completion criteria for the pending items
  stated (section 2.4, 9). {{REVIEW2}}"""),
])

s = open(W + 'FORMAL.md').read()
if '7.13' not in s:
    s += """7.13 Corrections after the GPT-6 review (00:20Z) [C, following the review].
(a) 1.3 is a statement about perturbations of layer l: the joint law of the future responses depends on them only through
their Gram relations with the replicas. It does not by itself make the frame of the nonlinear, cloud-averaged relevance
operator Haar relative to the cloud; that, and the free-product formula built on it, are HEURISTIC (the frozen
Jacobian's transverse frame is Haar given the past, relevance lane Corollary 1b, PROVEN).
(b) 4.1's numbers: the source was interpolated on a 201-point grid in c, which near c = 1 makes it vanish linearly instead
of quadratically and collapsed the recursion at depth. By quadrature (`scratch/vertex_exact.py`, `results/vertex_exact.json`):
PR/n = 0.650, 0.417, 0.240, 0.133, 0.0732, 0.0397, 0.0211, 0.0110, 0.0057 at l = 1, 2, 4, 8, 16, 32, 64, 128, 256, tending to
1.5/l as derived; the statement "breaks down at l ~ n" in 4.1 is withdrawn.
(c) 7.12(a): the two-probe identity holds up to finite-dimensional corrections (probes in the n - 1 transverse
dimensions) and a ratio-of-means weighting; the tangent data check one moment ratio, not the spectral law.
(d) 7.10: PR_C x T* = 3n/2 is leading order; with finite-Q definitions it is 1.28n, 1.40n, 1.46n at the median radius
for n = 64, 256, 1024.
(e) 1.5: log|a| and a/|a| need a convention on the all-off output event (probability 2^-n); the runs floor radii at
1e-300, so log moments are regularised estimands.
"""
    open(W + 'FORMAL.md', 'w').write(s)

f = json.load(open(N + 'fills.json'))
f['REVIEW2'] = ''
f['PA5'] = 'pending (n = 1024 running); with the registered baseline every clause holds at n = 64 and 256'
f['PA5_TEXT'] = 'PA5 (registered baseline): every clause holds at n = 64 and 256; n = 1024 pending.'
json.dump(f, open(N + 'fills.json', 'w'), indent=1)
print('ok')
