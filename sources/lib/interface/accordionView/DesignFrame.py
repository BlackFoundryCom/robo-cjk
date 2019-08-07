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
        # self.ui.glyph = self.ui.glyph

        self.ui.onOff_designFrame = 1
        self.ui.drawPreview_designFrame = 0
        self.ui.showMainFrames = 1
        self.ui.showproximityPoints = 1
        self.ui.showSecondLines = 1
        self.ui.showCustomsFrames = 1
        self.ui.translate_secondLine_X = 0
        self.ui.translate_secondLine_Y = 0

        if self.ui.glyph is not None:
            if "DesignFrame" in self.ui.glyph.lib:
                self.ui.translate_secondLine_X = self.ui.glyph.lib["DesignFrame"]["secondeLines"][0]
                self.ui.translate_secondLine_Y = self.ui.glyph.lib["DesignFrame"]["secondeLines"][1]

        y = 5
        self.onOff_checkBox = CheckBox((10,y,-10,20),
                "On/Off",
                value = self.ui.onOff_designFrame,
                sizeStyle = "small",
                callback = self._onOff_checkBox_callback)
        y += 20
        self.drawPreview_designFrame_checkBox = CheckBox((10,y,-10,20),
                'Draw Preview',
                value = self.ui.drawPreview_designFrame,
                sizeStyle = "small",
                callback = self._drawPreview_designFrame_checkBox_callback)
        y += 20
        self.showMainFrames_checkBox = CheckBox((10,y,-10,20),
                "Main Frames",
                value = self.ui.showMainFrames,
                sizeStyle = "small",
                callback = self._showMainFrames_checkBox_callback)
        y += 20
        self.showproximityPoints_checkBox = CheckBox((10,y,-10,20),
                "Proximity Points",
                value = self.ui.showproximityPoints,
                sizeStyle = "small",
                callback = self._showproximityPoints_checkBox_callback)
        y += 20
        self.showSecondLines_checkBox = CheckBox((10,y,-10,20),
                "Second Lines",
                value = self.ui.showSecondLines,
                sizeStyle = "small",
                callback = self._showSecondLines_checkBox_callback)
        
        y += 20
        self.translate_secondLine_X_slider = Slider((25,y,-10,20),
                minValue = -500,
                maxValue = 500,
                value = self.ui.translate_secondLine_X,
                sizeStyle = "small",
                callback = self._translate_secondLine_X_slider_callback)
        y += 20
        self.translate_secondLine_Y_slider = Slider((25,y,-10,20),
                minValue = -500,
                maxValue = 500,
                value = self.ui.translate_secondLine_Y,
                sizeStyle = "small",
                callback = self._translate_secondLine_Y_slider_callback)
        y += 20
        self.showCustomsFrames_checkBox = CheckBox((10,y,-10,20),
                "Customs Frames",
                value = self.ui.showCustomsFrames,
                sizeStyle = "small",
                callback = self._showCustomsFrames_checkBox_callback)

        self.ui.w.bind('close', self.windowWillClose)
        self.observer()

    def _onOff_checkBox_callback(self, sender):
        self.ui.onOff_designFrame = sender.get()
        self.ui.updateViews()

    def _drawPreview_designFrame_checkBox_callback(self, sender):
        self.drawPreview_designFrame = sender.get()
        self.ui.updateViews()

    def _showMainFrames_checkBox_callback(self, sender):
        self.ui.showMainFrames = sender.get()
        self.ui.updateViews()

    def _showproximityPoints_checkBox_callback(self, sender):
        self.ui.showproximityPoints = sender.get()
        self.ui.updateViews()

    def _showSecondLines_checkBox_callback(self, sender):
        self.ui.showSecondLines = sender.get()
        self.translate_secondLine_X_slider.show(self.ui.showSecondLines)
        self.translate_secondLine_Y_slider.show(self.ui.showSecondLines)
        self.ui.updateViews()

    def _showCustomsFrames_checkBox_callback(self, sender):
        self.ui.showCustomsFrames = sender.get()
        self.ui.updateViews()

    def _translate_secondLine_X_slider_callback(self, sender):
        self.ui.translate_secondLine_X = int(sender.get())
        self.set_DesignFrame_GlyphLib_Data()
        self.ui.updateViews()

    def set_DesignFrame_GlyphLib_Data(self):
        if self.ui.glyph is not None:
            if "DesignFrame" in self.ui.glyph.lib:
                self.ui.glyph.lib["DesignFrame"]["secondeLines"][0] = self.ui.translate_secondLine_X
                self.ui.glyph.lib["DesignFrame"]["secondeLines"][1] = self.ui.translate_secondLine_Y
            else:
                self.ui.glyph.lib["DesignFrame"] = {"secondeLines":[self.ui.translate_secondLine_X, self.ui.translate_secondLine_Y]}

    def _translate_secondLine_Y_slider_callback(self, sender):
        self.ui.translate_secondLine_Y = int(sender.get())
        self.set_DesignFrame_GlyphLib_Data()
        self.ui.updateViews()

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
        self.ui.glyph = info['glyph']
        if self.ui.glyph is not None:
            if "DesignFrame" in self.ui.glyph.lib:
                self.ui.translate_secondLine_X = self.ui.glyph.lib["DesignFrame"]["secondeLines"][0]
                self.ui.translate_secondLine_Y = self.ui.glyph.lib["DesignFrame"]["secondeLines"][1]
                self.ui.translate_secondLine_X_slider.set(self.ui.translate_secondLine_X)
                self.ui.translate_secondLine_Y_slider.set(self.ui.translate_secondLine_Y)
        self.ui.updateViews()

    def draw(self, info):
        self.ui.glyph = self.ui.glyph
        if not self.ui.onOff_designFrame: return
        if info['notificationName'] == "drawPreview" and not self.ui.drawPreview_designFrame: return
        s = info['scale']
        strokeWidth(.6*s)
        DesignFrameDrawer(self.ui).draw(
            glyph = self.ui.glyph,
            mainFrames = self.ui.showMainFrames, 
            secondLines = self.ui.showSecondLines, 
            customsFrames = self.ui.showCustomsFrames, 
            proximityPoints = self.ui.showproximityPoints,
            translate_secondLine_X = self.ui.translate_secondLine_X, 
            translate_secondLine_Y = self.ui.translate_secondLine_Y,
            scale = s)
