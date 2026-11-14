## 11. Files

All under `work/gram-chain/`:
- `FORMAL.md` (theory v2: sections 1-6 are v1 as frozen at 21:14:08Z, kept also as `coprover/FORMAL_v1_as_written.md`;
  section 7 holds the v2 additions); `notes/questions.md` (premises checked, open questions with their checks);
  `notes/for-siblings.md` (what I sent the relevance and bits-bounds lanes); `HANDOFF.md`.
- `lib/gc2.py` (the chain: any R, correlated / label / coordinate noise sharing, tangents, surgery, inputs, output layer,
  mean-field fixed point); `tests/test_gc2.py` (`logs/test_gc2.log`, 19 checks pass).
- `PREREG.md` (Parts A, B, C; Amendments A1, C1), `prereg_hashes.txt`, `coprover/PREREG_*_as_hashed.md`;
  `logs/deviations.log`.
- `scratch/`: `partA.py`, `partB.py` (`partB_as_registered.py`), `partC.py` (runs); `score_A.py`, `score_B.py`,
  `score_C.py` (scorers); `theory_numbers.py`, `predB.py`, `onestep.py`, `pr_by_radius.py`, `partD_gates.py`
  (theory and post hoc numbers); `figs.py`, `tables.py`; `quick_*.py` (exploratory, disclosed); queue scripts.
- `runs/` (one JSON or NPZ per run), `results/` (scores and tables), `figs/` (fig1_stationary_law, fig2_relevance,
  fig3_dimension, fig4_input), `coprover/` (astra prompts, raw logs, answers, `PROVENANCE.md`), `review/`.
Python: /home/agent/.venvs/arc-noisy/bin/python.
