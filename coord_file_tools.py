from PIL import Image, ImageDraw

def generate_rtf(pointlist):
    # Output pointlist to files. One file for x's one for y's 
    # since ev3 can only read one number per line.
    # Lego EV3 brick wants files to have an rtf extension, 
    # formatted as regular txt files. With ascii 13 as newline.
    xfile = open('output/x.rtf', 'w')
    yfile = open('output/y.rtf', 'w')

    # Ev3 can't determine file length. We have to spell it out.
    xfile.write(str(len(pointlist))+chr(13)) 

    for x, y in pointlist:
        # write each number on a new line
        xfile.write("{:.4f}".format(float(x))+chr(13))
        yfile.write("{:.4f}".format(float(y))+chr(13))

    xfile.close()
    yfile.close()


def generate_csv(pointlist, out_file="output/coords.csv"):
    # Wite the pointlist also to a single .csv file for other use
    coordsfile = open(out_file, 'w')
    coordsfile.write(str(len(pointlist))+"\n")
    coordsfile.writelines([ ",".join([str(float(c)) for c in point])+"\n" 
                            for point in pointlist])
    coordsfile.close()


def show_preview(file_path = "output/coords.csv", save_preview=True, width=500, height=500, thickness=1):
    IMG_SIZE = min(width, height)
    coordsfile = open(file_path, 'r')
    file_body = coordsfile.readlines()
    pointlist = []
    polygonlist = []
    pen = 1
    for s_coord in file_body:
        coords = [float(c) for c in s_coord.split(",")]
        if len(coords) >= 2 and coords[0] >= 0:
            # We have two regular coordinates
            pointlist += [(coords[0] * IMG_SIZE, coords[1] * IMG_SIZE)]
        
        # When the first coordinate is -1.0 or we have three coordinates,
        # there is a pen command. 0 means up, 1 means down.
        if len(coords) == 2 and coords[0] < 0:
            # A negative coordinates means a pen change in some coords files.
            pen = int(coords[1])

        elif len(coords) == 3:
            # We have coordinates and a pen lifting or lowering command afterwards.
            pen = int(coords[2])

        # Pen goes up. Save our polygon and start collecting a new one.
        if pen == 0 and len(pointlist)>1:
            polygonlist += [pointlist]
            pointlist = []

    # Add the last polygon if it wasn't terminated by a pen up.
    if pointlist:
            polygonlist += [pointlist]
    coordsfile.close()


    im_result = Image.new("L", (width, height), color=200)
    draw = ImageDraw.Draw(im_result)
    for poly in polygonlist:
            draw.line(poly, fill=60, width=thickness)
    del draw

    im_result.show()
    if save_preview:
        im_result.save('output/preview.jpg')