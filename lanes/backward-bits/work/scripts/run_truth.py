"""Output-level evaluation of the backward chains of one net, layer by layer (after run_chain.py).

Per layer l (fresh test points h_l; Monte Carlo over the whole future noise, M draws, counts of the output code c_L):
  truth      I*_l = I(h_l; c_L) = H(c_L) - E H(c_L | h_l)  (Miller-Madow)
  per chain  H(c_l), I(c_l; c_L) (best decoder: pooled posteriors per cell), and the chain's own prediction of c_L
             through its kernels (K, R: product of the per-step cell kernels; P: its table), I_chain = H(c_L) - CE
  direct     codes trained at layer l directly on the output code (same encoder class: posterior predictor on
             whole-future labels + DIB candidates), selected at the rate of each chain's code and at rate I*_l
  crn        shared-noise output distortion E|F(h_hat, Xi) - F(h, Xi)|^2 / V of each code with the cell-mean decoder
             and with a decoder optimised for this score (Adam on the cell states); the noise-averaged distortion
             with two independent future draws; the 0-bit baseline.
usage: run_truth.py --n 8 --L 8 --seed 9100 --sigma 0.01 --KL 64 --chains K,R_eps0.05,P --out runs_dev/x
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
ap.add_argument('--chains', default='K,R_eps0.05,P')
ap.add_argument('--layers', default='all')
ap.add_argument('--Ngt', type=int, default=1 << 16)
ap.add_argument('--Mgt', type=int, default=1024)
ap.add_argument('--Ntr', type=int, default=1 << 16)
ap.add_argument('--Mtr', type=int, default=64)
ap.add_argument('--Nsel', type=int, default=1 << 15)
ap.add_argument('--Msel', type=int, default=256)
ap.add_argument('--width', type=int, default=256)
ap.add_argument('--depth', type=int, default=2)
ap.add_argument('--steps', type=int, default=2500)
ap.add_argument('--batch', type=int, default=8192)
ap.add_argument('--restarts', type=int, default=2)
ap.add_argument('--tolH', type=float, default=0.02)
ap.add_argument('--rho', type=float, default=0.05)
ap.add_argument('--direct', type=int, default=1)
ap.add_argument('--crn', type=int, default=1)
ap.add_argument('--crn_steps', type=int, default=200)
ap.add_argument('--device', default='cpu')
ap.add_argument('--threads', type=int, default=4)
ap.add_argument('--out', required=True)
args = ap.parse_args()
torch.set_num_threads(args.threads)
dev = args.device
T0 = time.time()
L = args.L
netname = f'n{args.n}L{args.L}_s{args.seed}_sig{args.sigma:g}_K{args.KL}'
odir = os.path.join(args.out, netname)
tpath = os.path.join(odir, 'truth.json')
K_GRID = [2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 19, 22, 26, 30, 35, 41, 48, 56, 64, 75, 88, 103, 120, 140, 164, 192, 224,
          256, 300, 350, 410, 480, 512]


def log(*a):
    print(f'[{time.time() - T0:7.0f}s]', *a, flush=True)


def jdump(obj, path):
    tmp = path + '.tmp'
    json.dump(obj, open(tmp, 'w'), indent=1)
    os.replace(tmp, path)


net = bb.Net(args.seed, args.n, L, args.sigma, dev)
oc = torch.load(os.path.join(odir, 'outcode.pt'), map_location=dev)
out_code = bb.OutCode(oc['C'].to(dev), net)
KL = out_code.K
res = json.load(open(tpath)) if os.path.exists(tpath) else dict(args=vars(args), net=netname, layers={})

# chains: codes and kernels
chains = {}
for ch in [c for c in args.chains.split(',') if c]:
    cdir = os.path.join(odir, 'chain' + ch)
    if not os.path.exists(os.path.join(cdir, 'chain.json')):
        log(f'chain {ch}: missing, skipped')
        continue
    codes, Qs = {}, {}
    for l in range(L - 1):
        p = os.path.join(cdir, f'code_l{l}.pt')
        if os.path.exists(p):
            st = torch.load(p, map_location=dev)
            codes[l] = bb.load_code(lambda k, cdir=cdir: os.path.join(cdir, f'code_l{k}.pt'), l, L, net, out_code, dev)
            Qs[l] = st['Q'].to(dev).to(torch.float64)
    chains[ch] = dict(codes=codes, Q=Qs, kind=ch[0])


def chain_table(ch, l):
    """P(c_L | c_l) predicted by the chain: K/R product of kernels Q_l ... Q_{L-2}; P its own table."""
    c = chains[ch]

    def fixed(Q):          # empty rows -> mean of the other rows, all rows normalised (review r1 #7)
        ok = Q.sum(1) > 1e-12
        fb = Q[ok].mean(0) if bool(ok.any()) else torch.full((Q.shape[1],), 1.0 / Q.shape[1], dtype=Q.dtype, device=Q.device)
        Qf, nf = bb.fix_table(Q, fb)
        filled[ch] = filled.get(ch, 0) + nf
        return Qf
    if c['kind'] == 'P':
        return fixed(c['Q'][l])
    M = fixed(c['Q'][l])
    for k in range(l + 1, L - 1):
        M = M @ fixed(c['Q'][k])
    return M


def code_at(ch, l):
    if l == L - 1:
        return out_code
    return chains[ch]['codes'].get(l)


@torch.no_grad()
def crn_scores(h_tr, c_tr, K, h_te, c_te, xis1, xis2, a_te, a2_te, V, opt_steps):
    """Cell-mean decoder and a crn-optimised decoder; returns dict of normalised scores on the test points."""
    S = torch.zeros(K, h_tr.shape[1], device=dev).index_add_(0, c_tr, h_tr)
    nk = torch.bincount(c_tr, minlength=K).to(bb.DT)
    hm = S / nk.clamp_min(1)[:, None]
    hm[nk == 0] = h_tr.mean(0)
    out = {}
    for name, dec in [('mean', hm), ('opt', None)]:
        if dec is None:
            dec = optimise_decoder(hm.clone(), h_tr, c_tr, opt_steps)
        ah = net.run_xi(dec[c_te], l_cur, xis1)
        ah2 = net.run_xi(dec[c_te], l_cur, xis2)
        crn = float(((ah - a_te) ** 2).sum(1).mean()) / V
        avg = float(((ah - a_te) * (ah2 - a2_te)).sum(1).mean()) / V
        out[name] = dict(crn=crn, avg=avg)
    return out


def optimise_decoder(hd, h_tr, c_tr, steps):
    if steps <= 0:
        return hd
    hd = hd.clone().requires_grad_(True)
    opt = torch.optim.Adam([hd], lr=0.02 * float(h_tr.std()))
    g = bb.make_gen(dev, 'crnopt', args.seed, l_cur)
    N = h_tr.shape[0]
    with torch.enable_grad():
        for s in range(steps):
            idx = torch.randint(N, (4096,), generator=g, device=dev)
            xis = {k: torch.randn(4096, args.n, generator=g, device=dev) for k in range(l_cur + 1, L)}
            a = net.run_xi(h_tr[idx], l_cur, xis)
            ah = net.run_xi(hd[c_tr[idx]], l_cur, xis)
            loss = ((ah - a) ** 2).sum(1).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
    return hd.detach()


layers = list(range(L)) if args.layers == 'all' else [int(x) for x in args.layers.split(',')]
prev_direct = {'out': out_code}         # reuse candidates for the next (lower) layer's direct codes
for l in sorted(layers, reverse=True):
    key = str(l)
    if key in res['layers'] and res['layers'][key].get('done'):
        continue
    l_cur = l
    ts = time.time()
    g = bb.make_gen(dev, 'truth', args.seed, args.n, L, args.sigma, KL, l)
    h_te = net.sample(args.Ngt, l, g)
    if l == L - 1:
        cnt = torch.nn.functional.one_hot(out_code.assign(h_te), KL).to(torch.int32) * args.Mgt
    else:
        cnt = bb.mc_counts_out(net, l, h_te, out_code, args.Mgt, g)
    tst = bb.target_stats(cnt)
    tst['se_boot'] = bb.boot_se_T(cnt.to(torch.float64) / args.Mgt, bb.ent_counts(cnt, mm=True), seed=l)
    rec = dict(l=l, truth=tst, chains={}, direct={}, crn={})
    filled = {}
    Pte = cnt.to(torch.float64) / args.Mgt
    HcL = tst['H_next']
    # chains
    for ch in chains:
        code = code_at(ch, l)
        if code is None:
            continue
        cte = code.assign(h_te)
        r = bb.relevance(cte, cnt, code.K)
        tab = chain_table(ch, l) if l < L - 1 else torch.eye(KL, dtype=torch.float64, device=dev)
        ce = float(-(Pte * torch.log2(tab[cte].clamp_min(1e-12))).sum(1).mean())
        rec['chains'][ch] = dict(K=code.K, H=r['H'], I_out=r['I'], I_chain=HcL - ce, CE_chain=ce,
                                 table_rows_filled=filled.get(ch, 0))
    # direct codes on the whole-future posterior
    h_tr = net.sample(args.Ntr, l, g)
    if args.direct and l < L - 1:
        h_se = net.sample(args.Nsel, l, g)
        c_tr = bb.mc_counts_out(net, l, h_tr, out_code, args.Mtr, g)
        c_se = bb.mc_counts_out(net, l, h_se, out_code, args.Msel, g)
        P_tr, P_se = c_tr.float() / args.Mtr, c_se.float() / args.Msel
        pred, pinfo = bb.train_predictor(h_tr, P_tr, h_se, P_se, width=args.width, depth=args.depth,
                                         steps=args.steps, batch=args.batch,
                                         seed=bb.seed_of('dpred', args.seed, l) % (1 << 31), device=dev)
        pinfo['excess_ce_te'] = bb.cross_entropy_bits(pred, h_te, Pte.float()) - float(
            bb.ent_counts(cnt, mm=True).mean())
        Q_tr = bb.predict(pred, h_tr)
        T_se = bb.target_stats(c_se)['T']            # select set, before the candidates (review r2 #1)
        Kmax = int(min(512, max(8, 2 ** (math.ceil(max(T_se, 0.0)) + 3))))
        cands = bb.candidates(Q_tr, g, [k for k in K_GRID if k <= Kmax], restarts=args.restarts, dib_K0=Kmax)
        q_se, q_te = bb.predict(pred, h_se), bb.predict(pred, h_te)
        T_se = bb.target_stats(c_se)['T']
        ev, objs = [], []
        for i, c in enumerate(cands):
            code = bb.LayerCode(pred, c['logmu'], c['logpi'], c['beta'])
            rs = bb.relevance(code.assign_q(q_se), c_se, code.K)
            rt = bb.relevance(code.assign_q(q_te), cnt, code.K)
            ev.append(dict(i=i, kind=c['kind'], K=c['K'], H_sel=rs['H'], I_sel=rs['I'], H=rt['H'], I=rt['I']))
            objs.append(code)
        # the comparator also gets every chain's code at l and the reuse of the layer l+1 direct codes (review r1 #12)
        extra = {f'chain{ch}': code_at(ch, l) for ch in chains if code_at(ch, l) is not None}
        extra.update({f'reuse_{k}': bb.CompCode(v, net, l) for k, v in prev_direct.items()})
        for name, code in extra.items():
            rs = bb.relevance(code.assign(h_se), c_se, code.K)
            rt = bb.relevance(code.assign(h_te), cnt, code.K)
            ev.append(dict(i=len(objs), kind=name, K=code.K, H_sel=rs['H'], I_sel=rs['I'], H=rt['H'], I=rt['I']))
            objs.append(code)
        sels = {}
        # rate budgets from the select set: each chain code's rate measured on the direct select points (r1 #6)
        targets = {f'rate_{ch}': bb.relevance(code_at(ch, l).assign(h_se), c_se, code_at(ch, l).K)['H']
                   for ch in rec['chains'] if code_at(ch, l) is not None}
        targets['rate_truth'] = T_se
        for name, R in targets.items():
            ok = [e for e in ev if e['H_sel'] <= R + args.tolH]
            if ok:
                e = max(ok, key=lambda e: e['I_sel'])
                sels[name] = dict(i=e['i'], H=e['H'], I=e['I'], K=e['K'], rate=R, kind=e['kind'])
        ok = [e for e in ev if e['I_sel'] >= (1 - args.rho) * T_se]
        if ok:
            e = min(ok, key=lambda e: e['H_sel'])
            sels['relevance_rho'] = dict(i=e['i'], H=e['H'], I=e['I'], K=e['K'], kind=e['kind'])
        else:
            e = max(ev, key=lambda e: e['I_sel'])
            sels['relevance_rho'] = dict(i=e['i'], H=e['H'], I=e['I'], K=e['K'], kind=e['kind'], unreached=True)
        env = bb.envelope(ev)
        rec['direct'] = dict(predictor=pinfo, selected=sels, curve=[dict(H=ev[i]['H'], I=ev[i]['I'], K=ev[i]['K'])
                                                                    for i in env])
        direct_codes = {name: objs[s['i']] for name, s in sels.items()}
        prev_direct = {k: direct_codes[k] for k in ('rate_truth', 'relevance_rho') if k in direct_codes}
    else:
        direct_codes = {}
    # crn and noise-averaged output distortion
    if args.crn and l < L - 1:
        xis1 = {k: torch.randn(args.Ngt, args.n, generator=g, device=dev) for k in range(l + 1, L)}
        xis2 = {k: torch.randn(args.Ngt, args.n, generator=g, device=dev) for k in range(l + 1, L)}
        a_te = net.run_xi(h_te, l, xis1)
        a2_te = net.run_xi(h_te, l, xis2)
        V = float(a_te.double().var(0).sum())
        rec['crn']['V'] = V
        zero_tr = torch.zeros(h_tr.shape[0], dtype=torch.long, device=dev)
        zero_te = torch.zeros(h_te.shape[0], dtype=torch.long, device=dev)
        rec['crn']['zero_bit'] = crn_scores(h_tr, zero_tr, 1, h_te, zero_te, xis1, xis2, a_te, a2_te, V,
                                            args.crn_steps)
        allcodes = {f'chain{ch}': code_at(ch, l) for ch in chains if code_at(ch, l) is not None}
        allcodes.update({f'direct_{k}': v for k, v in direct_codes.items()})
        for name, code in allcodes.items():
            sc = crn_scores(h_tr, code.assign(h_tr), code.K, h_te, code.assign(h_te), xis1, xis2, a_te, a2_te, V,
                            args.crn_steps)
            rec['crn'][name] = sc
    rec['done'] = True
    rec['sec'] = time.time() - ts
    res['layers'][key] = rec
    jdump(res, tpath)
    msg = ' | '.join(f"{ch}: H {v['H']:.2f} I_out {v['I_out']:.3f} I_chain {v['I_chain']:.3f}"
                     for ch, v in rec['chains'].items())
    dmsg = ' '.join(f"{k} H {v['H']:.2f} I {v['I']:.3f}" for k, v in rec['direct'].get('selected', {}).items())
    log(f"l={l}: I*(h;c_L) {tst['T']:.3f} | {msg} | direct {dmsg} | {rec['sec']:.0f}s")
res['done'] = True
jdump(res, tpath)
log('done')
