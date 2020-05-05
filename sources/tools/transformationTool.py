"""
Copyright 2020 Black Foundry.

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
from mojo.events import BaseEventTool, getActiveEventTool
from mojo.UI import UpdateCurrentGlyphView
from AppKit import NSImage
from utils import decorators
reload(decorators)
glyphTransformUndo = decorators.glyphTransformUndo
import math
import os

toolbarIcon = NSImage.alloc().initByReferencingFile_(os.path.join(os.getcwd(), "resources/TransformationTool.pdf"))

def angle(cx: int, cy: int, ex: int, ey: int) -> int:
        dy = ey - cy
        dx = ex - cx
        theta = math.atan2(dx, dy)
        theta *= 180 / math.pi
        return theta

class TransformationTool(BaseEventTool):

    def __init__(self, RCJKI):
        super().__init__()
        self.RCJKI = RCJKI

    def getToolbarIcon(self):
        return toolbarIcon

    def becomeActive(self):
        self.RCJKI.transformationToolIsActiv = True

    def becomeInactive(self):
        self.RCJKI.transformationToolIsActiv = False

    @glyphTransformUndo
    def mouseDown(self, point, clickcount):
        self.px, self.py = self.deltax, self.deltay = point

    def mouseDragged(self, point, delta):
        modifiers = getActiveEventTool().getModifiers()
        option = modifiers['optionDown']
        command = modifiers['commandDown']
        shift = modifiers['shiftDown']

        def shiftLock(dx, dy, x, y):
            if abs(dx) > abs(dy):
                return x, 0
            return 0, y
        
        if option:
            rotation = angle(self.px, self.py, *point)
            self.RCJKI.currentGlyph.setRotationAngleToSelectedElements(rotation, append = False)
            
        elif command:
            deltax = int(point.x - self.deltax)
            deltay = int(point.y - self.deltay)
            sensibility = 500
            deltax /= sensibility
            deltay /= sensibility
            if shift:
                deltax, deltay = shiftLock(delta.x, delta.y, deltax, deltay)
            self.RCJKI.currentGlyph.setScaleToSelectedElements((round(deltax, 3), round(deltay, 3)))
            
        else:
            x = int(point.x - self.deltax)
            y = int(point.y - self.deltay)
            if shift:
                x, y = shiftLock(delta.x, delta.y, x, y)
            self.RCJKI.currentGlyph.setPositionToSelectedElements((x, y))

        self.deltax, self.deltay = point
        UpdateCurrentGlyphView()
