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

class ToolsBoxWindow():

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.w = Window((-200, 0, -0, 400),
            'Tools',
            closable = False,
            textured = True,
            miniaturizable = False)

        # self.displayOption = DisplayOptions((0,0,-0,-0), self)

  #       self.referenceViewer = ReferenceViewer((0,0,-0,-0), self)

  #       self.designFrame = DesignFrame((0,0,-0,-0), self)

        
        self.displayOption = Group((0,0,-0,-0))

        self.referenceViewer = Group((0,0,-0,-0))

        self.designFrame = Group((0,0,-0,-0))

        self.interpolaviour = Interpolaviour((0,0,-0,-0), self.RCJKI)

        self.accordionViewDescriptions = [
                        dict(label="Interpolaviour", 
                            view=self.interpolaviour, 
                            size=150, 
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

        self.w.open()

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
            maxValue = 1000,
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
        self.RCJKI.toolsBoxController.updateViews()
        
    def _points_checkBox_callback(self, sender): 
        self.RCJKI.settings["interpolaviour"]["showPoints"] = sender.get()
        self.RCJKI.toolsBoxController.updateViews()

    def _startPoints_checkBox_callback(self, sender): 
        self.RCJKI.settings["interpolaviour"]["showStartPoints"] = sender.get()
        self.RCJKI.toolsBoxController.updateViews()

    def _interpolation_checkBox_callback(self, sender): 
        self.RCJKI.settings["interpolaviour"]["showInterpolation"] = sender.get()
        self.RCJKI.toolsBoxController.updateViews()

    def _interpolationValue_Slider_callback(self, sender): 
        self.RCJKI.settings["interpolaviour"]["interpolationValue"] = sender.get()
        self.RCJKI.toolsBoxController.updateViews()

    def _deduce_button_callback(self, sender):
        pass
        