"""Amendment 2 (C3, rough-gain variogram): for pairs of states (h, c) at layer l, the future's log-gain difference
Delta = log(|g_l(h)| / |h|) - log(|g_l(c)| / |c|) against the layer-l angle phi. Prediction (astra r2, PROVEN only in the
iterated large-width / small-angle limit): Var(Delta) ~ (6 pi / n) phi x/(1+x), x = L' phi/(3 pi).
Usage: python scratch/run_gain.py N L SEED -> runs/gain_n{N}_L{L}_s{SEED}.json"""
import os
import sys
import json
import math
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import bb


def main():
    n, L, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    W = bb.make_weights(seed, n, L)
    rng = np.random.default_rng([seed, n, L, 13])
    out = {'n': n, 'L': L, 'seed': seed, 'layers': {}}
    for l in [L // 4, L // 2]:
        Lp = L - l
        rows = []
        U0 = bb.sphere(rng, 32, n)
        for u0 in U0:
            c = bb.forward(W, u0[None, :], 0, l)[0]
            gc = bb.forward(W, c[None, :], l)[0]
            if np.linalg.norm(gc) == 0 or np.linalg.norm(c) == 0:
                continue
            for dlt in [0.01, 0.03, 0.1, 0.3, 1.0]:
                xi = rng.standard_normal((16, n))
                xi -= np.outer(xi @ u0, u0)
                xi /= np.linalg.norm(xi, axis=1, keepdims=True)
                U = math.cos(dlt) * u0[None, :] + math.sin(dlt) * xi
                H = bb.forward(W, U, 0, l)
                G = bb.forward(W, H, l)
                phi = bb.angles_to(H, c)
                gh = np.linalg.norm(G, axis=1)
                ok = gh > 0
                D = np.log(gh[ok] / np.linalg.norm(H[ok], axis=1)) - math.log(np.linalg.norm(gc) / np.linalg.norm(c))
                for p, d in zip(phi[ok], D):
                    rows.append((dlt, float(p), float(d)))
        rows = np.array(rows)
        res = []
        for dlt in sorted(set(rows[:, 0])):
            s = rows[:, 0] == dlt
            phi = float(np.median(rows[s, 1]))
            x = Lp * phi / (3 * math.pi)
            var = float(np.mean(rows[s, 2] ** 2))  # second moment of Delta (its mean is ~0 by symmetry)
            pred = (6 * math.pi / n) * phi * x / (1 + x)
            res.append({'delta': dlt, 'phi_median': phi, 'Lp_phi': Lp * phi, 'second_moment': var,
                        'prediction': pred, 'ratio': var / pred if pred > 0 else None, 'pairs': int(s.sum())})
        out['layers'][str(l)] = {'Lp': Lp, 'bins': res}
    json.dump(out, open(f'runs/gain_n{n}_L{L}_s{seed}.json', 'w'), indent=1)
    print(json.dumps(out), flush=True)


if __name__ == '__main__':
    main()
