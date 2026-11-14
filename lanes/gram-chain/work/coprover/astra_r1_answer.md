**HEURISTIC:** The main predictions are a coupled radius/ratio diffusion, \(\mathrm{SD}(\ell)\sim1.887\,n^{-1/3}\), and angular participation ratio of order \(n^{2/3}\). The stationary convergence theorem and full joint spectral gap remain open.

**Convention:** Variances below are traces of covariance matrices. Set \(u(0)=0\). Distinguish a ratio of weight-averaged quantities from a weight average of per-net ratios.

**Q1. Stationary two-replica limit**

**HEURISTIC; stationary convergence is a CONJECTURE.** Put
\[
k=\frac{2\sqrt2}{3\pi},\quad A=k^{-2/3}=2.23092047,\quad
X=Q/n,\quad Y=n^{1/3}\ell,\quad s=\text{layers}/n.
\]
The proposed limit is
\[
(Q/n,n^{2/3}\delta,n^{1/3}\ell)\Longrightarrow(X,g(X),Y),
\qquad g(x)=Ax^{-2/3},
\]
where
\[
dX=ds+\sqrt5X\,dB,\qquad
dY=-\frac{Y}{X}\,ds+2\sqrt A\,X^{-1/3}dB^\perp,
\quad d[B,B^\perp]=0.
\]
The one-step coefficients giving this are
\[
\operatorname{Var}(\Delta\ell\mid G)\sim4\delta/n,\qquad
E[\Delta\ell\mid G]\sim-\ell/Q.
\]
Thus \(X,Y\) evolve together on \(n\) layers. The angle is fast and slaved, with
\[
\tau_\delta=\frac{2}{3k\sqrt{\delta_*}}
          \sim1.488\,Q^{1/3}.
\]
Its relative fluctuations are \(O(n^{-1/3})\).

**PROVEN within this diffusion.** The invariant radius density is
\[
p(x)=\beta x^{-2}e^{-\beta/x},\qquad \beta=2/5.
\]
The joint law is specified by stationary \(X\) and
\[
Y_0=2\sqrt A\int_{-\infty}^0
 X_s^{-1/3}\exp\!\left(-\int_s^0X_r^{-1}dr\right)dB^\perp_s.
\]
It is a Gaussian mixture over radius histories. Conditioning only on the current radius does not generally give a Gaussian.

**PROVEN within this diffusion.** Writing \(m(x)=E[Y^2\mid X=x]\),
\[
\frac52x^2m''+m'-\frac{2m}{x}+4Ax^{-2/3}=0,
\]
whose stationary solution is
\[
m(x)=\frac{24A}{25}\beta^{-2/3}
       e^{\beta/x}\Gamma(2/3,\beta/x).
\]
Consequently,
\[
E[\ell^2\mid Q/n=x]\sim n^{-2/3}m(x),\quad
E[\ell^2]\sim3.561344\,n^{-2/3}.
\]
Here \(m(0.577078)=3.510064\), \(m(\infty)=5.342016\), and
\[
\mathrm{SD}(\ell)\sim1.887152\,n^{-1/3}.
\]
The frozen-radius estimate \(2Ax^{1/3}\) misses the saturation.

**HEURISTIC, new second-order prediction.** For conditioning on \(Q=Q_{11}\), rather than the geometric mean of the two radii,
\[
E[\delta\mid Q=nx]
=\delta_*(nx)+n^{-4/3}H(x)+o(n^{-4/3}).
\]
An explicit coefficient algorithm is
\[
\lambda=\tfrac32k\sqrt g,
\]
\[
H=
\frac{m/(2x)+(14/15)g/x-(5/2)g}{\lambda}
+\frac89gm-\frac23xgm'-\frac4{15}\frac{gm}{x}.
\]
For conditioning on \(\sqrt{Q_1Q_2}/n\), omit the last three terms. This conditioning distinction matters at precisely the requested order.

