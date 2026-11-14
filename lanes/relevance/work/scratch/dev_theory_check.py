"""Dev check of theory-v1 ingredients against dev runs (dev nets only).
For each analysed layer: kernel-predicted s_1 and D (noiseless kernel for sigma = 0; L0 independent-noise kernel for
the stationary regime, plus the radial channel as pure degree 1), generic-model PCA capture vs measured PCA residuals,
free-product degree-1 spectrum (half-width Fuss-Catalan backward) vs measured R1 spectrum, combined N prediction."""
import json
import math
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import accounting as acc  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/relevance/'


def Nfrom(curve, V, eps):
    for k in sorted(curve, key=int):
        if curve[k] <= eps * V:
            return int(k)
    return None


def predict(o, dmax=60):
    n, t = o['n'], o['t']
    lam = np.array(o['cloud_evals'])
    lam = np.maximum(lam, lam[0] * 1e-12)
    m2 = o['m2']
    rad = o['radial_var']
    trS = o['trSigma']
    c0 = o['mean_cos']  # measured cosine between independent cloud points
    delta0 = 1 - c0
    Q = o.get('meanQ') if o['sigma'] > 0 else None
    s_ang, tot = acc.degree_spectrum_kernel(c0, t, noise_Q=Q, dmax=dmax)
    # angular variance (units of |m|^2) and radial (pure degree 1, attenuated in the stationary regime by the radial
    # response; v1 uses no attenuation for sigma = 0 and exp(-5 t / n) for the stationary regime)
    Vang = (m2 + trS - rad) * tot
    rgain = 1.0 if o['sigma'] == 0 else math.exp(-5.0 * t / n)
    Vrad = rad * rgain
    V = Vang + Vrad
    s = s_ang * Vang / V
    s[0] += Vrad / V
    D = float(np.sum(np.arange(1, dmax + 1) * s))
    return dict(s=s, s1=float(s[0]), D=D, Vpred=V, Vang=Vang, Vrad=Vrad, delta0=delta0)


def main(fn):
    d = json.load(open(BASE + fn))
    for o in d:
        V = o['V_gauss'][0]
        pr = predict(o)
        n = o['n']
        ks = sorted([int(k) for k in o['res_PCA_gauss']])
        lam = np.array(o['cloud_evals'])
        lam = np.maximum(lam, lam[0] * 1e-12)
        gen = acc.generic_capture(lam, pr['s'], ks)
        # measured
        s1 = o['V1_gauss'][0] / V
        D = o['J1_gauss'][0] / V
        resP = {k: o['res_PCA_gauss'][str(k)][0] / V for k in ks}
        lab = o.get('l', o.get('s'))
        print(f"{fn.split('_')[1]} n={n} lab={lab} t={o['t']} V={V:.4g} Vpred={pr['Vpred']:.4g} s1={s1:.3f} pred={pr['s1']:.3f} "
              f"D={D:.2f} pred={pr['D']:.2f} delta0={pr['delta0']:.4f}")
        print('    PCA resid meas', [(k, round(resP[k], 3)) for k in ks if k in (1, 2, 4, 8, 16, 32, 64)])
        print('    PCA resid gen ', [(k, round(1 - gen[k], 3)) for k in ks if k in (1, 2, 4, 8, 16, 32, 64)])


if __name__ == '__main__':
    for fn in sys.argv[1:]:
        main(fn)
