import math, sys, numpy as np
sys.path.insert(0, 'lib'); sys.path.insert(0, 'tests')
import line as LN
from test_line import make_net, fwd, brute_student, brute_gauss
for dims in ([3, 1], [3, 2], [3, 4, 2], [4,5,5,3]):
    Ws = make_net(1, dims)
    d = dims[0]
    rng = np.random.default_rng(5)
    u = rng.standard_normal(d); u /= np.linalg.norm(u)
    B = LN.orth_basis(u)
    print('u.B', np.abs(u @ B).max())
    Y = LN.bases_from_uniform(rng.random((2, d - 1)), B)
    wt = LN.Weight('student', d - 1)
    I, fl, cnt, _ = LN.line_integrals(Ws, Y, u, wt)
    for i in range(2):
        print(dims, i, I[i], brute_student(Ws, Y[i], u, d - 1), cnt[i])
    Yg = LN.bases_from_uniform(rng.random((2, d - 1)), B, normalise=False)
    Ig, _, _, _ = LN.line_integrals(Ws, Yg, u, LN.Weight('gauss'))
    for i in range(2):
        print(' gauss', Ig[i], brute_gauss(Ws, Yg[i], u))
