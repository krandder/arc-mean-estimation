"""Time the parts of one training step (ARC, one model) to find the bottleneck."""
import os, sys, time, math
import numpy as np, torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import vrlib as vr
torch.backends.cuda.matmul.allow_tf32 = True
cls = sys.argv[1] if len(sys.argv) > 1 else 'unres'
l = int(sys.argv[2]) if len(sys.argv) > 2 else 0
B = int(sys.argv[3]) if len(sys.argv) > 3 else 2048
W = int(sys.argv[4]) if len(sys.argv) > 4 else 1024
Ws, act = vr.family_weights('arc', 9100)
st = vr.pilot_stats(Ws, act, l, P=8192, seed=1)
bnet = vr.BNet([Ws], act)
anch = [-6 + 0.5 * j for j in range(13)]
init = vr.build_init([st], [Ws], l, cls, 256, 1, anch)
model = vr.VRCode(1, cls, 256, 256, W, 3, (-6, 0), init)
fr = vr.Frames([st], l, 32, 1)
opt = torch.optim.Adam(model.parameters(), lr=1e-4)
gen = torch.Generator(device='cuda').manual_seed(0)
G = 32
def tic():
    torch.cuda.synchronize(); return time.time()
acc = {}
for it in range(30):
    t0 = tic()
    h, a = vr.sample_batch(bnet, l, 1, B, gen)
    y = fr.white(h); xa = fr.pca_a(a)
    t = vr.stratified_t(1, G, (-6, 0), gen)
    t1 = tic()
    phi = vr.hat(t, model.anch_t)
    nu = model.encode(y.view(1, G, B // G, -1), xa.view(1, G, B // G, -1), t)
    t2 = tic()
    g = model.gains(phi)
    z = g.unsqueeze(2) * nu + torch.randn_like(nu)
    lp = model.log_prior(z, g, phi)
    rate = ((-0.5 * vr.LOG2PIE - lp) / vr.LN2).sum(-1)
    t3 = tic()
    zt = z * (g / (1 + g * g)).unsqueeze(2)
    yhat = model.dec(zt, phi) + torch.matmul(zt, model.Blin.unsqueeze(1))
    t4 = tic()
    hh = fr.unwhite(yhat.reshape(1, B, -1))
    ah = bnet.run(hh, l)
    D = ((ah - a) ** 2).sum(-1) / fr.V.view(1, 1)
    loss = rate.mean() + D.mean() / 1e-3
    t5 = tic()
    opt.zero_grad(); loss.backward()
    t6 = tic()
    opt.step()
    t7 = tic()
    if it >= 10:
        for k, v in dict(data=t1 - t0, enc=t2 - t1, prior=t3 - t2, dec=t4 - t3, future=t5 - t4, backward=t6 - t5, step=t7 - t6).items():
            acc[k] = acc.get(k, 0) + v / 20
print(cls, l, B, W, {k: round(1000 * v, 2) for k, v in acc.items()}, 'total ms', round(1000 * sum(acc.values()), 2), flush=True)
