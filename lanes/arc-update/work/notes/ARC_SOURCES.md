Model: Sonnet 5.5 (claude-sonnet-5-5), the model named in this worker's system prompt; no substitution.

# ARC primary sources: verbatim quotes with locators (re-fetched 2026-11-02)

Compiled 2026-11-02 UTC. Fetch window 04:41Z to 05:05Z. Facts only, except lines explicitly labelled "Derived" or "worker's own" (arithmetic in Section 4.3) and the last section, which is the one paragraph of interpretation and is marked DERIVED.
Old fact sheet used only as a pointer: /home/agent/workspaces/mats/work/cut-rank-ext/notes/arc_estimators.md (compiled 2026-10-31).
Scratch (untrusted downloads, never executed, will vanish on reboot): /tmp/arcsrc_1793594504/ ; scripts: /tmp/arcsrc_scripts/ (python run with -I).

Status tags: VERIFIED = I saw the exact text today. CHANGED = live source differs from the old sheet (both given). UNVERIFIED = could not open or confirm (reason given). NOT FOUND = searched, nothing there (search terms given). NEW = not in the old sheet.

Method. PDF: curl to /tmp, text via pypdf (venv /home/agent/.venvs/aggext, python -I), key pages rendered to PNG with ghostscript and read by eye. HTML: curl plus html.parser. Discourse: /raw/ endpoints and .json. GitHub: api.github.com and raw.githubusercontent.com. LessWrong/AF: GraphQL. Quotes marked "[math; image-checked]" were checked on a rendered page image because text extraction flattens fractions. Every other blockquote was machine-checked as a substring of the downloaded source text (case, whitespace, punctuation and markdown ignored); see the footer.

## 0. Status table

| Item | Source | Status |
|---|---|---|
| 1a-1i | arXiv:2605.05179 (latest = v2, 14 May 2026; no v3) | all VERIFIED, no change vs old sheet |
| 2 | Hilton blog, 7 May 2026, footnote 7 | VERIFIED |
| 3 | Competing with sampling, 18 Nov 2025 | VERIFIED (page last modified 2025-12-18 per sitemap; live text matches old sheet) |
| 4 setup and sentences | ARC post, AIcrowd forum 18026/18197/18251, Rules, starter kit | VERIFIED |
| 4 results/winners | AIcrowd forum, Rules, leaderboard, ARC blog | NOT FOUND (no official Phase 1 or Phase 2 results as of 2026-11-02 ~05:00Z); Rules say winners "tentatively on or about November 15, 2026" |
| 5 | Random products post, 15 May 2026 | VERIFIED |
| 6 | Returning to ARC, 4 Aug 2026 | VERIFIED (the "bold conjecture" is footnote 10; no sentence on depth or random MLPs) |
| 7 | Mike's-Eye View, 9 Jun 2026 | VERIFIED |
| 8 | GitHub mlp_cumulant_propagation | VERIFIED unchanged (HEAD 93d091a, 2026-08-04; TODO.md byte-identical to local clone) |
| 9 | newer ARC material | no ARC blog post, paper or LW/AF post on depth or contest results after 9 Jun 2026; NEW ARC-staff statements outside the blog: Hilton's comment of 23 Jun (Section 4.2), ARC's guidance post of 6 Jul and the townhall summary (Section 4.3); see Section 9 |

---------------------------------------------------------------------------------------------------

## 1. Wu, Lecomte, Winer, Robinson, Hilton, Christiano, "Estimating the expected output of wide random MLPs more efficiently than sampling", arXiv:2605.05179

URLs: https://arxiv.org/abs/2605.05179 ; https://arxiv.org/pdf/2605.05179 (served as 2605.05179v2.pdf, 68 pages, last-modified header Mon 18 May 2026). Fetched 2026-11-02 04:41Z (abs page and PDF).
Versions (arXiv abs page, "Submission history"): v1 Wed, 6 May 2026 17:46:12 UTC (178 KB); v2 Thu, 14 May 2026 22:12:20 UTC (179 KB). https://arxiv.org/abs/2605.05179v3 and https://arxiv.org/pdf/2605.05179v3 return HTTP 404 (2026-11-02 ~04:42Z), so v2 is the latest. Journal ref: None. Comments field: "68 pages. Code is available at this https URL" and the link points to github.com/alignment-research-center/mlp_cumulant_propagation. The PDF body (Sec. 4.1 p.5 and S.4.3 p.48) instead links github.com/alignment-research-center/mlp_kprop, which returns HTTP 404 today (curl and api.github.com, 2026-11-02 ~04:49Z), unchanged from the old sheet.
All page numbers below are PDF pages of v2.

### 1a. Abstract, main claim. VERIFIED
Locator: arXiv abs page "Abstract" (text taken from the page HTML, 04:41Z); identical on PDF p.1.
> We show both theoretically and empirically that for sufficiently wide networks, our estimator achieves a target mean squared error using substantially fewer FLOPs than Monte Carlo sampling.
Full abstract, same locator:
> By far the most common way to estimate an expected loss in machine learning is to draw samples, compute the loss on each one, and take the empirical average. However, sampling is not necessarily optimal. Given an MLP at initialization, we show how to estimate its expected output over Gaussian inputs without running samples through the network at all. Instead, we produce approximate representations of the distributions of activations at each layer, leveraging tools such as cumulants and Hermite expansions. We show both theoretically and empirically that for sufficiently wide networks, our estimator achieves a target mean squared error using substantially fewer FLOPs than Monte Carlo sampling. We find moreover that our methods perform particularly well at estimating the probabilities of rare events, and additionally demonstrate how they can be used for model training. Together, these findings suggest a path to producing models with a greatly reduced probability of catastrophic tail risks.

### 1b. Error criterion and Monte Carlo baseline. VERIFIED
Locator: Sec. 1 p.2; Sec. 2.2 p.3; Sec. 2.3 p.4; Sec. 6.1 p.7.
Sec. 1, p.2 (quenched versus annealed; weights averaged only after comparing with ground truth):
> Importantly, our algorithms take as input the weights of a particular network and estimate the expected output over random inputs, i.e., a quenched average, in the language of statistical physics.
> After comparing our estimates with ground truth, we average over the choice of weights, which are drawn independently from
(continues "N(0, c/n) for some constant c, where n is the width", math; image-checked on p.2.)
Sec. 2.2, p.3 [math; image-checked]: "Given weights θ ∈ R^{(L+1)×n×n} drawn independently from N(0, 2/n) (following He et al. [2015]), estimate E_{X∼N(0,I_n)}[M_θ(X)]," then:
> More precisely, an estimation procedure should take as input
(continues "θ and ε > 0, and produce an estimate with mean squared error O(ε²) over the choice of θ for each output neuron." [math; image-checked p.3])
Sec. 2.3, p.4, Monte Carlo cost baseline [math; image-checked]: "This procedure samples X^(1),…,X^(N) i.i.d.∼ N(0,I_n) for N = ⌈1/ε²⌉ and computes the estimate (1/N)Σ_{r=1}^N M_θ(X^(r)). This achieves the required mean squared error of Θ(ε²), since a single forward pass has variance Θ(1) under our choice of initialization, and runs in time Θ(n²/ε²) (recall that we treat the number of hidden layers L as a constant in our asymptotics)."
Footnote 5, p.2 (applies to the Θ(n²/ε²) claim):
> We assume the use of naive rather than Strassen-type matrix multiplication in all algorithms.
Sec. 6.1, p.7, "variance-normalized MSE":
> For each configuration, we calculate mean squared error (MSE) over all output neurons and over 5 different random seeds.
> To calculate MSE, we estimate ground truth using Monte Carlo sampling with
(continues "2^34 ≈ 2×10^10 samples", math)
> which greatly exceeds any of our algorithms' computational budgets. We use these same samples to estimate the variance of a single forward pass, and divide MSE by this variance to obtain variance-normalized MSE. This choice of units means that Monte Carlo sampling with N samples has a variance-normalized MSE of exactly
(continues "1/N", math; the extracted text reads "1N".)

