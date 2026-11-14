"""Descriptive tables for the report (post hoc presentation of the registered runs; the registered statistics are in
results/score_part1.json from scratch/score_part1.py). Writes results/tables_part1.md.
Review round 2 (findings 2, 3): imports the side-effect-free copies in score_helpers.py (importing score_part1 re-ran the
scorer and rewrote its output); T2 shows the raw b2 and the literal truth-floor ratios next to the hashed scorer's floored
statistic, each labelled; T4 is labelled as the residual-against-reference metric (the hybrid's direct error is in
results/hyb_direct.md)."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_helpers as S  # noqa: E402  (side-effect free)

RES = S.RES
CONF = S.CONF
out = []; J = {}


def fmt(x, p=2):
    if x is None or not np.isfinite(x):
        return '-'
    return f'{x:.{p}e}' if (abs(x) < 1e-2 or abs(x) >= 1e3) else f'{x:.{p + 1}g}'


def med(v):
    return S.med(v)


# ---- T1: single-cut benchmark ----
out.append('## T1. Single-cut benchmark (B1): median over nets of b2 (squared single-cut defect, nMSE)\n')
for n, L, seeds in CONF:
    ds = [S.load('cut', n, L, s) for s in seeds]
    ds = [d for d in ds if d]
    if not ds:
        continue
    cuts = sorted({int(c) for d in ds for c in d['cuts']})
    ks = [4, 16, n // 4, n // 2]
    cols = ['true', 'gauss', 'radg'] + [f'cond_{kd}{k}' for kd in ('futnl', 'pca', 'rand') for k in ks] + \
        ['radg_futnl16', f'radg_futnl{n // 4}', 'radg_pca16', f'radg_pca{n // 4}', 'edge_futnl16', 'edge_pca16']
    cols = list(dict.fromkeys(cols))
    out.append(f'\n### n = {n}, L = {L} ({len(ds)} nets)\n')
    out.append('| variant | ' + ' | '.join(f'l = {c}' for c in cuts) + ' |')
    out.append('|---|' + '---|' * len(cuts))
    for v in cols:
        row = []
        for c in cuts:
            vals = [d['cuts'][str(c)]['variants'].get(v, {}).get('b2') for d in ds if str(c) in d['cuts']]
            row.append(fmt(med([x for x in vals if x is not None])))
        out.append(f'| {v} | ' + ' | '.join(row) + ' |')
    # relevance spectra: top-k shares of the whitened nonlinear relevance (median over nets)
    out.append('\nWhitened nonlinear-relevance spectrum (median over nets): share of the trace in the top k, and stable '
               'rank tr/top:\n')
    kcols = list(dict.fromkeys([4, 16, n // 4, min(n // 2, 128)]))   # distinct k values (n = 64: 16 = n/4)
    out.append('| cut | ' + ' | '.join(f'top-{k}' for k in kcols) + ' | tr / top eigenvalue | participation ratio |')
    out.append('|---|' + '---|' * (len(kcols) + 2))
    for c in cuts:
        sh = {k: [] for k in kcols}; sr = []; prs = []
        for d in ds:
            if str(c) not in d['cuts']:
                continue
            cr = d['cuts'][str(c)]
            sp = np.array(cr['rel_nl_spec_top']); tr = cr['rel_nl_trace']
            for k in sh:
                sh[k].append(float(sp[:k].sum() / tr))
            sr.append(float(tr / sp[0])); prs.append(float(tr ** 2 / np.sum(sp ** 2)))
        out.append(f'| {c} | ' + ' | '.join(f'{med(sh[k]):.3f}' for k in sh) + f' | {med(sr):.1f} | {med(prs):.1f} |')

# ---- T2: recursion benchmark and its honest cost ----
out.append('\n## T2. Full-recursion benchmark (B2): median over nets of the squared recursion defect; improvement over '
           'the Gaussian closure; the particle recursion as an estimator at its flop-counted cost\n')
out.append('"raw b2" is the measured squared defect; "floored" is the hashed scorer\'s statistic max(b2, noise, 1e-7) '
           '(deviations item 8), kept because the registered P2-P4 outcomes were scored with it. "literal" ratios use raw b2 '
           'and drop values below 10x the truth floor (6e-8 at n = 64, 128; 1.5e-8 at n = 256), as the PREREG wording reads; '
           'the report quotes the raw and literal columns.\n')
out.append('| n | variant | median raw b2 | median floored b2 (hashed scorer) | gauss/variant, literal (median of per-net '
           'ratios; nets used) | gauss/variant, floored (hashed scorer) | passes per replicate | median per-replicate nMSE | '
           'G_RQMC at own cost |')
out.append('|---|---|---|---|---|---|---|---|---|')
for n, L, seeds in CONF:
    ds = {s: S.load('rec', n, L, s) for s in seeds}
    ds = {s: d for s, d in ds.items() if d}
    if not ds:
        continue
    vs = list(dict.fromkeys(v for d in ds.values() for v in d['variants']))
    for v in vs:
        b2s, rat, cost, nm, G = [], [], [], [], []
        raws, rlit = [], []
        lim = 10 * S.FLOOR[n]
        for s, d in ds.items():
            r = d['variants'].get(v)
            if r is None:
                continue
            b2 = S.rec_b2(d, v); b2s.append(b2)
            g = S.rec_b2(d, 'gauss')
            if g and b2:
                rat.append(g / b2)
            rb, rg = S.raw_b2(d, v), S.raw_b2(d, 'gauss')
            if rb is not None:
                raws.append(rb)
            if rb is not None and rg is not None and rb > lim and rg > lim:
                rlit.append(rg / rb)
            if 'passes_per_rep' in r:
                cost.append(r['passes_per_rep']); e = float(np.mean(r['nmse_reps'])); nm.append(e)
                er, _ = S.rqmc_err(S.rqmc_curve(n, L, s), r['passes_per_rep']); G.append(er / e)
        out.append(f'| {n} | {v} | {fmt(med(raws))} | {fmt(med(b2s))} | {fmt(med(rlit))} ({len(rlit)}) | {fmt(med(rat))} | '
                   f'{fmt(med(cost))} | {fmt(med(nm))} | {fmt(med(G))} |')

# ---- T3: D1 ----
out.append('\n## T3. Deductive (b)/(a): ARC k3 with the third cumulant projected on k directions (D1)\n')
out.append('| n | variant | median nMSE | median R | passes (this implementation) | G_RQMC there | '
           'best-case C_ded | G_RQMC at C_ded |')
out.append('|---|---|---|---|---|---|---|---|')
for n, L, seeds in CONF:
    ds = {s: S.load('k3p', n, L, s) for s in seeds}
    ds = {s: d for s, d in ds.items() if d}
    if not ds:
        continue
    k2 = [d['k2']['nmse'] for d in ds.values()]
    out.append(f'| {n} | ARC k2 (simple) | {fmt(med(k2))} | 0 | {fmt(med([d["k2"]["passes"] for d in ds.values()]))} | '
               f'{fmt(med([S.rqmc_err(S.rqmc_curve(n, L, s), d["k2"]["passes"])[0] / d["k2"]["nmse"] for s, d in ds.items()]))} | - | - |')
    vs = list(dict.fromkeys(v for d in ds.values() for v in d['variants']))
    for v in vs:
        e, R, C, G, Cd, Gd = [], [], [], [], [], []
        for s, d in ds.items():
            r = d['variants'].get(v)
            if r is None or not np.isfinite(r['nmse']):
                continue
            e.append(r['nmse']); C.append(r['passes'])
            e2 = d['k2']['nmse']; e3 = d['variants'].get('none', {}).get('nmse')
            if e3 is not None and e2 > e3:
                R.append((e2 - r['nmse']) / (e2 - e3))
            cur = S.rqmc_curve(n, L, s)
            G.append(S.rqmc_err(cur, r['passes'])[0] / r['nmse'])
            if r['kind'] in ('futv', 'futmf2', 'pca'):
                k = r['k']
                cb = (1 << 11) * 3 * (L - 1) / 2.0 if r['kind'] == 'futv' else (2.0 * n if r['kind'] == 'futmf2' else 0.0)
                cd = d['k2']['passes'] + k + 1.5 * k ** 4 / n ** 2 + cb
                Cd.append(cd); Gd.append(S.rqmc_err(cur, cd)[0] / r['nmse'])
        out.append(f'| {n} | {v} | {fmt(med(e))} | {fmt(med(R))} | {fmt(med(C))} | {fmt(med(G))} | {fmt(med(Cd))} | '
                   f'{fmt(med(Gd))} |')

# ---- T4: hybrid ----
out.append('\n## T4. Hybrid (H1): residual share eta, closure bias beta (exact Gaussian recursion), RQMC on the '
           'residual vs on h_L (median over nets)\n')
out.append('The residual column is |mean_RQMC(h_L - c) - (Y - E_P[c])|^2 / V, the residual against a reference mean. It is '
           'NOT the hybrid estimator\'s error: that is |E_Q[c] + mean_RQMC(h_L - c) - Y|^2 / V, which also contains a cross '
           'term between the residual error and the closure-mean error (review round 2, finding 1). The direct scores are in '
           'results/hyb_direct.md (scratch/run_hyb_direct.py, scratch/score_hyb_direct.py).\n')
for n, L, seeds in CONF:
    ds = [S.load('hyb', n, L, s) for s in seeds]
    ds = [d for d in ds if d]
    if not ds:
        continue
    out.append(f'\n### n = {n} ({len(ds)} nets); plain RQMC nMSE at N = 2^8..2^14: ' +
               ', '.join(fmt(med([d['rqmc_plain'][m] for d in ds if 'rqmc_plain' in d and m in d['rqmc_plain']]))
                         for m in ('8', '10', '12', '14')))
    out.append('\n| l | control | eta | beta_eg | beta_k2 | residual RQMC nMSE at 2^8, 2^10, 2^12, 2^14 |')
    out.append('|---|---|---|---|---|---|')
    for l in sorted({int(x) for d in ds for x in d['layers']}):
        for name in ('jac', 'jacmf', 'reg', 'regq16'):
            rows = [d['layers'][str(l)]['surrogates'][name] for d in ds if str(l) in d['layers']
                    and name in d['layers'][str(l)]['surrogates']]
            if not rows:
                continue
            rq = ', '.join(fmt(med([r['rqmc'].get(m) for r in rows if m in r['rqmc']])) for m in ('8', '10', '12', '14'))
            out.append(f'| {l} | {name} | {fmt(med([r["eta"] for r in rows]))} | '
                       f'{fmt(med([r["beta"]["eg"] for r in rows]))} | {fmt(med([r["beta"]["k2"] for r in rows]))} | {rq} |')

open(os.path.join(RES, 'tables_part1.md'), 'w').write('# future-aware result tables (scratch/tables_part1.py)\n\n'
                                                       + '\n'.join(out) + '\n')
print('wrote', os.path.join(RES, 'tables_part1.md'))
