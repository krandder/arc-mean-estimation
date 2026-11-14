# Literature: what each result says, and what it implies for deep random ReLU nets

Source of every quote, URL and status: notes/LITERATURE_raw.md (a verification worker fetched arXiv/ECCC/LIPIcs/author
pages, 13:09-13:43Z; VERIFIED unless marked). Implications are mine [C]; labels as in FORMAL.md.

## 1. Worst-case PRGs (fool every function in a class)
| result | class, distribution | seed length | status |
|---|---|---|---|
| Meka-Zuckerman, STOC'10 / SICOMP'13 | halfspaces; degree-d PTFs, {-1,1}^n | O(log n + log^2(1/eps)); 2^{O(d)} log n / eps^{8d+3} | VERIFIED |
| Gopalan-Kane-Meka, FOCS'15 / SICOMP'18 | halfspaces, {0,1}^n | O(log(n/eps) (log log(n/eps))^2) | VERIFIED |
| Kane CCC'14; OST STOC'20; OST+Kane arXiv 2103.07809; Kelley-Meka CCC'22 | degree-d PTFs, Gaussian | O_{c,d}(log n eps^-c); d^{O(log d)} log n (const. eps); poly(d/eps) log n; d^{O(1)} log(n/eps) log(1/eps)/eps^2 | VERIFIED |
| Harsha-Klivans-Meka, STOC'10 / JACM'12 | intersections of k halfspaces, Gaussian | O(log n poly(log k, 1/eps)) | VERIFIED |
| O'Donnell-Servedio-Tan, STOC'19 / JACM'22 | m-facet polytopes, {0,1}^n | poly(log m, 1/eps) log n | VERIFIED |
| Chattopadhyay-De-Servedio, CCC'19 | any Boolean function of k LTFs; AND of k LTFs; Gaussian | O(log n + poly(k, 1/eps)); O(log n + poly(log k, 1/eps)) | VERIFIED |
| Hatami-Hoza-Tal-Tell, FOCS'21 | depth-d threshold circuits with n^{1+delta} wires, delta = 2^{-O(d)}, Boolean | O(n^{1-delta}), error 2^{-n^delta} | VERIFIED |
| Chen-Li-Li-Meka, arXiv 2201.07206 | constant-depth poly-size ReLU discriminators | fooling all of them would imply TC0 != NC1 (a barrier) | VERIFIED |
Implications [C]. (i) The only structure of a ReLU net these cover is the first layer: its gate pattern is a function
of k = n origin halfspaces (CDS: seed O(log n + poly(n, 1/eps)), no better than n bits), and one first-layer cell is an
intersection of n halfspaces (HKM/CDS: O(log n + poly(log n, 1/eps))). Deeper gates are halfspaces of h_{l-1}, not of
x. (ii) Threshold-circuit PRGs stop at n^{1+delta} wires with delta = 2^{-O(d)}; a width-n ReLU layer has n^2 wires,
so even the Boolean analogue of ARC's net is out of range, and the GAN barrier says fooling all constant-depth ReLU
nets would separate TC0 from NC1. Worst-case derandomisation of ReLU nets is a frontier problem (consistent with the
hardness lane). (iii) None of it bears on ARC's average-case problem, where a fixed oblivious design already matches MC
(FORMAL T3): worst-case PRG seeds are long because the class contains adversarial functions, which ARC's ensemble does
not weight.

## 2. Bounded independence
DGJSV FOCS'09: k = O(log^2(1/eps)/eps^2)-wise independence fools halfspaces ({-1,1}^n; lower bound
Omega(1/(eps^2 log(1/eps)))). DKN FOCS'10: poly(1/eps) for degree 2 (Boolean and Gaussian). Kane CCC'11:
O_d(eps^{-4d 7^d})-independent Gaussians fool degree-d PTFs. GOWZ CCC'10: O(d^4 s^2/eps^2)-wise for size-s depth-d
decision trees of halfspaces. All VERIFIED. Nothing for ReLU nets (named searches; LITERATURE_raw A15).
Implication [C]: these are uniform guarantees over all k-wise independent laws; the supporting sets have ~n^{k/2}
points with k ~ 1/eps^2, astronomically more than MC's 1/eps^2 for one function. The lane measures the specific
polynomial-hash k-wise designs (full GF(q)^k enumeration) on the nets: at the sizes resolved they are MC-like at their
own size (dev: nMSE x N = 0.2-3 for k = 2-4); there is no k at which they start to "fool" a deep net faster than MC.

