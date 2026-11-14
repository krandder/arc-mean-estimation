"""Part S3, Kelvin's scheme (1 November, relayed by main): start as a plain autoencoder with more bits than needed, add
decoders for several horizons, shift the weight from reconstruction to the far horizons over training, then shrink
the bit budget. Two variants: reconstruction floor 0 and 0.05.

Per net (n x L, seed), layers l_0..l_m = {0, L/4, L/2, 3L/4, L-1}, one code per layer: c_i = sign(E_i(h_{l_i})), K = 32
nested sign bits (each example keeps its first b bits, b drawn log-uniformly in [1, B_max]). E_i: MLP (3 hidden layers of
width 256) on the whitened h_{l_i} only (it does not see a; it can learn to compute the future if it is able to).
Decoders from c_i: self (-> h_{l_i}), next (-> h_{l_{i+1}}), out (-> a). Losses (each relative to its target's total
variance): recon = |self - h_{l_i}|^2; next = |next - h_{l_{i+1}}|^2; out = |out - a|^2; fwd = |g_{l_i}(self) - a|^2
("sampling forward": decode, then run the true net); fwdnext = |g_{l_{i+1}}(next) - a|^2.
Schedule over T steps: A (0-20%): recon only; B (20-70%): w_recon from 1 to the floor, w_next = w_out = w_fwd =
w_fwdnext from 0 to 1; C (70-100%): weights fixed, B_max shrinks from 32 to 8.
Evaluation at the end of A, B, C: nMSE of every horizon at b in {1,2,3,4,6,8,12,16,24,32}, the mean error of fwd and
out. At the end: the transition T_i = sign(E_{i+1}(next_i(c_i))) on the first b bits (b in {4,8,12,16}): exact Walsh
spectrum, degree-d polynomial threshold accuracy of the data majority map on reachable codes, H(c_{i+1} | c_i),
baselines (as in run_chain.py).
usage: run_kelvin.py --configs 16x4 --seeds 5000 --out /root/runs/S_kelvin
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import smallnets as sn  # noqa: E402
import walsh as wl  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--configs', default='16x4')
ap.add_argument('--seeds', default='9100')
ap.add_argument('--floors', default='0,0.05')
ap.add_argument('--steps', type=int, default=4000)
ap.add_argument('--batch', type=int, default=1024)
ap.add_argument('--lr', type=float, default=1e-3)
ap.add_argument('--P_eval', type=int, default=32768)
ap.add_argument('--P_reach', type=int, default=262144)
ap.add_argument('--out', required=True)
ap.add_argument("--threads", type=int, default=2)
ap.add_argument("--trans_bs", default="4,8,12,16")
args = ap.parse_args()
torch.set_num_threads(args.threads)
os.makedirs(args.out, exist_ok=True)
DEV, DT = sn.DEV, sn.DT
FLOORS = [float(f) for f in args.floors.split(',')]
M = len(FLOORS)
K = 32
RATES = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32]
T0 = time.time()


def ste(z):
    sd = z.detach().std(1, keepdim=True).clamp(min=1e-3)
    t = torch.tanh(z / sd)
    return t + (torch.sign(z) - t).detach()


def weights(step):
    T = args.steps
    f = torch.tensor(FLOORS, device=DEV)
    if step < 0.2 * T:
        return torch.ones(M, device=DEV), torch.zeros(M, device=DEV), 32
    s = min(1.0, (step - 0.2 * T) / (0.5 * T))
    wrec = f + (1 - f) * (1 - s)
    bmax = 32 if step < 0.7 * T else int(round(32 - 24 * (step - 0.7 * T) / (0.3 * T)))
    return wrec, torch.full((M,), s, device=DEV), max(8, bmax)


class Arm(torch.nn.Module):
    def __init__(self, n, layers, frames, fr_a, starts):
        super().__init__()
        self.layers, self.frames, self.fr_a = layers, frames, fr_a
        m = len(layers)
        self.enc = torch.nn.ModuleList([sn.BMLP(M, n, K, 256, 3) for _ in range(m)])
        self.dself = torch.nn.ModuleList([sn.BMLP(M, K, n, 256, 3, last_scale=0.0) for _ in range(m)])
        self.dnext = torch.nn.ModuleList([sn.BMLP(M, K, n, 256, 3, last_scale=0.0) for _ in range(m - 1)])
        self.dout = torch.nn.ModuleList([sn.BMLP(M, K, n, 256, 3, last_scale=0.0) for _ in range(m)])
        with torch.no_grad():
            for i in range(m):
                self.dself[i].bs[-1].copy_(starts[i].view(1, 1, n).expand(M, 1, n))
                self.dout[i].bs[-1].copy_(starts[-1].view(1, 1, n).expand(M, 1, n))
                if i < m - 1:
                    self.dnext[i].bs[-1].copy_(starts[i + 1].view(1, 1, n).expand(M, 1, n))

    def code(self, i, h):
        fr = self.frames[i]
        x = (h - fr['m']) @ fr['Sm12']
        return ste(self.enc[i](x.unsqueeze(0).expand(M, *x.shape)))

    def unw(self, z, fr):
        return fr['m'] + z @ fr['S12']


for cfg in args.configs.split(','):
    n, L = [int(v) for v in cfg.split('x')]
    layers = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))
    m = len(layers)
    for seed in [int(s) for s in args.seeds.split(',')]:
        tag = f'K_n{n}_L{L}_s{seed}'
        path = os.path.join(args.out, tag + '.json')
        if os.path.exists(path):
            continue
        t1 = time.time()
        net = sn.Net(seed, n, L)
        gp = torch.Generator(device=DEV).manual_seed(10_000 + seed * 7 + n * 13 + L)
        Hp, Ap = net.sample(65536, set(layers), gp)
        V = float(Ap.double().var(0).sum())
        Vh = [float(Hp[l].double().var(0).sum()) for l in layers]
        frames = [sn.frame(Hp[l]) for l in layers]
        fr_a = sn.frame(Ap)
        i_star = int(((Ap - Ap.mean(0)) ** 2).sum(1).argmin())
        starts = [(Hp[l][i_star] - frames[i]['m']) @ frames[i]['Sm12'] for i, l in enumerate(layers)]
        starts.append((Ap[i_star] - fr_a['m']) @ fr_a['Sm12'])
        arm = Arm(n, layers, frames, fr_a, starts)
        opt = torch.optim.Adam(arm.parameters(), lr=args.lr)
        sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / 50) * (
            0.05 + 0.95 * 0.5 * (1 + math.cos(math.pi * min(s, args.steps) / args.steps))))
        gt = torch.Generator(device=DEV).manual_seed(90_000 + seed * 7 + n * 13 + L)
        res = dict(n=n, L=L, seed=seed, layers=layers, floors=FLOORS, V=V, Vh=Vh, rates=RATES, phases={})

        def losses(Hb, Ab, bvec):
            """Per-layer, per-horizon losses (M, ...) for nested truncation bvec (B,) (or a scalar b)."""
            mask = (torch.arange(K, device=DEV)[None, :] < bvec[:, None]).to(DT).unsqueeze(0)   # (1, B, K)
            out = []
            for i, l in enumerate(layers):
                c = arm.code(i, Hb[l]) * mask
                hs = arm.unw(arm.dself[i](c), frames[i])
                rec = ((hs - Hb[l]) ** 2).sum(-1) / Vh[i]
                fwd = ((net.run(hs, l) - Ab) ** 2).sum(-1) / V
                ao = arm.unw(arm.dout[i](c), fr_a)
                o = ((ao - Ab) ** 2).sum(-1) / V
                if i < m - 1:
                    l2 = layers[i + 1]
                    hn = arm.unw(arm.dnext[i](c), frames[i + 1])
                    nx = ((hn - Hb[l2]) ** 2).sum(-1) / Vh[i + 1]
                    fn = ((net.run(hn, l2) - Ab) ** 2).sum(-1) / V
                else:
                    nx = fn = torch.zeros_like(rec)
                out.append(dict(recon=rec, fwd=fwd, out=o, next=nx, fwdnext=fn))
            return out

        @torch.no_grad()
        def evaluate(phase):
            arm.eval()
            ge = torch.Generator(device=DEV).manual_seed(60_000 + seed)
            He, Ae = net.sample(args.P_eval, set(layers), ge)
            rec = {str(i): {h: [] for h in ['recon', 'fwd', 'out', 'next', 'fwdnext']} for i in range(m)}
            me = {str(i): {h: [] for h in ['fwd', 'out']} for i in range(m)}
            for b in RATES:
                acc = None
                for c0 in range(0, args.P_eval, 8192):
                    Hb = {l: He[l][c0:c0 + 8192] for l in layers}
                    Ab = Ae[c0:c0 + 8192]
                    ls = losses(Hb, Ab, torch.full((Ab.shape[0],), b, device=DEV))
                    if acc is None:
                        acc = [{k: [v.sum(1)] for k, v in d.items()} for d in ls]
                    else:
                        for d, a in zip(ls, acc):
                            for k, v in d.items():
                                a[k].append(v.sum(1))
                for i in range(m):
                    for h in rec[str(i)]:
                        rec[str(i)][h].append((torch.stack(acc[i][h]).sum(0) / args.P_eval).tolist())
                # mean errors of fwd and out at this b
                mask = (torch.arange(K, device=DEV) < b).to(DT).view(1, 1, K)
                for i, l in enumerate(layers):
                    c = arm.code(i, He[l]) * mask
                    d1 = net.run(arm.unw(arm.dself[i](c), frames[i]), l) - Ae
                    d2 = arm.unw(arm.dout[i](c), fr_a) - Ae
                    me[str(i)]['fwd'].append(((d1.double().mean(1)) ** 2).sum(-1).div(V).tolist())
                    me[str(i)]['out'].append(((d2.double().mean(1)) ** 2).sum(-1).div(V).tolist())
            arm.train()
            res['phases'][phase] = dict(nmse=rec, mean_err=me, seconds=time.time() - t1)

        for step in range(args.steps):
            wrec, wfar, bmax = weights(step)
            Hb, Ab = net.sample(args.batch, set(layers), gt)
            u = torch.rand(args.batch, generator=gt, device=DEV)
            bvec = torch.floor(torch.exp(u * math.log(bmax + 1.0))).clamp(1, bmax)
            ls = losses(Hb, Ab, bvec)
            loss = 0.0
            for d in ls:
                loss = loss + (wrec * d['recon'].mean(1)).sum() + (wfar * (d['next'].mean(1) + d['out'].mean(1) +
                                                                          d['fwd'].mean(1) + d['fwdnext'].mean(1))).sum()
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(arm.parameters(), 10.0)
            opt.step()
            sched.step()
            if step == int(0.2 * args.steps) - 1:
                evaluate('A')
            if step == int(0.7 * args.steps) - 1:
                evaluate('B')
        evaluate('C')
        # transitions T_i = sign(E_{i+1}(next_i(c_i))) on the first b bits
        arm.eval()
        rng = np.random.default_rng(80_000 + seed)
        with torch.no_grad():
            gr = torch.Generator(device=DEV).manual_seed(70_000 + seed)
            Hr, Ar = net.sample(args.P_reach, set(layers), gr)
            cr = [arm.code(i, Hr[l]) for i, l in enumerate(layers)]
            trans = {}
            for b in [int(v) for v in args.trans_bs.split(",")]:
                lst = []
                for i in range(m - 1):
                    out_mi = []
                    for mi in range(M):
                        allc = torch.cat([wl.all_codes(b), torch.zeros(2 ** b, K - b, device=DEV)], 1)
                        hn = arm.unw(arm.dnext[i](allc.unsqueeze(0).expand(M, 2 ** b, K)), frames[i + 1])[mi]
                        F = arm.code(i + 1, hn)[mi][:, :b]
                        F = torch.sign(F + 1e-9)
                        W, I_tot, nrel = wl.walsh_profile(F, b)
                        ci = cr[i][mi][:, :b]
                        cj = torch.sign(cr[i + 1][mi][:, :b] + 1e-9)
                        H_i, H_ji = wl.cond_entropy(wl.code_index(ci, b), wl.code_index(cj, b), b)
                        Cr, wr, Ymaj = wl.reachable_majority(ci, cj, b)
                        with torch.enable_grad():
                            maj = {str(d): float(wl.ptf_accuracy(Cr, Ymaj, wr, d).mean()) for d in (1, 2, 3)}
                            base = {k: wl.analyse_map(f, b, Cr, wr) for k, f in wl.baseline_maps(b, rng).items()}
                        out_mi.append(dict(floor=FLOORS[mi], learned_T=dict(W_by_degree=W.mean(0).tolist(),
                                           I_total=float(I_tot.mean()), n_relevant=float(nrel.mean())),
                                           H_in=H_i, H_out_given_in=H_ji, coverage=len(Cr) / 2 ** b,
                                           majority_ptf_acc=maj, baselines=base))
                    lst.append(out_mi)
                trans[str(b)] = lst
        res['transitions'] = trans
        res['seconds'] = time.time() - t1
        with open(path, 'w') as f:
            json.dump(res, f)
        torch.save(arm.state_dict(), path.replace('.json', '.pt'))
        C = res['phases']['C']['nmse']
        print(f'{tag}: {res["seconds"]:.0f}s | phase C fwd nMSE at b=32 by layer (floor 0, 0.05): ' +
              ' '.join(f'{C[str(i)]["fwd"][-1][0]:.3g}/{C[str(i)]["fwd"][-1][1]:.3g}' for i in range(m)) +
              ' | recon at b=32: ' + ' '.join(f'{C[str(i)]["recon"][-1][0]:.3g}/{C[str(i)]["recon"][-1][1]:.3g}'
                                              for i in range(m)) + f' | total {time.time() - T0:.0f}s', flush=True)
print('ALL DONE', f'{time.time() - T0:.0f}s', flush=True)
