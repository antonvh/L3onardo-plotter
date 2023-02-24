# Forked from linedraw.py Copyright (c) 2017 Lingdong Huang


from random import *
import math, random
import argparse
from PIL import Image, ImageDraw, ImageOps
import numpy as np

no_cv = True


def sortlines(lines):
    print("optimizing stroke sequence...")
    clines = lines[:]
    slines = [clines.pop(0)]
    while clines != []:
        x,s,r = None,1000000,False
        for l in clines:
            d = distsum(l[0],slines[-1][-1])
            dr = distsum(l[-1],slines[-1][-1])
            if d < s:
                x,s,r = l[:],d,False
            if dr < s:
                x,s,r = l[:],s,True

        clines.remove(x)
        if r == True:
            x = x[::-1]
        slines.append(x)
    return slines

def visualize(lines):
    import turtle
    wn = turtle.Screen()
    t = turtle.Turtle()
    t.speed(0)
    t.pencolor('red')
    t.pd()
    for i in range(0,len(lines)):
        for p in lines[i]:
            t.goto(p[0]*640/1024-320,-(p[1]*640/1024-320))
            t.pencolor('black')
        t.pencolor('red')
    turtle.mainloop()


F_Blur = {
    (-2,-2):2,(-1,-2):4,(0,-2):5,(1,-2):4,(2,-2):2,
    (-2,-1):4,(-1,-1):9,(0,-1):12,(1,-1):9,(2,-1):4,
    (-2,0):5,(-1,0):12,(0,0):15,(1,0):12,(2,0):5,
    (-2,1):4,(-1,1):9,(0,1):12,(1,1):9,(2,1):4,
    (-2,2):2,(-1,2):4,(0,2):5,(1,2):4,(2,2):2,
}
F_SobelX = {(-1,-1):1,(0,-1):0,(1,-1):-1,(-1,0):2,(0,0):0,(1,0):-2,(-1,1):1,(0,1):0,(1,1):-1}
F_SobelY = {(-1,-1):1,(0,-1):2,(1,-1):1,(-1,0):0,(0,0):0,(1,0):0,(-1,1):-1,(0,1):-2,(1,1):-1}


def appmask(IM,masks):
    PX = IM.load()
    w,h = IM.size
    NPX = {}
    for x in range(0,w):
        for y in range(0,h):
            a = [0]*len(masks)
            for i in range(len(masks)):
                for p in masks[i].keys():
                    if 0<x+p[0]<w and 0<y+p[1]<h:
                        a[i] += PX[x+p[0],y+p[1]] * masks[i][p]
                if sum(masks[i].values())!=0:
                    a[i] = a[i] / sum(masks[i].values())
            NPX[x,y]=int(sum([v**2 for v in a])**0.5)
    for x in range(0,w):
        for y in range(0,h):
            PX[x,y] = NPX[x,y]



def midpt(*args):
    xs,ys = 0,0
    for p in args:
        xs += p[0]
        ys += p[1]
    return xs/len(args),ys/len(args)

def distsum(*args):
    return sum([ ((args[i][0]-args[i-1][0])**2 + (args[i][1]-args[i-1][1])**2)**0.5 for i in range(1,len(args))])


#Perlin Noise
#Based on Javascript from p5.js (https://github.com/processing/p5.js/blob/master/src/math/noise.js)

PERLIN_YWRAPB = 4
PERLIN_YWRAP = 1<<PERLIN_YWRAPB
PERLIN_ZWRAPB = 8
PERLIN_ZWRAP = 1<<PERLIN_ZWRAPB
PERLIN_SIZE = 4095

perlin_octaves = 4
perlin_amp_falloff = 0.5

def scaled_cosine(i):
    return 0.5*(1.0-math.cos(i*math.pi))

perlin = None

def noise(x,y=0,z=0):
    global perlin
    if perlin == None:
        perlin = []
        for i in range(0,PERLIN_SIZE+1):
            perlin.append(random.random())
    if x<0:x=-x
    if y<0:y=-y
    if z<0:z=-z
    
    xi,yi,zi = int(x),int(y),int(z)
    xf = x-xi
    yf = y-yi
    zf = z-zi
    rxf = ryf = None
    
    r = 0
    ampl = 0.5
    
    n1 = n2 = n3 = None
    for o in range(0,perlin_octaves):
        of=xi+(yi<<PERLIN_YWRAPB)+(zi<<PERLIN_ZWRAPB)

        rxf = scaled_cosine(xf)
        ryf = scaled_cosine(yf)

        n1  = perlin[of&PERLIN_SIZE]
        n1 += rxf*(perlin[(of+1)&PERLIN_SIZE]-n1)
        n2  = perlin[(of+PERLIN_YWRAP)&PERLIN_SIZE]
        n2 += rxf*(perlin[(of+PERLIN_YWRAP+1)&PERLIN_SIZE]-n2)
        n1 += ryf*(n2-n1)

        of += PERLIN_ZWRAP
        n2  = perlin[of&PERLIN_SIZE]
        n2 += rxf*(perlin[(of+1)&PERLIN_SIZE]-n2)
        n3  = perlin[(of+PERLIN_YWRAP)&PERLIN_SIZE]
        n3 += rxf*(perlin[(of+PERLIN_YWRAP+1)&PERLIN_SIZE]-n3)
        n2 += ryf*(n3-n2)

        n1 += scaled_cosine(zf)*(n2-n1)

        r += n1*ampl
        ampl *= perlin_amp_falloff
        xi<<=1
        xf*=2
        yi<<=1
        yf*=2
        zi<<=1
        zf*=2
        
        if (xf>=1.0): xi+=1; xf-=1
        if (yf>=1.0): yi+=1; yf-=1
        if (zf>=1.0): zi+=1; zf-=1      
    return r
        
