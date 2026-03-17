difference (){
    cylinder(40, 20, 20);
    union(){
        translate([0, 0, 2]){
            rotate([45, -35.26, 0]){
                cube(40);
            }
        }    
        cylinder(10,2,2);
    }
}    