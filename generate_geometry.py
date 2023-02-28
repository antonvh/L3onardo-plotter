__author__ = "Anton's Mindstorms Hacks"

from math import sin, cos, pi
from coord_file_tools import generate_csv, generate_rtf, show_preview

CIRCLE_POINTS = 100
SQUARE_SIDE_POINTS = 10
MARGIN = 0.1
CIRCLE = 1
SQUARE = 2
GRID = 3
mode = CIRCLE

pointlist = []

if mode == CIRCLE:
    # Generate a list of (x,y) coordinates that make up a circle.
    offset = 0.5 # Center offset from top left
    radius = offset - MARGIN
    divisions = 2*pi/CIRCLE_POINTS
    pointlist = [(sin(divisions*p) * radius + offset, 
                  -cos(divisions * p) * radius + offset) 
                 for p in range(CIRCLE_POINTS+1)]

if mode == GRID:
    # Generate a list of coordinates that make a line grid.

    divisions = 4
    for x in range(0, divisions, 2):
        # Go down
        for y in range(0, divisions+1):
            pointlist += [(x/divisions, y/divisions)]
        
        # Go back up
        for y in range(divisions, -1, -1):
            pointlist += [((x+1)/divisions, y/divisions)]
    
    pointlist += [(-1, 0)]
    pointlist += [(1,0)]
    pointlist += [(-1, 1)]

    for y in range(divisions, -1, -2):
        # Go left
        for x in range(divisions+1,  -1, -1):
            pointlist += [(x/divisions, y/divisions)]

        # Go back right
        for x in range(0, divisions+1):
            pointlist += [(x/divisions, (y-1)/divisions)]

if mode == SQUARE:
    divisions = (1-2*MARGIN) / SQUARE_SIDE_POINTS

    # Left side
    for i in range(SQUARE_SIDE_POINTS):
        pointlist += [(MARGIN, MARGIN+i*divisions)]

    # Bottom side
    for i in range(SQUARE_SIDE_POINTS):
        pointlist += [(MARGIN + i * divisions, MARGIN + SQUARE_SIDE_POINTS * divisions)]

    # Right side side
    for i in range(SQUARE_SIDE_POINTS, 0, -1):
        pointlist += [(MARGIN + SQUARE_SIDE_POINTS * divisions, MARGIN + i * divisions)]

    # Bottom side
    for i in range(SQUARE_SIDE_POINTS, 0, -1):
        pointlist += [(MARGIN + i * divisions, MARGIN)]

    # Go back to the top left of the square
    pointlist += [(MARGIN, MARGIN)]

pointlist.insert(0, (-1, 0))  # Lift pen before starting
pointlist.insert(2, (-1, 1))  # Lower pen befor first point

generate_csv(pointlist)
generate_rtf(pointlist)
show_preview()

