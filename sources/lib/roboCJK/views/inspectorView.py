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
#coding=utf-8
from vanilla import *
from mojo.UI import AccordionView

class Inspector():

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.w = Window((-200, 0, -0, 400),
            'Inspector',
            minSize = (200, 200),
            maxSize = (200, 1000))

        self.interpolaviour = Interpolaviour((0,0,-0,-0), self.RCJKI)

        self.displayOption = DisplayOptions((0,0,-0,-0), self.RCJKI)

        self.referenceViewer = ReferenceViewer((0,0,-0,-0), self.RCJKI)

        self.designFrame = DesignFrame((0,0,-0,-0), self.RCJKI)

        self.accordionViewDescriptions = [
                        dict(label="Interpolaviour", 
                            view=self.interpolaviour, 
                            size=160, 
                            collapsed=False, 
                            canResize=0),

                        dict(label="Display Options", 
                            view=self.displayOption, 
                            size=55, 
                            collapsed=True, 
                            canResize=0),

                        dict(label="Reference Viewer", 
                            view=self.referenceViewer, 
                            size=55, 
                            collapsed=True, 
                            canResize=0),

                        dict(label="Design Frame", 
                            view=self.designFrame, 
                            size=173, 
                            collapsed=True, 
                            canResize=0),
                       ]

        self.w.accordionView = AccordionView((0, 0, -0, -0),
            self.accordionViewDescriptions,
            )
        self.w.bind('close', self.windowCloses)
        self.w.open()

    def windowCloses(self, sender):
        self.RCJKI.inspectorController.interface = None

class Interpolaviour(Group):

    def __init__(self, posSize, RCJKI):
        super(Interpolaviour, self).__init__(posSize)
        self.RCJKI = RCJKI

        y = 10
        self.onOff_checkBox = CheckBox((10, y, -10, 20),
            'On/Off',
            value = self.RCJKI.settings["interpolaviour"]["onOff"],
            sizeStyle = "small",
            callback = self._onOff_checkBox_callback)
        y+=20
        self.points_checkBox = CheckBox((10, y, -10, 20),
            'Points',
            value = self.RCJKI.settings["interpolaviour"]["showPoints"],
            sizeStyle = "small",
            callback = self._points_checkBox_callback)
        y+=20
        self.startPoints_checkBox = CheckBox((10, y, -10, 20),
            'Start Points',
            value = self.RCJKI.settings["interpolaviour"]["showStartPoints"],
            sizeStyle = "small",
            callback = self._startPoints_checkBox_callback)
        y+=20
        self.interpolation_checkBox = CheckBox((10, y, -10, 20),
            'Interpolation',
            value = self.RCJKI.settings["interpolaviour"]["showInterpolation"],
            sizeStyle = "small",
            callback = self._interpolation_checkBox_callback)
        y+=22
        self.interpolationValue_Slider = Slider((10, y, -10, 20),
            minValue = 0,
            maxValue = 1,
            value = self.RCJKI.settings["interpolaviour"]["interpolationValue"],
            sizeStyle = "small",
            callback = self._interpolationValue_Slider_callback)
        y+=30
        self.deduce_button = SquareButton((0, y, -0, 30),
            'Deduce',
            sizeStyle = "small",
            callback = self._deduce_button_callback)

    def _onOff_checkBox_callback(self, sender): 
        self.RCJKI.settings["interpolaviour"]["onOff"] = sender.get()
        self.RCJKI.inspectorController.updateViews()
        
    def _points_checkBox_callback(self, sender): 
        self.RCJKI.settings["interpolaviour"]["showPoints"] = sender.get()
        self.RCJKI.inspectorController.updateViews()

    def _startPoints_checkBox_callback(self, sender): 
        self.RCJKI.settings["interpolaviour"]["showStartPoints"] = sender.get()
        self.RCJKI.inspectorController.updateViews()

    def _interpolation_checkBox_callback(self, sender): 
        self.RCJKI.settings["interpolaviour"]["showInterpolation"] = sender.get()
        self.RCJKI.inspectorController.updateViews()

    def _interpolationValue_Slider_callback(self, sender): 
        self.RCJKI.settings["interpolaviour"]["interpolationValue"] = sender.get()
        self.RCJKI.inspectorController.updateViews()

    def _deduce_button_callback(self, sender):
        pass

