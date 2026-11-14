"""Tails exploration (dev nets only, not part of any prereg test): distribution of the last pre-activation z_L.
python tails_explore1.py SEED SIGMA LOG2N"""
import math, sys, time
import numpy as np
import torch
sys.path.insert(0, '/srv/agent-data/home/workspaces/mats/work/arc-noisy')
from anet import Net

torch.set_num_threads(4)
seed, sigma, lg = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
N = 1 << lg
net = Net(seed, sigma=sigma)
g = torch.Generator().manual_seed(4242 + seed)
B = 1 << 15
DEPTHS = (4, 8, 32)
Z = {L: [] for L in DEPTHS}; HN = {L: [] for L in DEPTHS}; XN = []
t0 = time.time()
with torch.no_grad():
    for b in range(N // B):
        x = torch.randn(B, 256, generator=g)
        XN.append(x.norm(dim=1))
        h = x
        for l in range(32):
            z = h @ net.W[l].float().T
            if (l + 1) in DEPTHS:
                Z[l + 1].append(z.clone()); HN[l + 1].append(h.norm(dim=1))
            a = torch.relu(z)
            h = a + float(net.s[l]) * torch.randn(a.shape, generator=g)
print('time %.0fs' % (time.time() - t0))
XN = torch.cat(XN).double()
for L in DEPTHS:
    z = torch.cat(Z[L]).double(); hn = torch.cat(HN[L]).double()
    mu = z.mean(0); sd = z.std(0); zs = (z - mu) / sd
    sk = (zs ** 3).mean(0); ku = (zs ** 4).mean(0) - 3
    zsort, idx = torch.sort(z, dim=0, descending=True)
    res = []
    for p in (1e-3, 1e-4, 1e-5):
        k = max(int(p * N), 1)
        q = zsort[k - 1]
        qg = mu + sd * float(torch.distributions.Normal(0, 1).icdf(torch.tensor(1 - p)))
        res.append((p, q, qg))
    print(f'--- depth {L}  sigma {sigma}  N=2^{lg}')
    print('  mean of neuron means %.3f, sd of means %.3f, median sd %.3f, frac mean<0 %.2f' % (mu.mean(), mu.std(), sd.median(), (mu < 0).double().mean()))
    print('  skew median %.2f [%.2f, %.2f]  exkurt median %.2f [%.2f, %.2f]' % (sk.median(), sk.quantile(0.1), sk.quantile(0.9), ku.median(), ku.quantile(0.1), ku.quantile(0.9)))
    for p, q, qg in res:
        zq = (q - mu) / sd
        print('  p=%g: empirical quantile in sd units median %.2f [%.2f, %.2f] (Gaussian %.2f); ratio emp/gauss excess median %.2f' % (
            p, zq.median(), zq.quantile(0.1), zq.quantile(0.9), float((qg - mu)[0] / sd[0]), ((q - mu) / (qg - mu)).median()))
    # radial share: for samples above the 1e-4 quantile, mean |x| and mean |h_{L-1}| relative
    k = int(1e-4 * N)
    top = idx[:k]                       # (k, 256) sample indices of the top k per neuron
    xr = XN[top].mean(0) / XN.mean()
    hr = hn[top].mean(0) / hn.mean()
    print('  top 1e-4: E|x| ratio median %.4f [%.4f, %.4f] (sd of |x|/mean = %.4f); E|h_{L-1}| ratio median %.3f [%.3f, %.3f]' % (
        xr.median(), xr.quantile(0.1), xr.quantile(0.9), float(XN.std() / XN.mean()), hr.median(), hr.quantile(0.1), hr.quantile(0.9)))
    # collapse: R^2 of z_i on |h_{L-1}|
    hc = hn - hn.mean(); zc = z - mu
    beta = (hc[:, None] * zc).mean(0) / (hc ** 2).mean()
    r2 = 1 - ((zc - beta[None] * hc[:, None]) ** 2).mean(0) / (zc ** 2).mean(0)
    print('  R^2 of z_i on |h_{L-1}|: median %.3f [%.3f, %.3f]; frac beta>0 %.2f' % (r2.median(), r2.quantile(0.1), r2.quantile(0.9), (beta > 0).double().mean()))
    # ARC fixed threshold 3 sqrt 2
    t = 3 * math.sqrt(2)
    pe = (z > t).double().mean(0)
    print('  ARC threshold 3*sqrt2: p over neurons quantiles 10/50/90%%: %.2e %.2e %.2e; frac p<1e-5 %.2f' % (
        pe.quantile(0.1), pe.median(), pe.quantile(0.9), (pe < 1e-5).double().mean()))
    np.savez_compressed(f'/tmp/tails_explore1_{seed}_{sigma:g}_L{L}.npz', mu=mu.numpy(), sd=sd.numpy(), sk=sk.numpy(), ku=ku.numpy(),
                        q3=res[0][1].numpy(), q4=res[1][1].numpy(), q5=res[2][1].numpy())
