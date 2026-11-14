"""Layered mixture of linear experts (LMLE), implemented against SPEC-learned-experts.md v1 + amendment A1 (main,
2 Nov ~17:00Z): projection-only state (d = 32 coordinates per layer, the remainder carried as noise inside the
residual covariances), Monte Carlo gate moments inside each component (256 common draws, no net evaluations),
generalised product-of-experts fusion, skip routes s in {1, 2, 4, 8} fused with learned route weights, component
split (two largest overlaps > 0.2) and merge (moment matching above K_pop), a separate mean-uncertainty per component.
Torch float64, differentiable end to end.

Coordinates: u_l = Pi_l^T (h_l - c_l). Pi_l (l < L): top-d eigenvectors of E[g g^T], g = J_l^T v (vector-Jacobian
products of the output with random v): the directions the downstream net reads. Pi_L: top-d principal axes of h_L.
c_0 = 0, c_l = training mean. Expert e of bank (l, s): gate pi_e N(u_l; mu_e, C_e) normalised over the bank;
map A_e u + b_e with A_e = B + U_e V_e^T (shared base, rank r); residual covariance R_e (full in d dims).
"""
import math
import numpy as np
import torch
from sklearn.mixture import GaussianMixture

DT = torch.float64


def chol_inv_spd(M, jitter=1e-9):
    d = M.shape[-1]
    return torch.cholesky_inverse(torch.linalg.cholesky(M + jitter * torch.eye(d, dtype=M.dtype)))


def std_draws(R, d, seed):
    """Common random numbers with exactly zero mean and identity covariance (so K = 1 moments are exact)."""
    g = np.random.RandomState(seed)
    E = g.standard_normal((R, d))
    E -= E.mean(0)
    C = E.T @ E / R
    E = E @ np.linalg.inv(np.linalg.cholesky(C)).T
    return torch.as_tensor(E, dtype=DT)


def fuse_tempered(beta, Ri, mu, ratio=10.0, active=1e-3):
    """Tempered product of experts (Kelvin via main ~18:40Z). Per coordinate i, the normalising (1/sum beta) tempering
    is applied only across the experts whose precision on i is within `ratio` of the largest among active experts
    (beta > active); the other experts keep weight beta (plain gated PoE). Weights enter symmetrically:
    Lambda = sum_k D_k^1/2 Ri_k D_k^1/2, eta = sum_k D_k^1/2 Ri_k D_k^1/2 mu_k, D_k = diag(w_k).
    beta (N, K), Ri (K, dv, dv), mu (N, K, dv) -> (eta, Lambda, Wsym (N, K, dv, dv))."""
    pd = torch.diagonal(Ri, dim1=-2, dim2=-1)                                    # (K, dv)
    act = (beta > active).to(Ri.dtype)                                           # (N, K)
    pdn = pd[None] * act[..., None]                                              # (N, K, dv)
    mx = pdn.max(1, keepdim=True).values
    comp = (pdn >= mx / ratio).to(Ri.dtype) * act[..., None]                     # comparable set C_{n,i}
    Bsum = (beta[..., None] * comp).sum(1, keepdim=True)                         # (N, 1, dv)
    w = torch.where(comp > 0, beta[..., None] / Bsum.clamp_min(1e-300), beta[..., None])
    sw = torch.sqrt(w)                                                           # (N, K, dv)
    Wsym = sw[..., :, None] * Ri[None] * sw[..., None, :]                        # (N, K, dv, dv)
    Lam = Wsym.sum(1)
    eta = torch.einsum('nkij,nkj->ni', Wsym, mu)
    return eta, Lam, Wsym


