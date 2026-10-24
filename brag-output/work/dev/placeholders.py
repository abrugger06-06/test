"""DEV ONLY: rough stand-in cases so the pipeline can be built before the real CAD arrives.
Never used for the shipped video."""
import math, sys, trimesh
OUT = sys.argv[1]
def cyl(r, h, z0, x=0, y=0, n=96):
    c = trimesh.creation.cylinder(radius=r, height=h, sections=n); c.apply_translation([x, y, z0 + h / 2]); return c
def ring(n, R, a0=0): return [(R * math.cos(a0 + 2 * math.pi * i / n), R * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]
cases = {  # name: OD, H, wells [(r, x, y)], magnets [(d, x, y)]
 "12-vial-3ml": (91, 34.5, [(8.2, x, y) for x, y in ring(12, 31)], [(6.1, x, y) for x, y in ring(13, 41.5, .2)] + [(10.4, 0, 0)]),
 "6-vial-3ml": (62, 34.5, [(8.2, x, y) for x, y in ring(6, 17)], [(6.1, x, y) for x, y in ring(6, 27, .52)] + [(6.1, 0, 0)]),
 "4-vial-10ml": (64, 48.5, [(11.6, x, y) for x, y in ring(4, 15.5, .785)], [(6.1, x, y) for x, y in ring(4, 27.5)] + [(6.1, 0, 0)]),
 "8-vial-10ml": (95, 48.4, [(11.6, x, y) for x, y in ring(8, 31)], [(10.4, x, y) for x, y in ring(8, 42.3, .39)] + [(10.4, 0, 0)]),
 "7-vial-mixed": (77, 48.5, [(11.6, 0, 0)] + [(8.2, x, y) for x, y in ring(6, 24)], [(10.4, x, y) for x, y in ring(6, 33.5, .52)]),
}
bases, lids = trimesh.Scene(), trimesh.Scene()
for i, (k, (od, h, wells, mags)) in enumerate(cases.items()):
    b = cyl(od / 2, h, 0)
    cut = [cyl(r, h, 4, x, y, 64) for r, x, y in wells] + [cyl(d / 2, 6.4, h - 3.2, x, y, 40) for d, x, y in mags]
    b = b.difference(trimesh.boolean.union(cut))
    b.apply_translation([i * 110, 0, 0]); bases.add_geometry(b, node_name=k + " base")
    l = cyl(od / 2, 11, 0)
    lcut = [cyl(od / 2 - 2.5, 11, 2.5)] if False else []
    lcut += [cyl(d / 2, 6.4, 11 - 3.2, x, -y, 40) for d, x, y in mags]  # flipped in print orientation
    l = l.difference(trimesh.boolean.union(lcut))
    l.apply_translation([i * 110, 150, 0]); lids.add_geometry(l, node_name=k + " lid")
bases.export(OUT + "/dev_bases.3mf"); lids.export(OUT + "/dev_lids.3mf")
