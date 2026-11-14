# usage: python3 -I best_of_k.py TARGET_ID ID...   (reads sub_<id>.html in cwd; ids = earlier runs)
# For each public MLP, checks whether the target's final-layer MSE equals (exactly, as printed) the MSE of some earlier run,
# and whether it equals the per-MLP minimum over the earlier runs.
import sys, html, json, statistics as st
def load(i):
    h = html.unescape(open('sub_%s.html' % i, encoding='utf-8', errors='replace').read())
    def arr(key):
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
    pub = arr('public_scores') or []
    c = h.find('"createdAt":"'); created = h[c+13:c+33]
    tel = arr('per_mlp') or []
    F = st.mean(r['telemetry']['flops_used'] for r in tel if r.get('telemetry')) if tel else None
    return created, {p['mlp_index']: p['scores']['final_layer_mse'] for p in pub}, F
tgt = sys.argv[1]
tc, T, TF = load(tgt)
runs = {}
for i in sys.argv[2:]:
    c, P, F = load(i)
    if c < tc and len(P) == 50 and i != tgt:
        runs[i] = (c, P, F)
print('target %s created %s mean MSE %.4g mean F %.4g; earlier runs with 50 public scores: %d' % (tgt, tc, st.mean(T.values()), TF, len(runs)))
match_any = match_min = 0; ratios = []
src = {}
for m in range(50):
    vals = {i: P[m] for i, (c, P, F) in runs.items()}
    mn = min(vals.values())
    hits = [i for i, v in vals.items() if v == T[m]]
    match_any += bool(hits); match_min += (T[m] == mn)
    ratios.append(T[m] / mn)
    if hits: src.setdefault(sorted(hits)[0], []).append(m)
print('public MLPs whose target MSE equals some earlier run exactly: %d/50; equals the per-MLP minimum over earlier runs: %d/50' % (match_any, match_min))
print('target / per-MLP-min ratio: min %.3f median %.3f max %.3f' % (min(ratios), st.median(ratios), max(ratios)))
print('mean over MLPs of per-MLP minimum across earlier runs: %.4g' % st.mean(min(P[m] for (c, P, F) in runs.values()) for m in range(50)))
print('source runs used (run: MLP indices):', {k: v for k, v in sorted(src.items())})
