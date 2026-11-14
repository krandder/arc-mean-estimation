"""Tables for S9 (real-valued chain spectra), S10 (compressed simulator) and S11 (controls through the same pipeline).
-> results/S9_S11_table.md"""
import glob
import json
import math
import os

import numpy as np

lines = []


def med(v):
    v = [x for x in v if x is not None]
    return f'{np.median(v):.3f}' if v else '-'


def s9_rows(d_glob, label):
    rows = []
    for p in sorted(glob.glob(d_glob)):
        d = json.load(open(p))
        for pm in d['per_model']:
            W1 = [t['learned']['W1_exact'] for t in pm['transitions']]
            nin = [t['learned']['n_inputs_1pct'] for t in pm['transitions']]
            hd = [t['base_highdeg']['W1_exact'] for t in pm['transitions']]
            ln = [t['base_linear']['W1_exact'] for t in pm['transitions']]
            r2 = [t['R2_T'] for t in pm['transitions']]
            rows.append(f'| {label} | {os.path.basename(p)[2:-5]} | {pm["lam"]} | {[round(x, 1) for x in pm["rate"]]} | '
                        f'{[round(x, 3) for x in pm["own"]]} | {[round(x, 3) for x in pm["chain"]]} | '
                        f'{[round(x, 2) for x in W1]} | {[round(x, 2) for x in r2]} | {nin} | {med(ln)} / {med(hd)} |')
    return rows


lines += ['# S9 real-valued chains and S11 controls', '',
          'W1 = degree-1 (linear) share of each learned transition in the Gaussian convention; R2_T = transition fit; '
          'inputs = inputs with total effect > 1% (of 8); baselines: random linear (W1 = 1) / random sine map.', '',
          '| net | chain | lambda | rate by layer | own nMSE | chain nMSE | W1 of T | R2 of T | inputs | baselines lin/sine |',
          '|---|---|---|---|---|---|---|---|---|---|']
lines += s9_rows('runs/S_real/R_*.json', 'relu')
for k in ['tanh4', 'feistel', 'linear']:
    lines += s9_rows(f'runs/S11_{k}/R_*.json', k)
lines += ['', '# S10 compressed simulator (final-layer nMSE by transition class; deductive error vs MC/RQMC)', '',
          '| net | class | rate c0 | nMSE at each grid layer (lambda 0.01) | final nMSE (0.01 / 0.001) | deductive err N=4096 / 65536 | MC / RQMC at 65536 |',
          '|---|---|---|---|---|---|---|']
for netlab, pat in [('relu', 'runs/S_sim/Q_*.json'), ('tanh4', 'runs/S11_tanh4/Q_*.json'), ('feistel', 'runs/S11_feistel/Q_*.json'),
                    ('linear', 'runs/S11_linear/Q_*.json')]:
    for p in sorted(glob.glob(pat)):
        d = json.load(open(p))
        de = d.get('deductive_err')
        lines.append(f'| {netlab} {d["n"]}x{d["L"]} | {d["kind"]} | {[round(x, 1) for x in d["rate_c0"]]} | '
                     f'{[round(x[0], 3) for x in d["nmse"]]} | {round(d["nmse"][-1][0], 3)} / {round(d["nmse"][-1][-1], 3)} | '
                     f'{(f"{min(de["4096"]):.1e} / {min(de["65536"]):.1e}") if de else "-"} | '
                     f'{d["mc_rqmc"]["65536"]["mc"]:.1e} / {d["mc_rqmc"]["65536"]["rqmc"]:.1e} |')
# S11 S7 rates by layer
lines += ['', '# S11: bits by layer (gfix R(0.1), fixed-noise real code) for the controls vs ReLU 16 x 16 seed 5000', '']


def rate_at(rates, nmse, eps):
    pts = sorted(zip(rates, nmse))
    env, best = [], float('inf')
    for r, e in pts:
        if e < best:
            env.append((r, e))
            best = e
    for i, (r, e) in enumerate(env):
        if e <= eps:
            if i == 0:
                return r
            r0, e0 = env[i - 1]
            f = (math.log(e0) - math.log(eps)) / (math.log(e0) - math.log(max(e, 1e-30)))
            return r0 + f * (r - r0)
    return None


lines.append('| net | class | l = 0 | 4 | 8 | 12 | 15 | out |')
lines.append('|---|---|---|---|---|---|---|---|')
for netlab, d0 in [('relu', 'runs/S_ent'), ('tanh4', 'runs/S11_tanh4'), ('feistel', 'runs/S11_feistel')]:
    for cls in ['local', 'unres']:
        row = []
        for l in [0, 4, 8, 12, 15, 16]:
            c = cls if l < 16 else 'unres'
            p = f'{d0}/E_n16_L16_s5000_l{l}_{c}.json'
            if os.path.exists(p):
                g = json.load(open(p))['curves']['gfix']
                r = rate_at(g['rate'], g['nmse'], 0.1)
                row.append('unreached' if r is None else f'{r:.1f}')
            else:
                row.append('-')
        lines.append(f'| {netlab} | {cls} | ' + ' | '.join(row) + ' |')
open('results/S9_S11_table.md', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
