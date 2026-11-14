"""POST HOC rank guard for the D1 projection (lib/fa_kprop.py is frozen and unchanged; this wraps it).

Why the registered k = n/2 runs (and n = 512's k = n/4) returned NaN: ARC's K = 3 'simple' state covariance S = K[2]
becomes indefinite after a few layers (at n = 128, seed 304: 5 non-positive eigenvalues of 128 at layer 4, 36 at
layer 13), so A^T S A for a wide feature block acquires non-positive eigenvalues and the frozen whitening divides by
sqrt(1e-300), overflowing Pi = S A A^T (diagnosed in /tmp/fa_r2/diag_nan.py, 15:55Z).
The guard keeps only the S-positive part of the kept span: whiten() drops eigen-directions of A^T S A below
tol * max (tol = 1e-10), and the future features drop eigen-directions of S^{1/2} R S^{1/2} below tol * max, so the
projector is Pi = S A A^T on the S-positive, R-relevant part of span(A) (k_eff <= k columns; recorded). When nothing
is dropped the projector equals the frozen one (Pi is invariant to rotations of A's columns), so successful runs are
reproduced up to rounding (checked by rerunning registered successes)."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fa  # noqa: E402
import fa_kprop as FK  # noqa: E402

TOL = 1e-10
STATS = dict(whiten_calls=0, whiten_dropped=[], feat_dropped=[])


def whiten_guard(A, S):
    if A.shape[1] == 0:
        return A
    Ca = A.T @ S @ A
    ev, U = np.linalg.eigh(0.5 * (Ca + Ca.T))
    keep = ev > TOL * max(ev.max(), 1e-300)
    STATS['whiten_calls'] += 1; STATS['whiten_dropped'].append(int((~keep).sum()))
    Uk = U[:, keep]
    return A @ (Uk / np.sqrt(ev[keep])[None, :]) @ Uk.T


_features_frozen = fa.features


def features_guard(kind, k, S, R=None, seed=0):
    if kind not in ('fut', 'futnl'):
        return _features_frozen(kind, k, S, R, seed)
    U, ev = fa.psd_sqrt(S)
    Sh = (U * np.sqrt(ev)) @ U.T
    M = Sh @ R @ Sh
    Uw, lw = fa.psd_sqrt(M)
    w = Uw[:, ::-1][:, :k]; lam = lw[::-1][:k]
    ok = lam > TOL * max(lam[0], 1e-300)
    STATS['feat_dropped'].append(int((~ok).sum()))
    w, lam = w[:, ok], lam[ok]
    A = R @ Sh @ w / lam[None, :]
    var = np.einsum('ik,ij,jk->k', A, S, A)
    good = var > TOL * max(var.max(), 1e-300)
    A = A[:, good]; var = var[good]
    return A / np.sqrt(var)[None, :]


def arc_k3_proj_guard(*a, **kw):
    """The frozen arc_k3_proj with whiten and the future features guarded; returns its dict plus the guard stats."""
    STATS['whiten_calls'] = 0; STATS['whiten_dropped'] = []; STATS['feat_dropped'] = []
    w0, f0 = FK.whiten, fa.features
    FK.whiten, fa.features = whiten_guard, features_guard
    try:
        r = FK.arc_k3_proj(*a, **kw)
    finally:
        FK.whiten, fa.features = w0, f0
    r['guard'] = dict(whiten_max_dropped=max(STATS['whiten_dropped'], default=0),
                      whiten_layers_dropping=sum(1 for x in STATS['whiten_dropped'] if x > 0),
                      feat_max_dropped=max(STATS['feat_dropped'], default=0))
    return r
