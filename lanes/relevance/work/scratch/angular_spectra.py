"""Offline angular cloud spectra (eigenvalues of P_perp Sigma P_perp, e = mean direction) for evaluation cells whose
run predates the cloud_evals_perp field. Fresh cloud samples (a forward-law statistic; independent of the run's samples).
Writes results/angular_spectra.json keyed by 'mode|n|seed|l or s'."""
import json
import os
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import rel  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/relevance/'
OUT = BASE + 'results/angular_spectra.json'


def spec(X):
    m = X.mean(0)
    C = np.cov(X, rowvar=False)
    e = m / np.linalg.norm(m)
    Pp = np.eye(len(m)) - np.outer(e, e)
    return np.sort(np.linalg.eigvalsh(Pp @ C @ Pp))[::-1].tolist()


def main():
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    rng = np.random.default_rng(2718)
    for seed in (4000, 4001, 4002, 4003):
        Ws = rel.input_weights(seed, 256, 32)
        x = rng.standard_normal((8192, 256))
        h = x
        lprev = 0
        for l in (0, 4, 8, 16, 24, 28, 31):
            for k in range(lprev, l):
                h = np.maximum(h @ Ws[k].T, 0.0)
            lprev = l
            res[f'arc|256|{seed}|{l}'] = spec(h)
        print('arc', seed, flush=True)
    for n, seeds, ss in ((32, (1000, 1001, 1002, 1003), (0, 1, 3, 7, 15, 31, 63)),
                         (64, (1000, 1001, 1002, 1003), (0, 1, 3, 7, 15, 31, 63, 127))):
        for seed in seeds:
            cl = rel.stationary_clouds(seed, n, list(ss), 8192, rng, chunk=8192)
            for s in ss:
                res[f'stat|{n}|{seed}|{s}'] = spec(cl[s])
            print('stat', n, seed, flush=True)
    json.dump(res, open(OUT, 'w'))


if __name__ == '__main__':
    main()
