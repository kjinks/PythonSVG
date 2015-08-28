"""
Ken Jinks
File: PythonSVGWrapper.py
July 30 2015

This file contains a wrapper for the SVG XML specification.
"""
import math
import random
from subprocess import check_output
import xml.etree.ElementTree as ET
import colorsys
import sys


ERROR = "error"

def clamp(mini, x, maxi):
    return max(mini, min(x, maxi)) 

def wrap(mini, x, maxi):    
    dif = maxi - mini
    
    return (x % dif) + mini

"""
multiply two matrices
https://www.youtube.com/watch?v=JSZC2vfa47I
Published on Jul 27, 2012
This tutorial presents some very useful python codes based on lists.
"""
def multi(x, y):
    d = []
    i = 0
    
    while i < len(x):
        j = 0
        e = []
        while j < len(y[0]):
            k = 0
            r = 0
            while k < len(x[0]):
                r += x[i][k] * y[k][j]
                k += 1
            j += 1
            e.append(r)
        d.append(e)
        i += 1
        
    return d

"""
class transform2D

This class maintains a transformation matrix
at initialization it is the identity matrix and each
method will transform the matrix accordingly.

There is also a stack where the current matrix can be
pushed and popped.

An svg transformation matrix string can be produced
by calling the svgOut method.

https://en.wikipedia.org/wiki/File:2D_affine_transformation_matrix.svg
"""
class transform2D:    
    def __init__(self):
        self.matrix = [
                       [1, 0, 0],
                       [0, 1, 0],
                       [0, 0, 1]
                      ]
        self.stack  = []
    
    #push the current matrix onto the stack
    def push(self):
        self.stack.append(self.matrix)
    
    #pop the last matrix from the stack 
    def pop(self):
        try:
            self.matrix = self.stack.pop()
        except:
            print("stack underflow in matrix transform")
            
    #get the svg matrix transform string
    def svgOut(self):
        a = str(self.matrix[0][0])
        c = str(self.matrix[0][1])
        e = str(self.matrix[0][2])
        b = str(self.matrix[1][0])
        d = str(self.matrix[1][1])
        f = str(self.matrix[1][2])
        
        out = "matrix(" + a + "," + b + "," + c + "," + d + "," + e + "," + f + ")"
        
        return out
        
    def translate(self, x, y):
        matrix = [
                  [1, 0, x],
                  [0, 1, y],
                  [0, 0, 1]
                 ]
                 
        self.matrix = multi(self.matrix, matrix)
        return self.matrix

    def scale(self, w, h):
        matrix = [
                  [w, 0, 0],
                  [0, h, 0],
                  [0, 0, 1]
                 ]
                 
        self.matrix = multi(self.matrix, matrix)
        return self.matrix
    
    def rotate(self, theta):
        s = math.sin(theta)
        c = math.cos(theta)
        
        matrix = [
                  [ c, s, 0],
                  [-s, c, 0],
                  [ 0, 0, 1]
                 ]
                 
        self.matrix = multi(self.matrix, matrix)
        return self.matrix
        
    def shearX(self, a):
        matrix = [
                  [1, a, 0],
                  [0, 1, 0],
                  [0, 0, 1]
                 ]
                 
        self.matrix = multi(self.matrix, matrix)
        return self.matrix
    
    def shearY(self, a):
        matrix = [
                  [1, 0, 0],
                  [a, 1, 0],
                  [0, 0, 1]
                 ]
                 
        self.matrix = multi(self.matrix, matrix)
        return self.matrix
    
    def reflectO(self):
        matrix = [
                  [-1,  0, 0],
                  [ 0, -1, 0],
                  [ 0,  0, 1]
                 ]
                 
        self.matrix = multi(self.matrix, matrix)
        return self.matrix
        
    def reflectX(self):
        matrix = [
                  [1,  0, 0],
                  [0, -1, 0],
                  [0,  0, 1]
                 ]
                 
        self.matrix = multi(self.matrix, matrix)
        return self.matrix
    
    def reflectY(self):
        matrix = [
                  [-1, 0, 0],
                  [ 0, 1, 0],
                  [ 0, 0, 1]
                 ]
                 
        self.matrix = multi(self.matrix, matrix)
        return self.matrix
    
class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        
    def __str__(self):
        s = str(self.x) + "," + str(self.y)
        return s
     
class Line:
    def __init__(self, p1=Point(), p2=Point()):
        self.p1 = p1
        self.p2 = p2
    
    def polar(self, angle=0, radius=0):
        newP2   = Point()
        newP2.x = (math.cos(angle) * radius) + self.p1.x
        newP2.y = (math.sin(angle) * radius) + self.p1.x
        
        self.p2 = newP2
        return self.p2
    
    def __str__(self):
        s = str(self.p1) + " " + str(self.p2)

