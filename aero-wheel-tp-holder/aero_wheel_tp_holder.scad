// =====================================================================
//  GT RS AERO-DISC WHEEL  TOILET PAPER HOLDER  (3M Command strip mount)
// =====================================================================
//  WALL PART:  black multi-spoke wheel + tire (with a brake caliper
//              behind the spokes) and a post with a screw thread on the end.
//  AERO DISC:  black disc with a green ring and lettering. It screws onto
//              the post and holds the roll on. Unscrew it to change the paper.
//
//  Parts (no supports needed):
//    "wall"          wheel + post, one piece      (print back down)
//    "wall_caliper"  just the caliper, for a multi-colour printer
//    "wall_black"    the wall part minus the caliper
//    "disc"          aero disc, one piece          (print back down)
//    "disc_green"    green ring only                } multi-colour
//    "disc_black"    everything but the green ring  } printers
// =====================================================================

/* [What to show] */
part = "assembly";   // [assembly, wall, wall_black, wall_caliper, disc, disc_black, disc_green]
show_roll = false;

/* [Lettering] */
text_top    = "GT3 RS";
text_side   = "MR";
text_bottom = "PORSCHE";
font        = "Liberation Sans:style=Bold Italic";
text_size   = 7.5;
emblem_d    = 30;        // pocket in the centre-lock nut for an emblem sticker
emblem_depth= 1.4;

/* [Wall wheel] */
tire_d    = 190;
rim_r     = 76;          // where the tire meets the rim
back_t    = 3;           // solid back plate (strips go here)
spoke_h   = 8;           // front of the spokes
hub_r     = 26;
spoke_pairs = 10;

/* [Post and thread] */
post_d    = 32;          // roll cores are about 42 mm inside
roll_room = 128;
thr_major = 30;
thr_depth = 1.4;
thr_pitch = 5;
thr_len   = 14;
thr_clear = 0.35;        // extra room in the disc's thread. Raise it if the disc screws on too tight

/* [Aero disc] */
disc_d    = 120;
disc_t    = 4;
band_w    = 13;          // green ring width
band_h    = 1.2;         // green ring height (the letters are cut through it)
dhub_r    = 23;
nut_r     = 20;
nut_h     = 16;

$fn = 120;
function polar(r, a) = [r*cos(a), r*sin(a)];

// ---------------------------------------------------------------------
//  Thread: a trapezoid profile swept as a helix (same code cuts the nut)
// ---------------------------------------------------------------------
function tf(t) = t < 0.1 ? 0 : t < 0.4 ? (t-0.1)/0.3 : t < 0.6 ? 1 : t < 0.9 ? (0.9-t)/0.3 : 0;
module thread_solid(h, extra = 0) {
    N = 90;
    rmin = thr_major/2 - thr_depth + extra;
    linear_extrude(height = h, twist = -360*h/thr_pitch, slices = ceil(h/thr_pitch*N/1.5), convexity = 4)
        polygon([for (i = [0:N-1]) let(a = i*360/N) polar(rmin + thr_depth*tf(i/N), a)]);
}

// ---------------------------------------------------------------------
//  Wall wheel + post  (z = 0 is the wall)
// ---------------------------------------------------------------------
module tire() {
    rotate_extrude() polygon([[rim_r,0],[tire_d/2,0],[tire_d/2,spoke_h-1],[tire_d/2-3,spoke_h+2],
                              [rim_r+8,spoke_h+2.5],[rim_r+2,spoke_h+1.5],[rim_r,spoke_h+1.5]]);
}
module spokes2d() {
    for (i = [0:spoke_pairs-1], side = [-1,1]) {
        a = i*360/spoke_pairs + 90;
        hull() {
            translate(polar(hub_r - 3, a + side*3.5)) circle(2.6);
            translate(polar(rim_r - 2, a + side*5.5)) circle(2.0);
        }
    }
}
// brake caliper, sitting behind the spokes at the lower right
module caliper() {
    translate([0,0,back_t - 0.01]) linear_extrude(spoke_h - 2.5)
        intersection() {
            difference() { circle(rim_r - 6); circle(rim_r - 22); }
            rotate(292) offset(3) offset(-3) polygon([[0,0],[200,-70],[200,70]]);
        }
}
module wall_body() {
    cylinder(r = rim_r + 0.5, h = back_t);                 // back plate
    tire();
    difference() {                                          // rim barrel / lip
        cylinder(r = rim_r + 0.5, h = spoke_h + 1.5);
        translate([0,0,-1]) cylinder(r = rim_r - 4, h = 20);
    }
    linear_extrude(spoke_h) spokes2d();                     // spokes
    cylinder(r = hub_r, h = spoke_h + 2);                   // hub
    translate([0,0,spoke_h + 2 - 0.01]) cylinder(r1 = hub_r - 2, r2 = post_d/2, h = 8);   // fillet
    // post, then the threaded end (shoulder stops the disc)
    cylinder(d = post_d, h = spoke_h + roll_room);
    translate([0,0,spoke_h + roll_room - 0.01]) intersection() {
        thread_solid(thr_len);
        cylinder(d1 = thr_major + 2*thr_len, d2 = thr_major - 2*thr_depth - 1, h = thr_len + thr_depth + 0.5);   // lead-in chamfer
    }
}
module wall()         { union() { wall_body(); caliper(); } }
module wall_black()   { difference() { wall_body(); caliper(); } }
module wall_caliper() { difference() { caliper(); wall_body(); } }

