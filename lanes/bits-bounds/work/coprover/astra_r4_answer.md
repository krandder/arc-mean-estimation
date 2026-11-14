PROVEN: §6.6(e)’s abstract covering bound is correct under its stated hypotheses. Its application to finite-width nets is not established: the global linear minorant is false, and surviving angular atoms violate the global small-ball hypothesis. §6.6(a)’s survival-conditioned variance identity also needs correction.

NUMERICAL: Both saved reports reproduce. The reported 88% bit-count agreement is mostly censored or zero-bit cases; agreement among resolved, nonzero counts is 23/64.

PROVEN: I completed Part 1 before reading §6.6. All calculations remained in memory; no files were modified.

**1. PROVEN: The log-radius martingale requires a precise treatment of death.**

Let \(\mathcal F_j\) contain the inputs and the first \(j\) weight matrices. For two nonzero states, write
\[
S=G(h)^2=\frac1n\sum_{i=1}^n 2(Z_i)_+^2,\qquad
S'=G(h')^2=\frac1n\sum_{i=1}^n 2(Z_i')_+^2,
\]
where the pairs are iid standard Gaussian with correlation \(\cos\theta\).

PROVEN: The unqualified claim is false. With positive probability, one logarithm becomes \(-\infty\); if both states die, their difference is undefined. Thus the original process is not an ordinary square-integrable martingale.

