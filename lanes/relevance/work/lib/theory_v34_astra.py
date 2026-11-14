"""Theory v3.4 [A]: gpt-6-astra's round-3 refinements (coprover/astra_r3_answer.md), implemented by C from that text.
Input regime, sigma = 0. Frozen with PREREG Amendment 3C before any output of nets 4006-4009 is read.

(1) Forward-conditional gain ratio (PROVEN UNDER conditioning on one forward trajectory; its use per net HEURISTIC).
    Along each trajectory h_0 = X, h_j = relu(W_j h_{j-1}): q_j = |h_j|^2, a_j = q_j/q_{j-1}, k_j = active count;
    u_j = 2 (k_j - 1)/(n a_j), v_j = 2/(n a_j), T_0 = 1, T_j = prod_{i<=j} u_i, H_t = T_t + sum_j v_j T_{j-1};
    r(X) = X^T Sigma X/|X|^2; J_hat = E_X[(q_t/q_0) (r(X) + (tr Sigma - r(X)) H_t)];
    Gamma_hat = q J_hat/(tr Sigma q_a), q = E|X|^2, q_a = E q_t; D_A = Gamma_hat D_v2.
    X ~ N(m, Sigma) with (m, Sigma) fitted on 16,384 forward pilot inputs (layer 0: N(0, I)); 4,096 trajectories.
(2) Radial channel at degree one (PROVEN: the input radius has zero first chaos; the network use HEURISTIC):
    b_corr = b_v2 - radvar/q + Var|X|/q,
    s1_A = (b_v2 (s1_dir + s1_amp) + |E[|X| Z]|^2/q)/b_corr,  E[|X| Z] = Sigma^{1/2} E[X/|X|],  X = m + Sigma^{1/2} Z.
Also returned: the simple variant Gamma_simple = (q/q_a) prod_j (2 E_X k_j/n)."""
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import rel  # noqa: E402
import theory_v2 as t2  # noqa: E402


def astra_stats(Ws, l, rng, P_pilot=16384, P=4096):
    n = Ws[0].shape[1]
    if l == 0:
        m = np.zeros(n)
        C = np.eye(n)
    else:
        H, _ = rel.input_cloud(Ws, l, P_pilot, rng)
        m = H.mean(0)
        C = np.cov(H, rowvar=False)
    ev, U = np.linalg.eigh(C)
    ev = np.clip(ev, 0.0, None)
    S12 = (U * np.sqrt(ev)) @ U.T
    Z = rng.standard_normal((P, n))
    X = m + Z @ S12
    trS = float(np.trace(C))
    q0 = (X ** 2).sum(1)
    rX = np.einsum('pi,ij,pj->p', X, C, X) / q0
    h = X
    qprev = q0
    T = np.ones(P)
    Hs = np.zeros(P)
    kmean = []
    for W in Ws[l:]:
        z = h @ W.T
        k = (z > 0).sum(1)
        h = np.maximum(z, 0.0)
        qj = (h ** 2).sum(1)
        aj = qj / qprev
        v = 2.0 / (n * aj)
        Hs += v * T
        T = T * 2.0 * (k - 1) / (n * aj)
        qprev = qj
        kmean.append(k.mean())
    Ht = T + Hs
    qt = qprev
    Jhat = float(np.mean(qt / q0 * (rX + (trS - rX) * Ht)))
    q = float(q0.mean())
    qa = float(qt.mean())
    gamma = q * Jhat / (trS * qa)
    gamma_simple = q / qa * float(np.prod(2.0 * np.array(kmean) / n))
    normX = np.sqrt(q0)
    varR = float(normX.var())
    EXZ = S12 @ (X / normX[:, None]).mean(0)
    return dict(gamma=gamma, gamma_simple=gamma_simple, q=q, trS=trS, varR_rel=varR / q,
                radial1_rel=float(EXZ @ EXZ) / q)


def predict_astra(o, st):
    pl = t2.predict_layer(o)
    sp = pl['s1_split']
    b = pl['V_rel']
    q = o['trSigma'] + o['m2']
    b_corr = b - o['radial_var'] / q + st['varR_rel']
    s1A = (b * (sp['dir'] + sp['amp']) + st['radial1_rel']) / b_corr
    return dict(D_A=pl['D'] * st['gamma'], s1_A=s1A, gamma=st['gamma'], gamma_simple=st['gamma_simple'],
                b_corr=b_corr)
