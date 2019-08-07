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

class DisplayOptions(Group):

    def __init__(self, posSize, interface):
        super(DisplayOptions, self).__init__(posSize)
        self.ui = interface
        
        self.stackMasters_CheckBox = CheckBox((10,5,-10,20), 
            "Stack Masters",
            value = self.ui.stackMasters,
            sizeStyle = "small", 
            callback = self._stackMasters_CheckBox_callback)

        self.waterFall_CheckBox = CheckBox((10,25,-10,20), 
            "Water Fall",
            value = self.ui.waterFall,
            sizeStyle = "small", 
            callback = self._waterFall_CheckBox_callback)

    def _stackMasters_CheckBox_callback(self, sender):
        self.ui.stackMasters = sender.get()
        self.ui.updateViews()

    def _waterFall_CheckBox_callback(self, sender):
        self.ui.waterFall = sender.get()
        self.ui.updateViews()