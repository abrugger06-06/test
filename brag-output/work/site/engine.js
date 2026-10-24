// Shared 3D stage for the Instagram stills: the same renderer, lights, materials and CAD
// loading as video.html. Set window.STAGE = { W, H } before importing.
import * as THREE from './vendor/three.module.js';
import { RoomEnvironment } from './vendor/RoomEnvironment.js';
import { toCreasedNormals, mergeGeometries } from './vendor/BufferGeometryUtils.js';
export { THREE };

const { W, H } = window.STAGE;
const MESH = new URLSearchParams(location.search).get('mesh') || 'mesh';

// ---------- renderer ----------
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.toneMapping = THREE.NeutralToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;

const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.85;

const key = new THREE.DirectionalLight(0xffffff, 2.2);
key.position.set(-150, 520, 220);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
key.shadow.radius = 7;
key.shadow.blurSamples = 16;
key.shadow.bias = -0.0004;
key.shadow.normalBias = 0.6;
Object.assign(key.shadow.camera, { left: -420, right: 420, top: 420, bottom: -420, near: 50, far: 1400 });
scene.add(key, key.target);
const rim = new THREE.DirectionalLight(0xffffff, 0.9);
rim.position.set(300, 200, -300);
scene.add(rim);
// Cool kick from back-left so black PETG separates from the background.
const kick = new THREE.DirectionalLight(0xd8e6ff, 2.4);
kick.position.set(-280, 170, -320);
scene.add(kick);

const floor = new THREE.Mesh(new THREE.PlaneGeometry(4000, 4000), new THREE.ShadowMaterial({ opacity: 0.13 }));
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

const camera = new THREE.PerspectiveCamera(30, W / H, 5, 5000);

// ---------- CAD ----------
const CASES = {
  c12: { name: '12-Vial-3mL', label: '12-Vial 3 mL' },
  c6:  { name: '6-Vial-3mL',  label: '6-Vial 3 mL' },
  c4:  { name: '4-Vial-10mL', label: '4-Vial 10 mL' },
  c8:  { name: '8-Vial-10mL', label: '8-Vial 10 mL' },
  c7:  { name: '7-Vial-Mixed', label: '7-Vial Mixed' },
};
const ORDER = ['c12', 'c6', 'c4', 'c8', 'c7'];

async function loadPart(entry) {
  const buf = await (await fetch(`${MESH}/${entry.bin}`)).arrayBuffer();
  const pos = new Float32Array(buf, 0, entry.verts * 3);
  const idx = new Uint32Array(buf, entry.verts * 12, entry.tris * 3);
  let g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  g = toCreasedNormals(g, THREE.MathUtils.degToRad(32));
  return g;
}

