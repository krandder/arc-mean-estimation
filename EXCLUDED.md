# What was left out, and why

Everything here was left out when the repository was assembled on 14 November 2026. Nothing was deleted or changed
at the sources. Each lane's own counts are in `lanes/<lane>/PROVENANCE.md`. The rules are in `tools/collect.py`.

## Inside the lane work directories

| reason | files | MB |
|---|---|---|
| checkpoint / array / binary (npz) | 2214 | 12983.3 |
| checkpoint / array / binary (pt) | 2468 | 9484.5 |
| checkpoint / array / binary (npy) | 89 | 2504.4 |
| third-party downloads (forum pages, other people's code and data) | 1020 | 2158.4 |
| over 5 MB | 9 | 108.9 |
| agent/model session transcript | 114 | 44.6 |
| vendored third-party git repository | 1189 | 42.9 |
| machine output over 1 MB (json) | 17 | 27.4 |
| third-party code | 76 | 4.8 |
| third-party papers (PDF/text of published papers) | 15 | 3.2 |
| cache | 187 | 2.6 |
| checkpoint / array / binary (pth) | 46 | 0.1 |
| job-queue state marker | 421 | 0.1 |
| fleet memory recall output (past conversation text) | 2 | 0.0 |
| identical copy of a third-party file | 2 | 0.0 |
| GPU infra state (holds an SSH private key) | 113 | 0.0 |
| binary without known research format | 1 | 0.0 |
| symlink | 12 | 0.0 |

Notes on these rows:

- **Checkpoints and arrays** (`.pt`, `.npz`, `.npy`, `.pth`): model weights, saved truths and sample arrays. 883 of them are over 5 MB.
  They stay on the host General under each lane's original work dir. Code that regenerates them is in the lane.
- **Over 5 MB, not arrays** (9 files):
  - `narrow-deep/runs/collapse_plain_n16_L256_s0.001.json` (6.4 MB)
  - `narrow-deep/runs/collapse_plain_n16_L256_s0.01.json` (6.4 MB)
  - `narrow-deep/runs/collapse_plain_n16_L256_s0.json` (5.7 MB)
  - `narrow-deep/runs/collapse_plain_n8_L256_s0.001.json` (6.2 MB)
  - `narrow-deep/runs/collapse_plain_n8_L256_s0.01.json` (6.5 MB)
  - `narrow-deep/runs/collapse_plain_n8_L256_s0.json` (5.0 MB)
  - `cut-rank-ext/logs/nl_n8_c4_d4.log` (9.0 MB)
  - `cut-rank-ext/logs/nl_n8_c64_d8.log` (33.7 MB)
  - `cut-rank-ext/logs/nl_n8_c8_d8.log` (30.0 MB)
- **Machine output over 1 MB**: single JSON result files between 1 and 5 MB. The limit for reports, code and
  figures is 5 MB; for machine-written `.json/.jsonl/.log/.out/.err/.txt/.csv/.tsv/.html/.xml` it is 1 MB, so that
  result files in the repository stay small. The lane reports and scorecards that summarise them are included.
- **Session transcripts** (114 files): raw session dumps of reviewer and co-prover models (prompt echo, tool calls,
  intermediate output), and one truncated dump that had been saved under an `.md` name. Where the lane had already
  saved the model's final answer as its own file, that file is included. Where it had not, the final message was
  extracted into `<name>.final-message.md` (28 files; these do not exist at the source). The prompts are included.
- **GPU infra state**: the `infra/` directories of `adaptive-regions`, `backward-bits`, `bit-accounting`, `bit-accounting-arc`, `scale-mode`.
  Each holds an SSH private key (`infra/state/soup_ed25519`) next to VM bookkeeping files. None of it was copied.
  The key files are still at the sources.
- **Fleet memory recall output**: two `logs/recall1.txt` files holding output of the fleet's memory search, which
  quotes past conversations.
- **Third-party code, downloads and papers**: other people's repositories vendored into lanes, scraped forum and
  leaderboard pages, datasets fetched from the contest, and PDFs of published papers. Copies of third-party files
  found elsewhere in a lane (same SHA-256) were left out too. Upstream addresses and commits:
  - https://github.com/alignment-research-center/mlp_cumulant_propagation.git at commit 93d091a (used by `arc-noisy`)
  - https://github.com/AIcrowd/flopscope.git at commit 8632052 (used by `arc-noisy`)
  - https://github.com/AIcrowd/whest-starterkit.git at commit 96e308c (used by `arc-noisy`)
  - https://github.com/alignment-research-center/alg-zoo.git at commit 4433f50 (used by `algzoo-noisy`)
  - a contest participant's public repository at commit bfeab38 (lane `scale-mode`; no licence file; address in the lane's notes; see `OPEN-DECISIONS.md`)
  - https://github.com/AIcrowd/whestbench.git at commit ef8416b (used by `phase1-board`)
