# Open decisions: do not publish or share past these

This repository is private. Three decisions about third parties are unresolved. Until Kelvin decides them, nothing
from the files listed below should be published, posted, sent to ARC or to the contest forum, or copied into a
public repository.

Source of the decisions: the header of `reports/paper-draft-arc-negative/arc-negative.md` (draft v2, 3 November 2026),
which lists decisions D1 to D12 and says "nothing below is decided; the draft takes the reversible default shown".
Checked on 14 November 2026 when this repository was assembled: no record of a decision on D3, D11 or D12 was found
in the paper draft, in `work/papers/READINESS.md`, or in the mats research log. That check covered those files only.

## D3. The Phase-1 leaderboard account: name, anonymise, or drop

Quoted from the draft header:

> D3. Phase-1 board account (now Appendix D, anonymised): name, anonymise, or drop until the private re-evaluation
> (~15 Nov). The organisers say public-set fitting is allowed under the rules, so the text must not read as an accusation.

What it is about: the lane `lanes/phase1-board/` is a read-only study of the public contest board. Its finding is that
the top public entry's score is likely explained by fitting to the 50 public networks, using the per-network errors
that every submission page publishes. The lane marks this VERIFIED for earlier runs of the same entrant (5-6 August)
and INFERRED for the final run. The organisers state that such fitting "is allowed, but the resulting performance is
unlikely to generalize to the post-Phase 1 private re-evaluation". So this is an account of a score, not a charge of
rule-breaking, and it has not been shown to the entrant.

State: unresolved. The draft's default is "moved to Appendix D, anonymised, marked for deletion". The contest's
private re-evaluation on fresh networks (expected about 15 November 2026) would test the account; this repository
does not contain its outcome.

## D11. Drop the leaderboard account from the paper whatever D3 decides

> D11. Referee 2 recommends dropping the Phase-1 board account from the paper whatever D3 decides. Default here: moved
> to Appendix D, anonymised, marked for deletion.

State: unresolved. Appendix D is still in the draft in this repository.

## D12. The scale-mode claim: name, anonymise, or notify its author

> D12. Section 3.3 evaluates an identifiable participant's public claim (forum topic 18298) and finds it fails our
> registered escape criteria: name, anonymise, or notify the author before circulating. Default here: topic number
> kept, no name, neutral pronouns.

What it is about: the lane `lanes/scale-mode/` ran a contest participant's public code unchanged and tested the
participant's public claim against criteria registered in advance. The claim did not meet them at the Phase-1 shape.
The author has not been told and has had no chance to reply.

State: unresolved.

## What in this repository is affected

The top-level files written for this repository (`README.md`, `NEGATIVE-RESULTS.md`, this file, `EXCLUDED.md`, the
`PROVENANCE.md` files) do not name any contest participant. The collected lane files are copies of the originals and
were not anonymised. These files contain a participant's handle or name:

- `lanes/phase1-board/work/FINDINGS.md` (handles of the top board entrants)
- `lanes/phase1-board/work/*_runs.tsv` (the file name itself is the entrant's handle; contents are public run scores)
- `lanes/scale-mode/report/scale-mode-2026-11-02.md`
- `lanes/scale-mode/work/scale-mode.md`
- `lanes/scale-mode/work/HANDOFF.md`
- `lanes/scale-mode/work/notes/AUDIT.md`
- `lanes/scale-mode/work/notes/SOURCES.md`
- `lanes/arc-update/work/notes/ARC_SOURCES.md`
- `reports/dated-log-arc-extract-2026-10-29.md`

This list is the output of a case-insensitive search of the whole tree for the #1 entrant's handle and the scale-mode
author's name on 14 November 2026 (8 files, plus the one file name). Handles of other board entrants appear in
`FINDINGS.md`, `lanes/scale-mode/work/notes/SOURCES.md` and `lanes/arc-update/work/notes/ARC_SOURCES.md` (a search
for two of the other handles; the remaining ones were not searched). Many more files mention the forum topic number
18298 without a name.

Also affected, without names: `reports/paper-draft-arc-negative/arc-negative.md` section 3.3 and Appendix D,
`reports/synthesis-draft-2026-11-02.md` (its conflict C10 is the board entry), and the rows for `scale-mode` and
`phase1-board` in `README.md` and `NEGATIVE-RESULTS.md`.

The participant's code itself was not copied into this repository (it has no licence file); see
`lanes/scale-mode/PROVENANCE.md`.

## The other decisions in the draft header

D1, D2 and D4 to D10 (venue, authorship and credit for the model-written proofs, framing, whether to show ARC a copy
first, which question the paper answers, which proofs need a human check, further runs) are also open. They are listed
in the draft header and are not repeated here. One of them bears on every "proved" label in `README.md`: per the
draft, "no proof has been checked by a human" (D9).