### 1c. Theorems 5.1 and 5.2. VERIFIED
Locator: Sec. 5, p.6 [math; image-checked on the rendered page]. Fetched 2026-11-02 04:41Z.
> [math; image-checked] Theorem 5.1. Fix an integer L ≥ 0 and polynomial activation functions φ_1,…,φ_L. Given weights θ ∈ R^{(L+1)×n×n} drawn independently from N(0, 2/n) for an integer n ≥ 1, write M_θ: R^n → R^n for the MLP with L hidden layers, width n, activation functions φ_1,…,φ_L and weights θ. Then there is an estimation procedure G(θ, ε) such that for every noticeable function 0 < ε(n) ≤ 1 and every output index i, as n → ∞, E_θ[((G(θ, ε(n)))_i − E_{X∼N(0,I_n)}[M_θ(X)]_i)²] = O(ε(n)²) and G(θ, ε) runs in time O(n²/ε²).
> [math; image-checked] Theorem 5.2. In Theorem 5.1, if we also require that ε(n)² = O(1/n²), then G(θ, ε) can be made to run in time O(n/ε²).
Footnote 8 (p.6) defines noticeable: "for some k ≥ 0, ε(n) ≥ 1/n^k for all sufficiently large n [Goldreich, 2005, Chapter 1.2]". Footnote 4 (p.2): "Our theoretical results assume polynomial activation functions and conditions on the growth rate of ε(n)." The intro (p.2) states the same bounds [math; image-checked]: "our best-performing algorithms achieve a mean squared error of O(ε²) in time O(n/ε²). By comparison, Monte Carlo sampling achieves a mean squared error of Θ(ε²) in time Θ(n²/ε²), a factor of n slower."
Supplement S.4 intro, p.46 (math typeset by worker from extracted text, not image-checked): "Our basic cumulant propagation estimator takes O(n^{K+1}) time and incurs O(n^{−K}) MSE for all integral K ≥ 0, thus matching sampling for non-integral K as well (by taking the floor). The factorized version of this algorithm takes only O(n^K) time to compute the same estimate (and thus obtain the same MSE)."

### 1d. The (L/n)^K conjecture and the runtime bounds. VERIFIED
Locator: Sec. 5, p.6 [math; image-checked]; App. D p.19; S.4.3 p.48.
> [math; image-checked] These results treat the number of hidden layers L as a constant, and choose the maximum cumulant order K based on the error tolerance ε. Expressed in terms of these parameters, we conjecture that our algorithms have mean squared error at most c_K (L/n)^K, although the dependence on L is difficult to analyze precisely. The runtime of the basic version of our algorithm is at most c'_K L n^{K+1}, and the runtime of the factorized version is at most c''_K L² n^K whenever K ≥ 3. Here, c_K, c'_K and c''_K are constants that depend only on K.
Footnote 7 (p.6) [math; image-checked]: "The new constant factors scale quadratically rather than linearly with depth, as can be seen for K ≤ 4 in Appendix J."
App. D, p.19:
> We conjecture this depth scaling based on a heuristic analysis of the error, but we can also test it empirically.
S.4.3, p.48:
> If we track the dependence on L explicitly, the time complexity of basic cumulant propagation through the entire MLP scales linearly with L, while that of the factored version scales quadratically.

### 1e. "Matches" sampling; factorized outperforms by a factor n. VERIFIED
Locator: Sec. 5, p.6 (directly under Theorem 5.2); Sec. 1, p.2.
> Theorem 5.1 is obtained from the basic version of our sample-free estimation procedure, and Theorem 5.2 from the factorized version. Thus our results show that, up to constant factors, the basic version of our algorithm matches the performance of Monte Carlo sampling in terms of mean squared error for a given computational budget, while the factorized version outperforms Monte Carlo sampling by a factor equal to the network width n, providing ε is not too large.
Footnote 9 (p.6) [math; image-checked]: "A mean squared error of ε(n)² = O(1/n²) is achieved with K ≥ 2, which costs as much as sampling with Ω(n) samples."
Sec. 1, p.2:
> This means that for any given depth, our algorithms are guaranteed to outperform Monte Carlo sampling at sufficiently large width, although the dependence of our algorithms on depth is worse.

### 1f. Sec. 6.2 results at width 256, by depth. VERIFIED
Locator: Sec. 6.2, p.7 (Figure 2); wider grid in App. C Fig. 7 p.18.
> Our results at width 256 with 2, 4 and 8 hidden layers are shown in Figure 2, and our results at additional widths and depths are given in Appendix C.
> The factorized and factorized augmented versions of our algorithm outperform Monte Carlo sampling by a factor of around 1,000 for 2 hidden layers, and around 10–100 for 4 hidden layers. They start to underperform sampling for 8 hidden layers once the maximum cumulant order K reaches 4, although by our theoretical results, they would outperform sampling once again if we were to increase the width further.
Setup, Sec. 6.1 p.7: "We vary the width n from 4 to 256 and the number of hidden layers L from 2 to 12 (using the same network for each choice of L, but stopping after different numbers of layers)." (p.6 into p.7, text extracted.)
Fig. 1 (p.2) is width 256 with 4 hidden layers; intro p.2: "We are able to outperform Monte Carlo sampling at computational budgets spanning 7 orders of magnitude, in some cases by a factor of over 100."

### 1g. Appendix C (narrow nets) and Appendix D (depth scaling). VERIFIED
Locator: App. C p.18; App. D p.19 (Figure 8, width 256).
App. C "Additional widths and depths":
> Our algorithms perform poorly at low width, especially when the number of hidden layers L is large, and can even get worse with the maximum cumulant order K in this setting. However, for any fixed L and K, our algorithms match or exceed the performance of sampling as the width grows.
> Note also that at low depth, factorized algorithms use fewer FLOPs than their unfactorized counterparts, but at high enough depth (for fixed width), they use more FLOPs.
App. D "Scaling with depth":
> As conjectured, the mean squared error roughly follows a curve proportional to
(continues "L^K when L is large", math)
> This depth scaling is worse than Monte Carlo sampling, whose error does not increase with depth. We believe that a sample-free algorithm can be developed whose error also does not increase with depth either, but we leave this problem to future work.
(The doubled "also ... either" is in the source.)
Range of the paper's own depth evidence (read from Fig. 8 p.19 and Sec. 6.1 p.7): Fig. 8 is width 256 only, with the depth axis spanning about L = 2 to 12 (ticks 2^1 to 2^3); the paper's grid is L = 2 to 12 and n = 4 to 256 (Sec. 6.1). No experiment in the paper reaches the contest depth of 32.

