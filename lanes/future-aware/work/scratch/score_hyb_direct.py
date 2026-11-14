"""POST HOC (GPT-6 review round 2, findings 1, 10, 13): direct scores of the H1 hybrid estimates.
Reads runs/hybd_n{N}_L{L}_s{S}.json (scratch/run_hyb_direct.py) and the registered runs/hyb_*.json (for the cost
ledger: eg_cost, setup_passes, a). Side-effect free apart from writing results/hyb_direct.{json,md}.
Per net and control (l, name), with the closure mean from the exact Gaussian recursion ('eg') or ARC K = 2 ('k2'):
  direct error curve e_Q(N) = mean over the 8 scrambles of |E_Q[c] + mean_RQMC(h_L - c) - Y|^2 / V, N = 2^8..2^16;
  equal-cost gain at C passes = plain RQMC error at C / e_Q((C - B) / a) under three ledgers:
    'reg' (registered, historical): B = eg_cost(l) + setup, a = 1 + per-sample control evaluation (run_hyb.py);
    'exp' (expanded; review round 3): the closure charged for the mean actually used (eg_cost(l) or k2_cost(l); not
          again for jacmf, whose setup already runs the Gaussian recursion to L) + setup + the work the registered
          ledger leaves out (Gram/covariance matrices, pseudo-inverses, the 2^16-sample cloud and relevance matrices of
          the quadratic control; formulas below); a as registered;
    'sum' (the evaluation run_hyb_direct.py v2 actually does): as 'exp', but the control is applied once to the sums
          (per sample only the accumulation of h_l, plus the quadratic features for regq: a = 1 + (n [+ 2 n qk +
          2 nq]) / pass) and the one-time matrix-vector products (2 n^2 [+ 2 n nq] flops) are added to B.
          An approximate cost of ONE selected control (GPT-6 review round 4): not charged are the separate computation
          of the control's closure mean (~2 n^2 more unless fused), the full qk^2 outer products and centring of the
          quadratic features, the diagnostics, and the construction of the competing controls.
  N is never above 2^16 (B > 0, a > 1),
  so the hybrid curve is interpolated, not extrapolated; N < 2^8 is not scored. Plain RQMC: (i) the same scrambles'
  plain estimate in the same run, measured to 2^16 at every width (primary, paired, no extrapolation); (ii) arc-update's
  curve, the registered comparator (extrapolated with slope -1 beyond 2^14 at n = 64, 128).
The registered best-of-controls rule (max over (l, name) per net, median over nets) selects on noisy ratios; the best
single control chosen across nets is also reported."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_helpers as S  # noqa: E402

MS = [8, 10, 12, 14, 15, 16]
OUT = {}


def curve_at(Ns, es, N):
    """log-log interpolation inside [Ns[0], Ns[-1]]; None outside (never extrapolated here)."""
    if N < Ns[0] or N > Ns[-1]:
        return None
    return float(np.exp(np.interp(np.log(N), np.log(Ns), np.log(es))))


def uncharged(name, n, L, l, nfit=1 << 15, qk=16):
    """Work the registered H1 ledger leaves out, in passes (1 pass = 2 n^2 L flops)."""
    P = 2.0 * n * n * L
    nq = qk * (qk + 1) // 2
    if name == 'jac':      # 128 true samples to layer l; averaging 128 Jacobians
        return (128 * l / L) + 128.0 * n * n / P
    if name == 'jacmf':    # the gate-probability einsums, 2 n^3 per future layer (the Jacobian product is charged)
        return (L - l) * 2.0 * n ** 3 / P
    if name == 'reg':      # Gram Cxx, cross Cfx (2 N n^2 each), pseudo-inverse (~20 n^3), product (2 n^3)
        return (4.0 * nfit * n * n + 22.0 * n ** 3) / P
    if name.startswith('regq'):
        m = n + nq          # regressors: h (n) and the quadratic features (nq)
        fl = 2.0 * nfit * m * m + 2.0 * nfit * n * m + 22.0 * m ** 3   # Gram, cross, pinv + product
        fl += 2.0 * (1 << 16) * n * n                                  # covariance S_l of the 2^16-sample cloud
        fl += 4.0 * 4096 * n * n + 10.0 * n ** 3                       # Bn = Bv - Vv Jb, Rnl = Bn^T Bn; eigensolve
        fl += 2.0 * ((1 << 16) + nfit) * n * qk + ((1 << 16) + nfit) * nq   # quadratic features on cloud and pilot
        return fl / P + (1 << 16) * l / L                              # + the 2^16 layer-l samples themselves
    raise ValueError(name)


rows_md = []
for n, L, seeds in S.CONF:
    per = {}
    repro = dict(eta=0.0, beta=0.0, old=0.0, plain=0.0)
    cross_share = []
    for s in seeds:
        p = os.path.join(S.RUNS, f'hybd_n{n}_L{L}_s{s}.json')
        if not os.path.exists(p):
            continue
        D = json.load(open(p)); R = S.load('hyb', n, L, s)
        if 'plain' not in D or str(MS[-1]) not in D['plain']:
            continue
        # reproduction of the registered values
        for l, row in R['layers'].items():
            for name, sv in row['surrogates'].items():
                sd = D['layers'][l]['surrogates'][name]
                repro['eta'] = max(repro['eta'], abs(sv['eta'] / sd['eta'] - 1))
                for q in ('eg', 'k2'):
                    repro['beta'] = max(repro['beta'], abs(sv['beta'][q] / sd['beta'][q] - 1))
                for m, v in sv['rqmc'].items():
                    repro['old'] = max(repro['old'], abs(v / np.mean(sd['rqmc'][m]['old']) - 1))
        for m, v in R['rqmc_plain'].items():
            repro['plain'] = max(repro['plain'], abs(v / np.mean(D['plain'][m]) - 1))
        Ns = np.array([2.0 ** m for m in MS])
        plain = np.array([np.mean(D['plain'][str(m)]) for m in MS])
        cur = S.rqmc_curve(n, L, s)
        net = dict(plain=dict(zip(MS, plain.tolist())), ctrl={})
        for l, row in R['layers'].items():
            l_ = int(l)
            for name, sv in row['surrogates'].items():
                sd = D['layers'][l]['surrogates'][name]
                e = {q: np.array([np.mean(sd['rqmc'][str(m)][f'dir_{q}']) for m in MS]) for q in ('eg', 'k2')}
                old_plus_beta = np.array([np.mean(sd['rqmc'][str(m)]['old']) for m in MS]) + sd['beta']['eg']
                cross_share += list((e['eg'] - old_plus_beta) / e['eg'])
                P = 2.0 * n * n * L
                quad = name.startswith('regq'); qk = 16; nq = qk * (qk + 1) // 2
                B = row['eg_cost'] + sv['setup_passes']
                clo = {'eg': (0.0 if name == 'jacmf' else row['eg_cost']), 'k2': row['k2_cost']}
                Bexp = {q: clo[q] + sv['setup_passes'] + uncharged(name, n, L, l_) for q in ('eg', 'k2')}
                a_sum = 1.0 + (n + ((2.0 * n * qk + 2.0 * nq) if quad else 0.0)) / P
                once = (2.0 * n * n + (2.0 * n * nq if quad else 0.0)) / P
                c = dict(eta=sv['eta'], beta_eg=sv['beta']['eg'], dir_eg=e['eg'].tolist(), dir_k2=e['k2'].tolist(),
                         old_plus_beta=old_plus_beta.tolist(), B=B, B_exp=Bexp, a=sv['a'], a_sum=a_sum, gain={})
                for C in (1e4, 6.5e4):
                    for led in ('reg', 'exp', 'sum'):
                      for q in ('eg', 'k2'):
                            BB = B if led == 'reg' else Bexp[q] + (once if led == 'sum' else 0.0)
                            Nn = (C - BB) / (a_sum if led == 'sum' else sv['a'])
                            eh = curve_at(Ns, e[q], Nn) if Nn > 0 else None
                            if eh is None:
                                continue
                            gp = curve_at(Ns, plain, C) / eh
                            ga = S.rqmc_err(cur, C)[0] / eh
                            c['gain'][f'{int(C)}_{led}_{q}'] = dict(paired=gp, arc=ga, N=Nn,
                                                                    arc_extrap=bool(S.rqmc_err(cur, C)[1]))
                net['ctrl'][f'{l_}/{name}'] = c
        per[s] = net
    if not per:
        continue
    res = dict(nets=sorted(per), reproduction_max_rel_diff=repro,
               cross_term_share=dict(median=S.med(cross_share), p05=float(np.percentile(cross_share, 5)),
                                     p95=float(np.percentile(cross_share, 95))))
    # l = 1 (exact control means): residual / plain at 2^14 and 2^16, direct
    l1 = {}
    for name in ('jac', 'jacmf', 'reg', 'regq16'):
        r14 = [per[s]['ctrl'][f'1/{name}']['dir_eg'][MS.index(14)] / per[s]['plain'][14] for s in per]
        r16 = [per[s]['ctrl'][f'1/{name}']['dir_eg'][MS.index(16)] / per[s]['plain'][16] for s in per]
        l1[name] = dict(eta=S.med([per[s]['ctrl'][f'1/{name}']['eta'] for s in per]), rho14=S.med(r14), rho16=S.med(r16))
    res['l1'] = l1
    # equal-cost gains: registered best-of rule and the best single control
    gains = {}
    for key in ('10000_reg_eg', '65000_reg_eg', '10000_exp_eg', '65000_exp_eg', '10000_sum_eg', '65000_sum_eg',
                '65000_reg_k2', '65000_exp_k2', '65000_sum_k2'):
        for comp in ('paired', 'arc'):
            best = []; who = []
            for s in per:
                cand = [(c['gain'][key][comp], k) for k, c in per[s]['ctrl'].items() if key in c['gain']]
                if cand:
                    g, k = max(cand); best.append(g); who.append(k)
            ctrls = sorted({k for s in per for k, c in per[s]['ctrl'].items() if key in c['gain']})
            fixed = {k: S.med([per[s]['ctrl'][k]['gain'][key][comp] for s in per if key in per[s]['ctrl'][k]['gain']])
                     for k in ctrls}
            kbest = max(fixed, key=lambda k: fixed[k]) if fixed else None
            gains[f'{key}_{comp}'] = dict(best_per_net=best, median_best=S.med(best),
                                          range=[min(best), max(best)] if best else None, chosen=who,
                                          best_fixed=kbest, best_fixed_median=fixed.get(kbest) if kbest else None)
    res['gains'] = gains
    res['per_net'] = {str(s): v for s, v in per.items()}
    OUT[str(n)] = res
    rows_md.append((n, res))

json.dump(OUT, open(os.path.join(S.RES, 'hyb_direct.json'), 'w'), indent=1, default=float)


def f(x):
    return '-' if x is None or not np.isfinite(x) else (f'{x:.2e}' if abs(x) < 1e-2 else f'{x:.3g}')


md = ['# H1 hybrid estimates scored directly (POST HOC; scratch/run_hyb_direct.py, scratch/score_hyb_direct.py)', '',
      'Direct error = |E_Q[c] + mean_RQMC(h_L - c) - Y|^2 / V, mean over 8 scrambles; Q = exact Gaussian recursion '
      'unless stated. Gains: plain RQMC error at C over the hybrid\'s direct error at N = (C - B) / a; "paired" = plain '
      'RQMC on the same scrambles in the same run (measured to 2^16, no extrapolation); "arc" = arc-update\'s curve (the '
      'registered comparator). Ledgers (see the script header): reg = registered (historical); exp = expanded (closure '
      'charged for the mean used, plus the uncharged linear algebra and the quadratic control\'s 2^16-sample cloud); '
      'sum = exp with the sum-based evaluation that run_hyb_direct.py v2 performs (an approximate cost of one selected '
      'control; see the script header for what it leaves out). Best = max over controls per net (the '
      'registered rule), median over nets; best fixed = the single control with the highest median.', '']
for n, r in rows_md:
    md.append(f'## n = {n} ({len(r["nets"])} nets)')
    rp = r['reproduction_max_rel_diff']
    md.append(f'Reproduction of the registered runs (max relative difference): eta {rp["eta"]:.1e}, beta {rp["beta"]:.1e}, '
              f'residual metric {rp["old"]:.1e}, plain RQMC {rp["plain"]:.1e}.')
    cs = r['cross_term_share']
    md.append(f'(direct - (residual metric + beta)) / direct over all controls, scrambles sizes and nets: median '
              f'{cs["median"]:.3f}, 5-95% {cs["p05"]:.3f} to {cs["p95"]:.3f}.')
    md.append('')
    md.append('| l = 1 control (exact mean) | eta | direct residual / plain RQMC at 2^14 | at 2^16 |')
    md.append('|---|---|---|---|')
    for name, v in r['l1'].items():
        md.append(f'| {name} | {f(v["eta"])} | {f(v["rho14"])} | {f(v["rho16"])} |')
    md.append('')
    md.append('| budget, ledger, closure mean | best per net vs paired plain (median; range) | best fixed control | '
              'vs arc-update curve (median) |')
    md.append('|---|---|---|---|')
    for key in ('10000_reg_eg', '10000_exp_eg', '10000_sum_eg', '65000_reg_eg', '65000_exp_eg', '65000_sum_eg',
                '65000_reg_k2', '65000_exp_k2', '65000_sum_k2'):
        gp, ga = r['gains'][f'{key}_paired'], r['gains'][f'{key}_arc']
        rng = f'{f(gp["range"][0])}-{f(gp["range"][1])}' if gp['range'] else '-'
        md.append(f'| {key.replace("_", ", ")} | {f(gp["median_best"])} ({rng}) | {gp["best_fixed"]}: '
                  f'{f(gp["best_fixed_median"])} | {f(ga["median_best"])} |')
    md.append('')
open(os.path.join(S.RES, 'hyb_direct.md'), 'w').write('\n'.join(md) + '\n')
print('\n'.join(md))
