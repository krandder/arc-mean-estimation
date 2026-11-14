"""Population-level mixture of linear experts with generalised product-of-experts fusion (Kelvin's step-4 choices,
relayed by main 2 Nov ~16:40-16:50Z). Torch, float64, differentiable end to end.

Coordinates: u_0 = x in R^n (the input population is exactly Gaussian); u_l = P_l^T (h_l - c_l) in R^d for l >= 1
(top-d principal axes of a pilot cloud). Layer l -> l+1 has K experts: gate N(u; g_k, G_k) with G_k diagonal (isotropic at
the input), prior weight pi_k; affine map B_k u + b_k; output noise covariance R_k = Q_k Q_k^T + diag(r_k).
Propagation of a population component N(m, S):
- gate weights beta_k proportional to pi_k N(m; g_k, S + G_k) (the gate integrated over the component's spread, then
  normalised over experts);
- expert k predicts N(B_k m + b_k, B_k S B_k^T + R_k);
- fusion 'gpoe' (generalised product of experts, Cao and Fleet 2014): precision sum_k beta_k C_k^-1, mean
  (that)^-1 sum_k beta_k C_k^-1 mu_k; 'poe' (unnormalised: beta_k = 1); 'mix' (moment-matched mixture).
One Gaussian per population component per layer (no splitting in this version).
"""
import math
import numpy as np
import torch

DT = torch.float64


class PopMoE(torch.nn.Module):
    def __init__(self, dims, K, init=None):
        """dims = [d_0, d_1, ..., d_L]; init: optional list of per-layer dicts from EM (pi, g, G, B, b, R)."""
        super().__init__()
        self.dims, self.K = dims, K
        self.layers = torch.nn.ModuleList()
        for l in range(len(dims) - 1):
            du, dv = dims[l], dims[l + 1]
            m = torch.nn.Module()
            p = init[l] if init is not None else None
            def P(x):
                return torch.nn.Parameter(torch.as_tensor(x, dtype=DT).clone())
            if p is None:
                m.logpi = P(np.zeros(K)); m.g = P(np.random.randn(K, du) * 0.1); m.logG = P(np.zeros((K, du)))
                m.B = P(np.random.randn(K, dv, du) / math.sqrt(du)); m.b = P(np.zeros((K, dv)))
                m.Q = P(np.zeros((K, dv, 4))); m.logr = P(np.full((K, dv), -2.0))
            else:
                m.logpi = P(np.log(np.maximum(p['pi'], 1e-12))); m.g = P(p['g']); m.logG = P(np.log(np.maximum(p['G'], 1e-8)))
                m.B = P(p['B']); m.b = P(p['b'])
                # low-rank (rank 4) + diagonal from the EM residual covariance
                R = p['R']
                Qs, diags = [], []
                for k in range(K):
                    ev, U = np.linalg.eigh(R[k])
                    idx = np.argsort(ev)[::-1][:4]
                    Qk = U[:, idx] * np.sqrt(np.maximum(ev[idx], 0))[None, :]
                    Qs.append(Qk); diags.append(np.maximum(np.diag(R[k]) - (Qk ** 2).sum(1), 1e-6))
                m.Q = P(np.stack(Qs)); m.logr = P(np.log(np.stack(diags)))
            self.layers.append(m)

    def layer_push(self, l, m, S, fusion='gpoe'):
        """m (B, du), S (B, du, du) -> next (B, dv), (B, dv, dv); also returns beta (B, K)."""
        L = self.layers[l]
        K = self.K
        G = torch.exp(L.logG)                                                  # (K, du)
        # gate overlap log N(m; g_k, S + diag(G_k)) for each component and expert
        Sg = S[:, None, :, :] + torch.diag_embed(G)[None]                      # (B, K, du, du)
        diff = m[:, None, :] - L.g[None]                                       # (B, K, du)
        ch = torch.linalg.cholesky(Sg)
        z = torch.cholesky_solve(diff[..., None], ch)[..., 0]
        logdet = 2 * torch.log(torch.diagonal(ch, dim1=-2, dim2=-1)).sum(-1)
        logN = -0.5 * (diff * z).sum(-1) - 0.5 * logdet
        logw = torch.log_softmax(L.logpi, 0)[None] + logN
        beta = torch.softmax(logw, 1)                                          # (B, K)
        mu = torch.einsum('kvu,bu->bkv', L.B, m) + L.b[None]                   # (B, K, dv)
        R = L.Q @ L.Q.transpose(-1, -2) + torch.diag_embed(torch.exp(L.logr))  # (K, dv, dv)
        C = torch.einsum('kvu,buw,kxw->bkvx', L.B, S, L.B) + R[None]           # (B, K, dv, dv)
        if fusion == 'mix':
            mn = (beta[..., None] * mu).sum(1)
            dm = mu - mn[:, None]
            Sn = (beta[..., None, None] * (C + dm[..., :, None] * dm[..., None, :])).sum(1)
            return mn, 0.5 * (Sn + Sn.transpose(-1, -2)), beta
        w = beta if fusion == 'gpoe' else torch.ones_like(beta)
        Ci = torch.linalg.inv(C)
        Lam = (w[..., None, None] * Ci).sum(1)
        Sn = torch.linalg.inv(Lam)
        mn = (Sn @ (w[..., None, None] * Ci @ mu[..., None]).sum(1))[..., 0]
        return mn, 0.5 * (Sn + Sn.transpose(-1, -2)), beta

    def forward(self, m0, S0, fusion='gpoe'):
        """Propagate input populations; returns lists of per-layer means and covariances (l = 1..L)."""
        ms, Ss, betas = [], [], []
        m, S = m0, S0
        for l in range(len(self.layers)):
            m, S, beta = self.layer_push(l, m, S, fusion)
            ms.append(m); Ss.append(S); betas.append(beta)
        return ms, Ss, betas
