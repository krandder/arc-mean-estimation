"""Kelvin's backward bit recursion on one Model S net (one chain type per run).

Chains (FORMAL.md section 7): target x rule.
  K   target next code c_{l+1}, rate rule: most relevant candidate with H(c_l) <= T_l + tolH        (Kelvin's rule)
  R   target next code, relevance rule: cheapest candidate with I(c_l; c_{l+1}) >= (1 - rho) T_l   (main's 2nd part)
  P   target output code c_L carried back one noisy layer per step: rows P~_l(h) = E_xi Qtab_{l+1}[c_{l+1}(h_{l+1})],
      rate rule
  PR  same target as P, relevance rule
Per step l = L-2 .. 0 (the code at L-1 is the output code itself: no noise between L-1 and L):
  fresh points h_l (train / select / test, independent forward paths); Monte Carlo counts of the next code (M draws of
  xi_{l+1}); target stats (Miller-Madow and Grassberger; the test draws in two halves for a Richardson check);
  posterior predictor (MLP) on soft labels; candidates (KL-k-means over a K grid + annealed DIB paths) on the predicted
  posteriors; selection on the select set; evaluation of every candidate and the selected code on the test set;
  reuse baseline (noise-free composition with the next code); look-ahead control (clustering the Monte Carlo rows);
  Pinsker-spectral lower bound on the loss of codes with at most K cells.
usage: run_chain.py --n 8 --L 8 --seed 9100 --sigma 0.3 --KL 64 --chain K --out runs_dev/x [--device cuda]
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
import bb  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--n', type=int, required=True)
ap.add_argument('--L', type=int, required=True)
ap.add_argument('--seed', type=int, required=True)
ap.add_argument('--sigma', type=float, required=True)
ap.add_argument('--KL', type=int, default=64)
ap.add_argument('--chain', choices=['K', 'R', 'P', 'PR'], required=True)
ap.add_argument('--rho', type=float, default=0.05, help='relevance rule: I >= (1 - rho) T')
ap.add_argument('--KmaxRel', type=int, default=512)
ap.add_argument('--tolH', type=float, default=0.02, help='rate tolerance for the rate rule (bits)')
ap.add_argument('--Nvq', type=int, default=1 << 18)
ap.add_argument('--Ntr', type=int, default=1 << 16)
ap.add_argument('--Mtr', type=int, default=64)
ap.add_argument('--Nsel', type=int, default=1 << 15)
ap.add_argument('--Msel', type=int, default=256)
ap.add_argument('--Nte', type=int, default=1 << 16)
ap.add_argument('--Mte', type=int, default=1024)
ap.add_argument('--width', type=int, default=256)
ap.add_argument('--depth', type=int, default=2)
ap.add_argument('--steps', type=int, default=2500)
ap.add_argument('--batch', type=int, default=8192)
ap.add_argument('--lr', type=float, default=3e-3)
ap.add_argument('--restarts', type=int, default=2)
ap.add_argument('--Kmax', type=int, default=256)
ap.add_argument('--lookahead', type=int, default=1)
ap.add_argument('--cert', type=int, default=0)
ap.add_argument('--cert_depths', default='4')
ap.add_argument('--device', default='cpu')
ap.add_argument('--threads', type=int, default=4)
ap.add_argument('--out', required=True)
ap.add_argument('--outcode_only', type=int, default=0)
args = ap.parse_args()
torch.set_num_threads(args.threads)
dev = args.device
T0 = time.time()
netname = f'n{args.n}L{args.L}_s{args.seed}_sig{args.sigma:g}_K{args.KL}'
odir = os.path.join(args.out, netname)
cdir = os.path.join(odir, f'chain{args.chain}')
TARGET_OUT = args.chain in ('P', 'PR')
RULE_REL = args.chain in ('R', 'PR')
os.makedirs(cdir, exist_ok=True)
K_GRID = [2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 19, 22, 26, 30, 35, 41, 48, 56, 64, 75, 88, 103, 120, 140, 164, 192, 224,
          256, 300, 350, 410, 480, 512]


def log(*a):
    print(f'[{time.time() - T0:7.0f}s]', *a, flush=True)


def jdump(obj, path):
    tmp = path + '.tmp'
    json.dump(obj, open(tmp, 'w'), indent=1)
    os.replace(tmp, path)


net = bb.Net(args.seed, args.n, args.L, args.sigma, dev)
L = args.L

# ---------------------------------------------------------------- output code (shared by the chains of this net)
oc_path = os.path.join(odir, 'outcode.pt')
if os.path.exists(oc_path):
    oc = torch.load(oc_path, map_location=dev)
    C = oc['C'].to(dev)
    out_info = oc['info']
else:
    g = bb.make_gen(dev, 'outcode', args.seed, args.n, L, args.sigma, args.KL)
    A = net.sample(args.Nvq, L, g)
    C, dist, kinfo = bb.kmeans(A, args.KL, g, restarts=8)
    At = net.sample(1 << 17, L, g)
    V = float(At.double().var(0).sum())
    ct = bb.assign_euclid(At, C)
    nmse = float(((At - C[ct]) ** 2).sum(1).mean()) / V
    H_cL = bb.ent_of_marginal(torch.bincount(ct, minlength=args.KL)[None])
    dists = sorted(r['dist'] for r in kinfo)
    out_info = dict(nmse=nmse, H_cL=H_cL, V=V, train_dist=dist, restart_dists=dists,
                    restart_spread=(dists[-1] - dists[0]) / dists[0], lloyd_iters=[r['iters'] for r in kinfo])
    torch.save(dict(C=C.cpu(), info=out_info), oc_path)
    log(f'output code K={args.KL}: nMSE {nmse:.4f}, H(c_L) {H_cL:.3f} bits, restart spread {out_info["restart_spread"]:.2e}')
out_code = bb.OutCode(C, net)
if args.outcode_only:
    sys.exit(0)

# ---------------------------------------------------------------- the chain
summary_path = os.path.join(cdir, 'chain.json')
summary = json.load(open(summary_path)) if os.path.exists(summary_path) else dict(
    args=vars(args), net=netname, out=out_info, steps={})
code_next = out_code                                  # code at L-1 = c_L (composition with the noiseless output layer)
Qnext = torch.eye(args.KL, dtype=torch.float64, device=dev)     # chain P: P(c_L | c_{L-1}) (exact)
summary['steps'][str(L - 1)] = dict(l=L - 1, T=out_info['H_cL'], H=out_info['H_cL'], I=out_info['H_cL'],
                                    note='code at L-1 is the output code; no noise between L-1 and L')


def target_rows(counts, M):
    P = counts.to(torch.float64) / M
    if TARGET_OUT:
        P = P @ Qnext
    return P


def rows_entropy_bc(ca, cb):
    """Per-point target entropy with bias correction from two half-sets of draws (each M/2).
    K/R: Miller-Madow on the pooled counts (and Richardson as a check); P: Richardson 2 H(M) - mean H(M/2)."""
    Mh = int(ca[0].sum())
    Pa, Pb = target_rows(ca, Mh), target_rows(cb, Mh)
    Pf = 0.5 * (Pa + Pb)
    H_full = bb.ent_rows(Pf)
    H_half = 0.5 * (bb.ent_rows(Pa) + bb.ent_rows(Pb))
    rich = 2 * H_full - H_half
    if TARGET_OUT:
        return rich, dict(H_plugin=float(H_full.mean()), H_rich=float(rich.mean()))
    mm = bb.ent_counts(ca + cb, mm=True)
    gr = bb.ent_counts_grassberger(ca + cb)
    return mm, dict(H_plugin=float(H_full.mean()), H_rich=float(rich.mean()), H_mm=float(mm.mean()),
                    H_gr=float(gr.mean()))


def rel_rows(codes, P, K):
    """Rate and relevance of a code against target rows (counts or probabilities): cell posteriors = pooled rows."""
    return bb.relevance(codes, P, K)


def lower_bound_K(Prows, Kc, M):
    """(1/(2 ln 2)) sum_{j >= Kc} lambda_j(Cov S), Cov S = Cov(rows) - E[diag(p) - p p^T]/M (multinomial MC term)."""
    X = Prows.to(torch.float64)
    Cv = torch.cov(X.T)
    if not TARGET_OUT:      # multinomial Monte Carlo term; unbiased denominator M - 1 (review r1 #8). An estimate,
        Cv = Cv - (torch.diag(X.mean(0)) - X.T @ X / X.shape[0]) / (M - 1)     # not a certified bound
    lam = torch.linalg.eigvalsh(Cv).flip(0).clamp_min(0)
    return float(lam[Kc - 1:].sum()) / (2 * LN2_) if Kc - 1 < lam.numel() else 0.0


LN2_ = math.log(2.0)

for l in range(L - 2, -1, -1):
    key = str(l)
    cpath = os.path.join(cdir, f'code_l{l}.pt')
    if key in summary['steps'] and os.path.exists(cpath):        # resume
        st = torch.load(cpath, map_location=dev)
        code_next = bb.load_code(lambda k: os.path.join(cdir, f'code_l{k}.pt'), l, L, net, out_code, dev)
        Qnext = st['Q'].to(dev)
        log(f'l={l}: resumed')
        continue
    ts = time.time()
    g = bb.make_gen(dev, 'chain', args.chain, args.seed, args.n, L, args.sigma, args.KL, l)
    t_counts0 = time.time()
    h_tr = net.sample(args.Ntr, l, g)
    h_se = net.sample(args.Nsel, l, g)
    h_te = net.sample(args.Nte, l, g)
    c_tr = bb.mc_counts_next(net, l, h_tr, code_next, args.Mtr, g)
    c_se_a = bb.mc_counts_next(net, l, h_se, code_next, args.Msel // 2, g)    # halves: select-set bias correction
    c_se_b = bb.mc_counts_next(net, l, h_se, code_next, args.Msel // 2, g)
    c_se = c_se_a + c_se_b
    c_te_a = bb.mc_counts_next(net, l, h_te, code_next, args.Mte // 2, g)
    c_te_b = bb.mc_counts_next(net, l, h_te, code_next, args.Mte // 2, g)
    c_te = c_te_a + c_te_b
    P_tr, P_se, P_te = target_rows(c_tr, args.Mtr), target_rows(c_se, args.Msel), target_rows(c_te, args.Mte)
    t_counts = time.time() - t_counts0
    # targets
    Hrow_te, hinfo = rows_entropy_bc(c_te_a, c_te_b)
    H_next_te = float(bb.ent_rows(P_te.mean(0)[None]))
    T_te = H_next_te - float(Hrow_te.mean())
    T_se_info = None
    if TARGET_OUT:                  # select set: its own Richardson correction from two halves (review r1 #5)
        Hrow_se, _ = rows_entropy_bc(c_se_a, c_se_b)
        T_se = float(bb.ent_rows(P_se.mean(0)[None])) - float(Hrow_se.mean())
    else:
        T_se_info = bb.target_stats(c_se)
        T_se = T_se_info['T']
    tstat = dict(T=T_te, se=bb.boot_se_T(P_te, Hrow_te, seed=l), se_condterm=float(Hrow_te.std()) / math.sqrt(args.Nte),
                 H_next=H_next_te, erased=float(Hrow_te.mean()), T_sel=T_se, **hinfo)
    if not TARGET_OUT:
        tstat['T_gr'] = H_next_te - hinfo['H_gr']
        tstat['T_rich'] = H_next_te - hinfo['H_rich']
    Kmax = int(min(args.KmaxRel if RULE_REL else args.Kmax,
                   max(8, 2 ** (math.ceil(max(T_se, 0.0)) + (3 if RULE_REL else 2)))))   # from the select set (r1 #6)
    Klist = [k for k in K_GRID if k <= Kmax]

    # Kelvin's "use the last encoding": the noise-free composition with the next code is a selectable candidate
    comp = bb.CompCode(code_next, net, l)
    r_reuse_se = rel_rows(comp.assign(h_se), P_se, comp.K)
    r_reuse_te = rel_rows(comp.assign(h_te), P_te, comp.K)
    reuse_ev = dict(i=-1, kind='reuse', K0=comp.K, beta='none', K=comp.K, H_tr=None, I_tr=None, H_sel=r_reuse_se['H'],
                    I_sel=r_reuse_se['I'], H=r_reuse_te['H'], I=r_reuse_te['I'], I_plugin=r_reuse_te['I_plugin'],
                    K_used=r_reuse_te['K_used'])

    def fit_select(h_fit, P_fit, depth, seed, keep_curve):
        """Predictor (depth) on soft labels, candidates, selection by the chain rule on the select set, test eval."""
        t_a = time.time()
        pred, pinfo = bb.train_predictor(h_fit, P_fit.float(), h_se, P_se.float(), width=args.width, depth=depth,
                                         steps=args.steps, batch=args.batch, lr=args.lr, seed=seed % (1 << 31),
                                         device=dev)
        pinfo['excess_ce_te'] = bb.cross_entropy_bits(pred, h_te, P_te.float()) - float(Hrow_te.mean())
        Q_fit = bb.predict(pred, h_fit)          # float32: clustering cost is O(N K K_t)
        gg = bb.make_gen(dev, 'cands', seed)
        t_b = time.time()
        cands = bb.candidates(Q_fit, gg, Klist, restarts=args.restarts, dib_K0=Kmax)
        t_c = time.time()
        q_se, q_te = bb.predict(pred, h_se), bb.predict(pred, h_te)
        ev = []
        for i, c in enumerate(cands):
            code = bb.LayerCode(pred, c['logmu'], c['logpi'], c['beta'])
            rs = rel_rows(code.assign_q(q_se), P_se, code.K)
            rt = rel_rows(code.assign_q(q_te), P_te, code.K)
            ev.append(dict(i=i, kind=c['kind'], K0=c['K0'], beta=c['beta'] if math.isfinite(c['beta']) else 'inf',
                           K=c['K'], H_tr=c['H'], I_tr=c['I'], H_sel=rs['H'], I_sel=rs['I'], H=rt['H'], I=rt['I'],
                           I_plugin=rt['I_plugin'], K_used=rt['K_used']))
        ev.append(dict(reuse_ev))
        if not RULE_REL:
            ok = [e for e in ev if e['H_sel'] <= T_se + args.tolH]
            sel = max(ok, key=lambda e: e['I_sel']) if ok else min(ev, key=lambda e: e['H_sel'])
        else:
            ok = [e for e in ev if e['I_sel'] >= (1 - args.rho) * T_se]
            sel = min(ok, key=lambda e: e['H_sel']) if ok else max(ev, key=lambda e: e['I_sel'])
        if sel['kind'] == 'reuse':
            code = comp
            codes_te = comp.assign(h_te)
        else:
            c = cands[sel['i']]
            code = bb.LayerCode(pred, c['logmu'], c['logpi'], c['beta'])
            codes_te = code.assign_q(q_te)
        r = rel_rows(codes_te, P_te, code.K)
        out = dict(kind=sel['kind'], K=code.K, beta=sel['beta'], H=r['H'], I=r['I'], I_plugin=r['I_plugin'],
                   H_sel=sel['H_sel'], I_sel=sel['I_sel'], reached=bool(ok), excess_ce_te=pinfo['excess_ce_te'],
                   t_pred=t_b - t_a, t_cands=t_c - t_b, t_eval=time.time() - t_c, n_cands=len(cands))
        env = [dict(H=ev[i]['H'], I=ev[i]['I'], K=ev[i]['K'], kind=ev[i]['kind']) for i in bb.envelope(ev)]
        return code, codes_te, Q_fit, out, pinfo, (ev if keep_curve else env)

    code, codes_te, Q_tr, sel_out, pinfo, ev = fit_select(h_tr, P_tr, args.depth,
                                                         bb.seed_of('pred', args.chain, args.seed, l), True)
    r_sel = dict(H=sel_out['H'], I=sel_out['I'], I_plugin=sel_out['I_plugin'])
    sel = sel_out
    reached = sel_out['reached']
    # certificates: an independent restart (fresh training points and draws, new seeds) and other predictor depths
    cert = {}
    if args.cert:
        h_tr2 = net.sample(args.Ntr, l, g)
        P_tr2 = target_rows(bb.mc_counts_next(net, l, h_tr2, code_next, args.Mtr, g), args.Mtr)
        for name, hf, Pf, d in [('restart', h_tr2, P_tr2, args.depth)] + [
                (f'depth{d}', h_tr, P_tr, d) for d in [int(x) for x in args.cert_depths.split(',') if x]]:
            _, _, _, o, pi, env = fit_select(hf, Pf, d, bb.seed_of('cert', name, args.chain, args.seed, l), False)
            o['curve'] = env
            cert[name] = o
    # kernel / table for the next step and for chain predictions: pooled test rows per cell
    S = torch.zeros(code.K, P_te.shape[1], dtype=torch.float64, device=dev).index_add_(0, codes_te, P_te)
    nk = torch.bincount(codes_te, minlength=code.K).to(torch.float64)
    Qcell = S / nk.clamp_min(1)[:, None]
    empty = nk == 0
    if bool(empty.any()):            # cells not hit by test points: the training points (and their target rows)
        codes_tr = comp.assign(h_tr) if isinstance(code, bb.CompCode) else code.assign_q(Q_tr)
        S2 = torch.zeros_like(S).index_add_(0, codes_tr, P_tr.to(torch.float64))
        n2 = torch.bincount(codes_tr, minlength=code.K).to(torch.float64)
        fill = empty & (n2 > 0)
        Qcell[fill] = S2[fill] / n2[fill][:, None]
    Qcell, n_filled = bb.fix_table(Qcell, P_te.mean(0))        # remaining empty rows: the marginal (review r1 #7)
    assert torch.allclose(Qcell.sum(1), torch.ones(Qcell.shape[0], dtype=Qcell.dtype, device=dev), atol=1e-6)
    # reuse baseline (Kelvin's "use the last encoding": c_{l+1}(relu(W_{l+1} h)))
    r_reuse = r_reuse_te
    # look-ahead control: cluster the Monte Carlo rows themselves; assign test points with the first half of their
    # draws, measure with the second half
    la = None
    if args.lookahead:
        la_c = bb.candidates(P_tr.float(), g, Klist, restarts=args.restarts, dib_K0=Kmax)   # with DIB (r1 #11)
        Pa = target_rows(c_te_a, args.Mte // 2)
        Pb = target_rows(c_te_b, args.Mte // 2)
        la = []
        for cc in la_c:
            cl = bb.LayerCode(None, cc['logmu'], cc['logpi'], cc['beta'])
            rr = rel_rows(cl.assign_q(Pa.float()), Pb, cl.K)
            la.append(dict(K=cc['K'], H=rr['H'], I=rr['I']))
    lb = None if TARGET_OUT else lower_bound_K(P_te, code.K, args.Mte)   # P, PR: no valid MC correction
    rec = dict(l=l, target=tstat, predictor=pinfo, Kmax=Kmax, n_cands=len(ev), selected=sel_out, cert=cert,
        deficit=tstat['T'] - r_sel['I'], overhead=r_sel['H'] - tstat['T'], lower_bound_Kcells=lb,
        reuse=dict(K=comp.K, H=r_reuse['H'], I=r_reuse['I']), lookahead=la, cands=ev,
        t_counts=t_counts, q_rows_filled=n_filled, sec=time.time() - ts)
    summary['steps'][key] = rec
    torch.save(dict(code=code.state(), Q=Qcell.cpu()), cpath)
    jdump(summary, summary_path)
    log(f"l={l}: T {tstat['T']:.3f} (erased {tstat['erased']:.3f} of {H_next_te:.3f}) | code K={code.K} H {r_sel['H']:.3f} "
        f"I {r_sel['I']:.3f} deficit {rec['deficit']:.3f} | reuse H {r_reuse['H']:.3f} I {r_reuse['I']:.3f} | "
        f"exCE {pinfo['excess_ce_te']:.4f} | {rec['sec']:.0f}s")
    code_next = code
    Qnext = Qcell
summary['done'] = True
summary['sec'] = time.time() - T0
jdump(summary, summary_path)
log('done')
