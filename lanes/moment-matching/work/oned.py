"""1D reference: moment-matching gap for relu(x), x~N(0,1), d moments. MEASURED (exploratory).
Grid LP on [-R,R]; relu sd = sqrt(1/2 - 1/(2pi))."""
import math, json, numpy as np
from scipy.optimize import linprog
sd = math.sqrt(0.5 - 1/(2*math.pi))
out = {}
for d in range(1, 41):
    R = 4 + 2*math.sqrt(d)
    for G in (4001, 16001):
        x = np.linspace(-R, R, G); x = np.union1d(x, [0.0])
        H = np.empty((d+1, len(x))); H[0] = 1
        if d >= 1: H[1] = x
        for k in range(1, d): H[k+1] = x*H[k] - k*H[k-1]
        for k in range(d+1): H[k] /= math.sqrt(math.factorial(k))
        b = np.zeros(d+1); b[0] = 1
        f = np.maximum(x, 0)
        r1 = linprog(-f, A_eq=H, b_eq=b, bounds=(0, None), method="highs")
        r2 = linprog(f, A_eq=H, b_eq=b, bounds=(0, None), method="highs")
        g = (-r1.fun - r2.fun)/sd if r1.status == 0 and r2.status == 0 else None
        out.setdefault(d, []).append((G, R, g))
    print(d, out[d], flush=True)
json.dump(out, open("oned_relu.json", "w"))
