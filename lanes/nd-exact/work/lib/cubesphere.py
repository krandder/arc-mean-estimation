"""Adaptive cube-sphere cone code for E[f_c(x)], x ~ N(0, I_8), f_c = layers 1..c of a bias-free ReLU net.

Cells are cones over dyadic boxes on the faces of the cube: face (i, s) = {s x_i > 0, |x_j| <= |x_i|}; a cell is
C = {s x_i > 0, x_j / |x_i| in [alpha_j, beta_j] for j != i}. Such a cone is convex and polyhedral, and given
t = |x_i| the other coordinates are independent, so its Gaussian moments are one-dimensional integrals:
  P(C)        = int_0^inf phi(t) prod_j [Phi(beta_j t) - Phi(alpha_j t)] dt
  E[x_i 1_C]  = s int_0^inf t phi(t) prod_j [...] dt
  E[x_j 1_C]  = int_0^inf phi(t) [phi(alpha_j t) - phi(beta_j t)] prod_{k != j} [...] dt
(Gauss-Legendre on [0, T]; the integrands are smooth). On a cone where the activation pattern of layers 1..c is
constant, f_c(x) = A x, and since the conditional mean m = E[x 1_C]/P(C) lies in C, E[f_c 1_C] = P(C) f_c(m) exactly.
The pattern is certified constant by exact interval arithmetic in the gnomonic coordinates (w.x / |x_i| =
s w_i + sum_j w_j gamma_j, gamma_j in [alpha_j, beta_j]), layer by layer with the cell's linear map.
Every cell's estimate is P(C) f_c(m): exact on certified (linear) cells, the centroid rule on the others.
The tree is refined adaptively (largest P(C) |f_c(m)| first); the estimate is available at any time.
Costs are counted in FLOPs with the flopscope conventions of work/narrow-deep/lib/nd.py and reported in mv
(1 mv = 128 FLOPs = one 8x8 matrix-vector product with ReLU).
"""
import heapq
import math

import numpy as np
from scipy.special import ndtr

MV = 128.0
F_CDF, F_PDF = 96, 54
SQ2PI = math.sqrt(2.0 * math.pi)


def _phi(x):
    return np.exp(-0.5 * x * x) / SQ2PI


class Moments:
    """Gaussian moments of cube-sphere cones with cached Phi/phi tables at the dyadic breakpoints."""

    def __init__(self, Q=64, T=9.0, n=8):
        x, w = np.polynomial.legendre.leggauss(Q)
        self.t = 0.5 * T * (x + 1.0)
        self.w = 0.5 * T * w
        self.bw = self.w * _phi(self.t)          # weights times phi(t)
        self.tbw = self.t * self.bw
        self.Q, self.n = Q, n
        self.cache = {}
        self.flops = 0.0

    def table(self, g):
        r = self.cache.get(g)
        if r is None:
            gt = g * self.t
            r = (ndtr(gt), _phi(gt))
            self.cache[g] = r
            self.flops += self.Q * (1 + F_CDF + 1 + F_PDF)
        return r

    def cone(self, i, s, alpha, beta):
        """P(C) and E[x 1_C] (n-vector) for the cone over face (i, s) with box [alpha, beta] (entries j != i)."""
        n, Q = self.n, self.Q
        js = [j for j in range(n) if j != i]
        D = np.empty((len(js), Q))
        E = np.empty((len(js), Q))
        for r, j in enumerate(js):
            Pa, pa = self.table(alpha[j])
            Pb, pb = self.table(beta[j])
            D[r] = Pb - Pa
            E[r] = pa - pb
        m = len(js)
        pre = np.ones((m + 1, Q))
        suf = np.ones((m + 1, Q))
        for r in range(m):
            pre[r + 1] = pre[r] * D[r]
            suf[m - 1 - r] = suf[m - r] * D[m - 1 - r]
        prod = pre[m]
        P = float(self.bw @ prod)
        mom = np.zeros(n)
        mom[i] = s * float(self.tbw @ prod)
        for r, j in enumerate(js):
            mom[j] = float(self.bw @ (E[r] * pre[r] * suf[r + 1]))
        self.flops += 2 * m * Q + 2 * 2 * m * Q + 2 * Q + 2 * Q + m * (3 * Q + 2 * Q)
        return P, mom


