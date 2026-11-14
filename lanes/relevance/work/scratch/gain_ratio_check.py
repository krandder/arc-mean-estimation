"""Post hoc diagnostic (not registered): is the per-net miss of the v2 mean degree at l <= 8 the per-net ratio of the
future's transverse gain to its radial gain?

At sigma = 0 the net is positively homogeneous, so E|a|^2 = E|J(X) X|^2 and
    D = J(1)/V = R_meas * (tr Sigma / E|X|^2) / (V/E|a|^2),   R_meas = (J(1)/tr Sigma) / (E|a|^2/E|X|^2),
where J(1) = E|J(X) Sigma^{1/2}|_F^2 is the measured gradient energy. The v2 identity (annealed) sets R = 1.
Forward-only estimate along the sample paths (no Jacobians): per future layer k the Frobenius gain on directions
transverse to the path is about 2 a_k (a_k = active fraction; the transverse block of W_k is independent of the gate
pattern, Theorem 1) and the radial gain is |h_k|^2/|h_{k-1}|^2, so
    R_fwd = E_x[prod_k 2 a_k(x)] / (E|a|^2 / E|X|^2).
Annealed theory: per layer log(2a/rho) has mean 2/n and variance 4/n (rho = radial chi-square factor), so for aligned
paths log R ~ N(2 t/n, 4 t/n) over t future layers.
Writes results/gain_ratio_check.json."""
import json
import math
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import rel  # noqa: E402
import theory_v2 as t2  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/relevance/'


def r_fwd(Ws, l, P, rng):
    X, _ = rel.input_cloud(Ws, l, P, rng)
    h = X
    logt = np.zeros(P)
    for W in Ws[l:]:
        z = h @ W.T
        logt += np.log(2.0 * (z > 0).mean(1))
        h = np.maximum(z, 0.0)
    rad = (h ** 2).sum(1).mean() / (X ** 2).sum(1).mean()
    return float(np.exp(logt).mean() / rad), float(np.exp(logt).mean()), float(rad)


def main():
    rng = np.random.default_rng(20261102)
    out = []
    for seed in range(4000, 4006):
        Ws = rel.input_weights(seed, 256, 32)
        for o in json.load(open(BASE + f'runs/eval_arc_n256_L32_seed{seed}.json')):
            l = o['l']
            V = o['V_gauss'][0]
            J1 = o['J1_gauss'][0]
            trS = o['trSigma']
            pl = t2.predict_layer(o)
            Rf, T, rad = r_fwd(Ws, l, 1024, rng)
            rec = dict(seed=seed, l=l, D=J1 / V, D_v2=pl['D'], Vrel=V / o['Ea2_true'], Vrel_v2=pl['V_rel'],
                       R_fwd=Rf, transverse=T, radial=rad, D_v2_quenched=pl['D'] * Rf)
            if True:
                rec['R_meas'] = (J1 / trS) / (o['Ea2_true'] / (trS + o['m2']))
            out.append(rec)
            print(f"{seed} l={l:2d} D={rec['D']:6.2f} v2={pl['D']:6.2f} ratio={pl['D'] / rec['D']:.2f} "
                  f"R_meas={rec['R_meas']:.2f} R_fwd={Rf:.2f} quenched ratio={pl['D'] * Rf / rec['D']:.2f}", flush=True)
    json.dump(out, open(BASE + 'results/gain_ratio_check.json', 'w'), indent=1)
    for tag, key in (('v2', 'D_v2'), ('v2 x R_fwd', 'D_v2_quenched')):
        ok = [0.75 <= r[key] / r['D'] <= 1.33 for r in out]
        print(tag, 'within [0.75, 1.33]:', sum(ok), 'of', len(ok))
        for s in range(4000, 4006):
            print('  ', s, sum(o for o, r in zip(ok, out) if r['seed'] == s))
    lr = {l: [math.log(r['R_fwd']) for r in out if r['l'] == l] for l in sorted(set(r['l'] for r in out))}
    for l, v in lr.items():
        t = 32 - l
        print(f'l={l}: log R_fwd mean {np.mean(v):.3f} sd {np.std(v, ddof=1):.3f}; aligned-path annealed '
              f'mean {2 * t / 256:.3f} sd {math.sqrt(4 * t / 256):.3f}')


if __name__ == '__main__':
    main()
