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

class LayersPreviewCanvas():
    
    def __init__(self, interface, glyphLayerGroup):
        self.ui = interface
        self.gl = glyphLayerGroup
        self.translateX, self.translateY = 194,40
        self.scale = .15
        
    def mouseDragged(self, info):
        deltaX = info.deltaX()/self.scale
        deltaY = info.deltaY()/self.scale
        self.translateX += deltaX
        self.translateY -= deltaY
        self.update()
        
    def update(self):
        self.gl.layersPreviewCanvas.update()
        
    def draw(self):
        try:
            if self.gl.storageGlyph is None:
                return
            newGlyph = deepolation(RGlyph(), self.gl.storageGlyph, layersInfo = {e["Layer"]:int(e["Values"]) for e in self.gl.slidersValuesList})
            if not newGlyph:
                fill(.9,0,.3,1)
                rect(0,0,1000,1000)
            else:
                scale(self.scale, self.scale)
                translate(0,200)
                translate(self.translateX, self.translateY)
                DesignFrameDrawer(self.ui).draw(glyph = newGlyph, scale = self.scale)
                fill(0,0,0,1)
                drawGlyph(newGlyph)

        except Exception as e:
            print(e)