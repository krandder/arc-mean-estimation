"""Figure for the exact 1-D chain: per layer, what each chain's code knows about the output code (I(c_l; c_L)) against
the truth I(h_l; c_L), and each chain's rate. usage: figs_exact.py <exact_chain json> [<prsweep json>] <out.png>"""
import json
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

main = json.load(open(sys.argv[1]))
sweep = json.load(open(sys.argv[2])) if len(sys.argv) > 3 else None
out = sys.argv[-1]
L = main['L']
COL = {'truth': '#0b0b0b', 'K': '#2a78d6', 'PR': '#eb6834', 'P': '#1baf7a', 'R': '#eda100'}
NAME = {'K': "K: your rule (rate <= target)", 'R': 'R: next code, 95% rule', 'P': 'P: output code, rate rule',
        'PR': 'PR: output code, 95% rule'}
ls = list(range(L - 2, -1, -1))
fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.0))
ax = axes[0]
ax.plot([L - 1] + ls, [main['truth'][str(L - 1)]] + [main['truth'][str(l)] for l in ls], '-', color=COL['truth'], lw=2,
        label='truth I(h_l; c_L)')
for ch in ('R', 'PR', 'K', 'P'):
    ax.plot(ls, [main['chains'][ch][str(l)]['I_out'] for l in ls], '-o', color=COL[ch], ms=3, lw=1.6, label=NAME[ch])
if sweep:
    for name, st in [(n, sweep['chains'][n]) for n in sweep['chains'] if not n.endswith('_curves')]:
        thr = name.replace('PR', '') or '0.9'
        ax.plot(ls, [st[str(l)]['I_out'] for l in ls], ':', color=COL['PR'], lw=1.2)
        ax.annotate(f'PR {thr}', (0, st['0']['I_out']), fontsize=7, color='#52514e', xytext=(-30, 0),
                    textcoords='offset points')
ax.set_xlabel('layer l')
ax.set_ylabel('bits about the output code')
ax.set_title(f"exact 1-D chain, rho = {main['rho']}: what each code knows", fontsize=9)
ax.grid(alpha=0.25)
ax.legend(fontsize=7, loc='upper center', bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False)
ax = axes[1]
ax.plot(ls, [main['truth'][str(l)] for l in ls], '--', color=COL['truth'], lw=1.5, label='truth (lower end of any rate)')
for ch in ('R', 'PR', 'K', 'P'):
    ax.plot(ls, [main['chains'][ch][str(l)]['H'] for l in ls], '-o', color=COL[ch], ms=3, lw=1.6, label=NAME[ch])
ax.plot(ls, [main['direct'][str(l)]['rate_for_95'] for l in ls], '-s', color='#6250d6', ms=3, lw=1.6,
        label='best code carrying 95% of the truth')
ax.set_xlabel('layer l')
ax.set_ylabel('rate (bits)')
ax.set_title('rate of each chain\'s code', fontsize=9)
ax.grid(alpha=0.25)
ax.legend(fontsize=7, loc='upper center', bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False)
fig.tight_layout()
fig.savefig(out, dpi=130)
print('wrote', out)