def noiseDetail(lod, falloff):
    if lod>0:perlin_octaves=lod
    if falloff>0:perlin_amp_falloff=falloff 
    
    
class LCG():
    def __init__(self):
        self.m = 4294967296.0
        self.a = 1664525.0
        self.c = 1013904223.0   
        self.seed = self.z = None
    def setSeed(self,val=None):
        self.z = self.seed = (math.random()*self.m if val == None else val) >> 0
    def getSeed(self):
        return self.seed
    def rand(self):
        self.z = (self.a * self.z + self.c) % self.m
        return self.z/self.m        
        
    
def noiseSeed(seed):
    lcg = LCG()
    lcg.setSeed(seed)
    perlin = []
    for i in range(0,PERLIN_SIZE+1):
        perlin.append(lcg.rand())
        
        

no_cv = False
export_path = "output/out.svg"
draw_contours = True
draw_hatch = True
show_bitmap = False
resolution = 1024
hatch_size = 16
contour_simplify = 3



def find_edges(IM):
    print("finding edges...")
    # if no_cv:
        #appmask(IM,[F_Blur])
    appmask(IM,[F_SobelX,F_SobelY])
    # else:
    #     im = np.array(IM) 
    #     im = cv2.GaussianBlur(im,(3,3),0)
    #     im = cv2.Canny(im,100,200)
    #     IM = Image.fromarray(im)
    return IM.point(lambda p: p > 128 and 255)  


def getdots(IM):
    print("getting contour points...")
    PX = IM.load()
    dots = []
    w,h = IM.size
    for y in range(h-1):
        row = []
        for x in range(1,w):
            if PX[x,y] == 255:
                if len(row) > 0:
                    if x-row[-1][0] == row[-1][-1]+1:
                        row[-1] = (row[-1][0],row[-1][-1]+1)
                    else:
                        row.append((x,0))
                else:
                    row.append((x,0))
        dots.append(row)
    return dots
    
def connectdots(dots):
    print("connecting contour points...")
    contours = []
    for y in range(len(dots)):
        for x,v in dots[y]:
            if v > -1:
                if y == 0:
                    contours.append([(x,y)])
                else:
                    closest = -1
                    cdist = 100
                    for x0,v0 in dots[y-1]:
                        if abs(x0-x) < cdist:
                            cdist = abs(x0-x)
                            closest = x0

                    if cdist > 3:
                        contours.append([(x,y)])
                    else:
                        found = 0
                        for i in range(len(contours)):
                            if contours[i][-1] == (closest,y-1):
                                contours[i].append((x,y,))
                                found = 1
                                break
                        if found == 0:
                            contours.append([(x,y)])
        for c in contours:
            if c[-1][1] < y-1 and len(c)<4:
                contours.remove(c)
    return contours


def getcontours(IM,sc=2):
    print("generating contours...")
    IM = find_edges(IM)
    IM1 = IM.copy()
    IM2 = IM.rotate(-90,expand=True).transpose(Image.FLIP_LEFT_RIGHT)
    dots1 = getdots(IM1)
    contours1 = connectdots(dots1)
    dots2 = getdots(IM2)
    contours2 = connectdots(dots2)

    for i in range(len(contours2)):
        contours2[i] = [(c[1],c[0]) for c in contours2[i]]    
    contours = contours1+contours2

    for i in range(len(contours)):
        for j in range(len(contours)):
            if len(contours[i]) > 0 and len(contours[j])>0:
                if distsum(contours[j][0],contours[i][-1]) < 8:
                    contours[i] = contours[i]+contours[j]
                    contours[j] = []

    for i in range(len(contours)):
        contours[i] = [contours[i][j] for j in range(0,len(contours[i]),8)]


    contours = [c for c in contours if len(c) > 1]

    for i in range(0,len(contours)):
        contours[i] = [(v[0]*sc,v[1]*sc) for v in contours[i]]

    for i in range(0,len(contours)):
        for j in range(0,len(contours[i])):
            contours[i][j] = int(contours[i][j][0]+10*noise(i*0.5,j*0.1,1)),int(contours[i][j][1]+10*noise(i*0.5,j*0.1,2))

    return contours


