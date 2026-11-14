"""Gaussian-channel comparison at each step of a saved chain (target: the chain's next code c_{l+1}).

Code z = u(h_l) + nu, nu ~ N(0, I_d), u an MLP (the encoder chooses the signal power, the noise is fixed: only the SNR
matters). Trained on CE(target row, q(c | z)) + beta * R_KL(batch), R_KL the pairwise-KL upper bound on the batch
mixture's information, for a grid of beta (one curve per layer).
Evaluation on held-out points (Kolchinsky-Tracey 2017 pairwise bounds on the empirical mixture, bits):
  rate     I_lo = -mean_i log2 mean_j exp(-|u_i - u_j|^2 / 8) <= I(h; z) <= I_hi = -mean_i log2 mean_j exp(-|u_i - u_j|^2 / 2)
           (Bhattacharyya lower, KL upper; computed at two sample sizes as a convergence check)
  relevance I_dec = H(c) - CE(decoder) (a decoder lower bound, up to Monte Carlo error) and I_mix = H(c) - mean H(p(c | z)),
           p(c | z) the mixture posterior sum_i w_i(z) S_i over the other held-out points (a consistent plug-in, biased
           up at finite N by the concavity of entropy; reported at N and N/2).
usage: run_gauss.py --n 16 --L 16 --seed 9100 --sigma 0.1 --KL 64 --chain K --layers all --out runs_gpu/dev
"""
import argparse
import json
import math
import os
import sys
import time

import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import bb  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--n', type=int, required=True)
ap.add_argument('--L', type=int, required=True)
ap.add_argument('--seed', type=int, required=True)
ap.add_argument('--sigma', type=float, required=True)
ap.add_argument('--KL', type=int, default=64)
ap.add_argument('--chain', default='K')
ap.add_argument('--layers', default='all')
ap.add_argument('--d', type=int, default=8)
ap.add_argument('--betas', default='0.02,0.04,0.07,0.1,0.14,0.2,0.28,0.4')
ap.add_argument('--powers', default='', help='if set: power-constrained codes (per-dimension SNR grid), no beta penalty (D8)')
ap.add_argument('--tag', default='')
ap.add_argument('--Ntr', type=int, default=1 << 17)
ap.add_argument('--Mtr', type=int, default=64)
ap.add_argument('--Nev', type=int, default=1 << 14)
ap.add_argument('--Mev', type=int, default=1024)
ap.add_argument('--steps', type=int, default=3000)
ap.add_argument('--batch', type=int, default=2048)
ap.add_argument('--width', type=int, default=256)
ap.add_argument('--device', default='cpu')
ap.add_argument('--threads', type=int, default=4)
ap.add_argument('--out', required=True)
args = ap.parse_args()
torch.set_num_threads(args.threads)
dev = args.device
L = args.L
T0 = time.time()
odir = os.path.join(args.out, f'n{args.n}L{args.L}_s{args.seed}_sig{args.sigma:g}_K{args.KL}')
cdir = os.path.join(odir, 'chain' + args.chain)
net = bb.Net(args.seed, args.n, L, args.sigma, dev)
oc = torch.load(os.path.join(odir, 'outcode.pt'), map_location=dev)
out_code = bb.OutCode(oc['C'].to(dev), net)
LN2 = math.log(2.0)


def load(l):
    if l == L - 1:
        return out_code
    return bb.load_code(lambda k: os.path.join(cdir, f'code_l{k}.pt'), l, L, net, out_code, dev)


def pair_bounds(u, chunk=2048):
    """KT bounds (bits) on I(x; u(x) + N(0, I)) for the empirical law of u (rows)."""
    N = u.shape[0]
    hi, lo = 0.0, 0.0
    for i in range(0, N, chunk):
        d2 = torch.cdist(u[i:i + chunk].double(), u.double()) ** 2
        hi += float(-(torch.logsumexp(-d2 / 2, 1) - math.log(N)).sum())
        lo += float(-(torch.logsumexp(-d2 / 8, 1) - math.log(N)).sum())
    return lo / N / LN2, hi / N / LN2


