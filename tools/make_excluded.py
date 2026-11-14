#!/usr/bin/env python3
"""Write EXCLUDED.md from the collector's exclusions.json. Usage: make_excluded.py EXCLUSIONS_JSON OUT_MD"""
import collections
import json
import sys

d = json.load(open(sys.argv[1]))
agg = collections.defaultdict(lambda: [0, 0])
for lane, v in d["summary"].items():
    for r, (n, b) in v["excluded"].items():
        agg[r][0] += n
        agg[r][1] += b
tr = d["transcripts"]
n_extracted = sum(v["final_messages_extracted"] for v in d["summary"].values())
key_lanes = sorted(l for l, v in d["summary"].items() if any("SSH" in r for r in v["excluded"]))
big_other = [(l, r, s) for l, r, s in d["over_5mb"] if not r.endswith((".pt", ".npz", ".npy", ".pth", ".parquet"))]
n_big_bin = len(d["over_5mb"]) - len(big_other)
tp = []
for lane, v in d["summary"].items():
    for rel, url, rev in v.get("third_party_repos", []):
        tp.append((lane, rel, url, rev))

L = []
A = L.append
A("# What was left out, and why")
A("")
A("Everything here was left out when the repository was assembled on 14 November 2026. Nothing was deleted or changed")
A("at the sources. Each lane's own counts are in `lanes/<lane>/PROVENANCE.md`. The rules are in `tools/collect.py`.")
A("")
A("## Inside the lane work directories")
A("")
A("| reason | files | MB |")
A("|---|---|---|")
for r, (n, b) in sorted(agg.items(), key=lambda kv: -kv[1][1]):
    if n:
        A("| %s | %d | %.1f |" % (r, n, b / 1048576))
A("")
A("Notes on these rows:")
A("")
A("- **Checkpoints and arrays** (`.pt`, `.npz`, `.npy`, `.pth`): model weights, saved truths and sample arrays. %d of them are over 5 MB." % n_big_bin)
A("  They stay on the host General under each lane's original work dir. Code that regenerates them is in the lane.")
A("- **Over 5 MB, not arrays** (%d files):" % len(big_other))
for l, r, s in big_other:
    A("  - `%s/%s` (%.1f MB)" % (l, r, s / 1048576))
A("- **Machine output over 1 MB**: single JSON result files between 1 and 5 MB. The limit for reports, code and")
A("  figures is 5 MB; for machine-written `.json/.jsonl/.log/.out/.err/.txt/.csv/.tsv/.html/.xml` it is 1 MB, so that")
A("  result files in the repository stay small. The lane reports and scorecards that summarise them are included.")
A("- **Session transcripts** (%d files): raw session dumps of reviewer and co-prover models (prompt echo, tool calls," % len(tr))
A("  intermediate output), and one truncated dump that had been saved under an `.md` name. Where the lane had already")
A("  saved the model's final answer as its own file, that file is included. Where it had not, the final message was")
A("  extracted into `<name>.final-message.md` (%d files; these do not exist at the source). The prompts are included." % n_extracted)
A("- **GPU infra state**: the `infra/` directories of %s." % ", ".join("`%s`" % x for x in key_lanes))
A("  Each holds an SSH private key (`infra/state/soup_ed25519`) next to VM bookkeeping files. None of it was copied.")
A("  The key files are still at the sources.")
A("- **Fleet memory recall output**: two `logs/recall1.txt` files holding output of the fleet's memory search, which")
A("  quotes past conversations.")
A("- **Third-party code, downloads and papers**: other people's repositories vendored into lanes, scraped forum and")
A("  leaderboard pages, datasets fetched from the contest, and PDFs of published papers. Copies of third-party files")
A("  found elsewhere in a lane (same SHA-256) were left out too. Upstream addresses and commits:")
seen = set()
for lane, rel, url, rev in tp:
    k = (url, rev)
    if k in seen:
        continue
    seen.add(k)
    if url == "withheld":
        A("  - a contest participant's public repository at commit %s (lane `%s`; no licence file; address in the lane's notes; see `OPEN-DECISIONS.md`)" % (rev, lane))
    else:
        A("  - %s at commit %s (used by `%s`)" % (url, rev, lane))
