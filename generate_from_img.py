__author__ = "Anton's Mindstorms Hacks"

# using pillow
from PIL import Image, ImageDraw, ImageOps
from random import randrange
import time
import numpy as np

# settings
NUM_POINTS = 15000
# NUM_CLOSEST = 3000
MAX_BRIGHTNESS = 180    # Ignore pixels brighter than this
EXPONENT = 1           # Number between 1 and 3 to control grayscale curve
MAX_LOTTERY = 10        # A lower number means a tendency to pick more dark pixels
FILE_NAME = "input/anton.jpg"

# load image and convert to grayscale ("L")
im = Image.open(FILE_NAME).convert("L")
w, h = im.size
pixels = im.load()


# find NUM_POINTS points in dark areas and put them in pointlist#
def find_another_dark_pixel(img_px, img_w, img_h):
    x = randrange(img_w)
    y = randrange(img_h)
    px = img_px[x, y]
    if px > MAX_BRIGHTNESS:
        # bah. This pixel is too bright. Bring me another one!
        x, y = find_another_dark_pixel(img_px, img_w, img_h)
    else:
        # Now let's roll the dice. We want darker pixels to be more popular.
        if randrange(px + 1) ** EXPONENT > MAX_LOTTERY:
            # Oops. Bad luck for this pixel.
            x, y = find_another_dark_pixel(img_px, img_w, img_h)
    return x, y


pointlist = []

t = time.time()
for i in range(NUM_POINTS):
    pointlist += [find_another_dark_pixel(pixels, w, h)]
print("Generated dots in:", time.time() - t)
print("Connecting the dots...")

# sort points randomish by vicinity #
# Very lazy TSP. Slow too. :S
# good_enough = (w * 0.01) ** 2   # Within 1% of the image width is good enough
def get_coord(n, arr):
    return (tuple(arr[n]),)
pointlist = np.array(pointlist)
best = 0
sorted_pointlist = []
while len(pointlist) > 1:
    p=pointlist[best]
    sorted_pointlist += get_coord(best, pointlist)
    pointlist = np.delete(pointlist,best,axis=0)
    
    # get the next set of points (if that many are left)
    dists = np.sqrt(((pointlist-p)**2).sum(axis=1))
    best = np.argmin(dists)

sorted_pointlist += get_coord(0, pointlist)

# Preview: draw lines connecting sorted points
im_result = Image.new("L", im.size, color=200)
draw = ImageDraw.Draw(im_result)
draw.line(sorted_pointlist, fill=20, width=2)
del draw
im_result.show()
im_result.save('output/preview.jpg')

# output pointlist to files. One file for x's one for y's since ev3 can only read one number per line.
# Lego EV3 brick wants files to have an rtf extension, formatted as regular txt files. With ascii 13 as newline. :S
xfile = open('output/x.rtf', 'w')
yfile = open('output/y.rtf', 'w')

xfile.write(str(len(sorted_pointlist)) + chr(13))  # Ev3 can't determine file length. We have to spell it out.

for x, y in sorted_pointlist:
    # normalize the point cloud to 0.0 - 1.0 & write each number on a new line
    xfile.write("{:.4f}".format(float(x) / w) + chr(13))
    yfile.write("{:.4f}".format(float(y) / w) + chr(13))

xfile.close()
yfile.close()


# Now write it to a single file for Ev3dev
coordsfile = open('output/coords.csv', 'w')
coordsfile.write(str(len(sorted_pointlist)) + "\n")
coordsfile.writelines([str(float(x) / w) + ',' + str(float(y) / w) + '\n' for x, y in sorted_pointlist])
coordsfile.close()