"""
class DNA

This class represents 'genetic' data
The DNA sequence length, the number of base pairs (AMINOS) and chromosome length are all
analogous to the biological namesake.

-The DNA sequence is a list of numbers in the range 0 to numAminos - 1.
-When data is read from the sequence the chromeLength determines how many base pairs are read
-The base pairs together are read as a base n number, where n = numAmino, the number is normalized between 0-1

"""
class DNA:
    def __init__(self, length = 100, seed = 666, chromoLength = 5, numAmino = 256):
        self.numAmino     = 256
        self.seed         = seed
        self.index        = 0
        self.chromoLength = chromoLength
        self.sequence     = []
        
        random.seed(self.seed)
        
        for i in range(length):
            amino = random.randrange(self.numAmino)
            self.sequence.append(amino)
    
    #reads a section (chromosome) of the sequence as a base n number and normalizes it to between 0-1
    #index is where in the sequence it is read, length is how many base pairs are in the chromosome
    def read(self, index = 0, length = 5):
        result = 0
        
        seqLength = len(self.sequence)
        
        #calc base n number
        for i in range(length):
            amino = self.sequence[ (self.index + i) % seqLength ]
            
            result += amino * pow(self.numAmino, i)
        
        #normalize result to be in range 0-1
        result = result / pow(self.numAmino, length)
        
        return result
    
    #reads the next section (chromosome) and shifts the index to point to the next chromosome
    def next(self):
        result = self.read(self.index, self.chromoLength) 
        
        seqLength = len(self.sequence)
        self.index = (self.index + self.chromoLength) % seqLength
        
        return result
        
    def setIndex(self, newIndex = 0):
        self.index = newIndex
    
    def getIndex(self):
        return self.index
    
class Colour:
    def __init__(self, r = 0.0, b = 0.0, g = 0.0):
        self.r = r
        self.g = g
        self.b = b
        
    def hex(self):
        red   = int(clamp(0, self.r * 255, 255))
        blue  = int(clamp(0, self.b * 255, 255))
        green = int(clamp(0, self.g * 255, 255))
        
        hRed = hex(red)[2:]
        
        if len(hRed) < 2:
            hRed = "0" + hRed
        
        hGreen = hex(green)[2:]
        
        if len(hGreen) < 2:
            hGreen = "0" + hGreen
        
        hBlue = hex(blue)[2:]
        
        if len(hBlue) < 2:
            hBlue = "0" + hBlue
        
        hRGB = '#' + hRed + hGreen + hBlue
        return hRGB
    
    
    def setHLS(self, h = 0.0, l = 0.0, s = 0.0):
        rgb = colorsys.hls_to_rgb(h, l, s)
        
        self.r = rgb[0]
        self.g = rgb[1]
        self.b = rgb[2]
                
        return rgb
    
    def getHLS(self):
        hls = colorsys.rgb_to_hls(self.r, self.g, self.b)
        
        return hls
    
    def setHSV(self, h = 0.0, s = 0.0, v = 0.0):
        rgb = colorsys.hsv_to_rgb(h, s, v)
        
        self.r = rgb[0]
        self.g = rgb[1]
        self.b = rgb[2]
        
        return rgb
    
    def getHSV(self):
        hsv = colorsys.rgb_to_hsv(self.r, self.g, self.b)
        
        return hsv
        
    def setYIQ(self, y = 0.0, i = 0.0, q = 0.0):
        rgb = colorsys.yiq_to_rgb(y, i, q)
        
        self.r = rgb[0]
        self.g = rgb[1]
        self.b = rgb[2]
        
        return rgb
        
    def getYIQ(self):
        yiq = colorsys.rgb_to_yiq(self.r, self.g, self.b)
        
        return yiq
    
    def getRGB(self):
        return (self.r, self.g, self.b)
"""
class Palette

this class takes a DNA object and produces variation of a given colour
    -the colours are based on a triad relationship, 
    -the width of the triad is determined by the degree
    -the colour variation is a list of three floats which
determine the +/- ratio of [hue, lightness, saturation] 
    -the DNA object gives the arbitrary values when the method
getCol() is called

"""
class Palette:
    def __init__(self, dna = DNA(), col = Colour(), degree = (math.pi * (2/3)), variation = [0.05, 1.0, 1.0]):
        self.dna = dna
        
        self.prime = col
                               
        hls = col.getHLS()
        
        
        leftHue  = wrap(0.0, hls[0] + (degree / (2.0 * math.pi)), 1.0)
        rightHue = wrap(0.0, hls[0] - (degree / (2.0 * math.pi)), 1.0)
        
        
        self.left = Colour(col.r, col.g, col.b)
        self.left.setHLS(h = leftHue, l = hls[1], s = hls[2])
        
        self.right = Colour(col.r, col.g, col.b)
        self.right.setHLS(h = rightHue, l = hls[1], s = hls[2])
        
        self.variation = variation
    
    #The DNA object given when creating the instance gives
    #the values which selects an arbitrary colour
    def getCol(self):
        newCol = Colour()
        
        choice = self.dna.next() * 3000.0
        
        if choice < 1000:
            newCol = Colour(self.prime.r, self.prime.g, self.prime.b)
        elif choice > 2000:
            newCol = Colour(self.left.r, self.left.g, self.left.b)
        else:
            newCol = Colour(self.right.r, self.right.g, self.right.b)
            
        hls = newCol.getHLS()
        
        hVariant = (self.dna.next() * (self.variation[0] * 2.0)) - self.variation[0]
        h = wrap(0.0, hls[0] + hVariant, 1.0)
        
        lVariant = (self.dna.next() * (self.variation[1] * 2.0)) - self.variation[1]            
        l = wrap(0.0, hls[1] + lVariant, 1.0)
        
        sVariant = (self.dna.next() * (self.variation[2] * 2.0)) - self.variation[2]
        s = wrap(0.0, hls[2] + sVariant, 1.0)
        
        newCol.setHLS(h = h, l = l, s = s)
        
        return newCol
