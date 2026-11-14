"""Cube-sphere cone code, version 2: certified exact cells for the full 256-layer net.

A cell C (cone over a dyadic box on a face of the cube, see cubesphere.py) is CERTIFIED when
  (i)  the activation pattern of layers 1..c0 is constant on C (exact interval arithmetic in gnomonic coordinates,
       with the cell's linear map kept in factored form A = U V^T once fewer than 8 units are active), and
  (ii) the image A C lies in the tail cone K: a gnomonic box cone at layer c0 around the synchronised direction u* on
       which the pattern of layers c0+1..256 is certified constant (setup, once per net), so f = J A on C.
A certified cell contributes P(C) J A m exactly (m = E[x | C]). Open cells contribute P(C) f(m) (centroid rule; the
tail map is J if f_c0(m) lies in K, else a full forward pass). The tree is refined adaptively.
Costs in FLOPs (flopscope conventions) and mv (1 mv = 128 FLOPs).
"""
import heapq

import numpy as np

from cubesphere import MV, Moments

N = 8


def interval(M, i, s, alpha, beta, mask):
    """Exact range over the gnomonic box of the linear forms M x / |x_i| (rows of M)."""
    Ma = M[:, mask] * alpha[mask]
    Mb = M[:, mask] * beta[mask]
    lo = s * M[:, i] + np.minimum(Ma, Mb).sum(1)
    hi = s * M[:, i] + np.maximum(Ma, Mb).sum(1)
    return lo, hi


class Certifier:
    """Layer-by-layer certification on one cell with the map in factored form A = U Vt (U: n x r, Vt: r x n)."""

    def __init__(self, Ws):
        self.Ws = Ws
        self.flops = 0.0

    def run(self, i, s, alpha, beta, k0, k1, U, Vt):
        """Certify layers k0..k1-1 (0-indexed weights). Returns (k_straddle or None, U, Vt, M, strad, dead)."""
        n = U.shape[0]
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        for k in range(k0, k1):
            r = Vt.shape[0]
            Mf = self.Ws[k] @ U                       # n x r
            M = Mf @ Vt                                # n x n pre-activation forms
            self.flops += n * r * (2 * n - 1) + n * n * (2 * r - 1)
            lo, hi = interval(M, i, s, alpha, beta, mask)
            self.flops += 6 * n * (n - 1) + 2 * n
            act = lo >= 0.0
            inact = hi <= 0.0
            strad = ~(act | inact)
            if strad.any():
                return k, U, Vt, M, strad, False
            na = int(act.sum())
            if na == 0:
                return None, U, Vt, None, None, True
            if na < r:                                   # refactor: A = E_S (Mf[S] Vt)
                S = np.nonzero(act)[0]
                Vt = Mf[S] @ Vt
                self.flops += na * n * (2 * r - 1)
                U = np.zeros((n, na))
                U[S, np.arange(na)] = 1.0
            else:
                U = act[:, None] * Mf
                self.flops += n * r
        return None, U, Vt, None, None, False


def tail_cone(Ws, c0, u, cert, max_halvings=24):
    """Largest gnomonic box (half-width delta = 2^-j around u's chart coordinates) at layer c0 on which layers
    c0+1..L are certified constant. Returns dict(i, s, alpha, beta, J, Lmat, delta, flops) or None."""
    n, L = len(u), len(Ws)
    i = int(np.argmax(np.abs(u)))
    s = 1.0 if u[i] > 0 else -1.0
    g = u / abs(u[i])
    f0 = cert.flops
    for j in range(1, max_halvings + 1):
        d = 2.0 ** -j
        alpha = g - d
        beta = g + d
        alpha[i] = beta[i] = 0.0
        ks, U, Vt, M, strad, dead = cert.run(i, s, alpha, beta, c0, L, np.eye(n), np.eye(n))
        if ks is None and not dead:
            J = U @ Vt
            # containment constraints for h: s h_i > 0, h_j - alpha_j s h_i >= 0, beta_j s h_i - h_j >= 0
            rows = []
            e = np.zeros(n)
            e[i] = s
            rows.append(e)
            for jj in range(n):
                if jj == i:
                    continue
                r1 = np.zeros(n)
                r1[jj] = 1.0
                r1[i] = -alpha[jj] * s
                r2 = np.zeros(n)
                r2[jj] = -1.0
                r2[i] = beta[jj] * s
                rows += [r1, r2]
            return dict(i=i, s=s, alpha=alpha, beta=beta, J=J, Lmat=np.array(rows), delta=d,
                        flops=cert.flops - f0)
    return None


