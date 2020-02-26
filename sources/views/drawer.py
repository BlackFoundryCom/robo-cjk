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
        
    def draw(self, info, color=None):
        g = self.RCJKI.currentGlyph
        f = self.RCJKI.currentFont
        view = info["view"]
        scale = info['scale']
        if self.RCJKI.currentGlyph.type == "characterGlyph" and self.RCJKI.currentGlyph.preview:
            self.drawCharacterGlyphPreview(
                g,
                scale, 
                color = (0, 0, 0, 0), 
                strokecolor = (0, 0, 0, .2)
                )
                            
        if self.RCJKI.currentGlyph.type == "deepComponent" and self.RCJKI.currentGlyph.preview:
            self.drawDeepComponentPreview(
                g,
                scale, 
                color = (0, 0, 0, 0), 
                strokecolor = (0, 0, 0, .2)
                )

        elif self.RCJKI.currentGlyph.type == "atomicElement" and self.RCJKI.currentGlyph.preview:
            self.drawAtomicElementPreview(
                g,
                scale, 
                color = (0, 0, 0, 0), 
                strokecolor = (0, 0, 0, .2) 
                )
        
        if self.RCJKI.currentGlyph.type == "deepComponent" and hasattr(self.RCJKI.currentGlyph, "computedAtomicSelectedSourceInstances") and self.RCJKI.currentGlyph.computedAtomicSelectedSourceInstances:            
            for i, d in enumerate(self.RCJKI.currentGlyph.computedAtomicSelectedSourceInstances):
                for atomicElementName, (atomicInstanceGlyph, atomicVariations, atomicCoord) in d.items():
                    mjdt.save()
                    mjdt.fill(.5, .25, 0, .2)
                    if color is not None:
                        mjdt.fill(*color)
                    elif i in self.RCJKI.currentGlyph.selectedElement:
                        mjdt.fill(0, .8, .8, .5)
                    for c in atomicInstanceGlyph:
                        if c.clockwise:
                            mjdt.stroke(1, 0, 0, 1)
                            mjdt.strokeWidth(2*scale)
                    mjdt.drawGlyph(atomicInstanceGlyph) 
                    if color is None: 
                        self.drawIndexOfElements(i, atomicInstanceGlyph, view)
                    mjdt.restore()
            
        elif self.RCJKI.currentGlyph.type == "deepComponent" and hasattr(self.RCJKI.currentGlyph, "computedAtomicInstances"):            
            for i, d in enumerate(self.RCJKI.currentGlyph.computedAtomicInstances):
                for atomicElementName, (atomicInstanceGlyph, atomicVariations, atomicCoord) in d.items():
                    mjdt.save()
                    mjdt.fill(0, .5, .25, .4)
                    if color is not None:
                        mjdt.fill(*color)
                    elif i in self.RCJKI.currentGlyph.selectedElement:
                        mjdt.fill(0, .8, .8, .5)
                    for c in atomicInstanceGlyph:
                        if c.clockwise:
                            mjdt.stroke(1, 0, 0, 1)
                            mjdt.strokeWidth(2*scale)
                    mjdt.drawGlyph(atomicInstanceGlyph)
                    if color is None:
                        self.drawIndexOfElements(i, atomicInstanceGlyph, view)
                    mjdt.restore()
                    
        elif self.RCJKI.currentGlyph.type == "characterGlyph" and hasattr(self.RCJKI.currentGlyph, "computedDeepComponents") and self.RCJKI.currentGlyph.computedDeepComponents:            
            for i, e in enumerate(self.RCJKI.currentGlyph.computedDeepComponents):
                for dcName, (dcCoord, l) in e.items():
                    for j, dcAtomicElements in enumerate(l):
                        for atomicElementName, (atomicInstanceGlyph, atomicVariations, atomicCoord) in dcAtomicElements.items():
                            mjdt.save()
                            mjdt.fill(.25, 0, .5, .8)
                            if color is not None:
                                mjdt.fill(*color)
                            elif i in self.RCJKI.currentGlyph.selectedElement:
                                mjdt.fill(0, .8, .8, .5)
                            for c in atomicInstanceGlyph:
                                if c.clockwise:
                                    mjdt.stroke(1, 0, 0, 1)
                                    mjdt.strokeWidth(2*scale)
                            mjdt.drawGlyph(atomicInstanceGlyph)  
                            if color is None and not j:
                                self.drawIndexOfElements(i, atomicInstanceGlyph, view)
                            mjdt.restore()
                            
        elif self.RCJKI.currentGlyph.type == "characterGlyph" and hasattr(self.RCJKI.currentGlyph, "computedDeepComponentsVariation"):   
            for i, e in enumerate(self.RCJKI.currentGlyph.computedDeepComponentsVariation):
                for dcName, (dcCoord, l) in e.items():
                    for j, dcAtomicElements in enumerate(l):
                        for atomicElementName, (atomicInstanceGlyph, atomicVariations, atomicCoord) in dcAtomicElements.items():
                            mjdt.save()
                            mjdt.fill(.5, 0, .25, .4)                            
                            if color is not None:
                                mjdt.fill(*color)
                            elif i in self.RCJKI.currentGlyph.selectedElement:
                                mjdt.fill(0, .8, .8, .5)
                            for c in atomicInstanceGlyph:
                                if c.clockwise:
                                    mjdt.stroke(1, 0, 0, 1)
                                    mjdt.strokeWidth(2*scale)
                            mjdt.drawGlyph(atomicInstanceGlyph)  
                            if color is None and not j:
                                self.drawIndexOfElements(i, atomicInstanceGlyph, view)
                            mjdt.restore()