"""
class SVGWrap
this class builds an ElementTree of an SVG XML document

svg tags are added to the tree by passing the parent node and a dict of attributes

the main body of the svg document, the <svg> tag, is the root of the ElementTree
"""
class SVGWrap:       
    def body(self, attr = {
                           "width" : 100,
                           "height" : 100
                           }):
                           
        self.root = ET.Element('svg')
        self.tree._setroot(self.root)
        
        for i in attr:
            self.root.set(i, str(attr[i]))
        
        return self.root
    
    def __init__(self, attr = {
                               "width" : 100,
                               "height" : 100,
                               "version" : "1.1"
                               }):
        self.tree = ET.ElementTree()
        self.body(attr)
        self.defs = ET.SubElement(self.root, 'defs')
    """
    ________________________________
    SVG REFERENCE BUILDER
    """
    """
    def addToDefs(self, reference)
    
    this method adds an svg reference to the defs section of the svg
    document. SVG references are used to reuse objects, and create
    patterns and gradients.
    
    parameter:
        reference - reference is an instance of one of the below classes
        inheriting from the class Reference
    """
    def addToDefs(self, reference):
        #clone the instance
        tempRef = ET.fromstring(ET.tostring(reference.tree))
        
        self.defs.append(tempRef)
    
    
            
    """
    ________________________________
    GROUP
    """
    """
    def group(parent, attr={})
    
    this is the group node used for grouping svg elements
    
    Attributes:
        parent - this is the parent node of the group, <g>, tag
        attr   - this is a dict of attributes the tag will hold
            
    """
    def group(self, parent, attr = {
                                    "id"     : "main"                             
                                 }):
        g = ET.SubElement(parent, 'g')
        
        for i in attr:
            g.set(i, str(attr[i]))
        
        return g
   
    """
    ________________________________
    USE
    """
    def use(self, parent, reference, attr = {}):
        assert (isinstance(reference, Reference)), "Not an instance of Reference"
        
        u = ET.SubElement(parent, 'use')
        
        u.set('href', reference.url)
        
        for i in attr:
            u.set(i, str(attr[i]))
            
        return u
    """
    ________________________________
    BASIC SHAPES
    """    
    
    """
    def rect(parent, attr={})
    
    this is the rectangle node used for creating rectangles
    
    Attributes:
        parent - this is the parent node of the rectangle, <rect>, tag
        attr   - this is a dict of attributes the tag will hold
            
    """
    def rect(self, parent, attr = {
                                   "x"      : 0,
                                   "y"      : 0,
                                   "width"  : 0,
                                   "height" : 0,
                                   "rx"     : 0,
                                   "ry"     : 0
                                }):
        
        rect = ET.SubElement(parent, 'rect')
        
        for i in attr:
            rect.set(i, str(attr[i]))
        
        return rect
    
    """
    def circle(parent, attr={})
    
    this is the circle  node used for creating circles
    
    Attributes:
        parent - this is the parent node of the circle, <circle>, tag
        attr   - this is a dict of attributes the tag will hold
            
    """
    def circle(self, parent, attr = {
                                    "cx" : 0,
                                    "cy" : 0,
                                    "r"  : 0
                                  }):
                                  
        circle = ET.SubElement(parent, 'circle')
        
        for i in attr:
            circle.set(i, str(attr[i]))
        
        return circle
    
    """
    def ellipse(parent, attr={})
    
    this is the ellipse  node used for creating ellipses
    
    Attributes:
        parent - this is the parent node of the ellipse, <ellipse>, tag
        attr   - this is a dict of attributes the tag will hold
            
    """
    def ellipse(self, parent, attr = {
                                     "cx" : 0,
                                     "cy" : 0,
                                     "rx" : 0,
                                     "ry" : 0
                                   }):
        
        ellipse = ET.SubElement(parent, 'ellipse')
        
        for i in attr:
            ellipse.set(i, str(attr[i]))
            
        return ellipse
    
    """
    def line(parent, attr={})
    
    this is the line  node used for creating lines
    
    Attributes:
        parent - this is the parent node of the line, <line>, tag
        attr   - this is a dict of attributes the tag will hold
            
    """
    def line(self, parent, attr = {
                                  "x1" : 0,
                                  "y1" : 0,
                                  "x2" : 0,
                                  "y2" : 0
                                }):
        
        line = ET.SubElement(parent, 'line')
        
        for i in attr:
            line.set(i, str(attr[i]))
        
        return line
    
    """
    def polyline(parent, attr={}, points=[])
    
    this is the polyline node used for creating polylines
    
    Attributes:
        parent - this is the parent node of the polyline, <polyline>, tag
        attr   - this is a dict of attributes the tag will hold
        points = this is a list of Point()s the polyline will draw
            
    """
    def polyline(self, parent, attr = {}, points = [
                                                  Point()
                                                 ]):
                
        polyline = ET.SubElement(parent, 'polyline')
        
        for i in attr:
            polyline.set(i, str(attr[i]))
        
        pointStr = ""
        
        for p in points:
            pointStr += str(p) + " "
        
        polyline.set('points', pointStr)
        
        return polyline
    
    """
    class Path
    the path class contains methods for building up path data that is later
    added to the 'd' attribute of the path tag using the method tag
    """
    class Path:
        def __init__(self, pathData = ""):
                                  
            self.pathData = pathData
            
            self.commands = {
                            "moveRel"       : "m",
                            "moveAbs"       : "M", 
                            "close"         : "z",
                            "lineRel"       : "l",
                            "lineAbs"       : "L",
                            "horizRel"      : "h",
                            "horizAbs"      : "H",
                            "vertRel"       : "v",
                            "vertAbs"       : "V",
                            "bCurveRel"     : "c",
                            "bCurveAbs"     : "C",
                            "bSmoothRel"    : "s",
                            "bSmoothAbs"    : "S",
                            "qCurveRel"     : "q",
                            "qCurveAbs"     : "Q",
                            "qSmoothRel"    : "t",
                            "qSmoothAbs"    : "T",
                            "ellipticalRel" : "a",
                            "ellipticalAbs" : "A",
                           }
        
        def __str__(self):
            return self.pathData
            
        """
        def tag(parent, attr={})
        
        this is the path node used for creating paths, after path data has been
        created the path data is added to the 'd' attribute of the tag
        
        Attributes:
            parent - this is the parent node of the path, <path>, tag
            attr   - this is a dict of attributes the tag will hold
                
        """
        def tag(self, parent, attr = {
                                        "id" : "main"
                                    }):
            
            path = ET.SubElement(parent, 'path')
            
            for i in attr:
                path.set(i, str(attr[i]))
                
            path.set('d', str(self))

            return path
                
        def load(self, filename):
            f = ""
            result = ""
         
            try:
                f = open(filename, 'r')
                self.pathData += f.read()
                f.close()
                result = self.tag({"id" : filename})
            except:
                print("Could not find file: " + filename)
                result = ERROR
                
            return result
        
        def reset(self):
            self.pathData = ""
        
        """
        methods below for adding path data as represent in the SVG specification
        """
        #'lifts' pen to new location
        def move(self, isRelative = False, x = 0, y =  0):
            
            if isRelative:
                self.pathData += self.commands["moveRel"]
            else:
                self.pathData += self.commands["moveAbs"]
            
            
            p = Point(x, y)
            
            self.pathData += " " + str(p) + " "
        
        #connects the last point on the path to the first making a closed shape
        def close(self):
            self.pathData += self.commands["close"] + " "
        
        #draws a straight line from the current position to a new position
        def line(self, isRelative = False, x = 0, y = 0):
            
            if isRelative:
                self.pathData += self.commands["lineRel"]
            else:
                self.pathData += self.commands["lineAbs"]
            
            p = Point(x, y)
            
            self.pathData += " " + str(p) + " "
        
        #draws a horizontal line from the current position to a new x coordinate
        def horizontal(self, isRelative =  False, x = 0):
            
            if isRelative:
                self.pathData += self.commands["horizRel"]
            else:
                self.pathData += self.commands["horizAbs"]
            
            self.pathData += " " + str(x) + " "
        
        #draws a vertical line from the current position to the new y coordinate
        def vertical(self, isRelative =  False, y =  0):
            
            if isRelative:
                self.pathData += self.commands["vertRel"]
            else:
                self.pathData += self.commands["vertAbs"]
            
            self.pathData += " " + str(y) + " "
        
        #draws a bezier curve to position x, y; x1, y1, x2, y2 are the spline handles
        def bCurve(self, isRelative = False, x1 = 0, y1 = 0, x2 = 0, y2 = 0, x = 0, y = 0):
            
            if isRelative:
                self.pathData += self.commands["bCurveRel"]
            else:
                self.pathData += self.commands["bCurveAbs"]
            
            c1 = Point(x1, y1)
            c2 = Point(x2, y2)
            p  = Point(x, y)
            
            self.pathData += " " + str(c1) + " " + str(c2) + " " + str(p) + " "
        
        #draws a bezier curve to position x, y; x2, y2 is the control point
        def bSmooth(self, isRelative = False, x2 = 0, y2 = 0, x = 0, y = 0):
            
            if isRelative:
                self.pathData += self.commands["bSmoothRel"]
            else:
                self.pathData += self.commands["bSmoothAbs"]

            c2 = Point(x2, y2)
            p  = Point(x, y)
            
            self.pathData += " " + str(c2) + " " + str(p) + " "
        
        #draws a quadratic curve from the current point to x, y; x1, y1 is the control point
        def qCurve(self, isRelative = False, x1 = 0, y1 = 0, x = 0, y = 0):
            
            if isRelative:
                self.pathData += self.commands["qCurveRel"]
            else:
                self.pathData += self.commands["qCurveAbs"]
            
            c1 = Point(x1, y1)
            p  = Point(x, y)
            
            self.pathData += " " + str(c1) + " " + str(p) + " "
        
        #draws a quadratic curve to x, y
        def qSmooth(self, isRelative = False, x = 0, y = 0):
            
            if isRelative:
                self.pathData += self.commands["qSmoothRel"]
            else:
                self.pathData += self.commands["qSmoothAbs"]

            p  = Point(x, y)
            
            self.pathData += " " + str(p) + " "
        
        #draws an elliptical curve from the current point to x, y
        #rx, ry are the radii, 
        #arcF is a flag to choose the small or large curve
        #sweepF is the direction of the curve
        def elliptical(self, isRelative = False, rx = 0, ry = 0, rotate = 0, arcF = False, sweepF = False, x = 0, y = 0):
            
            if isRelative:
                self.pathData += self.commands["ellipticalRel"]
            else:
                self.pathData += self.commands["ellipticalAbs"]
            
            arcB   = "0"
            sweepB = "0"
            
            if arcF:
                arcB = "1"
            
            if sweepF:
                sweepB = "1"
            
            radius = Point(rx, ry)
            p  = Point(x, y)
            
            self.pathData += " " + str(radius) + " " + str(rotate) + " " + arcB + " " + sweepB + " " + str(p) + " "
    
    """
    ________________________________
    FILE OPERATIONS
    """
    #loadGroup takes an svg xml file (filename) and extracts the group
    #with the id matching id, groupName and returns the group
    #including the subelements of that group
    #If the group is not found or the file is not found this will
    #return None
    def loadGroup(self, filename, groupName):
        try:
            file = open(filename, 'r')
        except:
            print("Unable to open file " + filename)
            return None
        
        content = file.read()
        file.close()
            
        svgDoc = ET.fromstring(content)
        
        foundGroup = None
        
        for group in svgDoc.findall(".//*"):
             
            #remove namespace entries on tags
            checkNamespace = group.tag.split('}')
            
            if len(checkNamespace) > 1:
                group.tag = checkNamespace[1]

            id = group.get('id')
            
            if id == groupName:
                #remove any transforms on the group
                group.set('transform', "")
                foundGroup = group

        groupTree = ET.fromstring(ET.tostring(foundGroup)) 
        return groupTree
    
    def writeDoc(self, filename):
        try:
            self.tree.write(filename)
        except:
            print("Unable to write file: " + filename)
            
    def display(self):
        TEMP_FILE = r'temp.html'
        
        self.writeDoc(TEMP_FILE)
        
        check_output("start " + TEMP_FILE, shell=True)
    
    #appendGroup takes a group tree applies attributes (attr) to it and
    #appends it to the given parent element
    def appendGroup(self, parent, groupTree, attr = {}):
        
        tempGroup = ET.fromstring(ET.tostring(groupTree))
        
        for i in attr:
            tempGroup.set(i, str(attr[i]))
            
        parent.append(tempGroup)

