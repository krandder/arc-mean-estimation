"""scale-mode lane: adapters that run the topic-18298 estimator (third-party, audited in notes/AUDIT.md) and comparators.

Third-party code is loaded from paths given by the caller and nothing else from that repository is executed:
- lvlib.py (the law-vertex estimator) imported by file path (importlib), run on CPU in float64;
- descale_fac_src.py (the factored de-scaling hook) exec'd into a namespace supplied here, as sl_fac.py does.
ARC's code: the local clone at 93d091a (work/arc-noisy/ext/mlp_cumulant_propagation), through arc-update's lib/au.py.

Conventions (arc-update): W_l is (out, in), z_l = W_l h_{l-1}, h_l = relu(z_l), x ~ N(0, I_n), estimand E h_L (no output
layer). nMSE = |est - Y|^2 / tr Var. One forward pass = 2 n^2 L flops. ARC's NamedFlopCounter for every method.
The claim's own accounting is reproduced for its estimator: NamedFlopCounter + 1 flop per ndtr element + its hand count of
scalar special functions (lv2.py). Also recorded: ndtr and exp element counts, for a flopscope-priced sensitivity
(flopscope 0.12: norm.cdf ~96, exp 16 flops per element; ARC's counter charges exp 1 and does not see ndtr).
"""
import importlib.util, math, os, sys, time
import numpy as np
import torch

ARC_SRC = '/home/agent/workspaces/mats/work/arc-noisy/ext/mlp_cumulant_propagation/src'
AU_LIB = '/home/agent/workspaces/mats/work/arc-update/lib'
for p in (ARC_SRC, AU_LIB):
    if p not in sys.path:
        sys.path.insert(0, p)
import au                                                    # noqa: E402  (arc-update library; sets torch threads)
from mlp_kprop import kprop_harmonic as kh                   # noqa: E402
from mlp_kprop.harmonic import HTensor                       # noqa: E402
from mlp_kprop.factor_k3 import FactoredTensor               # noqa: E402
from mlp_kprop.flop_utils import NamedFlopCounter, flop_name  # noqa: E402

torch.set_grad_enabled(False)
DT = torch.float64
CPU = torch.device('cpu')


