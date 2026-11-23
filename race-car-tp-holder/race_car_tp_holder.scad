// =====================================================================
//  911 GT3 RS-STYLE TOILET PAPER HOLDER  -  mounts with 3M Command strips
//  Green car, black accents (wheels, wing, windows, splitter, diffuser)
// =====================================================================
//  The side profile of the car sticks straight out from a wall plate.
//  Its front wheel is the axle: the roll slides onto the bar from the
//  open end, so changing rolls takes two seconds.
//
//  Parts (no supports needed for any of them):
//    part = "base"        plate + car as one piece, for a single-colour printer
//                         (swap to green filament at 6 mm: black plate, green car)
//    part = "base_green"  the green parts only   } load both together as one
//    part = "base_black"  the black parts only   } object on a multi-colour printer
//    part = "axle"        the roll bar (print in black, tire end down)
//  Glue the axle's hex peg into the hex hole in the front wheel.
// =====================================================================

/* [What to show] */
part = "assembly";        // [assembly, base, base_green, base_black, axle]
car_side = "left";        // [left, right]  side the car is on, as you face the wall
show_roll = false;        // show a roll of paper in the assembly view

/* [Wall plate] */
plate_w = 100;            // fits 4 large Command strips laid sideways
plate_h = 170;
plate_t = 6;
plate_r = 10;

/* [Roll bar] */
axle_out  = 92;           // wall to axle centre (fits rolls up to 150 mm across)
axle_z    = -15;          // axle height on the plate
axle_d    = 30;           // roll cores are about 42 mm inside
roll_room = 128;          // usable length on the bar
cap_d     = 38;           // tire on the open end
hex_af    = 18;           // hex peg, across flats
hex_clear = 0.4;          // extra size on the hole for the peg

/* [Details] */
fin_t   = 14;             // thickness of the car
inlay   = 0.8;            // depth of the black window / intake inlays

$fn = 96;

s = car_side == "left" ? -1 : 1;
lx_out = -plate_w/2;            // car built on the left, mirrored for the right
lx_in  = -plate_w/2 + fin_t;

// ---------------------------------------------------------------------
//  Helpers
// ---------------------------------------------------------------------
// 2D shapes are drawn in profile space: u = distance out from the wall
// (rear of car at the wall, nose in the room), v = height above the axle.
module prof(x0, x1) {
    translate([max(x0,x1), 0, axle_z])
        multmatrix([[0,0,-1,0],[-1,0,0,0],[0,1,0,0],[0,0,0,1]])
            linear_extrude(abs(x1-x0)) children();
}
module rrect(w, h, r) { offset(r) square([w-2*r, h-2*r], center=true); }

// wheel with a 45 degree point toward the wall so it prints without supports
module wheel2d(c, r) {
    hull() { translate([c,0]) circle(r); translate([c - r*sqrt(2), 0]) square(0.01, center=true); }
}
module hex_prism(af, z0, z1) { translate([0,0,z0]) cylinder(r = af/sqrt(3), h = z1-z0, $fn = 6); }
module axle_frame(x) { translate([x, -axle_out, axle_z]) rotate([0, 90, 0]) children(); }

// ---------------------------------------------------------------------
//  Car profile
// ---------------------------------------------------------------------
front_wheel = axle_out;
rear_wheel  = axle_out - 64;
wheel_r     = 22;

module behind_wall_clip() { translate([0,-100]) square([300,200]); }

// green body
module body2d() {
    polygon([[0,-14],[160,-14],[160,-8],[163,0],[160,10],[150,18],[140,22],
             [128,22],[110,26],[100,30],[78,47],[64,48],[40,41],[20,34],[0,32]]);
}
// black parts that go all the way through the car
module black_full2d() {
    intersection() {
        union() {
            wheel2d(front_wheel, wheel_r);
            wheel2d(rear_wheel,  wheel_r);
            // swan-neck rear wing: blade, gurney lip and mount
            translate([0,56]) square([40,6]);
            translate([0,62]) square([5,3]);
            polygon([[3,30],[18,35],[26,57],[3,57]]);
            // front splitter
            polygon([[118,-14],[166,-14],[166,-10],[118,-10]]);
        }
        behind_wall_clip();
    }
}
// rear diffuser sits at the bottom rear
module diffuser2d() { translate([0,-14]) polygon([[0,0],[16,0],[16,3],[0,6]]); }

