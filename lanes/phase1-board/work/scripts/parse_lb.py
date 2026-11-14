# usage: python3 -I parse_lb.py LB_HTML
# Prints rank, participant, adjusted score, final-layer MSE, utilisation, failed, entries, last submission, submission id
import sys, re, html as H
h = open(sys.argv[1], encoding='utf-8', errors='replace').read()
i = h.find('id="leaderboards-div"')
body = h[i:]
rows = body.split('<tr class=')
for r in rows[1:]:
    rank = re.search(r'<td class=""><strong>(\d+)</strong></td>', r)
    names = re.findall(r'class="text-link truncate">([^<]+)</span>', r)
    team = re.search(r'reputation-score truncate">\s*<a href="[^"]*">([^<]+)</a>', r)
    nums = re.findall(r'<td class="text-right "><strong>([0-9.eE+-]+)</strong></td>', r)
    ent = re.findall(r'<td class="text-right ">(\d+)</td>', r)
    t = re.search(r'<time datetime="([^"]+)"', r)
    sub = re.search(r'/submissions/(\d+)', r)
    if not rank: continue
    who = team.group(1).strip() if team else ','.join(names)
    print(rank.group(1), '|', who, '|', ' '.join(nums), '| entries', ent[:1], '|', t.group(1) if t else None, '| sub', sub.group(1) if sub else None)