class DisplayOptions(Group):

    def __init__(self, posSize, RCJKI):
        super(DisplayOptions, self).__init__(posSize)
        self.RCJKI = RCJKI
        
        self.stackMasters_CheckBox = CheckBox((10,5,-10,20), 
            "Stack Masters",
            value = self.RCJKI.settings["stackMasters"],
            sizeStyle = "small", 
            callback = self._stackMasters_CheckBox_callback)

        self.waterFall_CheckBox = CheckBox((10,25,-10,20), 
            "Water Fall",
            value = self.RCJKI.settings["waterFall"],
            sizeStyle = "small", 
            callback = self._waterFall_CheckBox_callback)

    def _stackMasters_CheckBox_callback(self, sender):
        self.RCJKI.settings["stackMasters"] = sender.get()
        self.RCJKI.inspectorController.updateViews()

    def _waterFall_CheckBox_callback(self, sender):
        self.RCJKI.settings["waterFall"] = sender.get()
        self.RCJKI.inspectorController.updateViews()

class ReferenceViewer(Group):

    def __init__(self, posSize, RCJKI):
        super(ReferenceViewer, self).__init__(posSize)
        self.RCJKI = RCJKI
        
        self.OnOff_referenceViewer_checkBox = CheckBox((10,5,-10,20),
                'On/Off',
                value = self.RCJKI.settings["referenceViewer"]["onOff"],
                sizeStyle = "small",
                callback = self._OnOff_referenceViewer_callback)

        self.drawPreview_referenceViewer_checkBox = CheckBox((10,25,-10,20),
                'Draw Preview',
                value = self.RCJKI.settings["referenceViewer"]["drawPreview"],
                sizeStyle = "small",
                callback = self._drawPreview_referenceViewer_callback)

    def _OnOff_referenceViewer_callback(self, sender):
        self.RCJKI.settings["referenceViewer"]["onOff"] = sender.get()
        self.RCJKI.inspectorController.updateViews()

    def _drawPreview_referenceViewer_callback(self, sender):
        self.RCJKI.settings["referenceViewer"]["drawPreview"] = sender.get()
        self.RCJKI.inspectorController.updateViews()


