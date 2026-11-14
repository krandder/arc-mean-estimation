"""Placeholder values for notes/report_v2_summary.txt, computed from results/P1_scores.json. Imported by
build_report.py (fill(text) -> text)."""
import json
import math

import numpy as np

W = '/home/agent/workspaces/mats/work/bit-accounting'


def fill(text):
    S = json.load(open(f'{W}/results/P1_scores.json'))
    cells = S['cells']

    def v(kind, n, L, l, cls, D, field='R'):
        out = [cells[f'{kind}_{n}_{L}_{s}_{l}_{cls}'][field].get(str(D)) for s in (5000, 5001, 5002)
               if f'{kind}_{n}_{L}_{s}_{l}_{cls}' in cells]
        return out

    def m(x, nd=1):
        x2 = [q for q in x if q is not None]
        if not x:
            return 'pending'
        if not x2:
            return 'unreached'
        return f'{np.median(x2):.{nd}f}'

    def rng(x, nd=1):
        x2 = [q for q in x if q is not None]
        if not x2:
            return 'pending' if not x else 'unreached'
        return f'{min(x2):.{nd}f}' + (f'-{max(x2):.{nd}f}' if max(x2) - min(x2) >= 0.05 else '')

    def sl(kind, n, L, l, cls):
        a, b = v(kind, n, L, l, cls, 0.1), v(kind, n, L, l, cls, 0.01)
        s = [(y - x) / math.log2(10) for x, y in zip(a, b) if x is not None and y is not None]
        return f'{np.median(s):.1f}' if s else '-'

    d = {}
    u1 = [x for l in (0, 4, 8, 12, 15) for x in v('relu', 16, 16, l, 'unres', 0.1)]
    u2 = [x for l in (0, 4, 8, 12, 15) for x in v('relu', 16, 16, l, 'unres', 0.01)]
    d['U16_1'], d['U16_2'] = rng(u1), rng(u2)
    d['O16_1'], d['O16_2'] = rng(v('relu', 16, 16, 16, 'unres', 0.1)), rng(v('relu', 16, 16, 16, 'unres', 0.01))
    dev = {0.1: [], 0.01: []}
    for n, L in ((16, 4), (32, 8), (16, 16), (32, 32)):
        for sd in (5000, 5001, 5002):
            o = cells.get(f'relu_{n}_{L}_{sd}_{L}_unres')
            if o is None:
                continue
            for l in sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1])):
                c = cells.get(f'relu_{n}_{L}_{sd}_{l}_unres')
                for D in (0.1, 0.01):
                    if c is not None and c['R'].get(str(D)) is not None and o['R'].get(str(D)) is not None:
                        dev[D].append(abs(c['R'][str(D)] - o['R'][str(D)]))
    exc = []
    for n, L in ((16, 4), (32, 8), (16, 16), (32, 32)):
        for sd in (5000, 5001, 5002):
            o = cells.get(f'relu_{n}_{L}_{sd}_{L}_unres')
            if o is None:
                continue
            for l in sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1])):
                c = cells.get(f'relu_{n}_{L}_{sd}_{l}_unres')
                for D in (0.1, 0.01):
                    a, b = (c or {}).get('R', {}).get(str(D)), o['R'].get(str(D))
                    if a is not None and b is not None and abs(a - b) > max(0.5, 0.15 * b):
                        exc.append((f'{n}x{L} s{sd} l={l} at {int(D * 100)}%', a, b))
    exc.sort(key=lambda e: -(e[1] - e[2]))
    d['UEXC'] = (f'{len(exc)} exceptions; the largest: ' + '; '.join(f'{e[0]}: {e[1]:.1f} against {e[2]:.1f}' for e in exc[:4])
                 if exc else 'no exceptions')
    d['UDEV1'] = f'{np.median(dev[0.1]):.2f} (max {max(dev[0.1]):.2f})' if dev[0.1] else 'pending'
    d['UDEV2'] = f'{np.median(dev[0.01]):.2f} (max {max(dev[0.01]):.2f})' if dev[0.01] else 'pending'
    d['NUDEV'] = str(len(dev[0.1]))
    lines = []
    for n, L in ((16, 4), (32, 8), (16, 16), (32, 32)):
        ls = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))
        parts = [f'l = {l}: {m(v("relu", n, L, l, "local", 0.1))} / {m(v("relu", n, L, l, "local", 0.01))}' for l in ls]
        parts.append(f'output: {m(v("relu", n, L, L, "unres", 0.1))} / {m(v("relu", n, L, L, "unres", 0.01))}')
        lines.append(f'\n   - {n}x{L}: ' + '; '.join(parts))
    d['LOCAL_LINES'] = ''.join(lines)
    d['SL0_16'], d['SL0_32'] = sl('relu', 16, 16, 0, 'local'), sl('relu', 32, 32, 0, 'local')
    d['SLO'] = sl('relu', 16, 16, 16, 'unres') + ' (16x16), ' + sl('relu', 32, 32, 32, 'unres') + ' (32x32)'
    d['SL4'] = sl('relu', 16, 16, 4, 'local')
    d['LIN0'] = (f'single anchored model r0: 16x16 {m(v("relu", 16, 16, 0, "local", 0.1, "R_r0"))} / '
                 f'{m(v("relu", 16, 16, 0, "local", 0.01, "R_r0"))} bits against the linear reference '
                 f'{m(v("relu", 16, 16, 0, "local", 0.1, "R_linref"))} / {m(v("relu", 16, 16, 0, "local", 0.01, "R_linref"))}; '
                 f'32x32 {m(v("relu", 32, 32, 0, "local", 0.1, "R_r0"))} / {m(v("relu", 32, 32, 0, "local", 0.01, "R_r0"))} '
                 f'against {m(v("relu", 32, 32, 0, "local", 0.1, "R_linref"))} / {m(v("relu", 32, 32, 0, "local", 0.01, "R_linref"))}')
    d['LIN4'] = (f'16x16 at L/4: {m(v("relu", 16, 16, 4, "local", 0.1))} / {m(v("relu", 16, 16, 4, "local", 0.01))} against '
                 f'{m(v("relu", 16, 16, 4, "local", 0.1, "R_linref"))} / {m(v("relu", 16, 16, 4, "local", 0.01, "R_linref"))}')
    sc = S['scores']
    d['CERT2'] = (f'Coverage of these extra checks: {sc["coverage"]["certificates"]} cells ({{XCOV}}; the controls\' local '
                  'cells and all unrestricted cells were not reached within the GPU budget).')
    ctrl = []
    for kind in ('tanh4', 'feistel', 'linear'):
        a = [v(kind, 16, 16, l, 'local', 0.1) for l in (0, 4, 8, 12, 15)]
        o = v(kind, 16, 16, 16, 'unres', 0.1)
        if any(a) or o:
            ctrl.append(f'{kind}: local bits for 10% at l = 0, 4, 8, 12, 15: ' +
                        ', '.join(m(x) for x in a) + f'; output {m(o)}')
    d['CONTROLS'] = '; '.join(ctrl) if ctrl else 'pending (they run after the ReLU nets)'
    pct = lambda k: ('-' if sc.get(k, {}).get('frac') is None else  # noqa: E731
                     f'{round(sc[k]["frac"] * sc[k]["n"])}/{sc[k]["n"]}')
    d['C1'], d['C2'], d['C3'], d['C4'], d['C7'] = pct('C1'), pct('C2'), pct('C3'), pct('C4'), pct('C7')
    d['C6R0'], d['C6LONG'] = pct('C6_r0'), pct('C6_long')
    d['C3L_FAIL'] = ('-' if sc['C3_local']['frac'] is None else f'{100 * (1 - sc["C3_local"]["frac"]):.0f}%')
    d['NCOV'] = str(sc['C7']['not_covered'])
    spreads = []
    for k, c in cells.items():
        pass
    import glob as _g
    for f in _g.glob(f'{W}/runs/P1/P_*.json'):
        dd = json.load(open(f))
        cv = dd['groups']['G1']['curves']
        for D in (0.1, 0.01):
            rr = []
            for nm in ('r0', 'r1', 'r2'):
                pts = sorted(zip(cv[nm]['rate'], cv[nm]['nmse']))
                env, best = [], float('inf')
                for r, e in pts:
                    if e < best:
                        env.append((r, e)); best = e
                x = None
                for i, (r, e) in enumerate(env):
                    if e <= D:
                        x = r if i == 0 else env[i - 1][0] + (env[i - 1][1] - D) / (env[i - 1][1] - e) * (r - env[i - 1][0])
                        break
                rr.append(x)
            if all(q is not None for q in rr):
                spreads.append(max(rr) - min(rr))
    d['SPREAD'] = f'{np.median(spreads):.2f} (90th percentile {np.percentile(spreads, 90):.2f})' if spreads else '-'
    hit = lambda k: str(sc[k]['hit']).replace('True', 'all hit').replace('False', 'missed')  # noqa: E731
    d['KA1'] = f'{sc["KA1"]["n"]} points, ' + hit('KA1')
    d['KA2'] = pct('KA2 (empirical comparison)')
    d['KA3'] = f'{sc["KA3"]["n"]} points, ' + hit('KA3')
    d['TANH_LOCAL'] = ', '.join(m(v('tanh4', 16, 16, l, 'local', 0.1)) for l in (15, 12, 8, 4, 0))
    d['TANH_OUT'] = m(v('tanh4', 16, 16, 16, 'unres', 0.1))
    d['FEI'] = ('l = 12 and 15: ' + ', '.join(m(v('feistel', 16, 16, l, 'local', 0.1)) for l in (12, 15)) +
                f' bits for 10%; output {m(v("feistel", 16, 16, 16, "unres", 0.1))}')
    d['LIN'] = (f'{m(v("linear", 16, 16, 0, "local", 0.1))} / {m(v("linear", 16, 16, 0, "local", 0.01))} bits against '
                f'the Gaussian {cells.get("linear_16_16_5000_0_local", {}).get("RG", {}).get("0.1", float("nan")):.1f} / '
                f'{cells.get("linear_16_16_5000_0_local", {}).get("RG", {}).get("0.01", float("nan")):.1f}')
    # explorer (gates inside the data cloud) against the anchored local codes, by layer position
    import glob as _g2
    from collections import defaultdict as _dd
    gain = _dd(list)
    wd = []
    cen = []
    for f in _g2.glob(f'{W}/runs/P1X/X_*.json'):
        x = json.load(open(f))
        for q in x.get('centroid2', []):
            cen.append(q['nmse_model'] / max(q['nmse_corrected'], 1e-12))
        if x['cls'] != 'local' or 'explorer' not in x:
            continue
        dd = json.load(open(f'{W}/runs/P1/P_' + f.split('X_')[1]))
        L, l = dd['L'], dd['l']
        pos = 'input' if l == 0 else ('L/4' if l == L // 4 else ('L/2' if l == L // 2 else 'late'))
        for D in ('0.1', '0.01'):
            an = [dd['summary'][k]['cross'][D] for k in ('r0', 'r1', 'r2', 'long', 'r0_refit') if k in dd['summary']]
            an = [a for a in an if a is not None]
            ex = [x['summary'][k]['cross'][D] for k in ('x0', 'x1', 'x2') if k in x['summary']]
            ex = [e for e in ex if e is not None]
            if an and ex and dd['netkind'] == 'relu':
                gain[(pos, D)].append(1.0 - min(ex) / min(an))
            w = x['summary'].get('wdec', {}).get('cross', {}).get(D)
            if w is not None and dd['summary']['r0']['cross'][D] is not None:
                wd.append(w - dd['summary']['r0']['cross'][D])
    parts = []
    for pos in ('input', 'L/4', 'L/2', 'late'):
        g1, g2 = gain.get((pos, '0.1'), []), gain.get((pos, '0.01'), [])
        if g1 or g2:
            parts.append(f'{pos} {100 * np.median(g1):.0f}% / {100 * np.median(g2):.0f}% (n = {len(g1)})' if g1 and g2 else f'{pos} n/a')
    d['EXPL'] = '; '.join(parts) if parts else 'pending'
    d['WDEC'] = (f'median {np.median(wd):+.2f} bit, range {min(wd):+.2f} to {max(wd):+.2f} ({len(wd)} points)' if wd else 'pending')
    d['CEN2'] = (f'the model is within {100 * (np.median(cen) - 1):.1f}% of the corrected output (median; worst '
                 f'{100 * (max(cen) - 1):.0f}%, {len(cen)} points)' if cen else 'pending')
    # ---- review r2c: primary crossings for post-pass comparisons, extrema, gaps, coverage
    def ts(rates, nmse, D):
        pts = sorted((r, e) for r, e in zip(rates, nmse) if r is not None and e is not None and np.isfinite(r) and np.isfinite(e))
        env, best = [], float('inf')
        for r, e in pts:
            if e < best:
                env.append((max(r, 0.0), e))
                best = e
        for i, (r, e) in enumerate(env):
            if e <= D:
                if i == 0:
                    return r
                r0, e0 = env[i - 1]
                return r0 + (e0 - D) / (e0 - e) * (r - r0)
        return None
    gain2, wd2, gaps = _dd(list), [], _dd(list)
    nomark = 0
    for f in _g2.glob(f'{W}/runs/P1X/X_*.json'):
        x = json.load(open(f))
        if 'explorer_init_data' not in x:
            nomark += 1
        if x['cls'] != 'local' or 'explorer' not in x:
            continue
        dd = json.load(open(f'{W}/runs/P1/P_' + f.split('X_')[1]))
        if dd['netkind'] != 'relu':
            continue
        L, l = dd['L'], dd['l']
        pos = 'input' if l == 0 else ('L/4' if l == L // 4 else ('L/2' if l == L // 2 else 'late'))
        cv = {}
        for g in dd['groups'].values():
            cv.update(g['curves'])
        if 'refit' in dd:
            cv['r0_refit'] = dict(rate=[min(q['rate_trained_B'], q['rate_refit_mix8'], q['rate_refit_fullgauss'])
                                        for q in dd['refit']], nmse=cv['r0']['nmse'])
        for D in (0.1, 0.01):
            an = [ts(cv[k]['rate'], cv[k]['nmse'], D) for k in ('r0', 'r1', 'r2', 'long', 'r0_refit') if k in cv]
            an = [a for a in an if a is not None]
            ex = [ts(c['rate'], c['nmse'], D) for c in x['explorer'].values()]
            ex = [e for e in ex if e is not None]
            if an and ex:
                gain2[(pos, D)].append(1.0 - min(ex) / min(an))
            w, b = ts(x['wdec']['rate'], x['wdec']['nmse'], D), ts(cv['r0']['rate'], cv['r0']['nmse'], D)
            if w is not None and b is not None:
                wd2.append(w - b)
    parts = []
    for pos in ('input', 'L/4', 'L/2', 'late'):
        g1, g2 = gain2.get((pos, 0.1), []), gain2.get((pos, 0.01), [])
        if g1 and g2:
            parts.append(f'{pos} {100 * np.median(g1):.0f}% / {100 * np.median(g2):.0f}% (n = {len(g1)})')
    d['EXPL'] = '; '.join(parts) if parts else 'pending'
    d['WDEC'] = (f'median {np.median(wd2):+.2f} bit, range {min(wd2):+.2f} to {max(wd2):+.2f} ({len(wd2)} points)'
                 if wd2 else 'pending')
    d['NOMARK'] = str(nomark)
    for k, c in cells.items():
        kind, n, L, sd, l, cls = k.split('_')
        if kind == 'relu' and cls == 'local':
            L, l = int(L), int(l)
            pos = 'input' if l == 0 else ('L/4' if l == L // 4 else ('L/2' if l == L // 2 else 'late'))
            for D in ('0.1', '0.01'):
                a, b = c['R_r0'].get(D), c['R'].get(D)
                if a is not None and b is not None:
                    gaps[pos].append(a - b)
    d['R0GAP'] = '; '.join(f'{pos} {np.median(gaps[pos]):.1f}' for pos in ('input', 'L/4', 'L/2', 'late') if gaps[pos])
    red = []
    import glob as _g3
    for f in _g3.glob(f'{W}/runs/P1/P_*.json'):
        for q in json.load(open(f)).get('refit', []):
            if q['rate_trained_B'] > 1.0:
                red.append(1.0 - min(q['rate_refit_mix8'], q['rate_refit_fullgauss']) / q['rate_trained_B'])
    d['C4MAX'] = f'{100 * max(red):.0f}%' if red else '-'
    exc7 = []
    for c in cells.values():
        for D in ('0.3', '0.1', '0.03', '0.01', '0.003', '0.001'):
            a, b = c['R'].get(D), c['R_linref'].get(D)
            if a is not None and b is not None and a > b + 1e-9:
                exc7.append(a - b)
    d['C7EXC'] = (f'{len(exc7)} points exceed it within that tolerance (by up to {max(exc7):.1f} bits)' if exc7 else
                  'none exceeds it')
    lg = [abs(c['R'][D] - c['RG'][D]) for k, c in cells.items() if k.startswith('linear_') for D in ('0.1', '0.03', '0.01')
          if c['R'].get(D) is not None]
    d['LINMAX'] = f'{max(lg):.2f}' if lg else '-'
    man_local = 0
    done_local = 0
    xs = {f.split('X_')[1][:-5] for f in _g2.glob(f'{W}/runs/P1X/X_*.json')}
    for k in cells:
        kind, n, L, sd, l, cls = k.split('_')
        if kind == 'relu' and cls == 'local':
            man_local += 1
            done_local += f'relu_n{n}_L{L}_s{sd}_l{l}_local' in xs
    d['XCOV'] = f'{done_local} of the {man_local} ReLU local cells'
    for k, val in d.items():
        text = text.replace('{' + k + '}', val)
    return text