def mc_rate(u, gen, nz=8192, chunk=1024):
    """Monte Carlo I(x; z) (bits) with the mixture density over the held-out points: with the source component (the
    empirical-mixture information; as a population estimate it is biased down in expectation) and leave-one-out (biased
    up). Neither realisation is a guaranteed population bound (review r1 #13); their spread and the N/2 values are the
    reliability check."""
    N, d = u.shape
    idx = torch.randint(N, (nz,), generator=gen, device=u.device)
    nu = torch.randn(nz, d, generator=gen, device=u.device)
    z = u[idx] + nu
    tot_in, tot_loo = 0.0, 0.0
    for i in range(0, nz, chunk):
        lw = -(torch.cdist(z[i:i + chunk].double(), u.double()) ** 2) / 2
        lpz_in = torch.logsumexp(lw, 1) - math.log(N)
        lw[torch.arange(lw.shape[0]), idx[i:i + chunk]] = -float('inf')
        lpz_loo = torch.logsumexp(lw, 1) - math.log(N - 1)
        lpzx = -(nu[i:i + chunk].double() ** 2).sum(1) / 2
        tot_in += float((lpzx - lpz_in).sum())
        tot_loo += float((lpzx - lpz_loo).sum())
    return tot_in / nz / LN2, tot_loo / nz / LN2


def mix_relevance(u, S, Hc, gen, nz=8192, chunk=1024):
    """I_mix = H(c) - E H(p(c | z)), z = u_m + nu for held-out m, p(c|z) = sum_{i != m} w_i(z) S_i."""
    N = u.shape[0]
    idx = torch.randint(N, (nz,), generator=gen, device=u.device)
    z = u[idx] + torch.randn(nz, u.shape[1], generator=gen, device=u.device)
    H = 0.0
    for i in range(0, nz, chunk):
        d2 = torch.cdist(z[i:i + chunk].double(), u.double()) ** 2
        lw = -d2 / 2
        lw[torch.arange(lw.shape[0]), idx[i:i + chunk]] = -float('inf')      # leave the source point out
        w = torch.softmax(lw, 1)
        H += float(bb.ent_rows(w @ S.double()).sum())
    return Hc - H / nz


class GCode(torch.nn.Module):
    def __init__(self, n, d, Kt, width, mu, sd):
        super().__init__()
        self.enc = bb.MLP(n, d, width, 2)
        self.dec = bb.MLP(d, Kt, width, 2)
        self.register_buffer('mu', mu)
        self.register_buffer('sd', sd)

    def u(self, h):
        return self.enc((h - self.mu) / self.sd)

    def u_pow(self, h, P, train, mom=0.02):
        """Encoder output scaled to mean per-dimension power P (batch statistics in training, running average after)."""
        u = self.u(h)
        if train:
            pw = u.pow(2).mean()
            with torch.no_grad():
                self.run_pw = pw.detach() if not hasattr(self, 'run_pw') else (1 - mom) * self.run_pw + mom * pw.detach()
        else:
            pw = self.run_pw
        return u * torch.sqrt(P / pw.clamp_min(1e-12))


