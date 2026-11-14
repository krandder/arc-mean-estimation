"""Score PREREG Part 1 (P1-P8 and validity) from runs/s1_*, s2_*, s3_*. Writes results/scores.json, results/scorecard.md.
Uses the frozen fit protocol (frozen/fit.py)."""
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT, 'frozen'))
import fit as FT  # noqa: E402
import line as LN  # noqa: E402


def load(pattern):
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'runs', pattern))):
        d = json.load(open(f))
        key = (d['family'], d['n'], d['L'], d['seed'])
        if key in out:
            out[key]['methods'].update(d['methods'])
        else:
            out[key] = d
    return out


def alpha(rows):
    """Frozen fit protocol; the registered rule needs at least four valid (finite, positive) points (else NaN)."""
    if rows is None:
        return (float('nan'), float('nan'))
    rows = [r for r in rows if np.isfinite(r.get('nmse_rep', float('nan'))) and r['nmse_rep'] > 0]
    if len(rows) < 4:
        return (float('nan'), float('nan'))
    r = FT.fit_curve(rows, 0.6)
    return (r['alpha'], r['se']) if r else (float('nan'), float('nan'))


# expected (method -> (pmin, pmax)) per suite, from PREREG Part 1 and Amendments 1-2 (review finding 7)
def expected(family, n, L, seed):
    if family == 'small':
        pmax_pi = 13 if n == 8 else 14
        return {'RQMC': (6, 18), 'RQMCRB': (6, 18), 'PI_rand': (2, pmax_pi), 'PI_as': (2, pmax_pi)}
    if family == 'nd':
        return {'RQMC': (6, 16), 'RQMCRB': (6, 16), 'RQMCJ': (6, 16), 'PIJ_as': (2, 11), 'PIJ_rand': (2, 11),
                'MLMC_32': (8, 16)}
    if n == 256:
        return {'RQMC': (6, 14), 'RQMCRB': (6, 14), 'PI_as_w': (1, 6 if seed == 201 else 5), 'PI_rand_w': (1, 5),
                'MLMC_16': (8, 14)}
    pmax_pi = {32: 11, 64: 9, 128: 8}[n]
    return {'RQMC': (6, 14), 'RQMCRB': (6, 14), 'PI_as_w': (2, pmax_pi), 'PI_rand_w': (2, pmax_pi),
            'MLMC_%d' % (L // 2): (8, 14)}


def complete(d):
    """True if every expected method of this net has every registered (or amended) budget lo..hi and the registered
    replicate count (16 for small nets, 8 otherwise)."""
    exp = expected(d['family'], d['n'], d['L'], d['seed'])
    reps_needed = 16 if d['family'] == 'small' else 8
    if d.get('reps') != reps_needed:                    # metadata must be present and match
        return False
    for m, (lo, hi) in exp.items():
        rows = d['methods'].get(m)
        if not rows:
            return False
        byp = {r['p']: r for r in rows}
        for q in range(lo, hi + 1):
            r = byp.get(q)
            if r is None or r.get('N') != (1 << q) or not np.isfinite(r.get('nmse_rep', float('nan'))) \
                    or r['nmse_rep'] <= 0:
                return False
    return True


def registered_rows(d, m):
    """Rows of method m inside its registered (or amended) budget range; extra budgets are post hoc."""
    exp = expected(d['family'], d['n'], d['L'], d['seed'])
    rows = d['methods'].get(m, [])
    if m in exp:
        lo, hi = exp[m]
        rows = [r for r in rows if lo <= r['p'] <= hi]
    return rows


EXPECTED_NETS = {'s1': [('small', n, L, s) for (n, L) in ((4, 2), (6, 3), (8, 4)) for s in (11, 12, 13)],
                 's2': [('nd', 8, 256, s) for s in (203, 216, 217, 220, 221, 223)],
                 's3': [('arc', n, L, s) for (n, L) in ((32, 4), (64, 8), (128, 16)) for s in (302, 303, 304)]
                 + [('arc', 256, 32, s) for s in (201, 202, 203, 204)]}


def status(coll, suite, pred=lambda k: True):
    keys = [k for k in EXPECTED_NETS[suite] if pred(k)]
    missing = [list(k) for k in keys if k not in coll or not complete(coll[k])]
    return missing


def interp(rows, cost):
    c = np.array([r['cost'] for r in rows])
    y = np.array([r['nmse_rep'] for r in rows])
    if cost < c.min() * (1 - 1e-9) or cost > c.max() * (1 + 1e-9):
        return float('nan')
    return float(np.exp(np.interp(math.log(cost), np.log(c), np.log(y))))


def common_ratio(rows_a, rows_b):
    """Ratios nMSE_a / nMSE_b at b's cost points inside a's range."""
    out = []
    for r in rows_b:
        v = interp(rows_a, r['cost'])
        if np.isfinite(v):
            out.append(v / r['nmse_rep'])
    return out


def local_alpha(rows, last=3):
    rr = rows[-last:]
    X = np.log([r['cost'] for r in rr])
    Y = np.log([r['nmse_rep'] for r in rr])
    return -np.polyfit(X, Y, 1)[0]


def main():
    s1 = load('s1_small_*.json')
    s2 = load('s2_nd_*.json')
    s3 = load('s3_arc_*.json')
    kb = json.load(open(os.path.join(ROOT, 'frozen', '..', 'results', 'kernel_bound.json')))
    sc = {}
    lines = []
    # ---- P1, P2 (S3)
    p1, p2r, p2a = [], [], []
    for key, d in sorted(s3.items()):
        n, L = key[1], key[2]
        wt = LN.Weight('student', n - 1)
        psi0 = math.atan(wt.window(1e-8))
        pred = 3 + n * L * 2 * psi0 / math.pi
        for meth in ('PI_rand_w', 'PI_as_w'):
            rows = d['methods'].get(meth)
            if not rows:
                continue
            vm = rows[-1]['vertices_mean']
            vr = rows[-1]['line_var_ratio']
            vr_corr = vr + rows[-1]['nmse_rep']        # I.var(0) of dependent RQMC lines misses Var(mean) (review 12)
            if meth == 'PI_rand_w':
                p1.append(dict(net=key, vertices=vm, pred=pred, ratio=vm / pred, ok=0.6 <= vm / pred <= 1.5))
                if n >= 64:
                    p2r.append(dict(net=key, vr=vr, vr_corrected=vr_corr, ok=vr >= 0.8))
            elif n >= 64:
                p2a.append(dict(net=key, vr=vr, vr_corrected=vr_corr, ok=vr >= 0.6))
    sc['P1'] = dict(rows=[{**r, 'net': list(r['net'])} for r in p1], holds=sum(r['ok'] for r in p1), of=len(p1),
                    verdict=bool(p1) and all(r['ok'] for r in p1))
    sc['P2'] = dict(rand=[{**r, 'net': list(r['net'])} for r in p2r], active=[{**r, 'net': list(r['net'])} for r in p2a],
                    verdict=bool(p2r) and all(r['ok'] for r in p2r) and all(r['ok'] for r in p2a))
    # ---- P3a, P3b, P3c (S3)
    p3a, p3b, p3c32, p3c64 = [], [], [], []
    for key, d in sorted(s3.items()):
        n = key[1]
        M = d['methods']
        if 'RQMC' not in M:
            continue
        rq = M['RQMC']
        ratios = []
        for c in rq:
            vals = [interp(M[m], c['cost']) for m in ('PI_as_w', 'PI_rand_w') if m in M]
            vals = [v for v in vals if np.isfinite(v)]
            if vals:
                ratios.append(min(vals) / c['nmse_rep'])
        p3a.append(dict(net=list(key), min_ratio=min(ratios) if ratios else float('nan'), npts=len(ratios),
                        ok=bool(ratios) and min(ratios) >= 10.0))
        a_rq = alpha(rq)[0]
        a_as = alpha(M['PI_as_w'])[0] if 'PI_as_w' in M else float('nan')
        a_rd = alpha(M['PI_rand_w'])[0] if 'PI_rand_w' in M else float('nan')
        a_best = np.nanmax([a_as, a_rd])
        rec = dict(net=list(key), alpha_rqmc=a_rq, alpha_pi_as=a_as, alpha_pi_rand=a_rd, alpha_pi_best=float(a_best))
        if n >= 128:
            p3b.append({**rec, 'ok': a_best <= a_rq + 0.15})
        elif n == 32:
            p3c32.append({**rec, 'steeper': a_as > a_rq + 0.1})
        elif n == 64:
            p3c64.append({**rec, 'steeper': a_as > a_rq + 0.1})
    sc['P3a'] = dict(rows=p3a, holds=sum(r['ok'] for r in p3a), of=len(p3a), verdict=bool(p3a) and all(r['ok'] for r in p3a))
    sc['P3b'] = dict(rows=p3b, holds=sum(r['ok'] for r in p3b), of=len(p3b), verdict=sum(r['ok'] for r in p3b) >= 5)
    sc['P3c'] = dict(n32=p3c32, n64=p3c64, steeper32=sum(r['steeper'] for r in p3c32),
                     steeper64=sum(r['steeper'] for r in p3c64),
                     verdict=sum(r['steeper'] for r in p3c32) >= 2 and sum(r['steeper'] for r in p3c64) <= 1)
    # ---- P4 (S1)
    p4 = []
    for key, d in sorted(s1.items()):
        M = d['methods']
        if not all(m in M for m in ('RQMCRB', 'RQMC', 'PI_as', 'PI_rand')):
            continue
        a_rb = alpha(M['RQMCRB'])[0]
        a_rq = alpha(M['RQMC'])[0]
        a_as = alpha(M['PI_as'])[0]
        a_rd = alpha(M['PI_rand'])[0]
        dd = key[1]
        p4.append(dict(net=list(key), alpha_rqmc=a_rq, alpha_rqmcrb=a_rb, alpha_pi_as=a_as, alpha_pi_rand=a_rd,
                       f5_rb=1 + 3.0 / (dd - 1), f5_pi=1 + 4.0 / (dd - 2), ok=a_as > a_rb + 0.1,
                       ratio_at_top=common_ratio(M['PI_as'], M['RQMCRB'])[-1:] or [float('nan')]))
    sc['P4'] = dict(rows=p4, holds=sum(r['ok'] for r in p4), of=len(p4), verdict=sum(r['ok'] for r in p4) >= 6)
    # ---- P5 (S2)
    p5a, p5b = [], []
    for key, d in sorted(s2.items()):
        M = d['methods']
        if 'RQMCJ' not in M:
            continue
        rj = M['RQMCJ']
        worse_all = True
        ratios = []
        for c in rj:
            vals = [interp(M[m], c['cost']) for m in ('PIJ_as', 'PIJ_rand') if m in M]
            vals = [v for v in vals if np.isfinite(v)]
            if vals:
                ratios.append(min(vals) / c['nmse_rep'])
        worse_all = bool(ratios) and min(ratios) > 1.0
        p5a.append(dict(net=list(key), min_ratio=min(ratios) if ratios else float('nan'), npts=len(ratios), ok=worse_all))
        if not all(m in M for m in ('PIJ_as', 'PIJ_rand', 'RQMC', 'RQMCRB')):
            continue
        a_j = alpha(rj)[0]
        a_best = np.nanmax([alpha(M[m])[0] for m in ('PIJ_as', 'PIJ_rand') if m in M])
        p5b.append(dict(net=list(key), alpha_rqmcj=a_j, alpha_pij_best=float(a_best),
                        alpha_pij_as=alpha(M['PIJ_as'])[0], alpha_pij_rand=alpha(M['PIJ_rand'])[0],
                        alpha_rqmc=alpha(M['RQMC'])[0], alpha_rqmcrb=alpha(M['RQMCRB'])[0],
                        ok=abs(a_best - a_j) < 0.3))
    sc['P5a'] = dict(rows=p5a, holds=sum(r['ok'] for r in p5a), of=len(p5a), verdict=sum(r['ok'] for r in p5a) >= 5)
    sc['P5b'] = dict(rows=p5b, holds=sum(r['ok'] for r in p5b), of=len(p5b), verdict=sum(r['ok'] for r in p5b) >= 4)
    # ---- P6, P7 (S3 RQMC)
    p6, p7 = [], []
    for key, d in sorted(s3.items()):
        n, L = key[1], key[2]
        rq = d['methods'].get('RQMC')
        if not rq:
            continue
        b = kb.get('%dx%d' % (n, L))
        pts = sorted((int(k.split('^')[1]), v['N_times_nmse_lb']) for k, v in b['bounds'].items() if k.startswith('points'))
        lx = np.array([p[0] for p in pts], dtype=float)
        ly = np.array([p[1] for p in pts])
        worst = float('inf')
        for r in rq:
            lb = float(np.interp(r['p'], lx, ly))
            worst = min(worst, r['N'] * r['nmse_rep'] / lb if lb > 0 else float('inf'))
        p6.append(dict(net=list(key), min_measured_over_bound=worst, ok=worst >= 1.0))
        la = local_alpha(rq, 3)
        p7.append(dict(net=list(key), local_alpha=float(la), ok=la <= 1.3,
                       N_nmse_last=[r['N'] * r['nmse_rep'] for r in rq[-3:]]))
    sc['P6'] = dict(rows=p6, holds=sum(r['ok'] for r in p6), of=len(p6), verdict=bool(p6) and all(r['ok'] for r in p6))
    sc['P7'] = dict(rows=p7, holds=sum(r['ok'] for r in p7), of=len(p7), verdict=sum(r['ok'] for r in p7) >= 10)
    # ---- P8 (MLMC)
    p8 = []
    for coll in (s2, s3):
        for key, d in sorted(coll.items()):
            for m in d['methods']:
                if m.startswith('MLMC'):
                    rows = registered_rows(d, m)
                    a = alpha(rows)[0]
                    p8.append(dict(net=list(key), method=m, alpha=a, ok=0.8 <= a <= 1.2))
    sc['P8'] = dict(rows=p8, holds=sum(r['ok'] for r in p8), of=len(p8), verdict=bool(p8) and all(r['ok'] for r in p8))
    # ---- validity: bias flags
    flags, cells = {}, {}
    for coll in (s2, s3):
        for key, d in coll.items():
            for m in d['methods']:
                for r in registered_rows(d, m):
                    if 'bias_ratio' in r:
                        cells[m] = cells.get(m, 0) + 1
                        if r['bias_ratio'] > 16:
                            flags.setdefault(m, []).append([list(key), r['p'], r['bias_ratio']])
    sc['validity'] = dict(cells=cells, flags=flags,
                          suspect=[m for m in cells if len(flags.get(m, [])) > 0.1 * cells[m]])
    # ---- completeness (review finding 7): a verdict is 'pending' while any net it needs is incomplete
    miss = dict(
        P1=status(s3, 's3'), P2=status(s3, 's3', lambda k: k[1] >= 64), P3a=status(s3, 's3'),
        P3b=status(s3, 's3', lambda k: k[1] >= 128), P3c=status(s3, 's3', lambda k: k[1] in (32, 64)),
        P4=status(s1, 's1'), P5a=status(s2, 's2'), P5b=status(s2, 's2'), P6=status(s3, 's3'), P7=status(s3, 's3'),
        P8=status(s2, 's2') + status(s3, 's3'))
    for t, m in miss.items():
        sc[t]['missing_or_incomplete'] = m
        if m:
            sc[t]['verdict'] = 'pending'
    json.dump(sc, open(os.path.join(ROOT, 'results', 'scores.json'), 'w'), indent=1, default=float)
    # ---- scorecard
    L_ = ['| test | prediction | outcome |', '|---|---|---|']

    def v(x):
        if x == 'pending':
            return 'PENDING'
        return 'holds' if x else 'fails'
    L_.append('| P1 cost law (window vertices / Rice) | in [0.6, 1.5] on 13 of 13 | %s, %d of %d (ratios %s) |' % (
        v(sc['P1']['verdict']), sc['P1']['holds'], sc['P1']['of'],
        ', '.join('%.2f' % r['ratio'] for r in sc['P1']['rows'])))
    L_.append('| P2 line variance ratio, n >= 64 | rand >= 0.8, active >= 0.6 on all | %s (rand %s; active %s) |' % (
        v(sc['P2']['verdict']), ', '.join('%.2f' % r['vr'] for r in sc['P2']['rand']),
        ', '.join('%.2f' % r['vr'] for r in sc['P2']['active'])))
    L_.append('| P3a PI >= 10x worse than RQMC at equal cost (S3) | all 13 | %s, %d of %d (min ratios %s) |' % (
        v(sc['P3a']['verdict']), sc['P3a']['holds'], sc['P3a']['of'],
        ', '.join('%.0f' % r['min_ratio'] for r in sc['P3a']['rows'])))
    L_.append('| P3b alpha(PI best) <= alpha(RQMC) + 0.15, n >= 128 | >= 5 of 7 | %s, %d of %d |' % (
        v(sc['P3b']['verdict']), sc['P3b']['holds'], sc['P3b']['of']))
    L_.append('| P3c PI_as steeper by > 0.1: n = 32 (>= 2 of 3), n = 64 (<= 1 of 3) | both | %s (n=32: %d, n=64: %d) |' % (
        v(sc['P3c']['verdict']), sc['P3c']['steeper32'], sc['P3c']['steeper64']))
    L_.append('| P4 small nets: alpha(PI_as) > alpha(RQMCRB) + 0.1 | >= 6 of 9 | %s, %d of %d |' % (
        v(sc['P4']['verdict']), sc['P4']['holds'], sc['P4']['of']))
    L_.append('| P5a 8 x 256: PIJ worse than RQMCJ at every common cost | >= 5 of 6 | %s, %d of %d |' % (
        v(sc['P5a']['verdict']), sc['P5a']['holds'], sc['P5a']['of']))
    L_.append('| P5b 8 x 256: abs(alpha(PIJ best) - alpha(RQMCJ)) < 0.3 | >= 4 of 6 | %s, %d of %d |' % (
        v(sc['P5b']['verdict']), sc['P5b']['holds'], sc['P5b']['of']))
    L_.append('| P6 RQMC N x nMSE >= NNGP-proxy bound | all 13 | %s, %d of %d (min measured/bound %s) |' % (
        v(sc['P6']['verdict']), sc['P6']['holds'], sc['P6']['of'],
        ', '.join('%.2f' % r['min_measured_over_bound'] for r in sc['P6']['rows'])))
    L_.append('| P7 RQMC local exponent (last 3 budgets) <= 1.3 | >= 10 of 13 | %s, %d of %d |' % (
        v(sc['P7']['verdict']), sc['P7']['holds'], sc['P7']['of']))
    L_.append('| P8 MLMC alpha in [0.8, 1.2] | all | %s, %d of %d |' % (v(sc['P8']['verdict']), sc['P8']['holds'], sc['P8']['of']))
    L_.append('')
    L_.append('Validity: bias-flag cells by method: %s; suspect methods: %s' % (
        {m: len(f) for m, f in sc['validity']['flags'].items()}, sc['validity']['suspect']))
    open(os.path.join(ROOT, 'results', 'scorecard.md'), 'w').write('\n'.join(L_) + '\n')
    print('\n'.join(L_))


if __name__ == '__main__':
    main()
