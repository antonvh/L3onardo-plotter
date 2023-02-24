__author__ = "Anton's Mindstorms Hacks"

# using pillow
from PIL import Image
from random import randrange
import time
import numpy as np
from coord_file_tools import generate_csv, generate_rtf, show_preview

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
size = min(w,h)


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
print("Generating the dots...")
t = time.time()
for i in range(NUM_POINTS):
    pointlist += [find_another_dark_pixel(pixels, w, h)]
print("Generated {} dots in: {} seconds".format(
    len(pointlist), 
    time.time() - t)
    )

# sort points randomish by vicinity #
print("Connecting the dots...")
t = time.time()

def get_coord(n, arr):
    return ([c/size for c in arr[n]],)

pointlist = np.array(pointlist)
best = 0
sorted_pointlist = []
while len(pointlist) > 1:
    p=pointlist[best]
    sorted_pointlist += get_coord(best, pointlist)
    pointlist = np.delete(pointlist, best, axis=0)
    
    # Calculate the square of the distances of p to all points in pointlist
    dists = ((pointlist-p)**2).sum(axis=1)
    # Closest point has the lowest squared distance.
    best = np.argmin(dists)

sorted_pointlist += get_coord(best, pointlist)
sorted_pointlist += get_coord(0, pointlist)

print("Connected the dots in:", time.time() - t, "seconds")

generate_csv(sorted_pointlist)
generate_rtf(sorted_pointlist)
show_preview(thickness=2)