**HEURISTIC derivation check.** The relevant one-step angular coefficients are
\[
b_\delta=-k\delta^{3/2}-\frac{k}{20}\delta^{5/2}
+\frac{\cosh\ell-\delta}{Q}+\frac{2\delta}{n}+\cdots,
\]
\[
a_{\delta\delta}\sim8\delta^2/n,\qquad
a_{Q\delta}\sim-4Q\delta/n.
\]
Expanding the stationary conditional-moment equation gives \(H\). I have not established the stationary remainder bound.

**NUMERICAL evaluation of these formulas**, at \(Q/n=\beta/\log2\), where \(H=3.660343\):

| \(n\) | Mean-field \(\delta_*\) | Predicted correction | Predicted SD\((\ell)\) | Leading \(\tau_\delta\), layers |
|---:|---:|---:|---:|---:|
| 64 | .17578 | +.01430 | .4718 | 4.95 |
| 256 | .07556 | +.00225 | .2972 | 7.86 |
| 1024 | .03099 | +.000355 | .1872 | 12.48 |

**Q2. Mixing**

**PROVEN for the limiting radius diffusion.** Its \(L^2(p)\) spectral gap is \(5/8\), giving layer relaxation rate \(5/(8n)\), or relaxation times
\[
102.4,\quad409.6,\quad1638.4
\]
at the three widths. This is the bottom of continuous spectrum, not an isolated first excited eigenvalue.

**PROVEN within the joint diffusion.** The operators governing the homogeneous parts of the \(Y^j\) moment equations are
\[
\mathcal L_X-j/x.
\]
For integer \(j\ge1\), their spectral bottom is also \(5/8\). Thus ratio correlations have an \(n\)-layer slow component. Along a typical radius history, an initial ratio displacement contracts at exponent
\[
E[X^{-1}]/n=5/(2n),
\]
which differs from the annealed relaxation exponent.

**CONJECTURE:** The full joint process has relaxation edge \(5/8\). The polynomial-moment calculation alone does not prove its full semigroup gap.

**PROVEN distinction.** The radius itself has no stationary mean or autocorrelation. Mixing must specify a metric or an integrable observable, such as log radius, bounded overlaps, or tail indicators. Uniform mixing over arbitrarily large initial radii cannot have a finite common time.

**HEURISTIC:** Although angle deviations from \(g(X)\) relax quickly, the stationary scaled angle inherits the radius’s slow fluctuations. Tail-sensitive radius observables approach the spectral edge; there is no single slowest eigen-observable.

**Q3. Closed, total, and block relevance**

**HEURISTIC, frozen equal-radius closure.** Define
\[
\psi(d)=1-\kappa(1-d),\quad
F_0(d)=\frac{Q\psi(d)+1}{Q+1},\quad
F_1(d)=\frac{Q\psi(d)}{Q+1}.
\]
Here \(F_0\) uses independent noise and \(F_1\) shared noise. Including the noiseless output layer correctly,
\[
V_P(t)\approx1-\frac{\psi(F_0^{\,t-1}(0))}{\psi(\delta_*)},
\qquad
T_P(t)\approx\frac{\psi(F_1^{\,t-1}(\delta_*))}{\psi(\delta_*)}.
\]
Both equal one at \(t=1\).

**HEURISTIC:** With \(d=\delta_*w\) and \(s=k\sqrt{\delta_*}(t-1)\), the leading closed curve satisfies
\[
w'=1-w^{3/2},\qquad w(0)=0,\qquad V_P=1-w.
\]
Its terminal exponential rate is \(3k\sqrt{\delta_*}/2\), so its principal time scale is \(n^{1/3}\).

**HEURISTIC:** Shared-noise propagation from angle \(d_0\) gives
\[
d(s)=
\frac{d_0e^{-s/Q}}
 {[1+kQ\sqrt{d_0}(1-e^{-s/(2Q)})]^2}.
\]
For \(d_0=\delta_*\), this predicts initial relaxation on \(n^{1/3}\), a \(s^{-2}\) window, and eventual exponential decay on \(Q\) layers.

**FAILS as a uniform long-time approximation:** Equal radii omit
\[
\Delta\delta\supset \frac{\ell^2}{2Q}
\]
under shared noise. Unequal amplitudes make the same additive noise rotate the replicas differently.