## 3. Noise sensitivity and Gaussian surface area
Kane CCC'10 / Comput. Complexity'11: degree-d PTFs have GSA <= d/sqrt(2 pi) and NS_eps ~ d sqrt(2 eps)/pi (tight for
products of d homogeneous linear forms). KOS FOCS'08: NS_delta(K) <= sqrt(pi delta) Gamma(K); Hermite concentration
O(Gamma^2/eps^2); Nazarov: Gamma(intersection of k halfspaces) <= sqrt(2 ln k) + 2 (KOS's Fact 4 misprints a halfspace's
GSA as 0.8; it is 1/sqrt(2 pi)). Hanin-Rolnick ICML'19: region-boundary (Lebesgue) volume ~ #neurons per unit volume,
needing biases with bounded density (vacuous for bias-free nets). De Palma-Kiani-Lloyd NeurIPS'19: random deep ReLU
classifiers of bit strings are biased to simple (noise-stable) functions. Jonasson-Steif-Zetterqvist SPA'23: bias-free
SIGN-activation deep nets are quenched noise sensitive once depth >> log(1/eps_n); with biases (Jonasson 2026) the
annealed covariance stays bounded away from zero via the net-dependent mean.
Implications [C]: the gate partition of a bias-free He-ReLU net is the Gaussian analogue of Hanin-Rolnick's count:
GSA n/sqrt(2 pi) per layer at layer 1 exactly (a hyperplane arrangement), measured 0.7-1.2 x that at depth (FORMAL T7;
registered PN1-PN3), so the pattern is noise-sensitive like JSZ's sign nets; the ReLU OUTPUT is not (Lipschitz, NS
linear in delta with slope ~ mean Hermite degree), like De Palma et al.'s simplicity bias. KOS's GSA-to-concentration
route concerns indicators (one cell has GSA O(sqrt(log n)) at layer 1 by Nazarov), not the output mean.

## 4. Randomness-efficient sampling
Chor-Goldreich J. Complexity'89 (via Goldreich's survey): pairwise-independent sampler, 1/(4 delta eps^2) samples, 2n
or 3n - 1 coins. Gillman SICOMP'98 (expander walks; constants UNVERIFIED): m + O(log(1/delta)/eps^2) coins in Vadhan's
table. Zuckerman RSA'97: (1 + alpha)(m + log(1/gamma)) coins. Canetti-Even-Goldreich IPL'95: any sampler for all
functions on {0,1}^n needs >= n + log2(1/delta) - log2(samples) - O(1) coins.
Implication [C]: the CEG lower bound (~input length) is for worst-case functions with a confidence delta; for ARC's
MSE criterion pairwise independence costs 2 n b coins for any N (registered PC4), and on the random-net ensemble even
zero coins suffice (FORMAL T3; weight-derived seeds [prior: unrestricted 3.1]).

## 5. QMC, designs and average-case integration
Owen SINUM'97 / J. Complexity'98: scrambled (0,m,s)-nets have Var <= e Var_MC and o(1/N) for every L^2 f; (t,m,s)-nets
<= b^t ((b+1)/(b-1))^s Var_MC (vacuous for Sobol in 256 dims). Owen AoS'97: O(N^-3 (log N)^{s-1}) for smooth f.
He-Wang SINUM'15: RMSE O(N^{-1/2 - 1/(4d-2) + eps}) for certain discontinuous f in d dims. Griewank-Kuo-Leovey-Sloan
JCAM'18 (preintegration smooths kinks, under monotonicity) and Gilbert-Kuo-Sloan 2022 (not smoothing without it): the
sibling preint lane's topic. Wozniakowski BAMS'91 / Novak-Wozniakowski Vol. II Cor. 13.1 (VERIFIED-r): the
average-case error of a linear rule equals the worst-case error on the RKHS of the covariance kernel (a discrepancy).
Delsarte-Goethals-Seidel'77 (VERIFIED-r via Bannai-Bannai): a spherical 2e-design has >= C(n+e-1, e) + C(n+e-2, e-1)
points, a (2e+1)-design >= 2 C(n+e-1, e). Calderbank-Cameron-Kantor-Seidel PLMS'97: Z4-Kerdock codes and extremal
line-sets (the MUB/5-design property is checked numerically here, tests/test_rnd.py, not from the paper).
Implications [C]: (i) FORMAL T2 is Wozniakowski's identity for the random field g_W with covariance kernel
k(t) = E_W <g(u), g(v)>: ARC's average-case problem, restricted to linear rules, IS average-case integration in that
kernel, and designs are its quadrature rules. (ii) At n = 256 the DGS bound for a 5-design is 65,792 points; the
antipodal Kerdock set has 66,048, within 0.4% of tight, and a 7-design needs >= 5.66e6 points (87x ARC's budget): the
Kerdock set is essentially the strongest design affordable at ARC's budget. (iii) Owen's o(1/N) means RQMC beats MC by
an unbounded factor as N -> infinity at FIXED n, but He-Wang's exponent 1/(4d - 2) is ~0.001 at d = 256: no useful
rate (registered PQ1).

## 6. Deterministic approximate counting
GKMSVV FOCS'11: deterministic FPTAS for #Knapsack. De-Diakonikolas-Servedio (arXiv 1311.7105): degree-2 PTFs in
poly(n, 2^{poly(1/eps)}) (Boolean), poly(n, 1/eps) (Gaussian); De-Servedio STOC'14: degree d in O_{d,eps}(1) poly(n^d);
CDS'19: functions of k LTFs in poly(n) 2^{poly(k, 1/eps)}. Elekes'86 / Barany-Furedi (exact statements UNVERIFIED;
Dadush-Vempala's restatement VERIFIED): deterministic membership-oracle volume estimation needs Omega(1/eps)^n queries.
Implication [C]: deterministic counting reaches constant additive eps in poly time for depth-1 classes, with
super-polynomial cost in 1/eps (except Gaussian degree 2); nothing exists for compositions of halfspaces of
halfspaces. The Elekes-type separation is worst-case (an adversarial body against fixed queries); on ARC's ensemble a
fixed design is as good as MC on average (FORMAL T3), so that separation does not transfer.
