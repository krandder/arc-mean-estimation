"""POST HOC cross-lane comparison (asked by main): the bits formula of FORMAL 6.6 on the bit-accounting lane's ARC net
(256 x 32, st.W_layer(4000, 256, l), l = 1..32; work/bit-accounting/lib/bitlib.py) against that lane's learned
local-code bits at nMSE 0.1. Runs scratch/run_eval.e1_layer (forward-only k-means references, M in
{1, 4, 16, 64, 256}) at cuts l in {1, 2, 4, 8, 16, 24, 28, 31} on 2048 + 2048 unit input directions, plus the
log-radius variance of the layer-l states under Gaussian inputs. Writes results/compare_bitacc.json."""
import os
import sys
import json
import math
import time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
sys.path.insert(0, HERE)
sys.path.insert(0, '/home/agent/workspaces/mats/work/stationary/lib')
import bb
import run_eval
import st
import score_bits5 as sb


def main():
    seed, n, L = 4000, 256, 32
    W = [st.W_layer(seed, n, l) for l in range(1, L + 1)]
    rng = np.random.default_rng([seed, n, L, 11])
    U = bb.sphere(rng, 4096, n)
    fit, test = U[:2048], U[2048:]
    cuts = [1, 2, 4, 8, 16, 24, 28, 31]
    Hf = bb.forward_keep(W, fit, set(cuts) | {L})
    Ht = bb.forward_keep(W, test, set(cuts) | {L})
    Af, At = Hf[L], Ht[L]
    Vang = float(np.sum(At.var(axis=0)))
    EA2 = float(np.mean(np.sum(At * At, axis=1)))
    X = rng.standard_normal((4096, n))
    Hx = bb.forward_keep(W, X, set(cuts) | {L})
    out = {'seed': seed, 'n': n, 'L': L, 'Vang': Vang, 'EA2': EA2, 'cuts': []}
    t0 = time.time()
    for l in cuts:
        e = run_eval.e1_layer(W, l, Hf, Ht, Af, At, Vang, rng, [1, 4, 16, 64, 256], [])
        rho = e['theta_median'] * e['Lp'] / 2
        D1R, D1F = e['fwd']['1']['D_R'], e['fwd']['1']['D_F']
        g = sb.gamma_R(e)
        rough_bits = max(0.0, (e['PR'] / 0.72) * math.log2(D1R / 0.1))
        smooth_bits = max(0.0, (1.75 * e['PR'] / 3) * math.log2(D1F / 0.1))
        meas = sb.bits_measured(e, 0.1)
        best = min(e['fwd'][str(M)]['D_best'] for M in [1, 4, 16, 64, 256])
        out['cuts'].append({'l': l, 'Lp': e['Lp'], 'PR': e['PR'], 'theta_median': e['theta_median'], 'rho': rho,
                            'D_R': {M: e['fwd'][str(M)]['D_R'] for M in [1, 4, 16, 64, 256]},
                            'D_F': {M: e['fwd'][str(M)]['D_F'] for M in [1, 4, 16, 64, 256]},
                            'D_best_min': best, 'gamma_R': g, 'formula_bits_rough': rough_bits,
                            'formula_bits_smooth': smooth_bits, 'measured_radial_bits': meas,
                            'var_log_radius_gauss': float(np.var(np.log(np.linalg.norm(Hx[l], axis=1))))})
        print(f"l={l} PR={e['PR']:.1f} rho={rho:.2f} D_R(1)={D1R:.3f} D_F(1)={D1F:.3f} gamma_R={g} "
              f"rough={rough_bits:.0f} smooth={smooth_bits:.0f} meas={meas} {time.time() - t0:.0f}s", flush=True)
    json.dump(out, open(os.path.join(HERE, '..', 'results', 'compare_bitacc.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
