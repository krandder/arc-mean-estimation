"""Checks for lib/ndx.py. Run with the arc-noisy venv (has torch for the nd.py comparison)."""
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/lib')
sys.path.insert(0, '/home/agent/workspaces/mats/work/narrow-deep/lib')
import ndx  # noqa: E402


def test_weights_match_nd():
    import nd
    for seed in [103, 203, 223]:
        W, _ = nd.make_weights('plain', seed, 8, 256)
        W2 = ndx.make_weights(seed)
        assert len(W) == len(W2) == 256
        for a, b in zip(W, W2):
            assert np.array_equal(a.numpy(), b)


def test_patterns_and_forward_agree():
    Ws = ndx.make_weights(111)
    X = np.random.default_rng(0).standard_normal((1000, 8))
    h1 = ndx.fwd(Ws, X, 0, 40)
    h2, pat = ndx.fwd_patterns(Ws, X, 0, 40)
    assert np.allclose(h1, h2, rtol=0, atol=0)
    # linear map from patterns reproduces the state exactly
    i = 7
    A = np.eye(8)
    for k in range(40):
        D = np.unpackbits(np.array([pat[i, k]], dtype=np.uint8), bitorder='little').astype(float)
        A = (D[:, None] * Ws[k]) @ A
    assert np.allclose(A @ X[i], h1[i], rtol=1e-12, atol=1e-300)


def test_hash_distinguishes():
    p = np.zeros((3, 5), dtype=np.uint8)
    p[1, 4] = 1
    p[2, 0] = 1
    h = ndx.hash2(p)
    assert len({tuple(r) for r in h.tolist()}) == 3


if __name__ == '__main__':
    for name, f in list(globals().items()):
        if name.startswith('test_'):
            f()
            print('ok', name)