**CONJECTURE:** With stationary \(\ell=O(n^{-1/3})\), this source balances finite-angle contraction at \(\delta=O(n^{-10/9})\). It interrupts the equal-radius algebraic law around \(n^{5/9}\) layers and produces a smaller \(n\)-layer tail.

**HEURISTIC:** For noise indices \([l-b,l)\), the block total curve is
\[
T_B(t)\approx
\frac{\psi\!\left(F_1^{\,t}(F_0^{\,b}(0))\right)}
     {\psi(\delta_*)}.
\]
The extra shared step accounts for noise at layer \(l\). For short blocks, the injected angle is approximately \(b/Q\).

**PROVEN interpretation.** Closed variance of the actual value function
\[
g_l(h)=E[a\mid h_l=h]
\]
is the relevant outer-sampling variance after integrating future noise. Total effects measure sensitivity including interactions. Neither a total-effect sum nor direction relevance alone defines the bits needed to estimate \(E[a]\); the latter discards amplitude.

**Q4. Participation ratios and spectra**

**DEFINITION.** For \(F(P,U)=u\), past \(P\), future noise \(U\), define
\[
C_{\rm cl}=\operatorname{Cov}_P(E_UF),\qquad
C_{\rm tot}=E_U\operatorname{Cov}_P(F).
\]
Use the finite-replica, variance-weighted participation ratio
\[
\operatorname{PR}_w(C)=
\frac{E_W[(\operatorname{tr}C)^2]}
     {E_W[\operatorname{tr}(C^2)]}.
\]
This is not \(E_W[\operatorname{PR}(C)]\).

**PROVEN constructions.** Four replicas suffice for the total version: two independent past pairs, with future noise shared within each pair and independent between pairs. Their difference vectors give both trace-square moments. Eight suffice for the closed version: evaluate each of two independent past-pair differences under two independent futures, then take an independent copy of that four-output construction. All replicas share weights.

**PROVEN under asymptotic freeness and concentration.** For a linear map with \(M=J^\top J\),
\[
\frac1{\operatorname{PR}(C^{1/2}MC^{1/2})}
=
\frac1{\operatorname{PR}_C}
+\frac1{\operatorname{PR}_M}-\frac1n.
\]
Rotation invariance of the future does not automatically establish these hypotheses: the state direction is distinguished.

**HEURISTIC:** A fresh tangent product has
\[
\operatorname{PR}_M(t)\approx\frac{n}{1+2t},
\qquad t\ll n.
\]
Replacing the cloud-averaged future map by one tangent map additionally requires approximately \(t\theta_{\rm cloud}\ll1\). Stationarity gives a coherence window of order \(n^{1/3}\).

**CONJECTURE from the stationary four-point expansion.** For the angular cloud,
\[
\operatorname{PR}_C(X=x)\sim
\lambda(x)n^{2/3},\qquad
\operatorname{PR}_w(C)\sim1.086511\,n^{2/3}.
\]
The contrast \((u_1-u_2)\cdot(u_3-u_4)\) has one-step variance source \(8\delta^2/n\) and damping \(\lambda n^{-1/3}\); balancing them gives this result.

**NUMERICAL:** The weighted predictions are \(17.4,43.8,110.4\). Exploratory exact-chain runs here gave \(21.6,47.4,117.8\), with a chain-bootstrap SE of \(5.9\) for the last value. These are finite-width checks, not a convergence demonstration.

**FAILS as an established conclusion:** A \(1/k\) spectrum is not derivable from the supplied evidence. An untruncated \(1/k\) spectrum predicts \((\log n)^2\), incompatible with the proposed \(n^{2/3}\) asymptote. Higher spectral moments require additional replicas. Raw-state covariance also includes a radial component and has divergent annealed trace.

**Q5. Input regime**

**PROVEN distinction.** Equicorrelation of finitely many inputs at infinite width does not imply an isotropic fixed-net covariance spectrum. The \(1/n\) four-point term determines its leading participation ratio.

