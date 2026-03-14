# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Initial author: Eric Sibert 

# Generate a 3D maze defined by 2D mazes cut out of cube''s faces.
# Also known as Oskar's cube maze, or 3D maze with 2D projections on faces.
# https://www.youtube.com/watch?v=G02t4F2opCU
# Inspired from an article in "La Recherche" in late 80s
# Initially programmed by the author in Turbo Pascal on a PC 80286
# Save faces to SVG file for laser cutting.
# Need post-processing in Inkscape to convert path to cut lines and add surrending box
# box : https://boxes.hackerspace-bamberg.de/ClosedBox?language=en
# Save 6ways node to navigate to SCAD files for 3D printing. Use OpenSCAD to generate STL file for 3D printing.

import numpy as np
import random
import argparse

directions = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]])

# parameters for projection on cube faces
# including no projection with (1, 1, 1)
all_faces = ((1, 1, 1), (0, 1, 1), (1, 0, 1), (1, 1, 0)) 

def generate_one_try(n, branching, verbose=False):
    # n : maze size
    # branching : probability of going backward to start a new lateral branch instead of trying to prolongate the current one

    # the maze is represented by a cube. 
    # Inner part of the cube is a 3D maze
    # Nodes are odd positions i.e. from [1,1,1] to [2*n-1, 2*n-1, 2*n-1]
    # Connexions between nodes are at even positions between nodes
    # surfaces (at x,y,z=0 resp.) of the cube are 2D projections of the 3D maze i.e. 2D mazes
    maze_bulk = np.full([2*n+1, 2*n+1, 2*n+1], False)

    # starting point
    active_nodes = [np.array([1,1,1])]

    for face in all_faces:
        maze_bulk[tuple([a*b for a, b in zip(face, active_nodes[0])])] = True

    end_node = np.array([2*n-1, 2*n-1, 2*n-1])
    reach_end = False

    while len(active_nodes) > 0:
        if random.random() < branching:
            # use a random active node to go forward
            current_node = random.randint(0, len(active_nodes) - 1)
        else:
            # use the last active node to go forward
            # current_node =  len(active_nodes) - 1   
            current_node =  - 1   

        # choose randomly the first direction to explore around the current node     
        first_direction = random.randint(0, 5)

        # for each direction, look if one can prolongate the path both in the bulk and on the surface
        # until finding one new prolongation
        prolongation = False
        for i in range(6):
            current_dir = (first_direction + i) % 6
            new_connexion = active_nodes[current_node] + directions[current_dir]
            new_node = new_connexion + directions[current_dir]
            # check if the current direction stay inside the cube
            if (0 < new_connexion[0] < 2 * n) and (0 < new_connexion[1] < 2 * n) and (0 < new_connexion[2] < 2 * n):
                # check if the current direction is going to an empty node
                if not maze_bulk[tuple(new_node)]:
                    # check in surface (on the 3 faces) if, whatever, 
                    # it will use an existing corridor (connexion and next node already exists)
                    # or ir corridor is free (connexion and next node not used)
                    virgin = True
                    for face in all_faces[1:]:
                        if not ((maze_bulk[tuple([a*b for a, b in zip(face, new_connexion)])] and \
                        maze_bulk[tuple([a*b for a, b in zip(face, new_node)])]) or \
                        (not maze_bulk[tuple([a*b for a, b in zip(face, new_connexion)])] and \
                        not maze_bulk[tuple([a*b for a, b in zip(face, new_node)])])):
                            virgin = False
                    # all is OK, add connexion and next node in 3D and on each face
                    if virgin:
                        for face in all_faces:
                            maze_bulk[tuple([a*b for a, b in zip(face, new_connexion)])] = True
                            maze_bulk[tuple([a*b for a, b in zip(face, new_node)])] = True
                        # if outlet is reached (node in [2*n-1, 2*n-1, 2*n-1]), set reach_end to True
                        #if (new_node[0] == end_node[0]) and (new_node[1] == end_node[1]) and (new_node[2] == end_node[2]):
                        if (new_node == end_node).all():
                            reach_end = True
                        else:
                            # add new node to active_nodes list
                            active_nodes.append(new_node)
                        # break the i loop that is looking for a continuation as continuation was found
                        prolongation = True
                        break
        # at this point, no continuation has been found on the current node
        # current node is removed from the list
        if not prolongation:
            del active_nodes[current_node]

    # no more active nodes available for prolongation
    # it is time to check maze consistancy
    # was outlet reached
    if not reach_end:
        if verbose:
            print('Failed to reach opposite point')
        result = False
    else:
        # are lateral faces fully used
        faceX = maze_bulk[0, 1::2, 1::2].all()
        faceY = maze_bulk[1::2, 0, 1::2].all()
        faceZ = maze_bulk[1::2, 1::2, 0].all()

        result = faceX and faceY and faceZ

        if verbose:
            print('Opposite point reached')

            maze_char = [".", "#"]

            if faceX:
                print('X face complete')
            else:
                print('X face not full')
            for lig in maze_bulk[0]:
                one_line = ''
                for b in lig:
                    one_line += maze_char[int(b)]
                print(one_line)

            if faceY:
                print('Y face complete')
            else:
                print('Y face not full')
            for lig in maze_bulk[:, 0]:
                one_line = ''
                for b in lig:
                    one_line += maze_char[int(b)]
                print(one_line)

            if faceZ:
                print('Z face complete')
            else:
                print('Z face not full')
            for lig in maze_bulk[:, :, 0]:
                one_line = ''
                for b in lig:
                    one_line += maze_char[int(b)]
                print(one_line)
        else:
            if result:
                print('*')
            else:
                print('.', end=' ')
    return result, maze_bulk

