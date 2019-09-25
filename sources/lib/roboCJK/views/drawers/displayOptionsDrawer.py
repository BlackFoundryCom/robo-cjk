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

from mojo.roboFont import *
from mojo.drawingTools import *

class StackMasterDrawer():

    def __init__(self, RCJKI, controller):
        self.RCJKI = RCJKI
        self.c = controller
        # print(self.c.__class__.__name__)

    def getFonts(self):
        self.fonts = []

        if self.RCJKI.designStep == '_deepComponentsEdition_glyphs' and self.c.__class__.__name__ != "MainCanvas":
            for f in self.RCJKI.DCFonts2Fonts.keys():
                if f == self.RCJKI.currentFont: continue
                self.fonts.append(f)
        else:
            for t in self.RCJKI.allFonts:
                for _ , f in t.items():
                    self.fonts.append(f)
        return self.fonts

    def draw(self, glyph, preview = False):
        save()
        if not preview:

            stackMasterColor = self.RCJKI.settings["stackMastersColor"]

            red = stackMasterColor.redComponent() 
            green = stackMasterColor.greenComponent()
            blue = stackMasterColor.blueComponent() 
            alpha = stackMasterColor.alphaComponent()

            fill(red, green, blue, alpha)

            for font in self.getFonts():

                if glyph is None: continue
                if glyph.name not in font: continue
                if font[glyph.name] == glyph: continue

                drawGlyph(font[glyph.name].getLayer(glyph.layer.name))

        restore()

class WaterFallDrawer():

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI

    def draw(self, glyph, preview = False):
        save() 
        if not preview:

            EM_Dimension_X, EM_Dimension_Y = self.RCJKI.project.settings['designFrame']['em_Dimension']

            s = .5
            scale(s,s)
            translate(0, -EM_Dimension_Y - 200)

            waterFallColor = self.RCJKI.settings["waterFallColor"]

            red = waterFallColor.redComponent() 
            green = waterFallColor.greenComponent()
            blue = waterFallColor.blueComponent() 
            alpha = waterFallColor.alphaComponent()

            fill(red, green, blue, alpha)
            
            for i in range(1, 5):

                drawGlyph(glyph)

                translate(EM_Dimension_X + 150, 0)
                scale(s,s)

        restore()