def load_lvlib(path):
    spec = importlib.util.spec_from_file_location('lvlib_thirdparty', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def lv_weights(W):
    """lvlib convention: list of (out, in) float64 tensors, layers 0..L with an identity output layer (unused for E h_L)."""
    n = W[0].shape[0]
    return [w.to(DT).contiguous() for w in W] + [torch.eye(n, dtype=DT)]


class _Count:
    def __init__(self):
        self.ndtr = 0
        self.exp = 0


def run_lv(lv, W, R=24, b_up=6.5, mode='full', rule='v2f'):
    """The claim's estimator lvt2_chain (rule 'v2f' = V2 rule + feasibility cap; 'lead' = old rule; 'zero' = V = 0
    Gaussian closure with the exact pair vertex), counted as lv2.py counts it. Returns dict."""
    Ws = lv_weights(W)
    L = len(W)
    cnt = _Count()
    nd_orig = torch.special.ndtr
    exp_orig = torch.exp

    def nd(x):
        cnt.ndtr += x.numel()
        return nd_orig(x)

    def ex(x, *a, **k):
        cnt.exp += x.numel()
        return exp_orig(x, *a, **k)

    lv.ndtr = nd
    lv.SCAL[0] = 0
    lv.V2FLAGS.clear()
    torch.exp = ex
    t0 = time.time()
    try:
        fc = NamedFlopCounter()
        with fc:
            with flop_name('lv2'):
                h, y, Vs = lv.lvt2_chain(Ws, L, R, mode, b_up, rule)
    finally:
        torch.exp = exp_orig
        lv.ndtr = nd_orig
    arc = fc.total()
    flops = arc + cnt.ndtr + lv.SCAL[0]
    flags = list(lv.V2FLAGS)
    return dict(mean=h.numpy().copy(), Vs=[float(v) for v in Vs], flops=float(flops), arc_counter=float(arc),
                ndtr=int(cnt.ndtr), exp=int(cnt.exp), scal=int(lv.SCAL[0]),
                flops_flopscope_special=float(flops + 95 * cnt.ndtr + 15 * cnt.exp),
                secs=time.time() - t0, flags={k: flags.count(k) for k in set(flags)})


def load_descale_fac(lv, src_path):
    """exec the factored de-scaling hook (descale_fac_src.py) in a private namespace, with the scale law routed to the
    exact Gamma law (as sl_fac.py does: lognormal_cums = gamma_law)."""
    ns = dict(math=math, torch=torch, HTensor=HTensor, FactoredTensor=FactoredTensor, dev=CPU, dt=DT)
    exec(compile(open(src_path).read(), src_path, 'exec'), ns)

    def gamma_law(V):
        s1 = lv.gmom(V, .5)
        E = {k: lv.gmom(V, k / 2) / s1 ** k for k in range(1, 5)}
        return {1: 1.0, 2: E[2] - 1, 3: E[3] - 3 * E[2] + 2, 4: E[4] - 4 * E[3] - 3 * E[2] ** 2 + 12 * E[2] - 6}, E

    ns['lognormal_cums'] = gamma_law
    return ns


def run_sl3(ns, W, kind='SIMPLE', gate=False, metric=2.0):
    """SL3 = ARC's factored K3 chain (unmodified) + the factored de-scaling hook with the exact Gamma law, V from the
    carried kappa4 (2,2) trace (R186a rule), as sl_fac.py. gate=True: the hook is skipped (= plain ARC k3f).
    metric = ARC's average metric E[W W^T] = 2 for our nets (every layer N(0, 2/n))."""
    n, L = W[0].shape[0], len(W)
    Ws = [w.to(DT).contiguous() for w in W]
    kind_e = getattr(kh.Kind, kind)
    wick = kh.WICK_COEF_D['relu']
    Vs = []
    t0 = time.time()
    fc = NamedFlopCounter()
    with fc:
        with flop_name('sl3'):
            K = kh.coerce_input({1: torch.zeros(n, dtype=DT), 2: torch.eye(n, dtype=DT)}, k_max=3, kind=kind_e)
            for l in range(L):
                K = kh.linear_kprop(K, Ws[l], k_max=3, set_metric=float(metric))
                K = kh.nonlin_kprop(K, nonlin_wick_coef=wick, k_max=3, kind=kind_e, use_pK=True, factor=True)
                if (not gate) and l < L - 1:
                    Sg = K[2].core
                    tau = K[4].core
                    num = float(tau) * (n * n + 2 * n) / 3.0
                    den = float(torch.trace(Sg)) ** 2 + 2 * float((Sg * Sg).sum())
                    V = min(max(num / den, 0.0), 0.999)
                    Vs.append(V)
                    if V > 0:
                        K = ns['descale_tower'](K, V, n)
            h = K[1].core.double()
    return dict(mean=h.numpy().copy(), Vs=Vs, flops=float(fc.total()), secs=time.time() - t0)


def run_covprop_gain(W):
    """The starter kit's covariance-propagation baseline (examples/03_covariance_propagation.py), same math in torch float64:
    exact per-neuron Gaussian mean and variance after the ReLU, off-diagonal covariance scaled by Phi(a_i) Phi(a_j).
    Counted with ARC's counter (+1 flop per ndtr element; the starter kit bills it with flopscope: 5.17e10 at 1024x16)."""
    n, L = W[0].shape[0], len(W)
    cnt = _Count()
    t0 = time.time()
    fc = NamedFlopCounter()
    with fc:
        with flop_name('covprop'):
            mu = torch.zeros(n, dtype=DT)
            cov = torch.eye(n, dtype=DT)
            for l in range(L):
                w = W[l].to(DT)
                mu_pre = w @ mu
                cov_pre = w @ cov @ w.T
                var_pre = torch.clamp(torch.diagonal(cov_pre), min=1e-12)
                sig = torch.sqrt(var_pre)
                a = mu_pre / sig
                phi = torch.exp(-0.5 * a * a) / math.sqrt(2 * math.pi)
                Phi = torch.special.ndtr(a)
                cnt.ndtr += a.numel()
                mu = mu_pre * Phi + sig * phi
                ez2 = (mu_pre * mu_pre + var_pre) * Phi + mu_pre * sig * phi
                var_post = torch.clamp(ez2 - mu * mu, min=0.0)
                gain = torch.where(sig > 1e-12, Phi, torch.zeros_like(Phi))
                cov = torch.outer(gain, gain) * cov_pre
                cov.diagonal().copy_(var_post)
    return dict(mean=mu.numpy().copy(), flops=float(fc.total() + cnt.ndtr), secs=time.time() - t0)


def run_arc(W, variant):
    """ARC's mlp_kprop variant through arc-update's wrapper (avg metric 2, sigma = 0, float64, ARC's counter)."""
    spec = dict(k1=(1, False, 'simple'), k2=(2, False, 'simple'), k2a=(2, False, 'augment'), k3f=(3, True, 'simple'),
                k3fa=(3, True, 'augment'), k3=(3, False, 'simple'))[variant]
    r = au.arc_kprop(W, spec[0], factor=spec[1], kind=spec[2])
    return dict(mean=np.asarray(r['mean']), flops=float(r['flops']), secs=r['secs'])


def nmse(est, Y, var):
    return float(((np.asarray(est) - Y) ** 2).sum() / var.sum())


def nmse_cross(est, YA, YB, var):
    """Cross-half (truth-noise-free) squared error, normalised: (est - YA).(est - YB) / tr Var."""
    est = np.asarray(est)
    return float(((est - YA) * (est - YB)).sum() / var.sum())


def passes(flops, n, L):
    return flops / au.pass_flops(n, L)
