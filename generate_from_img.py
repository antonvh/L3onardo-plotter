__author__ = "Anton's Mindstorms Hacks"

# using pillow
from PIL import Image, ImageDraw, ImageOps
from random import randrange
import time

# settings
NUM_POINTS = 15000
NUM_CLOSEST = 3000
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
good_enough = (w * 0.01) ** 2   # Within 1% of the image width is good enough

sorted_pointlist = [pointlist.pop(0)]
while len(pointlist) > 0:
    # get the next set of points (if that many are left)
    sublist = pointlist[:NUM_CLOSEST]
    closest_dist = (w * 2) ** 2
    test_point = sorted_pointlist[-1]
    for p in sublist:
        # calculate distance from the test point to the last point in the sorted point list
        distance = (p[0] - test_point[0]) ** 2 + (p[1] - test_point[1]) ** 2
        if distance < closest_dist:
            closest_dist = distance
            closest = p
            if distance < good_enough: 
                break
    pointlist.remove(closest)
    sorted_pointlist += [closest]

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
