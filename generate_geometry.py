__author__ = "Anton's Mindstorms Hacks"

from math import sin, cos, pi
from PIL import Image, ImageDraw


NUM_POINTS = 150
PREVIEW_SIZE = 500
CIRCLE = 1
SQUARE = 2
GRID = 3
mode = SQUARE

pointlist = []

if mode == CIRCLE:
    # Generate a list of (x,y) coordinates that make up a circle.
    radius = PREVIEW_SIZE * 0.4
    offset = PREVIEW_SIZE / 2
    step = 2*pi/NUM_POINTS
    pointlist = [(cos(step*p) * radius + offset, 
                  sin(step * p) * radius + offset) 
                 for p in range(NUM_POINTS + 1)]

if mode == GRID:
    # Generate a list of coordinates that make a line grid.

    step = PREVIEW_SIZE//10
    for x in range(0, PREVIEW_SIZE + step, 2 * step):
        # Go down
        for y in range(0, PREVIEW_SIZE + step, step):
            pointlist += [(x, y)]
        # Go back up if there's enough space
        if x + step <= PREVIEW_SIZE:
            for y in range(PREVIEW_SIZE, 0 - step, -step):
                pointlist += [(x+step, y)]

    for y in range(PREVIEW_SIZE, -1, -2 * step):
        # Go left
        for x in range(PREVIEW_SIZE,  -1, -step):
            pointlist += [(x, y)]
        # Go back right
        if y - step >= 0:
            for x in range(0, PREVIEW_SIZE+1, step):
                pointlist += [(x, y-step)]

if mode == SQUARE:
    steps = 10
    margin = PREVIEW_SIZE // 10
    step = (PREVIEW_SIZE - 2*margin) // steps

    # Left side
    for i in range(steps):
        pointlist += [(margin, margin+i*step)]

    # Bottom side
    for i in range(steps):
        pointlist += [(margin + i * step, margin + steps * step)]

    # Right side side
    for i in range(steps, 0, -1):
        pointlist += [(margin + steps * step, margin + i * step)]

    # Bottom side
    for i in range(steps, 0, -1):
        pointlist += [(margin + i * step, margin)]

    # Go back to the top left of the square
    pointlist += [(margin, margin)]


# Preview the result
# New empty image
im_result = Image.new("L", (PREVIEW_SIZE, PREVIEW_SIZE), color=200)
# New drawing object
draw = ImageDraw.Draw(im_result)
draw.line(pointlist, fill=20)
del draw
# Showtime
im_result.show()
im_result.save('output/preview.jpg')

pointlist.insert(0, [-1*PREVIEW_SIZE, 0])  # Lift pen before starting
pointlist.insert(2, (-1*PREVIEW_SIZE, 1*PREVIEW_SIZE))  # Lower pen befor first point

# Output pointlist to files. One file for x's one for y's 
# since ev3 can only read one number per line.
# Lego EV3 brick wants files to have an rtf extension, 
# formatted as regular txt files. With ascii 13 as newline.
xfile = open('output/x.rtf', 'w')
yfile = open('output/y.rtf', 'w')

# Ev3 can't determine file length. We have to spell it out.
xfile.write(str(len(pointlist))+chr(13)) 

for x, y in pointlist:
    # Normalize the point cloud to 0.0 - 1.0 
    # write each number on a new line
    xfile.write("{:.4f}".format(float(x)/PREVIEW_SIZE)+chr(13))
    yfile.write("{:.4f}".format(float(y)/PREVIEW_SIZE)+chr(13))

xfile.close()
yfile.close()

# Wite the pointlist also to a single .csv file for other use
coordsfile = open('output/coords.csv','w')
coordsfile.write(str(len(pointlist))+"\n")
coordsfile.writelines([str(float(x)/PREVIEW_SIZE) +
                       ',' +
                       str(float(y)/PREVIEW_SIZE) +
                       '\n'
                       for x, y in pointlist])
coordsfile.close()
