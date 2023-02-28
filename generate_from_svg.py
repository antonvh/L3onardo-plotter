__author__ = "Anton's Mindstorms Hacks"

from svg import parse_path, Line
from coord_file_tools import generate_rtf, generate_csv, show_preview
import math

IMG_SIZE = 1000
SVG_FILE = "input/amh.svg"

def read_svg(image_file):
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
        # try:
        #     itemlist = filter(lambda x: x.attributes['id'].value != "borders", itemlist)
        # except:
        #     pass
        path = [s.attributes['d'].value for s in itemlist]

        svg_polyline_points = []
        actual = (0+0j)
        for p_ in path:
            p__ = parse_path(p_)
            for p in p__:
                start = p.point(0.)
                if not feq(actual, start):
                    svg_polyline_points.append(0)
                    svg_polyline_points.append(svg_point_to_coord(start))
                    svg_polyline_points.append(1)
                if (isinstance(p, Line)):
                    interv = 15
                else:
                    interv = 8
                length = p.length(error=1e-2)
                for i in range(interv, int(math.floor(length)), interv):
                    svg_polyline_points.append(svg_point_to_coord(p.point(i/length)))
                end = p.point(1.)
                svg_polyline_points.append(svg_point_to_coord(end))
                actual = end
        svg_polyline_points.append(0)

        # Convert rectangles to plottable polylines
        itemlist = xmldoc.getElementsByTagName('rect')

        for rect in itemlist:
            x = float(rect.attributes['x'].value) *10
            y = float(rect.attributes['y'].value) *10
            w = float(rect.attributes['width'].value) *10
            h = float(rect.attributes['height'].value) *10
            svg_polyline_points.append(0) # Pen up
            svg_polyline_points.append((x,y))
            svg_polyline_points.append(1) # Pen down
            svg_polyline_points.append((x+w,y))
            svg_polyline_points.append((x+w,y+h))
            svg_polyline_points.append((x,y+h))
            svg_polyline_points.append((x,y))

        def get_bounding_box(points):
            min_x, max_x = min([pix[0] for pix in points if type(pix) is not int]),max([pix[0] for pix in points if type(pix) is not int])
            min_y, max_y = min([pix[1] for pix in points if type(pix) is not int]),max([pix[1] for pix in points if type(pix) is not int])
            return (min_x, min_y, max_x-min_x, max_y-min_y)

        # Make sure the image fits on the canvas, normalize to (0...1) coordinates.
        (bbox_x, bbox_y, bbox_w, bbox_h) = get_bounding_box(svg_polyline_points)
        if bbox_w > bbox_h:
            best_scale = 1/bbox_w
            x_offset = 0
            y_offset = (bbox_w-bbox_h)/2*best_scale
        else:
            best_scale = 1/bbox_h
            x_offset = (bbox_h-bbox_w)/2*best_scale
            y_offset = 0
        
        pointlist = []
        for point in svg_polyline_points:
            if type(point) is int:
                # Starting a new curve. Left the pen with '-1' code.
                pointlist.append((-1, point))
            else:
                pointlist.append(((point[0]-bbox_x)*best_scale + x_offset,
                                   (point[1]-bbox_y)*best_scale + y_offset))
        return pointlist


if __name__ == '__main__':
    pointlist = read_svg(SVG_FILE)
    generate_csv(pointlist)
    generate_rtf(pointlist)
    show_preview()
    

