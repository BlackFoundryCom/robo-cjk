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
from drawers.ReferenceViewerDrawer import ReferenceViewerDraw
from mojo.UI import OpenGlyphWindow
from mojo.events import extractNSEvent
from ufoLib.glifLib import readGlyphFromString
from drawers.DeepComponentDrawer import DeepComponentDrawer
from drawers.Tester_DeepComponentDrawer import TesterDeepComponent
from Helpers import deepolation
import Global
import os

cwd = os.getcwd()
rdir = os.path.abspath(os.path.join(cwd, os.pardir))

RoboCJKIconPath = os.path.join(rdir, "resources/RoboCJKIcon.xml")

eps = 1e-10

class MainCanvas():

    scale = .32
    translateX = 330
    translateY = 420

    def __init__(self, interface):
        self.ui = interface
        
        self.canvasWidth = 386
        
        self.preview = 0

    def mouseDown(self, info):
        if info.clickCount() == 2 and self.ui.glyph is not None:
            OpenGlyphWindow(self.ui.glyph)

    def update(self):
        self.ui.w.mainCanvas.update()

    def mouseDragged(self, info):
        command = extractNSEvent(info)['commandDown']
        deltaX = info.deltaX()/(self.scale+eps)
        deltaY = info.deltaY()/(self.scale+eps)
        if command:
            TesterDeepComponent.translateX += deltaX
            TesterDeepComponent.translateY -= deltaY
        else:
            self.translateX += deltaX
            self.translateY -= deltaY
        self.update()

    def magnifyWithEvent(self, info):
        x, y = info.locationInWindow()
        scale = self.scale
        oldX, oldY = (self.translateX + x)*self.scale , (self.translateY + y)*self.scale
        delta = info.deltaZ()
        sensibility = .002
        scale += (delta / (abs(delta)+eps) * sensibility) / (self.scale + eps)
        minScale = .009
        if scale > minScale:
            self.scale = scale

        self.translateX -=  (((self.translateX + x)*self.scale - oldX)/2)/self.scale
        self.translateY -=  (((self.translateY + y)*self.scale - oldY)/2)/self.scale

        self.update()

    def scrollWheel(self, info):
        alt = extractNSEvent(info)['optionDown']
        if not alt: return
        scale = self.scale
        delta = info.deltaY()
        sensibility = .009
        scale += (delta / (abs(delta)+eps) * sensibility) / (self.scale + eps)
        minScale = .005
        if scale > minScale:
            self.scale = scale
        self.update()

    def keyDown(self, info):
        char = info.characters()
        command = extractNSEvent(info)['commandDown']

        if char == " ":
            self.preview = 1
            
        elif char == "+" and command:
            self.scale += .05

        elif char == "-" and command:
            scale = self.scale
            scale -= .05
            if scale > .05:
                self.scale = scale

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
                iconText = Global.roboCJK_Icon.get()
                icon = RGlyph()
                pen = icon.getPointPen()
                readGlyphFromString(iconText, icon, pen)
                drawGlyph(icon)
            else:
                if not len(g) and not "deepComponentsGlyph" in g.lib and g.unicode and not self.preview:
                    fill(0, 0, 0, .1)
                    rect(-10000, -10000, 20000, 20000)
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
                    if self.ui.OnOff_referenceViewer and not self.preview:
                        if self.ui.glyph.name.startswith("uni"):
                            self.ui.txt = chr(int(self.ui.glyph.name[3:7],16))
                        elif self.ui.glyph.unicode: 
                            self.ui.txt = chr(self.ui.glyph.unicode)
                        else:
                            self.ui.txt=""
                        ReferenceViewerDraw(self.ui, self.ui.txt).draw()

                    f = self.ui.font2Storage[self.ui.font]
                    fill(.2, 0, 1, .5)
                    if self.preview: 
                        fill(0, 0, 0, 1)
                    DeepComponentDrawer(self.ui, g, f)

                    TesterDeepComponent(self.ui, self.ui.w.deepComponentGroup.creator.storageFont_Glyphset)
            restore()
        except Exception as e:
            print(e)