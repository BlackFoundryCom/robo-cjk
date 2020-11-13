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
from vanilla import *
from mojo.canvas import CanvasGroup
from mojo.UI import UpdateCurrentGlyphView
from mojo.roboFont import *
from AppKit import NSColor, NSNoBorder, NumberFormatter
import mojo.drawingTools as mjdt
from imp import reload
from utils import decorators, interpolation
# reload(decorators)
from utils import files
# reload(files)

from views import sheets, drawer
# reload(sheets)
# reload(drawer)

import copy

lockedProtect = decorators.lockedProtect
refresh = decorators.refresh

transparentColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, 0)
numberFormatter = NumberFormatter()

INPROGRESS = (1., 0., 0., 1.)
CHECKING1 = (1., .5, 0., 1.)
CHECKING2 = (1., 1., 0., 1.)
CHECKING3 = (0., .5, 1., 1.)
DONE = (0., 1., .5, 1.)
STATE_COLORS = (INPROGRESS, CHECKING1, CHECKING2, CHECKING3, DONE)


class GlyphPreviewCanvas(CanvasGroup):

    def __init__(self, posSize, RCJKI, glyphType):
        super().__init__(posSize, delegate = self)
        self.RCJKI = RCJKI
        self.glyphType = glyphType
        self.glyphName = ''
        self.drawer = drawer.Drawer(RCJKI)

    def draw(self):
        if not self.RCJKI.get("currentFont"): return
        if not self.glyphName: return

        self.glyph = self.RCJKI.currentFont[self.glyphName]
        # glyph = self.glyph.preview.computeCharacterGlyphPreview(self.glyph, {"WGHT":1})

        mjdt.save()
        scale = .15
        mjdt.scale(scale, scale)
        mjdt.translate(((200-(self.glyph.width*scale))/scale)*.5, 450)
        for g in self.glyph.preview({}, forceRefresh=False):
            mjdt.drawGlyph(g.glyph)
        mjdt.restore()
        # outlines, items, width = self.instantiateCharacterGlyph(self.glyph, {"WGHT":1})
        # print(outlines, items, width)


        # self.glyph = self.RCJKI.currentFont[self.glyphName]
        # d = self.glyph._glyphVariations
        # if self.glyph.type ==  "atomicElement":
        #     self.glyph.sourcesList = [
        #         {"Axis":axisName, "Layer":layer, "PreviewValue":layer.minValue} for axisName, layer in  d.items()
        #         ]
        # else:
        #     self.glyph.sourcesList = [
        #         {"Axis":axisName, "Layer":layerName, "PreviewValue":layerName.minValue} for axisName, layerName in  d.items()
        #         ]

        if self.glyph.markColor is not None:
            mjdt.fill(*self.glyph.markColor)
            mjdt.rect(0, 0, 200, 20)

        # scale = .15
        # mjdt.scale(scale, scale)
        # mjdt.translate(((200-(self.glyph.width*scale))/scale)*.5, 450)
        # self.glyph.preview.computeDeepComponentsPreview(update = False)
        # if self.glyph.preview.variationPreview is not None:
        #     self.drawer.drawVariationPreview(
        #             self.glyph, 
        #             scale, 
        #             color = (0, 0, 0, 1), 
        #             strokecolor = (0, 0, 0, 0)
        #             )
        # else:
        #     self.glyph.preview.computeDeepComponents(update = False)
        #     self.drawer.drawAxisPreview(
        #         self.glyph, 
        #         (0, 0, 0, 1), 
        #         scale, 
        #         (0, 0, 0, 1), flatComponentColor = (0, 0, 0, 1)
        #         )

