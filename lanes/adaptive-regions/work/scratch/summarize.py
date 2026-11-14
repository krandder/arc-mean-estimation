"""Tables for the report from runs/*.json (steps 1, 2a, 2b, 4, 4b). Writes results/tables.md and prints it."""
import glob, json, math, os, sys
import numpy as np

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
R = os.path.join(HERE, 'runs')
lines = []


def P(s=''):
    lines.append(s)


def fmt(x, k=3):
    if x is None:
        return '-'
    if isinstance(x, str):
        return x
    if x == 0:
        return '0'
    if abs(x) < 1e-3 or abs(x) >= 1e4:
        return f'{x:.1e}'
    return f'{x:.{k}f}'


def load(pat):
    out = []
    for f in sorted(glob.glob(os.path.join(R, pat))):
        try:
            out.append(json.load(open(f)))
        except Exception:
            pass
    return out


# ---------------- step 1
P('## Step 1: exact pieces (eps = 0), held-out coverage of the top-K training pieces')
P()
P('Per-output pieces: suffix gate pattern of layers l+1..L-1 plus the output\'s own gate; cones where the output is off')
P('merged into one zero piece ("merged"). Medians over the outputs of each class. back = L-1-l.')
P()
P('| n x L | net | classes zero/on/sw | on-class var share | back 1: on cov K=1 / 1000 | back 1: zero cones K=1000 | back 2: on cov K=1000 | layers back with on-class cov >= 50% (K=1000) | vector pieces for 50% at back 0 |')
P('|---|---|---|---|---|---|---|---|---|')
for d in load('step1_n*_L*_s*.json'):
    lay = {r['l']: r for r in d['layers']}
    L = d['L']
    cs = lambda l, c, key: (lay[l]['class_summary'].get(c, {}).get(key) if l in lay and not lay[l].get('per_output_skipped') else None)
    b1 = L - 2; b2 = L - 3
    surv = 0
    for b in range(0, L):
        l = L - 1 - b
        v = cs(l, 'on', 'merged_cov_K1000_median')
        if v is None:
            v = cs(l, 'switching', 'cones_cov_K1000_median')
        if v is not None and v >= 0.5:
            surv = b
        else:
            break
    v31 = lay[L - 1]['vector']
    vec = v31['pieces_q50'] if v31['pieces_q50'] is not None else (f">= {0.25 * (v31['n_eff'] or v31['n_eff_lower95']):.1e}")
    cl = d['classes']
    P(f"| {d['n']} x {L} | {d['seed']} | {cl['zero']}/{cl['on']}/{cl['switching']} | {fmt(d['var_share_class']['on'])} | "
      f"{fmt(cs(b1, 'on', 'merged_cov_K1_median'))} / {fmt(cs(b1, 'on', 'merged_cov_K1000_median'))} | "
      f"{fmt(cs(b1, 'zero', 'cones_cov_K1000_median'))} | {fmt(cs(b2, 'on', 'merged_cov_K1000_median'))} | {surv} | {vec} |")
P()
P('Switching units per layer (gate not constant on >= 99.9% of inputs) and the marginal-entropy upper bound on the')
P('suffix pattern (bits) at back 0, 1, 8, 16, L-1:')
P()
for d in load('step1_n*_L*_s*.json'):
    lay = {r['l']: r for r in d['layers']}
    L = d['L']
    hs = [round(lay[L - 1 - b]['H_marg_suffix_vector']) if (L - 1 - b) in lay and 'H_marg_suffix_vector' in lay[L - 1 - b] else None for b in (0, 1, 8, 16, L - 1) if L - 1 - b >= 0]
    sw = d['switching_units_per_layer']
    P(f"- {d['n']} x {L} net {d['seed']}: switching units at layers 1, 2, L/2, L-1, L: {sw[0]}, {sw[1]}, {sw[L // 2 - 1]}, {sw[L - 2]}, {sw[L - 1]}; suffix bits {hs}")
P()

# ---------------- step 2a
P('## Step 2a: one-shot CROWN certificates over PCA boxes (box) and box + CROWN halfspace slices (slice)')
P()
P('Median over outputs of each class of the best held-out certified coverage; eps in units of the output\'s RMS.')
P()
P('| n x L | net | back | class | box: eps 0 / 1e-3 / 1e-2 / 1e-1 | slice: eps 0 / 1e-3 / 1e-2 / 1e-1 |')
P('|---|---|---|---|---|---|')
for d in load('step2a_n*_L*_s*.json'):
    for row in d['layers']:
        for c, sm in row['class_summary'].items():
            P(f"| {d['n']} x {d['L']} | {d['seed']} | {row['back']} | {c} | " +
              ' / '.join(fmt(sm.get(f'box_cov_e{e:g}_median')) for e in d['eps']) + ' | ' +
              ' / '.join(fmt(sm.get(f'slice_cov_e{e:g}_median')) for e in d['eps']) + ' |')
