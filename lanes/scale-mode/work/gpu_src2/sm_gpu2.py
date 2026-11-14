"""scale-mode lane, GPU runner 2 (PREREG Amendment 2): the E3 256 x 64 cell and every E4 job (Phase 2 public MLPs).
Same estimators, counters and file formats as scripts/run_cell.py + scripts/smlib.py (and gpu_src/sm_gpu.py), on CUDA:
- NET au:SEED:N:L (anet.make_weights) or p2:ID (weights from p2/p2_mlp_ID.npz, dataset (in, out) convention, transposed);
- truth (au only), lv (four claim arms, R = 24, b = 6.5, the claim's accounting), arc (k2, k2a, k3f; ARC's counter),
  sl3 (ARC factored K3 SIMPLE + the claim's factored de-scaling hook with the exact Gamma law, as smlib.run_sl3),
  cov (the starter kit's covariance propagation, as smlib.run_covprop_gain), rqmc (scrambled Sobol, as au.rqmc).
usage: python -I sm_gpu2.py OUT_DIR JOB NET [args]"""
import importlib.util, json, math, os, sys, time
import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'lib'))
import anet                                                        # noqa: E402
import kprop_noisy as KN                                           # noqa: E402
from kprop_noisy import KH, NamedFlopCounter, flop_name, WICK_COEF_D  # noqa: E402
from mlp_kprop import kprop_harmonic as kh                         # noqa: E402
from mlp_kprop.harmonic import HTensor                             # noqa: E402
from mlp_kprop.factor_k3 import FactoredTensor                     # noqa: E402

torch.backends.cuda.matmul.allow_tf32 = False
torch.backends.cudnn.allow_tf32 = False
torch.set_grad_enabled(False)
DEV = torch.device('cuda')
DT = torch.float64

OUT, JOB, NET = sys.argv[1], sys.argv[2], sys.argv[3]
ARGS = sys.argv[4:]
os.makedirs(OUT, exist_ok=True)
pref = os.environ.get('SM_PREFIX', '')
p = NET.split(':')
if p[0] == 'au':
    seed, n, L = int(p[1]), int(p[2]), int(p[3])
    tag = f'au{seed}_n{n}_L{L}'
    W64 = anet.make_weights(seed, n, L)
    chk = float(anet.weights_checksum(W64))
elif p[0] == 'p2':
    i = int(p[1])
    Wd = np.load(os.path.join(HERE, 'p2', f'p2_mlp_{i:02d}.npz'))['weights']
    W64 = [torch.from_numpy(np.ascontiguousarray(Wd[l].T).astype(np.float64)) for l in range(Wd.shape[0])]
    n, L = Wd.shape[1], Wd.shape[0]
    tag = f'p2_{i:02d}'
    chk = float(sum(float(w.sum()) * (k + 1) for k, w in enumerate(W64)))
else:
    raise ValueError(NET)
t0 = time.time()


def passes(fl):
    return fl / (2.0 * n * n * L)


def load_lv():
    spec = importlib.util.spec_from_file_location('lvlib_thirdparty', os.path.join(HERE, 'tp', 'lvlib.py'))
    lv = importlib.util.module_from_spec(spec); spec.loader.exec_module(lv)
    return lv


if JOB == 'truth':
    lg = int(ARGS[0]); N = 1 << lg
    Wt = [w.to(DEV, torch.float32).T.contiguous() for w in W64]
    gen = torch.Generator(device=DEV).manual_seed(880_000 + sum(map(ord, tag)) * 101)
    S1 = torch.zeros(2, L, n, dtype=DT, device=DEV); S2 = torch.zeros(2, L, n, dtype=DT, device=DEV)
    chunk = 1 << 14; done = 0
    while done < N:
        m = min(chunk, N - done); half = 0 if done < N // 2 else 1
        h = torch.randn(m, n, generator=gen, device=DEV, dtype=torch.float32)
        for l in range(L):
            h = torch.relu(h @ Wt[l])
            hd = h.double()
            S1[half, l] += hd.sum(0); S2[half, l] += (hd * hd).sum(0)
        done += m
    S1 = S1.cpu().numpy(); S2 = S2.cpu().numpy()
    np.savez(os.path.join(OUT, f'{pref}truth_{tag}.npz'), S1A=S1[0], S1B=S1[1], S2A=S2[0], S2B=S2[1], N=N, n=n, L=L, net=NET,
             secs=time.time() - t0, checksum=chk, device=torch.cuda.get_device_name(0))
    print(f'truth {NET} 2^{lg} {time.time() - t0:.0f}s checksum {chk:.10e}', flush=True)

