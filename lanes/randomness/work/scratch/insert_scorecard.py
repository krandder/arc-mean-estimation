"""Builds the report's scorecard section from the hashed scorers' outputs (results/score.json, results/rates.json,
results/score_a2.json) and writes results/scorecard_full.md; prints the counts."""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
R = lambda p: os.path.join(ROOT, p)
rows = json.load(open(R('results/score.json')))
rates = json.load(open(R('results/rates.json')))
for pid, text, val, ok, k in rates['rows']:
    rows.append(dict(id=pid, prediction=text, measured=round(val, 3),
                     result=('HOLDS' if ok else 'FAILS') if k == 5 else f'PARTIAL ({k} of 5 nets)'))
a2 = json.load(open(R('results/score_a2.json')))
rows += [r for r in a2['rows'] if r['result'] != 'descriptive']
lines = ['| id | prediction (PREREG wording abbreviated) | measured | result |', '|---|---|---|---|']
for r in rows:
    lines.append(f"| {r['id']} | {r['prediction']} | {r['measured']} | {r['result']} |")
cnt = {}
for r in rows:
    key = r['result'].split(' ')[0]
    cnt[key] = cnt.get(key, 0) + 1
open(R('results/scorecard_full.md'), 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
print(cnt, len(rows))
