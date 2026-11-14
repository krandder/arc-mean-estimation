codex
**S1 — PROVEN equality; FALSE numerical constants and “unavoidable error” wording.** For \(\sigma=\|w\|>0\), the round-1 Gaussian lifting proves
\[
\operatorname{spread}_0(Eh_{1,i})=\Gamma_d(N(0,\sigma^2)).
\]
Write \(s=\operatorname{sd}(T_+)=\sigma\sqrt{(\pi-1)/(2\pi)}\). Exact endpoints and spreads are:

| \(d\) | \(\inf E T_+\) | \(\sup E T_+\) | \(\Gamma_d/s\) | \(\Gamma_d/(2s)\) |
|---|---:|---:|---:|---:|
| 1 | \(0\) | \(+\infty\) | \(+\infty\) | \(+\infty\) |
| 2, 3 | \(0\) | \(\sigma/2\) | \(0.856429\) | \(0.428215\) |
| 4, 5 | \(\sigma/(2\sqrt3)\) | \(\sigma/2\) | \(0.361970\) | \(0.180985\) |

For \(d=2,3\), the infimum is unattained; for \(d=4,5\), the supremum is unattained. Symmetrization removes odd constraints. Cauchy–Schwarz gives the upper endpoint; interpolation gives \(E|T|\ge \sigma/\sqrt3\) at orders 4–5. The formula with prefactor \(1/2\) is already the **ReLU** spread; the \(|T|\) spread is twice that.

The round-1 asymptotic remains
\[
\Gamma_d/s\sim 1.68605/d.
\]
This is the **spread**; the minimax absolute error is half. Neither is an error lower bound at the Gaussian law itself. For \(w=0\), the actual spread is zero.

**S2 — PROVEN, with two qualifications.** For the mathematical definitions,
\[
\mathrm{gap(all)}\le\mathrm{gap(input)}\le\mathrm{prop}.
\]
The first inclusion is immediate; the second follows by choosing every block equal to the same input-feasible \(Q\).

Every consistent closure path, **including the final activation-mean update**, is feasible. Conversely, every feasible path can be realized by layer-specific consistent rules, extended arbitrarily elsewhere. Thus the prop interval is precisely the closure-output range, with endpoints understood as infimum/supremum. The true \(P_0\) path is included.

If that interval is \([\ell,u]\) and \(y_0=E_{P_0}f\), worst-case consistent-closure error at \(P_0\) is
\[
\max(u-y_0,y_0-\ell),
\]
not necessarily \(\mathrm{prop}/2\). Separately, every estimator whose input-law information consists only of \(m_0\) satisfies
\[
\sup_{Q\in A_d(\mathrm{input})}|\widehat y-E_Qf|
\ge \tfrac12\mathrm{gap(input}).
\]

**S3 — FALSE universally: re-selection can help, and no finite deterministic universal \(C\) exists.** Here is a Gaussian-input counterexample for every finite \(d\ge1\), width 5 and depth 3. Use two input coordinates \(x,y\), and set
\[
h_1=(A,B,C,D,E)
=(x_+,(-x)_+,(y+x)_+,(y-x)_+,(-y)_+),
\]
\[
h_2=((C-D)_+,D,A,B,E),\qquad
h_3=((h_{2,1}+h_{2,2}-h_{2,3}-h_{2,4})_+,h_{2,5},0,0,0).
\]
Then \(h_3=(y_+,(-y)_+,0,0,0)\), so choose \(f=h_{3,1}-h_{3,2}=y\). Consequently \(\mathrm{gap(input)}=0\).

Yet \(y\) is outside the span of degree-\(\le d\) polynomials in \(h_1\): homogeneity would force a linear representation; the distinct kink lines force the coefficients of \(C,D,E\) to vanish, making that impossible. Therefore bounded density perturbations \(Q_\pm=(1\pm\epsilon b)P_0\) exist preserving all those moments but changing \(Ey\). One construction projects \(y\) onto that polynomial span on a compact region and uses the bounded residual as \(b\).

