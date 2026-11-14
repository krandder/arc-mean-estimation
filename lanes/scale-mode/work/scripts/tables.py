"""Format results/score.json (the hashed scorer's output) into markdown tables. Formatting only: every number comes from
score.json. usage: tables.py SCORE_JSON OUT_MD"""
import json, math, sys
import numpy as np

d = json.load(open(sys.argv[1]))
out = []
P = out.append


def f(x, fmt='{:.2g}'):
    if x is None:
        return '-'
    if isinstance(x, str):
        return x
    if not np.isfinite(x):
        return 'nan'
    return fmt.format(x)


def e(x):
    return f(x, '{:.2e}') if x is not None else '-'


LAW = {'E1': math.log(8) / math.log(256), 'E2_n32': math.log(8) / math.log(32), 'E2_n64': 0.5, 'E2_n128': math.log(8) / math.log(128),
       'E3_n64': math.log(4) / math.log(64), 'E3_n128': math.log(4) / math.log(128), 'E3_n256': 0.25, 'E3_n512': math.log(4) / math.log(512),
       'E3_n1024': 0.2, 'E4': math.log(64) / math.log(1024)}
SHAPE = {'E1': '256 x 32', 'E2_n32': '32 x 4', 'E2_n64': '64 x 8', 'E2_n128': '128 x 16', 'E3_n64': '64 x 16', 'E3_n128': '128 x 32',
         'E3_n256': '256 x 64', 'E3_n512': '512 x 128', 'E3_n1024': '1024 x 256', 'E4': '1024 x 16'}

P('## T1. Every method at its own cost (medians over nets; min-max in brackets)\n')
P('G_MC = gain over MC at the method\'s own cost; G_RQ = over RQMC; X_RQ = cost multiple at which RQMC reaches the method\'s '
  'error; R_ARC = best ARC variant at <= that cost / the method\'s error; wins = nets with G > 1.\n')
order = ['E2_n32', 'E2_n64', 'E2_n128', 'E1', 'E3_n64', 'E3_n128', 'E3_n256', 'E3_n512', 'E3_n1024', 'E4']
meths = ['LVTV2', 'LVT', 'LVTV2f1', 'LVT0', 'SL3', 'COV', 'ARC-k2', 'ARC-k2a', 'ARC-k3f', 'ARC-k3fa']
for s in order:
    ps = d['per_set'].get(s)
    if not ps:
        if s in d.get('not_scored', {}):
            P(f'\n{SHAPE[s]} ({s}): not scored ({d["not_scored"][s]} nets finished, < 3).\n')
        continue
    P(f'\n### {SHAPE[s]} ({s})\n')
    P('| method | nets | nMSE | cost (passes) | G_MC | G_RQ | wins vs MC / RQMC | X_RQ | R_ARC |')
    P('|---|---|---|---|---|---|---|---|---|')
    for m in meths:
        x = ps.get(m)
        if not x:
            continue
        P(f"| {m} | {x['nets']} | {e(x.get('med_e'))} [{e(x.get('min_e'))}, {e(x.get('max_e'))}] | {f(x.get('med_C'), '{:.0f}')} | "
          f"{f(x.get('med_G_MC'))} [{f(x.get('min_G_MC'))}, {f(x.get('max_G_MC'))}] | {f(x.get('med_G_RQ'))} [{f(x.get('min_G_RQ'))}, {f(x.get('max_G_RQ'))}]"
          f"{' (extrap.)' if x.get('any_G_RQ_extrap') else ''} | {x['n_beat_MC']} / {x['n_beat_RQ']} | {f(x.get('med_X_RQ'))} | {f(x.get('med_R_ARC'))} |")
    g1 = ps.get('gamma_SL'); g2 = ps.get('gamma_ARC')
    P(f"\ngamma_SL (LVTV2 -> SL3) median {f(g1['median'] if g1 else None)} [{f(g1['min'] if g1 else None)}, {f(g1['max'] if g1 else None)}]; "
      f"of medians {f(ps.get('gamma_SL_of_medians'))}. gamma_ARC (k2a -> best K = 3) median {f(g2['median'] if g2 else None)} "
      f"[{f(g2['min'] if g2 else None)}, {f(g2['max'] if g2 else None)}]. Uniform law log(n/L)/log n = {LAW[s]:.3f}; sampling 1.")
    if ps.get('rqmc_med_gain_mc'):
        P('RQMC gain over MC (median over nets) by N: ' + ', '.join(f'{k}: {f(v)}' for k, v in ps['rqmc_med_gain_mc'].items()) + '.')
    if s == 'E4':
        P(f"\nPhase 2 contest metric: mean avg_variance {f(ps.get('mean_avgvar'), '{:.3f}')}; full-budget MC raw MSE "
          f"{e(ps.get('mean_mc_full_raw'))}; full-budget RQMC raw MSE {e(ps.get('mean_rqmc_full_raw'))} (mean over nets).")
        P('| method | mean raw final-layer MSE | its cost (passes, ARC counter) | adjusted score with ARC-counter cost |')
        P('|---|---|---|---|')
        for m in meths:
            x = ps.get(m)
            if x and x.get('mean_raw_mse') is not None:
                P(f"| {m} | {e(x['mean_raw_mse'])} | {f(x.get('med_C'), '{:.0f}')} | {e(x.get('mean_adj_score_arc_counter'))} |")

P('\n## T2. Width exponents (slope of log median on log n; 95% bootstrap over nets)\n')
P('| series | slope | 95% CI | widths |')
P('|---|---|---|---|')
for k, w in sorted(d.get('width', {}).items()):
    P(f"| {k} | {w['slope']:+.2f} | [{w['lo']:+.2f}, {w['hi']:+.2f}] | {', '.join(str(x) for x in w['widths'])} |")

P('\n## T3. Registered predictions and the decision rule (PREREG sections 5-6)\n')
P('| id | registered statement | result | measured |')
P('|---|---|---|---|')
for v in d['verdicts']:
    meas = v['measured']
    if isinstance(meas, dict):
        meas = '; '.join(f'{k}: {f(x) if not isinstance(x, (dict, list)) else json.dumps(x, default=float)[:120]}' for k, x in meas.items())
    elif isinstance(meas, float):
        meas = f(meas, '{:.3g}')
    P(f"| {v['id']} | {v['text']} | {v['result']} | {str(meas)[:220]} |")
open(sys.argv[2], 'w').write('\n'.join(out) + '\n')
print('wrote', sys.argv[2])
