import math, mpmath as mp
mp.mp.dps = 40
def f(d):  # 1 - kappa(1 - d)
    th = mp.acos(1 - d)
    return d - (mp.sin(th) - th*mp.cos(th))/mp.pi
ck = 2*mp.sqrt(2)/(3*mp.pi); e = 1/(15*mp.sqrt(2)*mp.pi)
for d in [mp.mpf('1e-2'), mp.mpf('1e-3'), mp.mpf('1e-4')]:
    r = (f(d) - (d - ck*d**1.5)) / d**2.5
    print('delta=%s  (f - (d - ck d^1.5))/d^2.5 = %s  (pred -%s)' % (d, mp.nstr(r, 8), mp.nstr(e, 8)))
def fp(Q, c):
    return mp.findroot(lambda d: d*(Q+1) - (1-c) - Q*f(d), ((1-c)/(ck*Q))**(mp.mpf(2)/3))
for c in [0, 0.5, -1]:
    for Q in [100, 1000, 10000]:
        eps = ((1-c)/(ck*Q))**(mp.mpf(2)/3)
        two = eps*(1 - (mp.mpf(2)/(3*(1-c)) + mp.mpf(1)/30)*eps)
        d = fp(mp.mpf(Q), mp.mpf(c))
        print('c=%s Q=%d exact=%s two-term=%s rel.err=%s  (rel.err/eps^2=%s)' % (c, Q, mp.nstr(d, 8), mp.nstr(two, 8), mp.nstr(two/d - 1, 4), mp.nstr((two/d-1)/eps**2, 4)))
