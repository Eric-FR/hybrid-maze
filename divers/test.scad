difference(){
    union(){
        sphere(7.5);
        cylinder(h=322 , r = 3.5, center = true);
        rotate([90,0,0]){
            cylinder(h=322 , r = 3.5, center = true);
        }
        rotate([0,90,0]){
            cylinder(h=322 , r = 3.5, center = true);
        }
    }
    translate([0, 0, -161.5]){
        cube([323, 323, 323],true);
    }
}
