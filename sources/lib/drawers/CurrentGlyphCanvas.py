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
from drawers.DesignFrameDrawer import DesignFrameDrawer


class CurrentGlyphCanvas():

    def __init__(self, interface):
        self.ui = interface
        self.scale = .22
        self.canvasWidth = 386

    def draw(self):
    	try:
    		g = self.ui.glyph
    		if g is None: return
    		scale(self.scale, self.scale)
    		translate(((self.canvasWidth/self.scale)-1000)*.5,250)
    		drawGlyph(g)
    		DesignFrameDrawer(self.ui).draw(scale = self.scale)
    	except Exception as e:
    		print(e)