### 1h. Sec. 7.3 open problems. VERIFIED
Locator: Sec. 7.3, p.10.
> There is enormous scope for further research on mechanistic estimation. Even for random MLPs, we do not know whether it is possible to match the performance of random sampling at large depth (i.e., asymptotically as the number of hidden layers L tends to infinity), or for narrow networks (i.e., asymptotically as the error tolerance ε→0 while the width n is held fixed). We could also ask the same questions for MLPs with weights drawn from non-independent or non-Gaussian distributions.
Related, Sec. 7.1, p.9 (the broad conjecture):
> Following Neyman et al. [2025], we conjecture that the performance of any estimation procedure can be matched (or exceeded) by a mechanistic one, providing we are given the training trajectory or selection process of any parameters involved.

### 1i. Hermite series not expected to converge at fixed width. VERIFIED
Locator: Supplement S.6.2 "Tameness", p.57; also the opening of S.7, p.57.
> We do not, in fact, expect this infinite summation formula to converge at any fixed width n, but instead that a fixed truncation should be an asymptotically good approximation as n → ∞. This is the property of an asymptotic expansion, and in fact we can motivate the diagram summation formula through the theory of Edgeworth expansions, a special form of asymptotic series [Hall, 1992].
S.7 intro, p.57:
> Convergence of these formal expansions is fragile: we do not expect these expansions to converge for a fixed n, but instead truncate to a finite summation such that the error converges to zero as n→∞.
Scope note, S.6 p.56-57: the proofs are for polynomial activations; for ReLU "the Hermite coefficients of ReLU have a singularity at σ² = 0, so much more care is required (see Section S.3.4)".

---------------------------------------------------------------------------------------------------

## 2. Hilton, "Mechanistic estimation for wide random MLPs" (alignment.org, 7 May 2026). VERIFIED

URL: https://www.alignment.org/blog/mechanistic-estimation-for-wide-random-mlps/ . Fetched 2026-11-02 04:43Z (curl; page text). Sitemap lastmod 2026-05-15T17:06:17Z, so the live text may postdate 7 May; the quote below is from the live text. Cross-posts: https://www.alignmentforum.org/posts/fsG4m6sRMpomd7Rk6 and LessWrong.
Footnote 7 (the footnote marker sits on the sentence "We have produced mechanistic estimates for these networks that significantly outperform random sampling (for wide networks),"; section "Significance of results"):
> It remains an open problem to match the performance of random sampling for random MLPs in other regimes, for example, with the depth growing linearly in the width.
Companion footnotes in the same post:
Footnote 2, verbatim LaTeX from the page source (attached to the "a factor of n faster" claim): `This works providing that \(\varepsilon^2\) grows like \(\frac 1{n^k}\) for some \(k\geq 2\).` Plain: eps^2 grows like 1/n^k for some k >= 2.
> The depth scaling of our algorithms is discussed Appendix D of the paper.
(footnote 3; the missing "in" is in the source.)
Body, same post:
> This means that for any given depth, our algorithm is guaranteed to outperform Monte Carlo sampling at large enough width, although the dependence of our algorithms on depth is worse.

---------------------------------------------------------------------------------------------------

## 3. Neyman, Lecomte, Wu, Winer, Hilton, Robinson, "Competing with sampling" (alignment.org, 18 Nov 2025). VERIFIED

URL: https://www.alignment.org/blog/competing-with-sampling/ . Fetched 2026-11-02 04:43Z. Sitemap lastmod 2025-12-18T00:06:48Z (edited after 18 Nov 2025). Section "Our actual MSP statement" is the mainline version; the earlier section "A first attempt at stating the MSP" has no context variable c and the post says it "does not quite make sense".
Intro (purpose list):
> Introduce what we call the matching sampling principle (MSP) as a semi-formalization of the belief underpinning our research agenda, and discuss why we believe this principle.
Section "The matching sampling principle":
> While above I talked about outperforming sampling, in the fully general case we can only hope to match the performance of sampling.
Section "Our actual MSP statement", verbatim (page source is LaTeX; the three requirement lines are the nested bullets under "For all tolerance parameters"):
> Here is ARC's mainline "matching sampling principle" (MSP):
```
For all architectures M (with parameters theta) mapping pairs (c in {0,1}^{n_c}, x in {0,1}^{n_x}) to R, there exists an estimator G_M mapping tuples (theta, pi, c, eps) to R, such that:
 For all parameters theta, there exists a short explanation pi (|pi| <= O(|theta|)), such that:
  For all tolerance parameters eps > 0, G_M(theta, pi, c, eps) satisfies the following three properties:
   - It runs in time \(O \left( \frac{1}{\varepsilon^2} \text{Time}(M _ \theta) \right)\).
   - Its error is competitive with sampling, on average over random c:
     \(\mathbb{E} _ c[(\mathbb{G} _ M(\theta, \pi, c, \varepsilon) - \mathbb{E} _ x[M _ \theta(c, x)])^2] \le \varepsilon^2 \mathbb{E} _ c[\text{Var}_x[M _ \theta(c, x)]]\), where c ~ {0,1}^{n_c} and x ~ {0,1}^{n_x}.
   - It is mechanistic.
```
(The "mainline" sentence and the "Its error is competitive with sampling, on average over random c" line are exact; the LaTeX lines are copied from the page source; the plain-text layout and the n_c, n_x ranges are my transcription of the nested list.)
Transcription of the two formulas: time O((1/eps^2) Time(M_theta)); error E_c[(G_M(theta,pi,c,eps) - E_x[M_theta(c,x)])^2] <= eps^2 E_c[Var_x[M_theta(c,x)]].
Interpretation lines in the post (same section "A first attempt at stating the MSP", "Let's parse these three requirements"): the time bound "is the time that it takes to estimate [E_x M_θ(x)] by running 1/ε² randomly sampled values of x through M_θ", and the error bound's right-hand side "represents the expected squared error via taking the empirical average of 1/ε² samples of M_θ(x)".
Heuristic definition of "mechanistic", section "What makes an algorithm 'mechanistic'?":
> We do not have a formal definition of "mechanistic."
> A simple, though not entirely correct, heuristic for whether an estimation algorithm is deductive, is whether it avoids any random or pseudorandom sampling. This heuristic should work for the purposes of engaging with this post.
Why only matching, section "Why only matching sampling?":
> In general, we expect that there will often be a range of [...]-values for which the best mechanistic estimate is only slightly better than sampling-based estimation.
> Thus, for some parameters [...] and tolerance parameters [...], we only expect to be able to match (or perhaps slightly outperform) sampling, not to strongly outperform sampling.
(The elided symbols are epsilon, theta and epsilon in LaTeX in the source.)
Random MLPs section ("Problem statement"), the same post, for the regime ARC had in mind:
> there are k hidden layers (k is some fixed constant), each of width n;
> The runtime of [...] is competitive with the runtime of the naive sampling-based algorithm, i.e. [...] forward passes.
(The elided symbols are the estimator G and O(1/eps^2) in LaTeX in the source.)
> Can we solve the problem in the case of narrow MLPs (as opposed to the infinite-width limit)?
(For the random-MLP instance the post says this is the MSP "in the particular case where θ is the empty string; c = W" (math transcribed from LaTeX).)

---------------------------------------------------------------------------------------------------

