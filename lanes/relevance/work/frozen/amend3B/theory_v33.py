"""Theory v3.3: quenched gain-ratio correction of the v2 mean degree and linear share (input regime, sigma = 0).
FORMAL.md v3.3. HEURISTIC. Frozen with PREREG Amendment 3B before any of its nets is run.

At sigma = 0 the net is positively homogeneous, so the measured mean degree is exactly
    D = J(1)/V = R (tr Sigma/E|X|^2) / (V/E|a|^2),   R = (J(1)/tr Sigma) / (E|a|^2/E|X|^2),
and the v2.3 identity sets R = 1 (annealed). Forward-only estimate (no Jacobians): per future layer the transverse
block of W_k is independent of the gate pattern (Theorem 1), so the Frobenius gain on directions transverse to the
path is about 2 a_k (a_k = active fraction on the path) while the path direction gains the radial factor; hence
    R_perp = E_x[prod_k 2 a_k(x)] / (E|a|^2 / E|X|^2),   R_q = r + (1 - r) R_perp,   r = radial_var / tr Sigma,
    D_q = D_v2 R_q,   s1_q = s1_dir / sqrt(R_perp) + s1_amp + s1_rad
(the last from s_1 = D^{-1/2} in the small-angle model, applied to the direction channel only)."""
import math
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import rel  # noqa: E402
import theory_v2 as t2  # noqa: E402


def r_perp(Ws, l, P, rng):
    """Forward-only transverse/radial gain ratio of the future of layer l (Ws = [W_1..W_L], input x ~ N(0, I))."""
    X, _ = rel.input_cloud(Ws, l, P, rng)
    h = X
    logt = np.zeros(P)
    for W in Ws[l:]:
        z = h @ W.T
        logt += np.log(2.0 * (z > 0).mean(1))
        h = np.maximum(z, 0.0)
    rad = (h ** 2).sum(1).mean() / (X ** 2).sum(1).mean()
    return float(np.exp(logt).mean() / rad)


def predict_quenched(o, Rp):
    """v3.3 predictions for one cell record o (runs/eval_*.json) given R_perp."""
    pl = t2.predict_layer(o)
    r = o['radial_var'] / o['trSigma']
    Rq = r + (1 - r) * Rp
    sp = pl['s1_split']
    return dict(R_perp=Rp, R_q=Rq, D_q=pl['D'] * Rq, s1_q=sp['dir'] / math.sqrt(Rp) + sp['amp'] + sp['rad'],
                D_v2=pl['D'], s1_v2=pl['s1'])


def measured_R(o):
    """The exact per-net factor defined by the measured quantities (diagnostic)."""
    return (o['J1_gauss'][0] / o['trSigma']) / (o['Ea2_true'] / (o['trSigma'] + o['m2']))
