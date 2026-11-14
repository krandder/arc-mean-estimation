"""Input-cloud vertex recursion with the source computed by exact quadrature (review r1 finding 2: the first version
interpolated a Monte Carlo source on a 201-point grid in c, which near c = 1 turns its quadratic vanishing into linear).
v_{j+1} = kappa'(c_j)^2 v_j + S(c_j), v_0 = 1, c_{j+1} = kappa(c_j), PR(l) = n (1 - c_l)^2 / v_l, with
S(c) = E_Z[ Var_eta( sqrt2 relu(sqrt(c) Z + sqrt(1-c) eta) )^2 ] (four equicorrelated inputs share Z)."""
import math, json
import numpy as np
from scipy import integrate
from scipy.stats import norm


def kap(c):
    c = min(max(c, -1.0), 1.0)
    return (math.sqrt(max(1 - c * c, 0.0)) + (math.pi - math.acos(c)) * c) / math.pi


def kprime(c):
    return (math.pi - math.acos(min(max(c, -1.0), 1.0))) / math.pi


def cond_var(z, c):
    mu = math.sqrt(2 * c) * z
    s = math.sqrt(2 * max(1 - c, 0.0))
    if s == 0:
        return 0.0
    a = mu / s
    m1 = mu * norm.cdf(a) + s * norm.pdf(a)
    m2 = (mu * mu + s * s) * norm.cdf(a) + mu * s * norm.pdf(a)
    return max(m2 - m1 * m1, 0.0)


def S(c):
    if c >= 1:
        return 0.0
    s = math.sqrt(2 * (1 - c))
    zc = 0.0
    width = 12 * s / math.sqrt(2 * c) if c > 0 else 12
    f = lambda z: cond_var(z, c) ** 2 * norm.pdf(z)
    pts = [-8.0, -width, zc, width, 8.0] if width < 8 else [-8.0, 0.0, 8.0]
    pts = sorted(set(pts))
    tot = 0.0
    for a, b in zip(pts[:-1], pts[1:]):
        tot += integrate.quad(f, a, b, limit=200, epsabs=1e-16, epsrel=1e-10)[0]
    return tot


out = {}
c, v = 0.0, 1.0
rows = []
for l in range(1, 513):
    v = kprime(c) ** 2 * v + S(c)
    c = kap(c)
    if l in (1, 2, 4, 8, 16, 32, 64, 127, 128, 256, 512):
        rows.append(dict(l=l, c=c, v=v, PR_over_n=(1 - c) ** 2 / v, asym=1.5 / l))
for r in rows:
    print('l=%3d PR/n=%.5f (n=256: %.2f, n=64: %.2f)  1.5/l=%.5f' % (r['l'], r['PR_over_n'], 256 * r['PR_over_n'], 64 * r['PR_over_n'], r['asym']))
json.dump(rows, open('/home/agent/workspaces/mats/work/gram-chain/results/vertex_exact.json', 'w'), indent=1)