PROVEN: One exact repair is to freeze the log ratio at its pre-death value. While both states are alive, use increment
\[
\Delta_{j+1}=
\begin{cases}
\frac12\log(S/S'),&S,S'>0,\\
0,&\text{otherwise},
\end{cases}
\]
and use zero increments thereafter. Exchangeability of \((S,S')\) makes its conditional mean zero. Its conditional second moment \(v_n^\dagger(\theta)\) depends only on the angle. If \(\tau\) is the first death,
\[
\operatorname{Var} Z_L
=\sum_{j=0}^{L-1}
\mathbb E\!\left[1_{\{\tau>j\}}v_n^\dagger(\theta_j)\right].
\]
The stopped process agrees with the original log ratio through depth \(L\) except on an event of probability at most \(2L\,2^{-n}\).

PROVEN: Conditioning on survival through a fixed final depth also preserves zero drift, by exchangeability, but changes the conditional variance. Define \(q_r(\theta)\) as the probability that both states survive another \(r\) layers. Under survival through \(L\), the next-layer law is tilted by
\[
1_{\{S,S'>0\}}q_{L-j-1}(\theta_{j+1}).
\]
Consequently its increment variance generally depends on both \(\theta_j\) and the remaining horizon. It is not the variance obtained by conditioning only on survival of the next layer.

PROVEN UNDER \(n\to\infty\) at fixed angle, with either the stopped convention or one-step survival conditioning: define
\[
b(\theta)=3-\frac{(\pi-\theta)(1+2\cos^2\theta)
                         +3\sin\theta\cos\theta}{\pi}.
\]
Then
\[
v_n(\theta)=\frac{b(\theta)}n+O_\theta(n^{-2}).
\]
Indeed, for \(X=2Z_+^2\), \(Y=2Z_+'^2\),
\[
\mathbb EX=1,\quad \operatorname{Var}X=5,\quad
\mathbb EXY=4k_2(\cos\theta),
\]
and the delta method gives
\[
\operatorname{Var}\!\left[\tfrac12(\log\bar X-\log\bar Y)\right]
=\frac{3-2k_2(\cos\theta)}n+O_\theta(n^{-2}).
\]

PROVEN UNDER the iterated limit “large width, then small angle”:
\[
b(\theta)=2\theta^2-\frac23\theta^4+\frac{4}{15\pi}\theta^5+O(\theta^6),
\qquad v_n(\theta)\sim\frac{2\theta^2}{n}.
\]
This is not a uniform assertion as \(\theta\to0\) at fixed \(n\); exceptionally small positive gains make the logarithmic statistic delicate.

PROVEN UNDER deterministic mean-field angle evolution: set
\[
\theta_0=\frac\pi2,\qquad
\cos\theta_{j+1}=\kappa(\cos\theta_j),\qquad
B_L=\sum_{j=0}^{L-1}b(\theta_j).
\]
Then the leading prediction is \(n\operatorname{Var}(\text{pair log ratio})=B_L\), and the future share is
\[
F_{l,L}=\frac{B_L-B_l}{B_L}.
\]
Independent spherical inputs have random initial inner product at finite \(n\); replacing it by zero is the large-width approximation.

NUMERICAL: Iterating this recursion gives \(B_\infty\approx21.3011\). The corresponding expected variance across inputs has coefficient \(B_\infty/2\approx10.6505\).

| \(l\) | \(F_{l,\infty}\) |
|---:|---:|
| 8 | 0.48639 |
| 16 | 0.32481 |
| 32 | 0.19686 |
| 64 | 0.11093 |
| 128 | 0.05954 |
| 256 | 0.03100 |

PROVEN UNDER the same deterministic recursion:
\[
\theta_j\sim\frac{3\pi}{j},\qquad
B_\infty-B_l\sim\frac{18\pi^2}{l},\qquad
F_{l,\infty}\sim\frac{8.3401}{l}.
\]
For large finite \(l<L\), the tail numerator is approximately
\(18\pi^2(1/l-1/L)\). These are mean-field profile statements; transferring them to \(L=\alpha n\) requires uniform finite-width control.

**2. PROVEN: Radial-merge error has an exact angle kernel, but strict mean field does not produce the rough linear term.**

For nonzero, past-chosen \(h,c\), put \(x=h/\|h\|\), \(y=c/\|c\|\), \(t=L'\). Homogeneity and rotational invariance give
\[
\mathbb E_{\rm future}
\left\|g(h)-\frac{\|h\|}{\|c\|}g(c)\right\|^2
=\|h\|^2\rho_{n,t}(\phi),
\]
where
\[
\rho_{n,t}(\phi)=2\bigl[1-K_{n,t}(\cos\phi)\bigr],
\qquad K_{n,t}(\cos\phi)=\mathbb E\langle g(x),g(y)\rangle .
\]
The equality uses \(\mathbb E\|g(x)\|^2=\mathbb E\|g(y)\|^2=1\), including dead trajectories.

PROVEN UNDER infinite width at fixed \(t\):
\[
K_{\infty,t}(c)=\kappa^{\circ t}(c),\qquad
\rho_{\infty,t}(\phi)=2[1-\kappa^{\circ t}(\cos\phi)].
\]
For small \(\phi\), writing \(z=t\phi/(3\pi)\),
\[
\rho_{\infty,t}(\phi)\simeq\frac{\phi^2}{(1+z)^2}.
\]
Thus, for \(z\gg1\), strict mean field gives approximately \(9\pi^2/t^2\), not \(6\pi\phi/n\).

PROVEN: The finite-width radial contribution can be isolated without logarithms. For unit initial states, let \(R_j,R_j'\) be their radii and \(\Theta_j\) their angle. Then
\[
\rho_{n,t}
=\underbrace{\mathbb E(R_t-R_t')^2}_{B_t^{\rm rad}}
+2\mathbb E[R_tR_t'(1-\cos\Theta_t)].
\]
Moreover,
\[
B_{j+1}^{\rm rad}-B_j^{\rm rad}
=\mathbb E\!\left[
R_jR_j'\,
\mathbb E_W(G(x_j)-G(y_j))^2
\right]\ge0.
\]
The one-layer squared-gain-norm difference has leading coefficient \(b(\theta)/n\), the same coefficient as the log-ratio variance.

PROVEN UNDER a uniform, summable mean-field approximation to these weighted moments:
\[
B_t^{\rm rad}\simeq
\frac1n\sum_{j<t}b(\phi_j)
\simeq \frac{6\pi}{n}\phi\,\frac{z}{1+z}.
\]
With corresponding control of the angular term,
\[
\rho_{n,t}(\phi)\simeq
\frac{\phi^2}{(1+z)^2}
+\frac{6\pi}{n}\phi\,\frac{z}{1+z}.
\]
The familiar version is justified conditionally in the window
\(1/\phi\ll t\ll n\); extending it uniformly to \(t=O(n)\) needs additional estimates.

HEURISTIC: In a small-angle rough window with \(z\gg1\), the radial term is \(6\pi\phi/n\). It dominates the remaining-angle term only when
\[
\frac{t^2\phi}{n}\gg1.
\]
The conditions \(t\phi\gg3\pi\) and \(t\le\alpha n\) alone do not ensure that dominance.

PROVEN UNDER quantitative control of the preceding approximation: on that restricted rough window, any fixed margin
\[
a=(1-\eta)\frac{6\pi}{n},\qquad \eta>0,
\]
can serve as an asymptotic linear minorant once the approximation errors are smaller than the margin. This is not an all-width theorem from the stated roughness conditions alone.

PROVEN: A positive global linear minorant is impossible at every finite \(n,t\). Annealed nonexpansion gives
\[
\rho_{n,t}(\phi)\le2(1-\cos\phi)\le\phi^2.
\]
In fact, for fixed finite \(n,t\),
\[
\rho_{n,t}(\phi)=\phi^2+o(\phi^2),
\]
using \(\mathbb E J_g(x)^TJ_g(x)=I\). Therefore
\(\rho_{n,t}(\phi)\ge a\min(\phi,\phi_0)\) cannot hold for all sufficiently small \(\phi\) with \(a>0\).

HEURISTIC: In units of annealed output energy, the rough linear coefficient is \(6\pi/n\). If additionally
\[
\frac{\mathbb E_W V_{\rm ang}}{\mathbb E_{W,u}\|A(u)\|^2}
\sim\frac{B_\infty}{2n},
\]
the normalized coefficient becomes
\[
\frac{12\pi}{B_\infty}\approx1.7698.
\]
Thus the explicit \(1/n\) cancels in the normalized rough prediction. This does not make the residual universally width-independent: the reference angles, remaining depth, and quenched normalization still vary with width. In particular, if the typical reference angle is \(O(1/l)\), the predicted normalized residual is \(O(1/l)\), hence \(O(1/n)\) at \(l=\Theta(n)\).

**3. PROVEN UNDER the minorant, small-ball condition, and future-independent assignments: the covering bound holds with a truncation qualification.**

Let \(Q=\mathbb E\|h\|^2>0\), and let \(P_w\) be the radius-squared-weighted angular law. References and assignments must be measurable from the prefix and independent randomness; future-selected assignments invalidate the reduction to a fixed future-averaged distortion.

For \(R=\min_{k\le M}\angle(h,c_k)\),
\[
P_w(R\le r)\le KM(r/\theta)^d,\qquad r\le\theta.
\]
Define
\[
r_*=\theta(KM)^{-1/d},\qquad
b=\min(\phi_0,\theta,r_*).
\]
Then
\[
\begin{aligned}
D(M)
&\ge aQ\,\mathbb E_w\min(R,\phi_0)\\
&\ge aQ\int_0^b[1-KM(r/\theta)^d]\,dr\\
&=aQ\left[b-\frac{KM\,b^{d+1}}{(d+1)\theta^d}\right].
\end{aligned}
\]

PROVEN UNDER \(r_*\le\min(\phi_0,\theta)\): this reduces to
\[
D(M)\ge aQ\,\frac d{d+1}\theta(KM)^{-1/d},
\]
and therefore, for a positive deterministic or consistently annealed normalization \(V\),
\[
\boxed{\;
\log_2 M\ge
d\log_2\!\left(
a\frac QV\frac d{d+1}\frac{\theta}{\varepsilon^2}
\right)-\log_2K.
\;}
\]
The sufficient conditions \(\theta\le\phi_0\) and \(KM\ge1\), which §6.6(e) explicitly includes, ensure this branch.

PROVEN: Without such a qualification, the proposed bound is false because the minorant saturates at \(\phi_0\). Also, this theorem bounds future-averaged pointwise distortion, not the error of an estimated mean and not a per-network distortion quantile.

**4. PROVEN UNDER an exact geometric Gaussian model: effective dimension depends on scale.**

Use tangent coordinates with Euclidean distance comparable to angle. Write
\[
\lambda_k=\lambda_1e^{-2\beta(k-1)},\qquad \beta=l/n.
\]
For the infinite sequence,
\[
\mathrm{PR}=\coth\beta.
\]
For a finite rank \(d_0\), the exact expression is
\(\coth\beta\,\tanh(\beta d_0)\).

PROVEN UNDER the infinite geometric Gaussian model: if
\(S=\sum_k\lambda_k Z_k^2\), a useful small-ball saddle is
\[
I(r)=\sup_{s>0}
\left\{\frac12\sum_k\log(1+2s\lambda_k)-sr^2\right\}.
\]
The optimizing \(s\) satisfies
\[
r^2=\sum_k\frac{\lambda_k}{1+2s\lambda_k}.
\]
Its local exponent is
\[
-\frac{dI}{d\log r}
=2sr^2
=\sum_k\frac{2s\lambda_k}{1+2s\lambda_k}.
\]
Thus the relevant number of directions grows as the radius decreases.

PROVEN UNDER the same model, as \(r\downarrow0\):
\[
-\log P(\|X\|\le r)
\sim\frac{\log^2(\sigma/r)}{2\beta},
\qquad \sigma^2=\sum_k\lambda_k.
\]
The leading effective exponent is consequently
\[
d_{\rm sb}(r)\sim\frac{\log(\sigma/r)}{\beta},
\]
with logarithmic corrections. For finite rank, this spectral regime eventually ends and the small-ball exponent becomes \(d_0\). It is not permanently \(\mathrm{PR}\).

PROVEN UNDER the infinite geometric Gaussian model: for optimal \(M\)-point quantization with expected distance loss,
\[
\log\frac{D(M)}{\sigma}
=-\sqrt{2\beta\log M}+o(\sqrt{\log M}).
\]
A small-ball union bound gives the lower logarithmic rate; product quantization with geometrically allocated resolution gives the matching upper rate.

HEURISTIC: Differentiating the smooth asymptotic envelope gives
\[
\gamma(M):=-\frac{d\log D}{d\log M}
\approx\sqrt{\frac{\beta}{2\log M}}.
\]
This derivative approximation is stronger than the leading logarithmic asymptotic and should not be called an exact finite-\(M\) theorem.

HEURISTIC: A more useful finite-rate proxy comes from Gaussian squared-error water filling:
\[
R=\log M=\frac12\sum_k\log(\lambda_k/\tau)_+,\qquad
D_2(R)=\sum_k\min(\lambda_k,\tau).
\]
Using \(\sqrt{D_2}\) as the linear-distortion proxy gives
\[
\gamma(R)\approx\frac{\tau}{D_2(R)}.
\]
With \(m\) active modes and small \(\beta\),
\[
\gamma\,\mathrm{PR}\approx\frac{2}{1+2\beta m}.
\]
There is no universal constant equal to one.

NUMERICAL: The reported rough-cell product has median \(0.7180\) and 10–90% range \(0.2931\)–\(1.2424\). The intermediate-cell median is \(1.0328\).

HEURISTIC: These measurements are compatible with scale-dependent quantization dimension. Interpreting the rough median as \(d_{\rm eff}=1/\gamma\) gives \(d_{\rm eff}/\mathrm{PR}\approx1.39\), but this describes the fitted construction over \(M=4,\ldots,256\). It establishes neither an intrinsic source dimension nor the optimal quantization exponent. Covariance eigenvalues alone, without a quantitative Gaussian approximation, establish no small-ball theorem.

**5. PROVEN UNDER two-sided source regularity and two-sided power distortion: the bits formula is a high-resolution law, not a general computational lower bound.**

For a compact regular \(d\)-dimensional source, with distortion comparable to angular distance raised to \(p\), covering constructions and small-ball bounds give
\[
D(M)\asymp C_lM^{-p/d}.
\]
Consequently,
\[
N_l(\varepsilon)
=\frac d p\log_2\frac{C_l}{\varepsilon^2}
\]
up to constants determined by the regularity and distortion bounds, with a floor at zero. Replacing \(C_l\) by the observed \(D_l(1)\) requires an additional calibration assumption.

PROVEN: A one-sided small-ball hypothesis supplies only the lower bound. Achievability needs covering or mass regularity and an upper distortion bound.

PROVEN: Direct radial merges are locally quadratic at fixed finite width and depth. The smooth \(p=3\) law belongs to frozen-Jacobian merges, not radial merges. The rough \(p=1\) law can describe only a scale window; increasing \(M\) eventually leaves it.

PROVEN UNDER the geometric Gaussian quantization asymptotic: a constant \(d_l\) is inappropriate across arbitrarily high precision. In the spectral regime, the required rate grows quadratically in \(\log(C_l/\varepsilon^2)\), before eventual finite-rank power-law behavior.

HEURISTIC: If \(d_l\asymp n/l\), then early fixed-depth cuts have dimension proportional to width, while cuts at a fixed fraction of \(L=\alpha n\) have dimension \(O(1)\). Coupled with the \(1/l\) residual profile, this explains why late angular compression can be cheap while early compression is expensive. It is not a lower bound on mean estimation.

PROVEN UNDER equal evaluation costs and free exact cell statistics: the inequality
\[
(D_l(1)/\varepsilon^2)^{d_l/p}<\varepsilon^{-2}
\]
compares full enumeration sufficient for a pointwise distortion target with plain sampling. It is not necessary for an integration method to beat sampling: mean errors may cancel, and an algorithm may sample the residual.

PROVEN UNDER a computable baseline with cost
\[
C(M)=aM+b\varepsilon^{-2}M^{-p/d}:
\]
optimizing \(M\) gives \(C_{\rm opt}\asymp\varepsilon^{-2/(1+p/d)}\). This can improve the precision exponent for every finite \(d\), although the gain becomes small at large \(d\). The assumption that the baseline is cheaply computable is essential.

PROVEN UNDER standard multilevel variance and cost hypotheses: optimal sampling work is
\[
\varepsilon^{-2}
\left(\sum_k\sqrt{v_kc_k}\right)^2,
\]
where \(v_k\) is level variance divided by the target variance. For dyadic depths, \(v_k\asymp1/l_k\) and \(c_k\asymp l_k\) give ideal work
\[
O(\varepsilon^{-2}\log^2 L),
\]
versus \(O(L\varepsilon^{-2})\) for plain sampling. Charging a reference trajectory and minimum level work adds \(O(L)\).

HEURISTIC: At \(L=\alpha n\), the advertised \(n/\log^2n\) gain therefore requires those coupling hypotheses and excluded or amortized setup. The bits formula alone provides no evidence that cell enumeration beats this shared-trajectory sampler.

PROVEN: The following audit uses the files read at **2026-11-01 23:33:56 UTC**. The two report generators were executed with their output-file writes intercepted in memory: `variance_made.md` matched exactly, and `bits5_posthoc_old.json` matched as parsed JSON.

1. **Critical — PROVEN — [§6.6(a)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:215): final-horizon survival is conflated with one-step survival.**  
   The drift argument survives, but the stated angle-only, time-independent conditional variance does not. There is an explicit counterexample at \(n=2\), initial angle \(\pi/2\). Conditional on first-layer survival, the active-count pair types have
   \[
   p=(4/9,4/9,1/9),\quad
   f=\left(\pi^2/4,\;\pi^2/6+\log^22,\;\pi^2/12\right),
   \]
   where \(f\) is the conditional squared log-ratio increment. Their probabilities of surviving the second layer average to
   \[
   q=(21/32,\;31/48,\;65/96).
   \]
   Thus the two first-increment variances are \(\sum p_if_i\) and
   \(\sum p_if_iq_i/\sum p_iq_i\), which differ.  
   **NUMERICAL:** They are \(2.13262442\) and \(2.12803793\).  
   **Fix:** use the stopped martingale and its bracket, or explicitly introduce horizon-dependent variances under final survival.

2. **Major — PROVEN — [§6.6(b)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:225): the statistic and limits are ambiguous.**  
   “\(n\operatorname{Var}\log|h_\infty|=10.63\)” must specify variance across inputs, averaged over weights, with a death convention and limit order. A single input’s variance across weights grows with depth; it is not this constant. The log-normal output formula and the \(t=O(n)\) extrapolation also do not inherit an exact label from fixed-depth mean field.  
   **Fix:** distinguish the fixed-depth leading theorem, numerical kernel sums, log-normal closure, and any separately proved joint-depth result.

3. **Moderate — NUMERICAL — [§6.6(b)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:226): the purported infinite profile is truncated.**  
   \(B_{4096}/2=10.62894963\), which rounds to the quoted \(10.63\). Using this truncated denominator also reproduces the quoted tail shares \(0.058\) and \(0.029\). The infinite values are approximately \(10.6505\), \(0.05954\), and \(0.03100\). The approximation \(5.5/(l+5.5)\) has the wrong tail coefficient; the coefficient is \(8.3401\).  
   **Fix:** identify the truncation or use a tail correction, and replace the rational approximation.

4. **Major — PROVEN — [§6.6(b), (d)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:229): one-reference distortion is not literally the future variance share.**  
   It depends on the reference policy and weighted angular distribution. For a typical independent reference, the rough prediction contains approximately twice the pairwise future variance share; a central reference changes that factor. In addition, the scorer substitutes an unweighted RMS angle to the k-means **centre**, whereas the evaluated merge uses a selected **member** as reference.  
   **Fix:** call \(D_R(1)\) a normalized one-reference distortion; identify the centre/member and RMS/weighted-mean substitutions as approximations.

5. **Moderate — NUMERICAL — [§6.6(c)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:232): the numerical summaries are correct, but the regime definitions need completion.**  
   I reproduce the variance ratios, the \(0.95\,[0.24,2.22]\) residual ratio, and the rough exponent statistics. The reported 77 intermediate and 62 smooth cells require thresholds \(0.5\le\theta_{\rm median}L'/2\le2\) and \(<0.5\), respectively; these differ from the smooth threshold used elsewhere. Moreover, among the 117 “rough” cells, only 55 have even the measured \(M=1\) quantity \(L'\phi>3\pi\); its median is \(9.0167\).  
   **Fix:** state the thresholds and distinguish the empirical bin from the asymptotic requirement \(L'\phi\gg3\pi\), separately at each cell resolution.

6. **Major — HEURISTIC — [§6.6(c)–(e)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:237): fitted dimension is promoted into source dimension.**  
   The values \(1.4\,\mathrm{PR}\) and \(1.75\,\mathrm{PR}\) are interpretations of fitted slopes for a particular construction. They do not establish the \(d\) in the small-ball theorem. Even the proposed geometric Gaussian model predicts a dimension that changes with resolution.  
   **Fix:** label these as empirical effective exponents over the tested \(M\)-range; independently establish source bounds before inserting them into a lower bound.

7. **Major — NUMERICAL — [§6.6(d)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:245): “matches on 88%” hides substantial censoring.**  
   The scorer’s result \(308/351=87.75\%\) is correct under its registered criterion. Its decomposition is:

   | Case | Cases | Agreements |
   |---|---:|---:|
   | Measured count \(>8\), censored | 251 | 249 |
   | Measured count \(=0\) | 36 | 36 |
   | Resolved, nonzero count | 64 | 23 |

   **Fix:** report both the registered agreement and the \(23/64=35.94\%\) agreement on resolved nonzero counts. The 88% figure alone does not demonstrate accurate bit-count prediction.

8. **Moderate — NUMERICAL — [§6.6(d)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:243): \((3\!-\!9)/l\) is not valid across the stated deep configurations and cuts.**  
   For \(L\ge n\), configuration/cut medians of \(lD_R(1)\) range from \(0.2113\) to \(8.5687\). For example, the table gives approximately \(0.844\) at \(256\times256,l=224\), and \(0.211\) at \(32\times128,l=112\).  
   **Fix:** restrict that calibration to the relevant rough cuts, and use the finite-horizon expression elsewhere. Also write the bits formula with a zero floor.

9. **Critical — PROVEN — [§6.6(e)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:248): the abstract theorem is valid, but its proposed global linear minorant is false for these nets.**  
   The stated \(\theta\le\phi_0\) and \(KM\ge1\) conditions correctly handle truncation. However, \(\rho_{n,t}(\phi)\le\phi^2\) rules out every positive global linear minorant. Calling it “the mean-field variogram” does not repair this: strict mean field lacks the finite-width linear term altogether.  
   **Fix:** prove a crossover or restricted-scale minorant and restrict the usable cell radii accordingly. The resulting bound is not an arbitrarily high-resolution \(p=1\) bound.

10. **Critical — PROVEN — [§6.6(e)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:251): the actual angular law has atoms, so the global small-ball hypothesis also fails when those rays survive.**  
    \(W_1\) is invertible almost surely. For each coordinate \(i\), the open input cone with exactly neuron \(i\) active has positive spherical measure, and all its first-layer outputs lie on the ray \(e_i\). Its radius-weighted mass is positive. If that ray survives to layer \(l\), homogeneity preserves an angular atom. A bound \(P_w(B(c,r))\le K(r/\theta)^d\), \(d>0\), cannot hold at that atom as \(r\downarrow0\).  
    **Fix:** formulate a quantitative bound for a restricted bulk law, account for exceptional mass, and specify that assignments as well as references are future-independent.

11. **Major — PROVEN — [§6.6(e)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:258): “nearly attained” does not follow from the measurements.**  
    A slope from one construction, combined with unverified source and minorant hypotheses, supplies neither a matching optimal exponent nor an achievability theorem for the proposed dimension.  
    **Fix:** retain the conditional lower bound and describe the measurements as empirical comparison. A matching theorem requires upper covering and upper distortion bounds over the same scale range.

12. **Major — PROVEN — [§6.6(f)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:261): a pointwise representation bound is used as a necessary condition for beating sampling.**  
    Mean estimation can benefit from cancellation, stratification, and sampled residuals without meeting the full pointwise distortion target. Prefix integration, assignments, reference construction, and multilevel setup also have costs.  
    **Fix:** present the displayed inequality as an idealized enumeration comparison. Compare complete estimators using their mean-square errors and charged costs; no separation from the shared-trajectory sampler follows from this cell-count argument.

PROVEN: The attribution to [input-bits §2.2](/home/agent/workspaces/mats/outbox/input-bits-2026-10-31.md:109) is correct. Its notation satisfies
\[
B(c)=4k_2(c)-1,\qquad
\frac14\sum_j[5-B(c_j)]
=\frac12\sum_j b(\theta_j)=\frac{B_L}{2}.
\]
The source contains the \(5.5,7.2,8.6,9.5,10.0\) profile and \(C_\infty=10.65\). The later combination with cloud geometry and quantization exponents is the bits-bounds contribution; those extra claims need their own hypotheses.
99,659
PROVEN: §6.6(e)’s abstract covering bound is correct under its stated hypotheses. Its application to finite-width nets is not established: the global linear minorant is false, and surviving angular atoms violate the global small-ball hypothesis. §6.6(a)’s survival-conditioned variance identity also needs correction.

NUMERICAL: Both saved reports reproduce. The reported 88% bit-count agreement is mostly censored or zero-bit cases; agreement among resolved, nonzero counts is 23/64.

PROVEN: I completed Part 1 before reading §6.6. All calculations remained in memory; no files were modified.

**1. PROVEN: The log-radius martingale requires a precise treatment of death.**

Let \(\mathcal F_j\) contain the inputs and the first \(j\) weight matrices. For two nonzero states, write
\[
S=G(h)^2=\frac1n\sum_{i=1}^n 2(Z_i)_+^2,\qquad
S'=G(h')^2=\frac1n\sum_{i=1}^n 2(Z_i')_+^2,
\]
where the pairs are iid standard Gaussian with correlation \(\cos\theta\).

PROVEN: The unqualified claim is false. With positive probability, one logarithm becomes \(-\infty\); if both states die, their difference is undefined. Thus the original process is not an ordinary square-integrable martingale.

PROVEN: One exact repair is to freeze the log ratio at its pre-death value. While both states are alive, use increment
\[
\Delta_{j+1}=
\begin{cases}
\frac12\log(S/S'),&S,S'>0,\\
0,&\text{otherwise},
\end{cases}
\]
and use zero increments thereafter. Exchangeability of \((S,S')\) makes its conditional mean zero. Its conditional second moment \(v_n^\dagger(\theta)\) depends only on the angle. If \(\tau\) is the first death,
\[
\operatorname{Var} Z_L
=\sum_{j=0}^{L-1}
\mathbb E\!\left[1_{\{\tau>j\}}v_n^\dagger(\theta_j)\right].
\]
The stopped process agrees with the original log ratio through depth \(L\) except on an event of probability at most \(2L\,2^{-n}\).

PROVEN: Conditioning on survival through a fixed final depth also preserves zero drift, by exchangeability, but changes the conditional variance. Define \(q_r(\theta)\) as the probability that both states survive another \(r\) layers. Under survival through \(L\), the next-layer law is tilted by
\[
1_{\{S,S'>0\}}q_{L-j-1}(\theta_{j+1}).
\]
Consequently its increment variance generally depends on both \(\theta_j\) and the remaining horizon. It is not the variance obtained by conditioning only on survival of the next layer.

PROVEN UNDER \(n\to\infty\) at fixed angle, with either the stopped convention or one-step survival conditioning: define
\[
b(\theta)=3-\frac{(\pi-\theta)(1+2\cos^2\theta)
                         +3\sin\theta\cos\theta}{\pi}.
\]
Then
\[
v_n(\theta)=\frac{b(\theta)}n+O_\theta(n^{-2}).
\]
Indeed, for \(X=2Z_+^2\), \(Y=2Z_+'^2\),
\[
\mathbb EX=1,\quad \operatorname{Var}X=5,\quad
\mathbb EXY=4k_2(\cos\theta),
\]
and the delta method gives
\[
\operatorname{Var}\!\left[\tfrac12(\log\bar X-\log\bar Y)\right]
=\frac{3-2k_2(\cos\theta)}n+O_\theta(n^{-2}).
\]

PROVEN UNDER the iterated limit “large width, then small angle”:
\[
b(\theta)=2\theta^2-\frac23\theta^4+\frac{4}{15\pi}\theta^5+O(\theta^6),
\qquad v_n(\theta)\sim\frac{2\theta^2}{n}.
\]
This is not a uniform assertion as \(\theta\to0\) at fixed \(n\); exceptionally small positive gains make the logarithmic statistic delicate.

PROVEN UNDER deterministic mean-field angle evolution: set
\[
\theta_0=\frac\pi2,\qquad
\cos\theta_{j+1}=\kappa(\cos\theta_j),\qquad
B_L=\sum_{j=0}^{L-1}b(\theta_j).
\]
Then the leading prediction is \(n\operatorname{Var}(\text{pair log ratio})=B_L\), and the future share is
\[
F_{l,L}=\frac{B_L-B_l}{B_L}.
\]
Independent spherical inputs have random initial inner product at finite \(n\); replacing it by zero is the large-width approximation.

NUMERICAL: Iterating this recursion gives \(B_\infty\approx21.3011\). The corresponding expected variance across inputs has coefficient \(B_\infty/2\approx10.6505\).

| \(l\) | \(F_{l,\infty}\) |
|---:|---:|
| 8 | 0.48639 |
| 16 | 0.32481 |
| 32 | 0.19686 |
| 64 | 0.11093 |
| 128 | 0.05954 |
| 256 | 0.03100 |

PROVEN UNDER the same deterministic recursion:
\[
\theta_j\sim\frac{3\pi}{j},\qquad
B_\infty-B_l\sim\frac{18\pi^2}{l},\qquad
F_{l,\infty}\sim\frac{8.3401}{l}.
\]
For large finite \(l<L\), the tail numerator is approximately
\(18\pi^2(1/l-1/L)\). These are mean-field profile statements; transferring them to \(L=\alpha n\) requires uniform finite-width control.

**2. PROVEN: Radial-merge error has an exact angle kernel, but strict mean field does not produce the rough linear term.**

For nonzero, past-chosen \(h,c\), put \(x=h/\|h\|\), \(y=c/\|c\|\), \(t=L'\). Homogeneity and rotational invariance give
\[
\mathbb E_{\rm future}
\left\|g(h)-\frac{\|h\|}{\|c\|}g(c)\right\|^2
=\|h\|^2\rho_{n,t}(\phi),
\]
where
\[
\rho_{n,t}(\phi)=2\bigl[1-K_{n,t}(\cos\phi)\bigr],
\qquad K_{n,t}(\cos\phi)=\mathbb E\langle g(x),g(y)\rangle .
\]
The equality uses \(\mathbb E\|g(x)\|^2=\mathbb E\|g(y)\|^2=1\), including dead trajectories.

PROVEN UNDER infinite width at fixed \(t\):
\[
K_{\infty,t}(c)=\kappa^{\circ t}(c),\qquad
\rho_{\infty,t}(\phi)=2[1-\kappa^{\circ t}(\cos\phi)].
\]
For small \(\phi\), writing \(z=t\phi/(3\pi)\),
\[
\rho_{\infty,t}(\phi)\simeq\frac{\phi^2}{(1+z)^2}.
\]
Thus, for \(z\gg1\), strict mean field gives approximately \(9\pi^2/t^2\), not \(6\pi\phi/n\).

PROVEN: The finite-width radial contribution can be isolated without logarithms. For unit initial states, let \(R_j,R_j'\) be their radii and \(\Theta_j\) their angle. Then
\[
\rho_{n,t}
=\underbrace{\mathbb E(R_t-R_t')^2}_{B_t^{\rm rad}}
+2\mathbb E[R_tR_t'(1-\cos\Theta_t)].
\]
Moreover,
\[
B_{j+1}^{\rm rad}-B_j^{\rm rad}
=\mathbb E\!\left[
R_jR_j'\,
\mathbb E_W(G(x_j)-G(y_j))^2
\right]\ge0.
\]
The one-layer squared-gain-norm difference has leading coefficient \(b(\theta)/n\), the same coefficient as the log-ratio variance.

PROVEN UNDER a uniform, summable mean-field approximation to these weighted moments:
\[
B_t^{\rm rad}\simeq
\frac1n\sum_{j<t}b(\phi_j)
\simeq \frac{6\pi}{n}\phi\,\frac{z}{1+z}.
\]
With corresponding control of the angular term,
\[
\rho_{n,t}(\phi)\simeq
\frac{\phi^2}{(1+z)^2}
+\frac{6\pi}{n}\phi\,\frac{z}{1+z}.
\]
The familiar version is justified conditionally in the window
\(1/\phi\ll t\ll n\); extending it uniformly to \(t=O(n)\) needs additional estimates.

HEURISTIC: In a small-angle rough window with \(z\gg1\), the radial term is \(6\pi\phi/n\). It dominates the remaining-angle term only when
\[
\frac{t^2\phi}{n}\gg1.
\]
The conditions \(t\phi\gg3\pi\) and \(t\le\alpha n\) alone do not ensure that dominance.

PROVEN UNDER quantitative control of the preceding approximation: on that restricted rough window, any fixed margin
\[
a=(1-\eta)\frac{6\pi}{n},\qquad \eta>0,
\]
can serve as an asymptotic linear minorant once the approximation errors are smaller than the margin. This is not an all-width theorem from the stated roughness conditions alone.

PROVEN: A positive global linear minorant is impossible at every finite \(n,t\). Annealed nonexpansion gives
\[
\rho_{n,t}(\phi)\le2(1-\cos\phi)\le\phi^2.
\]
In fact, for fixed finite \(n,t\),
\[
\rho_{n,t}(\phi)=\phi^2+o(\phi^2),
\]
using \(\mathbb E J_g(x)^TJ_g(x)=I\). Therefore
\(\rho_{n,t}(\phi)\ge a\min(\phi,\phi_0)\) cannot hold for all sufficiently small \(\phi\) with \(a>0\).

HEURISTIC: In units of annealed output energy, the rough linear coefficient is \(6\pi/n\). If additionally
\[
\frac{\mathbb E_W V_{\rm ang}}{\mathbb E_{W,u}\|A(u)\|^2}
\sim\frac{B_\infty}{2n},
\]
the normalized coefficient becomes
\[
\frac{12\pi}{B_\infty}\approx1.7698.
\]
Thus the explicit \(1/n\) cancels in the normalized rough prediction. This does not make the residual universally width-independent: the reference angles, remaining depth, and quenched normalization still vary with width. In particular, if the typical reference angle is \(O(1/l)\), the predicted normalized residual is \(O(1/l)\), hence \(O(1/n)\) at \(l=\Theta(n)\).

**3. PROVEN UNDER the minorant, small-ball condition, and future-independent assignments: the covering bound holds with a truncation qualification.**

Let \(Q=\mathbb E\|h\|^2>0\), and let \(P_w\) be the radius-squared-weighted angular law. References and assignments must be measurable from the prefix and independent randomness; future-selected assignments invalidate the reduction to a fixed future-averaged distortion.

For \(R=\min_{k\le M}\angle(h,c_k)\),
\[
P_w(R\le r)\le KM(r/\theta)^d,\qquad r\le\theta.
\]
Define
\[
r_*=\theta(KM)^{-1/d},\qquad
b=\min(\phi_0,\theta,r_*).
\]
Then
\[
\begin{aligned}
D(M)
&\ge aQ\,\mathbb E_w\min(R,\phi_0)\\
&\ge aQ\int_0^b[1-KM(r/\theta)^d]\,dr\\
&=aQ\left[b-\frac{KM\,b^{d+1}}{(d+1)\theta^d}\right].
\end{aligned}
\]

PROVEN UNDER \(r_*\le\min(\phi_0,\theta)\): this reduces to
\[
D(M)\ge aQ\,\frac d{d+1}\theta(KM)^{-1/d},
\]
and therefore, for a positive deterministic or consistently annealed normalization \(V\),
\[
\boxed{\;
\log_2 M\ge
d\log_2\!\left(
a\frac QV\frac d{d+1}\frac{\theta}{\varepsilon^2}
\right)-\log_2K.
\;}
\]
The sufficient conditions \(\theta\le\phi_0\) and \(KM\ge1\), which §6.6(e) explicitly includes, ensure this branch.

PROVEN: Without such a qualification, the proposed bound is false because the minorant saturates at \(\phi_0\). Also, this theorem bounds future-averaged pointwise distortion, not the error of an estimated mean and not a per-network distortion quantile.

**4. PROVEN UNDER an exact geometric Gaussian model: effective dimension depends on scale.**

Use tangent coordinates with Euclidean distance comparable to angle. Write
\[
\lambda_k=\lambda_1e^{-2\beta(k-1)},\qquad \beta=l/n.
\]
For the infinite sequence,
\[
\mathrm{PR}=\coth\beta.
\]
For a finite rank \(d_0\), the exact expression is
\(\coth\beta\,\tanh(\beta d_0)\).

PROVEN UNDER the infinite geometric Gaussian model: if
\(S=\sum_k\lambda_k Z_k^2\), a useful small-ball saddle is
\[
I(r)=\sup_{s>0}
\left\{\frac12\sum_k\log(1+2s\lambda_k)-sr^2\right\}.
\]
The optimizing \(s\) satisfies
\[
r^2=\sum_k\frac{\lambda_k}{1+2s\lambda_k}.
\]
Its local exponent is
\[
-\frac{dI}{d\log r}
=2sr^2
=\sum_k\frac{2s\lambda_k}{1+2s\lambda_k}.
\]
Thus the relevant number of directions grows as the radius decreases.

PROVEN UNDER the same model, as \(r\downarrow0\):
\[
-\log P(\|X\|\le r)
\sim\frac{\log^2(\sigma/r)}{2\beta},
\qquad \sigma^2=\sum_k\lambda_k.
\]
The leading effective exponent is consequently
\[
d_{\rm sb}(r)\sim\frac{\log(\sigma/r)}{\beta},
\]
with logarithmic corrections. For finite rank, this spectral regime eventually ends and the small-ball exponent becomes \(d_0\). It is not permanently \(\mathrm{PR}\).

PROVEN UNDER the infinite geometric Gaussian model: for optimal \(M\)-point quantization with expected distance loss,
\[
\log\frac{D(M)}{\sigma}
=-\sqrt{2\beta\log M}+o(\sqrt{\log M}).
\]
A small-ball union bound gives the lower logarithmic rate; product quantization with geometrically allocated resolution gives the matching upper rate.

HEURISTIC: Differentiating the smooth asymptotic envelope gives
\[
\gamma(M):=-\frac{d\log D}{d\log M}
\approx\sqrt{\frac{\beta}{2\log M}}.
\]
This derivative approximation is stronger than the leading logarithmic asymptotic and should not be called an exact finite-\(M\) theorem.

HEURISTIC: A more useful finite-rate proxy comes from Gaussian squared-error water filling:
\[
R=\log M=\frac12\sum_k\log(\lambda_k/\tau)_+,\qquad
D_2(R)=\sum_k\min(\lambda_k,\tau).
\]
Using \(\sqrt{D_2}\) as the linear-distortion proxy gives
\[
\gamma(R)\approx\frac{\tau}{D_2(R)}.
\]
With \(m\) active modes and small \(\beta\),
\[
\gamma\,\mathrm{PR}\approx\frac{2}{1+2\beta m}.
\]
There is no universal constant equal to one.

NUMERICAL: The reported rough-cell product has median \(0.7180\) and 10–90% range \(0.2931\)–\(1.2424\). The intermediate-cell median is \(1.0328\).

HEURISTIC: These measurements are compatible with scale-dependent quantization dimension. Interpreting the rough median as \(d_{\rm eff}=1/\gamma\) gives \(d_{\rm eff}/\mathrm{PR}\approx1.39\), but this describes the fitted construction over \(M=4,\ldots,256\). It establishes neither an intrinsic source dimension nor the optimal quantization exponent. Covariance eigenvalues alone, without a quantitative Gaussian approximation, establish no small-ball theorem.

**5. PROVEN UNDER two-sided source regularity and two-sided power distortion: the bits formula is a high-resolution law, not a general computational lower bound.**

For a compact regular \(d\)-dimensional source, with distortion comparable to angular distance raised to \(p\), covering constructions and small-ball bounds give
\[
D(M)\asymp C_lM^{-p/d}.
\]
Consequently,
\[
N_l(\varepsilon)
=\frac d p\log_2\frac{C_l}{\varepsilon^2}
\]
up to constants determined by the regularity and distortion bounds, with a floor at zero. Replacing \(C_l\) by the observed \(D_l(1)\) requires an additional calibration assumption.

PROVEN: A one-sided small-ball hypothesis supplies only the lower bound. Achievability needs covering or mass regularity and an upper distortion bound.

PROVEN: Direct radial merges are locally quadratic at fixed finite width and depth. The smooth \(p=3\) law belongs to frozen-Jacobian merges, not radial merges. The rough \(p=1\) law can describe only a scale window; increasing \(M\) eventually leaves it.

PROVEN UNDER the geometric Gaussian quantization asymptotic: a constant \(d_l\) is inappropriate across arbitrarily high precision. In the spectral regime, the required rate grows quadratically in \(\log(C_l/\varepsilon^2)\), before eventual finite-rank power-law behavior.

HEURISTIC: If \(d_l\asymp n/l\), then early fixed-depth cuts have dimension proportional to width, while cuts at a fixed fraction of \(L=\alpha n\) have dimension \(O(1)\). Coupled with the \(1/l\) residual profile, this explains why late angular compression can be cheap while early compression is expensive. It is not a lower bound on mean estimation.

PROVEN UNDER equal evaluation costs and free exact cell statistics: the inequality
\[
(D_l(1)/\varepsilon^2)^{d_l/p}<\varepsilon^{-2}
\]
compares full enumeration sufficient for a pointwise distortion target with plain sampling. It is not necessary for an integration method to beat sampling: mean errors may cancel, and an algorithm may sample the residual.

PROVEN UNDER a computable baseline with cost
\[
C(M)=aM+b\varepsilon^{-2}M^{-p/d}:
\]
optimizing \(M\) gives \(C_{\rm opt}\asymp\varepsilon^{-2/(1+p/d)}\). This can improve the precision exponent for every finite \(d\), although the gain becomes small at large \(d\). The assumption that the baseline is cheaply computable is essential.

PROVEN UNDER standard multilevel variance and cost hypotheses: optimal sampling work is
\[
\varepsilon^{-2}
\left(\sum_k\sqrt{v_kc_k}\right)^2,
\]
where \(v_k\) is level variance divided by the target variance. For dyadic depths, \(v_k\asymp1/l_k\) and \(c_k\asymp l_k\) give ideal work
\[
O(\varepsilon^{-2}\log^2 L),
\]
versus \(O(L\varepsilon^{-2})\) for plain sampling. Charging a reference trajectory and minimum level work adds \(O(L)\).

HEURISTIC: At \(L=\alpha n\), the advertised \(n/\log^2n\) gain therefore requires those coupling hypotheses and excluded or amortized setup. The bits formula alone provides no evidence that cell enumeration beats this shared-trajectory sampler.

PROVEN: The following audit uses the files read at **2026-11-01 23:33:56 UTC**. The two report generators were executed with their output-file writes intercepted in memory: `variance_made.md` matched exactly, and `bits5_posthoc_old.json` matched as parsed JSON.

1. **Critical — PROVEN — [§6.6(a)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:215): final-horizon survival is conflated with one-step survival.**  
   The drift argument survives, but the stated angle-only, time-independent conditional variance does not. There is an explicit counterexample at \(n=2\), initial angle \(\pi/2\). Conditional on first-layer survival, the active-count pair types have
   \[
   p=(4/9,4/9,1/9),\quad
   f=\left(\pi^2/4,\;\pi^2/6+\log^22,\;\pi^2/12\right),
   \]
   where \(f\) is the conditional squared log-ratio increment. Their probabilities of surviving the second layer average to
   \[
   q=(21/32,\;31/48,\;65/96).
   \]
   Thus the two first-increment variances are \(\sum p_if_i\) and
   \(\sum p_if_iq_i/\sum p_iq_i\), which differ.  
   **NUMERICAL:** They are \(2.13262442\) and \(2.12803793\).  
   **Fix:** use the stopped martingale and its bracket, or explicitly introduce horizon-dependent variances under final survival.

2. **Major — PROVEN — [§6.6(b)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:225): the statistic and limits are ambiguous.**  
   “\(n\operatorname{Var}\log|h_\infty|=10.63\)” must specify variance across inputs, averaged over weights, with a death convention and limit order. A single input’s variance across weights grows with depth; it is not this constant. The log-normal output formula and the \(t=O(n)\) extrapolation also do not inherit an exact label from fixed-depth mean field.  
   **Fix:** distinguish the fixed-depth leading theorem, numerical kernel sums, log-normal closure, and any separately proved joint-depth result.

3. **Moderate — NUMERICAL — [§6.6(b)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:226): the purported infinite profile is truncated.**  
   \(B_{4096}/2=10.62894963\), which rounds to the quoted \(10.63\). Using this truncated denominator also reproduces the quoted tail shares \(0.058\) and \(0.029\). The infinite values are approximately \(10.6505\), \(0.05954\), and \(0.03100\). The approximation \(5.5/(l+5.5)\) has the wrong tail coefficient; the coefficient is \(8.3401\).  
   **Fix:** identify the truncation or use a tail correction, and replace the rational approximation.

4. **Major — PROVEN — [§6.6(b), (d)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:229): one-reference distortion is not literally the future variance share.**  
   It depends on the reference policy and weighted angular distribution. For a typical independent reference, the rough prediction contains approximately twice the pairwise future variance share; a central reference changes that factor. In addition, the scorer substitutes an unweighted RMS angle to the k-means **centre**, whereas the evaluated merge uses a selected **member** as reference.  
   **Fix:** call \(D_R(1)\) a normalized one-reference distortion; identify the centre/member and RMS/weighted-mean substitutions as approximations.

5. **Moderate — NUMERICAL — [§6.6(c)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:232): the numerical summaries are correct, but the regime definitions need completion.**  
   I reproduce the variance ratios, the \(0.95\,[0.24,2.22]\) residual ratio, and the rough exponent statistics. The reported 77 intermediate and 62 smooth cells require thresholds \(0.5\le\theta_{\rm median}L'/2\le2\) and \(<0.5\), respectively; these differ from the smooth threshold used elsewhere. Moreover, among the 117 “rough” cells, only 55 have even the measured \(M=1\) quantity \(L'\phi>3\pi\); its median is \(9.0167\).  
   **Fix:** state the thresholds and distinguish the empirical bin from the asymptotic requirement \(L'\phi\gg3\pi\), separately at each cell resolution.

6. **Major — HEURISTIC — [§6.6(c)–(e)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:237): fitted dimension is promoted into source dimension.**  
   The values \(1.4\,\mathrm{PR}\) and \(1.75\,\mathrm{PR}\) are interpretations of fitted slopes for a particular construction. They do not establish the \(d\) in the small-ball theorem. Even the proposed geometric Gaussian model predicts a dimension that changes with resolution.  
   **Fix:** label these as empirical effective exponents over the tested \(M\)-range; independently establish source bounds before inserting them into a lower bound.

7. **Major — NUMERICAL — [§6.6(d)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:245): “matches on 88%” hides substantial censoring.**  
   The scorer’s result \(308/351=87.75\%\) is correct under its registered criterion. Its decomposition is:

   | Case | Cases | Agreements |
   |---|---:|---:|
   | Measured count \(>8\), censored | 251 | 249 |
   | Measured count \(=0\) | 36 | 36 |
   | Resolved, nonzero count | 64 | 23 |

   **Fix:** report both the registered agreement and the \(23/64=35.94\%\) agreement on resolved nonzero counts. The 88% figure alone does not demonstrate accurate bit-count prediction.

8. **Moderate — NUMERICAL — [§6.6(d)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:243): \((3\!-\!9)/l\) is not valid across the stated deep configurations and cuts.**  
   For \(L\ge n\), configuration/cut medians of \(lD_R(1)\) range from \(0.2113\) to \(8.5687\). For example, the table gives approximately \(0.844\) at \(256\times256,l=224\), and \(0.211\) at \(32\times128,l=112\).  
   **Fix:** restrict that calibration to the relevant rough cuts, and use the finite-horizon expression elsewhere. Also write the bits formula with a zero floor.

9. **Critical — PROVEN — [§6.6(e)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:248): the abstract theorem is valid, but its proposed global linear minorant is false for these nets.**  
   The stated \(\theta\le\phi_0\) and \(KM\ge1\) conditions correctly handle truncation. However, \(\rho_{n,t}(\phi)\le\phi^2\) rules out every positive global linear minorant. Calling it “the mean-field variogram” does not repair this: strict mean field lacks the finite-width linear term altogether.  
   **Fix:** prove a crossover or restricted-scale minorant and restrict the usable cell radii accordingly. The resulting bound is not an arbitrarily high-resolution \(p=1\) bound.

10. **Critical — PROVEN — [§6.6(e)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:251): the actual angular law has atoms, so the global small-ball hypothesis also fails when those rays survive.**  
    \(W_1\) is invertible almost surely. For each coordinate \(i\), the open input cone with exactly neuron \(i\) active has positive spherical measure, and all its first-layer outputs lie on the ray \(e_i\). Its radius-weighted mass is positive. If that ray survives to layer \(l\), homogeneity preserves an angular atom. A bound \(P_w(B(c,r))\le K(r/\theta)^d\), \(d>0\), cannot hold at that atom as \(r\downarrow0\).  
    **Fix:** formulate a quantitative bound for a restricted bulk law, account for exceptional mass, and specify that assignments as well as references are future-independent.

11. **Major — PROVEN — [§6.6(e)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:258): “nearly attained” does not follow from the measurements.**  
    A slope from one construction, combined with unverified source and minorant hypotheses, supplies neither a matching optimal exponent nor an achievability theorem for the proposed dimension.  
    **Fix:** retain the conditional lower bound and describe the measurements as empirical comparison. A matching theorem requires upper covering and upper distortion bounds over the same scale range.

12. **Major — PROVEN — [§6.6(f)](/home/agent/workspaces/mats/work/bits-bounds/FORMAL.md:261): a pointwise representation bound is used as a necessary condition for beating sampling.**  
    Mean estimation can benefit from cancellation, stratification, and sampled residuals without meeting the full pointwise distortion target. Prefix integration, assignments, reference construction, and multilevel setup also have costs.  
    **Fix:** present the displayed inequality as an idealized enumeration comparison. Compare complete estimators using their mean-square errors and charged costs; no separation from the shared-trajectory sampler follows from this cell-count argument.

PROVEN: The attribution to [input-bits §2.2](/home/agent/workspaces/mats/outbox/input-bits-2026-10-31.md:109) is correct. Its notation satisfies
\[
B(c)=4k_2(c)-1,\qquad
\frac14\sum_j[5-B(c_j)]
=\frac12\sum_j b(\theta_j)=\frac{B_L}{2}.
\]
The source contains the \(5.5,7.2,8.6,9.5,10.0\) profile and \(C_\infty=10.65\). The later combination with cloud geometry and quantization exponents is the bits-bounds contribution; those extra claims need their own hypotheses.
