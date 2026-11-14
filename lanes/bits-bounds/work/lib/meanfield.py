"""Mean-field (infinite-width, annealed) recursions for the bits-bounds lane.

Three trajectories through the same future layers l+1..L: the true state h_j, the reference c_j, and the frozen-gate
propagation v_j of h with c's gates (v_l = h_l). At infinite width with He weights all norms are preserved, the
reference and the frozen vector keep their angle (c.v is preserved, |v| preserved), and only two angles evolve:
    phi_j = angle(h_j, c_j)   (true trajectories; arc-cosine kernel contraction)
    psi_j = angle(h_j, v_j)   (true versus frozen)
The frozen-gate residual at the output is |h_L - v_L|^2 = 2 |h|^2 (1 - cos psi_L); the radial-merge residual
(h projected on the reference ray, then the reference's future) is |h_L - |h| c_L / |c||^2 = 2 |h|^2 (1 - cos phi_L).
Derivation: per unit, (X, Y, Z) = (w.h, w.c, w.v) jointly Gaussian; h'.v' = 2 |h|^2 E[X 1{X>0} 1{Y>0} Z] for unit
variances; write Z = a X + b Y + e with e independent of (X, Y); E[X^2 1{X>0,Y>0}] = (pi - t + sin t cos t)/(2 pi),
E[X Y 1{X>0,Y>0}] = (sin t + (pi - t) cos t)/(2 pi), t = angle between X and Y.
"""
import math
import numpy as np


def kappa(t):
    """Normalised arc-cosine kernel of degree 1: cos of the next angle given cos t of the current one."""
    t = min(1.0, max(-1.0, t))
    return (math.sqrt(max(0.0, 1.0 - t * t)) + (math.pi - math.acos(t)) * t) / math.pi


def step(phi, psi, phi0):
    """One layer: returns (phi', psi'). phi0 = angle(c, v) (constant), phi = angle(h, c), psi = angle(h, v)."""
    cxy, cxz, cyz = math.cos(phi), math.cos(psi), math.cos(phi0)
    det = 1.0 - cxy * cxy
    if det < 1e-300:
        a, b = cxz, 0.0
    else:
        a = (cxz - cxy * cyz) / det
        b = (cyz - cxy * cxz) / det
    t = phi
    e_xx = (math.pi - t + math.sin(t) * math.cos(t)) / (2 * math.pi)
    e_xy = (math.sin(t) + (math.pi - t) * math.cos(t)) / (2 * math.pi)
    cos_psi_new = 2.0 * (a * e_xx + b * e_xy)
    cos_phi_new = kappa(cxy)
    return math.acos(min(1.0, max(-1.0, cos_phi_new))), math.acos(min(1.0, max(-1.0, cos_psi_new)))


def residuals(phi, Lp):
    """Mean-field residuals after Lp future layers for a pair at angle phi (equal norms, |h| = 1):
    returns (frozen, radial) = (2(1 - cos psi_L), 2(1 - cos phi_L))."""
    ph, ps = phi, 0.0
    for _ in range(Lp):
        ph, ps = step(ph, ps, phi)
    return 2.0 * (1.0 - math.cos(ps)), 2.0 * (1.0 - math.cos(ph))


if __name__ == '__main__':
    for Lp in [1, 4, 16, 48]:
        print(f"L'={Lp}")
        for phi in [1e-3, 3e-3, 1e-2, 3e-2, 0.1, 0.3, 1.0]:
            fr, ra = residuals(phi, Lp)
            print(f"  phi={phi:.0e} frozen={fr:.3e} (/(L' phi^3)={fr / (Lp * phi ** 3):.4f}) radial={ra:.3e}"
                  f"  exact-1layer={(2 / math.pi) * (phi - math.sin(phi) * math.cos(phi)):.3e}")