## 4. The ARC White-Box Estimation Challenge (WhestBench)

### 4.1 ARC announcement, 2 June 2026. VERIFIED
URL: https://www.alignment.org/blog/announcing-the-arc-white-box-estimation-challenge/ (Hilton, Christiano, Wu; June 2nd, 2026). Fetched 2026-11-02 04:43Z.
> To begin with, we are fixing the width n=256 and the number of hidden layers L=8, but we expect to change this setup in future rounds.
> The contest setup is actually slightly different in that it omits the final linear layer, but this makes essentially no difference.
> In our recent paper, we produced white-box methods that outperform black-box methods for MLPs with large width, but they break down as the depth grows, and we are very confident that our methods can be significantly improved.
> However, we strongly expect the best possible algorithms for this problem to be "mechanistic" (i.e., to avoid black-box sampling entirely), mirroring our existing results in the large width setting.
> Even though "white-box" is in the name of the challenge, contestants are permitted to use any methods they choose, whether white-box or black-box: as stated above, we ultimately want the best-performing algorithm.
> The warm-up round begins this week, and later rounds will have a total prize pool of at least $100,000.

### 4.2 ARC staff comment on the LessWrong cross-post (Jacob Hilton, 23 June 2026). VERIFIED, NEW (not in old sheet)
URL: https://www.lesswrong.com/posts/Kben8CzS4awCwNw5c/announcing-the-arc-white-box-estimation-challenge?commentId=CqBi8r2YnkXLLseY3 . Comment dated 2026-06-23 17:28Z; read via the LessWrong GraphQL API 2026-11-02 04:51Z.
> For Phase 1, we have increased the depth of the network from 8 to 32 hidden layers. Our existing algorithms scale poorly with depth, and so we expect there to be significant room for improvement. Phase 1 lasts until the end of July, after which Phase 2 begins. For Phase 2, there will be a prize pool of at least $100,000, and we may change the architectural parameters again.
> The best-performing algorithms in the warm-up round appear to be variants on the factorized 3rd cumulant propagation algorithm we introduced in our paper, combined with learned networks that consume the cumulant estimates as features.
> For Phase 1, we expect the increased depth to advantage approaches that go beyond basic cumulant propagation in their mechanistic analysis.
Same thread, Christiano, 2026-06-03 16:25Z (commentId YWCaGNPvBXbvaXzdo): "We think there probably do exist adequate algorithms for analyzing random networks and the reason we haven't found them is because so little research has addressed the question head on."

### 4.3 Round parameters (all VERIFIED; sources per cell)

| Round | MLP (width x hidden layers) | FLOP budget per MLP | Dates | Source |
|---|---|---|---|---|
| Warm-up | 256 x 8 | 6.8 x 10^10 | 28 May to 17 Jun 2026 | forum 18026 table; Rules key dates |
| Phase 1 | 256 x 32 | 2.72 x 10^11 | 18 Jun to 10 Aug 2026 | forum 18026; Rules key dates |
| Phase 2 | 1,024 x 16 | 2^41 (about 2.199 x 10^12) | Rules: 22 Aug to 17 Oct 2026; forum 18251: submissions extended to 21 Oct | forum 18197; Rules; starter kit |

Derived arithmetic, worker's own (not stated by the sources): forward-pass FLOPs 2*n^2*L give budget/forward-pass = 6.48e4 (Phase 1: 2.72e11 / 4,194,304), 6.55e4 (Phase 2: 2^41 / 33,554,432), 6.48e4 (warm-up). So every round allows about 6.5e4 forward passes. The starter kit says this itself for Phase 2 ("roughly 6.5e4 forward passes"). Width-to-depth ratio L/n: warm-up 0.031, Phase 1 0.125, Phase 2 0.0156.

Phase 1 launch post. URL: https://discourse.aicrowd.com/t/18026 ("Phase 1 Launch - deeper models, and increased prizes!"), post #1 by mohanty; topic created 2026-06-17 18:35 UTC, and the /raw/ header shows 2026-06-19 00:29:49 UTC (its last-edit time; Phase 1 opened 2026-06-18 00:00 UTC per the post). Fetched 2026-11-02 04:45Z via /raw/18026.
> The target MLP gets 4× deeper: 256×8 → 256×32
> Even with the larger budget, submissions must stay ~15,000× smaller than the sampling budget used for the reference targets
> Phase 1:  256 width × 32 layers
Prize tables in the same post: Phase 1 = $50,000 (25,000 / 10,000 / 5,000 score-based plus 10,000 algorithmic contribution); Phase 2 = $100,000 (50,000 / 20,000 / 10,000 plus 20,000); total "150,000+ USD".

Phase 2 launch post. URL: https://discourse.aicrowd.com/t/18197 ("Phase 2 of the ARC White-Box Estimation Challenge is live"), post #1 by mohanty, created 2026-08-23 23:49:41 UTC, last edited 23:50:31 UTC (the /raw/ header time). Fetched 2026-11-02 04:44Z via /raw/18197 and /t/18197.json.
Summary table rows (as rendered in the post, "Item | Phase 1 | Phase 2"): "MLP dimensions | 256 wide, 32 deep | 1,024 wide, 16 deep"; "FLOP budget per MLP | 2.72 × 10¹¹ | 2⁴¹ (approximately 2.199 × 10¹²)"; "Wall-clock cap per MLP | 60 seconds | 120 seconds".
Section "Model architecture" (this is the sentence the brief asked about, and the stated reason for 1,024 x 16):
> The best-performing methods in Phase 1 tended to be based on variations of sampling. We have made the network wider and shallower for Phase 2, to make cumulant-propagation-style methods more competitive. Nevertheless, 16 layers is deep enough that we expect handling depth-dependence well to be a challenge.
> Phase 1:    256 wide, 32 deep     2.1 M parameters
> Phase 2:  1,024 wide, 16 deep    16.8 M parameters
Section "Phase 1 status" (posted 23 Aug):
> The Phase 1 private re-evaluations are in progress. We will report the Phase 1 results, the community contribution prizes, and the algorithmic contribution prizes when they are decided.
> Phase 2 carries $100,000 in prizes, in addition to the $50,000 in Phase 1.
Phase 2 code rules in the same post: computation must go through flopscope; numpy, compiled kernels, threads and subprocesses are prohibited; Phase 2 effective cost equals metered FLOPs.

Phase 2 update post. URL: https://discourse.aicrowd.com/t/18251 ("Phase 2 update: flopscope v0.12.3, deadline extension, and final submission nomination"), post #1 by mohanty, 2026-10-17 08:28:01 UTC. Fetched 2026-11-02 04:44Z.
> Phase 2 submissions close 21 October 2026, 23:59 UTC.
> Algorithmic-contribution write-ups are due 28 October 2026, 23:59 UTC.
> Prize rankings will come from the Phase 2 Private Re-evaluations.
(Rules page still lists Phase 2 End 17 Oct and write-up deadline 24 Oct; see 4.5.)

