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
from mojo.events import addObserver, removeObserver#, extractNSEvent
from vanilla.dialogs import message
from mojo.roboFont import *
from mojo.UI import OpenGlyphWindow, UpdateCurrentGlyphView
from mojo.drawingTools import *

class OpenSelectedComponent():

    def __init__(self, interface):
        self.ui = interface
        self.ui.w.bind('close', self.windowWillClose)
        self.observer()

    def windowWillClose(self, sender):
        self.observer(remove=True)
        
    def observer(self, remove = False):
        if not remove:
            addObserver(self, "keyUp", "keyUp")
            return
        removeObserver(self, "keyUp")

    def keyUp(self, info):
        char = info['event'].characters()
        if char == "o":
            self.openSelectedComponent(self.ui.font, self.ui.glyph)

    def openSelectedComponent(self, f, g):
        selectedComponents = [c for c in g.components if c.selected]

        if not len(selectedComponents):
            message("There is no selected components")
            return

        selectedComponent = selectedComponents[0]
        self.selectedComponentName = selectedComponent.baseGlyph
        self.selectedComponentOffset = selectedComponent.transformation[-2:]
        
        self.oldGlyph = g

        self.ui.window = OpenGlyphWindow(f[self.selectedComponentName])
        self.ui.windows.add(self.ui.window)

        self.currentGlyph = CurrentGlyph()

        addObserver(self, "currentGlyphChanged", "currentGlyphChanged")
        addObserver(self, "draw", "draw")
        addObserver(self, "draw", "drawPreview")
        addObserver(self, "draw", "drawInactive")
        addObserver(self, "mouseDown", "mouseDown")

        UpdateCurrentGlyphView()

    def mouseDown(self, info):
        if info['clickCount'] == 2:
            x, y = info['point']
            tx, ty = self.selectedComponentOffset
            if self.oldGlyph.pointInside((x+tx, y+ty)):
                OpenGlyphWindow(self.oldGlyph)

    def draw(self, info):
        s = info["scale"]
        save()
        stroke(0, 0, 0, .3)
        strokeWidth(1*s)
        fill(None)
        if info['notificationName'] == "drawPreview":
            stroke(None)
            fill(0,0,0,1)
        tx, ty = self.selectedComponentOffset
        translate(-tx, -ty)
        drawGlyph(self.oldGlyph)
        restore()

    def currentGlyphChanged(self, info):
        if CurrentGlyph() != self.currentGlyph:
            removeObserver(self, "currentGlyphChanged")
            removeObserver(self, "draw")
            removeObserver(self, "drawPreview")
            removeObserver(self, "drawInactive")
            removeObserver(self, "mouseDown")

