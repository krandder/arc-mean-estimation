"""Print the first rows of an AIcrowd leaderboard HTML page (untrusted data). usage: lb_parse.py PATH [nrows]"""
import sys, re, html
from html.parser import HTMLParser
s = open(sys.argv[1], encoding='utf-8', errors='replace').read()
k = int(sys.argv[2]) if len(sys.argv) > 2 else 8
class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.rows = []; self.cur = None; self.cell = None
    def handle_starttag(self, t, a):
        if t == 'tr': self.cur = []
        elif t in ('td', 'th') and self.cur is not None: self.cell = []
    def handle_endtag(self, t):
        if t in ('td', 'th') and self.cur is not None and self.cell is not None:
            self.cur.append(' '.join(''.join(self.cell).split())); self.cell = None
        elif t == 'tr' and self.cur is not None:
            if self.cur: self.rows.append(self.cur)
            self.cur = None
    def handle_data(self, d):
        if self.cell is not None: self.cell.append(d)
p = P(); p.feed(s)
for r in p.rows[:k]:
    print(' | '.join(r)[:300])
