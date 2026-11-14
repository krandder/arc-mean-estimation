"""Tests for lib/closure.py: bivariate normal CDF, exact ReLU moments of a Gaussian vector against Monte Carlo, and the
first layer of the recursion (exact for Gaussian input). Run: python tests/test_closure.py"""
import os
import sys
import math
import numpy as np
from scipy.stats import multivariate_normal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import closure
import bb


def test_phi2():
    rng = np.random.default_rng(0)
    for _ in range(20):
        a, b = rng.normal(size=2) * 1.5
        r = rng.uniform(-0.98, 0.98)
        ref = multivariate_normal(mean=[0, 0], cov=[[1, r], [r, 1]]).cdf([a, b])
        got = closure.phi2(a, b, r)
        assert abs(ref - got) < 2e-6, (a, b, r, ref, got)


def test_relu_moments_mc():
    rng = np.random.default_rng(1)
    n = 5
    mu = rng.normal(size=n)
    A = rng.normal(size=(n, n))
    C = A @ A.T / n + 0.2 * np.eye(n)
    m1, cov = closure.relu_moments(mu, C)
    N = 2_000_000
    Z = rng.multivariate_normal(mu, C, size=N)
    R = np.maximum(Z, 0)
    m_mc = R.mean(axis=0)
    c_mc = np.cov(R.T)
    assert np.max(np.abs(m1 - m_mc)) < 4e-3, (m1, m_mc)
    assert np.max(np.abs(cov - c_mc)) < 6e-3, (cov, c_mc)


def test_first_layer_exact():
    W = bb.make_weights(5, 16, 1)
    m = closure.gaussian_recursion(W)
    exact = np.linalg.norm(W[0], axis=1) / math.sqrt(2 * math.pi)
    assert np.allclose(m, exact, rtol=1e-9, atol=1e-12)


if __name__ == '__main__':
    for name, f in list(globals().items()):
        if name.startswith('test_') and callable(f):
            f()
            print('PASS', name, flush=True)
