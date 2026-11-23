// =====================================================================
//  GT3 RS-STYLE WHEEL TOILET PAPER HOLDER  -  mounts with 3M Command strips
// =====================================================================
//  A wall disc with a post. The roll slides onto the post, then the
//  wheel pushes onto the end of the post (tapered press fit) and holds
//  the roll. Pull the wheel off to change the roll.
//
//  Parts (no supports needed):
//    part = "wall"   wall disc + post   (print disc down)
//    part = "wheel"  10-spoke wheel     (print back down, face up)
//    part = "wheel_body" + "wheel_letters"  the wheel split in two colours
//                    for a multi-colour printer (load together as one object)
//
//  The centre-lock nut has a round pocket for a real emblem / centre-cap
//  sticker: measure yours and set emblem_d. The lettering on the rim is
//  raised, so you can swap filament colour at the height shown in the
//  console ("Colour change height") to print it in a second colour.
// =====================================================================

/* [What to show] */
part = "assembly";            // [assembly, wall, wheel, wheel_body, wheel_letters]
show_roll = false;

/* [Text and emblem] */
top_text    = "GT3 RS";
bottom_text = "911";
font        = "Liberation Sans:style=Bold";
text_size   = 8;
emblem_d    = 40;             // pocket for your emblem (measure it)
emblem_depth= 1.4;

/* [Wall disc and post] */
disc_d    = 150;
disc_t    = 6;
post_d    = 32;               // roll cores are about 42 mm inside
roll_room = 128;              // space for the roll between disc and wheel
fit_len   = 12;               // tapered part of the post that goes into the wheel
taper     = 1.4;              // post narrows by this much over fit_len
fit_clear = 0.3;              // extra size on the wheel's socket

/* [Wheel] */
wheel_d   = 148;
rim_w     = 22;               // depth of the wheel from back to front lip
hub_r     = 30;
nut_r     = 26;
nut_h     = 10;
hub_h     = 18;
spoke_pairs = 5;

$fn = 120;

post_len = roll_room + fit_len;
R  = wheel_d/2;
Ri = R - 8;                   // inner edge of the barrel

// ---------------------------------------------------------------------
//  Wall disc + post   (z = 0 is the wall)
// ---------------------------------------------------------------------
module wall() {
    // disc with a small chamfer on the front edge
    cylinder(d = disc_d, h = disc_t - 1.2);
    translate([0,0,disc_t-1.2]) cylinder(d1 = disc_d, d2 = disc_d - 2.4, h = 1.2);
    // fillet where the post meets the disc
    translate([0,0,disc_t - 0.01]) cylinder(d1 = post_d + 16, d2 = post_d, h = 8);
    // straight post
    translate([0,0,disc_t]) cylinder(d = post_d, h = post_len - fit_len);
    // tapered press-fit end, with a lead-in chamfer
    translate([0,0,disc_t + post_len - fit_len]) {
        cylinder(d1 = post_d, d2 = post_d - taper, h = fit_len - 1);
        translate([0,0,fit_len-1]) cylinder(d1 = post_d - taper, d2 = post_d - taper - 2, h = 1);
    }
}

// ---------------------------------------------------------------------
//  Wheel   (z = 0 is the back of the wheel, front faces +z)
// ---------------------------------------------------------------------
function polar(r, a) = [r*cos(a), r*sin(a)];

module spokes2d() {
    for (i = [0:spoke_pairs-1], side = [-1, 1]) {
        a = i * 360/spoke_pairs + 90;
        hull() {
            translate(polar(hub_r - 4, a + side*5))  circle(5.2);
            translate(polar(Ri + 2,    a + side*10)) circle(4.0);
        }
    }
}

// concave face: spokes rise from the hub toward the rim
module spoke_top_envelope() {
    rotate_extrude() polygon([[0,0],[Ri+3,0],[Ri+3,rim_w-3],[hub_r-2,rim_w-9],[0,rim_w-9]]);
}

module curved_text(str, r, center_a, dir) {
    n = len(str);
    step = text_size * 0.82 / r * 180 / PI;   // angle per character
    for (k = [0:n-1]) {
        a = center_a - dir * (k - (n-1)/2) * step;
        translate(polar(r, a)) rotate(a - dir*90)
            text(str[k], size = text_size, font = font, halign = "center", valign = "center");
    }
}

module wheel() {
    sock_d0 = post_d - taper + fit_clear;     // socket narrows going in, like the post
    sock_d1 = post_d + fit_clear;
    difference() {
        union() {
            // barrel
            difference() { cylinder(r = R, h = rim_w - 4); translate([0,0,-1]) cylinder(r = Ri, h = rim_w); }
            // front lip: 45 degree chamfer inward, then a flat band for the lettering
            translate([0,0,rim_w-8]) difference() {
                cylinder(r = R, h = 8);
                translate([0,0,-0.01]) cylinder(r1 = Ri, r2 = Ri - 4, h = 4.02);
                translate([0,0,4]) cylinder(r = Ri - 4, h = 5);
            }
            // spokes
            intersection() { linear_extrude(rim_w) spokes2d(); spoke_top_envelope(); }
            // hub
            cylinder(r = hub_r, h = hub_h);
            // centre-lock nut with notches
            translate([0,0,hub_h - 0.01]) difference() {
                union() {
                    cylinder(r = nut_r, h = nut_h - 1);
                    translate([0,0,nut_h-1]) cylinder(r1 = nut_r, r2 = nut_r - 1, h = 1);
                }
                for (a = [0:30:359]) rotate(a) translate([nut_r - 2.2, -2, 2]) cube([4, 4, nut_h]);
            }
        }
        // tapered socket for the post (open at the back), cone roof so it prints without supports
        translate([0,0,-0.01]) cylinder(d1 = sock_d1, d2 = sock_d0, h = fit_len + 0.5);
        translate([0,0,fit_len + 0.49]) cylinder(d1 = sock_d0, d2 = 8, h = (sock_d0 - 8)/2);
        // emblem pocket
        translate([0,0,hub_h + nut_h - emblem_depth]) cylinder(d = emblem_d, h = 5);
    }
    // raised lettering on the front lip
    translate([0,0,rim_w - 0.01]) linear_extrude(1.01) {
        curved_text(top_text,    (R + Ri - 4)/2,  90,  1);
        curved_text(bottom_text, (R + Ri - 4)/2, 270, -1);
    }
}

echo(str("Colour change height for the lettering (wheel): ", rim_w + 0.2, " mm"));
echo(str("Post length from wall: ", disc_t + post_len, " mm"));

// ---------------------------------------------------------------------
if (part == "wall")       wall();
else if (part == "wheel") wheel();
else if (part == "wheel_body")    intersection() { wheel(); translate([-200,-200,0]) cube([400,400,rim_w + 0.2]); }
else if (part == "wheel_letters") intersection() { wheel(); translate([-200,-200,rim_w + 0.2]) cube([400,400,50]); }
else {
    color("#1a1a1a") wall();
    color("#1a1a1a") translate([0,0,disc_t + roll_room]) wheel();
    if (show_roll) color("white", 0.9) translate([0,0,disc_t + 4])
        difference() { cylinder(d = 120, h = 112); translate([0,0,-1]) cylinder(d = 42, h = 114); }
}
