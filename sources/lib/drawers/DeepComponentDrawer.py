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

class DeepComponentDrawer():

    def __init__(self, interface, glyph, storageFont):
        self.ui = interface
        self.glyph = glyph
        self.font = storageFont
        self.draw()

    def draw(self):
        g = self.glyph
        f = self.font

        if "deepComponentsGlyph" in g.lib: 

            save()
            for glyph in self.ui.current_DeepComponents:
                save()
                name, value = self.ui.current_DeepComponents[glyph]
                ID = value[0]
                offset_X, offset_Y = value[1]
                if glyph == self.ui.current_DeepComponent_selection:
                    translate(self.ui.deepCompo_DeltaX, self.ui.deepCompo_DeltaY)
                stroke(None)
                if glyph == self.ui.current_DeepComponent_selection:
                    stroke(1, 0, 0, 1)
                drawGlyph(glyph)
                restore()
            restore()

        ##### TEMP DEEP COMP #####
        save()
        if self.ui.temp_DeepCompo_slidersValuesList and self.ui.selectedVariantName and self.ui.activeMaster:
            newGlyph = deepolation(RGlyph(), self.ui.font2Storage[self.ui.font][self.ui.selectedVariantName], layersInfo = {e["Layer"]:int(e["Values"]) for e in self.ui.temp_DeepCompo_slidersValuesList})
            fill(1, 0, .3, .8)
            drawGlyph(newGlyph)
        restore()