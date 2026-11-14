# usage: python3 -I gql_list.py PARTICIPANT ROUND_ID OUT_PREFIX  -> pages through public GraphQL submissionsPage (read-only)
import sys, json, urllib.request
name, rnd, out = sys.argv[1], sys.argv[2], sys.argv[3]
Q = ('query($slug: ID!, $after: String, $filter: SubmissionFilter){ challenge(slug: $slug){ submissionsPage(first: 100, after: $after, filter: $filter){ '
     'nodes{ id createdAt status score scoreSecondary participant{ name } team{ name } round{ id name } } endCursor hasNextPage totalCount } } }')
after, page, nodes = None, 0, []
while True:
    body = json.dumps({'query': Q, 'variables': {'slug': 'arc-white-box-estimation-challenge-2026', 'after': after, 'filter': {'participantName': name, 'roundId': rnd}}}).encode()
    req = urllib.request.Request('https://www.aicrowd.com/graphql', data=body, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    d = json.loads(urllib.request.urlopen(req, timeout=60).read())
    sp = d['data']['challenge']['submissionsPage']
    open('%s_p%d.json' % (out, page), 'w').write(json.dumps(d))
    nodes += sp['nodes']; page += 1
    if not sp['hasNextPage']: break
    after = sp['endCursor']
print(name, 'total', sp['totalCount'], 'fetched', len(nodes))
g = sorted([n for n in nodes if n['status'] == 'GRADED' and n['scoreSecondary'] is not None], key=lambda n: n['createdAt'])
best = sorted(g, key=lambda n: n['score'])[:8]
print('best by adjusted:', [(n['id'], n['createdAt'][:16], '%.3g' % n['score'], '%.3g' % n['scoreSecondary']) for n in best])
from collections import Counter
days = Counter(n['createdAt'][:10] for n in nodes)
print('per-day counts:', sorted(days.items()))
