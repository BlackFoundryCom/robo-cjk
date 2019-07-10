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
from drawers.DeepComponentDrawer import DeepComponentDrawer

class CurrentGlyphViewDrawer():

	def __init__(self, interface):
		self.ui = interface

	def draw(self, info):
		g = self.ui.glyph
		f = self.ui.font2Storage[self.ui.font]
		fill(.2, 0, 1, .5)
		if info['notificationName'] == "drawPreview":
			fill(0, 0, 0, 1)
		DeepComponentDrawer(self.ui, g, f)
