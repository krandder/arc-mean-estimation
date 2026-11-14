# gpt-6-astra round 4 answer (extracted from astra_r4.raw; model line gpt-6-astra; r4 exit 0 09:45:38Z)

**PROVEN UNDER local-error and Gram hypotheses:** the radial recursion has nMSE \(\Theta(\alpha/n)\). Cap concentration alone does not establish those hypotheses.  
**CONJECTURE:** a stable matrix-cost angular correction improves this rate; neither diagonal skewness nor a third-moment trace currently proves it.  
**PROVEN UNDER a multiplicative-amplitude error model:** the quoted \(0.04\%\) independent and \(0.007\%\) systematic per-layer tolerances are correct.

I read the requested files and scripts, read-only. Numerical observations below are the supplied **MEASURED** inputs; their interpretations have separate labels. Recall failed because of the read-only environment and SSH configuration.

**1. The recursion’s own defects and the \(p_{\mathrm{full}}=1\) claim**

**PROVEN.** Write the ideal recursion as
\[
\widetilde P_\ell=\Phi_\ell Q_{\ell-1},\qquad
Q_\ell=\Pi_{\mathrm{rad}}\widetilde P_\ell,\qquad Q_0=P_0.
\]
For the monotone-transport version,
\[
\Pi_{\mathrm{rad}}P
=\mathcal L\!\left[
\frac{F^{-1}_{R_P}(F_{\|G\|}(\|G\|))}{\|G\|}G
\right],
\quad
G\sim N(m_P,C_P).
\]
This preserves the radius marginal of \(P\). It generally changes its mean and covariance.

Take the last step exactly, as in `run_ipr2.py`, so \(Q_L=\Phi_LQ_{L-1}\). Define
\[
\Delta_\ell=Q_\ell-\widetilde P_\ell,\qquad
e_\ell=\int g_\ell\,d\Delta_\ell,\qquad t_\ell=L-\ell.
\]
Then A1 and A2 give
\[
\boxed{\widehat Y-Y=\sum_{\ell=1}^{L-1}e_\ell,}
\]
\[
\boxed{
\mathbb E\!\left[\|e_\ell\|^2\mid W_{\le\ell}\right]
=\sum_{d\ge1}b_d^{(n,t_\ell)}
       \|M_d(\Delta_\ell)\|_F^2.
}
\tag{R1}
\]
The \(d=0\) term vanishes because the projection preserves its **own push-forward’s** radius marginal. The \(d=1\) term need not vanish.

These are not the oracle single-cut defects
\(\Pi_{\mathrm{rad}}P_\ell-P_\ell\). Substituting those into the telescoping sum would be incorrect.

For normalization, use
\[
\overline V=\mathbb E_W V(W),\qquad
\mathcal R=\frac{\mathbb E_W\|\widehat Y-Y\|^2}{\overline V}.
\]
A2 directly prices the numerator. It does not directly price division by the future-dependent \(V(W)\), or medians of per-net nMSE. The earlier \(\overline V=\Theta_\alpha(1)\) result transfers absolute-error exponents to \(\mathcal R\); transferring them to measured medians needs additional distributional control.

**PROVEN UNDER \(H_{\rm shell}\).** Round 3 established an \(\Omega(n^{-2})\) first-layer priced defect. It did **not** establish a matching \(O(n^{-2})\) bound. Thus “the first-layer exponent is 2” is stronger than the theorem.

At a middle layer, the following makes the missing assumption precise.

Let
\[
\nu_P(du)=\mathbb E_P[R\mid U=u]P_U(du)
\]
be the radius-weighted direction measure. Suppose both \(\widetilde P_\ell\) and \(Q_\ell\) have radius scale \(\sqrt n\), and their relevant directions lie in a common cap
\[
u_n(z)=\frac{v+z/n}{\|v+z/n\|},\qquad z\perp v.
\]
Push their weighted difference into these tangent coordinates:
\[
\nu_{Q_\ell}-\nu_{\widetilde P_\ell}
=\sqrt n\,(u_n)_\#\sigma_{\ell,n},
\qquad \int d\sigma_{\ell,n}=0.
\]

