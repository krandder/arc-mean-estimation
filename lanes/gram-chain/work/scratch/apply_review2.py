"""Apply GPT-6 review round 2 residuals."""
import json
N = '/home/agent/workspaces/mats/work/gram-chain/notes/'


def rep(fn, pairs):
    p = N + fn
    s = open(p).read()
    for a, b in pairs:
        if a not in s:
            if b in s:
                continue
            raise SystemExit('NOT FOUND in %s: %s' % (fn, a[:80]))
        s = s.replace(a, b)
    open(p, 'w').write(s)


rep('head_template.md', [
    ("DRAFT IN PROGRESS (four runs still landing: PA5 at n = 1024, PA7, PA8, PA9, PB5 at n >= 256; GPT-6 review pending).",
     "{{STATUS_LINE}}"),
    ("""weight-averaged theory: the exact chain confirms its relevance curves to within a few percent and its other laws to
within 10-30%, and real nets follow it once each net's radius is used.""",
     """weight-averaged theory: the exact chain confirms its closed-relevance curves to within 0.003-0.014 (absolute) at
n = 256-1024 and its other laws to within 10-30%, and real nets follow it once each net's radius is used."""),
    ("""amplified directions sit in random relative position, so dimensions combine harmonically,""",
     """amplified directions sit in random relative position (PROVEN for the frozen Jacobian given the past, HEURISTIC for
the full nonlinear relevance operator), so dimensions combine harmonically,"""),
    ("""4. **How much the state at layer L - t matters, and for how long, stationary** (HEURISTIC [C+A]; NUMERICAL; PB1, PB2 hit).""",
     """4. **How much the state at layer L - t matters, and for how long, stationary** (HEURISTIC [C+A]; NUMERICAL; PB2 hit, PB1
   hit only under the revised analysis)."""),
])

rep('body2.md', [
    ("""  independent noise afterwards. It is what any description of h_l can explain about E[a] (the relevance lane's memory""",
     """  independent noise afterwards. It is what any description of h_l can explain about the conditional mean of the output
  direction u (for E[a] itself see 3.2: the radius carries the rest) (the relevance lane's memory"""),
    ("""3.1 How much and for how long: the direction (HEURISTIC mean field [C+A]; NUMERICAL; PB1, PB2 hit). Two replicas that""",
     """3.1 How much and for how long: the direction (HEURISTIC mean field [C+A]; NUMERICAL; PB2 hit, PB1 hit only under the
revised analysis). Two replicas that"""),
    ("""variance-weighted participation ratios); the radius carries a share rho(q) of the raw output variance for order n layers.""",
     """variance-weighted participation ratios); the radius carries a share rho(q) of the output variance (small-fluctuation
variance proxy, HEURISTIC) for order n layers."""),
    ("""Given the past, the future's singular frame is Haar relative to the cloud (section 7), so in the linear
regime the relevant covariance has the free multiplicative convolution""",
     """Given the past, the frozen future Jacobian's transverse singular frame is Haar (section 7, PROVEN);
assuming the same for the full relevance operator (HEURISTIC), in the linear regime the relevant covariance has the free
multiplicative convolution"""),
])

rep('body5.md', [
    ("""  the replicas (rotations of layer l fixing the replicas, or the mean direction, leave it unchanged). So the chain, which""",
     """  the replicas (rotations of layer l fixing the replicas leave it unchanged). So the chain, which"""),
    ("""- What this means for M1 (interpretation, not a bound). The chain says how much of the output's variance each layer's
  state decides, for how long, and in how many directions. An estimator that integrates the layer-l state against its
  future without sampling would need per-net information about those directions: for the frozen Jacobian their frame is
  Haar given the past apart from the state's own direction (PROVEN), and for the full relevance operator that is the
  free-product heuristic. The description length is about k(n - k) log2(1/eps) bits per layer with k of the order of
  n/(n/PR_C + c t), order n^{5/3} log2(1/eps) near the output in the stationary regime. This adds a mechanism to the earlier
  lanes' finding that structured sampling gains constants but no width-growing rate in the stationary regime; it is not
  a lower bound on estimators, which is the bits-bounds lane's question.""",
     """- What this means for M1 (interpretation only). The chain says how much of the output's variance each layer's state
  decides, for how long, and with what participation ratio. It says nothing about which directions, and for the frozen
  Jacobian those are Haar given the past apart from the state's own direction (PROVEN). If a method had to encode a
  generic rank-k relevant subspace per layer, that would cost about k(n - k) log2(1/eps) bits; the measured moments do
  not establish the required rank k (a participation ratio is not a rank), and nothing here shows that estimating the
  mean requires encoding any subspace. Whether it does is the bits-bounds lane's question."""),
])

f = json.load(open(N + 'fills.json'))
f['STATUS_LINE'] = ('Status: complete except PA5 at n = 1024 (its per-layer and antithetic parts were still running at '
                    'the final check; every available clause passes) and the dropped or late three- and six-replica runs '
                    '(PA7, the third-moment part of PA8). Revised after two GPT-6 reviews (section 10).')
json.dump(f, open(N + 'fills.json', 'w'), indent=1)

# body1: registered-baseline mean orders at n = 256 (round 2 finding 17)
rep('body1.md', [
    ("""| 16 | 0.182, 0.386, 0.630 | 0.186, 0.389, 0.632 | 0.193, 0.406, 0.654 | 2.80 / 2.54 / 1.90 | 1.603 |
| 64 | 0.179, 0.383, 0.616 | 0.183, 0.383, 0.617 | 0.187, 0.389, 0.629 | 3.45 / 3.44 / 2.60 | 1.583 |
| 256 | 0.186, 0.368, 0.606 | 0.173, 0.374, 0.610 | 0.177, 0.380, 0.613 | 4.10 / 4.11 / 3.38 | 1.587 |""",
     """| 16 | 0.182, 0.386, 0.630 | 0.186, 0.389, 0.632 | 0.193, 0.406, 0.654 | 2.79 / 2.54 / 1.90 | 1.603 |
| 64 | 0.179, 0.383, 0.616 | 0.183, 0.383, 0.617 | 0.187, 0.389, 0.629 | 3.45 / 3.44 / 2.60 | 1.583 |
| 256 | 0.186, 0.368, 0.606 | 0.173, 0.374, 0.610 | 0.177, 0.380, 0.613 | 4.06 / 4.06 / 3.34 | 1.587 |"""),
    ("""(block) mean order is the smallest and grows like n^{0.21} (1.90 to 3.38 from n = 16 to 256), the slope of the numerics""",
     """(block) mean order is the smallest and grows like n^{0.21} (1.90 to 3.34 from n = 16 to 256), the slope of the numerics"""),
])
rep('body4.md', [
    ("""finite-eps block order 1.90, 2.60, 3.38 at n = 16, 64, 256 (slope 0.21; a lower bound)""",
     """finite-eps block order 1.90, 2.60, 3.34 at n = 16, 64, 256 (slope 0.20; a lower bound)"""),
])
rep('head_template.md', [
    ("""(chain's finite-eps block order 1.90, 2.60, 3.38 at
   n = 16, 64, 256, slope 0.21,""", """(chain's finite-eps block order 1.90, 2.60, 3.34 at
   n = 16, 64, 256, slope 0.20,"""),
])
print('ok')
