"""Summary numbers of results/P2_noisy_maps.json for report section 3.5 (descriptive). usage: summ_noisy.py [file]"""
import json, sys
D = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'results/P2_noisy_maps.json'))
for sel in ('all', 'n16', 'n32'):
    st, tr = [], []
    for net, v in D.items():
        if sel != 'all' and not net.startswith(sel):
            continue
        for l, e in v.items():
            if not isinstance(e, dict) or 'r2_affine' not in e:
                continue
            st.append((e['r2_affine'], e['r2_mlp']))
            for k, t in e['transfer'].items():
                tr.append((net, int(l), int(k), t['affine'], t['mlp']))
    if not st:
        continue
    a = [x[0] for x in st]; m = [x[1] for x in st]
    print(sel, f'steps n={len(st)} affine {min(a):.2f}-{max(a):.2f} mlp {min(m):.2f}-{max(m):.2f}')
    print(sel, f'transfers n={len(tr)} mlp<0 {sum(t[4] < 0 for t in tr)} (max {max(t[4] for t in tr):.2f}); '
               f'affine>0 {sum(t[3] > 0 for t in tr)} (max {max(t[3] for t in tr):.2f})')
    k4 = [t[3] for t in tr if t[2] == 4]
    if k4:
        print(sel, f'l+4 affine {min(k4):.2f}-{max(k4):.2f} n={len(k4)}; mlp', [round(t[4], 2) for t in tr if t[2] == 4])