"""
class Reference

all tags in the defs group of an svg document are references
this is a base class to define those references

the id is used as the url reference and should be unique 
"""
class Reference:
    referenceList = []
    
    def __init__(self, id, tag):
        assert (id not in Reference.referenceList), "Reference already defined :" + id
        
        Reference.referenceList.append(id)
        
        self.id = id
        self.root = ET.Element(tag)
        
        self.tree = ET.ElementTree()
        self.tree._setroot(self.root)
        
        self.id = id
        
    def url(self):
        return "url(" + str(self.id) + ")"
        
class GroupRef(Reference):
    def __init__(self, id, groupTree):
        Reference.__init__(self, id, 'g')
        
        self.root.set('id', id)
        
        self.tree = ET.fromstring(ET.tostring(groupTree))


class LinearGradient(Reference):
    def __init__(self, id, attr = {
                                   "x1" : 0,
                                   "y1" : 0,
                                   "x2" : 0,
                                   "y2" : 0                                           
                                  }):
        Reference.__init__(self, id, 'linearGradient')
                    
        self.root.set('id', id)
        
        for i in attr:
            self.root.set(i, attr[i])
    
    def stop(self, attr = {
                           "offset"       : "0%",
                           "stop-color"   : "black",
                           "stop-opacity" : 1.0
                          }):
        
        stop = ET.SubElement(self.root, 'stop')
        
        for i in attr:
            stop.set(i, attr[i])
    
