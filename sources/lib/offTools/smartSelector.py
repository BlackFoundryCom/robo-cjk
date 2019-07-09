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

from mojo.extensions import ExtensionBundle
from mojo.events import EditingTool
from vanilla import *
# from AppKit import *
import os

toolbarIcon = ExtensionBundle("sources/resources").get("SmartSelectorIcon")
# print(toolbarIcon)

class SmartSelector(EditingTool):

    def __init__(self, interface):
        super(SmartSelector, self).__init__()
        self.ui = interface

    def mouseUp(self, point):
        g = self.getGlyph()
        anythingSelected = False
        contours = []
        for p in g.selection:
            c = p.getParent()
            if c not in contours:
                contours.append(c)
        for c in contours:
            anythingSelected = True
            c.selected = True 

    def getToolbarIcon(self):
        return toolbarIcon

    def getToolbarTip(self):
        return "SmartSelector"
