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
from mojo.drawingTools import *
from mojo.events import extractNSEvent
from Helpers import deepolation
from drawers.DesignFrameDrawer import DesignFrameDrawer
from mojo.roboFont import *

class TesterDeepComponent():

    translateX,translateY  = 0,0
    
    def __init__(self, interface, glyphLayerGroup):
        self.ui = interface
        self.gl = glyphLayerGroup
        self.scale = .15
        self.draw()
        
    def draw(self):
        try:
            if self.gl.storageGlyph is None:
                return
            newGlyph = deepolation(RGlyph(), self.gl.storageGlyph, layersInfo = {e["Layer"]:int(e["Values"]) for e in self.gl.slidersValuesList})
            if not newGlyph:
                save()
                fill(.9,0,.3,.4)
                oval(0,0,1000,1000)
                restore()
            else:
                save()
                translate(self.translateX, self.translateY)
                fill(1,0,0,.8)
                drawGlyph(newGlyph)
                restore()

        except Exception as e:
            print(e)