class RadialGradient(Reference):
    def __init__(self, id, attr = {
                                   "cx" : 0,
                                   "cy" : 0,
                                   "r"  : 0,
                                   "fx" : 0,
                                   "fy" : 0
                                  }):
        Reference.__init__(self, id, 'radialGradient')
                    
        self.root.set('id', id)
        
        for i in attr:
            self.root.set(i, attr[i])
    
    def stop(self, attr = {
                           "offset"       : "0%",
                           "stop-color"   : "black",
                           "stop-opacity" : 1.0
                          }):
        
        stop = ET.SubElement(self.root, 'stop')
        
        for i in attr:
            stop.set(i, attr[i])
MANDALA_CANVAS_SIZE = 1000
class Mandala:
    def __init__(self, seed = 888):
        self.dna = DNA(length = 500, seed = seed)
    
    #svgDoc is an instance of SVGWrap and parent is the parent node in the document
    #attr is the attributes for this SVG group
    def circles(self, colourOn, svgDoc, parent, attr = {
                                                "id"           : "circleMandala",
                                                "stroke-width" : "5",
                                                "stroke"       : "black",
                                                "fill"         : "none"
                                             }):
        self.dna.setIndex(3) #arbitrary index just need result to be repeatable
        
        #dna = DNA(), col = Colour(), degree = (math.pi * (2/3)), variation = [0.05, 1.0, 1.0]):
        colour = Colour()
        colour.setHLS(self.dna.next(), self.dna.next(), 0.5)
        degree = (self.dna.next() * math.pi) / 8.0
        variation = [self.dna.next() * 0.05, self.dna.next() / 2.0, 0.0]
        palette = Palette(dna = self.dna, col = colour, degree = degree, variation = variation)
        
        mainGroup = svgDoc.group(parent = parent, attr = attr)
        
        #number of rings of circles 3 - 12
        numRings = int((self.dna.next() * 9.0)  + 3.0)
        
        #all number of circles are integer multiples 3 - 10
        harmonic = int((self.dna.next() * 5.0) + 3.0)
        
        dnaIndex = self.dna.getIndex()
        
        #calc data for each ring
        if colourOn:
            #colour
            for i in range(numRings):
                #num circles in ring 
                numCircs = int((self.dna.next() * 5.0) + 1.0) * harmonic
                
                #radius of circles in ring
                circRadii = self.dna.next() * (MANDALA_CANVAS_SIZE / 4.0)
                
                #radius of ring
                ringRadii = self.dna.next() * (MANDALA_CANVAS_SIZE / 4.0)
                
                angleCirc = (2.0 * math.pi) / numCircs
                
                #phase of ring, where circles are placed, either no phase shift or half phase
                ringPhase = 0.0 if (self.dna.next() < 0.5) else (0.5 * angleCirc)
                
                #stroke width
                strokeW = self.dna.next() * 5.0
                
                #colour
                colour = palette.getCol()
                
                #calc placement for circles
                for c in range(numCircs):
                    cx = math.sin(angleCirc * c) * ringRadii + (MANDALA_CANVAS_SIZE / 2.0)
                    cy = math.cos(angleCirc * c) * ringRadii + (MANDALA_CANVAS_SIZE / 2.0)
                    
                    svgDoc.circle(parent = mainGroup, attr = {"cx" : cx,
                                                           "cy" : cy,
                                                           "r"  : circRadii,
                                                           "fill" : colour.hex(),
                                                           "stroke-width" : strokeW,
                                                           "opacity" : 0.5
                                                          })
            
        #outlines
        self.dna.setIndex(dnaIndex)
        for i in range(numRings):
            #num circles in ring 
            numCircs = int((self.dna.next() * 5.0) + 1.0) * harmonic
            
            #radius of circles in ring
            circRadii = self.dna.next() * (MANDALA_CANVAS_SIZE / 4.0)
            
            #radius of ring
            ringRadii = self.dna.next() * (MANDALA_CANVAS_SIZE / 4.0)
            
            angleCirc = (2.0 * math.pi) / numCircs
            
            #phase of ring, where circles are placed, either no phase shift or half phase
            ringPhase = 0.0 if (self.dna.next() < 0.5) else (0.5 * angleCirc)
            
            #stroke width
            strokeW = self.dna.next() * 5.0
            
            #colour
            colour = palette.getCol()
            
            
            #calc placement for circles
            for c in range(numCircs):
                cx = math.sin(angleCirc * c) * ringRadii + (MANDALA_CANVAS_SIZE / 2.0)
                cy = math.cos(angleCirc * c) * ringRadii + (MANDALA_CANVAS_SIZE / 2.0)
                
                svgDoc.circle(parent = mainGroup, attr = {"cx" : cx,
                                                       "cy" : cy,
                                                       "r"  : circRadii,
                                                       "fill" : "none",
                                                       "stroke-width" : strokeW,
                                                       "stroke" : "black",
                                                       "opacity" : 0.5
                                                      })

            
