"""Gaussian-mixture mixture of linear experts (main's step-4 proposal, 2 Nov ~16:35Z), propagated as a population.

Per layer l: a K-component GMM on the joint low-rank coordinates (u, v) = (P_l^T (h_l - c_l), P_{l+1}^T (h_{l+1} - c_{l+1}))
of sampled pairs (EM, full covariances). Its conditional p(v | u) is a mixture of linear experts: gates
P(k | u) proportional to pi_k N(u; mu_u,k, S_uu,k) (input fit), affine maps v = B_k u + b_k with residual covariance
R_k = S_vv,k - S_vu,k S_uu,k^-1 S_uv,k (output fit / confidence).
Population propagation: a Gaussian mixture sum_j w_j N(m_j, S_j) in u-coordinates is pushed through every expert in
closed form: the gate is applied as a Gaussian factor, so component j sends mass
w_j pi_k N(m_j; mu_u,k, S_j + S_uu,k) / sum_k' (same) to expert k, with the product Gaussian
N(m_jk, S_jk), S_jk = (S_j^-1 + S_uu,k^-1)^-1, m_jk = S_jk (S_j^-1 m_j + S_uu,k^-1 mu_u,k); expert k maps it to
N(B_k m_jk + b_k, B_k S_jk B_k^T + R_k). The J x K pieces are reduced to K components by moment matching onto the
experts (all pieces through expert k merged). The output mean is sum mass x (c_L + P_L mean).
"""
import numpy as np
from sklearn.mixture import GaussianMixture


def logN(x, m, S):
    """log N(x; m, S) for a single vector x."""
    d = len(m)
    L = np.linalg.cholesky(S)
    z = np.linalg.solve(L, x - m)
    return -0.5 * (z @ z) - np.log(np.diag(L)).sum() - 0.5 * d * np.log(2 * np.pi)


