"""Assemble preint.md from notes/preint_template.md, the generated tables (results/tables.md 4.1-4.3,
results/degree_table.md, results/scorecard.md) and numbers computed from results/scores.json and
results/posthoc_matched.json. Manual strings (status, review, compute) come from notes/report_meta.json."""
import json
import os

import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


def section(text, start, end=None):
    a = text.index(start)
    b = text.index(end, a + len(start)) if end else len(text)
    return '\n'.join(l for l in text[a:b].split('\n') if not l.startswith('###')).strip()


def rng_str(vals, fmt='%.2f', sep='-'):
    vals = [v for v in vals if v is not None and np.isfinite(v)]
    if not vals:
        return 'n/a'
    lo, hi = min(vals), max(vals)
    return (fmt % lo) if fmt % lo == fmt % hi else (fmt % lo) + sep + (fmt % hi)


def verdict(t, count=True):
    v = t['verdict']
    if v == 'pending':
        return 'is pending'
    if count and 'holds' in t:
        return ('holds (%d of %d)' if v else 'fails (%d of %d)') % (t['holds'], t['of'])
    return 'holds' if v else 'fails'


def interp_min(pi_rows, ref_rows):
    c = np.array([r['cost'] for r in pi_rows])
    y = np.array([r['nmse_rep'] for r in pi_rows])
    vals = []
    for r in ref_rows:
        if c.min() <= r['cost'] <= c.max():
            vals.append(float(np.exp(np.interp(np.log(r['cost']), np.log(c), np.log(y)))) / r['nmse_rep'])
    return min(vals) if vals else float('nan')


def main():
    t = open(os.path.join(ROOT, 'results', 'tables.md')).read()
    sc = json.load(open(os.path.join(ROOT, 'results', 'scores.json')))
    pm = json.load(open(os.path.join(ROOT, 'results', 'posthoc_matched.json')))
    meta = json.load(open(os.path.join(ROOT, 'notes', 'report_meta.json')))
    p3a = sc['P3a']['rows']
    r256 = [r['min_ratio'] for r in p3a if r['net'][1] == 256]
    eq256 = [r['equiv_points_per_line_median'] for r in pm if '_n256_' in r['file']]
    m256_pi = [r['slope_pi'] for r in pm if '_n256_' in r['file'] and r['method'] == 'PI_as_w']
    m256_ref = [r['slope_ref'] for r in pm if '_n256_' in r['file'] and r['method'] == 'PI_as_w']
    p7 = [r for r in sc['P7']['rows'] if r['net'][1] == 256]
    plateau256 = [x for r in p7 for x in r['N_nmse_last']]
    p3b_not = sum(1 for r in sc['P3b']['rows'] if not r['ok'])
    p6_fail = [r for r in sc['P6']['rows'] if not r['ok']]
    p2r = [r['vr'] for r in sc['P2']['rand']]
    p2a = [r['vr'] for r in sc['P2']['active']]
    p2c = [r['vr_corrected'] - r['vr'] for r in sc['P2']['rand'] + sc['P2']['active']]
    v = sc['validity']
    nflags = sum(len(x) for x in v['flags'].values())
    ncells = sum(v['cells'].values())
    p7v = sc['P7']['verdict']
    # post-hoc larger-N follow-up at 128 x 16 (PI_as_w 2^9..2^10 lines appended to the scored 2^2..2^8)
    import sys as _s
    _s.path.insert(0, os.path.join(ROOT, 'frozen'))
    import fit as _FT
    fu = []
    for sd in (302, 304):
        fp = os.path.join(ROOT, 'runs', 'posthoc_largeN_n128_L16_s%d.json' % sd)
        sp = os.path.join(ROOT, 'runs', 's3_arc_n128_L16_s%d.json' % sd)
        if not os.path.exists(fp):
            continue
        extra = json.load(open(fp))['methods'].get('PI_as_w', [])
        base = json.load(open(sp))['methods']
        rows = base['PI_as_w'] + [r for r in extra if r['p'] > base['PI_as_w'][-1]['p']]
        if len(rows) <= len(base['PI_as_w']):
            continue
        a_ext = _FT.fit_curve(rows, 0.6)['alpha']
        a_reg = _FT.fit_curve(base['PI_as_w'], 0.6)['alpha']
        a_rq = _FT.fit_curve(base['RQMC'], 0.6)['alpha']
        ratio = interp_min(rows, base['RQMC'])
        fu.append('net %d: PI_as_w exponent %.2f over 2^2..2^%d lines (registered window: %.2f), RQMC %.2f.'
                  % (sd, a_ext, rows[-1]['p'], a_reg, a_rq))
    followup = (' '.join(fu)) if fu else 'not finished at assembly time.'
    rep = {
        'FOLLOWUP': followup,
        '{T41}': section(t, '### 4.1', '### 4.2'),
        '{T42}': section(t, '### 4.2', '### 4.3'),
        '{T43}': section(t, '### 4.3'),
        '{DEG}': open(os.path.join(ROOT, 'results', 'degree_table.md')).read().strip(),
        '{SCORE}': open(os.path.join(ROOT, 'results', 'scorecard.md')).read().strip(),
        'EQCOST_MAX': '{:,.0f}'.format(max(r['min_ratio'] for r in p3a if np.isfinite(r['min_ratio']))),
        'EQCOST_256': rng_str(r256, '%.0f') + 'x',
        'LINE_256': rng_str(eq256),
        'MATCHED_256': 'PI_as %s vs RQMC-RB %s' % (rng_str(m256_pi), rng_str(m256_ref)),
        'PLATEAU_256': rng_str(plateau256),
        'PLATEAU_P7': verdict(sc['P7']),
        'P3B_COUNT': '%d of %d' % (p3b_not, len(sc['P3b']['rows'])),
        'P6_FAIL': ('%d of %d nets (%s)' % (len(p6_fail), len(sc['P6']['rows']),
                                            ', '.join('%dx%d s%d' % (r['net'][1], r['net'][2], r['net'][3]) for r in p6_fail))
                    if p6_fail else 'no net'),
        'P2_RANGE': '%s with a random u and %s with the active-subspace u' % (rng_str(p2r), rng_str(p2a)),
        'P2_CORR': '%.3f' % max(p2c),
        'BIAS_FLAGS': '%d of %d' % (nflags, ncells),
        'P1_V': verdict(sc['P1']), 'P2_V': verdict(sc['P2'], count=False),
        'P3B_V': verdict(sc['P3b']), 'P3C_V': verdict(sc['P3c'], count=False),
        'P1_RANGE': rng_str([r['ratio'] for r in sc['P1']['rows']]),
        'STATUS_LINE': meta['status'],
        'REVIEW_LINE': meta['review'],
        'COMPUTE_HOURS': meta['compute_hours'],
    }
    s = open(os.path.join(ROOT, 'notes', 'preint_template.md')).read()
    for k, val in rep.items():
        s = s.replace(k, val)
    open(os.path.join(ROOT, 'preint.md'), 'w').write(s)
    left = [k for k in rep if k in s]
    print('preint.md assembled, %d lines; unresolved markers: %s' % (s.count('\n'), left))
    for k in ('EQCOST_MAX', 'EQCOST_256', 'LINE_256', 'MATCHED_256', 'PLATEAU_256', 'PLATEAU_P7', 'P3B_COUNT', 'P6_FAIL',
              'P2_RANGE', 'P2_CORR', 'BIAS_FLAGS'):
        print('  %s = %s' % (k, rep[k]))


if __name__ == '__main__':
    main()
