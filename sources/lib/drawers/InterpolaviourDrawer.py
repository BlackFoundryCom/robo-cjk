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
from Helpers import (interpol_glyph_glyph_ratioX_ratioY_scaleX_scaleY_toFont_glyphName,
	checkInterpolationResult)

class InterpolaviourDrawer():

	def __init__(self, interface):
		self.ui = interface

	def drawPoints(self, glyph, scale):
		save()
		if self.ui.interpolaviourShowPoints:
			fill(0, .5, 1, 1)
			for x, y, ptype in [(p.x, p.y, p.type) for c in glyph for p in c.points]:
				w, h = 4 / scale, 4 / scale
				if ptype == "offcurve":
					w, h = 3 / scale, 3 / scale
				x -= w / 2
				y -= h / 2
				if ptype == "offcurve":
					oval(x, y, w, h)
				else:
					rect(x, y, w, h)
			fill(None)
			stroke(0, .5, 1, 1)
			strokeWidth(1/scale)
			drawGlyph(glyph)
		restore()

	def drawStartPoints(self, glyph, scale):
		save()
		if self.ui.interpolaviourShowStartPoints:
			fill(1, 0, 0, 1)
			for x, y in [(c.points[0].x, c.points[0].y) for c in glyph]:
				w, h = 5 / scale, 5 / scale
				x -= w / 2
				y -= h / 2
				oval(x, y, w, h)
		restore()

	def draw(self, glyph, scaleValue, preview = False):
		if not preview:
			self.drawPoints(glyph, scaleValue)
			self.drawStartPoints(glyph, scaleValue)

		save()
		fill(0)
		for font in self.ui.font2Storage:
			
			g = font[glyph.name]
			if g == glyph: continue

			if self.ui.interpolaviourShowInterpolation:
				save()
				fill(0, 0, 1*abs(preview-1), 1)
				translate(x = 5 * (self.ui.EM_Dimension_X * .25))
				scale(.5, .5)
				tempFont = NewFont(showUI = False)
				success, gI = interpol_glyph_glyph_ratioX_ratioY_scaleX_scaleY_toFont_glyphName(
					g1 = glyph, 
					g2 = g, 
					ratio_x = self.ui.interpolaviourInterpolationValue / 1000,
					ratio_y = self.ui.interpolaviourInterpolationValue / 1000,
					scale_x = 1,
					scale_y = 1,
					f = tempFont,
					glyphName = glyph.name
					)
				if success == True:
					drawGlyph(gI)
				else:
					fill(1, 0, .3, .8)
					oval(0, 0, 1000, 1000)
				tempFont.close()
				restore()

				translate(x = 2 * self.ui.EM_Dimension_X)
				drawGlyph(g)
				if not preview:
					self.drawPoints(g, scaleValue)
					self.drawStartPoints(g, scaleValue)
		restore()