Taking \(q^{(0)}=P_0\), \(q^{(1)}=q^{(2)}=Q_\pm\) proves \(\mathrm{prop}>0\). This is a fixed-weight counterexample, not a typical-He claim.

**PROVEN:** for \(d\ge2\), a crude absolute bound is
\[
\mathrm{prop}\le 2\|a\|_2\sqrt n\prod_{\ell=1}^L\|W_\ell\|_{\mathrm{op}}.
\]
It follows by propagating second-moment bounds through each feasible block. Depth monotonicity fails: an all-negative next matrix kills nonnegative activations.

**HEURISTIC:** closeness for typical random networks may reflect approximately determined transitions or an insensitive final objective. The reported LP ratios establish neither explanation nor a typical-network bound.

**S4 — FALSE as the proposed causal conclusion; PROVEN that the ambiguity bound does not establish Gaussian-input error.** A large worst-case ambiguity does **not** exclude moment closure as ARC’s error mechanism. It shows that this law-agnostic minimax argument does not quantify ARC’s error on its promised Gaussian input. A valid negative result must establish error within that promise; it may be worst-case over weights rather than average-case.

For errors \(e_j\) and output standard deviations \(\sigma_j\),
\[
\sqrt{\mathrm{nMSE}}
=\sqrt{\frac{\sum_j\sigma_j^2(e_j/\sigma_j)^2}{\sum_j\sigma_j^2}}.
\]
This is a **variance-weighted** RMS standardized error, not generally an equally weighted per-neuron RMS. It measures final error after propagation, not a sum of layer errors.

Comparing this with a first-layer unit’s normalized half-spread is only a scale comparison. For a linear readout, the relevant quantities are \(a^\top e\) and \(\sqrt{a^\top\operatorname{Cov}(h_L)a}\); correlations and cancellation matter. Using your supplied nMSE values and the corrected half-spreads gives illustrative ratios approximately **14, 30, 19**, assuming \(K=d\), not a common-target theorem.

**S5 — PROVEN framework; CONJECTURE of a positive bound for the relevant deeper Gaussian-generated families.** The cleanest restriction is a universal local rule
\[
\widehat Y=\Phi_\ell(m_\ell,W_{\ell+1}),
\]
fed **true moments**, with no upstream weights, history, or extra state. Require permutation equivariance if desired, but equivariance alone provides no lower bound.

For random upstream networks with Gaussian inputs, let \(M=m_\ell\) and let \(Y\) be the true next statistic. Then
\[
\inf_\Phi E\|Y-\Phi(M,W)\|^2
=E\,\operatorname{tr}\operatorname{Cov}(Y\mid M,W).
\]
Thus a positive average-case bound requires proving positive conditional variance. A worst-case bound instead follows from two Gaussian-generated hidden laws with identical \(M\), the same next weights, and different \(Y\).

**PROVEN limitations:** at the first hidden layer, \(h_1=\operatorname{ReLU}(Z)\) for centered Gaussian \(Z\); its second moments identify the covariance of \(Z\) through the strictly increasing ReLU kernel. Hence \(d\ge2\) identifies its entire law, allowing exact next-step integration. At \(d=1\), \((Z_+,Z_+)\) and \((Z_+,(-Z)_+)\) give an explicit collision, distinguished by \(g(h)=(h_1-h_2)_+\).

For deeper layers and \(d=2,3,4\), positivity and useful quantitative rates remain **CONJECTURE here**. Extending a local bound to ARC also requires handling approximate states, possible history encoding, and downstream cancellation.

**PROVEN implementation caveat, inspected 2026-11-03:** [ps.py:128](/home/agent/workspaces/mats/work/cumulant-ambiguity/ps.py:128) restricts block \(q^{(\ell)}\) using both reference masks `vals[l]` and `vals[l+1]`. Propagated moments need not retain the reference’s null relations. These masks can therefore exclude legitimate sequential paths; in particular, an input-feasible law need not pass every later mask. The mathematical ordering does not automatically certify the reported masked LP ordering. Exact propagation requires retaining the original moment constraints, or proving each discarded relation and support restriction valid on every reachable path.