// Magnets are always silver. The CAD models them as plain discs; the brief says ring magnets,
// so they are drawn as rings with the CAD's outer diameter, thickness and position.
const magnetMat = new THREE.MeshStandardMaterial({ color: 0xD4D7DA, metalness: 1, roughness: 0.16, envMapIntensity: 1.5, emissive: 0xC8CBCE, emissiveIntensity: 0 });
function ringGeometry(mags) {
  const gs = mags.map(m => {
    const r = m.r, ri = r * 0.42, c = Math.min(0.3, r * 0.08), z0 = m.z0, z1 = m.z1;
    const pts = [[ri, z0 + c], [ri + c, z0], [r - c, z0], [r, z0 + c], [r, z1 - c], [r - c, z1], [ri + c, z1], [ri, z1 - c], [ri, z0 + c]]
      .map(([x, y]) => new THREE.Vector2(x, y));
    const g = new THREE.LatheGeometry(pts, 48);
    g.rotateX(Math.PI / 2);
    g.translate(m.x, m.y, 0);
    return toCreasedNormals(g, THREE.MathUtils.degToRad(40));
  });
  return mergeGeometries(gs);
}
// Soft contact shadow under each case.
const contactTex = (() => {
  // 512 px with a little noise, so the soft falloff has no visible steps.
  const N = 512, cv = document.createElement('canvas'); cv.width = cv.height = N;
  const g = cv.getContext('2d'), img = g.createImageData(N, N);
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    const r = Math.hypot(x - N / 2 + 0.5, y - N / 2 + 0.5) / (N / 2);
    const a = r >= 1 ? 0 : (r < 0.62 ? 0.55 - 0.13 * r / 0.62 : 0.42 * (1 - (r - 0.62) / 0.38) ** 1.6);
    const i = (y * N + x) * 4;
    img.data[i + 3] = Math.max(0, Math.min(255, a * 255 + (Math.random() - 0.5) * 3));
  }
  g.putImageData(img, 0, 0);
  return new THREE.CanvasTexture(cv);
})();
const contactMat = new THREE.MeshBasicMaterial({ map: contactTex, transparent: true, depthWrite: false, toneMapped: false });
// Plain 10 mL glass vial with a teal flip cap (no label, no claim).
const glassMat = new THREE.MeshPhysicalMaterial({ color: 0xffffff, metalness: 0, roughness: 0.04, transparent: true, opacity: 0.32, envMapIntensity: 2.2, clearcoat: 1, depthWrite: false, side: THREE.DoubleSide });
const crimpMat = new THREE.MeshStandardMaterial({ color: 0xA9ADB1, metalness: 0.35, roughness: 0.55 });
// Base colour is set so the lit top of the cap renders close to brand teal #74CABF.
const capMat = new THREE.MeshPhysicalMaterial({ color: 0x46857D, roughness: 0.45, clearcoat: 0.15, clearcoatRoughness: 0.5 });
// Plain glass vials (no label, no claim): 10 mL serum vial, or a 3 mL vial for the smaller wells.
// Sizes are scaled from the 10 mL profile; the cap is brand teal.
function vial(x, y, z0, small = false) {
  const s = small ? 0.68 : 1;                 // 3 mL: about 15 mm across for the 16.5 mm wells
  const h = small ? 0.72 : 1;
  const g = new THREE.Group();
  const body = [[0, 0], [9.6, 0], [11, 1.4], [11, 35], [10.4, 37.5], [7.2, 40.5], [6.4, 42], [6.4, 43]].map(([a, b]) => new THREE.Vector2(a * s, b * h));
  const bodyG = new THREE.LatheGeometry(body, 48); bodyG.rotateX(Math.PI / 2);
  const glass = new THREE.Mesh(bodyG, glassMat); glass.renderOrder = 2;
  const crimp = new THREE.Mesh(new THREE.CylinderGeometry(10 * s, 10 * s, 4 * h, 48).rotateX(Math.PI / 2).translate(0, 0, 45 * h), crimpMat);
  const capP = [[0, 47], [9.6, 47], [9.6, 49.6], [9.1, 50.2], [8.4, 50.4], [0, 50.4]].map(([a, b]) => new THREE.Vector2(a * s, 47 * h + (b - 47)));
  const capG = toCreasedNormals(new THREE.LatheGeometry(capP, 48).rotateX(Math.PI / 2), THREE.MathUtils.degToRad(30));
  const cap = new THREE.Mesh(capG, capMat);
  crimp.castShadow = cap.castShadow = true;
  g.add(glass, crimp, cap);
  g.position.set(x, y, z0);
  return g;
}

function plastic(hex) {
  return new THREE.MeshPhysicalMaterial({ color: hex, roughness: 0.4, metalness: 0, clearcoat: 0.3, clearcoatRoughness: 0.4, envMapIntensity: 1.2 });
}

