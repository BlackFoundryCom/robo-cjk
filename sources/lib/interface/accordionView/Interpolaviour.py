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

class Interpolaviour(Group):

    def __init__(self, posSize, interface):
        super(Interpolaviour, self).__init__(posSize)
        self.ui = interface

        y = 10
        self.onOff_checkBox = CheckBox((10, y, -10, 20),
            'On/Off',
            value = self.ui.interpolaviourOnOff,
            sizeStyle = "small",
            callback = self._onOff_checkBox_callback)
        y+=20
        self.points_checkBox = CheckBox((10, y, -10, 20),
            'Points',
            value = self.ui.interpolaviourShowPoints,
            sizeStyle = "small",
            callback = self._points_checkBox_callback)
        y+=20
        self.startPoints_checkBox = CheckBox((10, y, -10, 20),
            'Start Points',
            value = self.ui.interpolaviourShowStartPoints,
            sizeStyle = "small",
            callback = self._startPoints_checkBox_callback)
        y+=20
        self.interpolation_checkBox = CheckBox((10, y, -10, 20),
            'Interpolation',
            value = self.ui.interpolaviourShowInterpolation,
            sizeStyle = "small",
            callback = self._interpolation_checkBox_callback)
        y+=22
        self.interpolationValue_Slider = Slider((10, y, -10, 20),
            minValue = 0,
            maxValue = 1000,
            value = self.ui.interpolaviourInterpolationValue,
            sizeStyle = "small",
            callback = self._interpolationValue_Slider_callback)
        y+=30
        self.deduce_button = SquareButton((0, y, -0, 30),
            'Deduce',
            sizeStyle = "small",
            callback = self._deduce_button_callback)

    def _onOff_checkBox_callback(self, sender):
        self.ui.interpolaviourOnOff = sender.get()
        self.ui.updateViews()
        
    def _points_checkBox_callback(self, sender):
        self.ui.interpolaviourShowPoints = sender.get()
        self.ui.updateViews()

    def _startPoints_checkBox_callback(self, sender):
        self.ui.interpolaviourShowStartPoints = sender.get()
        self.ui.updateViews()

    def _interpolation_checkBox_callback(self, sender):
        self.ui.interpolaviourShowInterpolation = sender.get()
        self.ui.updateViews()

    def _interpolationValue_Slider_callback(self, sender):
        self.ui.interpolaviourInterpolationValue = int(sender.get())
        self.ui.updateViews()

    def _deduce_button_callback(self, sender):
        pass