"""
Testing
"""              
TEST_FILE = r'SVGWrapTest.html'

TEST_CIRCLE          = False
TEST_PATH            = False
TEST_DNA             = False
TEST_MANDALA_CIRCLES = False
TEST_COLOUR          = False
TEST_PALETTE         = False
TEST_LOAD_GROUP      = False
TEST_TRANSFORM2D     = True

def openTestFile():
    check_output("start " + TEST_FILE, shell=True)

class SVGWrapTesting:
    
    """
    testCircle(width, height)
    
    testCircle generates an svg document with circles arranged in a grid with varying radii and colour
    
    if the circles are present, then the SVGWrap.circle method works
    
    params:
        width - width of svg canvas
        height - height of svg canvas
        
    returns:
        svgOut - a string containing the svg document    
    """
    def testCircle(width = 800, height = 800):
        UNITS_WIDE = 16
        UNITS_TALL = 16
        
        UNITX = width  / UNITS_WIDE
        UNITY = height / UNITS_TALL

        svgOut = SVGWrap({"width" : width, "height" : height})

        #build a matrix of circles with random size and colour
        for crx in range(UNITS_WIDE):
            for cry in range(UNITS_TALL):
                #create random radius
                radius = UNITX * random.random()
                
                #colour will be green at the top left, random green looks pretty 
                #redder from left to right
                #bluer from top to bottom
                                
                h = crx / UNITS_WIDE + 0.1
                s = random.random() + 0.5
                v = cry / UNITS_TALL + 0.1
                
                opacity = random.random()
                
                col = Colour()
                
                col.setHSV(h, s, v)
                
                #calculate circle origin
                cx = crx * UNITX + (UNITX / 2.0)
                cy = cry * UNITY + (UNITY / 2.0)
                
                #build circle tag, add it to svg output string
                svgOut.circle( svgOut.root, {
                                          "cx"     : str(cx),
                                          "cy"     : str(cy),
                                          "r"      : radius,
                                          "fill"   : col.hex(),
                                          "stroke" : col.hex(),
                                          "opacity" : opacity
                                         })
        print(ET.dump(svgOut.root))
        
        svgOut.tree.write(TEST_FILE)
        
        return svgOut
   
    def testPath(width = 800, height = 800):
        UNITS_WIDE = 16
        UNITS_TALL = 16
        
        MIDX = width / 2
        MIDY = height / 2
        
        UNITX = width  / UNITS_WIDE
        UNITY = height / UNITS_TALL

        svgOut = ""
        
        #start svg output with header, svg body and a group for the paths
        svgOut = SVGWrap({"width" : width, "height" : height})
        
        #LINES GROUP___________________________
        lines = svgOut.group(svgOut.root, {"id": "lines"}) 
        
        testPath = SVGWrap.Path()
        
        testPath.reset()
        
        testPath.move(False, MIDX, MIDY)
        
        #build a matrix of lines with some spatial randomness
        for x in range(UNITS_WIDE):
            for y in range(UNITS_TALL):
               jitter = Point(random.randrange(UNITX), random.randrange(UNITY))
               testPath.line(False, (x * UNITX) + jitter.x, (y * UNITY) + jitter.y)
        
        #close the line to create a closed shape
        testPath.close()
        
        testPath.tag(lines, {
                            "fill"   : "black",
                            "stroke" : "red",
                            "stroke-width" : 5
                            })

        #BEZIER GROUP_______________________________
        testPath.reset()
                
        beziers = svgOut.group(svgOut.root, {"id": "beziers"}) 
        
        testPath.move(False, MIDX, MIDY)
        
        for y in range(UNITS_TALL):        
            for x in range(UNITS_WIDE):               
               jitter1 = Point(random.randrange(UNITX), random.randrange(UNITY))
               jitter2 = Point(random.randrange(UNITX), random.randrange(UNITY))
               jitter3 = Point(random.randrange(UNITX), random.randrange(UNITY))
               
               testPath.bCurve(False, (x * UNITX) + jitter1.x, (y * UNITY) + jitter1.y, (x * UNITX) + jitter2.x, (y * UNITY) + jitter2.y, (x * UNITX) + jitter3.x, (y * UNITY) + jitter3.y)
        
        #close the line to create a closed shape
        testPath.close()
        
        col = Colour(1.0, 0.5, 0.0)
        
        testPath.tag(beziers, {
                                "fill"         : col.hex(),
                                "stroke"       : "blue",
                                "stroke-width" : 2,
                                "opacity"      : "0.5"})

        #ELLIPSE GROUP_______________________________
        testPath.reset()
                
        elliptical  = svgOut.group(svgOut.root, {"id": "elliptical"}) 
        
        testPath.move(False, MIDX, MIDY)
        
        #rx = 0, ry = 0, rotate = 0, arcF = False, sweepF = False, x = 0, y = 0
        for i in range(4):
           rx = random.randrange(width)
           ry = random.randrange(height)
           rotate = random.randrange(360)
           arcF = True if random.randrange(100) > 50 else False
           sweepF = True if random.randrange(100) > 50 else False
           x = random.randrange(width)
           y = random.randrange(height)
           testPath.elliptical(False, rx, ry, rotate, arcF, sweepF, x, y)
        
        col = Colour(1.0, 0.0, 1.0)
        
        testPath.tag(elliptical, {"fill"         : "none",                                
                                "stroke"       : col.hex(),
                                "stroke-width" : 10,
                                "opacity"      : "0.5"})
        

        print(ET.dump(svgOut.root))
        
        svgOut.tree.write(TEST_FILE)
        
        return svgOut
    
