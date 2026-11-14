"""Scorecard (results/scorecard.md) from the hashed scorer's output results/score_part1.json and the registered
correction results/score_corrections.json. Presentation only; wording abbreviated (PREREG.md has the exact text)."""
import json, os
import numpy as np

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
S = json.load(open(os.path.join(RES, 'score_part1.json')))
C = json.load(open(os.path.join(RES, 'score_corrections.json'))) if os.path.exists(os.path.join(RES, 'score_corrections.json')) else {}


def f(x):
    try:
        x = float(x)
    except Exception:
        return str(x)
    if not np.isfinite(x):
        return 'nan'
    return f'{x:.3g}'


rows = []
p1 = S['P1']['cuts']
rows.append(('P1', 'n = 256: median b2(cond_futnl64)/b2(cond_pca64) <= 0.5 at >= 3 of l = 4, 8, 16, 24',
             '; '.join(f'l={l}: {f(v["median"])} ({len(v["ratios"])} nets)' for l, v in p1.items()), S['P1']['holds']))
rows.append(('P2', 'I_16(256) < I_16(64), I_16 = gauss/futnl16 in the recursion',
             '; '.join(f'{n}: {f(v)}' for n, v in S['P2']['I16'].items()), S['P2']['holds']))
rows.append(('P3', 'gauss/futnl{n/4} >= 2 and gauss/futnl{n/2} >= 10 at every width',
             '; '.join(f'{n}: {f(v["I_quarter"])}, {f(v["I_half"])}' for n, v in S['P3']['widths'].items()), S['P3']['holds']))
rows.append(('P4', 'median b2 futnl{n/4} < pca{n/4} at every width',
             '; '.join(f'{n}: {f(v["futnl"])} vs {f(v["pca"])}' for n, v in S['P4']['widths'].items()), S['P4']['holds']))
rows.append(('P5', 'particle recursion futnl{n/2} at its honest cost: G_RQMC < 0.5 on every net',
             '; '.join(f'{n}: max {f(max([g for g in v["G"] if g is not None], default=float("nan")))}'
                       for n, v in S['P5']['widths'].items()), S['P5']['holds']))
rows.append(('P6', '(a) R(futv, n/4) >= 0.7; (b) R(pca, n/8) < R(futv, n/8), every width',
             '; '.join(f'{n}: R(futv,n/4) {f(v["R"]["futv"][str(n // 4)] if str(n // 4) in v["R"]["futv"] else v["R"]["futv"].get(n // 4))}, '
                       f'R(futv,n/8) {f(v["R"]["futv"][str(n // 8)] if str(n // 8) in v["R"]["futv"] else v["R"]["futv"].get(n // 8))} vs '
                       f'R(pca,n/8) {f(v["R"]["pca"][str(n // 8)] if str(n // 8) in v["R"]["pca"] else v["R"]["pca"].get(n // 8))}'
                       for n, v in ((int(k), w) for k, w in S['P6']['widths'].items())), S['P6']['holds']))
p7c = C.get('P7_corrected')
rows.append(('P7', 'n = 256: every D1 variant at its implemented cost has G_RQMC < 0.2 (5/5 nets)',
             f'hashed scorer: {"holds" if S["P7"]["holds"] else "fails"} (NaN runs included); corrected (NaN runs '
             f'excluded, deviations item 3): max G {f(p7c["max_G"]) if p7c else "-"} over {p7c["n_runs"] if p7c else "-"} runs, '
             f'{len(p7c["failed_runs"]) if p7c else "-"} failed runs', (p7c or {}).get('holds', S['P7']['holds'])))
PH = os.path.join(RES, 'score_corrections_posthoc.json')
ph = json.load(open(PH))['P8_posthoc'] if os.path.exists(PH) else None
rows.append(('P8', 'n = 256, dedicated best-case cost: median G_RQMC of k3p(futmf2, 64) and k3p(futv, 64) <= 3',
             'hashed scorer: ' + '; '.join(f'{k}: {f(v["median"])}' for k, v in S['P8']['kinds'].items())
             + ' (FAILS: it looked up "futmf264", the runs are "futmf2_64"; deviations item 7)'
             + ('; post hoc with the actual names: ' + '; '.join(f'{k}: {f(v["median"])}' for k, v in ph['kinds'].items())
                + (' -> holds' if ph['holds'] else ' -> fails') if ph else ''),
             S['P8']['holds']))
p9 = S['P9']
rows.append(('P9', '(a) l = 1 best eta >= 0.25; (b) l >= 8 every control beta_eg >= 1e-4; (c) best equal-cost gain at '
             '6.5e4 passes <= 2 (n = 256)',
             f'(a) median eta {f(np.median(p9["eta_l1"]) if p9["eta_l1"] else float("nan"))}: {p9["a"]}; (b) min median beta '
             f'{f(p9["beta_min_median_l8plus"])}: {p9["b"]}; (c) median gain {f(np.median(p9["best_gain"]) if p9["best_gain"] else float("nan"))}: {p9["c"]}',
             p9['holds']))
out = ['| id | prediction (abbreviated) | measured | result |', '|---|---|---|---|']
for r in rows:
    out.append(f'| {r[0]} | {r[1]} | {r[2]} | {"HOLDS" if r[3] else "FAILS"} |')
open(os.path.join(RES, 'scorecard.md'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
