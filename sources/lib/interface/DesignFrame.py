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
from mojo.events import addObserver, removeObserver
from mojo.UI import UpdateCurrentGlyphView
from mojo.drawingTools import *
from imp import reload
from drawers.DesignFrameDrawer import DesignFrameDrawer

class DesignFrame(Group):

    def __init__(self, posSize, interface):
        super(DesignFrame, self).__init__(posSize)
        self.ui = interface
        self.glyph = self.ui.glyph

        self.onOff_designFrame = 1
        self.drawPreview_designFrame = 1
        self.showMainFrames = 1
        self.showproximityPoints = 1
        self.showSecondLines = 1
        self.showCustomsFrames = 1
        self.translate_secondLine_X = 0
        self.translate_secondLine_Y = 0

        if self.glyph is not None:
            if "DesignFrame" in self.glyph.lib:
                self.translate_secondLine_X = self.glyph.lib["DesignFrame"]["secondeLines"][0]
                self.translate_secondLine_Y = self.glyph.lib["DesignFrame"]["secondeLines"][1]

        y = 5
        self.onOff_checkBox = CheckBox((10,y,-10,20),
                "On/Off",
                value = self.onOff_designFrame,
                sizeStyle = "small",
                callback = self._onOff_checkBox_callback)
        y += 20
        self.drawPreview_designFrame_checkBox = CheckBox((10,y,-10,20),
                'Draw Preview',
                value = self.drawPreview_designFrame,
                sizeStyle = "small",
                callback = self._drawPreview_designFrame_checkBox_callback)
        y += 20
        self.showMainFrames_checkBox = CheckBox((10,y,-10,20),
                "Main Frames",
                value = self.showMainFrames,
                sizeStyle = "small",
                callback = self._showMainFrames_checkBox_callback)
        y += 20
        self.showproximityPoints_checkBox = CheckBox((10,y,-10,20),
                "Proximity Points",
                value = self.showproximityPoints,
                sizeStyle = "small",
                callback = self._showproximityPoints_checkBox_callback)
        y += 20
        self.showSecondLines_checkBox = CheckBox((10,y,-10,20),
                "Second Lines",
                value = self.showSecondLines,
                sizeStyle = "small",
                callback = self._showSecondLines_checkBox_callback)
        
        y += 20
        self.translate_secondLine_X_slider = Slider((25,y,-10,20),
                minValue = -500,
                maxValue = 500,
                value = self.translate_secondLine_X,
                sizeStyle = "small",
                callback = self._translate_secondLine_X_slider_callback)
        y += 20
        self.translate_secondLine_Y_slider = Slider((25,y,-10,20),
                minValue = -500,
                maxValue = 500,
                value = self.translate_secondLine_Y,
                sizeStyle = "small",
                callback = self._translate_secondLine_Y_slider_callback)
        y += 20
        self.showCustomsFrames_checkBox = CheckBox((10,y,-10,20),
                "Customs Frames",
                value = self.showCustomsFrames,
                sizeStyle = "small",
                callback = self._showCustomsFrames_checkBox_callback)

        self.ui.w.bind('close', self.windowWillClose)
        self.observer()

    def _onOff_checkBox_callback(self, sender):
        self.onOff_designFrame = sender.get()
        UpdateCurrentGlyphView()

    def _drawPreview_designFrame_checkBox_callback(self, sender):
        self.drawPreview_designFrame = sender.get()
        UpdateCurrentGlyphView()

    def _showMainFrames_checkBox_callback(self, sender):
        self.showMainFrames = sender.get()
        UpdateCurrentGlyphView()

    def _showproximityPoints_checkBox_callback(self, sender):
        self.showproximityPoints = sender.get()
        UpdateCurrentGlyphView()

    def _showSecondLines_checkBox_callback(self, sender):
        self.showSecondLines = sender.get()
        self.translate_secondLine_X_slider.show(self.showSecondLines)
        self.translate_secondLine_Y_slider.show(self.showSecondLines)
        UpdateCurrentGlyphView()

    def _showCustomsFrames_checkBox_callback(self, sender):
        self.showCustomsFrames = sender.get()
        UpdateCurrentGlyphView()

    def _translate_secondLine_X_slider_callback(self, sender):
        self.translate_secondLine_X = int(sender.get())
        self.set_DesignFrame_GlyphLib_Data()
        UpdateCurrentGlyphView()

    def set_DesignFrame_GlyphLib_Data(self):
        if self.glyph is not None:
            if "DesignFrame" in self.glyph.lib:
                self.glyph.lib["DesignFrame"]["secondeLines"][0] = self.translate_secondLine_X
                self.glyph.lib["DesignFrame"]["secondeLines"][1] = self.translate_secondLine_Y
            else:
                self.glyph.lib["DesignFrame"] = {"secondeLines":[self.translate_secondLine_X, self.translate_secondLine_Y]}

    def _translate_secondLine_Y_slider_callback(self, sender):
        self.translate_secondLine_Y = int(sender.get())
        self.set_DesignFrame_GlyphLib_Data()
        UpdateCurrentGlyphView()

    def windowWillClose(self, sender):
        self.observer(remove=True)
        
    def observer(self, remove = False):
        if not remove:
            addObserver(self, "draw", "draw")
            addObserver(self, "draw", "drawPreview")
            addObserver(self, "draw", "drawInactive")
            addObserver(self, "currentGlyphChanged", "currentGlyphChanged")
            return
        removeObserver(self, "draw")
        removeObserver(self, "drawPreview")
        removeObserver(self, "drawInactive")
        removeObserver(self, "currentGlyphChanged")

    def currentGlyphChanged(self, info):
        self.glyph = info['glyph']
        if self.glyph is not None:
            if "DesignFrame" in self.glyph.lib:
                self.translate_secondLine_X = self.glyph.lib["DesignFrame"]["secondeLines"][0]
                self.translate_secondLine_Y = self.glyph.lib["DesignFrame"]["secondeLines"][1]
                self.translate_secondLine_X_slider.set(self.translate_secondLine_X)
                self.translate_secondLine_Y_slider.set(self.translate_secondLine_Y)
        UpdateCurrentGlyphView()

    def draw(self, info):
        self.glyph = self.ui.glyph
        if not self.onOff_designFrame: return
        if info['notificationName'] == "drawPreview" and not self.drawPreview_designFrame: return
        s = info['scale']
        strokeWidth(.6*s)
        DesignFrameDrawer(self.ui).draw(
            mainFrames = self.showMainFrames, 
            secondLines = self.showSecondLines, 
            customsFrames = self.showCustomsFrames, 
            proximityPoints = self.showproximityPoints,
            translate_secondLine_X = self.translate_secondLine_X, 
            translate_secondLine_Y = self.translate_secondLine_Y,
            scale = s)
