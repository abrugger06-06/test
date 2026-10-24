// Lifestyle sets for the v3 film: real-world surfaces and props built in code (units: mm).
// Each set is a THREE.Group with a top surface at y = 0, a back wall and a few props. Textures are
// procedural canvases, so there is nothing to license and nothing to download.
import * as THREE from './vendor/three.module.js';
import { RoundedBoxGeometry } from './vendor/pp/RoundedBoxGeometry.js';

const rnd = (() => { let s = 7; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();

function canvasTex(w, h, draw, repeat = [1, 1]) {
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h;
  draw(cv.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(...repeat);
  t.anisotropy = 16;
  return t;
}
function noise(g, w, h, amt, alpha = 0.06) {
  for (let i = 0; i < amt; i++) {
    g.fillStyle = rnd() < 0.5 ? `rgba(0,0,0,${alpha})` : `rgba(255,255,255,${alpha})`;
    g.fillRect(rnd() * w, rnd() * h, 1 + rnd() * 2, 1 + rnd() * 2);
  }
}

// Oak / walnut planks: long grain lines with gentle waves and a few knots.
function woodTex(base, dark, light, planks = 4) {
  return canvasTex(2048, 1024, (g, w, h) => {
    const ph = h / planks;
    for (let p = 0; p < planks; p++) {
      g.fillStyle = base; g.fillRect(0, p * ph, w, ph);
      const tint = (rnd() - 0.5) * 0.12;
      g.fillStyle = tint > 0 ? `rgba(255,240,220,${tint})` : `rgba(40,20,0,${-tint})`;
      g.fillRect(0, p * ph, w, ph);
      for (let i = 0; i < 90; i++) {
        const y0 = p * ph + rnd() * ph, amp = 2 + rnd() * 9, f = 0.002 + rnd() * 0.006, ph0 = rnd() * 6;
        g.strokeStyle = rnd() < 0.7 ? dark : light;
        g.globalAlpha = 0.08 + rnd() * 0.22; g.lineWidth = 0.6 + rnd() * 2.2;
        g.beginPath();
        for (let x = 0; x <= w; x += 16) g.lineTo(x, y0 + Math.sin(x * f + ph0) * amp);
        g.stroke();
      }
      g.globalAlpha = 1;
      g.fillStyle = 'rgba(30,15,5,0.35)'; g.fillRect(0, p * ph, w, 2);   // plank seam
    }
    noise(g, w, h, 40000, 0.05);
  }, [2, 2]);
}
// Pale quartz with soft grey veins.
function marbleTex() {
  return canvasTex(2048, 1024, (g, w, h) => {
    g.fillStyle = '#cfccc5'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 26; i++) {
      let x = rnd() * w, y = rnd() * h, a = rnd() * Math.PI * 2;
      g.strokeStyle = `rgba(105,105,112,${0.12 + rnd() * 0.22})`; g.lineWidth = 0.8 + rnd() * 3;
      g.beginPath(); g.moveTo(x, y);
      for (let k = 0; k < 60; k++) { a += (rnd() - 0.5) * 0.5; x += Math.cos(a) * 18; y += Math.sin(a) * 18; g.lineTo(x, y); }
      g.stroke();
    }
    noise(g, w, h, 30000, 0.035);
  });
}
// White subway tile with soft grout.
function tileTex() {
  return canvasTex(1024, 1024, (g, w, h) => {
    g.fillStyle = '#cfcfca'; g.fillRect(0, 0, w, h);
    const tw = 128, th = 64;
    for (let r = 0; r < h / th; r++) for (let c = -1; c < w / tw + 1; c++) {
      const x = c * tw + (r % 2 ? tw / 2 : 0), y = r * th;
      const gr = g.createLinearGradient(0, y, 0, y + th);
      gr.addColorStop(0, '#fbfbf9'); gr.addColorStop(1, '#eeeeea');
      g.fillStyle = gr; g.fillRect(x + 3, y + 3, tw - 6, th - 6);
    }
    noise(g, w, h, 10000, 0.03);
  }, [3, 2]);
}
// Plaster wall with a soft tone change.
function plasterTex(c0, c1) {
  return canvasTex(1024, 1024, (g, w, h) => {
    const gr = g.createLinearGradient(0, 0, w, h); gr.addColorStop(0, c0); gr.addColorStop(1, c1);
    g.fillStyle = gr; g.fillRect(0, 0, w, h);
    noise(g, w, h, 60000, 0.025);
  });
}
// Linen weave for the travel set.
function linenTex(c) {
  return canvasTex(512, 512, (g, w, h) => {
    g.fillStyle = c; g.fillRect(0, 0, w, h);
    for (let i = 0; i < w; i += 8) { g.fillStyle = `rgba(0,0,0,${0.02 + rnd() * 0.03})`; g.fillRect(i, 0, 3, h); }
    for (let j = 0; j < h; j += 8) { g.fillStyle = `rgba(255,255,255,${0.02 + rnd() * 0.03})`; g.fillRect(0, j, w, 3); }
    noise(g, w, h, 8000, 0.04);
  }, [2, 2]);
}

const std = (o) => new THREE.MeshStandardMaterial(o);
function mesh(geo, mat, { cast = true, receive = true } = {}) { const m = new THREE.Mesh(geo, mat); m.castShadow = cast; m.receiveShadow = receive; return m; }
function surface(tex, w = 3200, d = 2400, rough = 0.6) {
  const top = mesh(new THREE.BoxGeometry(w, 30, d), std({ map: tex, roughness: rough }), { cast: false });
  top.position.y = -15;
  return top;
}
function wall(tex, w = 5000, h = 2400, z = -520, rough = 0.95) {
  const m = mesh(new THREE.PlaneGeometry(w, h), std({ map: tex, roughness: rough }), { cast: false });
  m.position.set(0, h / 2 - 40, z);
  return m;
}

// ---------- props ----------
function mug(color = '#ece6dc') {
  const g = new THREE.Group();
  const body = mesh(new THREE.LatheGeometry([[0, 0], [40, 0], [44, 4], [44, 96], [41, 98], [39, 92], [38, 6], [0, 6]].map(p => new THREE.Vector2(...p)), 48), new THREE.MeshPhysicalMaterial({ color, roughness: 0.25, clearcoat: 1, clearcoatRoughness: 0.15 }));
  const coffee = mesh(new THREE.CircleGeometry(38, 40), std({ color: '#3b2416', roughness: 0.15 }), { cast: false });
  coffee.rotation.x = -Math.PI / 2; coffee.position.y = 84;
  const handle = mesh(new THREE.TorusGeometry(24, 6, 16, 32, Math.PI * 1.2), std({ color, roughness: 0.35 }));
  handle.position.set(46, 52, 0); handle.rotation.z = -Math.PI * 0.6;
  g.add(body, coffee, handle);
  return g;
}
function notebook(cover = '#2f3a36') {
  const g = new THREE.Group();
  const pages = mesh(new THREE.BoxGeometry(150, 12, 210), std({ color: '#f4f1e8', roughness: 0.9 }));
  pages.position.y = 7;
  const c1 = mesh(new THREE.BoxGeometry(154, 1.5, 214), std({ color: cover, roughness: 0.7 }));
  c1.position.y = 13.5;
  const c0 = c1.clone(); c0.position.y = 0.75;
  const band = mesh(new THREE.BoxGeometry(6, 15, 216), std({ color: '#7a2e24', roughness: 0.6 }));
  band.position.set(50, 7, 0);
  g.add(pages, c0, c1, band);
  return g;
}
function pen() {
  const m = mesh(new THREE.CylinderGeometry(4.5, 4.5, 140, 20).rotateZ(Math.PI / 2), std({ color: '#1b1c1e', roughness: 0.3, metalness: 0.2 }));
  m.position.y = 4.5;
  return m;
}
function plant() {
  const g = new THREE.Group();
  const pot = mesh(new THREE.LatheGeometry([[0, 0], [50, 0], [62, 120], [58, 120], [46, 6], [0, 6]].map(p => new THREE.Vector2(...p)), 40), std({ color: '#c46a45', roughness: 0.85 }));
  const soil = mesh(new THREE.CircleGeometry(58, 32), std({ color: '#3a2a1e', roughness: 1 }), { cast: false });
  soil.rotation.x = -Math.PI / 2; soil.position.y = 112;
  g.add(pot, soil);
  const leafMat = std({ color: '#4f7a47', roughness: 0.55, side: THREE.DoubleSide });
  for (let i = 0; i < 16; i++) {
    const leaf = mesh(new THREE.SphereGeometry(1, 16, 10).scale(14, 4, 46), leafMat);
    const a = i / 16 * Math.PI * 2 + rnd() * 0.4, r = 10 + rnd() * 22, up = 0.35 + rnd() * 0.6;
    leaf.position.set(Math.cos(a) * r, 140 + rnd() * 70, Math.sin(a) * r);
    leaf.rotation.set(-up, -a + Math.PI / 2, 0);
    g.add(leaf);
  }
  return g;
}
function laptop() {
  const g = new THREE.Group();
  const alu = std({ color: '#9ea2a6', roughness: 0.35, metalness: 0.7 });
  const base = mesh(new RoundedBoxGeometry(320, 8, 220, 2, 3), alu); base.position.y = 4;
  const kb = mesh(new THREE.BoxGeometry(280, 1, 110), std({ map: canvasTex(560, 220, (g, w, h) => { g.fillStyle = '#3a3d41'; g.fillRect(0, 0, w, h); for (let r = 0; r < 5; r++) for (let c = 0; c < 14; c++) { g.fillStyle = '#1d1f22'; g.fillRect(c * 40 + 3, r * 44 + 3, 34, 38); } }), roughness: 0.7 }), { cast: false }); kb.position.set(0, 8.6, -30);
  const lid = new THREE.Group(); lid.position.set(0, 8, -110); lid.rotation.x = -0.32;
  const shell = mesh(new THREE.BoxGeometry(320, 210, 6), alu); shell.position.set(0, 105, -3);
  const screen = mesh(new THREE.PlaneGeometry(296, 186), std({ color: '#1a2630', roughness: 0.2, emissive: '#22343f', emissiveIntensity: 0.6 }), { cast: false });
  screen.position.set(0, 105, 0.2);
  lid.add(shell, screen);
  g.add(base, kb, lid);
  return g;
}
function board() {
  const m = mesh(new THREE.BoxGeometry(380, 18, 240), std({ map: woodTex('#c79a63', '#8a5a2b', '#e5c38f', 2), roughness: 0.55 }));
  m.position.y = 9;
  return m;
}
function jar() {
  const g = new THREE.Group();
  const glass = mesh(new THREE.CylinderGeometry(55, 55, 150, 40, 1, true), std({ color: '#e8f1ee', roughness: 0.05, transparent: true, opacity: 0.25 }), { cast: false });
  glass.position.y = 75;
  const lidM = mesh(new THREE.CylinderGeometry(57, 57, 22, 40), std({ color: '#b98c5a', roughness: 0.5 }));
  lidM.position.y = 161;
  const fill = mesh(new THREE.CylinderGeometry(50, 50, 95, 32), std({ color: '#d9c49a', roughness: 0.9 }));
  fill.position.y = 50;
  g.add(fill, glass, lidM);
  return g;
}
function lamp() {
  const g = new THREE.Group();
  const base = mesh(new THREE.LatheGeometry([[0, 0], [70, 0], [72, 10], [30, 30], [14, 200], [0, 200]].map(p => new THREE.Vector2(...p)), 40), std({ color: '#d9cfbf', roughness: 0.4 }));
  const shade = mesh(new THREE.CylinderGeometry(80, 120, 150, 40, 1, true), std({ map: linenTex('#f0e3c8'), roughness: 0.95, emissive: '#ffcf8a', emissiveIntensity: 0.9, side: THREE.DoubleSide }), { cast: false });
  shade.position.y = 260;
  const bulb = new THREE.PointLight(0xffc27a, 400000, 0, 2); bulb.position.y = 250;
  g.add(base, shade, bulb);
  g.userData.light = bulb; g.userData.shade = shade;
  return g;
}
function books() {
  const g = new THREE.Group(); let y = 0;
  [['#2f4b5a', 230, 32], ['#b5835a', 210, 26], ['#e1dccf', 200, 22]].forEach(([c, w, h], i) => {
    const b = mesh(new THREE.BoxGeometry(w, h, 150), std({ color: c, roughness: 0.75 }));
    b.position.set((i - 1) * 6, y + h / 2, 0); b.rotation.y = (i - 1) * 0.08; y += h; g.add(b);
  });
  return g;
}
function passport() {
  const cover = canvasTex(256, 360, (g, w, h) => {
    g.fillStyle = '#1f2c45'; g.fillRect(0, 0, w, h); noise(g, w, h, 6000, 0.05);
    g.strokeStyle = 'rgba(214,180,110,0.85)'; g.lineWidth = 5;
    g.beginPath(); g.arc(w / 2, h * 0.45, 52, 0, Math.PI * 2); g.stroke();
    g.beginPath(); g.arc(w / 2, h * 0.45, 34, 0, Math.PI * 2); g.stroke();
    g.fillStyle = 'rgba(214,180,110,0.85)'; g.fillRect(w * 0.3, h * 0.72, w * 0.4, 6); g.fillRect(w * 0.36, h * 0.17, w * 0.28, 6);
  });
  const m = mesh(new RoundedBoxGeometry(88, 6, 125, 2, 2.5), [0, 0, 1, 0, 0, 0].map(i => i ? std({ map: cover, roughness: 0.65 }) : std({ color: '#1a253b', roughness: 0.7 })));
  m.position.y = 3;
  return m;
}
function pouch() {
  const g = new THREE.Group();
  const bodyM = std({ map: linenTex('#a8916f'), roughness: 0.95 });
  const body = mesh(new RoundedBoxGeometry(300, 70, 170, 4, 22), bodyM);
  body.position.y = 35;
  const zipM = std({ color: '#2e2a24', roughness: 0.45, metalness: 0.5 });
  const zip = mesh(new THREE.BoxGeometry(280, 4, 8), zipM); zip.position.set(0, 71, 0);
  const pull = mesh(new RoundedBoxGeometry(10, 4, 34, 2, 1.5), zipM); pull.position.set(150, 70, 14); pull.rotation.y = 0.3;
  g.add(body, zip, pull);
  return g;
}
function towel() {
  const g = new THREE.Group();
  const m1 = mesh(new RoundedBoxGeometry(520, 22, 360, 4, 10), std({ map: linenTex('#e7dfcf'), roughness: 1 }));
  m1.position.y = 11;
  const m2 = mesh(new RoundedBoxGeometry(500, 20, 340, 4, 9), std({ map: linenTex('#ded5c3'), roughness: 1 }));
  m2.position.set(6, 31, -4); m2.rotation.y = 0.03;
  g.add(m1, m2);
  return g;
}

// A window frame that never appears on camera: it sits between the sun (key light) and the set, so
// the table gets the soft cross-bar shadows of a real window.
export function windowFrame(w = 900, h = 700, bar = 26) {
  const g = new THREE.Group();
  const m = new THREE.MeshBasicMaterial({ color: 0x000000, colorWrite: false });
  const add = (x, y, bw, bh) => { const b = new THREE.Mesh(new THREE.BoxGeometry(bw, bh, 20), m); b.position.set(x, y, 0); b.castShadow = true; g.add(b); };
  add(0, h / 2, w, bar); add(0, -h / 2, w, bar); add(-w / 2, 0, bar, h); add(w / 2, 0, bar, h);
  add(0, 0, bar * 0.8, h); add(0, 0, w, bar * 0.8);
  return g;
}

// ---------- sets ----------
export function buildSets(scene) {
  const S = {};
  const mk = (name, build) => { const g = new THREE.Group(); g.name = name; build(g); g.visible = false; scene.add(g); S[name] = g; };

  // Morning desk: oak, warm plaster wall, coffee, notebook, plant, laptop.
  mk('desk', g => {
    g.add(surface(woodTex('#a98563', '#6e4e33', '#cdb08c')), wall(plasterTex('#efe6da', '#e2d5c4')));
    const m = mug(); m.position.set(-330, 0, -90); g.add(m);
    const n = notebook(); n.position.set(300, 0, -40); n.rotation.y = 0.35; g.add(n);
    const p = pen(); p.position.set(290, 15, 40); p.rotation.y = 0.5; g.add(p);
    const pl = plant(); pl.position.set(-560, 0, -360); g.add(pl);
    const l = laptop(); l.position.set(470, 0, -330); l.rotation.y = -0.4; g.add(l);
  });
  // Kitchen: quartz counter, subway tile, cutting board, jar, herb pot.
  mk('kitchen', g => {
    g.add(surface(marbleTex(), 3200, 2400, 0.5), wall(tileTex(), 5000, 2400, -500, 0.4));
    const b = board(); b.position.set(-520, 0, -330); b.rotation.y = 0.15; g.add(b);
    const j = jar(); j.position.set(420, 0, -330); g.add(j);
    const pl = plant(); pl.position.set(-620, 0, -380); pl.scale.setScalar(0.8); g.add(pl);
  });
  // Nightstand: walnut top, dusk-blue wall, warm lamp, book stack.
  mk('night', g => {
    g.add(surface(woodTex('#5e3d27', '#2d1a0e', '#7d5638'), 3200, 2400), wall(plasterTex('#3b4752', '#2c353e')));
    const l = lamp(); l.position.set(-260, 0, -330); g.add(l); g.userData.light = l.userData.light; g.userData.shade = l.userData.shade;
    const b = books(); b.position.set(300, 0, -200); b.rotation.y = -0.2; g.add(b);
  });
  // Travel: linen bed cover, folded towel, passport, zip pouch.
  mk('travel', g => {
    g.add(surface(linenTex('#d8d2c5'), 3200, 2400, 1), wall(plasterTex('#e9e4dc', '#dcd5ca')));
    const tw = towel(); tw.position.set(-420, 0, -260); tw.rotation.y = 0.2; g.add(tw);
    const ps = passport(); ps.position.set(-150, 0, 50); ps.rotation.y = 0.35; g.add(ps);
    const po = pouch(); po.position.set(190, 0, -150); po.rotation.y = -0.25; g.add(po);
  });
  // Shelf for the size line-up: pale oak, paper wall.
  mk('shelf', g => {
    const oak = std({ map: woodTex('#d2b48c', '#a07a50', '#ead2ae', 1), roughness: 0.55 });
    const board = mesh(new RoundedBoxGeometry(2600, 32, 300, 3, 4), oak); board.position.set(0, -16, -110); board.receiveShadow = true;
    const w = wall(plasterTex('#f1eee8', '#e4dfd6'), 6000, 3000, -262); w.position.y = 0;
    const brM = std({ color: '#2b2b2b', roughness: 0.5, metalness: 0.4 });
    for (const x of [-900, 900]) { const b = mesh(new THREE.BoxGeometry(12, 160, 240), brM); b.position.set(x, -112, -130); g.add(b); }
    const bk = books(); bk.position.set(-1050, 0, -170); bk.rotation.y = 0.1; bk.scale.setScalar(0.9);
    const pl = plant(); pl.position.set(1060, 0, -180); pl.scale.setScalar(0.75);
    const below = mesh(new THREE.PlaneGeometry(6000, 1200), std({ color: '#d9d3c9', roughness: 1 }), { cast: false }); below.position.set(0, -640, -261);
    g.add(board, w, below, bk, pl);
  });
  return S;
}

// ---------- a hand ----------
// A simple, softly lit hand with a knit sleeve: palm, four three-joint fingers and a two-joint thumb.
// Local frame: fingers point along +z, palm faces -y (down), the back of the hand faces +y.
// pose({ curl, pinch, point }) bends the joints; units are mm.
export function makeHand(skin = '#d4a284', sleeve = '#8f9a8c') {
  const root = new THREE.Group();
  const skinM = new THREE.MeshPhysicalMaterial({ color: skin, roughness: 0.55, sheen: 0.6, sheenRoughness: 0.7, sheenColor: new THREE.Color('#ffd2bd') });
  const sleeveM = std({ map: linenTex(sleeve), roughness: 1 });
  const seg = (r, len) => mesh(new THREE.CapsuleGeometry(r, len, 6, 16).rotateX(Math.PI / 2).translate(0, 0, len / 2), skinM);
  const palm = mesh(new THREE.SphereGeometry(1, 32, 20).scale(42, 13, 50), skinM);
  palm.position.z = 40;
  const wrist = mesh(new THREE.CapsuleGeometry(24, 40, 8, 20).rotateX(Math.PI / 2).scale(1.25, 0.75, 1), skinM);
  wrist.position.z = -8;
  const cuff = mesh(new THREE.CylinderGeometry(42, 46, 260, 32, 1, true).rotateX(Math.PI / 2), sleeveM);
  cuff.position.z = -150;
  const cuffEnd = mesh(new THREE.TorusGeometry(42, 6, 12, 32), sleeveM);
  cuffEnd.position.z = -20;
  root.add(palm, wrist, cuff, cuffEnd);
  const fingers = [];
  const spec = [[-27, 80, [40, 26, 20], 8.2], [-9, 86, [45, 28, 21], 8.6], [9, 84, [43, 27, 21], 8.4], [26, 76, [34, 22, 18], 7.6]];
  for (const [x, z, lens, r] of spec) {
    const base = new THREE.Group(); base.position.set(x, -2, z); root.add(base);
    let parent = base; const joints = [];
    lens.forEach((L, i) => {
      const j = new THREE.Group(); parent.add(j);
      if (i > 0) j.position.z = lens[i - 1];
      j.add(seg(r * (1 - i * 0.08), L - r));
      joints.push(j); parent = j;
    });
    fingers.push({ base, joints });
  }
  // thumb: from the inner side of the palm, angled forward and down
  const tb = new THREE.Group(); tb.position.set(-40, -10, 22); tb.rotation.set(0.5, -0.9, 0.3); root.add(tb);
  const t1 = new THREE.Group(); t1.add(seg(10, 32)); tb.add(t1);
  const t2 = new THREE.Group(); t2.position.z = 36; t2.add(seg(9, 24)); t1.add(t2);
  root.userData = { fingers, thumb: [tb, t1, t2] };
  root.pose = ({ curl = 0.15, pinch = 0, point = 0, spread = 0 } = {}) => {
    fingers.forEach((f, i) => {
      const c = i === 0 ? curl * (1 - point) + pinch * 0.55 : curl + pinch * 0.35 * (i / 3);
      f.base.rotation.set(c * 0.9, (i - 1.5) * spread * 0.08, 0);
      f.joints[1].rotation.x = c * 1.2; f.joints[2].rotation.x = c * 0.9;
    });
    t1.rotation.y = 0.2 + pinch * 0.7; t2.rotation.x = 0.3 + pinch * 0.4;
  };
  root.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  root.pose();
  return root;
}
