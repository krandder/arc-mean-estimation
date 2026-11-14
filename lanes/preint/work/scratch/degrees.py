"""Angular degree energies of one net (v2 about 14:46Z: F centred by the other half's mean in the degree-1/2 moments) (F7 calibration on actual nets, not the NNGP proxy).
F(xhat) = f(xhat) on the unit sphere (radius exact). Energies (summed over outputs, normalised measure):
  total angular variance V_ang = E|F|^2 - |E F|^2;  odd part E|F_o|^2, F_o = (F(x) - F(-x))/2 (all odd degrees);
  even part (degrees >= 2) E|F_e|^2 - |E F|^2;  degree 1: d ||E[F xhat^T]||_F^2;
  degree 2: (d(d+2)/2) ||E[F (xhat xhat^T - I/d)]||_F^2.
Squared norms of means are estimated without noise bias by the product of two independent halves (A, B).
Also reported: the radial share (Var of the radius-exact estimator vs plain f: 1 - V_rb / V_plain).
Usage: degrees.py N L SEED LOG2M OUT.json"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import est as E  # noqa: E402
import line as LN  # noqa: E402
import nets  # noqa: E402


def main():
    n, L, seed, lm, outp = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    Ws = nets.arc_weights(seed, n, L)
    d = n
    M = 1 << lm
    rng = np.random.default_rng([555, seed, n, L])
    half = {}
    data = {}
    for h in ('A', 'B'):
        X = rng.standard_normal((M // 2, d))
        R = np.linalg.norm(X, axis=1)
        U = X / R[:, None]
        data[h] = (X, U, E.forward(Ws, U), E.forward(Ws, -U), E.forward(Ws, X))
    for h, other in (('A', 'B'), ('B', 'A')):
        X, U, Fp, Fm, fx = data[h]
        c = data[other][2].mean(0)                       # centring by the other half: unbiased up to a factor 1 + (M/2)^-2 (co-prover r2)
        Fc = Fp - c
        m1 = Fp.mean(0)
        e1 = (Fc.T @ U) / U.shape[0]                     # E[F xhat^T] (centring by a constant changes nothing in expectation)
        acc = np.zeros((Fp.shape[1], d * d))
        for i in range(0, U.shape[0], 256):
            Uc = U[i:i + 256]
            Q = (Uc[:, :, None] * Uc[:, None, :]).reshape(Uc.shape[0], d * d)
            acc += Fc[i:i + 256].T @ Q
        acc /= U.shape[0]
        acc -= np.outer(Fc.mean(0), np.eye(d).ravel()) / d
        Fo = 0.5 * (Fp - Fm)
        Fe = 0.5 * (Fp + Fm)
        half[h] = dict(m1=m1, e1=e1, e2=acc, F2=float((Fp ** 2).sum(1).mean()), Fo2=float((Fo ** 2).sum(1).mean()),
                       Fe2=float((Fe ** 2).sum(1).mean()), me=Fe.mean(0), vplain=float(fx.var(0).sum()),
                       mplain=fx.mean(0), f2plain=float((fx ** 2).sum(1).mean()))
        print('half', h, 'done', flush=True)
    A, B = half['A'], half['B']
    mean2 = float(A['m1'] @ B['m1'])
    V_ang = 0.5 * (A['F2'] + B['F2']) - mean2
    odd = 0.5 * (A['Fo2'] + B['Fo2'])
    even = 0.5 * (A['Fe2'] + B['Fe2']) - float(A['me'] @ B['me'])
    deg1 = d * float((A['e1'] * B['e1']).sum())
    deg2 = d * (d + 2) / 2.0 * float((A['e2'] * B['e2']).sum())
    cm = LN.chi_mean(d)
    V_rb = cm * cm * V_ang                               # variance of E chi f(xhat)
    V_plain = 0.5 * (A['f2plain'] + B['f2plain']) - float(A['mplain'] @ B['mplain'])
    res = dict(n=n, L=L, seed=seed, M=M, V_ang=V_ang, odd=odd, even_ge2=even, deg1=deg1, deg2=deg2,
               shares=dict(odd=odd / V_ang, deg1=deg1 / V_ang, odd_ge3=(odd - deg1) / V_ang, deg2=deg2 / V_ang,
                           even_ge4=(even - deg2) / V_ang, even_ge2=even / V_ang),
               radial_share=1.0 - V_rb / V_plain, V_plain=V_plain, V_rb=V_rb)
    json.dump(res, open(outp, 'w'), indent=1)
    print(json.dumps(res['shares']), 'radial_share %.3f' % res['radial_share'], flush=True)


if __name__ == '__main__':
    main()
