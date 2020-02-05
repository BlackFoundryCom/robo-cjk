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

    def drawPosition(self, d, glyph, view):
        x, y = glyph[0].points[0].x, glyph[0].points[0].y
        view._drawTextAtPoint(
            str(d), 
            attributes, 
            (x, y), 
            drawBackground = True, 
            backgroundColor = red, 
            backgroundStrokeColor = NSColor.whiteColor()
            )
        
    def draw(self, info, color=None):
        g = self.RCJKI.currentGlyph
        f = self.RCJKI.currentFont
        view = info["view"]
        self.scale = info['scale']
        
        if self.RCJKI.isCharacterGlyph and self.RCJKI.currentGlyph.preview:
            for i, e in enumerate(self.RCJKI.currentGlyph.preview):
                for dcName, (dcCoord, l) in e.items():
                    for dcAtomicElements in l:
                        for atomicInstanceGlyph in dcAtomicElements.values():
                            mjdt.save()
                            mjdt.fill(None)
                            mjdt.stroke(0, 0, 0, .2)
                            mjdt.strokeWidth(self.scale)
                            mjdt.drawGlyph(atomicInstanceGlyph[0])  
                            mjdt.restore()
                            
        if self.RCJKI.isDeepComponent and self.RCJKI.currentGlyph.preview:
            for i, d in enumerate(self.RCJKI.currentGlyph.preview):
                for atomicInstanceGlyph in d.values():
                    mjdt.save()
                    mjdt.fill(None)
                    mjdt.stroke(0, 0, 0, .2)
                    mjdt.strokeWidth(self.scale)
                    mjdt.drawGlyph(atomicInstanceGlyph[0])  
                    mjdt.restore()

        elif self.RCJKI.isAtomic and self.RCJKI.currentGlyph.preview:
            mjdt.save()
            mjdt.fill(None)
            mjdt.stroke(0, 0, 0, .2)
            mjdt.strokeWidth(self.scale)
            mjdt.drawGlyph(self.RCJKI.currentGlyph.preview)  
            mjdt.restore()
        
        if self.RCJKI.isDeepComponent and hasattr(self.RCJKI.currentGlyph, "computedAtomicSelectedSourceInstances") and self.RCJKI.currentGlyph.computedAtomicSelectedSourceInstances:            
            for i, d in enumerate(self.RCJKI.currentGlyph.computedAtomicSelectedSourceInstances):
                for atomicElementName, (atomicInstanceGlyph, atomicVariations, atomicCoord) in d.items():
                    mjdt.save()
                    mjdt.fill(.5, .25, 0, .2)
                    if color is not None:
                        mjdt.fill(color[0], color[1], color[2], color[3])
                    elif self.RCJKI.currentGlyph.selectedElement == dict(index = i, element = atomicElementName):
                        mjdt.fill(0, .8, .8, .5)
                    mjdt.drawGlyph(atomicInstanceGlyph) 
                    if color is None: 
                        self.drawPosition(i, atomicInstanceGlyph, view)
                    mjdt.restore()
            
        elif self.RCJKI.isDeepComponent and hasattr(self.RCJKI.currentGlyph, "computedAtomicInstances"):            
            for i, d in enumerate(self.RCJKI.currentGlyph.computedAtomicInstances):
                for atomicElementName, (atomicInstanceGlyph, atomicVariations, atomicCoord) in d.items():
                    mjdt.save()
                    mjdt.fill(0, .5, .25, .4)
                    if color is not None:
                        mjdt.fill(color[0], color[1], color[2], color[3])
                    elif self.RCJKI.currentGlyph.selectedElement == dict(index = i, element = atomicElementName):
                        mjdt.fill(0, .8, .8, .5)
                    mjdt.drawGlyph(atomicInstanceGlyph)
                    if color is None:
                        self.drawPosition(i, atomicInstanceGlyph, view)
                    mjdt.restore()
                    
        elif self.RCJKI.isCharacterGlyph and hasattr(self.RCJKI.currentGlyph, "computedDeepComponents") and self.RCJKI.currentGlyph.computedDeepComponents:            
            for i, e in enumerate(self.RCJKI.currentGlyph.computedDeepComponents):
                for dcName, (dcCoord, l) in e.items():
                    for j, dcAtomicElements in enumerate(l):
                        for atomicElementName, (atomicInstanceGlyph, atomicVariations, atomicCoord) in dcAtomicElements.items():
                            mjdt.save()
                            mjdt.fill(.25, 0, .5, .8)
                            if color is not None:
                                mjdt.fill(color[0], color[1], color[2], color[3])
                            elif self.RCJKI.currentGlyph.selectedElement == dict(index = i, element = dcName):
                                mjdt.fill(0, .8, .8, .5)
                            mjdt.drawGlyph(atomicInstanceGlyph)  
                            if color is None and not j:
                                self.drawPosition(i, atomicInstanceGlyph, view)
                            mjdt.restore()
                            
        elif self.RCJKI.isCharacterGlyph and self.RCJKI.get("computedDeepComponentsVariation"):            
            for i, e in enumerate(self.RCJKI.currentGlyph.computedDeepComponentsVariation):
                for dcName, (dcCoord, l) in e.items():
                    for j, dcAtomicElements in enumerate(l):
                        for atomicElementName, (atomicInstanceGlyph, atomicVariations, atomicCoord) in dcAtomicElements.items():
                            mjdt.save()
                            mjdt.fill(.5, 0, .25, .4)
                            if color is not None:
                                mjdt.fill(color[0], color[1], color[2], color[3])
                            elif self.RCJKI.currentGlyph.selectedElement == dict(index = i, element = dcName):
                                mjdt.fill(0, .8, .8, .5)
                            mjdt.drawGlyph(atomicInstanceGlyph)  
                            if color is None and not j:
                                self.drawPosition(i, atomicInstanceGlyph, view)
                            mjdt.restore()