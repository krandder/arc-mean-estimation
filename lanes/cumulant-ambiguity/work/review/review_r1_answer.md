codex
**0 — PROVEN, with a wording qualification.** Matching \(E[h_L]\) fixes \(E[f]=a^\top E[h_L]\). Thus any **nontrivial ambiguity claim** must exclude the final activation layer; the phrase “up to the output” itself is ambiguous.

**1 — PROVEN.** The feasible sets satisfy \(A_d(\mathrm{all})\subseteq A_d(\mathrm{last})\). Moreover, \(t_i^k=(w_i^\top h_{L-1})^k\) is a degree-\(k\) polynomial. Hence each feasible marginal of \(t_i\) matches its first \(d\) moments, and
\[
\operatorname{gap}_d(\mathrm{all})
\le \operatorname{gap}_d(\mathrm{last})
\le \sum_i |a_i|\Gamma_d(\mu_i).
\]
This is an upper bound, without any assertion that the marginal extrema are jointly realizable. For \(d=1\), a two-sided scalar range gives \(\Gamma_1=\infty\).

**2 — PROVEN; the compactness argument needs one addition.** For fixed weights, \(|t_i(x)|\le C\|x\|\), so \(E e^{\epsilon t_i^2}<\infty\) for some \(\epsilon>0\), implying moment determinacy. Given feasible \(\nu_d\), the fixed second moment gives tightness. For each \(k\), an eventually fixed higher even moment ensures uniform integrability of \(t^k\), so every subsequential limit matches **all** moments and equals \(\mu_i\). The fixed second moment also makes ReLU uniformly integrable. Thus \(\Gamma_d\to0\). Finite empirical reference laws satisfy the conclusion too.

**3 — PROVEN as an information lower bound; FALSE if “strictly” means always.** Every such estimator returns the same number \(c\) throughout \(A_d(\mathrm{input})\), and
\[
\sup_{Q\in A_d(\mathrm{input})}|c-E_Qf|
\ge \tfrac12\operatorname{gap}_d(\mathrm{input}).
\]
This applies to any estimator using only those input moments, regardless of propagation architecture. The all-layer oracle is weakly more informative and sometimes strictly more informative; \(L=1\) gives equality. This does **not** establish an error lower bound when inputs are promised to be Gaussian, rather than arbitrary members of the ambiguity set.

**4 — FALSE as a blanket conclusion; PROVEN for the stated parity pair if its last preactivation is the signed minimum.** Write
\[
g=\Bigl(\prod_j\operatorname{sign}x_j\Bigr)\min_j|x_j|.
\]
Conditioning independent Gaussian signs on positive parity preserves the requisite low-order input moments and doubles \(E[g_+]\), but changes \(E[g]\) from \(0\) to \(E[\min_j|x_j|]>0\). If \(t_i=g\), last-hidden-layer **first moments already exclude this alternative**. Such laws may nevertheless match some earlier layers. Claim 1 alone only bounds residual ambiguity; it does not prove that every parity-type construction fails against the oracle.

**(b) — PROVEN equality for \(L=1\), Gaussian input, one unit.** Let \(t=w^\top x\), \(\sigma=\|w\|>0\), \(u=w/\sigma\). For any scalar feasible law \(\nu\), take independently
\[
T\sim\nu,\qquad Z\sim N(0,I-uu^\top),\qquad X=uT/\sigma+Z.
\]
Every polynomial moment of \(X\) through degree \(d\) matches \(N(0,I)\), and \(w^\top X=T\). Therefore
\[
\boxed{\operatorname{gap}_d(\mathrm{all})=\Gamma_d(N(0,\sigma^2)).}
\]
This lifting argument does not automatically extend to empirical \(P_0\).

**(b), general lower bound — FALSE, even with Gaussian \(t\).** At width \(2\), depth \(2\), set
\[
h_1=(x_1^+,(-x_1)^+),\qquad t_1=h_{1,1}-h_{1,2}=x_1.
\]
Then \(f=t_1^+=h_{1,1}\), whose expectation is fixed by the first hidden-layer moments. Thus
\[
\operatorname{gap}_d(\mathrm{all})
=\operatorname{gap}_d(\mathrm{last})=0,
\qquad \Gamma_d(N(0,1))>0
\]
for every finite \(d\ge2\). No universal \(c>0\) exists.

**(c) — PROVEN: \(\Theta(1/d)\), with an explicit asymptotic constant.**
\[
\boxed{\Gamma_d(N(0,\sigma^2))
\sim \frac{\pi^{3/2}}{4\sqrt2}\frac{\sigma}{d}.}
\]
Consequently,
\[
\boxed{\frac{\Gamma_d}{\operatorname{sd}(T_+)}
\sim \frac{\pi^2}{4\sqrt{\pi-1}}\frac1d
=\frac{1.68605\ldots}{d}.}
\]
The reported \(1.4/d\) is a small-order fit, not the asymptotic constant.