P()

# ---------------- step 2b
P('## Step 2b: slices with pinned gates (cloud-fixed units always pinned, plus 0..all switching units by effect)')
P()
P('Best held-out certified coverage per output (over tau and the number of pinned switching units), listed per class.')
P()
P('| n x L | net | back | eps | zero outputs | on outputs | switching outputs |')
P('|---|---|---|---|---|---|---|')
for d in load('step2b_n*_L*_s*.json'):
    best = {}
    for x in d['results']:
        k = (x['back'], x['eps'], x['cls'], x['j'])
        best[k] = max(best.get(k, 0.0), x['cov'])
    for back in sorted(set(k[0] for k in best)):
        for e in d['eps']:
            cols = []
            for c in ('zero', 'on', 'switching'):
                v = sorted([best[k] for k in best if k[0] == back and k[1] == e and k[2] == c])
                cols.append(', '.join(fmt(x, 2) for x in v) if v else '-')
            P(f"| {d['n']} x {d['L']} | {d['seed']} | {back} | {e:g} | " + ' | '.join(cols) + ' |')
P()

# ---------------- step 4 (centroid zones, free regression)
st4 = load('step4_n*_L*_s*.json')
if st4:
    P('## Step 4 (centroid zones, freely regressed experts): held-out pointwise nMSE of the expert prediction')
    P()
    for d in st4:
        P(f"n x L = {d['n']} x {d['L']}, net {d['seed']} (zones: K-means on top-{d['d']} PCA coords; experts: ridge on them):")
        P()
        P('| l | back | ' + ' | '.join(f"K={K}: nMSE (pred, calib, cov)" for K in d['Ks']) + ' |')
        P('|---|---|' + '---|' * len(d['Ks']))
        for row in d['layers']:
            P(f"| {row['l']} | {row['back']} | " + ' | '.join(
                f"{fmt(r_['nmse_all'], 4)} ({fmt(r_['pred_res_nmse'], 4)}, {fmt(r_['calib_median'], 2)}, {fmt(r_['coverage'], 3)})" for r_ in row['rows']) + ' |')
        P()
        for t in d.get('transitions', []):
            P(f"- landing {t['l'] - 1}->{t['l']}, K={t['K']}: landing entropy {t['T_entropy_bits']:.2f} bits; output error of the landing-mean"
              f" approximation (independent landing) {fmt(t['err_i_nmse'])}, (per-expert Gaussian) {fmt(t['err_ii_nmse'])} (nMSE units)")
        for c in d.get('closure', []):
            P(f"- mixture closure from l0 = {c['l0']}, K = {c['K']}: nMSE {fmt(c['nmse'])}")
        P()

# ---------------- step 4b (composed gate-pattern experts)
st4b = load('step4b_n*_L*_s*.json')
if st4b:
    P('## Step 4 (Kelvin\'s variant a): composed gate-pattern experts; leftover variance and estimates')
    P()
    P('| n x L | net | p_deep (zones/layer <= 2^p) | leftover Var(f-g)/Var f at back 0 / 1 / L/2 / L-2 | input zones: leftover | model-only nMSE | unbiased nMSE (expected) | cost (passes) | RQMC at that cost | MC at that cost |')
    P('|---|---|---|---|---|---|---|---|---|---|')
    for d in st4b:
        L = d['L']
        for run in d['runs']:
            lay = {x['l']: x for x in run['layers']}
            lo = [lay[L - 1 - b]['leftover_te'] if (L - 1 - b) in lay else None for b in (0, 1, L // 2, L - 2)]
            for x in run['input']:
                P(f"| {d['n']} x {L} | {d['seed']} | {run['p_deep']} | " + ' / '.join(fmt(v, 3) for v in lo) +
                  f" | {x['zones']}: {fmt(x['leftover_te'], 3)} | {fmt(x['nmse_model'])} | {fmt(x['nmse_unbiased'])} ({fmt(x['expected_unbiased'])}) | "
                  f"{x['cost_unbiased']:.0f} | {fmt(x['rqmc_at_cost_unbiased'])} | {fmt(x['mc_at_cost_unbiased'])} |")
    P()

out = os.path.join(HERE, 'results', 'tables.md')
open(out, 'w').write('# adaptive-regions tables (generated by scratch/summarize.py)\n\n' + '\n'.join(lines) + '\n')
print('\n'.join(lines))
