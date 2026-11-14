#!/bin/bash
cd /home/agent/workspaces/mats/work/future-aware
echo "r4 start $(date -u +%H:%M:%SZ)" >> coprover/status.txt
timeout 3600 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"xhigh"' -C /home/agent/workspaces/mats/work/future-aware "You are an independent co-prover (mathematician). Read coprover/STATEMENT_r4.md in this directory and nothing else of this lane except coprover/astra_r2_answer.md (your earlier mean-field proof). Answer Q1-Q3 with full proofs where you claim PROVEN, explicit hypotheses otherwise, counterexamples where false. Be rigorous and adversarial. Write your whole answer as your final message (markdown), short summary first. You cannot write files." < /dev/null >> coprover/astra_r4.raw 2>&1
echo "r4 exit $? $(date -u +%H:%M:%SZ)" >> coprover/status.txt
