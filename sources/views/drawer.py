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

    def drawCharacterGlyphPreview(self, glyph, scale, color, strokecolor):
        mjdt.save()
        mjdt.fill(*color)
        mjdt.stroke(*strokecolor)
        mjdt.strokeWidth(scale)
        for i, e in enumerate(glyph.preview):
            for dcName, (dcCoord, l) in e.items():
                for dcAtomicElements in l:
                    for atomicInstanceGlyph in dcAtomicElements.values():
                        mjdt.drawGlyph(self.roundGlyph(atomicInstanceGlyph[0]))  
        if glyph.outlinesPreview is not None:
            mjdt.drawGlyph(self.roundGlyph(glyph.outlinesPreview))  
        mjdt.restore()

    def drawDeepComponentPreview(self, glyph, scale, color, strokecolor):
        for i, d in enumerate(glyph.preview):
            for atomicInstanceGlyph in d.values():
                mjdt.save()
                mjdt.fill(*color)
                mjdt.stroke(*strokecolor)
                mjdt.strokeWidth(scale)
                mjdt.drawGlyph(self.roundGlyph(atomicInstanceGlyph[0]))  
                mjdt.restore()

    def drawAtomicElementPreview(self, glyph, scale, color, strokecolor):
        mjdt.save()
        mjdt.fill(*color)
        mjdt.stroke(*strokecolor)
        mjdt.strokeWidth(scale)
        mjdt.drawGlyph(self.roundGlyph(glyph.preview))  
        mjdt.restore()

    def drawGlyph(self, glyph, scale, color, strokecolor, customColor, drawSelectedElements = True):
        if not glyph.preview:
            if glyph.type == 'atomicElement':
                if not len(glyph): return
            else:
                glyph.computeDeepComponents()
            self.drawGlyphAtomicInstance(
                glyph,
                color,
                scale,
                customColor,
                drawSelectedElements = drawSelectedElements
                )
        else:
            args = (glyph, scale, color, strokecolor)
            if glyph.type == 'atomicElement':
                self.drawAtomicElementPreview(*args)

            elif glyph.type == "deepComponent":
                self.drawDeepComponentPreview(*args)

            elif glyph.type == "characterGlyph":
                self.drawCharacterGlyphPreview(*args)
        
    def draw(self, info, customColor = None, refGlyph = None):
        view = info["view"]
        scale = info['scale']
        color = customColor
        if self.RCJKI.currentGlyph.preview:
            if self.RCJKI.currentGlyph.type == "characterGlyph":
                self.drawCharacterGlyphPreview(
                    self.RCJKI.currentGlyph,
                    scale, 
                    color = (0, 0, 0, 0), 
                    strokecolor = (0, 0, 0, .2)
                    )
                                
            if self.RCJKI.currentGlyph.type == "deepComponent":
                self.drawDeepComponentPreview(
                    self.RCJKI.currentGlyph,
                    scale, 
                    color = (0, 0, 0, 0), 
                    strokecolor = (0, 0, 0, .2)
                    )

            elif self.RCJKI.currentGlyph.type == "atomicElement":
                self.drawAtomicElementPreview(
                    self.RCJKI.currentGlyph,
                    scale, 
                    color = (0, 0, 0, 0), 
                    strokecolor = (0, 0, 0, .2) 
                    )
        if self.RCJKI.currentGlyph.type == "atomicElement": return
        if self.RCJKI.currentGlyph.type == "deepComponent":
            if not color:
                if self.RCJKI.currentGlyph.computedAtomicInstances:
                    color = (0, .5, .25, .4)
                else: color = (.5, .25, 0, .2)

        elif self.RCJKI.currentGlyph.type == "characterGlyph":
            if not color:
                if self.RCJKI.currentGlyph.computedDeepComponents:
                    color = (.25, 0, .5, .8)
                else: color = (.5, 0, .25, .4)

        self.drawGlyphAtomicInstance(self.RCJKI.currentGlyph, color, scale, customColor, view)
        if self.refGlyph is not None:
            mjdt.save()
            mjdt.fill(0, 0, 0, .2)
            mjdt.translate(*self.refGlyphPos)
            mjdt.drawGlyph(self.roundGlyph(self.refGlyph))
            mjdt.restore()

    def drawGlyphAtomicInstance(self, glyph, color, scale, customColor, view = False, flatComponentColor = (.8, .6, 0, .7), drawSelectedElements = True):
        mjdt.save()
        index = None
        for i, atomicInstanceGlyph in glyph.atomicInstancesGlyphs:
            mjdt.fill(*color)
            if drawSelectedElements and i in glyph.selectedElement:
                mjdt.fill(0, .8, .8, .5)
            for c in atomicInstanceGlyph:
                if c.clockwise:
                    mjdt.stroke(1, 0, 0, 1)
                    mjdt.strokeWidth(2*scale)
            mjdt.drawGlyph(self.roundGlyph(atomicInstanceGlyph)) 
            if customColor is None and view: 
                if i != index:
                    self.drawIndexOfElements(i, atomicInstanceGlyph, view)
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
                self.RCJKI.currentFont[c.baseGlyph].computeDeepComponents()
                self.drawGlyphAtomicInstance(self.RCJKI.currentFont[c.baseGlyph],
                                            flatComponentColor,
                                            scale,
                                            customColor,
                                            view)
