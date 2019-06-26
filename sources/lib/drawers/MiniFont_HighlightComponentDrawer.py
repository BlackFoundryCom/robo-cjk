from mojo.drawingTools import *
from fontTools.pens.cocoaPen import CocoaPen
from mojo.roboFont import *

class MiniFont_HighlightComponent():

    def __init__(self, controller):
        self.c = controller
        self.draw()

    def draw(self):
        if not self.c.showWipCompo: return
        if not self.c.minifontList: return
        if not self.c.glyph.components: return
        if "temp" not in self.c.font.path: return
        save()
        for compo in self.c.glyph.components:
            if compo.baseGlyph not in self.c.font.keys(): continue
            if self.c.font[compo.baseGlyph].markColor != (1,0,0,1): continue
            for c in self.c.font[compo.baseGlyph]:
                pen = CocoaPen(c)
                c.draw(pen)
                path = pen.path
                NSColor.colorWithCalibratedRed_green_blue_alpha_(.9,0,0,.8)
                path.fill()
        restore()