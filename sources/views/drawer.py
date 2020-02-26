import mojo.drawingTools as mjdt
from AppKit import NSFont, NSColor, NSFontAttributeName, NSForegroundColorAttributeName

attributes = {
            NSFontAttributeName : NSFont.boldSystemFontOfSize_(9),
            NSForegroundColorAttributeName : NSColor.whiteColor(),
            }
red = transparentColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(.8, .2, .2, .5)

class Drawer():

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI

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

    def drawCharacterGlyphPreview(self, glyph, scale, color, strokecolor):
        for i, e in enumerate(glyph.preview):
            for dcName, (dcCoord, l) in e.items():
                for dcAtomicElements in l:
                    for atomicInstanceGlyph in dcAtomicElements.values():
                        mjdt.save()
                        mjdt.fill(*color)
                        mjdt.stroke(*strokecolor)
                        mjdt.strokeWidth(scale)
                        mjdt.drawGlyph(atomicInstanceGlyph[0])  
                        mjdt.restore()

    def drawDeepComponentPreview(self, glyph, scale, color, strokecolor):
        for i, d in enumerate(glyph.preview):
            for atomicInstanceGlyph in d.values():
                mjdt.save()
                mjdt.fill(*color)
                mjdt.stroke(*strokecolor)
                mjdt.strokeWidth(scale)
                mjdt.drawGlyph(atomicInstanceGlyph[0])  
                mjdt.restore()

    def drawAtomicElementPreview(self, glyph, scale, color, strokecolor):
        mjdt.save()
        mjdt.fill(*color)
        mjdt.stroke(*strokecolor)
        mjdt.strokeWidth(scale)
        mjdt.drawGlyph(glyph.preview)  
        mjdt.restore()
        
    def draw(self, info, customColor = None):
        view = info["view"]
        scale = info['scale']
        color = customColor
        if self.RCJKI.currentGlyph.type == "characterGlyph" and self.RCJKI.currentGlyph.preview:
            self.drawCharacterGlyphPreview(
                self.RCJKI.currentGlyph,
                scale, 
                color = (0, 0, 0, 0), 
                strokecolor = (0, 0, 0, .2)
                )
                            
        if self.RCJKI.currentGlyph.type == "deepComponent" and self.RCJKI.currentGlyph.preview:
            self.drawDeepComponentPreview(
                self.RCJKI.currentGlyph,
                scale, 
                color = (0, 0, 0, 0), 
                strokecolor = (0, 0, 0, .2)
                )

        elif self.RCJKI.currentGlyph.type == "atomicElement" and self.RCJKI.currentGlyph.preview:
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

        for i, atomicInstanceGlyph in self.RCJKI.currentGlyph.atomicInstancesGlyphs:
            mjdt.save()
            mjdt.fill(*color)
            if i in self.RCJKI.currentGlyph.selectedElement:
                mjdt.fill(0, .8, .8, .5)
            for c in atomicInstanceGlyph:
                if c.clockwise:
                    mjdt.stroke(1, 0, 0, 1)
                    mjdt.strokeWidth(2*scale)
            mjdt.drawGlyph(atomicInstanceGlyph) 
            if customColor is None: 
                self.drawIndexOfElements(i, atomicInstanceGlyph, view)
            mjdt.restore()
