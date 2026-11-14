import math
def kappa(c):
    c=min(max(c,-1.0),1.0); return (math.sqrt(max(1-c*c,0.0))+(math.pi-math.acos(c))*c)/math.pi
def fp(Q, c=0.0):
    # mean-field fixed point: delta (Q+1) = (1-c) + Q (1 - kappa(1-delta))
    lo, hi = 1e-12, 2.0
    for _ in range(200):
        d = 0.5*(lo+hi)
        g = d*(Q+1) - (1-c) - Q*(1-kappa(1-d))
        if g > 0: hi = d
        else: lo = d
    return 0.5*(lo+hi)
ck = 2*math.sqrt(2)/(3*math.pi)
for Q in [4.6, 9.2, 36.9, 147.7, 590.9, 2363.6]:
    e = ck**(-2/3)*Q**(-2/3)
    d = fp(Q)
    print('Q=%.1f exact=%.5f eps=%.5f eps(1-0.7eps)=%.5f ratio_exact/1term=%.4f /2term=%.4f' % (Q, d, e, e*(1-0.7*e), d/e, d/(e*(1-0.7*e))))
for n in [16, 64, 128, 256, 1024]:
    Q = 0.577*n
    d0 = fp(Q)
    print(n, " ".join("C(%.2f)=%.3f" % (t, 1-fp(Q,t)/d0) for t in (0.25,0.5,0.75)), " s_even=%.3f" % ((2 - fp(Q,-1.0)/d0)/2))
print('large-Q', [round(1-(1-t)**(2/3),3) for t in (0.25,0.5,0.75)], 'seven', round((2-2**(2/3))/2,3))