def DNATesting():
    
    dna = DNA(seed = 111)
    
    for i in range(100):
        print(dna.next())
    
def MandalaCirclesTest():
    svgOut = SVGWrap({
                      "width"  : MANDALA_CANVAS_SIZE,
                      "height" : MANDALA_CANVAS_SIZE,
                     })
    
    seed = 1

    if len(sys.argv) > 1:
        try:
            seed = int(sys.argv[1])
        except:
            print('Unknown argument ' + sys.argv[1])
    
    mandala = Mandala(seed = seed)
    """
    svgOut.rect(svgOut.root, {"x" : 0,
                              "y" : 0,
                              "width" : MANDALA_CANVAS_SIZE,
                              "height" : MANDALA_CANVAS_SIZE,
                              "fill" : "black"
                              })
    """
    mandala.circles(colourOn = False, svgDoc = svgOut, parent = svgOut.root)
    
    print(ET.dump(svgOut.root))
    
    svgOut.tree.write(TEST_FILE)
    
    openTestFile()
    
    return svgOut

def ColourTest():
    testCols = [ 
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [0.5, 0.5, 0.5],
                [0.0, 0.0, 0.0]
               ]
    
    print("Testing colour class")
    
    for c in testCols:
        colour = Colour(c[0], c[1], c[2])
    
        print("Testing colour with RGB values" + str(c))
        print("Hex out: " + colour.hex())
        print("HLS    : " + str(colour.getHLS()))
        print("HSV    : " + str(colour.getHSV()))
        print("YIQ    : " + str(colour.getYIQ()))

