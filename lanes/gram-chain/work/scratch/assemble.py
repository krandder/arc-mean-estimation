"""Assemble the lane's outbox document from the summary (already in the outbox file) and the body parts in notes/.
Fills placeholders from a small dict; anything still missing stays visible as {{...}}."""
import sys, re
OUT = '/home/agent/workspaces/mats/outbox/gram-chain-2026-11-01.md'
N = '/home/agent/workspaces/mats/work/gram-chain/notes/'
import json
fill = json.load(open(N + "fills.json"))
for arg in sys.argv[1:]:
    k, v = arg.split('=', 1)
    fill[k] = v
s = open(OUT).read()
head = open(N + 'head_template.md').read()
body = ''.join(open(N + f).read().rstrip() + '\n\n' for f in ('body1.md', 'body2.md', 'body3.md', 'body4.md', 'body5.md', 'body6.md',
                                                             'sec11_files.md'))
doc = head.rstrip() + '\n\n' + body
for k, v in fill.items():
    doc = doc.replace('{{' + k + '}}', v)
open(OUT, 'w').write(doc)
left = sorted(set(re.findall(r'\{\{[A-Z0-9_]+\}\}', doc)))
print('written; placeholders left:', left, '; words:', len(doc.split()))
