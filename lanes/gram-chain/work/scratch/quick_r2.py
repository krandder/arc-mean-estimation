"""Quick R=2 checks for the explainer: exact-L0 fixed point vs chain, tau_delta, radius-ratio SD, single-injection decay."""
import sys, numpy as np, math, time
sys.path.insert(0, 'lib')
import gram_chain_v1 as gc
def kappa(c):
    c=min(max(c,-1.0),1.0); return (math.sqrt(max(1-c*c,0.0))+(math.pi-math.acos(c))*c)/math.pi
def fp(Q, c=0.0):
    lo, hi = 1e-12, 2.0
    for _ in range(100):
        d = 0.5*(lo+hi)
        if d*(Q+1) - (1-c) - Q*(1-kappa(1-d)) > 0: hi = d
        else: lo = d
    return 0.5*(lo+hi)
for n in [16, 64, 256]:
    rng = np.random.default_rng(11)
    P = 4000 if n < 256 else 1000
    Q0 = gc.sample_Q_stationary(n, P, rng, steps=40*n)
    G = np.repeat(Q0[:, None, None], 2, 1).repeat(2, 2).astype(float)
    lab = np.array([[1,0],[0,1]])
    T = 6*n
    trace = []
    for t in range(T):
        G = gc.step(G, lab, n, rng)
        if t >= T - 64:
            d = gc.diffs(G, n); trace.append(1 - d['rho'])
    tr = np.array(trace)  # (64, P)
    Qm = 0.5*(G[:,0,0]+G[:,1,1])
    L0 = np.array([fp(q) for q in Qm])
    dl = tr[-1]
    # autocorrelation of delta/L0 residual over lags
    x = tr / L0[None, :]; x = x - x.mean(0, keepdims=True)
    ac = [np.mean(x[:-k or None]*x[k:]) / np.mean(x*x) for k in (1, 2, 4, 8, 16)]
    l12 = 0.5*np.log(G[:,0,0]/G[:,1,1])
    print('n=%d: E delta/E L0(Q)=%.3f  median(delta/L0)=%.3f  sd(delta/L0)=%.3f  ac(lag 1,2,4,8,16)=%s  1.49 Qmed^(1/3)=%.1f  sd(l12) n^(1/3)=%.2f' % (
        n, dl.mean()/L0.mean(), np.median(dl/L0), np.std(dl/L0), np.round(ac, 2), 1.49*np.median(Qm)**(1/3), np.std(l12)*n**(1/3)), flush=True)
