"""Anytime error curve of the certified cube-sphere code (lib/cs2.py) on one net; all work charged (setup included).
Usage: run_cs2.py SEED C0 LOG2BUDGET RULE FLOOR Q OUT.json"""
import json
import sys
import time

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/lib')
import cs2  # noqa: E402
import ndx  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/nd-exact/'


def main():
    seed, c0, lb = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    rule, floor, Q, outp = sys.argv[4], float(sys.argv[5]), int(sys.argv[6]), sys.argv[7]
    Ws = ndx.make_weights(seed)
    tr = json.load(open(BASE + f'runs/truth_s{seed}.json'))
    mu, trV = np.array(tr['trunc_mean']), tr['trV']
    t0 = time.time()
    est = cs2.CS2(Ws, c0=c0, Q=Q, rule=rule, floor=floor)
    est.setup()
    K = est.K
    print('tail cone: delta %s, setup mv %.0f' % (None if K is None else K['delta'], est.cost_mv()), flush=True)
    nxt = 12
    pts = []
    while True:
        cost = est.cost_mv()
        if cost >= 2.0 ** nxt:
            e = est.estimate()
            p = dict(cost_mv=cost, nmse=ndx.nmse(e, mu, trV), n_cells=est.n_cells, n_open=len(est.heap),
                     n_cert=est.n_cert, P_cert=est.P_cert, tailmiss=est.n_open_tailmiss,
                     open_share=float(np.linalg.norm(est.S_open) / np.linalg.norm(e)), sec=time.time() - t0)
            pts.append(p)
            print('2^%d mv: nMSE %.3e cells %d open %d cert %d Pcert %.4f open share %.3e tailmiss %d (%.0fs)' % (
                nxt, p['nmse'], p['n_cells'], p['n_open'], p['n_cert'], p['P_cert'], p['open_share'],
                p['tailmiss'], p['sec']), flush=True)
            nxt += 1
            if nxt > lb:
                break
            json.dump(dict(seed=seed, c0=c0, rule=rule, floor=floor, Q=Q,
                           K_delta=None if K is None else K['delta'], points=pts), open(outp, 'w'), indent=1)
        if not est.refine_one():
            print('heap exhausted', flush=True)
            break
    json.dump(dict(seed=seed, c0=c0, rule=rule, floor=floor, Q=Q, K_delta=None if K is None else K['delta'],
                   points=pts, final=est.estimate().tolist()), open(outp, 'w'), indent=1)


if __name__ == '__main__':
    main()