Here is a quadrature proof. By symmetrization, put \(Y=T^2/2\sim\rho=\mathrm{Gamma}(1/2,1)\); the objective becomes \(E\sqrt Y/\sqrt2\). At \(d=4k\), let \(G_k\) be \(k\)-node Gauss quadrature for \(\rho\), and \(R_k\) the Radau rule with node \(0\) and \(k\) positive nodes. Hermite interpolation gives sharp bounds
\[
\Gamma_{4k}=\frac{G_k(\sqrt{\cdot})-R_k(\sqrt{\cdot})}{\sqrt2}.
\]
The lower endpoint is attained; the upper is approached by sending the prescribed node of a right-Radau rule to infinity.

For completeness, define
\[
A_k(s)=\frac{L_k^{-1/2}(-s)}{L_k^{-1/2}(0)},\quad
B_k(s)=\frac{L_k^{1/2}(-s)}{L_k^{1/2}(0)},\quad
\lambda_k=\frac{\Gamma(3/2)k!}{\Gamma(k+3/2)}.
\]
Their Stieltjes-transform difference gives
\[
\Gamma_{4k}
=\frac{\lambda_k}{\pi\sqrt2}
\int_0^\infty\frac{s^{-1/2}}{A_k(s)B_k(s)}\,ds.
\]
Under \(s=u/k\),
\[
A_k(u/k)\to\cosh(2\sqrt u),\qquad
B_k(u/k)\to\frac{\sinh(2\sqrt u)}{2\sqrt u}.
\]
Positive coefficients give the integrable domination
\(A_k(u/k)B_k(u/k)\ge(1+2u)(1+2u/3)\). Since
\[
\sqrt{k}\lambda_k\to\frac{\sqrt\pi}{2},\qquad
\int_0^\infty
\frac{u^{-1/2}\,du}{\cosh(2\sqrt u)\sinh(2\sqrt u)/(2\sqrt u)}
=\frac{\pi^2}{8},
\]
the stated constant follows. Monotonicity in \(d\) extends it from multiples of four to all orders.

**(d) — PROVEN growth when averaging over Gaussian He weights; no general monotonicity for fixed weights.** Specify iid \(W_{\ell,ij}\sim N(0,2/n)\). For one random input, the squared-norm multipliers are iid
\[
A_\ell=\frac2n\sum_{j=1}^n(Z_j^+)^2,\qquad
EA_\ell=1,\quad EA_\ell^2=1+\frac5n.
\]
Averaging over both weights and input gives
\[
E[T_L^2]=2,\qquad
\kappa_L:=\frac{E[T_L^4]}{E[T_L^2]^2}
=3(1+2/n)(1+5/n)^{L-1}.
\]
For any symmetric scalar reference law on \(\mathbb R\), with variance \(v>0\) and kurtosis \(\kappa\),
\[
\boxed{\Gamma_4=\Gamma_5=\frac{\sqrt v}{2}(1-\kappa^{-1/2}).}
\]
Indeed, \(\inf E|T|=\sqrt{v/\kappa}\), attained on \(\{0,\pm\sqrt{\kappa v}\}\), while \(\sup E|T|=\sqrt v\), approached using vanishing mass at infinity. Thus the averaged He law has **strictly increasing \(\Gamma_4\) at constant variance**. Conversely, \(\Gamma_2=\Gamma_3=\sqrt v/2\) is constant.

This does not establish growth of \(\Gamma_d(\mu_L)\) for a typical fixed-weight network, or of its average over networks. Fixed-weight laws retain Gaussian-type tails. Growth is possible, but monotonicity is false; an infinite iid sequence at fixed width eventually encounters an all-negative hidden matrix and kills the entire network almost surely. “Log-normal-like” norm behavior is a **HEURISTIC** approximation in an appropriate finite-depth, large-width regime, not a fixed-weight tail theorem.

**PROVEN numerical caveats from the source inspection (2026-11-03).**

- The grid LPs compute restricted-support gaps, hence underestimates of scalar \(\Gamma_d\), **not certified upper bounds** on the network gap.
- [lw.py](/home/agent/workspaces/mats/work/cumulant-ambiguity/lw.py:95) drops directions null under the reference sample; these need not vanish on extra candidate points. Its reported feasible laws require checking all original moment constraints.
- [gamma1d.py](/home/agent/workspaces/mats/work/cumulant-ambiguity/gamma1d.py:54) incorrectly returns zero merely because the reference has fewer than \(d+1\) support points. Counterexample: reference \(\tfrac12(\delta_{-1}+\delta_1)\), \(d=2\), scalar range \(\mathbb R\); the true gap is \(1/2\).
tokens used
46,232
**0 — PROVEN, with a wording qualification.** Matching \(E[h_L]\) fixes \(E[f]=a^\top E[h_L]\). Thus any **nontrivial ambiguity claim** must exclude the final activation layer; the phrase “up to the output” itself is ambiguous.

