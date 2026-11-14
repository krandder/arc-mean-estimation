import sys, numpy as np, math, time
sys.path.insert(0, 'lib')
import gram_chain_v1 as gc
for n in [16, 64, 256]:
    rng = np.random.default_rng(7)
    P = 2000 if n < 256 else 600
    Q0 = gc.sample_Q_stationary(n, P, rng, steps=40*n)
    R = 3
    G = np.repeat(Q0[:, None, None], R, 1).repeat(R, 2).astype(float)
    lab = np.tile(np.arange(R), (P, 1))
    t0 = time.time()
    for t in range(6*n):
        G = gc.step(G, lab, n, rng)
    d = np.sqrt(np.einsum('pii->pi', G)); rho = G/(d[:, :, None]*d[:, None, :])
    dl = np.stack([1-rho[:,0,1], 1-rho[:,0,2], 1-rho[:,1,2]], 1)
    Q = d**2
    Qm = Q.mean(1)
    l12 = 0.5*np.log(Q[:,0]/Q[:,1])
    # L0 prediction at each chain's mean radius
    ck = 2*math.sqrt(2)/(3*math.pi); eps = ck**(-2/3)*Qm**(-2/3); L0 = eps*(1-0.7*eps)
    asym = (dl.max(1)-dl.min(1))/dl.mean(1)
    c = np.corrcoef(dl[:,0]-dl.mean(1), dl[:,1]-dl.mean(1))[0,1]
    print('n=%d P=%d: E delta=%.4f, E L0(Qm)=%.4f ratio=%.3f; median Q/n=%.3f; CV(delta_12 | rel to L0)=%.3f; mean (max-min)/mean of 3 angles=%.3f; sd(l12)*n^(1/3)=%.3f; corr(d12,d13)=%.3f; %.0fs' % (
        n, P, dl.mean(), L0.mean(), dl.mean()/L0.mean(), np.median(Qm)/n, np.std(dl[:,0]/L0), asym.mean(), np.std(l12)*n**(1/3), np.corrcoef(dl[:,0], dl[:,1])[0,1], time.time()-t0), flush=True)
