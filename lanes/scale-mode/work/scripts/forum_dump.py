"""Print a Discourse topic JSON's metadata and each post's cooked text (HTML stripped) and links. usage: forum_dump.py PATH"""
import json, sys, re, html
d = json.load(open(sys.argv[1]))
print('title:', d.get('title'), '| id', d.get('id'), '| created', d.get('created_at'), '| posts_count', d.get('posts_count'),
      '| last_posted', d.get('last_posted_at'), '| views', d.get('views'))
for p in d['post_stream']['posts']:
    c = p.get('cooked', '')
    links = re.findall(r'href="([^"]+)"', c)
    txt = html.unescape(re.sub(r'<[^>]+>', '', c))
    print(f"--- post #{p.get('post_number')} by {p.get('username')} at {p.get('created_at')} (updated {p.get('updated_at')}, version {p.get('version')})")
    print(txt.strip()[:6000])
    print('links:', links)
