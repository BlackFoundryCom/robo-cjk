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
from mojo.drawingTools import *
from mojo.roboFont import *

class ReferenceViewerDraw():

    def __init__(self, controller, text):
        self.c = controller
        self.t = text
        self.draw()

    def draw(self):
        save()
        for settings in self.c.referenceViewerSettings:
            fontFamily = settings['font']
            size = settings['size']
            color = settings['color']
            x = settings['x']
            y = settings['y']

            font(fontFamily, size)
            r, g, b, a = color
            fill(r, g, b, a)
            text(self.t, (x, y))

            font(fontFamily, 20)
            text(fontFamily, (x, y-10))
        restore()