def PaletteTest():
    ROWS    = 20
    COLUMNS = 20
    
    rowHeight = MANDALA_CANVAS_SIZE / ROWS
    colWidth  = MANDALA_CANVAS_SIZE / COLUMNS
    
    seed = 1

    if len(sys.argv) > 1:
        try:
            seed = int(sys.argv[1])
        except:
            print('Unknown argument ' + sys.argv[1])
    
    dna = DNA(seed = seed, length = 5000)
    
    svgOut = SVGWrap({
                  "width"  : MANDALA_CANVAS_SIZE,
                  "height" : MANDALA_CANVAS_SIZE
                  })
    
    group = svgOut.group(svgOut.root, {
                                        "id" : "paletteTest"
                                      })
    
    print("Testing palette class")
    
    
    colour = Colour(random.random(), random.random(), random.random())
    
    deg = (1.0 / 2.0) * math.pi
    var = [0.02, 0.5, 0.0]
    p = Palette(dna, colour, deg, var)
    
    for row in range(ROWS):
        x = row * rowHeight
        newCol = p.getCol()      
        for col in range(COLUMNS):
        
            newCol = p.getCol()

            
            y = col * colWidth
            svgOut.rect(group, {
                                "x"      : x,
                                "y"      : y,
                                "width"  : colWidth,
                                "height" : rowHeight,
                                "fill"   : newCol.hex(),
                                "stroke" : colour.hex(),
                                "stroke-width" : 8
                               })
                               
    svgOut.tree.write(TEST_FILE)
    
    openTestFile()
    
    return svgOut

GROUP_WIDTH = 1000
GROUP_FILE = "./Art/grid.svg"
GROUP_NAME = "grid"

def LoadGroupTest():
    svgOut = SVGWrap({ "width"  : GROUP_WIDTH,
                       "height" : GROUP_WIDTH 
                     })
    g = svgOut.loadGroup(GROUP_FILE, GROUP_NAME)
    
    svgOut.appendGroup(svgOut.root, g)
    
    svgOut.tree.write(TEST_FILE)
    
    openTestFile()
    
    return svgOut

def Transform2DTest():
    ROTATIONS = 18
    
    svgOut = SVGWrap({ "width"  : GROUP_WIDTH,
                       "height" : GROUP_WIDTH 
                     })
                     
    svgOut.rect(svgOut.root, {"x" : 0.0,
                              "y" : 0.0,
                              "width" : GROUP_WIDTH,
                              "height" : GROUP_WIDTH,    
                               "fill" : "red"})
                               
    g = svgOut.loadGroup(GROUP_FILE, GROUP_NAME)
    
    grid = GroupRef('grid', g)
    
    svgOut.addToDefs(grid)
    
    trans = transform2D()
    
    trans.push()
    
    rot = (2.0 * math.pi) / ROTATIONS
    
    for r in range(ROTATIONS):
        #trans.scale(0.5, 0.5)
        svgOut.use(svgOut.root, grid, {"transform" : trans.svgOut()})
        #trans.scale(2.0, 2.0)
        trans.translate((GROUP_WIDTH / 2.0), (GROUP_WIDTH / 2.0))
        trans.rotate(rot)    
        trans.translate(-(GROUP_WIDTH / 2.0), -(GROUP_WIDTH / 2.0))    
    
    svgOut.display()
    print(ET.tostring(svgOut.root))
    return svgOut
    
if TEST_CIRCLE:
    SVGWrapTesting.testCircle()
elif TEST_PATH:
    SVGWrapTesting.testPath()
elif TEST_DNA:
    DNATesting()
elif TEST_MANDALA_CIRCLES:
    MandalaCirclesTest()
elif TEST_COLOUR:
    ColourTest()
elif TEST_PALETTE:
    PaletteTest()
elif TEST_LOAD_GROUP:
    LoadGroupTest()
elif TEST_TRANSFORM2D:
    Transform2DTest()