"""Descriptive summary of the noise runs (E3): pooled GSA per layer relative to n/sqrt(2 pi), total partition GSA,
P(pattern changes) vs delta, output NS slope relative to n/V, spherical NS curve. Medians over nets per width."""
import json, math, os, sys, numpy as np
sys.path.insert(0, 'lib'); import rnd
W = {32: (4, range(300, 308)), 64: (8, range(300, 308)), 128: (16, range(300, 308)), 256: (32, range(200, 205))}
ds = ('1e-06', '1e-05', '0.0001')
out = {}
for n, (L, seeds) in W.items():
    rows = []
    for s in seeds:
        r = json.load(open(f'runs/noise_n{n}_L{L}_s{s}.json'))
        fl = sum(np.array(r['gauss'][d]['flips']) for d in ds)
        gsa = fl / sum(2 * math.sqrt(float(d) / math.pi) for d in ds) / (n / math.sqrt(2 * math.pi))
        V = rnd.load_truth(s, n, L)['V']
        rows.append(dict(gsa=gsa, tot=gsa.sum() / L, pany={d: r['gauss'][d]['p_any'][-1] for d in r['gauss']},
                         ns_slope=r['gauss']['1e-05']['ns'][-1] / 1e-5 / (n / V), mean_deg=r['gauss']['1e-05']['ns'][-1] / 1e-5,
                         n_over_V=n / V, nssph={d: r['sph'][d]['ns_sph'] for d in r['sph']},
                         ns_layers=[r['gauss']['1e-05']['ns'][l] / 1e-5 for l in range(L)]))
    G = np.array([x['gsa'] for x in rows])
    q = lambda k: [round(float(np.median([x[k] for x in rows])), 3)]
    print(f'n={n} L={L}: GSA/layer (median over nets) first,mid,last = {np.median(G[:,0]):.3f} {np.median(G[:,L//2]):.3f} {np.median(G[:,-1]):.3f};'
          f' min..max over layers&nets {G.min():.2f}..{G.max():.2f}; total/(nL/sqrt2pi) median {np.median([x["tot"] for x in rows]):.3f}')
    print(f'   P(pattern changes) by delta: ' + ' '.join(f'{d}:{np.median([x["pany"][d] for x in rows]):.3f}' for d in ('1e-06','1e-05','0.0001','0.001')))
    print(f'   NS_out slope (mean Hermite degree) median {np.median([x["mean_deg"] for x in rows]):.1f}; n/V median {np.median([x["n_over_V"] for x in rows]):.1f}; ratio median {np.median([x["ns_slope"] for x in rows]):.2f} range {min(x["ns_slope"] for x in rows):.2f}-{max(x["ns_slope"] for x in rows):.2f}')
    print(f'   NS_sph curve (median): ' + ' '.join(f'{d}:{np.median([x["nssph"][d] for x in rows]):.4f}' for d in ('1e-05','0.001','0.01','0.03','0.1','0.3','1')))
    nl = np.median(np.array([x['ns_layers'] for x in rows]), axis=0)
    print(f'   state NS slope by layer (median): ' + ' '.join(f'{v:.1f}' for v in nl[::max(1, L//8)]))
