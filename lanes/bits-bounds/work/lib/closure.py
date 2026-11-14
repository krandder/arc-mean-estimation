"""Exact single-Gaussian recursion (moment-matching Gaussian closure) for bias-free ReLU nets.

State: mean m and covariance S of a Gaussian surrogate N(m, S) of h_{l-1}. Update: z = W y, y ~ N(m, S) gives
z ~ N(mu, C), mu = W m, C = W S W^T; the next state is the exact mean and covariance of relu(z) under that Gaussian
(per-unit and pairwise closed forms below), i.e. moment matching after the exact Gaussian ReLU push-forward.
Input x ~ N(0, I): the first layer is exact. Estimate of E h_L: the final mean.

Closed forms for (X, Y) standard bivariate normal with correlation r, truncation points h = -a, k = -b (a = mu_i/s_i,
b = mu_j/s_j), L = P(X > h, Y > k) = Phi2(a, b; r):
  E[X 1] = phi(h) Q(k*) + r phi(k) Q(h*),   h* = (h - r k)/sqrt(1 - r^2),  k* = (k - r h)/sqrt(1 - r^2),  Q = 1 - Phi,
  E[XY 1] = r L + r h phi(h) Q(k*) + r k phi(k) Q(h*) + sqrt(1 - r^2)/(2 pi) exp(-(h^2 - 2 r h k + k^2)/(2 (1 - r^2))),
  E[relu(s_i X + mu_i) relu(s_j Y + mu_j)] = mu_i mu_j L + mu_i s_j E[Y 1] + mu_j s_i E[X 1] + s_i s_j E[XY 1]
(Tallis 1961 / Rosenbaum 1961; checked against Monte Carlo in tests/test_closure.py). Phi2 by Drezner's arcsine form
with Gauss-Legendre nodes: Phi2(a, b; r) = Phi(a) Phi(b) + (1/2pi) int_0^{arcsin r} exp(-(a^2 + b^2 - 2 a b sin t)/
(2 cos^2 t)) dt.
Cost: O(n^3) per layer for W S W^T plus O(n^2 q) for the pairwise moments (q quadrature nodes).
"""
import math
import numpy as np
from scipy.special import ndtr

_GL = {}


def _gl(q):
    if q not in _GL:
        _GL[q] = np.polynomial.legendre.leggauss(q)
    return _GL[q]


def phi(x):
    return np.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def phi2(a, b, r, q=48):
    """Phi2(a, b; r) = P(X < a, Y < b) for standard bivariate normal with correlation r (arrays broadcast)."""
    a, b, r = np.broadcast_arrays(np.asarray(a, float), np.asarray(b, float), np.asarray(r, float))
    r = np.clip(r, -1 + 1e-12, 1 - 1e-12)
    T = np.arcsin(r)
    x, w = _gl(q)
    out = ndtr(a) * ndtr(b)
    acc = np.zeros_like(out)
    for xi, wi in zip(x, w):
        t = 0.5 * T * (xi + 1.0)
        st, ct2 = np.sin(t), np.cos(t) ** 2
        acc += wi * np.exp(-(a * a + b * b - 2 * a * b * st) / (2 * ct2))
    return out + acc * 0.5 * T / (2 * math.pi)


def relu_moments(mu, C, q=48):
    """Exact mean and covariance of relu(z), z ~ N(mu, C)."""
    s = np.sqrt(np.maximum(np.diag(C), 1e-300))
    a = mu / s
    m1 = mu * ndtr(a) + s * phi(a)
    e2 = (mu * mu + s * s) * ndtr(a) + mu * s * phi(a)
    R = C / np.outer(s, s)
    np.fill_diagonal(R, 1.0)
    R = np.clip(R, -1 + 1e-12, 1 - 1e-12)
    A = a[:, None] * np.ones_like(R)
    B = a[None, :] * np.ones_like(R)
    h, k = -A, -B
    sq = np.sqrt(1 - R * R)
    Lm = phi2(A, B, R, q)
    hs = (h - R * k) / sq
    ks = (k - R * h) / sq
    EX = phi(h) * ndtr(-ks) + R * phi(k) * ndtr(-hs)
    EY = phi(k) * ndtr(-hs) + R * phi(h) * ndtr(-ks)
    EXY = R * Lm + R * h * phi(h) * ndtr(-ks) + R * k * phi(k) * ndtr(-hs) + \
        sq / (2 * math.pi) * np.exp(-(h * h - 2 * R * h * k + k * k) / (2 * (1 - R * R)))
    MU = mu[:, None] * np.ones_like(R)
    MV = mu[None, :] * np.ones_like(R)
    SU = s[:, None] * np.ones_like(R)
    SV = s[None, :] * np.ones_like(R)
    E2 = MU * MV * Lm + MU * SV * EY + MV * SU * EX + SU * SV * EXY
    np.fill_diagonal(E2, e2)
    cov = E2 - np.outer(m1, m1)
    cov = 0.5 * (cov + cov.T)
    return m1, cov


def gaussian_recursion(W, q=48):
    """Single-Gaussian recursion for x ~ N(0, I): returns the estimate of E h_L."""
    n = W[0].shape[0]
    m = np.zeros(n)
    S = np.eye(n)
    for Wl in W:
        mu = Wl @ m
        C = Wl @ S @ Wl.T
        m, S = relu_moments(mu, C, q)
    return m