def hatch(IM,sc=16):
    print("hatching...")
    PX = IM.load()
    w,h = IM.size
    lg1 = []
    lg2 = []
    for x0 in range(w):
        for y0 in range(h):
            x = x0*sc
            y = y0*sc
            if PX[x0,y0] > 144:
                pass
                
            elif PX[x0,y0] > 64:
                lg1.append([(x,y+sc/4),(x+sc,y+sc/4)])
            elif PX[x0,y0] > 16:
                lg1.append([(x,y+sc/4),(x+sc,y+sc/4)])
                lg2.append([(x+sc,y),(x,y+sc)])

            else:
                lg1.append([(x,y+sc/4),(x+sc,y+sc/4)])
                lg1.append([(x,y+sc/2+sc/4),(x+sc,y+sc/2+sc/4)])
                lg2.append([(x+sc,y),(x,y+sc)])

    lines = [lg1,lg2]
    for k in range(0,len(lines)):
        for i in range(0,len(lines[k])):
            for j in range(0,len(lines[k])):
                if lines[k][i] != [] and lines[k][j] != []:
                    if lines[k][i][-1] == lines[k][j][0]:
                        lines[k][i] = lines[k][i]+lines[k][j][1:]
                        lines[k][j] = []
        lines[k] = [l for l in lines[k] if len(l) > 0]
    lines = lines[0]+lines[1]

    for i in range(0,len(lines)):
        for j in range(0,len(lines[i])):
            lines[i][j] = int(lines[i][j][0]+sc*noise(i*0.5,j*0.1,1)),int(lines[i][j][1]+sc*noise(i*0.5,j*0.1,2))-j
    return lines


def sketch(path):
    IM = None
    possible = [path,"images/"+path,"images/"+path+".jpg","images/"+path+".png","images/"+path+".tif"]
    for p in possible:
        try:
            IM = Image.open(p)
            break
        except FileNotFoundError:
            print("The Input File wasn't found. Check Path")
            exit(0)
            pass
    w,h = IM.size

    IM = IM.convert("L")
    IM=ImageOps.autocontrast(IM,10)

    lines = []
    if draw_contours:
        lines += getcontours(IM.resize((resolution//contour_simplify,resolution//contour_simplify*h//w)),contour_simplify)
    if draw_hatch:
        lines += hatch(IM.resize((resolution//hatch_size,resolution//hatch_size*h//w)),hatch_size)

    lines = sortlines(lines)
    if show_bitmap:
        disp = Image.new("RGB",(resolution,resolution*h//w),(255,255,255))
        draw = ImageDraw.Draw(disp)
        for l in lines:
            draw.line(l,(0,0,0),5)
        disp.show()

    f = open(export_path,'w')
    f.write(makesvg(lines))
    f.close()
    print(len(lines),"strokes.")
    print("done.")
    return lines


def makesvg(lines):
    print("generating svg file...")
    out = '<svg xmlns="http://www.w3.org/2000/svg" version="1.1">'
    for l in lines:
        l = ",".join([str(p[0]*0.5)+","+str(p[1]*0.5) for p in l])
        out += '<polyline points="'+l+'" stroke="black" stroke-width="2" fill="none" />\n'
    out += '</svg>'
    return out



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert image to vectorized line drawing for plotters.')
    parser.add_argument('-i','--input',dest='input_path',
        default='lenna',action='store',nargs='?',type=str,
        help='Input path')

    parser.add_argument('-o','--output',dest='output_path',
        default=export_path,action='store',nargs='?',type=str,
        help='Output path.')

    parser.add_argument('-b','--show_bitmap',dest='show_bitmap',
        const = not show_bitmap,default= show_bitmap,action='store_const',
        help="Display bitmap preview.")

    parser.add_argument('-nc','--no_contour',dest='no_contour',
        const = draw_contours,default= not draw_contours,action='store_const',
        help="Don't draw contours.")
       
    parser.add_argument('-nh','--no_hatch',dest='no_hatch',
        const = draw_hatch,default= not draw_hatch,action='store_const',
        help='Disable hatching.')

    parser.add_argument('--no_cv',dest='no_cv',
        const = not no_cv,default= no_cv,action='store_const',
        help="Don't use openCV.")


    parser.add_argument('--hatch_size',dest='hatch_size',
        default=hatch_size,action='store',nargs='?',type=int,
        help='Patch size of hatches. eg. 8, 16, 32')
    parser.add_argument('--contour_simplify',dest='contour_simplify',
        default=contour_simplify,action='store',nargs='?',type=int,
        help='Level of contour simplification. eg. 1, 2, 3')

    args = parser.parse_args()
    
    export_path = args.output_path
    draw_hatch = not args.no_hatch
    draw_contours = not args.no_contour
    hatch_size = args.hatch_size
    contour_simplify = args.contour_simplify
    show_bitmap = args.show_bitmap
    no_cv = args.no_cv
    sketch(args.input_path)