**1 — PROVEN.** The feasible sets satisfy \(A_d(\mathrm{all})\subseteq A_d(\mathrm{last})\). Moreover, \(t_i^k=(w_i^\top h_{L-1})^k\) is a degree-\(k\) polynomial. Hence each feasible marginal of \(t_i\) matches its first \(d\) moments, and
\[
\operatorname{gap}_d(\mathrm{all})
\le \operatorname{gap}_d(\mathrm{last})
\le \sum_i |a_i|\Gamma_d(\mu_i).
\]
This is an upper bound, without any assertion that the marginal extrema are jointly realizable. For \(d=1\), a two-sided scalar range gives \(\Gamma_1=\infty\).

**2 — PROVEN; the compactness argument needs one addition.** For fixed weights, \(|t_i(x)|\le C\|x\|\), so \(E e^{\epsilon t_i^2}<\infty\) for some \(\epsilon>0\), implying moment determinacy. Given feasible \(\nu_d\), the fixed second moment gives tightness. For each \(k\), an eventually fixed higher even moment ensures uniform integrability of \(t^k\), so every subsequential limit matches **all** moments and equals \(\mu_i\). The fixed second moment also makes ReLU uniformly integrable. Thus \(\Gamma_d\to0\). Finite empirical reference laws satisfy the conclusion too.

**3 — PROVEN as an information lower bound; FALSE if “strictly” means always.** Every such estimator returns the same number \(c\) throughout \(A_d(\mathrm{input})\), and
\[
\sup_{Q\in A_d(\mathrm{input})}|c-E_Qf|
\ge \tfrac12\operatorname{gap}_d(\mathrm{input}).
\]
This applies to any estimator using only those input moments, regardless of propagation architecture. The all-layer oracle is weakly more informative and sometimes strictly more informative; \(L=1\) gives equality. This does **not** establish an error lower bound when inputs are promised to be Gaussian, rather than arbitrary members of the ambiguity set.

**4 — FALSE as a blanket conclusion; PROVEN for the stated parity pair if its last preactivation is the signed minimum.** Write
\[
g=\Bigl(\prod_j\operatorname{sign}x_j\Bigr)\min_j|x_j|.
\]
Conditioning independent Gaussian signs on positive parity preserves the requisite low-order input moments and doubles \(E[g_+]\), but changes \(E[g]\) from \(0\) to \(E[\min_j|x_j|]>0\). If \(t_i=g\), last-hidden-layer **first moments already exclude this alternative**. Such laws may nevertheless match some earlier layers. Claim 1 alone only bounds residual ambiguity; it does not prove that every parity-type construction fails against the oracle.

**(b) — PROVEN equality for \(L=1\), Gaussian input, one unit.** Let \(t=w^\top x\), \(\sigma=\|w\|>0\), \(u=w/\sigma\). For any scalar feasible law \(\nu\), take independently
\[
T\sim\nu,\qquad Z\sim N(0,I-uu^\top),\qquad X=uT/\sigma+Z.
\]
Every polynomial moment of \(X\) through degree \(d\) matches \(N(0,I)\), and \(w^\top X=T\). Therefore
\[
\boxed{\operatorname{gap}_d(\mathrm{all})=\Gamma_d(N(0,\sigma^2)).}
\]
This lifting argument does not automatically extend to empirical \(P_0\).

**(b), general lower bound — FALSE, even with Gaussian \(t\).** At width \(2\), depth \(2\), set
\[
h_1=(x_1^+,(-x_1)^+),\qquad t_1=h_{1,1}-h_{1,2}=x_1.
\]
Then \(f=t_1^+=h_{1,1}\), whose expectation is fixed by the first hidden-layer moments. Thus
\[
\operatorname{gap}_d(\mathrm{all})
=\operatorname{gap}_d(\mathrm{last})=0,
\qquad \Gamma_d(N(0,1))>0
\]
for every finite \(d\ge2\). No universal \(c>0\) exists.

**(c) — PROVEN: \(\Theta(1/d)\), with an explicit asymptotic constant.**
\[
\boxed{\Gamma_d(N(0,\sigma^2))
\sim \frac{\pi^{3/2}}{4\sqrt2}\frac{\sigma}{d}.}
\]
Consequently,
\[
\boxed{\frac{\Gamma_d}{\operatorname{sd}(T_+)}
\sim \frac{\pi^2}{4\sqrt{\pi-1}}\frac1d
=\frac{1.68605\ldots}{d}.}
\]
The reported \(1.4/d\) is a small-order fit, not the asymptotic constant.