def save2svg(svg_filename, spacing, rel_width, mat_thickness, the_maze):
# spacing is the distance in millimeter between consecutive paths
# rel_witdh : relative width of path vs. separation.
# 50% : path and separation are equal; 0% : no path; 100% : no separation
# mat_thickness : thickness in millimeter of the material to be cutted. 
# spacing between each part of the box is supposed to be equal to material thickness
# i.e. in ClosedBox interface "spacing"=1.
# also assume "burn correction"=0.
    with open(svg_filename, "w") as file_svg:
        a = the_maze.shape[0]
        border_rel = 2 * mat_thickness/spacing
        file_svg.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
        file_svg.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n')
        file_svg.write('  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
        file_svg.write('<svg width="{0:.1f}mm" height="{1:.1f}mm"  viewBox="{2:.1f} {2:.1f} {3:.1f} {4:.1f}" xmlns="http://www.w3.org/2000/svg">\n'.\
                       format(a * spacing + mat_thickness * 5, 1.5 * a * spacing + mat_thickness * 8, \
                              -border_rel,  \
                              2 * a + 5 * border_rel,  3 * a + 8 * border_rel))
        
        file_svg.write('<path id="inner_square" fill-opacity="0" stroke="blue" stroke-linecap="round" stroke-linejoin="round" stroke-width="0.05"\n')
        file_svg.write('d="M0 0 L{0} 0 L{0} {0} L0 {0} L0 0" />\n'.format(a))
        Delta_sq = a+3*border_rel
        file_svg.write('<g transform="translate({} {})"><use xlink:href="#inner_square" /></g>\n'.format(Delta_sq, 0))
        file_svg.write('<g transform="translate({} {})"><use xlink:href="#inner_square" /></g>\n'.format(0, Delta_sq))
        file_svg.write('<g transform="translate({} {})"><use xlink:href="#inner_square" /></g>\n'.format(Delta_sq, Delta_sq))
        file_svg.write('<g transform="translate({} {})"><use xlink:href="#inner_square" /></g>\n'.format(0, 2 * Delta_sq))
        file_svg.write('<g transform="translate({} {})"><use xlink:href="#inner_square" /></g>\n'.format(Delta_sq, 2 * Delta_sq))

                       
        # face X=0
        # front = Wall 1
        file_svg.write('<g transform="translate(0 {})">\n'.format(2 * Delta_sq, 0))
        file_svg.write('<path id="frontx" fill-opacity="0" stroke="black" stroke-linecap="round" stroke-linejoin="round" stroke-width="{}"\n'.format(rel_width/100*2))
        file_svg.write('d="')
        for Y in range(1,a-1):
            for Z in range(1,a-2):
                if the_maze[0, Y, Z] and the_maze[0, Y, Z + 1]:
                    file_svg.write('M{} {} l0 1 '.format(Y + 0.5, Z + 0.5))
        for Z in range(1,a-1):
            for Y in range(1,a-2):
                if the_maze[0, Y, Z] and the_maze[0, Y + 1, Z]:
                    file_svg.write('M{} {} l1 0 '.format(Y + 0.5, Z + 0.5))
        file_svg.write('" />\n')
        file_svg.write('</g>\n')
        # back = Wall 3
        file_svg.write('<g transform="translate(0 {}) scale(-1 1) translate({} 0)"><use xlink:href="#frontx" /></g>\n'.format(Delta_sq, -a))

        # face Y=0
        # front = Wall 4
        file_svg.write('<g transform="translate({0} {0})">\n'.format(Delta_sq, 0))
        file_svg.write('<path id="fronty" fill-opacity="0" stroke="black" stroke-linecap="round" stroke-linejoin="round" stroke-width="{}"\n'.format(rel_width/100*2))
        file_svg.write('d="')
        for Z in range(1,a-1):
            for X in range(1,a-2):
                if the_maze[X, 0, Z] and the_maze[X + 1, 0, Z]:
                    file_svg.write('M{} {} l0 1 '.format(Z + 0.5, X + 0.5))
        for X in range(1,a-1):
            for Z in range(1,a-2):
                if the_maze[X, 0, Z] and the_maze[X , 0, Z + 1]:
                    file_svg.write('M{} {} l1 0 '.format(Z + 0.5, X + 0.5))
        file_svg.write('" />\n')
        file_svg.write('</g>\n')
        # back = Wall 2
        file_svg.write('<g transform="translate({} {}) scale(-1 1) translate({} 0)"><use xlink:href="#fronty" /></g>\n'.format(Delta_sq, 2 * Delta_sq, -a))

        # face Z=0
        # front = Top
        file_svg.write('<g transform="translate(0 0)">\n')
        file_svg.write('<path id="frontz" fill-opacity="0" stroke="black" stroke-linecap="round" stroke-linejoin="round" stroke-width="{}"\n'.format(rel_width/100*2))
        file_svg.write('d="')
        for X in range(1,a-1):
            for Y in range(1,a-2):
                if the_maze[X, Y, 0] and the_maze[X, Y + 1, 0]:
                    file_svg.write('M{} {} l0 1 '.format(X + 0.5, Y + 0.5))
        for Y in range(1,a-1):
            for X in range(1,a-2):
                if the_maze[X, Y, 0] and the_maze[X + 1, Y, 0]:
                    file_svg.write('M{} {} l1 0 '.format(X + 0.5, Y + 0.5))
        file_svg.write('" />\n')
        file_svg.write('</g>\n')
        # back = Bottom
        file_svg.write('<g transform="translate({} 0) scale(-1 1) translate({} 0)"><use xlink:href="#frontz" /></g>\n'.format(Delta_sq, -a))

        # start marker
        file_svg.write('<circle id="start_circle" fill="black" cx="0.5" cy="0.5" r="0.5" />\n')
        file_svg.write('<g transform="translate(0 {})"><use xlink:href="#start_circle" /></g>\n'.format(2 * Delta_sq))
        file_svg.write('<g transform="translate({0} {0})"><use xlink:href="#start_circle" /></g>\n'.format(Delta_sq))

        # end marker
        file_svg.write('<g transform="translate({} 0)"><rect id="end_square" fill="black" x="0" y="{}" width="1" height="1" /></g>\n'.format(Delta_sq, a-1))
        file_svg.write('<g transform="translate(0 {})"><use xlink:href="#end_square" /></g>\n'.format(Delta_sq))
        file_svg.write('<g transform="translate({} {})"><use xlink:href="#end_square" /></g>\n'.format(Delta_sq, 2 * Delta_sq))

        file_svg.write('</svg>\n')

def save_6ways_node(scad_filename, spacing, rel_width, mat_thickness, the_maze):
    with open(scad_filename, "w") as file_scad:
        a = the_maze.shape[0]
        tige_length = a * spacing + 4 * mat_thickness
        tige_radius = spacing * rel_width / 100.0 / 2.0
        file_scad.write('difference(){\n')
        file_scad.write('    union(){\n')
        file_scad.write('        sphere({});\n'.format(spacing * 0.75))
        file_scad.write('        cylinder(h={} , r = {}, center = true);\n'.format(tige_length, tige_radius))
        file_scad.write('        rotate([90,0,0]){\n')
        file_scad.write('            cylinder(h={} , r = {}, center = true);\n'.format(tige_length, tige_radius))
        file_scad.write('        }\n')
        file_scad.write('        rotate([0,90,0]){\n')
        file_scad.write('            cylinder(h={} , r = {}, center = true);\n'.format(tige_length, tige_radius))
        file_scad.write('        }\n')
        file_scad.write('    }\n')
        file_scad.write('    translate([0, 0, {}]){{\n'.format(-(tige_length + 1)/2.0))
        file_scad.write('        cube([{0}, {0}, {0}],true);\n'.format(tige_length + 1))
        file_scad.write('    }\n')
        file_scad.write('}\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a 3D maze defined by 2D mazes cut out of cube''s faces. Save faces to SVG file and 6ways node to navigate to SCAD files.')
    parser.add_argument('--n', '--size', type=int, default=5, help='Maze size (default: 5)')
    parser.add_argument('--branching', type=float, default=0.01, help='Branching probability (default: 0.01)')
    parser.add_argument('--svg', type=str, default='./maze.svg', help='Output SVG filename (default: ./maze.svg)')
    parser.add_argument('--scad', type=str, default='./node.scad', help='Output SCAD filename (default: ./node.scad)')
    parser.add_argument('--spacing', type=float, default=10, help='Corridor spacing in mm (default: 10)')
    parser.add_argument('--width', type=float, default=70, help='Relative corridor width in percent (default: 70)')
    parser.add_argument('--thickness', type=float, default=3, help='Material thickness in mm (default: 3)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')

    args = parser.parse_args()
    
    maze_size = args.n
    branching = args.branching
    svgfilename = args.svg
    scadfilename = args.scad
    corridor_spacing = args.spacing
    corridor_width = args.width
    material_thickness = args.thickness
    verbose = args.verbose

    maze_gen = (False, None)
    while not maze_gen[0]:
        maze_gen = generate_one_try(maze_size, branching, verbose=verbose)
    
    save2svg(svgfilename, corridor_spacing, corridor_width, material_thickness, maze_gen[1])

    save_6ways_node(scadfilename, corridor_spacing, corridor_width, material_thickness, maze_gen[1])
    
    if verbose:
        print('Succes' \
        'nMaze size: {}, branching: {}, SVG file: {}, SCAD file: {}, spacing: {}mm, relative width: {}%, material thickness: {}mm'\
            .format(maze_size, branching, svgfilename, scadfilename, corridor_spacing, corridor_width, material_thickness))
    else:
        print(f"Success: output saved to {svgfilename} and {scadfilename}")