GJ = os.path.join(cdir, f'gauss{args.tag}.json')
res = json.load(open(GJ)) if os.path.exists(GJ) else {}
layers = list(range(L - 2, -1, -1)) if args.layers == 'all' else [int(x) for x in args.layers.split(',')]
chain = json.load(open(os.path.join(cdir, 'chain.json')))
for l in layers:
    if str(l) in res:
        continue
    ts = time.time()
    nxt = load(l + 1)
    g = bb.make_gen(dev, 'gauss', args.seed, l)
    h_tr = net.sample(args.Ntr, l, g)
    h_ev = net.sample(args.Nev, l, g)
    P_tr = bb.mc_counts_next(net, l, h_tr, nxt, args.Mtr, g).float() / args.Mtr
    c_ev = bb.mc_counts_next(net, l, h_ev, nxt, args.Mev, g)
    S_ev = c_ev.float() / args.Mev
    st = bb.target_stats(c_ev)
    Hc = st['H_next']
    rows = []
    grid = [('power', float(p)) for p in args.powers.split(',') if p] or [('beta', float(b)) for b in args.betas.split(',')]
    for mode, beta in grid:
        torch.manual_seed(bb.seed_of('gcode', args.seed, l, mode, beta) % (1 << 31))
        m = GCode(args.n, args.d, nxt.K, args.width, h_tr.mean(0), h_tr.std(0).clamp_min(1e-6)).to(dev)
        opt = torch.optim.Adam(m.parameters(), lr=2e-3)
        sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=2e-3, total_steps=args.steps, pct_start=0.05)
        for s in range(args.steps):
            idx = torch.randint(args.Ntr, (args.batch,), generator=g, device=dev)
            u = m.u_pow(h_tr[idx], beta, True) if mode == 'power' else m.u(h_tr[idx])
            z = u + torch.randn(u.shape, generator=g, device=dev)
            ce = -(P_tr[idx] * torch.log_softmax(m.dec(z), 1)).sum(1).mean() / LN2
            if mode == 'power':
                loss = ce
            else:
                d2 = torch.cdist(u, u) ** 2
                rkl = -(torch.logsumexp(-d2 / 2, 1) - math.log(args.batch)).mean() / LN2
                loss = ce + beta * rkl
            opt.zero_grad()
            loss.backward()
            opt.step()
            sched.step()
        m.eval()
        with torch.no_grad():
            u_ev = m.u_pow(h_ev, beta, False) if mode == 'power' else m.u(h_ev)
            lo, hi = pair_bounds(u_ev)
            lo2, hi2 = pair_bounds(u_ev[: args.Nev // 2])
            mc_in, mc_loo = mc_rate(u_ev, g)
            mc_in2, mc_loo2 = mc_rate(u_ev[: args.Nev // 2], g)
            ces = []
            for r in range(4):
                z = u_ev + torch.randn(u_ev.shape, generator=g, device=dev)
                ces.append(float(-(S_ev * torch.log_softmax(m.dec(z), 1)).sum(1).mean()) / LN2)
            I_dec = Hc - sum(ces) / len(ces)
            I_mix = mix_relevance(u_ev, S_ev, Hc, g)
            I_mix_half = mix_relevance(u_ev[: args.Nev // 2], S_ev[: args.Nev // 2], Hc, g)   # N/2 check (r1 #14)
        rows.append(dict(mode=mode, beta=beta, rate_lo=lo, rate_hi=hi, rate_lo_half=lo2, rate_hi_half=hi2, rate_mc=mc_in,
                         rate_mc_loo=mc_loo, rate_mc_half=mc_in2, rate_mc_loo_half=mc_loo2, I_dec=I_dec, I_mix_half=I_mix_half,
                         I_mix=I_mix, power=float((u_ev - u_ev.mean(0)).pow(2).sum(1).mean())))
        print(f"l={l} {mode}={beta}: rate KT [{lo:.3f}, {hi:.3f}] MC {mc_in:.3f} / loo {mc_loo:.3f} (half N: MC "
              f"{mc_in2:.3f} / loo {mc_loo2:.3f}) I_dec {I_dec:.3f} "
              f"I_mix {I_mix:.3f} | T {st['T']:.3f}", flush=True)
    st_c = chain['steps'][str(l)]
    res[str(l)] = dict(T=st['T'], H_next=Hc, rows=rows, discrete=dict(H=st_c['selected']['H'],
                                                                        I=st_c['selected']['I']), sec=time.time() - ts)
    json.dump(res, open(GJ, 'w'), indent=1)
print('done', time.time() - T0)
