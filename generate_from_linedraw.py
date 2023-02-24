__author__ = "Anton's Mindstorms Hacks"
import linedraw
from coord_file_tools import generate_csv, show_preview

IMG_SIZE = 1000
INPUT_IMG = "input/fh.jpg"
draw_hatch = False
polygonlist = linedraw.sketch(INPUT_IMG)

pointlist = [[0,0,0]] # start with pen up at 0,0
for poly in polygonlist:
    for point in poly:
        pointlist += [[point[0]/IMG_SIZE, point[1]/IMG_SIZE, 1]]
    pointlist[-1][2] = 0 # Lift pen at last point of poly

generate_csv(pointlist)
show_preview()