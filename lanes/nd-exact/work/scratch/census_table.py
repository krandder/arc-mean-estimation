"""Tabulate the region census (runs/census_s*_n22.json) into results/census_table.md."""
import json
import sys

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/lib')
import ndx  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/nd-exact/'
rows = []
R = {s: json.load(open(BASE + f'runs/census_s{s}_n22.json')) for s in ndx.EVAL_SEEDS}
out = ['# Region census: activation regions of layers 1..d, 2^22 Gaussian inputs per net (scratch/census.py)', '',
       'Region = activation pattern of layers 1..d (a polyhedral cone; the net is linear on it). Output mass of a region =',
       'its share of E|a| (bounds its share of E[a]). GT = Good-Turing estimate of the mass in regions never seen',
       '(singletons / N). k(q) = number of regions (largest first, empirical) that cover a fraction q of the output mass;',
       'a k marked > is unresolved (GT unseen mass above 1 - q). H = Chao-Shen entropy of the region distribution (bits).', '']
for d in ['1', '2', '4', '8', '16', '24', '32']:
    out.append(f'## depth d = {d}')
    out.append('| net | distinct regions | Chao1 richness | H (bits) | GT unseen prob / output mass | k(0.9) | k(0.99) | k(0.999) | k(0.9999) |')
    out.append('|---|---|---|---|---|---|---|---|---|')
    for s in ndx.EVAL_SEEDS:
        p = R[s]['prefix'][d]
        ks = []
        for q in (0.9, 0.99, 0.999, 0.9999):
            k = p[f'k_amass_{q}']
            ks.append(('> %d' % k) if p['gt_unseen_amass'] > (1 - q) else '%d' % k)
        out.append('| %d | %d | %.3g | %.1f | %.2g / %.2g | %s |' % (
            s, p['distinct'], p['chao1'], p['H_chaoshen_bits'], p['gt_unseen_prob'], p['gt_unseen_amass'],
            ' | '.join(ks)))
    out.append('')
out.append('## Downstream classes (pattern of layers c+1..256), share of output mass in the top class')
out.append('| net | ' + ' | '.join(f'c = {c}' for c in R[203]['cuts']) + ' |')
out.append('|---|' + '---|' * len(R[203]['cuts']))
for s in ndx.EVAL_SEEDS:
    cells = []
    for c, v in R[s]['cuts'].items():
        cells.append('%d cl., %.6f' % (v['distinct'] - 1, v['top_amass']))
    out.append(f'| {s} | ' + ' | '.join(cells) + ' |')
out.append('')
out.append('Classes counted exclude the dead class (h_c = 0). A top-class share of 1.000000 means every sampled live input')
out.append('shares one downstream pattern, so E[a] = J_c E[h_c] on the sample.')
out.append('')
out.append('## Rank: share of output mass on inputs that passed a layer with exactly one active unit by depth d')
out.append('| net | d = 8 | 16 | 24 | 32 | min active units <= 2 by d = 24 (share of inputs) |')
out.append('|---|---|---|---|---|---|')
for s in ndx.EVAL_SEEDS:
    p = R[s]['prefix']
    h = p['24']['minact_hist']
    le2 = sum(h[:3]) / sum(h)
    out.append('| %d | %.3f | %.3f | %.3f | %.3f | %.4f |' % (s, p['8']['rank1_amass'], p['16']['rank1_amass'],
                                                         p['24']['rank1_amass'], p['32']['rank1_amass'], le2))
open(BASE + 'results/census_table.md', 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
