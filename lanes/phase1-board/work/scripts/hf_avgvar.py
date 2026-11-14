"""Read only small columns (mlp_id, mlp_name, avg_variance) from remote parquet files via HTTP range requests.
usage: python -I -B hf_avgvar.py OUT_TSV URL...
Data is untrusted: only parquet metadata and the three named columns are read; nothing in the data is executed."""
import sys, urllib.request
import pyarrow.parquet as pq

class HTTPRangeFile:
    def __init__(self, url):
        req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as r:
            self.url = r.geturl(); self.size = int(r.headers['Content-Length'])
        self.pos = 0; self.closed = False; self.nbytes = 0
    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.pos
    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else (self.pos + off if whence == 1 else self.size + off)
        return self.pos
    def read(self, n=-1):
        if n is None or n < 0: n = self.size - self.pos
        if n == 0 or self.pos >= self.size: return b''
        end = min(self.size, self.pos + n) - 1
        req = urllib.request.Request(self.url, headers={'Range': 'bytes=%d-%d' % (self.pos, end), 'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
        self.pos += len(data); self.nbytes += len(data)
        return data
    def close(self): self.closed = True

out = open(sys.argv[1], 'w')
out.write('file\tmlp_id\tmlp_name\tavg_variance\n')
for url in sys.argv[2:]:
    f = HTTPRangeFile(url)
    pf = pq.ParquetFile(f)
    names = pf.schema_arrow.names
    cols = [c for c in ('mlp_id', 'mlp_name', 'avg_variance') if c in names]
    t = pf.read(columns=cols)
    d = {c: t.column(c).to_pylist() for c in cols}
    for i in range(t.num_rows):
        out.write('%s\t%s\t%s\t%r\n' % (url.rsplit('/', 1)[-1], d.get('mlp_id', [None]*t.num_rows)[i], d.get('mlp_name', [None]*t.num_rows)[i], d['avg_variance'][i]))
    print(url.rsplit('/', 1)[-1], 'rows', t.num_rows, 'bytes read', f.nbytes, 'file size', f.size, 'schema', names, flush=True)
out.close()
