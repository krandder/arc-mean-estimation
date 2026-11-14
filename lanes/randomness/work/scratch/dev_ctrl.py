"""Dev only: how much of the radius-exact output variance do first-layer features with closed-form means explain?
Fits on one sample, evaluates R^2 on an independent one; also splits by parity (antipodal even/odd parts)."""
import sys, os, numpy as np, torch
sys.path.insert(0, 'lib'); import rnd
seed, n, L = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
net = rnd.Net(seed, n, L); rng = np.random.default_rng(5)
W1 = net.W64[0].numpy()
def feats(U, kind):
    Z = U @ W1.T
    cols = {'z': Z, 'absz': np.abs(Z), 'relu': np.maximum(Z, 0), 'z2': Z**2, 'zabsz': Z*np.abs(Z)}
    if kind == 'h1norm2': return (np.maximum(Z,0)**2).sum(1, keepdims=True)
    return np.concatenate([cols[k] for k in kind.split('+')], axis=1)
P = 1 << 14
res = {}
for part in ('all', 'even', 'odd'):
    U1 = rnd.to_sphere(rng.standard_normal((P, n))); U2 = rnd.to_sphere(rng.standard_normal((P, n)))
    def tgt(U):
        G = net.outs(U)
        if part == 'all': return G
        Gm = net.outs(-U)
        return 0.5*(G+Gm) if part=='even' else 0.5*(G-Gm)
    Y1, Y2 = tgt(U1), tgt(U2)
    for kind in ('z', 'absz', 'z+absz', 'h1norm2', 'z2', 'zabsz', 'z+absz+z2+zabsz'):
        F1, F2 = feats(U1, kind), feats(U2, kind)
        mu = F1.mean(0)
        A1 = np.concatenate([np.ones((P,1)), F1 - mu], 1); A2 = np.concatenate([np.ones((P,1)), F2 - mu], 1)
        B, *_ = np.linalg.lstsq(A1, Y1, rcond=None)
        r = Y2 - A2 @ B
        R2 = 1 - r.var(0).sum() / Y2.var(0).sum()
        res[(part, kind)] = R2
        print(f'{part:5s} {kind:20s} held-out R^2 = {R2:.3f}', flush=True)