// black inlays on both faces of the car
module black_inlay2d() {
    // side windows
    polygon([[36,34],[44,40.5],[64,45],[76,44.5],[88,34]]);
    // side air intake ahead of the rear wheel
    polygon([[52,4],[62,4],[66,16],[54,16]]);
    // lower door stripe
    translate([54,-10]) square([14,3]);
    // headlight
    translate([146,15]) scale([1.6,1]) circle(3.2);
}

module car_solid2d() {
    intersection() { union() { body2d(); black_full2d(); } behind_wall_clip(); }
}

// ---------------------------------------------------------------------
//  Base (built for a car on the left)
// ---------------------------------------------------------------------
module plate3d() { rotate([90,0,0]) linear_extrude(plate_t) rrect(plate_w, plate_h, plate_r); }

module brace3d() {   // brace on the roll side between car and plate
    translate([0,0,axle_z-12]) linear_extrude(30)
        polygon([[lx_in-0.01,-plate_t+0.01],[lx_in+12,-plate_t+0.01],[lx_in-0.01,-plate_t-10]]);
}

module hex_hole() { axle_frame(lx_in) hex_prism(hex_af + hex_clear, -fin_t - 1, 1); }

// black regions of the car, as solids
module car_black3d() {
    difference() {
        union() {
            prof(lx_out, lx_in) intersection() { union() { black_full2d(); diffuser2d(); } behind_wall_clip(); }
            prof(lx_out - 0.01, lx_out + inlay)  black_inlay2d();
            prof(lx_in - inlay,  lx_in + 0.01)   black_inlay2d();
        }
        hex_hole();
    }
}

module car_all3d() {
    difference() {
        union() { prof(lx_out, lx_in) car_solid2d(); brace3d(); }
        hex_hole();
    }
}

module green_left() { difference() { car_all3d(); car_black3d(); plate3d(); } }
module black_left() { union() { plate3d(); intersection() { car_black3d(); car_all3d(); } } }
module whole_left() { union() { plate3d(); car_all3d(); } }

module side(m) { if (s < 0) children(); else mirror([1,0,0]) children(); }

// ---------------------------------------------------------------------
//  Axle (local frame: +z runs from the car toward the open end)
// ---------------------------------------------------------------------
hub_d    = 40;
shaft_z0 = 6.5;
cap_z0   = shaft_z0 + roll_room;
cap_t    = 10;
axle_len = cap_z0 + cap_t;

module axle() {
    peg_len = fin_t - 0.3;           // sits flush in the wheel like a centre-lock nut
    hull() {
        hex_prism(hex_af, -peg_len + 0.6, 0);
        hex_prism(hex_af - 1.2, -peg_len, -peg_len + 0.6);
    }
    cylinder(d = hub_d, h = 1.5);
    translate([0,0,1.5]) cylinder(d1 = hub_d, d2 = axle_d, h = (hub_d-axle_d)/2);
    cylinder(d = axle_d, h = cap_z0 + 0.01);
    translate([0,0,cap_z0]) difference() {       // tire with tread on the open end
        union() {
            cylinder(d = cap_d, h = cap_t - 1.5);
            translate([0,0,cap_t-1.5]) cylinder(d1 = cap_d, d2 = cap_d - 3, h = 1.5);
        }
        for (a = [0:20:359]) rotate(a) translate([cap_d/2 - 0.9, -1, -1]) cube([3, 2, cap_t + 2]);
        translate([0,0,cap_t - 0.8]) difference() { cylinder(d = cap_d - 9, h = 2); cylinder(d = cap_d - 12, h = 2); }
    }
}

// ---------------------------------------------------------------------
//  Output
// ---------------------------------------------------------------------
green = "#5DBB3F";
black = "#1a1a1a";

if (part == "base")             rotate([-90,0,0]) side() whole_left();    // wall side down
else if (part == "base_green")  rotate([-90,0,0]) side() green_left();
else if (part == "base_black")  rotate([-90,0,0]) side() black_left();
else if (part == "axle")        translate([0,0,axle_len]) rotate([180,0,0]) axle();   // tire end down
else {
    color(green) side() green_left();
    color(black) side() black_left();
    color(black) translate([s*(plate_w/2 - fin_t), -axle_out, axle_z]) rotate([0, -s*90, 0]) axle();
    if (show_roll) color("white", 0.9)
        translate([s*(plate_w/2 - fin_t) - s*(roll_room/2 + 8), -axle_out, axle_z]) rotate([0,90,0])
            difference() { cylinder(d = 115, h = 112, center = true); cylinder(d = 42, h = 114, center = true); }
}
