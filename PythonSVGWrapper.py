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

ERROR = "error"

def clamp(mini, x, maxi):
    return max(mini, min(x, maxi)) 

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
    
class SVGWrap:
    """
    SVGWrap.attrDict(attr)
    This method takes a dictionary and produces a string
    based on the keys and values that can be inserted into
    an svg tag.
    ex.
    >>>print(SVGWrap.attrDict({"foo" : 2, "bar" : 6}))
    foo="2" bar="6"
    >>>
    """
    @staticmethod
    def attrDict(attr = {}):
        attrStr = ""
        for i in attr:
            attrStr += str(i) + '="' + str(attr[i]) + '" '
        
        return attrStr
            
    """
    __________________________________________
    SVG initialization and closing
    """
    
    tabCount = 0 #used to indent nested tags
    
    def header():
        docType = r'<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">' + '\n'
        return docType
    
    def bodyStart(attr = {
                          "width" : "100", 
                          "height" : "100", 
                          "version" : "1.1"
                         }):
                            
        attrStr = SVGWrap.attrDict(attr)
        
        openTag = ('\t' * SVGWrap.tabCount) + '<svg ' + attrStr + '>\n'
        
        SVGWrap.tabCount += 1
        
        return openTag
    
    def bodyEnd():
        SVGWrap.tabCount -= 1
        return ('\t' * SVGWrap.tabCount) + "</svg>\n"
        
    def groupStart(attr = {
                           "id"     : "main"                             
                          }):
        
        attrStr = SVGWrap.attrDict(attr)
        
        openTag = ('\t' * SVGWrap.tabCount) + '<g ' + attrStr + '>\n'
        
        SVGWrap.tabCount += 1
        
        return openTag
    
    def groupEnd():
        SVGWrap.tabCount -= 1
        return ('\t' * SVGWrap.tabCount) + "</g>\n"
    
    """
    PAINT
    """
    def rgb(r = 0.0, g = 0.0, b = 0.0):
        red   = int(clamp(0, r * 255, 255))
        blue  = int(clamp(0, b * 255, 255))
        green = int(clamp(0, g * 255, 255))
        
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
        
    """
    ________________________________
    BASIC SHAPES
    """    
    def rect(attr = {
                       "x"      : 0,
                       "y"      : 0,
                       "width"  : 0,
                       "height" : 0,
                       "rx"     : 0,
                       "ry"     : 0
                    }):
        attrStr = SVGWrap.attrDict(attr)
        
        tag = ('\t' * SVGWrap.tabCount) + '<rect ' + attrStr + " />\n"
        return tag
        
    def circle(attr = {
                        "cx" : 0,
                        "cy" : 0,
                        "r"  : 0
                      }):
        attrStr = SVGWrap.attrDict(attr)
        
        tag = ('\t' * SVGWrap.tabCount) + '<circle ' + attrStr + " />\n"
        return tag
                    
    def ellipse(attr = {
                         "cx" : 0,
                         "cy" : 0,
                         "rx" : 0,
                         "ry" : 0
                       }):
        attrStr = SVGWrap.attrDict(attr)
        
        tag = ('\t' * SVGWrap.tabCount) + '<ellipse ' + attrStr + " />\n"
        return tag
    
    def line(attr = {
                      "x1" : 0,
                      "y1" : 0,
                      "x2" : 0,
                      "y2" : 0
                    }):
        attrStr = SVGWrap.attrDict(attr)
        
        tag = ('\t' * SVGWrap.tabCount) + '<line ' + attrStr + " />\n"
        return tag
    
    def polyline(attr = {}, points = [
                                      Point()
                                     ]):
    
        attrStr = SVGWrap.attrDict(attr)
        
        pointStr = ' points="'
        
        for p in points:
            pointStr += str(p) + " "
            
        pointStr += '"'
        
        tag = ('\t' * SVGWrap.tabCount) + '<polyline ' + attrStr + pointStr + ' />\n'
        return tag
        
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
        
        def tag(self, attr = {
                                "id" : "main"
                            }):
                            
            attrStr = SVGWrap.attrDict(attr)
            
            tagStr = ('\t' * SVGWrap.tabCount) + '<path d="' + str(self) + '" ' + attrStr + '/>\n'
            
            return tagStr
                
        def load(self, filename):
            f = ""
            result = ""
            
            try:
                f = open(filename, 'r')
                self.pathData += f.read()
                f.close()
                result = self.tag({"id" : "filename"})
            except:
                print("Could not find file: " + filename)
                result = ERROR
                
            return result
        
        def reset(self):
            self.pathData = ""
        
        def move(self, isRelative = False, x = 0, y =  0):
            
            if isRelative:
                self.pathData += self.commands["moveRel"]
            else:
                self.pathData += self.commands["moveAbs"]
            
            
            p = Point(x, y)
            
            self.pathData += " " + str(p) + " "
		
        def close(self):
            self.pathData += self.commands["close"] + " "
				
        def line(self, isRelative = False, x = 0, y = 0):
            
            if isRelative:
                self.pathData += self.commands["lineRel"]
            else:
                self.pathData += self.commands["lineAbs"]
            
            p = Point(x, y)
            
            self.pathData += " " + str(p) + " "
		
        def horizontal(self, isRelative =  False, x = 0):
            
            if isRelative:
                self.pathData += self.commands["horizRel"]
            else:
                self.pathData += self.commands["horizAbs"]
            
            self.pathData += " " + str(x) + " "
		
        def vertical(self, isRelative =  False, y =  0):
            
            if isRelative:
                self.pathData += self.commands["vertRel"]
            else:
                self.pathData += self.commands["vertAbs"]
            
            self.pathData += " " + str(y) + " "
            
        def bCurve(self, isRelative = False, x1 = 0, y1 = 0, x2 = 0, y2 = 0, x = 0, y = 0):
            
            if isRelative:
                self.pathData += self.commands["bCurveRel"]
            else:
                self.pathData += self.commands["bCurveAbs"]
            
            c1 = Point(x1, y1)
            c2 = Point(x2, y2)
            p  = Point(x, y)
            
            self.pathData += " " + str(c1) + " " + str(c2) + " " + str(p) + " "
            
        def bSmooth(self, isRelative = False, x2 = 0, y2 = 0, x = 0, y = 0):
            
            if isRelative:
                self.pathData += self.commands["bSmoothRel"]
            else:
                self.pathData += self.commands["bSmoothAbs"]

            c2 = Point(x2, y2)
            p  = Point(x, y)
            
            self.pathData += " " + str(c2) + " " + str(p) + " "
            
        def qCurve(self, isRelative = False, x1 = 0, y1 = 0, x = 0, y = 0):
            
            if isRelative:
                self.pathData += self.commands["qCurveRel"]
            else:
                self.pathData += self.commands["qCurveAbs"]
            
            c1 = Point(x1, y1)
            p  = Point(x, y)
            
            self.pathData += " " + str(c1) + " " + str(p) + " "
            
        def qSmooth(self, isRelative = False, x = 0, y = 0):
            
            if isRelative:
                self.pathData += self.commands["qSmoothRel"]
            else:
                self.pathData += self.commands["qSmoothAbs"]

            p  = Point(x, y)
            
            self.pathData += " " + str(p) + " "
		
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