// ---------------------------------------------------------------------
//  Aero disc  (z = 0 is the back, facing the roll)
// ---------------------------------------------------------------------
band_r1 = disc_d/2 - 1.5;
band_r0 = band_r1 - band_w;
band_rm = (band_r0 + band_r1)/2;

module curved_text(str, r, center_a, dir, size) {
    n = len(str);
    step = size * 0.86 / r * 180 / PI;
    for (k = [0:n-1]) {
        a = center_a - dir * (k - (n-1)/2) * step;
        translate(polar(r, a)) rotate(a - dir*90)
            text(str[k], size = size, font = font, halign = "center", valign = "center");
    }
}
module letters2d() {
    curved_text(text_top,    band_rm,  95,  1, text_size);
    curved_text(text_side,   band_rm, 192,  1, text_size);
    curved_text(text_bottom, band_rm, 298, -1, text_size);
}
module band() {
    translate([0,0,disc_t - 0.01]) difference() {
        linear_extrude(band_h + 0.01) difference() { circle(band_r1); circle(band_r0); }
        translate([0,0,-1]) linear_extrude(band_h + 2) letters2d();     // letters cut through to the black
    }
}
module disc_body() {
    difference() {
        union() {
            // flat disc with a small chamfer on the front edge
            cylinder(d = disc_d, h = disc_t - 1);
            translate([0,0,disc_t-1]) cylinder(d1 = disc_d, d2 = disc_d - 2, h = 1);
            // hub and centre-lock nut
            cylinder(r = dhub_r, h = disc_t + 5);
            translate([0,0,disc_t + 5 - 0.01]) difference() {
                union() { cylinder(r = nut_r, h = nut_h - 1); translate([0,0,nut_h-1]) cylinder(r1 = nut_r, r2 = nut_r - 1, h = 1); }
                for (a = [0:30:359]) rotate(a) translate([nut_r - 2, -1.8, 2]) cube([4, 3.6, nut_h]);
            }
        }
        // threaded hole from the back, with a lead-in and a cone roof
        translate([0,0,-0.01]) thread_solid(thr_len + 1, thr_clear);
        translate([0,0,-0.01]) cylinder(d1 = thr_major + 1.5, d2 = thr_major - 2*thr_depth, h = 1.6);
        // 45 degree cone, then a short flat roof (bridges fine; hidden under the emblem)
        translate([0,0,thr_len + 0.98]) cylinder(r1 = thr_major/2 + thr_clear, r2 = 9, h = thr_major/2 + thr_clear - 9);
        // emblem pocket
        translate([0,0,disc_t + 5 + nut_h - emblem_depth]) cylinder(d = emblem_d, h = 5);
    }
}
module disc()       { union() { disc_body(); band(); } }
module disc_black() { disc_body(); }
module disc_green() { difference() { band(); disc_body(); } }

disc_top = disc_t + 5 + nut_h;
roof_top = thr_len + 0.98 + thr_major/2 + thr_clear - 9;
assert(roof_top < disc_top - emblem_depth - 1.5, "thread hole would break through the nut: raise nut_h");
echo(str("Wall part height: ", spoke_h + roll_room + thr_len, " mm.  Disc height: ", disc_top, " mm"));
echo(str("Single-colour printer: swap to GREEN at ", disc_t, " mm and back to BLACK at ", disc_t + band_h, " mm on the disc"));

// ---------------------------------------------------------------------
if      (part == "wall")         wall();
else if (part == "wall_black")   wall_black();
else if (part == "wall_caliper") wall_caliper();
else if (part == "disc")         disc();
else if (part == "disc_black")   disc_black();
else if (part == "disc_green")   disc_green();
else {
    color("#1a1a1a") wall_black();
    color("#f2c200") wall_caliper();
    translate([0,0,spoke_h + roll_room]) { color("#222") disc_black(); color("#5DBB3F") disc_green(); }
    if (show_roll) color("white", 0.9) translate([0,0,spoke_h + 6])
        difference() { cylinder(d = 118, h = 114); translate([0,0,-1]) cylinder(d = 42, h = 116); }
}
