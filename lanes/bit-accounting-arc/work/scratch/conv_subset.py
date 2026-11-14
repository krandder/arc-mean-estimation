"""Convergence subset (PREREG A18): ARC net 4000, layers 0, 16, 31, local and unrestricted, at nMSE 0.1 and 0.01.
For each (cell, accuracy): every run of the cell with its bits (variable-rate curves at eps; a dedicated fixed-lambda
model counts as a point with its own nMSE <= eps), the count (lowest), the run that gives it, the current upper bound
(the registered count: base, and for local cells the better of the two starts), and the convergence verdict:
converged when the last doubling of steps, of depth and (unrestricted) of width along the best run's family each
change the count by < 3%, and (local) no other start is lower by >= 3%.
usage: conv_subset.py <runs base> <out md>
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import vrb  # noqa: E402

BASE, OUT = sys.argv[1], sys.argv[2]
TOL = 0.03
JS = []
runs, refs, idx = vrb.load(BASE)
SEED = 4000
# variant -> (start, depth, width, steps); the base and restart 2 are the reference start (local) / output PCA (unres)
SPEC = {'base': ('informed', 3, 1, 12), 'r2': ('informed', 3, 1, 12), 'steps2': ('informed', 3, 1, 24),
        'steps4': ('informed', 3, 1, 48), 'cap2': ('informed', 6, 1, 12), 'cap2steps4': ('informed', 6, 1, 48),
        'cap2steps8': ('informed', 6, 1, 96), 'cap4steps4': ('informed', 12, 1, 48),
        'wide2steps2': ('informed', 3, 2, 24), 'h1': ('look-ahead', 3, 1, 12), 'h1s2': ('look-ahead', 3, 1, 24),
        'h1s4': ('look-ahead', 3, 1, 48), 'h1c2': ('look-ahead', 6, 1, 12), 'h1lr': ('look-ahead lr 3e-4', 3, 1, 12),
        'reflr': ('informed lr 3e-4', 3, 1, 12), 'rndhi': ('random lr 1e-3', 3, 1, 12),
        'rndmid': ('random lr 3e-4', 3, 1, 12), 'bwd': ('backward', 3, 1, 12), 'bwds2': ('backward', 3, 1, 24),
        'steps8': ('informed', 3, 1, 96), 'h1s8': ('look-ahead', 3, 1, 96), 'cap2steps2': ('informed', 6, 1, 24),
        'h1c2s4': ('look-ahead', 6, 1, 48), 'h1c2s2': ('look-ahead', 6, 1, 24), 'wide2steps4': ('informed', 3, 2, 48),
        'h1c2s8': ('look-ahead', 6, 1, 96), 'bwd1': ('backward one-step', 3, 1, 12)}
MAIN = ('informed', 'look-ahead', 'backward')     # start families with doubling runs
DEDICATED = ('fixlam', 'fixlamlo', 'fixlamh1')


def bits(rs, e):
    v = [vrb.R_lin(r['pc'], e) for r in rs]
    v = [x for x in v if x is not None]
    return (sum(v) / len(v)) if (v and len(v) == len(rs)) else None


def f(x):
    return '-' if x is None else ('%.0f' % x if x >= 20 else '%.1f' % x)


L = ['| layer | class | nMSE | current count (registered) | lowest found | run giving it | doublings of the best main start '
     '(informed, look-ahead, backward) | best other start | verdict |', '|' + '---|' * 9]
detail = ['', '### All runs (bits at nMSE 0.1 / 0.01)', '', '| layer | class | run | start | depth | width | steps (k) | '
          '0.1 | 0.01 |', '|' + '---|' * 9]
for l in (0, 16, 31):
    for cls in ('local', 'unres'):
        allr = {}
        for v in SPEC:
            if v == 'base':
                rs = vrb.base_runs(idx, 'arc', SEED, l, cls)
            elif v == 'r2':
                rs = [r for r in idx.get(('arc', SEED, l, cls, 'base'), []) if r.get('restart') == 2]
            else:
                rs = idx.get(('arc', SEED, l, cls, v), [])
            if rs:
                allr[v] = rs
        for v, rs in allr.items():
            st, d, w, k = SPEC[v]
            detail.append(f'| {l} | {cls} | {v} | {st} | {d} | {w}x | {k} | {f(bits(rs, 0.1))} | {f(bits(rs, 0.01))} |')
        for e in (0.1, 0.01):
            vals = {v: bits(rs, e) for v, rs in allr.items()}
            for dv in DEDICATED:
                for r in idx.get(('arc', SEED, l, cls, dv), []):
                    pt = min(r['pc'], key=lambda c: abs(c['t'] - r['fixed_t']))
                    if pt['nmse'] <= e:
                        vals[f'{dv} t={r["fixed_t"]:g}'] = pt['rate']
            vals = {k_: x for k_, x in vals.items() if x is not None}
            cur = vals.get('base')
            if cls == 'local' and vals.get('h1') is not None:
                cur = min(x for x in (cur, vals['h1']) if x is not None)
            if not vals:
                L.append(f'| {l} | {cls} | {e} | {f(cur)} | not reached by any run | | | | not reached |')
                JS.append(dict(layer=l, cls=cls, eps=e, registered=None, lowest=None, run=None, doublings='',
                               verdict='not reached'))
                continue
            best = min(vals, key=vals.get)
            b = vals[best]
            anchors = [v for v in vals if v in SPEC and SPEC[v][0] in MAIN]
            anchor = min(anchors, key=vals.get) if anchors else best
            spec = SPEC.get(anchor)
            bad = []
            if vals[anchor] > b * (1 + TOL):
                bad.append(f'search: {best} is {100 * (vals[anchor] - b) / vals[anchor]:.0f}% below the best main start')
            if spec:
                # A20: the doubling partners of the best main run must match it in every other setting; the change
                # must be < 3% in absolute value; a missing partner leaves that axis unverified
                dbl = []
                for name, ix in (('steps', 3), ('depth', 1), ('width', 2)):
                    if name == 'width' and cls != 'unres':
                        continue
                    part = None
                    for fac, lbl in ((0.5, 'down'), (2, 'up')):
                        want = list(spec)
                        want[ix] = spec[ix] * fac
                        cand = [v for v in vals if v in SPEC and v != anchor and tuple(SPEC[v]) == tuple(want)
                                and not (v == 'r2' and 'base' in vals)]
                        if cand:
                            part = (cand[0], lbl)
                            break
                    if part is None:
                        dbl.append(f'{name} unverified')
                        continue
                    v2, lbl = part
                    if lbl == 'down':
                        ch = (vals[anchor] - vals[v2]) / vals[v2]
                        dbl.append(f'{name} {100 * ch:+.0f}% ({v2} -> {anchor})')
                    else:
                        ch = (vals[v2] - vals[anchor]) / vals[anchor]
                        dbl.append(f'{name} {100 * ch:+.0f}% ({anchor} -> {v2})')
                    if abs(ch) >= TOL:
                        bad.append(f'{name} {100 * ch:+.0f}% per doubling')
                dstr = '; '.join(dbl)
            else:
                dstr = 'dedicated point'
            other = []
            if cls == 'local':
                bst = spec[0] if spec else 'dedicated'
                for v, x in vals.items():
                    s2 = SPEC.get(v)
                    if s2 and s2[0] != bst:
                        other.append((x, v))
                other.sort()
            ostr = (f'{other[0][1]} {f(other[0][0])} ({100 * (other[0][0] - b) / b:+.0f}%)' if other else '-')
            missing_axes = [a for a in ('steps', 'depth', 'width') if f'{a} unverified' in dstr]
            verdict = ('not converged: ' + ', '.join(bad)) if bad else (
                'converged' if not missing_axes else 'unverified: no matched ' + ', '.join(missing_axes) + ' partner')
            L.append(f'| {l} | {cls} | {e} | {f(cur)} | {f(b)} | {best} | {dstr} | {ostr} | {verdict} |')
            JS.append(dict(layer=l, cls=cls, eps=e, registered=cur, lowest=b, run=best, doublings=dstr, verdict=verdict))
open(OUT, 'w').write('\n'.join(L + detail) + '\n')
import json  # noqa: E402
json.dump(JS, open(os.path.splitext(OUT)[0] + '.json', 'w'), indent=1)
print('\n'.join(L + detail))

# the backward chain (A19) against the other local starts, every layer of net 4000 it reached
B = ['', '### The backward curriculum (A19) against the other local starts, ARC net 4000 (bits; change against the better '
     'of the reference and look-ahead starts)', '',
     '| layer | eps | backward start | reference start | look-ahead start | change |', '|---|---|---|---|---|---|']
for l in (28, 24, 20, 16, 12, 8, 4, 2, 0):
    bw = idx.get(('arc', SEED, l, 'local', 'bwd'), [])
    if not bw:
        continue
    for e in (0.1, 0.01, 0.001):
        xb = bits(bw, e)
        xr = bits(vrb.base_runs(idx, 'arc', SEED, l, 'local'), e)
        xh = bits(idx.get(('arc', SEED, l, 'local', 'h1'), []), e)
        ref = [x for x in (xr, xh) if x is not None]
        ch = f'{100 * (xb - min(ref)) / min(ref):+.0f}%' if (xb is not None and ref) else '-'
        B.append(f'| {l} | {e} | {f(xb)} | {f(xr)} | {f(xh)} | {ch} |')
open(OUT, 'a').write('\n'.join(B) + '\n')
print('\n'.join(B))