elif JOB == 'lv':
    lv = load_lv()
    Ws = [w.to(DEV, DT).contiguous() for w in W64] + [torch.eye(n, dtype=DT, device=DEV)]
    res = dict(net=NET, n=n, L=L, arms={}, checksum=chk, device=torch.cuda.get_device_name(0))
    for arm, mode, rule in (('LVTV2', 'full', 'v2f'), ('LVT', 'full', 'lead'), ('LVTV2f1', 'first', 'v2f'), ('LVT0', 'full', 'zero')):
        cnt = dict(ndtr=0, exp=0)
        nd_orig = torch.special.ndtr; exp_orig = torch.exp

        def nd(x):
            cnt['ndtr'] += x.numel(); return nd_orig(x)

        def ex(x, *a, **k):
            cnt['exp'] += x.numel(); return exp_orig(x, *a, **k)
        lv.ndtr = nd; lv.SCAL[0] = 0; lv.V2FLAGS.clear(); torch.exp = ex
        ta = time.time()
        try:
            fc = NamedFlopCounter()
            with fc:
                with flop_name('lv2'):
                    h, y, Vs = lv.lvt2_chain(Ws, L, 24, mode, 6.5, rule)
        finally:
            torch.exp = exp_orig; lv.ndtr = nd_orig
        arc = fc.total(); flops = arc + cnt['ndtr'] + lv.SCAL[0]; flags = list(lv.V2FLAGS)
        res['arms'][arm] = dict(mean=h.cpu().numpy().tolist(), Vs=[float(v) for v in Vs], flops=float(flops), arc_counter=float(arc),
                                ndtr=int(cnt['ndtr']), exp=int(cnt['exp']), scal=int(lv.SCAL[0]),
                                flops_flopscope_special=float(flops + 95 * cnt['ndtr'] + 15 * cnt['exp']), secs=time.time() - ta,
                                flags={k: flags.count(k) for k in set(flags)})
        print(f'lv {NET} {arm}: V_L {Vs[-1]:.4f} flops {flops:.3e} passes {passes(flops):.0f} {time.time() - ta:.1f}s', flush=True)
    json.dump(res, open(os.path.join(OUT, f'{pref}lv_{tag}.json'), 'w'))

elif JOB == 'arc':
    for v in ARGS[0].split(','):
        k_max, factor, kind = dict(k2=(2, False, 'simple'), k2a=(2, False, 'augment'), k3f=(3, True, 'simple'))[v]
        net = anet.Net(0, n=n, L=L, sigma=0.0, W=W64)
        kind_e = {'simple': KH.SIMPLE, 'augment': KH.AUGMENT}[kind]
        mlp = KN.arc_mlp(net, L, DT).to(DEV)
        counter = NamedFlopCounter(); ta = time.time()
        with counter:
            with flop_name('kprop'):
                K_in = {1: torch.zeros(n, dtype=DT, device=DEV), 2: torch.eye(n, dtype=DT, device=DEV)}
                K = KH.coerce_input(K_in, k_max=k_max, kind=kind_e)
                for l in range(L):
                    K = KH.linear_kprop(K, mlp.Ws[l].weight, k_max=k_max, set_metric=mlp.init_scale[l], bias=None)
                    K = KH.nonlin_kprop(K, nonlin_wick_coef=WICK_COEF_D['relu'], k_max=k_max, kind=kind_e, use_pK=True, factor=factor)
                mean = K[1].to_tensor().clone()
        fl = counter.total()
        json.dump(dict(net=NET, n=n, L=L, variant=v, mean=mean.cpu().numpy().tolist(), flops=float(fl), secs=time.time() - ta,
                       device=torch.cuda.get_device_name(0)), open(os.path.join(OUT, f'{pref}arc_{tag}_{v}.json'), 'w'))
        print(f'arc {NET} {v}: flops {fl:.3e} passes {passes(fl):.0f} {time.time() - ta:.1f}s', flush=True)
        del mlp, K; torch.cuda.empty_cache()

