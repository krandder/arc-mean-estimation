"""Run the deterministic cube-sphere code on one net and record its anytime error curve.

E[a] estimate = J_c * CS estimate of E[h_c]. J_c = Jacobian of layers c+1..256 along u*, u* = the normalised CS estimate
after the 16 initial face cells (deterministic). All work is charged: cells (moments, certification, centroid passes),
the tail Jacobian ((256 - c) x 8 mv), priorities. Checkpoints at cost 2^k mv.
Usage: run_cs.py SEED C LOG2BUDGET RULE OUT.json [FLOOR] [Q]
"""
import json
import math
import sys
import time

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/lib')
import cubesphere as cs  # noqa: E402
import ndx  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/nd-exact/'
L = 256


def tail_jacobian(Ws, c, u):
    h = u.copy()
    J = np.eye(len(u))
    for k in range(c, L):
        z = Ws[k] @ h
        act = z > 0
        h = np.where(act, z, 0.0)
        J = act[:, None] * (Ws[k] @ J)
    return J


def main():
    seed, c, lb = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    rule, outp = sys.argv[4], sys.argv[5]
    floor = float(sys.argv[6]) if len(sys.argv) > 6 else 0.01
    Q = int(sys.argv[7]) if len(sys.argv) > 7 else 64
    Ws = ndx.make_weights(seed)
    tr = json.load(open(BASE + f'runs/truth_s{seed}.json'))
    mu, trV = np.array(tr['trunc_mean']), tr['trV']
    t0 = time.time()
    est = cs.CubeSphere(Ws, c, Q=Q, rule=rule, floor=floor)
    est.start()
    u = est.estimate()
    u = u / np.linalg.norm(u)
    J = tail_jacobian(Ws, c, u)
    setup_mv = (L - c) * 8.0
    est.J = J / np.linalg.norm(J)
    nxt = 10
    pts = []
    while True:
        cost = est.cost_mv() + setup_mv
        if cost >= 2.0 ** nxt:
            e = J @ est.estimate()
            pts.append(dict(cost_mv=cost, nmse=ndx.nmse(e, mu, trV), n_cells=est.n_cells, n_open=len(est.heap),
                            n_certified=est.n_res, P_certified=est.P_res,
                            open_share=float(np.linalg.norm(J @ est.S_open) / np.linalg.norm(e)),
                            max_level=int(max([h[-1] for h in est.heap], default=0)), sec=time.time() - t0))
            p = pts[-1]
            print('2^%d mv: nMSE %.3e cells %d open %d cert %d Pcert %.4f open share %.3e lvl %d (%.0fs)' % (
                nxt, p['nmse'], p['n_cells'], p['n_open'], p['n_certified'], p['P_certified'], p['open_share'],
                p['max_level'], p['sec']), flush=True)
            nxt += 1
            if nxt > lb:
                break
        if not est.refine_one():
            break
    out = dict(seed=seed, c=c, rule=rule, floor=floor, Q=Q, setup_mv=setup_mv, points=pts,
               final_estimate=(J @ est.estimate()).tolist(), truth=mu.tolist(), trV=trV)
    json.dump(out, open(outp, 'w'), indent=1)


if __name__ == '__main__':
    main()
