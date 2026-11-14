"""Markdown tables for the report from the registered runs. Prints to stdout and writes results/tables.md."""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/lib')
import ndx  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/nd-exact/'
sys.path.insert(0, BASE + 'scratch')
from score import interp  # noqa: E402

L = []


def p(s=''):
    L.append(s)


def load(name):
    f = BASE + 'runs/' + name
    return json.load(open(f)) if os.path.exists(f) else None


def fmt(x):
    return '-' if x is None else ('%.1e' % x)


def main():
    seeds = ndx.EVAL_SEEDS
    # 1. equal-cost table
    p('## nMSE at equal cost (mv); CS2 and CS2b are deterministic, the rest are means over replicates')
    p('| net | method | 2^16 | 2^18 | 2^20 | 2^22 | 2^24 | 2^26 |')
    p('|---|---|---|---|---|---|---|---|')
    budgets = [2 ** k for k in (16, 18, 20, 22, 24, 26)]
    for s in seeds:
        b = load(f'baselines_s{s}.json')
        cs = load(f'cs2_s{s}.json')
        csb = load(f'cs2b_s{s}.json')
        rc = load(f'region_code_s{s}.json')
        rows = []
        if b:
            for k in ('MC', 'RQMC', 'RQMCJ', 'RADQ'):
                cur = [(v[k]['cost_mv'], v[k]['nmse']) for v in b['res'].values() if k in v]
                rows.append((k, [interp(cur, c) if k != 'MC' else 257.0 / c for c in budgets]))
        csc = load(f'posthoc_cs2c_s{s}.json')
        for name, d in (('CS2', cs), ('CS2b', csb), ('CS2c (post hoc, stuck face fixed)', csc)):
            if d:
                cur = [(q['cost_mv'], q['nmse']) for q in d['points']]
                rows.append((name, [interp(cur, c) for c in budgets]))
        if rc:
            cur = [(q['cost_mv'], q['nmse_ho']) for q in rc['curves']['32']['curve'] if q['nmse_ho'] > 0]
            rows.append(('region code (held-out, 9 mv/region)', [interp(cur, c) for c in budgets]))
        for k, vals in rows:
            p(f'| {s} | {k} | ' + ' | '.join(fmt(v) for v in vals) + ' |')
    p()
    # 2. slopes: descriptive refit over the nominal checkpoints 2^18..2^24 for every method (the frozen scorer's
    #    window drops CS2's 2^24 checkpoint, whose cost lands just above 2^24)
    p('## Slopes over the nominal checkpoints 2^18-2^24 mv (nMSE ~ cost^-s) and bits per halving of the error (2/s)')
    p('| net | MC | RQMC | RQMCJ | RADQ | CS2 | CS2b | CS2c (post hoc) |')
    p('|---|---|---|---|---|---|---|---|')
    for s in seeds:
        b = load(f'baselines_s{s}.json')
        cells = ['2.00']
        for k in ('RQMC', 'RQMCJ', 'RADQ'):
            pts = [(int(B), v[k]['nmse']) for B, v in b['res'].items() if k in v and 2 ** 18 <= int(B) <= 2 ** 24]
            sl = -np.polyfit(np.log2([c for c, _ in pts]), np.log2([e for _, e in pts]), 1)[0]
            cells.append('%.2f' % (2 / sl))
        for name in ('cs2', 'cs2b', 'posthoc_cs2c'):
            d = load(f'{name}_s{s}.json')
            if not d:
                cells.append('-')
                continue
            sel = [(math.floor(math.log2(q['cost_mv'])), q['nmse']) for q in d['points']
                   if 18 <= math.floor(math.log2(q['cost_mv'])) <= 24]
            sl = -np.polyfit([k for k, _ in sel], np.log2([e for _, e in sel]), 1)[0]
            cells.append('%.2f' % (2 / sl) if sl > 0 else 'inf')
        p(f'| {s} | ' + ' | '.join(cells) + ' |')
    p()
    # 3. CS2 classes
    p('## CS2: constructed nodes / open leaves (the classes) / certified probability mass / nMSE at its checkpoints')
    p('| net | 2^20 mv | 2^23 mv | 2^26 mv |')
    p('|---|---|---|---|')
    for s in seeds:
        d = load(f'cs2_s{s}.json')
        if not d:
            continue
        cells = []
        for k in (20, 23, 26):
            q = [x for x in d['points'] if abs(math.log2(x['cost_mv']) - k) < 0.5]
            if q:
                q = q[0]
                cells.append('%d / %d / %.1e / %.1e' % (q['n_cells'], q['n_open'], q['P_cert'], q['nmse']))
            else:
                cells.append('-')
        p(f'| {s} | ' + ' | '.join(cells) + ' |')
    p()
    # 4. region code
    p('## Region codes with free exact integration (layers 1..32): nMSE of the dropped part (held-out / in-sample)')
    p('| net | regions seen in A (2^22) | B inputs in regions unseen in A | R = 2^10 | 2^14 | 2^16 | 2^17 | all seen |')
    p('|---|---|---|---|---|---|---|---|')
    for s in seeds:
        rc = load(f'region_code_s{s}.json')
        if not rc:
            continue
        c = rc['curves']['32']
        byR = {q['R']: q for q in c['curve']}
        G = c['regions_seen_A']
        cells = []
        for R in (1024, 16384, 65536, 131072, G):
            q = byR.get(R)
            cells.append('-' if q is None else '%.1e / %.1e' % (q['nmse_ho'], q['nmse_in']))
        p(f'| {s} | {G} | %.4f | ' % c['unseen_prob_B'] + ' | '.join(cells) + ' |')
    p()
    # 5. unbiased
    p('## Unbiased version (Amendment 1): D = CS2 at 2^20 mv plus a sampled correction')
    p('| net | D alone | Var(f - q)/Var(f) | RQMC correction M = 2^12 / 2^14 / 2^16: nMSE (cost) | RQMCJ at the same costs |')
    p('|---|---|---|---|---|')
    for s in seeds:
        u = load(f'unbiased_s{s}.json')
        b = load(f'baselines_s{s}.json')
        if not u or not b:
            continue
        curJ = [(v['RQMCJ']['cost_mv'], v['RQMCJ']['nmse']) for v in b['res'].values() if 'RQMCJ' in v]
        vr = [v['var_ratio'] for k, v in u['res'].items() if k.startswith('MC_') and v['var_ratio'] is not None]
        cells, cj = [], []
        for lm in (12, 14, 16):
            v = u['res'].get(f'RQMC_M{lm}')
            if v:
                cells.append('%.1e (%.1e)' % (v['nmse'], v['cost_mv']))
                cj.append(fmt(interp(curJ, v['cost_mv'])))
        p(f'| {s} | %.1e | %.2f | ' % (u['nmse_D'], np.mean(vr)) + ' / '.join(cells) + ' | ' + ' / '.join(cj) + ' |')
    p()
    # 6. depth-1 width study
    for name in ('depth1_rate4.json', 'depth1_rate3.json', 'depth1_rate2.json'):
        d = load(name)
        if not d:
            continue
        p(f'## One ReLU layer by width ({name}): nMSE at equal cost, deterministic code vs RQMC')
        p('| width n | seed | code: cells, cost (mv), nMSE, certified mass | RQMC at the same cost | code bits per halving (last 4 doublings of cells) |')
        p('|---|---|---|---|---|')
        for e in d:
            cs = e['cs']
            last = cs[-1]
            rq = [(q['cost_mv'], q['nmse']) for q in e['rqmc']]
            r = interp(rq, last['cost_mv'])
            sel = cs[-5:]
            if len(sel) >= 3 and all(q['nmse'] > 0 for q in sel):
                sl = -np.polyfit(np.log2([q['cost_mv'] for q in sel]), np.log2([q['nmse'] for q in sel]), 1)[0]
                bits = '%.2f' % (2 / sl) if sl > 0 else 'inf'
            else:
                bits = '-'
            p('| %d | %d | %d, %.1e, %.1e, %.3f | %s | %s |' % (e['n'], e['seed'], last['cells'], last['cost_mv'],
                                                             last['nmse'], last['P_cert'], fmt(r), bits))
        p()
        break
    # 7. preimages
    p('## Downstream classes and their preimages (2^20 inputs): classes covering 99% of the output mass at cut k,'
      ' and the number of distinct activation regions of layers 1..k inside the largest ones')
    p('| net | k = 4 | k = 8 | k = 16 | k = 24 |')
    p('|---|---|---|---|---|')
    for s in seeds:
        d = load(f'preimage_s{s}.json')
        if not d:
            continue
        cells = []
        for k in ('4', '8', '16', '24'):
            c = d['cuts'][k]
            cells.append('%d classes; %s' % (c['classes_99'], ', '.join(str(v) for v in c['regions_in_top_classes'][:3])))
        p(f'| {s} | ' + ' | '.join(cells) + ' |')
    open(BASE + 'results/tables.md', 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