class Bank(torch.nn.Module):
    """K experts from layer l (dim du) to layer l+s (dim dv)."""

    def __init__(self, du, dv, K, r):
        super().__init__()
        self.du, self.dv, self.K, self.r = du, dv, K, min(r, du, dv)
        z = lambda *s: torch.nn.Parameter(torch.zeros(*s, dtype=DT))
        self.logpi = z(K); self.mu = z(K, du)
        self.Lg = torch.nn.Parameter(torch.eye(du, dtype=DT).repeat(K, 1, 1))     # gate precision = Lg Lg^T
        self.B = z(dv, du); self.U = z(K, dv, self.r); self.V = z(K, du, self.r); self.b = z(K, dv)
        self.Lr = torch.nn.Parameter(torch.eye(dv, dtype=DT).repeat(K, 1, 1) * 0.1)  # R = Lr Lr^T
        self.R_err = None                                                            # held-out residual cov (A2)
        # plain-PoE confidences: diagonal, input-dependent, learned through the fused calibration loss:
        # precision_k,i(u) = exp(-logsig_k,i) * beta_k(u) ** cgate_k,i   (beta = normalised gate weight)
        self.logsig = torch.nn.Parameter(torch.zeros(K, dv, dtype=DT))
        self.cgate = torch.nn.Parameter(torch.ones(K, dv, dtype=DT))

    def init_em(self, U_l, U_t, seed=0, max_iter=100, reg=1e-6):
        """Warm start from a K-component joint GMM on (u_l, u_{l+s}) (per-sample EM)."""
        du = self.du
        gm = GaussianMixture(n_components=self.K, covariance_type='full', reg_covar=reg, random_state=seed,
                             max_iter=max_iter, init_params='kmeans').fit(np.concatenate([U_l, U_t], 1))
        C = gm.covariances_
        Suu, Suv, Svv = C[:, :du, :du], C[:, :du, du:], C[:, du:, du:]
        Bk = np.stack([np.linalg.solve(Suu[k], Suv[k]).T for k in range(self.K)])
        bk = gm.means_[:, du:] - np.einsum('kvu,ku->kv', Bk, gm.means_[:, :du])
        Rk = np.stack([Svv[k] - Suv[k].T @ np.linalg.solve(Suu[k], Suv[k]) for k in range(self.K)])
        base = (gm.weights_[:, None, None] * Bk).sum(0)
        Us, Vs = [], []
        for k in range(self.K):
            u_, s_, vt_ = np.linalg.svd(Bk[k] - base)
            Us.append(u_[:, :self.r] * s_[:self.r]); Vs.append(vt_[:self.r].T)
        with torch.no_grad():
            self.logpi.copy_(torch.as_tensor(np.log(np.maximum(gm.weights_, 1e-12))))
            self.mu.copy_(torch.as_tensor(gm.means_[:, :du]))
            self.Lg.copy_(torch.as_tensor(np.stack([np.linalg.cholesky(np.linalg.inv(Suu[k])) for k in range(self.K)])))
            self.B.copy_(torch.as_tensor(base)); self.U.copy_(torch.as_tensor(np.stack(Us)))
            self.V.copy_(torch.as_tensor(np.stack(Vs))); self.b.copy_(torch.as_tensor(bk))
            self.Lr.copy_(torch.as_tensor(np.stack([np.linalg.cholesky(Rk[k] + 1e-9 * np.eye(self.dv)) for k in range(self.K)])))
            self.logsig.copy_(torch.as_tensor(np.log(np.maximum(np.stack([np.diag(Rk[k]) for k in range(self.K)]), 1e-8))))
        self.em_iter = int(gm.n_iter_)
        return self

    def init_em_torch(self, U_l, U_t, seed=0, iters=60, kmeans_iters=15, reg=1e-5, chunk=1 << 16):
        """Same warm start as init_em (joint full-covariance GMM on (u_l, u_{l+s})), fitted by a chunked torch EM on
        the default device in float32 (accumulators float64), for 1M+ advice paths and K up to 4,096.
        Init: K random data points, then Lloyd k-means; reg is added to every covariance diagonal."""
        dev = torch.get_default_device() if hasattr(torch, 'get_default_device') else torch.device('cpu')
        X = torch.as_tensor(np.concatenate([U_l, U_t], 1), dtype=torch.float32, device=dev)
        N, D = X.shape; K = self.K
        g = torch.Generator(device='cpu').manual_seed(seed)
        mu = X[torch.randperm(N, generator=g, device="cpu")[:K].to(dev)].clone()
        for _ in range(kmeans_iters):                                                  # Lloyd k-means
            S1 = torch.zeros(K, D, dtype=torch.float64, device=dev); cnt = torch.zeros(K, dtype=torch.float64, device=dev)
            for i0 in range(0, N, chunk):
                x = X[i0:i0 + chunk]
                a = torch.cdist(x, mu).argmin(1)
                S1.index_add_(0, a, x.double()); cnt.index_add_(0, a, torch.ones_like(a, dtype=torch.float64))
            ok = cnt > 0
            mu[ok] = (S1[ok] / cnt[ok, None]).float()
        logw = torch.full((K,), -math.log(K), dtype=torch.float32, device=dev)
        Sig = torch.eye(D, device=dev).repeat(K, 1, 1) * float(X.var(0).mean()) / max(K, 1) ** (2.0 / D)
        I = torch.eye(D, device=dev)
        gcov = torch.cov(X[:min(N, 1 << 18)].double().T); gvar = float(torch.diagonal(gcov).mean())
        gcov = gcov + 1e-4 * gvar * torch.eye(D, dtype=torch.float64, device=dev)
        for it in range(iters):
            Sd = (Sig + reg * I).double()                                              # float64 Cholesky with jitter
            Lc, info = torch.linalg.cholesky_ex(Sd)
            if bool((info > 0).any()):
                Lc = torch.linalg.cholesky(Sd + 1e-3 * torch.diagonal(Sd, dim1=-2, dim2=-1).mean(-1)[:, None, None] * I.double() + 1e-6 * I.double())
            Lc = Lc.float()
            Linv = torch.linalg.solve_triangular(Lc.double(), I.double().expand(K, D, D), upper=False).float()
            half_logdet = torch.log(torch.diagonal(Lc, dim1=-2, dim2=-1)).sum(-1)
            Nk = torch.zeros(K, dtype=torch.float64, device=dev)
            S1 = torch.zeros(K, D, dtype=torch.float64, device=dev)
            S2 = torch.zeros(K, D, D, dtype=torch.float64, device=dev)
            for i0 in range(0, N, chunk):
                x = X[i0:i0 + chunk]                                                    # (n, D)
                lp = torch.empty(x.shape[0], K, device=dev)
                for k0 in range(0, K, 64):
                    k1 = min(K, k0 + 64)
                    z = torch.einsum('kij,nkj->nki', Linv[k0:k1], x[:, None, :] - mu[None, k0:k1])  # (n, kc, D)
                    lp[:, k0:k1] = -0.5 * (z * z).sum(-1) - half_logdet[k0:k1] + logw[k0:k1]
                r = torch.softmax(lp, 1)                                                # (n, K)
                Nk += r.sum(0).double()
                S1 += (r.T @ x).double()
                for k0 in range(0, K, 64):
                    k1 = min(K, k0 + 64)
                    S2[k0:k1] += torch.einsum('nk,ni,nj->kij', r[:, k0:k1], x, x).double()
            Nk_ = Nk.clamp_min(1e-6)
            m64 = S1 / Nk_[:, None]
            C64 = S2 / Nk_[:, None, None] - m64[:, :, None] * m64[:, None, :]
            C64 = 0.5 * (C64 + C64.transpose(1, 2))
            C64 = torch.nan_to_num(C64)
            ev, Ve = torch.linalg.eigh(C64)                       # clip eigenvalues: ReLU states give exact zeros
            ev = ev.clamp_min(1e-4 * gvar)
            C64 = (Ve * ev[:, None, :]) @ Ve.transpose(1, 2)
            thin = Nk < D + 1                                     # starved components: global covariance, data mean
            C64[thin] = gcov; m64[thin] = torch.nan_to_num(m64[thin])
            mu = m64.float(); Sig = C64.float()
            logw = torch.log((Nk_ / Nk_.sum()).float())
        Sig = Sig.double() + (reg + 1e-4 * torch.diagonal(Sig.double(), dim1=-2, dim2=-1).mean(-1))[:, None, None] * I.double()
        C = Sig.cpu().numpy(); M = mu.double().cpu().numpy(); Wt = torch.exp(logw).double().cpu().numpy()
        du = self.du
        Suu, Suv, Svv = C[:, :du, :du], C[:, :du, du:], C[:, du:, du:]
        Bk = np.stack([np.linalg.solve(Suu[k], Suv[k]).T for k in range(K)])
        bk = M[:, du:] - np.einsum('kvu,ku->kv', Bk, M[:, :du])
        Rk = np.stack([Svv[k] - Suv[k].T @ np.linalg.solve(Suu[k], Suv[k]) for k in range(K)])
        base = (Wt[:, None, None] * Bk).sum(0)
        Us, Vs = [], []
        for k in range(K):
            u_, s_, vt_ = np.linalg.svd(Bk[k] - base)
            Us.append(u_[:, :self.r] * s_[:self.r]); Vs.append(vt_[:self.r].T)
        with torch.no_grad():
            self.logpi.copy_(torch.as_tensor(np.log(np.maximum(Wt, 1e-12))))
            self.mu.copy_(torch.as_tensor(M[:, :du]))
            self.Lg.copy_(torch.as_tensor(np.stack([np.linalg.cholesky(np.linalg.inv(Suu[k])) for k in range(K)])))
            self.B.copy_(torch.as_tensor(base)); self.U.copy_(torch.as_tensor(np.stack(Us)))
            self.V.copy_(torch.as_tensor(np.stack(Vs))); self.b.copy_(torch.as_tensor(bk))
            self.Lr.copy_(torch.as_tensor(np.stack([np.linalg.cholesky(Rk[k] + 1e-9 * np.eye(self.dv)) for k in range(K)])))
            self.logsig.copy_(torch.as_tensor(np.log(np.maximum(np.stack([np.diag(Rk[k]) for k in range(K)]), 1e-8))))
        self.em_iter = iters
        return self

    def init_oracle(self, centres_u, gate_covs, priors, A, b):
        """Oracle experts (A3): gates at given centres with given covariances and priors; maps given (exact local
        linearisations from W, computed by the caller)."""
        with torch.no_grad():
            self.logpi.copy_(torch.as_tensor(np.log(np.maximum(priors, 1e-12))))
            self.mu.copy_(torch.as_tensor(centres_u))
            self.Lg.copy_(torch.as_tensor(np.stack([np.linalg.cholesky(np.linalg.inv(C)) for C in gate_covs])))
            Ab = np.asarray(A); base = Ab.mean(0)
            Us, Vs = [], []
            for k in range(self.K):
                u_, s_, vt_ = np.linalg.svd(Ab[k] - base)
                Us.append(u_[:, :self.r] * s_[:self.r]); Vs.append(vt_[:self.r].T)
            self.B.copy_(torch.as_tensor(base)); self.U.copy_(torch.as_tensor(np.stack(Us))); self.V.copy_(torch.as_tensor(np.stack(Vs)))
            self.b.copy_(torch.as_tensor(np.asarray(b)))
        self.em_iter = 0
        return self

    def set_heldout_error(self, U_l, U_t, reg=1e-8):
        """R_err[k] = gate-weighted covariance of the held-out residuals of expert k's predictions (A2)."""
        with torch.no_grad():
            Z = torch.as_tensor(U_l, dtype=DT); T = torch.as_tensor(U_t, dtype=DT)
            beta = torch.exp(self.log_gates(Z))
            res = T[:, None, :] - (torch.einsum('kvu,nu->nkv', self.A(), Z) + self.b)
            wsum = beta.sum(0) + 1e-300
            Rk = torch.einsum('nk,nki,nkj->kij', beta, res, res) / wsum[:, None, None]
            self.R_err = Rk + reg * torch.eye(self.dv, dtype=DT)
        return self

    def A(self):
        return self.B[None] + self.U @ self.V.transpose(-1, -2)                       # (K, dv, du)

    def R(self):
        return self.Lr @ self.Lr.transpose(-1, -2) + 1e-9 * torch.eye(self.dv, dtype=DT)

    def log_gates(self, Z):
        """Normalised log gate weights for rows of Z (..., du) -> (..., K)."""
        Lt = torch.tril(self.Lg)                    # review fix (astra #7): triangular factor so the logdet below is exact
        P = Lt @ Lt.transpose(-1, -2)                                                 # precisions (K, du, du)
        diff = Z[..., None, :] - self.mu                                              # (..., K, du)
        q = (torch.einsum('...ki,kij->...kj', diff, P) * diff).sum(-1)
        logdet = 2 * torch.log(torch.abs(torch.diagonal(Lt, dim1=-2, dim2=-1))).sum(-1)
        lg = torch.log_softmax(self.logpi, 0) + 0.5 * logdet - 0.5 * q
        return torch.log_softmax(lg, -1)

    def point(self, Z, mode='gpoe'):
        """Point prediction within the bank. 'gpoe': precision-weighted (beta R^-1) fusion; 'mix': mixture mean
        sum_k beta_k (A_k z + b_k) with covariance sum_k beta_k (R_k + spread). Returns (eta, Lam) = information form."""
        beta = torch.exp(self.log_gates(Z))                                           # (N, K)
        mu = torch.einsum('kvu,nu->nkv', self.A(), Z) + self.b                         # (N, K, dv)
        R = self.R()
        if mode == 'gpoe':
            Ri = chol_inv_spd(R)                                                      # (K, dv, dv)
            Lam = torch.einsum('nk,kij->nij', beta, Ri)
            eta = torch.einsum('nk,kij,nkj->ni', beta, Ri, mu)
            return eta, Lam
        mean = torch.einsum('nk,nkv->nv', beta, mu)
        D = mu - mean[:, None]
        cov = torch.einsum('nk,kij->nij', beta, R) + torch.einsum('nk,nki,nkj->nij', beta, D, D)
        Lam = chol_inv_spd(cov)
        return torch.einsum('nij,nj->ni', Lam, mean), Lam

    def component(self, m, S, eps):
        """Monte Carlo gate moments inside N(m, S) with common draws eps (R, du). Returns overlaps w (K,), predicted
        means (K, dv), predicted covariances (K, dv, dv), reweighted source moments (K, du), (K, du, du)."""
        Ls = torch.linalg.cholesky(S + 1e-10 * torch.eye(self.du, dtype=DT))
        Z = m + eps @ Ls.T                                                            # (R, du)
        G = torch.exp(self.log_gates(Z))                                              # (R, K)
        w = G.mean(0)
        om = G / (G.sum(0, keepdim=True) + 1e-300)                                    # (R, K)
        mk = om.T @ Z                                                                 # (K, du)
        D = Z[None] - mk[:, None]                                                     # (K, R, du)
        Sk = (om.T[:, :, None] * D).transpose(1, 2) @ D + 1e-10 * torch.eye(self.du, dtype=DT)
        A = self.A()
        mu = torch.einsum('kvu,ku->kv', A, mk) + self.b
        C = torch.einsum('kvu,kuw,kxw->kvx', A, Sk, A) + self.R()
        return w, mu, C, mk, Sk