class LayerMoE:
    def __init__(self, K, reg=1e-6, seed=0, max_iter=200):
        self.K, self.reg, self.seed, self.max_iter = K, reg, seed, max_iter

    def fit(self, U, V):
        du = U.shape[1]
        J = np.concatenate([U, V], 1)
        gm = GaussianMixture(n_components=self.K, covariance_type='full', reg_covar=self.reg,
                             random_state=self.seed, max_iter=self.max_iter, init_params='kmeans').fit(J)
        self.gm = gm
        self.du = du
        self.pi = gm.weights_
        self.mu_u = gm.means_[:, :du]; self.mu_v = gm.means_[:, du:]
        C = gm.covariances_
        self.Suu = C[:, :du, :du]; self.Suv = C[:, :du, du:]; self.Svv = C[:, du:, du:]
        self.B = np.stack([np.linalg.solve(self.Suu[k], self.Suv[k]).T for k in range(self.K)])     # (K, dv, du)
        self.b = self.mu_v - np.einsum('kvu,ku->kv', self.B, self.mu_u)
        self.R = np.stack([self.Svv[k] - self.Suv[k].T @ np.linalg.solve(self.Suu[k], self.Suv[k]) for k in range(self.K)])
        return self

    def heldout_loglik(self, U, V):
        return float(self.gm.score(np.concatenate([U, V], 1)))

    def predict_mean(self, U):
        """Conditional mean E[v | u] with normalised Gaussian gates (pointwise use)."""
        lg = np.stack([np.log(self.pi[k]) + self._logN_rows(U, self.mu_u[k], self.Suu[k]) for k in range(self.K)], 1)
        lg -= lg.max(1, keepdims=True)
        g = np.exp(lg); g /= g.sum(1, keepdims=True)
        preds = np.einsum('kvu,nu->nkv', self.B, U) + self.b[None]
        return (g[:, :, None] * preds).sum(1)

    @staticmethod
    def _logN_rows(X, m, S):
        L = np.linalg.cholesky(S)
        Z = np.linalg.solve(L, (X - m).T)
        return -0.5 * (Z * Z).sum(0) - np.log(np.diag(L)).sum() - 0.5 * len(m) * np.log(2 * np.pi)

    def push(self, w, M, S, rule='ratio'):
        """Push a population mixture (w (J,), M (J, du), S (J, du, du)) through the experts; return K components
        (w', M' (K, dv), S' (K, dv, dv)) by moment matching per expert.
        rule 'ratio' (default): the normalised gate P(k|u) = pi_k N_k(u) / p(u) is approximated by
        pi_k N(u; mu_k, S_k) / N(u; mu_a, S_a) with (mu_a, S_a) the moments of the GMM's u-marginal: a Gaussian factor
        of precision S_k^-1 - S_a^-1 (negative eigenvalues clipped) that is flat when K = 1 (exact limit).
        rule 'product': the gate is the unnormalised Gaussian pi_k N(u; mu_k, S_k) (double counts the density of u;
        kept as a comparison). Masses are normalised over experts per population component."""
        K, J = self.K, len(w)
        dv = self.mu_v.shape[1]; du = self.du
        mu_a = (self.pi[:, None] * self.mu_u).sum(0)
        dm = self.mu_u - mu_a
        S_a = (self.pi[:, None, None] * (self.Suu + np.einsum('ki,kj->kij', dm, dm))).sum(0)
        Sa_inv = np.linalg.inv(S_a)
        gates = []
        for k in range(K):
            Sk_inv = np.linalg.inv(self.Suu[k])
            if rule == 'ratio':
                Lam = Sk_inv - Sa_inv
                ev, U = np.linalg.eigh(0.5 * (Lam + Lam.T))
                Lam = (U * np.clip(ev, 0, None)) @ U.T
                eta = Sk_inv @ self.mu_u[k] - Sa_inv @ mu_a
                kap = (np.log(self.pi[k]) - 0.5 * np.linalg.slogdet(self.Suu[k])[1] - 0.5 * self.mu_u[k] @ Sk_inv @ self.mu_u[k]
                       + 0.5 * np.linalg.slogdet(S_a)[1] + 0.5 * mu_a @ Sa_inv @ mu_a)
            else:
                Lam = Sk_inv
                eta = Sk_inv @ self.mu_u[k]
                kap = np.log(self.pi[k]) - 0.5 * np.linalg.slogdet(self.Suu[k])[1] - 0.5 * self.mu_u[k] @ Sk_inv @ self.mu_u[k] \
                    - 0.5 * du * np.log(2 * np.pi)
            gates.append((Lam, eta, kap))
        logm = np.full((J, K), -np.inf)
        Mjk = np.zeros((J, K, du)); Sjk = np.zeros((J, K, du, du))
        for j in range(J):
            Sj_inv = np.linalg.inv(S[j])
            a0 = Sj_inv @ M[j]
            for k, (Lam, eta, kap) in enumerate(gates):
                Pinv = Sj_inv + Lam
                P = np.linalg.inv(Pinv); P = 0.5 * (P + P.T)
                a = a0 + eta
                Sjk[j, k] = P
                Mjk[j, k] = P @ a
                # log of E_{N(m_j, S_j)}[exp(-u^T Lam u / 2 + eta^T u)] + kap
                logm[j, k] = (kap - 0.5 * np.linalg.slogdet(np.eye(du) + S[j] @ Lam)[1]
                              + 0.5 * a @ P @ a - 0.5 * M[j] @ a0)
        logm -= logm.max(1, keepdims=True)
        frac = np.exp(logm); frac /= frac.sum(1, keepdims=True)
        mass = w[:, None] * frac                                       # (J, K)
        Wn = mass.sum(0)
        Mn = np.zeros((K, dv)); Sn = np.zeros((K, dv, dv))
        for k in range(K):
            if Wn[k] <= 0:
                Sn[k] = np.eye(dv); Mn[k] = self.mu_v[k]; continue
            means = np.einsum('vu,ju->jv', self.B[k], Mjk[:, k]) + self.b[k]
            covs = np.einsum('vu,juw,xw->jvx', self.B[k], Sjk[:, k], self.B[k]) + self.R[k][None]
            a = mass[:, k] / Wn[k]
            mk = (a[:, None] * means).sum(0)
            dmm = means - mk
            Sn[k] = (a[:, None, None] * (covs + np.einsum('jv,jx->jvx', dmm, dmm))).sum(0)
            Mn[k] = mk
        return Wn, Mn, Sn
