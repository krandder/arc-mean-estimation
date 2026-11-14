"""Consistency flags (main/Kelvin, 12:00Z; PREREG A18): in a noiseless net h_{l+1} = f(h_l), so (PROVEN, data processing)
every layer's count of any class is >= R_a(D), the output's rate-distortion function; for the unrestricted class
R_l <= R_{l'} for l < l' (a code of h_{l'} is a code of h_l), hence all unrestricted R_l equal R_a. Measured counts
that break these orders flag undertraining:
  (1) output cell: its count above the lower envelope of all codes of the net (any layer, class, run) by > 3%;
  (2) unrestricted monotonicity: R_l > R_{l'} by > 3% for some measured l < l';
  (3) unrestricted vs the envelope: R_l above the envelope by > 3% (the C1 shortfall; at early layers it is the
      decoder's failure to invert the remaining layers).
Counts: base runs (mean of restarts), every variant run as well for the envelope. Writes a markdown table.
usage: consistency.py <runs base> <out md>
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import vrb  # noqa: E402

BASE, OUT = sys.argv[1], sys.argv[2]
runs, refs, idx = vrb.load(BASE)
EPS = (0.1, 0.01, 0.001)
TOL = 0.03


def bits(rs, e):
    v = [vrb.R_lin(r['pc'], e) for r in rs]
    if not v or any(x is None for x in v):
        return None
    return sum(v) / len(v)


def f(x):
    return '-' if x is None else ('%.0f' % x if x >= 20 else '%.1f' % x)


L = ['| family | net | nMSE | envelope (all codes) | given by | output cell | output cell above envelope | unrestricted R_l by layer | '
     'monotonicity violations (consecutive measured layers) | unrestricted above envelope |', '|' + '---|' * 10]
nflags = 0
for fam in ('arc', 'nd'):
    lo = vrb.LOUT[fam]
    for s in vrb.SEEDS[fam]:
        cells = {k: v for k, v in idx.items() if k[0] == fam and k[1] == s and not k[4].startswith('fixlam')}
        for e in EPS:
            env, who = None, None
            for (fam_, s_, l_, c_, v_), rs in cells.items():
                rr = [r for r in rs if v_ != 'base' or r.get('restart') in (0, 1)] or rs
                x = bits(rr, e)
                if x is not None and (env is None or x < env):
                    env, who = x, f'l{l_ if l_ < lo else "out"} {c_} {v_}'
            out = bits(vrb.base_runs(idx, fam, s, lo, 'out'), e)
            o_flag = ''
            if out is not None and env is not None and out > env * (1 + TOL) and out - env > 0.5:
                o_flag = f'+{100 * (out - env) / env:.0f}%'
                nflags += 1
            un = {}
            for l in vrb.LAYERS[fam]:
                x = bits(vrb.base_runs(idx, fam, s, l, 'unres'), e)
                if vrb.base_runs(idx, fam, s, l, 'unres'):
                    un[l] = x if x is not None else math.inf
            mono = []
            ls = sorted(un)
            for a, b in zip(ls, ls[1:]):   # consecutive measured layers
                if un[a] > un[b] * (1 + TOL) and un[a] - un[b] > 0.5:
                    mono.append(f'l{a} > l{b}' + (f' by {100 * (un[a] - un[b]) / un[b]:.0f}%' if math.isfinite(un[a])
                                                     and math.isfinite(un[b]) else ' (not reached)'))
            over = [f'l{l} +{100 * (x - env) / env:.0f}%' if math.isfinite(x) else f'l{l} not reached'
                    for l, x in sorted(un.items()) if env is not None and x > env * (1 + TOL) and x - env > 0.5]
            nflags += len(mono) + len(over)
            if not (o_flag or mono or over or un):
                continue
            ustr = ', '.join(f'l{l} {f(x) if math.isfinite(x) else "not reached"}' for l, x in sorted(un.items()))
            L.append(f'| {fam} | {s} | {e} | {f(env)} | {who} | {f(out)} | {o_flag or "-"} | {ustr or "-"} | '
                     f'{"; ".join(mono) or "-"} | {", ".join(over) or "-"} |')
L.append(f'\n{nflags} flags (each = undertraining, a decoder limit or a structural limit of the flagged cell; tolerance '
         f'{int(TOL * 100)}% and 0.5 bit, as in C3).')
open(OUT, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
