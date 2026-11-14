# usage: python3 -I permlp_compare.py SUB_HTML...  (first file is the reference)
# Compares per-MLP public final-layer MSE across submissions (Spearman/Pearson on logs) and per-MLP flops/backend time.
import sys, html, json, math, statistics as st
def arr(h, key):
    j = h.find('"%s":[' % key)
    if j < 0: return None
    j += len('"%s":' % key); depth, k = 0, j
    while k < len(h):
        if h[k] == '[': depth += 1
        elif h[k] == ']':
            depth -= 1
            if depth == 0: break
        k += 1
    return json.loads(h[j:k+1])
def rank(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); r = [0]*len(v)
    for p, i in enumerate(o): r[i] = p
    return r
def pear(a, b):
    ma, mb = st.mean(a), st.mean(b)
    num = sum((x-ma)*(y-mb) for x, y in zip(a, b))
    den = math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
    return num/den
data = {}
for f in sys.argv[1:]:
    h = html.unescape(open(f, encoding='utf-8', errors='replace').read())
    pub = arr(h, 'public_scores'); rows = arr(h, 'per_mlp')
    mse = {p['mlp_index']: p['scores']['final_layer_mse'] for p in pub}
    names = {r['mlp_index']: r['mlp_name'] for r in rows}
    tel = {r['mlp_index']: r['telemetry'] for r in rows}
    data[f] = (mse, names, tel)
ref = sys.argv[1]
idx = sorted(data[ref][0])
for f in sys.argv[1:]:
    mse, names, tel = data[f]
    same_names = all(names.get(i) == data[ref][1].get(i) for i in range(100))
    a = [math.log(data[ref][0][i]) for i in idx]; b = [math.log(mse[i]) for i in idx]
    ratio = [mse[i]/data[ref][0][i] for i in idx]
    print('%s: same MLP names/order as ref: %s | log-MSE Pearson vs ref %.3f, Spearman %.3f | median MSE ratio to ref %.2f | spread max/min %.2f'
          % (f, same_names, pear(a, b), pear(rank(a), rank(b)), st.median(ratio), max(mse.values())/min(mse.values())))
# flops vs backend time correlation for ref
mse, names, tel = data[ref]
fl = [tel[i]['flops_used'] for i in range(100)]; bt = [tel[i]['flopscope_backend_time_s'] for i in range(100)]
print('ref flops_used vs backend time Pearson %.3f; flops range %.4g-%.4g; backend s per 1e9 FLOPs: %.3f' % (pear(fl, bt), min(fl), max(fl), st.mean(bt)/st.mean(fl)*1e9))
print('ref public MLP names (first 10):', [names[i] for i in range(10)])
print('ref per-MLP flops vs public MSE Pearson (log):', round(pear([math.log(tel[i]['flops_used']) for i in idx], [math.log(mse[i]) for i in idx]), 3))
