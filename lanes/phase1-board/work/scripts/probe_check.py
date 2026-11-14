# usage: python3 -I probe_check.py BASE_HTML FINAL_HTML PROBE_HTML...
# Per-MLP public final-layer MSE differences (probe - base) and (final - base); tests for a common positive offset.
import sys, html, json, statistics as st
def pub(f):
    h = html.unescape(open(f, encoding='utf-8', errors='replace').read())
    j = h.find('"public_scores":[') + len('"public_scores":'); depth, k = 0, j
    while k < len(h):
        if h[k] == '[': depth += 1
        elif h[k] == ']':
            depth -= 1
            if depth == 0: break
        k += 1
    return {p['mlp_index']: p['scores']['final_layer_mse'] for p in json.loads(h[j:k+1])}
base = pub(sys.argv[1]); final = pub(sys.argv[2])
idx = sorted(base)
print('base mean %.4g | final mean %.4g' % (st.mean(base.values()), st.mean(final.values())))
fr = [final[i]/base[i] for i in idx]
print('final/base per MLP: min %.3f median %.3f max %.3f; final<base on %d/50' % (min(fr), st.median(fr), max(fr), sum(final[i] < base[i] for i in idx)))
for f in sys.argv[3:]:
    p = pub(f)
    d = [p[i]-base[i] for i in idx]
    r = [p[i]/base[i] for i in idx]
    print('%s: mean %.4g | d=probe-base: mean %.3g median %.3g sd %.3g min %.3g max %.3g | n(d<0) %d | ratio median %.2f'
          % (f, st.mean(p.values()), st.mean(d), st.median(d), st.pstdev(d), min(d), max(d), sum(x < 0 for x in d), st.median(r)))
