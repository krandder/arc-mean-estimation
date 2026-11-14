"""Post-hoc check (after the review of the depth-1 rerun): do any of the 16 initial face cells get priority zero
(centroid output zero and zero a priori distortion), which would leave them unrefined in CS2/CS2b?
For each evaluation net: face, P, |f(centroid)|, priority used at setup. Usage: check_faces.py"""
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/lib')
import cs2  # noqa: E402
import ndx  # noqa: E402

for s in ndx.EVAL_SEEDS + [103, 111]:
    Ws = ndx.make_weights(s)
    est = cs2.CS2(Ws, c0=32, Q=32, rule='surplus', floor=0.01)
    est.setup()
    pr = sorted([(-h[0], h[2][0], h[2][1]) for h in est.heap])
    zero = [(i, sg) for p, i, sg in pr if p == 0.0]
    print(s, 'faces open', len(est.heap), 'certified', est.n_cert, 'zero-priority faces', zero,
          'min priority %.2e' % pr[0][0] if pr else '')