A("- **Job-queue state markers, caches, symlinks**: `.lock/.pid/.started/.done/.claimed` files, `__pycache__`, links.")
A("")
A("## Secret scan")
A("")
A("`tools/secret_scan.sh` was run on the whole tree before each commit (API-key and token formats of the common")
A("providers, private-key headers, URLs with embedded credentials, `KEY=`/`TOKEN=`/`password=` assignments, key-like")
A("file names). It found nothing in the copied tree. The only secrets met during collection were the SSH private")
A("keys named above, which were excluded with their directories. GPU logs in some lanes list the public IP addresses")
A("of cloud VMs that the lanes created and deleted; those were left in.")
A("")
A("## Left out as not ARC research, personal, or transcript-derived")
A("")
A("From `/srv/agent-data/home/workspaces/mats/outbox/` (about 250 files), only the ARC lane reports, the ARC")
A("literature notes, the 31 October summary, the 2 November synthesis draft and the programme definition were taken.")
A("Left out:")
A("")
A("- Forecasting, Market Pulse, Metaculus access and data-permission notes; MATS proposals, logistics, compute and")
A("  reimbursement notes; call transcripts and people notes.")
A("- Learned search, toy search, POMDP and active-inference search papers and studies; the rounds 4-9 experiment")
A("  papers and audits; the Gemini campaign critique.")
A("- Learned aggregation against exact Bayes (gate reviews, role keys, rich agents, atom and ordering energies), PFN")
A("  worlds, tiny PFN, the binding-plateau paper, World FA, the C6 note.")
A("- The in-context-Bayes mechanism study (noisy-channel phases A and B, `cm-interp-phaseB-*`), scale-free combination")
A("  (`scale-free-*`), the cooperation toys (`lob-*`, `energy-prudentbot`), attention-flow and tangled-architecture")
A("  notes other than the one literature note kept under `reports/literature/`.")
A("- `OPUS-MATS-CONTEXT.md` (an agent's working context file), `research-inventory-2026-11-03.md` (covers all eight")
A("  research groups and personal matters), `morning-summary-2026-10-30.md` (mostly other lanes and budget),")
A("  `pending-discussion-kelvin.md`, `kelvin-study-list.md`.")
A("- The full dated log `overnight-report-2026-10-29.md`: it mixes ARC entries with the other lanes and with admin and")
A("  people. `reports/dated-log-arc-extract-2026-10-29.md` is the ARC extract made by `tools/extract_log.py`, which")
A("  states how many entries it dropped. Its list of words that mark an entry as being about people (first names")
A("  among them) is kept outside the repository.")
A("")
A("From `/srv/agent-data/home/workspaces/mats/work/`: every lane that is not ARC mean estimation (among them")
A("`cm-interp`, `cm-interp-B`, `scale-free-*`, `tiny-pfn*`, `pfn-dedup`, `toy-search`, `worlds`, `modal-udt`,")
A("`steering-welfare`, the forecasting-bot lanes dated 12 November, the site and page builds). Also left out:")
A("")
A("- `papers/phaseB-mechanism.md` and the three figures in `papers/` (they belong to that other paper),")
A("  `papers/READINESS.md` (placements for all research groups).")
A("- `bubbles/`, `organize/`, `research-log/`, `not-circuits/`: planning maps and logs built from Kelvin's messages")
A("  and conversations with other people.")
A("- `deep-study/` (a different research agenda), except the two digests kept under")
A("  `reports/unverified-opus-digests-2026-11-09/` and the two wiki-page copies kept under `reports/wiki-copies/`.")
A("  Its wiki copies about people (`arc-mechanistic-estimation-robinson*.md`) and the chat-ingest history page of the")
A("  conjecture (`arc-pseudorandom-code-conjecture-history.md`) were left out.")
A("- `idea-review/gpt6_review.raw`: a session dump; its final message is in `reports/programme-review-2026-11-02/`.")
A("")
A("From GitHub `futarchy-fi/inconsistency-search` (clone at commit 647f3be, 6 November 2026): for every ARC lane the")
A("copy under `mats/interp/<lane>/` is a subset of the local work dir (checked file by file: no file differs), so the")
A("local work dir was used. Six files exist only in the GitHub copies of `hardness`, `narrow-deep` and")
A("`narrow-deep-m1` (final answers of reviewer sessions, saved for that repository); they are under")
A("`lanes/<lane>/only-in-github/`. The two review folders of the `arc-noisy` lane that exist only in")
A("`mats/reports/` are under `lanes/arc-noisy/review-from-github/`. `mats/interp/{phaseA,phaseB,tiny-pfn-interp,c6,")
A("scale-free-*}` and the non-ARC reports were left out. Three reports differ between GitHub and the outbox")
A("(`adaptive-regions-2026-11-03.md`, `overnight-report-2026-10-29.md`, `kelvin-study-list.md`); the outbox copies are")
A("newer and were used.")
A("")
A("Metaculus dataset: none of the ARC lanes uses it, and a search of the assembled tree for the word finds no file.")
open(sys.argv[2], "w").write("\n".join(L) + "\n")
print("wrote", sys.argv[2], len(L), "lines")