class LMLE(torch.nn.Module):
    """Banks (l, s) for every source l and skip s. Components are propagated by Monte Carlo inside the component
    (common standardised draws, no net evaluations) through the model's POINTWISE fused map, so the population mean
    and spread come from the draws; the pointwise fusion is 'gpoe' (spec: generalised product of experts with
    precisions beta_e R_e^-1, R_e = held-out residual covariance) or 'mix' (mixture of experts, sum_e beta_e (A_e z + b_e)).
    Mean-error covariance E (amendment A2): per route E_r = Jbar E_src Jbar^T + kappa_t mean_i Unc(z_i), Jbar the
    draw-averaged fused Jacobian, Unc the pointwise model error (gpoe: (sum beta R^-1)^-1; mix: sum beta (R + spread of
    the expert predictions)); routes (chain and skips) are fused by precision rho_s E_r^-1, the population spread by the
    route-weighted average. Splits use the s = 1 gate overlaps and the gate-reweighted part moments (they preserve the
    mean exactly at the split; merges preserve it by moment matching), so the split/merge error terms are 0."""

    def __init__(self, L, d, K, r, skips=(1, 2, 4, 8)):
        super().__init__()
        self.L, self.d, self.K = L, d, K
        self.skips = [s for s in skips if s <= L]
        self.banks = torch.nn.ModuleDict()
        for l in range(L):
            for s in self.skips:
                if l + s <= L:
                    self.banks[f'{l}_{s}'] = Bank(d, d, K, r)
        self.route_logit = torch.nn.Parameter(torch.zeros(L + 1, len(self.skips), dtype=DT))
        self.log_kappa = torch.nn.Parameter(torch.zeros(L + 1, dtype=DT))

    def routes(self, t):
        return [(s_i, s) for s_i, s in enumerate(self.skips) if t - s >= 0 and f'{t - s}_{s}' in self.banks]

    @staticmethod
    def pointwise(bank, Z, mode, chunk=512):
        """Pointwise fused prediction, model error and fused Jacobian, without 4-index intermediates (chunked)."""
        A = bank.A(); K, dv, du = A.shape
        R = bank.R_err if getattr(bank, 'R_err', None) is not None else bank.R()
        if mode in ('gpoe', 'tgpoe'):
            Ri = chol_inv_spd(R)
            RiA = (Ri @ A).reshape(K, -1)
            Rif = Ri.reshape(K, -1)
        Af = A.reshape(K, -1); Rf = R.reshape(K, -1)
        preds, Uncs, Js = [], [], []
        for i0 in range(0, Z.shape[0], chunk):
            z = Z[i0:i0 + chunk]
            beta = torch.exp(bank.log_gates(z))                                       # (N, K)
            mu = torch.einsum('kvu,nu->nkv', A, z) + bank.b                            # (N, K, dv)
            if mode == 'poe':
                logb = bank.log_gates(z)                                              # (N, K)
                lp = -bank.logsig[None] + bank.cgate[None] * logb[..., None]          # log precision (N, K, dv)
                lp = lp - lp.max(1, keepdim=True).values.detach()                   # stabilise; ratios unchanged
                prec = torch.exp(lp)
                scale = torch.exp((-bank.logsig[None] + bank.cgate[None] * logb[..., None]).max(1).values)  # (N, dv)
                Lsum = prec.sum(1)                                                    # (N, dv)
                pred = (prec * mu).sum(1) / Lsum
                var = 1.0 / (Lsum * scale)
                Unc = torch.diag_embed(var)
                J = torch.einsum('nkv,kvu->nvu', prec / Lsum[:, None, :], A)
                preds.append(pred); Uncs.append(Unc); Js.append(J)
                continue
            if mode == 'tgpoe':
                eta, Lam, Wsym = fuse_tempered(beta, Ri, mu)
                Unc = chol_inv_spd(Lam)
                pred = torch.einsum('nij,nj->ni', Unc, eta)
                J = Unc @ torch.einsum('nkij,kjl->nil', Wsym, A)
            elif mode == 'gpoe':
                Lam = (beta @ Rif).reshape(-1, dv, dv)
                Unc = chol_inv_spd(Lam)
                Rimu = torch.einsum('kij,nkj->nki', Ri, mu)
                eta = torch.einsum('nk,nki->ni', beta, Rimu)
                pred = torch.einsum('nij,nj->ni', Unc, eta)
                J = Unc @ (beta @ RiA).reshape(-1, dv, du)
            else:
                pred = torch.einsum('nk,nkv->nv', beta, mu)
                D = mu - pred[:, None]
                Unc = (beta @ Rf).reshape(-1, dv, dv) + (D * beta[..., None]).transpose(1, 2) @ D
                J = (beta @ Af).reshape(-1, dv, du)
            preds.append(pred); Uncs.append(Unc); Js.append(J)
        return torch.cat(preds), torch.cat(Uncs), torch.cat(Js)

    def point_chain(self, U0, mode='gpoe'):
        N = U0.shape[0]
        us = {0: U0}; Es = {0: torch.zeros(N, self.d, self.d, dtype=DT)}
        for t in range(1, self.L + 1):
            rts = self.routes(t)
            wts = torch.softmax(self.route_logit[t, [si for si, _ in rts]], 0)
            kappa = torch.exp(self.log_kappa[t])
            Lam_t = 0; eta_t = 0
            for w_r, (si, s) in zip(wts, rts):
                pred, Unc, J = self.pointwise(self.banks[f'{t - s}_{s}'], us[t - s], mode)
                Er = torch.einsum('nij,njk,nlk->nil', J, Es[t - s], J) + kappa * Unc
                Li = chol_inv_spd(Er)
                Lam_t = Lam_t + w_r * Li; eta_t = eta_t + w_r * torch.einsum('nij,nj->ni', Li, pred)
            Es[t] = chol_inv_spd(Lam_t)
            us[t] = torch.einsum('nij,nj->ni', Es[t], eta_t)
        return us, Es

    def _route_pred(self, bank, m, S, E, eps, kappa, mode):
        Ls = torch.linalg.cholesky(S + 1e-12 * torch.eye(len(m), dtype=DT))
        Z = m + eps @ Ls.T
        pred, Unc, J = self.pointwise(bank, Z, mode)
        mean = pred.mean(0)
        D = pred - mean
        Spop = D.T @ D / len(Z)
        Jbar = J.mean(0)
        Er = Jbar @ E @ Jbar.T + kappa * Unc.mean(0)
        G = torch.exp(bank.log_gates(Z))
        w = G.mean(0)
        om = G / (G.sum(0, keepdim=True) + 1e-300)
        mk = om.T @ Z
        Dk = Z[None] - mk[:, None]
        Sk = (om.T[:, :, None] * Dk).transpose(1, 2) @ Dk + 1e-12 * torch.eye(len(m), dtype=DT)
        return mean, Spop, Er, (w / w.sum(), mk, Sk)

    def _fuse(self, preds, wts):
        Lam = 0; eta = 0; Sp = 0
        for w_r, (mean_r, Spop_r, Er, _) in zip(wts, preds):
            Li = chol_inv_spd(Er)
            Lam = Lam + w_r * Li; eta = eta + w_r * Li @ mean_r; Sp = Sp + w_r * Spop_r
        E = chol_inv_spd(Lam); E = 0.5 * (E + E.T)
        return E @ eta, 0.5 * (Sp + Sp.T) + 1e-12 * torch.eye(self.d, dtype=DT), E

    def propagate(self, m0, S0, eps_by_layer, K_pop=64, split=0.2, split_on=True, mode='gpoe'):
        """One input population N(m0, S0) in u_0 coordinates. Components carry mass a and histories
        hist[layer] = (m, S, E). Returns per-layer population (mean, cov, E) for t = 1..L, the output components
        (mass, mean, E) for the per-component breakdown (A2), and stats."""
        if isinstance(m0, (list, tuple)):          # a mixture input: list of (mass, mean, cov)
            comps = [dict(a=torch.as_tensor(a, dtype=DT), hist={0: (m, S, torch.zeros_like(S))}) for a, m, S in m0]
        else:
            comps = [dict(a=torch.ones((), dtype=DT), hist={0: (m0, S0, torch.zeros_like(S0))})]
        out = []
        n_split = 0
        for t in range(1, self.L + 1):
            rts = self.routes(t)
            kappa = torch.exp(self.log_kappa[t])
            new = []
            for c in comps:
                avail = [(si, s) for si, s in rts if (t - s) in c['hist']]
                wts = torch.softmax(self.route_logit[t, [si for si, _ in avail]], 0)
                preds = [self._route_pred(self.banks[f'{t - s}_{s}'], *c['hist'][t - s], eps_by_layer[t - s], kappa, mode)
                         for (si, s) in avail]
                parts = next((p[3] for p, (si, s) in zip(preds, avail) if s == 1), None)
                if split_on and parts is not None:
                    wn, mk, Sk = parts
                    top = torch.topk(wn.detach(), min(2, len(wn))).values
                    if len(top) == 2 and float(top[1]) > split and len(comps) + len(new) < K_pop:
                        sel = torch.where(wn.detach() > split)[0]
                        tot = wn[sel].sum()
                        bank = self.banks[f'{t - 1}_1']
                        E_par = c['hist'][t - 1][2]
                        for k in sel.tolist():
                            child = dict(a=c['a'] * wn[k] / tot, hist={t - 1: (mk[k], Sk[k], E_par)})
                            p1 = self._route_pred(bank, mk[k], Sk[k], E_par, eps_by_layer[t - 1], kappa, mode)
                            child['hist'][t] = self._fuse([p1], torch.ones(1, dtype=DT))
                            new.append(child)
                        n_split += 1
                        continue
                c['hist'][t] = self._fuse(preds, wts)
                new.append(c)
            while len(new) > K_pop:
                ms = torch.stack([c['hist'][t][0] for c in new]).detach()
                Dm = torch.cdist(ms, ms) + torch.eye(len(new), dtype=DT) * 1e30
                i, j = divmod(int(torch.argmin(Dm)), len(new))
                ci, cj = new[i], new[j]
                a = ci['a'] + cj['a']
                (mi, Si, Ei), (mj, Sj, Ej) = ci['hist'][t], cj['hist'][t]
                m = (ci['a'] * mi + cj['a'] * mj) / a
                S = (ci['a'] * (Si + torch.outer(mi - m, mi - m)) + cj['a'] * (Sj + torch.outer(mj - m, mj - m))) / a
                E = (ci['a'] * Ei + cj['a'] * Ej) / a
                new = [c for k, c in enumerate(new) if k not in (i, j)] + [dict(a=a, hist={t: (m, S, E)})]
            comps = new
            a = torch.stack([c['a'] for c in comps])
            M = torch.stack([c['hist'][t][0] for c in comps])
            S = torch.stack([c['hist'][t][1] for c in comps])
            E = torch.stack([c['hist'][t][2] for c in comps])
            mean = (a[:, None] * M).sum(0) / a.sum()
            cov = (a[:, None, None] * (S + torch.einsum('ki,kj->kij', M - mean, M - mean))).sum(0) / a.sum()
            # error covariance of the population mean: component errors taken as fully correlated (conservative):
            # E_pop = (sum_j a_j E_j^{1/2})^2 approximated by sum_j a_j E_j scaled by the mass-weighted dispersion
            Eo = (a[:, None, None] * E).sum(0) / a.sum()
            out.append((mean, cov, Eo))
        final = [(float(c['a'].detach()), c['hist'][self.L][0].detach(), c['hist'][self.L][2].detach()) for c in comps]
        return out, dict(n_split=n_split, n_comp=len(comps), components=final)

    def propagate_parts(self, M, S, eps_by_layer, mode='tgpoe', jitter=1e-10):
        """Batched propagation of P fixed parts (no splits, no merges) along the chain s = 1. M (P, d), S (P, d, d) at
        layer 0. Returns [(M_t, S_t, E_t)] for t = 1..L (each (P, d), (P, d, d), (P, d, d)). Same rule as propagate():
        Monte Carlo draws through the pointwise fused map; E_t = Jbar E Jbar^T + kappa_t mean Unc."""
        P, d = M.shape
        E = torch.zeros(P, d, d, dtype=DT)
        I = torch.eye(d, dtype=DT)
        outs = []
        for t in range(1, self.L + 1):
            bank = self.banks[f'{t - 1}_1']
            kappa = torch.exp(self.log_kappa[t])
            Ls = torch.linalg.cholesky(S + jitter * I)
            eps = eps_by_layer[t - 1]
            R = eps.shape[0]
            Z = M[:, None, :] + eps[None] @ Ls.transpose(1, 2)
            pred, Unc, J = self.pointwise(bank, Z.reshape(-1, d), mode)
            pred = pred.reshape(P, R, d)
            Mn = pred.mean(1)
            D = pred - Mn[:, None]
            S = D.transpose(1, 2) @ D / R + jitter * I
            Jbar = J.reshape(P, R, d, d).mean(1)
            E = Jbar @ E @ Jbar.transpose(1, 2) + kappa * Unc.reshape(P, R, d, d).mean(1)
            M = Mn
            outs.append((M, S, E))
        return outs