**PROVEN fixed-depth vertex result.** Set \(c_0=0,v_0=1\), and
\[
c_{j+1}=\kappa(c_j),\qquad
v_{j+1}=\kappa'(c_j)^2v_j+S(c_j),
\]
where
\[
S(c)=E_Z\!\left[
\operatorname{Var}_\eta
\left(\sqrt2\,\mathrm{ReLU}(\sqrt c\,Z+\sqrt{1-c}\,\eta)\right)^2
\right].
\]
Then the leading angular result is
\[
\operatorname{PR}_{\rm ang}(l)
\sim n\frac{(1-c_l)^2}{v_l}.
\]
At fixed depth it also gives the leading raw-covariance result; that equivalence is not uniform in depth.

**NUMERICAL quadrature**, with the supplied measurements alongside:

| \(l\) | 1 | 4 | 16 | 32 | 64 | 128 | 256 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| Vertex prediction, \(n=256\) | 166.5 | 61.4 | 18.7 | 10.2 | 5.41 | 2.82 | 1.45 |
| Supplied angular PR | 159 | 57 | 17 | 9.6 | 6.1 | 3.6 | 1.9 |

**HEURISTIC depth extrapolation:** Since \(1-c_l\sim9\pi^2/(2l^2)\) and \(S(c)\sim2(1-c)^2\), this gives \(3n/(2l)\). At \(l=O(n)\), the fixed-depth expansion is insufficient. The quoted angular measurements must not be presented as measurements of raw \(\operatorname{Cov}(h_l)\), whose radial component becomes dominant.

