"""PREREG Part 1 evaluation runner (measurements only; predictions and scores in score_part1.py).
Usage:
  python eval_part1.py arc  seed                 (ARC 256 x 32, layers 0,4,8,16,24,28,31, P = 4096)
  python eval_part1.py nd   seed                 (narrow-deep 8 x 256, layers 0,2,4,8,16,32,64,128,192,255, P = 8192)
  python eval_part1.py stat n seed s_list P      (stationary, state h_{-s}, t = s + 1)
Writes runs/eval_<mode>_..._seed<seed>.json (one record per layer, appended as it goes).
"""
import json
import sys
import time

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import accounting as acc  # noqa: E402
import rel  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/relevance/'


def dump(name, outs):
    with open(BASE + name, 'w') as f:
        json.dump(outs, f)


def main():
    mode = sys.argv[1]
    outs = []
    if mode in ('arc', 'nd'):
        seed = int(sys.argv[2])
        rng = np.random.default_rng([31337, seed, 1 if mode == 'arc' else 2])
        if mode == 'arc':
            n, L, layers, P = 256, 32, [0, 4, 8, 16, 24, 28, 31], 4096
            Ws = rel.input_weights(seed, n, L)
        else:
            n, L, layers, P = 8, 256, [0, 2, 4, 8, 16, 32, 64, 128, 192, 255], 8192
            Ws = rel.narrow_deep_weights(seed, n, L)
        name = f'runs/eval_{mode}_n{n}_L{L}_seed{seed}.json'
        for l in layers:
            t0 = time.time()
            fut = rel.Future(Ws[l:], 0.0)
            X, _ = rel.input_cloud(Ws, l, 4 * P, rng)
            o = acc.analyse_layer(fut, X, rng, P)
            o.update(l=l, L=L, seed=seed, mode=mode, dead_frac=float(np.mean(np.all(X == 0, axis=1))))
            outs.append(o)
            dump(name, outs)
            print(f'{mode} seed {seed} l {l} done in {time.time() - t0:.0f}s', flush=True)
    else:
        n, seed = int(sys.argv[2]), int(sys.argv[3])
        ss = [int(x) for x in sys.argv[4].split(',')]
        P = int(sys.argv[5])
        rng = np.random.default_rng([31337, seed, n, 3])
        name = f'runs/eval_stat_n{n}_seed{seed}.json'
        clouds = rel.stationary_clouds(seed, n, ss, 4 * P, rng, chunk=4 * P)
        for s in sorted(ss):
            t0 = time.time()
            fut = rel.stationary_future(seed, n, s)
            o = acc.analyse_layer(fut, clouds[s], rng, P)
            o.update(s=s, seed=seed, mode='stat')
            outs.append(o)
            dump(name, outs)
            print(f'stat n {n} seed {seed} s {s} done in {time.time() - t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()