class DesignFrame(Group):

    def __init__(self, posSize, RCJKI):
        super(DesignFrame, self).__init__(posSize)
        self.RCJKI = RCJKI

        if self.RCJKI.currentGlyph is not None:
            if "DesignFrame" in self.RCJKI.currentGlyph.lib:
                self.RCJKI.settings["designFrame"]["translate_secondLine_X"] = self.RCJKI.currentGlyph.lib["DesignFrame"]["secondeLines"][0]
                self.RCJKI.settings["designFrame"]["translate_secondLine_Y"] = self.RCJKI.currentGlyph.lib["DesignFrame"]["secondeLines"][1]

        y = 5
        self.onOff_checkBox = CheckBox((10,y,-10,20),
                "On/Off",
                value = self.RCJKI.settings["showDesignFrame"],
                sizeStyle = "small",
                callback = self._onOff_checkBox_callback)
        y += 20
        self.drawPreview_designFrame_checkBox = CheckBox((10,y,-10,20),
                'Draw Preview',
                value = self.RCJKI.settings["designFrame"]["drawPreview"],
                sizeStyle = "small",
                callback = self._drawPreview_designFrame_checkBox_callback)
        y += 20
        self.showMainFrames_checkBox = CheckBox((10,y,-10,20),
                "Main Frames",
                value = self.RCJKI.settings["designFrame"]["showMainFrames"],
                sizeStyle = "small",
                callback = self._showMainFrames_checkBox_callback)
        y += 20
        self.showproximityPoints_checkBox = CheckBox((10,y,-10,20),
                "Proximity Points",
                value = self.RCJKI.settings["designFrame"]["showproximityPoints"],
                sizeStyle = "small",
                callback = self._showproximityPoints_checkBox_callback)
        y += 20
        self.showSecondLines_checkBox = CheckBox((10,y,-10,20),
                "Second Lines",
                value = self.RCJKI.settings["designFrame"]["showSecondLines"],
                sizeStyle = "small",
                callback = self._showSecondLines_checkBox_callback)
        y += 20
        self.translate_secondLine_X_slider = Slider((25,y,-10,20),
                minValue = -500,
                maxValue = 500,
                value = self.RCJKI.settings["designFrame"]["translate_secondLine_X"],
                sizeStyle = "small",
                callback = self._translate_secondLine_X_slider_callback)
        y += 20
        self.translate_secondLine_Y_slider = Slider((25,y,-10,20),
                minValue = -500,
                maxValue = 500,
                value = self.RCJKI.settings["designFrame"]["translate_secondLine_Y"],
                sizeStyle = "small",
                callback = self._translate_secondLine_Y_slider_callback)
        y += 20
        self.showCustomsFrames_checkBox = CheckBox((10,y,-10,20),
                "Customs Frames",
                value = self.RCJKI.settings["designFrame"]["showCustomsFrames"],
                sizeStyle = "small",
                callback = self._showCustomsFrames_checkBox_callback)

    def _onOff_checkBox_callback(self, sender):
        self.RCJKI.settings["showDesignFrame"] = sender.get()
        self.RCJKI.inspectorController.updateViews()

    def _drawPreview_designFrame_checkBox_callback(self, sender):
        self.RCJKI.settings["designFrame"]["drawPreview"] = sender.get()
        self.RCJKI.inspectorController.updateViews()

    def _showMainFrames_checkBox_callback(self, sender):
        self.RCJKI.settings["designFrame"]["showMainFrames"] = sender.get()
        self.RCJKI.inspectorController.updateViews()

    def _showproximityPoints_checkBox_callback(self, sender):
        self.RCJKI.settings["designFrame"]["showproximityPoints"] = sender.get()
        self.RCJKI.inspectorController.updateViews()

    def _showSecondLines_checkBox_callback(self, sender):
        self.RCJKI.settings["designFrame"]["showSecondLines"] = sender.get()
        self.translate_secondLine_X_slider.show(self.RCJKI.settings["designFrame"]["showSecondLines"])
        self.translate_secondLine_Y_slider.show(self.RCJKI.settings["designFrame"]["showSecondLines"])
        self.RCJKI.inspectorController.updateViews()

    def _showCustomsFrames_checkBox_callback(self, sender):
        self.RCJKI.settings["designFrame"]["showCustomsFrames"] = sender.get()
        self.RCJKI.inspectorController.updateViews()

    def _translate_secondLine_X_slider_callback(self, sender):
        self.RCJKI.settings["designFrame"]["translate_secondLine_X"] = int(sender.get())
        self.set_DesignFrame_GlyphLib_Data()
        self.RCJKI.inspectorController.updateViews()

    def _translate_secondLine_Y_slider_callback(self, sender):
        self.RCJKI.settings["designFrame"]["translate_secondLine_Y"] = int(sender.get())
        self.set_DesignFrame_GlyphLib_Data()
        self.RCJKI.inspectorController.updateViews()

    def set_DesignFrame_GlyphLib_Data(self):
        if self.RCJKI.currentGlyph is not None:
            if "DesignFrame" in self.RCJKI.currentGlyph.lib:
                self.RCJKI.currentGlyph.lib["DesignFrame"]["secondeLines"][0] = self.RCJKI.settings["designFrame"]["translate_secondLine_X"]
                self.RCJKI.currentGlyph.lib["DesignFrame"]["secondeLines"][1] = self.RCJKI.settings["designFrame"]["translate_secondLine_Y"]
            else:
                self.RCJKI.currentGlyph.lib["DesignFrame"] = {"secondeLines":[self.RCJKI.settings["designFrame"]["translate_secondLine_X"], self.RCJKI.settings["designFrame"]["translate_secondLine_Y"]]}

