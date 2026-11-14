"""Dev calibration on seed 9100 (CPU): output code distortion and rate, bits erased at the first backward step, and the
output-code information that survives to L/2 and to the input, over a grid of sigma and output-code sizes.
usage: calib.py --configs 8x8,16x16 --sigmas 0.1,0.2,0.3,0.5 --Ks 16,64 --out runs_dev/calib.json"""
import argparse, json, math, os, sys, time
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import bb
ap = argparse.ArgumentParser()
ap.add_argument('--configs', default='8x8,16x16')
ap.add_argument('--sigmas', default='0.1,0.2,0.3,0.5')
ap.add_argument('--Ks', default='16,64')
ap.add_argument('--seed', type=int, default=9100)
ap.add_argument('--N', type=int, default=8192)
ap.add_argument('--M', type=int, default=256)
ap.add_argument('--threads', type=int, default=4)
ap.add_argument('--out', required=True)
a = ap.parse_args()
torch.set_num_threads(a.threads)
res = json.load(open(a.out)) if os.path.exists(a.out) else {}
for cfg in a.configs.split(','):
    n, L = [int(v) for v in cfg.split('x')]
    for sigma in [float(s) for s in a.sigmas.split(',')]:
        net = bb.Net(a.seed, n, L, sigma)
        g = bb.make_gen('cpu', 'calib', a.seed, n, L, sigma)
        A = net.sample(1 << 17, L, g)
        V = float(A.double().var(0).sum())
        for K in [int(k) for k in a.Ks.split(',')]:
            key = f'{cfg}_s{sigma}_K{K}'
            if key in res:
                continue
            t0 = time.time()
            C, dist, info = bb.kmeans(A[: 1 << 16], K, g, restarts=3)
            out = bb.OutCode(C, net)
            At = net.sample(1 << 16, L, g)
            ct = out.assign_out(At)
            nmse = float(((At - C[ct]) ** 2).sum(1).mean()) / V
            Hc = bb.ent_of_marginal(torch.bincount(ct, minlength=K)[None])
            row = dict(n=n, L=L, sigma=sigma, K=K, nmse=nmse, H_cL=Hc, V=V)
            for l in sorted(set([L - 2, L - 3, L // 2, 0])):
                h = net.sample(a.N, l, g)
                if l == L - 2:
                    cnt = bb.mc_counts_next(net, l, h, out, a.M, g)
                    row['first_step'] = bb.target_stats(cnt)
                cnt = bb.mc_counts_out(net, l, h, out, a.M, g)
                row[f'I_h{l}_cL'] = bb.target_stats(cnt)['T']
            row['sec'] = time.time() - t0
            res[key] = row
            fs = row['first_step']
            print(f"{key}: nMSE {nmse:.4f} H(c_L) {Hc:.3f} | first step erased {fs['erased']:.3f} T {fs['T']:.3f} | "
                  + ' '.join(f"I(h{l};cL) {row[f'I_h{l}_cL']:.3f}" for l in sorted(set([L - 2, L - 3, L // 2, 0])))
                  + f" ({row['sec']:.0f}s)", flush=True)
            json.dump(res, open(a.out, 'w'), indent=1)