Here is a quadrature proof. By symmetrization, put \(Y=T^2/2\sim\rho=\mathrm{Gamma}(1/2,1)\); the objective becomes \(E\sqrt Y/\sqrt2\). At \(d=4k\), let \(G_k\) be \(k\)-node Gauss quadrature for \(\rho\), and \(R_k\) the Radau rule with node \(0\) and \(k\) positive nodes. Hermite interpolation gives sharp bounds
\[
\Gamma_{4k}=\frac{G_k(\sqrt{\cdot})-R_k(\sqrt{\cdot})}{\sqrt2}.
\]
The lower endpoint is attained; the upper is approached by sending the prescribed node of a right-Radau rule to infinity.

For completeness, define
\[
A_k(s)=\frac{L_k^{-1/2}(-s)}{L_k^{-1/2}(0)},\quad
B_k(s)=\frac{L_k^{1/2}(-s)}{L_k^{1/2}(0)},\quad
\lambda_k=\frac{\Gamma(3/2)k!}{\Gamma(k+3/2)}.
\]
Their Stieltjes-transform difference gives
\[
\Gamma_{4k}
=\frac{\lambda_k}{\pi\sqrt2}
\int_0^\infty\frac{s^{-1/2}}{A_k(s)B_k(s)}\,ds.
\]
Under \(s=u/k\),
\[
A_k(u/k)\to\cosh(2\sqrt u),\qquad
B_k(u/k)\to\frac{\sinh(2\sqrt u)}{2\sqrt u}.
\]
Positive coefficients give the integrable domination
\(A_k(u/k)B_k(u/k)\ge(1+2u)(1+2u/3)\). Since
\[
\sqrt{k}\lambda_k\to\frac{\sqrt\pi}{2},\qquad
\int_0^\infty
\frac{u^{-1/2}\,du}{\cosh(2\sqrt u)\sinh(2\sqrt u)/(2\sqrt u)}
=\frac{\pi^2}{8},
\]
the stated constant follows. Monotonicity in \(d\) extends it from multiples of four to all orders.

**(d) — PROVEN growth when averaging over Gaussian He weights; no general monotonicity for fixed weights.** Specify iid \(W_{\ell,ij}\sim N(0,2/n)\). For one random input, the squared-norm multipliers are iid
\[
A_\ell=\frac2n\sum_{j=1}^n(Z_j^+)^2,\qquad
EA_\ell=1,\quad EA_\ell^2=1+\frac5n.
\]
Averaging over both weights and input gives
\[
E[T_L^2]=2,\qquad
\kappa_L:=\frac{E[T_L^4]}{E[T_L^2]^2}
=3(1+2/n)(1+5/n)^{L-1}.
\]
For any symmetric scalar reference law on \(\mathbb R\), with variance \(v>0\) and kurtosis \(\kappa\),
\[
\boxed{\Gamma_4=\Gamma_5=\frac{\sqrt v}{2}(1-\kappa^{-1/2}).}
\]
Indeed, \(\inf E|T|=\sqrt{v/\kappa}\), attained on \(\{0,\pm\sqrt{\kappa v}\}\), while \(\sup E|T|=\sqrt v\), approached using vanishing mass at infinity. Thus the averaged He law has **strictly increasing \(\Gamma_4\) at constant variance**. Conversely, \(\Gamma_2=\Gamma_3=\sqrt v/2\) is constant.

This does not establish growth of \(\Gamma_d(\mu_L)\) for a typical fixed-weight network, or of its average over networks. Fixed-weight laws retain Gaussian-type tails. Growth is possible, but monotonicity is false; an infinite iid sequence at fixed width eventually encounters an all-negative hidden matrix and kills the entire network almost surely. “Log-normal-like” norm behavior is a **HEURISTIC** approximation in an appropriate finite-depth, large-width regime, not a fixed-weight tail theorem.

**PROVEN numerical caveats from the source inspection (2026-11-03).**

- The grid LPs compute restricted-support gaps, hence underestimates of scalar \(\Gamma_d\), **not certified upper bounds** on the network gap.
- [lw.py](/home/agent/workspaces/mats/work/cumulant-ambiguity/lw.py:95) drops directions null under the reference sample; these need not vanish on extra candidate points. Its reported feasible laws require checking all original moment constraints.
- [gamma1d.py](/home/agent/workspaces/mats/work/cumulant-ambiguity/gamma1d.py:54) incorrectly returns zero merely because the reference has fewer than \(d+1\) support points. Counterexample: reference \(\tfrac12(\delta_{-1}+\delta_1)\), \(d=2\), scalar range \(\mathbb R\); the true gap is \(1/2\).
