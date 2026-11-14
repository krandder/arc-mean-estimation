# usage: python3 -I parse_sub.py SUB_HTML...
# Summarises per-MLP telemetry and public scores embedded in an AIcrowd submission page.
import sys, html, json, statistics as st
def arr(h, key):
    j = h.find('"%s":[' % key)
    if j < 0: return None
    j += len('"%s":' % key)
    depth, k = 0, j
    while k < len(h):
        if h[k] == '[': depth += 1
        elif h[k] == ']':
            depth -= 1
            if depth == 0: break
        k += 1
    return json.loads(h[j:k+1])
def obj(h, key):
    j = h.find('"%s":{' % key)
    if j < 0: return None
    j += len('"%s":' % key)
    depth, k = 0, j
    while k < len(h):
        if h[k] == '{': depth += 1
        elif h[k] == '}':
            depth -= 1
            if depth == 0: break
        k += 1
    return json.loads(h[j:k+1])
for f in sys.argv[1:]:
    h = html.unescape(open(f, encoding='utf-8', errors='replace').read())
    sub = obj(h, 'submission')
    rows = arr(h, 'per_mlp') or []
    pub = arr(h, 'public_scores') or []
    agg = obj(h, 'aggregates')
    env = obj(h, 'runtime_environment')
    ev_start = h[h.find('"started_at":"')+14:h.find('"started_at":"')+34]
    print('=====', f, 'created', sub.get('createdAt') if sub else None, 'participant', (sub or {}).get('participant',{}).get('name'), 'team', (sub or {}).get('team'))
    print('eval started_at', ev_start, '| env', env)
    tel = [r['telemetry'] for r in rows if r.get('telemetry')]
    def s(key):
        v = [t[key] for t in tel if t.get(key) is not None]
        return (min(v), st.mean(v), max(v)) if v else None
    for key in ['flops_used','effective_compute','residual_wall_time_s','flopscope_backend_time_s','flopscope_server_overhead_wall_s','participant_predict_wall_s']:
        print('  %-36s min %.4g mean %.4g max %.4g' % ((key,)+s(key)) if s(key) else key)
    print('  n rows', len(rows), 'n public scores', len(pub))
    if tel:
        fu = st.mean([t['flops_used'] for t in tel]); ec = st.mean([t['effective_compute'] for t in tel])
        print('  metered share of effective compute: %.4f' % (fu/ec))
    if agg: print('  aggregates.public:', json.dumps(agg.get('public'))[:900])
    if pub:
        m = [p['scores']['final_layer_mse'] for p in pub]
        print('  public final_layer_mse: min %.3g median %.3g max %.3g mean %.4g' % (min(m), st.median(m), max(m), st.mean(m)))
