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
from Helpers import deepolation

class CurrentGlyphViewDrawer():

	def __init__(self, interface):
		self.ui = interface

	def draw(self):
		g = self.ui.glyph
		f = self.ui.font2Storage[self.ui.font]
		if "deepComponentsGlyph" not in g.lib: return
		save()
		for glyphName, value in g.lib["deepComponentsGlyph"].items():
			ID = value[0]
			offset_X, offset_Y = value[1]
			layersInfo = f.lib["deepComponentsGlyph"][glyphName][ID]
			newGlyph = deepolation(RGlyph(), f[glyphName].getLayer("foreground"), layersInfo)
			fill(.2, 0, 1, .5)
			translate(offset_X, offset_Y)
			drawGlyph(newGlyph)
		restore()

"""
def deepolation(newGlyph, masterGlyph, layersInfo = {}):
    
    if not deepCompatible(masterGlyph, list(layersInfo.keys())):
        return False
    
    pen = PointToSegmentPen(newGlyph.getPen())
    
    for contourIndex, contour in enumerate(masterGlyph):
        
        pen.beginPath()
        
        for pointIndex, point in enumerate(contour.points):
            
            px, py = point.x, point.y
            ptype = point.type if point.type != 'offcurve' else None
            
            points = [(px, py)]
            for layerName, value in layersInfo.items():
                
                ratio = value/1000*len(layersInfo+1)
                layerGlyph = masterGlyph.getLayer(layerName)
                
                pI = layerGlyph[contourIndex].points[pointIndex]
                pxI, pyI = pI.x, pI.y
                
                newPx = px + (pxI - px) * ratio
                newPy = py + (pyI - py) * ratio
                
                points.append((newPx, newPy))
                
            newX = int(sum(p[0] for p in points) / len(points))
            newY = int(sum(p[1] for p in points) / len(points))
            pen.addPoint((newX, newY), ptype)
            
        pen.endPath()
        
    return newGlyph
"""