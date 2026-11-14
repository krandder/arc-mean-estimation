"""The recursion with analog (Gaussian-channel) codes on the linear-Gaussian chain, in closed form.
h_l = rho h_{l-1} + s xi_l (stationary N(0, 1)); the code at layer l is z_l = b_l h_l + nu_l, nu_l ~ N(0, 1) (for jointly
Gaussian variables the information-bottleneck optimum is of this form; Chechik et al. 2005). The output code is
z_{L-1} = b h_{L-1} + nu with I(h; z) = R_out bits. Then, exactly:
  T_l = I(h_l; z_{l+1}) = 0.5 log2(1 + b_{l+1}^2 rho^2 / (1 + b_{l+1}^2 s^2)),   rate(z_l) = 0.5 log2(1 + b_l^2),
  I(z_l; z_{l+1}) = -0.5 log2(1 - r^2), r = b_l b_{l+1} rho / sqrt((1 + b_l^2)(1 + b_{l+1}^2)),
  truth I(h_l; z_{L-1}) with rho^m, s_m^2 = 1 - rho^(2m); I(z_l; z_{L-1}) likewise with the correlation of z_l and z_{L-1}.
Rate rule: rate(z_l) = T_l. Relevance rule: the least b_l with I(z_l; z_{l+1}) >= q T_l.
usage: exact_gauss_chain.py --rho 0.999 --L 16 --Rout 4.92"""
import argparse
import math

ap = argparse.ArgumentParser()
ap.add_argument('--rho', type=float, default=0.999)
ap.add_argument('--L', type=int, default=16)
ap.add_argument('--Rout', type=float, default=4.92)
args = ap.parse_args()
rho, L = args.rho, args.L
s2 = 1 - rho * rho
LOG2 = math.log(2)


def rate(b):
    return 0.5 * math.log2(1 + b * b)


def b_of_rate(R):
    return math.sqrt(2 ** (2 * R) - 1)


def T_of(bn):          # I(h_l; z_{l+1})
    return 0.5 * math.log2(1 + bn * bn * rho * rho / (1 + bn * bn * s2))


def mi_codes(b1, b2, m):   # I(z_l; z_{l+m}) for codes b1 at l, b2 at l+m
    r = b1 * b2 * rho ** m / math.sqrt((1 + b1 * b1) * (1 + b2 * b2))
    return -0.5 * math.log2(1 - r * r)


def truth(l, bL):      # I(h_l; z_{L-1})
    m = L - 1 - l
    rm2, sm2 = rho ** (2 * m), 1 - rho ** (2 * m)
    return 0.5 * math.log2(1 + bL * bL * rm2 / (1 + bL * bL * sm2))


bL = b_of_rate(args.Rout)
print(f"rho {rho}, L {L}, output code: analog with I(h; z) = {args.Rout} bits")
for rule, q in [('rate', None), ('relevance', 0.95), ('relevance', 0.99)]:
    b = {L - 1: bL}
    rows = []
    for l in range(L - 2, -1, -1):
        T = T_of(b[l + 1])
        if rule == 'rate':
            bl = b_of_rate(T)
        else:
            lo, hi = 0.0, 1e6
            for _ in range(200):
                mid = (lo + hi) / 2
                if mi_codes(mid, b[l + 1], 1) >= q * T:
                    hi = mid
                else:
                    lo = mid
            bl = hi
        b[l] = bl
        rows.append((l, truth(l, bL), T, rate(bl), mi_codes(bl, b[l + 1], 1), mi_codes(bl, bL, L - 1 - l)))
    name = 'rate rule (your rule)' if rule == 'rate' else f'relevance rule {q}'
    print(f"  {name}: l | truth | target | rate | carries about next | knows about output")
    for r in rows:
        if r[0] in (L - 2, L - 4, (L - 1) // 2, (L - 1) // 4, 0):
            print(f"    {r[0]:2d} | {r[1]:.3f} | {r[2]:.3f} | {r[3]:.3f} | {r[4]:.3f} ({r[4] / max(r[2], 1e-12):.0%}) | "
                  f"{r[5]:.3f} ({r[5] / r[1]:.0%})")
