"""Checks for lib/bitlib.py (run: python tests/test_bitlib.py)."""
import math
import os
import sys

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import bitlib as bl  # noqa: E402

torch.set_num_threads(2)
ok = True


def check(name, cond, info=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name, info)
    ok &= bool(cond)


# 1. water-filling: sums to C, matches a brute-force bisection, gradient conserves the sum
eta = torch.tensor([2.0, 1.0, 0.5, -1.0, -3.0], requires_grad=True)
C = torch.tensor([0.3, 1.0, 3.0, 10.0])
Ci = bl.waterfill(eta, C)
check('waterfill sums', torch.allclose(Ci.sum(1), C, atol=1e-5), Ci.sum(1).tolist())
e = eta.detach().numpy()
for r, c in enumerate(C.tolist()):
    lo, hi = -50.0, 50.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        s = np.maximum(0, (e - mid) / (2 * math.log(2))).sum()
        lo, hi = (mid, hi) if s > c else (lo, mid)
    ref = np.maximum(0, (e - lo) / (2 * math.log(2)))
    check(f'waterfill vs bisection C={c}', np.allclose(ref, Ci[r].detach().numpy(), atol=1e-4))
g = torch.autograd.grad(Ci.sum(), eta)[0]
check('waterfill gradient conserves the sum', torch.allclose(g, torch.zeros_like(g), atol=1e-5), g.tolist())

# 2. the nets: same weights as the relevance lane (float64), V = tr Var(a) at seed 4000 close to its V_true = 32.15
net = bl.make_net('arc', 4000)
st = bl.layer_stats(net, 0, 32768, seed=5)
check('ARC seed 4000 V near the relevance lane value 32.15 (+-5%)', abs(st['V'] / 32.15 - 1) < 0.05, st['V'])
x = np.random.default_rng(0).standard_normal((64, 256))
a64 = net.run64(x, 0)
a32 = net.run(torch.tensor(x, dtype=torch.float32), 0).double().numpy()
rel = np.abs(a64 - a32).max() / np.abs(a64).max()
check('float32 forward matches float64 (rel < 1e-4)', rel < 1e-4, rel)
nd = bl.make_net('nd', 203)
check('narrow-deep shape', nd.n == 8 and nd.L == 256)

# 3. binary code masking: bits beyond b are 0, the code is +-1 inside
m = bl.Bottleneck(256, 256, 'bin', 'local', 64, 1, st['h_mean'], st['h_std'], st['a_mean'], st['a_std'])
z = torch.randn(8, 256)
cin, Cr = m.code(z, torch.tensor([1, 2, 3, 5, 8, 100, 255, 256]))
check('binary mask', all(int((cin[i] != 0).sum()) == b for i, b in enumerate([1, 2, 3, 5, 8, 100, 255, 256])))
check('binary values', bool(torch.all((cin == 0) | (cin.abs() == 1))))

# 4. gauss channel: realised capacity equals the requested C
mg = bl.Bottleneck(256, 256, 'gauss', 'local', 64, 1, st['h_mean'], st['h_std'], st['a_mean'], st['a_std'])
with torch.no_grad():
    mg.eta.copy_(torch.randn(256))
cin, Cr = mg.code(torch.randn(4, 256), torch.tensor([1.0, 7.0, 50.0, 256.0]))
check('gauss realised C', torch.allclose(Cr, torch.tensor([1.0, 7.0, 50.0, 256.0]), rtol=1e-4), Cr.tolist())

# 5. reconstruction with all information: an 'ahead' identity-like check is training; here only the output-space
#    mode: layer L future is the identity
h = torch.randn(3, 256)
check('layer-L future is the identity', torch.equal(net.run(h, net.L), h))
print('ALL PASS' if ok else 'SOME FAILED')
