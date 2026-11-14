"""Dev runs (dev nets, seeds >= 9100) with the full per-layer analysis (lib/accounting.analyse_layer).
Usage:
  python dev2.py input n L seed layers P
  python dev2.py stat n s_list seed P
  python dev2.py nd seed layers P            (narrow-deep 8 x 256 weights, sigma = 0)
"""
import json
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import accounting as acc  # noqa: E402
import rel  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/relevance/'


def line(o, lab):
    V = o['V_gauss'][0]
    s1 = o['V1_gauss'][0] / V
    D = o['J1_gauss'][0] / V
    M = o['V_true'][0] / o['totvar_true'][0] if 'totvar_true' in o else 1.0
    res = o['res_AS_gauss']
    rsc = o['res_ASr_gauss']
    Vr = o['Vr_gauss'][0]

    def N(eps, rr, VV):
        for k in sorted(rr, key=int):
            if rr[k][0] <= eps * VV:
                return int(k)
        return None
    return (f"{lab:>10} t={o['t']:4d} c0={o['mean_cos']:.3f} M={M:.3f} Vt/Vg={o['V_true'][0] / V:.2f} s1={s1:.3f} "
            f"s1r={o['V1r_gauss'][0] / Vr:.3f} D={D:.2f} rad1={o['res_radial_gauss'][0] / V:.3f} "
            f"ov={o['AS1_radial_overlap']:.2f} N_vec={[N(e, res, V) for e in (.1, .01, .001)]} "
            f"N_sc={[N(e, rsc, Vr) for e in (.1, .01, .001)]} PR={o['cloud_PR']:.1f} [{o['seconds']:.0f}s]")


def main():
    reg = sys.argv[1]
    rng = np.random.default_rng(777)
    outs = []
    if reg == 'input':
        n, L, seed = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        layers = [int(x) for x in sys.argv[5].split(',')]
        P = int(sys.argv[6])
        Ws = rel.input_weights(seed, n, L)
        for l in layers:
            fut = rel.Future(Ws[l:], 0.0)
            X, _ = rel.input_cloud(Ws, l, 4 * P, rng)
            o = acc.analyse_layer(fut, X, rng, P)
            o['l'] = l
            outs.append(o)
            print(line(o, f'l={l}'), flush=True)
        name = f'runs/dev2_input_n{n}_L{L}_seed{seed}.json'
    elif reg == 'nd':
        seed = int(sys.argv[2])
        layers = [int(x) for x in sys.argv[3].split(',')]
        P = int(sys.argv[4])
        Ws = rel.narrow_deep_weights(seed, 8, 256)
        for l in layers:
            fut = rel.Future(Ws[l:], 0.0)
            X, _ = rel.input_cloud(Ws, l, 4 * P, rng)
            o = acc.analyse_layer(fut, X, rng, P)
            o['l'] = l
            outs.append(o)
            print(line(o, f'l={l}'), flush=True)
        name = f'runs/dev2_nd_seed{seed}.json'
    else:
        n, seed = int(sys.argv[2]), int(sys.argv[4])
        ss = [int(x) for x in sys.argv[3].split(',')]
        P = int(sys.argv[5])
        for s in ss:
            fut = rel.stationary_future(seed, n, s)
            X = rel.stationary_cloud(seed, n, s, 4 * P, rng)
            o = acc.analyse_layer(fut, X, rng, P)
            o['s'] = s
            outs.append(o)
            print(line(o, f's={s}'), flush=True)
            with open(BASE + f'runs/dev2_stat_n{n}_seed{seed}.json', 'w') as f:
                json.dump(outs, f)
        name = f'runs/dev2_stat_n{n}_seed{seed}.json'
    with open(BASE + name, 'w') as f:
        json.dump(outs, f)


if __name__ == '__main__':
    main()