**PROVEN operational radius construction.** Write \(h_l=rv\). Replace replica 1 by \(r_2v_1\), then propagate through the same noiseless future. Homogeneity gives the exact radius-surgery numerator
\[
N_R(l)=\tfrac12 E_W E_{x,x'}
 \|a_1-(r_2/r_1)a_1\|^2.
\]
After averaging future weights,
\[
N_R(l)=E_W\operatorname{Var}_x(|h_l|).
\]
This is an intervention measure, not generally a conditional Sobol share.

**PROVEN replica formula.** Start the Gram chain with independent directions of radius \(\sqrt n\), and define
\[
M_l=E\sqrt{Q_1Q_2},\qquad
K_L=E[\sqrt{Q_1Q_2}\rho],\qquad m_n=E\chi_n.
\]
Then
\[
E_W\operatorname{Var}_x(a)=n-m_n^2K_L,\qquad
R_l^{\rm surgery}=\frac{n-m_n^2M_l}{n-m_n^2K_L}.
\]

**NUMERICAL, computed here:** An exact squared-radius change of measure avoids rare-product sampling. Its row sampler replaces one first-replica Gaussian coordinate by positive \(\chi_3\); exchange symmetry supplies the bounded observable \(2R/(1+R^2)\), \(R=\sqrt{Q_2/Q_1}\).

| Net | Radius share at \(l=0\) | \(l=4\) | \(l=16\) | \(l=31\) |
|---|---:|---:|---:|---:|
| \(256\times32\) | .03725 | .30910 | .55593 | .63480 |
| \(8\times256\) | .14482 | .87792 | .99934 | approximately 1 |

**NUMERICAL qualifications:** These used 32,768 and 65,536 independent tilted paths. Corresponding output variances were \(13.408\pm0.061\) and \(3.3386\pm0.0095\), respectively; errors are Monte Carlo SEs. Late narrow-deep angular differences reached floating-point resolution, which does not prove exact equality.

**PROVEN:** For output direction, radial rescaling has exactly zero effect at every cut when \(\sigma=0\). A closed statistic conditioned on radius can nevertheless predict direction because radius and direction are dependent.

**HEURISTIC for small noise:** Future independent noise injects angular discrepancy approximately \(\sigma^2/Q_j\) per hidden layer. Propagate this with the kernel recursion along the radius history. Compare the resulting variance with input-dependent output variance, not total squared radius.

**PROVEN bound:** Averaged over weights, future-noise conditional variance is at most \(n\sigma^2(t-1)\). This follows from the expected squared-distance contraction of a critical ReLU layer and Efron–Stein.

**Q6. Annealed versus quenched**

**CONJECTURE, supported by the multiscale expansion.**
\[
\operatorname{Var}_{\rm noise}(u\mid W)
\sim A n^{-2/3}X_W^{-2/3}.
\]
Therefore it does not self-average:
\[
\operatorname{CV}_W\longrightarrow
\sqrt{\frac{\Gamma(7/3)}{\Gamma(5/3)^2}-1}
=0.67897.
\]
The exploratory four-replica runs gave hidden-direction CVs approximately \(0.56,0.62,0.64\).

**HEURISTIC:** At age \(t-1=\tau n^{1/3}\),
\[
V_P(W,t)\approx
\mathcal V(k\sqrt A\,\tau X_W^{-1/3}),
\]
where \(\mathcal V=1-w\) is the Q3 curve. Integrating over the inverse-gamma radius gives CVs \(0.245\) at \(\tau=1\) and \(0.530\) at \(\tau=2\). At fixed age, \(V_P\to1\) and its CV vanishes.

**HEURISTIC:** In the frozen-radius large-\(\tau\) window, the mean per-net closed ratio decays like \(\tau^{-3}\), whereas the ratio of annealed closed variance to annealed total variance decays like \(\tau^{-5}\). The variance weighting changes the answer.

**PROVEN limitations.** Fixed-depth input kernel quantities can concentrate while depth-\(O(n)\) radius gains do not. Stationary raw second moments diverge. Even bounded annealed direction statistics cannot identify a particular net’s important directions.

**Q7. Perturbation survival**

**HEURISTIC:** For a small orthogonal perturbation, \(\delta_0\simeq\epsilon^2/2\). Before radius-ratio feedback matters,
\[
E\|u-u'\|^2\approx
\frac{\epsilon^2e^{-t/Q}}
 {[1+(kQ\epsilon/\sqrt2)(1-e^{-t/(2Q)})]^2}.
\]
For \(t\ll Q\), this reduces to
\[
\frac{\epsilon^2}{(1+\epsilon t/(3\pi))^2}.
\]
Thus the finite-angle/tangent crossover is \(\epsilon t\asymp1\); using the displayed denominator’s crossover constant, \(\epsilon_c=3\pi/t\). At \(t=n\), these are \(0.1473,0.03682,0.009204\).

**PROVEN:** The unnormalised tangent identity
\[
E_W\|Jv\|^2=\|v\|^2
\]
does not establish typical survival, finite-perturbation survival, or normalized-direction survival.

**FAILS:** Dividing this identity by an average radius is invalid. At any finite \(n\ge2\), an output layer with exactly two active units gives a divergent inverse-radius contribution to the annealed squared directional derivative. Finite perturbation discrepancies remain bounded; the derivative and expectation limits do not commute.

**Q8. Red team**

**PROVEN defects requiring explicit conventions:**

- A nonzero state produces an all-off output with probability \(2^{-n}\). Without noise, survival through \(L\) layers is \((1-2^{-n})^L\): only \(0.36716\) at \(8\times256\).
- Radius/direction variance attribution depends on whether one means conditioning, rescaling, or an orthogonal decomposition.
- Conditioning on a replica radius changes the replica sampling law.
- Finite-replica moment ratios are not mean per-net participation ratios or Sobol indices.
- Neither PR nor a gate count supplies a computational lower bound for estimating a mean. The Gaussian surrogate also needs its own approximation-error check.

**CONJECTURE; best falsification computation:** Run one stationary four-replica width sweep, extending to \(n=4096\), with radius bins and errors clustered by independent chain. Simultaneously test
\[
n^{2/3}E[\ell^2\mid X]=m(X),\qquad
\operatorname{PR}_C/n^{2/3}=\lambda(X),
\]
and residual across-net variation after radius conditioning. Failure of these conditional collapses would directly refute the proposed radius-driven asymptotics. The short runs here support further testing; they do not establish them.

**CHECKED:** Computations were single-threaded and read-only; the forbidden directory was not read and no files were edited.
