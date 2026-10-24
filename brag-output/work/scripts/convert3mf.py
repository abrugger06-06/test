"""Convert Fluxcase 3MF files to binary meshes for three.js, and find magnet pockets.

Usage: python3 convert3mf.py OUT_DIR file1.3mf [file2.3mf ...]
Writes OUT_DIR/<name>.bin (float32 xyz positions, then uint32 indices) and
OUT_DIR/manifest.json with counts, bounding boxes (CAD units, Z up) and the
pockets found on each part.
"""
import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

import numpy as np

NS = "{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}"
PNS = "{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}"


def parse_transform(s):
    if not s:
        return np.eye(4)
    v = [float(x) for x in s.split()]
    m = np.eye(4)
    m[:3, :3] = np.array(v[:9]).reshape(3, 3)  # 3MF rows: m00 m01 m02 / m10 ...
    m[3, :3] = v[9:12]
    return m  # row-vector convention: p' = [p 1] @ m


def load_models(z):
    models = {}
    for name in z.namelist():
        if name.lower().endswith(".model"):
            models["/" + name.lstrip("/")] = ET.fromstring(z.read(name))
    return models


def object_index(models):
    idx = {}
    for path, root in models.items():
        for obj in root.iter(NS + "object"):
            idx[(path, obj.get("id"))] = obj
    return idx


def mesh_of(obj, path, idx, xf, out_v, out_f):
    mesh = obj.find(NS + "mesh")
    if mesh is not None:
        vs = np.array(
            [[float(v.get("x")), float(v.get("y")), float(v.get("z"))] for v in mesh.iter(NS + "vertex")]
        )
        fs = np.array(
            [[int(t.get("v1")), int(t.get("v2")), int(t.get("v3"))] for t in mesh.iter(NS + "triangle")]
        )
        vs = np.c_[vs, np.ones(len(vs))] @ xf
        base = sum(len(v) for v in out_v)
        out_v.append(vs[:, :3])
        out_f.append(fs + base)
    comps = obj.find(NS + "components")
    if comps is not None:
        for c in comps.iter(NS + "component"):
            cpath = c.get(PNS + "path") or path
            child = idx[(cpath, c.get("objectid"))]
            mesh_of(child, cpath, idx, parse_transform(c.get("transform")) @ xf, out_v, out_f)


def object_names(z):
    """Bambu/Prusa keep human names in Metadata/model_settings.config."""
    names = {}
    for cfg in ("Metadata/model_settings.config", "Metadata/Slic3r_PE_model.config"):
        if cfg in z.namelist():
            root = ET.fromstring(z.read(cfg))
            for obj in root.iter("object"):
                for md in obj.iter("metadata"):
                    if md.get("key") == "name":
                        names[obj.get("id")] = md.get("value")
                        break
    return names


def find_pockets(v, f):
    """Flat round faces (pocket floors) 5 to 25 mm across, with their centre."""
    tri = v[f]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    area2 = np.linalg.norm(n, axis=1)
    nz = n[:, 2] / np.maximum(area2, 1e-12)
    flat = np.abs(nz) > 0.999
    # group flat faces by z level and sign, then by vertex connectivity
    key = np.round(tri[:, 0, 2], 2) * np.sign(nz)
    pockets = []
    sel = np.where(flat)[0]
    from collections import defaultdict

    groups = defaultdict(list)
    for i in sel:
        groups[key[i]].append(i)
    for k, ids in groups.items():
        ids = np.array(ids)
        # union-find over shared rounded vertex positions
        parent = list(range(len(ids)))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        owner = {}
        for j, t in enumerate(ids):
            for p in tri[t]:
                pk = (round(p[0], 3), round(p[1], 3))
                if pk in owner:
                    ra, rb = find(owner[pk]), find(j)
                    if ra != rb:
                        parent[ra] = rb
                else:
                    owner[pk] = j
        comp = defaultdict(list)
        for j in range(len(ids)):
            comp[find(j)].append(ids[j])
        for c in comp.values():
            pts = tri[c].reshape(-1, 3)
            lo, hi = pts.min(0), pts.max(0)
            dx, dy = hi[0] - lo[0], hi[1] - lo[1]
            if not (5 < dx < 25 and abs(dx - dy) < 0.3):
                continue
            a = area2[c].sum() / 2
            disc = np.pi * (dx / 2) ** 2
            if a < 0.8 * disc:  # an annulus, not a floor
                continue
            pockets.append(
                {
                    "d": round(float(dx), 2),
                    "x": round(float((lo[0] + hi[0]) / 2), 3),
                    "y": round(float((lo[1] + hi[1]) / 2), 3),
                    "z": round(float(lo[2]), 3),
                    "up": bool(k > 0),
                }
            )
    return pockets


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    manifest = []
    for src in sys.argv[2:]:
        z = zipfile.ZipFile(src)
        models = load_models(z)
        idx = object_index(models)
        names = object_names(z)
        main_path = next(p for p in models if p.lower() == "/3d/3dmodel.model")
        root = models[main_path]
        for item in root.iter(NS + "item"):
            oid = item.get("objectid")
            ipath = item.get(PNS + "path") or main_path
            obj = idx[(ipath, oid)]
            vs, fs = [], []
            mesh_of(obj, ipath, idx, parse_transform(item.get("transform")), vs, fs)
            v = np.concatenate(vs)
            f = np.concatenate(fs)
            label = names.get(oid) or obj.get("name") or f"object_{oid}"
            stem = re.sub(r"[^a-z0-9]+", "-", (os.path.splitext(os.path.basename(src))[0] + "-" + label).lower()).strip("-")
            lo, hi = v.min(0), v.max(0)
            with open(os.path.join(out, stem + ".bin"), "wb") as fh:
                fh.write(v.astype("<f4").tobytes())
                fh.write(f.astype("<u4").tobytes())
            entry = {
                "file": os.path.basename(src),
                "name": label,
                "bin": stem + ".bin",
                "verts": int(len(v)),
                "tris": int(len(f)),
                "min": [round(float(x), 3) for x in lo],
                "max": [round(float(x), 3) for x in hi],
                "size": [round(float(x), 2) for x in hi - lo],
                "pockets": find_pockets(v, f),
            }
            manifest.append(entry)
            pk = {}
            for p in entry["pockets"]:
                pk[p["d"]] = pk.get(p["d"], 0) + 1
            print(f"{stem}: {len(f)} tris, size {entry['size']}, flat round floors {dict(sorted(pk.items()))}")
    with open(os.path.join(out, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=1)


if __name__ == "__main__":
    main()
