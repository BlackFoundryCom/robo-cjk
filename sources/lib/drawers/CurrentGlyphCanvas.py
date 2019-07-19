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
        self.preview = 0

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

    def keyDown(self, info):
        if info.characters() == " ":
            self.preview = 1
            self.update()

    def keyUp(self, info):
        self.preview = 0
        self.update()

    def draw(self):
        try:
            save()
            g = self.ui.glyph
            scale(self.scale, self.scale)
            translate(((self.canvasWidth/self.scale)-1000)*.5, 250)
            translate(self.translateX, self.translateY)
            if g is None: 
                with open(RoboCJKIconPath, "r") as file:
                    iconText = file.read()
                icon = RGlyph()
                pen = icon.getPointPen()
                readGlyphFromString(iconText, icon, pen)
                drawGlyph(icon)
            else:
                if not len(g) and not "deepComponentsGlyph" in g.lib and g.unicode and not self.preview:
                    fill(0, 0, 0, .1)
                    rect(-1000, -1000, 10000, 10000)
                    # fill(.5, 0, .3, .5)
                    fill(0, 0, .8, .2)
                    translate(0, -150)
                    fontSize(1000)
                    text(chr(g.unicode), (0, 0))
                    stroke(0)
                    strokeWidth(100*self.scale)
                    newPath()
                    moveTo((0, 0))
                    lineTo((1100, 1100))
                    drawPath()
                else:
                    fill(0, 0, 0, 1)
                    drawGlyph(g)
                    if self.ui.onOff_designFrame and not self.preview:
                        DesignFrameDrawer(self.ui).draw(
                            glyph = g,
                            mainFrames = self.ui.showMainFrames, 
                            secondLines = self.ui.showSecondLines, 
                            customsFrames = self.ui.showCustomsFrames, 
                            proximityPoints = self.ui.showproximityPoints,
                            translate_secondLine_X = self.ui.translate_secondLine_X, 
                            translate_secondLine_Y = self.ui.translate_secondLine_Y,
                            scale = self.scale
                            )
                    f = self.ui.font2Storage[self.ui.font]
                    fill(.2, 0, 1, .5)
                    if self.preview: 
                        fill(0, 0, 0, 1)
                    DeepComponentDrawer(self.ui, g, f)
            restore()
        except Exception as e:
            print(e)