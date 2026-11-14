"""Report tables for sections 5-7 from results/score.json (formatting only). usage: report_tables.py SCORE_JSON OUT_MD"""
import json, math, sys
import numpy as np

d = json.load(open(sys.argv[1]))
OUT = []
P = OUT.append


def g(x, fmt='{:.2g}'):
    return '-' if x is None else fmt.format(x)


def e2(x):
    return '-' if x is None else f'{x:.1e}'


def s_(s, m, k):
    return (d['per_set'].get(s, {}).get(m) or {}).get(k)


LAW = lambda n, L: math.log(n / L) / math.log(n)
CLAIM = {64: 2.17, 128: 1.52, 256: 1.51, 512: 1.41, 1024: 1.21}

P('### Section 5 table (L = n/8)\n')
P('| n x L | LVTV2 nMSE @ cost | G_MC | G_RQ (wins vs MC, RQMC) | X_RQ | SL3 nMSE @ cost | SL3 G_RQ | gamma_SL | gamma_ARC | law |')
P('|---|---|---|---|---|---|---|---|---|---|')
for s, n, L in (('E2_n32', 32, 4), ('E2_n64', 64, 8), ('E2_n128', 128, 16), ('E1', 256, 32)):
    ps = d['per_set'].get(s)
    if not ps:
        continue
    a = ps.get('LVTV2', {}); b = ps.get('SL3', {})
    P(f"| {n} x {L} | {e2(a.get('med_e'))} @ {g(a.get('med_C'), '{:.0f}')} | {g(a.get('med_G_MC'))} | {g(a.get('med_G_RQ'))} "
      f"({a.get('n_beat_MC')}/{a.get('nets')}, {a.get('n_beat_RQ')}/{a.get('nets')}) | {g(a.get('med_X_RQ'))} | {e2(b.get('med_e'))} @ "
      f"{g(b.get('med_C'), '{:.2g}')} | {g(b.get('med_G_RQ'))} | {g((ps.get('gamma_SL') or {}).get('median'))} | "
      f"{g((ps.get('gamma_ARC') or {}).get('median'))} | {LAW(n, L):.3f} |")

P('\n### Section 6 table (L = n/4, the claim\'s diagonal; fresh nets)\n')
P('| n x L | nets | LVTV2 nMSE @ cost | G_MC (median; of mean) | claim\'s G_MC | G_RQ (wins vs RQMC) | X_RQ | RQMC gain over MC near that cost | ARC best at <= cost / LVTV2 | SL3 nMSE @ cost, G_RQ | gamma_SL | law |')
P('|---|---|---|---|---|---|---|---|---|---|---|---|')
for n, L in ((64, 16), (128, 32), (256, 64), (512, 128), (1024, 256)):
    s = f'E3_n{n}'
    ps = d['per_set'].get(s)
    if not ps:
        P(f'| {n} x {L} | not scored ({d.get("not_scored", {}).get(s, 0)} nets) | | | | | | | | | | |')
        continue
    a = ps.get('LVTV2', {}); b = ps.get('SL3', {})
    rows = d['per_net'][s]
    gains = []
    for r in rows:
        if 'rqmc' in r and 'LVTV2' in r['m']:
            Ns = np.array(r['rqmc']['N']); gm = np.array(r['rqmc']['gain_mc']); C = r['m']['LVTV2']['C']
            gains.append(float(np.exp(np.interp(math.log(C), np.log(Ns), np.log(gm)))))
    P(f"| {n} x {L} | {a.get('nets')} | {e2(a.get('med_e'))} @ {g(a.get('med_C'), '{:.0f}')} | {g(a.get('med_G_MC'))}; {g(a.get('G_MC_of_mean'))} | "
      f"{CLAIM[n]} | {g(a.get('med_G_RQ'))} [{g(a.get('min_G_RQ'))}, {g(a.get('max_G_RQ'))}] ({a.get('n_beat_RQ')}/{a.get('nets')}) | "
      f"{g(a.get('med_X_RQ'))} | {g(float(np.median(gains)) if gains else None)} | {g(a.get('med_R_ARC'))} | "
      f"{(e2(b.get('med_e')) + ' @ ' + g(b.get('med_C'), '{:.2g}') + ', ' + g(b.get('med_G_RQ'))) if b else '-'} | "
      f"{g((ps.get('gamma_SL') or {}).get('median'))} | {LAW(n, L):.3f} |")

P('\n### Section 7 table (1024 x 16, Phase 2 public MLPs 0-11)\n')
ps = d['per_set'].get('E4', {})
P(f"Mean avg_variance {g(ps.get('mean_avgvar'), '{:.3f}')}; full-budget (65,536-pass) MC raw MSE {e2(ps.get('mean_mc_full_raw'))}; "
  f"full-budget RQMC raw MSE {e2(ps.get('mean_rqmc_full_raw'))}.\n")
P('| method | nets | mean raw final-layer MSE | cost (passes, ARC counter) | G_MC | G_RQ | full-budget RQMC raw / method raw (median) | adjusted score (contest formula, ARC-counter cost) |')
P('|---|---|---|---|---|---|---|---|')
for m in ('COV', 'ARC-k2', 'ARC-k2a', 'LVTV2', 'LVT', 'LVTV2f1', 'LVT0', 'ARC-k3f', 'SL3'):
    a = ps.get(m)
    if not a:
        continue
    rat = [r['rqmc_full_raw'] / r['m'][m]['raw_mse'] for r in d['per_net']['E4'] if m in r['m'] and 'rqmc_full_raw' in r]
    P(f"| {m} | {a['nets']} | {e2(a.get('mean_raw_mse'))} | {g(a.get('med_C'), '{:.0f}')} | {g(a.get('med_G_MC'))} | {g(a.get('med_G_RQ'))} | "
      f"{g(float(np.median(rat)) if rat else None)} | {e2(a.get('mean_adj_score_arc_counter'))} |")
ga = (ps.get('gamma_ARC') or {})
gs = (ps.get('gamma_SL') or {})
P(f"\ngamma_ARC (k2a -> k3f) median {g(ga.get('median'))} [{g(ga.get('min'))}, {g(ga.get('max'))}]; gamma_SL median {g(gs.get('median'))}; "
  f"law log 64 / log 1024 = 0.600.")
open(sys.argv[2], 'w').write('\n'.join(OUT) + '\n')
print('wrote', sys.argv[2])
