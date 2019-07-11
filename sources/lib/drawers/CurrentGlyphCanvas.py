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
from drawers.DesignFrameDrawer import DesignFrameDrawer
from mojo.UI import OpenGlyphWindow
from mojo.events import extractNSEvent
from ufoLib.glifLib import readGlyphFromString
from drawers.DeepComponentDrawer import DeepComponentDrawer
from Helpers import deepolation
import os

cwd = os.getcwd()
rdir = os.path.abspath(os.path.join(cwd, os.pardir))

RoboCJKIconPath = os.path.join(rdir, "resources/RoboCJKIcon.xml")

class CurrentGlyphCanvas():

    def __init__(self, interface, glyphsetGroup):
        self.gl = glyphsetGroup
        self.ui = interface
        self.scale = .22
        self.canvasWidth = 386
        self.translateX = 0
        self.translateY = 0

    def mouseDown(self, info):
        if info.clickCount() == 2:
            OpenGlyphWindow(self.ui.glyph)

    def update(self):
        self.gl.canvas.update()

    def mouseDragged(self, info):
        deltaX = info.deltaX()/self.scale
        deltaY = info.deltaY()/self.scale
        self.translateX += deltaX
        self.translateY -= deltaY
        self.update()

    def scrollWheel(self, info):
        alt = extractNSEvent(info)['optionDown']
        if not alt: return
        scale = self.scale
        delta = info.deltaY()
        sensibility = .009
        scale += (delta / abs(delta) * sensibility) / self.scale
        minScale = .005
        if scale > minScale:
            self.scale = scale
        self.update()

    def draw(self):
        try:
            save()
            g = self.ui.glyph
            scale(self.scale, self.scale)
            translate(((self.canvasWidth/self.scale)-1000)*.5,250)
            translate(self.translateX, self.translateY)
            if g is None: 
                with open(RoboCJKIconPath, "r") as file:
                    iconText = file.read()
                icon = RGlyph()
                pen = icon.getPointPen()
                readGlyphFromString(iconText, icon, pen)
                drawGlyph(icon)
            else:
                fill(0, 0, 0, 1)
                drawGlyph(g)
                DesignFrameDrawer(self.ui).draw(glyph = g, scale = self.scale)
                f = self.ui.font2Storage[self.ui.font]
                fill(.2, 0, 1, .5)
                DeepComponentDrawer(self.ui, g, f)
            restore()
        except Exception as e:
            print(e)