# LITERATURE_raw — citation and theorem verification

Lane: randomness complexity of estimating the output mean of deep random ReLU nets.
Compiled 2026-11-02, 13:09–13:43 UTC, by a literature-verification worker. These are raw inputs for the lane, not conclusions.

**Status legend**
- **VERIFIED**: the quoted statement comes from a primary page I fetched (arXiv API/abs/PDF, ECCC, LIPIcs, or an author-hosted PDF). Venue, pages and DOI come from Crossref (the DOI registry).
- **VERIFIED-m**: the publisher page blocked me (403/bot wall). The abstract text comes from OpenAlex's copy of the publisher abstract (`api.openalex.org/works/doi:...`), and the bibliographic data from Crossref.
- **VERIFIED-r**: I could not reach the original. The statement comes from a named primary restatement by an author or an expert (for example Goldreich's own survey, or Novak–Woźniakowski).
- **PARTIAL**: the bibliographic facts are verified, but the specific statement you asked for is UNVERIFIED (reason given).
- **UNVERIFIED**: I could not fetch it. I say what I tried.

**Blocked sources**: dblp.org and its mirrors (Anubis bot challenge), so DBLP was replaced by the Crossref API. Also blocked: epubs.siam.org (403), projecteuclid.org (Incapsula), link.springer.com (JS/login wall), ams.org (403), academiccommons.columbia.edu (Anubis).

**Quoting**: quotes marked "abstract" are verbatim from the arXiv API, ECCC HTML or OpenAlex. Quotes marked "PDF" are verbatim from pypdf text extraction, with only whitespace, sub/superscripts and ligatures normalised.

## Summary (10 rows)

| Items | Seed length / rate / bound (short) | Status |
|---|---|---|
| A1–A3 | MZ: degree-d PTF 2^{O(d)} log n/ε^{8d+3} (Boolean); halfspaces O(log n + log²(1/ε)); non-explicit O(d log n + log(1/ε)). DGJSV: k = O(log²(1/ε)/ε²)-wise independence (LB Ω(1/(ε² log(1/ε)))). DKN: k = poly(1/ε) for d = 2, Boolean and Gaussian | VERIFIED |
| A4–A6 | Kane: O_d(ε^{-4d·7^d})-wise independent Gaussians fool degree d. Kane seeds: log n·2^{O(d)}ε^{-4-c} (FOCS11), O_{c,d}(log n·ε^{-c}) (CCC14), polylog for d = 2 (CCC15). OST STOC20: d^{O(log d)}·log n. OST+Kane arXiv: poly(d/ε)·log n. Kelley–Meka: d^{O(1)} log(n/ε) log(1/ε)/ε² (all Gaussian) | VERIFIED |
| A7–A12 | GKM: halfspaces O(log(n/ε)(loglog(n/ε))²). HKM: Gaussian k-polytopes O(log n·poly(log k, 1/δ)). OST: Boolean m-polytopes poly(log m, 1/δ)·log n. CDS: Gaussian, f(k LTFs) O(log n + poly(k, 1/ε)) and AND of k LTFs O(log n + poly(log k, 1/ε)). GOWZ: O((d log(ds/ε) + log n) log(ds/ε)) and O(d⁴s²/ε²)-wise. ST: poly(log n, log k, t, 1/δ) | VERIFIED |
| A13–A15 | HHTT: depth-d LTF circuits with n^{1+δ} wires, δ = 2^{-O(d)}, have seed O(n^{1-δ}) and error 2^{-n^δ} (Boolean). KW: depth-2 LTF lower bounds o(ε³n^{3/2}/log³n) gates and o(ε³n^{5/2}/log^{7/2}n) wires. NN/ReLU-specific PRGs: **none found**; closest are "Fooling Thresholds of Halfspaces" (2026) and the GAN barrier (2022) | VERIFIED |
| B16–B17 | Kane: degree-d PTF GSA ≤ d/√(2π), Gaussian NS ~ d√(2ε)/π (tight). KOS: NS_δ(K) ≤ √π·√δ·Γ(K); Hermite concentration O(Γ²/ε²). Nazarov: Γ(∩ of k halfspaces) ≤ √(2 ln k) + 2 | VERIFIED |
| B18 | Hanin–Rolnick: E[vol_{n−k}(B_{N,k}∩K)]/vol(K) ≤ C(#neurons, k)·(C_grad·C_bias)^k (k = 1: linear in #neurons; needs bounded bias density). De Palma et al.: closest differently-classified string ≥ √(n/(2π log n)). JSZ: sign-activation nets are QNS once depth ≫ log(1/ε_n) | VERIFIED |
| C19–C23 | Pairwise sampler: 1/(4δε²) samples, 2n or 3n−1 coins. CEG lower bounds: samples ≥ min{2^{(n−4)/2}, ln(1/O(δ))/(4ε²)}; coins ≥ n + (1−o(1))log₂(1/δ) − 2log₂(1/ε) at O(log(1/δ)/ε²) samples. Best efficient: n + log₂(1/ε) + O(log(1/δ)). Zuckerman: (1+α)(m + log γ⁻¹) bits | VERIFIED-r / VERIFIED-m; Gillman's exact constants UNVERIFIED |
| D24–D28 | Scrambled (0,m,s)-nets: Var ≤ e ≈ 2.718 × MC variance; (t,m,s): b^t((b+1)/(b−1))^s ×; o(1/n) for all L². Smooth f: Var O(n^{-3}(log n)^{s−1}). He–Wang: RMSE O(n^{-1/2−1/(4d−2)+ε}) for discontinuous f. Preintegration smooths only under monotonicity | VERIFIED-m / VERIFIED |
| D29–D32 | Wiener sheet: e^avg(Q) = disc₂({1−t_j},{a_j}); complexity Θ(ε^{-1}(ln ε^{-1})^{(d−1)/2}). e^avg = e^wor on the RKHS of the covariance. DGS: \|X\| ≥ C(n+e−1, e) + C(n+e−2, e−1) for t = 2e, and 2·C(n+e−1, e) for t = 2e+1. CCKS: MUB / design-strength statement | VERIFIED-r; CCKS design strength UNVERIFIED |
| E33–E35 | #Knapsack FPTAS (deterministic). DDS degree 2: poly(n, 2^{poly(1/ε)}) Boolean, poly(n, 1/ε) Gaussian. De–Servedio degree d: O_{d,ε}(1)·poly(n^d). Elekes and Bárány–Füredi exact statements | VERIFIED; Elekes/BF statements UNVERIFIED |

---

## A. Gaussian / Boolean PRGs and bounded independence

### A1. Meka–Zuckerman, PRGs for PTFs
- **Authors / title**: Raghu Meka, David Zuckerman, "Pseudorandom Generators for Polynomial Threshold Functions".
- **Venue**: STOC 2010, pp. 427–436, doi:10.1145/1806689.1806749. Journal: SIAM J. Comput. 42(3):1275–1301 (2013), doi:10.1137/100811623.
- **arXiv / URLs fetched**: arXiv:0910.4122v5, via https://export.arxiv.org/api/query?id_list=0910.4122, https://arxiv.org/abs/0910.4122 and https://arxiv.org/pdf/0910.4122.
- **Abstract**: "We give a PRG with seed-length log n/eps^{O(d)} fooling degree d PTFs with error at most eps. [...] For the class of degree 1 threshold functions or halfspaces, we construct PRGs with much better dependence on the error parameter eps and obtain a PRG with seed-length O(log n + log^2(1/eps)). [...] We also obtain PRGs with similar seed lengths for fooling halfspaces over the n-dimensional unit sphere."
- **arXiv comments**: "Revision 2: Corrected the non-explicit bound to O(d log n + log(1/eps))". "Revision 4: Improves seed-length for halfspaces to O(log n + log^2(1/eps))".
- **Theorems (PDF v5)**: Thm 1.2: "For 0<ǫ<1, there exists an explicit PRG fooling PTFs of degree d with error at most ǫ and seed length 2^{O(d)} log n/ǫ^{8d+3}." Thm 1.3: "For all constants c, ǫ ≥ 1/n^c, there exists an explicit PRG fooling halfspaces with error at most ǫ and seed length O(log n + log²(1/ǫ))." Acknowledgements: "The preliminary version of this work appearing in STOC 2010 had a worse seed-length of O(log n log(1/ǫ))."
- **Distribution**: uniform {−1,1}^n (PTFs, halfspaces); the unit sphere (Thm 1.4: caps, for ε > c log n/n^{1/4}). There is no Gaussian theorem as such. However, OST+Kane (arXiv:2103.07809, Table 1) list [MZ13] at (d/ε)^{O(d)}·log n for Gaussian PTFs and note "The generators of [MZ13, DKN10] work for the more general setting of Boolean space".
- **Status**: VERIFIED. Explicit, plus the non-explicit bound above.

### A2. DGJSV, Bounded independence fools halfspaces
- **Authors / title**: Ilias Diakonikolas, Parikshit Gopalan, Ragesh Jaiswal, Rocco A. Servedio, Emanuele Viola, "Bounded Independence Fools Halfspaces".
- **Venue**: FOCS 2009, pp. 171–180, doi:10.1109/FOCS.2009.68. Journal: SIAM J. Comput. 39(8):3441–3462 (2010), doi:10.1137/100783030.
- **arXiv / URL**: arXiv:0902.3757, via the arXiv API and https://arxiv.org/abs/0902.3757.
- **Abstract**: "We show that any distribution on {-1,1}^n that is k-wise independent fools any halfspace h with error \eps for k = O(\log^2(1/\eps) /\eps^2). Up to logarithmic factors, our result matches a lower bound by Benjamini, Gurel-Gurevich, and Peled (2007) showing that k = Ω(1/(\eps^2 \cdot \log(1/\eps))). [...] Specifically, we fool halfspaces with error eps and seed length s = k \log n = O(\log n \cdot \log^2(1/\eps) /\eps^2)."
- **Distribution**: Boolean {−1,1}^n. Explicit.
- **Status**: VERIFIED.

### A3. Diakonikolas–Kane–Nelson, degree-2
- **Authors / title**: Ilias Diakonikolas, Daniel M. Kane, Jelani Nelson, "Bounded Independence Fools Degree-2 Threshold Functions".
- **Venue**: FOCS 2010, pp. 11–20, doi:10.1109/FOCS.2010.8. No journal version found.
- **arXiv / URL**: arXiv:0911.3389v2, via the arXiv API.
- **Abstract**: "Let x be a random vector coming from any k-wise independent distribution over {-1,1}^n. For an n-variate degree-2 polynomial p, we prove that E[sgn(p(x))] is determined up to an additive epsilon for k = poly(1/epsilon). [...] explicit generators that epsilon-fool the class of degree-2 threshold functions with seed length log(n)*poly(1/epsilon). [...] the intersection of any constant number of degree-2 threshold functions is epsilon-fooled by poly(1/epsilon)-wise independence. Our results also hold if the entries of x are k-wise independent standard normals".
- **Concrete exponent**: OST+Kane Table 1 gives "[DKN10] Õ(1/ε^9)·log n, d ≤ 2". MZ write "seed-length (log n)·Õ(1/ǫ^9) for degree 2 PTFs".
- **Distribution**: Boolean and Gaussian.
- **Status**: VERIFIED.

### A4. Kane, k-independent Gaussians fool PTFs (and other independence results)
- **Authors / title**: Daniel M. Kane, "k-Independent Gaussians Fool Polynomial Threshold Functions".
- **Venue**: CCC 2011, pp. 252–261, doi:10.1109/CCC.2011.13.
- **arXiv / URL**: arXiv:1012.1614v3, via the arXiv API.
- **Abstract (full)**: "We show that any $O_d(ε^{-4d 7^d})$-independent family of Gaussians $ε$-fools any degree-$d$ polynomial threshold function."
- **Distribution**: Gaussian only.
- **Related Kane independence results**, from "A Structure Theorem for Poorly Anticoncentrated Gaussian Chaoses and Applications to the Study of PTFs" (FOCS 2012, pp. 91–100, doi:10.1109/FOCS.2012.52; Annals of Probability 45(3):1612–1679 (2017), doi:10.1214/16-AOP1097; arXiv:1204.0543v2; PDF fetched):
  - Thm 22: "there exist integers k = O(d/c) and N = O_{c,d}(ǫ^{−2−c}) so that for any random variable X = (1/√N) Σ_{i=1}^N X_i where the X_i are chosen independently from k-independent distributions of Gaussians, and for any degree-d polynomial threshold function f, |E[f(X)] − E_{Y∼N}[f(Y)]| < ǫ." This is a sum of N independent k-wise families, not plain k-wise independence.
  - Thm 52 (Boolean): uses a 2-independent hash h:[n]→[a] with a = ǫ^{−6} and k-independent families with k = ǫ^{−5} + 4d. "A can be generated from a seed of length O(log(n)ǫ^{−11}) [...] |E[f(A)] − E[f(B)]| = O_{c,d}(ǫ^{1−c})". Remark: "a PRG with seed length O_{c,d}(log(n)ǫ^{−11−c})".
- **Status**: VERIFIED.

### A5. Kane, Gaussian PTF PRGs
- **Main item**: Daniel M. Kane, "A Pseudorandom Generator for Polynomial Threshold Functions of Gaussian with Subpolynomial Seed Length". The exact title has "Gaussian", singular. CCC 2014, pp. 217–228, doi:10.1109/CCC.2014.30. arXiv:1210.1280.
- **Abstract (full)**: "We develop a pseudorandom generator that fools degree-$d$ polynomial threshold functions in $n$ variables with respect to the Gaussian distribution and has seed length $O_{c,d}(\log(n) ε^{-c})$."
- **Kane FOCS 2011**: "A Small PRG for Polynomial Threshold Functions of Gaussians", pp. 257–266, doi:10.1109/FOCS.2011.16, arXiv:1104.1209. Abstract: "For $c>0$ any constant, we construct a pseudo-random generator that fools such functions to within $ε$ and has seed length $\log(n) 2^{O(d)} ε^{-4-c}$."
- **Kane CCC 2015**: "A Polylogarithmic PRG for Degree $2$ Threshold Functions in the Gaussian Setting", arXiv:1404.1103. Abstract: "We manage to achieve $ε$ error with seed length polylogarithmic in $ε$ and the dimension". The venue (CCC 2015, pp. 567–581) and the bound O(log^6(1/ε) log log(n/ε) log n) both come from the bibliography and Table 1 of arXiv:2103.07809; not checked in Crossref.
- **Kane–Rao, Boolean degree 2**: Daniel Kane, Sankeerth Rao, "A PRG for Boolean PTF of Degree 2 with Seed Length Subpolynomial in epsilon and Logarithmic in n", CCC 2018, LIPIcs 102, 2:1–2:24 (authors from https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2018.2). Abstract (OpenAlex): "we give an explicit construction that uses a seed length of O(log n + (1/epsilon)^{o(1)})".
- **Status**: VERIFIED.

### A6. O'Donnell–Servedio–Tan, local hyperconcentration
- **Authors / title**: Ryan O'Donnell, Rocco A. Servedio, Li-Yang Tan, "Fooling Gaussian PTFs via local hyperconcentration".
- **Venue**: STOC 2020, pp. 1170–1183, doi:10.1145/3357713.3384281.
- **STOC abstract** (OpenAlex mirror of the ACM abstract): "We give a pseudorandom generator that fools degree-d polynomial threshold functions over n-dimensional Gaussian space with seed length d O(logd) · logn. All previous generators had a seed length with at least a 2 d dependence on d." That is, d^{O(log d)}·log n.
- **Full version**: arXiv:2103.07809v2 (9 Feb 2022). The arXiv author list is "Ryan O'Donnell, Rocco A. Servedio, Li-Yang Tan, Daniel Kane". Abstract: "seed length $\mathrm{poly}(d)\cdot \log n$". PDF Thm 1: "For all n,d ∈ N and ε ∈ (0,1), there is an explicit PRG with seed length poly(d/ε)·log n that ε-fools the class of all degree-d PTFs over n-dimensional Gaussian space." Footnote: "A preliminary version of this paper [OST20] appeared in [...] (STOC 2020)."
- **Concurrent work**: Zander Kelley, Raghu Meka, "Random restrictions and PRGs for PTFs in Gaussian Space", arXiv:2103.14134; CCC 2022, doi:10.4230/LIPIcs.CCC.2022.21. Abstract: "a PRG that takes a seed of $d^{O(1)}\log ( n / \varepsilon)\log(1/\varepsilon)/\varepsilon^2$ random bits [...] The best previous generator due to O'Donnell, Servedio, and Tan (STOC'20) had a quasi-polynomial dependence (i.e., seedlength of $d^{O(\log d)}$)".
- **Status**: VERIFIED. **Citation note**: the STOC 2020 paper proves d^{O(log d)}·log n. The poly(d) bound is in the later arXiv version, which adds Kane as an author.

### A7. Gopalan–Kane–Meka, DFT
- **Authors / title**: Parikshit Gopalan, Daniel M. Kane, Raghu Meka, "Pseudorandomness via the Discrete Fourier Transform".
- **Venue**: FOCS 2015, pp. 903–922, doi:10.1109/FOCS.2015.60. Journal: SIAM J. Comput. 47(6):2451–2487 (2018), doi:10.1137/16M1062132.
- **arXiv / URL**: arXiv:1506.04350v2, abstract via the API and PDF fetched.
- **Theorems (PDF)**: Thm 1.1: "There is an explicit generator G : {0,1}^r → [m]^n that fools all (m,n)-Fourier shapes with error ε, and has seed-length r = O(log(mn/ε)·(log log(mn/ε))²)." Cor 1.2: "There is an explicit generator G : {0,1}^r → {0,1}^n that fools halfspaces over {0,1}^n under the uniform distribution with error ε, and has seed-length r = O(log(n/ε)(log log(n/ε))²)."
- **Abstract**: "Our result gives a single pseudorandom generator that fools several important classes of tests computable in logspace [...] including halfspaces (over general domains), modular tests and combinatorial shapes."
- **Distribution**: Boolean / product domains.
- **Status**: VERIFIED.

### A8. Harsha–Klivans–Meka, invariance principle for polytopes
- **Authors / title**: Prahladh Harsha, Adam Klivans, Raghu Meka, "An Invariance Principle for Polytopes".
- **Venue**: STOC 2010, pp. 543–552, doi:10.1145/1806689.1806764. Journal: JACM 59(6):29 (2012), doi:10.1145/2395116.2395118.
- **arXiv / URL**: arXiv:0912.4884v2, via the API.
- **Abstract**: "For any (possibly unbounded) polytope P formed by the intersection of k halfspaces, we prove that |Pr [X belongs to P] - Pr [Y belongs to P]| < log^{8/5}k * Delta, where Delta is a parameter that is small for polytopes formed by the intersection of "regular" halfspaces [...] (2) A pseudorandom generator (PRG) with seed length O((log n)*poly(log k,1/delta)) that delta-fools all polytopes with k faces with respect to the Gaussian distribution. We also obtain PRGs with similar parameters that fool polytopes formed by intersection of regular halfspaces over the hypercube."
- **Status**: VERIFIED.

### A9. O'Donnell–Servedio–Tan, Fooling polytopes
- **Authors / title**: Ryan O'Donnell, Rocco A. Servedio, Li-Yang Tan, "Fooling Polytopes".
- **Venue**: STOC 2019, pp. 614–625, doi:10.1145/3313276.3316321. Journal: JACM 69(2), pp. 1–37 (2022), doi:10.1145/3460532.
- **arXiv / URL**: arXiv:1808.04035, abstract and PDF.
- **Abstract**: "We give a pseudorandom generator that fools $m$-facet polytopes over $\{0,1\}^n$ with seed length $\mathrm{polylog}(m) \cdot \log n$."
- **Thm 1.1 (PDF)**: "For all n,m ∈ N and δ ∈ (0,1), there is an explicit pseudorandom generator with seed length poly(log m, 1/δ)·log n that δ-fools the class of intersections of m halfspaces over {0,1}^n."
- **Status**: VERIFIED.

### A10. Chattopadhyay–De–Servedio, Gaussian processes
- **Authors / title**: Eshan Chattopadhyay, Anindya De, Rocco A. Servedio, "Simple and Efficient Pseudorandom Generators from Gaussian Processes".
- **Venue**: CCC 2019, LIPIcs 137, 4:1–4:33, doi:10.4230/LIPIcs.CCC.2019.4. Preprint: ECCC TR18-100. There is no arXiv version (title search returned nothing).
- **URLs**: https://eccc.weizmann.ac.il/report/2018/100/ and the LIPIcs PDF https://drops.dagstuhl.de/storage/00lipics/lipics-vol137-ccc2019/LIPIcs.CCC.2019.4/LIPIcs.CCC.2019.4.pdf.
- **Thm 2 (PDF)**: "There is an explicit PRG which ε-fools any Boolean function of k LTFs g(h1,...,hk) over N(0,1)^n, for any ε>0 and any k, with seed length O(log n + poly(k, 1/ε))." The PDF also gives a lower bound for this class of "max{⌊log n⌋,k} = Ω(k + log n)".
- **Thm 3 (PDF)**: "There is an explicit PRG which ε-fools any intersection of k LTFs over N(0,1)^n, for any ε>0 and any k, with seed length O(log n + poly(log k, 1/ε))."
- **Status**: VERIFIED.

### A11. Gopalan–O'Donnell–Wu–Zuckerman, product distributions
- **Authors / title**: Parikshit Gopalan, Ryan O'Donnell, Yi Wu, David Zuckerman, "Fooling Functions of Halfspaces under Product Distributions".
- **Venue**: CCC 2010, pp. 223–234, doi:10.1109/CCC.2010.29.
- **arXiv / URL**: arXiv:1001.1593, via the API.
- **Abstract**: "This class includes [...] the uniform distribution on the discrete cube, the uniform distribution on the solid cube, and the multivariate Gaussian distribution [...] To eps-fool any size-s, depth-d decision tree of halfspaces, our pseudorandom generator uses seed length O((d log(ds/eps)+log n) log(ds/eps)). For monotone functions of d halfspaces, the seed length can be improved to O((d log(d/eps)+log n) log(d/eps)). [...] any function computable by a size-s, depth-d decision tree of halfspaces is eps-fooled by O(d^4s^2/eps^2)-wise independence."
- **Note**: the last claim needs "a certain stronger moment condition" on each coordinate. Here "d" means the number of halfspaces, not polynomial degree.
- **Status**: VERIFIED.

### A12. Servedio–Tan, low-weight halfspaces
- **Authors / title**: Rocco A. Servedio, Li-Yang Tan, "Fooling intersections of low-weight halfspaces".
- **Venue**: FOCS 2017, pp. 824–835, doi:10.1109/FOCS.2017.81. **No journal version found.** The Servedio–Tan article in Theory of Computing 18 (2022) (doi:10.4086/toc.2022.v018a004) is a different paper, on AC0 / sparse F2 polynomial PRGs.
- **arXiv / URL**: arXiv:1704.04855, via the API.
- **Abstract**: "We give an explicit pseudorandom generator that $δ$-fools any intersection of $k$ weight-$t$ halfspaces with seed length poly$(\log n, \log k,t,1/δ)$."
- **Distribution**: Boolean.
- **Status**: VERIFIED.

### A13. Hatami–Hoza–Tal–Tell, constant-depth threshold circuits
- **Authors / title**: Pooya Hatami, William M. Hoza, Avishay Tal, Roei Tell, "Fooling Constant-Depth Threshold Circuits (Extended Abstract)".
- **Venue**: FOCS 2021, pp. 104–115, doi:10.1109/FOCS52979.2021.00019. Preprint: ECCC TR21-002 (rev. 1, 19 June 2021).
- **URL**: https://eccc.weizmann.ac.il/report/2021/002/.
- **Abstract**: "This PRG fools circuits with depth $d\in\mathbb{N}$ and $n^{1+\delta}$ wires, where $\delta = 2^{-O(d)}$, using seed length $O(n^{1-\delta})$ and with error $2^{-n^{\delta}}$. This tightly matches the best known lower bounds for this circuit class. [...] we construct a PRG for arbitrary functions of $s$ LTFs that can handle even the extreme setting of parameters $s=n/\mathrm{polylog}(n)$ and $\epsilon=2^{-n/\mathrm{polylog}(n)}$."
- **Revision note**: "Improved the PRG for TC0 to be strongly explicit".
- **Distribution**: Boolean inputs.
- **Status**: VERIFIED.

### A14. Kane–Williams, depth-2/3 threshold circuit lower bounds
- **Authors / title**: Daniel M. Kane, Ryan Williams, "Super-Linear Gate and Super-Quadratic Wire Lower Bounds for Depth-Two and Depth-Three Threshold Circuits".
- **Venue**: STOC 2016, pp. 633–643, doi:10.1145/2897518.2897636.
- **arXiv / URL**: arXiv:1511.07860, via the API.
- **Abstract**: "We prove that for all $ε\gg \sqrt{\log(n)/n}$, the linear-time computable Andreev's function cannot be computed on a $(1/2+ε)$-fraction of $n$-bit inputs by depth-two linear threshold circuits of $o(ε^3 n^{3/2}/\log^3 n)$ gates, nor can it be computed with $o(ε^{3} n^{5/2}/\log^{7/2} n)$ wires."
- **Related**: Lijie Chen, Avishay Tal, Yichuan Wang, "Superquadratic Lower Bounds for Depth-2 Linear Threshold Circuits", STOC 2026, pp. 874–885, doi:10.1145/3798129.3800802. Crossref metadata only; content not fetched.
- **Status**: VERIFIED.

### A15. PRGs / fooling / counting for neural networks — what exists
**Searches run**: arXiv API abstract searches for "pseudorandom generator" AND "neural network"; "pseudorandom generator" AND ReLU; "fools" AND "neural networks"; "approximate counting" AND "neural network"; "noise sensitivity" AND ReLU; "quasi-Monte Carlo" AND ReLU; "Gaussian surface area" AND "neural network"; "pseudorandom" AND "random neural network". Web searches for "pseudorandom generator fooling ReLU neural networks seed length Gaussian inputs", "deterministic approximate counting neural networks / ReLU networks / threshold networks", and "bounded independence fools neural networks". **I found no paper that gives a PRG, a bounded-independence result or deterministic approximate counting for ReLU / piecewise-linear networks as such.** The closest results:
- **Qin, Yao, Zhao, Zhou, "Fooling Thresholds of Halfspaces"**, arXiv:2609.21329 (18 Sep 2026; no venue yet). Status: VERIFIED. Abstract: "the generator designed by O'Donnell, Servedio, and Tan for polytopes [OST22] also fools this broader class. [...] the generator $δ$-fools every $k$-out-of-$m$ threshold of $m$ halfspaces over $\{-1,1\}^n$ with seed length $\widetilde{O}(κ^{6+2\varepsilon}\log^{6+2\varepsilon}\!m\cdotδ^{-(2+2\varepsilon)}\log n)$ [...] where $κ=\min\{k,m-k+1\}$. The random thinning argument also yields bounds on the noise sensitivity and Gaussian surface area for thresholds of halfspaces". This class is depth-2 threshold circuits with an unweighted top gate.
- **Chen, Li, Li, Meka, "Minimax Optimality (Probably) Doesn't Imply Distribution Learning for GANs"**, arXiv:2201.07206. Status: VERIFIED (abstract plus PDF). Abstract: "if local pseudorandom generators (PRGs) exist, then [...] there are ReLU network generators of constant depth and polynomial size which take Gaussian random seeds so that (i) the output is far in Wasserstein distance from the target distribution, but (ii) no polynomially large Lipschitz discriminator ReLU network can detect this." Thm 1.2 (PDF, informal): "If one could explicitly construct generators G : R^m → R^d for d = Ω(m log m) and unconditionally prove that no ReLU network discriminator of constant depth, polynomial Lipschitzness, and size slightly super-linear in d can tell apart the distributions G(I_m) and I_d with inverse polynomial advantage, then this would imply breakthrough circuit lower bounds, e.g. TC0 ≠ NC1." Section 4 is titled "Fooling ReLU Networks Would Imply New Circuit Lower Bounds". This is a barrier to fooling *all* constant-depth ReLU nets; it says nothing about fooling *random* nets.
- **De, Nadimpalli, O'Donnell, Servedio, "Sparsifying Suprema of Gaussian Processes"**, arXiv:2411.14664; STOC 2026, pp. 420–431, doi:10.1145/3798129.3800761. Status: VERIFIED. Abstract: "any intersection of (possibly infinitely many) halfspaces in $\mathbb{R}^n$ that are at distance $r$ from the origin is $\varepsilon$-close (under $N(0,I_n)$) to an intersection of only $O_{r,\varepsilon}(1)$ halfspaces." Also: "there is an $O_\varepsilon(1)$-size subset $S \subseteq T$ [...] such that [...] $\sup_{s \in S} \{\boldsymbol{X}_s + c_s\}$ is an $\varepsilon$-approximator (in $L^1$) of [...] $\sup_{t \in T} {\boldsymbol{X}}_t$".
- **Kothari–Meka, "Almost optimal pseudorandom generators for spherical caps"**, STOC 2015, pp. 247–256. Seed O(log(1/ε) log log(1/ε) + log n) for Gaussian halfspaces. Taken only from Table 1 and the bibliography of arXiv:2103.07809; paper not fetched; UNVERIFIED as to the primary source.
- **Servedio–Tan, "Deterministic approximate counting of polynomial threshold functions via a derandomized regularity lemma"**, RANDOM 2021. Listed on Servedio's papers page (fetched). Content not fetched; no arXiv hit for the title.
- **Avron, Sindhwani, Yang, Mahoney, "Quasi-Monte Carlo Feature Maps for Shift-Invariant Kernels"**, arXiv:1412.8293. QMC replaces MC over random features (Gaussian kernel), with error controlled by "box discrepancy". This is shift-invariant kernels only; I found nothing similar for arc-cosine/ReLU features. Status: VERIFIED.
- **Tangential**: Daniely–Vardi, "From Local Pseudorandom Generators to Hardness of Learning", arXiv:2101.08303. It is about hardness of learning, not fooling.

---

## B. Noise sensitivity and Gaussian surface area

### B16. Kane, GSA and noise sensitivity of degree-d PTFs
- **Authors / title**: Daniel M. Kane, "The Gaussian Surface Area and Noise Sensitivity of Degree-d Polynomial Threshold Functions".
- **Venue**: CCC 2010, pp. 205–210, doi:10.1109/CCC.2010.27. Journal: Computational Complexity 20(2):389–412 (2011), doi:10.1007/s00037-011-0012-6.
- **arXiv**: arXiv:0912.2709. The arXiv title differs: "The Gaussian Surface Area and Noise Sensitivity of Degree-$d$ Polynomials".
- **Abstract (full main claim)**: "if $f$ is a degree-$d$ polynomial threshold function, then its Gaussian sensitivity at noise rate $ε$ is less than some quantity asymptotic to $\frac{d\sqrt{2ε}}π$ and the Gaussian surface area is at most $\frac{d}{\sqrt{2π}}$. Furthermore these bounds are asymptotically tight as $ε\to 0$ and $f$ the threshold function of a product of $d$ distinct homogeneous linear functions."
- **Boolean analogue**: Kane, FOCS 2012 / AoP 2017 (arXiv:1204.0543, PDF), Thm 46: "If f is a degree-d polynomial threshold function, and if c, δ > 0, then NS_δ(f) = O_{c,d}(δ^{1/6−c})". Thm 47: "AS(f) = O_{c,d}(n^{5/6+c})".
- **Status**: VERIFIED.

### B17. Klivans–O'Donnell–Servedio, Gaussian surface area
- **Authors / title**: Adam R. Klivans, Ryan O'Donnell, Rocco A. Servedio, "Learning Geometric Concepts via Gaussian Surface Area".
- **Venue**: FOCS 2008, pp. 541–550, doi:10.1109/FOCS.2008.64.
- **URLs**: http://www.cs.columbia.edu/~rocco/papers/focs08.html (abstract) and the extended version http://www.cs.columbia.edu/~rocco/Public/13perim.pdf (author page).
- **Definitions (PDF)**: Def 1: "Γ(A) := liminf_{δ→0} vol(A_δ \ A)/δ", with vol the Gaussian measure. Def 12: "NS_δ(K) := 1/2 − 1/2⟨K, T_{1−δ}K⟩", i.e. "Pr_{x,z}[K(x) ≠ K(y)]" with "y := (1 − δ)x + √(2δ − δ²) z".
- **GSA → NS → concentration (PDF)**:
  - Corollary 14: "Let K ⊆ R^n be a Borel set, and let δ ≥ 0. Then NS_δ(K) ≤ √π √δ · Γ(K)."
  - Then "Σ_{|S|≥1/δ} K̂(S)² ≤ 5·√δ·Γ(K)" (Hermite coefficients).
  - Thm 15: "Let K ⊆ R^n be a Borel set. Then the ±1 indicator function of K has Hermite concentration bound α(ǫ, n) = O(Γ(K)²/ǫ²)."
  - Learning result: time n^{O(S²)} for surface area S; precisely "n^{O(S²/ǫ⁴)}".
- **Nazarov (PDF, Thm 20, "communicated to us by Nazarov [Naz03a]")**: "Let K ⊆ R^n be an intersection of up to k halfspaces. Then Γ(K) ≤ √(2 ln k) + 2 ≤ O(√log k)." The text extraction reads "√ 2 ln k+2". The proof sums two parts, "at most k·ϕ(√(2 ln k)) ≤ 1" and "at most √(2 ln k) + 1", which confirms the reading √(2 ln k) + 2.
- **Caveat (verbatim)**: Fact 4 reads "Every halfspace in R^n has Gaussian surface area at most ϕ(0) = √2/π ≈ 0.8". By the paper's own ϕ(x) = (1/√(2π))e^{−x²/2}, ϕ(0) = 1/√(2π) ≈ 0.399, consistent with Kane's d/√(2π). The "≈ 0.8" value is internally inconsistent; do not reuse it.
- **Status**: VERIFIED.

### B18. Random deep nets: linear-region boundaries, simplicity bias, noise sensitivity
- **(a) Hanin & Rolnick, "Complexity of Linear Regions in Deep Networks"**. ICML 2019 (arXiv comment "ICML 2019"). arXiv:1901.09021v2, PDF fetched.
  - Thm 2 (informal): "E[vol_{n_in−1}(B_N∩K)/vol_{n_in}(K)] ≈ T·#{neurons}, where T is the number of breakpoints in the non-linearity of N (for ReLU nets, T = 1)". Also "E[distance(x, B_N)] ≥ C(#{neurons})^{−1}".
  - Thm 1 (informal, 1-D): "E[#{regions in I}] ≈ |I|·T·#{neurons}".
  - Formal Corollary 4, for weights "independent [...] drawn from a fixed probability measure µ on R that is symmetric around 0 and then rescaled to have Var[weights] = 2/fan-in": "E[vol_{n_in−k}(B_{N,k}∩K)]/vol_{n_in}(K) ≤ (#{neurons} choose k)(C_grad·C_bias)^k". Here "C_bias = sup_z sup_{b∈R} ρ_{b_z}(b)" and "C_grad = sup_z sup_x E[‖∇z(x)‖^{2k}]^{1/k} ≤ C e^{C Σ_{j=1}^d 1/n_j}". The matching lower bound is "(#{neurons} choose k) c_bias^k".
  - Notes: these are Lebesgue (not Gaussian) volumes. The bounds need biases with a bounded density, so they are vacuous for zero-bias nets.
  - Status: VERIFIED.
- **(b) De Palma, Kiani, Lloyd, "Random deep neural networks are biased towards simple functions"**. NeurIPS 2019, Advances in Neural Information Processing Systems 32, pp. 1962–1974 (arXiv journal-ref). arXiv:1812.10156v2.
  - Abstract: "We prove that the binary classifiers of bit strings generated by random wide deep neural networks with ReLU activation function are biased towards simple functions. [...] For any given input bit string, the average Hamming distance of the closest input bit string with a different classification is at least sqrt(n / (2π log n)), where n is the length of the string. Moreover, if the bits of the initial string are flipped randomly, the average number of flips required to change the classification grows linearly with n."
  - Status: VERIFIED.
- **(c) Jonasson, Steif, Zetterqvist, "Noise Sensitivity and Stability of Deep Neural Networks for Binary Classification"**. Stochastic Processes and their Applications 165 (2023) 130–167, doi:10.1016/j.spa.2023.08.003. arXiv:2308.09374, PDF fetched.
  - Model (PDF): "ω_t = sign(θ_t ω_{t−1}) where θ_t ∈ R^{n×n}". Output h(ω_T). The columns of θ_t are i.i.d. N(0, Σ), with Σ = I or Σ = ρ + (1−ρ)I. **Sign activation, width n, no bias** ("no bias term is present in our Boolean Network").
  - Def 2.3: "{f_n} is quantitatively noise sensitive (QNS) at level {ϵ_n} if lim_{n→∞} Cov(f_n(ω), f_n(ω^{ϵ_n})) = 0."
  - Thm 3.1: "Let 1/2 ≥ ϵ_n ↓ 0 be such that nϵ_n → ∞ and let lim_{n→∞} K_n/log(1/ϵ_n) = ∞. Then (i) if lim b_n = 0, lim nb_n = ∞ and T_n ∈ [K_n, e^{b_n n}], then for any Boolean functions {h_n}, the resulting {f_{n,T_n}} is annealed QNS at level {ϵ_n} [...] (iii) if T_n ≥ K_n then for any {h_n}, {f_{n,T_n}} is quenched QNS at level {ϵ_n}, (iv) there are Boolean functions {h_n} such that for T_n growing sufficiently fast with n, {f_{n,T_n}} is not annealed noise sensitive. [...] (v) if h_n is noise stable and T_n is bounded, then {f_{n,T_n}} is annealed (and hence quenched) noise stable."
  - Lemma 3.1: "P(sign(θx) ≠ sign(θy)) = (2/π) arctan √(v/(1−v))", for x, y differing in nv bits and θ ∼ N(0, I).
  - Status: VERIFIED. **Citation note**: these are sign-activation networks, not ReLU.
- **(d) Follow-up**: Johan Jonasson, "Annealed correlation and quenched noise sensitivity in biased deep neural networks", arXiv:2610.27983 (20 Oct 2026). Abstract: "Here we add independent Gaussian biases of the natural order and show that quenched noise sensitivity is retained over a broad range of depths [...] At the same time, the annealed covariance remains bounded away from zero and is entirely accounted for by fluctuations in the network-dependent output means." Status: VERIFIED.
- **(e) Related**: Araya, Datres, Kutyniok, "Random Spiking Neural Networks are Stable and Spectrally Simple", arXiv:2511.00904: "wide LIF-SNN classifiers are stable on average, a property explained by the concentration of their Fourier spectrum on low-frequency components". Status: VERIFIED.

---

## C. Randomness-efficient sampling

### C19. Chor–Goldreich, two-point based sampling
- **Authors / title**: Benny Chor, Oded Goldreich, "On the power of two-point based sampling".
- **Venue**: Journal of Complexity 5(1):96–106 (1989), doi:10.1016/0885-064X(89)90015-0 (Crossref).
- **Statement**: no abstract in OpenAlex; ScienceDirect not tried, since publisher pages for the other items were blocked. Restated in Goldreich, "A Sample of Samplers" (revised version, https://www.wisdom.weizmann.ac.il/~oded/PDF/samplers.pdf, fetched), citing [12] = Chor–Goldreich:
  - "The Pairwise-Independent Sampler [12]: On input parameters n, ǫ and δ, set m := 1/(4ǫ²δ) and generate a sequence of m pairwise-independently and uniformly distributed strings in {0,1}^n".
  - "Sample Complexity: 1/(4δǫ²). Randomness Complexity: 2n or 3n−1, depending on which of the constructions is used."
- **Status**: VERIFIED-r (bibliography verified; statement from Goldreich's own survey).

### C20. Gillman, Chernoff bound for expander walks
- **Authors / title**: David Gillman, "A Chernoff Bound for Random Walks on Expander Graphs".
- **Venue**: SIAM J. Comput. 27(4):1203–1220 (1998), doi:10.1137/S0097539794268765. Conference version: FOCS 1993, pp. 680–691, doi:10.1109/SFCS.1993.366819.
- **Abstract (SICOMP, OpenAlex mirror; SIAM returned 403)**: "we show that the fraction of time spent in a set of vertices A converges to the stationary probability $\pi (A)$ with error probability exponentially small in the length of the random walk and the square of the size of the deviation from $\pi (A)$. The exponential bound is in terms of the expansion of G [...] taking the sample average from one trajectory gives a more efficient estimate of $\pi (A)$ than the standard method of generating independent sample points from several trajectories."
- **Restatement**: Vadhan, *Pseudorandomness*, Ch. 4 (https://people.seas.harvard.edu/~salil/pseudorandomness/expanders.pdf), Thm 4.22, credited to Gillman: "Let G be a regular digraph with N vertices and spectral expansion 1 − λ, and let f : [N] → [0,1] be any function. Consider a random walk V_1,...,V_t in G from a uniform start vertex V_1. Then for any ε > 0, Pr[|(1/t)Σ_i f(V_i) − µ(f)| ≥ λ + ε] ≤ 2e^{−Ω(ε²t)}." Vadhan's table: expander walks use "O((1/ε²)·log(1/δ))" samples and "m + O(log(1/δ)·(log(1/ε)/ε²))" random bits. The pairwise-independent sampler uses "O((1/ε²)·(1/δ))" samples and "O(m + log(1/ε) + log(1/δ))" bits.
- **Gillman's exact Thm 2.1 constants**: UNVERIFIED. The commonly cited form, Pr[t_n − nπ(A) ≥ γ] ≤ (1 + γε/(10n))·N_q·e^{−γ²ε/(20n)}, is from memory and not checked.
- **Status**: PARTIAL (bibliography and abstract VERIFIED-m; the qualitative form is VERIFIED-r).

### C21. Zuckerman, randomness-optimal oblivious sampling
- **Authors / title**: David Zuckerman, "Randomness-optimal oblivious sampling".
- **Venue**: Random Structures & Algorithms 11(4):345–367 (1997), doi:10.1002/(SICI)1098-2418(199712)11:4<345::AID-RSA4>3.0.CO;2-Z. Conference version: STOC 1996, pp. 286–295, "Randomness-optimal sampling, extractors, and constructive leader election".
- **Abstract (OpenAlex mirror of the Wiley abstract)**: "for any α>0, it uses (1+α)(m+log γ−1) random bits to output d=poly(ϵ−1, log γ−1, m) sample points z1,…,zd∈{0, 1}m such that for any function f: {0, 1}m→[0, 1], Pr[|(1/d)∑i=1df(zi)−Ef|≤ϵ]≥1−γ."
- **Restatement**: Goldreich's Fig. 1 (C23) lists the poly(ǫ^{−1}, log(1/δ))-sample row with "n + (1 + α)·log₂(1/δ), ∀α > 0" coins (Thm 6.1). That is a later improvement credited there to "[26, Cor. 7.3]", where [26] = Reingold–Vadhan–Wigderson (zig-zag product), not to Zuckerman 1997.
- **Status**: VERIFIED-m.

### C22. Canetti–Even–Goldreich, sampling lower bounds
- **Authors / title**: Ran Canetti, Guy Even, Oded Goldreich, "Lower bounds for sampling algorithms for estimating the average".
- **Venue**: Information Processing Letters 53(1):17–25 (1995), doi:10.1016/0020-0190(94)00171-T.
- **Primary text**: no abstract in OpenAlex, and no free PDF was found by web search. Statements below are from Goldreich's revised survey (fetched), all citing [10] = CEG:
  - Thm 2.1 [10]: "Any sampler has sample complexity bounded below by min{2^{(n−4)/2}, ln(1/O(δ))/(4ǫ²)} provided ǫ ≤ 1/8 and δ ≤ 1/6."
  - Thm 2.2 [10]: "There exists a (non-efficient) sampler with sample complexity 2 ln(4/δ)/ǫ² and randomness complexity n + 2 log₂(2/δ) + log₂ log₂(1/ǫ)."
  - Thm 2.4 [10]: "Any sampler that has sample complexity at most s(n, ǫ, δ), has randomness complexity at least n + log₂(1/δ) − log₂ s(n, ǫ, δ) − log₂(1 − 2ǫ)^{−1} − 2, provided ǫ, δ < 0.5 and s(n, ǫ, δ) ≤ 2^{n−1}."
  - Cor 2.5 [10]: "Any sampler that has sample complexity O(log(1/δ)/ǫ²), has randomness complexity at least n + (1 − o(1))·log₂(1/δ) − 2 log₂(1/ǫ), provided ǫ, δ < 0.4 and log(1/δ)/ǫ² = o(2^n)."
- **Status**: VERIFIED-r.

### C23. Goldreich, "A sample of samplers"
- **Author / title**: Oded Goldreich, "A Sample of Samplers: A Computational Perspective on Sampling".
- **Venue**: ECCC TR97-020 (16 May 1997). Book chapter in *Studies in Complexity and Cryptography*, LNCS 6650, pp. 302–332 (2011), doi:10.1007/978-3-642-22670-0_24.
- **URLs**: https://eccc.weizmann.ac.il/report/1997/020/; the revised PDF https://www.wisdom.weizmann.ac.il/~oded/PDF/samplers.pdf. Text from the 1997 PDF could not be extracted (Type-3 fonts); the revised PDF was used.
- **ECCC abstract**: "we present an algorithm which makes $O(\epsilon^{-2} \cdot \log(1/\delta))$ queries and uses $n+O(\log(1/\epsilon))+O(\log(1/\delta))$ coin tosses, both complexities being very close to the corresponding lower bounds."
- **Fig. 1, "Summary of main results"** (sample complexity | randomness complexity | pointer):

  | Row | Samples | Coins | Pointer |
  |---|---|---|---|
  | lower bound | Ω(log(1/δ)/ǫ²) | | Thm 2.1 |
  | lower bound for O(log(1/δ)/ǫ²) | | n + (1 − o(1))·log₂(1/δ) − 2 log₂(1/ǫ) | Cor 2.5 |
  | upper bound | O(log(1/δ)/ǫ²) | n + log₂(1/δ) | Thm 2.3 |
  | algorithm | O(log(1/δ)/ǫ²) | n + O(log(1/δ)) + log₂(1/ǫ) | Thm 5.1 |
  | algorithm | poly(ǫ^{−1}, log(1/δ)) | n + (1 + α)·log₂(1/δ), ∀α > 0 | Thm 6.1 |

- **Fig. 2, samplers making Θ(log(1/δ)/ǫ²) queries** (coins):
  - lower bound (even Boolean): "n + log₂(1/δ) − 2 log₂(1/ǫ) − log₂ log₂(1/δ) − O(1)"
  - upper bound: "n + log₂(1/δ) − log₂ log₂(1/δ)"
  - efficient samplers: "n + (4 + α) log₂(1/δ) + log₂(1/ǫ), for any α > 0"
  - efficient Boolean samplers: "n + (4 + α) log₂(1/δ)"
- **Thm 5.1** [7, 16 = Bellare–Goldreich–Goldwasser; Goldreich–Wigderson]: "Sample Complexity: O(log(1/δ)/ǫ²). Randomness Complexity: n + log₂(1/ǫ) + O(log(1/δ))."
- **Status**: VERIFIED.

---

## D. QMC and lattice rules for kinks and piecewise-linear integrands

### D24. Owen, Monte Carlo variance of scrambled net quadrature
- **Author / title**: Art B. Owen, "Monte Carlo Variance of Scrambled Net Quadrature".
- **Venue**: SIAM J. Numer. Anal. 34(5):1884–1910 (1997), doi:10.1137/S0036142994277468.
- **Abstract (OpenAlex mirror; SIAM returned 403)**: "For any integrand in L2, the sampling variance tends to zero faster under scrambled net quadrature than under Monte Carlo sampling, as the number of function evaluations n tends to infinity. Some finite n results bound the variance under scrambled net quadrature by a small constant multiple of the Monte Carlo variance, uniformly over all integrands f. Latin hypercube sampling is a special case of scrambled net quadrature."
- **Exact constants**: these are not in the 1997 abstract. They are stated verbatim in Owen's own follow-up, "Scrambling Sobol' and Niederreiter–Xing Points", J. Complexity 14(4):466–489 (1998), doi:10.1006/jcom.1998.0487 (OpenAlex mirror of the abstract): "randomized (0, m, s)-nets in base b produce unbiased estimates of the integral, have a variance that tends to zero faster than 1/n for any square integrable integrand and have a variance that for finite n is never more than e≐2.718 times as large as the Monte Carlo variance. [...] scrambled (t, m, s)-nets enjoy the same properties as scrambled (0, m, s)-nets, except the sampling variance is guaranteed only to be below b^t[(b+1)/(b−1)]^s times the Monte Carlo variance for a least-favorable integrand and finite n."
- **Note**: the "Var ≤ Γσ²/N" gain-coefficient notation is later literature's framing, not the 1997 abstract's. The (t,m,s) constant b^t((b+1)/(b−1))^s is from the 1998 paper. Owen's AoS 1997 paper reportedly restates e and 1 + e (for n = λb^m), but I could not fetch it (Project Euclid blocked); unverified.
- **Status**: VERIFIED-m.

### D25. Owen, scrambled net variance for smooth functions
- **Author / title**: Art B. Owen, "Scrambled net variance for integrals of smooth functions".
- **Venue**: Annals of Statistics 25(4):1541–1562 (1997), doi:10.1214/aos/1031594731.
- **Abstract (OpenAlex mirror; Project Euclid blocked)**: "randomized $(t, m, s)$-nets, has the property that the integral estimates are unbiased and that the variance is $o(1/n)$, for any square integrable integrand. [...] This paper shows that for smooth integrands over s dimensions, the variance is of order $n^{-3}(\log n)^{s-1}$, compared to $n^{-1}$ for ordinary Monte Carlo. Thus the integration errors are of order $n^{-3/2}(\log n)^{(s-1)/2} in probability. This compares favorably with the rate $n^{-1}(\log n)^{s-1}$ for unrandomized $(t, m, s)$-nets."
- **Status**: VERIFIED-m. The exact smoothness hypothesis (Lipschitz mixed partials) is not in the abstract and was not verified.

### D26. He–Wang, RQMC for discontinuous functions
- **Authors / title**: Zhijian He, Xiaoqun Wang, "On the Convergence Rate of Randomized Quasi–Monte Carlo for Discontinuous Functions".
- **Venue**: SIAM J. Numer. Anal. 53(5):2488–2503 (2015), doi:10.1137/15M1007963.
- **Abstract (OpenAlex mirror; SIAM returned 403)**: "It was previously known that the root mean square error (RMSE) of RQMC is only $o(n^{-1/2})$ for discontinuous functions. For certain discontinuous functions in $d$ dimensions, we prove that the RMSE of RQMC is $O(n^{-1/2-1/(4d-2)+\epsilon})$ for any $\epsilon>0$ and arbitrary $n$. If some discontinuity boundaries are parallel to some coordinate axes, the rate can be improved to $O(n^{-1/2-1/(4d_u-2)+\epsilon})$, where $d_u$ denotes the so-called irregular dimension [...] Moreover, this paper shows that the RMSE is $O(n^{-1/2-1/(2d)})$ for certain indicator functions."
- **Related**: Zhijian He, "On the Error Rate of Conditional Quasi–Monte Carlo for Discontinuous Functions", SINUM 57(2):854–874 (2019), doi:10.1137/18M118270X (Crossref only).
- **Status**: VERIFIED-m. The "certain discontinuous functions" class (indicator times smooth, with a boundary condition) was not verified in detail.

### D27. Griewank–Kuo–Leövey–Sloan, preintegration
- **Authors / title**: Andreas Griewank, Frances Y. Kuo, Hernan Leövey, Ian H. Sloan, "High dimensional integration of kinks and jumps — Smoothing by preintegration".
- **Venue**: J. Comput. Appl. Math. 344 (2018) 259–274, doi:10.1016/j.cam.2018.04.009. arXiv:1712.00920.
- **Abstract**: "We show how simple kinks and jumps of otherwise smooth integrands over $\mathbb{R}^d$ can be dealt with by a preliminary integration with respect to a single well chosen variable. It is assumed that this preintegration, or conditional sampling, can be carried out with negligible error [...] It is proven that under appropriate conditions the preintegrated function of $d-1$ variables belongs to appropriate mixed Sobolev spaces, so potentially allowing high efficiency of Quasi Monte Carlo and Sparse Grid Methods applied to the preintegrated problem."
- **Status**: VERIFIED.

### D28. Gilbert–Kuo–Sloan, preintegration without monotonicity
- **Authors / title**: Alexander D. Gilbert, Frances Y. Kuo, Ian H. Sloan, "Preintegration is not smoothing when monotonicity fails".
- **Venue**: arXiv:2112.11621 (22 Dec 2021). Published as a **book chapter** in *Advances in Modeling and Simulation* (Springer, 2022), pp. 169–191, doi:10.1007/978-3-031-10193-9_9. Not a journal article.
- **Abstract**: "Griebel, Kuo, Sloan [Math. Comp. 82 (2013), 383--400] and Griewank, Kuo, Leövey, Sloan [...] showed that the resulting $(d-1)$-dimensional integrand is indeed smooth under appropriate conditions, including a key assumption -- the integrand of the smooth function underlying the kink or jump is strictly monotone with respect to the chosen special variable when all other variables are held fixed. [...] We show here that the answer is essentially yes, in the sense that without this property the resulting $(d-1)$-dimensional integrand is generally not smooth, having square-root or other singularities."
- **Related**: Gilbert–Kuo–Sloan, "Analysis of Preintegration Followed by Quasi–Monte Carlo Integration for Distribution Functions and Densities", SINUM 61(1):135–166 (2023), doi:10.1137/21M146658X (Crossref only).
- **Status**: VERIFIED.

### D29. Dick–Kuo–Sloan, Acta Numerica
- **Authors / title**: Josef Dick, Frances Y. Kuo, Ian H. Sloan, "High-dimensional integration: The quasi-Monte Carlo way".
- **Venue**: Acta Numerica 22 (2013) 133–288, doi:10.1017/S0962492913000044.
- **Abstract (OpenAlex mirror)**: "This paper is a contemporary review of QMC ('quasi-Monte Carlo') methods, that is, equal-weight rules for the approximate evaluation of high-dimensional integrals over the unit cube [0,1]^s [...] Important tools for the analysis are weighted function spaces, reproducing kernel Hilbert spaces, and discrepancy".
- **Worst-case/average-case identity**: not checked in DKS (full text not fetched). Verified instead in Novak–Woźniakowski, *Tractability of Multivariate Problems* Vol. II (author preprint, https://web.maths.unsw.edu.au/~josefdick/preprints/Novak_Wozniakowski_book_2.pdf), Corollary 13.1: "For an arbitrary linear algorithm A_{n,d} we have e^avg(A_{n,d}; I_d) = e^wor(A_{n,d}; I_d^res)". Here I_d^res is I_d restricted to the RKHS of the covariance kernel K_{µ_d}. The explicit formula: "e^avg(A_{n,d};I_d) = [‖h_d‖²_{H_{µ_d}} − 2Σ_j a_j h_d(x_j) + Σ_{i,j} a_i a_j K_{µ_d}(x_i,x_j)]^{1/2}".
- **Status**: PARTIAL (bibliography and abstract VERIFIED-m; the identity is VERIFIED-r via Novak–Woźniakowski, not via DKS).

### D30. Woźniakowski, average case complexity of multivariate integration
- **Author / title**: H. Woźniakowski, "Average case complexity of multivariate integration".
- **Venue**: Bull. Amer. Math. Soc. (N.S.) 24(1):185–194 (1991), doi:10.1090/S0273-0979-1991-15985-9.
- **Access**: ams.org returned 403 for the page and the PDF; the Columbia Academic Commons copy is behind Anubis.
- **Abstract (OpenAlex OCR mirror, verbatim including OCR damage)**: "In this paper we prove that optimal design is closely related to discrepancy theory [...] This relation enables us to show that optimal sample points can be derived from Hammersley points. [...] we conclude that the average case complexity ise(e-l (lne-l f-l)/2 )." My reading of the damaged formula is Θ(ε^{-1}(ln ε^{-1})^{(d−1)/2}). Novak–Woźniakowski Vol. II §15.2 confirms this: "average case complexity Θ(ε^{−1}(ln ε^{−1})^{(d−1)/2}), where the factors in the Θ notation depend on d, see [346]".
- **Exact identity**: Novak–Woźniakowski Vol. II §9.5.2, "Discrepancy and Wiener Sheet Measure" (fetched), "as in [346]". In NW's bibliography, [346] = "H. Woźniakowski, Average case complexity of multivariate integration, Bull. Amer. Math. Soc. 24, 185–191, 1991"; NW give pages 185–191, Crossref 185–194. With the Wiener sheet covariance Π_k min(x_k, y_k) and Q_{n,d}(f) = Σ a_j f(t_j):
  - "e^avg(Q_{n,d})² = 3^{−d} − 2Σ_j a_j Π_k (t_{j,k} − t_{j,k}²/2) + Σ_{i,j} a_i a_j Π_k min(t_{i,k}, t_{j,k})"
  - "Let x_j = 1 − t_j. [...] the last formula is the square of the L2 discrepancy for the points x_j [...] Hence, as in [346], we have e^avg(Q_{n,d}) = disc₂({1 − t_j}, {a_j})."
  - Corollary 9.3: "The (weighted) L2 discrepancy anchored at 0 corresponds to multivariate integration in the average case setting for the space of continuous functions equipped with the (weighted) Wiener sheet measure with the change of the sample points from t_j to 1 − t_j".
- **Status**: VERIFIED-r. The original BAMS theorem wording was not seen.

### D31. Calderbank–Cameron–Kantor–Seidel, Z4-Kerdock codes
- **Authors / title**: A. R. Calderbank, P. J. Cameron, W. M. Kantor, J. J. Seidel, "Z4-Kerdock Codes, Orthogonal Spreads, and Extremal Euclidean Line-Sets".
- **Venue**: Proc. London Math. Soc. (3) 75(2):436–480 (1997), doi:10.1112/S0024611597000403.
- **Abstract (OpenAlex mirror; superscripts lost, so "2m + 1" means R^{2^{m+1}} and "\CC 2 m" means C^{2^m})**: "When m is odd, spreads in an orthogonal vector space of type Ω+(2m + 2,2) are related to binary Kerdock codes and extremal line-sets in 2m + 1 with prescribed angles. Spreads in a 2m-dimensional binary symplectic vector space are related to Kerdock codes over Z4 and extremal line-sets in \CC 2 m with prescribed angles."
- **MUB and spherical-design-strength claim**: UNVERIFIED. It is not in the abstract, and Wiley/Cambridge/ResearchGate full text was not fetched. Primary sources that state related facts:
  - Klappenecker–Rötteler, arXiv:quant-ph/0502031 (ISIT 2005): "maximal sets of MUBs [...] are the same objects as the complex projective 2-designs with angle set {0,1/d}".
  - Can, Rengaswamy, Calderbank, Pfister, arXiv:1904.07842: Kerdock-code stabilizer states form "$N+1$ mutually unbiased bases" for N = 2^m, and the ensemble is "a unitary $2$-design".
  - Cohn, de Laat, Leijenhorst, arXiv:2403.16874: "mutually unbiased basis arrangements constructed using Kerdock codes [...] ($2^{4k} + 2^{2k+1}$ points in $2^{2k}$ dimensions for $2 \le k \le 5$)" are optimal spherical codes.
  - Abdukhalikov, Bannai, Suda, arXiv:0802.1425: Kerdock codes are linked to "maximal real mutually unbiased bases".
- **Status**: PARTIAL.

### D32. Delsarte–Goethals–Seidel, spherical codes and designs
- **Authors / title**: P. Delsarte, J. M. Goethals, J. J. Seidel, "Spherical codes and designs".
- **Venue**: Geometriae Dedicata 6(3):363–388 (1977), doi:10.1007/BF03187604. Springer is behind a JS wall; no free copy found.
- **Restatement**: Bannai & Bannai, "A survey on spherical designs and algebraic combinatorics on spheres", European J. Combin. 30 (2009) 1392–1425 (PDF fetched from https://www.math.unipd.it/~alvise/PHD_2024/LEZIONI/SPHERE/PDF/BANNAI%20Survey.pdf). Thm 2.12 ([88] = DGS), for X ⊂ S^{n−1} ⊂ R^n:
  - "(1) Let X be a spherical 2e-design, then |X| ≥ C(n+e−1, e) + C(n+e−2, e−1) holds."
  - "(2) Let X be a spherical (2e+1)-design, then |X| ≥ 2·C(n+e−1, e) holds."
  - Def 2.13: equality means "tight".
- **Status**: VERIFIED-r.

---

## E. Deterministic approximate counting

### E33. Gopalan–Klivans–Meka–Štefankovič–Vempala–Vigoda, #Knapsack
- **Authors / title**: Parikshit Gopalan, Adam Klivans, Raghu Meka, Daniel Štefankovič, Santosh Vempala, Eric Vigoda, "An FPTAS for #Knapsack and Related Counting Problems".
- **Venue**: FOCS 2011, pp. 817–826, doi:10.1109/FOCS.2011.32.
- **Abstract (OpenAlex mirror of the IEEE abstract)**: "We give the first deterministic, fully polynomial-time approximation scheme (FPTAS) for estimating the number of solutions to any knapsack constraint (our estimate has relative error $1 \pm \epsilon$). Our algorithm is based on dynamic programming. [...] In addition, we present a new method for deterministic approximate counting using {\em read-once branching programs.} Our approach yields an FPTAS for several other counting problems, including counting solutions for the multidimensional knapsack problem with a constant number of constraints, the general integer knapsack problem, and the contingency tables problem with a constant number of rows."
- **Merged preprints**:
  - GKM, arXiv:1008.3187 (abstract fetched): "On an instance of length n with total weight W and accuracy parameter eps, our algorithm produces a (1 + eps)-multiplicative approximation in time poly(n,log W,1/eps)."
  - Štefankovič–Vempala–Vigoda, "A Deterministic Polynomial-Time Approximation Scheme for Counting Knapsack Solutions", SIAM J. Comput. 41(2):356–366 (2012), doi:10.1137/11083976X (Crossref).
- **Status**: VERIFIED.

### E34. De–Diakonikolas–Servedio and De–Servedio, deterministic counting for PTFs
- **(a) De, Diakonikolas, Servedio, "Deterministic Approximate Counting for Degree-2 Polynomial Threshold Functions"**, arXiv:1311.7105. **No conference or journal venue found**: not in Crossref, and Servedio's papers page lists only the juntas paper.
  - Abstract: "approximates \[ \Pr_{x \sim \{-1,1\}^n}[p(x) \geq 0] \] to within an additive $\pm \eps$ in time $\poly(n,2^{\poly(1/\eps)})$. [...] The algorithm also runs in $\poly(n,1/\eps)$ time to approximate $\Pr_{x \sim N(0,1)^n}[p(x) \geq 0]$ to within an additive $\pm \eps$, for any degree-2 polynomial $p$."
  - Status: VERIFIED (arXiv); venue UNVERIFIED / not found.
- **(b) De, Diakonikolas, Servedio, "Deterministic Approximate Counting for Juntas of Degree-2 Polynomial Threshold Functions"**, CCC 2014, pp. 229–240, doi:10.1109/CCC.2014.31, arXiv:1311.7115.
  - Abstract: "For any constant $\eps > 0$ and $k \geq 1$ the running time of our algorithm is a fixed polynomial in $n$."
  - Status: VERIFIED.
- **(c) De, Servedio, "Efficient deterministic approximate counting for low-degree polynomial threshold functions"**, STOC 2014, pp. 832–841, doi:10.1145/2591796.2591800, arXiv:1311.7178.
  - Abstract: "our algorithm approximates $\Pr_{x \sim \{-1,1\}^n}[p(x) \geq 0]$ to within an additive $\pm ε$ in time $O_{d,ε}(1)\cdot \mathop{poly}(n^d)$. [...] The fastest previous algorithm for this problem (due to Kane), based on constructions of unconditional pseudorandom generators for degree-$d$ PTFs, runs in time $n^{O_{d,c}(1) \cdot ε^{-c}}$ for all $c > 0$."
  - Status: VERIFIED.
- **Related**: CDS (A10) gives deterministic counting for arbitrary functions of k LTFs over {0,1}^n "in time $\poly(n) \cdot 2^{\poly(k,1/\eps)}$" and for intersections in "$\poly(n) \cdot 2^{\poly(\log k, 1/\eps)}$" (ECCC abstract). OST polytopes (A9): "deterministic algorithm that runs in time n^{polylog(m)} and additively approximates the number of solutions to any n-variable {0,1}-integer program with m constraints" (PDF).

### E35. Elekes 1986 and Bárány–Füredi 1987, deterministic volume lower bounds
- **Elekes**: G. Elekes, "A geometric inequality and the complexity of computing volume", Discrete Comput. Geom. 1(4):289–292 (1986), doi:10.1007/BF02187701.
- **Bárány–Füredi**: I. Bárány, Z. Füredi, "Computing the volume is difficult", Discrete Comput. Geom. 2(4):319–326 (1987), doi:10.1007/BF02187886. EuDML record https://eudml.org/doc/131025 (fetched) confirms DCG 2:319–326 (1987), keywords "volume computation; time complexity; width of convex sets". The STOC 1986 conference version, pp. 442–447, comes from Dadush–Vempala's reference [13] and was not checked in Crossref.
- **Access**: the Springer article and PDF need a JS/cookie login wall; curl with a cookie jar got HTML; there is no OpenAlex abstract. **The exact statements are UNVERIFIED.**
- **Restatement**: Dadush–Vempala, arXiv:1201.5972 (PDF fetched), Thm 1.4, attributed to "[17] Furedi Z, Barany I (1988) Approximation of the sphere by polytopes having few vertices. Proc. AMS 102", **not** the 1987 DCG paper: "For any 0 ≤ ǫ ≤ 1, any deterministic algorithm that estimates the volume of any input convex body to within a (1 + ǫ)^n given only a membership oracle to the body, must make at least Ω(1/ǫ)^n queries to the membership oracle."
- **From memory, UNVERIFIED, do not cite**:
  - Elekes: the convex hull of N points in the unit n-ball has volume ≤ (N/2^n)·vol(ball). Hence a polynomial-time deterministic oracle algorithm cannot approximate volume within a factor of about 2^n/poly(n).
  - Bárány–Füredi: the ratio of upper to lower estimates must be at least about (c·n/log n)^n. I am unsure of the exact exponent and form.
- **Status**: PARTIAL (bibliography VERIFIED; statements UNVERIFIED).

---

## Citation corrections found
1. **A6**: the STOC 2020 OST paper claims seed d^{O(log d)}·log n. The poly(d/ε)·log n bound is in arXiv:2103.07809 (2021–22), which lists **Daniel Kane as a fourth author**. Kelley–Meka (CCC 2022) independently got d^{O(1)} log(n/ε) log(1/ε)/ε².
2. **A5**: the exact title is "...Polynomial Threshold Functions of **Gaussian** with Subpolynomial Seed Length" (CCC 2014).
3. **A12**: no journal version. The ToC 18 (2022) Servedio–Tan paper is a different (AC0) paper.
4. **A10**: not on arXiv (ECCC TR18-100 only).
5. **B16**: the arXiv title ends "...of Degree-d Polynomials". The CCC 2010 / Comput. Complexity 2011 titles say "Polynomial Threshold Functions".
6. **B17**: KOS Fact 4 internally misstates the halfspace GSA as "√2/π ≈ 0.8". By their own ϕ it is 1/√(2π) ≈ 0.399.
7. **B18(c)**: JSZ is Stoch. Proc. Appl. 165 (2023). It studies **sign-activation, bias-free** nets, not ReLU. The bias-added follow-up is Jonasson, arXiv:2610.27983 (2026).
8. **D24**: the 1997 SINUM abstract gives no explicit constant. e ≈ 2.718 for (0,m,s)-nets and b^t((b+1)/(b−1))^s for (t,m,s)-nets are verbatim in Owen, J. Complexity 1998.
9. **D28**: GKS 2022 is a Springer book chapter (Advances in Modeling and Simulation, pp. 169–191), not a journal paper.
10. **E34**: the single degree-2 PTF DDS paper (arXiv:1311.7105) has no venue I could find. The juntas paper is CCC 2014, and De–Servedio is STOC 2014 (pp. 832–841).
11. **E35**: Bárány–Füredi also has a STOC 1986 version. The modern restatement (Dadush–Vempala) attributes the Ω(1/ε)^n query bound to Bárány–Füredi, PAMS 1988.
