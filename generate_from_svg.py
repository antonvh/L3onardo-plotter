__author__ = "Anton's Mindstorms Hacks"

from svg import parse_path, Line
import math
from PIL import Image, ImageDraw

IMG_SIZE = 1000
SVG_FILE = "input/mfd2.svg"

def read_svg(image_file):
        # TODO: Also return the four corners of rects as points, not only paths.
        
        # Open simple svg
        # To remove transformations from svg and convert objects to path, use:
        # inkscape --verb=EditSelectAll --verb=ObjectToPath --verb=SelectionUnGroup --verb=FileSave --verb=FileClose --verb=FileQuit my_image.svg

        from xml.dom import minidom

        def svg_point_to_coord(svg_point):
            scale = 0.1
            ciblex = svg_point.real/scale
            cibley = svg_point.imag/scale
            return (ciblex, cibley)

        def feq(a, b):
            if abs(a-b) < 0.0001:
                return 1
            else:
                return 0

        xmldoc = minidom.parse(image_file)

        itemlist = xmldoc.getElementsByTagName('path')
        try:
            itemlist = filter(lambda x: x.attributes['id'].value != "borders", itemlist)
        except:
            pass
        path = [s.attributes['d'].value for s in itemlist]

        list_points = []
        actual = (0+0j)
        for p_ in path:
            p__ = parse_path(p_)
            for p in p__:
                start = p.point(0.)
                if not feq(actual, start):
                    list_points.append(0)
                    list_points.append(svg_point_to_coord(start))
                    list_points.append(1)
                if (isinstance(p, Line)):
                    interv = 15
                else:
                    interv = 3
                length = p.length(error=1e-2)
                for i in range(interv, int(math.floor(length)), interv):
                    list_points.append(svg_point_to_coord(p.point(i/length)))
                end = p.point(1.)
                list_points.append(svg_point_to_coord(end))
                actual = end
        list_points.append(0)
        return list_points


def fit_path(points):
        def get_bounding_box(points):
            min_x, max_x = min([pix[0] for pix in points if type(pix) is not int]),max([pix[0] for pix in points if type(pix) is not int])
            min_y, max_y = min([pix[1] for pix in points if type(pix) is not int]),max([pix[1] for pix in points if type(pix) is not int])
            return (min_x, min_y, max_x-min_x, max_y-min_y)

        # Make sure the image fits on the canvas, normalize to (0...1) coordinates.
        (bbox_x, bbox_y, bbox_w, bbox_h) = get_bounding_box(points)
        if bbox_w > bbox_h:
            best_scale = 1/bbox_w
            x_offset = 0
            y_offset = (bbox_w-bbox_h)/2*best_scale
        else:
            best_scale = 1/bbox_h
            x_offset = (bbox_h-bbox_w)/2*best_scale
            y_offset = 0
        
        new_points = []
        for point in points:
            if type(point) is int:
                # Starting a new curve. Left the pen with '-1' code.
                new_points.append((-1, point))
            else:
                new_points.append(((point[0]-bbox_x)*best_scale + x_offset,
                                   (point[1]-bbox_y)*best_scale + y_offset))
        return new_points


if __name__ == '__main__':
    pointlist = fit_path(read_svg(SVG_FILE))
    # print(pointlist)
    # Wite the pointlist also to a single .csv file for other use
    coordsfile = open('output/coords.csv', 'w')
    coordsfile.write(str(len(pointlist))+"\n")
    coordsfile.writelines([str(float(x)) +
                          ',' +
                           str(float(y)) +
                           '\n'
                           for x, y in pointlist])
    coordsfile.close()

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
        xfile.write("{:.4f}".format(float(x))+chr(13))
        yfile.write("{:.4f}".format(float(y))+chr(13))

    xfile.close()
    yfile.close()

    # Generate preview image
    coordsfile = open('output/coords.csv', 'r')
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
            pen = int(coords[1])
        elif len(coords) == 3:
            pen = int(coords[2])

        # Pen goes up. Save our polygon and start collecting a new one.
        if pen == 0 and len(pointlist)>1:
            polygonlist += [pointlist]
            pointlist = []

    # Add the last polygon if it wasn't terminated by a pen up.
    if pointlist:
            polygonlist += [pointlist]
    coordsfile.close()


    im_result = Image.new("L", (IMG_SIZE, IMG_SIZE), color=200)
    draw = ImageDraw.Draw(im_result)
    for poly in polygonlist:
            draw.line(poly, fill=60, width=1)
    del draw

    im_result.show()
    im_result.save('output/preview.jpg')

