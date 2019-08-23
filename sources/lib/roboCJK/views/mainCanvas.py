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
from imp import reload

from mojo.drawingTools import *
from mojo.roboFont import *
from views.drawers import interpolaviourDrawer, displayOptionsDrawer, referenceViewDrawer, designFrameDrawer
from utils import robocjk
# from drawers.DeepComponentDrawer import DeepComponentDrawer
# from drawers.Tester_DeepComponentDrawer import TesterDeepComponent
# from drawers.InterpolaviourDrawer import InterpolaviourDrawer

from mojo.UI import OpenGlyphWindow, CurrentGlyphWindow
from mojo.events import extractNSEvent
from ufoLib.glifLib import readGlyphFromString

import os

reload(designFrameDrawer)
reload(referenceViewDrawer)
reload(interpolaviourDrawer)
reload(displayOptionsDrawer)
reload(robocjk)

cwd = os.getcwd()
rdir = os.path.abspath(os.path.join(cwd, os.pardir))

RoboCJKIconPath = os.path.join(rdir, "resources/RoboCJKIcon.xml")

eps = 1e-10

class MainCanvas():

    scale = .32
    translateX = 300
    translateY = 280

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.canvasWidth = 386
        self.preview = 0
        self.dfv = designFrameDrawer.DesignFrameDrawer(self.RCJKI)
        self.rvd = referenceViewDrawer.ReferenceViewerDraw(self.RCJKI)
        self.interpolaviourDrawer = interpolaviourDrawer.InterpolaviourDrawer(self.RCJKI)
        self.stackMaster = displayOptionsDrawer.StackMasterDrawer(self.RCJKI)
        self.waterFall = displayOptionsDrawer.WaterFallDrawer(self.RCJKI)

    def mouseDown(self, info):
        if info.clickCount() == 2 and self.RCJKI.currentGlyph is not None:
            self.RCJKI.openGlyphWindow(self.RCJKI.currentGlyph)
            # Helpers.setDarkMode(self.ui.window, self.ui.darkMode)

    def update(self):
        self.RCJKI.initialDesignController.interface.w.mainCanvas.update()

    def mouseDragged(self, info):
        command = extractNSEvent(info)['commandDown']
        deltaX = info.deltaX()/(self.scale+eps)
        deltaY = info.deltaY()/(self.scale+eps)
        if command:
            pass
            # TesterDeepComponent.translateX += deltaX
            # TesterDeepComponent.translateY -= deltaY
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
        delta = info.deltaY()
        sensibility = .009

        if not alt: 
            self.translateY -= delta/sensibility

        else:
            scale = self.scale
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
            g = self.RCJKI.currentGlyph
            scale(self.scale, self.scale)
            translate(((self.canvasWidth/self.scale)-1000)*.5, 250)
            translate(self.translateX, self.translateY)
            if g is None: 
                iconText = robocjk.roboCJK_Icon.get()
                icon = RGlyph()
                pen = icon.getPointPen()
                readGlyphFromString(iconText, icon, pen)
                save()
                fill(0, 0, 0, .9)
                drawGlyph(icon)
                restore()
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
                    if g.name in self.RCJKI.collab._userLocker(self.RCJKI.user).glyphs:
                        fill(0, 0, 0, 1)
                    elif g.name in self.RCJKI.lockedGlyphs:
                        fill(1, 0, 0, 1)
                    else:
                        fill(0, 0, 0, .5)
                    drawGlyph(g)

                    # save()
                    # if self.ui.stackMasters and not self.preview:
                    #     fill(0, .3, 1, .3)
                    #     for f in self.ui.font2Storage:
                    #         if f[g.name] == g: continue
                    #         drawGlyph(f[g.name])
                    # restore()

                    # save()
                    # if self.ui.waterFall and not self.preview:
                    #     s = .5
                    #     scale(s,s)
                    #     translate(0, -self.ui.EM_Dimension_Y - 200)
                    #     for i in range(1, 5):
                    #         drawGlyph(g)
                    #         translate(self.ui.EM_Dimension_X + 150, 0)
                    #         scale(s,s)
                    # restore()

                    # if self.ui.onOff_designFrame and not self.preview:
                    if self.RCJKI.settings["showDesignFrame"]:
                        if not self.preview or self.preview == self.RCJKI.settings["designFrame"]["drawPreview"]:
                            self.dfv.draw(
                                glyph = g,
                                mainFrames = self.RCJKI.settings['designFrame']['showMainFrames'], 
                                secondLines = self.RCJKI.settings['designFrame']['showSecondLines'], 
                                customsFrames = self.RCJKI.settings['designFrame']['showCustomsFrames'], 
                                proximityPoints = self.RCJKI.settings['designFrame']['showproximityPoints'],
                                translate_secondLine_X = self.RCJKI.settings['designFrame']['translate_secondLine_X'], 
                                translate_secondLine_Y = self.RCJKI.settings['designFrame']['translate_secondLine_Y'],
                                scale = self.scale
                                )
                    # if self.ui.OnOff_referenceViewer and not self.preview:
                    if self.RCJKI.settings["referenceViewer"]["onOff"]:

                        if g.name.startswith("uni"):
                            char = chr(int(g.name[3:7],16))
                        elif g.unicode: 
                            char = chr(g.unicode)
                        else:
                            char = ""

                        if not self.preview or self.preview == self.RCJKI.settings["referenceViewer"]["drawPreview"]:
                            self.rvd.draw(char)
                        
                    # f = self.ui.font2Storage[self.ui.font]
                    fill(.2, 0, 1, .5)
                    if self.preview: 
                        fill(0, 0, 0, 1)
                    # DeepComponentDrawer(self.ui, g, f)
                    if self.RCJKI.settings["interpolaviour"]["onOff"]:
                        self.interpolaviourDrawer.draw(g, self.scale, self.preview)

                    if self.RCJKI.settings["stackMasters"]:
                        self.stackMaster.draw(g, self.preview)

                    if self.RCJKI.settings["waterFall"]:
                        self.waterFall.draw(g, self.preview)
                        
                    # if self.ui.interpolaviourOnOff:
                    #     InterpolaviourDrawer(self.ui).draw(g, self.scale, self.preview)
                    # TesterDeepComponent(self.ui, self.ui.w.deepComponentGroup.creator.storageFont_Glyphset)
            restore()
        except Exception as e:
            print(e)