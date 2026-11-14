# usage: python3 -I identical_mlps.py HTML_A HTML_B [...]  -> for consecutive pairs, count public MLPs whose final-layer MSE is exactly equal
import sys, html, json
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
fs = sys.argv[1:]
P = [pub(f) for f in fs]
for a in range(len(fs)-1):
    A, B = P[a], P[a+1]
    same = [i for i in sorted(A) if A[i] == B[i]]
    lower = sum(B[i] < A[i] for i in A); higher = sum(B[i] > A[i] for i in A)
    print('%s -> %s: identical %2d/50, lower %2d, higher %2d; identical idx %s' % (fs[a], fs[a+1], len(same), lower, higher, same[:20]))