class SVGMandala:
    
    def reset(self):
        self.svgOut = ""
    
    def __init__(self):
        self.reset()
        
    def wave(self, origin, numWaves, weight, radius1, radius2):
        result = SVGWrap.Path()
        
        p = Point()
        
        w = (2.0 * math.pi) / numWaves
        
        r = (radius1 + radius2) / 2.0
        
        a = (radius1 - radius2)
        
        for i in range(numWaves):
            radius = (math.sin(i * w) * a) + r
            p.x = math.sin(i * w) * radius
            p.y = math.cos(i * w) * radius
            
            if i == 0:
                result.move(False, p.x, p.y)
            else:
                result.line(False, p.x, p.y)
                
        result.close()
"""
Testing
"""              
TEST_FILE = r'SVGWrapTest.html'

class SVGWrapTesting:
    def writeTest(content):
        f = open(TEST_FILE, 'w')
        
        f.write(content)        
        f.close()
    
    def openTest():
        check_output('start ' + TEST_FILE, shell=True)
    
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

        svgOut = ""
        
        #start svg output with header, svg body and a group for the circles
        svgOut += SVGWrap.header()
        svgOut += SVGWrap.bodyStart({"width" : width, "height" : height})
        svgOut += SVGWrap.groupStart({"id": "circles"}) 
        
        #build a matrix of circles with random size and colour
        for crx in range(UNITS_WIDE):
            for cry in range(UNITS_TALL):
                #create random radius
                radius = UNITX * random.random()
                
                #colour will be green at the top left, random green looks pretty 
                #redder from left to right
                #bluer from top to bottom
                                
                r = crx / UNITS_WIDE + 0.1
                g = random.random() + 0.5
                b = cry / UNITS_TALL + 0.1
                
                col = SVGWrap.rgb(r, g, b)
                
                #calculate circle origin
                cx = crx * UNITX + (UNITX / 2.0)
                cy = cry * UNITY + (UNITY / 2.0)
                
                #build circle tag, add it to svg output string
                svgOut += SVGWrap.circle({
                                          "cx"     : str(cx),
                                          "cy"     : str(cy),
                                          "r"      : radius,
                                          "fill"   : col,
                                          "stroke" : col
                                         })
        
        #close the group and end the svg body
        svgOut += SVGWrap.groupEnd()
        svgOut += SVGWrap.bodyEnd()
        
        print(svgOut)
        
        SVGWrapTesting.writeTest(svgOut)
        SVGWrapTesting.openTest()
        
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
        svgOut += SVGWrap.header()
        svgOut += SVGWrap.bodyStart({"width" : width, "height" : height})
        
        #LINES GROUP___________________________
        svgOut += SVGWrap.groupStart({"id": "lines"}) 
        
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
        
        svgOut += testPath.tag({
                                "fill"   : "black",
                                "stroke" : "red",
                                "stroke-width" : 5
                                })
        
        #close the group 
        svgOut += SVGWrap.groupEnd()
        
        #BEZIER GROUP_______________________________
        testPath.reset()
                
        svgOut += SVGWrap.groupStart({"id": "beziers"}) 
        
        testPath.move(False, MIDX, MIDY)
        
        for y in range(UNITS_TALL):        
            for x in range(UNITS_WIDE):               
               jitter1 = Point(random.randrange(UNITX), random.randrange(UNITY))
               jitter2 = Point(random.randrange(UNITX), random.randrange(UNITY))
               jitter3 = Point(random.randrange(UNITX), random.randrange(UNITY))
               
               testPath.bCurve(False, (x * UNITX) + jitter1.x, (y * UNITY) + jitter1.y, (x * UNITX) + jitter2.x, (y * UNITY) + jitter2.y, (x * UNITX) + jitter3.x, (y * UNITY) + jitter3.y)
        
        #close the line to create a closed shape
        testPath.close()
        
        svgOut += testPath.tag({
                                "fill"         : SVGWrap.rgb(1.0, 0.5, 0.0),
                                "stroke"       : "blue",
                                "stroke-width" : 2,
                                "opacity"      : "0.5"})
        
        #close the group 
        svgOut += SVGWrap.groupEnd()
        
        #ELLIPSE GROUP_______________________________
        testPath.reset()
                
        svgOut += SVGWrap.groupStart({"id": "beziers"}) 
        
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
        
        svgOut += testPath.tag({"fill"         : "none",                                
                                "stroke"       : SVGWrap.rgb(1.0, 0.0, 1.0),
                                "stroke-width" : 10,
                                "opacity"      : "0.5"})
        
        #close the group 
        svgOut += SVGWrap.groupEnd()
                
        svgOut += SVGWrap.bodyEnd()
        
        print(svgOut)
        
        SVGWrapTesting.writeTest(svgOut)
        SVGWrapTesting.openTest()
        
        return svgOut
              
SVGWrapTesting.testPath()