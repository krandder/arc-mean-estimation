# Audit of the untrusted scale-separation repository (written 2026-11-02 ~10:45Z, before any of its code ran)

Source: https://github.com/PranavViswanath/scale-separation, cloned 10:28Z into `thirdparty/scale-separation/` (a new empty
directory). HEAD bfeab38a01050aa4200c0f265b4a0c6abce9b876 ("updates", 2026-10-30T17:01Z); tag `phase2-submission` =
431fe4261b6f3de5ceb1de4120304f1ef83aa8a4 (2026-10-29T03:04Z). 19 commits, 2026-10-28T23:51Z to 2026-10-30T17:01Z, one author.
Repo created 2026-10-28T23:50:33Z, about 7 minutes before forum topic 18298 was opened (23:57:09Z).

## What I read
Every text file, line by line: README.md, WRITEUP.md, run_cell.sh, requirements.txt, .gitignore; estimator/lvlib.py (509
lines), lv2.py, conv.py, convI.py, verify_v2.py; arc_ladder/arc.py, dsc.py, descale_src.py, sl_fac.py,
descale_fac_src.py; evaluation/nets.py, mc.py, ana.py, expo.py; challenge_1024x16/README.md, run.sh, get_nets.py,
score_k2.py, graded_ablation.sh, k3_scale_law.py (329 lines), LICENSE-504aldo-V29; docs/PREREG.md, VRULE.md, build_pdf.sh,
writeup.css; extensions/README.md, THEOREM.md, verify_theorem.py, verify_theorem.log; figures/figs.py.
Partly read: challenge_1024x16/graded_entry_336823.py (1909 lines; a contest entry built on 504aldo's V29). I read its
docstring, its embedded coefficient tables, every environment read, and its `__main__` block, and grepped the whole file
for imports, open/exec/eval/pickle/save/write, os/subprocess/socket/urllib/requests/http/shutil/remove: it imports only
math, flopscope, whestbench, os (environment reads), gc, and local_engine inside `__main__`. It is not run here. It is
also not the claim's estimator: it carries fitted tables (CORR_BETA ridge-fitted on public MLPs, the LAM table).
Not read as code: WRITEUP.pdf and figures/*.png (data). The PDF text was extracted with pypdf (scripts/pdf_text.py).

## Findings
- Network: no Python file makes a network call. docs/build_pdf.sh calls pandoc with a KaTeX CDN URL and headless Chrome
  (network and processes); docs/writeup.css imports Google Fonts. Neither is run.
- Processes: run_cell.sh, challenge_1024x16/run.sh and graded_ablation.sh launch python and the `whest` CLI; no Python
  file spawns a process. None of the shell scripts is run.
- Writes: every Python script writes only into its working directory (np.save / np.savez of results, figures) or prints.
  k3_scale_law.py also writes np.savez(path) when the environment variable XDUMP is set. graded_ablation.sh copies and
  sed-edits the entry into runs/.
- exec: dsc.py, sl_fac.py exec() a sibling file (descale_src.py, descale_fac_src.py) read by path. Both files contain only
  function definitions (partition machinery and the de-scaling maps), which I read.
- Devices: every runnable script hard-codes "cuda" (mc.py, lv2.py, arc.py, dsc.py, sl_fac.py, conv*.py, verify_v2.py,
  k3_scale_law.py). lvlib.py is device-agnostic (uses the input tensors' device).
- Environment: graded_entry reads ~25 V*_ knobs from os.environ; nothing else reads the environment except XDUMP, HORIZON,
  HUBTAU, NTRUTH, SEED in k3_scale_law.py and ANT, RQ in mc.py / expo.py.

## Decision
- I do not run any of their scripts. My adapters in `scripts/` (a separate directory) load exactly two of their files:
  estimator/lvlib.py, imported by file path with importlib (module-level code: imports of math, numpy, torch,
  scipy.special, numpy.polynomial.hermite, and definitions), and arc_ladder/descale_fac_src.py, exec'd into a private
  namespace that I supply (dev = cpu, dt = float64, math, torch, ARC's HTensor and FactoredTensor), which is what
  sl_fac.py does. ARC's own code is the local clone at commit 93d091a (work/arc-noisy/ext/mlp_cumulant_propagation), not
  anything from this repository.
- Paths are passed as arguments; runs use `python -I`, `nice -n 19 ionice -c3`, and `env -i` with only PATH, HOME (a
  scratch directory) and thread-count variables, so LINEAR_API_KEY, ANTHROPIC_AUTH_TOKEN and the other secrets in my
  environment are not visible to the process. Outputs go to work/scale-mode/runs/ through my own code only.
- No GPU is needed: the estimator is float64 torch on CPU; the claim's frozen numerics (R = 24, b = 6.5, rule 'v2f',
  Gamma moments 'full') are used unchanged.

## The PDF attached to the forum post vs the repository today
- The attachment (sha256 d7f1c06d..., created 2026-10-29 16:07Z) is titled "Solving cumulant propagation's depth problem
  with scale separation", subtitle "A fit-free estimator that beats sampling at every width tested when depth grows with
  width", and says "This note answers it on ARC's own criterion, with ARC's own code."
- The repository's WRITEUP.md since commit bfeab38 (2026-10-30 17:01Z) is titled "Addressing ...", adds "with a margin
  that narrows as width grows", replaces "answers it" by "a substantial step on the open problem rather than a complete
  answer to it", and adds two scope items: the pre-registered width test failed (exponent of the margin over naive
  sampling -0.20, 95% CI [-0.38, -0.04]; the line required the CI to include 0), and the scale-law ladder is not monotone
  at 64x32 (L/n = 1/2). The repository's WRITEUP.pdf (16:43Z on 29 Oct) still has the older text.