elif JOB == 'sl3':
    lv = load_lv()
    ns = dict(math=math, torch=torch, HTensor=HTensor, FactoredTensor=FactoredTensor, dev=DEV, dt=DT)
    src = os.path.join(HERE, 'tp', 'descale_fac_src.py')
    exec(compile(open(src).read(), src, 'exec'), ns)

    def gamma_law(V):
        s1 = lv.gmom(V, .5)
        E = {k: lv.gmom(V, k / 2) / s1 ** k for k in range(1, 5)}
        return {1: 1.0, 2: E[2] - 1, 3: E[3] - 3 * E[2] + 2, 4: E[4] - 4 * E[3] - 3 * E[2] ** 2 + 12 * E[2] - 6}, E
    ns['lognormal_cums'] = gamma_law
    Ws = [w.to(DEV, DT).contiguous() for w in W64]
    kind_e = kh.Kind.SIMPLE; wick = kh.WICK_COEF_D['relu']; Vs = []; ta = time.time()
    fc = NamedFlopCounter()
    with fc:
        with flop_name('sl3'):
            K = kh.coerce_input({1: torch.zeros(n, dtype=DT, device=DEV), 2: torch.eye(n, dtype=DT, device=DEV)}, k_max=3, kind=kind_e)
            for l in range(L):
                K = kh.linear_kprop(K, Ws[l], k_max=3, set_metric=2.0)
                K = kh.nonlin_kprop(K, nonlin_wick_coef=wick, k_max=3, kind=kind_e, use_pK=True, factor=True)
                if l < L - 1:
                    Sg = K[2].core; tau = K[4].core
                    num = float(tau) * (n * n + 2 * n) / 3.0
                    den = float(torch.trace(Sg)) ** 2 + 2 * float((Sg * Sg).sum())
                    V = min(max(num / den, 0.0), 0.999); Vs.append(V)
                    if V > 0:
                        K = ns['descale_tower'](K, V, n)
            h = K[1].core.double()
    fl = float(fc.total())
    json.dump(dict(net=NET, n=n, L=L, mean=h.cpu().numpy().tolist(), Vs=Vs, flops=fl, secs=time.time() - ta,
                   device=torch.cuda.get_device_name(0)), open(os.path.join(OUT, f'{pref}sl3_{tag}.json'), 'w'))
    print(f'sl3 {NET}: flops {fl:.3e} passes {passes(fl):.0f} {time.time() - ta:.1f}s', flush=True)

elif JOB == 'cov':
    cnt = 0; ta = time.time()
    fc = NamedFlopCounter()
    with fc:
        with flop_name('covprop'):
            mu = torch.zeros(n, dtype=DT, device=DEV); cov = torch.eye(n, dtype=DT, device=DEV)
            for l in range(L):
                w = W64[l].to(DEV, DT)
                mu_pre = w @ mu; cov_pre = w @ cov @ w.T
                var_pre = torch.clamp(torch.diagonal(cov_pre), min=1e-12); sig = torch.sqrt(var_pre)
                a = mu_pre / sig
                phi = torch.exp(-0.5 * a * a) / math.sqrt(2 * math.pi)
                Phi = torch.special.ndtr(a); cnt += a.numel()
                mu = mu_pre * Phi + sig * phi
                ez2 = (mu_pre * mu_pre + var_pre) * Phi + mu_pre * sig * phi
                var_post = torch.clamp(ez2 - mu * mu, min=0.0)
                gain = torch.where(sig > 1e-12, Phi, torch.zeros_like(Phi))
                cov = torch.outer(gain, gain) * cov_pre
                cov.diagonal().copy_(var_post)
    fl = float(fc.total() + cnt)
    json.dump(dict(net=NET, n=n, L=L, mean=mu.cpu().numpy().tolist(), flops=fl, secs=time.time() - ta,
                   device=torch.cuda.get_device_name(0)), open(os.path.join(OUT, f'{pref}cov_{tag}.json'), 'w'))
    print(f'cov {NET}: flops {fl:.3e} passes {passes(fl):.0f} {time.time() - ta:.1f}s', flush=True)

elif JOB == 'rqmc':
    from scipy.stats import qmc
    from scipy.special import ndtri
    ms = [int(a) for a in ARGS[0].split(',')]; R = int(ARGS[1])
    Wt = [w.to(DEV, torch.float32).T.contiguous() for w in W64]
    res = dict(net=NET, n=n, L=L, R=R, rows=[], device=torch.cuda.get_device_name(0))
    for m in ms:
        Nq = 1 << m; s0 = sum(map(ord, tag)) * 10 + m
        reps = np.zeros((R, n))
        for r in range(R):
            eng = qmc.Sobol(d=n, scramble=True, seed=int(s0) * 1000 + r)
            s = torch.zeros(n, dtype=DT, device=DEV); done = 0
            while done < Nq:
                k = min(1 << 13, Nq - done)
                u = np.clip(eng.random(k), 1e-12, 1 - 1e-12)
                h = torch.from_numpy(ndtri(u)).to(DEV, torch.float32)
                for l in range(L):
                    h = torch.relu(h @ Wt[l])
                s += h.double().sum(0); done += k
            reps[r] = (s / Nq).cpu().numpy()
        res['rows'].append(dict(m=m, N=Nq, est=reps.tolist()))
        print(f'rqmc {NET} m={m} {time.time() - t0:.0f}s', flush=True)
    json.dump(res, open(os.path.join(OUT, f'{pref}rqmc_{tag}.json'), 'w'))
else:
    raise ValueError(JOB)
