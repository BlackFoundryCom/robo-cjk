"""
Copyright 2019 Black Foundry.

This file is part of Robo-CJK.

Robo-CJK is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Robo-CJK is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Robo-CJK.  If not, see <https://www.gnu.org/licenses/>.
"""
from mojo.drawingTools import *
from mojo.roboFont import *


class DesignFrameDrawer():

    def __init__(self, controller):
        self.c = controller

    def getEmRatioFrame(self, frame, w, h):
        charfaceW = w * (frame / 100)
        charfaceH = h * (frame / 100)
        x = (w - charfaceW) * .5
        y = (h - charfaceH) * .5
        return x, y, charfaceW, charfaceH

    def makeOvershoot(self, glyph, origin_x, origin_y, width, height, outSide, inSide):
        ox = origin_x - outSide
        oy = origin_y - outSide
        width += outSide
        height += outSide
        pen = glyph.getPen()
        pen.moveTo((ox, oy))
        pen.lineTo((ox + width + outSide, oy))
        pen.lineTo((ox + width + outSide, oy + height + outSide))
        pen.lineTo((ox, oy + height + outSide))
        pen.closePath()

        ox = origin_x + inSide
        oy = origin_y + inSide
        width -= outSide + inSide
        height -= outSide + inSide
        pen.moveTo((ox, oy))
        pen.lineTo((ox, oy + height - inSide))
        pen.lineTo((ox + width - inSide, oy + height - inSide))
        pen.lineTo((ox + width - inSide, oy))
        pen.closePath()
        glyph.round()
        drawGlyph(glyph)

    def makeHorSecLine(self, glyph, origin_x, origin_y, width, height):
        pen = glyph.getPen()
        pen.moveTo((origin_x, origin_y))
        pen.lineTo((origin_x + width, origin_y))
        pen.closePath()

        pen.moveTo((origin_x, height))
        pen.lineTo((origin_x + width, height))
        pen.closePath()

        glyph.round()
        drawGlyph(glyph)

    def makeVerSecLine(self, glyph, origin_x, origin_y, width, height):
        pen = glyph.getPen()
        pen.moveTo((origin_x, origin_y))
        pen.lineTo((origin_x, origin_y+height))
        pen.closePath()

        pen.moveTo((width, origin_y))
        pen.lineTo((width, origin_y+height))
        pen.closePath()

        glyph.round()
        drawGlyph(glyph)

    def findProximity(self, pos, point, left=0, right = 0):
        for p in pos:
            if p+left <= point < p+right:
                return True
        return False

    def draw(self, 
            mainFrames = True, 
            secondLines = True, 
            customsFrames = True,
            proximityPoints = False, 
            translate_secondLine_X = 0, 
            translate_secondLine_Y = 0,
            scale = 1):
        save()
        fill(None)
        stroke(0)
        x, y = 0, 0
        w, h = self.c.EM_Dimension_X, self.c.EM_Dimension_Y
        translateY = -12 * h / 100
        translate(0,translateY)
        if mainFrames:
            rect(x, y, w, h)

            x, y, charfaceW, charfaceH = self.getEmRatioFrame(self.c.characterFace, w, h)
            rect(x, y, charfaceW, charfaceH)

            stroke(None)
            fill(0,.75,1,.3)
            outside, inside = self.c.overshootOutsideValue, self.c.overshootInsideValue
            self.makeOvershoot(RGlyph(), x, y, charfaceW, charfaceH, outside, inside)
            g = self.c.glyph
            if proximityPoints and g is not None:
                listXleft = [x-outside, x+charfaceW-inside]
                listXright = [x+inside, x+charfaceW+outside]
                listYbottom = [y-outside+ translateY, y+charfaceH-inside+ translateY]
                listYtop = [y+inside+ translateY, y+charfaceH+outside+ translateY]
                for c in g:
                    for p in c.points:
                        px, py = p.x, p.y
                        if p.type == "offcurve": continue
                        if px in [x, charfaceW+x] or py in [y+ translateY, y+charfaceH+ translateY]:
                            fill(0,0,1,.4)
                            oval(px-10*scale, py-10*scale-translateY, 20*scale, 20*scale)
                            continue
                        fill(1,0,0,.4)
                        drawOval = 0
                        if self.findProximity(listXleft, px, left = -3, right = 0):
                            drawOval = 1
                        elif self.findProximity(listXright, px, left = 0, right = 3):
                            drawOval = 1
                        elif self.findProximity(listYbottom, py, left = -3, right = 0):
                            drawOval = 1
                        elif self.findProximity(listYtop, py, left = 0, right = 3):
                            drawOval = 1
                        if drawOval:
                            oval(px-10*scale, py-10*scale-translateY, 20*scale, 20*scale)
                            continue                  
        if secondLines:
            fill(None)
            stroke(.65, 0.16, .39, 1)
            ratio = (h * .5 * (self.c.horizontalLine / 50))
            y = h * .5 - ratio
            height = h * .5 + ratio
            self.makeHorSecLine(RGlyph(), 0, y+translate_secondLine_Y, w, height+translate_secondLine_Y)
            ratio = (w * .5 * (self.c.verticalLine / 50))
            x = w * .5 - ratio
            width = w * .5 + ratio
            self.makeVerSecLine(RGlyph(), x+translate_secondLine_X, 0, width+translate_secondLine_X, h)
        
        if customsFrames:
            fill(None)
            stroke(0)
            for frame in self.c.customsFrames:
                if not "Values" in frame: continue
                x, y, charfaceW, charfaceH = self.getEmRatioFrame(frame["Values"], w, h)
                rect(x, y, charfaceW, charfaceH)
        restore()