Assume the **finite-width** suffix kernel, at \(t_\ell/n\to\beta>0\), satisfies
\[
\kappa_{n,t_\ell}(u_n(z)\!\cdot u_n(z'))
=1-\frac{\Psi_\beta(z,z')}{n^2}+r_{\ell,n}(z,z'),
\tag{R2}
\]
with negligible off-cap contributions and sufficient control of the signed integrals of \(r_{\ell,n}\).

**PROVEN UNDER these cap and remainder hypotheses.**
\[
\mathbb E_F\|e_\ell\|^2
=-\frac1n\iint\Psi_\beta\,d\sigma_{\ell,n}d\sigma_{\ell,n}
+\text{controlled remainder}.
\tag{R3}
\]
Consequently:

- An order-one discrepancy in the priced tangent profile gives a one-step defect of order \(n^{-1}\).
- A discrepancy of order \(n^{-1/2}\) in that profile gives a one-step defect of order \(n^{-2}\).
- Smaller discrepancies can give faster decay.

For the second case, an explicit sufficient hypothesis is
\[
\sigma_{\ell,n}=n^{-1/2}\tau_{\ell,n},\qquad
-\iint\Psi_\beta\,d\tau_{\ell,n}d\tau_{\ell,n}\longrightarrow B_\ell>0,
\]
and
\[
\iint r_{\ell,n}\,d\tau_{\ell,n}d\tau_{\ell,n}=o(n^{-2}).
\]
Then
\[
\boxed{\mathbb E_F\|e_\ell\|^2=B_\ell n^{-2}+o(n^{-2}).}
\tag{R4}
\]
The convergence can be formulated in the kernel’s seminorm; total-variation convergence is unnecessary.

**HEURISTIC.** There is a possible local mechanism for (R4). A cap of width \(1/n\) crosses a fresh row’s gate boundary with probability \(O(1/n)\), giving \(O(1)\) borderline neurons. With radius \(\sqrt n\) and He weights, their nonlinear output perturbations have size \(O(1/n)\). Their squared perturbation is therefore \(O(n^{-2})\).

That becomes an upper-bound argument only if the projection reproduces the linearly propagated part accurately and introduces no larger radius-direction or mean error. Nondegeneracy is additionally needed for a lower bound. These properties have not been established for the measured reconstruction.

**PROVEN.** This separates the two uses of the cap hypothesis:

- Round 3’s oracle single-cut \(H_{\rm cap}\) permits an order-one profile discrepancy and an \(n^{-1}\) error.
- An \(n^{-2}\) **local** defect requires a smaller discrepancy between the closure’s own push and its projection.

The first statement does not imply the second.

To accumulate local defects, set
\[
D_\ell=\frac{\mathbb E\|e_\ell\|^2}{\overline V},\qquad
G_{\ell k}=\frac{\mathbb E[e_\ell\cdot e_k]}{\overline V}.
\]
Then
\[
\mathcal R=\mathbf1^\top G\mathbf1.
\]
For nonzero diagonal entries, define the normalized Gram matrix
\[
C_{\ell k}=\frac{G_{\ell k}}{\sqrt{D_\ell D_k}}.
\]

**PROVEN UNDER the following hypotheses:**

1. \(\sum_\ell D_\ell=\Theta(L/n^2)\). Sufficient conditions are \(D_\ell=O(n^{-2})\) throughout, with \(D_\ell\ge c n^{-2}\) on a positive fraction of layers. Early and terminal layers must also satisfy the required aggregate bound.
2. The Gram matrix satisfies
   \[
   cI\preceq C\preceq CI
   \]
   with positive constants independent of \(n\).

Then
\[
\boxed{\mathcal R=\Theta(L/n^2)=\Theta(\alpha/n).}
\tag{R5}
\]
For fixed \(\alpha\), this gives \(p_{\rm full}=1\). Uniform dependence on \(\alpha\) requires uniform hypothesis constants.

Pairwise \(L^2\)-orthogonality suffices in place of the Gram bounds. Independence plus zero means also suffices. Independent weight matrices alone do not: the \(e_\ell\) share suffix weights.

A lower Gram bound alone proves only \(\mathcal R=\Omega(\alpha/n)\). Without an upper correlation bound, aligned defects of squared size \(n^{-2}\) can accumulate to order \(L^2/n^2\).

**HEURISTIC, interpreting the supplied measurements.**
\[
p_{\rm radial}
=\frac{\log(1.8\times10^{-3}/4.8\times10^{-4})}{\log4}
=0.953,
\]
which is consistent with (R5), but does not identify its mechanism. The Gaussian slope is approximately \(0.404\). That is compatible with an \(\Omega(n^{-1})\) Gaussian lower bound: a lower bound permits slower decay.

The measured first-cut slope \(2.5\) also does not refute the asymptotic, annealed \(\Omega(n^{-2})\) result with its small coefficient.

**PROVEN UNDER (R5), matrix cost, and the earlier multilevel hypotheses.** At \(O(Jn^3)\) per layer, cost is \(\Theta(Jn)\) forward passes. Equation (34), with \(K=2,p=1\), gives
\[
G_{\rm MC}=\Theta(J^{-1}),\qquad
G_{\rm multilevel}=O\!\left(\frac{\log^2 n}{Jn}\right).
\tag{R6}
\]
Thus the measured radial rate is consistent with constant gain over MC at its own cost and a growing disadvantage to the multilevel comparator.

**2. Can a matrix-cost correction remove the next angular order?**

**PROVEN.** The trace of the radius-normalized third feature is
\[
\boxed{(\operatorname{tr}M_3)_i
=\int R\,u_i\sum_j u_j^2\,dP
=\int h_i\,dP=M_{1,i}.}
\tag{R7}
\]
Therefore matching the trace sector of \(M_3\) adds no information once the mean is matched. The present radial projection can change the mean, so restoring it may help; that does not remove the traceless cubic discrepancy.

The trace of the **central third cumulant**, \(\operatorname{tr}\kappa_3\), is a different statistic.

**PROVEN.** For a symmetric cubic tensor \(T\), with \(t=\operatorname{tr}T\),
\[
T^{\rm trace}_{ijk}
=\frac{\delta_{ij}t_k+\delta_{ik}t_j+\delta_{jk}t_i}{n+2},
\qquad
\|T^{\rm trace}\|_F^2=\frac{3\|t\|^2}{n+2}.
\]
For the diagonal skewness tensor
\[
T=\gamma_3\sum_i e_i^{\otimes3},
\]
its total energy is \(n\gamma_3^2\), while its trace-sector energy is
\[
\frac{3n\gamma_3^2}{n+2}.
\]
Trace augmentation removes only a fraction \(3/(n+2)\) of this tensor’s energy. It cannot remove the leading diagonal-skewness obstruction by itself.

**PROVEN.** Matching diagonal third cumulants does not generally control mixed third cumulants. A relevant first-layer calculation illustrates why. For
\[
X_i=\sqrt2(Z_i)_+,\qquad
\operatorname{Corr}(Z_i,Z_j)=\rho_{ij},\qquad a=\pi^{-1/2},
\]
the Hermite expansion gives
\[
\kappa(X_i,X_i,X_j)=a\rho_{ij}+O(\rho_{ij}^2).
\tag{R8}
\]
Random first-layer rows have \(\rho_{ij}=O_{\mathbb P}(n^{-1/2})\). Across \(O(n^2)\) mixed entries, these terms can have squared Frobenius norm \(\Theta(n)\), the same order as the diagonal tensor.

Transferring (R8) to an \(M_3\) lower bound requires normalization-remainder control, but it already defeats the argument that diagonal skewness is automatically the whole leading cubic correction.

**PROVEN UNDER a structured cubic-dominance hypothesis.** A matrix-cost improvement is possible if all of the following hold:

- The leading relevant third tensor has a representation
  \[
  T_\ell=\sum_{a=1}^{r_\ell}c_a v_a^{\otimes3}+E_\ell,
  \qquad r_\ell=O(n),\qquad \|E_\ell\|_F^2=o(n).
  \]
- Its factors and coefficients can be updated through the nonlinear projection in \(O(Jn^3)\), without accumulating an uncompressed factor list.
- After correction,
  \[
  M_3(\Delta_\ell)=n^{-1}E_\ell+o_F(n^{-1/2}),
  \qquad b_3^{(n,t_\ell)}=O(n^{-1}),
  \]
  with corresponding mean and radius control.
- All other priced sectors together contribute \(o(n^{-2})\).

Then its one-step priced defect is \(o(n^{-2})\). Multiplying an \(n\times O(n)\) factor matrix by \(W_\ell\) costs \(O(n^3)\); the unproved part is maintaining such a representation after gating and reconstruction.

**CONJECTURE.** Such a stable representation exists for the radial recursion’s *innovations*. The current measurements neither establish nor exclude it. Low rank of the true cloud’s third cumulant does not establish it for these innovations or for the full future-priced error.

**PROVEN.** There is also no general guarantee from retaining the full third cumulant alone. Distinct clouds on a common sphere can agree through degree three and differ in positively priced higher features. A cubic correction therefore needs a higher-sector remainder theorem.

Accordingly, neither “diagonal third cumulants suffice” nor “the full third tensor is computationally necessary” is presently proved.

**PROVEN UNDER transfer of ARC’s error-cost ladder to a radial hierarchy.** Suppose additional orders cost a factor \(n\) and reduce error by a factor \(q\):
\[
C_r=C_0n^r,\qquad e_r=e_0q^{-r}.
\]
Ignoring the bounded staircase effect between orders,
\[
\boxed{e(C)\asymp e_0(C/C_0)^{-\gamma_n},
\qquad \gamma_n=\frac{\log q}{\log n}.}
\tag{R9}
\]
For \(q=4\)–\(8\) and \(n=256\),
\[
\gamma_{256}=0.25\text{–}0.375,
\]
versus MC’s exponent \(1\). Radial correction improves the starting error \(e_0\); it does not improve this precision exponent unless it changes the subsequent ladder.

**HEURISTIC.** ARC’s measurements motivate this conditional concern. They do not establish the ladder for a new radial hierarchy, or uniformly over arbitrarily high orders. The width exponent \(p_{\rm full}\approx1\) and the fixed-problem precision exponent \(\gamma_n\) are different quantities.

**3. Amplitude accuracy and quadrature**

**PROVEN UNDER multiplicative scale errors and scale-equivariant updates.** Suppose layer \(\ell\) introduces a small relative amplitude error \(\delta_\ell\). Positive homogeneity gives
\[
Y_{\rm perturbed}
=\left[\prod_{\ell=1}^{L}(1+\delta_\ell)\right]Y_{\rm baseline}.
\]
To first order,
\[
\frac{\|Y_{\rm perturbed}-Y_{\rm baseline}\|^2}{V}
=A\left(\sum_{\ell=1}^{L}\delta_\ell\right)^2,
\qquad A=\frac{\|Y_{\rm baseline}\|^2}{V}.
\tag{R10}
\]

If errors are independent, centered, and have RMS size \(\delta\), their expected contribution is \(AL\delta^2\). If they are equal systematic errors, it is \(AL^2\delta^2\). Allocating nMSE \(\varepsilon\) to numerical amplitude error therefore requires
\[
\boxed{
\delta_{\rm independent}\lesssim\sqrt{\frac{\varepsilon}{AL}},
\qquad
\delta_{\rm systematic}\lesssim\frac1L\sqrt{\frac{\varepsilon}{A}}.
}
\tag{R11}
\]
With \(A=20,L=32,\varepsilon=10^{-4}\),
\[
\delta_{\rm independent}\lesssim3.95\times10^{-4}=0.0395\%,
\]
\[
\delta_{\rm systematic}\lesssim6.99\times10^{-5}=0.00699\%.
\]

**PROVEN.** The exact A2 contribution of a mean-radius defect is
\[
b_0^{(n,t_\ell)}(\Delta r_\ell)^2.
\]
For a coherent scale error, however, **all** features scale, and (R10) already gives the exact first-order sensitivity. Multiplying \(A\) by \(b_0\) is not an additional exact correction.

**HEURISTIC.** Using \(b_0A\approx19\) as a radius-dominated proxy gives \(0.0406\%\) and \(0.00717\%\), explaining the quoted rounded figures.

These tolerances concern amplitude modes that affect homogeneous queries. They are not a bound on an arbitrary CDF-distance between radius laws. Radius-direction coupling also matters. Moreover, this is a numerical-error budget: improving quadrature cannot by itself reduce a closure bias of \(4.8\times10^{-4}\) below \(10^{-4}\).

For equation (40), one defensible quadrature is log-scale sinc quadrature.

**PROVEN.** For \(a=p/2\), \(q>0\), and the relevant homogeneous numerator \(f\),
\[
\mathbb E\frac{f(G)}{\|G\|^p}
=
\frac{q^{-a}}{\Gamma(a)}
\int_{-\infty}^{\infty}
e^{ax}\,
\mathbb E\!\left[f(G)e^{-e^x\|G\|^2/q}\right]dx.
\tag{R12}
\]
Apply the trapezoidal rule at \(x_j=jh\), \(-M\le j\le M\), with \(J=2M+1\).

The tilted Gaussian has
\[
C_s=(I+2sC)^{-1}C,\qquad
m_s=(I+2sC)^{-1}m,
\]
and normalizing factor
\[
Z_s=\det(I+2sC)^{-1/2}
\exp[-s\,m^\top(I+2sC)^{-1}m].
\]
Each node therefore uses the Gaussian calculations described in round 3.

**PROVEN UNDER analytic-strip, tail, and update-stability hypotheses.** Suppose the scaled integrands have a uniformly controlled analytic strip \(|\operatorname{Im}x|<d\), exponential tails, and relative errors propagate to the needed amplitude statistic with bounded sensitivity. Standard sinc estimates give
\[
\delta_J
\le C_1e^{-2\pi d/h}
   +C_2e^{-c_-Mh}
   +C_3e^{-c_+Mh}.
\]
Balancing discretization and truncation errors yields
\[
\boxed{\delta_J\le C_Qe^{-c_Q\sqrt J},
\qquad
J=O\!\left(\log^2\frac{C_Q}{\delta_{\rm required}}\right).}
\tag{R13}
\]
Thus (R11) gives, conditionally,
\[
J_{\rm independent}
=O\!\left(\log^2\!\left[C_Q\sqrt{AL/\varepsilon}\right]\right),
\]
\[
J_{\rm systematic}
=O\!\left(\log^2\!\left[C_QL\sqrt{A/\varepsilon}\right]\right).
\tag{R14}
\]

The constants and uniformity have not been established for the reachable states. Consequently, no defensible numerical value of \(J\), particularly \(J=1\)–\(3\), follows yet. Deterministic quadrature errors also need systematic-error accounting unless decorrelation is demonstrated.

**PROVEN.** Equation (40) applies to the independent-radius reconstruction. The measured monotone-transport reconstruction couples radius to Gaussian norm. Transferring its observed error to the independent-radius/lognormal implementation requires a separate argument. Accurate quadrature also does not eliminate lognormal modeling bias.

**4. Brief audit**

For [E10](/home/agent/workspaces/mats/work/arc-update/FORMAL.md:384):

- **PROVEN correction:** retain the first-layer result as an asymptotic lower bound, not an established \(\Theta(n^{-2})\) law or certified finite-\(n\) bound.
- **PROVEN correction:** after radius matching, the complete residual includes \(b_1\|M_1\|^2\). The displayed \(d\ge2\) sum is only that sector unless mean preservation or negligibility is assumed.
- **PROVEN correction:** the cap calculation prices the actual signed discrepancy inserted into it. It does not supply the smaller local discrepancy required by (R4).
- **HEURISTIC cost claim:** “one quadrature node equals 393 passes” is an unimplemented constant-factor estimate. \(O(Jn^3)\) does not prove it.
- **PROVEN distinction:** independent radius, lognormal radius, and monotone transport are different reconstructions. The experimental result is not automatically an upper or lower bound for all three.

For [E11](/home/agent/workspaces/mats/work/arc-update/FORMAL.md:440):

- **PROVEN:** \(b_0=\kappa_{n,t}(0)\), since \(\kappa_{n,t}(1)=1\). The estimator’s ratio-of-averages and delta-method SE are appropriate numerical procedures.
- **PROVEN correction:** the \(\Omega(1/n)\) finite-width lower bound establishes nonuniformity of the infinite-width approximation. It does not force a factor-two discrepancy at \(n=256,t=31\). Replace “as E10.6 says it must be” with “consistent with E10.6.”

For [section 4.4](/home/agent/workspaces/mats/work/arc-update/arc-update.md:385):

- **PROVEN correction:** “three measurements bound what any version can do” overstates the evidence. They evaluate specified projections and numerical recursions.
- **PROVEN correction:** independent replicate cross-products satisfy
  \[
  \mathbb E[(\widehat Y_A-Y)\cdot(\widehat Y_B-Y)]
  =\|\mathbb E\widehat Y_A-Y\|^2.
  \]
  This removes replicate variance, not bias from finite-sample covariance fitting, empirical quantiles, or finite-batch rank transport. The script correctly says “noise-averaged closure”; “exact per-layer moments” is an approximation requiring convergence evidence. Shared estimated truth adds a further small qualification.
- **HEURISTIC:** the proposed \(n^{-2}\)-per-layer accumulation mechanism is plausible under (R4)–(R5), but neither single-cut scaling nor the total slope establishes it.
- **PROVEN correction:** three widths and a \(1.4\times\) window increase do not establish “neither grows polynomially.”
- **PROVEN arithmetic:** a gain \(g\) at assumed \(J=1\) becomes approximately \(g/J\). A gain near \(3\) can permit a win at \(J=2\); winning does not require \(J=1\).
- **HEURISTIC wording correction:** the supplied radial result is modestly better than ARC augment at \(256\), by about \(1.75\times\). “Does about as well, not better” is too categorical.
- **PROVEN correction:** \(b_0\approx0.95\) applies to long suffixes here, not every remaining depth: the supplied values are about \(0.82,0.91,0.95\) at \(t=8,16,31\).

**CONJECTURE, with a concrete test:** measure the recursion’s own \(\Delta_\ell\), their suffix-priced diagonal energies, and their cross-layer Gram contribution. Those measurements would distinguish the proposed \(n^{-2}\)-per-step mechanism from correlated, boundary-dominated, or compensating errors that produce the same observed full-recursion slope.