class CS2:
    def __init__(self, Ws, c0=32, Q=64, rule='surplus', floor=0.01, max_level=60):
        self.Ws, self.c0, self.L = Ws, c0, len(Ws)
        self.n = Ws[0].shape[0]
        self.mom = Moments(Q, 9.0, self.n)
        self.cert = Certifier(Ws)
        self.flops = 0.0
        self.rule, self.floor, self.max_level = rule, floor, max_level
        self.heap = []
        self.counter = 0
        self.S_cert = np.zeros(self.n)
        self.S_open = np.zeros(self.n)
        self.P_cert = 0.0
        self.n_cert = self.n_cells = self.n_open_tailmiss = 0
        self.K = None
        self.Jn = np.eye(self.n)

    # -- helpers ----------------------------------------------------------------------------------------------------
    def _fwd(self, h, k0, k1):
        for k in range(k0, k1):
            h = np.maximum(self.Ws[k] @ h, 0.0)
        self.flops += (k1 - k0) * MV
        return h

    def _in_K(self, h):
        K = self.K
        self.flops += 3 * self.n
        if K['s'] * h[K['i']] <= 0:
            return False
        g = h / abs(h[K['i']])
        msk = np.ones(self.n, dtype=bool)
        msk[K['i']] = False
        return bool(np.all(g[msk] >= K['alpha'][msk]) and np.all(g[msk] <= K['beta'][msk]))

    def _tail_value(self, h):
        """f_{c0 -> L}(h): J h if h in K (exact there), else a forward pass."""
        if self.K is not None and self._in_K(h):
            self.flops += self.n * (2 * self.n - 1)
            return self.K['J'] @ h
        if np.all(h == 0):
            return h
        self.n_open_tailmiss += 1
        return self._fwd(h, self.c0, self.L)

    def _mag(self, v):
        self.flops += 2 * self.n
        return float(np.linalg.norm(v))   # values are already in output space

    # -- cells ------------------------------------------------------------------------------------------------------
    def _make(self, i, s, alpha, beta, k0, U, Vt, level):
        """Returns (value in output space, pending open cell or None)."""
        P, mom = self.mom.cone(i, s, alpha, beta)
        self.n_cells += 1
        if P <= 0.0:
            return np.zeros(self.n), None
        m = mom / P
        msk = np.ones(self.n, dtype=bool)
        msk[i] = False
        if k0 < self.c0:
            ks, U, Vt, M, strad, dead = self.cert.run(i, s, alpha, beta, k0, self.c0, U, Vt)
        else:
            ks, M, strad, dead = None, None, None, False
        if dead:
            self.n_cert += 1
            self.P_cert += P
            return np.zeros(self.n), None
        if ks is None:
            # pattern constant through c0: containment of the image in K
            A = U @ Vt
            self.flops += self.n * self.n * (2 * Vt.shape[0] - 1)
            if self.c0 >= self.L:          # no tail: the cell is exact
                val = P * (A @ m)
                self.flops += self.n * (2 * self.n - 1) + self.n
                self.S_cert += val
                self.P_cert += P
                self.n_cert += 1
                return val, None
            if self.K is not None:
                LA = self.K['Lmat'] @ A
                self.flops += LA.shape[0] * self.n * (2 * self.n - 1)
                lo, hi = interval(LA, i, s, alpha, beta, msk)
                self.flops += 6 * LA.shape[0] * (self.n - 1)
                ok = lo >= 0.0
                ok[0] = lo[0] > 0.0
                if ok.all():
                    val = P * (self.K['J'] @ (A @ m))
                    self.flops += 2 * self.n * (2 * self.n - 1) + self.n
                    self.S_cert += val
                    self.P_cert += P
                    self.n_cert += 1
                    return val, None
                # image straddles K's boundary: split along the most-straddled coordinate
                score = np.abs(LA[~ok]).sum(0) * (beta - alpha)
            else:
                score = np.ones(self.n) * (beta - alpha)
            hc = A @ m
            self.flops += self.n * (2 * self.n - 1)
            out = self._tail_value(hc)
            kres = self.c0
            dist = self.floor * float(np.linalg.norm(P * out))
        else:
            score = np.abs(M[strad]).sum(0) * (beta - alpha)
            hk = U @ (Vt @ m)
            self.flops += self.n * (2 * Vt.shape[0] - 1) * 2
            hc = self._fwd(hk, ks, self.c0)
            out = self._tail_value(hc)
            kres = ks
            # forward-propagated within-cell distortion of the centroid's linear map (a priori estimate): for each
            # straddling unit, the pre-activation extent on the side opposite the centroid's gate, times the share of
            # the cell beyond it (uniform-spread approximation), times the cell's gain from layer ks to the output
            lo, hi = interval(M[strad], i, s, alpha, beta, msk)
            zm = M[strad] @ m
            wrong = np.where(zm > 0, -lo, hi)
            span = np.maximum(hi - lo, 1e-300)
            gain = float(np.linalg.norm(out)) / max(float(np.linalg.norm(hk)), 1e-300)
            dist = P * abs(m[i]) * gain * float((wrong * wrong / span).sum())
            self.flops += 6 * int(strad.sum()) * self.n + 40
        val = P * out
        self.S_open += val
        score[i] = -1.0
        j = int(np.argmax(score))
        return val, (i, s, alpha, beta, kres, U, Vt, j, val, level, dist)

    def _push(self, cell, pri):
        if cell[9] >= self.max_level:
            pri = 0.0
        self.counter += 1
        heapq.heappush(self.heap, (-pri, self.counter, cell))

    def setup(self, probe_cells=True):
        """Initial 16 face cells, u* from their estimate's layer-c0 direction, tail cone K."""
        n = self.n
        first = []
        for i in range(n):
            for s in (1.0, -1.0):
                alpha = -np.ones(n)
                beta = np.ones(n)
                alpha[i] = beta[i] = 0.0
                first.append((i, s, alpha, beta))
        # u*: layer-c0 state of the centroid of the face cell with the largest layer-c0 output (deterministic probes)
        best, ustar = -1.0, None
        for (i, s, alpha, beta) in first:
            P, mom = self.mom.cone(i, s, alpha, beta)
            h = self._fwd(mom / P, 0, self.c0)
            nh = float(np.linalg.norm(h))
            if nh > best:
                best, ustar = nh, h / nh
        self.K = tail_cone(self.Ws, self.c0, ustar, self.cert) if self.c0 < self.L else None
        if self.K is not None:
            self.Jn = self.K['J'] / np.linalg.norm(self.K['J'])
        for (i, s, alpha, beta) in first:
            val, cell = self._make(i, s, alpha, beta, 0, np.eye(n), np.eye(n), 0)
            if cell is not None:
                self._push(cell, max(self._mag(val), cell[10]))

    def refine_one(self):
        if not self.heap:
            return False
        negp, cnt, cell = heapq.heappop(self.heap)
        if negp == 0.0:
            heapq.heappush(self.heap, (negp, cnt, cell))
            return False
        i, s, alpha, beta, kres, U, Vt, j, val, level, _ = cell
        self.S_open -= val
        mid = 0.5 * (alpha[j] + beta[j])
        b1 = beta.copy()
        b1[j] = mid
        a2 = alpha.copy()
        a2[j] = mid
        self.flops += 64
        v1, c1 = self._make(i, s, alpha, b1, kres, U, Vt, level + 1)
        v2, c2 = self._make(i, s, a2, beta, kres, U, Vt, level + 1)
        sur = 0.5 * self._mag(val - v1 - v2)
        if self.rule == 'surplus':        # a posteriori: half the change the split made
            p1 = max(sur, self.floor * self._mag(v1)) if c1 is not None else 0.0
            p2 = max(sur, self.floor * self._mag(v2)) if c2 is not None else 0.0
        elif self.rule == 'distortion':   # a priori: forward-propagated within-cell distortion
            p1 = c1[10] if c1 is not None else 0.0
            p2 = c2[10] if c2 is not None else 0.0
        elif self.rule == 'hybrid':
            p1 = max(sur, c1[10]) if c1 is not None else 0.0
            p2 = max(sur, c2[10]) if c2 is not None else 0.0
        else:
            p1 = self._mag(v1) if c1 is not None else 0.0
            p2 = self._mag(v2) if c2 is not None else 0.0
        if c1 is not None:
            self._push(c1, p1)
        if c2 is not None:
            self._push(c2, p2)
        return True

    def estimate(self):
        return self.S_cert + self.S_open

    def cost_mv(self):
        return (self.flops + self.cert.flops + self.mom.flops) / MV