ARC's guidance on the algorithmic prize. URL: https://discourse.aicrowd.com/t/18041 , post #1 by mohanty; topic created 2026-06-23 20:15 UTC, post last edited 2026-07-06 14:38:28 UTC (heading "Guidance from the Alignment Research Center (ARC)"). Fetched 04:45Z.
> We are most interested in "mechanistic" estimation methods, as discussed in our blog posts on competing with sampling and mechanistic estimation for wide random MLPs. We are less interested in methods that rely heavily on sampling, fine-tuned constants, careful performance optimization, and opaque LLM-optimized code
Townhall summary (AIcrowd's paraphrase of ARC answers, not ARC's own words; video not watched). URL: https://discourse.aicrowd.com/t/18078 , aicrowd_team, posted 2026-07-17, edited 2026-09-07. Fetched 04:45Z. Status: VERIFIED as AIcrowd text, UNVERIFIED as ARC's words.
> As network depth increases, the effective rank of the activation covariance matrix decreases (eigenvalues become more skewed). ARC is internally exploring spending more compute on higher-variance directions rather than tracking every direction equally, as a way to make cumulant propagation scale better with depth.
> Pushing cumulant propagation to higher-order moments improves results initially but eventually diverges. ARC has explored Borel resummation as a possible fix but hasn't fully solved it. They believe this issue matters more for very narrow networks (e.g. width 16) than for the current challenge parameters (width 256), where it shouldn't be a blocker.
> Scoring is based on final-layer MSE only.

### 4.4 AIcrowd challenge page, Rules, starter kit, leaderboard text
Challenge page. URL: https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026 (the older slug /challenges/white-box-estimation-challenge-2026 returns the same 698,833-byte page). Fetched 2026-11-02 04:46Z. VERIFIED.
> Given the weights of a randomly initialized ReLU MLP, can you estimate its expected per-neuron activations more accurately than running the network on a comparable number of sampled inputs?
> Any compliant method is allowed: white-box, black-box sampling, or a hybrid. The leaderboard decides.
> This summary carries no dates, budgets, prize amounts, or scoring parameters.
Round states embedded in the leaderboards page (04:46Z, two data blobs on the same page): the JSON with ids 1425/1428/1429 reads Warm-Up Round CLOSED, Phase 1 CLOSED, Phase 2 CLOSED with "active": true; a second config blob (ids r0/r1/r2) reads COMPLETED, COMPLETED, LIVE. So the page itself is inconsistent about whether Phase 2 is closed. Forum post 18251 says submissions closed on 21 Oct; the Rules table says 17 Oct. The Insights, Resources and Submissions tabs are JavaScript-rendered and contain no readable results text: UNVERIFIED.
Official Rules (decoded from the page HTML). URL: https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/challenge_rules . Fetched 04:46Z. VERIFIED.
> A Private Re-evaluation may take up to three (3) weeks from the close of the corresponding Phase. That Phase's prize ranking is determined exclusively by its Private Re-evaluation.
> Phase 2 End | October 17, 2026, 23:59 UTC
> Phase 2 algorithmic-contribution write-up deadline (write-up only; the Phase 2 evaluator is closed) | October 24, 2026, 23:59 UTC
> Tentative Winner Announcement | Promptly after the Phase 2 Private Re-evaluation concludes; tentatively on or about November 15, 2026
> Phase 1 prize-eligible Participants will be notified by email after the Phase 1 Private Re-evaluation concludes.
> The per-MLP budget is approximately 2.72 × 10^11 FLOPs in Phase 1 and 2^41 FLOPs (approximately 2.199 × 10^12) in Phase 2.
> The primary metric is the MSE of the Participant's final-layer predictions
> s_m = MSE_final,m × max( 0.1 , C_m / B_m )
Discrepancy to note: the Rules table (Phase 2 End 17 Oct) was not updated for the forum extension to 21 Oct.
Starter kit README (current main, Phase 2). URL: https://raw.githubusercontent.com/AIcrowd/whest-starterkit/main/README.md . Fetched 04:50Z. VERIFIED.
> You are given a randomly-initialized ReLU MLP and a FLOP budget. Predict the per-neuron mean activation under N(0, 1) input, without spending the whole budget on forward passes. Your score is the error on the **final layer only** (`final_layer_mse`, against N=1e9 Monte-Carlo ground truth), multiplied by `max(0.1, C_m / B_m)`
> Every MLP in the suite has width 1024 and depth 16, so `predict()` returns a `(16, 1024)` array, and each MLP carries its own budget of `2**41` FLOPs (roughly 6.5e4 forward passes).
Leaderboard text (public boards, server-rendered HTML; columns "Adjusted Score | Final Layer MSE | Compute utilisation | MLPs failed | Entries | Last Submission"). Fetched 04:46Z (Phase 2, default board, leaderboard id 1480, round 1429) and 04:52Z (round 1428 = Phase 1, round 1425 = warm-up, via ?challenge_round_id=). These are public-board standings, NOT the prize ranking.
- Phase 2 board rows 1 to 4: marius_binner 0.0000000013 / 0.0000000110 / 0.1221553603 (327 entries, last 16 Oct 2026 12:59); oliver_chen 0.0000000013 / 0.0000000110 / 0.1217872081 (151 entries, last 20 Oct 17:55); team J2W 0.0000000014 / 0.0000000136 / 0.1065148461; mliston 0.0000000014 / 0.0000000132 / 0.1099203684. Latest "Last Submission" visible on page 1: Wed, 21 Oct 2026 22:46 (team thegamers). 7 pages of entries.
- Phase 1 board rows 1 to 3: ednacob 0.0000000184 / 0.0000000363 / 0.5082181609 (169 entries, last 10 Aug 2026 02:51); team J2W 0.0000000539 / 0.0000002784 / 0.2046026674; dstepanov 0.0000000622 / 0.0000002199 / 0.2835534538.
- Warm-up board row 1: Puffi 0.0000000391 / 0.0000003269 / 0.1194597561 (last 15 Jun 2026).
The adjusted score equals final-layer MSE times max(0.1, utilisation) per the Rules formula (check: 1.10e-8 x 0.1222 = 1.34e-9). /home/agent/workspaces/mats/outbox/arc-deep-networks-2026-10-29.md cites forum topic 18157 for a claim that two Phase 1 top entries were removed in an 18 August rescore; I read only the opening of 18157 and did not verify that claim.

