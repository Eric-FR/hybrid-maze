difference(){
    union(){
        sphere(7.5);
            cylinder(h=122 , r = 3.5, center = true);
        rotate([90,0,0]){
            cylinder(h=122 , r = 3.5, center = true);
        }
        rotate([0,90,0]){
            cylinder(h=122 , r = 3.5, center = true);
        }
    }
    translate([0, 0, -61.5]){
        cube([123, 123, 123],true);
    }
}
