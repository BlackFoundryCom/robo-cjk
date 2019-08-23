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
from vanilla import *
from mojo.canvas import Canvas
from mojo.roboFont import *
from mojo.drawingTools import *
from mojo.events import extractNSEvent
from lib.UI.spaceCenter.glyphSequenceEditText import splitText
from mojo.UI import OpenGlyphWindow

from views.drawers import designFrameDrawer
# from Helpers import deepolation
# import Helpers
reload(designFrameDrawer)
eps = 1e-10

class TextCenterWindow():

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.windowWidth, self.windowHeight = 800, 600
        self.w = Window((self.windowWidth, self.windowHeight), "Text Center", minSize = (200, 200))
        self.dfd = designFrameDrawer.DesignFrameDrawer(self.RCJKI)
        self.inverse = 0
        self.scale = .15
        self.margin = 50
        
        self.scroll = 0
        self.scrollX = 0
        self.scrollWheel_ZoomSensibility = .005
        self.keyDown_ZoomSensibility = .05
        self.glyphName2Glyph = {}
        self.selectedGlyph  = None
        self.text = []

        self.glyphLocation_in_Window = {}

        
        self.mainInputString = ""
        self.w.mainInputText_EditText = EditText((100, 10, -100, 20),
            self.mainInputString,
            sizeStyle = "small",
            callback = self._mainInputText_EditText_callback)

        self.leftInputString = ""
        self.w.leftInputText_EditText = EditText((10, 10, 80, 20),
            self.leftInputString,
            sizeStyle = "small",
            callback = self._leftInputText_EditText_callback)


        self.rightInputString = ""
        self.w.rightInputText_EditText = EditText((-90, 10, -10, 20),
            self.rightInputString,
            sizeStyle = "small",
            callback = self._rightInputText_EditText_callback)

        self.verticalMode = 0
        self.w.verticalMode_checkBox = CheckBox((10, -20, 150, -0),  
            "Vertical Mode", 
            value = self.verticalMode,
            sizeStyle = "small",
            callback = self._verticalMode_checkBox_callback)

        self.lineHeight = 1000
        self.w.lineHeight_Slider = Slider((-220, -20, -10, -0),
            minValue = 1000,
            maxValue = 2000,
            value = self.lineHeight,
            callback = self._lineHeight_Slider_callback,
            sizeStyle = "small")

        # self.w.displayDesignFrame_checkBox = CheckBox((-110, -20, -10, -0),  
        #     "Design Frame", 
        #     value = self.RCJKI.settings['showDesignFrame'],
        #     sizeStyle = "small",
        #     callback = self._displayDesignFrame_checkBox_callback)

        self.w.canvas = Canvas((0, 60, -0, -20), 
            delegate = self, 
            canvasSize=(10000, 10000),
            hasHorizontalScroller=False, 
            hasVerticalScroller=False)

        # Helpers.setDarkMode(self.w, self.ui.darkMode)
        self.w.bind('resize', self.windowDidResize)
        self.w.bind('close', self.windowCloses)
        self.w.open()

    def windowCloses(self, sender):
        self.RCJKI.textCenterController.interface = None

    def windowDidResize(self, sender):
        _, _, self.windowWidth, self.windowHeight = sender.getPosSize()
        self.w.canvas.update()

    def _verticalMode_checkBox_callback(self, sender):
        self.scroll = 0
        self.scrollX = 0
        self.verticalMode = sender.get()
        self.w.canvas.update()

    # def _displayDesignFrame_checkBox_callback(self, sender):
    #     self.RCJKI.settings['showDesignFrame'] = sender.get()
    #     self.w.canvas.update()

    def _lineHeight_Slider_callback(self, sender):
        self.lineHeight = sender.get()
        self.w.canvas.update()

    def _leftInputText_EditText_callback(self, sender):
        self.leftInputString = sender.get()

        self.getGlyphsFromString()
        self.w.canvas.update()

    def _mainInputText_EditText_callback(self, sender):
        self.mainInputString = sender.get()

        self.getGlyphsFromString()
        self.w.canvas.update() 

    def _rightInputText_EditText_callback(self, sender):
        self.rightInputString = sender.get()

        self.getGlyphsFromString()
        self.w.canvas.update()       

    def getGlyphsFromString(self):

        self.glyphName2Glyph = {}

        string = ""
        for e in self.mainInputString:
            string += self.leftInputString
            string += e
            string += self.rightInputString

        txt = splitText(string, self.RCJKI.currentFont.naked().unicodeData)

        self.text = txt

        for glyphName in txt:

            if glyphName in self.RCJKI.currentFont:
                glyph = self.RCJKI.currentFont[glyphName].copy()

    # def decomposeGlyph(self, glyph):

    #     storageFont = self.ui.font2Storage[self.ui.font]
    #     if "deepComponentsGlyph" in glyph.lib:

    #         for deepComp_Name, value in glyph.lib["deepComponentsGlyph"].items():

    #             ID = value[0]
    #             offset_x, offset_Y = value[1]

    #             layersInfo = storageFont.lib["deepComponentsGlyph"][deepComp_Name][ID]

    #             newGlyph = deepolation(RGlyph(), storageFont[deepComp_Name].getLayer("foreground"), layersInfo)

    #             if newGlyph:
    #                 newGlyph.moveBy((offset_x, offset_Y))

    #                 for c in newGlyph:
    #                     glyph.appendContour(c)
    #     return glyph


    def keyDown(self, info):
        char = info.characters()
        command = extractNSEvent(info)['commandDown']

        if char == "i":
            self.inverse = abs(self.inverse - 1)
            self.w.canvas.update()

        if command and char == "+":
            self.scale += self.keyDown_ZoomSensibility

        elif command and char == "-":
            scale = self.scale
            scale -= self.keyDown_ZoomSensibility
            if scale > 0:
                self.scale = scale

        self.w.canvas.update()

    def scrollWheel(self, info):
        alt = extractNSEvent(info)['optionDown']
        deltaY = info.deltaY()

        deltaX = info.deltaX()

        if alt:
            scale = self.scale
            scale += (deltaY / (abs(deltaY)+eps) * self.scrollWheel_ZoomSensibility) / self.scale
            if scale > 0:
                self.scale = scale

        else:
            if not self.verticalMode:
                self.scrollX = 0
                scroll = self.scroll
                scroll -= (deltaY / (abs(deltaY)+eps) * 50) / self.scale
                if scroll < 0:
                    scroll = 0
                self.scroll = scroll

            else:
                self.scroll = 0
                scrollX = self.scrollX
                scrollX += (deltaX / (abs(deltaX)+eps) * 50) / self.scale
                if scrollX < 0:
                    scrollX = 0
                self.scrollX = scrollX

        self.w.canvas.update()

    def mouseDown(self, info):
        pointX, pointY = info.locationInWindow()
        didInside = False

        for loc in self.glyphLocation_in_Window:
            
            x, y, w, h = loc
            if x < (pointX - self.margin) / self.scale -self.scrollX < x+w and y < (pointY+20)/self.scale-self.scroll < y+h:
                self.selectedGlyph = self.glyphLocation_in_Window[loc]
                didInside = True
                if info.clickCount() == 2:
                    self.RCJKI.currentGlyph = self.RCJKI.currentFont[self.selectedGlyph.name]
                    self.RCJKI.openGlyphWindow(self.RCJKI.currentGlyph)

                    # OpenGlyphWindow(self.RCJKI.currentFont[self.selectedGlyph.name])
                    

        if not didInside:
            self.selectedGlyph=None
        self.w.canvas.update()
        

    def draw(self):
        try:
            save()
            self.glyphLocation_in_Window = {}

            inclr = lambda x: abs(x - self.inverse)

            blackColor = (inclr(0), inclr(0), inclr(0), 1)
            whiteColor = (inclr(1), inclr(1), inclr(1), 1)
            selectedColor = (0, 0, inclr(.4), 1)

            rc, gc, bc, ac = whiteColor
            fill(rc, gc, bc, ac)
            rect(0, 0, 10000, 10000)

            scale(self.scale, self.scale)

            columnWidth = self.lineHeight

            ### Margin shift ####
            translate(self.margin / self.scale, -(self.margin / self.scale))

            ### Scroll ####
            translate(self.scrollX, self.scroll)

            save()
            ### Horizontal type setting shift ###
            if not self.verticalMode:
                width = 0
                height = ((self.windowHeight - 80) / self.scale) - self.lineHeight
                translate(width, height)

            else:
                width = self.windowWidth / self.scale - columnWidth - 2*self.margin/self.scale
                height = 0
                initialHeight = ((self.windowHeight - 80) / self.scale) - self.RCJKI.project.settings['designFrame']['em_Dimension'][1]
                translate(width , initialHeight+height)

            for glyphName in self.text:
                if glyphName not in self.RCJKI.currentFont: continue
                if self.RCJKI.currentFont[glyphName].width == 0: continue
                glyph = self.RCJKI.currentFont[glyphName]

                rc, gc, bc, ac = blackColor
                if glyph == self.selectedGlyph:
                    rc, gc, bc, ac = selectedColor

                stroke(None)
                fill(rc, gc, bc, ac)

                if self.RCJKI.settings['showDesignFrame']:
                        self.dfd.draw(
                            glyph = glyph,
                            mainFrames = self.RCJKI.settings['designFrame']['showMainFrames'], 
                            secondLines = self.RCJKI.settings['designFrame']['showSecondLines'], 
                            customsFrames = self.RCJKI.settings['designFrame']['showCustomsFrames'], 
                            proximityPoints = self.RCJKI.settings['designFrame']['showproximityPoints'],
                            translate_secondLine_X = self.RCJKI.settings['designFrame']['translate_secondLine_X'], 
                            translate_secondLine_Y = self.RCJKI.settings['designFrame']['translate_secondLine_Y'],
                            scale = self.scale,
                            inverse = self.inverse
                            )

                if not self.verticalMode:
                    glyphWidth = glyph.width
                else:
                    glyphWidth = columnWidth

                drawGlyph(glyph)
                # rect(0, 0, glyphWidth, self.lineHeight)
                if not self.verticalMode:
                    x, y, w, h = width, height, glyphWidth, self.lineHeight
                else: 
                    x, y, w, h = width, initialHeight-height, glyphWidth, self.RCJKI.project.settings['designFrame']['em_Dimension'][1]

                self.glyphLocation_in_Window[(x, y, w, h)] = glyph

                if not self.verticalMode:
                    translate(x=glyphWidth)
                    width += glyphWidth
                    if width + glyphWidth >= self.windowWidth / self.scale - 2 * (self.margin / self.scale):
                        translate(-width, -self.lineHeight)
                        width = 0
                        height -= self.lineHeight 
                else:
                    translate(y=-self.RCJKI.project.settings['designFrame']['em_Dimension'][1])
                    height += self.RCJKI.project.settings['designFrame']['em_Dimension'][1]
                    if height + self.RCJKI.project.settings['designFrame']['em_Dimension'][1] >= ((self.windowHeight - 80) / self.scale) - 2 * (self.margin / self.scale):
                        translate(-columnWidth, height)
                        height = 0
                        width -= columnWidth
            restore()

            # save()

            # for pos, glyph in self.glyphLocation_in_Window.items():
            #     x, y, w, h = pos 
            #     stroke(1, 0, 0, 1)
            #     fill(None)
            #     if glyph == self.selectedGlyph:
            #         fill(1, 0, 0, .2)
            #     rect(x, y, w, h)

            # restore()


            restore()


        except Exception as e:
            print(e)


