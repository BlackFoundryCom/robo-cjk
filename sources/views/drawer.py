"""
Copyright 2020 Black Foundry.

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
import mojo.drawingTools as mjdt
from utils import interpolation
from AppKit import NSFont, NSColor, NSFontAttributeName, NSForegroundColorAttributeName

attributes = {
            NSFontAttributeName : NSFont.boldSystemFontOfSize_(9),
            NSForegroundColorAttributeName : NSColor.whiteColor(),
            }
red = NSColor.colorWithCalibratedRed_green_blue_alpha_(.8, .2, .2, .5)

class Drawer():

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.refGlyph = None
        self.refGlyphPos = [0, 0]
        self.refGlyphScale = [1, 1]

        self.existingInstance = None
        self.existingInstancePos = [0, 0]
        self.existingInstanceScale = [1, 1]

    def drawIndexOfElements(self, d, glyph, view):
        x, y = glyph[0].points[0].x, glyph[0].points[0].y
        view._drawTextAtPoint(
            str(d), 
            attributes, 
            (x, y), 
            drawBackground = True, 
            backgroundColor = red, 
            backgroundStrokeColor = NSColor.whiteColor()
            )

    def roundGlyph(self, g):
        if self.RCJKI.roundToGrid:
            g.round()
        return g

    def drawGlyph(self, glyph, scale, color, strokecolor, customColor, drawSelectedElements = True):
        if glyph.selectedSourceAxis:
            if glyph.type == 'atomicElement':
                if not len(glyph): return
            # else:
            #     glyph.preview.computeDeepComponents(update = False)
            self.drawAxisPreview(
                glyph,
                color,
                scale,
                customColor,
                drawSelectedElements = drawSelectedElements
                )
        else:
            self.drawVariationPreview(glyph, scale, color, strokecolor)
        
    def draw(self, info, customColor = None, refGlyph = None, onlyPreview = False):
        view = info["view"]
        scale = info['scale']
        color = customColor
        # if self.RCJKI.currentGlyph.preview.variationPreview:
        if info["notificationName"] == "draw":
            previewColor = [(0, 0, 0, 0), (0, 0, 0, .7)][onlyPreview]
            previewStrokeColor = [(0, 0, 0, .2), (0, 0, 0, 0)][onlyPreview]
        else:    
            previewColor = [(0, 0, 0, 0), (0, 0, 0, 1)][onlyPreview]
            previewStrokeColor = [(0, 0, 0, .2), (0, 0, 0, 0)][onlyPreview]

        self.drawVariationPreview(
            self.RCJKI.currentGlyph,
            scale, 
            color = previewColor, 
            strokecolor = previewStrokeColor
            )

        if self.RCJKI.currentGlyph.type == "atomicElement": return

        if self.refGlyph is not None:
            mjdt.save()
            mjdt.fill(0, 0, 0, .2)
            mjdt.translate(*self.refGlyphPos)
            mjdt.scale(*self.refGlyphScale)
            mjdt.drawGlyph(self.roundGlyph(self.refGlyph))
            mjdt.restore()

        if self.existingInstance is not None:
            mjdt.save()
            mjdt.fill(1, .8, 0, .8)
            mjdt.translate(*self.existingInstancePos)
            mjdt.scale(*self.existingInstanceScale)
            for c in self.existingInstance:
                mjdt.drawGlyph(self.roundGlyph(c))
            mjdt.restore()

        if onlyPreview: return
        if self.RCJKI.currentGlyph.type == "deepComponent":
            if not color:
                if not self.RCJKI.currentGlyph.selectedSourceAxis:
                    color = (0, .5, .25, .4)
                else: color = (.5, .25, 0, .2)

        elif self.RCJKI.currentGlyph.type == "characterGlyph":
            if not color:
                if not self.RCJKI.currentGlyph.selectedSourceAxis:
                    color = (.25, 0, .5, .8)
                else: color = (.5, 0, .25, .4)

        self.drawAxisPreview(self.RCJKI.currentGlyph, color, scale, customColor, view)   

    def drawVariationPreview(self, glyph, scale, color, strokecolor):
        mjdt.save()
        mjdt.fill(*color)
        mjdt.stroke(*strokecolor)
        mjdt.strokeWidth(scale)
        loc = {}
        if glyph.sourcesList: 
            loc = {x["Axis"]:x["PreviewValue"] for x in glyph.sourcesList}
        for g in glyph.preview(loc, forceRefresh=False):
        # for g in glyph.previewGlyph:
            mjdt.drawGlyph(self.roundGlyph(g.glyph))  
        mjdt.restore()

    def drawAxisPreview(self, glyph, color, scale, customColor, view = False, flatComponentColor = (.8, .6, 0, .7), drawSelectedElements = True):
        mjdt.save()
        index = None
        # loc = {}
        # if glyph.selectedSourceAxis:
        #     loc = {glyph.selectedSourceAxis:1}
        # for i, atomicInstance in enumerate(glyph.preview()):
        for i, atomicInstance in enumerate(glyph.preview(forceRefresh=False, axisPreview=True)):
        # for i, atomicInstance in enumerate(glyph.previewGlyph):
            transformIntance = atomicInstance._transformation
            atomicInstance = atomicInstance.glyph

            mjdt.fill(*color)
            if drawSelectedElements and i in glyph.selectedElement:
                mjdt.save()
                mjdt.stroke(1, 0, 0, 1)
                mjdt.strokeWidth(1*scale)
                tx = transformIntance['x']+transformIntance['tcenterx']
                ty = transformIntance['y']+transformIntance['tcentery']
                mjdt.line((tx-5*scale, ty), (tx+5*scale, ty))
                mjdt.line((tx, ty-5*scale), (tx, ty+5*scale))
                mjdt.stroke(None)
                mjdt.fill(1, 0, 0, 1)
                mjdt.fontSize(8*scale)
                mjdt.textBox(f"{int(transformIntance['tcenterx'])} {int(transformIntance['tcentery'])}", ((tx-30*scale, ty-30*scale, 60*scale, 20*scale)), align = "center")
                mjdt.restore()
                mjdt.fill(0, .8, .8, .5)

            for c in atomicInstance:
                if c.clockwise:
                    mjdt.stroke(1, 0, 0, 1)
                    mjdt.strokeWidth(2*scale)
            mjdt.save()
            # mjdt.drawGlyph(atomicInstance.getTransformedGlyph(round = self.RCJKI.roundToGrid)) 
            mjdt.drawGlyph(atomicInstance) 
            mjdt.restore()
            if customColor is None and view: 
                if i != index:
                    self.drawIndexOfElements(i, atomicInstance, view)
            index = i
        if customColor is None:
            mjdt.fill(customColor)
        else:    
            mjdt.fill(*customColor)

        mjdt.drawGlyph(glyph)
        mjdt.restore()

        for c in glyph.flatComponents:
            if self.RCJKI.currentFont[c.baseGlyph].type == "atomicElement":
                mjdt.drawGlyph(self.roundGlyph(self.RCJKI.currentFont[c.baseGlyph]))
            else:
                # self.RCJKI.currentFont[c.baseGlyph].preview.computeDeepComponents(update = False)
                self.drawAxisPreview(self.RCJKI.currentFont[c.baseGlyph],
                                            flatComponentColor,
                                            scale,
                                            customColor,
                                            view)