class CubeSphere:
    """Anytime adaptive estimator of E[f_c(x)]. Ws: list of (8, 8) weights (layers 1..c are Ws[0..c-1])."""

    def __init__(self, Ws, c, Q=64, T=9.0, max_level=40, J=None, rule='surplus', floor=0.01):
        self.J = np.eye(Ws[0].shape[0]) if J is None else J   # output functional used only for priorities
        self.rule, self.floor = rule, floor
        self.Ws = Ws
        self.c = c
        self.n = Ws[0].shape[0]
        self.mom = Moments(Q, T, self.n)
        self.flops = 0.0
        self.heap = []
        self.counter = 0
        self.S_res = np.zeros(self.n)       # sum over certified cells of P f_c(m)
        self.S_open = np.zeros(self.n)      # sum over open (uncertified) leaves
        self.P_res = 0.0
        self.n_res = 0
        self.n_cells = 0
        self.max_level = max_level

    # --- per-cell work ------------------------------------------------------------------------------------------
    def _test(self, i, s, alpha, beta, k0, A):
        """Certify layers k0..c-1 (0-indexed) on the cell. Returns (k_straddle or None, A valid before it, M, strad)."""
        n = self.n
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        for k in range(k0, self.c):
            M = self.Ws[k] @ A
            self.flops += n * n * (2 * n - 1)
            Ma = M[:, mask] * alpha[mask]
            Mb = M[:, mask] * beta[mask]
            lo = s * M[:, i] + np.minimum(Ma, Mb).sum(1)
            hi = s * M[:, i] + np.maximum(Ma, Mb).sum(1)
            self.flops += n * (n - 1) * 4 + 2 * n * n
            act = lo >= 0.0
            inact = hi <= 0.0
            strad = ~(act | inact)
            if strad.any():
                return k, A, M, strad
            A = act[:, None] * M
            self.flops += n * n
            if not act.any():
                return None, A, None, None   # dead on the whole cell
        return None, A, None, None

    def _forward_from(self, A, k, m):
        h = A @ m
        self.flops += self.n * (2 * self.n - 1)
        for kk in range(k, self.c):
            h = np.maximum(self.Ws[kk] @ h, 0.0)
        self.flops += (self.c - k) * MV
        return h

    def _make(self, i, s, alpha, beta, k0, A, level, pri_in=None):
        """Create a cell; returns its value P f_c(m) (zero vector if P = 0). Open cells go on the heap with priority
        pri_in (surplus rule, set by the caller) or |J val| (value rule)."""
        P, mom = self.mom.cone(i, s, alpha, beta)
        self.n_cells += 1
        if P <= 0.0:
            return np.zeros(self.n)
        m = mom / P
        ks, A2, M, strad = self._test(i, s, alpha, beta, k0, A)
        if ks is None:
            out = A2 @ m
            self.flops += self.n * (2 * self.n - 1)
            self.S_res += P * out
            self.P_res += P
            self.n_res += 1
            return P * out
        out = self._forward_from(A2, ks, m)
        val = P * out
        self.S_open += val
        # split coordinate: largest straddle extent
        mask = np.ones(self.n, dtype=bool)
        mask[i] = False
        score = (np.abs(M[strad]).sum(0)) * (beta - alpha)
        score[i] = -1.0
        j = int(np.argmax(score))
        self._pending = (i, s, alpha, beta, ks, A2, j, val, level)
        return val

    def _push(self, cell, pri):
        i, s, alpha, beta, ks, A2, j, val, level = cell
        if level >= self.max_level:
            pri = 0.0
        self.counter += 1
        heapq.heappush(self.heap, (-pri, self.counter, i, s, alpha, beta, ks, A2, j, val, level))

    # --- driver --------------------------------------------------------------------------------------------------
    def _mag(self, v):
        self.flops += self.n * (2 * self.n - 1) + 2 * self.n
        return float(np.linalg.norm(self.J @ v))

    def start(self):
        n = self.n
        for i in range(n):
            for s in (1.0, -1.0):
                alpha = -np.ones(n)
                beta = np.ones(n)
                alpha[i] = beta[i] = 0.0
                self._pending = None
                val = self._make(i, s, alpha, beta, 0, np.eye(n), 0)
                if self._pending is not None:
                    self._push(self._pending, self._mag(val))

    def refine_one(self):
        if not self.heap:
            return False
        negp, _, i, s, alpha, beta, ks, A, j, val, level = heapq.heappop(self.heap)
        if negp == 0.0:
            heapq.heappush(self.heap, (negp, _, i, s, alpha, beta, ks, A, j, val, level))
            return False
        self.S_open -= val
        mid = 0.5 * (alpha[j] + beta[j])
        b1 = beta.copy()
        b1[j] = mid
        a2 = alpha.copy()
        a2[j] = mid
        self.flops += 64  # heap and bookkeeping (nominal)
        self._pending = None
        v1 = self._make(i, s, alpha, b1, ks, A, level + 1)
        c1 = self._pending
        self._pending = None
        v2 = self._make(i, s, a2, beta, ks, A, level + 1)
        c2 = self._pending
        if self.rule == 'surplus':
            sur = 0.5 * self._mag(val - v1 - v2)
            p1 = max(sur, self.floor * self._mag(v1)) if c1 is not None else 0.0
            p2 = max(sur, self.floor * self._mag(v2)) if c2 is not None else 0.0
        else:
            p1 = self._mag(v1) if c1 is not None else 0.0
            p2 = self._mag(v2) if c2 is not None else 0.0
        if c1 is not None:
            self._push(c1, p1)
        if c2 is not None:
            self._push(c2, p2)
        return True

    def estimate(self):
        return self.S_res + self.S_open

    def cost_mv(self):
        return (self.flops + self.mom.flops) / MV
