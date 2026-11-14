"""Infinite-width price spectrum of a depth-t future (FORMAL A2): power-series coefficients b_d^{(t)} of
kappa_t = kappa_1 o ... o kappa_1 (t times), kappa_1(s) = (sqrt(1 - s^2) + (pi - arccos s) s)/pi, computed by
evaluating kappa_t on the circle |z| = r < 1 (complex principal branches; analytic for |z| < 1) and an FFT.
Outputs results/kernel_spectrum.json: for each t, b_0 (radius feature), b_1 (mean), sum_{d>=2} b_d (higher radially
normalised moments), sum_{d >= 2} d b_d, the degree d50/d90 below which 50%/90% of the d >= 2 mass lies, and checks
(sum_d b_d = kappa_t(1) = 1). NUMERICAL (r = 0.9995, M = 2^17; truncation tail estimated by the check)."""
import json, os
import numpy as np

r, M = 0.9995, 1 << 17
z0 = r * np.exp(2j * np.pi * np.arange(M) / M)


def kappa1(z):
    return (np.sqrt(1 - z * z) + (np.pi / 2 + np.arcsin(z)) * z) / np.pi


out = {}
z = z0.copy()
for t in range(1, 65):
    z = kappa1(z)
    c = np.fft.fft(z) / M                     # c_d = b_d r^d
    d = np.arange(M)
    DMAX = 20000                              # beyond this, 1e-16 / r^d swamps b_d ~ d^-2.5
    b = (c.real / r ** d)[:DMAX]
    # exact b0, b1 and the d >= 2 mass from kappa_t(0), kappa_t'(0) and kappa_t(1) = 1
    s0, der = 0.0, 1.0
    for _ in range(t):
        der *= np.real(0.5 + np.arcsin(s0) / np.pi) if False else (0.5 + np.arcsin(s0) / np.pi)
        s0 = float(np.real(kappa1(np.array([s0 + 0j]))[0]))
    b0x, b1x = s0, der
    tot = float(b.sum())
    hi = b[2:]
    cum = np.cumsum(hi) / max(hi.sum(), 1e-300)
    d50 = int(np.searchsorted(cum, 0.5)) + 2
    d90 = int(np.searchsorted(cum, 0.9)) + 2
    kap0 = float(np.real(kappa1(np.array([0.0]))[0])) if t == 1 else None
    out[t] = dict(b0_exact=b0x, b1_exact=b1x, b_ge2_exact=1.0 - b0x - b1x, b0_fft=float(b[0]), b1_fft=float(b[1]),
                  b_ge2_fft=float(hi.sum()), mean_deg_ge2=float((d[2:DMAX] * hi).sum() /
                  max(hi.sum(), 1e-300)), d50=d50, d90=d90, sum_b=tot, min_b=float(b[:2000].min()))
    if t in (1, 2, 4, 8, 16, 24, 28, 31, 32, 64):
        print(f"t={t:2d} exact b0 {b0x:.4f} b1 {b1x:.4f} b>=2 {1 - b0x - b1x:.4f} | fft b0 {b[0]:.4f} b1 {b[1]:.4f} "
              f"b>=2 {hi.sum():.4f} d50 {d50} d90 {d90} mean_deg {out[t]['mean_deg_ge2']:.1f}", flush=True)
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results'), exist_ok=True)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results', 'kernel_spectrum.json'),
                    'w'), indent=1)