// One instance of a case. CAD space is Z-up; `root` is Y-up world space.
function makeCase(parts, { vials = false } = {}) {
  const { base, baseMag, lid, lidMag } = parts;
  const bb = base.entry, lb = lid.entry;
  const cx = (bb.min[0] + bb.max[0]) / 2, cy = (bb.min[1] + bb.max[1]) / 2;
  const lcx = (lb.min[0] + lb.max[0]) / 2, lcy = (lb.min[1] + lb.max[1]) / 2;
  const baseH = bb.max[2], lidH = lb.max[2];

  const root = new THREE.Group();
  const cad = new THREE.Group();
  cad.rotation.x = -Math.PI / 2;
  root.add(cad);

  const mat = plastic(0x74CABF);
  const mk = (g, m) => { const o = new THREE.Mesh(g, m); o.castShadow = true; o.receiveShadow = true; return o; };

  const baseMesh = mk(base.geo, mat);
  baseMesh.position.set(-cx, -cy, 0);
  const baseMagGrp = new THREE.Group();
  const bm = mk(ringGeometry(MAGS[baseMag.entry.name]), magnetMat);
  bm.position.set(-cx, -cy, 0);
  baseMagGrp.add(bm);
  const vialGrp = new THREE.Group();
  cad.add(baseMesh, baseMagGrp, vialGrp);
  if (vials) {
    bb.pockets.filter(p => p.up && p.d > 20).forEach(p => vialGrp.add(vial(p.x - cx, p.y - cy, p.z)));
    bb.pockets.filter(p => p.up && p.d > 15 && p.d < 18).forEach(p => vialGrp.add(vial(p.x - cx, p.y - cy, p.z, true)));
  }
  const contact = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), contactMat);
  const cs = (bb.max[0] - bb.min[0]) * 1.22;
  contact.scale.set(cs, cs, 1);
  contact.rotation.x = -Math.PI / 2;
  contact.position.y = 0.05;
  contact.userData.noFit = true;
  root.add(contact);

  // Lid is printed upside down (z=0 is the outer top) and mirrored in Y on the plate.
  // Flip 180 deg about X: (x,y,z) -> (x,-y,-z), then shift so the lid's open face sits on the base.
  const lidPivot = new THREE.Group();          // origin: lid centre, half way up the lid
  const lidInner = new THREE.Group();
  lidInner.rotation.x = Math.PI;
  lidInner.position.set(-lcx, lcy, lidH / 2);
  const lidMesh = mk(lid.geo, mat);
  const lidMagGrp = new THREE.Group();
  lidMagGrp.add(mk(ringGeometry(MAGS[lidMag.entry.name]), magnetMat));
  lidInner.add(lidMesh, lidMagGrp);
  lidPivot.add(lidInner);
  cad.add(lidPivot);

  const c = { root, mat, contact, lid: lidPivot, baseH, lidH, dia: bb.max[0] - bb.min[0] };
  c.set = ({ lift = 0, tiltX = 0, tiltZ = 0, back = 0, magOut = 0, vialLift = 0, color } = {}) => {
    vialGrp.position.z = vialLift;
    lidPivot.position.set(0, back, baseH + lidH / 2 + lift);
    lidPivot.rotation.set(tiltX, 0, tiltZ);
    baseMagGrp.position.z = magOut;
    lidMagGrp.position.z = magOut;           // lid print +z points toward its open face
    if (color !== undefined) mat.color.set(color);
  };
  c.set();
  return c;
}

const manifest = await (await fetch(`${MESH}/manifest.json`)).json();
const MAGS = await (await fetch(`${MESH}/magnets.json`)).json();
const geos = {};
await Promise.all(manifest.map(async e => { geos[e.name] = { entry: e, geo: await loadPart(e) }; }));
function partsFor(k) {
  const n = CASES[k].name;
  const find = suffix => geos[Object.keys(geos).find(x => x.startsWith(n + ' ' + suffix))];
  return { base: geos[n + ' base'], lid: geos[n + ' lid'], baseMag: find('base magnets'), lidMag: find('lid magnets') };
}


// ---------- colors ----------
// Fluxcase is printed in black PETG only. Magnets are always silver.
const COL = { black: '#1E1F21' };


const sph = (r, az, el, tgt = [0, 0, 0]) => {
  const a = THREE.MathUtils.degToRad(az), e = THREE.MathUtils.degToRad(el);
  return [tgt[0] + r * Math.cos(e) * Math.sin(a), tgt[1] + r * Math.sin(e), tgt[2] + r * Math.cos(e) * Math.cos(a)];
};
// Frame the camera; shiftX/shiftY move the subject in pixels (positive = right / down).
function look(pos, target, fov = 30, shiftX = 0, shiftY = 0) {
  camera.fov = fov;
  camera.position.set(...pos);
  camera.lookAt(new THREE.Vector3(...target));
  camera.setViewOffset(W, H, -shiftX, -shiftY, W, H);
  camera.updateProjectionMatrix();
}
function render(bgHex) { renderer.setClearColor(bgHex, 1); renderer.render(scene, camera); }
export { scene, camera, renderer, makeCase, partsFor, CASES, ORDER, COL, look, sph, render, magnetMat, key, rim, kick, floor };