### 4.5 Official results or winners published? NOT FOUND as of 2026-11-02 ~05:00Z
What I checked and saw:
- Forum category 2991 (ARC White-Box Estimation Challenge 2026), JSON topic list, 132 topics, newest created 2026-10-31 (https://discourse.aicrowd.com/c/white-box-estimation-challenge-2026/2991.json, fetched 04:45Z). The last topic created by the organizer account mohanty about this contest is 18251 (2026-10-17); aicrowd_team's last topic created about this contest is 18078 (2026-07-17), last reply seen 2026-08-10 (18130); snehananavati's last post in this category is a reply of 2026-07-16 (18048). No topic titled results, winners or private leaderboard from any organizer account (user_actions.json, 04:55Z).
- Forum search (search.json, category 2991, terms "Phase 1 results", "private re-evaluation results", "winners announced", "congratulations winners", "final leaderboard", "Phase 1 private leaderboard", "prize winners"): only participant write-ups and the organizer posts quoted above.
- The Rules table above: Phase 2 winners "tentatively on or about November 15, 2026"; a participant (oleksandr_barskyi, post #3 of 18197, 2026-09-26) also writes "Winners are announced on 15 November".
- ARC blog index, RSS and sitemap: newest post 9 Jun 2026 (Section 9).
- Search engine (WebSearch, "ARC White-Box Estimation Challenge results winners announced Phase 2 AIcrowd"): no announcement found.
UNVERIFIED: whether Phase 1 prize-eligible participants were notified privately by email (the Rules say email); I cannot read email, so "no public Phase 1 results" is the claim, not "no Phase 1 results".

### 4.6 Participant material (community, not ARC; I read the opening of each cited post and the replies in 18251, and reproduced no number)
Listed because it bears on depth. Treat as UNVERIFIED third-party claims; most state AI assistance.
- Topic 18147 (jonah_butterbaugh, 2026-08-10): "The non-Gaussianity wall, measured with certificates" at depth 32 width 256: diagonal Gaussian closure 7.18e-4, exact full-covariance Gaussian closure 9.61e-5, "a budget-matched sampling estimator: ~2.5e-7".
- Topic 18198 (keenanpepper, 2026-08-24): six leaderboard entries tied at "3.93e-7 adj / 3.93e-6 MSE" are "probably all the plain & simple covariance propagation baseline. Which decisively beats sampling in Phase 2."
- Topic 18298 (pranav_viswanath, 2026-10-30): claims "when depth grows with width, a collective scale mode builds up that poisons the order-by-order expansion", a one-parameter law restoring convergence, tested "64x16 through 1024x256"; repo https://github.com/PranavViswanath/scale-separation (not run).
- Topics 18246/18248/18249/18282 (Oct 2026): titles and openings describe Phase 2 estimators built on factorized third-cumulant chains with fitted fourth-cumulant closures and learned correctors. Topic 18282 (megan_park, 2026-10-24): "It never samples. From the weights alone, it propagates means, covariances and low-rank third cumulants through all 16 layers." and "Its public score is 1.918e-9, and its final-layer MSE is 84× below full-budget Monte Carlo at 14 % of the budget."

---------------------------------------------------------------------------------------------------

## 5. Hilton et al., "Mechanistic estimation for expectations of random products" (alignment.org, 15 May 2026). VERIFIED

URL: https://www.alignment.org/blog/mechanistic-estimation-for-expectations-of-random-products/ . Fetched 2026-11-02 04:43Z. Authors: Jacob Hilton, George Robinson, Eric Neyman, Paul Christiano, Michael Winer, Victor Lecomte, Wilson Wu, Gabriel Wu. The post's four linked notes are halfspace intersections, products of symmetric random functions (#3-SAT), the {0,1}-permanent, and Fourier random-walk estimators (in that order, under "Detailed notes").
Section "Detailed notes", last sentence (the claim asked about):
> In each case, we roughly match or outperform random sampling up to logarithmic factors, except for the third case, where we are further behind.
(The post does not name the third case; by list order it is the permanent note. That identification is mine.)
Section "Deduction–projection estimators":
> The general idea of a deduction–projection estimator is to split up an expensive computation into multiple steps, and then to alternate between "deduction" steps, which perform one step of the computation exactly, and "projection" steps, which simplify the computational state, preventing an exponential blowup in complexity.
> For example, our cumulant propagation algorithm for wide random MLPs has this form: in the "deduction" step, we use the activation cumulants at one layer to deduce the activation cumulants at the next layer exactly, and in the "projection" step, we drop terms that are insignificant relative to their computational expense.
Footnote 2: 
> In practice, the deduction and projection steps are not so cleanly separated, and instead we perform an approximate deduction step that combines both.
Section "Mechanistic L² sketching":
> We refer to this problem as mechanistic [...] sketching, because we want the representation of [...] to be "mechanistic" (rather than consisting of the value of the function on random points, say)
> Once the problem is isolated in this way, the solution ends up being a straightforward application of linear algebra.
> The maximum mean squared error is then determined by the largest unused eigenvalue
Section "Random instances of the matching sampling principle":
> In fact, they are all choices in which [...] has no learned or worst-case parameters [...]. They still have random parameters, which are captured in the "context" variable [...], making them similar to randomly-initialized networks rather than trained networks.
> Generally speaking, we have been able to do this in cases where the function [...] and the distributions from which [...] and [...] are drawn have sufficient symmetry, rather than being highly complex.

---------------------------------------------------------------------------------------------------

## 6. Christiano, "Returning to ARC" (Alignment Forum, 4 Aug 2026). VERIFIED

URL: https://www.alignmentforum.org/posts/vLFh8HP3hyNy9MCwe/returning-to-arc (LessWrong mirror: https://www.lesswrong.com/posts/vLFh8HP3hyNy9MCwe). Page header date "4th Aug 2026", "11 min read". Fetched 2026-11-02 04:47Z (curl, server-rendered HTML).
The "bold conjecture" is footnote 10, attached to the main-text sentence "Despite that initial surprise, in essentially every case humanity has eventually been able to "understand" what is going on well enough that our mechanistic analysis approximately[10] agrees with the empirical results."
> The quality of the prediction depends on how much compute you are willing to spend on the task. ARC believes the bold conjecture that for all problems the approximation quality for mechanistic estimates improves faster than the best empirical method (though we are particularly interested in problems, like predicting out of distribution generalization, for which we think we can have much better efficiency than empirical methods).
Footnote 11 (sampling):
> (iii) we can use those explanations make mechanistic estimates at the level of quality we are targeting, including answering questions about behavior that are intractable for sampling but that we believe should be straightforward if you "understood" how a given model works.
(The missing "to" is in the source.)
Depth or random MLPs in the post: none. Grep of the whole page text for depth, MLP, width, cumulant, contest, challenge: no hit in the post body (the only "depth" is in a reader comment). The word "random" appears only in examples (a random SAT instance, random numbers, randomly generated math problems).
Related Christiano comments under the post (LessWrong GraphQL, 2026-11-02 05:00Z): 2026-08-09 (commentId 823W69qEqTepKcyFw), on chess: "for a given position under random play you should have a mechanistic estimate for the the probability that white wins which is more accurate than sampling. I think that's a really interesting and probably very tractable problem---I expect a solution to involve tracking how various features evolve over the course of the game, and then to track increasingly high-order interactions between features as you improve your precision." 2026-08-05 (commentId GaiQucrt2xmtvCxWo): "We can't yet succeed even for the simplest networks; explaining the AlgZoo models would be a huge milestone for us."

---------------------------------------------------------------------------------------------------

## 7. Winer, "A Mike's-Eye View of ARC's Research" (alignment.org, 9 June 2026). VERIFIED

URL: https://www.alignment.org/blog/a-mikes-eye-view-of-arcs-research/ . Fetched 2026-11-02 04:43Z. Author Michael Winer, "June 9th, 2026".
Section "Matching Sampling Principle":
> We use the word "mechanistic", even though we don't have a clear definition of it.
> The definition ARC gives is usually something like "never assume the input-output behavior you haven't seen looks like the behavior you have seen, for any object."
> Never assume that if you construct a ridiculously complicated object mechanistically from the model, and give that object 100 samples, the sample average equals that ridiculously complicated object's average behavior.
> The (average case) MSP states that for any architecture and degree of precision, there is a mechanistic estimator that at least matches the performance of sampling over random instances of that architecture.
> At the time of writing, one of the crown jewels of this approach is an algorithm that takes in the weights
(continues with LaTeX: "θ of a multilayer perceptron f_θ, and outputs an estimate EST(θ,ε) which approximates E_{x∼N(0,I)} f_θ(x) to within additive error ε averaged over assignments of θ, while running more efficiently than a Monte Carlo estimator.")
Footnote 2 of the same post:
> For most values of
(continues "θ, including more and more cumulants will give a more and more accurate estimate in a way that beats Monte Carlo estimation.")
Randomness to choose what to analyse is allowed (the Liouville-function example, bullet "This sort of estimator can be randomized."):
> This sort of estimator can be randomized. I didn't specify how we chose the subset of points to analyze in our estimator. They could absolutely have been chosen randomly. Using randomness to determine what aspects of a system to analyze more carefully doesn't violate mechanisticness. The only violation would be to assume the things we haven't carefully examined yet look like the things we have.
Same example, why the evaluated-subset estimator is still mechanistic:
> Note that this only differs from the sampling estimator by a factor out front
(continues "1/2^30 instead of 1/m".)

---------------------------------------------------------------------------------------------------

## 8. ARC code repo: https://github.com/alignment-research-center/mlp_cumulant_propagation . VERIFIED, unchanged

Fetched 2026-11-02 04:48Z (api.github.com and raw.githubusercontent.com).
- Default branch main, HEAD 93d091a ("Skip kprop metric bookkeeping when no radial pieces are tracked", by wilson, committed 2026-08-04T20:54:27Z; I saw only the 7-character hash). Identical to the local clone /home/agent/workspaces/mats/work/arc-noisy/ext/mlp_cumulant_propagation (git log -1 = 93d091a). 9 commits on main; no commit after 2026-08-04. Repo metadata: description "Public code for wide random MLPs paper", created 2026-04-27, pushed_at 2026-08-04T20:56:30Z, updated_at 2026-10-20T18:27:40Z (metadata only), 0 open issues, 2 closed PRs (#1 Var clamp, #2 Edgeworth terms).
- TODO.md on GitHub main versus the local clone's TODO.md: `diff` reports IDENTICAL. The text is (verbatim, the stale-outputs paragraph):
> **All cached kprop outputs, data files, and FLOP counts (and any downstream
  figures) for `k_max >= 2` are stale and need to be refreshed.** (`k_max = 1`
  is unaffected; test goldens have already been refreshed via
  `scripts/refresh_goldens.py`.)
and the third bullet ends: "**The paper needs updating** to reflect both the augmented Edgeworth cap (equation (14) with K+1 instead of K for the augmented algorithm, contra S.4.2's "all other parts remain the same") and that factorized-augmented computes a different estimate than (unfactorized) augmented."
- Other branches (NEW, not in old sheet; unmerged, scripts only, no published claims): `max` (fc302a7, 2026-07-13, Max Misterka, "fix small variance cumulant explosion"; 3 ahead, 4 behind main); `experiment/max-endpoint` (357c455, 2026-07-16, Kunal Chawla, "Fixed-width FLOPs-vs-MSE plot (n=128 depth 4): direct dense estimators vs MC Var/m tradeoff"; 29 ahead); `treewidth-fixed-width-plot` (ef81e90, 2026-07-16, Kunal Chawla, "Fixed-width FLOPs-vs-MSE plot for treewidth-pipeline estimators (n=1448 depth 4) vs MC Var/m"; 30 ahead). The experiment branches also contain a commit titled "Add max-endpoint estimator: Edgeworth expansion of E[max] via cumulant" (title truncated at 70 characters in my listing). The two Kunal Chawla commits carry an AI co-author trailer, i.e. AI-assisted authorship.
- ARC org public repos (api.github.com/orgs/alignment-research-center/repos, 04:49Z): alg-zoo (pushed 2026-08-19), mlp_cumulant_propagation (2026-08-04), low-probability-estimation (2024-10-23), heuristic-hafnian (2024-10-03). `mlp_kprop` does not exist (404).

---------------------------------------------------------------------------------------------------

## 9. Anything newer from ARC on depth, deep random MLPs, or contest results (after June 2026)

Result: no ARC-authored blog post, arXiv paper or LessWrong/Alignment Forum post on depth, deep random MLPs or contest results after 9 June 2026. ARC-staff statements on depth and the contest do exist outside the blog and are NEW to the old sheet: Hilton's comment of 23 June (Section 4.2; also cited in /home/agent/workspaces/mats/outbox/arc-deep-networks-2026-10-29.md) and, not cited in either the old sheet or that outbox summary (grep for 18041, 18078, townhall, Borel, higher-variance: no hits), ARC's guidance post 18041 and the AIcrowd townhall summary 18078 (Section 4.3). What I checked:
- alignment.org/blog index pages 1 and 2 (curl, 04:43Z): newest post "A Mike's-Eye View of ARC's Research", June 9th, 2026. RSS https://www.alignment.org/blog/feed/ lastBuildDate Thu, 29 Oct 2026 11:49:01 GMT, newest item pubDate Tue, 09 Jun 2026 18:27:31 GMT. https://www.alignment.org/sitemap-posts.xml lastmod 2026-06-09T19:06:07Z (that is the bird's-eye-view post being touched). Pages sitemap: home and blog index lastmod 2026-10-29T13:12Z with no new post listed. The posts in the feed after 9 June: none.
- arXiv API (export.arxiv.org, 04:55Z), sorted by submission date: au:Hilton_Jacob, Christiano_Paul, Lecomte_Victor, Winer_Michael, Neyman_Eric, Robinson_George (cs.LG/stat.ML), Wu_Wilson (cs.LG/stat.ML/cond-mat.dis-nn). Newest relevant: 2605.05179 v2 (2026-05-14). Off-topic newer papers: Lecomte and Ramakrishnan, "Optimal Shallow Circuits for Majority" (arXiv 2609.34029, 2026-09-27, Boolean circuits); Sous and Winer, "Asymmetric Scaling Laws from Sparse Features" (2605.23591, 2026-05-22). Phrase searches (all:"cumulant propagation", "mechanistic estimation", "matching sampling principle", "white-box estimation", "deduction-projection", "expected output" AND "random MLP" AND "sampling"): nothing from ARC; unrelated hits only.
- LessWrong and Alignment Forum: all posts from 2026-06-10 to 2026-11-02 pulled through the GraphQL API (about 3,000 posts: 717 + 738 + 610 + 1,000 in four date windows; the newest window hit the 1,000-post cap but its oldest post is 2026-09-21, which meets the previous window, so there is no gap) and filtered by ARC author names and by keywords (ARC, Alignment Research Center, cumulant, mechanistic estimat, matching sampling, MSP, white-box estimation, random MLP, heuristic estimat, deduction, presumption of independence, no-coincidence, AlgZoo). Hits: Christiano "Returning to ARC" (2026-08-04); Christiano "Personal statement on joining the OpenAI nonprofit board" (2026-09-09, not research); third-party: Kubů "ARC's research agenda: solid mathematics, an unclear safety case" (2026-07-28), Zach Allen "Where Did D Go? A Gap Between ARC's Motivation and Its Formalism" (2026-08-26), Josh Snider "Brute-Force Progress on AlgZoo's 432-param Interpretability Challenge" (2026-10-26). Hilton's and Christiano's own comments since 24 June (profileComments): Hilton's newest are about AI-use levels and math time horizons (Oct 2026); Hilton on AlgZoo, 2026-08-17: "we are not much closer to succeeding at the challenge given at the end of the post"; nothing on depth or the contest after 23 June.
- ARC GitHub org: Section 8 (no new code after 4 Aug; AlgZoo repo 19 Aug).
- AIcrowd forum: 132 topics to 31 Oct 2026; Section 4.5 (no organizer results post).
- Web searches (WebSearch): "ARC White-Box Estimation Challenge results winners announced Phase 2 AIcrowd"; "Alignment Research Center cumulant propagation deep random MLP depth growing with width mechanistic estimation sampling". Found only the sources above plus participant GitHub repos (acco-cyber/arc-whitebox-estimation-2026, Hero988/arc-whitebox-estimation-2026-phase2, PranavViswanath/scale-separation), not opened beyond the search summary.
Not checked: X/Twitter, Slack/Discord, email, YouTube townhall video, Hugging Face dataset card text, Lever job postings, the PDFs attached to forum posts.

---------------------------------------------------------------------------------------------------

## 10. Changes relative to the old fact sheet (arc_estimators.md, 2026-10-31)

CHANGED (a quote or fact in the old sheet is now different): none. Every quote I re-checked from entries E2, E3-E6, E12, E14 and the Returning-to-ARC line matches the live text.
Unchanged on re-check: arXiv latest is v2 (no v3); paper body link mlp_kprop still 404; ARC blog newest post still 9 Jun 2026; repo HEAD still 93d091a and TODO.md byte-identical; AIcrowd landing-page text.
NEW or refined (additions, not contradictions):
1. E15 had no Phase 1 or Phase 2 facts. Added: warm-up 256x8 at 6.8e10; Phase 1 256x32 at 2.72e11 (18 Jun to 10 Aug); Phase 2 1024x16 at 2^41 (22/23 Aug to 17 Oct, forum-extended to 21 Oct); about 6.5e4 forward passes of budget in every round (derived); prize pools; the "best-performing methods in Phase 1 tended to be based on variations of sampling" sentence and the stated reason for 1024x16.
2. New primary ARC statement: Hilton's 23 June LessWrong comment (depth raised 8 to 32; "Our existing algorithms scale poorly with depth"; warm-up winners were factorized third-cumulant variants plus learned networks). Also new to the old sheet and to /home/agent/workspaces/mats/outbox/arc-deep-networks-2026-10-29.md (grep for 18041, 18078, townhall, Borel, higher-variance: no hits): ARC's algorithmic-prize guidance (forum 18041, 6 July) and the AIcrowd townhall summary (forum 18078; AIcrowd's paraphrase of ARC remarks on spending compute on higher-variance directions to scale cumulant propagation with depth, and on Edgeworth divergence with Borel resummation "not fully solved").
3. The old sheet's "bold conjecture" line is footnote 10 of Returning to ARC (locator added), and the post has no depth or random-MLP sentence; Christiano's 9 Aug comment adds "increasingly high-order interactions ... as you improve your precision".
4. Official results: not published. Rules: winners "tentatively on or about November 15, 2026"; Phase 1 notification is by email.
5. Rules page versus forum: Phase 2 End 17 Oct and write-ups 24 Oct on the Rules page; 21 Oct and 28 Oct in forum post 18251.
6. Unmerged ARC-repo branches about fixed-width plots and a "treewidth-pipeline" estimator (July 2026), and an Edgeworth E[max] estimator.
7. The canonical contest URL is https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026 (the old sheet used the older slug, which still serves the same page).
8. The old sheet saw participant forum posts only as search snippets and treated them as out of scope (E15); the organizer posts on the forum are now read in full, and participant posts are listed, with the limits stated, in 4.6.

---------------------------------------------------------------------------------------------------

## 11. Verification footer

Machine check run 2026-11-02 ~05:05Z on this file (scripts /tmp/arcsrc_scripts/verify_quotes.py and verify_strict.py): every blockquote line (except the 3 lines marked "[math; image-checked]" and the fenced LaTeX block) was compared with the downloaded source texts, "[...]" splitting a quote into segments that must each occur. Lenient pass (case, whitespace, punctuation and markdown ignored): 93 of 93 blockquote lines match. Strict pass (punctuation and case kept, curly quotes and PDF line-break hyphens normalized): 84 of 93 match; the other 9 are PDF text-extraction spacing artifacts around italic words, arrows and math ("particularnetwork", "Aftercomparing", "providingεis", "getworsewith", "anyestimation", "n→ ∞") and I checked them by eye on rendered page images (pp. 2, 6, 10, 18, 57). Rendered pages read by eye: 2, 3, 4, 6, 7, 10, 18, 19, 57. Quotes from the blog posts, forum posts, Rules, README and AF page all match strictly. Not machine-checked: the fenced LaTeX block in Section 3 (copied from the page source) and the non-blockquote paraphrases and numbers (leaderboard rows, dates, hashes), which were read from the fetched text at the times given.

---------------------------------------------------------------------------------------------------

## 12. What "matching sampling" means to ARC (DERIVED by this worker; not a statement by ARC)

Read from the quotes above, "matching sampling" is a parity claim against plain Monte Carlo on random instances, stated in the same units for time and error. In the principle itself (Section 3), an estimator matches sampling at tolerance eps if it runs in time of order (1/eps^2) forward passes of the model and its squared error, averaged over the random instance c, is at most eps^2 times the average variance of one forward pass, which is exactly the error of averaging N = 1/eps^2 samples (the paper calls this variance-normalized MSE = 1/N, Section 1b). It is an average-case, per-instance-family statement with an advice string pi for trained parameters; for a random MLP the parameters are empty, c is the weight tensor, and the average runs over Gaussian weights per output neuron (Sections 1b, 3). In the 2026 paper "matches" is weaker and more specific: asymptotic in the width n, constants ignored, fixed depth L, tolerance eps(n)^2 at least 1/poly(n), and proved only for polynomial activations (Sections 1c, 1e). The word "mechanistic" attached to it is informal: the Nov 2025 post offers "avoids any random or pseudorandom sampling" as a heuristic it calls not entirely correct, while Winer's post says randomly choosing what to analyse is allowed and only extrapolating from unexamined cases is forbidden (Sections 3, 7); the contest allows any method but ARC "strongly expect[s]" the best to be mechanistic (Section 4.1). Two points follow by my arithmetic from the stated bounds, not from ARC. First, the match is a worst-case-over-eps statement: order-K cumulant propagation reaches MSE n^(-K) in time about L n^(K+1) (basic), while sampling needs n^K forward passes at n^2 L each, so at eps^2 exactly n^(-K) the basic estimator is a factor n cheaper and just below n^(-(K-1)) it ties; the paper's "factor n" for the factorized version (time L^2 n^K for K >= 3) is the worst-case gap n/L between L^2 n^K and L n^(K+1), so the advantage over sampling vanishes when depth is of order the width. Second, the conjectured error c_K (L/n)^K stops shrinking with K once L is of order n, which is the regime ARC lists as open ("the depth growing linearly in the width"); at the contest's Phase 1 shape (n = 256, L = 32, L/n = 0.125) and Phase 2 shape (n = 1024, L = 16, L/n = 0.0156) the ratio is small but not asymptotically small, and the contest scores raw final-layer MSE against a 10^9-sample reference at about 6.5e4 forward passes of budget, not the paper's variance-normalized MSE.
