"""Split each CAD magnet part into individual magnets (connected components).
Writes site/mesh/magnets.json: {part name: [{x, y, z0, z1, r}, ...]} in CAD units."""
import json, sys
import numpy as np
D = sys.argv[1] if len(sys.argv) > 1 else 'site/mesh'
out = {}
for e in json.load(open(f'{D}/manifest.json')):
    if 'magnets' not in e['name']:
        continue
    b = open(f"{D}/{e['bin']}", 'rb').read()
    v = np.frombuffer(b[:e['verts'] * 12], '<f4').reshape(-1, 3)
    f = np.frombuffer(b[e['verts'] * 12:], '<u4').reshape(-1, 3)
    parent = np.arange(len(v))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for t in f:
        ra, rb, rc = find(t[0]), find(t[1]), find(t[2])
        parent[rb] = ra; parent[rc] = ra
    roots = np.array([find(i) for i in range(len(v))])
    mags = []
    for r in np.unique(roots):
        p = v[roots == r]
        lo, hi = p.min(0), p.max(0)
        mags.append({'x': round(float((lo[0] + hi[0]) / 2), 3), 'y': round(float((lo[1] + hi[1]) / 2), 3),
                     'z0': round(float(lo[2]), 3), 'z1': round(float(hi[2]), 3), 'r': round(float((hi[0] - lo[0]) / 2), 3)})
    out[e['name']] = mags
    print(e['name'], len(mags), sorted({m['r'] for m in mags}))
json.dump(out, open(f'{D}/magnets.json', 'w'), indent=1)