- **Job-queue state markers, caches, symlinks**: `.lock/.pid/.started/.done/.claimed` files, `__pycache__`, links.

## Secret scan

`tools/secret_scan.sh` was run on the whole tree before each commit (API-key and token formats of the common
providers, private-key headers, URLs with embedded credentials, `KEY=`/`TOKEN=`/`password=` assignments, key-like
file names). It found nothing in the copied tree. The only secrets met during collection were the SSH private
keys named above, which were excluded with their directories. GPU logs in some lanes list the public IP addresses
of cloud VMs that the lanes created and deleted; those were left in.

## Left out as not ARC research, personal, or transcript-derived

From `/srv/agent-data/home/workspaces/mats/outbox/` (about 250 files), only the ARC lane reports, the ARC
literature notes, the 31 October summary, the 2 November synthesis draft and the programme definition were taken.
Left out:

- Forecasting, Market Pulse, Metaculus access and data-permission notes; MATS proposals, logistics, compute and
  reimbursement notes; call transcripts and people notes.
- Learned search, toy search, POMDP and active-inference search papers and studies; the rounds 4-9 experiment
  papers and audits; the Gemini campaign critique.
- Learned aggregation against exact Bayes (gate reviews, role keys, rich agents, atom and ordering energies), PFN
  worlds, tiny PFN, the binding-plateau paper, World FA, the C6 note.
- The in-context-Bayes mechanism study (noisy-channel phases A and B, `cm-interp-phaseB-*`), scale-free combination
  (`scale-free-*`), the cooperation toys (`lob-*`, `energy-prudentbot`), attention-flow and tangled-architecture
  notes other than the one literature note kept under `reports/literature/`.
- `OPUS-MATS-CONTEXT.md` (an agent's working context file), `research-inventory-2026-11-03.md` (covers all eight
  research groups and personal matters), `morning-summary-2026-10-30.md` (mostly other lanes and budget),
  `pending-discussion-kelvin.md`, `kelvin-study-list.md`.
- The full dated log `overnight-report-2026-10-29.md`: it mixes ARC entries with the other lanes and with admin and
  people. `reports/dated-log-arc-extract-2026-10-29.md` is the ARC extract made by `tools/extract_log.py`, which
  states how many entries it dropped. Its list of words that mark an entry as being about people (first names
  among them) is kept outside the repository.

From `/srv/agent-data/home/workspaces/mats/work/`: every lane that is not ARC mean estimation (among them
`cm-interp`, `cm-interp-B`, `scale-free-*`, `tiny-pfn*`, `pfn-dedup`, `toy-search`, `worlds`, `modal-udt`,
`steering-welfare`, the forecasting-bot lanes dated 12 November, the site and page builds). Also left out:

- `papers/phaseB-mechanism.md` and the three figures in `papers/` (they belong to that other paper),
  `papers/READINESS.md` (placements for all research groups).
- `bubbles/`, `organize/`, `research-log/`, `not-circuits/`: planning maps and logs built from Kelvin's messages
  and conversations with other people.
- `deep-study/` (a different research agenda), except the two digests kept under
  `reports/unverified-opus-digests-2026-11-09/` and the two wiki-page copies kept under `reports/wiki-copies/`.
  Its wiki copies about people (`arc-mechanistic-estimation-robinson*.md`) and the chat-ingest history page of the
  conjecture (`arc-pseudorandom-code-conjecture-history.md`) were left out.
- `idea-review/gpt6_review.raw`: a session dump; its final message is in `reports/programme-review-2026-11-02/`.

From GitHub `futarchy-fi/inconsistency-search` (clone at commit 647f3be, 6 November 2026): for every ARC lane the
copy under `mats/interp/<lane>/` is a subset of the local work dir (checked file by file: no file differs), so the
local work dir was used. Six files exist only in the GitHub copies of `hardness`, `narrow-deep` and
`narrow-deep-m1` (final answers of reviewer sessions, saved for that repository); they are under
`lanes/<lane>/only-in-github/`. The two review folders of the `arc-noisy` lane that exist only in
`mats/reports/` are under `lanes/arc-noisy/review-from-github/`. `mats/interp/{phaseA,phaseB,tiny-pfn-interp,c6,
scale-free-*}` and the non-ARC reports were left out. Three reports differ between GitHub and the outbox
(`adaptive-regions-2026-11-03.md`, `overnight-report-2026-10-29.md`, `kelvin-study-list.md`); the outbox copies are
newer and were used.

Metaculus dataset: none of the ARC lanes uses it, and a search of the assembled tree for the word finds no file.
