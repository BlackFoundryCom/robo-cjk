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
from vanilla import *
from mojo.roboFont import *
from mojo.UI import OpenGlyphWindow, CurrentGlyphWindow
from mojo.canvas import Canvas
from AppKit import NSAppearance, NSColor
from drawers.CurrentGlyphCanvas import CurrentGlyphCanvas
from lib.cells.colorCell import RFColorCell

class GlyphSet(Box):

    def __init__(self, posSize, interface):
        super(GlyphSet, self).__init__(posSize)
        self.ui = interface

        self.goTo = EditText((0,0,165,20),
            placeholder = "🔎 Char/Name",
            sizeStyle = "small")

        self.glyphset_List = List((0,20,165,-0),
            [],
            columnDescriptions = [
                                {"title": "Char", "width" : 30},
                                {"title": "Name", "width" : 105},                  
                                ],
            drawFocusRing=False, 
            selectionCallback = self._glyphset_List_selectionCallback,
            doubleClickCallback = self._glyphset_List_doubleClickCallback)

        self.set_glyphset_List()

        self.canvas = Canvas((165,20,-0,-0), delegate=CurrentGlyphCanvas(self.ui))

    def set_glyphset_List(self):
        if self.ui.font in self.ui.glyphsSetDict:
            self.glyphset_List.set(self.ui.glyphsSetDict[self.ui.font])

    def _glyphset_List_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        name = self.ui.glyphset[sel[0]]
        self.ui.glyph = self.ui.font[name]
        self.ui.getSuggestComponent()
        print(self.ui.suggestComponent)
        self.ui.w.activeMasterGroup.glyphData.glyphCompositionRules_List.set(self.ui.suggestComponent)
        self.canvas.update()

    def _glyphset_List_doubleClickCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        if self.ui.glyph is None: return
        OpenGlyphWindow(self.ui.glyph)
        gw = CurrentGlyphWindow()
        appearance = NSAppearance.appearanceNamed_('NSAppearanceNameVibrantDark')
        gw.window().getNSWindow().setAppearance_(appearance)

    # def draw(self):
    #     CurrentGlyphCanvas(self.ui)